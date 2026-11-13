# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
import json

import numpy as np
import pytest

import bolts
from bolts.cli import main
from bolts.errors import BoltsError
from bolts.io.readers import read_json, read_series_csv


def test_public_api_surface():
    for name in ("load_parameters", "load_waveform", "build_network", "run_transient", "assess", "export_spice", "register_element", "Result"):
        assert hasattr(bolts, name) and name in bolts.__all__
    assert bolts.__version__ == "0.2.3"


def test_end_to_end_matches_the_pfe_design_example_summary(params, legacy_record):
    """Reference numbers from the pfe_design study (output/window_summary.csv): the same record, 1.5 kV total limit, tau = 5 ms."""
    p = params.with_overrides({"pfe.max_voltage_kV_per_end": 0.75})
    res = bolts.run_transient(bolts.build_network(p, legacy_record), p)
    s = bolts.assess(res)
    assert s["di_min_mA"] == pytest.approx(-139.830, abs=0.05)
    assert s["frac_pfe_clamped"] == pytest.approx(0.019151, abs=1e-4)
    assert s["min_margin_dB"] == pytest.approx(10.733, abs=0.01)
    assert s["jump_bound_mA"] == pytest.approx(169.996, abs=0.01)
    assert s["frac_time_outage"] == 0.0 and s["adaptive_250G_mean_rate_fraction"] == 1.0
    assert s["v_pfe_max_V"] == pytest.approx(1500.0) and s["v_cs_peak_V"] == pytest.approx(747.4, abs=1.0)


def test_run_transient_needs_a_record_or_axis(params):
    net = bolts.build_network(params, None)
    with pytest.raises(ValueError, match="no record"):
        bolts.run_transient(net, params)
    res = bolts.run_transient(net, params, t_s=np.arange(0.0, 11.0))
    assert res.summary()["di_min_mA"] == pytest.approx(0.0, abs=1e-6)


def test_save_writes_series_summary_manifest(params, example_record, tmp_path):
    p = params
    res = bolts.run_transient(bolts.build_network(p, example_record), p)
    out = res.save(tmp_path / "out", extra_manifest={"note": "test"})
    series = read_series_csv(out / "series.csv")
    assert {"t_s", "v_in_V", "v_pfe_total_V", "di_min_mA", "q_margin_dB"} <= set(series) and len(series["t_s"]) == 1801
    assert read_json(out / "manifest.json")["parameters_fingerprint"] == p.fingerprint() and read_json(out / "manifest.json")["note"] == "test"
    assert "adaptive_200G_ses" in json.loads((out / "summary.json").read_text())


def test_cli_run_params_validate_doctor(tmp_path, capsys):
    assert main(["run", "--out", str(tmp_path / "r"), "--set", "pfe.max_voltage_kV_per_end=0.75", "--start", "400", "--end", "800"]) == 0
    out = capsys.readouterr().out
    assert "PFE total" in out and "wrote series.csv" in out and (tmp_path / "r" / "summary.json").exists()
    assert main(["params", "--filter", "repeater.", "--status", "unknown"]) == 0
    assert "zener_knee_current_A" in capsys.readouterr().out
    assert main(["validate"]) == 0
    assert main(["doctor"]) == 0 and "bolts 0.2.3" in capsys.readouterr().out


def test_cli_reports_errors_without_a_traceback(tmp_path, capsys):
    assert main(["run", "--csv", str(tmp_path / "missing.csv"), "--out", str(tmp_path)]) == 2
    assert "not found" in capsys.readouterr().err
    assert main(["params", "--set", "pfe.nothing=1"]) == 2


def test_load_waveform_without_params(tmp_path):
    f = tmp_path / "x.csv"
    f.write_text("a,b\n0,1\n1,2\n2,3\n")
    r = bolts.load_waveform(f, time_column="a", value_column="b")
    assert r.values.tolist() == [1.0, 2.0, 3.0]
    with pytest.raises(BoltsError):
        bolts.export_spice(bolts.build_network(bolts.load_parameters(), None), tmp_path / "n.cir")
