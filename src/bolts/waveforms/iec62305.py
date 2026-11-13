# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""IEC 62305 stroke classes (first positive 10/350 us, first negative 1/200 us, subsequent 0.25/100 us).

NOT implemented: the parameter values must be verified from the standard before they are used (roadmap v0.2)."""
from __future__ import annotations

from ..errors import NotImplementedYet


def stroke(kind: str, peak_A: float, dt_s: float):
    """Not implemented yet: raises ``NotImplementedYet`` naming the roadmap item."""
    raise NotImplementedYet("IEC 62305 stroke classes", "ROADMAP v0.2: verify parameters from the standard")
