# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
import numpy as np
import pytest

import bolts
from bolts import registry
from bolts.elements import CableSegment, EarthElectrode, LinearZener, Repeater
from bolts.elements.lumped import Capacitor, Resistor, VSource
from bolts.errors import NotImplementedYet, TopologyError
from bolts.mna.stamp import ConstantSource
from bolts.network.graph import Network
from bolts.network.power_modes import PowerMode, end_weights, max_total_voltage_V
from bolts.waveforms.step_ramp_sine import ramp


def test_p2p_builder_structure(params):
    net = bolts.build_network(params, ramp(1.0, 10, 1.0))
    kinds = [type(e).__name__ for e in net.elements]
    assert kinds.count("CableSegment") == 13 and kinds.count("Repeater") == 12 and kinds.count("PFE") == 2
    sysm = net.compile()
    assert sysm.n_nodes == 26 and len(sysm.branches) == 27
    assert net.meta["span_km"] == pytest.approx(750.8 / 13) and net.meta["margin_A"] == pytest.approx(0.1)


def test_floating_node_is_rejected():
    net = Network()
    net.add(Resistor("r", "a", "b", 10.0))
    net.add(Capacitor("c", "b", "a", 1e-6))
    with pytest.raises(TopologyError, match="no path to the sea"):
        net.compile()


def test_power_modes():
    assert end_weights(PowerMode.DOUBLE_END, 0.5) == (0.5, -0.5)
    assert end_weights(PowerMode.SINGLE_END_A) == (1.0, 0.0)
    assert max_total_voltage_V(PowerMode.DOUBLE_END, 750.0, 0.5) == 1500.0
    assert max_total_voltage_V(PowerMode.SINGLE_END_B, 750.0) == 750.0
    assert max_total_voltage_V(PowerMode.DOUBLE_END, 750.0, 0.25) == 1000.0       # the larger share reaches its limit first


def test_linear_zener():
    z = LinearZener(56.0, 5.0, 1.0)
    assert z.drop_V(1.0) == 56.0 and z.drop_V(1.1) == pytest.approx(56.5)
    r, src = z.series_parameters()
    assert r == 5.0 and src == pytest.approx(-51.0)
    assert z.power_W(1.0) == 56.0


def test_element_validation_and_registry():
    with pytest.raises(ValueError):
        EarthElectrode("e", "n", 0.0)
    assert {"cable_segment", "repeater", "pfe", "earth_electrode"} <= set(registry.element_names())
    assert registry.get_element("cable_segment") is CableSegment
    with pytest.raises(KeyError):
        registry.get_element("flux_capacitor")
    registry.register_element("my_element", Repeater)
    assert registry.get_element("my_element") is Repeater


@pytest.mark.parametrize("mod,cls", [("branching_unit", "BranchingUnit"),
                                     ("relay", "Relay"), ("shunt_fault", "ShuntFault")])
def test_future_elements_are_documented_stubs(mod, cls):
    import importlib
    m = importlib.import_module(f"bolts.elements.{mod}")
    with pytest.raises(NotImplementedYet, match="ROADMAP"):
        getattr(m, cls)()


def test_future_modules_raise_not_implemented():
    from bolts.damage import arrester_energy, criteria, thermal_i2t
    from bolts.earthing.impulse_impedance import impulse_impedance_ohm
    from bolts.lightning import coupling, monte_carlo, protection_stage, statistics, stroke_parameters
    from bolts.mna.timestep import adaptive_axis
    from bolts.network.segments import split_into_powering_segments
    from bolts.network.switch_states import reconfigure
    from bolts.network.topology_trunk_branch import build_trunk_branch
    from bolts.waveforms.iec62305 import stroke
    for fn in (impulse_impedance_ohm, adaptive_axis, split_into_powering_segments, reconfigure, build_trunk_branch,
               arrester_energy.assess, criteria.assess, thermal_i2t.assess, coupling.run, monte_carlo.run, protection_stage.run,
               statistics.run, stroke_parameters.run):
        with pytest.raises(NotImplementedYet):
            fn()
    with pytest.raises(NotImplementedYet):
        stroke("first_positive", 1.0, 1e-7)


def test_branching_topology_is_not_built_yet(params):
    with pytest.raises(NotImplementedYet, match=r"v0\.3"):
        bolts.build_network(params, None, topology="trunk_branch")


def test_open_loop_network_without_controller_runs():
    from bolts.mna.transient import run_transient
    net = Network()
    net.add(VSource("vs", None, "in", ConstantSource(5.0)))
    net.add(Resistor("r", "in", "out", 100.0))
    net.add(Resistor("load", "out", None, 100.0))
    res = run_transient(net.compile(), np.arange(0.0, 3.0))
    assert res.node_V("out")[-1] == pytest.approx(2.5) and np.isnan(res.v_tot_V).all()
