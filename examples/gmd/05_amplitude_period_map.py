# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Experiment 5: how big, how fast? Question: for sinusoidal storms, how does the worst repeater current change depend on amplitude and
period, at the 1.5 kV limit and at the operator's 5 kV?

Expect: at 1.5 kV the worst change is set by the headroom (71 V) and not by the period: (amplitude - 71 V) / 816.8 ohm for amplitudes above
the headroom; at 5 kV nothing reaches the repeaters until the 5 ms regulator can no longer follow the fastest waves."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))     # so that `_common` is found from any folder
import numpy as np

import bolts
from _common import out_dir
from bolts.plotting import style
from bolts.waveforms.step_ramp_sine import sine

# pure sinusoids are a stress test (a real storm is random, see chapter 01), chosen because the answer has a closed form to check against
amps = np.array([50.0, 100.0, 200.0, 400.0, 800.0])
periods = np.array([1.0, 3.0, 10.0, 30.0, 100.0])


params = bolts.load_parameters()
maps = {}
for kv in (0.75, 2.5):           # the 1.5 kV what-if and the 5 kV operator design basis (per-end limits)
    p0 = params.with_overrides({"pfe.max_voltage_kV_per_end": kv})
    z = np.empty((len(periods), len(amps)))
    for j, per in enumerate(periods):
        dt = min(0.5, per / 40)      # at least 40 samples per period, so the sine is well resolved
        for i, a in enumerate(amps):
            rec = sine(float(a), 1.0 / float(per), duration_s=max(3 * per, 30.0), dt_s=dt)
            z[j, i] = bolts.run_transient(bolts.build_network(p0, rec), p0, dt_s=dt).summary()["di_min_mA"]
    maps[kv] = z
    print(f"limit {2 * kv:.1f} kV total: worst current change (mA), rows = period {periods.tolist()} s, columns = amplitude {amps.tolist()} V")
    print(np.round(z, 1))

plt = style.require_matplotlib()
style.apply()
fig, axs = plt.subplots(1, 2, figsize=(style.DOUBLE_COL_IN, 2.9), sharey=True)
for ax, (kv, z), lab in zip(axs, maps.items(), ("(a)", "(b)"), strict=True):
    im = ax.pcolormesh(np.arange(len(amps) + 1), np.arange(len(periods) + 1), np.clip(z, -600, 0), cmap="viridis", vmin=-600, vmax=0)
    ax.set_xticks(np.arange(len(amps)) + 0.5, [f"{a:g}" for a in amps])
    ax.set_yticks(np.arange(len(periods)) + 0.5, [f"{p:g}" for p in periods])
    ax.set_xlabel("Amplitude (V)")
    ax.set_title(f"PFE limit {2 * kv:.1f} kV total")
    style.panel_label(ax, lab, x=-0.02, y=1.02)
axs[0].set_ylabel("Period (s)")
fig.colorbar(im, ax=axs, label="Worst repeater current change (mA)", shrink=0.9)
print("wrote", style.save(fig, out_dir(__file__) / "amplitude_period_map"))
