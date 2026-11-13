# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Element: BU power-switching relay. Planned for v0.3; see ROADMAP.md. The slot exists so the module tree, the docs and the registry are complete."""
from __future__ import annotations

from ..errors import NotImplementedYet
from ..mna.stamp import Stamper
from .base import Element


class Relay(Element):
    """Placeholder for the Relay device/model of a later release; instantiating it is allowed, using it raises ``NotImplementedYet``."""

    def __init__(self, *args, **kwargs):
        raise NotImplementedYet("BU power-switching relay", "ROADMAP v0.3")

    def stamp(self, st: Stamper) -> None:   # pragma: no cover
        """Not implemented yet: raises ``NotImplementedYet`` naming the roadmap item."""
        raise NotImplementedYet("BU power-switching relay", "ROADMAP v0.3")
