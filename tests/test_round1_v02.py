# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""v0.2 round 1: cable property providers, coil / land cable / beach joint / PFE filter, the synthetic-record library, and the PFE stress metrics."""
import numpy as np
import pytest

import bolts
from bolts.elements.beach_joint import BeachJoint
from bolts.elements.cable_segment import CableSegment
from bolts.elements.coil import Coil
from bolts.elements.land_cable import LandCable
from bolts.elements.lumped import Resistor, VSource
from bolts.elements.pfe_filter import PfeFilter
from bolts.errors import ConfigError
from bolts.mna.assemble import assemble
from bolts.mna.stamp import RecordSource, Stamper
from bolts.mna.transient import run_transient
from bolts.properties.base import RLCG
from bolts.properties.constant import ConstantRLCG
from bolts.properties.depth_profile import DepthProfileRLCG
from bolts.properties.section_table import SectionTableRLCG
from bolts.properties.temperature_R import TemperatureRLCG
from bolts.space_weather.synthetic import synthetic_vind
from bolts.waveforms.step_ramp_sine import ramp_hold, step

BASE = RLCG(1.0, 0.2e-6, 0.0)


def _table(r=(1.0, 2.0), edges=(0.0, 375.4, 750.8), inductance=None):
    return SectionTableRLCG(np.array(edges), np.array(r), np.full(len(r), 0.2e-6), np.zeros(len(r)), inductance)


# ---- A1 section table -------------------------------------------------------------------------------------------------------------------
def test_uniform_section_table_equals_the_constant_provider(params):
    const = ConstantRLCG.from_parameters(params)
    tab = _table(r=(1.0, 1.0))
    assert tab.rlcg(100.0) == const.rlcg(100.0) and tab.rlcg(750.8) == const.rlcg(0.0)


def test_section_lookup_and_boundaries():
    tab = _table()
    assert tab.rlcg(0.0).r_ohm_per_km == 1.0 and tab.rlcg(375.3).r_ohm_per_km == 1.0
    assert tab.rlcg(375.4).r_ohm_per_km == 2.0 and tab.rlcg(750.8).r_ohm_per_km == 2.0     # a boundary belongs to the next section; the far end to the last
    with pytest.raises(ValueError):
        tab.rlcg(800.0)


def test_section_table_gives_each_span_its_own_resistance(params):
    """6 spans in the first section (1 ohm/km), 7 in the second (2 ohm/km): the static need follows the summed resistance."""
    p = params.with_overrides({"pfe.max_voltage_kV_per_end": 2.5})
    net = bolts.build_network(p, None, provider=_table())
    span_km = net.meta["span_km"]
    r_cable = (6 * 1.0 + 7 * 2.0) * span_km
    expect = 1.0 * (r_cable + 2 * 3.0) + 12 * float(p.get("repeater", "voltage_drop_V"))
    assert net.meta["static_need_V"] == pytest.approx(expect, rel=1e-9)


def test_section_table_csv_roundtrip_and_errors(tmp_path):
    f = tmp_path / "t.csv"
    f.write_text("x_start_km,x_end_km,r_ohm_per_km,c_uF_per_km,g_S_per_km,l_mH_per_km\n0,100,1.0,0.2,0,0.5\n100,300,1.2,0.25,1e-9,0.6\n")
    t = SectionTableRLCG.from_csv(f)
    v = t.rlcg(150.0)
    assert v.r_ohm_per_km == 1.2 and v.c_F_per_km == pytest.approx(0.25e-6) and v.g_S_per_km == 1e-9 and v.inductance_known and v.l_H_per_km == pytest.approx(0.6e-3)
    f.write_text("x_start_km,x_end_km,r_ohm_per_km,c_uF_per_km\n0,100,1,0.2\n150,300,1,0.2\n")
    with pytest.raises(ConfigError, match="contiguous"):
        SectionTableRLCG.from_csv(f)
    f.write_text("x_start_km,x_end_km,r_ohm_per_km\n0,100,1\n")
    with pytest.raises(ConfigError, match="missing columns"):
        SectionTableRLCG.from_csv(f)
    f.write_text("x_start_km,x_end_km,r_ohm_per_km,c_uF_per_km\n0,100,1,0.2\n")
    assert not SectionTableRLCG.from_csv(f).rlcg(10.0).inductance_known       # no L column: inductance stays unknown
    with pytest.raises(ConfigError):
        SectionTableRLCG(np.array([0.0, 10.0]), np.array([1.0, 2.0]), np.array([1e-7]), np.array([0.0]))


# ---- A3 temperature, A2 depth -----------------------------------------------------------------------------------------------------------
def test_temperature_law():
    prov = TemperatureRLCG(ConstantRLCG(BASE))
    assert prov.rlcg(0.0, temperature_C=20.0).r_ohm_per_km == pytest.approx(1.0)
    assert prov.rlcg(0.0, temperature_C=4.0).r_ohm_per_km == pytest.approx(1.0 - 16 * 0.00393)       # about 6% lower in cold deep water
    assert prov.rlcg(0.0, temperature_C=40.0).r_ohm_per_km == pytest.approx(1.0 + 20 * 0.00393)
    with pytest.raises(ValueError):
        prov.rlcg(0.0, temperature_C=-300.0)


def test_temperature_provider_lowers_the_static_need(params):
    cold = bolts.build_network(params, None, provider=TemperatureRLCG(ConstantRLCG.from_parameters(params)))      # seabed 4 C
    ref = bolts.build_network(params, None)
    drop = ref.meta["static_need_V"] - cold.meta["static_need_V"]
    assert drop == pytest.approx(1.0 * 750.8 * 16 * 0.00393, rel=1e-9)


def test_depth_profile_interpolates_and_drives_temperature():
    shallow_warm = DepthProfileRLCG(TemperatureRLCG(ConstantRLCG(BASE)), np.array([0.0, 100.0, 700.0]), np.array([20.0, 1000.0, 4000.0]),
                                    np.array([0.0, 1000.0, 4000.0]), np.array([15.0, 6.0, 2.0]))
    assert shallow_warm.depth_at(50.0) == pytest.approx(510.0)
    r_shore = shallow_warm.rlcg(0.0).r_ohm_per_km
    r_deep = shallow_warm.rlcg(700.0).r_ohm_per_km
    assert r_shore > r_deep                                                       # warm shallow water: higher R than the cold deep sea
    assert r_deep == pytest.approx(1.0 * (1.0 + 0.00393 * (2.0 - 20.0)))
    plain = DepthProfileRLCG(ConstantRLCG(BASE), np.array([0.0, 10.0]), np.array([0.0, 10.0]))
    assert plain.rlcg(5.0) == BASE                                                # no temperature table, constant base: unchanged
    with pytest.raises(ConfigError):
        DepthProfileRLCG(ConstantRLCG(BASE), np.array([0.0, 10.0]), np.array([0.0, 10.0]), np.array([0.0, 100.0]), None)
    with pytest.raises(ConfigError):
        DepthProfileRLCG(ConstantRLCG(BASE), np.array([10.0, 0.0]), np.array([0.0, 10.0]))


# ---- A4, A5 elements --------------------------------------------------------------------------------------------------------------------
def _series_run(elements, nodes, dt, n):
    st = Stamper(nodes)
    for el in elements:
        el.stamp(st)
    sysm = assemble(st)
    t = dt * np.arange(n)
    return sysm, run_transient(sysm, t)


def test_coil_dc_drop_and_time_constant():
    """A 9 V step through a 10 ohm / 1 H coil into 90 ohm: i(t) = 0.09 (1 - exp(-t / tau)), tau = L / (R_coil + R_load) = 10 ms."""
    tau, dt = 1.0 / 100.0, 1.0 / 100.0 / 400
    rec = step(9.0, duration_s=6 * tau, dt_s=dt, t_step_s=dt)
    st = Stamper(["in", "mid"])
    for el in (VSource("v", None, "in", RecordSource(rec, 1.0)), Coil("coil", "in", "mid", 1.0, 10.0), Resistor("load", "mid", None, 90.0)):
        el.stamp(st)
    res = run_transient(assemble(st), rec.t_s)
    i = res.branch_I("coil")
    for k in (1, 3, 5):
        idx = int(k * tau / dt) + 1
        assert abs(i[idx]) == pytest.approx(0.09 * (1 - np.exp(-k)), rel=5e-3)
    with pytest.raises(ValueError):
        Coil("c", "a", "b", 0.0)


def test_land_cable_is_a_cable_span():
    lc = LandCable("land0", "a", "b", 20.0, 1.0, 0.2e-6)
    assert isinstance(lc, CableSegment) and lc.r_ohm == pytest.approx(20.0) and lc.c_F == pytest.approx(4e-6)


def test_beach_joint_resistance_and_capacitance():
    st = Stamper(["a", "b"])
    BeachJoint("bj", "a", "b", r_ohm=0.5, c_F=2e-9, withstand_V=15e3).stamp(st)
    sysm = assemble(st)
    assert sysm.branches[0].r_ohm == 0.5 and sysm.C[0, 0] == pytest.approx(1e-9) and sysm.C[1, 1] == pytest.approx(1e-9)
    with pytest.raises(ValueError):
        BeachJoint("bj", "a", "b", r_ohm=-1.0)


def test_pfe_filter_rings_at_its_natural_frequency():
    """1 H and 1 uF: f0 = 159.15 Hz. A step into the filter makes the output ring at that frequency (series R = 1 ohm barely damps it)."""
    filt = PfeFilter("filt", "a", "b", 1.0, 1e-6, r_ohm=1.0)
    f0 = filt.natural_frequency_Hz
    assert f0 == pytest.approx(1.0 / (2 * np.pi * np.sqrt(1e-6)), rel=1e-12)
    dt = 1.0 / f0 / 400
    n = int(6.0 / f0 / dt)
    # run_transient starts from the DC state, so drive with a step from zero instead of a constant source
    rec = step(100.0, duration_s=n * dt, dt_s=dt, t_step_s=dt)
    st2 = Stamper(["a", "b"])
    for el in [VSource("v", None, "a", RecordSource(rec, 1.0)), filt, Resistor("load", "b", None, 1e7)]:
        el.stamp(st2)
    sysm = assemble(st2)
    res = run_transient(sysm, rec.t_s)
    v = res.node_V("b") - 100.0
    up = np.where((v[:-1] < 0) & (v[1:] >= 0))[0]
    assert len(up) >= 3
    period = (up[-1] - up[0]) / (len(up) - 1) * dt
    assert period == pytest.approx(1.0 / f0, rel=0.01)
    with pytest.raises(ValueError):
        PfeFilter("f", "a", "b", -1.0, 1e-6)


# ---- B1 synthetic record ---------------------------------------------------------------------------------------------------------------
def test_synthetic_library_reproduces_the_shipped_example(example_record):
    ts, vs = np.loadtxt("data/storm_may2024_vind_72V.csv", delimiter=",", skiprows=1, unpack=True)
    rec = synthetic_vind(ts, vs)
    assert np.allclose(rec.values, example_record.values, atol=1e-4)           # the CSV is rounded to 4 decimals
    again = synthetic_vind(ts, vs)
    assert np.array_equal(rec.values, again.values)                              # a fixed seed is reproducible
    other = synthetic_vind(ts, vs, seed=1)
    assert not np.allclose(other.values, rec.values) and np.argmin(other.values) > 0


# ---- C2 PFE stress metrics -------------------------------------------------------------------------------------------------------------
NEED = 1428.8


def _stress(amp, kv):
    p = bolts.load_parameters(overrides={"pfe.max_voltage_kV_per_end": kv})
    rec = ramp_hold(amp, 600.0, 1200.0, 1.0)
    return bolts.assess(bolts.run_transient(bolts.build_network(p, rec), p, dt_s=1.0))


def test_assisting_storm_beyond_zero_volts_excess_and_overcurrent():
    s = _stress(2000.0, 0.75)
    t0 = 600.0 * NEED / 2000.0
    integral = (2000.0 - NEED) * (600.0 - t0) / 2.0 + (2000.0 - NEED) * 1200.0
    assert s["pfe_excess_peak_V"] == pytest.approx(2000.0 - NEED)
    assert s["pfe_excess_integral_Vs"] == pytest.approx(integral, rel=0.02)
    assert s["pfe_shortfall_peak_V"] == 0.0
    assert s["pfe_i_max_over_set"] == pytest.approx((2000.0 - 612.0) / 816.8, rel=0.03)        # the PFE is a short: I = (E - V_rep) / R_loop
    assert s["pfe_time_above_1.5x_set_s"] > 1000.0 and s["pfe_time_at_zero_s"] > 1000.0


def test_opposing_storm_beyond_the_cap_shortfall():
    s = _stress(-2000.0, 0.75)
    t0 = 600.0 * (1500.0 - NEED) / 2000.0
    integral = (NEED + 2000.0 - 1500.0) * (600.0 - t0) / 2.0 + (NEED + 2000.0 - 1500.0) * 1200.0
    assert s["pfe_shortfall_peak_V"] == pytest.approx(NEED + 2000.0 - 1500.0)
    assert s["pfe_shortfall_integral_Vs"] == pytest.approx(integral, rel=0.02)
    assert s["pfe_excess_peak_V"] == 0.0 and s["pfe_time_at_upper_limit_s"] > 1000.0


def test_storm_inside_the_range_is_harmless():
    s = _stress(-500.0, 2.5)
    assert s["pfe_shortfall_peak_V"] == 0.0 and s["pfe_excess_peak_V"] == 0.0 and s["pfe_time_at_upper_limit_s"] == 0.0
    assert s["pfe_i_max_over_set"] == pytest.approx(1.0, abs=1e-3)


# ---- provider selection from the parameters, and the example tables --------------------------------------------------------------------
def test_properties_package_reexports_the_providers():
    from bolts import properties
    for name in ("RLCG", "ConstantRLCG", "SectionTableRLCG", "DepthProfileRLCG", "TemperatureRLCG", "PropertyProvider", "provider_from_parameters"):
        assert hasattr(properties, name) and name in properties.__all__


def test_default_parameters_select_the_constant_provider(params):
    from bolts.properties import provider_from_parameters
    assert isinstance(provider_from_parameters(params), ConstantRLCG)


def test_parameters_select_the_example_tables():
    from bolts.properties import provider_from_parameters
    p = bolts.load_parameters(overrides={
        "cable.section_table_csv": "data/example_cable_sections.csv", "cable.temperature_model": "copper",
        "cable.depth_profile_csv": "data/example_route_depth.csv", "cable.depth_temperature_csv": "data/example_depth_temperature.csv"})
    prov = provider_from_parameters(p)
    assert isinstance(prov, DepthProfileRLCG) and isinstance(prov.base, TemperatureRLCG) and isinstance(prov.base.base, SectionTableRLCG)
    shore, deep = prov.rlcg(10.0), prov.rlcg(400.0)
    assert shore.r_ohm_per_km == pytest.approx(0.90 * (1 + 0.00393 * (np.interp(np.interp(10.0, [0, 50], [5, 40]), [0, 30, 60], [8, 2, 0]) - 20)))
    assert deep.r_ohm_per_km < 1.05 and shore.c_F_per_km == pytest.approx(0.22e-6)


def test_bad_temperature_model_is_rejected():
    from bolts.properties import provider_from_parameters
    with pytest.raises(ConfigError):
        provider_from_parameters(bolts.load_parameters(overrides={"cable.temperature_model": "silver"}))


def test_example_temperature_changes_the_headroom_by_the_copper_law():
    """4 C instead of 20 C removes 16 K x 0.00393 of the cable resistance from the static need (the whole 1 ohm/km x 750.8 km)."""
    base = bolts.build_network(bolts.load_parameters(), None).meta["static_need_V"]
    cold = bolts.build_network(bolts.load_parameters(overrides={"cable.temperature_model": "copper"}), None).meta["static_need_V"]
    assert base - cold == pytest.approx(750.8 * 16 * 0.00393)


def test_capacitance_sets_the_fast_current_when_the_pfe_has_room():
    """5 kV basis, a 60 V swing at 1 Hz: the current change is the cable's charging current, so it grows with C'."""
    amps = []
    for c in (0.05, 0.2, 0.8):
        p = bolts.load_parameters(overrides={"cable.capacitance_uF_per_km": c})
        rec = sine_rec()
        amps.append(bolts.assess(bolts.run_transient(bolts.build_network(p, rec), p, dt_s=0.025))["di_max_mA"])
    assert amps[0] < amps[1] < amps[2] and amps[2] / amps[0] > 5.0


def sine_rec():
    from bolts.waveforms.step_ramp_sine import sine
    return sine(60.0, 1.0, duration_s=30.0, dt_s=0.025)
