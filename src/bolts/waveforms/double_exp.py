# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Double-exponential pulse i(t) = I0 (exp(-t/tau_fall) - exp(-t/tau_rise)) / k, normalised so that the peak equals ``peak``.
The classic surge shape (lightning currents, switching surges); ``tau_rise`` < ``tau_fall``."""
from __future__ import annotations

import math

import numpy as np

from .base import Record


def double_exponential(peak: float, tau_rise_s: float, tau_fall_s: float, duration_s: float, dt_s: float,
                       unit: str = "A") -> Record:
    """Sample the pulse on a uniform grid of step ``dt_s``; ``peak`` is the maximum value (in ``unit``)."""
    if not 0 < tau_rise_s < tau_fall_s:
        raise ValueError("need 0 < tau_rise_s < tau_fall_s")
    # time of the maximum, found by setting the derivative to zero, then the value there, so the normalised peak is exactly `peak`
    t_pk = tau_rise_s * tau_fall_s / (tau_fall_s - tau_rise_s) * math.log(tau_fall_s / tau_rise_s)
    k = math.exp(-t_pk / tau_fall_s) - math.exp(-t_pk / tau_rise_s)
    t = np.arange(0.0, duration_s + 0.5 * dt_s, dt_s)
    return Record(t, peak / k * (np.exp(-t / tau_fall_s) - np.exp(-t / tau_rise_s)),
                  f"double exponential {peak:g} {unit}", unit)
