# 08. Limits and what is left out

> **Status:** implemented (a register, kept current with each release)

Two registers: **assumptions taken** (what the model does instead) and **not implemented** (what is left out and why that is acceptable here). Each
row says what would change it. **S** = sourced, **A** = assumed, **U** = unknown.

> **Read this box first.** (1) The example record is synthetic. (2) Vendor values are placeholders or unknown. (3) Nothing has been compared with a real
> PFE record. (4) With 1-second data a faster swing is invisible; `jump_bound_mA` is the worst case.

## A. Assumptions taken

| Item | What BOLTS does | Why acceptable here | What would change it |
|---|---|---|---|
| Uniform net voltage, spread evenly (A) | one record applied equally over every span | the sea gradient cancels local EMF; only the net voltage acts ([06](06_field_along_the_link.md)) | a field model with hotspots |
| 1-second or 1-minute data (A) | linear between samples | nothing faster is known | sub-second magnetometer data |
| First-order regulator, tau = 1/200 s (A) | exact integration of `x' + x/tau = dS/dt / R_loop` | the book gives only "about 200 Hz bandwidth" | the vendor's step response |
| Linear Zener, `r_dyn` = 5 ohm (A) | `Vz + rz dI` | slow storms stay in the linear range | vendor Zener data ([13](13_zener_protection.md)) |
| Constant per-km R, C; G = 0; no L (A/U) | the constant provider | irrelevant for the GMD band | the cable design ([12](12_cable_properties.md)) |
| 60 km spacing, 12 repeaters (A) | `floor(L / spacing)` | typical (50 to 70 km in the book) | the route design |
| 1 A feed (A) | inside the sourced 0.5 to 1.5 A | typical | the system specification |
| PFE limit (A) | 5 kV total by default; 1.5 kV is a what-if | an operator design basis | the equipment actually installed |
| Repeater current split 80/10/10, Zener shunt (S/A) | Chesnoy Table 10.1 with the author's reading of the shunt | the design the book describes | the vendor's repeater |
| Output power follows pump power (A) | gain compression, p. 428 | saturated amplifiers | EDFA test data |
| Lowest repeater current drives the optics (A) | conservative | repeaters differ only for fast changes | per-repeater optics |
| 25 GBd, 100G QPSK anchor, 3.5 dB impairments, 5.0 dB Q limit (S/A) | Chesnoy Table 5.1 and Fig. 5.25 | the book's ideal transponder; conservative | the terminal vendor |
| Terminal relock 10 s, adaptation delay 5 s (A) | placeholders | not in the book | the vendor |
| ES / SES / UAS definitions (A) | from general knowledge | G.826 not held | the standard |
| Earth electrode at sea potential, 3 ohm (A) | R_e in series with the sea | Chesnoy: system earth electrodes below 3 ohm; siting at the landings not documented | the earth design |

## B. Not implemented

| Item | Why left out | Roadmap |
|---|---|---|
| Branching units, powering modes, switching sequences | one segment first | v0.3 ([14](14_branching_units.md)) |
| Nonlinear Zener, diode chain, coil, arrester | needs vendor data and a Newton solver | v0.2 ([13](13_zener_protection.md)) |
| Cable inductance and travelling waves | irrelevant in the GMD band; needed for surges | v0.2 / v0.3 ([15](15_lightning.md)) |
| Lightning and switching surges, thunderstorm statistics | a different regime | v0.2 to v0.4 |
| PFE converter failover, output filter, electroding tone | no data (a "<50 ms" web claim is unverified) | v0.2 / v0.5 |
| Spatial field (hotspot) | v0.1 takes the net voltage | v0.2 ([06](06_field_along_the_link.md)) |
| Frequency-dependent cable, impulse earth, electro-thermal Zener | microsecond physics | v0.5 |
| Damage criteria (thermal, insulation, arrester energy) | no ratings | v0.4 ([16](16_earthing_damage.md)) |
| Repair and ageing margins, nonlinear fibre penalty | do not change which storms matter | not planned |
| Inverse search (largest tolerated forcing) | sweeps and maps give the same answer by hand | later |
| Validation against a real PFE record | none yet | needs data |

## C. What would be checked first

1. The net record: bare EMF against net voltage ([01](01_storm_to_volts.md)).
2. The PFE regulator's real response (step test).
3. The repeater's protection circuit and the 10% current margin.
4. The terminal's relock and adaptation times.

Next: [09. Validation and tests](09_validation_and_tests.md).
