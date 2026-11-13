# config: parameters with provenance

Every number in a run is a `Param` (value, unit, status = sourced / assumed / unknown / override, source). `load_parameters` merges the shipped TOML defaults, an optional user file and `--set section.key=value` overrides; an `unknown` value raises `MissingParameter` when it is used.

Status: implemented. Chapter 07 (parameters and provenance).

**Read first:** [Parameters and provenance](../chapters/07_parameters_and_provenance.md)

| Module | What it does |
|---|---|
| [`loader`](#bolts.config.loader) | Read parameter files (TOML) and merge them over the shipped defaults. |
| [`overrides`](#bolts.config.overrides) | Parse ``section.key=value`` strings (command line ``--set``) into an override dictionary. |
| [`provenance`](#bolts.config.provenance) | Parameter provenance: every number carries its unit, its status and where it came from. |
| [`schema`](#bolts.config.schema) | The parameter set: sections of :class:`~bolts.config.provenance.Param`, with lookup, overrides and a Markdown table. |
| [`validate`](#bolts.config.validate) | Sanity checks on a parameter set (ranges that would make the physics meaningless). |

::: bolts.config.loader
    options:
      show_root_heading: true

::: bolts.config.overrides
    options:
      show_root_heading: true

::: bolts.config.provenance
    options:
      show_root_heading: true

::: bolts.config.schema
    options:
      show_root_heading: true

::: bolts.config.validate
    options:
      show_root_heading: true
