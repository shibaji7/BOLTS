# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Topology: the element list, the point-to-point builder and the (planned) branching-unit topologies.

`build_network` turns a parameter set and a record into a `Network`: PFE A, cable spans with repeaters, PFE B and the sea return. `graph` holds the container, `validate` checks connectivity. Trunk-and-branch topologies, power modes, segments and switch states are stubs for v0.3.

Status: point-to-point implemented. Chapters 03 and 14.
"""
