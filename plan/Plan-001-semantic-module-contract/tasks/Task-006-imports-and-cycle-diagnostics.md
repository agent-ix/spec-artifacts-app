---
id: Task-006
title: "FR-003 — Imports, imported types, and the four import diagnostics"
type: Task
status: done
track: B
priority: P0
relationships:
  - target: ix://agent-ix/spec-artifacts-app/FR-003
    type: references
  - target: ix://agent-ix/spec-artifacts-app/FR-004
    type: references
  - target: ix://agent-ix/spec-artifacts-app/TC-014
    type: verifies
  - target: ix://agent-ix/spec-artifacts-app/TC-015
    type: verifies
  - target: ix://agent-ix/spec-artifacts-app/TC-024
    type: verifies
---
# Task-006: FR-003 — Imports, imported types, and the four import diagnostics

## Scope

What it means for this module to reference a type another module owns, and the
four distinct ways that can be wrong.

## Subtasks

- [x] **`semantic.imports` in the only shape the contract admits:** package to exact semver. FR-035 types it that way and the quire loader reads it that way; a type list here is a rejected manifest.
- [x] **`imported_types` in `mappings.yaml`.** The per-package type list the contract has no place for, with agent-ix/quoin#339 filed for the amendment that would move it.
- [x] **The `<org>/<repo>#<Type>` cell parse.** Splits into `ImportedTypeRef { module, type }` and copies no field of the imported type.
- [x] **Missing import.** A cell naming a package the manifest does not pin, or a type `imported_types` does not list, fails naming the line, the module, and the type — and distinguishes the two cases.
- [x] **Over-declared import.** A pinned package no `ImportedTypeRef` and no `composition.expected_artifacts` entry reaches fails naming it: an import nothing uses is a pin nobody can retire.
- [x] **Self-import.** `semantic.imports` naming this module's own `package` fails as the degenerate one-node cycle.
- [x] **Cycles.** Built from this module's manifest plus dynamic-module fixtures synthesized into a temporary directory — never from the machine's installed module root, whose contents are not reproducible. Two-module cycle, three-module cycle, and an acyclic graph that must pass. Traversal starts from the lowest-sorting module on the cycle so the reported order is deterministic.

## Deliverables

- `spec_artifacts_app/manifest.yaml` `semantic.imports`
- `spec_artifacts_app/mappings.yaml` `imported_types`
- `tests/support/import_graph.py` and the synthesized dynamic-module fixtures
- Tests for TC-014, TC-015, TC-024

## Notes

- The three diagnostics are deliberately distinct. A cycle reported as a missing
  import sends the reader to the wrong file.
- A cycle that does not reach this module is reported the same way: the check is
  a property of the graph, not of this module's position in it.
