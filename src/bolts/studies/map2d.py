# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""A two-parameter grid of one metric (for example surge amplitude against period)."""
from __future__ import annotations

from collections.abc import Callable

import numpy as np

from ..config.schema import ParameterSet


def grid(params: ParameterSet, key_x: str, xs, key_y: str, ys, metric: Callable[[ParameterSet], float]) -> np.ndarray:
    """Array of shape (len(ys), len(xs)): ``metric(params with key_x = x and key_y = y)``."""
    out = np.empty((len(ys), len(xs)))
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            out[j, i] = metric(params.with_overrides({key_x: x, key_y: y}))
    return out
