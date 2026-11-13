# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""The PFE current regulator, a first-order loop: the current error relaxes to the ramp-tracking value with time constant tau.

    x' + x/tau = (1/R_loop) dS/dt,    x = I_sense - I_set,   S = the loop's exogenous source (the induced voltage along the feed direction)

The transient solver integrates it EXACTLY over each step, x_new = x_ss + (x_old - x_ss) exp(-dt/tau) with x_ss = (tau/R_loop) dS/dt, so any
dt / tau is stable and accurate. The total voltage is clamped to [v_tot_min, v_tot_max] (the PFE's range) and, if ``slew_V_per_s`` is set, its change per step is limited to ``slew * dt``.
The error state is re-read from the circuit's actual current at every step, so there is no integrator wind-up: when the clamp or the slew limit releases, the loop
resumes from the real current error (the pfe_design behaviour)."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from ..mna.assemble import System
from ..mna.stamp import ControlledSource


@dataclass
class PowerFeedController:
    """Settings of the regulator plus the little algebra the transient loop needs (see :func:`bolts.mna.transient.run_transient`)."""

    sources: list[ControlledSource]
    sense_branch: str
    i_set_A: float
    tau_s: float
    v_tot_max_V: float
    disturbance_fn: Callable[[np.ndarray], np.ndarray] | None = None
    v_tot_min_V: float = 0.0
    branch_of_source: dict | None = None          # filled by the network builder: id(source) -> branch name
    slew_V_per_s: float | None = None             # fastest rate the PFE total voltage can change (slow ramp-up/down, Chesnoy p. 397); None = no limit

    def unit_rhs(self, system: System) -> np.ndarray:
        """Change of the right-hand side for 1 V of v_tot: each controlled source s = weight v_tot sits in a branch row whose
        right-hand side is -s."""
        u = np.zeros(system.n)
        for src in self.sources:
            u[system.branch_row(self.branch_of_source[id(src)])] -= src.weight
        return u

    def sense_row(self, system: System) -> int:
        """Unknown-vector position of the sensed current."""
        return system.branch_row(self.sense_branch)

    def disturbance(self, t_s: np.ndarray) -> np.ndarray:
        """The loop's exogenous source ``S(t)`` (the induced voltage seen by the loop); only its slope enters the regulator."""
        return np.zeros(len(t_s)) if self.disturbance_fn is None else self.disturbance_fn(t_s)

    def v_tot_for_set_current(self, i_dc_at_zero_A: float, beta_dc_A_per_V: float) -> float:
        """The v_tot for which the DC sensed current equals the set point (linear: i = i0 + beta v)."""
        return (self.i_set_A - i_dc_at_zero_A) / beta_dc_A_per_V
