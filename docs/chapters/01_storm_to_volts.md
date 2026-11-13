# 01. From storm to volts

> **Status:** implemented (the record and its application); the field model that *produces* the record is outside BOLTS · **Code:**
> `bolts.waveforms`, `bolts.space_weather`

## The story

A magnetic disturbance changes the magnetic field at the Earth's surface. By Faraday's law a changing field induces an electric field in the
ground and the sea. Over a long cable the electric field along its length adds up to an **electromotive force (EMF)**. But the sea carries the same field,
so it also develops a potential between the two landings, and most of the cable's EMF is cancelled locally. What the PFE sees is the **net
end-to-end voltage**.

## What BOLTS takes as input

BOLTS does not compute the field. It takes the net voltage as a **record** `V_ind(t)` (volts):

```
V_ind(t) = sum of the EMF along the cable  +  sea-earth potential at one landing  -  at the other
```

For the Point Hope to Gambell link studied before BOLTS (the `pfe_design` study, using the SCUBAS earthed-cable solution), the bare EMF was 641 V
but the net voltage only 72 V, because the sea potentials (+285 V and -285 V) cancel most of the EMF. Which of the two the PFE actually sees is the
first open question of the whole study: **use the net record from a field model, not the bare E x L**. `space_weather.from_efield` gives
`E x L` for quick estimates and says so.

## The record

| Property | Convention |
|---|---|
| Unit | volts |
| Sign | positive when the voltage drives current toward **increasing chainage**; with feed direction `s = +1` it then **assists** the PFEs |
| Between samples | linear (a jump between two samples is a ramp over the sampling step; see [chapter 03](03_circuit_model.md)) |
| Where it acts | spread over every span in proportion to its length, so it acts along the whole cable |
| Source | `RecordSource(record, weight)` in every span's branch; `GMDSource` for the weights |

## Forcing knobs (the experiment dials)

| Knob | How |
|---|---|
| your own 1-second or sub-second data | `bolts.load_waveform(path, params=...)`; columns, time format, window, scale and step in the `[forcing]` parameters |
| amplitude what-if | `forcing.scale` or `Record.scaled(k)` |
| speed what-if | `Record.compressed(k)` plays the record `k` times faster |
| a burst on top of a storm | `waveforms.combine.plus` |
| test waves | `waveforms.step_ramp_sine`: step, ramp, sine, ramp-hold |
| surge pulses (for later chapters) | `double_exponential`, `heidler` |

## Where it lives in the code

| Item | Location |
|---|---|
| Record and its transformations | `bolts.waveforms.base`, `window`, `combine` |
| CSV reading (seconds or ISO time, window, scale, step) | `bolts.waveforms.csv_record` |
| Spreading over spans | `bolts.space_weather.gmd_source`, `bolts.network.topology_p2p` |
| Tests | `tests/test_waveforms.py`, `tests/test_space_weather_properties.py` |

## Assumptions and limits of this chapter

- **The field is uniform along the cable.** A non-uniform field changes how the voltage is spread, not the net voltage ([chapter 06](06_field_along_the_link.md)).
- **The data are what they are.** A 1-minute record has no sub-minute content; a 1-second record cannot show a faster swing. The summary reports
  `jump_bound_mA` for the worst instantaneous jump.
- **The example record is synthetic** (the frozen storm backbone scaled to about -200 V, four bands of random pulsations (2.5 to 600 s) and one onset impulse; `scripts/make_synthetic_vind.py`).

Next: [02. Powering the cable](02_power_feeding.md).
