# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Element: the PFE output L-C filter. A series inductor (with winding resistance) from the converter node ``a`` to the line node ``b`` and a
shunt capacitor from ``b`` to the sea: a second-order low-pass with natural frequency f0 = 1 / (2 pi sqrt(L C)).

Its values are unknown (``pfe.output_filter_L_mH`` and ``pfe.output_filter_C_uF`` are TBD), so the standard network builder does not insert it
yet; wire it in by hand or through a custom builder once vendor data exist. It matters for fast surges, not for the slow GMD runs."""
from __future__ import annotations

import math

from ..mna.stamp import Stamper
from .base import Element


class PfeFilter(Element):
    """Series ``l_H`` (with ``r_ohm``) from ``a`` to ``b``; ``c_F`` from ``b`` to the sea."""

    def __init__(self, name: str, a: str, b: str, l_H: float, c_F: float, r_ohm: float = 0.0):
        if l_H <= 0 or c_F <= 0 or r_ohm < 0:
            raise ValueError("a filter needs positive L and C and a non-negative series resistance")
        self.name, self.a, self.b, self.l_H, self.c_F, self.r_ohm = name, a, b, l_H, c_F, r_ohm

    @property
    def nodes(self):
        """Names of the nodes this element connects."""
        return (self.a, self.b)

    @property
    def natural_frequency_Hz(self) -> float:
        """Undamped resonance of the L-C pair."""
        return 1.0 / (2.0 * math.pi * math.sqrt(self.l_H * self.c_F))

    def stamp(self, st: Stamper) -> None:
        """Add the series branch and the shunt capacitor to the MNA system."""
        st.add_series_branch(self.name, self.a, self.b, self.r_ohm, self.l_H)
        st.add_capacitance(self.b, None, self.c_F)
