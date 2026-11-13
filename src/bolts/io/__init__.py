# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Reading and writing results: CSV for time series, JSON for numbers, a manifest for provenance.

`writers` and `readers` handle `series.csv` and `summary.json`; `manifest` records the version, the parameter fingerprint and the time of a run so a result can be traced back.

Status: implemented. Chapter 10.
"""
