# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""v0.2 round 4: ground potential rise and the landing earth from the soil and the rod electrode."""
import math

import numpy as np
import pytest

import bolts
from bolts.earthing.electrode_resistance import (
    landing_resistance_from_parameters,
    rods_in_line_ohm,
    single_rod_ohm,
)
from bolts.earthing.gpr import gpr_metrics, ground_potential_rise_V, required_resistance_ohm
from bolts.earthing.soil import wenner_resistivity_ohm_m
from bolts.waveforms.step_ramp_sine import ramp_hold

ROD = {"earthing.rod_count": 4, "earthing.rod_length_m": 3.0, "earthing.rod_radius_m": 0.01, "earthing.rod_spacing_m": 3.0}


def test_gpr_is_current_times_resistance():
    assert ground_potential_rise_V(2.0, 3.0) == 6.0
    assert np.allclose(ground_potential_rise_V(np.array([1.0, -2.0]), 3.0), [3.0, -6.0])
    assert required_resistance_ohm(1.0, 20.0) == 20.0 and required_resistance_ohm(2.5, 90.0) == pytest.approx(36.0)
    with pytest.raises(ValueError):
        required_resistance_ohm(0.0, 20.0)


def test_gpr_metrics_on_a_known_record():
    i = np.array([1.0, -4.0, 8.0, 12.0, 0.5])            # A through a 5 ohm electrode: 5, 20, 40, 60 and 2.5 V (polarity does not matter)
    m = gpr_metrics(i, 5.0, 2.0)
    assert m["earth_gpr_peak_V"] == 60.0
    assert m["earth_time_above_nominal_s"] == 2 * 2.0          # 40 V and 60 V are above 20 V (20 V itself is not)
    assert m["earth_time_above_exceptional_s"] == 0.0          # nothing reaches 90 V
    assert gpr_metrics(i, 5.0, 2.0, 20.0, 50.0)["earth_time_above_exceptional_s"] == 1 * 2.0      # a 50 V limit is exceeded by the 60 V sample only


def test_landing_resistance_from_the_rods_and_the_soil(params):
    assert landing_resistance_from_parameters(params) == 3.0                                # nothing given: the sourced bound
    p = params.with_overrides({"earthing.soil_resistivity_ohm_m": 100.0, **ROD})
    rs = single_rod_ohm(100.0, 3.0, 0.01)
    assert rs == pytest.approx(100.0 / (2 * math.pi * 3.0) * (math.log(4 * 3.0 / 0.01) - 1))
    assert landing_resistance_from_parameters(p) == pytest.approx(rods_in_line_ohm(100.0, rs, 3.0, 4))
    one = params.with_overrides({"earthing.soil_resistivity_ohm_m": 100.0, **ROD, "earthing.rod_count": 1})
    assert landing_resistance_from_parameters(one) == pytest.approx(rs)
    partial = params.with_overrides({"earthing.soil_resistivity_ohm_m": 100.0, "earthing.rod_count": 4})     # missing rod geometry: still the bound
    assert landing_resistance_from_parameters(partial) == 3.0
    with pytest.raises(ValueError):
        landing_resistance_from_parameters(params.with_overrides({"earthing.soil_resistivity_ohm_m": 100.0, **ROD, "earthing.rod_count": 7}))


def test_wenner_roundtrip_for_thin_electrodes():
    rho = 80.0
    assert wenner_resistivity_ohm_m(4.0, 1e-9, rho / (2 * math.pi * 4.0)) == pytest.approx(rho, rel=1e-6)       # b -> 0: rho = 2 pi a R


def test_earth_resistance_enters_the_static_need(params):
    base = bolts.build_network(params, None).meta
    p = params.with_overrides({"earthing.soil_resistivity_ohm_m": 100.0, **ROD})
    poor = bolts.build_network(p, None).meta
    r_e = landing_resistance_from_parameters(p)
    assert poor["r_earth_ohm"] == pytest.approx(r_e) and base["r_earth_ohm"] == 3.0
    assert poor["static_need_V"] - base["static_need_V"] == pytest.approx(2.0 * (r_e - 3.0) * 1.0)            # I_set x both landing earths


def test_assess_reports_the_gpr(params, example_record):
    s = bolts.assess(bolts.run_transient(bolts.build_network(params, example_record), params))
    assert s["earth_resistance_ohm"] == 3.0 and s["earth_gpr_peak_V"] == pytest.approx(3.0, abs=0.01)         # 1 A x 3 ohm in a storm that barely moves the current
    assert s["earth_time_above_nominal_s"] == 0.0 and s["earth_time_above_exceptional_s"] == 0.0


def test_gpr_follows_the_current_in_a_storm_beyond_the_pfe_range(params):
    """+2 kV assisting (the PFE falls to 0 V): the line current is (E - V_rep)/R_loop = 1.70 A, so the earth sees 1.70 x 3 ohm."""
    rec = ramp_hold(2000.0, 60.0, 120.0, 1.0)
    p = params.with_overrides({"pfe.max_voltage_kV_per_end": 2.5})
    s = bolts.assess(bolts.run_transient(bolts.build_network(p, rec), p, dt_s=1.0))
    assert s["earth_gpr_peak_V"] == pytest.approx(1.70 * 3.0, rel=0.03)
    poor = p.with_overrides({"earthing.soil_resistivity_ohm_m": 300.0, **ROD})
    sp = bolts.assess(bolts.run_transient(bolts.build_network(poor, rec), poor, dt_s=1.0))
    assert sp["earth_gpr_peak_V"] > 20.0 and sp["earth_time_above_nominal_s"] > 0.0
