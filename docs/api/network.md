# network: topology and power modes

`build_network` turns a parameter set and a record into a `Network`: PFE A, cable spans with repeaters, PFE B and the sea return. `graph` holds the container, `validate` checks connectivity. Trunk-and-branch topologies, power modes, segments and switch states are stubs for v0.3.

Status: point-to-point implemented. Chapters 03 and 14.

**Read first:** [The circuit model](../chapters/03_circuit_model.md), [Branching units](../chapters/14_branching_units.md)

| Module | What it does |
|---|---|
| [`builder`](#bolts.network.builder) | Build a network from parameters: picks the topology. Point-to-point only in v0.1; trunk-and-branch (branching units) in v0.3. |
| [`graph`](#bolts.network.graph) | A network is a list of elements; nodes are named by the elements that use them. ``compile()`` stamps everything and returns the |
| [`power_modes`](#bolts.network.power_modes) | How the PFEs share the feed: double-end (each end supplies a share, with opposite signs) or single-end (one PFE failed). |
| [`segments`](#bolts.network.segments) | Split a network into powering segments (a long cable cannot be fed from two PFEs). Planned for v0.3. *(stub)* |
| [`switch_states`](#bolts.network.switch_states) | Branching-unit switch states and the power-reconfiguration state machine (zero-potential switching, current-limiting resistors *(stub)* |
| [`topology_p2p`](#bolts.network.topology_p2p) | Point-to-point power-feed line: PFE A - (cable span, repeater) x N - cable span - PFE B, returned through the sea. |
| [`topology_trunk_branch`](#bolts.network.topology_trunk_branch) | Trunk-and-branch topologies (star, fish-bone, branch-on-branch; Chesnoy Sec. 10.4.2). Planned for v0.3 with the branching unit. *(stub)* |
| [`validate`](#bolts.network.validate) | Topology checks on a stamped circuit: every node must be connected to the sea (ground) through some path. |

::: bolts.network.builder
    options:
      show_root_heading: true

::: bolts.network.graph
    options:
      show_root_heading: true

::: bolts.network.power_modes
    options:
      show_root_heading: true

::: bolts.network.segments
    options:
      show_root_heading: true

::: bolts.network.switch_states
    options:
      show_root_heading: true

::: bolts.network.topology_p2p
    options:
      show_root_heading: true

::: bolts.network.topology_trunk_branch
    options:
      show_root_heading: true

::: bolts.network.validate
    options:
      show_root_heading: true
