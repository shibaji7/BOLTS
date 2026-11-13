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
from collections.abc import Sequence
from typing import Any

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


def load_waveform(path: str | pathlib.Path | None = None, params: ParameterSet | None = None, **kwargs: Any) -> Record:
    """Read a voltage record: the net induced voltage along the cable as a function of time.

    With ``params`` the columns, time format, window, scale and step come from its ``[forcing]`` section (``path`` then overrides the file); without it
    pass the column names as keywords.

    Args:
        path: CSV file. ``None`` uses ``forcing.csv_path`` of ``params``.
        params: Parameter set whose ``[forcing]`` section describes the file. ``None`` reads the file with the keywords only.
        **kwargs: Without ``params``: ``time_column``, ``value_column`` and the other options of
            :func:`bolts.waveforms.csv_record.read_csv_record` (time format, window, scale, step).

    Returns:
        A :class:`~bolts.waveforms.base.Record` (time axis in s, values in V), ready for :func:`build_network`.

    Raises:
        FileNotFoundError: The file does not exist.
        KeyError: A requested column is not in the file.
        ValueError: The file has no rows, or ``time_format`` is not ``"seconds"`` or ``"iso"``.

    Example:
        >>> record = bolts.load_waveform("data/example_vind_1s.csv", params=params)  # doctest: +SKIP
    """
    if params is not None:
        return record_from_parameters(params, path)
    return read_csv_record(path, **kwargs)


def run_transient(network: Network, params: ParameterSet, dt_s: float | None = None, t_s: np.ndarray | None = None, newton: bool | None = None) -> Result:
    """Run a built network through time (backward Euler on the modified-nodal-analysis system, the PFE regulator integrated exactly over each step).

    The regulator is exact for any ratio of step to time constant. A network with nonlinear elements (piecewise Zener, diode chain, arrester) is solved by
    Newton iteration automatically.

    Args:
        network: The circuit from :func:`build_network`.
        params: The parameter set the network was built with (the integrator comes from ``solver.integrator``).
        dt_s: Time step (s). Default: the record's own spacing, or ``solver.dt_s`` for a network without a record.
        t_s: An explicit, evenly spaced time axis (s). Needed for a network built without a record; overrides ``dt_s``.
        newton: ``None`` picks the path from the circuit; ``True`` forces Newton iteration for a linear network (a check that both paths agree to 1e-8);
            ``False`` refuses a nonlinear network.

    Returns:
        A :class:`~bolts.result.Result` with the node voltages, branch currents, PFE voltage and the metric methods.

    Raises:
        ValueError: The network has no record and no ``t_s`` was given.
        BoltsError: The time axis has no fixed step, or ``newton=False`` on a nonlinear network.
        ConvergenceError: A Newton step did not converge.
    """
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


def assess(result: Result, targets: Sequence[float] = (100, 200, 250)) -> dict:
    """Electrical, optical and traffic metrics of a run, in one flat dictionary.

    Args:
        result: A finished run from :func:`run_transient`.
        targets: Terminal rates (Gbit/s) for which the traffic metrics are evaluated, each with an adaptive and a fixed-rate policy.

    Returns:
        ``{name: number}``: current dip, PFE headroom and stress, conductor-to-sea voltage, ground potential rise, Q margin and OSNR drop, and per target the
        mean rate fraction, severely errored and unavailable seconds, availability and lost traffic. Key names are listed in chapter 02 and chapter 05.
    """
    return result.assess(targets)


def export_spice(result_or_network: Result | Network, path: str | pathlib.Path, params: ParameterSet | None = None) -> pathlib.Path:
    """Write an ngspice netlist of the circuit, for an independent cross-check.

    Linear elements, nonlinear branches (as behavioural sources), nonlinear shunts and the exogenous current sources are exported. The SPICE code is
    imported only when this is called.

    Args:
        result_or_network: A :class:`~bolts.result.Result`; the simulated PFE voltage is replayed in the netlist. A bare
            :class:`~bolts.network.graph.Network` raises ``NotImplementedYet`` (run it first).
        path: Where to write the ``.cir`` file.
        params: Accepted for symmetry with the other entry points; not used.

    Returns:
        The path written.
    """
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
