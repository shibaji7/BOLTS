# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Write results: CSV for time series, JSON for numbers."""
from __future__ import annotations

import csv
import json
import pathlib

import numpy as np


def write_series_csv(path, columns: dict[str, np.ndarray]) -> pathlib.Path:
    """Write equal-length columns to a CSV (9 significant digits, enough to reproduce a plot); creates the folder."""
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    names = list(columns)
    n = len(columns[names[0]])
    with open(p, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(names)
        for i in range(n):
            w.writerow([f"{float(columns[k][i]):.9g}" for k in names])
    return p


def write_json(path, obj) -> pathlib.Path:
    """Write ``obj`` as indented JSON; numpy scalars and arrays are converted."""
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        json.dump(obj, f, indent=2, default=_default)
    return p


def _default(o):
    """JSON fallback for numpy types and anything else (as its string)."""
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)
