---
id: Task-010
title: "Gate — both artifact types end to end"
type: Task
status: pending
track: gate
priority: P0
relationships:
  - target: ix://agent-ix/spec-artifacts-app/FR-002
    type: references
  - target: ix://agent-ix/spec-artifacts-app/FR-003
    type: references
  - target: ix://agent-ix/spec-artifacts-app/FR-004
    type: references
  - target: ix://agent-ix/spec-artifacts-app/FR-005
    type: references
---
# Gate Task-010: both artifact types end to end

## Scope

The gate that decides whether the contract holds, run on both declared artifact
types rather than on a convenient one. It mints no test case of its own; it is the
condition under which the others are believed.

## Subtasks

- [ ] **Skeleton to record to schema.** For `ApplicationSpec` and `MasterRequirements`: the shipped skeleton validates under `validate_document`, extracts under `extract_semantic` with zero error diagnostics, maps to a record under the reference mapping, and that record validates against the emitted schema the manifest binds by digest.
- [ ] **Both `## Properties` forms.** The typed table and the `sysml` fence yield the same `FieldDecl` list, in the same order.
- [ ] **Every negative fixture refused**, each by the check its `expect` names.
- [ ] **No skipped row.** The gate fails if any semantic row skipped rather than ran.
- [ ] **`make lint` and `make schemas-check` both green** on the committed tree, and `quire validate` structurally clean over `spec/**/*.md` and `plan/**/*.md`.

## Deliverables

- A passing suite with the gate assertions above
- `quire coverage` output recorded in the PR

## Notes

- The gate is deliberately end to end. Each layer of this contract can be green in
  isolation while the composition is broken — a schema that validates nothing a
  mapping produces, a mapping that names properties no model declares — and only
  running the whole path catches that.
