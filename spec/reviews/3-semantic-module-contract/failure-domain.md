---
id: SR-004
title: "Failure-domain review of the #3 semantic-module contract spec"
type: SpecReview
analysis: failure-domain
scope: "spec/spec.md, spec/stakeholder/StR-001-module-activation.md, spec/usecase/US-001-consume-application-artifacts-as-records.md, spec/functional/FR-001-module-manifest-activates.md, spec/functional/FR-002-semantic-data-schemas.md, spec/functional/FR-003-semantic-manifest-contract.md, spec/functional/FR-004-markdown-mappings-and-imports.md, spec/functional/FR-005-executable-skeletons.md, spec/non-functional/NFR-001-reproducible-additive-projection.md, spec/integration/IT-001-manifest-activation-roundtrip.md, spec/integration/IT-002-module-load-and-extraction-roundtrip.md, spec/tests.md"
review_set: all
---
# SR-001: Failure-domain review of the #3 semantic-module contract spec

## Summary

Failure-domain analysis (extension-point failure policy, entity identity,
evaluation purity, topological robustness) of the agent-ix/spec-artifacts-app#3
spec set on branch `spec/3-semantic-module-contract`, run against the contracts
the spec names as its consumers rather than against the spec's own prose:

- quire-rs `src/semantic/contract.rs` (`read_semantic_block`, `SemanticModule`),
  `src/semantic/surface.rs` (`declaration_record`), `src/semantic/resolver.rs`
  (`resolve_reference`), `src/semantic/properties.rs` (type-token resolution),
  `src/semantic/context.rs` (`BundleIndex`), `src/validate_document.rs`
  (`semantic_findings`), `src/loader/mod.rs` (`read_module_semantic`,
  `resolve_data_schema`, the import graph and cycle pass).
- quoin `src/semantic/manifest.ts` (`readSemanticBlock`),
  `src/semantic/package-manifest.ts` (`derivePackageManifest`,
  `resolveImports`), `src/semantic/schemas/module-manifest.schema.json` (the
  `semantic` block and `ArtifactTypeEntry.data_schema` forms this repository
  bundles as the FR-035 gate).
- The reference sets named in the ticket: spec-objects-business#4 (`reviews/`
  SR-002 failure-domain) and spec-artifacts-iso#34 (`reviews/`
  26-09-03-spec-review-failure-domain-34.md, and the resolutions carried into
  its FR-006 Behavior).
- This repository's shipped `spec_artifacts_app/manifest.yaml` at the branch
  point.

Much of this set is specified better than its siblings. The offline `$ref`
boundary (FR-002-AC-3), the version-embedded `$id` rule (FR-002-CON-5), the
one-pass mapping failure rule with no partial record (FR-004 Behavior), the
`sourceSpan`-requires-`sourceIdentity` rule, the `## Invariants` clause-opacity
boundary (FR-004-CON-2), the negative-fixture-that-passes-is-a-gate-that-is-not-
gating rule (FR-005 Behavior), the refusal to skip on a missing wheel (NFR-001
Engine floor), and the explicit expected failures naming quire-rs#221 / #394
are all failure modes named and owned rather than assumed away.

Seventeen findings: three high, eight medium, six low. The three high findings
are each a requirement that cannot hold together with the contract it names.
Two of them (FND-100, FND-102) are the same two gaps spec-artifacts-iso#34
already recorded in its own FR-006 Behavior as `agent-ix/quire-rs#393` and
`agent-ix/quoin#336`; this spec's "Evidence, not obligation" section names
quire-rs#221, quire-rs#394, and filament-core-service#23 but not those two, so
the sibling module of the same wave carries a disclosure this one does not.
The third (FND-101) is new to this module because this module is the first in
the wave to declare a non-empty `semantic.imports`.

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|----|----------|---------|------|--------------|
| FND-100 | high | Identity confusion between the artifact-type record and the declaration record: the digest-bound `data_schema` is validated by quire against `SemanticExtraction::declaration_record()` — `{fields, clauses, operations}` only (`surface.rs`), pushed as a `semantic.record-invalid` **error** unconditionally (`validate_document.rs`) — while FR-002's models require `id`, `title`, `type`, `purpose`, `provenance`. Every shipped skeleton yields `{}` or `{clauses: […]}` against a schema requiring five keys it does not carry, so FR-003-AC-3, FR-005-AC-1 and IT-002-SC-02 (`is_valid == true`, no errors) cannot pass. spec-artifacts-iso records this as agent-ix/quire-rs#393; FR-003 does not. | FR-002 Behavior (Identity/status/provenance), FR-003 Description + AC-3, FR-005-AC-1, IT-002-SC-02, TC-013, TC-028, TC-034 | wrong-requirement |
| FND-101 | high | `semantic.imports` is specified with a value shape neither consumer accepts. quoin's module-manifest schema types it `object` → string matching `^[0-9]+\.[0-9]+\.[0-9]+$` (package → **exact version**), quoin's `resolveImports` matches that string against the provider's `module.version`, and quire reads it as `BTreeMap<String, String>` via `v.as_str().unwrap_or_default()`. FR-003's "map each imported module reference to the list of type names" is rejected by the bundled FR-035 schema (so FR-003-AC-1 and AC-4 cannot both pass) or, past the schema, coerced to `""` — which resolves against no module version, emits `semantic.import-unresolved` for every declared import, and contributes **no edge** to either engine's import graph. | FR-003 Description, Outputs, Behavior (Imports bullets), FR-003-AC-1, FR-003-AC-4, FR-003-AC-5, FR-004 Inputs, TC-014, TC-015 | wrong-requirement |
| FND-102 | high | The quoin install boundary is neither specified nor tested. quoin's `readSemanticBlock` builds its export check from `manifest.object_types` alone; this manifest declares `object_types: []` and both exported types under `artifact_types`, so every export earns `semantic.unknown-export` (and `semantic.export-without-schema` per the sibling's reading of the same file) once that quoin ships. No FR, AC, or IT of this set runs `quoin module install`; IT-002 covers the quire boundary only, and spec.md's Out of Scope does not name the gap. iso records it as agent-ix/quoin#336. | FR-003 Description, FR-003 Outputs (`exports`), FR-003 Behavior ("Evidence, not obligation"), IT-002 Target Integration, spec.md Out of Scope | missing-requirement |
| FND-103 | medium | `## Properties` is required in every skeleton, filled by nothing, mapped by nothing, and read by the engine. FR-005 requires each skeleton to author its typed declarations in the `Field \| Type \| Multiplicity \| Constraints` form; FR-002 declares no model property that form fills; FR-004's six mapping kinds name no entry for it; FR-004-AC-2 then fails on every skeleton unless the module's own declaration table is declared `prose_only: true`. Meanwhile quire's `properties.rs` *does* read it, and its output is precisely the `fields` array of FND-100's declaration record. | FR-005 Description, FR-005 Behavior (typed table bullet), FR-002 Outputs, FR-004 Behavior (mapping kinds), FR-004-AC-2, TC-022 | missing-requirement |
| FND-104 | medium | Cycle detection is redeclared downstream and left underdefined on all four topological axes: no rooting rule (a cycle has no canonical first node, so TC-015's "every module on the cycle in traversal order" asserts an unpinned string), no termination rule for a cycle among installed modules that does *not* reach this module, no handling for an installed module whose manifest is malformed or carries no `semantic` block, and a stated input — "every module installed under the Filament module root" — that makes the result machine-dependent against NFR-001's reproducibility, while AC-5 quietly measures a fixture graph instead. Both engines already implement this (quoin `resolveImports`: candidate-rooted DFS, open/done state map, `a -> b -> a`; quire `loader/mod.rs`: DFS with a color map). | FR-003 Behavior (cycle bullets), FR-003-AC-5, NFR-001 Statement + Scope, TC-015 | missing-requirement |
| FND-105 | medium | The missing-import check is one-directional and self-validating. It checks only that every `ImportedTypeRef` names a module and type present in this module's own `semantic.imports`. Nothing checks a declared type name against the imported module's actual `semantic.exports`; nothing flags a declared import no artifact references (over-declaration, which manufactures graph edges); nothing flags a declared import that is not installed, which is the one case both engines already diagnose (`semantic.import-unresolved`). "A missing import and a cross-module cycle are both detectable from the manifest alone" is stronger than the rules deliver. | FR-003 Description, FR-003 Behavior (Imports bullets), FR-003-AC-4, TC-014 | wrong-requirement |
| FND-106 | medium | Import sources are undercounted. The shipped manifest already names three spec-artifacts-iso types outside every scanned surface: `archetypes[0].composition.expected_artifacts: [MasterRequirements, StR, FR, NFR]`. FR-003's rule enumerates a skeleton, a negative fixture, or a `mappings.yaml` entry, so a cross-module type reference authored in the manifest itself is invisible to the missing-import check the same manifest is supposed to make sufficient. `allowed_links` and `doc_kinds` carry the same class of cross-module vocabulary. | FR-003 Behavior (`ImportedTypeRef` bullet), FR-003-AC-4, `spec_artifacts_app/manifest.yaml` archetypes | missing-requirement |
| FND-107 | medium | Two imported-type reference forms with no agreement rule. quire resolves a bare type token against `BundleIndex.imports` (package → exports, populated from every loaded module's `semantic.exports`) and mints the identity `ix://<org>/<repo>/type/<Token>`. This module publishes a second form, `<org>/<repo>#<Type>` mapping to `ImportedTypeRef { module, type }`. No requirement states that the two denote the same thing, and `IxTarget` — emitted in this module's own scalar set — is never connected to `ImportedTypeRef`, so the US-001 consumers receive two spellings of one identity. | FR-002 Behavior (Imported types), FR-002-AC-10, FR-004 Behavior (Imported types), FR-004-AC-4 | missing-requirement |
| FND-108 | medium | The `MasterRequirements` identity is ambiguous across the two modules *and* the engine resolves it by first match. quire iterates `bundle.imports` (a `BTreeMap` keyed by package) and returns the first package whose exports contain the token, so a `MasterRequirements` token is claimed by whichever package sorts first. This module exports `MasterRequirements`; spec-artifacts-iso exports `master-requirements` while shipping `MasterRequirements.json`. spec.md names agent-ix/quoin#345 as out of scope, but no requirement pins which spelling this module's `ImportedTypeRef` must write for the iso type, nor forbids the collision the two `exports` lists already create. | spec.md Out of Scope, FR-003 Outputs (`exports`, `imports`), FR-004 Behavior (Imported types), FR-002 Outputs | missing-requirement |
| FND-109 | medium | FR-003-AC-8 and IT-002-SC-05 mis-state the digest failure they carry as an expected failure. `resolver.rs` already computes `semantic.data-schema-digest-mismatch` naming the file, the computed digest and the recorded digest; the observable effect is that the archetype is dropped as an `ArchetypeLoadFailure`, not that "the load is refused". The criterion therefore conflates "no diagnostic exists" with "the Python surface does not report it", and a change that surfaces the failure while keeping per-archetype granularity flips a strict expected failure green for a step whose words still do not hold. | FR-003 Behavior ("Evidence, not obligation"), FR-003-AC-8, IT-002 step 5 + SC-05, IT-002-AC-2, TC-017, tests.md 🚧 note | wrong-requirement |
| FND-110 | medium | Generator purity is unstated and self-blessing. `make manifest-digests` "rewrites every `data_schema.digest` from the shipped bytes" and is folded into `make schemas`, so a corrupted, truncated, or hand-edited schema is silently re-blessed by the next build; no `--check` mode is declared to write nothing; and the FR-002 failure policy covers only the `@jsonSchema`-version mismatch — a `tsp compile` failure, an emission of zero module-base files, and a partially written `schemas/` directory have no stated outcome. FR-004-CON-3's "no file in the module derives Markdown from a record" is never reconciled with the generator that does write `manifest.yaml` and `schemas/`. | FR-002 Outputs (`make schemas`), FR-002 Behavior (Projection), FR-003 Outputs (`make manifest-digests`), FR-004-CON-3, TC-020, TC-030 | missing-requirement |
| FND-111 | medium | Mapping failure discipline covers a fixed list and is silent outside it, so the strict/resilient choice is undeclared for inputs the corpus produces: unparseable or absent frontmatter; a required section absent; a table with the right header and zero data rows (`[]` versus absent — no array carries `minItems`, so both validate and mean different things); a `Verification` cell with an opening `(` and no `)` (the "text between the first `(` and the last `)`" rule has no defined result); an `<org>/<repo>#<Type>` cell carrying two `#`; and a row id whose `^[A-Z]{2,4}-[0-9]+-` prefix names a different document than the frontmatter `id` (`AS-002-CAP-1` inside `AS-001` matches the pattern). | FR-004 Behavior (Failure discipline, typed-table bullets), FR-004-AC-6, FR-002 Behavior (Application structure), TC-025 | missing-requirement |
| FND-112 | low | Intra-record referential identity is unstated. `Capability.actors: ActorId[]` need not name rows of `## Actors`; `RequirementRef.source` and `RequirementRef.target` need not agree about which module owns the requirement; `DataDependency.source` is unresolved against anything. Row-id uniqueness is required within one table only, never across the document, so one id may appear in two tables. | FR-002 Behavior (Application structure), FR-004 Behavior (Failure discipline) | missing-requirement |
| FND-113 | low | The record is not a function of the document alone, which contradicts FR-004's own goal ("every consumer builds the same record from the same document"): `sourceSpan` is emitted only when the caller supplies `sourceIdentity`, and `provenance.sourceIdentity` is likewise caller-supplied and never synthesized, so two consumers reading one document build two different records and two different `provenance` values. | FR-004 Description, FR-004 Behavior (`ocl-clause`, `provenance`), FR-004-AC-5, FR-002 Behavior (provenance) | wrong-requirement |
| FND-114 | low | `provenance.digest` is over corpus document bytes "with no line-ending normalization", but NFR-001's `.gitattributes` LF pin covers this repository only. The documents this mapping reads live in other repositories, so one document yields two provenance digests on two checkouts; no requirement names which is authoritative, refuses a CRLF document, or normalizes before digesting. The same gap makes the `typed-table` "cells trimmed of `\r`" rule the only place CRLF is acknowledged. | NFR-001 Scope (Line endings), FR-004 Behavior (`provenance`, `typed-table`), FR-002 Behavior (provenance) | missing-requirement |
| FND-115 | low | The published mapping declaration is inert to every consumer named. quoin types `semantic.mappings` as a free-form `string[]` with no registry; quire's `SemanticModule` doc-comment records `mappings` as an install-time key it "accepts, not records". So `sysml-fence` is a name only this module knows, FR-004-AC-1's "only the six mapping kinds the manifest lists" is a self-check, and the only executable reader of `mappings.yaml` is the reference implementation FR-004 explicitly ships as test support and not as module code. | FR-003 Outputs (`mappings`), FR-004 Outputs (reference mapping), FR-004-AC-1, US-001 Story | correct-requirement-no-evidence |
| FND-116 | low | Refusal granularity is never stated for the consumer. Under the engines as written a bad digest, `$id`, or `$ref` drops that one artifact type, while an import cycle drains **every** archetype of the module into `ArchetypeLoadFailure`s. IT-002 asserts neither shape — SC-01 asserts a successful load and SC-05 a refusal — so a consumer of this module cannot learn from this spec how much of the module disappears on each class of refusal. | FR-003 Behavior (refusal bullets), IT-002-SC-01, IT-002-SC-05, FR-003-AC-6 | missing-requirement |
| FND-117 | low | The `application-spec` archetype entry is outside every rule this change adds. FR-005 adds `body_extraction` locators to "both artifact types"; the manifest's third declaration — the `kind: application-spec` archetype named `Application Spec` — is loaded by quire through the same `Archetype` path as the artifact types, carries no `data_schema`, no locators, and no export, and its `composition.expected_artifacts` is the FND-106 surface. FR-003-AC-3's "lists every archetype the manifest declares" therefore covers a declaration no other requirement mentions. | FR-005 Outputs (locators), FR-003-AC-3, `spec_artifacts_app/manifest.yaml` archetypes | missing-requirement |

## Verdict

Not ready for `spec-to-plan` until FND-100, FND-101 and FND-102 are
dispositioned. Each is a case where two of this spec's own criteria, or one
criterion and the contract source it names, assert opposite outcomes for the
same input — not a gap that a test can be written around. FND-103 belongs with
them in practice: it is the concrete form FND-100 takes in the skeletons, and
it makes FR-004-AC-2 unsatisfiable on the module's own fixtures.

The remaining medium findings are each a one-paragraph addition to an existing
Behavior section. The low findings are proposed additions, not blockers.

Nothing here changes the design. The TypeSpec source, the reference-form
`data_schema`, the digest binding, the six mapping kinds, the Markdown-as-sole-
authority policy, the executable skeletons with negative counterparts, and the
refusal to skip on a missing engine all stand.

## Recommendations

One concrete edit per high and medium finding, in the file the finding names.

1. **FND-100 (FR-003 Behavior, FR-002 Description).** Say which record the
   binding governs and what the engine may validate against it. Add to FR-003
   Behavior, beside the existing "Evidence, not obligation" bullets: "The
   schema a `data_schema` reference names is the artifact-type record of
   FR-002 and FR-004. The engine's declaration record (`{fields, clauses,
   operations}`, quire-rs FR-072) is not an instance of it; where the engine
   validates a declaration record against the bound schema it reports
   `semantic.record-invalid` for every document of this module, which is the
   wording gap filed as `agent-ix/quire-rs#393`." Then decide what FR-003-AC-3,
   FR-005-AC-1 and IT-002-SC-02 assert in the meantime — either an expected
   failure naming that issue (the pattern this spec already uses for #221 and
   #394), or `is_valid` with `semantic.record-invalid` filtered out and named.
   Add the issue to spec.md Out of Scope beside the other three.

2. **FND-101 (FR-003 Description, Outputs, Behavior, AC-4/AC-5).** Restate
   `semantic.imports` as the contract defines it: `imports: {agent-ix/spec-artifacts-iso: 0.2.0}`,
   a package-to-exact-version map, matched against the provider's manifest
   version. Move the type-name list that FR-003 currently puts there into a
   surface the contract admits — the natural home is `mappings.yaml` beside
   the `ImportedTypeRef` entries that consume it, or a module-local
   `imports.yaml` the suite reads. Then reword AC-4 as "every
   `ImportedTypeRef` names a package `semantic.imports` declares and a type
   that package's own `semantic.exports` declares" (which also closes
   FND-105), and reword AC-5 against the version-keyed graph.

3. **FND-102 (FR-003 Behavior, spec.md Out of Scope, IT-002).** Add the
   quoin-side evidence bullet the sibling module carries: "Evidence, not
   obligation — quoin: `readSemanticBlock` checks `semantic.exports` against
   `object_types` names only, so once that code ships this manifest will emit
   `semantic.unknown-export` and `semantic.export-without-schema` per exported
   artifact type; the manifest keeps `exports` as specified because the FR-070
   amendment is quoin's to make (agent-ix/quoin#336)." Add an IT-002 step, or
   a sibling IT, that runs `quoin module install` against the module root and
   records the diagnostic set verbatim, so the install-time consumer has a gate
   at all.

4. **FND-103 (FR-005 Behavior, FR-002 Outputs, FR-004 Behavior).** Decide
   whether the skeletons author `## Properties` at all. If they do, FR-002 must
   declare the model property it fills (`fields: FieldDecl[]`, borrowed from
   semantic-core) and FR-004 must map it; if they do not, delete the
   `Field | Type | Multiplicity | Constraints` requirement from FR-005 and say
   why an application composite declares no semantic-core fields. Declaring the
   module's own declaration table `prose_only: true` satisfies FR-004-AC-2 by
   letter and should be refused.

5. **FND-104 (FR-003 Behavior, FR-003-AC-5).** Replace the cycle bullets with
   the upstream algorithm rather than a second one: "The suite SHALL build the
   import graph from a fixture set of module manifests, root the traversal at
   this module's `package`, mark each node open/done so traversal terminates on
   any cycle whether or not it reaches this module, and report a cycle as the
   open-stack slice from the repeated node, joined `a -> b -> a` — the form
   both quoin `resolveImports` and the quire loader emit. A module in the
   fixture set carrying no `semantic` block contributes no edges." Drop
   "every module installed under the Filament module root" from Behavior, since
   AC-5 already measures a fixture graph and NFR-001 forbids a machine-
   dependent result.

6. **FND-105 (FR-003 Behavior, AC-4).** Add the two missing directions: "A
   type named in an `ImportedTypeRef` SHALL appear in the `semantic.exports`
   of the module `semantic.imports` names, read from that module's installed
   manifest; a declared import that no `ImportedTypeRef` references SHALL fail
   as an over-declaration, because an unused import is an edge in the graph
   the cycle check walks."

7. **FND-106 (FR-003 Behavior).** Extend the scanned surface: "…names an
   `ImportedTypeRef`, or appears in `archetypes[].composition.expected_artifacts`,
   `allowed_links`, or `doc_kinds` as a type this module does not declare…".
   Either declare `MasterRequirements`, `StR`, `FR`, and `NFR` in the imports
   the composition list already depends on, or state that composition entries
   are vocabulary rather than type references and are out of the check.

8. **FND-107 (FR-002 Behavior, FR-004 Behavior).** Tie the two forms together:
   "An `ImportedTypeRef { module: <org>/<repo>, type: <T> }` denotes the
   identity `ix://<org>/<repo>/type/<T>`, which is the identity the quire
   extractor mints for the bare token `<T>` resolved through the bundle index;
   a consumer MAY compute one from the other, and this module publishes the
   pair form because a cross-module `$ref` cannot resolve offline."

9. **FND-108 (FR-004 Behavior, spec.md Out of Scope).** Pin the spelling
   pending quoin#345: "Where two installed modules export a type of the same
   name, an `ImportedTypeRef` SHALL name the exporting module explicitly and
   SHALL use that module's own `semantic.exports` spelling — for
   spec-artifacts-iso's master-requirements type that spelling is
   `master-requirements`, not `MasterRequirements`. The bare-token form is not
   used by this module, because the engine resolves it by first match over the
   package map."

10. **FND-109 (FR-003-AC-8, IT-002 step 5, tests.md).** Restate the criterion
    against what the engine does: "A copy of the module with one
    `data_schema.digest` altered by one hex digit SHALL make that artifact type
    unavailable, with a failure whose reason carries
    `semantic.data-schema-digest-mismatch`, the schema path, the computed
    digest and the recorded digest. Recorded as a strict expected failure while
    the Python surface reports no failure detail (agent-ix/quire-rs#394)."
    Replace "the load is refused" in SC-05, which is not the granularity the
    loader has.

11. **FND-110 (FR-002 Behavior, FR-003 Outputs).** Add the generator's failure
    and purity policy: "`make schemas-check` and `make manifest-digests --check`
    SHALL write no file. A `tsp compile` failure, or an emission producing zero
    files under the module base, SHALL exit non-zero and leave the committed
    `schemas/` directory and `manifest.yaml` untouched. `make manifest-digests`
    SHALL refuse to rewrite a digest for a file that `make schemas-check`
    reports as differing from a fresh projection, so a corrupted schema is
    never re-blessed by the digest step." Reword FR-004-CON-3 to name the
    mapping rather than "the module", since the generator writes by design.

12. **FND-111 (FR-004 Behavior).** Enumerate the remaining inputs with a stated
    policy each: unparseable frontmatter and an absent required section fail
    naming the document; a table with a header and no data rows yields an empty
    array (and the models declare no `minItems` for exactly that reason, said
    once); a `Verification` cell with an unbalanced parenthesis fails naming
    the line; a cell with two `#` fails naming the line; and a row id whose
    document prefix differs from the frontmatter `id` fails naming both.

## Checklist Coverage

### 1. Extension points (trust boundaries)

| Boundary | Policy | Finding |
|----------|--------|---------|
| `make schemas` / `tsp compile` | strict on the `@jsonSchema` version mismatch (FR-002 Behavior); compile failure, zero-file emission, partial write and `--check` purity unstated | FND-110 |
| `make manifest-digests` | rewrites unconditionally, folded into `make schemas` | FND-110 |
| Negative fixture `expect` frontmatter | strict, and a fixture that passes fails the suite (FR-005 Behavior) — well specified | — |
| Quire wheel absent | strict: rows fail, never skip (NFR-001 Engine floor, IT-002 Preconditions) — well specified, and the corrective for the sibling repo's FND-110 | — |
| Quire load of a bad digest / `$id` / `$ref` | strict per archetype; the spec says "refused at load" | FND-109, FND-116 |
| Quire validation of the declaration record | strict error on every document, unstated | FND-100 |
| Quoin install of the semantic block | unspecified; no gate exists | FND-102 |
| FR-004 reference mapping | strict, all-failures-in-one-pass, no partial record — well specified for the listed conditions, silent outside them | FND-111 |
| `## Invariants` clause text | opaque bytes, never parsed (FR-004-CON-2) — well specified | — |

### 2. Entity identity

| Entity | Uniqueness key | Finding |
|--------|----------------|---------|
| Artifact-type record vs declaration record | conflated: one `data_schema` key, two instance shapes | FND-100 |
| Exported artifact type | manifest `name`; quire keys archetypes by name across all three sections, quoin from `object_types` only | FND-102, FND-117 |
| Imported type | two spellings (`<org>/<repo>#<Type>` and the bare token → `ix://…/type/…`), and a name collision on `MasterRequirements` resolved by map order | FND-107, FND-108 |
| Imported module | package identity, but the map's value shape disagrees with both engines | FND-101 |
| Typed-table row | `id_pattern` plus uniqueness within one table; not across tables, and the document prefix is unchecked | FND-111, FND-112 |
| `ClauseRef` | `clauseId`, unique within one document — well specified | — |
| Cross-row references (`Capability.actors`, `RequirementRef.source`/`target`, `DataDependency.source`) | none stated | FND-112 |
| Document provenance | `path` + byte digest, but caller-supplied `sourceIdentity` makes the record caller-dependent, and CRLF makes the digest checkout-dependent | FND-113, FND-114 |

### 3. Evaluation purity

- Markdown is the sole authority and the record derived; the module ships no
  code that writes Markdown (FR-004 Round-trip policy, FR-004-CON-3) — the
  strongest purity statement in the set, but not reconciled with the generator
  that writes `manifest.yaml` and `schemas/` (FND-110).
- Clause text is carried verbatim beside the record and never tokenized,
  typechecked, or evaluated (FR-004-CON-2, TC-019) — well specified.
- The mapping does not validate the record against the model, and mapping
  failures and schema failures are reported separately (FR-004 Behavior) —
  well specified.
- The record depends on caller-supplied inputs (`sourceIdentity`), so it is not
  a pure function of the document (FND-113).
- The cycle check reads the machine's installed module set (FND-104).

### 4. Topological robustness

- **Import graph.** Termination on a cycle not reaching this module is
  unstated; the traversal root and therefore the reported order are unstated;
  a malformed or block-less module in the graph is unstated; the graph is
  built from a value shape that yields no edges under either engine
  (FND-101, FND-104).
- **Schema `$ref` graph.** Confined to the module base and semantic-core
  0.1.0, resolved offline from shipped siblings, with no cross-module `$ref`
  by construction (FR-002-CON-2, FR-002-AC-3). `$ref` cycles are refused by
  the resolver upstream. No finding.
- **Document structure.** Section, table, and fence traversal is flat — no
  recursion, no nesting — so there is no depth or cycle risk; the edge cases
  are empty and duplicated structures rather than deep ones (FND-111).
- **Refusal blast radius.** Per-archetype for a schema refusal, module-wide
  for an import cycle; neither asserted (FND-116).

## Proposed Additions

- **FR** (FR-003 Behavior): which record the `data_schema` binding governs, and
  the engine-side divergence recorded as a named issue (FND-100).
- **FR** (FR-003 Description/Outputs/Behavior/AC-4/AC-5): `semantic.imports` as
  a package-to-exact-version map, with the type-name list moved to a surface
  the contract admits (FND-101).
- **FR** (FR-003 Behavior) and **IT** (IT-002 or a sibling): the quoin
  install-time boundary, its expected diagnostics, and a gate that runs it
  (FND-102).
- **FR** (FR-005 Behavior + FR-002 Outputs): resolve the `## Properties`
  contradiction — declare the model property or drop the table (FND-103).
- **FR** (FR-003 Behavior): rooted, terminating, fixture-based cycle traversal
  with the upstream diagnostic form (FND-104).
- **FR** (FR-003 Behavior): imports checked against the provider's `exports`,
  and over-declared imports refused (FND-105); the manifest's own
  `composition.expected_artifacts` added to the scanned surface (FND-106).
- **FR** (FR-002/FR-004 Behavior): the `ImportedTypeRef` ↔ `ix://…/type/…`
  equivalence (FND-107) and the collision rule for a type two modules export
  (FND-108).
- **FR** (FR-003-AC-8) and **IT** (IT-002 step 5): the digest-mismatch
  criterion restated at the granularity the loader has (FND-109).
- **FR** (FR-002 Behavior, FR-003 Outputs): generator failure policy, `--check`
  purity, and a digest step that cannot re-bless a bad projection (FND-110).
- **FR** (FR-004 Behavior): the unlisted mapping inputs and their strict or
  resilient policy (FND-111); intra-record reference rules (FND-112).
- **NFR** (NFR-001 Scope): CRLF handling for corpus documents this repository's
  `.gitattributes` does not cover (FND-114).
- **FR** (FR-004 Behavior / US-001 Story): state that the mapping declaration
  is data no shipped engine consumes today, so the claim is scoped to what the
  reference implementation demonstrates (FND-115).
- **IT** (IT-002): assert the blast radius of each refusal class (FND-116).
- **FR** (FR-005 Outputs): say what the `application-spec` archetype entry
  contributes under the contract, or that it contributes nothing (FND-117).
