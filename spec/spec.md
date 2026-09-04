---
id: AS-001
title: "spec-artifacts-app application spec"
type: ApplicationSpec
status: DRAFT
relationships:
  - target: "ix://agent-ix/filament-core-service/FR-035"
    type: "depends_on"
    cardinality: "1:1"
  - target: "ix://agent-ix/filament-core-data/FR-031"
    type: "depends_on"
    cardinality: "1:1"
  - target: "ix://agent-ix/quoin/FR-070"
    type: "depends_on"
    cardinality: "1:1"
  - target: "ix://agent-ix/spec-artifacts-iso/FR-005"
    type: "references"
    cardinality: "1:N"
---
# Specification: spec-artifacts-app

## Purpose

Multi-service applications need composite specs that aggregate per-service
requirements with a master-requirements rollup. This module contributes the
`application-spec` archetype, the `app-spec` grammar, and the two artifact types
that carry those composites — `ApplicationSpec` and `MasterRequirements` — and,
under the semantic-module contract, the typed data schemas, Markdown mappings,
and executable skeletons that let a consumer read an application composite as a
record instead of as prose.

## Scope

### In Scope

- The Module manifest (`spec_artifacts_app/manifest.yaml`), the
  `application-spec` archetype, the `app-spec` grammar, and the two artifact
  types it contributes.
- The functional requirement that the manifest activates idempotently against
  `filament-core-service`, and the integration test that verifies it.
- The semantic-module contract (agent-ix/spec-artifacts-app#3): a TypeSpec source
  importing `@agent-ix/semantic-core` 0.1.0; the emitted JSON Schema for every
  declared artifact type and every support model and scalar it references,
  shipped under `spec_artifacts_app/schemas/`; the manifest `semantic` block with
  reference-form `data_schema` and a declared `imports` set; the Markdown
  mappings in `spec_artifacts_app/mappings.yaml`; and the skeletons rewritten as
  executable typed fixtures with negative counterparts.
- The three fixture families the ticket names, minus the one it defers.
  *Compatibility* fixtures: the legacy-manifest fixture (this manifest with the
  `semantic` block and every `data_schema` removed) and the pre-change
  `spec/spec.md` baseline, which together prove the change is additive.
  *Dynamic-module* fixtures: minimal module manifests synthesized in a temporary
  directory at test time, carrying only a `semantic` block, used to exercise the
  missing-import and cross-module-cycle diagnostics of FR-003 without installing
  or editing a real module. *Generated-language* fixtures are deferred; see Out
  of Scope.

### Out of Scope

- The behaviour of `filament-core-service` itself, referenced here only by the
  relationship to its manifest schema (FR-035).
- The `quire-rs` validation and extraction engine; this Module declares the
  artifact types, the engine enforces them.
- Render templates and `template_ref`; these were removed ecosystem-wide and are
  not part of this Module.
- Any edit to a corpus repository. This ticket edits no corpus and sweeps no
  legacy form; the corpus promotion gate is agent-ix/quoin#291.
- Generated-language fixtures (Rust, TypeScript, Python) for the application
  types: produced by `agent-ix/filament-core-data#21`, `#22`, and `#23` and
  published only behind the promotion gate `agent-ix/quoin#290`; the
  semantic-core language packages are `agent-ix/filament-core-data#11`. None is
  produced or faked here.
- Publishing the quire wheel exposing `extract_semantic` to an index a repository
  may commit against: `agent-ix/quire-rs#392`. This Module provisions the wheel
  with a documented `make dev-quire` target, and its semantic tests **fail**
  rather than skip when the engine is absent (NFR-001). Declaring `quire` as a
  committed dev dependency waits on that issue.
- Naming what a module load refused: `agent-ix/quire-rs#221` (an unknown manifest
  key empties the model silently) and `agent-ix/quire-rs#394` (a `data_schema`
  digest mismatch drops the type with no diagnostic). FR-003-AC-6's "naming the
  key or the path" half and FR-003-AC-8 are carried as explicit expected failures
  naming those issues.
- Record validation of a legacy-form artifact that declares `object:`:
  `agent-ix/quire-rs#391` (the engine validates an `unavailable` record as `{}`).
  No artifact this Module ships carries `object:`, and the defect is carried
  beside the criterion rather than worked around by relaxing a schema.
- Resolving a reference-form `data_schema` into a stored snapshot at activation:
  `agent-ix/filament-core-service#23`. Until it lands the service stores the
  reference verbatim, which is what IT-002-SC-03 asserts.
- Deciding which module owns the `MasterRequirements` artifact type. Both this
  Module and `spec-artifacts-iso` declare one; the overlap predates this ticket
  and resolving it is a cross-module vocabulary decision filed as
  `agent-ix/quoin#338`, not a side effect of this schema set.
- Installing this Module under a quoin carrying the FR-070 reader. quoin
  resolves `semantic.exports` and `data_schema` against `object_types` only, so
  a Module whose semantic types are artifact types is refused at install
  (`agent-ix/quoin#336`). The published quoin carries no semantic-block reader
  at all, so the block is inert to every quoin a user can install today; the
  amendment is quoin's to make and this Module does not bend its exports to it.
- Declaring, in the manifest, *which types* this Module imports from a package.
  FR-035 types `semantic.imports` as package to exact semver and carries no type
  list, so the list is declared in `mappings.yaml` under `imported_types` and
  the contract amendment is `agent-ix/quoin#339`.
- Validating an artifact-type record against its `data_schema` at load time.
  quire's `validate_document` validates a *declaration* record
  (`{fields, clauses, operations}`) and never reaches an artifact-type record,
  so no engine validates this Module's `ApplicationSpec` or `MasterRequirements`
  record today (`agent-ix/quire-rs#393`). Until it lands, this Module's own test
  suite is the record oracle.
- Closing the `status` frontmatter vocabulary. Closing it is a sweep-and-report,
  not a side effect of this schema set.
- Making the offline, no-network run a CI job. NFR-001 records it as a manual
  gate; no CI job is claimed here.
- Any UI implementation change. This Module declares UI *rendering requirements*
  as data; it renders nothing.

## System Overview

### System Description

`spec-artifacts-app` is a config-only Filament Module, published as both a Python
package and an npm package, whose payload is a manifest, a set of JSON Schemas,
a set of authoring skeletons, and a Markdown mapping declaration. It contributes
the `application-spec` archetype and the `ApplicationSpec` and
`MasterRequirements` artifact types, and it declares one semantic data model per
artifact type as TypeSpec under `typespec/`, projected to JSON Schema 2020-12
under `spec_artifacts_app/schemas/`. Each artifact type is bound to the exact
shipped schema bytes through the manifest `semantic` block and a reference-form
`data_schema`. Markdown remains the sole authority; the record is a derived
projection.

### Intended Users

The Filament platform (which activates and serves the contributed artifact
types), spec authors writing application composite specs, and the semantic
consumers of the emitted schemas and records — the quire-contract-ir frontends,
the filament-core-data code generators, and the Filament extraction API.

## Structure

- `stakeholder/` — StR-XXX stakeholder requirements.
- `usecase/` — US-XXX user stories stating the consumer-side need.
- `functional/` — FR-XXX functional requirements.
- `non-functional/` — NFR-XXX quality requirements.
- `integration/` — IT-XXX integration tests.
- `tests.md` — the requirements test matrix.

## Properties

| Field | Type | Multiplicity | Constraints |
|---|---|---|---|
| module_name | String | 1..1 | identity, pattern: /^[a-z][a-z0-9-]*$/ |
| manifest_version | String | 1..1 | pattern: /^[0-9]+\.[0-9]+\.[0-9]+$/ |
| contract_version | String | 1..1 | pattern: /^[0-9]+\.[0-9]+\.[0-9]+$/ |
| semantic_core | String | 1..1 | pattern: /^[0-9]+\.[0-9]+\.[0-9]+$/ |
| implementation_language | String | 1..1 | nonEmpty |

## Boundaries

| ID | Name | Kind | Description |
|---|---|---|---|
| AS-001-BND-1 | Application artifact types | owned | `ApplicationSpec` and `MasterRequirements` — their schemas, mappings, skeletons and locators are specified here. |
| AS-001-BND-2 | ISO artifact types | consumed | `StR`, `US`, `FR`, `NFR`, `IT`, `TC` are owned by `spec-artifacts-iso` and referenced, never restated. |
| AS-001-BND-3 | Validation and extraction engine | external | `quire-rs` enforces what this Module declares; its behaviour is not specified here. |
| AS-001-BND-4 | Corpus promotion | deferred | Named so its absence is deliberate: no corpus repository is edited by this Module, and promotion is `agent-ix/quoin#291`. |

## Capabilities

| ID | Name | Description | Actors |
|---|---|---|---|
| AS-001-CAP-1 | Declare the application artifact types | Contribute the `application-spec` archetype, the `app-spec` grammar, and the two artifact types with their frontmatter schemas and locators. | AS-001-ACT-1, AS-001-ACT-2 |
| AS-001-CAP-2 | Publish a typed record contract | Ship one emitted JSON Schema per artifact type, bound to the manifest by path and SHA-256 digest. | AS-001-ACT-3 |
| AS-001-CAP-3 | Declare the Markdown mapping | Say, per record property, which authored form fills it and whether that form round-trips. | AS-001-ACT-3 |
| AS-001-CAP-4 | Ship executable authoring fixtures | Skeletons that validate, extract, and map, with negative counterparts that must be refused. | AS-001-ACT-2 |

## Actors

| ID | Name | Kind | Description |
|---|---|---|---|
| AS-001-ACT-1 | Filament platform | service | Activates the manifest and serves the contributed artifact types. |
| AS-001-ACT-2 | Spec author | human | Writes application composites from the shipped skeletons. |
| AS-001-ACT-3 | Semantic consumer | service | Reads a composite as a typed record — the quire-contract-ir frontends, the filament-core-data generators, the Filament extraction API. |
| AS-001-ACT-4 | Quire engine | service | Loads the module, validates documents, and extracts semantic records. |

## Interfaces

| ID | Name | Kind | Direction | Contract |
|---|---|---|---|---|
| AS-001-IFC-1 | Module manifest | file | outbound | `spec_artifacts_app/manifest.yaml` under filament-core-service FR-035 |
| AS-001-IFC-2 | Emitted schema bundle | file | outbound | `spec_artifacts_app/schemas/<Model>.json`, JSON Schema 2020-12 |
| AS-001-IFC-3 | Markdown mapping declaration | file | outbound | `spec_artifacts_app/mappings.yaml` under `mappings.schema.json` |
| AS-001-IFC-4 | Activation endpoint | http_api | outbound | POST /api/v1/modules/activate |
| AS-001-IFC-5 | Semantic-core grammar | library | inbound | `@agent-ix/semantic-core` 0.1.0 |

## Data Dependencies

| ID | Name | Source | Access |
|---|---|---|---|
| AS-001-DAT-1 | Stakeholder requirements referenced by a composite | agent-ix/spec-artifacts-iso#StR | read |
| AS-001-DAT-2 | Functional requirements referenced by a composite | agent-ix/spec-artifacts-iso#FR | read |
| AS-001-DAT-3 | Non-functional requirements referenced by a composite | agent-ix/spec-artifacts-iso#NFR | read |
| AS-001-DAT-4 | Integration tests referenced by a composite | agent-ix/spec-artifacts-iso#IT | read |

This Module declares no `## UI Rendering Requirements`. It renders nothing — it
declares UI rendering requirements as *data* for the applications that do — and
the section is optional precisely so a module with no surface omits it rather
than authoring an empty table.

## Requirements

| ID | Kind | Source | Target |
|---|---|---|---|
| StR-001 | StR | agent-ix/spec-artifacts-iso#StR | ix://agent-ix/spec-artifacts-app/StR-001 |
| US-001 | US | agent-ix/spec-artifacts-iso#US | ix://agent-ix/spec-artifacts-app/US-001 |
| FR-001 | FR | agent-ix/spec-artifacts-iso#FR | ix://agent-ix/spec-artifacts-app/FR-001 |
| FR-002 | FR | agent-ix/spec-artifacts-iso#FR | ix://agent-ix/spec-artifacts-app/FR-002 |
| FR-003 | FR | agent-ix/spec-artifacts-iso#FR | ix://agent-ix/spec-artifacts-app/FR-003 |
| FR-004 | FR | agent-ix/spec-artifacts-iso#FR | ix://agent-ix/spec-artifacts-app/FR-004 |
| FR-005 | FR | agent-ix/spec-artifacts-iso#FR | ix://agent-ix/spec-artifacts-app/FR-005 |
| NFR-001 | NFR | agent-ix/spec-artifacts-iso#NFR | ix://agent-ix/spec-artifacts-app/NFR-001 |
| IT-001 | IT | agent-ix/spec-artifacts-iso#IT | ix://agent-ix/spec-artifacts-app/IT-001 |
| IT-002 | IT | agent-ix/spec-artifacts-iso#IT | ix://agent-ix/spec-artifacts-app/IT-002 |

## Invariants

The clauses this Module's own declaration enforces. Each clause owns one `ocl`
fence under its own `### <clauseId>` heading; the fence text is carried verbatim
and is never evaluated here.

### EveryExportedTypeCarriesADataSchema

```ocl
context ApplicationSpec
inv EveryExportedTypeCarriesADataSchema:
  self.requirements->forAll(r | r.source.module = 'agent-ix/spec-artifacts-iso')
```

### EveryDataDependencyNamesAnImportedModule

```ocl
context ApplicationSpec
inv EveryDataDependencyNamesAnImportedModule:
  self.dataDependencies->forAll(d | d.source.type->notEmpty())
```

## Requirements Architecture

The requirement classes trace from the stakeholder need for application composite
specs (`stakeholder/`) through the consumer's story of reading those composites
as typed records (`usecase/`) to the functional requirements (`functional/`):
FR-001 activates the manifest against filament-core; FR-002 emits the semantic
data schemas; FR-003 declares the semantic block, the digest-bound
`data_schema` references, and the imports; FR-004 declares the Markdown mappings
and the imported-type reference form; FR-005 makes the skeletons executable
fixtures with negative counterparts. NFR-001 bounds all of it to a reproducible,
offline, additively-compatible projection. IT-001 verifies the activation
boundary and IT-002 the Quire engine boundary. `tests.md` records every
criterion's test case.

## References

- ISO/IEC/IEEE 29148 — Requirements engineering.
- filament-core-service FR-035 — Module Manifest Schema, the upstream this Module
  activates against.
- `agent-ix/filament-core-data` FR-031..FR-034 and ADR-0005 — semantic-core
  grammar, scalars, JSON Schema projection, and TypeSpec as the structural
  source.
- `agent-ix/quoin` FR-070..FR-075 — the semantic-module contract, mappings,
  `data_schema` by digest, legacy forms, and package manifests.
- `agent-ix/quire-rs` FR-069..FR-072 — the contract at load, typed `Properties`,
  clauses and operations, and the extraction surface.
