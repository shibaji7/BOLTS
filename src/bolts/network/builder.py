# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Build a network from parameters: picks the topology. Point-to-point only in v0.1; trunk-and-branch (branching units) in v0.3."""
from __future__ import annotations

from ..config.schema import ParameterSet
from ..waveforms.base import Record
from .graph import Network
from .power_modes import PowerMode
from .topology_p2p import build_p2p


def build_network(params: ParameterSet, record: Record | None = None, topology: str = "p2p",
                  mode: PowerMode = PowerMode.DOUBLE_END, provider=None) -> Network:
    """Entry point for building a network. ``record`` is the net induced voltage in volts (``None`` = a quiet line). ``provider`` is a cable-property provider (see :mod:`bolts.properties`); the default is the constant one from the parameters. Any topology other than
    ``"p2p"`` is routed to the trunk-and-branch builder, which raises ``NotImplementedYet`` until branching units exist (v0.3)."""
    if topology == "p2p":
        return build_p2p(params, record, mode, provider)
    from .topology_trunk_branch import build_trunk_branch
    return build_trunk_branch(params, record)
