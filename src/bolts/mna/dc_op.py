# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""DC operating point: capacitors open, inductors short. Used as the initial condition of a transient (a window that starts away from
zero then begins in equilibrium, not with an artificial step) and to find the loop resistance seen by the PFE."""
from __future__ import annotations

import numpy as np

from .assemble import System


def solve_dc(system: System, rhs: np.ndarray) -> np.ndarray:
    """Solve ``G x = rhs`` (the ``C dx/dt`` term vanishes at DC). ``G`` is singular only if a node floats; the stamps always tie one to the sea."""
    return np.linalg.solve(system.G, rhs)


def dc_sensitivity(system: System, unit_rhs: np.ndarray, sense_row: int) -> float:
    """d(sensed branch current) / d(controlled source value), A per V, at DC. For a PFE pair it equals 1 / R_loop."""
    return float(solve_dc(system, unit_rhs)[sense_row])
