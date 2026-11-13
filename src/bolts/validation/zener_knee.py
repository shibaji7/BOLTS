# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""DC solution of a source through a resistor into a piecewise Zener stack (Newton iteration), checked on its three segments::

    above the knee   I = (V - V_k + rz I_k) / (R + rz)             the stack conducts
    below the knee   I = V / (R + V_k / I_k)                       the stack is off
    reverse          I = V / (R + rz)  (V < 0)                     forward diodes

with V_k = Vz + rz (I_k - I_nom). The knee current ``I_k`` is chosen so that all three segments are visited."""
from __future__ import annotations

import numpy as np

from ..elements.lumped import Resistor, VSource
from ..elements.zener import PiecewiseZener
from ..mna.assemble import assemble
from ..mna.newton import newton_solve
from ..mna.stamp import ConstantSource, Stamper
from ._case import ValidationCase


def run(r_ohm: float = 50.0, vz_V: float = 56.0, rz_ohm: float = 5.0, i_nom_A: float = 1.0, i_knee_A: float = 0.9) -> ValidationCase:
    """Worst relative error of the current over drives that fall on each segment."""
    z = PiecewiseZener(vz_V, rz_ohm, i_nom_A, i_knee_A)
    vk = z.v_knee_V
    worst = 0.0
    for v in (-40.0, -5.0, 10.0, 30.0, 60.0, 100.0, 120.0, 200.0):
        st = Stamper(["in", "m"])
        VSource("vs", None, "in", ConstantSource(v)).stamp(st)
        Resistor("r", "in", "m", r_ohm).stamp(st)
        st.add_nonlinear_branch("zener", "m", None, z)
        sysm = assemble(st)
        x, _ = newton_solve(sysm, sysm.G, sysm.exogenous_rhs(np.array([0.0]))[0], np.zeros(sysm.n))
        i = float(x[sysm.branch_row("zener")])
        if v < 0.0:
            expected = v / (r_ohm + rz_ohm)
        else:
            i_below = v / (r_ohm + vk / i_knee_A)
            expected = i_below if i_below < i_knee_A else (v - vk + rz_ohm * i_knee_A) / (r_ohm + rz_ohm)
        worst = max(worst, abs(i - expected) / max(abs(expected), 1e-3))
    return ValidationCase("zener_knee", worst, 1e-9, f"V_k = {vk:.1f} V at I_k = {i_knee_A:g} A")
