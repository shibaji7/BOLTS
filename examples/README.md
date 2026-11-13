# Examples: experiments

Each script is one experiment. They are runnable (`python examples/gmd/02_storm_record.py`), write their results and figures to
`outputs/examples/<script name>/` and print the headline numbers. Figures use the polar_connect paper style (`bolts.plotting.style`).
`make examples` runs the GMD set; `tests/test_examples.py` smoke-tests them.

| Folder | Study | Status |
|---|---|---|
| [`gmd/`](gmd) | geomagnetic disturbances and space weather on a point-to-point cable | **runnable** |
| [`lightning/`](lightning) | thunderstorms, ground potential rise, surges | planned (v0.2 to v0.4) |
| [`branching_units/`](branching_units) | trunk-and-branch powering, switching, BU surges | planned (v0.3) |

## Adding an experiment

1. Copy a script of the closest study; keep the SPDX header and a docstring that says **what question it asks and what you expect**.
2. Use only the public API (`bolts.*`) so the script doubles as documentation; put shared helpers in `examples/_common.py`.
3. Write outputs under `outputs/examples/<script name>/` (`common.out_dir(__file__)`).
4. Add it to the table in the folder's README and to `tests/test_examples.py`.
5. When the experiment becomes a result you rely on, add a validation case or a regression test for it.
