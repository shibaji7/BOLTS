# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Read a voltage (or current) record from a CSV file: any time origin, seconds or ISO timestamps, a window, a scale and a step."""
from __future__ import annotations

import csv
import pathlib

import numpy as np

from ..config.schema import ParameterSet
from .base import Record
from .window import window


def read_csv_record(path, time_column: str = "t_s", value_column: str = "v_ind_V", time_format: str = "seconds",
                    window_s: tuple[float, float] | None = None, scale: float = 1.0, dt_s: float = 0.0,
                    unit: str = "V") -> Record:
    """Read ``time_column`` / ``value_column`` of a CSV file into a :class:`Record`.

    ``time_format`` is ``"seconds"`` (numbers) or ``"iso"`` (timestamps); either way the time axis is shifted to start at 0. ``window_s`` is
    ``(start, end)`` in seconds from the first row (``end < 0`` means "to the end"). ``scale`` multiplies the values. ``dt_s > 0`` resamples
    to that step; ``0`` keeps the file's own sampling."""
    p = pathlib.Path(path)
    if not p.exists():
        raise FileNotFoundError(f"record file {p} not found")
    with open(p, newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"{p.name} has no rows")
    for c in (time_column, value_column):
        if c not in rows[0]:
            raise KeyError(f"column {c!r} not in {p.name}; columns are {list(rows[0])}")
    # rows with an empty time or value are skipped (instrument gaps), not interpolated
    raw_t = [r[time_column] for r in rows if r[time_column] != "" and r[value_column] != ""]
    v = np.array([float(r[value_column]) for r in rows if r[time_column] != "" and r[value_column] != ""]) * scale
    if time_format == "iso":                                 # numpy parses ISO 8601 strings directly
        ts = np.array(raw_t, dtype="datetime64[ns]")
        t = (ts - ts[0]).astype("timedelta64[ns]").astype(float) * 1e-9
    elif time_format == "seconds":
        t = np.array([float(x) for x in raw_t])
        t = t - t[0]
    else:
        raise ValueError(f"time_format must be 'seconds' or 'iso', got {time_format!r}")
    keep = np.concatenate([[True], np.diff(t) > 0])            # drop repeated or out-of-order times
    rec = Record(t[keep], v[keep], p.name, unit)
    if window_s is not None:
        t0, t1 = window_s
        rec = window(rec, t0, rec.t_s[-1] if t1 < 0 else t1)
    return rec.resampled(dt_s) if dt_s > 0 else rec


def record_from_parameters(params: ParameterSet, path=None) -> Record:
    """The record named in the ``[forcing]`` section of a parameter set (columns, time format, window, scale, step)."""
    g = lambda k: params.get("forcing", k)       # noqa: E731
    return read_csv_record(path if path is not None else g("csv_path"), g("time_column"), g("voltage_column"), g("time_format"),
                           (float(g("window_start_s")), float(g("window_end_s"))), float(g("scale")), float(g("model_dt_s")))
