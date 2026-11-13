# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Compare two sets of node voltages."""
from __future__ import annotations

import numpy as np


def compare_voltages(v_bolts: np.ndarray, v_spice: np.ndarray) -> dict:
    """Largest and RMS difference, also as a fraction of the largest voltage in the reference."""
    diff = np.asarray(v_bolts) - np.asarray(v_spice)
    scale = float(np.abs(v_spice).max()) or 1.0      # relative errors are quoted against the largest reference voltage; avoid dividing by 0
    return {"max_abs_V": float(np.abs(diff).max()), "rms_V": float(np.sqrt(np.mean(diff ** 2))), "scale_V": scale,
            "max_rel": float(np.abs(diff).max() / scale), "rms_rel": float(np.sqrt(np.mean(diff ** 2)) / scale)}
