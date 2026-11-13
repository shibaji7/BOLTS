# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Run ngspice in batch mode and read the node voltages it writes."""
from __future__ import annotations

import pathlib
import shutil
import subprocess
import tempfile

import numpy as np

from ..errors import BoltsError
from ..mna.assemble import System
from .netlist import netlist_text


def ngspice_path() -> str | None:
    """Location of the ``ngspice`` binary, or ``None`` if it is not installed (the cross-check is optional)."""
    return shutil.which("ngspice")


def run_ngspice(system: System, t_s: np.ndarray, v_tot_V: np.ndarray | None = None, timeout_s: float = 120.0) -> np.ndarray:
    """Node voltages from ngspice on the time axis ``t_s``, shape (len(t_s), n_nodes)."""
    exe = ngspice_path()
    if exe is None:
        raise BoltsError("ngspice was not found on PATH (install it, for example `conda install -c conda-forge ngspice`)")
    # run in a scratch directory so the output file never lands in the user's working folder
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        (d / "net.cir").write_text(netlist_text(system, t_s, v_tot_V))
        proc = subprocess.run([exe, "-b", "net.cir"], cwd=d, capture_output=True, text=True, timeout=timeout_s)
        out = d / "ngspice_out.txt"
        if not out.exists():
            raise BoltsError(f"ngspice produced no output:\n{proc.stdout[-800:]}\n{proc.stderr[-800:]}")
        data = np.loadtxt(out)
    # wrdata writes (time, value) pairs for each vector; SPICE may use its own time points, so interpolate back to BOLTS' axis
    t_sp = data[:, 0]
    return np.column_stack([np.interp(t_s, t_sp, data[:, 2 * i + 1]) for i in range(system.n_nodes)])
