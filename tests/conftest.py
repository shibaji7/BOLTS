# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
import pathlib

import pytest

import bolts

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "data" / "example_vind_1s.csv"
LEGACY_BURST = ROOT / "data" / "legacy_pfe_design_burst_1s.csv"   # the old pfe_design record, kept for the regression test


@pytest.fixture(scope="session")
def params():
    return bolts.load_parameters()


@pytest.fixture(scope="session")
def example_record(params):
    return bolts.load_waveform(EXAMPLE, params=params)


@pytest.fixture
def legacy_record(params):
    """The pfe_design example record (72 V storm plus a 120 V, 5 s burst) used for the numerical regression."""
    return bolts.load_waveform(LEGACY_BURST, params=params)
