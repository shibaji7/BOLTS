# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Time integration of ``G x + C dx/dt = b``.

Backward Euler:  (G + C/dt) x_n = b_n + (C/dt) x_(n-1). It is L-stable, so the stiff cable ladder (time constants from
milliseconds to hours) cannot ring numerically. The trapezoid rule is planned (roadmap v0.3)."""
from __future__ import annotations

import numpy as np

from ..errors import NotImplementedYet


def backward_euler_matrices(G: np.ndarray, C: np.ndarray, dt_s: float) -> tuple[np.ndarray, np.ndarray]:
    """(A, C/dt) with A = G + C/dt."""
    c_dt = C / dt_s
    return G + c_dt, c_dt


def trapezoid_matrices(G: np.ndarray, C: np.ndarray, dt_s: float):
    """Second-order trapezoid rule. Not implemented yet (it can ring on the stiff ladder, so it needs the adaptive step first)."""
    raise NotImplementedYet("the trapezoid integrator", "ROADMAP v0.3")


def get_integrator(name: str):
    """Look up an integrator by name; each returns ``(A, C/dt)`` so the transient loop does not care which one it is."""
    if name == "backward_euler":
        return backward_euler_matrices
    if name == "trapezoid":
        return trapezoid_matrices
    raise ValueError(f"unknown integrator {name!r}")
