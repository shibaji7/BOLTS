# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
import shutil

import pytest

import bolts
from bolts.errors import BoltsError
from bolts.spice.compare import compare_voltages
from bolts.spice.netlist import netlist_text
from bolts.spice.run_ngspice import run_ngspice

needs_ngspice = pytest.mark.skipif(shutil.which("ngspice") is None, reason="ngspice is not installed")


def _short_run(params, example_record, dt=0.5, n=240):
    rec = example_record.__class__(example_record.t_s[:n], example_record.values[:n], "short")
    return bolts.run_transient(bolts.build_network(params, rec), params, dt_s=dt)


def test_netlist_text_is_self_consistent(params, example_record):
    res = _short_run(params, example_record)
    text = netlist_text(res.transient.system, res.transient.t_s, res.transient.v_tot_V)
    assert text.count("\nV_") == 27 and ".tran" in text and "wrdata" in text and "PWL(" in text
    with pytest.raises(ValueError):
        netlist_text(res.transient.system, res.transient.t_s, None)


def test_export_spice_writes_a_file(params, example_record, tmp_path):
    p = bolts.export_spice(_short_run(params, example_record), tmp_path / "net.cir")
    assert p.read_text().startswith("* BOLTS export")


@pytest.mark.spice
@needs_ngspice
def test_bolts_agrees_with_ngspice(params, example_record):
    res = _short_run(params, example_record)
    v = run_ngspice(res.transient.system, res.transient.t_s, res.transient.v_tot_V)
    c = compare_voltages(res.transient.nodes_V, v)
    assert c["max_rel"] < 1e-5, c


def test_missing_ngspice_is_a_clear_error(params, example_record, monkeypatch):
    monkeypatch.setattr("bolts.spice.run_ngspice.shutil.which", lambda _: None)
    res = _short_run(params, example_record)
    with pytest.raises(BoltsError, match="ngspice was not found"):
        run_ngspice(res.transient.system, res.transient.t_s, res.transient.v_tot_V)
