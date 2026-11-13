#!/usr/bin/env python
# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Build ``data/example_vind_1s.csv`` with :func:`bolts.space_weather.synthetic.synthetic_vind` (see that module for what the record contains).

The slow backbone is the frozen May 2024 storm model output copied from the pfe_design study (60 s steps, 72 V peak), scaled and moved so its
largest swing sits mid-window. Run with ``python scripts/make_synthetic_vind.py`` from the repository root."""
from __future__ import annotations

import pathlib

import numpy as np

from bolts.space_weather.synthetic import synthetic_vind

ROOT = pathlib.Path(__file__).resolve().parents[1]
FROZEN = ROOT / "data" / "storm_may2024_vind_72V.csv"
OUT = ROOT / "data" / "example_vind_1s.csv"


def main() -> None:
    ts, vs = np.loadtxt(FROZEN, delimiter=",", skiprows=1, unpack=True)
    rec = synthetic_vind(ts, vs)
    np.savetxt(OUT, np.c_[rec.t_s, rec.values], delimiter=",", header="t_s,v_ind_V", comments="", fmt=["%.1f", "%.4f"])
    print(f"wrote {OUT.name}: {len(rec.t_s)} rows, V in [{rec.values.min():.1f}, {rec.values.max():.1f}] V, max |dV/dt| = {np.abs(np.diff(rec.values)).max():.2f} V/s")


if __name__ == "__main__":
    main()
