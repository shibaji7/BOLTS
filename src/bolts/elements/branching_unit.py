# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Element: branching unit (sea earth, relays, powering states). Planned for v0.3; see ROADMAP.md. The slot exists so the module tree, the docs and the registry are complete."""
from __future__ import annotations

from ..errors import NotImplementedYet
from ..mna.stamp import Stamper
from .base import Element


class BranchingUnit(Element):
    """Placeholder for the BranchingUnit device/model of a later release; instantiating it is allowed, using it raises ``NotImplementedYet``."""

    def __init__(self, *args, **kwargs):
        raise NotImplementedYet("branching unit (sea earth, relays, powering states)", "ROADMAP v0.3")

    def stamp(self, st: Stamper) -> None:   # pragma: no cover
        """Not implemented yet: raises ``NotImplementedYet`` naming the roadmap item."""
        raise NotImplementedYet("branching unit (sea earth, relays, powering states)", "ROADMAP v0.3")
