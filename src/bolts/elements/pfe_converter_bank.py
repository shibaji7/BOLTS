# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""PFE converter bank: converter modules in series that together generate the output voltage, protected N:1 (Chesnoy p. 397; a vendor catalogue shows 6
modules with 5 needed). While no more than ``n_spare`` modules have failed the spare takes over and the voltage range is unchanged; each further failure
removes one module's rating from the range.

    working   = n_modules - failed
    in use    = min(working, n_modules - n_spare)
    V_cap     = rating * in use

This is a range model only: the failover transfer time and the sharing of voltage between modules are not modelled (``pfe.failover_time_s`` is unknown)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PfeConverterBank:
    """Modules of one PFE terminal: how many, the voltage each can generate, and how many are spare."""

    n_modules: int
    module_rating_V: float
    n_spare: int = 1

    def __post_init__(self):
        if self.n_modules < 1 or self.module_rating_V <= 0 or not 0 <= self.n_spare < self.n_modules:
            raise ValueError("a converter bank needs at least one module, a positive rating and fewer spares than modules")

    def max_voltage_V(self, failed: int = 0) -> float:
        """Highest total voltage the terminal can generate with ``failed`` modules out of service."""
        if not 0 <= failed <= self.n_modules:
            raise ValueError("failed must be between 0 and the number of modules")
        in_use = min(self.n_modules - failed, self.n_modules - self.n_spare)
        return self.module_rating_V * in_use
