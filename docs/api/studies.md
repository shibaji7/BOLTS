# studies: sweeps and maps

`sweep` runs a study function over a list of values of one parameter, `sensitivity` changes each listed parameter up and down, `map2d` fills a grid of one metric. The GMD experiments use them.

Status: implemented. Chapter 10.

**Read first:** [Run and extend](../chapters/10_run_and_extend.md)

| Module | What it does |
|---|---|
| [`map2d`](#bolts.studies.map2d) | A two-parameter grid of one metric (for example surge amplitude against period). |
| [`sensitivity`](#bolts.studies.sensitivity) | One-at-a-time sensitivity: change each listed parameter by a relative step (up and down) and report the change of a metric. |
| [`sweep`](#bolts.studies.sweep) | Run one study function over a list of values of one parameter. |

::: bolts.studies.map2d
    options:
      show_root_heading: true

::: bolts.studies.sensitivity
    options:
      show_root_heading: true

::: bolts.studies.sweep
    options:
      show_root_heading: true
