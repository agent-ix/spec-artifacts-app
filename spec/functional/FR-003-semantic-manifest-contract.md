---
id: FR-003
title: "The manifest declares the semantic block, references each data schema by digest, and declares its imports"
type: FR
relationships:
  - target: "ix://agent-ix/spec-artifacts-app/US-001"
    type: "implements"
  - target: "ix://agent-ix/spec-artifacts-app/FR-001"
    type: "depends_on"
  - target: "ix://agent-ix/spec-artifacts-app/FR-002"
    type: "depends_on"
  - target: "ix://agent-ix/quoin/FR-070"
    type: "implements"
  - target: "ix://agent-ix/quoin/FR-073"
    type: "implements"
---
# FR-003: The manifest declares the semantic block, references each data schema by digest, and declares its imports

## Description

The module manifest (`spec_artifacts_app/manifest.yaml`) SHALL carry one
`semantic` block under the quoin FR-070 contract (`contract_version: 1.0.0`).

The manifest SHALL reference, on every artifact type
[FR-002](./FR-002-semantic-data-schemas.md) gives a model, the emitted schema by
module-relative path and SHA-256 digest (`data_schema: { schema:
schemas/<Model>.json, digest: sha256:<hex> }`), so that quoin at install time and
quire at load time bind the artifact type to the exact shipped bytes.

The manifest SHALL declare, in `semantic.imports`, every module whose types this
module's artifacts reference, so that a missing import and a cross-module cycle
are both detectable from the manifest alone.

## Inputs

- `spec_artifacts_app/manifest.yaml` with its existing `archetypes`, `grammars`,
  `artifact_types`, `doc_kinds`, and `frontmatter_schema_ref` values.
- The emitted schemas of [FR-002](./FR-002-semantic-data-schemas.md) and the
  export-name to model map fixed there.
- The FR-035 module-manifest schema, bundled for the suite at
  `tests/fixtures/module-manifest.schema.json`, carrying the `semantic` block and
  the reference-form `data_schema` of filament-core-service FR-035 CR-003. The
  copy is vendored byte-for-byte from the revision `quoin` ships at
  `src/semantic/schemas/module-manifest.schema.json`, and the suite records that
  revision's SHA-256 so a silent divergence from upstream is a failing test
  rather than an assumption.
- The quire engine the suite runs against: the wheel exposing
  `extract_semantic`, provisioned by `make dev-quire`. No index a repository may
  commit against carries it, so `quire` is not a declared dependency;
  agent-ix/quire-rs#392 is the blocking issue and the semantic rows **fail**
  rather than skip when the wheel is absent.

## Outputs

- The `semantic` block: `contract_version: 1.0.0`, `semantic_core: 0.1.0`,
  `package: agent-ix/spec-artifacts-app`, `exports: [ApplicationSpec,
  MasterRequirements]`, `imports` naming `agent-ix/spec-artifacts-iso` and the
  types this module's artifacts reference from it, `targets: [json-schema,
  markdown]`, `mappings: [frontmatter, section, typed-table, sysml-fence,
  ocl-clause, provenance]`, `compatibility_posture: additive`, and
  `legacy_forms: warning`.
- One `data_schema` reference per exported artifact type, beside its
  `frontmatter_schema_ref`, using the FR-002 map.
- `version: 0.2.0`, bumped as the first step of the change so `make schemas` and
  the digests are computed once against one version.
- A legacy-manifest fixture at `tests/fixtures/manifest-legacy.yaml`: this
  manifest with the `semantic` block and every `data_schema` removed, which
  CON-1 uses to prove the module still validates and loads for a consumer that
  predates the block. This is the compatibility fixture the ticket asks for.
- Dynamic-module fixtures: minimal module manifests synthesized into a temporary
  directory at test time, each carrying a `name`, a `version`, and a `semantic`
  block and nothing else, used to build the import graphs AC-4 and AC-5 exercise.
  They are synthesized rather than committed so that a cycle fixture cannot be
  installed by accident, and no real module is edited to produce one.
- `make manifest-digests`, folded into `make schemas`, which rewrites every
  `data_schema.digest` from the shipped bytes; the suite never hand-computes a
  digest.

## Behavior

- The `semantic` block SHALL carry exactly the nine keys listed in Outputs.
  `sweep_report` is absent because `legacy_forms` is `warning`: this module's own
  documents author no legacy `## Properties` form, so `warning` is the value that
  changes nothing, and promoting it to `error` is what would demand a
  `sweep_report`.
- Each `data_schema.digest` SHALL equal the SHA-256 over the raw bytes of the
  file `data_schema.schema` names, with no line-ending normalization.
- The manifest SHALL carry no inline `data_schema` object on any artifact type;
  the reference form is the only form.
- The manifest SHALL add no new required key at the manifest root or on any
  artifact-type entry.
- If any `data_schema.digest` differs from the SHA-256 of the shipped file, then
  the module's test suite SHALL fail naming the artifact type, the recorded
  digest, and the computed digest.
- If the manifest declares a `semantic` key outside the admitted set, a
  `package` that is not `<org>/<repo>`, or a `targets` value outside the
  registry, then the bundled FR-035 schema SHALL reject the manifest naming the
  key or value.
- The bundled FR-035 schema does *not* reject a `data_schema` mixing
  `schema`/`digest` with another key on an *artifact* type: `ArtifactTypeEntry.data_schema`
  is typed `{type: object}`, and only `ObjectTypeEntry.data_schema` carries the
  FR-073 `oneOf`. The module SHALL record that as a strict expected failure
  naming agent-ix/quoin#341 rather than assert a refusal the schema does not
  make.

Imports, cycles, and missing references:

- `semantic.imports` SHALL map each imported module reference
  (`^[a-z0-9][a-z0-9._-]*/[a-z0-9][a-z0-9._-]*$`) to that package's exact
  version, which is the only shape the FR-035 schema and the quire loader admit.
- The manifest SHALL NOT carry a per-package *type* list under
  `semantic.imports`; the contract has no place for one.
- The module SHALL declare, in `mappings.yaml` under `imported_types`, the types
  it references from each imported package. The contract amendment that would
  move them into the manifest is agent-ix/quoin#339.
- If a shipped skeleton, negative fixture, or `mappings.yaml` entry names an
  `ImportedTypeRef` whose `module` is absent from `semantic.imports`, or whose
  `type` is absent from that module's `imported_types` list, then the module's
  test suite SHALL fail naming the module and the type, and SHALL distinguish
  the two cases.
- If `semantic.imports` names a package that no `ImportedTypeRef` and no
  `composition.expected_artifacts` entry reaches, then the module's test suite
  SHALL fail naming the over-declared import, because an import nothing uses is
  a pin nobody can retire.
- If `semantic.imports` names this module's own `package`, then the module's
  test suite SHALL fail naming the self-import, because a module importing
  itself is the degenerate one-node cycle.
- The suite SHALL build the import graph from a fixed, committed set of module
  manifests: this module's own, plus dynamic-module fixtures synthesized into a
  temporary directory by the test. It SHALL NOT read the machine's installed
  Filament module root, because a graph whose nodes depend on what a developer
  happens to have installed is not reproducible (NFR-001).
- If the import graph contains a cycle, then the suite SHALL fail naming every
  module on the cycle in traversal order, starting from the lowest-sorting
  module on it so the reported order is deterministic. A cycle that does not
  reach this module SHALL be reported the same way; the check is a property of
  the graph, not of this module's position in it.
- The suite SHALL report a missing import, an over-declared import, and a cycle
  as three distinct diagnostics.
- The suite SHALL NOT report a cycle as a missing import.

Evidence, not obligation:

- Adding the `semantic` block and the `data_schema` references breaks no consumer
  that ignores them: the legacy-manifest fixture and the current manifest both
  validate under the same FR-035 schema and both load under quire with the same
  artifact types.
- Naming what a module load refused is not available at this engine: an unknown
  manifest key empties the model silently (agent-ix/quire-rs#221) and a
  `data_schema` digest mismatch drops the artifact type with no diagnostic
  (agent-ix/quire-rs#394). AC-6's "naming the key or the path" half is carried as
  an explicit expected failure naming those issues rather than worked around.
- Resolving a reference-form `data_schema` into a stored snapshot at activation
  is filament-core-service#23; until it lands the service stores the reference
  verbatim, which is what [IT-002](../integration/IT-002-module-load-and-extraction-roundtrip.md) asserts.

## Constraints

| ID | Constraint | Type | Validation |
|----|------------|------|------------|
| FR-003-CON-1 | The manifest SHALL add no new required key at the manifest root or on any artifact-type entry, so that a consumer that ignores the `semantic` block loads the module as before; the suite carries a legacy-manifest fixture that validates under the same FR-035 schema. | Compatibility | Test (TC-011) |
| FR-003-CON-2 | The manifest SHALL carry no inline `data_schema` object on any artifact type; the reference form is the only form. | Integrity | Test (TC-012) |
| FR-003-CON-3 | `semantic.imports` SHALL NOT name this module's own `package`. | Integrity | Test (TC-014) |

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-003-AC-1 | The manifest validates against the bundled FR-035 schema with the `semantic` block present, and the block's key set equals exactly `{contract_version, semantic_core, package, exports, imports, targets, mappings, compatibility_posture, legacy_forms}` with the values of Outputs. | Test (TC-011) |
| FR-003-AC-2 | For each exported artifact type, `data_schema.schema` names an existing file under `spec_artifacts_app/schemas/` per the FR-002 map, `data_schema.digest` equals `sha256:` plus the hex SHA-256 of that file's bytes, and `exports` equals the set of artifact types carrying a reference; a one-byte edit to any emitted schema without a digest refresh fails the suite naming the artifact type and both digests. | Test (TC-012) |
| FR-003-AC-3 | With the block and the references present, `quire.Registry.load_from` over the module's parent directory lists every archetype the manifest declares and `validate_document` passes every shipped skeleton — the block breaks no consumer. | Test (TC-013) |
| FR-003-AC-4 | `semantic.imports` names `agent-ix/spec-artifacts-iso` at an exact version and carries no type list; `mappings.yaml` `imported_types` names the types referenced from it; every `ImportedTypeRef` in a skeleton, a negative fixture, or `mappings.yaml` names a package the manifest pins and a type `imported_types` declares; an undeclared module, an undeclared type, an over-declared import, and a self-import each fail with their own distinct diagnostic. | Test (TC-014) |
| FR-003-AC-5 | An import graph built from this module plus synthesized dynamic-module fixtures fails on a cycle naming every module on it in deterministic traversal order, distinctly from the missing-import failure of AC-4; the fixtures exercise a two-module cycle, a three-module cycle, and an acyclic graph that must pass. No fixture is read from the machine's installed module root. | Test (TC-015) |
| FR-003-AC-6 | The bundled FR-035 schema rejects `semantic: {…, foo: 1}` naming `foo`, rejects `package: ix://agent-ix/x`, and rejects `targets: [go]`. Two halves of this criterion are expected failures rather than claims: the schema does **not** reject `data_schema: {schema: x.json, digest: sha256:…, type: object}` on an *artifact* type, because `ArtifactTypeEntry.data_schema` is typed `{type: object}` while only `ObjectTypeEntry.data_schema` carries the FR-073 `oneOf` (agent-ix/quoin#341); and no engine load names the refused key or the refused path (agent-ix/quire-rs#221, agent-ix/quire-rs#394). Each is recorded as a strict expected failure naming its issue. | Test (TC-016) |
| FR-003-AC-7 | The legacy-manifest fixture (no `semantic` block, no `data_schema`) validates under the bundled FR-035 schema and loads under quire with the same artifact types as the current manifest. | Test (TC-011) |
| FR-003-AC-8 | A copy of the module with one `data_schema.digest` altered by one hex digit is refused at load. Recorded as a strict expected failure naming agent-ix/quire-rs#394 until an engine that diagnoses the mismatch is published. | Test (TC-017) |

## Dependencies

- **Upstream**: [FR-001](./FR-001-module-manifest-activates.md) (the FR-035 gate), [FR-002](./FR-002-semantic-data-schemas.md) (the referenced files), quoin FR-070 and FR-073 (agent-ix/quoin#293), quire-rs FR-069 (agent-ix/quire-rs#388)
- **Blocked downstream**: `quoin module install` of this module cannot succeed once quoin's FR-070 reader ships, because it resolves `semantic.exports` and `data_schema` against `object_types` only and this module exports artifact types (agent-ix/quoin#336). The manifest keeps the exports as specified rather than bend to it; the amendment is quoin's.
- **Downstream**: [FR-004](./FR-004-markdown-mappings-and-imports.md), [IT-002](../integration/IT-002-module-load-and-extraction-roundtrip.md)
