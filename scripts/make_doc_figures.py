#!/usr/bin/env python
# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Run the GMD examples and copy the figures the documentation uses into docs/figures/ (``make doc-figures``)."""
from __future__ import annotations

import pathlib
import runpy
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIG = ROOT / "docs" / "figures"
# (example script, produced file under outputs/examples/<stem>/, name used in the docs)
WANTED = [("02_storm_record", "run.png", "storm_run.png"), ("02_storm_record", "node_profile.png", "node_profile.png"), ("13_storm_impact", "run.png", "storm_impact.png"),
          ("03_pfe_limit_sweep", "pfe_limit.png", "pfe_limit.png"), ("04_regulator_tau", "regulator_tau.png", "regulator_tau.png"),
          ("05_amplitude_period_map", "amplitude_period_map.png", "amplitude_period_map.png")]


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(ROOT / "examples"))
    for stem in sorted({w[0] for w in WANTED}):
        runpy.run_path(str(ROOT / "examples" / "gmd" / f"{stem}.py"), run_name="__main__")
    for stem, produced, name in WANTED:
        shutil.copy(ROOT / "outputs" / "examples" / stem / produced, FIG / name)
        print("copied", name)


if __name__ == "__main__":
    main()
