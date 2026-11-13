# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Cable per-length properties. A *provider* answers ``rlcg(x_km, ...)``, so how R, L, G and C are known (constant, a section
table from the cable design, depth or temperature dependent, frequency dependent) never changes the solver."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class RLCG:
    """Per-kilometre cable parameters at one place: R (ohm/km), C (F/km), G (S/km), L (H/km)."""
    r_ohm_per_km: float
    c_F_per_km: float
    g_S_per_km: float = 0.0
    l_H_per_km: float = 0.0
    inductance_known: bool = False          # False: l_H_per_km is a placeholder 0 (slow GMD runs do not need it)


class PropertyProvider(Protocol):
    """Anything that can answer :meth:`rlcg`; the cable builder only depends on this."""

    def rlcg(self, x_km: float, depth_m: float = 0.0, temperature_C: float = 4.0, f_Hz: float = 0.0) -> RLCG:
        """R, L, G, C at chainage ``x_km`` (and, for the later providers, depth, temperature and frequency)."""
        ...
