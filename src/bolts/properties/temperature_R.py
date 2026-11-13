# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Temperature-dependent conductor resistance: a wrapper around any other provider.

    R(T) = R_ref (1 + alpha (T - T_ref))        copper: alpha about 0.0039 per K

The wrapped provider's R is taken to be the value at the reference temperature ``t_ref_C``. Cold seabed water makes the copper conductor
about 6% less resistive than at 20 C, which lowers the static voltage the PFEs must supply. Wrapping is opt-in, so the default
(constant) behaviour and the pfe_design regression do not change."""
from __future__ import annotations

from dataclasses import dataclass, replace

from .base import RLCG, PropertyProvider


@dataclass(frozen=True)
class TemperatureRLCG:
    """``base`` gives R at ``t_ref_C``; this provider rescales it to the temperature passed to :meth:`rlcg`."""

    base: PropertyProvider
    alpha_per_K: float = 0.00393
    t_ref_C: float = 20.0

    def rlcg(self, x_km: float, depth_m: float = 0.0, temperature_C: float = 4.0, f_Hz: float = 0.0) -> RLCG:
        """The base values with R scaled by ``1 + alpha (T - T_ref)``."""
        v = self.base.rlcg(x_km, depth_m, temperature_C, f_Hz)
        factor = 1.0 + self.alpha_per_K * (temperature_C - self.t_ref_C)
        if factor <= 0.0:
            raise ValueError("temperature is below the range where the linear resistance law applies")
        return replace(v, r_ohm_per_km=v.r_ohm_per_km * factor)
