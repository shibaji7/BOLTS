# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Unit conversions. Quantities in code carry their unit in the name (``r_ohm_per_km``); these helpers are the only place
where a prefix is converted."""
from __future__ import annotations

KM = 1.0e3          # m per km
UF = 1.0e-6         # F per microfarad
NF = 1.0e-9         # F per nanofarad
MH = 1.0e-3         # H per millihenry
MA = 1.0e-3         # A per milliampere
KV = 1.0e3          # V per kilovolt


def uF_per_km_to_F_per_m(c_uF_per_km: float) -> float:
    """Convert microfarad per kilometre to farad per metre."""
    return c_uF_per_km * UF / KM


def mH_per_km_to_H_per_m(l_mH_per_km: float) -> float:
    """Convert millihenry per kilometre to henry per metre."""
    return l_mH_per_km * MH / KM


def to_dB(ratio: float) -> float:
    """Power ratio to decibel (10 log10)."""
    import math
    return 10.0 * math.log10(ratio)
