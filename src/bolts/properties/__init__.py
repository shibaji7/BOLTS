# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Cable property providers: how R, L, G and C along the route are known. A provider answers ``rlcg(x_km, ...)``; the wrappers compose."""
from .base import RLCG, PropertyProvider
from .constant import ConstantRLCG
from .depth_profile import DepthProfileRLCG
from .factory import provider_from_parameters
from .section_table import SectionTableRLCG
from .temperature_R import TemperatureRLCG

__all__ = [
    "RLCG",
    "ConstantRLCG",
    "DepthProfileRLCG",
    "PropertyProvider",
    "SectionTableRLCG",
    "TemperatureRLCG",
    "provider_from_parameters",
]
