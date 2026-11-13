# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Parse ``section.key=value`` strings (command line ``--set``) into an override dictionary."""
from __future__ import annotations

import json
from typing import Any

from ..errors import ConfigError


def parse_overrides(items: list[str] | None) -> dict[str, Any]:
    """``["pfe.max_voltage_kV_per_end=2.5", ...]`` -> ``{"pfe.max_voltage_kV_per_end": 2.5}``."""
    out: dict[str, Any] = {}
    for item in items or []:
        if "=" not in item:
            raise ConfigError(f"override {item!r} must look like section.key=value")
        key, raw = item.split("=", 1)
        try:
            out[key.strip()] = json.loads(raw)       # numbers, true/false, lists, "quoted strings"
        except json.JSONDecodeError:
            out[key.strip()] = raw                    # bare words stay strings
    return out
