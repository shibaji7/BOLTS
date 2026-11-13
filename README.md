# BOLTS

**B**ranching-unit and **O**ptical-repeater power-feed **L**oop **T**ransient **S**imulator.

BOLTS models the **stress and vulnerability of submarine power-feed systems** (the PFE, the cable, the repeaters and, next, branching
units) under **geomagnetic disturbances (GMD / space weather)** first, then lightning and switching surges, and traces the
consequences to **loss of signal, failures and traffic loss**.

[![License: LGPL v3+](https://img.shields.io/badge/license-LGPL--3.0--or--later-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-informational.svg)](pyproject.toml)
[![status](https://img.shields.io/badge/status-alpha%20v0.1-orange.svg)](ROADMAP.md)

> Status: **v0.1 (alpha)**. Point-to-point GMD is implemented and validated; branching units, nonlinear protection devices and
> lightning are documented slots that raise `NotImplementedYet` (see the [roadmap](ROADMAP.md)).

## What it does

A repeatered cable is a long series circuit fed with a constant current. A storm adds a voltage along the cable; the PFE changes its own
voltage to keep the current constant, and the repeaters live on that current. BOLTS follows the chain

```
induced voltage -> PFE regulator and voltage range -> line current at every repeater -> pump power -> OSNR / Q margin -> terminal rate and traffic
```

with a modular, tested circuit solver (modified nodal analysis), parameters that carry their unit, status and source, and an
independent ngspice cross-check.

## Install

```bash
git clone <your repository URL> BOLTS && cd BOLTS
make env                  # conda env "bolts": python 3.12, numpy, scipy only
conda activate bolts
make dev                  # editable install with pytest, ruff, build, twine
make test
```

or `pip install .` in any Python >= 3.11 environment. Optional extras: `plots` (matplotlib), `data` (pandas), `docs` (mkdocs).
`ngspice` (optional, system binary) enables the SPICE cross-check.

## Quick start

```python
import bolts

params = bolts.load_parameters(overrides={"pfe.max_voltage_kV_per_end": 0.75})   # a 1.5 kV total what-if
record = bolts.load_waveform("data/example_vind_1s.csv", params=params)           # your 1-second voltage record
net    = bolts.build_network(params, record)                                      # point-to-point: PFE, 13 spans, 12 repeaters
result = bolts.run_transient(net, params)
print(bolts.assess(result)["di_min_mA"])                                          # worst repeater current change, mA
```

```bash
bolts run --csv mydata.csv --start 3600 --end 4200 --scale 1.5 --set pfe.max_voltage_kV_per_end=2.5 --out outputs/run --plot
bolts params --status unknown        # what we still do not know
bolts validate                       # analytic validation cases
bolts spice --run                    # compare with ngspice
bolts doctor
```

## Honest by design

Every parameter is `value, unit, status, source` with status **sourced**, **assumed**, **unknown** or **override**. An `unknown` value
(`TBD`) raises `MissingParameter` instead of being guessed. The shipped example record is **synthetic**. Vendor data (repeater circuit, PFE
filter, branching-unit design) are mostly proprietary, so results are scenario ranges, not predictions.

## Layout

| Path | What |
|---|---|
| `src/bolts/config/` | parameter store, provenance, defaults (TOML) |
| `src/bolts/waveforms/`, `space_weather/` | records (CSV, step, ramp, sine, double-exponential, Heidler) and the GMD source |
| `src/bolts/properties/` | cable R, L, G, C providers |
| `src/bolts/elements/` | cable segment, repeater, Zener, PFE, regulator, electrodes, lumped parts, and future device slots |
| `src/bolts/network/`, `mna/`, `lines/` | topology, modified nodal analysis, time integration |
| `src/bolts/metrics/`, `impact/`, `damage/` | current dip, headroom, device stress; optics and terminal; damage laws |
| `src/bolts/earthing/`, `lightning/` | earth formulas now; lightning slots for v0.2 to v0.4 |
| `src/bolts/spice/`, `validation/`, `studies/`, `plotting/`, `io/` | ngspice export and compare, analytic cases, sweeps, figures, results |
| `docs/` | Read the Docs site (mkdocs-material) |
| `tests/` | one test file per module group |

## Develop

`make help` lists everything: `test`, `cov`, `lint`, `fmt`, `docs`, `build`, `check`, `spice-check`, `tree`, `clean`.
See [CONTRIBUTING.md](CONTRIBUTING.md) and [ROADMAP.md](ROADMAP.md).

## Making the repository private on GitHub (when you are ready)

```bash
gh repo create shibaji7/BOLTS --private --source . --remote origin
git push -u origin main
```

## License and citation

Copyright (C) 2026 Shibaji Chakraborty. Licensed under the **GNU Lesser General Public License v3.0 or later** (`LICENSE`, with the
GPL text in `COPYING` as the LGPL requires). Cite with `CITATION.cff`.
