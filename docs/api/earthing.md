# earthing: soil, electrodes, GPR

Wenner resistivity (Eq. 10.2), a single rod (Eq. 10.3), rods in a line (Eq. 10.4, Sunde form) and the ground potential rise GPR = I R against the 20 V / 90 V recommendations. `impulse_impedance` (soil ionisation, frequency dependence) is a stub for v0.5.

Status: implemented except the impulse impedance. Chapter 16.

**Read first:** [Earthing and damage](../chapters/16_earthing_damage.md)

| Module | What it does |
|---|---|
| [`electrode_resistance`](#bolts.earthing.electrode_resistance) | Resistance of ground electrodes: Chesnoy Eqs. 10.3 and 10.4 (printed p. 388). |
| [`gpr`](#bolts.earthing.gpr) | Ground potential rise (GPR): the potential an earth electrode reaches against remote earth when it carries a current, GPR = I R. |
| [`impulse_impedance`](#bolts.earthing.impulse_impedance) | Impulse (frequency-dependent) earth impedance with soil ionisation. Planned for v0.5; see ROADMAP.md. *(stub)* |
| [`soil`](#bolts.earthing.soil) | Soil resistivity from a four-terminal (Wenner) measurement: Chesnoy Eq. 10.2 (printed p. 387). |

::: bolts.earthing.electrode_resistance
    options:
      show_root_heading: true

::: bolts.earthing.gpr
    options:
      show_root_heading: true

::: bolts.earthing.impulse_impedance
    options:
      show_root_heading: true

::: bolts.earthing.soil
    options:
      show_root_heading: true
