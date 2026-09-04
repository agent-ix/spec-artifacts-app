---
id: SR-001
title: "EARS conformance review of the semantic module contract spec set"
type: SpecReview
analysis: ears-conformance
scope: "spec/stakeholder/StR-001-module-activation.md, spec/functional/FR-001-module-manifest-activates.md, spec/functional/FR-002-semantic-data-schemas.md, spec/functional/FR-003-semantic-manifest-contract.md, spec/functional/FR-004-markdown-mappings-and-imports.md, spec/functional/FR-005-executable-skeletons.md, spec/non-functional/NFR-001-reproducible-additive-projection.md"
review_set: subset
---
# SR-001: EARS conformance review of the semantic module contract spec set

## Summary

This lens read the 122 `shall` obligations carried by the seven
requirement-bearing documents of agent-ix/spec-artifacts-app#3 (StR-001,
FR-001..FR-005, NFR-001); US-001, IT-001, and IT-002 are out of scope for
EARS grammar. The engine check (`quire validate --scope . "spec/**/*.md"
--summary`, quire 0.31.0 / engine 0.46.0) reports 17/19 docs grammar-clean
(89%) with 5 advisories: `ears:missing-subject` and `ears:unclassifiable` on
FR-004 lines 93 and 117, and `ears:vague-response` on StR-001 line 11. The
dominant defect is not the advisory count but statement packing: the
requirement set is otherwise disciplined and pattern-correct, yet a handful of
statements bundle two to four `shall` obligations into one sentence, which is
also what drives both engine findings — the trailing clauses lose the subject
the first clause named and stop matching any EARS pattern.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | medium | FR-004 line 93 (`ears:unclassifiable`, `ears:missing-subject`): the bullet "If one section carries both a typed table and a `sysml` fence, then the mapping SHALL fail naming the section's heading line, because one artifact carries one form" is a correct unwanted-behavior statement whose subject sits on the previous line and whose trailing `because` rationale defeats the pattern match — restate as one line, "If a section carries both a typed table and a `sysml` fence, then the mapping SHALL fail naming the heading line", and move the rationale to Rationale | FR-004 |
| FND-002 | medium | FR-004 line 117 (`ears:unclassifiable`, `ears:missing-subject`): the `provenance` bullet packs four obligations — fill `provenance.path`, fill `provenance.digest`, fill `provenance.sourceIdentity` from the caller, leave it absent and never synthesize one — so the trailing `SHALL NOT synthesize one` names no subject and matches no pattern; split into one ubiquitous statement per field plus an `If the caller supplies no `sourceIdentity`, then …` unwanted statement | FR-004 |
| FND-003 | medium | StR-001 line 11 (`ears:vague-response`): "multi-service applications **shall** be able to express composite specs" uses the unverifiable `be able to`, and the obligated subject is wrong — the need's Validation Criteria measure module activation and generator output, not what applications can do; restate as a concrete response by the module ("The module SHALL declare a composite application spec that aggregates per-service requirements into a master-requirements rollup") | StR-001 |
| FND-004 | medium | NFR-001 Statement chains three distinct obligations under one subject — byte-for-byte reproduction, `$ref` resolution with no network read, and no compatibility-invalidating type change — each with its own Measurement row and its own verification; split into three statements so each maps to one metric | NFR-001 |
| FND-005 | medium | FR-002 Behavior ("Free text and scope", lines 224–228) nests three `shall` in one statement: constrain every property, *or* declare it free text, *in which case* carry `free text:` and a reason; the nested obligation is the one AC-4 actually tests, so state it separately as "If a property is declared free text, then its description SHALL carry `free text:` and the reason" | FR-002 |
| FND-006 | medium | FR-004 lines 84–88 packs the verification-cell parse into three `shall` under two different triggers (cell with parentheses, cell without) plus a standalone "SHALL drop no byte of the cell"; split into two `If … then …` statements and one ubiquitous statement so each maps to an atomic criterion | FR-004 |
| FND-007 | medium | FR-004 lines 121–123 leads with the non-canonical trigger "Where a cell is mapped to an `ImportedTypeRef`" and then packs three `shall` across two different subjects (the author writes the cell, the mapping splits it, the mapping copies nothing); the author obligation is an authoring convention, not module behavior — separate the subjects and use a ubiquitous or `While …` form | FR-004 |
| FND-008 | medium | FR-005 Behavior "One artifact SHALL carry one form; the alternate is a separate file, never a second block in the same artifact" names an artifact rather than a system or actor as the obligated subject, so nothing in the statement says what refuses a violation; restate against the checking subject, e.g. "If a skeleton carries both a typed `## Properties` table and a `sysml` fence, then the suite SHALL fail naming the file" (the same rule FR-004 line 93 states for the mapping) | FR-005 |
| FND-009 | medium | FR-001 Description carries one `shall` but two independently verifiable responses — conforming to FR-035 v1.0.0 and activating idempotently — which is why AC-1 tests the first and AC-2/AC-3 the second; split into two atomic requirement statements | FR-001 |
| FND-010 | medium | FR-003 Behavior section "Evidence, not obligation" (lines 110–123) carries three declarative paragraphs with no `shall` inside a normative Behavior section; the engine cannot flag a statement with no modal, but non-normative narrative in Behavior reads as requirement text — move it to Rationale and leave Behavior obligations only | FR-003 |
| FND-011 | medium | FR-005 Description second paragraph packs the default form, the alternate `sysml` form, the separate-file rule, and the `ocl` clause form under one `shall`; each is separately verified (AC-1, AC-2, AC-3), so state each as its own requirement | FR-005 |
| FND-012 | low | FR-003 Behavior line 88 states four disjunct triggers (unadmitted `semantic` key, mixed `data_schema`, malformed `package`, unregistered `targets` value) under a single `If … then …`; the pattern is correct EARS but the disjunction is what forces AC-6 to pack four assertions into one criterion — consider one statement per refused form | FR-003 |
| FND-013 | low | FR-004 line 105 "If a `## Invariants` section carries no fenced block, then the mapping SHALL leave `invariants` absent and SHALL NOT fail" is a non-singular unwanted statement; the second clause is the absence of a response and is better stated as the requirement that the mapping succeed | FR-004 |
| FND-014 | low | FR-005 Behavior "The skeleton set and the locator set SHALL agree in both directions" leads with a near-vague verb (`agree`) and is rescued only by the enumerated conjuncts that follow; lead with the concrete response ("Every asserted heading SHALL exist in the skeleton at the asserted level, …") | FR-005 |
| FND-015 | low | FR-002-CON-1 states two obligations in one constraint ("no field without a Markdown source, no locator output without a field"), each verified by a different test case (TC-001, TC-002); split so each constraint id binds to one test | FR-002 |
| FND-016 | low | FR-005 Description carries the typo "with a a `sysml`-tagged fence"; editorial, but it sits inside a requirement statement | FR-005 |
