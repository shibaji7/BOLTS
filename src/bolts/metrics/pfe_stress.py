# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Stress on the PFE itself when the induced voltage takes it toward or beyond its voltage range.

Quasi-static picture (slow storms): the regulator holds the set current, so the PFE total voltage it WANTS is

    V_want = V_static - S(t)          S = the loop's induced source (positive assists the feed)

and the PFE can only deliver ``0 <= V <= V_cap``. Two kinds of excursion follow:

* **shortfall** ``max(V_want - V_cap, 0)``: the storm opposes the feed beyond what the cap can cancel; the current falls (and the light goes out);
* **excess** ``max(-V_want, 0) = max(S - V_static, 0)``: the storm assists beyond what 0 V can absorb; the PFE is a short in the loop and the
  current rises above its set point (heat in the repeaters' Zener shunts; an over-current trip may fire).

Both are in volts, with their time integrals in volt-seconds (a measure of how long and how far past the range). ``dwell_above_*`` is the time the
PFE spends near its cap. Trip levels are not vendor data yet, so the over-current exposure is reported for a few multiples of the set current."""
from __future__ import annotations

import numpy as np

from ..mna.transient import TransientResult


def pfe_stress_metrics(res: TransientResult, v_tot_max_V: float, static_need_V: float, source_V: np.ndarray | None, i_set_A: float,
                       dwell_fractions=(0.9, 0.95), overcurrent_multiples=(1.1, 1.2, 1.5)) -> dict:
    """Stress metrics of the PFE for one run. ``source_V`` is the loop source S(t) on the run's time axis (``None``: a quiet line)."""
    t = res.t_s
    dt = float(t[1] - t[0])
    s = np.zeros_like(t) if source_V is None else np.asarray(source_V, float)
    v_want = static_need_V - s
    shortfall = np.maximum(v_want - v_tot_max_V, 0.0)
    excess = np.maximum(-v_want, 0.0)
    v = res.v_tot_V
    out = {
        "pfe_shortfall_peak_V": float(shortfall.max()), "pfe_shortfall_integral_Vs": float(shortfall.sum() * dt),
        "pfe_excess_peak_V": float(excess.max()), "pfe_excess_integral_Vs": float(excess.sum() * dt),
        "pfe_time_at_upper_limit_s": float(np.sum(v >= v_tot_max_V - 1e-9) * dt),
        "pfe_time_at_zero_s": float(np.sum(v <= 1e-9) * dt),
    }
    if res.slew_limited is not None:
        out["pfe_time_slew_limited_s"] = float(np.sum(res.slew_limited) * dt)
    for x in dwell_fractions:       # time spent within (1 - x) of the cap, e.g. above 90% of it
        out[f"pfe_dwell_above_{round(100 * x)}pct_s"] = float(np.sum(v >= x * v_tot_max_V) * dt)
    i = res.i_sense_A
    out["pfe_i_max_over_set"] = float(np.nanmax(i) / i_set_A)
    for k in overcurrent_multiples:
        out[f"pfe_time_above_{k:g}x_set_s"] = float(np.sum(i > k * i_set_A) * dt)
    return out
