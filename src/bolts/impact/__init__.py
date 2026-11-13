# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""From line current to the consequences: light, bit errors and traffic.

`optical` turns the current at each repeater into pump power, OSNR, Q and bit-error margin; `terminal` turns the Q margin into link state and lost traffic with placeholder timings. Ported from the pfe_design study.

Status: implemented. Chapters 04 and 05.
"""
