# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Property provider: named cable types from a catalogue. Planned for v0.5; see ROADMAP.md."""
from __future__ import annotations

from ..errors import NotImplementedYet
from .base import RLCG


class Provider:
    """Placeholder for the Provider device/model of a later release; instantiating it is allowed, using it raises ``NotImplementedYet``."""

    def __init__(self, *args, **kwargs):
        raise NotImplementedYet("named cable types from a catalogue", "ROADMAP v0.5")

    def rlcg(self, x_km: float, depth_m: float = 0.0, temperature_C: float = 4.0, f_Hz: float = 0.0) -> RLCG:   # pragma: no cover
        """Not implemented yet: raises ``NotImplementedYet`` naming the roadmap item."""
        raise NotImplementedYet("named cable types from a catalogue", "ROADMAP v0.5")
