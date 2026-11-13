# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""An earth electrode: a resistor from a node to the sea (ground)."""
from __future__ import annotations

from ..mna.stamp import Stamper
from .base import Element


class EarthElectrode(Element):
    """Resistance to the sea from one node (a station earth, a branching-unit earth). The sea is the 0 V reference, so this is a plain shunt."""

    def __init__(self, name: str, node: str, r_ohm: float):
        if r_ohm <= 0:
            raise ValueError("an electrode resistance must be positive")
        self.name, self.node, self.r_ohm = name, node, r_ohm

    @property
    def nodes(self):
        """Names of the nodes this element connects."""
        return (self.node,)

    def stamp(self, st: Stamper) -> None:
        """Add this element's branch or conductance to the MNA system (called once when the matrix is assembled)."""
        st.add_conductance(self.node, None, 1.0 / self.r_ohm)
