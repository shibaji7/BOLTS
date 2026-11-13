# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""v0.2 round 3: Newton iteration, piecewise Zener, clamp devices (diode chain, arrester) and the SPICE export of nonlinear devices and current sources."""
import shutil

import numpy as np
import pytest

import bolts
from bolts.elements.arrester import Arrester
from bolts.elements.diode_chain import DiodeChain
from bolts.elements.lumped import Capacitor, Resistor, VSource
from bolts.elements.zener import LinearZener, PiecewiseZener
from bolts.errors import BoltsError, ConfigError, ConvergenceError
from bolts.mna import newton
from bolts.mna.assemble import assemble
from bolts.mna.stamp import ConstantSource, RecordSource, Stamper
from bolts.mna.transient import run_transient
from bolts.spice.compare import compare_voltages
from bolts.spice.netlist import netlist_text
from bolts.spice.run_ngspice import run_ngspice
from bolts.waveforms.step_ramp_sine import ramp_hold, step

needs_ngspice = pytest.mark.skipif(shutil.which("ngspice") is None, reason="ngspice is not installed")


def _run(overrides, rec, dt, **kw):
    p = bolts.load_parameters(overrides=overrides)
    net = bolts.build_network(p, rec)
    return net, bolts.run_transient(net, p, dt_s=dt, **kw)


# ---- D1 Newton ---------------------------------------------------------------------------------------------------------------------------
def test_newton_path_equals_the_linear_path_on_a_linear_network(params, example_record):
    p = params.with_overrides({"pfe.max_voltage_kV_per_end": 0.75})          # the 1.5 kV what-if: the PFE clamps, so the clamp logic is compared too
    net = bolts.build_network(p, example_record)
    lin = bolts.run_transient(net, p).transient
    nwt = bolts.run_transient(net, p, newton=True).transient
    assert np.abs(lin.x - nwt.x).max() < 1e-8 and np.array_equal(lin.clamped, nwt.clamped) and lin.r_loop_ohm == pytest.approx(nwt.r_loop_ohm)
    assert np.abs(lin.v_tot_V - nwt.v_tot_V).max() < 1e-8


def test_newton_path_equals_the_linear_path_with_a_slew_limit(params):
    rec = step(-300.0, duration_s=5.0, dt_s=0.01, t_step_s=1.0)
    p = params.with_overrides({"pfe.output_slew_limit_V_per_s": 100.0})
    net = bolts.build_network(p, rec)
    a = bolts.run_transient(net, p, dt_s=0.01).transient
    b = bolts.run_transient(net, p, dt_s=0.01, newton=True).transient
    assert np.abs(a.v_tot_V - b.v_tot_V).max() < 1e-8 and np.array_equal(a.slew_limited, b.slew_limited)


def test_nonlinear_network_refuses_the_linear_path(params):
    rec = ramp_hold(-100.0, 10.0, 10.0, 1.0)
    p = params.with_overrides({"repeater.zener_knee_current_A": 0.9})
    net = bolts.build_network(p, rec)
    assert net.compile().has_nonlinear
    with pytest.raises(BoltsError, match="nonlinear"):
        bolts.run_transient(net, p, dt_s=1.0, newton=False)


def test_newton_reports_non_convergence(monkeypatch, params):
    monkeypatch.setattr(newton, "MAX_ITER", 1)
    st = Stamper(["in", "m"])
    VSource("vs", None, "in", ConstantSource(50.0)).stamp(st)
    Resistor("r", "in", "m", 100.0).stamp(st)
    DiodeChain("d", "m", None, 2, 0.7, 2.0).stamp(st)
    sysm = assemble(st)
    with pytest.raises(ConvergenceError):
        newton.newton_solve(sysm, sysm.G, sysm.exogenous_rhs(np.array([0.0]))[0], np.zeros(sysm.n))


# ---- D2 piecewise Zener ------------------------------------------------------------------------------------------------------------------
def test_piecewise_zener_law():
    z = PiecewiseZener(56.0, 5.0, 1.0, 0.9)
    assert z.v_knee_V == pytest.approx(55.5)
    assert z.drop_V(1.0) == pytest.approx(56.0) and z.drop_V(1.0) == pytest.approx(LinearZener(56.0, 5.0, 1.0).drop_V(1.0))       # same as the linear law above the knee
    assert z.drop_V(0.9) == pytest.approx(55.5)                                                           # continuous at the knee ...
    assert z.drop_V(0.9 - 1e-9) == pytest.approx(55.5, abs=1e-6) and z.drop_V(0.0) == 0.0 and z.drop_V(-1e-9) == pytest.approx(0.0, abs=1e-6)   # ... and at zero
    assert z.slope_ohm(1.0) == 5.0 and z.slope_ohm(0.5) == pytest.approx(55.5 / 0.9) and z.slope_ohm(-0.2) == 5.0
    assert z.power_W(0.5) == pytest.approx(0.5 * z.drop_V(0.5))
    assert z.series_parameters() == LinearZener(56.0, 5.0, 1.0).series_parameters()
    for bad in ((56.0, 5.0, 1.0, 1.5), (56.0, 5.0, 1.0, 0.0)):
        with pytest.raises(ConfigError):
            PiecewiseZener(*bad)
    with pytest.raises(ConfigError):
        PiecewiseZener(2.0, 50.0, 1.0, 0.01)                # would make the knee voltage negative


def test_below_knee_fraction_sets_the_voltage_at_zero_current():
    z0, z5, z1 = (PiecewiseZener(56.0, 5.0, 1.0, 0.9, f) for f in (0.0, 0.5, 1.0))
    assert z0.drop_V(0.0) == 0.0 and z5.drop_V(0.0) == pytest.approx(27.75) and z1.drop_V(0.0) == pytest.approx(55.5)
    assert z5.drop_V(0.45) == pytest.approx(27.75 + 0.5 * 27.75) and z5.slope_ohm(0.45) == pytest.approx(27.75 / 0.9) and z1.slope_ohm(0.45) == 0.0
    assert z5.drop_V(-0.1) == pytest.approx(27.75 - 0.5) and z5.drop_V(0.9) == pytest.approx(55.5)               # reverse: f V_k + rz I; continuous at the knee
    with pytest.raises(ConfigError):
        PiecewiseZener(56.0, 5.0, 1.0, 0.9, 1.5)


def test_flat_below_the_knee_is_the_linear_model_for_forward_current():
    """f = 1 keeps the voltage at about V_k all the way down, like the linear Zener (which holds 56 V, here 4.5 to 5 V more per repeater at low current): the two
    currents differ by less than 12 x 5 V / 816.8 ohm = 74 mA, against 0.7 A for f = 0."""
    rec = ramp_hold(-1000.0, 60.0, 60.0, 1.0)
    _, lin = _run({"pfe.max_voltage_kV_per_end": 0.75}, rec, 1.0)
    _, flat = _run({"pfe.max_voltage_kV_per_end": 0.75, "repeater.zener_knee_current_A": 0.9, "repeater.zener_below_knee_fraction": 1.0}, rec, 1.0)
    i_lin, i_flat = lin.repeater_currents_A().min(), flat.repeater_currents_A().min()
    assert abs(i_flat - i_lin) < 0.074


def test_builder_picks_the_piecewise_zener_from_the_knee_parameter(params):
    assert not bolts.build_network(params, None).compile().has_nonlinear                                           # default: linear, as in v0.1
    net = bolts.build_network(params.with_overrides({"repeater.zener_knee_current_A": 0.9}), None)
    assert net.compile().has_nonlinear and net.meta["static_need_V"] == pytest.approx(1428.8)                 # same need at the nominal current


def test_piecewise_equals_linear_while_the_current_stays_above_the_knee(params, example_record):
    kw = {"pfe.max_voltage_kV_per_end": 2.5}
    _, lin = _run(kw, example_record, 1.0)
    _, pw = _run({**kw, "repeater.zener_knee_current_A": 0.5}, example_record, 1.0)
    assert np.abs(lin.transient.x - pw.transient.x).max() < 1e-8


def test_below_the_knee_the_current_falls_less_than_with_the_linear_zener():
    """Opposing -2 kV at the 1.5 kV what-if: the PFE sits at its cap and the loop is V_cap + E = (R_nonrep + 12 rz) I (the stack is a small resistance below zero current),
    so I = -500 / (756.8 + 60) = -0.612 A, a change of -1.612 A; the linear Zener (constant 56 V per repeater) falls to -2.361 A."""
    rec = ramp_hold(-2000.0, 60.0, 60.0, 1.0)
    _, lin = _run({"pfe.max_voltage_kV_per_end": 0.75}, rec, 1.0)
    _, pw = _run({"pfe.max_voltage_kV_per_end": 0.75, "repeater.zener_knee_current_A": 0.9}, rec, 1.0)
    d_lin, d_pw = lin.repeater_current_change_A().min(), pw.repeater_current_change_A().min()
    assert d_lin == pytest.approx(-2.361, abs=0.01)
    assert d_pw == pytest.approx(-1.0 - 500.0 / 816.8, abs=0.01) and d_pw > d_lin


# ---- D3 clamp devices --------------------------------------------------------------------------------------------------------------------
def test_clamp_law_segments_and_directions():
    arr = Arrester("a", "m", None, 100.0, r_on_ohm=2.0, g_off_S=1e-6)
    assert arr.current_A(50.0) == pytest.approx(50e-6) and arr.conductance_S(50.0) == pytest.approx(1e-6)
    assert arr.current_A(150.0) == pytest.approx(25.0 + 150e-6) and arr.conductance_S(150.0) == pytest.approx(0.5 + 1e-6)
    assert arr.current_A(-150.0) == pytest.approx(-25.0 - 150e-6)                                         # bidirectional
    one = DiodeChain("d", "m", None, 3, 0.7, 0.1, bidirectional=False)
    assert one.v_clamp_V == pytest.approx(2.1) and one.current_A(-50.0) == 0.0 and one.current_A(3.1) == pytest.approx(10.0)
    assert arr.energy_J(np.full(10, 150.0), 0.1) == pytest.approx(10 * 0.1 * 150.0 * 25.00015)
    for bad in ({"v_clamp_V": 0.0}, {"v_clamp_V": 5.0, "r_on_ohm": 0.0}, {"v_clamp_V": 5.0, "g_off_S": -1.0}):
        with pytest.raises(ValueError):
            Arrester("a", "m", None, **{"r_on_ohm": 1.0, **bad})
    with pytest.raises(ValueError):
        DiodeChain("d", "m", None, 0)


def test_clamp_elements_are_registered():
    from bolts import registry
    assert registry.get_element("arrester") is Arrester and registry.get_element("diode_chain") is DiodeChain


def test_arrester_limits_a_pulse_and_absorbs_its_energy():
    """A 1 kV step through 100 ohm into an arrester (clamp 300 V, 2 ohm) with a 1 uF node capacitance: the node settles at 300 + 700 * 2 / 102 = 313.7 V."""
    dt = 1e-6
    rec = step(1000.0, duration_s=2e-3, dt_s=dt, t_step_s=dt)
    st = Stamper(["in", "m"])
    for el in (VSource("vs", None, "in", RecordSource(rec, 1.0)), Resistor("r", "in", "m", 100.0), Capacitor("c", "m", None, 1e-6), Arrester("arr", "m", None, 300.0, 2.0)):
        el.stamp(st)
    sysm = assemble(st)
    res = run_transient(sysm, rec.t_s)
    v = res.node_V("m")
    assert v[-1] == pytest.approx(300.0 + 700.0 * 2.0 / 102.0, rel=2e-3)
    assert v.max() < 1000.0 and v.max() < 330.0                                  # the clamp holds the node far below the 1 kV drive
    arr = Arrester("arr", "m", None, 300.0, 2.0)
    assert arr.energy_J(v, dt) > 0.0


def test_arrester_across_a_pfe_terminal_bounds_its_voltage(params):
    from bolts.elements.arrester import Arrester as A
    rec = ramp_hold(-2500.0, 120.0, 60.0, 1.0)
    p = params.with_overrides({"pfe.max_voltage_kV_per_end": 2.5})
    free = bolts.build_network(p, rec)
    clamp = bolts.build_network(p, rec)
    clamp.add(A("arr_A", "A", None, 1200.0, r_on_ohm=1.0))
    v_free = bolts.run_transient(free, p, dt_s=1.0).transient.node_V("A").max()
    tr = bolts.run_transient(clamp, p, dt_s=1.0).transient
    assert v_free > 1500.0 and tr.node_V("A").max() < v_free and tr.node_V("A").max() > 1200.0          # conducting above 1.2 kV, so the terminal stays lower


# ---- D4 SPICE ----------------------------------------------------------------------------------------------------------------------------
def test_netlist_has_the_nonlinear_and_current_source_lines(params):
    rec = ramp_hold(-100.0, 10.0, 10.0, 1.0)
    p = params.with_overrides({"repeater.zener_knee_current_A": 0.9})
    net = bolts.build_network(p, rec)
    net.add(Arrester("arr", "A", None, 1200.0))
    st = Stamper(["a"])
    st.add_current_source(None, "a", ConstantSource(0.5))
    res = bolts.run_transient(net, p, dt_s=1.0).transient
    text = netlist_text(res.system, res.t_s, res.v_tot_V)
    assert "Vs_rep1 " in text and "B_rep1 " in text and "i(Vs_rep1)" in text and "B_s0 n_A 0 I = " in text and "max((v(n_A,0))-1200" in text
    sysm = assemble(st)
    assert "\nI_0 0 n_a PWL(" in netlist_text(sysm, np.array([0.0, 1.0, 2.0]))


@needs_ngspice
def test_piecewise_zener_network_agrees_with_ngspice():
    rec = ramp_hold(-1500.0, 60.0, 60.0, 0.5)
    _, res = _run({"pfe.max_voltage_kV_per_end": 0.75, "repeater.zener_knee_current_A": 0.9}, rec, 0.5)
    tr = res.transient
    assert res.repeater_current_change_A().min() < -0.95          # the current is driven through every segment of the Zener law
    c = compare_voltages(tr.nodes_V, run_ngspice(tr.system, tr.t_s, tr.v_tot_V))
    assert c["max_rel"] < 1e-5


@needs_ngspice
def test_clamp_and_current_source_agree_with_ngspice():
    dt = 1e-5          # the node time constant (100 uF x a few ohm) is hundreds of steps, so BOLTS and ngspice both resolve it; a much shorter one would compare time-stepping, not circuits
    rec = ramp_hold(1000.0, 5e-4, 3.5e-3, dt)           # a ramp, not a step: after a sharp edge the two solvers differ for a few steps in how they start, which is not the circuit
    st = Stamper(["in", "m"])
    for el in (VSource("vs", None, "in", RecordSource(rec, 1.0)), Resistor("r", "in", "m", 100.0), Capacitor("c", "m", None, 100e-6),
               DiodeChain("d", "m", None, 4, 0.7, 2.0, g_off_S=1e-9), Arrester("arr", "m", None, 500.0, 5.0)):
        el.stamp(st)
    st.add_current_source(None, "m", RecordSource(rec, 1e-3))                     # a small injected current as well
    sysm = assemble(st)
    res = run_transient(sysm, rec.t_s)
    # ngspice's first steps start differently (about 1% off at step 16); the difference dies out with the circuit's time constant (0.4 ms = 40 steps), so compare
    # once the start-up is over: the clamps, the capacitor and the current source then agree to better than 1e-4
    c = compare_voltages(res.nodes_V[200:], run_ngspice(sysm, rec.t_s)[200:])
    assert c["max_rel"] < 1e-4
