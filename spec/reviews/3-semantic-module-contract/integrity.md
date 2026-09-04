---
id: SR-002
title: "Integrity review of the #3 semantic-module contract spec"
type: SpecReview
analysis: integrity
scope: "spec/spec.md, spec/stakeholder/StR-001-module-activation.md, spec/usecase/US-001-consume-application-artifacts-as-records.md, spec/functional/FR-001-module-manifest-activates.md, spec/functional/FR-002-semantic-data-schemas.md, spec/functional/FR-003-semantic-manifest-contract.md, spec/functional/FR-004-markdown-mappings-and-imports.md, spec/functional/FR-005-executable-skeletons.md, spec/non-functional/NFR-001-reproducible-additive-projection.md, spec/integration/IT-001-manifest-activation-roundtrip.md, spec/integration/IT-002-module-load-and-extraction-roundtrip.md, spec/tests.md"
review_set: all
---
# SR-001: Integrity review of the #3 semantic-module contract spec

## Summary

Integrity gate — completeness, consistency, atomicity and testability — over the
twelve artifacts that deliver `agent-ix/spec-artifacts-app#3`, read at commit
`b2f4cfa` (the base-review dispositions) and grounded against the tree they
describe: `spec_artifacts_app/manifest.yaml` at 0.2.0 with its `semantic` block,
both reference-form `data_schema` values and the per-artifact-type locator sets;
the 39-file emitted bundle under `spec_artifacts_app/schemas/` with its
`toolchain.json`; `typespec/main.tsp`; the `spec-artifacts-iso` 0.2.0 manifest;
and the quoin FR-070..FR-075 / quire-rs FR-069..FR-072 contract the spec cites.

Three things in this spec set are better than the house standard and should not
be lost in the finding list. The Test Matrix is internally consistent in both
directions: every one of the 36 test cases traces back to the criterion the FR
tables claim for it, no `TC` is orphaned, and no acceptance criterion,
constraint or NFR metric is missing a row — a check that fails in most specs of
this size. The matrix also refuses to hide anything: ten rows carry `🚧` with a
stated reason, the digest-mismatch row is a *strict* expected failure that fails
the suite if it starts passing, the semantic rows **fail** rather than skip when
the quire wheel is absent, and the Overview now explains the two verification
vocabularies rather than letting a reader mistake the mismatch for a defect. And
`spec.md` Out of Scope names eleven deferrals with a ticket each, so the shape
of what was *not* done is legible.

The gate does not pass. One high: FR-004 now has two mapping kinds
(`typed-table` over the `## Properties` table and `sysml-fence` over its
alternate fence) that both fill the same `fields` property, which FR-004-AC-1's
"declares every property of both exported models exactly once" forbids — the
criterion the base review's FND-001 disposition depends on cannot pass as
written. Twelve mediums follow: the `MasterRequirements` section properties are
still declared for `ApplicationSpec` only while the manifest, FR-005 and the
emitted schema give them to both; the `ConstraintDecl` keyword vocabulary the
new `## Properties` mapping splits into is named and never enumerated; offline
`$ref` resolution rests on a semantic-core bundle this module does not ship and
no requirement obliges a consumer to have; `toolchain.json` carries an
undeclared post-emit normalization pass inside the reproducibility boundary;
section drops are undeclared where frontmatter drops are declared; FR-003
Behavior still builds the cycle graph from the machine's installed module root
while its own Outputs now specify synthesized fixtures; FR-003-AC-6 is marked
complete on one of its two halves; the record is a function of the caller as
well as of the document; no requirement owns the Node/`tsp` toolchain or
`make dev-quire`; the vendored FR-035 schema has no sync rule; the free-text
list is delegated to the test; NFR-001 measures an FR it does not constrain; and
FR-001 and IT-001 are silent about the reference-form `data_schema` the 0.2.0
manifest now posts. Nine lows close the list.

Findings the base review (`base.md`) already carries — the `## Properties` form
without a model property (its FND-001), the `MasterRequirements` locator split
(FND-002), `## Boundaries` coverage (FND-003), the three dead emitted models
(FND-004), the NFR-001 addressable criteria (FND-005), the FR-001 verification
vocabulary (FND-006), StR-001-VC-2's templates (FND-007), the `🚧` row count
(FND-011) and FR-004-CON-3's method cell (FND-012) — were all dispositioned in
`b2f4cfa` and are re-verified as closed here rather than restated as findings.

## Verdict

**Not ready for `spec-to-plan`.** FND-001 is a one-line authoring decision
(either `mappings.yaml` admits two entries per property when they are declared
alternates, and FR-004-AC-1 says so, or the two forms become one entry with two
sources) but until it is made the criterion that guards the whole
`## Properties` disposition is unsatisfiable. FND-002..FND-013 are spec edits or
new criteria that fit in one authoring pass; FND-014..FND-022 are consistency
and atomicity cleanups that can ride the same pass. Once they are dispositioned
the matrix can be regenerated and the plan started.

## Traceability Matrix

Completeness deliverable: US -> FR -> StR -> verification. "StR (via US)" means
the only path to a stakeholder need is transitive through US-001.

| US | FR | StR | Verification (AC/CON -> TC) | Gap |
|---|---|---|---|---|
| — | FR-001 | none in frontmatter; StR-001 in prose only | AC-1 -> TC-036; AC-2..4 -> none, `🚧` needs a service; IT-001 | FND-013, FND-020 |
| US-001 | FR-002 | StR-001 (via US) | AC-1..11 -> TC-002..TC-010; CON-1..5 -> TC-001..TC-006 | FND-002, FND-004, FND-005, FND-012 |
| US-001 | FR-003 | StR-001 (via US) | AC-1..7 -> TC-011..TC-016; AC-8 -> TC-017 strict xfail; CON-1..3 -> TC-011, TC-012, TC-014; IT-002 | FND-007, FND-008, FND-011 |
| US-001 | FR-004 | StR-001 (via US) | AC-1..8 -> TC-018..TC-025; CON-1..3 -> TC-018, TC-019, TC-020 | FND-001, FND-003, FND-006, FND-010 |
| US-001 | FR-005 | StR-001 (via US) | AC-1..7 -> TC-018, TC-019, TC-026..TC-029; CON-1..3 -> TC-018, TC-026, TC-027; IT-002 | FND-002, FND-009 |
| — | NFR-001 (constrains FR-002, FR-003 only) | — | AC-1..4 -> TC-030..TC-033 | FND-009, FND-016, FND-022 |
| — | StR-001-VC-1, VC-2 | StR-001 | — (both `🚧`) | FND-021 |
| — | IT-001-AC-1, AC-2 | via FR-001 | — (both `🚧`) | FND-013 |
| — | IT-002-AC-1..3 | via FR-003, FR-005 | TC-034, TC-017, TC-035 | FND-013 |

Every FR maps to at least one verification method and every criterion carries a
matrix row. The gaps are at the two ends: no stakeholder requirement describes
the need this ticket serves (FND-021), and FR-001 declares no relationship to a
need of this repository at all (FND-020).

## Hidden Assumption Probes

| FR | Pattern | Result |
|---|---|---|
| FR-002 | Delegates to external CLIs (`node`, `npm`, `tsp`, `make`) | No requirement names a Node minimum, a detection method, or the error when the toolchain is absent (FND-010) |
| FR-002 | Lookup over multiple registries for `@agent-ix/semantic-core` | FR-002-CON-3 forbids a repository `.npmrc` and requires a committed lockfile; whether that lockfile may carry npm.ix resolved URLs is unstated, and it decides reproducibility on a second machine (FND-022) |
| FR-002 | Generation command | `make schemas` (build) and `make schemas-check` (check) are both specified; no interactive mode is needed. OK |
| FR-002 | Post-emit transformation | `toolchain.json` records a `normalization` pass (`absolute-id-and-ref` 1.0.0) that no requirement declares, inside the byte-reproducibility boundary (FND-005) |
| FR-002 | Depends on an external schema bundle at runtime | Every semantic-core `$ref` (`ClauseRef`, `FieldDecl`, `SemanticId`) resolves only for a consumer that already vendors semantic-core 0.1.0; no requirement states that precondition (FND-004) |
| FR-003 | Lookup over multiple modules | Behavior builds the cycle graph from the machine's installed module root; Outputs and AC-5 now specify synthesized fixtures instead, and the two were not reconciled (FND-007) |
| FR-003 | Depends on an unpublished package | The quire wheel is declared, ticketed (`agent-ix/quire-rs#392`) and made to fail rather than skip — but `make dev-quire` has no owning requirement and no minimum version (FND-010) |
| FR-003 | Consumes a vendored copy of an upstream schema | `tests/fixtures/module-manifest.schema.json` is the sole oracle for four criteria with no stated upstream revision or sync rule (FND-011) |
| FR-004 | Maps into an external closed vocabulary | The `ConstraintDecl` keyword set and `type.multiplicity` forms are named and never enumerated, so no test can tell a valid token from an invalid one (FND-003) |
| FR-001 | Calls an authenticated external API | No auth requirement, no minimum service revision, and no statement of what activation does with a reference-form `data_schema` (FND-013) |

## Failure Domain Check

- Extension failures. `b2f4cfa` added `unevaluatedProperties: { not: {} }` to
  FR-002 Behavior and to FR-002-AC-8, so an undeclared key is now refused rather
  than ignored and the negative-fixture set gained the case that proves it. The
  posture is deliberate and consistent with `legacy_forms: warning`. The
  remaining extension edge is upstream, not downstream: FR-003-AC-6 relies on
  the *vendored* FR-035 schema to reject an unknown `semantic` key, so a tenth
  key added upstream is rejected by this module's fixture (FND-011).
- Identity keys. `provenance.sourceIdentity` and every `ClauseRef.sourceSpan`
  remain conditional on a caller-supplied identity, so two consumers reading one
  document produce two different records against FR-004's own round-trip
  sentence (FND-008). `RequirementRefId` (`^(StR|US|FR|NFR|IT|TC)-[0-9]+$`) and
  `ArtifactId` (`^[A-Z]{2,4}-[0-9]+$`) overlap — `FR-014` satisfies both — so an
  aggregated requirement's id and the document's own id are not distinguishable
  by form. No requirement says they must be, and none says they need not be.
- Evaluation purity. FR-002-AC-5, NFR-001-AC-1 and the `.gitattributes` LF pin
  (present in the tree, as NFR-001 Scope claims) cover the projection, and
  FR-004-CON-2 keeps clause text opaque so no evaluation happens in this module
  at all. The undeclared `normalization` pass sits inside that boundary without
  a requirement (FND-005).
- Topological robustness. FR-003 covers the two-node and three-node cycle, the
  self-import, and demands the cycle and missing-import diagnostics stay
  distinct — the strongest part of the set, now backed by the synthesized
  dynamic-module fixtures `b2f4cfa` added. The weakness is the graph's
  provenance, not its traversal (FND-007).

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-001 | high | FR-004 now gives two mapping kinds the same target — a `typed-table` mapping fills `fields` from the `## Properties` table and a `sysml-fence` mapping fills `fields` from the alternate fence — while FR-004-AC-1 requires `mappings.yaml` to declare "every property of both exported models exactly once"; the criterion that guards the base review's `## Properties` disposition cannot pass, and neither `mappings.schema.json` nor any criterion says how two alternate sources for one property are expressed | FR-004 Behavior, FR-004-AC-1, FR-004-AC-7 | wrong-requirement |
| FND-002 | medium | FR-002 Behavior still says "The `ApplicationSpec` model SHALL carry `purpose: Section` as its one required section, and the optional sections `scope`, `systemOverview`, and `structure`", and its closing bullet lists only the six domain arrays as `ApplicationSpec`-only; but FR-005 Outputs, the manifest and the emitted `MasterRequirements.json` all give `MasterRequirements` those four sections with `purpose` required. The `MasterRequirements` section properties are declared by no requirement | FR-002 Behavior, FR-005 Outputs, manifest, MasterRequirements.json | missing-requirement |
| FND-003 | medium | FR-004 splits the `Constraints` cell of `## Properties` "into the closed `ConstraintDecl` keyword vocabulary" and sets `identity` from "the `identity` constraint token", and splits `Multiplicity` into `type.multiplicity`; neither vocabulary is enumerated in this spec nor pinned to a named semantic-core artifact, so TC-023 cannot distinguish a valid token from an invalid one and FR-005 ships a `## Properties` table whose legal cell contents are undefined | FR-004 Behavior, FR-004-AC-3, FR-005 Behavior | missing-requirement |
| FND-004 | medium | FR-002-AC-3, FR-002-CON-2 and NFR-001's Statement all assert every `$ref` resolves "with no network read", but FR-002 Behavior excludes the semantic-core schemas from the shipped bundle ("those ship in the semantic-core bundle quoin and quire vendor, never here") while `ClauseRef`, `FieldDecl` and `SemanticId` are `$ref`-ed from it; offline resolution is therefore a property of the consumer's vendored bundle, and no requirement states that precondition or the version it must carry | FR-002, NFR-001 | missing-requirement |
| FND-005 | medium | FR-002 Outputs describes `toolchain.json` as the compiler, emitter and semantic-core versions, the file list and a digest; the shipped file also carries `base` and a `normalization` record naming a post-emit `$id`/`$ref` rewrite pass (`absolute-id-and-ref` 1.0.0, `applied: false`). No requirement declares that pass, its determinism, or that not-applied is the expected steady state, yet FR-002-AC-7's digest and NFR-001-AC-1's byte equality both close over it | FR-002 Outputs, FR-002-AC-7, NFR-001-AC-1 | missing-requirement |
| FND-006 | medium | FR-004 requires `mappings.yaml` to record the frontmatter keys it drops but states no equivalent for dropped *sections*: FR-004-AC-2's "typed or `prose_only`" rule is scoped to shipped skeletons, so in any other document an unnamed H2 vanishes undeclared — including `## Requirements Architecture` and `## References` of `spec/spec.md`, the document FR-004-AC-8 requires to map cleanly | FR-004 Behavior, FR-004-AC-2, FR-004-AC-8 | missing-requirement |
| FND-007 | medium | FR-003 Behavior still builds the cycle graph from "the `semantic.imports` of every module installed under the Filament module root", making the suite's verdict a property of the machine and contradicting NFR-001; `b2f4cfa` added synthesized dynamic-module fixtures to FR-003 Outputs and FR-005 Outputs precisely so no real module is involved, and FR-003-AC-5 verifies the fixture graph — the Behavior sentence was not reconciled with either | FR-003 Behavior, FR-003 Outputs, FR-003-AC-5, NFR-001 | wrong-requirement |
| FND-008 | medium | FR-004 Description promises "every consumer builds the same record from the same document", but Behavior makes `provenance.sourceIdentity` and every `ClauseRef.sourceSpan` conditional on a caller-supplied identity and FR-004-AC-5 asserts both shapes are correct; the record is a function of document *and* caller, so two consumers legitimately disagree and the round-trip claim as written is false | FR-004 Description, FR-004 Behavior, FR-004-AC-5 | wrong-requirement |
| FND-009 | medium | NFR-001 declares `constrains` on FR-002 and FR-003 only, but NFR-001-AC-3 measures "every `body_extraction` locator this change adds", which FR-005-CON-1 and FR-005-AC-5 own and FR-004-CON-1 restates; the NFR measures two requirements it does not constrain, and neither FR-004 nor FR-005 names it downstream | NFR-001, FR-004, FR-005 | missing-requirement |
| FND-010 | medium | No requirement owns the execution preconditions the whole change rests on: no Node minimum for TypeSpec 1.15.0, no detection method, no user-facing error when `node`, `npm` or `tsp` is absent; and `make dev-quire` — named in FR-003 Inputs, NFR-001 Scope, NFR-001-AC-2 and IT-002 Preconditions — has no owning requirement, no minimum quire version, and no stated source for the wheel | FR-002, FR-003, NFR-001, IT-002 | missing-requirement |
| FND-011 | medium | `tests/fixtures/module-manifest.schema.json` is the sole oracle for FR-003-AC-1, AC-6, AC-7 and CON-1, but no requirement states which upstream revision it copies (FR-003 Inputs says only "FR-035 CR-003") or how it is refreshed; drift lets four criteria pass against a contract filament-core no longer enforces | FR-003 Inputs, FR-003-AC-1, AC-6, AC-7 | missing-requirement |
| FND-012 | medium | FR-002-AC-4 defers the normative free-text set to "the closed list the test enumerates", so the spec fixes no set and the criterion cannot fail; the shipped `Verification.json` already declares `method` and `annotation` as free text while FR-002 Behavior types `Verification.method` among the strings with `minLength: 1` | FR-002-AC-4, FR-002 Behavior, Verification.json | wrong-requirement |
| FND-013 | medium | FR-001 and IT-001 are unchanged from 0.1.0 and never mention the reference-form `data_schema` the 0.2.0 manifest now posts: FR-001-AC-4 and IT-001-SC-03's "with the correct attributes" have two readings, no minimum service revision is pinned, and the verbatim-storage assertion for `agent-ix/filament-core-service#23` is placed on IT-002-SC-03, the Quire boundary, where no activation-time snapshot resolution occurs at all | FR-001, IT-001, IT-002-SC-03 | missing-requirement |
| FND-014 | low | FR-002's record-naming rule ("the camelCase form of the frontmatter key or locator name with a trailing `_table` dropped") does not produce `fields` from either `properties_table` or `properties_fence`, and two locators mapping to one property is an unstated exception to a rule the spec otherwise applies literally | FR-002 Behavior, FR-005 Outputs, manifest | wrong-requirement |
| FND-015 | low | Both this module and `spec-artifacts-iso` 0.2.0 ship a `MasterRequirements.json` bound by digest to a master-requirements artifact type with a different property set; `spec.md` defers ownership to `agent-ix/quoin#345`, which is right for the decision, but no requirement says which model a consumer with both modules installed reads meanwhile, and US-001 Context names two disagreeing definitions of one type as the outcome the story exists to avoid | spec.md Out of Scope, FR-002, FR-003, US-001 Context | wrong-requirement |
| FND-016 | low | NFR-001 bundles byte reproducibility, offline resolution and additive compatibility under one requirement and one `quality_attribute: maintainability`; the last two are compatibility and portability qualities. Metric 2's row still reads "Network reads ... 0" measured by disabling the network namespace, which makes the count 0 by construction, while NFR-001-AC-2 restates it correctly as "both exit 0" — the metric row and its own criterion now say different things | NFR-001 Statement, NFR-001 Measurement, NFR-001-AC-2 | wrong-requirement |
| FND-017 | low | FR-003-AC-4's "the type list this module references" is self-referential: no requirement names the types imported from `spec-artifacts-iso`, so the criterion checks the manifest against itself; the manifest chose `StR`, `US`, `FR`, `NFR`, `IT`, `TC`, which is exactly FR-002's `RequirementKind` closed set and could simply be stated in FR-003 Outputs | FR-003 Outputs, FR-003-AC-4, FR-002 Behavior | missing-requirement |
| FND-018 | low | Duplicated obligations restated in different words across sections, so a change has three places to miss: FR-005-CON-1 equals the first half of FR-005-AC-5 equals NFR-001-AC-3 and overlaps FR-004-CON-1; FR-002-CON-4 equals FR-002-AC-6 and a Behavior bullet; FR-003-CON-1 equals FR-003-AC-7 and a Behavior bullet; the last clause of FR-002-AC-5 equals NFR-001-AC-1 | FR-002, FR-003, FR-004, FR-005, NFR-001 | wrong-requirement |
| FND-019 | low | Non-atomic criteria: FR-004-AC-5 carries eleven separable obligations, FR-005-AC-7 eight, FR-004-AC-6 five, FR-002-AC-8 four and FR-003-AC-2 four, each behind a single test case, so a partial failure names the criterion but not the obligation that broke | FR-002-AC-8, FR-003-AC-2, FR-004-AC-5, AC-6, FR-005-AC-7 | wrong-requirement |
| FND-020 | low | FR-001 carries no relationship to StR-001 or US-001 in frontmatter — only `implements` filament-core-service FR-035 — so this repository's activation requirement traces to no need of this repository; StR-001 asserts the link in Dependencies prose only, and `tests.md` carries no StR-to-FR-001 row | FR-001, StR-001 Dependencies | missing-requirement |
| FND-021 | low | `b2f4cfa` fixed StR-001-VC-2's wording off "templates" onto skeletons, but the stakeholder layer still states no need for the semantic contract itself: StR-001 is the composite-spec registration need, and FR-002..FR-005 reach a stakeholder need only transitively through US-001, so the typed-record need exists nowhere above the story | StR-001, US-001, FR-002..FR-005 | missing-requirement |
| FND-022 | low | NFR-001-AC-4 and metric 4 bound `make schemas-check` at 30 s "on the reference machine", which no requirement defines, so TC-033 cannot fail reproducibly; and FR-002-CON-3 forbids a repository `.npmrc` while requiring a committed `package-lock.json` without saying whether that lockfile may carry npm.ix resolved URLs, which decides whether NFR-001-AC-1 holds on a second machine | NFR-001-AC-4, FR-002-CON-3, NFR-001 Scope | missing-requirement |

## Finding Details

### FND-001 (high) — one property, two mapping entries

Evidence. `b2f4cfa` resolved the base review's FND-001 by giving both models
`fields?: FieldDecl[]` and adding two Behavior bullets to FR-004: "A
`typed-table` mapping SHALL fill `fields` from the `## Properties` table ..."
and "A `sysml-fence` mapping SHALL fill `fields` — the same property the
`## Properties` `typed-table` mapping fills — from a single fenced block tagged
`sysml` under the same heading". The manifest carries both locators
(`properties_table`, `properties_fence`) on both artifact types. FR-004-AC-1 is
unchanged: "`mappings.yaml` ... declares every property of both exported models
exactly once, names no undeclared property, uses only the six mapping kinds the
manifest lists, and each `typed-table` column list equals the locator's
`assert.columns`." One property with two mapping entries fails "exactly once";
one entry with two kinds has no expressible `lossless` value under FR-004-AC-7,
which assigns `lossless` per kind. `mappings.schema.json` is named as the
authority for the file's shape but its structure is described nowhere, so there
is no third reading to fall back on.

Proposed fix. Decide and record which shape `mappings.yaml` takes for an
alternate-form property — either one entry naming a primary kind and an
`alternates:` list, or two entries plus an `alternate_of` marker — then rewrite
FR-004-AC-1 as "declares every property ... exactly once, except a property
whose alternate forms are declared together, which is declared once per form
with the alternate marked", and extend FR-004-AC-7 to say `lossless` is carried
per form. Add a criterion that the two forms produce identical `fields` (today
only FR-005-AC-2 / TC-029 asserts it, from the skeleton side).

### FND-002 (medium) — the MasterRequirements sections

FR-002's "Application structure" block opens with "The `ApplicationSpec` model
SHALL carry `purpose: Section` as its one required section, and the optional
sections `scope`, `systemOverview`, and `structure` as `Section`" and closes
with "The `boundaries`, `capabilities`, `actors`, `interfaces`,
`dataDependencies`, and `renderingRequirements` properties belong to
`ApplicationSpec` only." The closing bullet implies the four sections are
shared; the opening bullet says they are not. FR-005 Outputs is unambiguous —
`title` and `purpose` required and `scope`, `system_overview`, `structure`
optional "on both types" — the manifest grants all five locators to
`MasterRequirements`, and the emitted `MasterRequirements.json` carries all four
sections with `purpose` in its required set. So the shipped schema is correct and
no requirement declares it. Under FR-002-CON-1 ("no locator output without a
field") the spec as written rejects the manifest the change actually ships.

Proposed fix. Change the opening bullet to "Both models SHALL carry `purpose:
Section` as their one required section, and `scope`, `systemOverview` and
`structure` as optional `Section` properties", which makes the closing bullet's
six-array exception the whole of the difference between the two models.

### FND-003 (medium) — an unenumerated closed vocabulary

FR-004 Behavior now requires the `## Properties` mapping to split "the
`Multiplicity` cell into `type.multiplicity` and the `Constraints` cell into the
closed `ConstraintDecl` keyword vocabulary, and setting `identity` from the
`identity` constraint token". `ConstraintDecl` is a semantic-core type and the
spec cites `@agent-ix/semantic-core` 0.1.0, but the keyword set, the
multiplicity forms, and the spelling of the `identity` token appear in no
artifact here. FR-005 fixes the header row (`Field | Type | Multiplicity |
Constraints`) and nothing about the cells. A skeleton author has no legal-value
list, TC-023 has no oracle for a bad token, and FR-005-AC-7's negative-fixture
set contains no malformed-constraint case.

Proposed fix. Enumerate the admitted `Constraints` keywords and `Multiplicity`
forms in FR-004 Behavior (or cite the semantic-core requirement id that
enumerates them, as FR-002 does for `ClauseRef` and `SourceLocus`), add an AC
that an unrecognised keyword fails naming the line, and add the matching
negative fixture to FR-005-AC-7.

### FND-004 (medium) — offline resolution needs a bundle this module does not ship

FR-002 Behavior: "The generator SHALL exclude from the shipped bundle every
schema whose `$id` falls outside the module base ... those ship in the
semantic-core bundle quoin and quire vendor, never here." FR-002-AC-3 then
requires every `$ref` to resolve "to a shipped sibling or to a file name of the
semantic-core 0.1.0 bundle, with no network read", and NFR-001's Statement
generalises it to "SHALL resolve every `$ref` of that bundle with no network
read". Both are true only where semantic-core 0.1.0 is already present. With
`fields?: FieldDecl[]` and `invariants?: ClauseRef[]` on both models, that is now
the common case rather than an edge. State the consumer precondition — which
bundle, which version, and that a consumer without it resolves the module-base
refs and nothing else — in FR-002 Outputs or NFR-001 Scope, beside the
npm-configuration precondition that is already recorded there in exactly this
form.

### FND-006 (medium) — declared frontmatter drops, undeclared section drops

FR-004 Behavior: "A `frontmatter` mapping SHALL drop every frontmatter key it
does not name, and `mappings.yaml` SHALL record the dropped key set per model,
so the loss is declared rather than silent." No sentence does the same for
sections; FR-004-AC-2 supplies the discipline for shipped skeletons only. The
consequence is visible in the document FR-004-AC-8 names: `spec/spec.md` carries
`## Requirements Architecture` and `## References`, which no locator names, so
its record omits them and AC-8 still passes. Either extend the
`prose_only`/declared-drop rule to any section a mapping does not name, or state
that unmapped sections are dropped by design and record the policy in
`mappings.yaml` beside the frontmatter drops.

### FND-007 (medium) — where the cycle graph comes from

FR-003 Behavior: "If the import graph built from this module's
`semantic.imports` and the `semantic.imports` of every module installed under
the Filament module root contains a cycle reaching this module, then the
module's test suite SHALL fail." `b2f4cfa` added to FR-003 Outputs "Dynamic-module
fixtures: minimal module manifests synthesized into a temporary directory at
test time ... synthesized rather than committed so that a cycle fixture cannot be
installed by accident, and no real module is edited to produce one", and
FR-003-AC-5 verifies that fixture graph. The Behavior sentence still describes
the installed-root scan the fixtures were introduced to avoid, and it is the
sentence a reader implementing FR-003 would follow. Rewrite it to "the import
graph built from this module's `semantic.imports` and the manifests supplied to
the check"; if a scan of the installed root is still wanted, add it as a
separate advisory criterion that cannot fail the suite.

### FND-008 (medium) — the record is a function of the caller too

FR-004 Description closes with "so that every consumer builds the same record
from the same document." Behavior then says "The mapping SHALL emit `sourceSpan`
only when the caller supplies a `sourceIdentity`" and the `provenance` mapping
"SHALL fill `provenance.sourceIdentity` from the caller and SHALL leave it
absent when the caller supplies none". FR-004-AC-5 asserts both shapes are
correct. The conditionality is right — semantic-core `SourceLocus` requires a
`sourceIdentity`, so synthesizing one would be worse — but the Description
sentence is then false as written. Restate it as "every consumer given the same
document and the same source identity builds the same record", and say in
Behavior that the identity is part of the mapping's input, not of the document.

### Lows

- FND-014: note the exception in FR-002's naming rule — `properties_table` and
  `properties_fence` are two forms of one declaration and both fill `fields` —
  or rename the locators so the rule still reads literally.
- FND-015: record in FR-002 or `spec.md` which `MasterRequirements` model a
  consumer with both modules installed reads while `agent-ix/quoin#345` is open,
  and whether this module's should become an `ImportedTypeRef` to iso's.
- FND-016: split NFR-001 into a reproducibility NFR and a compatibility NFR with
  their own `quality_attribute` values, and restate metric 2's row to match
  NFR-001-AC-2, which already says what is actually measured.
- FND-017: name the six imported types in FR-003 Outputs.
- FND-018: keep each obligation in one place — the Constraints table or the
  Behavior — and let the criterion reference it rather than restate it.
- FND-019: split FR-004-AC-5 into the positive mapping, the `sourceSpan`
  conditionality, the `invariantsText` fidelity and the five refusals; do the
  same for FR-005-AC-7's eight fixtures and FR-002-AC-8's four clauses.
- FND-020: add `traces_to` StR-001 to FR-001's frontmatter so it matches
  StR-001's Dependencies prose, and give the StR-to-FR-001 link a matrix row.
- FND-021: add StR-002, or StR-001-VC-3, stating the typed-record need in
  stakeholder terms — one structural contract per application artifact type,
  readable offline by the quire-contract-ir frontends and the filament-core-data
  generators — with its own validation criterion and matrix row.
- FND-022: define the reference machine, or make metric 4 a relative bound; and
  state whether `package-lock.json` may carry npm.ix resolved URLs.
