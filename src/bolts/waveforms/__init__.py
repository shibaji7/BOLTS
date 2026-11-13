# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Waveforms. The built-in constructors are registered by name (``bolts.registry.get_waveform("sine")``); register your own with
:func:`bolts.registry.register_waveform` or the ``bolts.waveforms`` entry-point group."""
from ..registry import register_waveform
from .base import Record
from .csv_record import read_csv_record
from .double_exp import double_exponential
from .heidler import heidler
from .step_ramp_sine import ramp, ramp_hold, sine, step

for _name, _fn in {"step": step, "ramp": ramp, "sine": sine, "ramp_hold": ramp_hold, "double_exponential": double_exponential,
                   "heidler": heidler, "csv": read_csv_record}.items():
    register_waveform(_name, _fn)

__all__ = ["Record", "double_exponential", "heidler", "ramp", "ramp_hold", "read_csv_record", "sine", "step"]
