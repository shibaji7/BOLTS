# plotting: figures in the paper style

`style` sets the shared look (including `pct()`, a percent sign that survives LaTeX), `timeseries` draws the standard five-panel run figure and `network` the conductor-to-sea voltage along the cable. Install the `plots` extra.

Status: implemented. Chapter 10.

**Read first:** [Run and extend](../chapters/10_run_and_extend.md)

| Module | What it does |
|---|---|
| [`network`](#bolts.plotting.network) | Figures about the cable itself: the conductor-to-sea voltage along it, and how the repeaters see the current. |
| [`style`](#bolts.plotting.style) | Plot style shared by every BOLTS figure: the same look as the polar_connect paper figures. |
| [`timeseries`](#bolts.plotting.timeseries) | The standard figure of a run, in the polar_connect paper style: five stacked panels on one time axis. |

::: bolts.plotting.network
    options:
      show_root_heading: true

::: bolts.plotting.style
    options:
      show_root_heading: true

::: bolts.plotting.timeseries
    options:
      show_root_heading: true
