# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Experiment 13: a storm that does reach the light and the traffic. Question: how strong must the induced voltage be before the Q margin
and the delivered rate move, and what does it cost?

Input: the shipped SYNTHETIC record of experiment 2 (peak about -200 V) multiplied by 3 and by 4 (peaks near -600 V and -800 V; pass other factors as arguments), run against the 1.5 kV what-if limit. Experiment 2 is the mild case; this is the same storm made stronger, so only the amplitude differs.
Expect: the PFE sits at its limit while the induced voltage opposes the feed, the repeater current falls far below the 100 mA margin, the Q margin
drops toward and below 0 dB, and the 250G terminal loses the most traffic (it needs the most OSNR), then 200G, while 100G holds longest. This is a
scenario for a storm the 1.5 kV what-if cannot absorb; the 5 kV design basis would absorb a much larger one."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))     # so that `_common` is found from any folder

import bolts
from _common import EXAMPLE_CSV, out_dir, tight_limit_params
from bolts.plotting.timeseries import plot_compare

SCALES = (3.0, 4.0)       # the same storm at two strengths; pass other values as arguments, for example `13_storm_impact.py 2 5`
if len(sys.argv) > 1:
    SCALES = tuple(float(a) for a in sys.argv[1:])
out = out_dir(__file__)
runs = []
for scale in SCALES:
    params = tight_limit_params().with_overrides({"forcing.scale": scale})      # the same record, `scale` times stronger
    record = bolts.load_waveform(EXAMPLE_CSV, params=params)
    result = bolts.run_transient(bolts.build_network(params, record), params)
    s = bolts.assess(result)
    result.save(out / f"x{scale:g}")
    runs.append(result)
    print(f"x{scale:g}: peak induced {record.values.min():.0f} V; PFE clamped {100 * s['frac_pfe_clamped']:.1f}% of the time; "
          f"repeater current down to {s['di_min_mA']:.0f} mA; Q margin down to {s['min_margin_dB']:.1f} dB")
    for g in (100, 200, 250):
        print(f"    {g}G: adaptive availability {100 * s[f'adaptive_{g}G_availability']:.1f}%, lost {s[f'adaptive_{g}G_lost_Gbit'] / 1000:.0f} Tbit; "
              f"fixed availability {100 * s[f'fixed_{g}G_availability']:.1f}%")
print("wrote", plot_compare(runs, [f"Record x{sc:g}" for sc in SCALES], out / "run"))
