# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Element: air-core surge coil with DC resistance. In series it passes the DC feed current (dropping I R) and chokes fast transients (L di/dt)."""
from __future__ import annotations

from ..mna.stamp import Stamper
from .base import Element


class Coil(Element):
    """Series inductor ``l_H`` with winding resistance ``r_dc_ohm`` from ``a`` to ``b``; a branch, so its current is a result."""

    def __init__(self, name: str, a: str | None, b: str | None, l_H: float, r_dc_ohm: float = 0.0):
        if l_H <= 0 or r_dc_ohm < 0:
            raise ValueError("a coil needs a positive inductance and a non-negative DC resistance")
        self.name, self.a, self.b, self.l_H, self.r_dc_ohm = name, a, b, l_H, r_dc_ohm

    @property
    def nodes(self):
        """Names of the nodes this element connects."""
        return tuple(n for n in (self.a, self.b) if n)

    def stamp(self, st: Stamper) -> None:
        """Add the series branch (R and L) to the MNA system."""
        st.add_series_branch(self.name, self.a, self.b, self.r_dc_ohm, self.l_H)
