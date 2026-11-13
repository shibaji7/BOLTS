# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Energy dissipated in a device from its power series (trapezoid rule)."""
from __future__ import annotations

import numpy as np


def energy_J(power_W: np.ndarray, t_s: np.ndarray) -> float:
    """Joules: the area under the power curve."""
    return float(np.trapezoid(power_W, t_s))
