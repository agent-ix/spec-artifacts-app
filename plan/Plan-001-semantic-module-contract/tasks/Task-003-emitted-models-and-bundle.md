---
id: Task-003
title: "FR-002 — The exported models, the support models, and the emitted bundle"
type: Task
status: done
track: A
priority: P0
relationships:
  - target: ix://agent-ix/spec-artifacts-app/FR-002
    type: references
  - target: ix://agent-ix/spec-artifacts-app/TC-001
    type: verifies
  - target: ix://agent-ix/spec-artifacts-app/TC-002
    type: verifies
  - target: ix://agent-ix/spec-artifacts-app/TC-003
    type: verifies
  - target: ix://agent-ix/spec-artifacts-app/TC-005
    type: verifies
  - target: ix://agent-ix/spec-artifacts-app/TC-007
    type: verifies
  - target: ix://agent-ix/spec-artifacts-app/TC-009
    type: verifies
  - target: ix://agent-ix/spec-artifacts-app/TC-010
    type: verifies
---
# Task-003: FR-002 — The exported models, the support models, and the emitted bundle

## Scope

The models themselves: one per declared artifact type, plus every support model
and scalar they reach, and the emitted bundle with its recorded toolchain.

## Subtasks

- [x] **`ApplicationSpec` and `MasterRequirements`.** Identity, status, relationships, provenance, the section properties, `fields`, `requirements`, `invariants`; and on `ApplicationSpec` only, `boundaries`, `capabilities`, `actors`, `interfaces`, `dataDependencies`, `renderingRequirements`.
- [x] **The support models.** `Section`, `Provenance`, `Relationship`, `Verification`, `ImportedTypeRef`, `Boundary`, `Capability`, `Actor`, `Interface`, `DataDependency`, `RenderingRequirement`, `RequirementRef`.
- [x] **The scalars and enums.** Every one constrained by `pattern`, `minLength`, `minValue`, or an enum; no bare `string`.
- [x] **Reference, never duplicate.** An imported type is reached through `ImportedTypeRef { module, type }` and an id. No property restates a field an imported type declares, and no `$ref` names another module's base — a cross-module `$ref` cannot resolve offline from this module's shipped bytes.
- [x] **`fields` and `invariants` by `$ref` to semantic-core.** `FieldDecl` and `ClauseRef` are never redeclared here.
- [x] **Free text is declared, not defaulted.** Nine properties are free text; each says `free text:` and why in its doc comment, and the closed set is enumerated in FR-002 rather than left to whatever the test happens to list.
- [x] **Declaration, not runtime state.** No property named `deployed`, `running`, `health`, `uptime`, `instanceCount`, or `lastDeployedAt`, and `ApplicationSpec`'s description says so.
- [x] **Emit and record.** 39 files plus `toolchain.json`, whose digest is recomputable from the shipped bytes with no toolchain run.

## Deliverables

- `typespec/main.tsp` (complete)
- `spec_artifacts_app/schemas/*.json` (39 emitted files) and `schemas/toolchain.json`
- Tests for TC-001, TC-002, TC-003, TC-005, TC-007, TC-009, TC-010

## Notes

- FR-002-CON-1 runs both ways: no field without a Markdown source, and no locator
  output without a field. A model property nothing fills is as much a defect as a
  locator nothing types.
- Sealing (`unevaluatedProperties`) is what makes the negative fixture for an
  undeclared property fail rather than pass quietly.
- Unblocks: Task-004 (the files the manifest references by digest).
