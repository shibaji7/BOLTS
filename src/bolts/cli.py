# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Command line: ``bolts run | params | validate | spice | doctor``."""
from __future__ import annotations

import argparse
import sys

from . import __version__
from .api import assess, build_network, load_parameters, load_waveform, run_transient
from .config.overrides import parse_overrides
from .errors import BoltsError


def _add_input_args(sp: argparse.ArgumentParser) -> None:
    """Options shared by every command that reads a voltage record (``run`` and ``spice``)."""
    sp.add_argument("--params", help="parameter TOML merged over the shipped defaults")
    sp.add_argument("--set", action="append", metavar="section.key=value", help="override any parameter (repeatable)")
    sp.add_argument("--csv", help="voltage CSV (overrides forcing.csv_path)")
    sp.add_argument("--start", type=float, help="window start, s from the first row")
    sp.add_argument("--end", type=float, help="window end, s from the first row (negative = end of file)")
    sp.add_argument("--scale", type=float, help="multiply the voltages")
    sp.add_argument("--dt", type=float, help="time step of the run, s (default: the record's spacing)")


def _params(a) -> object:
    """Parameters from the defaults, the optional file, ``--set`` items and the window / scale flags (flags win over ``--set``)."""
    ov = parse_overrides(a.set)
    for key, val in (("forcing.window_start_s", a.start), ("forcing.window_end_s", a.end), ("forcing.scale", a.scale)):
        if val is not None:
            ov[key] = val
    return load_parameters(a.params, ov or None)


def _cmd_run(a) -> int:
    """``bolts run``: record -> network -> transient -> assessment, printed and saved."""
    p = _params(a)
    rec = load_waveform(a.csv, params=p)
    net = build_network(p, rec)
    res = run_transient(net, p, dt_s=a.dt)
    s = assess(res)
    print(f"{rec.label}: {s['samples']} samples at {s['dt_s']:g} s = {s['duration_s']:.0f} s; V_ind {s['v_in_min_V']:.1f} to {s['v_in_max_V']:.1f} V")
    print(f"PFE total {s['v_pfe_min_V']:.0f} to {s['v_pfe_max_V']:.0f} V (static need {s['static_need_V']:.0f} V, limit {s['v_tot_max_V']:.0f} V); "
          f"clamped {100 * s['frac_pfe_clamped']:.2f}% of the time")
    print(f"repeater current change {s['di_min_mA']:.1f} to {s['di_max_mA']:+.1f} mA (margin {s['margin_mA']:.0f} mA; below it "
          f"{100 * s['frac_time_below_margin']:.2f}% of the time); an instantaneous jump of the largest sample step would reach {s['jump_bound_mA']:.0f} mA")
    print(f"Q margin down to {s['min_margin_dB']:.2f} dB; outage {100 * s['frac_time_outage']:.2f}% of the time; largest conductor-to-sea voltage {s['v_cs_peak_V']:.0f} V")
    for tg in (100, 200, 250):      # one line per terminal target rate: delivered share when adaptive vs fixed-format
        k = f"adaptive_{tg}G_mean_rate_fraction"
        if k in s:
            print(f"  {tg}G target: adaptive {100 * s[k]:.1f}% delivered ({s[f'adaptive_{tg}G_ses']} SES), fixed {100 * s[f'fixed_{tg}G_mean_rate_fraction']:.1f}%")
    out = res.save(a.out, extra_manifest={"command": "run", "csv": str(a.csv or p.get('forcing', 'csv_path'))})
    print(f"wrote series.csv, summary.json, manifest.json, node_peaks_V.csv in {out}")
    if a.plot:
        from .plotting.timeseries import plot_result
        print("wrote", plot_result(res, out / "run.png"))
    return 0


def _cmd_params(a) -> int:
    """``bolts params``: list parameters with their status; filter by text or by status (``--status unknown`` shows what is missing)."""
    p = load_parameters(a.params, parse_overrides(a.set) or None)
    rows = [q for q in p.params() if (not a.filter or a.filter in q.key) and (not a.status or q.status.value == a.status)]
    print(f"{'key':44s} {'value':>14s} {'unit':10s} {'status':9s}")
    for q in rows:
        print(f"{q.key:44s} {str(q.value)[:14]:>14s} {q.unit:10s} {q.status.value:9s}")
    print(f"\n{len(rows)} shown; counts {p.counts()}; fingerprint {p.fingerprint()}")
    return 0


def _cmd_validate(a) -> int:
    """``bolts validate``: run the analytic cases; the exit code is 1 if any fails (usable in CI)."""
    from .validation import run_all
    bad = 0
    for c in run_all():
        ok = "PASS" if c.passed else "FAIL"
        bad += not c.passed
        print(f"{c.name:16s} error {c.error:.2e} (tolerance {c.tolerance:.1e})  {ok}  {c.detail}")
    return 1 if bad else 0


def _cmd_spice(a) -> int:
    """``bolts spice``: write the netlist; with ``--run`` also run ngspice and compare every node voltage."""
    from .spice.compare import compare_voltages
    from .spice.netlist import write_netlist
    from .spice.run_ngspice import ngspice_path, run_ngspice
    p = _params(a)
    rec = load_waveform(a.csv, params=p)
    res = run_transient(build_network(p, rec), p, dt_s=a.dt)
    path = write_netlist(res, a.out)
    print("wrote", path)
    if a.run:
        if ngspice_path() is None:
            print("ngspice not found on PATH; netlist written only", file=sys.stderr)
            return 1
        v = run_ngspice(res.transient.system, res.transient.t_s, res.transient.v_tot_V)
        c = compare_voltages(res.transient.nodes_V, v)
        print(f"BOLTS against ngspice: max difference {c['max_abs_V']:.3e} V ({c['max_rel']:.2e} of {c['scale_V']:.0f} V), RMS {c['rms_V']:.3e} V")
    return 0


def _cmd_doctor(a) -> int:
    """``bolts doctor``: versions, optional tools found, and what is registered (first thing to run when something misbehaves)."""
    import platform

    import numpy
    import scipy

    from .registry import element_names, waveform_names
    from .spice.run_ngspice import ngspice_path
    print(f"bolts {__version__}  python {platform.python_version()}  numpy {numpy.__version__}  scipy {scipy.__version__}")
    print(f"ngspice: {ngspice_path() or 'not found (optional; needed only for the SPICE cross-check)'}")
    for mod in ("matplotlib", "pandas"):
        try:
            __import__(mod)
            print(f"{mod}: available")
        except ImportError:
            print(f"{mod}: not installed (optional extra)")
    p = load_parameters()
    print(f"parameters: {p.counts()}  fingerprint {p.fingerprint()}")
    print(f"elements: {', '.join(element_names())}")
    print(f"waveforms: {', '.join(waveform_names()) or '(none registered yet)'}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """The argument parser (separate from :func:`main` so tests can inspect it)."""
    ap = argparse.ArgumentParser(prog="bolts", description="BOLTS: Branching-unit and Optical-repeater power-feed Loop Transient Simulator.")
    ap.add_argument("--version", action="version", version=f"bolts {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="run a voltage record through the whole chain")
    _add_input_args(r)
    r.add_argument("--out", default="outputs/run", help="output directory")
    r.add_argument("--plot", action="store_true", help="also write a figure (needs matplotlib)")
    r.set_defaults(fn=_cmd_run)
    q = sub.add_parser("params", help="list parameters with unit, status and source")
    q.add_argument("--params")
    q.add_argument("--set", action="append")
    q.add_argument("--filter", help="only keys containing this text")
    q.add_argument("--status", choices=["sourced", "assumed", "unknown", "override"])
    q.set_defaults(fn=_cmd_params)
    v = sub.add_parser("validate", help="run the analytic validation cases")
    v.set_defaults(fn=_cmd_validate)
    s = sub.add_parser("spice", help="export an ngspice netlist (and compare with ngspice)")
    _add_input_args(s)
    s.add_argument("--out", default="outputs/bolts.cir")
    s.add_argument("--run", action="store_true", help="run ngspice and compare the node voltages")
    s.set_defaults(fn=_cmd_spice)
    d = sub.add_parser("doctor", help="check the installation")
    d.set_defaults(fn=_cmd_doctor)
    return ap


def main(argv: list[str] | None = None) -> int:
    """Entry point (``bolts`` script). Returns 0 on success, 1 for failed validation, 2 for a user error such as a missing file."""
    a = build_parser().parse_args(argv)
    try:
        return a.fn(a)
    except BoltsError as e:
        print(f"bolts: {e}", file=sys.stderr)
        return 2
    except FileNotFoundError as e:
        print(f"bolts: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
