# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""A sampled waveform: time (s) and values (V for voltages, A for currents). Everything that drives a network is a Record."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Record:
    """Immutable sampled waveform. Between samples it is taken to vary linearly; every transformation returns a new Record."""

    t_s: np.ndarray
    values: np.ndarray
    label: str = ""
    unit: str = "V"

    def __post_init__(self):
        # validate once here so every consumer can rely on a clean, strictly increasing time axis
        t = np.asarray(self.t_s, float)
        v = np.asarray(self.values, float)
        if t.shape != v.shape or t.ndim != 1 or len(t) < 2:
            raise ValueError("t_s and values must be 1-D arrays of the same length (>= 2)")
        if np.any(np.diff(t) <= 0):
            raise ValueError("t_s must be strictly increasing")
        object.__setattr__(self, "t_s", t)      # frozen dataclass: store the converted arrays
        object.__setattr__(self, "values", v)

    # ---- properties --------------------------------------------------------------------------------------------
    @property
    def dt_s(self) -> float:
        """Median spacing of the samples."""
        return float(np.median(np.diff(self.t_s)))

    @property
    def duration_s(self) -> float:
        """Time from the first to the last sample."""
        return float(self.t_s[-1] - self.t_s[0])

    @property
    def rate_per_s(self) -> np.ndarray:
        """d(value)/dt on each interval (the waveform is taken to move linearly between samples)."""
        return np.diff(self.values) / np.diff(self.t_s)

    # ---- transformations (each returns a new Record) -------------------------------------------------------------
    def scaled(self, k: float) -> Record:
        """Values multiplied by ``k`` (e.g. a stronger storm)."""
        return Record(self.t_s, self.values * k, f"{self.label} x{k:g}", self.unit)

    def compressed(self, k: float) -> Record:
        """The same waveform k times faster (time axis divided by k)."""
        return Record(self.t_s / k, self.values, f"{self.label} rate x{k:g}", self.unit)

    def resampled(self, dt_s: float) -> Record:
        """The record on a uniform grid of step ``dt_s`` (linear interpolation)."""
        t = np.arange(self.t_s[0], self.t_s[-1] + 0.5 * dt_s, dt_s)
        t = t[t <= self.t_s[-1] + 1e-12]      # arange can overshoot the end by one step; trim it
        return Record(t, np.interp(t, self.t_s, self.values), self.label, self.unit)

    def sample(self, t_s) -> np.ndarray:
        """Linear interpolation at arbitrary times (held at the end values outside the record)."""
        return np.interp(np.asarray(t_s, float), self.t_s, self.values)
