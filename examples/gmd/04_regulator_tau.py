# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Experiment 4: the regulator time constant. Question: how much does tau matter, and what does the sampling step hide?

(a) a 0.89 V/s ramp (the pfe_design storm's largest slope): the steady current error is tau x rate / R_loop for every tau, exactly, for
any step; (b) a 100 V jump: the simulated peak depends on how many samples describe the jump, (dV / R_loop)(tau / dt)(1 - exp(-dt / tau)).
Expect (a) 5.4 microamps at tau = 5 ms and 2.2 mA at 2 s; (b) 119 mA at dt = 0.25 ms falling to 0.6 mA at dt = 1 s (tau = 5 ms)."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))     # so that `_common` is found from any folder
import numpy as np

import bolts
from _common import out_dir
from bolts.plotting import style
from bolts.waveforms.step_ramp_sine import ramp, step

params = bolts.load_parameters()
# (a) ramp error for a range of regulator speeds; 0.8 ms is 1/(2 pi 200 Hz), 5 ms the default (1/200 Hz)
taus = np.array([0.0008, 0.005, 0.05, 0.5, 2.0])
err = []
for tau in taus:
    p = params.with_overrides({"pfe.regulator_response_s": float(tau)})
    dt = 0.05 if tau < 1 else 0.5          # the regulator is exact for any dt/tau, so a coarse step does not spoil the answer
    res = bolts.run_transient(bolts.build_network(p, ramp(0.89, max(60.0, 12 * tau), dt)), p, dt_s=dt)
    err.append(1e3 * (res.transient.i_sense_A[-1] - 1.0))     # steady-state current error at the end of the ramp, mA (set point is 1 A)
    print(f"tau {tau * 1e3:8.1f} ms: ramp error {err[-1]:.5f} mA (formula {1e3 * 0.89 * tau / res.transient.r_loop_ohm:.5f} mA)")

# (b) the same 100 V jump described with finer and finer sampling: a coarse record hides how sharp the jump really is
dts = np.array([0.00025, 0.001, 0.005, 0.05, 0.25, 1.0])
peaks = []
p5 = params.with_overrides({"pfe.regulator_response_s": 0.005})
for dt in dts:
    res = bolts.run_transient(bolts.build_network(p5, step(100.0, max(2.0, 40 * dt), dt, 0.5)), p5, dt_s=dt)
    peaks.append(1e3 * np.abs(res.transient.i_sense_A - 1.0).max())
    print(f"dt {dt * 1e3:8.2f} ms: 100 V jump peak {peaks[-1]:7.2f} mA")

plt = style.require_matplotlib()
style.apply()
fig, (a, b) = plt.subplots(1, 2, figsize=(style.DOUBLE_COL_IN, 2.8))
a.loglog(taus, err, "o-", color=style.TOL["blue"])
a.set_xlabel(r"Regulator time constant $\tau$ (s)")
a.set_ylabel("Ramp error (mA)")
b.semilogx(dts, peaks, "o-", color=style.TOL["orange"])
b.set_xlabel("Sampling step (s)")
b.set_ylabel("Peak for a 100 V jump (mA)")
for ax, lab in zip((a, b), ("(a)", "(b)"), strict=True):
    style.panel_label(ax, lab, x=-0.02, y=1.02)
fig.tight_layout()
print("wrote", style.save(fig, out_dir(__file__) / "regulator_tau"))
