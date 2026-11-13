# Later: microsecond windows for surges (deferred from v0.2)

**Status:** not started. `bolts.mna.window_run.run_window` is a stub that raises `NotImplementedYet`.

## Why it is separate
The GMD runs use fixed steps of 25 ms to 1 s over minutes to hours. A lightning stroke (front about 1 to 10 microseconds) or a switching surge needs a
step of about a microsecond over a few milliseconds. One fixed step cannot do both, and a 750 km cable takes about 4 ms one way, so the cable cannot be
a single lump for these pulses.

## Plan
1. **Window run.** Run the slow case first; take its state (node voltages, branch currents) at the event time as the initial state of a short window
   (a few ms at about 1 us) in which the surge source is added. The regulator is frozen during the window (its 5 ms time constant is long against a
   microsecond pulse, but not against a few ms; make this explicit and test both).
2. **Sectioning.** Use `lines.sectioning.sections_for_rise_time` so each lumped section's delay is at most one tenth of the pulse front, or switch to
   the travelling-wave `lines.bergeron` line (roadmap v0.3) for the cable.
3. **Cost check.** About 800 nodes, 1 us steps, 5 ms (5000 steps): the cached LU makes this seconds on a laptop; verify before promising it.
4. **Nonlinear devices.** Zeners, diode chains and arresters (v0.2, group D) are what the surge actually drives, so the window run needs the Newton solver.

## Open questions
- How the PFE output filter and the earth electrode behave at microsecond rates (frequency-dependent earth impedance is roadmap v0.5).
- Initial-state handoff when the slow run has a clamped PFE.
- Validation: analytic line step plus an ngspice cross-check; there are no measured surge records.
