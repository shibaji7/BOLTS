# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
import pytest

import bolts
from bolts.config.loader import load_parameters
from bolts.config.overrides import parse_overrides
from bolts.config.provenance import Param, Status
from bolts.errors import ConfigError, MissingParameter


def test_defaults_load_and_carry_provenance(params):
    c = params.counts()
    assert c["sourced"] >= 15 and c["assumed"] >= 20 and c["unknown"] >= 10
    p = params.param("cable", "resistance_ohm_per_km")
    assert p.status is Status.SOURCED and "479" in p.source and p.unit == "ohm/km"


def test_unknown_parameter_refuses_to_guess(params):
    with pytest.raises(MissingParameter, match="inductance"):
        params.get("cable", "inductance_mH_per_km")
    assert not params.has("cable", "inductance_mH_per_km")
    assert params.has("cable", "resistance_ohm_per_km")


def test_overrides_change_status_and_leave_original_alone(params):
    p2 = params.with_overrides({"pfe.max_voltage_kV_per_end": 0.75})
    assert p2.get("pfe", "max_voltage_kV_per_end") == 0.75 and p2.param("pfe", "max_voltage_kV_per_end").status is Status.OVERRIDE
    assert params.get("pfe", "max_voltage_kV_per_end") == 2.5
    assert p2.fingerprint() != params.fingerprint()


def test_bad_override_keys(params):
    with pytest.raises(ConfigError):
        params.with_overrides({"nope": 1})
    with pytest.raises(ConfigError):
        params.with_overrides({"pfe.nothing": 1})


def test_user_file_merges_bare_values_and_rejects_unknown_keys(tmp_path):
    f = tmp_path / "u.toml"
    f.write_text("[pfe]\nfeed_current_A = 1.2\n")
    p = load_parameters(f)
    assert p.get("pfe", "feed_current_A") == 1.2 and p.param("pfe", "feed_current_A").status is Status.OVERRIDE
    g = tmp_path / "bad.toml"
    g.write_text("[pfe]\nnot_a_key = 1\n")
    with pytest.raises(ConfigError, match="unknown parameter"):
        load_parameters(g)
    with pytest.raises(ConfigError):
        load_parameters(tmp_path / "missing.toml")


def test_validation_rejects_nonsense(params):
    with pytest.raises(ConfigError, match="positive"):
        load_parameters(overrides={"pfe.feed_current_A": -1.0})
    with pytest.raises(ConfigError, match="split_fraction"):
        load_parameters(overrides={"pfe.split_fraction_end_A": 1.5})


def test_parse_overrides():
    assert parse_overrides(["a.b=2.5", "c.d=true", 'e.f="x"', "g.h=word", "i.j=[1,2]"]) == {"a.b": 2.5, "c.d": True, "e.f": "x", "g.h": "word", "i.j": [1, 2]}
    with pytest.raises(ConfigError):
        parse_overrides(["no_equals"])


def test_table_and_param_require():
    assert Param("s", "n", "TBD", "", Status.UNKNOWN, "why").is_unknown
    assert "| key |" in bolts.load_parameters().table_md()
