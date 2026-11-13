# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""The parameter set: sections of :class:`~bolts.config.provenance.Param`, with lookup, overrides and a Markdown table."""
from __future__ import annotations

import copy
import hashlib
import json
from typing import Any

from ..errors import ConfigError
from .provenance import Param, Status


class ParameterSet:
    """All parameters, grouped in sections. Immutable by convention: changes go through :meth:`with_overrides`, which returns a copy."""

    def __init__(self, data: dict[str, dict[str, Param]]):
        self._data = data

    # ---- lookup ------------------------------------------------------------------------------------------------
    def param(self, section: str, name: str) -> Param:
        """The full :class:`Param` (value, unit, status, source); use :meth:`get` for just the value."""
        try:
            return self._data[section][name]
        except KeyError as e:
            raise ConfigError(f"no parameter {section}.{name}") from e

    def get(self, section: str, name: str) -> Any:
        """The value; raises :class:`~bolts.errors.MissingParameter` while it is ``TBD``."""
        return self.param(section, name).require()

    def has(self, section: str, name: str) -> bool:
        """True if the parameter has a value (i.e. is not ``TBD``)."""
        p = self.param(section, name)
        return not p.is_unknown

    def params(self) -> list[Param]:
        """Every parameter, flat, in file order."""
        return [p for sec in self._data.values() for p in sec.values()]

    def sections(self) -> list[str]:
        """Section names, in file order."""
        return list(self._data)

    # ---- changing -----------------------------------------------------------------------------------------------
    def with_overrides(self, overrides: dict[str, Any]) -> ParameterSet:
        """A copy with ``{"section.name": value}`` replaced; the status becomes ``override``."""
        data = copy.deepcopy(self._data)      # never mutate the original: other runs may hold it
        for key, value in overrides.items():
            if "." not in key:
                raise ConfigError(f"override key {key!r} must be 'section.name'")
            sec, name = key.split(".", 1)
            if sec not in data or name not in data[sec]:
                raise ConfigError(f"no parameter {key} to override")
            old = data[sec][name]
            data[sec][name] = Param(sec, name, value, old.unit, Status.OVERRIDE, f"override of: {old.source}")
        return ParameterSet(data)

    # ---- reporting -----------------------------------------------------------------------------------------------
    def table_md(self) -> str:
        """Every parameter as a Markdown table (used by the docs)."""
        rows = ["| key | value | unit | status | source |", "|---|---|---|---|---|"]
        for p in self.params():
            rows.append(f"| `{p.key}` | {p.value} | {p.unit} | {p.status.value} | {p.source} |")
        return "\n".join(rows)

    def counts(self) -> dict[str, int]:
        """How many parameters have each status."""
        out = {s.value: 0 for s in Status}
        for p in self.params():
            out[p.status.value] += 1
        return out

    def fingerprint(self) -> str:
        """Short hash of every value and status (stored in run manifests so a result can be traced to its inputs)."""
        blob = json.dumps([(p.key, p.value, p.status.value) for p in self.params()], sort_keys=True, default=str)
        return hashlib.sha256(blob.encode()).hexdigest()[:12]
