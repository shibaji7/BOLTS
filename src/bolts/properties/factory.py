# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Pick the cable-property provider from the ``[cable]`` parameters, so a TOML file, ``--set`` on the command line or ``load_parameters(overrides=...)``
can select a section table, a depth profile and the temperature model without any Python.

    cable.section_table_csv    "none" | path   per-section R, C, G, L (see ``SectionTableRLCG``); "none" keeps the constant per-km values
    cable.depth_profile_csv    "none" | path   columns x_km, depth_m (see ``DepthProfileRLCG``)
    cable.depth_temperature_csv "none" | path  columns depth_m, temperature_C (seabed temperature of each depth); with "none" the constant
                                               ``cable.seabed_temperature_C`` is used
    cable.temperature_model    "off" | "copper" scale R with temperature (``TemperatureRLCG``)

Paths are relative to the directory the program is run from. The order of wrapping is: depth profile (outermost, supplies depth and temperature)
around the temperature model around the section table or constant values."""
from __future__ import annotations

import numpy as np

from ..config.schema import ParameterSet
from ..errors import ConfigError
from .constant import ConstantRLCG
from .depth_profile import DepthProfileRLCG
from .section_table import SectionTableRLCG
from .temperature_R import TemperatureRLCG


def _is_set(p: ParameterSet, name: str) -> bool:
    return str(p.get("cable", name)).strip().lower() not in ("none", "")


def _two_columns(path: str, a: str, b: str) -> tuple[np.ndarray, np.ndarray]:
    """Read two named columns of a CSV (header required)."""
    data = np.genfromtxt(path, delimiter=",", names=True, dtype=float)
    if a not in (data.dtype.names or ()) or b not in (data.dtype.names or ()):
        raise ConfigError(f"{path}: needs the columns {a!r} and {b!r}")
    return np.atleast_1d(data[a]), np.atleast_1d(data[b])


def provider_from_parameters(params: ParameterSet):
    """The provider chosen by the ``[cable]`` parameters; with the defaults it is the constant provider, exactly as in v0.1."""
    prov = SectionTableRLCG.from_csv(str(params.get("cable", "section_table_csv"))) if _is_set(params, "section_table_csv") else ConstantRLCG.from_parameters(params)
    model = str(params.get("cable", "temperature_model")).strip().lower()
    if model not in ("off", "copper"):
        raise ConfigError(f"cable.temperature_model must be 'off' or 'copper', not {model!r}")
    if model == "copper":
        prov = TemperatureRLCG(prov, float(params.get("cable", "conductor_tempco_per_K")), float(params.get("cable", "resistance_reference_temperature_C")))
    if _is_set(params, "depth_profile_csv"):
        x, d = _two_columns(str(params.get("cable", "depth_profile_csv")), "x_km", "depth_m")
        dt_args = (None, None)
        if _is_set(params, "depth_temperature_csv"):
            dt_args = _two_columns(str(params.get("cable", "depth_temperature_csv")), "depth_m", "temperature_C")
        prov = DepthProfileRLCG(prov, x, d, *dt_args)
    return prov
