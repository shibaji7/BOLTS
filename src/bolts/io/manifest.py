# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Run provenance: what produced a result (versions, parameter fingerprint, parameter counts, time). Written next to every output."""
from __future__ import annotations

import datetime
import platform
import sys

import numpy as np
import scipy

from .._version import __version__
from ..config.schema import ParameterSet


def make_manifest(params: ParameterSet, extra: dict | None = None) -> dict:
    """A small dict recording versions, platform and the parameter fingerprint; ``extra`` adds run-specific items such as the command."""
    m = {"bolts": __version__, "python": sys.version.split()[0], "numpy": np.__version__, "scipy": scipy.__version__,
         "platform": platform.platform(), "parameters_fingerprint": params.fingerprint(), "parameter_status_counts": params.counts(),
         "created_utc": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")}
    if extra:
        m.update(extra)
    return m
