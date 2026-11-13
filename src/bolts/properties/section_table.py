# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Property provider from a section table: R, C (and optionally G and L) that change along the route, as a cable design lists them.

CSV columns (header required, one row per section, sections contiguous and increasing along the chainage):
``x_start_km, x_end_km, r_ohm_per_km, c_uF_per_km`` and optionally ``g_S_per_km, l_mH_per_km``. A missing L column leaves the inductance
unknown (a placeholder 0, flagged), exactly as the constant provider does."""
from __future__ import annotations

import csv
import pathlib
from dataclasses import dataclass

import numpy as np

from ..errors import ConfigError
from .base import RLCG


@dataclass(frozen=True)
class SectionTableRLCG:
    """Piecewise-constant properties. ``edges_km`` has one more entry than the per-km arrays; section k covers ``edges_km[k]`` to ``edges_km[k+1]``."""

    edges_km: np.ndarray
    r_ohm_per_km: np.ndarray
    c_F_per_km: np.ndarray
    g_S_per_km: np.ndarray
    l_H_per_km: np.ndarray | None = None

    def __post_init__(self):
        e = np.asarray(self.edges_km, float)
        n = len(e) - 1
        if n < 1 or np.any(np.diff(e) <= 0):
            raise ConfigError("a section table needs increasing section edges and at least one section")
        for name in ("r_ohm_per_km", "c_F_per_km", "g_S_per_km"):
            if len(getattr(self, name)) != n:
                raise ConfigError(f"{name} must have one value per section ({n})")
        if self.l_H_per_km is not None and len(self.l_H_per_km) != n:
            raise ConfigError(f"l_H_per_km must have one value per section ({n})")
        if np.any(np.asarray(self.r_ohm_per_km) < 0) or np.any(np.asarray(self.c_F_per_km) < 0):
            raise ConfigError("R and C per km must not be negative")

    def rlcg(self, x_km: float, depth_m: float = 0.0, temperature_C: float = 4.0, f_Hz: float = 0.0) -> RLCG:
        """The section containing chainage ``x_km`` (a boundary belongs to the section that starts there; the far end belongs to the last section)."""
        e = np.asarray(self.edges_km, float)
        if x_km < e[0] - 1e-9 or x_km > e[-1] + 1e-9:
            raise ValueError(f"chainage {x_km} km is outside the table ({e[0]} to {e[-1]} km)")
        k = min(int(np.searchsorted(e, x_km, side="right")) - 1, len(e) - 2)
        k = max(k, 0)
        has_l = self.l_H_per_km is not None
        return RLCG(float(self.r_ohm_per_km[k]), float(self.c_F_per_km[k]), float(self.g_S_per_km[k]),
                    float(self.l_H_per_km[k]) if has_l else 0.0, has_l)

    @classmethod
    def from_csv(cls, path: str | pathlib.Path) -> SectionTableRLCG:
        """Read a section table; checks the sections are contiguous so no stretch of cable is silently left out."""
        with open(path, newline="") as fh:
            rows = list(csv.DictReader(fh))
        if not rows:
            raise ConfigError(f"{path}: no sections")
        need = {"x_start_km", "x_end_km", "r_ohm_per_km", "c_uF_per_km"}
        if not need <= set(rows[0]):
            raise ConfigError(f"{path}: missing columns {sorted(need - set(rows[0]))}")
        start = np.array([float(r["x_start_km"]) for r in rows])
        end = np.array([float(r["x_end_km"]) for r in rows])
        if not np.allclose(start[1:], end[:-1]):
            raise ConfigError(f"{path}: sections must be contiguous (each x_start_km equals the previous x_end_km)")
        r = np.array([float(x["r_ohm_per_km"]) for x in rows])
        c = np.array([float(x["c_uF_per_km"]) for x in rows]) * 1e-6
        g = np.array([float(x.get("g_S_per_km") or 0.0) for x in rows])
        l_col = "l_mH_per_km" in rows[0] and all(x["l_mH_per_km"].strip() for x in rows)
        el = np.array([float(x["l_mH_per_km"]) for x in rows]) * 1e-3 if l_col else None
        return cls(np.append(start, end[-1]), r, c, g, el)
