# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Constant per-km R, C, G (L only if known): the v0.1 provider."""
from __future__ import annotations

from dataclasses import dataclass

from ..config.schema import ParameterSet
from ..units import mH_per_km_to_H_per_m, uF_per_km_to_F_per_m
from .base import RLCG


@dataclass(frozen=True)
class ConstantRLCG:
    """Provider that returns one fixed :class:`RLCG` for the whole route."""
    value: RLCG

    def rlcg(self, x_km: float, depth_m: float = 0.0, temperature_C: float = 4.0, f_Hz: float = 0.0) -> RLCG:
        """The same value everywhere: position, depth, temperature and frequency are ignored in v0.1."""
        return self.value

    @classmethod
    def from_parameters(cls, params: ParameterSet) -> ConstantRLCG:
        """Build from the ``[cable]`` parameters; per-km units are converted once here. An unknown inductance leaves L at 0 and flags it."""
        has_l = params.has("cable", "inductance_mH_per_km")
        l_h_per_km = mH_per_km_to_H_per_m(float(params.get("cable", "inductance_mH_per_km"))) * 1e3 if has_l else 0.0
        return cls(RLCG(float(params.get("cable", "resistance_ohm_per_km")),
                        uF_per_km_to_F_per_m(float(params.get("cable", "capacitance_uF_per_km"))) * 1e3,
                        float(params.get("cable", "leakage_S_per_km")), l_h_per_km, has_l))
