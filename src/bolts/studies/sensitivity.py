# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""One-at-a-time sensitivity: change each listed parameter by a relative step (up and down) and report the change of a metric."""
from __future__ import annotations

from collections.abc import Callable

from ..config.schema import ParameterSet


def one_at_a_time(params: ParameterSet, keys: list[str], metric: Callable[[ParameterSet], float], rel_step: float = 0.1) -> list[dict]:
    """Rows sorted by swing: the metric for each key moved down and up by ``rel_step`` while the others stay fixed."""
    base = metric(params)
    rows = []
    for key in keys:
        sec, name = key.split(".", 1)
        v0 = float(params.get(sec, name))
        lo = metric(params.with_overrides({key: v0 * (1 - rel_step)}))
        hi = metric(params.with_overrides({key: v0 * (1 + rel_step)}))
        rows.append({"key": key, "value": v0, "metric": base, "metric_down": lo, "metric_up": hi,
                     "swing": abs(hi - lo)})
    return sorted(rows, key=lambda r: -r["swing"])
