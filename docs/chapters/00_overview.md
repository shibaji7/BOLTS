# 00. The big picture

> **Status:** implemented (v0.1) · **Code:** the whole package · **Figures:** [storm run](../figures/storm_run.png)

## The story

An undersea cable has no power station near its repeaters. The only thing that reaches them is the wire that runs past each one. The trick
that makes this work is to feed the wire with a **constant current** (about 1 A) from power feed equipment (PFE) at the two landings, and to
return the current through the sea. The PFE needs about 1.4 kV for a 751 km link (the wire's own resistance, 12 repeaters at 56 V each, the
earth electrodes).

Now a solar storm arrives. The Earth's magnetic field wobbles, and by Faraday's law that drives electric fields in the ground and the sea. A
long conductor lying in that field collects a voltage along its length. The cable has become a battery of unknown size and changing sign, in
series with the loop. The question is: **does that extra voltage reach the repeaters, and if so, what does it do to the signal and the traffic?**

The answer has a shape. A constant-current supply is built to ignore voltage disturbances: it changes its own voltage by the same amount in
the opposite direction. So slow, moderate storms are absorbed. A disturbance gets through if it is **too big** (the PFE runs out of voltage
range) or **too fast** (faster than the regulator). When the current does change, the repeaters do not care about a rise (the surplus is shunted
off as heat) but they do care about a fall of more than about 10%: the pump lasers starve, the light weakens, the signal quality drops, and at the
extreme the traffic stops.

## The chain

```
voltage record  ->  PFE regulator and range  ->  line current at each repeater  ->  pump power  ->  OSNR, Q margin  ->  terminal and traffic
 (chapter 01)           (02, 03)                       (03)                          (04)             (04)              (05)
```

## The module map

| Package | Role | Chapter |
|---|---|---|
| `config` | parameters with unit, status, source | [07](07_parameters_and_provenance.md) |
| `waveforms`, `space_weather` | the voltage record and how it is applied | [01](01_storm_to_volts.md) |
| `properties`, `elements`, `network` | the cable, repeaters, PFEs as a circuit | [02](02_power_feeding.md), [12](12_cable_properties.md), [13](13_zener_protection.md) |
| `mna` | the solver, including the regulator | [03](03_circuit_model.md) |
| `metrics`, `impact` | current dip, headroom; optics; terminal | [04](04_repeater_and_optics.md), [05](05_terminal_and_traffic.md) |
| `spice`, `validation` | independent checks | [09](09_validation_and_tests.md) |
| `earthing`, `damage`, `lightning`, `lines` | formulas now, slots for later | [15](15_lightning.md), [16](16_earthing_damage.md) |
| `studies`, `plotting`, `io` | sweeps, figures, results | [10](10_run_and_extend.md) |

## Headline results of the first experiments

All for the shipped **synthetic** record and the default parameters; see `examples/gmd/` and the limits in [chapter 08](08_limitations_and_not_implemented.md).

| Question | Answer |
|---|---|
| Voltage the PFEs need in normal running | 1428.8 V (cable 750.8 V, 12 repeaters 672 V, earth 6 V) |
| Loop resistance, and the current change per volt that gets through | 816.8 ohm, 1.224 mA per volt |
| Opposing storm the PFEs can absorb (operator basis, 5 kV total) | up to 3571 V; at a 1.5 kV what-if only 71 V |
| Steady current error for a ramp (regulator 5 ms) | `tau x rate / R_loop`: 5.4 microamps at 0.89 V/s |
| 100 V jump seen through 1 s samples | 0.6 mA (the data cannot show the pulse; the instantaneous bound is 122 mA) |
| Opposing 400 V against 71 V of headroom | the repeater current falls by 403 mA, below the 100 mA margin |
| Optical Q margin at nominal | 10.8 dB above the 5.0 dB limit |

## What this is not

Not a prediction: vendor data are placeholders or unknown, the example record is synthetic, and the field is taken as uniform. It is a way to
ask "what would it take?" with every assumption written down. Not (yet) a branching-unit, lightning or surge model: those are designed in
chapters [14](14_branching_units.md) and [15](15_lightning.md) and raise `NotImplementedYet` today.

Next: [01. From storm to volts](01_storm_to_volts.md).
