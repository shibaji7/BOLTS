# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Figures about the cable itself: the conductor-to-sea voltage along it, and how the repeaters see the current."""
from __future__ import annotations

import pathlib

import numpy as np

from ..result import Result
from . import style


def node_distances_km(result: Result) -> np.ndarray:
    """Distance of every node from PFE A: nodes are A, r1_in, r1_out, ..., B and a span lies between each pair r_out -> r_in."""
    span = result.meta["span_km"]
    names = result.transient.system.node_names
    d = []      # km from PFE A, in node order
    for n in names:
        if n == "A":
            d.append(0.0)
        elif n == "B":
            d.append(result.meta["length_km"])
        else:
            j = int(n[1:].split("_")[0])      # node 'r<j>_in' / 'r<j>_out' sits at repeater j, j spans from A
            d.append(j * span)
    return np.array(d)


def plot_node_profile(result: Result, path) -> pathlib.Path:
    """Conductor-to-sea voltage along the cable: before the storm, at the largest induced voltage, and the largest value reached."""
    plt = style.require_matplotlib()
    style.apply()
    C = style.TOL
    tr = result.transient
    x = node_distances_km(result)
    order = np.argsort(x, kind="stable")      # r_in and r_out share a distance; a stable sort keeps their order so the Zener drop shows as a step
    rec = result.meta.get("record")
    # the time step of the largest induced voltage (or of the largest node voltage if there is no record)
    k = int(np.argmax(np.abs(rec.sample(tr.t_s)))) if rec is not None else int(np.argmax(np.abs(tr.nodes_V).max(axis=1)))
    fig, ax = plt.subplots(figsize=(style.SINGLE_COL_IN * 1.6, 2.8))
    ax.plot(x[order], tr.nodes_V[0][order], color="0.5", lw=1.0, label="start of the window")
    ax.plot(x[order], tr.nodes_V[k][order], color=C["blue"], lw=1.2, label="at the largest induced voltage")
    ax.plot(x[order], np.abs(tr.nodes_V).max(axis=0)[order], color=C["red"], lw=0.8, ls=(0, (4, 2)), label="largest magnitude reached")
    ax.axhline(0.0, color="0.7", lw=0.5)
    ax.set_xlabel("Distance along the cable (km)")
    ax.set_ylabel("Conductor to sea (V)")
    ax.legend(frameon=False)
    fig.tight_layout()
    out = style.save(fig, path)
    plt.close(fig)
    return out
