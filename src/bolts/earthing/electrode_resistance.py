# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Resistance of ground electrodes: Chesnoy Eqs. 10.3 and 10.4 (printed p. 388).

Single rod:       Rs = rho / (2 pi b) * (ln(4b / r) - 1)      b buried length, r radius.
n rods in a line: Rn = Rs / n * (1 + lambda rho / (2 pi Rs a)),  a = spacing; lambda = 2 (n=2), 1.66 (n=3), 2.15 (n=4).

NOTE on the source: the printed Eq. 10.4 reads ``Rn = Rs (1 + lambda rho / (2 pi Rs)) / n`` with no spacing ``a``, which is
dimensionally inconsistent (metres added to a number). The standard (Sunde) form with the spacing ``a`` in the denominator is used here;
the book's reference [5] should be checked."""
from __future__ import annotations

import math

LAMBDA = {2: 2.0, 3: 1.66, 4: 2.15}


def single_rod_ohm(rho_ohm_m: float, b_m: float, r_m: float) -> float:
    """Resistance of one buried rod of length ``b_m`` and radius ``r_m`` in soil of resistivity ``rho`` (Eq. 10.3)."""
    return rho_ohm_m / (2.0 * math.pi * b_m) * (math.log(4.0 * b_m / r_m) - 1.0)


def rods_in_line_ohm(rho_ohm_m: float, rs_ohm: float, a_m: float, n: int) -> float:
    """Resistance of ``n`` rods in a line, ``a_m`` apart, given one rod's resistance (Sunde form of Eq. 10.4; the rods shield each other)."""
    if n not in LAMBDA:
        raise ValueError(f"lambda is tabulated for n = 2, 3, 4 only (got {n})")
    return rs_ohm / n * (1.0 + LAMBDA[n] * rho_ohm_m / (2.0 * math.pi * rs_ohm * a_m))


def landing_resistance_from_parameters(params) -> float:
    """Resistance of the landing earth (ohm): from the rod electrode and the soil when ``earthing.soil_resistivity_ohm_m`` and the four ``earthing.rod_*`` parameters are all given
    (one rod, or ``rod_count`` rods in a line), otherwise the sourced upper bound ``earthing.landing_earth_resistance_ohm`` (Chesnoy p. 387: below 3 ohm)."""
    names = ("soil_resistivity_ohm_m", "rod_count", "rod_length_m", "rod_radius_m", "rod_spacing_m")
    if not all(params.has("earthing", n) for n in names):
        return float(params.get("earthing", "landing_earth_resistance_ohm"))
    rho, n = float(params.get("earthing", "soil_resistivity_ohm_m")), int(params.get("earthing", "rod_count"))
    rs = single_rod_ohm(rho, float(params.get("earthing", "rod_length_m")), float(params.get("earthing", "rod_radius_m")))
    return rs if n == 1 else rods_in_line_ohm(rho, rs, float(params.get("earthing", "rod_spacing_m")), n)
