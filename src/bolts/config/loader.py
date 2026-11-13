# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Read parameter files (TOML) and merge them over the shipped defaults."""
from __future__ import annotations

import pathlib
import tomllib
from typing import Any

from ..errors import ConfigError
from .provenance import TBD, Param, Status
from .schema import ParameterSet
from .validate import validate

DEFAULTS_DIR = pathlib.Path(__file__).with_name("defaults")


def _parse_table(section: str, name: str, raw: Any, from_user: bool) -> Param:
    """Turn one TOML entry into a :class:`Param`. Shipped defaults must be complete tables (value, status, source) so that nothing enters
    the package without provenance; user files may use a bare value, which becomes an ``override``."""
    if isinstance(raw, dict):
        if "value" not in raw:
            raise ConfigError(f"{section}.{name}: a table needs a 'value'")
        status = raw.get("status", "override" if from_user else None)
        if status is None:
            raise ConfigError(f"{section}.{name}: missing 'status'")
        if "source" not in raw and not from_user:
            raise ConfigError(f"{section}.{name}: missing 'source'")
        try:
            st = Status(status)
        except ValueError as e:
            raise ConfigError(f"{section}.{name}: status {status!r} not in {[s.value for s in Status]}") from e
        return Param(section, name, raw["value"], raw.get("unit", ""), st, raw.get("source", "user file"))
    if not from_user:
        raise ConfigError(f"{section}.{name}: defaults must be tables with value, status and source")
    return Param(section, name, raw, "", Status.OVERRIDE, "user file")      # a bare value in a user file


def _read(path: pathlib.Path) -> dict[str, Any]:
    """Parse a TOML file (stdlib ``tomllib``, so no extra dependency)."""
    with open(path, "rb") as f:
        return tomllib.load(f)


def load_parameters(path: str | pathlib.Path | None = None, overrides: dict[str, Any] | None = None) -> ParameterSet:
    """Shipped defaults, then the optional user TOML ``path``, then ``overrides`` ({"section.name": value}).

    In a user file a parameter may be a full table (``{value, unit, status, source}``) or a bare value, which becomes an
    ``override``. Unknown (TBD) parameters stay unknown until somebody supplies them."""
    data: dict[str, dict[str, Param]] = {}
    # layer 1: every shipped defaults file (one per topic: cable, repeater, pfe, ...)
    for f in sorted(DEFAULTS_DIR.glob("*.toml")):
        for sec, params in _read(f).items():
            for name, raw in params.items():
                data.setdefault(sec, {})[name] = _parse_table(sec, name, raw, from_user=False)
    # layer 2: the user's file; a key that does not exist in the defaults is a typo, so it is an error, not a silent new setting
    if path is not None:
        p = pathlib.Path(path)
        if not p.exists():
            raise ConfigError(f"parameter file {p} not found")
        for sec, params in _read(p).items():
            for name, raw in params.items():
                if sec not in data or name not in data[sec]:
                    raise ConfigError(f"{p.name}: unknown parameter {sec}.{name}")
                old = data[sec][name]
                new = _parse_table(sec, name, raw, from_user=True)
                data[sec][name] = Param(sec, name, new.value, new.unit or old.unit, new.status, new.source)   # keep the unit if the user gave none
    ps = ParameterSet(data)
    # layer 3: programmatic or command-line overrides
    if overrides:
        ps = ps.with_overrides(overrides)
    validate(ps)         # last: reject values that would make the physics meaningless
    return ps


__all__ = ["DEFAULTS_DIR", "TBD", "load_parameters"]
