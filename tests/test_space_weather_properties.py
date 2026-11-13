# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
import numpy as np
import pytest

from bolts.errors import NotImplementedYet
from bolts.properties.constant import ConstantRLCG
from bolts.space_weather.from_efield import net_voltage_from_efield
from bolts.space_weather.gmd_source import GMDSource
from bolts.waveforms.base import Record


def test_gmd_source_spreads_the_voltage_and_applies_direction():
    rec = Record(np.arange(3.0), np.array([0.0, 10.0, -20.0]))
    emf = GMDSource(rec, feed_direction=-1, emf_share=0.5).span_emf_V(4)
    assert emf.shape == (3, 4) and np.allclose(emf.sum(axis=1), -0.5 * rec.values)
    w = GMDSource(rec).span_emf_V(2, weights=np.array([1.0, 3.0]))
    assert np.allclose(w[1], [2.5, 7.5])


def test_efield_conversion():
    e = Record(np.arange(3.0), np.array([0.0, 0.1, 0.2]), unit="V/km")
    assert net_voltage_from_efield(e, 750.0).values[-1] == pytest.approx(150.0)


def test_constant_provider_units(params):
    v = ConstantRLCG.from_parameters(params).rlcg(100.0)
    assert v.r_ohm_per_km == 1.0 and v.c_F_per_km == pytest.approx(0.2e-6) and v.g_S_per_km == 0.0 and not v.inductance_known
    v2 = ConstantRLCG.from_parameters(params.with_overrides({"cable.inductance_mH_per_km": 0.5})).rlcg(0.0)
    assert v2.inductance_known and v2.l_H_per_km == pytest.approx(0.5e-3)


@pytest.mark.parametrize("mod", ["freq_dependent", "catalog"])
def test_future_providers_are_stubs(mod):
    import importlib
    m = importlib.import_module(f"bolts.properties.{mod}")
    with pytest.raises(NotImplementedYet):
        m.Provider()
