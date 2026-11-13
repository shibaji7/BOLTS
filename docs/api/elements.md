# elements: devices that stamp into the circuit

Circuit elements. Each is a small class with ``stamp(st)``; register your own with :func:`bolts.registry.register_element`.

**Read first:** [Zener and protection](../chapters/13_zener_protection.md), [Repeater and optics](../chapters/04_repeater_and_optics.md), [Power feeding](../chapters/02_power_feeding.md)

| Module | What it does |
|---|---|
| [`arrester`](#bolts.elements.arrester) | Element: surge arrester (a varistor or gas-tube stand-in): conducts above its clamp voltage, in both directions, with a small on-resistance. |
| [`base`](#bolts.elements.base) | The element protocol. An element has a name and one method, ``stamp(st)``, that adds its branches, shunts and sources to a |
| [`beach_joint`](#bolts.elements.beach_joint) | Element: the beach joint box between the land cable and the submarine cable: a contact resistance in series and a small capacitance to *(stub)* |
| [`branching_unit`](#bolts.elements.branching_unit) | Element: branching unit (sea earth, relays, powering states). Planned for v0.3; see ROADMAP.md. The slot exists so the module tree, the docs and th... *(stub)* |
| [`cable_segment`](#bolts.elements.cable_segment) | A cable span: series R (and L) with the geoelectric EMF as a source, shunt C and G to the local sea split between its two ends. |
| [`coil`](#bolts.elements.coil) | Element: air-core surge coil with DC resistance. In series it passes the DC feed current (dropping I R) and chokes fast transients (L di/dt). |
| [`diode_chain`](#bolts.elements.diode_chain) | Elements: voltage-clamp shunts, the surge protection that bypasses a repeater's electronics. A clamp conducts when the voltage across it exceeds it... |
| [`earth_electrode`](#bolts.elements.earth_electrode) | An earth electrode: a resistor from a node to the sea (ground). |
| [`fit_zener`](#bolts.elements.fit_zener) | Fit Zener parameters (Vz, rz, knee, leakage) to datasheet points. Planned for v0.3; see ROADMAP.md. *(stub)* |
| [`land_cable`](#bolts.elements.land_cable) | Element: the land cable between the station and the beach joint. Electrically a cable span whose shunt capacitance goes to the station |
| [`lumped`](#bolts.elements.lumped) | Plain lumped elements (resistor, capacitor, inductor, ideal voltage source). Used by the validation cases and for quick |
| [`pfe`](#bolts.elements.pfe) | One power feed equipment (PFE) terminal: a controlled voltage source behind the landing earth resistance. |
| [`pfe_converter_bank`](#bolts.elements.pfe_converter_bank) | PFE converter bank: converter modules in series that together generate the output voltage, protected N:1 (Chesnoy p. 397; a vendor catalogue shows 6 |
| [`pfe_filter`](#bolts.elements.pfe_filter) | Element: the PFE output L-C filter. A series inductor (with winding resistance) from the converter node ``a`` to the line node ``b`` and a |
| [`pfe_regulator`](#bolts.elements.pfe_regulator) | The PFE current regulator, a first-order loop: the current error relaxes to the ramp-tracking value with time constant tau. |
| [`pump_laser`](#bolts.elements.pump_laser) | Pump laser: light output against drive current. Below the threshold current there is no light; above it the output rises linearly (the slope effici... |
| [`relay`](#bolts.elements.relay) | Element: BU power-switching relay. Planned for v0.3; see ROADMAP.md. The slot exists so the module tree, the docs and the registry are complete. *(stub)* |
| [`repeater`](#bolts.elements.repeater) | A repeater in the power-feed line: the Zener stack (and, later, the surge chain) between its input and output nodes. |
| [`shunt_fault`](#bolts.elements.shunt_fault) | Element: shunt fault to the sea. Planned for v0.3; see ROADMAP.md. The slot exists so the module tree, the docs and the registry are complete. *(stub)* |
| [`zener`](#bolts.elements.zener) | Zener stack of the repeater. v0.1: linear, drop = Vz + rz (I - I_nom), as in the pfe_design study. The piecewise (v0.2), smooth |

::: bolts.elements.arrester
    options:
      show_root_heading: true

::: bolts.elements.base
    options:
      show_root_heading: true

::: bolts.elements.beach_joint
    options:
      show_root_heading: true

::: bolts.elements.branching_unit
    options:
      show_root_heading: true

::: bolts.elements.cable_segment
    options:
      show_root_heading: true

::: bolts.elements.coil
    options:
      show_root_heading: true

::: bolts.elements.diode_chain
    options:
      show_root_heading: true

::: bolts.elements.earth_electrode
    options:
      show_root_heading: true

::: bolts.elements.fit_zener
    options:
      show_root_heading: true

::: bolts.elements.land_cable
    options:
      show_root_heading: true

::: bolts.elements.lumped
    options:
      show_root_heading: true

::: bolts.elements.pfe
    options:
      show_root_heading: true

::: bolts.elements.pfe_converter_bank
    options:
      show_root_heading: true

::: bolts.elements.pfe_filter
    options:
      show_root_heading: true

::: bolts.elements.pfe_regulator
    options:
      show_root_heading: true

::: bolts.elements.pump_laser
    options:
      show_root_heading: true

::: bolts.elements.relay
    options:
      show_root_heading: true

::: bolts.elements.repeater
    options:
      show_root_heading: true

::: bolts.elements.shunt_fault
    options:
      show_root_heading: true

::: bolts.elements.zener
    options:
      show_root_heading: true
