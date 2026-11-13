# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
import numpy as np
import pytest

from bolts.waveforms.base import Record
from bolts.waveforms.combine import concatenate, plus
from bolts.waveforms.csv_record import read_csv_record, record_from_parameters
from bolts.waveforms.double_exp import double_exponential
from bolts.waveforms.heidler import heidler
from bolts.waveforms.step_ramp_sine import ramp, ramp_hold, sine, step
from bolts.waveforms.window import piecewise_hold, window


def test_record_validates():
    with pytest.raises(ValueError):
        Record(np.array([0.0, 1.0]), np.array([1.0]))
    with pytest.raises(ValueError):
        Record(np.array([0.0, 0.0]), np.array([1.0, 2.0]))
    r = Record(np.array([0.0, 1.0, 2.0]), np.array([0.0, 2.0, 2.0]))
    assert r.dt_s == 1.0 and r.duration_s == 2.0 and list(r.rate_per_s) == [2.0, 0.0] and r.sample(0.5) == 1.0


def test_transformations():
    r = ramp(2.0, duration_s=10, dt_s=1.0)
    assert r.scaled(3).values[-1] == 60.0 and r.compressed(10).t_s[-1] == 1.0
    assert len(r.resampled(0.5).t_s) == 21
    w = window(r, 3.0, 6.0)
    assert w.t_s[0] == 0.0 and w.values[0] == 6.0
    with pytest.raises(ValueError):
        window(r, 3.1, 3.2)
    assert plus(r, r).values[-1] == 40.0
    c = concatenate(r, r)
    assert c.t_s[0] == 0.0 and np.all(np.diff(c.t_s) > 0)
    h = piecewise_hold(Record(np.array([0.0, 2.0, 4.0]), np.array([1.0, 2.0, 3.0])), np.array([0.0, 1.9, 2.0, 5.0]))
    assert list(h) == [1.0, 1.0, 2.0, 3.0]


def test_elementary_waveforms():
    assert step(5.0, duration_s=10, dt_s=1.0, t_step_s=3.0).values[2:5].tolist() == [0.0, 5.0, 5.0]
    s = sine(2.0, 0.25, duration_s=4.0, dt_s=0.5)
    assert abs(s.values[2] - 2.0) < 1e-12               # the first peak, at t = 1 s
    rh = ramp_hold(10.0, 5.0, 5.0, 1.0)
    assert rh.values[5] == 10.0 and rh.values[-1] == 10.0


def test_double_exponential_and_heidler_peaks():
    d = double_exponential(30e3, 1e-6, 100e-6, 1e-3, 1e-8)
    assert d.values.max() == pytest.approx(30e3, rel=1e-3) and d.unit == "A"
    h = heidler(30e3, 1.8e-6, 95e-6, 10, 5e-4, 1e-8)
    assert h.values.max() == pytest.approx(30e3, rel=2e-3)
    with pytest.raises(ValueError):
        double_exponential(1.0, 2e-6, 1e-6, 1e-3, 1e-8)


def test_csv_read_variants(tmp_path):
    p = tmp_path / "v.csv"
    p.write_text("time,volts\n" + "\n".join(f"{100 + 0.5 * i},{0.1 * i}" for i in range(200)) + "\n")
    r = read_csv_record(p, "time", "volts", window_s=(10.0, 20.0), scale=2.0)
    assert r.t_s[0] == 0.0 and r.t_s[-1] == pytest.approx(10.0) and r.values[0] == pytest.approx(4.0)
    assert np.allclose(np.diff(read_csv_record(p, "time", "volts", dt_s=0.1).t_s), 0.1)
    q = tmp_path / "iso.csv"
    q.write_text("when,v\n2024-05-10T22:10:00.000,0\n2024-05-10T22:10:00.200,1\n2024-05-10T22:10:00.400,2\n")
    assert read_csv_record(q, "when", "v", time_format="iso").t_s[1] == pytest.approx(0.2)
    with pytest.raises(KeyError, match="columns are"):
        read_csv_record(p, "nope", "volts")
    with pytest.raises(FileNotFoundError):
        read_csv_record(tmp_path / "missing.csv")
    with pytest.raises(ValueError, match="time_format"):
        read_csv_record(p, "time", "volts", time_format="weird")


def test_record_from_parameters(params, example_record):
    assert example_record.dt_s == 1.0 and example_record.values.min() < -50
    r = record_from_parameters(params.with_overrides({"forcing.scale": 0.5}))
    assert r.values.min() == pytest.approx(0.5 * example_record.values.min())
