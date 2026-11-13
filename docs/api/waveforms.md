# waveforms: records and pulses

Waveforms. The built-in constructors are registered by name (``bolts.registry.get_waveform("sine")``); register your own with
:func:`bolts.registry.register_waveform` or the ``bolts.waveforms`` entry-point group.

**Read first:** [From storm to volts](../chapters/01_storm_to_volts.md)

| Module | What it does |
|---|---|
| [`base`](#bolts.waveforms.base) | A sampled waveform: time (s) and values (V for voltages, A for currents). Everything that drives a network is a Record. |
| [`combine`](#bolts.waveforms.combine) | Combine records: superpose, concatenate. |
| [`csv_record`](#bolts.waveforms.csv_record) | Read a voltage (or current) record from a CSV file: any time origin, seconds or ISO timestamps, a window, a scale and a step. |
| [`double_exp`](#bolts.waveforms.double_exp) | Double-exponential pulse i(t) = I0 (exp(-t/tau_fall) - exp(-t/tau_rise)) / k, normalised so that the peak equals ``peak``. |
| [`heidler`](#bolts.waveforms.heidler) | Heidler function for lightning return-stroke currents: |
| [`iec62305`](#bolts.waveforms.iec62305) | IEC 62305 stroke classes (first positive 10/350 us, first negative 1/200 us, subsequent 0.25/100 us). *(stub)* |
| [`step_ramp_sine`](#bolts.waveforms.step_ramp_sine) | Elementary test waveforms: step, ramp, sine, and a ramp that is then held. |
| [`window`](#bolts.waveforms.window) | Cut a time window out of a record. |

::: bolts.waveforms.base
    options:
      show_root_heading: true

::: bolts.waveforms.combine
    options:
      show_root_heading: true

::: bolts.waveforms.csv_record
    options:
      show_root_heading: true

::: bolts.waveforms.double_exp
    options:
      show_root_heading: true

::: bolts.waveforms.heidler
    options:
      show_root_heading: true

::: bolts.waveforms.iec62305
    options:
      show_root_heading: true

::: bolts.waveforms.step_ramp_sine
    options:
      show_root_heading: true

::: bolts.waveforms.window
    options:
      show_root_heading: true
