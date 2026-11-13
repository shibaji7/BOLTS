# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""DC solution of a source through a resistor into a linear Zener stack. The stack is the branch ``drop = Vz + rz (I - I_nom)``, i.e. an
ideal source of (Vz - rz I_nom) in series with rz, so  I = (V - (Vz - rz I_nom)) / (R + rz)."""
from __future__ import annotations

import numpy as np

from ..elements.lumped import Resistor, VSource
from ..elements.zener import LinearZener
from ..mna.assemble import assemble
from ..mna.dc_op import solve_dc
from ..mna.stamp import ConstantSource, Stamper
from ._case import ValidationCase


def run(v_V: float = 100.0, r_ohm: float = 50.0, vz_V: float = 56.0, rz_ohm: float = 5.0, i_nom_A: float = 0.1) -> ValidationCase:
    """Compare the DC current through a resistor and linear Zener with the closed form."""
    st = Stamper(["in", "m"])
    z = LinearZener(vz_V, rz_ohm, i_nom_A)
    r_z, src = z.series_parameters()
    VSource("vs", None, "in", ConstantSource(v_V)).stamp(st)
    Resistor("r", "in", "m", r_ohm).stamp(st)
    st.add_series_branch("zener", "m", None, r_z, 0.0, [ConstantSource(src)])
    sysm = assemble(st)
    x = solve_dc(sysm, sysm.exogenous_rhs(np.array([0.0]))[0])
    i = float(x[sysm.branch_row("zener")])
    expected = (v_V - (vz_V - rz_ohm * i_nom_A)) / (r_ohm + rz_ohm)
    return ValidationCase("zener_dc", abs(i - expected) / abs(expected), 1e-9, f"I = {i:.6f} A")
