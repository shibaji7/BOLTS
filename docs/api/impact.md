# impact: optics and terminal

`optical` turns the current at each repeater into pump power, OSNR, Q and bit-error margin; `terminal` turns the Q margin into link state and lost traffic with placeholder timings. Ported from the pfe_design study.

Status: implemented. Chapters 04 and 05.

**Read first:** [Repeater and optics](../chapters/04_repeater_and_optics.md), [Terminal and traffic](../chapters/05_terminal_and_traffic.md)

| Module | What it does |
|---|---|
| [`optical`](#bolts.impact.optical) | From the line current at the repeaters to OSNR, Q and bit errors (ported from the pfe_design study; Chesnoy printed pages). |
| [`terminal`](#bolts.impact.terminal) | Terminal behaviour and traffic accounting (ported from pfe_design; the timings are placeholders). |

::: bolts.impact.optical
    options:
      show_root_heading: true

::: bolts.impact.terminal
    options:
      show_root_heading: true
