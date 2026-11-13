# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""How many lumped sections a cable needs. A lumped section is accurate for signals whose rise time is much longer than the delay across
the section, so the number of sections follows the fastest feature of the drive: ``n >= total_delay / (rise_time / per_rise)``."""
from __future__ import annotations

import math

from .telegrapher import lossless_delay_s


def sections_for_rise_time(length_km: float, l_H_per_km: float, c_F_per_km: float, t_rise_s: float, per_rise: float = 10.0) -> int:
    """Smallest number of sections so that each section's delay is at most ``t_rise / per_rise`` (at least one section)."""
    if t_rise_s <= 0:
        raise ValueError("t_rise_s must be positive")
    delay = lossless_delay_s(length_km * 1e3, l_H_per_km * 1e-3, c_F_per_km * 1e-3)
    return max(1, math.ceil(delay / (t_rise_s / per_rise)))
