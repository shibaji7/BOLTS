# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Build a network from parameters: picks the topology. Point-to-point only in v0.1; trunk-and-branch (branching units) in v0.3."""
from __future__ import annotations

from ..config.schema import ParameterSet
from ..properties.base import PropertyProvider
from ..waveforms.base import Record
from .graph import Network
from .power_modes import PowerMode
from .topology_p2p import build_p2p


def build_network(params: ParameterSet, record: Record | None = None, topology: str = "p2p",
                  mode: PowerMode = PowerMode.DOUBLE_END, provider: PropertyProvider | None = None) -> Network:
    """Build the circuit of a power-feed line: PFE A, cable spans with a repeater after each, PFE B, and the sea return through the landing earths.

    Each span gets its own R, L, G, C from the cable-property provider (at the span mid-point and the seabed temperature), the repeaters become Zener
    shunts (piecewise when the knee is known), and the PFE regulator is set from the PFE parameters (voltage cap, converter bank, slew limit).

    Args:
        params: The parameter set (see :func:`~bolts.config.loader.load_parameters`).
        record: The net induced voltage in volts as a function of time, spread over the spans. ``None`` builds a quiet line.
        topology: ``"p2p"`` (point to point). Anything else goes to the trunk-and-branch builder, which raises ``NotImplementedYet`` until branching
            units exist (v0.3).
        mode: How the two PFEs share the feed, :class:`~bolts.network.power_modes.PowerMode` (double-end by default).
        provider: A cable-property provider (see :mod:`bolts.properties`). ``None`` takes the constant one from the parameters, or the one chosen by
            ``cable.section_table_csv``, ``cable.temperature_model`` and ``cable.depth_profile_csv``.

    Returns:
        A :class:`~bolts.network.graph.Network`: the element list, the regulator and ``meta`` (set current, margins, static need, repeater branches,
        earth resistance, the record).

    Raises:
        MissingParameter: A needed parameter is still ``unknown``.
        NotImplementedYet: ``topology`` is not ``"p2p"``.
    """
    if topology == "p2p":
        return build_p2p(params, record, mode, provider)
    from .topology_trunk_branch import build_trunk_branch
    return build_trunk_branch(params, record)
