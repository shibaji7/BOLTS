# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Newton iteration for nonlinear elements (piecewise Zener, diode chains, arresters).

Each nonlinear element is linearised at the current iterate into a *companion model*:

* a nonlinear series branch with drop ``V(i)``:   ``v_a - v_b - R_eq i = e_eq``   with ``R_eq = V'(i0)`` and ``e_eq = V(i0) - R_eq i0``;
* a nonlinear shunt with current ``I(v)``:        ``i = g_eq v + i_eq``           with ``g_eq = I'(v0)`` and ``i_eq = I(v0) - g_eq v0``.

The linearised system ``(A + dG(x)) x = rhs + db(x)`` is solved, the companions are rebuilt at the new ``x``, and the loop repeats until the
unknowns stop changing. For piecewise-linear laws this converges in a few iterations (it is exact once the iterate sits on the right segment);
a damping fallback handles the rare cycle at a kink.

With the PFE regulator the supply voltage ``v`` is an extra unknown, fixed by one more equation: the sensed current equals the regulator's target.
That augmented system is solved by the same iteration (``v_fixed=None``); if the supply is clamped or slew-limited, ``v_fixed`` pins it and only ``x`` is solved.
A network without nonlinear elements never comes here (it uses the cached-LU path), unless ``newton=True`` is asked for, which the tests use to check
that both paths agree."""
from __future__ import annotations

import numpy as np

from ..errors import ConvergenceError
from .assemble import System

MAX_ITER = 80
DAMP_AFTER = 25          # iterations after which the update is halved to break a cycle at a kink


def _two_terminal(M: np.ndarray, a: int, b: int, v: float) -> None:
    """Standard two-terminal stamp (ground index -1 contributes only its diagonal)."""
    if a >= 0:
        M[a, a] += v
    if b >= 0:
        M[b, b] += v
    if a >= 0 and b >= 0:
        M[a, b] -= v
        M[b, a] -= v


def companion(system: System, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Matrix and right-hand-side corrections ``(dG, db)`` of the nonlinear elements linearised at ``x``."""
    n, nn = system.n, system.n_nodes
    dG = np.zeros((n, n))
    db = np.zeros(n)
    for br in system.branches:
        law = br.nonlinear
        if law is None:
            continue
        row, i = nn + br.index, x[nn + br.index]
        r_eq = law.slope_ohm(i)
        dG[row, row] -= r_eq
        db[row] += law.drop_V(i) - r_eq * i
    for a, b, law in system.nl_shunts:
        v = (x[a] if a >= 0 else 0.0) - (x[b] if b >= 0 else 0.0)
        g_eq = law.conductance_S(v)
        i_eq = law.current_A(v) - g_eq * v
        _two_terminal(dG, a, b, g_eq)
        if a >= 0:
            db[a] -= i_eq
        if b >= 0:
            db[b] += i_eq
    return dG, db


def newton_solve(system: System, A: np.ndarray, rhs: np.ndarray, x0: np.ndarray, unit: np.ndarray | None = None, sense_row: int | None = None,
                 target: float | None = None, v_fixed: float | None = None, v0: float = 0.0, tol: float = 1e-9) -> tuple[np.ndarray, float]:
    """Solve ``(A + dG(x)) x = rhs + db(x) + v unit`` by Newton iteration from ``x0``; returns ``(x, v)``.

    ``v_fixed`` given (or no ``unit``/``sense_row`` at all, meaning no controller, then 0): the supply voltage is that value.
    ``v_fixed`` None: ``v`` is also unknown and the extra equation ``x[sense_row] = target`` closes the system."""
    if v_fixed is None and unit is None and sense_row is None:
        v_fixed = 0.0                      # no controller: a plain nonlinear circuit
    n = len(x0)
    x = np.array(x0, float)
    v = v0 if v_fixed is None else v_fixed
    free = v_fixed is None
    if free and (unit is None or sense_row is None or target is None):
        raise ValueError("a free supply voltage needs unit, sense_row and target")
    for it in range(MAX_ITER):
        dG, db = companion(system, x)
        M = A + dG
        if free:
            big = np.zeros((n + 1, n + 1))
            big[:n, :n] = M
            big[:n, n] = -unit
            big[n, sense_row] = 1.0
            sol = np.linalg.solve(big, np.append(rhs + db, target))
            x_new, v_new = sol[:n], float(sol[n])
        else:
            x_new = np.linalg.solve(M, rhs + db + (0.0 if unit is None else v_fixed * unit))
            v_new = v
        step = max(np.max(np.abs(x_new - x)), abs(v_new - v) if free else 0.0)
        if step <= tol * (1.0 + np.max(np.abs(x_new))):
            return x_new, v_new
        w = 0.5 if it >= DAMP_AFTER else 1.0
        x = x + w * (x_new - x)
        v = v + w * (v_new - v) if free else v
    raise ConvergenceError(f"Newton iteration did not converge in {MAX_ITER} iterations (last step {step:.3e})")


def loop_resistance(system: System, x: np.ndarray, unit: np.ndarray, sense_row: int) -> float:
    """DC loop resistance seen by the regulator at the operating point ``x``: 1 / (d sensed current / d supply voltage) with the nonlinear elements
    linearised at ``x`` and the capacitors open. For a linear network it is the constant ``R_loop``."""
    dG, _ = companion(system, x)
    return 1.0 / float(np.linalg.solve(system.G + dG, unit)[sense_row])


def solve_nonlinear(system: System, A: np.ndarray, rhs: np.ndarray, x0: np.ndarray, **kw):
    """Alias of :func:`newton_solve` (the name the v0.1 stub announced)."""
    return newton_solve(system, A, rhs, x0, **kw)
