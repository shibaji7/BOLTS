# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Parameters with provenance: load, override and validate the parameter set.

Every number in a run is a `Param` (value, unit, status = sourced / assumed / unknown / override, source). `load_parameters` merges the shipped TOML defaults, an optional user file and `--set section.key=value` overrides; an `unknown` value raises `MissingParameter` when it is used.

Status: implemented. Chapter 07 (parameters and provenance).
"""
