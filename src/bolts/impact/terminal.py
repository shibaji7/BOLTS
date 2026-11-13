# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Terminal behaviour and traffic accounting (ported from pfe_design; the timings are placeholders).

* Format ladder: bits per symbol 2..6 (QPSK..64QAM, Chesnoy 5.7.2, pp. 225-227), rate = 2 R_s x bits; the SNR each needs comes from the
  Shannon-gap calibration of :func:`bolts.impact.optical.shannon_gap`.
* State machine: carries its format while the segment Q^2 >= the format's need; otherwise traffic stops; after ``adaptation_delay_s``
  of outage it drops to the highest format that fits (with ``switch_margin_dB``); after any outage or format change it needs
  ``relock_time_s`` before traffic resumes; it steps back up after ``upshift_hold_s`` of sufficient margin.
* Counters: ES/SES/UAS are named in Chesnoy p. 366 and defined in ITU-T G.826, which is NOT in our PDFs: the definitions here are from
  general knowledge (SES: traffic stopped for at least 30% of the second; UAS starts at 10 consecutive SES and ends after 10 consecutive
  non-SES) and must be verified before they are quoted.
"""
from __future__ import annotations

import numpy as np

from ..config.schema import ParameterSet
from .optical import required_snr_dB_for_rate

NAMES = {2: "PDM-QPSK", 3: "PDM-8QAM", 4: "PDM-16QAM", 5: "PDM-32QAM", 6: "PDM-64QAM"}


def format_ladder(p: ParameterSet) -> list[dict]:
    """The modulation formats a terminal can step through: name, bits per symbol, bit rate and the SNR each needs."""
    rs = float(p.get("optical", "baud_rate_GBd"))
    out = []
    for b in p.get("optical", "bits_per_symbol_ladder"):
        rate = 2.0 * rs * b
        out.append({"name": NAMES.get(int(b), f"{b}-bit"), "bits": int(b), "rate_Gbps": rate, "req_snr_dB": required_snr_dB_for_rate(p, rate)})
    return out


def terminal_trace(p: ParameterSet, t_s, q2_seg_dB, target_rate_Gbps: float, adapt: bool = True) -> dict:
    """Delivered rate (Gbit/s) and format index along a segment-Q^2 series. ``adapt=False`` is a fixed-format terminal."""
    t_s = np.asarray(t_s, float)
    lad = format_ladder(p)
    rates = np.array([f["rate_Gbps"] for f in lad])
    req = np.array([f["req_snr_dB"] for f in lad])
    k_target = int(np.argmin(np.abs(rates - target_rate_Gbps)))
    relock = float(p.get("optical", "relock_time_s"))
    delay = float(p.get("optical", "adaptation_delay_s"))
    hold_up = float(p.get("optical", "upshift_hold_s"))
    marg = float(p.get("optical", "switch_margin_dB"))
    n = len(t_s)
    dt = np.diff(t_s, prepend=t_s[0])      # step length at each sample
    dt[0] = dt[1] if n > 1 else 0.0
    fmt, rate, fidx = k_target, np.zeros(n), np.zeros(n, int)     # current format index, delivered rate, format trace
    bad = lock = hold = 0.0       # seconds: continuous outage so far, relock time still to wait, continuous good margin for an upshift
    was_out = False
    for i in range(n):
        q = q2_seg_dB[i]
        if q >= req[fmt]:                                  # the signal is good enough for the current format
            if was_out:
                lock, was_out = relock, False            # the outage ended: the receiver must relock
            bad = 0.0
            # an upshift needs the next format's SNR plus a margin, held for a while, so the terminal does not flap
            if adapt and fmt < k_target and q >= req[fmt + 1] + marg:
                hold += dt[i]
                if hold >= hold_up:
                    fmt += 1
                    lock = max(lock, relock)               # a format change also costs a relock
                    hold = 0.0
            else:
                hold = 0.0
            if lock > 0.0:                                 # still relocking: no traffic yet
                lock -= dt[i]
            else:
                rate[i] = rates[fmt]
        else:                                              # not enough Q^2: traffic stops
            was_out, lock, hold = True, 0.0, 0.0
            bad += dt[i]
            # after the adaptation delay, drop to the highest format that fits with margin (or the lowest if none does)
            if adapt and bad >= delay:
                ok = np.where(req + marg <= q)[0]
                new = int(ok.max()) if len(ok) else 0
                if new < fmt:
                    fmt, bad = new, 0.0
        fidx[i] = fmt
    return {"rate_Gbps": rate, "format_index": fidx, "target_rate_Gbps": rates[k_target], "ladder": lad}


def traffic_metrics(t_s, rate_Gbps, target_Gbps: float) -> dict:
    """Errored-second style counters from the delivered-rate series (see the module note on definitions)."""
    t_s = np.asarray(t_s, float)
    rate_Gbps = np.asarray(rate_Gbps, float)
    dt = float(np.median(np.diff(t_s)))
    n_sec = int(np.floor((t_s[-1] - t_s[0]) / 1.0))
    if n_sec < 1:
        return {"seconds": 0, "ses": 0, "uas": 0, "availability": float("nan"), "mean_rate_Gbps": float(rate_Gbps.mean()),
                "mean_rate_fraction": float(rate_Gbps.mean() / target_Gbps), "lost_Gbit": float(((target_Gbps - rate_Gbps) * dt).sum())}
    # bin every sample into its whole second; a second is 'severely errored' if traffic was down for >= 30% of its samples
    idx = np.minimum(((t_s - t_s[0]) // 1.0).astype(int), n_sec - 1)
    down = np.bincount(idx, weights=(rate_Gbps <= 0.0).astype(float), minlength=n_sec)
    total = np.bincount(idx, minlength=n_sec)
    ses = down / np.maximum(total, 1) >= 0.3
    # unavailable time (UAS): starts after 10 consecutive SES and ends after 10 consecutive non-SES; the 10 s that trigger it count too
    uas = np.zeros(n_sec, bool)
    i, unavailable = 0, False
    while i < n_sec:
        if not unavailable and i + 10 <= n_sec and ses[i:i + 10].all():
            unavailable, uas[i:i + 10] = True, True
            i += 10
            continue
        if unavailable:
            if i + 10 <= n_sec and (~ses[i:i + 10]).all():
                unavailable = False
                i += 10
                continue
            uas[i] = True
        i += 1
    return {"seconds": n_sec, "ses": int(ses.sum()), "uas": int(uas.sum()), "availability": float(1.0 - uas.sum() / max(n_sec, 1)),
            "mean_rate_Gbps": float(rate_Gbps.mean()), "mean_rate_fraction": float(rate_Gbps.mean() / target_Gbps),
            "lost_Gbit": float(((target_Gbps - rate_Gbps) * dt).sum())}
