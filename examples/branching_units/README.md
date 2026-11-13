# Branching-unit experiments (planned, v0.3)

Nothing runs here yet: `bolts.network.topology_trunk_branch` and `bolts.elements.branching_unit` are documented slots. Planned:

| Planned script | Question |
|---|---|
| `01_trunk_branch_budget.py` | voltage and current budget of a trunk with one branch fed to the BU sea earth |
| `02_gmd_on_branch.py` | how a GMD voltage on the trunk and on the branch shares between the PFEs and the BU earth |
| `03_switching_sequence.py` | zero-potential switching and current-limited hot switching during a reconfiguration |
| `04_bu_surge.py` | a surge arriving at a BU: reflection at the sea earth and stress on the relays |

Needs the branching-unit architecture and its parameters (`config/defaults/bu.toml` is all `unknown`).
