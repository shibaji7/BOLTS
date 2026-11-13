# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Experiment 6: independent check. Question: does an independent circuit solver (ngspice) agree with BOLTS on every node voltage?

Needs the ngspice binary. Expect agreement to about 1e-9 of the largest voltage for the point-to-point cable (the regulator itself is
checked by the analytic tests, because the PFE voltage is replayed in SPICE)."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))     # so that `_common` is found from any folder

import bolts
from _common import EXAMPLE_CSV, out_dir
from bolts.spice.compare import compare_voltages
from bolts.spice.run_ngspice import ngspice_path, run_ngspice

if ngspice_path() is None:
    sys.exit("ngspice not found on PATH; install it to run this experiment")
params = bolts.load_parameters()
# only the first 5 minutes: ngspice does not need more to prove the point
record = bolts.load_waveform(EXAMPLE_CSV, params=params.with_overrides({"forcing.window_end_s": 300.0}))
result = bolts.run_transient(bolts.build_network(params, record), params, dt_s=0.5)
# SPICE cannot host the regulator, so it replays the PFE voltage BOLTS computed; what it checks is the whole passive circuit
v = run_ngspice(result.transient.system, result.transient.t_s, result.transient.v_tot_V)
c = compare_voltages(result.transient.nodes_V, v)
print(f"max difference {c['max_abs_V']:.2e} V ({c['max_rel']:.1e} of {c['scale_V']:.0f} V); RMS {c['rms_V']:.2e} V")
print("netlist:", bolts.export_spice(result, out_dir(__file__) / "bolts.cir"))
