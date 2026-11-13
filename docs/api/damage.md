# damage: life laws

`insulation_withstand` implements V^n t = constant (Chesnoy Eq. 10.1) with Miner's rule over a record. `arrester_energy`, `thermal_i2t` and `criteria` are documented stubs for v0.4.

Status: insulation life implemented; the rest planned. Chapter 16 (earthing and damage).

**Read first:** [Earthing and damage](../chapters/16_earthing_damage.md)

| Module | What it does |
|---|---|
| [`arrester_energy`](#bolts.damage.arrester_energy) | Damage: arrester energy absorption limit. Planned for v0.4; see ROADMAP.md. *(stub)* |
| [`criteria`](#bolts.damage.criteria) | Damage: pass/fail damage criteria combining the above. Planned for v0.4; see ROADMAP.md. *(stub)* |
| [`insulation_withstand`](#bolts.damage.insulation_withstand) | Insulation withstand: the life law  V^n t = constant  (Chesnoy Eq. 10.1, printed p. 383, from Dakin 1983). ``n`` and the constant are |
| [`thermal_i2t`](#bolts.damage.thermal_i2t) | Damage: thermal limit of a device from its I^2 t. Planned for v0.4; see ROADMAP.md. *(stub)* |

::: bolts.damage.arrester_energy
    options:
      show_root_heading: true

::: bolts.damage.criteria
    options:
      show_root_heading: true

::: bolts.damage.insulation_withstand
    options:
      show_root_heading: true

::: bolts.damage.thermal_i2t
    options:
      show_root_heading: true
