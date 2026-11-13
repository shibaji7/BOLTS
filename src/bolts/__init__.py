# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""BOLTS: Branching-unit and Optical-repeater power-feed Loop Transient Simulator.

Stress and vulnerability of submarine power-feed systems (PFE, cable, repeaters, branching units) under geomagnetic disturbances
(GMD / space weather), lightning and switching surges, down to loss of signal, failures and traffic loss.
"""
from . import api as _api
from ._version import __version__
from .api import (
    Result,
    assess,
    build_network,
    export_spice,
    load_parameters,
    load_waveform,
    register_element,
    register_waveform,
    run_transient,
)

__all__ = ["__version__", *_api.__all__]
