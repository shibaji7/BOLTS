# 14. Branching units and branched networks

> **Status:** graph, builder and validation implemented · BU circuit v0.3 · **Code:** `bolts.network`, `bolts.elements.branching_unit` (stub)

## The story

The network is a **graph**: nodes are the stations, repeaters, BUs and sea-earth electrodes; edges are cable segments. Point to point is the two-node
special case and works end to end today. The builder already accepts the trunk and branch topologies; the BU element itself raises `NotImplementedYet`.

## What a BU model needs (v0.3)

- A **switch matrix** with states: trunk through, branch isolated, branch fed from the BU, branch to sea earth.
- **Powering modes**: double-end trunk; single-end branch to the BU sea earth; polarity rule (negative feed toward a BU sea earth, electrode elution by Faraday's law, Chesnoy Eq. 10.7); bipolar repeaters in branches.
- **Switching sequences** by PFE current and voltage steps (zero-potential switching; current-limiting resistors against hot switching).
- `segments` splits a network into powering segments.
- Surge behaviour: the BU sea earth is a reflection and drain point; arresters across relays; its own earth resistance.

All BU internals are `unknown` placeholders until architecture data exist.

## Assumptions and limits

Branch lengths and earth resistances are inputs; no real BU design is held.

Next: [15. Lightning and thunderstorms](15_lightning.md).
