---
id: Task-004
title: "FR-003 — Manifest 0.2.0, the semantic block and reference-form data_schema"
type: Task
status: done
track: A
priority: P0
relationships:
  - target: ix://agent-ix/spec-artifacts-app/FR-003
    type: references
  - target: ix://agent-ix/spec-artifacts-app/TC-011
    type: verifies
  - target: ix://agent-ix/spec-artifacts-app/TC-012
    type: verifies
  - target: ix://agent-ix/spec-artifacts-app/TC-016
    type: verifies
---
# Task-004: FR-003 — Manifest 0.2.0, the semantic block and reference-form data_schema

## Scope

The manifest half of the contract: the `semantic` block, the digest-bound
`data_schema` references, the version bump, and the compatibility fixture that
proves the addition breaks nobody.

## Subtasks

- [x] **Bump `version` to 0.2.0** as the first step, so `make schemas` and the digests are computed once against one version.
- [x] **Add the `semantic` block** with exactly the nine admitted keys. `sweep_report` is absent because `legacy_forms` is `warning`: this module's own documents author no legacy form, so `warning` is the value that changes nothing.
- [x] **Add one reference-form `data_schema`** per exported artifact type. No inline `data_schema` on any type.
- [x] **Vendor the FR-035 schema** at `tests/fixtures/module-manifest.schema.json`, byte-for-byte from the revision quoin ships, and record its SHA-256 so a silent divergence from upstream is a failing test.
- [x] **Build the legacy-manifest fixture** — this manifest with the block and every `data_schema` removed — and prove it validates under the same schema.
- [x] **Fold the digest refresh into `make schemas`,** so the suite never hand-computes a digest.

## Deliverables

- `spec_artifacts_app/manifest.yaml` at 0.2.0
- `tests/fixtures/module-manifest.schema.json`, `tests/fixtures/manifest-legacy.yaml`
- Tests for TC-011, TC-012, TC-016

## Notes

- FR-003-CON-1: the block adds no required key anywhere, which is what makes the
  legacy fixture a real gate rather than a formality.
- Once quoin's FR-070 reader ships, `quoin module install` will refuse this
  module, because it resolves `semantic.exports` against `object_types` only
  (agent-ix/quoin#336). The manifest keeps its exports as specified rather than
  bend to a gap that is quoin's to close; `spec/spec.md` records it out of scope.
- Unblocks: Task-005, Task-006, Gate 2.
