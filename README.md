# BOLTS

**B**ranching-unit and **O**ptical-repeater power-feed **L**oop **T**ransient **S**imulator.

BOLTS models the **stress and vulnerability of submarine power-feed systems** (the PFE, the cable, the repeaters and, next, branching
units) under **geomagnetic disturbances (GMD / space weather)** first, then lightning and switching surges, and traces the
consequences to **loss of signal, failures and traffic loss**.

[![tests](https://github.com/shibaji7/BOLTS/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/shibaji7/BOLTS/actions/workflows/tests.yml)
[![build](https://github.com/shibaji7/BOLTS/actions/workflows/build.yml/badge.svg?branch=main)](https://github.com/shibaji7/BOLTS/actions/workflows/build.yml)
[![docs](https://github.com/shibaji7/BOLTS/actions/workflows/docs.yml/badge.svg?branch=main)](https://github.com/shibaji7/BOLTS/actions/workflows/docs.yml)
[![Docs](https://readthedocs.org/projects/bolts/badge/?version=latest)](https://bolts.readthedocs.io/en/latest/)
[![PyPI](https://img.shields.io/pypi/v/bolts.svg?label=pypi)](https://pypi.org/project/bolts/)
[![Python versions](https://img.shields.io/pypi/pyversions/bolts.svg?label=python)](https://pypi.org/project/bolts/)
[![codecov](https://codecov.io/gh/shibaji7/BOLTS/branch/main/graph/badge.svg)](https://codecov.io/gh/shibaji7/BOLTS)
[![License: LGPL v3+](https://img.shields.io/badge/license-LGPL--3.0--or--later-blue.svg)](LICENSE)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Roadmap](https://img.shields.io/badge/roadmap-published-blue)](ROADMAP.md)
[![status](https://img.shields.io/badge/status-alpha%20v0.2-orange.svg)](ROADMAP.md)
[![Last commit](https://img.shields.io/github/last-commit/shibaji7/BOLTS)](https://github.com/shibaji7/BOLTS/commits/main)
[![Issues](https://img.shields.io/github/issues/shibaji7/BOLTS)](https://github.com/shibaji7/BOLTS/issues)

**[📖 Documentation](https://bolts.readthedocs.io/) · [📦 PyPI](https://pypi.org/project/bolts/) · [🐙 GitHub](https://github.com/shibaji7/BOLTS) · [🐛 Issues](https://github.com/shibaji7/BOLTS/issues) · [📜 Changelog](CHANGELOG.md) · [🗺️ Roadmap](ROADMAP.md)**

> Status: **v0.2 (alpha)**. Point-to-point GMD, PFE over-range stress, nonlinear protection devices (Newton solver) and earthing are implemented and validated; branching units and
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

or `pip install .` in any Python >= 3.11 environment. Optional extras: `plots` (matplotlib), `data` (pandas), `docs` (Sphinx).
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
| `docs/` | Read the Docs site (Sphinx, Markdown chapters) |
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
