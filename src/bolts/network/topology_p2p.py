# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Point-to-point power-feed line: PFE A - (cable span, repeater) x N - cable span - PFE B, returned through the sea.

Nodes: ``A`` and ``B`` at the landings, ``r<j>_in`` and ``r<j>_out`` around repeater j. The induced voltage is spread over the spans
in proportion to their length (equal spans here), with the feed direction and the share applied."""
from __future__ import annotations

import math

from ..config.schema import ParameterSet
from ..earthing.electrode_resistance import landing_resistance_from_parameters
from ..elements.cable_segment import CableSegment
from ..elements.pfe import PFE
from ..elements.pfe_converter_bank import PfeConverterBank
from ..elements.pfe_regulator import PowerFeedController
from ..elements.repeater import Repeater
from ..elements.zener import LinearZener, PiecewiseZener
from ..mna.stamp import RecordSource
from ..properties.factory import provider_from_parameters
from ..waveforms.base import Record
from .graph import Network
from .power_modes import PowerMode, end_weights, max_total_voltage_V


def repeater_count(length_km: float, spacing_km: float) -> int:
    """Number of repeaters on a route: whole spacings that fit (the landing spans are shorter or equal to one spacing)."""
    return math.floor(length_km / spacing_km)


def build_p2p(params: ParameterSet, record: Record | None = None, mode: PowerMode = PowerMode.DOUBLE_END,
              provider=None) -> Network:
    """Build the network. ``record`` is the net induced voltage V_ind(t) (volts); ``None`` builds a quiet line."""
    # --- geometry: N repeaters split the cable into N+1 equal spans ---
    length = float(params.get("cable", "length_km"))
    n_rep = repeater_count(length, float(params.get("repeater", "spacing_km")))
    n_span = n_rep + 1
    span_km = length / n_span
    # --- electrical parameters, each read through the parameter store so an `unknown` value raises instead of defaulting ---
    # a provider answers per position, so a section table or a depth profile gives each span its own R, C, G, L (the constant one gives all the same)
    provider = provider or provider_from_parameters(params)
    t_seabed = float(params.get("cable", "seabed_temperature_C"))
    span_rlcg = [provider.rlcg((k + 0.5) * span_km, 0.0, t_seabed) for k in range(n_span)]
    i_set = float(params.get("pfe", "feed_current_A"))
    s_dir = int(params.get("pfe", "feed_direction"))
    share = float(params.get("cable", "emf_share_of_loop"))
    vz, rz = float(params.get("repeater", "voltage_drop_V")), float(params.get("repeater", "dynamic_resistance_ohm"))
    # a known knee current selects the piecewise Zener (nonlinear, solved by Newton iteration); otherwise the linear one of v0.1
    zener = PiecewiseZener(vz, rz, i_set, float(params.get("repeater", "zener_knee_current_A")),
                   float(params.get("repeater", "zener_below_knee_fraction")) if params.has("repeater", "zener_below_knee_fraction") else 0.0) \
        if params.has("repeater", "zener_knee_current_A") else LinearZener(vz, rz, i_set)
    r_e = landing_resistance_from_parameters(params)      # 3 ohm bound, or computed from the soil and the rod electrode when those are given
    f = float(params.get("pfe", "split_fraction_end_A"))
    # a single-end configuration in the parameters overrides the default double-end mode
    if params.get("pfe", "feed_configuration") != "double_end" and mode is PowerMode.DOUBLE_END:
        mode = PowerMode.SINGLE_END_A
    w_a, w_b = end_weights(mode, f)

    # --- elements: A - span - rep - span - ... - span - B, nodes named so that repeater j sits between r<j>_in and r<j>_out ---
    net = Network()
    weight = s_dir * share * (span_km / length)                  # each span's share of the record
    nodes = ["A"] + [x for j in range(1, n_rep + 1) for x in (f"r{j}_in", f"r{j}_out")] + ["B"]
    for k in range(n_span):
        a, b = nodes[2 * k], nodes[2 * k + 1]
        emf = RecordSource(record, weight) if record is not None else None
        rl = span_rlcg[k]
        net.add(CableSegment(f"span{k}", a, b, span_km, rl.r_ohm_per_km, rl.c_F_per_km, rl.g_S_per_km, rl.l_H_per_km, emf))
        if k < n_rep:
            net.add(Repeater(f"rep{k + 1}", f"r{k + 1}_in", f"r{k + 1}_out", zener))
    # the two PFE terminals: opposite-sign weights share one total voltage, which the regulator controls
    pfe_a = net.add(PFE("pfe_A", "A", r_e, w_a))
    pfe_b = net.add(PFE("pfe_B", "B", r_e, w_b))

    # --- regulator: holds the current at the set point; the sensed branch is pfe_A (the loop current is the same everywhere in DC) ---
    v_max_end = 1e3 * float(params.get("pfe", "max_voltage_kV_per_end"))
    if params.has("pfe", "converter_modules") and params.has("pfe", "converter_module_rating_V"):      # a converter bank, when given, sets the cap
        bank = PfeConverterBank(int(params.get("pfe", "converter_modules")), float(params.get("pfe", "converter_module_rating_V")),
                                int(params.get("pfe", "converter_spare_modules")))
        v_max_end = bank.max_voltage_V(int(params.get("pfe", "converter_failed_modules")))
    slew = float(params.get("pfe", "output_slew_limit_V_per_s")) if params.has("pfe", "output_slew_limit_V_per_s") else None
    disturbance = None
    if record is not None:
        disturbance = lambda t: s_dir * share * record.sample(t)      # noqa: E731  S(t): the loop's induced source
    net.controller = PowerFeedController(
        [pfe_a.source, pfe_b.source], "pfe_A", i_set, float(params.get("pfe", "regulator_response_s")),
        max_total_voltage_V(mode, v_max_end, f), disturbance,
        branch_of_source={id(pfe_a.source): "pfe_A", id(pfe_b.source): "pfe_B"}, slew_V_per_s=slew)
    # bookkeeping used by the metrics: static_need = what the PFEs must supply with no storm (conductor + earths + Zener drops)
    net.meta = {"n_repeaters": n_rep, "n_spans": n_span, "span_km": span_km, "length_km": length, "i_set_A": i_set, "r_earth_ohm": r_e,
                "margin_A": i_set * float(params.get("repeater", "current_margin_fraction")),
                "repeater_branches": [f"rep{j}" for j in range(1, n_rep + 1)],
                "span_branches": [f"span{k}" for k in range(n_span)], "mode": mode.value,
                "v_max_end_V": v_max_end, "v_tot_max_V": net.controller.v_tot_max_V,
                "static_need_V": i_set * (sum(rl.r_ohm_per_km for rl in span_rlcg) * span_km + 2 * r_e) + n_rep * zener.vz_V, "record": record}
    return net
