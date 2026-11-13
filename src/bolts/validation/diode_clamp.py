# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""DC solution of a source through a resistor into a clamp (a piecewise-linear nonlinear shunt), solved by Newton iteration. Above the clamp voltage the node sits at::

    v = V_c + (V - V_c) r_on / (R + r_on)        (the clamp and the series resistor divide the excess)

and below it the clamp is off and v = V. Both segments, in both polarities, are checked against these closed forms."""
from __future__ import annotations

import numpy as np

from ..elements.diode_chain import DiodeChain
from ..elements.lumped import Resistor, VSource
from ..mna.assemble import assemble
from ..mna.newton import newton_solve
from ..mna.stamp import ConstantSource, Stamper
from ._case import ValidationCase


def _node_voltage(v_V: float, r_ohm: float, clamp: DiodeChain) -> float:
    st = Stamper(["in", "m"])
    VSource("vs", None, "in", ConstantSource(v_V)).stamp(st)
    Resistor("r", "in", "m", r_ohm).stamp(st)
    clamp.stamp(st)
    sysm = assemble(st)
    x, _ = newton_solve(sysm, sysm.G, sysm.exogenous_rhs(np.array([0.0]))[0], np.zeros(sysm.n))
    return float(x[sysm.node_index("m")])


def run(r_ohm: float = 100.0, n_diodes: int = 4, v_forward_V: float = 0.7, r_on_ohm: float = 2.0) -> ValidationCase:
    """Worst relative error of the node voltage over drives below, just above and far above the clamp voltage, of both signs."""
    clamp = DiodeChain("clamp", "m", None, n_diodes, v_forward_V, r_on_ohm)
    vc = n_diodes * v_forward_V
    worst = 0.0
    for v in (1.0, 2.0, 2.79, 2.81, 5.0, 50.0, 1000.0, -2.0, -2.81, -50.0, -1000.0):
        got = _node_voltage(v, r_ohm, clamp)
        sign, mag = np.sign(v), abs(v)
        expected = v if mag <= vc else sign * (vc + (mag - vc) * r_on_ohm / (r_ohm + r_on_ohm))
        worst = max(worst, abs(got - expected) / max(abs(expected), 1.0))
    return ValidationCase("diode_clamp", worst, 1e-9, f"V_c = {vc:.1f} V, r_on = {r_on_ohm:g} ohm, R = {r_ohm:g} ohm")
