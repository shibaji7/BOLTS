# 13. Zener and protection devices

> **Status:** linear and piecewise Zener, diode chain and arrester implemented (v0.2 round 3) · smooth model v0.3 · electro-thermal v0.5 · **Code:** `bolts.elements.zener`, `diode_chain`, `arrester`, `bolts.mna.newton`

## The story

Inside every repeater a Zener stack holds the supply near 56 V and takes the surplus. In v0.1 it is **linear**: `V = Vz + rz (I - I_nom)`, which is right
while storms move the line current by milliamps. Surges push it far beyond, so the model has a ladder of devices:

| Device | Version | Role |
|---|---|---|
| Linear Zener (`Vz`, `rz`) | **v0.1** | GMD band |
| Piecewise-linear with knee (`PiecewiseZener`) | **v0.2** | what the repeater does when the line current falls below the knee |
| Diode chain (`DiodeChain`, anti-parallel) | **v0.2** | clamp at `n V_f`; book: bypass 200 A long, 450 A / 15 kV short, Chesnoy p. 392 (ratings recorded, not enforced) |
| Surge coil with DC resistance | v0.2 | slows the rising front |
| Arrester (`Arrester`) | **v0.2** | clamp across a node or relay, bidirectional, on-resistance `r_on` |
| Smooth model (soft knee plus exponential) | v0.3 | Newton-friendly |
| Electro-thermal (self-heating, `Vz(T)`) | v0.5 | long pulses |

`fit_zener` (stub) will fit parameters from datasheet points.

## Parameters still unknown

Number of diodes, dynamic resistance, knee current, reverse leakage, temperature coefficient, continuous and surge ratings, thermal resistance and
capacity. All are `unknown` with sweep ranges until a vendor supplies them; asking for one raises `MissingParameter`.

## The piecewise Zener and its two unknowns

`PiecewiseZener` has the linear law above a knee current `I_k` and a falling law below it:

```
I >= I_k      V = V_k + rz (I - I_k)                    the stack conducts (the linear model)
0 <= I < I_k  V = V_k (f + (1 - f) I / I_k)             the stack is off
I < 0         V = f V_k + rz I
```

It is selected when `repeater.zener_knee_current_A` is given (unknown by default, so the default build is the linear model of v0.1). The fraction `f`
(`repeater.zener_below_knee_fraction`, also unknown, 0 if absent) is how much of its knee voltage the repeater keeps at zero current: 0 for a resistive repeater circuit, 1 for a
laser-diode-like stack that holds its voltage (then nothing changes from the linear model). **This matters:** with a constant 56 V per repeater, a storm that the PFE
cannot cancel makes the current collapse because the loop keeps demanding the repeaters' 672 V. Below a knee the demand shrinks and the current falls far less. At the 1.5 kV what-if with
a -2 kV storm the worst repeater current change is -2.36 A (linear), -2.02 A (f = 0.5), -1.61 A (f = 0), and a -1 kV storm costs 67% of the time in lost light with the linear
model and none with f = 0 and a knee at 0.9. The **earlier results in these chapters that use the linear Zener at the 1.5 kV what-if** (study 08, experiment 10, the example
record's dips) therefore describe the linear model; they are the worst case within the range the two unknowns allow, not a prediction (experiment 11).

## Clamp devices

`DiodeChain` and `Arrester` are nonlinear shunts with the piecewise-linear law `I = g_on (v - V_c)+ - g_on (-v - V_c)+ + g_off v`: off below the clamp voltage, a resistance `r_on`
above it. A 1 kV step through 100 ohm into a 1 uF node settles at 313.7 V with a 300 V / 2 ohm arrester (which absorbs 3.1 J while the drive lasts) and at 7.8 V with a four-diode chain.
Exponential diode curves and an arrester's arc collapse are v0.3.

## Nonlinear solving

Nonlinear elements are solved by Newton iteration in `bolts.mna.newton` (v0.2): each device supplies its current or drop and its derivative, the stamp is the
companion linearisation `R_eq = V'(i0), e_eq = V(i0) - R_eq i0` (branch) or `g_eq = I'(v0), i_eq = I(v0) - g_eq v0` (shunt), and the iteration repeats until the unknowns stop changing (a damping
fallback breaks a cycle at a kink). With the PFE regulator the supply voltage is one more unknown, closed by the equation "sensed current = regulator target"; if the supply is clamped or slew-limited
it is pinned and the circuit is solved again. A network without nonlinear elements keeps the cached-LU path; `run_transient(..., newton=True)` forces the Newton path, and the tests show the two agree
to 1e-8. The loop resistance that scales the regulator's ramp term is re-evaluated at each step's operating point.
