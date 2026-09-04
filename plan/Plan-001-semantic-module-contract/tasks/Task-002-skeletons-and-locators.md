---
id: Task-002
title: "FR-005 — Skeletons, the sysml alternate, and the added locators"
type: Task
status: done
track: A
priority: P0
relationships:
  - target: ix://agent-ix/spec-artifacts-app/FR-005
    type: references
  - target: ix://agent-ix/spec-artifacts-app/NFR-001
    type: references
  - target: ix://agent-ix/spec-artifacts-app/TC-018
    type: verifies
  - target: ix://agent-ix/spec-artifacts-app/TC-027
    type: verifies
  - target: ix://agent-ix/spec-artifacts-app/TC-028
    type: verifies
  - target: ix://agent-ix/spec-artifacts-app/TC-029
    type: verifies
  - target: ix://agent-ix/spec-artifacts-app/TC-032
    type: verifies
---
# Task-002: FR-005 — Skeletons, the sysml alternate, and the added locators

## Scope

The Markdown forms this module publishes and the `body_extraction` asserts that
enforce them. This is the head of the chain: the models type what these locators
extract, so nothing downstream can be authored first.

## Subtasks

- [x] **Author `skeletons/application-spec.md`.** Frontmatter satisfying the shipped frontmatter schema; the H1 and `## Purpose` as the only required sections; `## Scope`, `## System Overview`, `## Structure`, `## Requirements Architecture`, `## References`, `## Properties`, `## Boundaries`, `## Capabilities`, `## Actors`, `## Interfaces`, `## Data Dependencies`, `## UI Rendering Requirements`, `## Requirements`, `## Invariants`.
- [x] **Author `skeletons/master-requirements.md`.** The same identity and section core, minus the six sections that describe a running system — a master-requirements document is the front page of a specification, not a description of one.
- [x] **Author `skeletons/application-spec.sysml.md`.** The same field set in the same order, as one `sysml` fence under `## Properties`. One artifact carries one form; the alternate is a separate file.
- [x] **Write the constraints cells in the closed vocabulary.** `identity`, `nonEmpty`, `minLength: n`, `maxLength: n`, `min: n`, and `pattern: /…/` — the slash-delimited form the engine's closed keyword set actually admits. A cell outside it is a `semantic.unknown-constraint-keyword` error, not a style preference.
- [x] **Add the locators.** Every one this change introduces is `required: false` except `title` and `purpose`, which the pre-change document already carries.
- [x] **Fix the id-pattern defect the review found.** `defaults.id_pattern` generated `ApplicationSpec-001`, which the shipped frontmatter schema rejects (`^[A-Z]{2,4}-[0-9]+$`); it becomes `AS-{next:03d}` and `MR-{next:03d}`.
- [x] **Commit the pre-change baseline.** `spec/spec.md` as it stood at the branch point, so "existing valid application specs remain readable" is measured rather than asserted.

## Deliverables

- `spec_artifacts_app/skeletons/*.md` (three files)
- `spec_artifacts_app/manifest.yaml` `body_extraction` on both artifact types
- `tests/fixtures/baseline/spec.md`
- Tests for TC-018, TC-027, TC-028, TC-029, TC-032

## Notes

- FR-005-CON-1 is the whole point of the optionality: a module that already has
  documents in the corpus can only adopt the contract additively.
- The skeleton/assert parity check runs in both directions. A skeleton heading
  that no locator asserts and no mapping declares prose-only is a gap, not a
  freedom.
- Unblocks: Task-003 (what the models type), Task-005 (what the mappings read).
