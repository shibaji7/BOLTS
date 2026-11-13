# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""How the PFEs share the feed: double-end (each end supplies a share, with opposite signs) or single-end (one PFE failed)."""
from __future__ import annotations

from enum import StrEnum


class PowerMode(StrEnum):
    """Placeholder for the PowerMode device/model of a later release; instantiating it is allowed, using it raises ``NotImplementedYet``."""
    DOUBLE_END = "double_end"
    SINGLE_END_A = "single_end_A"
    SINGLE_END_B = "single_end_B"


def end_weights(mode: PowerMode, split_fraction_A: float = 0.5) -> tuple[float, float]:
    """Source weights (A, B) as multiples of v_tot: A drives +w_A v_tot, B drives w_B v_tot (negative, so the ends are opposite)."""
    if mode is PowerMode.DOUBLE_END:
        return split_fraction_A, -(1.0 - split_fraction_A)
    if mode is PowerMode.SINGLE_END_A:
        return 1.0, 0.0
    return 0.0, -1.0


def max_total_voltage_V(mode: PowerMode, v_max_end_V: float, split_fraction_A: float = 0.5) -> float:
    """Largest v_tot the PFEs can supply together before one of them reaches its own limit."""
    if mode is PowerMode.DOUBLE_END:
        f = split_fraction_A
        return min(v_max_end_V / f, v_max_end_V / (1.0 - f)) if 0.0 < f < 1.0 else v_max_end_V
    return v_max_end_V
