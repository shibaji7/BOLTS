# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Ground potential rise (GPR): the potential an earth electrode reaches against remote earth when it carries a current, GPR = I R.

Chesnoy Sec. 10.2.4 (p. 387) recommends that the nominal voltage between the system earth and the station earth stays below 20 V, with an exceptional rise to
90 V in a lightning environment, and that the earth electrodes stay below about 3 ohm. The electrode of a PFE carries the line current, so a storm that moves the
current moves the potential of the electrode; a poor soil (high resistivity) makes the same current a larger potential. This module turns a current record into
the GPR and compares it with those two limits. The system-earth to station-earth *difference* is bounded by the larger of the two electrodes' GPR, which is what
is reported (an upper bound; the electrodes' mutual coupling is not modelled)."""
from __future__ import annotations

import numpy as np


def ground_potential_rise_V(i_A, r_ohm: float):
    """Potential of an electrode above remote earth when it carries ``i_A`` (V; scalar or array)."""
    return np.asarray(i_A, float) * r_ohm if np.ndim(i_A) else i_A * r_ohm


def required_resistance_ohm(i_A: float, v_limit_V: float) -> float:
    """Largest electrode resistance that keeps the GPR at or below ``v_limit_V`` when the electrode carries ``i_A`` (ohm)."""
    if i_A <= 0 or v_limit_V <= 0:
        raise ValueError("current and voltage limit must be positive")
    return v_limit_V / i_A


def gpr_metrics(i_A, r_ohm: float, dt_s: float, v_nominal_V: float = 20.0, v_exceptional_V: float = 90.0) -> dict:
    """Peak GPR and the time above the nominal and the exceptional limits for a current record on a fixed step."""
    g = np.abs(np.asarray(i_A, float)) * r_ohm
    return {"earth_gpr_peak_V": float(g.max()), "earth_time_above_nominal_s": float(np.sum(g > v_nominal_V) * dt_s),
            "earth_time_above_exceptional_s": float(np.sum(g > v_exceptional_V) * dt_s)}
