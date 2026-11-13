# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Common result type of a validation case."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationCase:
    """Outcome of one case: the measured error, the tolerance it must stay under and a human-readable detail."""
    name: str
    error: float            # the measured error (relative unless the name says otherwise)
    tolerance: float
    detail: str = ""

    @property
    def passed(self) -> bool:
        """True when the error is within the tolerance."""
        return self.error <= self.tolerance
