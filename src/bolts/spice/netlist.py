# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Export a linear network to an ngspice netlist, so every circuit can be cross-checked by an independent solver.

A series branch a -> b with resistance R, inductance L and sources s(t) becomes, in this order,
    V(s) from node a to an internal node x1 (v_x1 = v_a + s),  R from x1 to x2,  L from x2 to b.
Exogenous sources are written as piecewise-linear (PWL) tables; the regulator-controlled PFE sources are replayed from the simulated
``v_tot(t)``, so the comparison checks the circuit solver (the regulator itself is checked by the analytic tests).
Nonlinear series branches (the piecewise Zener) become a zero-volt current sensor plus a behavioural voltage source ``B`` whose value is the law's drop as an
expression of that current; nonlinear shunts (clamps, arresters) become behavioural current sources ``B`` of the voltage across them; independent current
sources become piecewise-linear ``I`` sources. The laws write their own expressions (``spice_drop`` / ``spice_current``).
"""
from __future__ import annotations

import pathlib

import numpy as np

from ..errors import NotImplementedYet
from ..mna.assemble import System

R_MIN = 1e-9


def _name(s: str) -> str:
    """A SPICE-safe identifier: anything that is not a letter or digit becomes an underscore."""
    return "".join(ch if ch.isalnum() else "_" for ch in s)


def node_label(system: System, idx: int) -> str:
    """SPICE node name; index -1 (the sea) is node ``0``, which SPICE treats as ground."""
    return "0" if idx < 0 else f"n_{_name(system.node_names[idx])}"


def netlist_text(system: System, t_s: np.ndarray, v_tot_V: np.ndarray | None = None, title: str = "BOLTS export",
                 out_file: str = "ngspice_out.txt") -> str:
    """The netlist as text. ``v_tot_V`` is the simulated PFE voltage that replaces the controlled sources."""
    t_s = np.asarray(t_s, float)
    dt = float(t_s[1] - t_s[0])
    # Gear order 1 is backward Euler: the same integrator as BOLTS, so the two solvers should agree to round-off, not just roughly
    lines = [f"* {title}", ".options method=gear maxord=1 reltol=1e-6 abstol=1e-12"]
    for br in system.branches:
        a, b = node_label(system, br.a), node_label(system, br.b)
        nm = _name(br.name)
        if br.nonlinear is not None:     # sense the branch current with a 0 V source, then drive the drop from a behavioural source
            lines.append(f"Vs_{nm} {a} x1_{nm} 0")
            lines.append(f"B_{nm} x1_{nm} {b} V = {br.nonlinear.spice_drop(f'i(Vs_{nm})')}")
            continue
        s_tot = np.zeros(len(t_s))      # the branch's total source voltage over time
        for s in br.sources:
            if s.dynamic:
                if v_tot_V is None:
                    raise ValueError("a controlled source needs v_tot_V to be replayed")
                s_tot += s.weight * np.asarray(v_tot_V, float)
            else:
                s_tot += s.values(t_s)
        start = a
        if br.sources:
            start = f"x1_{nm}"
            pwl = " ".join(f"{t:.9g} {v:.9g}" for t, v in zip(t_s, s_tot, strict=True))
            lines.append(f"V_{nm} {start} {a} PWL({pwl})")
        if br.r_ohm > 0 and br.l_H > 0:
            lines.append(f"R_{nm} {start} x2_{nm} {br.r_ohm:.9g}")
            lines.append(f"L_{nm} x2_{nm} {b} {br.l_H:.9g}")
        elif br.r_ohm > 0:
            lines.append(f"R_{nm} {start} {b} {br.r_ohm:.9g}")
        elif br.l_H > 0:
            lines.append(f"L_{nm} {start} {b} {br.l_H:.9g}")
        else:
            lines.append(f"R_{nm} {start} {b} {R_MIN:.1e}")           # an ideal source branch: a near-zero resistor
    # shunt elements: capacitances as C, conductances as resistors (1/G)
    for k, (a, b, c) in enumerate(system.capacitances):
        lines.append(f"C_{k} {node_label(system, a)} {node_label(system, b)} {c:.9g}")
    for k, (a, b, g) in enumerate(system.conductances):
        lines.append(f"R_g{k} {node_label(system, a)} {node_label(system, b)} {1.0 / g:.9g}")
    for k, (a, b, law) in enumerate(system.nl_shunts):
        la, lb = node_label(system, a), node_label(system, b)
        lines.append(f"B_s{k} {la} {lb} I = {law.spice_current(f'v({la},{lb})')}")
    for k, (a, b, src) in enumerate(system.isources):
        pwl = " ".join(f"{t:.9g} {v:.9g}" for t, v in zip(t_s, src.values(t_s), strict=True))
        lines.append(f"I_{k} {node_label(system, a)} {node_label(system, b)} PWL({pwl})")
    # ask ngspice for every node voltage, written as (time, value) pairs per vector
    vec = " ".join(f"v({node_label(system, i)})" for i in range(system.n_nodes))
    lines += [f".tran {dt:.9g} {t_s[-1]:.9g} 0 {dt:.9g}", ".control", "run", f"wrdata {out_file} {vec}", ".endc", ".end"]
    return "\n".join(lines) + "\n"


def write_netlist(obj, path) -> pathlib.Path:
    """Write the netlist of a :class:`~bolts.result.Result` (its simulated v_tot is replayed)."""
    from ..result import Result
    if not isinstance(obj, Result):
        raise NotImplementedYet("export of a network without a result", "run it first and export the Result")
    p = pathlib.Path(path)
    p.write_text(netlist_text(obj.transient.system, obj.transient.t_s, obj.transient.v_tot_V))
    return p
