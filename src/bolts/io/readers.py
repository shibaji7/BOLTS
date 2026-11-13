# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Read results back."""
from __future__ import annotations

import csv
import json

import numpy as np


def read_series_csv(path) -> dict[str, np.ndarray]:
    """A results CSV as ``{column name: array}``; every cell must be numeric."""
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    return {k: np.array([float(r[k]) for r in rows]) for k in rows[0]}


def read_json(path):
    """A JSON file (summary or manifest)."""
    with open(path) as f:
        return json.load(f)
