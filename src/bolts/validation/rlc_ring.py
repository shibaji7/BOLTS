# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Series RLC step (under-damped): v_c(t) = V [1 - e^(-a t) (cos wd t + (a/wd) sin wd t)], a = R/2L, wd = sqrt(1/LC - a^2).
Checks the inductor stamp. Backward Euler damps ringing numerically, so a fine step is used."""
from __future__ import annotations

import numpy as np

from ..elements.lumped import Capacitor, Inductor, Resistor, VSource
from ..mna.assemble import assemble
from ..mna.stamp import Stamper
from ..mna.transient import run_transient
from ._case import ValidationCase
from .rc_step import _Step


def run(r_ohm: float = 10.0, l_H: float = 1e-3, c_F: float = 1e-6, v_V: float = 10.0, steps_per_period: int = 4000) -> ValidationCase:
    """Step a series RLC circuit and compare with the damped-oscillation formula."""
    a = r_ohm / (2 * l_H)
    wd = np.sqrt(1.0 / (l_H * c_F) - a * a)
    dt = (2 * np.pi / wd) / steps_per_period
    st = Stamper(["in", "m1", "out"])
    for el in (VSource("vs", None, "in", _Step(v_V)), Resistor("r", "in", "m1", r_ohm), Inductor("l", "m1", "out", l_H), Capacitor("c", "out", None, c_F)):
        el.stamp(st)
    sysm = assemble(st)
    t = dt * np.arange(int(3 * steps_per_period) + 1)
    res = run_transient(sysm, t)
    ana = v_V * (1.0 - np.exp(-a * t) * (np.cos(wd * t) + a / wd * np.sin(wd * t)))
    err = float(np.max(np.abs(res.node_V("out") - ana)) / v_V)
    return ValidationCase("rlc_ring", err, 0.02, f"f = {wd / 2 / np.pi:.0f} Hz, {steps_per_period} steps per period")
