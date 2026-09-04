---
id: Task-005
title: "FR-004 — mappings.yaml, its schema, and the reference mapping oracle"
type: Task
status: done
track: B
priority: P0
relationships:
  - target: ix://agent-ix/spec-artifacts-app/FR-004
    type: references
  - target: ix://agent-ix/spec-artifacts-app/TC-019
    type: verifies
  - target: ix://agent-ix/spec-artifacts-app/TC-020
    type: verifies
  - target: ix://agent-ix/spec-artifacts-app/TC-021
    type: verifies
  - target: ix://agent-ix/spec-artifacts-app/TC-022
    type: verifies
  - target: ix://agent-ix/spec-artifacts-app/TC-023
    type: verifies
  - target: ix://agent-ix/spec-artifacts-app/TC-025
    type: verifies
---
# Task-005: FR-004 — mappings.yaml, its schema, and the reference mapping oracle

## Scope

The mapping declaration the module ships, the schema it validates against, and the
Python reference mapping the suite uses as the record oracle. The oracle is test
support, not module code: the module ships data only.

## Subtasks

- [x] **`mappings.schema.json`.** The six kinds, the per-property shape, the `prose_only` + `reason` pair, the `alternate_form` object, and the `imported_types` map.
- [x] **`scripts/build_mappings.py`.** Derive `mappings.yaml` from `manifest.yaml`, so a column list, a locator name, or an id pattern is written once and cannot drift. `--check` writes nothing and fails on drift.
- [x] **One entry per property.** `fields` is one `typed-table` entry carrying a `sysml-fence` `alternate_form` — never two entries, which is what would make "exactly once" unsatisfiable for the one property that has two authored forms.
- [x] **Round-trip policy.** `authority: markdown` and `round_trip: derived` per model; `lossless: true` on `section` and `ocl-clause`, `false` on the rest; the dropped frontmatter key set declared per model.
- [x] **The reference mapping.** Builds a record from a document: frontmatter identity, byte-exact sections with line spans, typed rows with per-cell parses, `FieldDecl` rows, `ClauseRef` clauses with `invariantsText` beside them, and provenance.
- [x] **Failure discipline.** Every failure in one document reported together, none first-only, and no partial record when any failure is found.
- [x] **Read-only.** No file in the module or its test support writes a Markdown document; the oracle opens every document read-only, and the check enumerates the tree rather than sampling it.

## Deliverables

- `spec_artifacts_app/mappings.yaml`, `spec_artifacts_app/mappings.schema.json`
- `scripts/build_mappings.py`
- `tests/support/reference_mapping.py`
- Tests for TC-019, TC-020, TC-021, TC-022, TC-023, TC-025

## Notes

- FR-004-CON-3 is checked by enumeration, not by sampling: a single unenumerated
  writer is exactly the file that would make the round-trip policy a lie.
- The `sourceSpan` rule matches the engine rather than diverging from it: the
  identity defaults to `ix://local/scope/spec` with an advisory when the caller
  supplies none, because semantic-core `SourceLocus` cannot carry an absent one.
