# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Topology checks on a stamped circuit: every node must be connected to the sea (ground) through some path."""
from __future__ import annotations

from ..errors import TopologyError
from ..mna.stamp import Stamper


def check_connected(st: Stamper) -> None:
    """Raise :class:`TopologyError` if any node has no path to the sea; such a node would make the DC matrix singular.

    Union-find over every two-terminal connection; node index -1 is the sea."""
    parent = {i: i for i in range(-1, len(st.node_names))}

    def find(x):
        """Root of ``x`` in the union-find forest, with path compression."""
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        """Merge the components of ``a`` and ``b``."""
        parent[find(a)] = find(b)

    for br in st.branches:
        union(br.a, br.b)
    for a, b, _ in st.conductances:
        union(a, b)
    for a, b, _ in st.isources:
        union(a, b)
    root = find(-1)                      # the component containing the sea
    floating = [st.node_names[i] for i in range(len(st.node_names)) if find(i) != root]
    if floating:
        raise TopologyError(f"nodes with no path to the sea (ground): {floating}")
