# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""The transient run: backward Euler on the MNA system, with an optional PFE regulator integrated exactly over each step."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..errors import BoltsError
from .assemble import System
from .dc_op import dc_sensitivity, solve_dc
from .integrators import get_integrator
from .linear_solve import LUSolver
from .newton import loop_resistance, newton_solve


@dataclass
class TransientResult:
    """Everything a run produces, on the time axis ``t_s``. Rows of ``x`` are time steps; columns are the MNA unknowns (node voltages
    first, then the series-branch currents), so use :meth:`node_V` / :meth:`branch_I` instead of indexing by hand."""

    system: System
    t_s: np.ndarray
    x: np.ndarray                 # (nt, n) unknowns
    v_tot_V: np.ndarray           # PFE total voltage (nan without a controller)
    clamped: np.ndarray           # the PFE sat at a voltage limit during this step
    i_sense_A: np.ndarray         # the current the regulator senses (nan without a controller)
    r_loop_ohm: float             # loop resistance seen by the regulator (nan without one)
    slew_limited: np.ndarray | None = None    # the slew limit held the voltage back during this step
    limit_state: np.ndarray | None = None     # +1 sat at the upper limit, -1 at the lower limit (0 V), 0 in current-control mode

    def node_V(self, name: str) -> np.ndarray:
        """Voltage of the named node against the sea (V), one value per time step."""
        return self.x[:, self.system.node_index(name)]

    @property
    def nodes_V(self) -> np.ndarray:
        """All node voltages, shape (nt, n_nodes), in the order of ``system.node_names``."""
        return self.x[:, : self.system.n_nodes]

    def branch_I(self, name: str) -> np.ndarray:
        """Current in the named series branch (A), positive from its node ``a`` to its node ``b``."""
        return self.x[:, self.system.branch_row(name)]

    @property
    def branches_I(self) -> np.ndarray:
        """All branch currents, shape (nt, n_branches), in the order of ``system.branches``."""
        return self.x[:, self.system.n_nodes:]


def run_transient(system: System, t_s: np.ndarray, controller=None, integrator: str = "backward_euler", newton: bool | None = None) -> TransientResult:
    """March the circuit through time on the fixed axis ``t_s``.

    Without a ``controller`` this is a plain linear transient: one cached LU factorisation, one back-substitution per step.
    With a ``controller`` (the PFE regulator) the supply voltage is unknown at every step. The loop is first-order, so its error state is
    advanced exactly over the step; the new supply voltage then follows from the circuit's *linear sensitivity* to that voltage, which costs
    one extra back-substitution per step, not an iteration. The state is clamped to the supply's voltage limits and the clamp is recorded.

    A network with nonlinear elements (``system.has_nonlinear``) takes the Newton path instead (:func:`_run_newton`): same regulator logic, but each step is
    solved by iteration, so the cached factorisation and the linear sensitivity are not used. ``newton=True`` forces that path for a linear network
    (the tests use it to check that both paths agree); ``newton=False`` refuses a nonlinear one.
    """
    if newton is None:
        newton = system.has_nonlinear
    if newton:
        return _run_newton(system, np.asarray(t_s, float), controller, integrator)
    if system.has_nonlinear:
        raise BoltsError("this network has nonlinear elements; run it with newton=True or leave newton unset")
    t_s = np.asarray(t_s, float)
    nt = len(t_s)
    dt = float(t_s[1] - t_s[0])
    if not np.allclose(np.diff(t_s), dt, rtol=1e-9, atol=1e-15):
        raise BoltsError("the time axis must have a fixed step")
    A, c_dt = get_integrator(integrator)(system.G, system.C, dt)   # A = G + C/dt for backward Euler; constant, because dt is fixed
    lu = LUSolver(A)                                               # factor once, reuse at every step
    b_exo = system.exogenous_rhs(t_s)
    x = np.zeros((nt, system.n))
    v_tot = np.full(nt, np.nan)
    clamped = np.zeros(nt, bool)
    slew_limited = np.zeros(nt, bool)
    limit_state = np.zeros(nt, int)
    i_sense = np.full(nt, np.nan)

    if controller is None:
        x_prev = solve_dc(system, b_exo[0])      # start in DC equilibrium so the first sample is not an artificial step
        for k in range(nt):
            x[k] = x_prev = lu.solve(b_exo[k] + c_dt @ x_prev)
        return TransientResult(system, t_s, x, v_tot, clamped, i_sense, float("nan"))

    unit = controller.unit_rhs(system)                      # RHS change for one volt of v_tot
    sense_row = controller.sense_row(system)                # the branch whose current the regulator holds
    beta_dc = dc_sensitivity(system, unit, sense_row)       # A/V at DC = 1 / R_loop (capacitors open)
    r_loop = 1.0 / beta_dc
    dx_unit = lu.solve(unit)                                # one-step response of ALL unknowns to one volt of v_tot (linearity)
    beta = float(dx_unit[sense_row])                        # one-step current change per volt: a bit below beta_dc while C is charging
    s_tot = controller.disturbance(t_s)                     # the loop's exogenous source, for the ramp-tracking term

    # initial state: the steady state at the first sample, current held at the set point if the PFE can
    base0 = solve_dc(system, b_exo[0])
    v0 = controller.v_tot_for_set_current(float(base0[sense_row]), beta_dc)
    v_cur = min(max(v0, controller.v_tot_min_V), controller.v_tot_max_V)
    x_prev = solve_dc(system, b_exo[0] + v_cur * unit)
    x_err = float(x_prev[sense_row]) - controller.i_set_A
    decay = float(np.exp(-dt / controller.tau_s))
    for k in range(nt):
        # 1. trial step: where would the circuit go if the PFE voltage stayed as it is?
        x0 = lu.solve(b_exo[k] + c_dt @ x_prev + v_cur * unit)
        i0 = float(x0[sense_row])
        # 2. the loop wants the current error to follow x' + x/tau = (dS/dt)/R_loop; for a ramp-like disturbance the steady error is x_ss
        x_ss = controller.tau_s * ((s_tot[k] - s_tot[k - 1]) / dt if k else 0.0) / r_loop
        target = controller.i_set_A + x_ss + (x_err - x_ss) * decay  # exact first-order update over the step (any dt/tau)
        # 3. the voltage change that moves the sensed current from the trial value to the target, using the linear sensitivity
        new = v_cur + (target - i0) / beta
        # 4. the PFE has voltage limits: saturate, and remember that it did (this is when the current really leaves its set point)
        clamped[k] = new < controller.v_tot_min_V or new > controller.v_tot_max_V
        limit_state[k] = 1 if new > controller.v_tot_max_V else (-1 if new < controller.v_tot_min_V else 0)
        new = min(max(new, controller.v_tot_min_V), controller.v_tot_max_V)
        if controller.slew_V_per_s is not None:        # the PFE cannot change its output faster than its slew rate: hold back the step
            step_max = controller.slew_V_per_s * dt
            held = min(max(new, v_cur - step_max), v_cur + step_max)
            slew_limited[k] = abs(held - new) > 1e-9
            new = held
        # 5. finish the step with the voltage actually applied: by linearity, add the unit response scaled by the change
        xk = x0 + dx_unit * (new - v_cur)
        v_cur = new
        x_err = float(xk[sense_row]) - controller.i_set_A
        x[k] = x_prev = xk
        v_tot[k] = v_cur
        i_sense[k] = xk[sense_row]
    return TransientResult(system, t_s, x, v_tot, clamped, i_sense, r_loop, slew_limited, limit_state)


def _run_newton(system: System, t_s: np.ndarray, controller, integrator: str) -> TransientResult:
    """The transient loop for circuits with nonlinear elements. Per step: the regulator's target current (exact first-order update, as in the linear path),
    then one Newton solve of the circuit with the supply voltage as an extra unknown; if the supply is clamped or slew-limited it is pinned and the circuit
    is solved again. The loop resistance that scales the ramp-tracking term is re-evaluated at the previous operating point, because a nonlinear loop has no
    single value (for a linear network it is constant, so the result is the same as the linear path)."""
    nt = len(t_s)
    dt = float(t_s[1] - t_s[0])
    if not np.allclose(np.diff(t_s), dt, rtol=1e-9, atol=1e-15):
        raise BoltsError("the time axis must have a fixed step")
    A, c_dt = get_integrator(integrator)(system.G, system.C, dt)
    b_exo = system.exogenous_rhs(t_s)
    x = np.zeros((nt, system.n))
    v_tot = np.full(nt, np.nan)
    clamped = np.zeros(nt, bool)
    slew_limited = np.zeros(nt, bool)
    limit_state = np.zeros(nt, int)
    i_sense = np.full(nt, np.nan)

    if controller is None:
        x_prev, _ = newton_solve(system, system.G, b_exo[0], np.zeros(system.n))     # DC start (capacitors open)
        for k in range(nt):
            x[k] = x_prev = newton_solve(system, A, b_exo[k] + c_dt @ x_prev, x_prev)[0]
        return TransientResult(system, t_s, x, v_tot, clamped, i_sense, float("nan"), slew_limited, limit_state)

    unit = controller.unit_rhs(system)
    sense_row = controller.sense_row(system)
    s_tot = controller.disturbance(t_s)
    # initial state: the DC state at the first sample, current held at the set point if the PFE can
    x_prev, v_cur = newton_solve(system, system.G, b_exo[0], np.zeros(system.n), unit=unit, sense_row=sense_row, target=controller.i_set_A)
    v_clamped = min(max(v_cur, controller.v_tot_min_V), controller.v_tot_max_V)
    if v_clamped != v_cur:
        v_cur = v_clamped
        x_prev, _ = newton_solve(system, system.G, b_exo[0], x_prev, unit=unit, v_fixed=v_cur)
    r_loop0 = loop_resistance(system, x_prev, unit, sense_row)
    x_err = float(x_prev[sense_row]) - controller.i_set_A
    decay = float(np.exp(-dt / controller.tau_s))
    for k in range(nt):
        r_loop = loop_resistance(system, x_prev, unit, sense_row)
        x_ss = controller.tau_s * ((s_tot[k] - s_tot[k - 1]) / dt if k else 0.0) / r_loop
        target = controller.i_set_A + x_ss + (x_err - x_ss) * decay
        rhs = b_exo[k] + c_dt @ x_prev
        xk, new = newton_solve(system, A, rhs, x_prev, unit=unit, sense_row=sense_row, target=target, v0=v_cur)
        free = new
        clamped[k] = new < controller.v_tot_min_V or new > controller.v_tot_max_V
        limit_state[k] = 1 if new > controller.v_tot_max_V else (-1 if new < controller.v_tot_min_V else 0)
        new = min(max(new, controller.v_tot_min_V), controller.v_tot_max_V)
        if controller.slew_V_per_s is not None:
            step_max = controller.slew_V_per_s * dt
            held = min(max(new, v_cur - step_max), v_cur + step_max)
            slew_limited[k] = abs(held - new) > 1e-9
            new = held
        if abs(new - free) > 1e-12:                       # the supply could not follow the loop: pin it and solve the circuit again
            xk, _ = newton_solve(system, A, rhs, xk, unit=unit, v_fixed=new)
        v_cur = new
        x_err = float(xk[sense_row]) - controller.i_set_A
        x[k] = x_prev = xk
        v_tot[k] = v_cur
        i_sense[k] = xk[sense_row]
    return TransientResult(system, t_s, x, v_tot, clamped, i_sense, r_loop0, slew_limited, limit_state)

