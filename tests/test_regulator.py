# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""The PFE regulator: a first-order loop integrated exactly over each step (checks carried over from the pfe_design study)."""
import numpy as np
import pytest

import bolts
from bolts.waveforms.step_ramp_sine import ramp, sine, step


def _run(params, rec, dt, tau=None, limit_kV=None):
    ov = {}
    if tau is not None:
        ov["pfe.regulator_response_s"] = tau
    if limit_kV is not None:
        ov["pfe.max_voltage_kV_per_end"] = limit_kV
    p = params.with_overrides(ov) if ov else params
    net = bolts.build_network(p, rec)
    return net, bolts.run_transient(net, p, dt_s=dt)


def test_loop_resistance_and_static_need(params):
    net, res = _run(params, ramp(0.0, 10, 1.0), 1.0)
    assert res.transient.r_loop_ohm == pytest.approx(816.8, abs=1e-6)         # 751 + 12 x 5 + 2 x 3
    assert res.transient.v_tot_V[0] == pytest.approx(1428.8, abs=1e-6)       # the static need
    assert net.meta["n_repeaters"] == 12 and net.meta["static_need_V"] == pytest.approx(1428.8)
    assert np.abs(res.repeater_current_change_A()).max() < 1e-9


@pytest.mark.parametrize("tau,dt", [(0.005, 0.0005), (0.005, 0.1), (2.0, 0.2), (2.0, 1.0), (2.0, 5.0), (0.5, 1.0)])
def test_ramp_error_is_rate_tau_over_rloop_for_any_dt_over_tau(params, tau, dt):
    _net, res = _run(params, ramp(1.0, max(60.0, 12 * tau), dt), dt, tau=tau)
    err = res.transient.i_sense_A[-1] - 1.0
    assert err == pytest.approx(tau / res.transient.r_loop_ohm, rel=0.01)


def test_step_peak_follows_ramp_over_dt_and_tends_to_dv_over_rloop(params):
    tau, peaks = 0.005, []
    for dt in (0.0001, 0.001, 0.005, 0.05):
        _net, res = _run(params, step(100.0, max(1.0, 40 * dt), dt, 0.2), dt, tau=tau)
        peaks.append(np.abs(res.transient.i_sense_A - 1.0).max())
        assert res.transient.v_tot_V[-1] == pytest.approx(1428.8 - 100.0, abs=1e-3)       # the PFE ends up absorbing the step
        r = res.transient.r_loop_ohm
        assert peaks[-1] == pytest.approx(100.0 / r * (tau / dt) * (1 - np.exp(-dt / tau)), rel=0.03)
    assert peaks == sorted(peaks, reverse=True) and peaks[0] == pytest.approx(100.0 / 816.8, rel=0.03)


def test_sine_gain_matches_the_analytic_high_pass(params):
    tau, f, dt = 2.0, 0.08, 1.0
    _net, res = _run(params, sine(10.0, f, 160.0, dt), dt, tau=tau)
    m = res.t_s > 80.0
    gain = np.abs(res.transient.i_sense_A[m] - 1.0).max() / 10.0
    w = 2 * np.pi * f * tau
    assert gain == pytest.approx(w / np.sqrt(1 + w * w) / res.transient.r_loop_ohm, rel=0.03)


def test_pfe_clamps_at_its_limit_and_the_current_falls(params):
    _net, res = _run(params, step(-400.0, 60.0, 1.0, 20.0), 1.0, limit_kV=0.75)       # an opposing 400 V against 71 V of headroom
    s = res.summary()
    assert s["frac_pfe_clamped"] > 0.5 and res.transient.v_tot_V.max() <= 1500.0 + 1e-9
    assert s["di_min_mA"] == pytest.approx(-1e3 * (400.0 - 71.2) / 816.8, rel=0.02)


def test_assisting_storm_drives_the_pfe_to_zero(params):
    _net, res = _run(params, step(2000.0, 60.0, 1.0, 20.0), 1.0)
    assert res.transient.v_tot_V.min() == pytest.approx(0.0) and res.summary()["di_max_mA"] > 500


def test_window_starting_away_from_zero_has_no_start_up_step(params):
    from bolts.waveforms.base import Record
    rec = Record(np.arange(0.0, 60.0, 1.0), np.full(60, -50.0))
    _net, res = _run(params, rec, 1.0)
    assert np.abs(res.repeater_current_change_A()).max() < 1e-9


def test_single_end_feed_keeps_the_earth_path(params):
    from bolts.network.power_modes import PowerMode
    net = bolts.build_network(params, ramp(0.0, 10, 1.0), mode=PowerMode.SINGLE_END_A)
    res = bolts.run_transient(net, params)
    assert res.transient.r_loop_ohm == pytest.approx(816.8) and net.meta["mode"] == "single_end_A"
