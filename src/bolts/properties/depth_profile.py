# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Depth along the route, and the temperature that goes with it: a wrapper that tells another provider where it is.

The route's water depth is a table (chainage, depth). An optional second table (depth, seabed temperature) gives the temperature for that
depth; without it the temperature passed by the caller is used. The wrapped provider (for example :class:`TemperatureRLCG`) then answers for that depth
and temperature, so shallow warm water and the cold deep sea get different conductor resistance."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..errors import ConfigError
from .base import RLCG, PropertyProvider


@dataclass(frozen=True)
class DepthProfileRLCG:
    """``base`` is asked for the properties at the interpolated depth (and temperature) of each chainage."""

    base: PropertyProvider
    x_km: np.ndarray
    depth_m: np.ndarray
    depth_table_m: np.ndarray | None = None
    temperature_table_C: np.ndarray | None = None

    def __post_init__(self):
        if len(self.x_km) != len(self.depth_m) or len(self.x_km) < 2 or np.any(np.diff(self.x_km) <= 0):
            raise ConfigError("a depth profile needs matching, increasing chainage and depth arrays (at least two points)")
        if (self.depth_table_m is None) != (self.temperature_table_C is None):
            raise ConfigError("give both depth_table_m and temperature_table_C, or neither")
        if self.depth_table_m is not None and (len(self.depth_table_m) != len(self.temperature_table_C) or np.any(np.diff(self.depth_table_m) <= 0)):
            raise ConfigError("the temperature table needs increasing depths and one temperature per depth")

    def depth_at(self, x_km: float) -> float:
        """Water depth at a chainage, linear between the table points (held constant beyond the ends)."""
        return float(np.interp(x_km, self.x_km, self.depth_m))

    def rlcg(self, x_km: float, depth_m: float = 0.0, temperature_C: float = 4.0, f_Hz: float = 0.0) -> RLCG:
        """The wrapped provider's answer at this chainage's depth and (if a table is given) the temperature of that depth."""
        d = self.depth_at(x_km)
        t = float(np.interp(d, self.depth_table_m, self.temperature_table_C)) if self.depth_table_m is not None else temperature_C
        return self.base.rlcg(x_km, d, t, f_Hz)
