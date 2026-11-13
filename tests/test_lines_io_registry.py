# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
import cmath
import math

import numpy as np
import pytest

from bolts import registry
from bolts.errors import NotImplementedYet
from bolts.io.readers import read_json, read_series_csv
from bolts.io.writers import write_json, write_series_csv
from bolts.lines.bergeron import BergeronLine
from bolts.lines.lumped_ladder import section_edges_km, section_lengths_km
from bolts.lines.sectioning import sections_for_rise_time
from bolts.lines.telegrapher import characteristic_impedance_ohm, lossless_delay_s, propagation_constant_per_m


def test_lossless_line_impedance_and_delay():
    l_h, c_f = 250e-9, 100e-12                                  # a coaxial-like line, per metre
    z0 = characteristic_impedance_ohm(0.0, l_h, 0.0, c_f, 1e5)
    assert z0.real == pytest.approx(math.sqrt(l_h / c_f)) and abs(z0.imag) < 1e-9
    g = propagation_constant_per_m(0.0, l_h, 0.0, c_f, 1e5)
    assert g.real == pytest.approx(0.0, abs=1e-12) and g.imag == pytest.approx(2 * math.pi * 1e5 * math.sqrt(l_h * c_f))
    assert lossless_delay_s(750e3, l_h, c_f) == pytest.approx(750e3 * math.sqrt(l_h * c_f))


def test_rc_cable_is_diffusive():
    g = propagation_constant_per_m(1e-3, 0.0, 0.0, 0.2e-9, 1e-3)          # 1 ohm/km, 0.2 uF/km at 1 mHz
    assert g.real == pytest.approx(g.imag, rel=1e-9)                       # equal attenuation and phase: diffusion
    assert cmath.phase(characteristic_impedance_ohm(1e-3, 0.0, 0.0, 0.2e-9, 1e-3)) == pytest.approx(-math.pi / 4)


def test_sectioning_rule():
    n = sections_for_rise_time(750.0, 0.5, 200e-9, 1e-6)       # a microsecond rise needs many sections
    assert n > 1000
    assert sections_for_rise_time(750.0, 0.5, 200e-9, 10.0) == 1               # a slow drive needs one
    with pytest.raises(ValueError):
        sections_for_rise_time(1.0, 1.0, 1.0, 0.0)


def test_ladder_sections():
    assert section_lengths_km(750.0, 5).tolist() == [150.0] * 5 and section_edges_km(10.0, 4).tolist() == [0.0, 2.5, 5.0, 7.5, 10.0]
    with pytest.raises(ValueError):
        section_lengths_km(1.0, 0)
    with pytest.raises(NotImplementedYet):
        BergeronLine()


def test_builtin_waveforms_are_registered():
    names = registry.waveform_names()
    assert {"step", "ramp", "sine", "ramp_hold", "double_exponential", "heidler", "csv"} <= set(names)
    r = registry.get_waveform("sine")(2.0, 0.25, duration_s=4.0, dt_s=0.5)
    assert r.values.max() == pytest.approx(2.0)
    with pytest.raises(KeyError):
        registry.get_waveform("nothing")
    registry.register_waveform("mine", lambda: 1)
    assert registry.get_waveform("mine")() == 1


def test_io_round_trip(tmp_path):
    cols = {"t_s": np.array([0.0, 1.0, 2.0]), "v": np.array([1.5, -2.0, 3.25])}
    p = write_series_csv(tmp_path / "x" / "s.csv", cols)
    back = read_series_csv(p)
    assert back["v"].tolist() == [1.5, -2.0, 3.25]
    write_json(tmp_path / "j.json", {"a": np.float64(1.5), "b": np.arange(2), "c": object})
    j = read_json(tmp_path / "j.json")
    assert j["a"] == 1.5 and j["b"] == [0, 1] and "object" in j["c"]


def test_fit_zener_is_a_documented_slot():
    from bolts.elements.fit_zener import fit_zener
    with pytest.raises(NotImplementedYet):
        fit_zener()
