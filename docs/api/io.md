# io: reading and writing

`writers` and `readers` handle `series.csv` and `summary.json`; `manifest` records the version, the parameter fingerprint and the time of a run so a result can be traced back.

Status: implemented. Chapter 10.

**Read first:** [Run and extend](../chapters/10_run_and_extend.md)

| Module | What it does |
|---|---|
| [`manifest`](#bolts.io.manifest) | Run provenance: what produced a result (versions, parameter fingerprint, parameter counts, time). Written next to every output. |
| [`readers`](#bolts.io.readers) | Read results back. |
| [`writers`](#bolts.io.writers) | Write results: CSV for time series, JSON for numbers. |

::: bolts.io.manifest
    options:
      show_root_heading: true

::: bolts.io.readers
    options:
      show_root_heading: true

::: bolts.io.writers
    options:
      show_root_heading: true
