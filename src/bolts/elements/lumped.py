# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Plain lumped elements (resistor, capacitor, inductor, ideal voltage source). Used by the validation cases and for quick
experiments; a real cable is built from :class:`~bolts.elements.cable_segment.CableSegment`."""
from __future__ import annotations

from ..mna.stamp import Source, Stamper
from .base import Element


class Resistor(Element):
    """Series resistor from ``a`` to ``b`` (either may be ``None`` for the sea). It is a branch, so its current is available as a result."""

    def __init__(self, name: str, a: str | None, b: str | None, r_ohm: float):
        self.name, self.a, self.b, self.r = name, a, b, r_ohm

    @property
    def nodes(self):
        """Names of the nodes this element connects."""
        return tuple(n for n in (self.a, self.b) if n)

    def stamp(self, st: Stamper) -> None:
        """Add this element's branch or conductance to the MNA system (called once when the matrix is assembled)."""
        st.add_series_branch(self.name, self.a, self.b, self.r)


class Capacitor(Element):
    """Shunt capacitor between two nodes."""

    def __init__(self, name: str, a: str | None, b: str | None, c_F: float):
        self.name, self.a, self.b, self.c = name, a, b, c_F

    @property
    def nodes(self):
        """Names of the nodes this element connects."""
        return tuple(n for n in (self.a, self.b) if n)

    def stamp(self, st: Stamper) -> None:
        """Add this element's branch or conductance to the MNA system (called once when the matrix is assembled)."""
        st.add_capacitance(self.a, self.b, self.c)


class Inductor(Element):
    """Series inductor; a branch with zero resistance, so its current is a state of the circuit."""

    def __init__(self, name: str, a: str | None, b: str | None, l_H: float):
        self.name, self.a, self.b, self.l = name, a, b, l_H

    @property
    def nodes(self):
        """Names of the nodes this element connects."""
        return tuple(n for n in (self.a, self.b) if n)

    def stamp(self, st: Stamper) -> None:
        """Add this element's branch or conductance to the MNA system (called once when the matrix is assembled)."""
        st.add_series_branch(self.name, self.a, self.b, 0.0, self.l)


class VSource(Element):
    """Ideal voltage source: v_b = v_a + s(t) (the potential rises by s in the direction of the current a -> b)."""

    def __init__(self, name: str, a: str | None, b: str | None, source: Source):
        self.name, self.a, self.b, self.source = name, a, b, source

    @property
    def nodes(self):
        """Names of the nodes this element connects."""
        return tuple(n for n in (self.a, self.b) if n)

    def stamp(self, st: Stamper) -> None:
        """Add this element's branch or conductance to the MNA system (called once when the matrix is assembled)."""
        st.add_series_branch(self.name, self.a, self.b, 0.0, 0.0, [self.source])
