# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Elements: voltage-clamp shunts, the surge protection that bypasses a repeater's electronics. A clamp conducts when the voltage across it exceeds its clamp
voltage ``V_c`` and then behaves like a small resistance ``r_on``:

    I(v) = g_on (v - V_c)+  -  g_on (-v - V_c)+  +  g_off v       (bidirectional; the second term is dropped for a unidirectional clamp)

with ``g_on = 1 / r_on`` and ``g_off`` a small leakage (0 by default). :class:`DiodeChain` has ``V_c = n_diodes V_f`` (a stack of forward-biased silicon diodes;
anti-parallel stacks make it bidirectional); :class:`~bolts.elements.arrester.Arrester` is the same law with a clamp voltage given directly. The ratings
(``i_withstand_A``, for example the 200 A long-pulse and 450 A / 15 kV short-pulse bypass of Chesnoy p. 392) are recorded for the damage checks, not enforced.
Piecewise-linear laws keep the Newton iteration exact once the right segment is found; the exponential diode curve is a v0.3 item."""
from __future__ import annotations

from ..mna.stamp import Stamper
from .base import Element


class ClampShunt(Element):
    """Two-terminal nonlinear shunt with the piecewise-linear clamp law above."""

    def __init__(self, name: str, a: str | None, b: str | None, v_clamp_V: float, r_on_ohm: float, g_off_S: float = 0.0,
                 bidirectional: bool = True, i_withstand_A: float | None = None):
        if v_clamp_V <= 0 or r_on_ohm <= 0 or g_off_S < 0:
            raise ValueError("a clamp needs a positive clamp voltage and on-resistance and a non-negative leakage")
        self.name, self.a, self.b = name, a, b
        self.v_clamp_V, self.r_on_ohm, self.g_off_S = v_clamp_V, r_on_ohm, g_off_S
        self.bidirectional, self.i_withstand_A = bidirectional, i_withstand_A

    @property
    def nodes(self):
        """Names of the nodes this element connects."""
        return tuple(n for n in (self.a, self.b) if n)

    @property
    def g_on_S(self) -> float:
        """Conductance once the clamp conducts."""
        return 1.0 / self.r_on_ohm

    def current_A(self, v_V: float) -> float:
        """Current from ``a`` to ``b`` at voltage ``v_V = v_a - v_b``."""
        i = self.g_off_S * v_V
        if v_V > self.v_clamp_V:
            i += self.g_on_S * (v_V - self.v_clamp_V)
        elif self.bidirectional and v_V < -self.v_clamp_V:
            i += self.g_on_S * (v_V + self.v_clamp_V)
        return i

    def conductance_S(self, v_V: float) -> float:
        """Dynamic conductance dI/dv on the segment that contains ``v_V``."""
        on = v_V > self.v_clamp_V or (self.bidirectional and v_V < -self.v_clamp_V)
        return self.g_off_S + (self.g_on_S if on else 0.0)

    def spice_current(self, v: str) -> str:
        """The current as an ngspice expression of the voltage expression ``v``."""
        g, vc = self.g_on_S, self.v_clamp_V
        neg = f"-{g:.9g}*max(-({v})-{vc:.9g},0)" if self.bidirectional else ""
        return f"{g:.9g}*max(({v})-{vc:.9g},0){neg}+{self.g_off_S:.9g}*({v})"

    def stamp(self, st: Stamper) -> None:
        """Register the nonlinear shunt with the stamper; the Newton iteration builds its companion model."""
        st.add_nonlinear_shunt(self.a, self.b, self)

    def energy_J(self, v_V, dt_s: float):
        """Energy absorbed over a voltage record (sum of v i dt), for the arrester-energy check."""
        import numpy as np
        v = np.asarray(v_V, float)
        i = np.array([self.current_A(x) for x in v])
        return float(np.sum(v * i) * dt_s)


class DiodeChain(ClampShunt):
    """A stack of ``n_diodes`` forward-biased diodes, each dropping ``v_forward_V``; anti-parallel when ``bidirectional``."""

    def __init__(self, name: str, a: str | None, b: str | None, n_diodes: int = 1, v_forward_V: float = 0.7, r_on_ohm: float = 0.05,
                 g_off_S: float = 0.0, bidirectional: bool = True, i_withstand_A: float | None = None):
        if n_diodes < 1:
            raise ValueError("a diode chain needs at least one diode")
        super().__init__(name, a, b, n_diodes * v_forward_V, r_on_ohm, g_off_S, bidirectional, i_withstand_A)
        self.n_diodes, self.v_forward_V = n_diodes, v_forward_V
