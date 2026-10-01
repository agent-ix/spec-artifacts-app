---
id: FR-002
title: "Semantic data schemas for the application artifact types are emitted from TypeSpec"
type: FR
relationships:
  - target: "ix://agent-ix/spec-artifacts-app/US-001"
    type: "implements"
  - target: "ix://agent-ix/filament-core-data/FR-031"
    type: "uses"
  - target: "ix://agent-ix/quoin/FR-073"
    type: "implements"
---
# FR-002: Semantic data schemas for the application artifact types are emitted from TypeSpec

## Description

The module SHALL declare one semantic data model per declared artifact type —
`ApplicationSpec` and `MasterRequirements` — as TypeSpec source importing
`@agent-ix/semantic-core`.

The module SHALL ship the JSON Schema 2020-12 projection of every declared model
at `spec_artifacts_app/schemas/<Model>.json`, covering both artifact-type models
and every support model and scalar they reference.

Each model is the typed form of the record the artifact type's `body_extraction`
locators extract: the frontmatter identity, the application's boundaries,
capabilities, actors, interfaces, data dependencies, UI rendering requirements,
the requirements it aggregates, and the document's provenance. The models
describe application *declarations*; the runtime state of a deployed application
is not a field of any model.

## Inputs

- `typespec/main.tsp`: the TypeSpec source, namespace `AgentIx.SpecArtifactsApp`,
  `@jsonSchema` base
  `https://schemas.agent-ix.org/agent-ix/spec-artifacts-app/`.
- `@agent-ix/semantic-core`, resolved from the registry the developer's npm
  configuration routes the `@agent-ix` scope to (today GitHub Packages), for `ClauseRef`, `SourceLocus`, and `SemanticId`.
- `@typespec/compiler` and `@typespec/json-schema` as
  devDependencies of the repository, with a committed `package-lock.json`.
- The frontmatter schemas already shipped at
  `spec_artifacts_app/schemas/applicationspec-frontmatter.schema.json` and
  `spec_artifacts_app/schemas/masterrequirements-frontmatter.schema.json`, which
  fix the identity keys and the `^[A-Z]{2,4}-[0-9]+$` id form.
- The `body_extraction` locators [FR-005](./FR-005-executable-skeletons.md) adds
  to the two artifact types, which fix the section and table set the models type.

## Outputs

- `spec_artifacts_app/schemas/ApplicationSpec.json` and
  `spec_artifacts_app/schemas/MasterRequirements.json`, the two exported models.
- One emitted schema file for every support model the two reference:
  `Section`, `Provenance`, `Relationship`, `Verification`, `ImportedTypeRef`,
  `Boundary`, `Capability`, `Actor`, `Interface`, `DataDependency`,
  `RenderingRequirement`, and `RequirementRef`.
- One emitted schema file for every scalar and enum the models reference:
  `NonEmptyText`, `ArtifactId`, `CapabilityId`, `ActorId`, `BoundaryId`,
  `InterfaceId`, `DataDependencyId`, `RenderingRequirementId`,
  `RequirementRefId`, `TestCaseRef`, `EdgeVerb`, `IxTarget`, `Cardinality`,
  `Sha256Digest`, `LineNumber`, `ArtifactStatus`, `ModuleRef`, `TypeName`,
  `UiSurface`, `ActorKind`, `InterfaceKind`, `InterfaceDirection`,
  `DataAccessMode`, `BoundaryKind`, and `RequirementKind` — 39 emitted files in
  all, and no model or scalar the two exported models do not reach.
- `make schemas` (regenerate) and `make schemas-check` (fail on any byte
  difference), each run after `npm ci`. The hand-authored
  `*-frontmatter.schema.json` files in the same directory are not projections and
  are outside both targets.
- The shipped payload — identical in the wheel, the sdist and the npm tarball —
  SHALL carry `manifest.yaml`, `mappings.yaml`, `mappings.schema.json`,
  `schemas/` and `skeletons/`. The npm package root **is** the module root, so
  `scripts/stage-npm.mjs` copies the payload up from the Python package at
  `prepack` and removes the copies at `postpack`; the TypeSpec toolchain
  (`typespec/`, `node_modules/`, the lockfile) is a build input and SHALL NOT
  ship in any of the three.
- The export-name to model map, fixed by this requirement and restated in
  [FR-003](./FR-003-semantic-manifest-contract.md): `ApplicationSpec` →
  `ApplicationSpec.json`, `MasterRequirements` → `MasterRequirements.json`. The
  `type` `const` of each model is the artifact-type name as the frontmatter
  schema beside it declares it.

## Behavior

Projection:

- The generator SHALL write every emitted schema with `$schema:
  https://json-schema.org/draft/2020-12/schema` and `$id:
  https://schemas.agent-ix.org/agent-ix/spec-artifacts-app/<Model>.json`.
- The generator SHALL keep every `$ref` of the shipped bundle inside two bases:
  the module base above and
  `https://schemas.agent-ix.org/semantic-core/<version>/`, where `<version>` is the
  installed `@agent-ix/semantic-core` version.
- The generator SHALL exclude from the shipped bundle every schema whose `$id`
  falls outside the module base, which the emitter produces for the imported
  semantic-core models; those ship in the semantic-core bundle quoin and quire
  vendor, never here.
- The generator SHALL declare every property of every object schema inline (no
  `allOf`, `extends`, or spread), so that the Python `jsonschema` library and the
  Rust `jsonschema` crate agree on every record.
- The generator SHALL seal every object schema
  (`unevaluatedProperties: { not: {} }`), so that a property no model declares is
  refused rather than ignored.
- The generator SHALL render each file as `JSON.stringify(schema, null, 2)` plus
  one trailing newline, with no formatter dependency.
- If `make schemas-check` finds a committed projection whose bytes differ from a
  fresh one, or a committed projection the fresh run no longer produces, then
  `make schemas-check` SHALL exit non-zero naming each file.

Identity, status, provenance:

- Both models SHALL carry `id` (`^[A-Z]{2,4}-[0-9]+$`, the form the frontmatter
  schemas already pin), `title`, and `type` (a `const` equal to the artifact-type
  name).
- Both models SHALL carry `provenance: Provenance` — the document's
  corpus-relative `path`, its optional `sourceIdentity` (a semantic-core
  `SemanticId`), and a `sha256:<64 hex>` digest over the document bytes as read,
  with no line-ending normalization.
- Both models SHALL carry `relationships: Relationship[]` with `target`
  (`^ix://`), `type` (an edge verb, `^[a-z][a-z0-9_]*$`), and an optional
  `cardinality`; `Relationship` SHALL declare exactly those three properties.
- Both models SHALL carry an optional `status: ArtifactStatus`
  (`^[A-Za-z][A-Za-z_-]*$`). The value set stays open: closing it is a vocabulary
  sweep-and-report, not a side effect of this schema set (see `spec.md` Out of
  Scope).
- Record property names SHALL be the camelCase form of the frontmatter key or
  locator name with a trailing `_table` dropped (`data_dependencies_table` →
  `dataDependencies`, `system_overview` → `systemOverview`).
- The one pair of locators whose property name is not derived from them is
  `properties_table` and `properties_fence`, which both fill `fields`: the
  property is the list of field declarations, not the section, and the two
  locators are the two authored forms of one declaration. `mappings.yaml`
  records the rename, and it is the only one.

Application structure:

- Both models SHALL carry `purpose: Section` as their one required section, and
  the optional sections `scope`, `systemOverview`, `structure`,
  `requirementsArchitecture`, and `references` as `Section`.
- Both models SHALL carry `fields?: FieldDecl[]` (semantic-core, `minItems: 1`),
  one entry per row of the typed `## Properties` table
  (`Field | Type | Multiplicity | Constraints`) or, as the alternate form of the
  same declarations, one entry per declaration of a single `sysml` fence under
  the same heading. The models SHALL NOT redeclare any property of `FieldDecl`.
- The `ApplicationSpec` model SHALL carry `boundaries: Boundary[]`, one per data
  row of the optional `## Boundaries` table, where `Boundary` is `{ id:
  ^[A-Z]{2,4}-[0-9]+-BND-[0-9]+$, name, kind: BoundaryKind, description, line }`
  and `BoundaryKind` is the closed set `owned`, `consumed`, `external`,
  `deferred`.
- The `ApplicationSpec` model SHALL carry `capabilities: Capability[]`, where
  `Capability` is `{ id: ^[A-Z]{2,4}-[0-9]+-CAP-[0-9]+$, name, description,
  actors: ActorId[], line }`.
- The `ApplicationSpec` model SHALL carry `actors: Actor[]`, where `Actor` is
  `{ id: ^[A-Z]{2,4}-[0-9]+-ACT-[0-9]+$, name, kind: ActorKind, description,
  line }` and `ActorKind` is the closed set `human`, `service`, `agent`,
  `external_system`, `scheduler`.
- The `ApplicationSpec` model SHALL carry `interfaces: Interface[]`, where
  `Interface` is `{ id: ^[A-Z]{2,4}-[0-9]+-IFC-[0-9]+$, name, kind:
  InterfaceKind, direction: InterfaceDirection, contract, line }`,
  `InterfaceKind` is the closed set `http_api`, `grpc`, `cli`, `event_stream`,
  `ui`, `library`, `file`, and `InterfaceDirection` is `inbound`, `outbound`,
  `bidirectional`.
- The `ApplicationSpec` model SHALL carry `dataDependencies: DataDependency[]`,
  where `DataDependency` is `{ id: ^[A-Z]{2,4}-[0-9]+-DAT-[0-9]+$, name, source:
  ImportedTypeRef, access: DataAccessMode, line }` and `DataAccessMode` is
  `read`, `write`, `read_write`.
- The `ApplicationSpec` model SHALL carry `renderingRequirements:
  RenderingRequirement[]`, where `RenderingRequirement` is `{ id:
  ^[A-Z]{2,4}-[0-9]+-UI-[0-9]+$, surface: UiSurface, requirement, verification:
  Verification, line }`. `UiSurface` is `^[a-z][a-z0-9-]*$` and is deliberately
  open: the surface vocabulary belongs to the applications, not to this module.
- The `ApplicationSpec` and `MasterRequirements` models SHALL carry `requirements:
  RequirementRef[]`, where `RequirementRef` is `{ id: RequirementRefId, kind:
  RequirementKind, source: ImportedTypeRef, target: IxTarget, line }` and
  `RequirementKind` is the closed set `StR`, `US`, `FR`, `NFR`, `IT`, `TC`.
- Both models SHALL carry `invariants?: ClauseRef[]` (semantic-core,
  `minItems: 1`), filled by the FR-004 `ocl-clause` mapping from an optional
  `## Invariants` section; the clause text is never parsed here.
- The `boundaries`, `capabilities`, `actors`, `interfaces`, `dataDependencies`,
  and `renderingRequirements` properties belong to `ApplicationSpec` only. A
  `MasterRequirements` document is the front page of a specification, not a
  description of a running system, and its artifact type declares no locator
  that would fill them.

Imported types:

- `ImportedTypeRef` SHALL declare exactly `{ module: ModuleRef, type: TypeName }`,
  where `ModuleRef` matches `^[a-z][a-z0-9-]*/[a-z][a-z0-9-]*$` and `TypeName`
  matches `^[A-Za-z][A-Za-z0-9_-]*$`.
- No model SHALL restate a property that an imported type declares. An
  application artifact references an imported type through `ImportedTypeRef` and
  an id, never by copying the imported type's fields.
- No model SHALL carry a `$ref` to another module's schema base, because a
  cross-module `$ref` cannot resolve offline from this module's shipped bundle.
  The `ImportedTypeRef` name pair is the reference form this module publishes.

Free text and scope:

- The models SHALL type `name`, `description`, `contract`, `requirement`, and
  `Verification.method` as strings with `minLength: 1`.
- The models SHALL constrain every property of every emitted object schema:
  after following `$ref` it carries `pattern`, `minLength`, `minimum`, `enum`,
  `const`, or `format`, or is an object of such properties, or an array of such
  items, or `boolean`/`null`. This admits no exception — a free-text property is
  still `NonEmptyText`, so it is still constrained.
- The models SHALL additionally declare, with a description beginning
  `free text:` and carrying the reason, every property whose *vocabulary* is
  open — a prose cell no lint rule and no registry owns. The declared set SHALL
  be exactly `Section.text`, `Provenance.path`, `Verification.method`,
  `Verification.annotation`, `Boundary.description`, `Capability.description`,
  `Actor.description`, `Interface.contract`, and `RenderingRequirement.requirement`.
  Widening the set is a decision recorded here, never a side effect of adding a
  model.
- No model SHALL carry a property named `deployed`, `running`, `health`,
  `uptime`, `instanceCount`, or `lastDeployedAt`: an application *declaration*
  and a deployed application's runtime state stay distinct.
- No model SHALL restate a constraint more loosely than the frontmatter schema
  beside it.

## Constraints

| ID | Constraint | Type | Validation |
|----|------------|------|------------|
| FR-002-CON-1 | The models SHALL declare exactly the fields the locators, the frontmatter schemas, and the FR-004 mappings produce: no field without a Markdown source, no locator output without a field. | Integrity | Test (TC-001, TC-002) |
| FR-002-CON-2 | The emitted bundle SHALL carry no `$ref` outside the module base and the semantic-core base, so that a consumer resolves every reference without a network read. | Boundary | Test (TC-003) |
| FR-002-CON-3 | The repository SHALL carry a committed lockfile, no `file:` or `link:` reference, and no `.npmrc` in the repository. | Reproducibility | Analysis (TC-004) |
| FR-002-CON-4 | No model SHALL carry a property named `deployed`, `running`, `health`, `uptime`, `instanceCount`, or `lastDeployedAt`: declaration and runtime state stay distinct. | Scope | Analysis (TC-005) |

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-002-AC-1 | `spec_artifacts_app/schemas/` carries `ApplicationSpec.json` and `MasterRequirements.json`, each a JSON Schema 2020-12 document whose `$id` is `https://schemas.agent-ix.org/agent-ix/spec-artifacts-app/<Model>.json`, and each `type` `const` equals the artifact-type name of the map in Outputs. | Test (TC-003) |
| FR-002-AC-3 | Every `$ref` across the emitted bundle resolves to a shipped sibling or to a file name of the semantic-core bundle, with no network read; no `$ref` names another module's base, another semantic-core version, or an unshipped file. | Test (TC-003) |
| FR-002-AC-4 | Every property of every emitted object schema is constrained by `pattern`, `minLength`, `minimum`, `enum`, `const`, or `format` (after following `$ref`), or is an object or array of such, or is `boolean`/`null`; and the set of properties whose description begins `free text:` is exactly the nine the Behavior section names — a tenth fails the check. | Test (TC-002) |
| FR-002-AC-5 | `make schemas-check` exits 0 on the committed tree, and exits non-zero naming the file after any one emitted schema is edited by a single byte; `make schemas` run twice on one tree produces byte-identical output. | Test (TC-008, TC-030) |
| FR-002-AC-6 | No emitted schema property is named `deployed`, `running`, `health`, `uptime`, `instanceCount`, or `lastDeployedAt`, and the `ApplicationSpec.json` description carries the sentence `runtime state (deployment, health, uptime) is not modelled`. | Analysis (TC-005) |
| FR-002-AC-8 | Every emitted object schema declares its properties inline (no `allOf`/`oneOf`/`anyOf`/`$ref` at the object's top level except a nullable scalar's `anyOf`) and is sealed with `unevaluatedProperties: { not: {} }`; the Python `jsonschema` validator accepts every record built from a shipped skeleton and rejects a record carrying a property no model declares. No negative fixture reaches the schema — every one is refused by the archetype or by the mapping first — so the sealing case is exercised by mutating a good record rather than by a fixture that does not exist. | Test (TC-009) |
| FR-002-AC-10 | No emitted object schema declares a property whose name and meaning duplicate a property of an imported type, and no `$ref` in the bundle names a base other than this module's or semantic-core — the imported-type reference form is `ImportedTypeRef`. | Test (TC-010) |
| FR-002-AC-12 | A built wheel, a built sdist and the staged npm payload carry the same entry set — `manifest.yaml`, `mappings.yaml`, `mappings.schema.json`, every file under `schemas/` and every file under `skeletons/` — none of them carries a TypeSpec toolchain file, and `stage-npm.mjs --clean` leaves no staged copy at the repository root. | Test (TC-044) |
| FR-002-AC-11 | The repository carries no `.npmrc`, `package-lock.json` is committed, and no dependency uses a `file:` or `link:` specifier. | Analysis (TC-004) |

## Dependencies

- **Upstream**: [US-001](../usecase/US-001-consume-application-artifacts-as-records.md), [FR-005](./FR-005-executable-skeletons.md) (the locators and skeletons the models type), filament-core-data FR-031..FR-033 (`@agent-ix/semantic-core`, agent-ix/filament-core-data#35), filament-core-data ADR-0005 (TypeSpec as the structural source)
- **Downstream**: [FR-003](./FR-003-semantic-manifest-contract.md) (references the emitted files), [FR-004](./FR-004-markdown-mappings-and-imports.md) (maps Markdown onto these models), [NFR-001](../non-functional/NFR-001-reproducible-additive-projection.md)
