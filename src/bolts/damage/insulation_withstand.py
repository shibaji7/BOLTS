# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Insulation withstand: the life law  V^n t = constant  (Chesnoy Eq. 10.1, printed p. 383, from Dakin 1983). ``n`` and the constant are
device-specific and unknown here; they are arguments, never defaults."""
from __future__ import annotations


def time_to_failure_s(v_V: float, constant: float, n: float) -> float:
    """Seconds the insulation survives a constant voltage: t = constant / V^n."""
    return constant / v_V ** n


def withstand_voltage_V(t_s: float, constant: float, n: float) -> float:
    """Voltage the insulation survives for ``t_s`` seconds (the inverse of :func:`time_to_failure_s`)."""
    return (constant / t_s) ** (1.0 / n)


def constant_from_reference(v_ref_V: float, t_ref_s: float, n: float) -> float:
    """The constant of ``V^n t = constant`` from one reference point: the insulation survives ``t_ref_s`` at ``v_ref_V`` (for example the design life at the nominal voltage)."""
    return t_ref_s * v_ref_V ** n


def life_consumed(v_V, dt_s: float, constant: float, n: float):
    """Fraction of the life used up by a voltage record (Miner's rule): the sum over samples of ``dt / t_f(V)``, with ``t_f = constant / |V|^n``.

    ``v_V`` is one series (returns a number) or an array with time along the first axis (returns one fraction per column). 1.0 means the insulation is at its end of life."""
    import numpy as np
    v = np.abs(np.asarray(v_V, float))
    return np.sum(v ** n, axis=0) * dt_s / constant
