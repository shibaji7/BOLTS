# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Experiment 11: the nonlinear devices. Question: how much does the repeater's Zener knee change what a storm that overpowers the PFE does to the current
and the light, and what does a clamp (diode chain, arrester) do to a surge?

Three parts, on the Newton solver (``bolts.mna.newton``):
  1. the Zener law: the voltage across a repeater against the line current, linear (v0.1) and piecewise: knee at 0.9 of the nominal current with the voltage
     below the knee falling to 0, 50% and 90% of its knee value at zero current (``repeater.zener_below_knee_fraction`` f = 0, 0.5, 0.9), and a knee at 0.99;
  2. opposing storms of -0.5 to -3 kV at the 1.5 kV what-if, with the linear Zener and those four piecewise cases (knee current and f are both unknown);
  3. a 1 kV step through 100 ohm into a 1 uF node, free and with an arrester (clamp 300 V, 2 ohm) or a 4-diode chain (2.8 V) across it, and the energy the clamp absorbs.
Expect: with the linear Zener each repeater drops a constant 56 V however small the current, so a loop that the PFE can no longer drive keeps demanding those 672 V and the
current collapses (-2.36 A at -2 kV). With a knee the drop shrinks with the current, so the same storm takes the current down far less (-1.61 A at -2 kV for f = 0:
I = (V_cap + E) / (R_nonrepeater + 12 rz) once the stack conducts backwards), and a storm of -0.5 to -1 kV that the linear model says costs the 250G traffic is harmless
for f = 0 or 0.5. The size of the effect depends entirely on the two unknowns: f = 0.9 is close to the linear model. Part 3 shows the clamp holding the node near its clamp
voltage while it carries the surge current. All device values are placeholders: the result is a sensitivity, not a prediction."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))     # so that `_common` is found from any folder
import numpy as np

import bolts
from _common import out_dir
from bolts.elements.arrester import Arrester
from bolts.elements.diode_chain import DiodeChain
from bolts.elements.lumped import Capacitor, Resistor, VSource
from bolts.elements.zener import LinearZener, PiecewiseZener
from bolts.mna.assemble import assemble
from bolts.mna.stamp import RecordSource, Stamper
from bolts.mna.transient import run_transient
from bolts.plotting import style
from bolts.waveforms.step_ramp_sine import ramp_hold, step

CASES = {"linear": None, "knee 0.9, f 0": (0.9, 0.0), "knee 0.9, f 0.5": (0.9, 0.5), "knee 0.9, f 0.9": (0.9, 0.9), "knee 0.99, f 0": (0.99, 0.0)}
STORMS = (-500.0, -1000.0, -2000.0, -3000.0)


def storm(e, case):
    ov = {"pfe.max_voltage_kV_per_end": 0.75} | ({} if case is None else {"repeater.zener_knee_current_A": case[0], "repeater.zener_below_knee_fraction": case[1]})
    p = bolts.load_parameters(overrides=ov)
    return bolts.assess(bolts.run_transient(bolts.build_network(p, ramp_hold(e, 600.0, 600.0, 1.0)), p, dt_s=1.0))


def surge(clamp):
    dt = 1e-6
    rec = step(1000.0, duration_s=1.5e-3, dt_s=dt, t_step_s=dt)
    st = Stamper(["in", "m"])
    for el in (VSource("vs", None, "in", RecordSource(rec, 1.0)), Resistor("r", "in", "m", 100.0), Capacitor("c", "m", None, 1e-6)):
        el.stamp(st)
    if clamp is not None:
        clamp.stamp(st)
    sysm = assemble(st)
    res = run_transient(sysm, rec.t_s)
    return rec.t_s, res.node_V("m"), dt


if __name__ == "__main__":
    out = out_dir(__file__)
    print("2. opposing storms at the 1.5 kV what-if (ramp 600 s, hold 600 s): worst repeater current change (mA), light lost (% of time), 250G delivered (%)")
    print(f"{'E V':>6} " + " ".join(f"{name:>22}" for name in CASES))
    table = {}
    for e in STORMS:
        row = []
        for name, case in CASES.items():
            s = storm(e, case)
            table[(e, name)] = s
            row.append(f"{s['di_min_mA']:8.0f} {100 * s['frac_time_outage']:6.1f} {100 * s['fixed_250G_mean_rate_fraction']:6.1f}")
        print(f"{e:6.0f} " + " ".join(f"{r:>22}" for r in row))
    print("\n3. 1 kV step through 100 ohm into 1 uF")
    clamps = {"free": None, "arrester 300 V, 2 ohm": Arrester("arr", "m", None, 300.0, 2.0), "4-diode chain (2.8 V), 0.5 ohm": DiodeChain("d", "m", None, 4, 0.7, 0.5)}
    traces = {}
    print(f"{'device':>30} {'v max V':>9} {'v end V':>9} {'energy in clamp mJ':>20}")
    for name, c in clamps.items():
        t, v, dt = surge(c)
        traces[name] = (t, v)
        print(f"{name:>30} {v.max():9.1f} {v[-1]:9.1f} {(0.0 if c is None else 1e3 * c.energy_J(v, dt)):20.2f}")

    plt = style.require_matplotlib()
    style.apply()
    fig, axs = plt.subplots(1, 4, figsize=(style.DOUBLE_COL_IN, 2.45), gridspec_kw={"wspace": 0.85, "left": 0.085, "right": 0.985, "bottom": 0.33, "top": 0.88})
    i = np.linspace(-0.2, 1.3, 400)
    lin = LinearZener(56.0, 5.0, 1.0)
    axs[0].plot(i, [lin.drop_V(x) for x in i], label="linear")
    for name, case in list(CASES.items())[1:4]:
        z = PiecewiseZener(56.0, 5.0, 1.0, case[0], case[1])
        axs[0].plot(i, [z.drop_V(x) for x in i], label=name.replace("knee 0.9, ", ""))
    axs[0].set_xlabel("Line current (A)")
    axs[0].set_ylabel("Repeater drop (V)")
    axs[0].legend(loc="lower right", fontsize=5.5)
    for name in CASES:
        axs[1].plot(np.abs(STORMS), [table[(e, name)]["di_min_mA"] for e in STORMS], "o-", label=name)
    axs[1].set_xlabel("Storm $|E|$ (V)")
    axs[1].set_ylabel("Worst current change (mA)")
    for name in CASES:
        axs[2].plot(np.abs(STORMS), [100 * table[(e, name)]["frac_time_outage"] for e in STORMS], "o-", label=name)
    axs[2].set_xlabel("Storm $|E|$ (V)")
    axs[2].set_ylabel(f"Light lost ({style.pct()} of time)")
    for name, (t, v) in traces.items():
        axs[3].plot(t * 1e3, v, label=name.split(" ")[0] if name != "4-diode chain (2.8 V), 0.5 ohm" else "4 diodes")
    axs[3].set_xlabel("Time (ms)")
    axs[3].set_ylabel("Node voltage (V)")
    axs[3].set_ylim(0, 1500)                                # headroom above the curves for the legend
    axs[3].legend(loc="upper right", fontsize=5.5)
    handles, labels = axs[1].get_legend_handles_labels()      # one legend for the storm panels (b) and (c): the five Zener cases
    fig.legend(handles, labels, loc="lower center", ncol=5, fontsize=5.5, bbox_to_anchor=(0.45, -0.01))
    for ax, lab in zip(axs, ("(a)", "(b)", "(c)", "(d)"), strict=True):
        style.panel_label(ax, lab, x=-0.02, y=1.02)
        ax.set_box_aspect(1)
        ax.set_anchor("S")
    print("wrote", style.save(fig, out / "nonlinear_devices"))
