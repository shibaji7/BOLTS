# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Slowest mode of a lumped RC cable ladder against the distributed RC line: tau = R' C' L^2 / pi^2 for a line pinned to the sea at both
ends (the same check as in the pfe_design study). Checks the ladder discretisation (error ~ 1/N^2)."""
from __future__ import annotations

import numpy as np
from scipy.linalg import eig

from ..elements.cable_segment import CableSegment
from ..elements.lumped import Resistor
from ..mna.assemble import assemble
from ..mna.stamp import Stamper
from ._case import ValidationCase


def run(sections: int = 60, length_km: float = 750.0, r_ohm_per_km: float = 1.0, c_uF_per_km: float = 0.2) -> ValidationCase:
    """Compare the slowest decay mode of a lumped RC ladder with the distributed-line formula."""
    names = ["end0"] + [f"n{k}" for k in range(1, sections)] + ["end1"]
    st = Stamper(names)
    seg = length_km / sections
    for k in range(sections):
        CableSegment(f"s{k}", names[k], names[k + 1], seg, r_ohm_per_km, c_uF_per_km * 1e-6).stamp(st)
    for k, n in ((0, "end0"), (1, "end1")):
        Resistor(f"pin{k}", n, None, 1e-6).stamp(st)             # both ends pinned to the sea
    sysm = assemble(st)
    w, _ = eig(sysm.G, -sysm.C)
    lam = w[np.isfinite(w)].real
    tau_sim = float(-1.0 / lam[lam < 0].max())
    tau_ana = r_ohm_per_km * c_uF_per_km * 1e-6 * (length_km ** 2) / np.pi ** 2
    return ValidationCase("line_modes", abs(tau_sim - tau_ana) / tau_ana, 0.01, f"tau_sim = {tau_sim * 1e3:.2f} ms, analytic {tau_ana * 1e3:.2f} ms")
