# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Conductor-to-sea voltage along the cable (what loads the insulation)."""
from __future__ import annotations

import numpy as np

from ..mna.transient import TransientResult


def node_peaks_V(res: TransientResult) -> np.ndarray:
    """Peak absolute voltage against the sea at each node."""
    return np.abs(res.nodes_V).max(axis=0)


def voltage_metrics(res: TransientResult) -> dict:
    """The highest conductor-to-sea voltage anywhere and the node where it occurs (in normal feeding it is near a PFE)."""
    pk = node_peaks_V(res)
    i = int(np.argmax(pk))
    return {"v_cs_peak_V": float(pk[i]), "v_cs_peak_node": res.system.node_names[i]}
