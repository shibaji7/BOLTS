# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Soil resistivity from a four-terminal (Wenner) measurement: Chesnoy Eq. 10.2 (printed p. 387).

    rho = 4 pi a R / (1 + 2a / sqrt(a^2 + 4 b^2) - 2a / sqrt(4 a^2 + 4 b^2))

``a`` is the spacing of the electrodes, ``b`` the buried length of the electrodes and ``R`` = V/I the measured resistance. For b -> 0 it
reduces to rho = 2 pi a R."""
from __future__ import annotations

import math


def wenner_resistivity_ohm_m(a_m: float, b_m: float, r_ohm: float) -> float:
    """Soil resistivity (ohm m) from a four-terminal measurement of spacing ``a_m``, electrode length ``b_m`` and resistance ``r_ohm``."""
    denom = 1.0 + 2.0 * a_m / math.sqrt(a_m ** 2 + 4.0 * b_m ** 2) - 2.0 * a_m / math.sqrt(4.0 * a_m ** 2 + 4.0 * b_m ** 2)
    return 4.0 * math.pi * a_m * r_ohm / denom
