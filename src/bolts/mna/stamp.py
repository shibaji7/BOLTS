# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Stamps for modified nodal analysis (MNA).

Unknowns: the node voltages (ground is the sea, potential 0, index -1) followed by one current per *series branch*.
A series branch from node ``a`` to node ``b`` carries the current ``i`` (a -> b) and obeys::

    v_a - v_b + s(t) = R i + L di/dt        (s = the sum of its sources; a source adds to the voltage that pushes the current)

so a cable span with a geoelectric EMF, a repeater with a Zener drop and a PFE with its earth resistance are all one kind of branch.
Shunt elements (conductance, capacitance) connect nodes; independent current sources inject into nodes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

import numpy as np

from ..waveforms.base import Record

GROUND_NAMES = {"gnd", "0", "sea", "ground"}


class NonlinearBranchLaw(Protocol):
    """The voltage-current law of a nonlinear series branch: the drop ``v_a - v_b`` as a function of the branch current, and its slope."""

    def drop_V(self, i_A: float) -> float:
        """Voltage across the branch (from its node ``a`` to ``b``) at current ``i_A``."""
        ...

    def slope_ohm(self, i_A: float) -> float:
        """Derivative of the drop with respect to the current (ohm): the dynamic resistance at ``i_A``."""
        ...


class NonlinearShuntLaw(Protocol):
    """The current-voltage law of a nonlinear shunt element between two nodes: current a -> b as a function of ``v_a - v_b``, and its slope."""

    def current_A(self, v_V: float) -> float:
        """Current from node ``a`` to node ``b`` at voltage ``v_V = v_a - v_b``."""
        ...

    def conductance_S(self, v_V: float) -> float:
        """Derivative of the current with respect to the voltage (S): the dynamic conductance at ``v_V``."""
        ...


class Source(Protocol):
    """Anything that can give a voltage (or current) per time step. ``dynamic`` sources are set by a controller during the run and are
    therefore left out of the precomputed right-hand side."""

    dynamic: bool

    def values(self, t_s: np.ndarray) -> np.ndarray:
        """The source's value (V or A) at each time in ``t_s``."""
        ...


@dataclass
class ConstantSource:
    """A fixed value (a DC supply, a bias)."""

    v: float
    dynamic: bool = False

    def values(self, t_s):
        """The constant, repeated for every step."""
        return np.full(len(t_s), self.v)


@dataclass
class RecordSource:
    """``weight * record(t)``: the exogenous drive (GMD voltage, a lightning pulse...)."""
    record: Record
    weight: float = 1.0
    dynamic: bool = False

    def values(self, t_s):
        """The record interpolated at ``t_s`` (linear between samples), times the weight (e.g. this span's share of the voltage)."""
        return self.weight * self.record.sample(t_s)


@dataclass
class ControlledSource:
    """A source whose value is set by a controller at every step (the PFE regulator): value = weight * v."""
    weight: float = 1.0
    v: float = 0.0
    dynamic: bool = True

    def values(self, t_s):
        """A constant source: the same value at every time (not used for exogenous right-hand sides)."""
        return np.full(len(t_s), self.weight * self.v)


@dataclass
class Branch:
    """One series branch: an element carrying a single current between two nodes (``a`` and ``b`` are node indices; -1 is the sea)."""

    name: str
    a: int
    b: int
    r_ohm: float
    l_H: float
    sources: list = field(default_factory=list)
    index: int = -1
    nonlinear: NonlinearBranchLaw | None = None     # a nonlinear branch has r_ohm = l_H = 0 here; the Newton iteration supplies its companion R and source


class Stamper:
    """Collects the elements' contributions; :func:`bolts.mna.assemble.assemble` turns them into matrices."""

    def __init__(self, node_names: list[str]):
        self.node_names = list(node_names)
        self._idx = {n: i for i, n in enumerate(node_names)}
        self.conductances: list[tuple[int, int, float]] = []
        self.capacitances: list[tuple[int, int, float]] = []
        self.branches: list[Branch] = []
        self.isources: list[tuple[int, int, Source]] = []
        self.nl_shunts: list[tuple[int, int, NonlinearShuntLaw]] = []

    def node(self, name: str | None) -> int:
        """Index of a node by name; ``None`` and the ground aliases map to -1 (the sea, 0 V, no equation of its own)."""
        if name is None or name in GROUND_NAMES:
            return -1
        try:
            return self._idx[name]
        except KeyError as e:
            raise KeyError(f"unknown node {name!r}") from e

    def add_conductance(self, a: str | None, b: str | None, g_S: float) -> None:
        """Shunt conductance between two nodes. A zero value is dropped (nothing to stamp)."""
        if g_S != 0.0:
            self.conductances.append((self.node(a), self.node(b), g_S))

    def add_capacitance(self, a: str | None, b: str | None, c_F: float) -> None:
        """Shunt capacitance between two nodes (it goes into the C matrix and so sets the time constants)."""
        if c_F != 0.0:
            self.capacitances.append((self.node(a), self.node(b), c_F))

    def add_series_branch(self, name: str, a: str | None, b: str | None, r_ohm: float, l_H: float = 0.0,
                          sources: list | None = None) -> Branch:
        """Series R-L branch from ``a`` to ``b`` with optional voltage ``sources``; gets its own current unknown. Returns the branch."""
        if r_ohm < 0 or l_H < 0:
            raise ValueError(f"branch {name}: R and L must not be negative")
        br = Branch(name, self.node(a), self.node(b), r_ohm, l_H, list(sources or []), len(self.branches))
        self.branches.append(br)
        return br

    def add_current_source(self, a: str | None, b: str | None, source: Source) -> None:
        """Current flowing a -> b through the source (it leaves node a and enters node b)."""
        self.isources.append((self.node(a), self.node(b), source))

    def add_nonlinear_branch(self, name: str, a: str | None, b: str | None, law: NonlinearBranchLaw) -> Branch:
        """Series branch whose voltage drop is a nonlinear function of its current (a Zener stack, say); handled by the Newton iteration."""
        br = Branch(name, self.node(a), self.node(b), 0.0, 0.0, [], len(self.branches), law)
        self.branches.append(br)
        return br

    def add_nonlinear_shunt(self, a: str | None, b: str | None, law: NonlinearShuntLaw) -> None:
        """Shunt element whose current from ``a`` to ``b`` is a nonlinear function of the voltage across it (a clamp, an arrester)."""
        self.nl_shunts.append((self.node(a), self.node(b), law))

