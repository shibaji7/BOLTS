# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""A repeater in the power-feed line: the Zener stack (and, later, the surge chain) between its input and output nodes.

    in o--[ Zener: Vz + rz dI ]--o out          the line current passes through every repeater; the pump laser and the control circuit
                                               are fed from this stack, so their light output is a function of the line current
                                               (see bolts.impact.optical).
"""
from __future__ import annotations

from ..mna.stamp import ConstantSource, Stamper
from .base import Element
from .zener import LinearZener, PiecewiseZener


class Repeater(Element):
    """The line sees a repeater as a nearly constant voltage drop (its Zener stack) with a small dynamic resistance; everything the repeater
    does optically is derived afterwards from the current through this branch."""

    def __init__(self, name: str, a: str, b: str, zener: LinearZener | PiecewiseZener):
        self.name, self.a, self.b, self.zener = name, a, b, zener

    @property
    def nodes(self):
        """Names of the nodes this element connects."""
        return (self.a, self.b)

    def stamp(self, st: Stamper) -> None:
        """Add this element's branch or conductance to the MNA system (called once when the matrix is assembled)."""
        if getattr(self.zener, "is_nonlinear", False):      # a piecewise Zener: the Newton iteration supplies its companion model at each step
            st.add_nonlinear_branch(self.name, self.a, self.b, self.zener)
            return
        r, src = self.zener.series_parameters()      # equivalent series R and constant source of the linear Zener
        st.add_series_branch(self.name, self.a, self.b, r, 0.0, [ConstantSource(src)])
