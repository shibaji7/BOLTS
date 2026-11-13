# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Transmission-line helpers: lumped ladders, sectioning and the telegrapher's equations.

`lumped_ladder` and `sectioning` choose how many lumped sections a cable needs (section delay well below the signal rise time); `telegrapher` gives the characteristic impedance and delay. `bergeron` (travelling-wave line for microsecond surges) is a stub.

Status: implemented except `bergeron`. Chapter 03.
"""
