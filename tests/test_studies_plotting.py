# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
import numpy as np
import pytest

import bolts
from bolts.studies.map2d import grid
from bolts.studies.sensitivity import one_at_a_time
from bolts.studies.sweep import sweep
from bolts.waveforms.step_ramp_sine import step


def _opposing_dip(params):
    rec = step(-400.0, 60.0, 1.0, 10.0)
    return bolts.run_transient(bolts.build_network(params, rec), params).summary()["di_min_mA"]


def test_sweep_over_the_pfe_limit(params):
    rows = sweep(params, "pfe.max_voltage_kV_per_end", [0.75, 2.5], lambda p: {"di_min_mA": _opposing_dip(p)})
    assert rows[0]["di_min_mA"] < -300 and abs(rows[1]["di_min_mA"]) < 50 and rows[0]["key"] == "pfe.max_voltage_kV_per_end"


def test_one_at_a_time_sensitivity_orders_by_swing(params):
    p = params.with_overrides({"pfe.max_voltage_kV_per_end": 0.75})
    rows = one_at_a_time(p, ["pfe.max_voltage_kV_per_end", "cable.capacitance_uF_per_km"], _opposing_dip, 0.1)
    assert rows[0]["key"] == "pfe.max_voltage_kV_per_end" and rows[0]["swing"] > rows[1]["swing"]


def test_map2d_shape(params):
    g = grid(params, "pfe.max_voltage_kV_per_end", [0.75, 2.5], "pfe.feed_current_A", [0.9, 1.0, 1.1], _opposing_dip)
    assert g.shape == (3, 2) and np.all(np.isfinite(g))


def test_plot_result(params, example_record, tmp_path):
    pytest.importorskip("matplotlib")
    from bolts.plotting.timeseries import plot_result
    res = bolts.run_transient(bolts.build_network(params, example_record), params)
    assert plot_result(res, tmp_path / "p.png").exists()


def test_plot_compare_two_strengths_clips_the_q_margin(tmp_path):
    pytest.importorskip("matplotlib")
    from bolts.plotting.timeseries import plot_compare
    runs = []
    for scale in (1.0, 6.0):      # 6x the example storm against a 1.5 kV limit puts the light out, so the Q-margin clip is drawn
        p = bolts.load_parameters(overrides={"pfe.max_voltage_kV_per_end": 0.75, "forcing.scale": scale})
        runs.append(bolts.run_transient(bolts.build_network(p, bolts.load_waveform(params=p)), p))
    assert plot_compare(runs, ["x1", "x6"], tmp_path / "c.png").exists()


def test_plot_without_matplotlib_gives_a_clear_message(monkeypatch):
    import builtins
    real = builtins.__import__

    def fake(name, *a, **k):
        if name.startswith("matplotlib"):
            raise ImportError("no matplotlib")
        return real(name, *a, **k)
    monkeypatch.setattr(builtins, "__import__", fake)
    from bolts.plotting.style import require_matplotlib
    with pytest.raises(ImportError, match="bolts\\[plots\\]"):
        require_matplotlib()


def test_node_profile_and_to_dataframe(params, example_record, tmp_path):
    pytest.importorskip("matplotlib")
    from bolts.plotting.network import node_distances_km, plot_node_profile
    res = bolts.run_transient(bolts.build_network(params, example_record), params)
    d = node_distances_km(res)
    assert d[0] == 0.0 and d.max() == pytest.approx(750.8) and len(d) == 26
    assert plot_node_profile(res, tmp_path / "prof").exists()
    pd = pytest.importorskip("pandas")
    assert isinstance(res.to_dataframe(), pd.DataFrame)
