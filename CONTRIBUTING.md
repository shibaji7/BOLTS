# Contributing to BOLTS

Thank you for helping. BOLTS is a small, careful scientific package; the rules below keep it that way.

## Set up

```bash
make env && conda activate bolts && make dev
make test lint
```

## Principles

1. **One concern per module.** A function that deserves a name deserves its own module (see `src/bolts/`).
2. **Elements share one protocol:** `Element.stamp(st)`. Adding a device never touches the solver.
3. **Units in names** (`r_ohm_per_km`), no global state, typed dataclasses, pure functions where possible.
4. **Parameters carry provenance.** New parameters go in `src/bolts/config/defaults/*.toml` with `value`, `unit`, `status`, `source`. If you do
   not know a value, set it to `"TBD"` with status `unknown` and say why; never invent a number.
5. **Say what is not implemented.** A planned capability is a module that raises `NotImplementedYet("...", "ROADMAP vX.Y")`.
6. **Cite sources** (book and printed page, standard, paper) in the module docstring. Mark values "to be verified" if they are from memory.
7. **Test everything you add.** Prefer an analytic check (RC, RLC, a closed form) to a snapshot; add a validation case to `src/bolts/validation/`
   when the physics has one. Tests mirror the source tree.

## Adding an element

1. `src/bolts/elements/my_device.py`: a class with `name`, `nodes` and `stamp(st)` (use `st.add_series_branch`, `st.add_capacitance`, ...).
2. Register it in `src/bolts/elements/__init__.py` (or from your own package through the `bolts.elements` entry-point group).
3. `tests/test_my_device.py`, a validation case if there is a closed form, a docs page under `docs/theory/`.

## Style and checks

`make lint` (ruff, line length 110), `make test`, `make cov`, `make docs` (strict). Every source file starts with the SPDX header
`# SPDX-License-Identifier: LGPL-3.0-or-later` and the copyright line.

## Commits and pull requests

Small, focused commits with a message that says why. Open an issue first for anything that changes the public API (`bolts.api`) or a
parameter's meaning. By contributing you agree your work is released under the project license (LGPL-3.0-or-later).

## Changelog policy

Every change under `src/bolts/` needs a line under `## [Unreleased]` in `CHANGELOG.md` (Added, Changed, Fixed, Removed). The pre-commit hook `changelog`
enforces it; `SKIP=changelog git commit` bypasses it for a change nobody will see. Run `make qa` before committing.
