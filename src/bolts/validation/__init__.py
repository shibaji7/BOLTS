# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Analytic validation cases. Each module has ``run() -> ValidationCase``; ``run_all()`` runs them (``bolts validate``)."""
from . import diode_clamp, energy_balance, line_step, rc_step, rlc_ring, zener_dc, zener_knee

CASES = [rc_step, rlc_ring, line_step, zener_dc, energy_balance, diode_clamp, zener_knee]


def run_all():
    """Run every analytic case and return the list of :class:`ValidationCase`."""
    return [c.run() for c in CASES]
