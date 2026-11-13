# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""One power feed equipment (PFE) terminal: a controlled voltage source behind the landing earth resistance.

    gnd o--[ R_earth, +/- weight * v_tot ]--o node        the current runs from the sea through the earth electrode into the cable

``weight`` is +f for the A end and -(1-f) for the B end (equal and opposite voltages for the 50/50 split); the regulator
(:class:`~bolts.elements.pfe_regulator.PowerFeedController`) sets v_tot. A failed PFE has weight 0 but keeps its earth path.
"""
from __future__ import annotations

from ..mna.stamp import ControlledSource, Stamper
from .base import Element


class PFE(Element):
    """The branch runs from the sea (``None``) to the cable node, so a positive current flows from the sea, through the electrode, into the cable.
    The voltage source is a :class:`~bolts.mna.stamp.ControlledSource`; the transient loop, not this class, sets its value each step."""

    def __init__(self, name: str, node: str, r_earth_ohm: float, weight: float):
        self.name, self.node, self.r_earth_ohm = name, node, r_earth_ohm
        self.source = ControlledSource(weight=weight)

    @property
    def nodes(self):
        """Names of the nodes this element connects."""
        return (self.node,)

    def stamp(self, st: Stamper) -> None:
        """Add this element's branch or conductance to the MNA system (called once when the matrix is assembled)."""
        st.add_series_branch(self.name, None, self.node, self.r_earth_ohm, 0.0, [self.source])
