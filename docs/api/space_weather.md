# space_weather: GMD forcing

`gmd_source` spreads a net end-to-end induced voltage V_ind(t) over the spans, `from_efield` computes V = E L from a uniform field, `synthetic` generates the shipped physically-shaped example record. A SCUBAS or measured series is read as CSV through `load_waveform`.

Status: implemented. Chapters 01 and 06.

**Read first:** [From storm to volts](../chapters/01_storm_to_volts.md), [Field along the link](../chapters/06_field_along_the_link.md)

| Module | What it does |
|---|---|
| [`from_efield`](#bolts.space_weather.from_efield) | Net voltage from a uniform geoelectric field: V = E L (E in V/km along the cable direction, L in km). A convenience for |
| [`gmd_source`](#bolts.space_weather.gmd_source) | GMD / space-weather forcing: a net end-to-end induced voltage V_ind(t) spread over every span of the cable. |
| [`synthetic`](#bolts.space_weather.synthetic) | A synthetic but physically shaped 1-second record of the net induced voltage along a long cable (the generator behind ``data/example_vind_1s.csv``). |

::: bolts.space_weather.from_efield
    options:
      show_root_heading: true

::: bolts.space_weather.gmd_source
    options:
      show_root_heading: true

::: bolts.space_weather.synthetic
    options:
      show_root_heading: true
