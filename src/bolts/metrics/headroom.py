# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""PFE voltage headroom: how much more voltage the PFEs can still supply, and how often they sit at a limit."""
from __future__ import annotations

import numpy as np

from ..mna.transient import TransientResult


def headroom_V(res: TransientResult, v_tot_max_V: float) -> np.ndarray:
    """Voltage still available at each step; zero means the PFE sits at its limit."""
    return v_tot_max_V - res.v_tot_V


def pfe_metrics(res: TransientResult, v_tot_max_V: float, static_need_V: float) -> dict:
    """PFE voltage range, minimum headroom and the fraction of steps spent clamped (where the current is no longer regulated)."""
    return {"static_need_V": static_need_V, "v_tot_max_V": v_tot_max_V, "v_pfe_min_V": float(np.nanmin(res.v_tot_V)),
            "v_pfe_max_V": float(np.nanmax(res.v_tot_V)), "min_headroom_V": float(np.nanmin(headroom_V(res, v_tot_max_V))),
            "frac_pfe_clamped": float(res.clamped.mean()), "r_loop_ohm": float(res.r_loop_ohm)}
