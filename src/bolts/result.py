# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""The result of a run: the network, the transient, the parameters and the record, with the quantities people ask for."""
from __future__ import annotations

import pathlib
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np

from .config.schema import ParameterSet
from .damage.insulation_withstand import constant_from_reference, life_consumed
from .earthing.gpr import gpr_metrics
from .impact.optical import evaluate, summarize
from .impact.terminal import terminal_trace, traffic_metrics
from .io.manifest import make_manifest
from .io.writers import write_json, write_series_csv
from .metrics.current_dip import dip_metrics, repeater_currents_A
from .metrics.headroom import pfe_metrics
from .metrics.pfe_stress import pfe_stress_metrics
from .metrics.voltage_extremes import node_peaks_V, voltage_metrics
from .mna.transient import TransientResult
from .network.graph import Network


@dataclass
class Result:
    """A finished run. Holds the inputs (network, parameters) and the raw transient; every derived quantity is computed on request."""

    network: Network
    transient: TransientResult
    params: ParameterSet

    # ---- raw quantities ----------------------------------------------------------------------------------------
    @property
    def t_s(self) -> np.ndarray:
        """Time axis of the run (s)."""
        return self.transient.t_s

    @property
    def meta(self) -> dict:
        """Bookkeeping from the network builder (repeater branch names, set current, limits, the input record)."""
        return self.network.meta

    def repeater_currents_A(self) -> np.ndarray:
        """Current through every repeater.

        Returns:
            Array of shape ``(nt, n_repeaters)`` in A, positive along the feed direction.
        """
        return repeater_currents_A(self.transient, self.meta["repeater_branches"])

    def repeater_current_change_A(self) -> np.ndarray:
        """Repeater current minus the set point (A): the quantity compared with the 10% margin."""
        return self.repeater_currents_A() - self.meta["i_set_A"]

    # ---- assessment ----------------------------------------------------------------------------------------------
    def summary(self) -> dict[str, Any]:
        """Electrical metrics only (no optics).

        Covers the current dip at the repeaters, PFE headroom and clamping, PFE stress (shortfall, excess, time at the cap or at zero, over-current exposure,
        slew limiting), conductor-to-sea voltage, the ground potential rise of the station earths and, when ``cable.insulation_exponent_n`` is known,
        the insulation life consumed.

        Returns:
            ``{name: number}``; units are in the key names (``_V``, ``_mA``, ``_s``).
        """
        tr, m = self.transient, self.meta
        out = {"samples": len(tr.t_s), "dt_s": float(tr.t_s[1] - tr.t_s[0]), "duration_s": float(tr.t_s[-1] - tr.t_s[0])}
        rec = m.get("record")
        if rec is not None:
            # jump bound: if the largest sample-to-sample change had been an instantaneous step, the current would change by dV / R_loop
            out.update({"v_in_min_V": float(rec.values.min()), "v_in_max_V": float(rec.values.max()),
                        "max_abs_dvdt_V_per_s": float(np.abs(rec.rate_per_s).max()),
                        "jump_bound_mA": float(1e3 * np.abs(np.diff(rec.values)).max() / tr.r_loop_ohm)})
        out.update(dip_metrics(self.repeater_current_change_A(), m["margin_A"]))
        out.update(pfe_metrics(tr, m["v_tot_max_V"], m["static_need_V"]))
        out.update(voltage_metrics(tr))
        dist = self.network.controller.disturbance if self.network.controller is not None else None
        out.update(pfe_stress_metrics(tr, m["v_tot_max_V"], m["static_need_V"], dist(tr.t_s) if dist is not None else None, m["i_set_A"]))
        # ground potential rise of the PFE earth electrodes (the larger of the two ends), against the 20 V / 90 V recommendations of Chesnoy p. 387
        i_earth = np.maximum(np.abs(tr.branch_I("pfe_A")), np.abs(tr.branch_I("pfe_B")))
        out.update(gpr_metrics(i_earth, m["r_earth_ohm"], out["dt_s"], float(self.params.get("earthing", "station_vs_system_earth_V_nominal")),
                               float(self.params.get("earthing", "station_vs_system_earth_V_lightning"))))
        out["earth_resistance_ohm"] = m["r_earth_ohm"]
        # insulation life: only when the exponent of the life law is known (it is not, by default). Reference point: the design life at half the static need,
        # the nominal conductor-to-sea voltage at a PFE end; the fraction is the worst over all nodes
        if self.params.has("cable", "insulation_exponent_n"):
            n_exp = float(self.params.get("cable", "insulation_exponent_n"))
            t_ref = 365.25 * 86400.0 * float(self.params.get("cable", "design_life_years"))
            const = constant_from_reference(0.5 * m["static_need_V"], t_ref, n_exp)
            out["insulation_life_consumed_max"] = float(np.max(life_consumed(tr.nodes_V, out["dt_s"], const, n_exp)))
        return out

    def assess(self, targets: Sequence[float] = (100, 200, 250)) -> dict[str, Any]:
        """Summary plus the optical margin and the terminal and traffic metrics.

        Args:
            targets: Terminal rates (Gbit/s). Each is evaluated with an adaptive and a fixed-rate policy; skipped for runs shorter than 2 s.

        Returns:
            The :meth:`summary` keys plus ``q_margin_*`` / OSNR keys and ``{policy}_{rate}G_{mean_rate_fraction, ses, uas, availability, lost_Gbit}``.
        """
        out = self.summary()
        ev = self.optical()                                           # lowest repeater current at each instant (conservative)
        out.update(summarize(ev))
        if self.t_s[-1] - self.t_s[0] >= 2.0:
            for tg in targets:
                for policy, adapt in (("adaptive", True), ("fixed", False)):
                    tr = terminal_trace(self.params, self.t_s, ev["q2_seg_dB"], float(tg), adapt=adapt)
                    mt = traffic_metrics(self.t_s, tr["rate_Gbps"], tr["target_rate_Gbps"])
                    out.update({f"{policy}_{tg}G_{k}": v for k, v in mt.items() if k in ("mean_rate_fraction", "ses", "uas", "availability", "lost_Gbit")})
        return out

    def optical(self) -> dict[str, Any]:
        """Optical evaluation of the lowest repeater current at each instant (the conservative case). Cached after the first call.

        Returns:
            A dictionary of arrays on the run's time axis: ``margin_dB`` (Q margin), ``d_osnr_dB``, ``pump_ratio``, ``q2_seg_dB`` and others.
        """
        ev = getattr(self, "_optical", None)
        if ev is None:
            ev = evaluate(self.params, self.repeater_currents_A().min(axis=1), self.meta["n_repeaters"])
            self._optical = ev
        return ev

    def terminal(self, target_gbps: float, adapt: bool = True) -> dict[str, Any]:
        """Delivered-rate trace of a terminal with the given target (see :mod:`bolts.impact.terminal`).

        Args:
            target_gbps: The rate the terminal is trying to carry (Gbit/s).
            adapt: ``True`` lets the terminal step its rate down and back up with the Q margin; ``False`` holds the rate and counts errored seconds.

        Returns:
            A dictionary with ``rate_Gbps`` and ``target_rate_Gbps`` on the run's time axis, plus the state series.
        """
        return terminal_trace(self.params, self.t_s, self.optical()["q2_seg_dB"], float(target_gbps), adapt=adapt)

    def to_dataframe(self) -> Any:
        """The time series as a pandas DataFrame, with the optical columns added.

        Returns:
            A ``DataFrame`` with the :meth:`series` columns plus ``q_margin_dB``, ``osnr_drop_dB`` and ``pump_ratio``.

        Raises:
            ImportError: pandas is not installed (``pip install bolts[data]``).
        """
        try:
            import pandas as pd
        except ImportError as e:                      # pragma: no cover
            raise ImportError("to_dataframe needs pandas: pip install bolts[data]") from e
        cols = self.series()
        ev = self.optical()
        cols.update({"q_margin_dB": ev["margin_dB"], "osnr_drop_dB": -ev["d_osnr_dB"], "pump_ratio": ev["pump_ratio"]})
        return pd.DataFrame(cols)

    def series(self) -> dict[str, np.ndarray]:
        """The time series worth saving or plotting (the columns of ``series.csv``).

        Returns:
            ``{name: array}`` with ``t_s``, ``v_pfe_total_V``, ``pfe_clamped``, ``i_sense_A``, ``di_min_mA``, ``di_max_mA`` and, with a record, ``v_in_V``.
        """
        tr = self.transient
        d = self.repeater_current_change_A()
        cols = {"t_s": tr.t_s, "v_pfe_total_V": tr.v_tot_V, "pfe_clamped": tr.clamped.astype(float), "i_sense_A": tr.i_sense_A,
                "di_min_mA": 1e3 * d.min(axis=1), "di_max_mA": 1e3 * d.max(axis=1)}
        rec = self.meta.get("record")
        if rec is not None:
            cols["v_in_V"] = rec.sample(tr.t_s)
        return cols

    def save(self, outdir: str | pathlib.Path, targets: Sequence[float] = (100, 200, 250), extra_manifest: dict | None = None) -> pathlib.Path:
        """Write the results of a run to a folder.

        Args:
            outdir: Folder to write (created if needed).
            targets: Terminal rates for the summary, as in :meth:`assess`.
            extra_manifest: Extra key-value pairs recorded in ``manifest.json``.

        Returns:
            The folder, containing ``series.csv``, ``summary.json``, ``manifest.json`` (parameter fingerprint, version, time) and ``node_peaks_V.csv``.
        """
        out = pathlib.Path(outdir)
        out.mkdir(parents=True, exist_ok=True)
        summary = self.assess(targets)
        cols = self.series()
        ev = self.optical()
        cols.update({"q_margin_dB": ev["margin_dB"], "osnr_drop_dB": -ev["d_osnr_dB"], "pump_ratio": ev["pump_ratio"]})
        write_series_csv(out / "series.csv", cols)
        write_json(out / "summary.json", summary)
        write_json(out / "manifest.json", make_manifest(self.params, extra_manifest))
        np.savetxt(out / "node_peaks_V.csv", np.column_stack([np.arange(self.transient.system.n_nodes), node_peaks_V(self.transient)]),
                   delimiter=",", header="node_index,peak_V", comments="")
        return out
