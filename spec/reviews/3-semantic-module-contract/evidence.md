---
id: SR-006
title: "Verification and evidence review of the #3 semantic-module contract spec set"
type: SpecReview
analysis: evidence
scope: "spec/spec.md, spec/stakeholder/StR-001-module-activation.md, spec/usecase/US-001-consume-application-artifacts-as-records.md, spec/functional/FR-001-module-manifest-activates.md, spec/functional/FR-002-semantic-data-schemas.md, spec/functional/FR-003-semantic-manifest-contract.md, spec/functional/FR-004-markdown-mappings-and-imports.md, spec/functional/FR-005-executable-skeletons.md, spec/non-functional/NFR-001-reproducible-additive-projection.md, spec/integration/IT-001-manifest-activation-roundtrip.md, spec/integration/IT-002-module-load-and-extraction-roundtrip.md, spec/tests.md"
review_set: all
---
# SR-006: Verification and evidence review of the #3 semantic-module contract spec set

## Summary

One lens only: the method each obligation declares, whether the catalog agrees,
and whether the evidence the Test Matrix names can produce it. The deterministic
half is `quoin advise` over the 46 obligations `quire coverage` mints from this
spec set, plus `quoin catalog methods --json`, which is where the class-to-
evidence-kind relation lives. Nothing here was recalled from memory.

The set is in unusually good shape on the axis the advisor measures: **0 of 46
obligations are inconclusive**, 5 are flagged `mismatch` and 4 `uncatalogued`,
and the four `uncatalogued` are the NFR-001 Measurement `Method` cells that
carry prose commands, which `base.md` FND-010 already carries. Of the five
mismatches, four are recommendations the rules could not have got right — the
applicability rules read the statement's shape and cannot see that an obligation
needs a cluster or a disabled network namespace — and are confirmed as authored
below.

What the lens does find is a different thing from a mismatch. `tests.md`
deliberately declares two vocabularies, the ISO 29148 *method* in a
`Verification` cell and the *Type* of the Test Case Summary, and says a row where
the two disagree is not a defect while a row whose `Type` cannot possibly
discharge the method is. That is the right rule, and the catalog is the thing
that decides it: every catalogued method carries an `evidenceKind`, and the
`Type` vocabulary of the Test Case Summary (`Unit`, `Static`, `Snapshot`,
`Integration`, `Benchmark`, `Manual`) *is* the evidence-kind vocabulary. Read
against it, five test cases pair a class with an evidence kind the catalog does
not join, and the Overview's own worked example — "an obligation verified by
`Inspection` is discharged by a `Static` test" — is one of them (FND-600).

The honesty of the rows that cannot run here is mostly good and is confirmed
row by row below. Three exceptions: `StR-001-VC-3` has a declared method and no
matrix row at all (FND-601); `StR-001-VC-1` declares `Inspection` for evidence
that is an activation against a live service (FND-602); and `StR-001-VC-2` is
marked un-runnable on a stale `minijinja-cli` rationale for a criterion that
`TC-028` already discharges in this package (FND-603). The six cluster-blocked
rows are honestly `🚧` but carry `—` where the one other manual gate carries a
`TC-` id, so nothing can ever bind evidence to them (FND-604).

Ten findings: five medium, five low, no high. No spec artifact was edited by
this review.

## Verdict

**CHANGES REQUIRED** — nothing in this lens blocks a plan by itself, but
FND-600..FND-604 are matrix and `Verification`-cell edits that must land before
`tests.md` can be read as a coverage claim rather than as a table. FND-605 is a
gate-design defect that survives the fix its own note anticipates.

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|----|----------|---------|------|--------------|
| FND-600 | medium | Five test cases pair an ISO class with an evidence kind the method catalog does not join. `quoin catalog methods --json` gives every catalogued method an `evidenceKind`, and the Test Case Summary `Type` vocabulary is that evidence-kind vocabulary. The `Inspection` class holds exactly one method (`inspection`, `evidenceKind: Manual`), so `Inspection (TC-020)` and `Inspection (TC-032)`, both backed by `Static` test cases, name a class that cannot produce `Static` evidence; and the `Test` class reaches `Static` only through `mutation-testing`, which TC-004, TC-005 and TC-027 are not. All five are one act — enumerate the shipped tree without executing the module — and the catalogued class for it is `Analysis` (`static-quality`, `architecture-conformance`, both `evidenceKind: Static`), which this spec uses nowhere. The Overview blesses `Inspection` → `Static` as a general dispensation; the catalog does not, so the rule that is supposed to decide which disagreements are defects is itself uncatalogued. | tests.md Overview ("Two vocabularies, deliberately"); TC-004, TC-005, TC-020, TC-027, TC-032; FR-002-AC-6, FR-002-AC-11, FR-002-CON-3, FR-002-CON-4; FR-004-CON-3; FR-005-AC-6, FR-005-CON-3; NFR-001-AC-3 | wrong-requirement |
| FND-601 | medium | `StR-001-VC-3` declares a method and has no Test Matrix row. It is the only obligation in the set with a `Validation` cell (`Demonstration`) and no row anywhere in `tests.md`: the Stakeholder and Integration table carries VC-1 and VC-2 only, and the `🚧` preamble enumerates ten rows without it. The demonstration it asks for — a consumer reading an application composite as a typed record bound to the exact shipped schema bytes — is what TC-034 already runs (`extract_semantic` over each skeleton with the reference-form `data_schema` reported verbatim), so the gap is a missing row, not missing evidence. StR-001's closing sentence still reads "demonstrating both outcomes against a filament-core instance" — two outcomes for three criteria, and VC-3 needs no filament-core instance at all. | StR-001 Validation Criteria (VC-3) and its closing sentence; tests.md "Stakeholder and Integration Coverage"; tests.md Overview `🚧` list; TC-034 | correct-requirement-no-evidence |
| FND-602 | medium | `StR-001-VC-1` declares `Inspection` for evidence that is an activation against a live service. The criterion is "Activating this Module against filament-core registers the contents it declares", and its own matrix row is `🚧 Needs a running filament-core-service` — an execution against a deployed dependency, which is the definition of `Demonstration` and is exactly the class FR-001-AC-2 and FR-001-AC-4 give the identical evidence one layer down. `Inspection` is static examination of an artifact with no execution, and holds one catalogued method whose evidence kind is `Manual`. Two classes for one act, and the row's own `🚧` reason contradicts the class it declares. | StR-001-VC-1; FR-001-AC-2, FR-001-AC-4; tests.md "Stakeholder and Integration Coverage" | wrong-requirement |
| FND-603 | medium | `StR-001-VC-2` is marked un-runnable on a rationale the criterion no longer states, and under-claims evidence the suite already produces. `b2f4cfa` reworded VC-2 to "An author starting from a skeleton this Module ships produces an artifact that `validate_document` accepts for its artifact type", but its matrix row still reads `🚧 minijinja-cli demonstration, not run in this package` — naming a template toolchain that FR-005-CON-3 and spec.md Out of Scope both forbid this module from shipping. As reworded, VC-2 is what TC-028 runs here today (every skeleton passes `validate_document` for its artifact type, `✅`, `Unit`). A row marked un-runnable that the suite discharges misreports coverage in the conservative direction, which is still misreporting. | StR-001-VC-2; tests.md "Stakeholder and Integration Coverage"; TC-028; FR-005-AC-1; FR-005-CON-3; spec.md Out of Scope | wrong-requirement |
| FND-604 | medium | The six cluster-blocked obligations carry `—` where the one other manual gate carries an id, so no evidence can ever bind to them. `NFR-001-AC-2` is the offline gate and is modelled correctly: class `Demonstration`, test case `TC-031`, `Type` `Manual`, status `🚧 Manual offline gate`. `FR-001-AC-2`, `FR-001-AC-3`, `FR-001-AC-4`, `StR-001-VC-1`, `IT-001-AC-1` and `IT-001-AC-2` are the same situation — a `Demonstration` this package cannot run — and get `—` instead. Because they carry no `TC-` id, no `@pytest.mark.trace` tag and no `quoin evidence` discharge can name them when a cluster does become available, and `quire coverage` mints them with no target. Give each a `Manual` test case as `TC-031` has; the `🚧` status and the honest reason stay. | tests.md "Functional Requirement Coverage" (FR-001-AC-2..4), "Stakeholder and Integration Coverage" (StR-001-VC-1, IT-001-AC-1..2), TC-031; FR-001-AC-2..4; IT-001-AC-1..2 | correct-requirement-no-evidence |
| FND-605 | medium | The `TC-017` strict expected failure has no negative control, so it cannot attribute a refusal to the mutation it introduces. IT-002 step 5 asserts the copy with one altered hex digit "is refused and the refusal names the artifact type and the path", but no step asserts that the *unmutated* copy reaches the same surface and is accepted — step 1 observes archetype registration, a different call and a different observation. Under quire-rs at `17b80e4` the contract check refuses this module's `semantic` block before any digest is computed (`src/semantic/contract.rs:264`, "semantic.exports names `<name>`, which object_types does not declare"; `src/semantic/resolver.rs:85` keys its locus on `object_types[...]`), so control and mutant are refused identically and by the same diagnostic. The row is honestly marked not-green, but for the wrong named cause, and the "a strict expected failure that starts passing announces the fixed engine" property does not hold: it would flip on the FND-400 fix, not on quire-rs#394. Sharpens `scope-boundary.md` FND-412 and `failure-domain.md` FND-109 from the evidence side — the gate design, not only the blocker list, is what needs the edit. | FR-003-AC-8; IT-002 step 5, IT-002-SC-05, IT-002-AC-2; TC-017; tests.md `🚧` preamble | correct-requirement-no-evidence |
| FND-606 | low | Twenty-two of the sixty-eight obligations are outside the advisor's population, so a third of the matrix's methods were chosen by hand and nothing says so. `quire coverage --json` mints 46 obligations — the 38 FR acceptance criteria, the 4 NFR acceptance criteria and the 4 NFR metric rows — and `quoin advise` therefore matched no applicability rule against the 14 `CON` `Validation` cells, the 3 StR `Validation` cells, or the 5 IT acceptance criteria. Its closing line, "0 inconclusive", is true of the 46 and says nothing about the other 22. Recorded so a later reader does not take the advisor's clean run as catalogue coverage of the whole set; the four rows this review flags on those cells (FND-600 in part, FND-601, FND-602, FND-603) all sit in the unadvised third, which is the population the deterministic half never saw. | `quoin advise` output; FR-002-CON-1..5, FR-003-CON-1..3, FR-004-CON-1..3, FR-005-CON-1..3; StR-001-VC-1..3; IT-001-AC-1..2, IT-002-AC-1..3 | correct-requirement-no-evidence |
| FND-607 | low | `FR-002-AC-5` binds two evidence kinds to one `Integration` test case, and one of its clauses is discharged by a test case the row does not name. `quoin advise` matches the criterion on both `stable-output` and `idempotence` and recommends `golden-approval-testing` (`Snapshot`) alongside `metamorphic-testing`. Its first clause — `make schemas-check` exits 0, then non-zero after a one-byte edit — is what TC-008 (`Integration`) runs. Its second — "`make schemas` run twice on one tree produces byte-identical output" — is verbatim `NFR-001-AC-1`, which is bound to TC-030 (`Snapshot`). TC-008's evidence cannot produce the snapshot half, and a failure of that half would be reported against a criterion whose named test never asserted it. Split the criterion, or point its second clause at TC-030. | FR-002-AC-5; TC-008; TC-030; NFR-001-AC-1 | correct-requirement-no-evidence |
| FND-608 | low | The Integration Test Matrix introduces a third, undeclared vocabulary in a column named `Type`. Its three rows carry `service`, which is neither an ISO 29148 method nor a Test Case Summary `Type`; the same test cases (TC-013, TC-017, TC-034, TC-035) are `Integration` in the summary. The Overview says the specification carries exactly two vocabularies and explains both, so a reader checking a `Type` against that explanation finds a value in neither. Two of the three rows also read `service` for an in-process library call (`quire.Registry.load_from`), not a service boundary. | tests.md "Integration Test Matrix"; tests.md Overview ("Two vocabularies, deliberately"); TC-013, TC-017, TC-034, TC-035 | wrong-requirement |
| FND-609 | low | `NFR-001-AC-4` is the one row where class, catalogued method and evidence kind agree exactly, and its threshold still has no reproducible baseline. `quoin advise` recommends `performance-benchmarking` on the matched values `latency` and `quantified-threshold`; the class is `Test`, the catalogued `evidenceKind` is `Benchmark`, and TC-033's `Type` is `Benchmark`. The 30 s bound is nonetheless "on the reference machine", which NFR-001 Scope defines by reference to "the machine that recorded the release notes for the version under test" — a machine no artifact of this set names. A benchmark whose baseline is named only forward, in a document that does not yet exist, cannot fail reproducibly. Confirms `integrity.md` FND-022 from the evidence side. | NFR-001-AC-4; NFR-001 Measurement metric 4; NFR-001 Scope ("Reference machine"); TC-033 | correct-requirement-no-evidence |

## The Deterministic Half

`quoin advise` over this spec set, run at `be4e64b`:

```
46 of 46 obligation(s) shown. Of all 46: 5 mismatch, 4 uncatalogued, 0 inconclusive.
```

The obligation population is what `quire coverage --json` mints: 38 FR
acceptance criteria, 4 NFR acceptance criteria, and the 4 NFR-001 Measurement
metric rows. FND-606 records what is *not* in it.

**The four `uncatalogued` rows** are `NFR-001-M-1..M-4`, whose `Method` cells
carry prose commands rather than a class or a catalogue id. Already carried as
`base.md` FND-010; not restated as a finding here. The matrix rows beside them
do carry catalogued classes, which is why the four NFR acceptance criteria are
not also flagged.

**The five `mismatch` rows**, and their disposition:

| Obligation | Authored | Recommended | Disposition |
|---|---|---|---|
| FR-001-AC-2 | Demonstration | `bdd-spec-by-example`, `unit-testing` (matched `property_shapes: example`) | **Confirm as authored.** The rules matched the statement's example shape and cannot see that "activation against a clean filament-core" needs a deployed service. Demonstration is right; the catalogued method under it is `demonstration`, evidence kind `Manual` — see FND-604. |
| FR-001-AC-3 | Demonstration | `bdd-spec-by-example`, `unit-testing` (`example`) | **Confirm as authored**, same reasoning. |
| FR-001-AC-4 | Demonstration | `property-based-testing` (`universal`) | **Confirm as authored.** The `universal` shape is real ("each declared archetype/object_type/artifact_type appears"), but the population is a database read-back over a live service; a property test over it is a cluster test, not a unit one. |
| NFR-001-AC-2 | Demonstration | `bdd-spec-by-example`, `unit-testing` (`example`) | **Confirm as authored.** This is the offline no-network gate; it is a manual procedure by construction and is the one row in the set already modelled correctly end to end (`Demonstration` → `TC-031` → `Type: Manual` → `🚧`). |
| NFR-001-AC-3 | Inspection | `property-based-testing` (`universal`) | **Correct, but not to the recommendation.** The evidence TC-032 produces is `Static`, which the `Inspection` class cannot yield (FND-600). Judgement, not catalogue: `Analysis` / `static-quality` is the class that joins the evidence actually planned; `property-based-testing` would be a stronger check over the added-locator set and a larger change than this row warrants. |

Recorded as judgement, per ADR-0010: the four confirmations and the
`Analysis` recommendation above are this reviewer's conclusions, not verdicts
the catalogue produced.

## Honesty of the Rows That Cannot Run Here

Checked row by row against the three populations named in the brief.

**Needs a live `filament-core-service`** — `FR-001-AC-2`, `FR-001-AC-3`,
`FR-001-AC-4`, `IT-001-AC-1`, `IT-001-AC-2`, `StR-001-VC-1`. All six are `🚧`
with the reason stated, none is claimed `✅`, and none is bound to a test case
that could not run. Honest. Two qualifications, carried as FND-602 (VC-1's
class) and FND-604 (the missing `TC-` ids).

**The manual offline gate** — `NFR-001-AC-2` / metric 2 / `TC-031`. Honest and,
on the class-to-evidence axis, the model row of the set: `Demonstration` →
`Manual` is a join the catalogue makes, the status is `🚧`, and NFR-001's
Verification section says in prose that no CI job is claimed. `spec.md` Out of
Scope says the same. No finding.

**The strict expected failure `TC-017`** — `FR-003-AC-8` / `IT-002-AC-2`.
Honest that the row is not green, and right to prefer a strict expected failure
to a skip; the `🚧` marker, the named blockers and the "never a skip and never a
silent pass" wording are all correct in form. The cause is misnamed and the gate
cannot discriminate: FND-605, confirming `scope-boundary.md` FND-412 and
`failure-domain.md` FND-109.

**The quire-engine rows** — `FR-003-AC-3` / `TC-013`, `IT-002-AC-1` / `TC-034`,
`IT-002-AC-3` / `TC-035` — are `✅ Complete` while the cluster rows are `🚧`,
and the distinction is defensible: `make dev-quire` provisions the wheel locally
whereas no target stands up a cluster, and NFR-001 plus IT-002 Preconditions both
say the rows **fail** rather than skip when the wheel is absent, which is the
correct discipline. It is worth noting only that `dependency.md` FND-204 shows
the wheel is not importable in this environment and the `dev-quire` target does
not exist yet, so those `✅` cells describe a suite that is red today for an
enablement reason the `🚧` preamble does not list. No separate finding: FND-204
carries it, and the classification itself is honest.

## Confirmations and Non-Restatements

Findings of the sibling reviews this lens independently reaches, listed so they
are not re-litigated here:

- `base.md` FND-006 — **disposed.** FR-001's `Verification` cells now read
  `Test (TC-036)` and `Demonstration`; `quoin advise` reports no
  `uncatalogued-verification-method` for any FR row.
- `base.md` FND-010 — **confirmed, still open.** All four NFR-001 metric
  `Method` cells are `⚠ uncatalogued` in the advisor output.
- `base.md` FND-011 — **disposed.** The preamble says ten and the tables carry
  ten.
- `base.md` FND-012 — **confirmed and resolved in a direction.** The single-row
  disagreement it flagged (`Inspection (TC-020)` against `Type: Static`) is one
  of the five rows of FND-600; the catalogue says the answer is `Analysis`, not
  that the two vocabularies may simply differ.
- `integrity.md` FND-022 — **confirmed** on the benchmark half; FND-609.
- `dependency.md` FND-204 — **confirmed** as the reason the engine-boundary `✅`
  rows are red today.
- `scope-boundary.md` FND-412 and `failure-domain.md` FND-109 — **confirmed and
  extended** by FND-605.
- `failure-domain.md` FND-104 — **adjacent.** `quoin advise` matches
  `FR-003-AC-5` on a `layering` shape and recommends `architecture-conformance`
  (`Analysis` / `Static`), which is the class a graph-topology property belongs
  to; TC-015's `Unit` fixtures discharge the enumerated cases only. Not raised
  separately — FND-104 owns the underdefinition, and fixing it settles the
  method.

## Recommendations

1. Adopt `Analysis` as the class for the five static-enumeration test cases
   (TC-004, TC-005, TC-020, TC-027, TC-032) and replace the Overview's
   `Inspection` → `Static` example with the catalogued relation: a `Type` is an
   evidence kind, and `quoin catalog methods --json` says which classes produce
   it. That turns the Overview's rule from a house convention into a checkable
   one (FND-600).
2. Add the `StR-001-VC-3` row bound to `TC-034`, and correct StR-001's closing
   sentence from "both outcomes" to the three criteria it now carries
   (FND-601).
3. Change `StR-001-VC-1`'s `Validation` cell to `Demonstration` (FND-602) and
   re-point `StR-001-VC-2`'s row at `TC-028` with `✅`, dropping the
   `minijinja-cli` reason (FND-603).
4. Mint `Manual` test cases for the six cluster-blocked obligations, modelled on
   `TC-031`, keeping their `🚧` status and reasons (FND-604).
5. Add an explicit acceptance step to IT-002 asserting the unmutated module copy
   reaches `Registry.load_from` and is accepted, so `TC-017` has a matched-pair
   control, and restate its blocker list against the surface that actually
   refuses this module today (FND-605).
6. Point `FR-002-AC-5`'s idempotence clause at `TC-030`, or split the criterion
   (FND-607); rename or explain the Integration Test Matrix `Type` column
   (FND-608); and name the reference machine before `TC-033` is treated as a
   gate (FND-609).
