# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Energy balance of an RC step: the source delivers E = V Q, the capacitor stores C V^2/2 and the resistor dissipates the rest
(also C V^2/2). Checks that no energy is created or destroyed by the discretisation beyond its first-order error."""
from __future__ import annotations

import numpy as np

from ..elements.lumped import Capacitor, Resistor, VSource
from ..mna.assemble import assemble
from ..mna.stamp import Stamper
from ..mna.transient import run_transient
from ._case import ValidationCase
from .rc_step import _Step


def run(r_ohm: float = 1e3, c_F: float = 1e-6, v_V: float = 10.0, steps_per_tau: int = 400) -> ValidationCase:
    """Charge a capacitor through a resistor and compare the source energy with resistor loss plus stored energy."""
    tau = r_ohm * c_F
    dt = tau / steps_per_tau
    st = Stamper(["in", "out"])
    for el in (VSource("vs", None, "in", _Step(v_V)), Resistor("r", "in", "out", r_ohm), Capacitor("c", "out", None, c_F)):
        el.stamp(st)
    sysm = assemble(st)
    t = dt * np.arange(int(12 * steps_per_tau) + 1)
    res = run_transient(sysm, t)
    i = res.branch_I("r")
    e_src = float(np.trapezoid(v_V * i, t))
    e_res = float(np.trapezoid(r_ohm * i ** 2, t))
    e_cap = 0.5 * c_F * float(res.node_V("out")[-1]) ** 2
    err = abs(e_src - e_res - e_cap) / e_src
    return ValidationCase("energy_balance", err, 5.0 / steps_per_tau, f"E_source = {e_src:.3e} J")
