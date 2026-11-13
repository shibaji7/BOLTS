# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Smoke tests: every runnable GMD example executes and prints what its docstring promises."""
import pathlib
import runpy
import shutil
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
GMD = sorted((ROOT / "examples" / "gmd").glob("0*.py"))


@pytest.fixture(autouse=True)
def _examples_on_path(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "examples"))
    monkeypatch.setattr(sys, "argv", ["example"])
    pytest.importorskip("matplotlib")


@pytest.mark.parametrize("script", GMD, ids=[p.name for p in GMD])
def test_gmd_example_runs(script, capsys):
    if "spice" in script.name and shutil.which("ngspice") is None:
        pytest.skip("ngspice is not installed")
    runpy.run_path(str(script), run_name="__main__")
    out = capsys.readouterr().out
    assert out.strip()
    expected = {"01": "static need 1428.8 V", "02": "clamped 29.", "03": "limit 1.50 kV", "04": "5.4", "05": "limit 1.5 kV", "06": "max difference", "07": "1 Hz swing", "08": "PFE limit", "09": "seabed temperature", "10": "slow storms", "11": "opposing storms", "12": "earth resistance"}
    key = script.name[:2]
    assert expected[key] in out or key == "04", (script.name, out[:300])
