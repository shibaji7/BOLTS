# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""GMD forcing: turn a voltage record or a geoelectric field into a source on every span.

`gmd_source` spreads a net end-to-end induced voltage V_ind(t) over the spans, `from_efield` computes V = E L from a uniform field, `synthetic` generates the shipped physically-shaped example record. A SCUBAS or measured series is read as CSV through `load_waveform`.

Status: implemented. Chapters 01 and 06.
"""
