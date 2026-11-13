# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Shared helpers for the example scripts: repository paths, the default parameters, an output directory per script."""
from __future__ import annotations

import pathlib

import bolts

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXAMPLE_CSV = ROOT / "data" / "example_vind_1s.csv"


def out_dir(script_file: str) -> pathlib.Path:
    """``outputs/examples/<script name>/`` (created)."""
    d = ROOT / "outputs" / "examples" / pathlib.Path(script_file).stem
    d.mkdir(parents=True, exist_ok=True)
    return d


def tight_limit_params(kv_per_end: float = 0.75):
    """Default parameters with the PFE limit changed (0.75 kV per end = the 1.5 kV total what-if of the pfe_design study)."""
    return bolts.load_parameters(overrides={"pfe.max_voltage_kV_per_end": kv_per_end})
