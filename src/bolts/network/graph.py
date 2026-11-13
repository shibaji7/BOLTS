# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""A network is a list of elements; nodes are named by the elements that use them. ``compile()`` stamps everything and returns the
MNA system. Point-to-point is the simplest topology; branching units extend the same container (roadmap v0.3)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..elements.base import Element
from ..mna.assemble import System, assemble
from ..mna.stamp import Stamper
from .validate import check_connected


@dataclass
class Network:
    """A circuit as a list of elements plus the PFE regulator and some bookkeeping (``meta``) that the metrics use."""

    elements: list[Element] = field(default_factory=list)
    controller: Any = None                  # PowerFeedController or None (open loop)
    meta: dict = field(default_factory=dict)

    def add(self, element: Element) -> Element:
        """Append an element and return it (so the caller can keep a handle)."""
        self.elements.append(element)
        return element

    def node_names(self) -> list[str]:
        """Every node named by an element, in first-use order (a dict keeps the order and drops duplicates)."""
        seen: dict[str, None] = {}
        for el in self.elements:
            for n in el.nodes:
                seen.setdefault(n, None)
        return list(seen)

    def compile(self) -> System:
        """Stamp every element, check the circuit has no floating node, and assemble the MNA matrices."""
        st = Stamper(self.node_names())
        for el in self.elements:
            el.stamp(st)
        check_connected(st)
        return assemble(st)
