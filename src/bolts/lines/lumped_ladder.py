# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""A uniform cable as a ladder of identical lumped sections (the point-to-point builder already does this, one section per repeater span).
This module gives the section lengths for a chosen number of sections, for studies that need a finer ladder than the repeater spacing."""
from __future__ import annotations

import numpy as np


def section_lengths_km(length_km: float, n_sections: int) -> np.ndarray:
    """Equal section lengths for a ladder of ``n_sections`` over ``length_km``."""
    if n_sections < 1:
        raise ValueError("need at least one section")
    return np.full(n_sections, length_km / n_sections)


def section_edges_km(length_km: float, n_sections: int) -> np.ndarray:
    """Positions of the section boundaries, from 0 to ``length_km``."""
    return np.linspace(0.0, length_km, n_sections + 1)
