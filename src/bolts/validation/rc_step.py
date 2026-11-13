# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""RC step: v_out(t) = V (1 - exp(-t/RC)). Checks the capacitor stamp and backward Euler (first-order accurate: error ~ dt/RC)."""
from __future__ import annotations

import numpy as np

from ..elements.lumped import Capacitor, Resistor, VSource
from ..mna.assemble import assemble
from ..mna.stamp import ConstantSource, Stamper
from ..mna.transient import run_transient
from ._case import ValidationCase


def run(r_ohm: float = 1e3, c_F: float = 1e-6, v_V: float = 10.0, steps_per_tau: int = 400) -> ValidationCase:
    """Step an RC circuit and compare the capacitor voltage with the exponential."""
    tau = r_ohm * c_F
    dt = tau / steps_per_tau
    st = Stamper(["in", "out"])
    for el in (VSource("vs", None, "in", ConstantSource(v_V)), Resistor("r", "in", "out", r_ohm), Capacitor("c", "out", None, c_F)):
        el.stamp(st)
    sysm = assemble(st)
    # start from a discharged capacitor: the DC operating point would charge it, so step the source at t = 0 instead
    t = dt * np.arange(int(6 * steps_per_tau) + 1)
    sysm.branches[0].sources[0] = _Step(v_V)
    res = run_transient(sysm, t)
    ana = v_V * (1.0 - np.exp(-t / tau))
    err = float(np.max(np.abs(res.node_V("out") - ana)) / v_V)
    return ValidationCase("rc_step", err, 2.0 / steps_per_tau, f"tau = {tau:g} s, dt = tau/{steps_per_tau}")


class _Step:
    """0 at the first sample, v afterwards (so the DC start is discharged)."""
    dynamic = False

    def __init__(self, v):
        self.v = v

    def values(self, t_s):
        """Zero at t = 0, the step value afterwards."""
        return np.where(np.asarray(t_s) > 0.0, self.v, 0.0)
