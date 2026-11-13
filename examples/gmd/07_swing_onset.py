# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Experiment 7: how large a swing within one second does it take to disturb the traffic? Question: at which amplitude of a 1-second
voltage swing does the repeater current leave the 100 mA electroding margin, the Q margin fall, and each terminal format lose traffic?

Input: pure 1 Hz sinusoids (a stress test, not a storm: the realistic ULF record of experiment 2 never moves faster than about 20 V/s),
amplitudes 50 V to 2000 V, run against the 1.5 kV what-if limit (headroom 71 V) and the 5 kV design basis, 120 s each at 25 ms steps.
Expect (1.5 kV): up to 100 V the dip stays inside the 100 mA margin; at 200 to 300 V it is -160 to -280 mA and the Q margin
stays above 10.3 dB with no traffic loss; at 500 V the dip is about -525 mA and Q margin 9.0 dB, 100G and 200G are untouched but a 250G terminal (0.7 dB of
headroom, 10 s relock) delivers about 1%; from 750 V up the light is lost (Q margin reported as the -103 dB outage sentinel) and every format fails. At 5 kV nothing
up to 500 V reaches the repeaters and even 2000 V costs only 0.5 dB."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))     # so that `_common` is found from any folder

import bolts
from _common import out_dir
from bolts.plotting import style
from bolts.waveforms.step_ramp_sine import sine

amps = [50.0, 100.0, 200.0, 300.0, 500.0, 750.0, 1000.0, 2000.0]
dt = 0.025
rows = {}
for kv in (0.75, 2.5):          # per-end limits: the 1.5 kV what-if and the 5 kV design basis
    p = bolts.load_parameters(overrides={"pfe.max_voltage_kV_per_end": kv})
    print(f"\nlimit {2 * kv:.1f} kV total; 1 Hz swing")
    print(f"{'amp V':>7} {'dI min mA':>10} {'below margin %':>15} {'Q margin dB':>12} {'100G %':>7} {'200G %':>7} {'250G %':>7}")
    rows[kv] = []
    for a in amps:
        rec = sine(a, 1.0, duration_s=120.0, dt_s=dt)
        s = bolts.assess(bolts.run_transient(bolts.build_network(p, rec), p, dt_s=dt))
        r = [s["di_min_mA"], 100 * s["frac_time_below_margin"], s["min_margin_dB"]] + [100 * s[f"fixed_{g}G_mean_rate_fraction"] for g in (100, 200, 250)]
        rows[kv].append(r)
        print(f"{a:7.0f} {r[0]:10.1f} {r[1]:15.1f} {r[2]:12.2f} {r[3]:7.1f} {r[4]:7.1f} {r[5]:7.1f}")

# a slow, very large swing: +-3 kV with a 2-minute period (dV/dt up to 157 V/s, the regulator follows it unless the PFE runs out of voltage)
print("\n+-3 kV swing with a 120 s period (600 s run)")
for kv in (0.75, 2.5):
    p = bolts.load_parameters(overrides={"pfe.max_voltage_kV_per_end": kv})
    rec = sine(3000.0, 1.0 / 120.0, duration_s=600.0, dt_s=0.5)
    s = bolts.assess(bolts.run_transient(bolts.build_network(p, rec), p, dt_s=0.5))
    print(f"limit {2 * kv:.1f} kV: dI min {s['di_min_mA']:.0f} mA, clamped {100 * s['frac_pfe_clamped']:.0f}%, light lost {100 * s['frac_time_outage']:.0f}% of the time, "
          f"delivered 100G/200G/250G {100 * s['fixed_100G_mean_rate_fraction']:.0f}/{100 * s['fixed_200G_mean_rate_fraction']:.0f}/{100 * s['fixed_250G_mean_rate_fraction']:.0f}%")

plt = style.require_matplotlib()
style.apply()
fig, axs = plt.subplots(1, 2, figsize=(style.DOUBLE_COL_IN, 2.8))
for kv, ls in ((0.75, "-"), (2.5, "--")):
    d = rows[kv]
    axs[0].plot(amps, [max(r[2], -2.0) for r in d], ls, marker="o", label=f"limit {2 * kv:.1f} kV")
    axs[1].plot(amps, [r[5] for r in d], ls, marker="o", label=f"250G, {2 * kv:.1f} kV")
    axs[1].plot(amps, [r[4] for r in d], ls, marker="s", label=f"200G, {2 * kv:.1f} kV")
axs[0].set_ylabel("Minimum Q margin (dB), outage shown at -2")
axs[1].set_ylabel(f"Delivered rate, fixed format ({style.pct()})")
for ax, lab in zip(axs, ("(a)", "(b)"), strict=True):
    ax.set_xscale("log")
    ax.set_xlabel("Swing amplitude at 1 Hz (V)")
    style.panel_label(ax, lab, x=-0.02, y=1.02)
    ax.legend()
print("wrote", style.save(fig, out_dir(__file__) / "swing_onset"))
