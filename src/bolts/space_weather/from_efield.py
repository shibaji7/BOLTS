# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Net voltage from a uniform geoelectric field: V = E L (E in V/km along the cable direction, L in km). A convenience for
quick estimates; the real end-to-end voltage also includes the sea-earth potentials (see the pfe_design study: 72 V net against
641 V bare EMF), which only a field model such as SCUBAS provides."""
from __future__ import annotations

from ..waveforms.base import Record


def net_voltage_from_efield(e_V_per_km: Record, length_km: float) -> Record:
    """Not implemented yet: raises ``NotImplementedYet`` naming the roadmap item."""
    return Record(e_V_per_km.t_s, e_V_per_km.values * length_km, f"E x {length_km:g} km", "V")
