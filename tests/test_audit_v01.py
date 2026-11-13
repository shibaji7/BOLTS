# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Checks added by the v0.1 audit: agreement with the pfe_design model on several records, and the paths that were not covered."""
import runpy
import shutil
import sys

import numpy as np
import pytest

import bolts
from bolts.cli import main
from bolts.config.loader import load_parameters
from bolts.elements.earth_electrode import EarthElectrode
from bolts.errors import ConfigError
from bolts.mna.assemble import assemble
from bolts.mna.stamp import Stamper
from bolts.waveforms.step_ramp_sine import sine

# worst repeater current change (mA) from pfe_design/src/model/circuit.py simulate() on the same records, 1 s / 25 ms / 0.5 s steps
PFE_DESIGN_REFERENCE = [
    # amplitude V, period s, duration s, dt s, per-end limit kV, pfe_design di_min mA, tolerance mA
    (500.0, 1.0, 120.0, 0.025, 0.75, -525.06, 0.2),
    (3000.0, 120.0, 600.0, 0.5, 0.75, -3585.70, 1.0),
    (3000.0, 120.0, 600.0, 0.5, 2.5, -3.93, 0.1),
]


@pytest.mark.parametrize("amp,per,dur,dt,kv,ref,tol", PFE_DESIGN_REFERENCE)
def test_agrees_with_pfe_design_on_sines(amp, per, dur, dt, kv, ref, tol):
    """Same circuit, regulator and limits: the worst current change agrees. The small remaining difference at high dV/dt comes from where the
    repeater sits in the capacitance ladder (BOLTS: half a span of cable capacitance on each side of the repeater; pfe_design lumps it
    at the repeater node), about 0.4 of the regulator ramp term, so at most 7 mA in the fastest case here."""
    p = load_parameters(overrides={"pfe.max_voltage_kV_per_end": kv})
    rec = sine(amp, 1.0 / per, duration_s=dur, dt_s=dt)
    s = bolts.assess(bolts.run_transient(bolts.build_network(p, rec), p, dt_s=dt))
    assert s["di_min_mA"] == pytest.approx(ref, abs=tol)


def test_earth_electrode_is_a_shunt_to_the_sea():
    with pytest.raises(ValueError):
        EarthElectrode("e", "n", 0.0)
    st = Stamper(["n"])
    EarthElectrode("e", "n", 4.0).stamp(st)
    assert assemble(st).G[0, 0] == pytest.approx(0.25)


def test_user_toml_errors_are_reported(tmp_path):
    bad = tmp_path / "bad.toml"
    bad.write_text('[pfe]\nregulator_response_s = { unit = "s" }\n')
    with pytest.raises(ConfigError):
        load_parameters(bad)
    bad.write_text('[pfe]\nregulator_response_s = { value = 0.01, status = "nonsense" }\n')
    with pytest.raises(ConfigError):
        load_parameters(bad)


def test_cli_spice_writes_and_compares(tmp_path, capsys):
    out = tmp_path / "n.cir"
    csv = "data/example_vind_1s.csv"
    assert main(["spice", "--csv", csv, "--start", "0", "--end", "120", "--dt", "0.5", "--out", str(out)]) == 0
    assert out.exists() and "wrote" in capsys.readouterr().out
    if shutil.which("ngspice"):
        assert main(["spice", "--csv", csv, "--start", "0", "--end", "120", "--dt", "0.5", "--out", str(out), "--run"]) == 0
        assert "BOLTS against ngspice" in capsys.readouterr().out


def test_python_dash_m_bolts_runs(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["bolts", "doctor"])
    with pytest.raises(SystemExit) as e:
        runpy.run_module("bolts", run_name="__main__")
    assert e.value.code == 0 and "bolts 0.2.1" in capsys.readouterr().out


def test_physical_constants():
    from bolts import constants
    assert pytest.approx(4e-7 * np.pi, rel=1e-8) == constants.MU0_H_PER_M
    assert pytest.approx(1.0, rel=1e-8) == constants.C_M_PER_S ** 2 * constants.MU0_H_PER_M * constants.EPS0_F_PER_M
