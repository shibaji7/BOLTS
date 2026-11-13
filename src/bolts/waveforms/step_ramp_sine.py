# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Elementary test waveforms: step, ramp, sine, and a ramp that is then held."""
from __future__ import annotations

import numpy as np

from .base import Record


def _axis(duration_s: float, dt_s: float) -> np.ndarray:
    """0 to ``duration_s`` inclusive; the half-step padding stops arange from dropping the last point to round-off."""
    return np.arange(0.0, duration_s + 0.5 * dt_s, dt_s)


def step(amp_V: float, duration_s: float = 600.0, dt_s: float = 1.0, t_step_s: float = 60.0) -> Record:
    """Zero until ``t_step_s``, then ``amp_V``. Sampled, so the jump occupies one step (a ramp of width ``dt_s``)."""
    t = _axis(duration_s, dt_s)
    return Record(t, np.where(t >= t_step_s, amp_V, 0.0), f"step {amp_V:g} V")


def ramp(rate_V_per_s: float, duration_s: float = 600.0, dt_s: float = 1.0) -> Record:
    """Linear rise at a constant slope; the textbook input for the regulator's tracking error ``tau * rate / R_loop``."""
    t = _axis(duration_s, dt_s)
    return Record(t, rate_V_per_s * t, f"ramp {rate_V_per_s:g} V/s")


def sine(amp_V: float, freq_Hz: float, duration_s: float = 3600.0, dt_s: float = 1.0) -> Record:
    """A pure sinusoid: a test signal for the regulator's frequency response. Real ULF pulsations are random, not pure tones."""
    t = _axis(duration_s, dt_s)
    return Record(t, amp_V * np.sin(2.0 * np.pi * freq_Hz * t), f"sine {amp_V:g} V {freq_Hz:g} Hz")


def ramp_hold(amp_V: float, ramp_s: float, hold_s: float, dt_s: float) -> Record:
    """Linear rise to ``amp_V`` over ``ramp_s``, then constant for ``hold_s`` (a storm-phase change of chosen rate)."""
    t = _axis(ramp_s + hold_s, dt_s)
    return Record(t, amp_V * np.clip(t / ramp_s, 0.0, 1.0), f"ramp to {amp_V:g} V")
