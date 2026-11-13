# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Zener stack of the repeater. v0.1: linear, drop = Vz + rz (I - I_nom), as in the pfe_design study. The piecewise (v0.2), smooth
(v0.3) and electro-thermal (v0.5) models will keep this interface: they provide ``series_parameters()`` for linear use and, for
nonlinear use, a companion model at each Newton iterate."""
from __future__ import annotations

from dataclasses import dataclass

from ..errors import ConfigError


@dataclass(frozen=True)
class LinearZener:
    """Linearised Zener stack: ``drop = Vz + rz (I - I_nom)``. Valid while the current stays within tens of mA of nominal (storm band)."""

    vz_V: float
    rz_ohm: float
    i_nominal_A: float

    def series_parameters(self) -> tuple[float, float]:
        """(R, source) of the equivalent series branch: v_drop = rz I + (Vz - rz I_nom), so R = rz and the branch source is
        -(Vz - rz I_nom) (a drop opposes the current)."""
        return self.rz_ohm, -(self.vz_V - self.rz_ohm * self.i_nominal_A)

    def drop_V(self, i_A: float) -> float:
        """Voltage across the stack at line current ``i_A``."""
        return self.vz_V + self.rz_ohm * (i_A - self.i_nominal_A)

    def power_W(self, i_A: float) -> float:
        """Power dissipated in the stack (the thermal stress), drop times current."""
        return i_A * self.drop_V(i_A)


@dataclass(frozen=True)
class PiecewiseZener:
    """Zener stack with a knee: the voltage across the repeater as a piecewise-linear function of the line current (v0.2).

        I >= I_knee :     V = V_k + rz (I - I_knee)                     the stack conducts: the same law as :class:`LinearZener` (V_k = Vz + rz (I_knee - I_nom))
        0 <= I < I_knee:  V = V_k (f + (1 - f) I / I_knee)              the stack is off: the voltage falls with the current, to ``f V_k`` at zero current
        I < 0         :   V = f V_k + rz I                              reverse current flows through the stack's forward diodes

    The laws agree at the nominal current, so with the current at or above the knee the result is the linear model exactly. Below the knee the repeater stops
    holding its 56 V and the drop shrinks with the current, so a falling line current takes the supply's voltage need down with it. Two numbers are unknown:
    the knee current (``repeater.zener_knee_current_A``, vendor; studies sweep 0.5 to 0.99 of the nominal current) and how far the voltage falls below it,
    ``below_knee_fraction`` f (``repeater.zener_below_knee_fraction``). f = 0 is a resistive repeater circuit (the voltage falls to zero with the current: the
    strongest effect and the default here); f = 1 is a voltage that stays at V_k until the current reaches zero, as for a stack of laser diodes (no effect: the linear
    model). The real behaviour lies between them."""

    vz_V: float
    rz_ohm: float
    i_nominal_A: float
    i_knee_A: float
    below_knee_fraction: float = 0.0
    is_nonlinear = True

    def __post_init__(self):
        if not 0.0 < self.i_knee_A <= self.i_nominal_A:
            raise ConfigError("the Zener knee current must be positive and not above the nominal current")
        if not 0.0 <= self.below_knee_fraction <= 1.0:
            raise ConfigError("the below-knee voltage fraction must be between 0 and 1")
        if self.vz_V + self.rz_ohm * (self.i_knee_A - self.i_nominal_A) <= 0.0:
            raise ConfigError("the Zener voltage at the knee would not be positive")

    @property
    def v_knee_V(self) -> float:
        """Voltage across the stack at the knee current."""
        return self.vz_V + self.rz_ohm * (self.i_knee_A - self.i_nominal_A)

    @property
    def v_zero_V(self) -> float:
        """Voltage across the stack at zero current (``f V_k``)."""
        return self.below_knee_fraction * self.v_knee_V

    def drop_V(self, i_A: float) -> float:
        """Voltage across the stack at line current ``i_A``."""
        if i_A >= self.i_knee_A:
            return self.v_knee_V + self.rz_ohm * (i_A - self.i_knee_A)
        if i_A >= 0.0:
            return self.v_zero_V + (self.v_knee_V - self.v_zero_V) * i_A / self.i_knee_A
        return self.v_zero_V + self.rz_ohm * i_A

    def slope_ohm(self, i_A: float) -> float:
        """Dynamic resistance dV/dI on the segment that contains ``i_A``."""
        if 0.0 <= i_A < self.i_knee_A:
            return (self.v_knee_V - self.v_zero_V) / self.i_knee_A
        return self.rz_ohm

    def series_parameters(self) -> tuple[float, float]:
        """(R, source) of the linear equivalent that holds above the knee (what :class:`LinearZener` would give)."""
        return self.rz_ohm, -(self.vz_V - self.rz_ohm * self.i_nominal_A)

    def power_W(self, i_A: float) -> float:
        """Power dissipated in the stack, drop times current."""
        return i_A * self.drop_V(i_A)

    def spice_drop(self, i: str) -> str:
        """The drop as an ngspice expression of the branch current expression ``i`` (a ternary chain)."""
        vk, v0, ik, rz = self.v_knee_V, self.v_zero_V, self.i_knee_A, self.rz_ohm
        return (f"(({i})>={ik:.9g} ? {vk:.9g}+{rz:.9g}*(({i})-{ik:.9g}) : "
                f"(({i})>=0 ? {v0:.9g}+{(vk - v0) / ik:.9g}*({i}) : {v0:.9g}+{rz:.9g}*({i})))")
