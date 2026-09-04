---
id: SR-001
title: "Base review of the issue #3 semantic-module contract specification"
type: SpecReview
analysis: base
scope: "spec/spec.md, spec/stakeholder/StR-001, spec/usecase/US-001, spec/functional/FR-001..FR-005, spec/non-functional/NFR-001, spec/integration/IT-001..IT-002, spec/tests.md"
review_set: base
---
# Base review of the issue #3 semantic-module contract specification

## Summary

Checklist review (id formats, story and requirement quality, the six coverage
rules, cross-references) of the specification authored on branch
`spec/3-semantic-module-contract` for `agent-ix/spec-artifacts-app#3`, measured
against the house standard set by `spec-objects-business#4` and
`spec-artifacts-iso#34`. Ids are well-formed, unique and sequential per class
(StR-001, US-001, FR-001..FR-005, NFR-001, IT-001..IT-002, TM-001,
TC-001..TC-036); every FR links US-001; every AC, CON and NFR metric row has a
matrix row and a test case, and every `Verification` cell of every FR agrees
with the matrix row that carries it. `quire validate --scope . "spec/**/*.md"`
reports zero structural errors and five grammar warnings.

Two contradictions between requirements would block implementation as written
(FND-001, FND-002): the typed `## Properties` form FR-005 makes mandatory has no
model property, no locator and no mapping kind, and the locator and clause
obligations FR-005 places on *both* artifact types contradict the model FR-002
gives `MasterRequirements`. Seven mediums and eight lows follow. All findings are
reported only; no spec artifact was edited by this review.

## Verdict

**CHANGES REQUIRED** — two high findings are internal contradictions between
FR-002, FR-004 and FR-005 that a plan cannot resolve by choosing; they need an
authoring decision before `spec-to-plan`.

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-001 | high | FR-005 requires each skeleton to author its typed declarations in the `Field / Type / Multiplicity / Constraints` table and FR-005-AC-2 asserts the `sysml` skeleton declares "the same field set as the typed `## Properties` table", but no FR-002 model declares a properties or fields array, FR-005 Outputs adds no `properties` locator (the added set is title, purpose, scope, systemOverview, structure, boundaries, capabilities, actors, interfaces, dataDependencies, renderingRequirements, requirements, invariants), and FR-004 declares no mapping entry for that section. FR-004-AC-2 then fails on the shipped skeleton, since `## Properties` is named by no mapping entry and carries no `prose_only`. Either drop the `## Properties` form from FR-005 or add the model property, the locator and the mapping entry. | FR-005 Description and Behavior, FR-005-AC-2, FR-002 Behavior, FR-004-AC-2, FR-005 Outputs | wrong-requirement |
| FND-002 | high | FR-005 applies one locator set to both artifact types and requires *each* skeleton to carry a `### clauseId` heading under `## Invariants` (FR-005-AC-3: "the record built from it carries one ClauseRef per heading"), but FR-002 gives `invariants?`, `boundaries`, `capabilities`, `actors`, `interfaces`, `dataDependencies` and `renderingRequirements` to `ApplicationSpec` only — `MasterRequirements` gets identity, provenance, relationships, status and `requirements`. As written FR-005-AC-3 is unsatisfiable for the `master-requirements` skeleton, and the shared locator set breaks FR-002-CON-1 in both directions (locator outputs with no field). | FR-005 Outputs and Behavior, FR-005-AC-3, FR-002 Behavior, FR-002-CON-1 | wrong-requirement |
| FND-003 | medium | FR-004-AC-3 enumerates the six domain tables it verifies (Capabilities, Actors, Interfaces, Data Dependencies, UI Rendering Requirements, Requirements) and omits `## Boundaries`, which FR-002 models as `boundaries: Boundary[]` and FR-005 lists among the domain tables. TC-023 repeats "the six domain tables", so no criterion and no test case covers the Boundary row mapping or the closed `BoundaryKind` set. | FR-004-AC-3, FR-002 Behavior, FR-005 Behavior, tests.md TC-023 | missing-requirement |
| FND-004 | medium | FR-002 Outputs makes `HeadingRef`, `ComponentType` and `TagName` mandatory emitted files, and FR-002-AC-2 requires the emitted set to equal `toolchain.json` exactly, but no property of any model in FR-002 Behavior references them. They are either dead outputs the AC forces to be shipped, or three model properties that were dropped from Behavior. | FR-002 Outputs, FR-002-AC-2, FR-002 Behavior | wrong-requirement |
| FND-005 | medium | `quire coverage` reports `section-matches-nothing` for NFR-001: the `nfr-acceptance-criterion` declaration mints trace targets from `## Acceptance Criteria` only, and NFR-001 has Statement, Scope, Rationale, Measurement and Evaluation, Verification, Dependencies. The four metrics mint nothing and TC-030..TC-033 trace to `NFR-001 (metric n)`, which binds to no target. The model repo fixed this by adding NFR-001-AC-1..4, one per metric. | NFR-001, tests.md TC-030..TC-033 | correct-requirement-no-evidence |
| FND-006 | medium | FR-001's Verification cells read `Schema Test` (1 row) and `Integration Test` (3 rows), which `quire coverage` reports as `uncatalogued-verification-method` — neither a catalog id nor a declared class. `Test` is the declared form. Pre-existing wording, unchanged by this branch, but the matrix now depends on those rows. | FR-001-AC-1..AC-4 | wrong-requirement |
| FND-007 | medium | StR-001-VC-2 validates that "agent CLI generators (minijinja-cli) can produce valid artifacts using the templates and schemas this Module ships", but FR-005-CON-3 and spec.md Out of Scope state the module ships no `*.md.j2` and no `template_ref`, template rendering having been removed ecosystem-wide. The stakeholder criterion validates against an artifact class this specification forbids; its matrix row is `🚧` and never runs, so the contradiction is not caught by the suite. | StR-001-VC-2, FR-005-CON-3, spec.md Out of Scope | wrong-requirement |
| FND-008 | medium | Issue #3 deliverable 3 asks for "generated-language, dynamic-module, and compatibility fixtures". Generated-language fixtures are deferred in spec.md Out of Scope with named issues, and the compatibility fixture is `tests/fixtures/manifest-legacy.yaml` (FR-003 Outputs, FR-003-AC-7). The word "dynamic-module" appears in no artifact — not in scope, not out of scope, no FR, no fixture. The deliverable is silently unaddressed rather than deferred. | gh issue 3 Deliverables, spec.md Out of Scope, FR-003 Outputs | missing-requirement |
| FND-009 | medium | `quire coverage` reports 0/76 rows backed and `no-symbol-bound`: the one existing test, `test_pack_exposes_manifest_path` at tests/test_manifest.py:16, carries no tag any declared form matches, so even FR-001-AC-1 / TC-036 (marked `✅ Complete`) has no binding symbol. 30 matrix rows read `✅ Complete` on a branch that adds no test. The Overview says the column counts criteria, not tests, but a reader and `quire coverage` disagree about what `✅` asserts. Recorded so gap analysis reads the green as "criterion has a TC assigned", not "criterion is backed". | tests.md, tests/test_manifest.py | correct-requirement-no-evidence |
| FND-010 | low | The four `Method` cells of the NFR-001 Measurement table carry prose commands, each reported by `quire coverage` as `uncatalogued-verification-method`. The matrix rows already carry the catalogued classes (Snapshot, Manual, Static, Benchmark), so the class is recorded twice in two vocabularies and only one is catalogued. | NFR-001 Measurement and Evaluation | correct-requirement-no-evidence |
| FND-011 | low | tests.md says "Nine rows are marked `🚧`"; the traceability tables carry ten (FR-001-AC-2..4, FR-003-AC-8, NFR-001 metric 2, StR-001-VC-1, StR-001-VC-2, IT-001-AC-1, IT-001-AC-2, IT-002-AC-2), because the prose groups FR-003-AC-8 and IT-002-AC-2 into one bullet while the tables carry a row each. | tests.md Overview | wrong-requirement |
| FND-012 | low | FR-004-CON-3's Validation cell reads `Inspection (TC-020)` while TC-020's Type in the Test Case Summary is `Static`. Every other CON in the specification uses `Test`, and the two vocabularies disagree on one row. | FR-004-CON-3, tests.md TC-020 | wrong-requirement |
| FND-013 | low | Five EARS grammar warnings, none structural: FR-004 lines 93 and 117 (`ears:unclassifiable` and `ears:missing-subject` — bullets whose subject sits on the previous physical line) and StR-001 line 11 (`ears:vague-response`, "shall be able to"). The FR-004 pair is a line-wrapping artefact; the StR-001 one is a real vague response verb. | FR-004, StR-001 | wrong-requirement |
| FND-014 | low | `quire coverage` reports `status-column-matches-nothing`: the `functional-coverage` declaration expects a `Status` column and the table header is `Coverage Status`, so complete-but-unbacked classification is skipped. The header matches `spec-objects-business` and `spec-artifacts-iso` exactly, so this is an ecosystem declaration mismatch, not this branch's defect. No change here. | tests.md, quoin declaration `functional-coverage` | wrong-requirement |
| FND-015 | low | US-001 carries illustrative examples (US-001-EX-1..3) rather than Given/When/Then acceptance criteria, so the checklist item "at least 2 acceptance criteria" is met by the examples plus the FR criteria they lead to. This follows the `spec-artifacts-iso` and `spec-objects-business` US skeleton, which keeps verification out of stories. No change. | US-001 | correct-requirement-no-evidence |
| FND-016 | low | IT-001's acceptance criteria cover steps 2-4 only ("All assertions in test-procedure steps 2-4 pass"); IT-001-SC-01, the clean-service and empty-`modules`-table precondition, is asserted by no AC. Pre-existing, and both IT-001 rows are `🚧` in this repository. | IT-001-AC-1, IT-001 Test Procedure | missing-requirement |
| FND-017 | low | `quire validate` reports `DuplicateArchetype` for `MasterRequirements`, `ApplicationSpec` and `Application Spec`; the `MasterRequirements` overlap with `spec-artifacts-iso` is deferred to agent-ix/quoin#345 in spec.md Out of Scope, and the `ApplicationSpec` / `Application Spec` pair is one module installed at two paths (`DuplicateModuleName`), not a spec defect. Recorded so gap analysis does not read either as this ticket's debt. | spec.md Out of Scope, quire validate output | wrong-requirement |
| FND-018 | low | FR-005 Description repeats the article across a line break: "with a / a `sysml`-tagged fence". Typo only. | FR-005 Description | wrong-requirement |

## Coverage Rules

1. **Coverage** — every criterion has at least one test case: FR-001 4 AC; FR-002 11 AC and 5 CON; FR-003 8 AC and 3 CON; FR-004 8 AC and 3 CON; FR-005 7 AC and 3 CON; NFR-001 4 metrics; StR-001 2 VC; IT-001 2 AC; IT-002 3 AC. Every one carries a matrix row. Nine rows carry a test case of `—` and a `🚧` reason (see FND-011 for the count); the rest name a TC. The gap is not a missing row but a missing *criterion*: Boundary mapping (FND-003).
2. **Option permutation** — the two authoring forms (typed table and `sysml` fence) are permuted by TC-029 and the both-forms refusal by TC-025; the two `data_schema` forms (reference and absent) by TC-011 and TC-034; `sourceSpan` present and absent by TC-019. No FR carries an `## Options` section; the design choice (TypeSpec over hand-authored schema) sits in US-001 Options, matching the model repos.
3. **Constraint boundary** — digest one-hex-digit edit (TC-017), one-byte schema edit (TC-008, TC-012), two-module and three-module cycles (TC-015), self-import (TC-014), zero fences and two fences under one heading (TC-019), required-versus-optional locator set (TC-018, TC-032).
4. **Error path** — unknown `semantic` key, ambiguous `data_schema`, non-`org/repo` package, unregistered target (TC-016); undeclared import module and type (TC-014, TC-024); five malformed clause forms (TC-019); five malformed document forms (TC-025); every negative fixture by its own `expect` (TC-026, TC-035). Two engine-side error paths are honestly carried as strict expected failures naming agent-ix/quire-rs#394 and #221 rather than skipped.
5. **State transition** — not applicable; the module contributes data, and the only transition (activation then re-activation idempotency) is IT-001-SC-04, `🚧` for want of a running service.
6. **Edge case** — legacy manifest with no `semantic` block (TC-011, TC-034), the pre-change `spec/spec.md` (TC-018), a `## Invariants` section with prose and no fence (TC-019), a fence owned by no heading (TC-019, TC-026).

## Checklist Notes

- **ID format and uniqueness** — pass. `US-001`, `FR-001..FR-005`, `NFR-001`, `IT-001..IT-002`, `StR-001`, `TC-001..TC-036` are all three-digit, sequential and duplicate-free; child ids use `{PARENT}-AC-N`, `{PARENT}-CON-N`, `{PARENT}-VC-N`, `{PARENT}-SC-NN` and `{PARENT}-EX-N` consistently.
- **User story quality** — pass with FND-015. As-a / I-want / So-that present, options and constraints carry rationale, dependencies and priority stated, framed on consumer value rather than implementation.
- **Functional requirement quality** — pass except FND-001..FND-004. Every FR carries Description, Inputs, Outputs, Behavior, Constraints, Acceptance Criteria and Dependencies; error conditions are written as `If … then … SHALL fail naming …` throughout; performance targets sit in NFR-001 with numeric targets and thresholds.
- **Cross-referencing** — pass. Every FR relationship target is a full `ix://` identity; internal links are relative Markdown per ADR-0007; every `Verification` cell agrees with its matrix row; terminology (`data_schema`, `ImportedTypeRef`, `semantic` block, reference form) is used consistently across all ten artifacts.
- **Ticket acceptance criteria** — issue #3's four ACs are each covered: imported types by reference (FR-002-AC-10, FR-004-AC-4), typed mapping or explicit prose-only per section (FR-004-AC-2), existing specs remain readable (FR-004-AC-8, FR-005-AC-5, FR-005-CON-1), cycles and missing imports fail clearly (FR-003-AC-4, FR-003-AC-5). Deliverable 3 is partly unaddressed (FND-008).
