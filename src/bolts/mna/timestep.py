# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Time axis of a run. v0.1 uses a fixed step; adaptive stepping is planned (roadmap v0.3)."""
from __future__ import annotations

import numpy as np

from ..errors import NotImplementedYet


def fixed_axis(duration_s: float, dt_s: float, t0_s: float = 0.0) -> np.ndarray:
    """Uniform axis ``t0, t0+dt, ..., t0+duration`` (both end points included)."""
    if dt_s <= 0 or duration_s <= 0:
        raise ValueError("dt_s and duration_s must be positive")
    n = round(duration_s / dt_s) + 1
    return t0_s + dt_s * np.arange(n)


def adaptive_axis(*args, **kwargs):
    """Placeholder for a step that shrinks around fast events (needed before lightning-scale pulses)."""
    raise NotImplementedYet("adaptive time stepping", "ROADMAP v0.3")
