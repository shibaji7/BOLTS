# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Run one study function over a list of values of one parameter."""
from __future__ import annotations

from collections.abc import Callable

from ..config.schema import ParameterSet


def sweep(params: ParameterSet, key: str, values, fn: Callable[[ParameterSet], dict]) -> list[dict]:
    """``fn(params_with_override)`` for every value; each row has the swept key and value plus what ``fn`` returned."""
    rows = []
    for v in values:
        out = dict(fn(params.with_overrides({key: v})))
        rows.append({"key": key, "value": v, **out})
    return rows
