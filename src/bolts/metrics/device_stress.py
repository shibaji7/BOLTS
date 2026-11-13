# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Stress on a device: the heat in a repeater's Zener shunt, relative to normal running.

In normal running the shunt carries 10% of the line current (Chesnoy Table 10.1), so about 5.6 W at 56 V; a higher line current goes
through it. The ratio is computed by :func:`bolts.impact.optical.repeater_state`."""
from __future__ import annotations

import numpy as np

from ..config.schema import ParameterSet
from ..impact.optical import repeater_state


def zener_power_ratio(p: ParameterSet, i_line_A) -> np.ndarray:
    """Shunt heat relative to normal running (1 = nominal)."""
    return repeater_state(p, i_line_A)["zener_power_ratio"]


def zener_power_W(p: ParameterSet, i_line_A) -> np.ndarray:
    """Shunt heat in watts."""
    return repeater_state(p, i_line_A)["zener_power_W"]
