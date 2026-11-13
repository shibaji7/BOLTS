# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Pump laser: light output against drive current. Below the threshold current there is no light; above it the output rises linearly (the slope efficiency)
up to the nominal drive, where the repeater's output power is the design value. The repeater is a saturated amplifier, so its output power follows
the pump power (Chesnoy p. 428) and the OSNR changes by ``10 log10(ratio)``.

    ratio = clip((I - I_th) / (I_nom - I_th), 0, 1)        I_th = threshold_fraction * I_nom

``threshold_fraction`` is the unknown ``optical.laser_threshold_fraction`` (swept 0, 0.2, 0.4 in the studies). ``slope_W_per_A`` is optional: without it only the
ratio is available, which is all the optical chain needs. The constant-current driver that holds the pump current while the line current falls is a property of
the repeater (:func:`bolts.impact.optical.repeater_state`), not of the laser."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class PumpLaser:
    """Threshold-and-slope laser model."""

    i_nominal_A: float
    threshold_fraction: float = 0.0
    slope_W_per_A: float | None = None

    def __post_init__(self):
        if self.i_nominal_A <= 0 or not 0.0 <= self.threshold_fraction < 1.0:
            raise ValueError("a pump laser needs a positive nominal current and a threshold fraction in [0, 1)")

    @property
    def threshold_A(self) -> float:
        """Threshold current: no light below it."""
        return self.threshold_fraction * self.i_nominal_A

    def power_ratio(self, i_drive_A):
        """Output power relative to nominal for a drive current (A, scalar or array), between 0 and 1."""
        i = np.asarray(i_drive_A, float)
        return np.clip((i - self.threshold_A) / (self.i_nominal_A - self.threshold_A), 0.0, 1.0)

    def optical_power_W(self, i_drive_A):
        """Absolute output (W) above threshold for a drive current; needs ``slope_W_per_A``."""
        if self.slope_W_per_A is None:
            raise ValueError("slope_W_per_A was not given")
        return self.slope_W_per_A * np.maximum(np.asarray(i_drive_A, float) - self.threshold_A, 0.0)
