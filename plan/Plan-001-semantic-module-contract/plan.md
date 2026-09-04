---
id: Plan-001
title: "spec-artifacts-app — semantic module contract (issue #3)"
type: Plan
status: active
relationships:
  - target: ix://agent-ix/spec-artifacts-app/StR-001
    type: references
  - target: ix://agent-ix/spec-artifacts-app/US-001
    type: references
  - target: ix://agent-ix/spec-artifacts-app/FR-001
    type: references
  - target: ix://agent-ix/spec-artifacts-app/FR-002
    type: references
  - target: ix://agent-ix/spec-artifacts-app/FR-003
    type: references
  - target: ix://agent-ix/spec-artifacts-app/FR-004
    type: references
  - target: ix://agent-ix/spec-artifacts-app/FR-005
    type: references
  - target: ix://agent-ix/spec-artifacts-app/NFR-001
    type: references
  - target: ix://agent-ix/spec-artifacts-app/IT-002
    type: references
---
# Implementation Plan: semantic module contract

## Requirements Summary

### Stakeholder Requirements
- [ ] **StR-001**: Application composite specs are registered, validated, and served, and a consumer reads one as a typed record bound to the exact shipped schema bytes (VC-1..VC-3).

### User Stories
- [ ] **US-001**: Consume application composite specs as typed semantic records, with imported types referenced rather than duplicated.

### Functional Requirements
- [ ] **FR-001**: The manifest conforms to filament-core-service FR-035 and activates idempotently.
- [ ] **FR-002**: One semantic data model per declared artifact type, authored in TypeSpec against `@agent-ix/semantic-core` 0.1.0 and projected to a sealed JSON Schema 2020-12 bundle with a recorded toolchain and a byte-drift gate.
- [ ] **FR-003**: The manifest carries the quoin FR-070 `semantic` block, a reference-form `data_schema` per exported artifact type, and a declared import set whose missing, over-declared, self-referential, and cyclic cases each have their own diagnostic.
- [ ] **FR-004**: Every property of every model has exactly one Markdown mapping entry; every structured section is typed or explicitly prose-only; Markdown is the authority and the record is derived.
- [ ] **FR-005**: Each artifact type ships a skeleton that is an executable fixture in the quoin FR-071/FR-072 forms, with a `sysml` alternate and eight negative counterparts.

### Non-Functional Requirements
- [ ] **NFR-001**: The projection is reproducible byte-for-byte, resolves offline, and adds no required locator.

### Integration Test Requirements
- [ ] **IT-002**: Module load, `validate_document`, and `extract_semantic` against the Quire engine, with the digest-refusal row a strict expected failure.

## Dependency Graph

### Core dependency edges

- `FR-005 (skeletons + locators) -> FR-002 (models)`
  Reason: the models are the typed form of what the locators extract. Nothing to
  type exists until the Markdown forms and their asserts do.
- `FR-002 (toolchain half) -> FR-002 (models)`
  Reason: a model cannot be authored until `tsp compile` runs against
  `@agent-ix/semantic-core` 0.1.0 and the generator normalizes what it emits. The
  requirement is split across Task-001 (enablement) and Task-003 (the models and
  the emitted set) for this reason; it is one requirement with two landing points,
  not a cycle.
- `FR-002 (emitted set) + FR-001 -> FR-003 (block + digests)`
  Reason: the manifest references the emitted files by path and digest, and the
  0.2.0 manifest must still be an FR-035-valid manifest.
- `FR-002 + FR-003 + FR-005 -> FR-004`
  Reason: a mapping entry names a model property, a locator, and — for an
  imported-type cell — a package the manifest pins.
- `FR-003 (block) -> FR-003 (imports)`
  Reason: the import diagnostics read `semantic.imports`, which the block half
  introduces.
- `FR-002 + FR-003 + FR-004 + FR-005 -> IT-002`
  Reason: the engine boundary exercises all four at once.

The four functional requirements form the chain
`FR-005 -> FR-002 -> FR-003 -> FR-004`. The apparent cycles the dependency review
found in the prose were removed from the requirements themselves; no task ordering
compensates for one.

### Enablement that is nobody's requirement

- **E-1** `make dev-quire` provisioning `quire >= 0.46.0` from `pypi.ix`, because
  no index a repository may commit against carries it
  (agent-ix/quire-rs#392). Owned by Task-008.
- **E-2** The vendored FR-035 schema copy and the recorded upstream digest that
  makes a silent divergence a failing test. Owned by Task-004.
- **E-3** The `@agent-ix` scope routing precondition: the repository carries no
  `.npmrc`, so `npm ci` works only on a machine whose npm config routes the scope
  (agent-ix/filament-core-data#11). Owned by Task-001, recorded in NFR-001 Scope.

## Execution Tracks

- **Track A (critical path)**: Task-001 → Task-002 → Task-003 → Task-004.
- **Track B (parallel once Track A reaches Task-004)**: Task-005, Task-006, Task-007.
- **Track C (post-critical-path)**: Task-008, Task-009.
- **Gate**: Task-010.

## Quality Gates

- **Gate 1 (after Task-001)**: `make schemas` and `make schemas-check` both run,
  and `make schemas-check` exits non-zero after a one-byte edit. A generator whose
  drift gate does not fire is worse than none.
- **Gate 2 (after Task-004)**: the manifest validates under the bundled FR-035
  schema with the block present, and the legacy-manifest fixture validates under
  the same schema.
- **Gate 3 (Task-010)**: both artifact types end-to-end — skeleton, then
  `validate_document`, then `extract_semantic`, then the reference mapping's
  record, then that record against its emitted schema — with zero engine
  diagnostics and no skipped row.

## Test Plan

Every TC id of `spec/tests.md` is owned by exactly one task. The table below is the
allocation; the criteria each TC discharges are in `spec/tests.md` and are not
restated here.

| Task | Test cases |
|------|------------|
| Task-001 | TC-004, TC-006, TC-008, TC-030, TC-033 |
| Task-002 | TC-018, TC-027, TC-028, TC-029, TC-032 |
| Task-003 | TC-001, TC-002, TC-003, TC-005, TC-007, TC-009, TC-010 |
| Task-004 | TC-011, TC-012, TC-016 |
| Task-005 | TC-019, TC-020, TC-021, TC-022, TC-023, TC-025 |
| Task-006 | TC-014, TC-015, TC-024 |
| Task-007 | TC-026, TC-035 |
| Task-008 | TC-013, TC-017, TC-034 |
| Task-009 | TC-031, TC-036 |
| Task-010 | (gate; mints no TC of its own) |

## Out of Plan

The plan implements no workaround for an upstream defect. Each of these is carried
as an out-of-scope entry or an expected failure naming its owner, exactly as
`spec/spec.md` records it: agent-ix/quire-rs#392, #221, #394, #391;
agent-ix/quoin#336, #338, #339; agent-ix/filament-core-service#23;
agent-ix/filament-core-data#11, #21, #22, #23; agent-ix/quoin#290, #291.
