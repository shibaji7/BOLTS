# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""v0.2 round 2: regulator slew limit and limit state, converter bank, pump laser, insulation life."""
import numpy as np
import pytest

import bolts
from bolts.damage.insulation_withstand import constant_from_reference, life_consumed, time_to_failure_s
from bolts.elements.pfe_converter_bank import PfeConverterBank
from bolts.elements.pump_laser import PumpLaser
from bolts.impact.optical import repeater_state
from bolts.waveforms.step_ramp_sine import ramp_hold, step


def _run(overrides, rec, dt):
    p = bolts.load_parameters(overrides=overrides)
    net = bolts.build_network(p, rec)
    return net, bolts.run_transient(net, p, dt_s=dt)


# ---- C3 slew limit and limit state --------------------------------------------------------------------------------------------------------
def test_slew_limit_caps_the_voltage_change_per_step():
    dt, slew = 0.01, 100.0
    rec = step(-300.0, duration_s=10.0, dt_s=dt, t_step_s=1.0)          # opposing step: the PFE must raise its voltage by 300 V
    _, free = _run({"pfe.max_voltage_kV_per_end": 2.5}, rec, dt)
    _, held = _run({"pfe.max_voltage_kV_per_end": 2.5, "pfe.output_slew_limit_V_per_s": slew}, rec, dt)
    dv_free = np.abs(np.diff(free.transient.v_tot_V)).max()
    dv_held = np.abs(np.diff(held.transient.v_tot_V))
    assert dv_free > 10.0 * slew * dt                               # without the limit the voltage jumps (a step the loop answers within a few ms)
    assert dv_held.max() == pytest.approx(slew * dt, rel=1e-6)       # with it the voltage ramps at exactly the slew rate
    assert held.transient.slew_limited.sum() > 100 and not free.transient.slew_limited.any()
    assert held.transient.v_tot_V[-1] == pytest.approx(free.transient.v_tot_V[-1], abs=0.5)      # the same end state once the ramp is done
    i_dev = np.abs(held.repeater_current_change_A()).max()
    assert i_dev > np.abs(free.repeater_current_change_A()).max()    # a slower PFE lets the current deviate more


def test_limit_state_marks_the_side_of_saturation():
    rec_op, rec_as = ramp_hold(-2000.0, 600.0, 1200.0, 1.0), ramp_hold(2000.0, 600.0, 1200.0, 1.0)
    _, op = _run({"pfe.max_voltage_kV_per_end": 0.75}, rec_op, 1.0)
    _, asst = _run({"pfe.max_voltage_kV_per_end": 0.75}, rec_as, 1.0)
    assert op.transient.limit_state[-1] == 1 and asst.transient.limit_state[-1] == -1 and op.transient.limit_state[0] == 0
    assert op.transient.clamped[-1] and asst.transient.clamped[-1]


def test_default_has_no_slew_limit(params):
    net = bolts.build_network(params, None)
    assert net.controller.slew_V_per_s is None
    net = bolts.build_network(params.with_overrides({"pfe.output_slew_limit_V_per_s": 25.0}), None)
    assert net.controller.slew_V_per_s == 25.0


def test_assess_reports_time_slew_limited():
    rec = step(-300.0, duration_s=10.0, dt_s=0.01, t_step_s=1.0)
    p = bolts.load_parameters(overrides={"pfe.output_slew_limit_V_per_s": 100.0})
    s = bolts.assess(bolts.run_transient(bolts.build_network(p, rec), p, dt_s=0.01))
    assert s["pfe_time_slew_limited_s"] > 1.0


# ---- C4 converter bank --------------------------------------------------------------------------------------------------------------------
def test_converter_bank_range_with_failover():
    bank = PfeConverterBank(6, 500.0, 1)
    assert bank.max_voltage_V(0) == 2500.0 and bank.max_voltage_V(1) == 2500.0        # the spare takes over
    assert bank.max_voltage_V(2) == 2000.0 and bank.max_voltage_V(6) == 0.0
    assert PfeConverterBank(4, 100.0, 0).max_voltage_V(1) == 300.0
    for bad in ((0, 500.0, 0), (6, -1.0, 1), (3, 500.0, 3)):
        with pytest.raises(ValueError):
            PfeConverterBank(*bad)
    with pytest.raises(ValueError):
        bank.max_voltage_V(7)


def test_builder_uses_the_converter_bank_when_given(params):
    healthy = bolts.build_network(params.with_overrides({"pfe.converter_modules": 6, "pfe.converter_module_rating_V": 500.0}), None)
    assert healthy.meta["v_max_end_V"] == 2500.0 and healthy.meta["v_tot_max_V"] == 5000.0
    failed = bolts.build_network(params.with_overrides({"pfe.converter_modules": 6, "pfe.converter_module_rating_V": 500.0,
                                                        "pfe.converter_failed_modules": 3}), None)
    assert failed.meta["v_max_end_V"] == 1500.0 and failed.meta["v_tot_max_V"] == 3000.0
    assert bolts.build_network(params, None).meta["v_max_end_V"] == 2500.0           # no bank: max_voltage_kV_per_end as before


# ---- A6 pump laser -----------------------------------------------------------------------------------------------------------------------
def test_pump_laser_ratio_threshold_and_power():
    laser = PumpLaser(0.8, 0.2, slope_W_per_A=0.5)
    assert laser.threshold_A == pytest.approx(0.16)
    assert laser.power_ratio(0.8) == 1.0 and laser.power_ratio(1.2) == 1.0 and laser.power_ratio(0.1) == 0.0
    assert laser.power_ratio(0.48) == pytest.approx(0.5)                                # halfway between threshold and nominal
    assert laser.optical_power_W(0.8) == pytest.approx(0.5 * 0.64)
    with pytest.raises(ValueError):
        PumpLaser(0.8).optical_power_W(0.5)
    with pytest.raises(ValueError):
        PumpLaser(0.0)


def test_repeater_state_matches_the_formula_it_replaced(params):
    i = np.linspace(0.0, 1.4, 57)
    st = repeater_state(params, i)
    i_ld = np.clip(i - 0.1, 0.0, 0.8)
    th = 0.2 * 0.8
    assert np.allclose(st["pump_ratio"], np.clip((i_ld - th) / (0.8 - th), 0.0, 1.0), atol=1e-15)


# ---- A7 insulation life -------------------------------------------------------------------------------------------------------------------
def test_life_law_and_miner_sum():
    n, v_ref, t_ref = 12.0, 1500.0, 25 * 365.25 * 86400.0
    const = constant_from_reference(v_ref, t_ref, n)
    assert time_to_failure_s(v_ref, const, n) == pytest.approx(t_ref)
    assert life_consumed(np.full(1000, v_ref), t_ref / 1000, const, n) == pytest.approx(1.0)                 # the reference voltage for the reference life
    assert life_consumed(np.full(10, 2 * v_ref), 1.0, const, n) == pytest.approx(10 * 2 ** n / t_ref)        # doubling V multiplies the damage rate by 2^n
    cols = life_consumed(np.column_stack([np.full(5, v_ref), np.zeros(5)]), 1.0, const, n)
    assert cols[0] == pytest.approx(5 / t_ref) and cols[1] == 0.0
    assert life_consumed(np.full(5, -v_ref), 1.0, const, n) == pytest.approx(5 / t_ref)                       # polarity does not matter


def test_assess_reports_insulation_life_only_when_n_is_given(params):
    rec = ramp_hold(-2000.0, 600.0, 600.0, 1.0)
    p0 = params.with_overrides({"pfe.max_voltage_kV_per_end": 2.5})
    assert "insulation_life_consumed_max" not in bolts.assess(bolts.run_transient(bolts.build_network(p0, rec), p0, dt_s=1.0))
    used = []
    for n in (10.0, 20.0):
        p = p0.with_overrides({"cable.insulation_exponent_n": n})
        used.append(bolts.assess(bolts.run_transient(bolts.build_network(p, rec), p, dt_s=1.0))["insulation_life_consumed_max"])
    assert 0.0 < used[0] < used[1]                                   # a steeper life law punishes the overvoltage more


def test_percent_sign_helper():
    from bolts.plotting import style
    style.apply()
    assert style.pct() in ("%", "\\%")
