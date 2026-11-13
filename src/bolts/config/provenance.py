# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Parameter provenance: every number carries its unit, its status and where it came from.

Statuses
    sourced   taken from a document (the source string names it)
    assumed   an illustrative placeholder, to be replaced or swept
    unknown   ``TBD``: asking for it raises :class:`~bolts.errors.MissingParameter` instead of guessing
    override  changed in code or on the command line for one run
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from ..errors import MissingParameter

TBD = "TBD"


class Status(StrEnum):
    """Where a number stands; see the module docstring for what each value commits the code to."""

    SOURCED = "sourced"
    ASSUMED = "assumed"
    UNKNOWN = "unknown"
    OVERRIDE = "override"


@dataclass(frozen=True)
class Param:
    """One parameter with its unit, status and source. Frozen: a changed value is a new Param with status ``override``."""

    section: str
    name: str
    value: Any
    unit: str
    status: Status
    source: str

    @property
    def key(self) -> str:
        """``section.name``, as used in overrides and messages."""
        return f"{self.section}.{self.name}"

    @property
    def is_unknown(self) -> bool:
        """True while the value is the ``TBD`` marker."""
        return isinstance(self.value, str) and self.value == TBD

    def require(self) -> Any:
        """The value, or :class:`MissingParameter` naming the parameter and the reason it is unknown."""
        if self.is_unknown:
            raise MissingParameter(f"{self.key} is unknown (TBD): {self.source}")
        return self.value
