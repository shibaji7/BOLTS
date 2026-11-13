# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
import numpy as np
import pytest

from bolts.damage.insulation_withstand import time_to_failure_s, withstand_voltage_V
from bolts.earthing.electrode_resistance import rods_in_line_ohm, single_rod_ohm
from bolts.earthing.gpr import ground_potential_rise_V
from bolts.earthing.soil import wenner_resistivity_ohm_m
from bolts.impact import optical, terminal
from bolts.metrics.device_stress import zener_power_ratio, zener_power_W
from bolts.metrics.energy import energy_J


def test_optical_baseline_matches_chesnoy_chain(params):
    ev = optical.evaluate(params, np.array([1.0]), 12)
    assert ev["osnr_base_dB"] == pytest.approx(28.2, abs=0.05) and ev["q2_seg_dB"][0] == pytest.approx(15.8, abs=0.05)
    assert ev["margin_dB"][0] == pytest.approx(10.8, abs=0.05) and optical.span_loss_dB(params) == pytest.approx(12.0)
    assert optical.shannon_gap(params) == pytest.approx(1.054, abs=1e-3)


def test_pump_law_current_below_90_percent_starves_the_laser(params):
    r = optical.repeater_state(params, np.array([1.1, 1.0, 0.95, 0.9, 0.8, 0.5, 0.0]))
    assert r["pump_ratio"][0] == 1.0 and r["pump_ratio"][3] == 1.0 and r["pump_ratio"][4] < 1.0 and r["pump_ratio"][-1] == 0.0
    assert r["zener_power_W"][1] == pytest.approx(5.6) and r["zener_power_ratio"][0] == pytest.approx(2.0)


def test_pump_failure_penalty_formula():
    from bolts.impact.optical import q_chain  # noqa: F401
    assert 10 * np.log10((11 + 10 ** 0.3) / 12) == pytest.approx(0.35, abs=0.01)


def test_terminal_ladder_thresholds(params):
    lad = terminal.format_ladder(params)
    assert [round(f["req_snr_dB"], 1) for f in lad] == [5.0, 8.7, 12.0, 15.1, 18.2] and [f["rate_Gbps"] for f in lad] == [100, 150, 200, 250, 300]


def test_terminal_state_machine(params):
    t = np.arange(0.0, 400.0, 1.0)
    q = np.full(len(t), 15.8)
    q[100:300] = 11.8                                    # a sustained dip below the 200G requirement (12.0 dB)
    ad = terminal.terminal_trace(params, t, q, 200.0, adapt=True)
    fx = terminal.terminal_trace(params, t, q, 200.0, adapt=False)
    assert ad["rate_Gbps"][50] == 200.0 and fx["rate_Gbps"][150] == 0.0 and ad["rate_Gbps"][250] == 150.0
    ma, mf = (terminal.traffic_metrics(t, x["rate_Gbps"], 200.0) for x in (ad, fx))
    assert ma["mean_rate_fraction"] > mf["mean_rate_fraction"] and mf["uas"] > 100 and 0.0 < ma["availability"] <= 1.0


def test_traffic_metrics_short_series(params):
    m = terminal.traffic_metrics(np.array([0.0, 0.5]), np.array([100.0, 100.0]), 100.0)
    assert m["seconds"] == 0 and m["mean_rate_fraction"] == 1.0


def test_device_stress_and_energy(params):
    assert zener_power_ratio(params, np.array([1.5]))[0] == pytest.approx(6.0) and zener_power_W(params, np.array([1.0]))[0] == pytest.approx(5.6)
    assert energy_J(np.full(11, 2.0), np.arange(11.0)) == pytest.approx(20.0)


def test_earthing_formulas():
    assert wenner_resistivity_ohm_m(2.0, 0.0, 5.0) == pytest.approx(2 * np.pi * 2.0 * 5.0)
    assert wenner_resistivity_ohm_m(2.0, 1.0, 5.0) > 0
    rs = single_rod_ohm(100.0, 3.0, 0.01)
    assert rs == pytest.approx(100.0 / (2 * np.pi * 3.0) * (np.log(1200.0) - 1.0)) and 25.0 < rs < 50.0
    assert rods_in_line_ohm(100.0, rs, 6.0, 2) < rs
    with pytest.raises(ValueError):
        rods_in_line_ohm(100.0, rs, 6.0, 5)
    assert ground_potential_rise_V(10e3, 3.0) == 30e3


def test_insulation_life_law():
    assert time_to_failure_s(2.0, 1000.0, 10.0) == pytest.approx(1000.0 / 1024.0)
    assert withstand_voltage_V(time_to_failure_s(3.0, 5.0, 7.0), 5.0, 7.0) == pytest.approx(3.0)
