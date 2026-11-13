# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""The line current at the repeaters and how far it falls below the nominal: the quantity that starves the pump lasers."""
from __future__ import annotations

import numpy as np

from ..mna.transient import TransientResult


def repeater_currents_A(res: TransientResult, repeater_branches: list[str]) -> np.ndarray:
    """(nt, n_repeaters) current through each repeater."""
    return np.column_stack([res.branch_I(b) for b in repeater_branches])


def dip_metrics(delta_A: np.ndarray, margin_A: float) -> dict:
    """Largest fall and rise of the repeater current from the set point, and how often the fall exceeds the margin."""
    # at each instant the worst repeater is the one with the lowest current; the optics follow that one
    worst_down = delta_A.min(axis=1)
    return {"di_min_mA": 1e3 * float(delta_A.min()), "di_max_mA": 1e3 * float(delta_A.max()),
            "worst_repeater": int(np.argmin(delta_A.min(axis=0))) + 1, "margin_mA": 1e3 * margin_A,
            "frac_time_below_margin": float(np.mean(worst_down < -margin_A))}
