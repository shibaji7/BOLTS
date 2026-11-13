# 10. Run and extend

> **Status:** implemented · **Commands:** `make help`

## Running it

| What | Command |
|---|---|
| Create the environment (numpy, scipy only) | `make env && conda activate bolts` |
| Editable install with the dev tools | `make dev` |
| Everything that should pass before a commit | `make qa` |
| Tests, coverage | `make test`, `make cov` |
| Lint, duplicate-code, header check | `make lint`, `make dupes`, `make spdx` |
| Pre-commit hooks (install once, run all) | `make pre-commit-install`, `make pre-commit` |
| The GMD experiments | `make examples`, or `python examples/gmd/02_storm_record.py` |
| A run from the command line | `bolts run --csv mydata.csv --start 3600 --end 4200 --scale 1.5 --set pfe.max_voltage_kV_per_end=2.5 --out outputs/run --plot` |
| Analytic validation, SPICE cross-check | `bolts validate`, `bolts spice --run` |
| Parameters with status | `bolts params --status unknown` |
| Docs | `make docs`, `make docs-serve`, `make api-docs`, `make doc-figures`, `make param-table` |
| Build and check the distribution | `make build check` |

## Your own record

```toml
# my.toml
[forcing]
csv_path = "mydata.csv"
time_column = "time"
time_format = "iso"          # or "seconds"
voltage_column = "v_ind_V"
window_start_s = 3600        # seconds from the first row
window_end_s = 4200
scale = 1.0
```

Read `jump_bound_mA` in the summary: it is the current an instantaneous jump of the largest sample-to-sample change would reach.

## Changing a parameter without breaking the rules

Edit `src/bolts/config/defaults/*.toml` (and keep `value`, `unit`, `status`, `source`), or pass `--set section.key=value`, or use `overrides=`. A new
parameter needs its status and a source; if you do not know it, set it to `"TBD"` with status `unknown` and say why.

## Adding a device

Write a class with `stamp(st)` ([`docs/dev/adding_element.md`](../dev/adding_element.md)), register it, test it, and add a validation case if the physics has a closed form.

## Adding an experiment

Copy the closest script under `examples/`, keep the SPDX header and a docstring that says what question it asks and what you expect; the README of the folder lists it.

## The changelog rule

Every change under `src/bolts/` needs a line under `## [Unreleased]` in `CHANGELOG.md` (Keep a Changelog sections: Added, Changed, Fixed, Removed). The pre-commit
hook `changelog` enforces it; `SKIP=changelog git commit ...` bypasses it for a change nobody will see.

Next: [11. Glossary](11_glossary.md).
