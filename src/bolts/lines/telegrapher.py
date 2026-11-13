# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Telegrapher's equations for a uniform line with per-length R, L, G, C (the cable seen as a transmission line).

    Z0 = sqrt((R + j w L) / (G + j w C)),   gamma = sqrt((R + j w L)(G + j w C)),   lossless delay = length sqrt(L C)

Per-length values in SI: ohm/m, H/m, S/m, F/m. At GMD frequencies the cable is diffusive (RC, L negligible); at lightning
frequencies L matters and the line propagates waves (a 750 km cable has roughly 4 ms of one-way delay for L' C' of a coaxial cable)."""
from __future__ import annotations

import cmath
import math


def characteristic_impedance_ohm(r_ohm_per_m: float, l_H_per_m: float, g_S_per_m: float, c_F_per_m: float, f_Hz: float) -> complex:
    """Characteristic impedance Z0 of a uniform line at frequency ``f_Hz`` (complex, ohm)."""
    w = 2.0 * math.pi * f_Hz
    return cmath.sqrt((r_ohm_per_m + 1j * w * l_H_per_m) / (g_S_per_m + 1j * w * c_F_per_m))


def propagation_constant_per_m(r_ohm_per_m: float, l_H_per_m: float, g_S_per_m: float, c_F_per_m: float, f_Hz: float) -> complex:
    """Propagation constant gamma = alpha + j beta (1/m): attenuation and phase per metre."""
    w = 2.0 * math.pi * f_Hz
    return cmath.sqrt((r_ohm_per_m + 1j * w * l_H_per_m) * (g_S_per_m + 1j * w * c_F_per_m))


def lossless_delay_s(length_m: float, l_H_per_m: float, c_F_per_m: float) -> float:
    """One-way propagation delay of a lossless line: length sqrt(L C)."""
    return length_m * math.sqrt(l_H_per_m * c_F_per_m)
