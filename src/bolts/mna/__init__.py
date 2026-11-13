# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""The circuit solver: modified nodal analysis, backward Euler, cached LU and Newton iteration.

`stamp` and `assemble` build the matrices, `dc_op` the starting state, `transient` marches in time (with the PFE regulator integrated exactly over each step), `newton` handles nonlinear devices, `integrators` and `linear_solve` are the numerical parts. `window_run` (microsecond windows) is deferred.

Status: implemented except `window_run`. Chapter 03 (the circuit model).
"""
