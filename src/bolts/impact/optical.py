# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""From the line current at the repeaters to OSNR, Q and bit errors (ported from the pfe_design study; Chesnoy printed pages).

Repeater (Chesnoy 12.2.2, p. 427; Table 10.1, p. 385): the pump lasers run from a constant-current driver fed by a Zener-regulated
supply. At the nominal line current I_set it splits 80% laser, 10% control, 10% Zener shunt, so

* a LOWER line current is harmless down to 0.9 I_set; below that the laser current falls one for one: ``I_LD = clip(I_line - I_ctl, 0, I_LD_nom)``
* a HIGHER line current goes through the Zener shunt (heat, no optical change): ``I_shunt = I_line - I_LD - I_ctl``.

Pump power ratio r = (I_LD - I_th) / (I_LD_nom - I_th); a saturated amplifier's output follows it (p. 428). (This is the author's reading
of the book; the Zener behaviour and the threshold are vendor data.)

Optical chain:
  OSNR(dB/0.1 nm) = P_in - 10 log10(k) - NF + 58                                   (Eq. 5.23, p. 189)
  SNR = OSNR B_opt / R_s;  PDM-QPSK: Q^2 = SNR;  BER = 0.5 erfc(sqrt(Q^2/2))      (Eq. 5.18-5.20, pp. 188-189)
  line Q^2 = SNR - impairments (Table 5.1);  1/Q2_seg = 1/Q2_line + 1/Q2_terminal  (Eq. 5.29, p. 200)
  margin = Q2_seg - Q2_limit (5.0 dB, Table 5.1 line 6); outage when negative.
"""
from __future__ import annotations

import numpy as np
from scipy.special import erfc

from ..config.schema import ParameterSet
from ..elements.pump_laser import PumpLaser

DB_FLOOR = -120.0


def span_loss_dB(p: ParameterSet) -> float:
    """Loss between two amplifiers: fibre attenuation over one spacing plus splices, connectors and gain-flattening filters (dB)."""
    return float(p.get("optical", "fiber_attenuation_dB_per_km")) * float(p.get("repeater", "spacing_km")) + float(p.get("optical", "extra_span_loss_dB"))


def osnr_baseline_dB(p: ParameterSet, n_amplifiers: int) -> float:
    """OSNR at the receiver in the undisturbed state (Eq. 5.23): noise from ``n`` identical amplifiers adds, so OSNR falls by 10 log10(n)."""
    k = max(int(n_amplifiers), 1)
    p_in = float(p.get("optical", "output_power_per_channel_dBm")) - span_loss_dB(p)
    return p_in - 10.0 * np.log10(k) - float(p.get("optical", "noise_figure_dB")) + float(p.get("optical", "osnr_constant_dB"))


def snr_dB(p: ParameterSet, osnr_dB):
    """Electrical SNR from OSNR: OSNR is quoted in 0.1 nm, SNR in the signal's own bandwidth, so the factor is (optical bandwidth / baud rate)."""
    b, r = float(p.get("optical", "optical_bandwidth_GHz")), float(p.get("optical", "baud_rate_GBd"))
    return np.asarray(osnr_dB) - 10.0 * np.log10(r / b)


def q2_limit_dB(p: ParameterSet) -> float:
    """Q^2 the FEC needs to deliver an error-free output (5.0 dB, Chesnoy Table 5.1 line 6)."""
    return float(p.get("optical", "q2_limit_dB"))


def q_chain(p: ParameterSet, osnr_dB) -> dict:
    """OSNR to SNR to Q^2 to BER, and the margin above the FEC limit (all dB except ``ber``)."""
    # line Q^2: the SNR less every impairment that is not noise (nonlinearity, PDL, filtering...), summed in dB
    snr = snr_dB(p, osnr_dB)
    q2_line = snr - float(p.get("optical", "penalties_total_dB"))
    q2_term = float(p.get("optical", "terminal_back_to_back_Q_dB"))
    # the terminal's own back-to-back penalty adds as inverse Q^2 (Eq. 5.29): the segment can never beat its weakest part
    q2_seg = -10.0 * np.log10(10.0 ** (-q2_line / 10.0) + 10.0 ** (-q2_term / 10.0))
    # PDM-QPSK: BER = 0.5 erfc(Q / sqrt(2)) with Q^2 in linear units
    ber = 0.5 * erfc(np.sqrt(10.0 ** (q2_seg / 10.0) / 2.0))
    return {"snr_dB": snr, "q2_line_dB": q2_line, "q2_seg_dB": q2_seg, "margin_dB": q2_seg - q2_limit_dB(p), "ber": ber}


def shannon_gap(p: ParameterSet) -> float:
    """Linear gap to the Shannon limit, calibrated so that the reference channel (100 Gbit/s PDM-QPSK at 25 GBd) needs exactly the
    ITU Q limit: R_ref = 2 R_s log2(1 + SNR_lim / gap). The anchor (that a 100G terminal just meets the limit) is an assumption."""
    rs, r_ref = float(p.get("optical", "baud_rate_GBd")), float(p.get("optical", "channel_rate_Gbps"))
    return 10.0 ** (q2_limit_dB(p) / 10.0) / (2.0 ** (r_ref / (2.0 * rs)) - 1.0)


def capacity_rate_Gbps(p: ParameterSet, snr_eff_dB):
    """Bit rate (Gbit/s) a gap-to-Shannon channel could carry at the given effective SNR, for two polarisations."""
    rs = float(p.get("optical", "baud_rate_GBd"))
    return 2.0 * rs * np.log2(1.0 + 10.0 ** (np.asarray(snr_eff_dB, float) / 10.0) / shannon_gap(p))


def required_snr_dB_for_rate(p: ParameterSet, rate_Gbps: float) -> float:
    """Inverse of :func:`capacity_rate_Gbps`: the SNR a given bit rate needs (dB)."""
    rs = float(p.get("optical", "baud_rate_GBd"))
    return float(10.0 * np.log10(shannon_gap(p) * (2.0 ** (rate_Gbps / (2.0 * rs)) - 1.0)))


def repeater_state(p: ParameterSet, i_line_A) -> dict:
    """Pump, shunt and pump-power ratio for a line-current series (A)."""
    i_line_A = np.asarray(i_line_A, float)
    i_set = float(p.get("pfe", "feed_current_A"))
    f_ld, f_ct = float(p.get("repeater", "pump_current_fraction")), float(p.get("repeater", "control_current_fraction"))
    th_frac = float(p.get("optical", "laser_threshold_fraction"))
    i_ld_nom, i_ctl = f_ld * i_set, f_ct * i_set       # nominal pump and control currents (80% and 10% of the line current)
    # below 0.9 I_set the constant-current driver can no longer hold the pump current: it falls one for one
    i_ld = np.clip(i_line_A - i_ctl, 0.0, i_ld_nom)
    # above nominal, the surplus is taken by the Zener shunt (heat only)
    i_shunt = np.maximum(i_line_A - i_ld - i_ctl, 0.0)
    i_shunt_nom = i_set - i_ld_nom - i_ctl
    r = PumpLaser(i_ld_nom, th_frac).power_ratio(i_ld)      # no light below the threshold current, linear up to the nominal drive
    v_rep = float(p.get("repeater", "voltage_drop_V"))
    return {"i_ld_A": i_ld, "i_shunt_A": i_shunt, "pump_ratio": r, "zener_power_W": i_shunt * v_rep,
            "zener_power_ratio": i_shunt / i_shunt_nom if i_shunt_nom > 0 else np.full_like(i_shunt, np.nan)}


def evaluate(p: ParameterSet, i_line_A, n_repeaters: int) -> dict:
    """Run the whole optical chain on a line-current series: pump state, OSNR change, Q^2, margin, BER and capacity.

    All repeaters are assumed to see the same (lowest) current, a conservative simplification noted in the limits chapter."""
    st = repeater_state(p, i_line_A)
    base = osnr_baseline_dB(p, n_repeaters)
    # a saturated amplifier's output power follows the pump power (p. 428), so OSNR changes by the pump ratio in dB (floored to avoid log 0)
    d_osnr = 10.0 * np.log10(np.maximum(st["pump_ratio"], 10 ** (DB_FLOOR / 10.0)))
    q = q_chain(p, base + d_osnr)
    return {**st, "osnr_base_dB": base, "d_osnr_dB": d_osnr, "osnr_dB": base + d_osnr, **q, "q2_limit_dB": q2_limit_dB(p),
            "capacity_Gbps": capacity_rate_Gbps(p, q["q2_seg_dB"])}


def summarize(res: dict) -> dict:
    """Worst-case numbers of an :func:`evaluate` result, for tables and the run summary."""
    return {"min_pump_ratio": float(res["pump_ratio"].min()), "max_osnr_drop_dB": float(-res["d_osnr_dB"].min()),
            "min_margin_dB": float(res["margin_dB"].min()), "max_ber": float(res["ber"].max()),
            "frac_time_outage": float((res["margin_dB"] < 0.0).mean()), "max_zener_power_ratio": float(np.nanmax(res["zener_power_ratio"]))}
