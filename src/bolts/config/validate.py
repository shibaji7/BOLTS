# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Sanity checks on a parameter set (ranges that would make the physics meaningless)."""
from __future__ import annotations

from ..errors import ConfigError
from .schema import ParameterSet

_POSITIVE = [("cable", "length_km"), ("cable", "resistance_ohm_per_km"), ("repeater", "spacing_km"), ("pfe", "feed_current_A"),
             ("pfe", "max_voltage_kV_per_end"), ("pfe", "regulator_response_s"), ("solver", "dt_s")]
_NON_NEGATIVE = [("cable", "capacitance_uF_per_km"), ("cable", "leakage_S_per_km"), ("repeater", "dynamic_resistance_ohm"),
                 ("repeater", "voltage_drop_V"), ("earthing", "landing_earth_resistance_ohm")]


def validate(ps: ParameterSet) -> None:
    """Raise :class:`ConfigError` for a value that would make the model meaningless; ``TBD`` values are skipped (they raise on use)."""
    for sec, name in _POSITIVE:
        p = ps.param(sec, name)
        if not p.is_unknown and not (float(p.value) > 0):
            raise ConfigError(f"{p.key} must be positive, got {p.value}")
    for sec, name in _NON_NEGATIVE:
        p = ps.param(sec, name)
        if not p.is_unknown and float(p.value) < 0:
            raise ConfigError(f"{p.key} must not be negative, got {p.value}")
    # the end-A share of the total voltage: 0.5 is the symmetric double-end feed, 1.0 a single-end feed
    f = float(ps.get("pfe", "split_fraction_end_A"))
    if not 0.0 < f <= 1.0:
        raise ConfigError(f"pfe.split_fraction_end_A must be in (0, 1], got {f}")
