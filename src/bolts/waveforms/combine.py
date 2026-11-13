# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Combine records: superpose, concatenate."""
from __future__ import annotations

import numpy as np

from .base import Record


def plus(a: Record, b: Record) -> Record:
    """``a + b`` on the time axis of ``a`` (b is interpolated; zero outside b's span is NOT assumed: b is held at its end values)."""
    if a.unit != b.unit:
        raise ValueError(f"cannot add {a.unit} and {b.unit}")
    return Record(a.t_s, a.values + b.sample(a.t_s), f"{a.label} + {b.label}", a.unit)


def concatenate(*records: Record, gap_s: float = 0.0) -> Record:
    """Records one after another; each starts where the previous ended (plus ``gap_s``)."""
    t, v, t0 = [], [], 0.0
    for r in records:
        t.append(r.t_s - r.t_s[0] + t0)
        v.append(r.values)
        t0 = t[-1][-1] + gap_s + r.dt_s
    return Record(np.concatenate(t), np.concatenate(v), " | ".join(r.label for r in records), records[0].unit)
