# 15. Lightning and thunderstorms

> **Status:** designed, stubs only · v0.2 waveforms · v0.4 Monte Carlo · **Code:** `bolts.waveforms`, `bolts.lightning`

## The story

A different regime: microsecond waves instead of storm hours. The solver is the same; what changes is the forcing and the line model.

| Piece | Version | Notes |
|---|---|---|
| Double-exponential and Heidler pulses | **implemented** | `bolts.waveforms` |
| IEC 62305 classes (10/350, 1/200, 0.25/100 us) | v0.2 | parameters to be verified from the standard before use |
| Stroke statistics (log-normal peak current, flash density, multiplicity) | v0.4 | to be verified |
| Coupling: station structure (GPR), land cable injection, induced voltage | v0.2 to v0.4 | sea strikes judged small |
| Protection staging, damage criteria (`V^n t`, I2t, arrester energy) | v0.4 | Chesnoy Eq. 10.1 |
| Impulse earth impedance | v0.5 | soil ionisation, stub |

## Transmission lines

A 750 km cable has about 4 ms one-way delay, so surge studies need a travelling-wave model: lumped sections sized below the rise time
(`sectioning`) or Bergeron lines (v0.3).

## Honest limit

No measured surge data. Validation is analytic plus the SPICE cross-check, and results are scenario ranges, not predictions.

Next: [16. Earthing and damage](16_earthing_damage.md).
