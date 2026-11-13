# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Export to ngspice and compare, so every circuit has an independent check.

`netlist` writes a netlist (linear and nonlinear branches, shunts, current sources), `run_ngspice` runs it in batch mode and reads the node voltages, `compare` measures the difference. Needs the `ngspice` binary.

Status: implemented. Chapter 09 (validation).
"""
