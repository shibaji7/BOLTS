# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
import numpy as np
import pytest

from bolts.elements.lumped import Capacitor, Inductor, Resistor, VSource
from bolts.errors import BoltsError
from bolts.mna.assemble import assemble
from bolts.mna.dc_op import solve_dc
from bolts.mna.integrators import get_integrator
from bolts.mna.stamp import ConstantSource, Stamper
from bolts.mna.timestep import fixed_axis
from bolts.mna.transient import run_transient
from bolts.validation import run_all


def test_all_validation_cases_pass():
    for case in run_all():
        assert case.passed, (case.name, case.error, case.tolerance)


def test_dc_operating_point_divider_and_inductor_short():
    st = Stamper(["in", "mid", "out"])
    for el in (VSource("v", None, "in", ConstantSource(9.0)), Resistor("r1", "in", "mid", 100.0), Inductor("l", "mid", "out", 1e-3), Resistor("r2", "out", None, 200.0),
               Capacitor("c", "mid", None, 1e-6)):
        el.stamp(st)
    sysm = assemble(st)
    x = solve_dc(sysm, sysm.exogenous_rhs(np.array([0.0]))[0])
    assert x[sysm.node_index("mid")] == pytest.approx(6.0) and x[sysm.node_index("out")] == pytest.approx(6.0)     # L short, C open


def test_negative_r_or_l_rejected():
    st = Stamper(["a"])
    with pytest.raises(ValueError):
        st.add_series_branch("b", "a", None, -1.0)
    with pytest.raises(KeyError):
        st.node("nowhere")


def test_fixed_time_axis_and_integrators():
    assert list(fixed_axis(1.0, 0.25)) == [0.0, 0.25, 0.5, 0.75, 1.0]
    with pytest.raises(ValueError):
        fixed_axis(-1.0, 0.1)
    with pytest.raises(ValueError):
        get_integrator("rk45")
    from bolts.errors import NotImplementedYet
    with pytest.raises(NotImplementedYet):
        get_integrator("trapezoid")(np.eye(1), np.eye(1), 0.1)


def test_uneven_time_axis_is_rejected():
    st = Stamper(["a"])
    Resistor("r", "a", None, 1.0).stamp(st)
    VSource("v", None, "a", ConstantSource(1.0)).stamp(st)
    with pytest.raises(BoltsError, match="fixed step"):
        run_transient(assemble(st), np.array([0.0, 1.0, 3.0]))
