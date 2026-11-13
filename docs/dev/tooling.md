# Tooling and quality gates

| Tool | Config | Command |
|---|---|---|
| **ruff** (lint and format) | `ruff.toml` | `make lint`, `make fmt` |
| **pylint duplicate-code** (R0801 only) | `.pylintrc` | `make dupes` |
| **SPDX header check** | `scripts/check_spdx.py` | `make spdx` |
| **Changelog guard** | `scripts/check_changelog.py` | `make changelog-check` |
| **pre-commit** | `.pre-commit-config.yaml` | `make pre-commit-install`, `make pre-commit` |
| Tests, coverage | `pyproject.toml` | `make test`, `make cov` |
| All of the above | | `make qa` |

## Rules

- Every `.py` file starts with the SPDX LGPL header and the copyright line.
- Duplicate code of 7 or more similar lines fails `make dupes`; factor it out.
- Anything under `src/bolts/` that you change needs an entry under `## [Unreleased]` in `CHANGELOG.md`. Bypass for invisible changes: `SKIP=changelog git commit`.
- Plot style lives in `bolts.plotting.style` and follows the polar_connect papers (SciencePlots, Tol palette, 190 mm double column); do not set rcParams in scripts.
- Parameter table in chapter 07 is generated: `make param-table`.
