# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""The public API: a few functions that cover a whole study. Everything here is also re-exported from ``bolts``.

    >>> import bolts
    >>> params = bolts.load_parameters()                       # shipped defaults (every value with unit, status and source)
    >>> record = bolts.load_waveform("data/example_vind_1s.csv", params=params)
    >>> net = bolts.build_network(params, record)
    >>> result = bolts.run_transient(net, params)
    >>> summary = bolts.assess(result)
"""
from __future__ import annotations

import pathlib

import numpy as np

from .config.loader import load_parameters
from .config.schema import ParameterSet
from .mna.timestep import fixed_axis
from .mna.transient import run_transient as _run
from .network.builder import build_network
from .network.graph import Network
from .registry import register_element, register_waveform
from .result import Result
from .waveforms.base import Record
from .waveforms.csv_record import read_csv_record, record_from_parameters


def load_waveform(path=None, params: ParameterSet | None = None, **kwargs) -> Record:
    """Read a voltage record. With ``params`` the columns, time format, window, scale and step come from its ``[forcing]`` section
    (``path`` overrides the file); without it pass ``time_column``, ``value_column`` ... as keywords."""
    if params is not None:
        return record_from_parameters(params, path)
    return read_csv_record(path, **kwargs)


def run_transient(network: Network, params: ParameterSet, dt_s: float | None = None, t_s: np.ndarray | None = None, newton: bool | None = None) -> Result:
    """Run a built network. The time axis is ``t_s`` if given, else the record's duration at ``dt_s`` (default: the record's own spacing,
    or ``solver.dt_s`` without a record). The regulator is exact for any dt / tau. A network with nonlinear elements is solved by Newton iteration
    automatically; ``newton=True`` forces that path for a linear network (a check that both paths agree)."""
    rec = network.meta.get("record")
    # the time axis comes from the record unless the caller gives one (needed for a network without a record)
    if t_s is None:
        if rec is None:
            dt = float(dt_s or params.get("solver", "dt_s"))
            raise ValueError(f"no record in the network: pass t_s (for example a {dt:g} s axis) or build the network with a record")
        dt = float(dt_s or rec.dt_s)
        t_s = fixed_axis(rec.duration_s, dt, rec.t_s[0])
    system = network.compile()      # stamp the elements and assemble the matrices
    res = _run(system, t_s, network.controller, str(params.get("solver", "integrator")), newton)
    return Result(network, res, params)


def assess(result: Result, targets=(100, 200, 250)) -> dict:
    """Electrical, optical and traffic metrics of a run; ``targets`` are the terminal rates (Gbit/s) to evaluate."""
    return result.assess(targets)


def export_spice(result_or_network, path, params: ParameterSet | None = None) -> pathlib.Path:
    """Write an ngspice netlist of the circuit, for an independent cross-check. Imported lazily: the SPICE code is optional."""
    from .spice.netlist import write_netlist
    return write_netlist(result_or_network, path)


__all__ = [
    "Result",
    "assess",
    "build_network",
    "export_spice",
    "load_parameters",
    "load_waveform",
    "register_element",
    "register_waveform",
    "run_transient",
]
