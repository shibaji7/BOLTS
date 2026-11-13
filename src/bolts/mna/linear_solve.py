# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""LU factorisation with caching: the matrix of a linear circuit with a fixed step is factored once and reused every step."""
from __future__ import annotations

import numpy as np
from scipy.linalg import lu_factor, lu_solve


class LUSolver:
    """Factor ``A`` once; every later :meth:`solve` is just two triangular solves (cheap)."""

    def __init__(self, A: np.ndarray):
        self._lu = lu_factor(A, check_finite=False)

    def solve(self, b: np.ndarray) -> np.ndarray:
        """Solve ``A x = b`` for the factored ``A``."""
        return lu_solve(self._lu, b, check_finite=False)
