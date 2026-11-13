# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Element: the beach joint box between the land cable and the submarine cable: a contact resistance in series and a small capacitance to
earth. ``withstand_V`` records the voltage it must withstand, for the insulation-life checks planned in ``bolts.damage``."""
from __future__ import annotations

from ..mna.stamp import Stamper
from .base import Element


class BeachJoint(Element):
    """Series resistance ``r_ohm`` from ``a`` to ``b`` with ``c_F`` of capacitance to the sea split between its two sides."""

    def __init__(self, name: str, a: str, b: str, r_ohm: float = 0.0, c_F: float = 0.0, withstand_V: float | None = None):
        if r_ohm < 0 or c_F < 0:
            raise ValueError("a beach joint needs non-negative resistance and capacitance")
        self.name, self.a, self.b, self.r_ohm, self.c_F, self.withstand_V = name, a, b, r_ohm, c_F, withstand_V

    @property
    def nodes(self):
        """Names of the nodes this element connects."""
        return (self.a, self.b)

    def stamp(self, st: Stamper) -> None:
        """Add the series resistance and the shunt capacitance (half at each side) to the MNA system."""
        st.add_series_branch(self.name, self.a, self.b, self.r_ohm)
        if self.c_F > 0:
            for node in (self.a, self.b):
                st.add_capacitance(node, None, 0.5 * self.c_F)
