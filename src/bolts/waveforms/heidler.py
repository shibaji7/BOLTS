# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Heidler function for lightning return-stroke currents:
    i(t) = I0 / eta * (t/tau1)^n / (1 + (t/tau1)^n) * exp(-t/tau2),   eta = exp(-(tau1/tau2) (n tau2/tau1)^(1/n)).
The factor eta makes the peak equal to ``peak``. Typical n = 10 (Heidler, Cvetic and Stanic)."""
from __future__ import annotations

import math

import numpy as np

from .base import Record


def heidler(peak_A: float, tau1_s: float, tau2_s: float, n: float = 10.0, duration_s: float = 1e-3, dt_s: float = 1e-7) -> Record:
    """Sample the Heidler current (A). ``tau1`` sets the rise (about 1.2 x tau1 to peak for n = 10), ``tau2`` the decay; steepness ``n`` > 1."""
    # eta rescales so the maximum equals `peak` (the bare function peaks below I0)
    eta = math.exp(-(tau1_s / tau2_s) * (n * tau2_s / tau1_s) ** (1.0 / n))
    t = np.arange(0.0, duration_s + 0.5 * dt_s, dt_s)
    x = (t / tau1_s) ** n              # the rising-front factor x/(1+x) rises from 0 to 1 around t = tau1
    return Record(t, peak_A / eta * x / (1.0 + x) * np.exp(-t / tau2_s), f"Heidler {peak_A:g} A", "A")
