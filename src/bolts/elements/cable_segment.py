# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""A cable span: series R (and L) with the geoelectric EMF as a source, shunt C and G to the local sea split between its two ends.

    a o--[ R, L, e(t) ]--o b           C and G to the sea: half at node a, half at node b
"""
from __future__ import annotations

from ..mna.stamp import Source, Stamper
from .base import Element


class CableSegment(Element):
    """One span of cable. Per-length values are multiplied by ``length_km`` once, here, so the solver only sees lumped totals.

    The EMF source is the span's share of the induced voltage (the sea-earth potentials at its ends are already inside the net record);
    splitting C and G half-and-half between the two ends is the usual pi section and is second-order accurate in the span length."""

    def __init__(self, name: str, a: str, b: str, length_km: float, r_ohm_per_km: float, c_F_per_km: float,
                 g_S_per_km: float = 0.0, l_H_per_km: float = 0.0, emf: Source | None = None):
        self.name, self.a, self.b = name, a, b
        self.length_km = length_km
        self.r_ohm = r_ohm_per_km * length_km      # total series resistance of the span
        self.l_H = l_H_per_km * length_km
        self.c_F = c_F_per_km * length_km
        self.g_S = g_S_per_km * length_km
        self.emf = emf

    @property
    def nodes(self):
        """Names of the nodes this element connects."""
        return (self.a, self.b)

    def stamp(self, st: Stamper) -> None:
        # the series branch carries the line current and the EMF that drives it
        """Add this element's branch or conductance to the MNA system (called once when the matrix is assembled)."""
        st.add_series_branch(self.name, self.a, self.b, self.r_ohm, self.l_H, [self.emf] if self.emf is not None else [])
        # shunt capacitance and leakage to the sea: pi section, half at each end
        for node in (self.a, self.b):
            st.add_capacitance(node, None, 0.5 * self.c_F)
            st.add_conductance(node, None, 0.5 * self.g_S)
