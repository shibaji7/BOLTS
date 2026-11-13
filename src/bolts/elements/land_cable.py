# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Element: the land cable between the station and the beach joint. Electrically a cable span whose shunt capacitance goes to the station
earth (the same 0 V reference as the sea in this model); it is a separate class so land and sea sections can be told apart in results and
so land-only effects (lightning entry, induction from power lines, Chesnoy Sec. 10.3) have a place to attach in later versions."""
from __future__ import annotations

from .cable_segment import CableSegment


class LandCable(CableSegment):
    """A cable span on land: same R, L, C, G and optional EMF as :class:`~bolts.elements.cable_segment.CableSegment`."""
