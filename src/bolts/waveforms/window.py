# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Cut a time window out of a record."""
from __future__ import annotations

import numpy as np

from .base import Record


def window(rec: Record, t0_s: float, t1_s: float, shift_to_zero: bool = True) -> Record:
    """The samples with ``t0_s <= t <= t1_s``; the time axis is shifted to start at 0 unless ``shift_to_zero`` is False."""
    m = (rec.t_s >= t0_s) & (rec.t_s <= t1_s)
    if int(m.sum()) < 2:
        raise ValueError(f"window [{t0_s:g}, {t1_s:g}] s contains fewer than two samples")
    t = rec.t_s[m]
    return Record(t - t[0] if shift_to_zero else t, rec.values[m], f"{rec.label} [{t0_s:g}-{t1_s:g}] s", rec.unit)


def piecewise_hold(rec: Record, t_s: np.ndarray) -> np.ndarray:
    """Zero-order hold of a record on a new time axis (for step-like data, as opposed to linear interpolation)."""
    idx = np.clip(np.searchsorted(rec.t_s, t_s, side="right") - 1, 0, len(rec.t_s) - 1)
    return rec.values[idx]
