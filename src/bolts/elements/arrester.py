# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Element: surge arrester (a varistor or gas-tube stand-in): conducts above its clamp voltage, in both directions, with a small on-resistance.
It uses the piecewise-linear clamp law of :mod:`bolts.elements.diode_chain`; a gas tube's arc-voltage collapse and hold-over are not modelled (roadmap v0.3)."""
from __future__ import annotations

from .diode_chain import ClampShunt


class Arrester(ClampShunt):
    """Bidirectional clamp with the clamp voltage given directly (``v_clamp_V``), ``r_on_ohm`` once conducting and an optional energy rating ``energy_J``."""

    def __init__(self, name: str, a: str | None, b: str | None, v_clamp_V: float, r_on_ohm: float = 1.0, g_off_S: float = 0.0,
                 i_withstand_A: float | None = None, energy_rating_J: float | None = None):
        super().__init__(name, a, b, v_clamp_V, r_on_ohm, g_off_S, True, i_withstand_A)
        self.energy_rating_J = energy_rating_J
