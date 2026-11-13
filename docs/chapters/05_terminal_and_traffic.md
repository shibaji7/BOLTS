# 05. Terminal and traffic

> **Status:** implemented (timings are placeholders) · **Code:** `bolts.impact.terminal`

## The story

When the light gets worse, a modern terminal does not just fail: it can slow down. But every outage, and every change of speed, costs a **relock**:
the coherent receiver has to find the signal again. Operators judge a link by counters of errored and unavailable seconds, not by the mean rate.

## The format ladder (Chesnoy 5.7.2, pp. 225-227)

Bits per symbol 2 to 6, two polarisations, 25 GBd: `rate = 2 R_s x bits`. The SNR each rate needs comes from a Shannon-gap calibration on one
assumption: **a 100G PDM-QPSK terminal just meets the ITU Q limit** (gap 1.054, 0.23 dB).

| Format | Rate | SNR needed | Margin at the link's 15.8 dB |
|---|---|---|---|
| PDM-QPSK | 100 Gbit/s | 5.0 dB | 10.8 dB |
| PDM-8QAM | 150 Gbit/s | 8.7 dB | 7.1 dB |
| PDM-16QAM | 200 Gbit/s | 12.0 dB | 3.8 dB |
| PDM-32QAM | 250 Gbit/s | 15.1 dB | 0.7 dB |
| PDM-64QAM | 300 Gbit/s | 18.2 dB | -2.4 dB: not supported |

## The state machine

```
carry the format while Q^2 >= its requirement  ->  otherwise traffic stops
after adaptation_delay_s of outage              ->  step down to the highest format that fits (with switch_margin_dB)
after any outage or format change               ->  relock_time_s before traffic resumes
after upshift_hold_s of enough margin           ->  step back up
```

A terminal with the **least margin** is hit first and by repeated dips; a sustained dip is where adaptation pays (one downshift, one relock).

## The counters

ES / SES / UAS are named in Chesnoy p. 366 and defined in ITU-T G.826, which we do **not** hold; the rules here are from general knowledge
(SES: traffic stopped for at least 30% of the second; UAS starts at 10 consecutive SES and ends after 10 consecutive non-SES) and must be verified
before they are quoted. `traffic_metrics` also reports mean delivered rate, lost Gbit and availability.

## How large a swing does it take? (experiment 7)

`examples/gmd/07_swing_onset.py` drives 1 Hz sinusoids of growing amplitude through the whole chain (120 s each, 25 ms steps). These are stress
tests, not storms: the realistic ULF record never moves faster than about 20 V/s.

| Amplitude | 1.5 kV what-if: current dip | Q margin | Traffic | 5 kV design basis |
|---|---|---|---|---|
| 50-100 V | -8 to -35 mA (inside the 100 mA margin) | 10.8 dB | all formats 100% | -8 to -15 mA, unchanged |
| 200-300 V | -158 to -280 mA | 10.7 to 10.4 dB | all 100% | -31 to -46 mA |
| 500 V | -525 mA | 9.0 dB | 100G, 200G 100%; **250G about 0.5%** | -77 mA, 10.8 dB, all 100% |
| 750 V and up | -830 mA and beyond | light lost | every format fails (about 0.5%) | -115 mA at 750 V, -308 mA at 2000 V (10.3 dB), all 100% |

The disturbance is set by how far the swing outruns the PFE's remaining voltage, not by the swing alone. Below the 71 V headroom (1.5 kV
what-if) nothing happens; above it the current falls by about (amplitude minus headroom) divided by the 816.8 ohm loop. The first format to
fail is the one with the least Q headroom (250G, 0.7 dB), then the light itself at about -700 mA.

**A very large, slow swing: +-3 kV with a 2-minute period** (dV/dt up to 157 V/s, 600 s run):

| PFE limit | Current dip | PFE clamped | Light lost | Delivered 100G / 200G / 250G |
|---|---|---|---|---|
| 1.5 kV what-if | about -3.6 A | 84% of the time | 43% of the time | 50 / 49 / 47% |
| 5 kV design basis | about -4 mA | 35% of the time | never | 100 / 100 / 100% |

At the 1.5 kV what-if the supply cannot hold the loop current through the swing, so the traffic is lost whenever the PFE is clamped and the
terminals are relocking. At the 5 kV basis the regulator follows the slow wave (5 ms tau against a 120 s period) and nothing reaches the
repeaters, but only while the storm stays inside the PFE voltage. The ramp-only case (+3 kV in 120 s) is harmless at both limits; the damage is done by the half-wave of
the opposing polarity. Remember that the optical layer here is a placeholder-heavy model ([chapter 07](07_parameters_and_provenance.md)) and that 3 kV
within two minutes is far beyond the 72 V storm backbone of the shipped record.

## Where it lives in the code

| Item | Location |
|---|---|
| Ladder, state machine, counters | `impact.terminal` (`format_ladder`, `terminal_trace`, `traffic_metrics`) |
| Tests | `tests/test_metrics_impact.py` (thresholds 5.0/8.7/12.0/15.1/18.2 dB; sustained-dip behaviour) |

## Assumptions and limits of this chapter

- **Relock time and adaptation delay are unknown** (10 s and 5 s are placeholders; the book gives none): the vendor datum to ask for first.
- **The state machine is conservative**: any dip below the format's threshold stops traffic and starts a relock; a real receiver with strong error correction might ride through short dips.
- Not modelled: protection switching, rerouting, FEC ride-through, traffic above the optical layer.

Next: [06. The field along the link](06_field_along_the_link.md).
