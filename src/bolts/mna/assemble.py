# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Build the MNA matrices from a stamped network.

The system is ``G x + C dx/dt = b(t)`` with x = (node voltages, branch currents). ``G`` and ``C`` are dense (a 12-repeater cable
has about 50 unknowns; sparse storage is a later optimisation behind the same interface)."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .stamp import Branch, Stamper


@dataclass
class System:
    """The assembled circuit: dense matrices and the bookkeeping needed to find any node or branch in the unknown vector."""

    node_names: list[str]
    branches: list[Branch]
    isources: list
    G: np.ndarray
    C: np.ndarray
    conductances: list = field(default_factory=list)     # (node a, node b, S) shunts, kept for exporters
    capacitances: list = field(default_factory=list)
    nl_shunts: list = field(default_factory=list)         # (node a, node b, law) nonlinear shunts, handled by the Newton iteration

    @property
    def has_nonlinear(self) -> bool:
        """True if any branch or shunt is nonlinear (the run then uses the Newton path)."""
        return bool(self.nl_shunts) or any(br.nonlinear is not None for br in self.branches)

    @property
    def n_nodes(self) -> int:
        """Number of node voltages (sea excluded)."""
        return len(self.node_names)

    @property
    def n(self) -> int:
        """Total number of unknowns: node voltages plus branch currents."""
        return self.n_nodes + len(self.branches)

    def node_index(self, name: str) -> int:
        """Position of a node voltage in the unknown vector."""
        return self.node_names.index(name)

    def branch_index(self, name: str) -> int:
        """Position of a branch among the branches (not in the unknown vector; see :meth:`branch_row`)."""
        for br in self.branches:
            if br.name == name:
                return br.index
        raise KeyError(f"no branch {name!r}")

    def branch_row(self, name: str) -> int:
        """Position of a branch current in the unknown vector (branch rows follow the node rows)."""
        return self.n_nodes + self.branch_index(name)

    def exogenous_rhs(self, t_s: np.ndarray) -> np.ndarray:
        """Right-hand side from every source that is not set by a controller, shape (len(t_s), n)."""
        b = np.zeros((len(t_s), self.n))
        for br in self.branches:
            row = self.n_nodes + br.index
            for s in br.sources:
                if not s.dynamic:
                    b[:, row] -= s.values(t_s)                  # branch row: v_a - v_b - R i - L di/dt = -s
        for a, bn, s in self.isources:
            v = s.values(t_s)
            if a >= 0:
                b[:, a] -= v
            if bn >= 0:
                b[:, bn] += v
        return b


def assemble(st: Stamper) -> System:
    """Turn the collected stamps into ``G`` and ``C``. Node rows are KCL (sum of currents leaving the node); branch rows are the branch law."""
    nn, nb = len(st.node_names), len(st.branches)
    n = nn + nb
    G = np.zeros((n, n))
    C = np.zeros((n, n))
    for a, b, g in st.conductances:      # shunt elements couple nodes directly
        _two_terminal(G, a, b, g)
    for a, b, c in st.capacitances:
        _two_terminal(C, a, b, c)
    for br in st.branches:
        row = nn + br.index
        if br.a >= 0:
            G[br.a, row] += 1.0               # the branch current leaves node a ...
            G[row, br.a] += 1.0
        if br.b >= 0:
            G[br.b, row] -= 1.0               # ... and enters node b
            G[row, br.b] -= 1.0
        G[row, row] -= br.r_ohm          # branch row: v_a - v_b - R i - L di/dt = -source  (the source goes to the right-hand side)
        C[row, row] -= br.l_H
    return System(list(st.node_names), list(st.branches), list(st.isources), G, C, list(st.conductances), list(st.capacitances), list(st.nl_shunts))


def _two_terminal(M: np.ndarray, a: int, b: int, v: float) -> None:
    """Standard two-terminal stamp: +v on the diagonals, -v off the diagonal; a ground end (index -1) contributes only its diagonal."""
    if a >= 0:
        M[a, a] += v
    if b >= 0:
        M[b, b] += v
    if a >= 0 and b >= 0:
        M[a, b] -= v
        M[b, a] -= v
