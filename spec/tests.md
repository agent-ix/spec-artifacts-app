---
id: TM-001
title: "Test Matrix"
type: TestMatrix
---
# Test Matrix

## Overview

Maps every acceptance criterion, constraint, and NFR metric of this
specification to the test that backs it.

**What the numbers count.** The `Coverage Status` column counts *criteria* — an
`FR-XXX-AC-N` row, an `FR-XXX-CON-N` row, an `IT-XXX-AC-N` row, an
`StR-XXX-VC-N` row, or one `Metric | Target | Threshold | Method` row of the NFR.
It does not count tests: one test case may back several criteria and one
criterion may take several. The `Test Case Summary` counts *test cases* — one row
per `TC-NNN`, each of which binds to exactly one test symbol through a
`@pytest.mark.trace` marker. The two totals are therefore different numbers of
different things, and `quire coverage` counts a third: written trace tags that
bind to a symbol.

**Rows that cannot be green in this repository.** Nine rows are marked `🚧` and
say why rather than being quietly dropped:

- `FR-001-AC-2`, `FR-001-AC-3`, `FR-001-AC-4`, `IT-001-AC-1`, `IT-001-AC-2`,
  `StR-001-VC-1` need a running `filament-core-service` to activate against;
  this package's suite runs no cluster.
- `StR-001-VC-2` is a `minijinja-cli` demonstration against a generated artifact
  and is likewise not run here.
- `NFR-001` metric 2 is the offline, no-network run; it is a manual gate of this
  repository recorded in the release notes, and no CI job is claimed for it.
- `FR-003-AC-8` / `IT-002-AC-2` (TC-017) is a **strict expected failure**, never
  a skip and never a silent pass: it asserts that a one-hex-digit `data_schema`
  digest edit is refused at load, which no published engine diagnoses
  (agent-ix/quire-rs#394, and agent-ix/quire-rs#221 for the sibling
  silent-empty-model defect). A strict expected failure that starts passing fails
  the suite, so the arrival of a fixed engine is announced by the gate itself.

An NFR has no `-AC-` ids — its criteria are its `Metric | Target | Threshold |
Method` rows — so its rows trace to `NFR-001 (metric n)`.

## Requirements Traceability

### Functional Requirement Coverage

| Functional Req | Acceptance Criteria | Test Cases | Coverage Status |
|----------------|---------------------|------------|-----------------|
| FR-001 | FR-001-AC-1 | TC-036 | ✅ Complete |
| FR-001 | FR-001-AC-2 | — | 🚧 Needs a running filament-core-service |
| FR-001 | FR-001-AC-3 | — | 🚧 Needs a running filament-core-service |
| FR-001 | FR-001-AC-4 | — | 🚧 Needs a running filament-core-service |
| FR-002 | FR-002-AC-1 | TC-003 | ✅ Complete |
| FR-002 | FR-002-AC-2 | TC-007 | ✅ Complete |
| FR-002 | FR-002-AC-3 | TC-003 | ✅ Complete |
| FR-002 | FR-002-AC-4 | TC-002 | ✅ Complete |
| FR-002 | FR-002-AC-5 | TC-008 | ✅ Complete |
| FR-002 | FR-002-AC-6 | TC-005 | ✅ Complete |
| FR-002 | FR-002-AC-7 | TC-007 | ✅ Complete |
| FR-002 | FR-002-AC-8 | TC-009 | ✅ Complete |
| FR-002 | FR-002-AC-9 | TC-006 | ✅ Complete |
| FR-002 | FR-002-AC-10 | TC-010 | ✅ Complete |
| FR-002 | FR-002-AC-11 | TC-004 | ✅ Complete |
| FR-002 | FR-002-CON-1 | TC-001, TC-002 | ✅ Complete |
| FR-002 | FR-002-CON-2 | TC-003 | ✅ Complete |
| FR-002 | FR-002-CON-3 | TC-004 | ✅ Complete |
| FR-002 | FR-002-CON-4 | TC-005 | ✅ Complete |
| FR-002 | FR-002-CON-5 | TC-006 | ✅ Complete |
| FR-003 | FR-003-AC-1 | TC-011 | ✅ Complete |
| FR-003 | FR-003-AC-2 | TC-012 | ✅ Complete |
| FR-003 | FR-003-AC-3 | TC-013 | ✅ Complete |
| FR-003 | FR-003-AC-4 | TC-014 | ✅ Complete |
| FR-003 | FR-003-AC-5 | TC-015 | ✅ Complete |
| FR-003 | FR-003-AC-6 | TC-016 | ✅ Complete |
| FR-003 | FR-003-AC-7 | TC-011 | ✅ Complete |
| FR-003 | FR-003-AC-8 | TC-017 | 🚧 Strict expected failure (agent-ix/quire-rs#394) |
| FR-003 | FR-003-CON-1 | TC-011 | ✅ Complete |
| FR-003 | FR-003-CON-2 | TC-012 | ✅ Complete |
| FR-003 | FR-003-CON-3 | TC-014 | ✅ Complete |
| FR-004 | FR-004-AC-1 | TC-021 | ✅ Complete |
| FR-004 | FR-004-AC-2 | TC-022 | ✅ Complete |
| FR-004 | FR-004-AC-3 | TC-023 | ✅ Complete |
| FR-004 | FR-004-AC-4 | TC-024 | ✅ Complete |
| FR-004 | FR-004-AC-5 | TC-019 | ✅ Complete |
| FR-004 | FR-004-AC-6 | TC-025 | ✅ Complete |
| FR-004 | FR-004-AC-7 | TC-021 | ✅ Complete |
| FR-004 | FR-004-AC-8 | TC-018 | ✅ Complete |
| FR-004 | FR-004-CON-1 | TC-018 | ✅ Complete |
| FR-004 | FR-004-CON-2 | TC-019 | ✅ Complete |
| FR-004 | FR-004-CON-3 | TC-020 | ✅ Complete |
| FR-005 | FR-005-AC-1 | TC-028 | ✅ Complete |
| FR-005 | FR-005-AC-2 | TC-029 | ✅ Complete |
| FR-005 | FR-005-AC-3 | TC-019 | ✅ Complete |
| FR-005 | FR-005-AC-4 | TC-026 | ✅ Complete |
| FR-005 | FR-005-AC-5 | TC-018 | ✅ Complete |
| FR-005 | FR-005-AC-6 | TC-027 | ✅ Complete |
| FR-005 | FR-005-AC-7 | TC-026 | ✅ Complete |
| FR-005 | FR-005-CON-1 | TC-018 | ✅ Complete |
| FR-005 | FR-005-CON-2 | TC-026 | ✅ Complete |
| FR-005 | FR-005-CON-3 | TC-027 | ✅ Complete |

### Non-Functional Requirement Coverage

| Non-Functional Req | Verification Method | Evidence/Test Cases | Status |
|--------------------|---------------------|---------------------|--------|
| NFR-001 | Snapshot (metric 1: byte differences between two `make schemas` runs) | TC-030 | ✅ Complete |
| NFR-001 | Manual (metric 2: network reads during `make schemas-check` and `make test`) | TC-031 | 🚧 Manual offline gate, no CI job claimed |
| NFR-001 | Static (metric 3: locators added by this change that are required) | TC-032 | ✅ Complete |
| NFR-001 | Benchmark (metric 4: wall time of `make schemas-check`) | TC-033 | ✅ Complete |

### Stakeholder and Integration Coverage

| Requirement | Criteria | Test Cases | Coverage Status |
|-------------|----------|------------|-----------------|
| StR-001 | StR-001-VC-1 | — | 🚧 Needs a running filament-core-service |
| StR-001 | StR-001-VC-2 | — | 🚧 minijinja-cli demonstration, not run in this package |
| IT-001 | IT-001-AC-1 | — | 🚧 Needs a running filament-core-service |
| IT-001 | IT-001-AC-2 | — | 🚧 Needs a running filament-core-service |
| IT-002 | IT-002-AC-1 | TC-034 | ✅ Complete |
| IT-002 | IT-002-AC-2 | TC-017 | 🚧 Strict expected failure (agent-ix/quire-rs#394) |
| IT-002 | IT-002-AC-3 | TC-035 | ✅ Complete |

## Integration Test Matrix

| Purpose | Target | Type | Test Cases |
|---------|--------|------|------------|
| Activate the manifest and read back every contribution | filament-core-service HTTP module API | service | — (🚧 needs a running service) |
| Load the module, validate and extract every skeleton | Quire engine (`Registry.load_from`, `validate_document`, `extract_semantic`) | service | TC-013, TC-034, TC-035 |
| Refuse a module whose `data_schema` digest is altered | Quire engine loader | service | TC-017 |

## Test Case Summary

| Test ID | Title | Type | Priority | Traces To | Status |
|---------|-------|------|----------|-----------|--------|
| TC-001 | Every locator output of every artifact type is a property of its model, and every model property traces to a locator, a frontmatter key, or a `mappings.yaml` entry | Unit | P0 | FR-002-CON-1 | ✅ |
| TC-002 | Every property of every emitted object schema is constrained, or its description carries `free text:` and a reason and its name is in the closed free-text list | Unit | P0 | FR-002-AC-4, FR-002-CON-1 | ✅ |
| TC-003 | Both exported schemas exist with the 2020-12 `$schema` and the versioned `$id`, each `type` `const` equals its artifact-type name, and every `$ref` in the bundle resolves offline to a shipped sibling or to semantic-core 0.1.0 | Unit | P0 | FR-002-AC-1, FR-002-AC-3, FR-002-CON-2 | ✅ |
| TC-004 | The repository carries no `.npmrc`, pins the compiler, emitter, and semantic-core exactly, commits the lockfile, and uses no `file:`/`link:` specifier | Static | P1 | FR-002-AC-11, FR-002-CON-3 | ✅ |
| TC-005 | No emitted property is a runtime-state field and `ApplicationSpec.json`'s description says runtime state is not modelled | Static | P1 | FR-002-AC-6, FR-002-CON-4 | ✅ |
| TC-006 | A `@jsonSchema` base whose version differs from the manifest `version` makes `make schemas` exit non-zero naming both values and write no file | Integration | P0 | FR-002-AC-9, FR-002-CON-5 | ✅ |
| TC-007 | The emitted schema file set equals `toolchain.json`'s `files`, covers every declared artifact type and every named support model and scalar, and the recomputed digest equals the recorded one with no toolchain run | Unit | P0 | FR-002-AC-2, FR-002-AC-7 | ✅ |
| TC-008 | `make schemas-check` exits 0 on the committed tree and non-zero naming the file after a one-byte edit to an emitted schema | Integration | P0 | FR-002-AC-5 | ✅ |
| TC-009 | Every emitted object schema declares its properties inline, and the Python `jsonschema` validator accepts every skeleton record and rejects every negative fixture that produces a record | Unit | P0 | FR-002-AC-8 | ✅ |
| TC-010 | No emitted property duplicates a property of an imported type and no `$ref` names a base other than this module's or semantic-core 0.1.0 | Unit | P0 | FR-002-AC-10 | ✅ |
| TC-011 | The manifest validates under the bundled FR-035 schema with the `semantic` block, whose key set is exactly the nine declared keys; the block adds no required key; and the legacy-manifest fixture validates under the same schema and loads with the same artifact types | Unit | P0 | FR-003-AC-1, FR-003-AC-7, FR-003-CON-1 | ✅ |
| TC-012 | Every exported artifact type carries a `{schema, digest}` reference to an existing file whose SHA-256 equals the digest, `exports` equals the referencing set, no inline `data_schema` remains, and a one-byte schema edit fails naming the type and both digests | Unit | P0 | FR-003-AC-2, FR-003-CON-2 | ✅ |
| TC-013 | `Registry.load_from` lists every declared artifact type with the `semantic` block and the `data_schema` references present, and `validate_document` passes every shipped skeleton | Integration | P0 | FR-003-AC-3 | ✅ |
| TC-014 | `semantic.imports` names the imported modules and types, every `ImportedTypeRef` in a skeleton, fixture, or mapping names a declared module and type, an undeclared module and an undeclared type each fail naming both values, and a self-import fails | Unit | P0 | FR-003-AC-4, FR-003-CON-3 | ✅ |
| TC-015 | A two-module and a three-module import cycle each fail naming every module on the cycle in traversal order, distinctly from the missing-import diagnostic | Unit | P0 | FR-003-AC-5 | ✅ |
| TC-016 | The bundled FR-035 schema rejects an unknown `semantic` key naming it, an ambiguous `data_schema`, a non-`<org>/<repo>` package, and an unregistered `targets` value | Unit | P0 | FR-003-AC-6 | ✅ |
| TC-017 | A module copy with one `data_schema.digest` altered by one hex digit is refused at load — strict expected failure until an engine diagnosing it is published (agent-ix/quire-rs#394) | Integration | P0 | FR-003-AC-8, IT-002-AC-2 | 🚧 Strict expected failure |
| TC-018 | Every locator added by this change is optional except `title` and `purpose`; the pre-change `spec/spec.md` validates unchanged and maps to a record that validates against the new schema | Snapshot | P0 | FR-004-AC-8, FR-004-CON-1, FR-005-AC-5, FR-005-CON-1 | ✅ |
| TC-019 | The `## Invariants` clause maps to a `ClauseRef` with `sourceSpan` only when a `sourceIdentity` is supplied, the `invariantsText` entry equals the fence bytes, five malformed clause forms each fail naming the line, a prose `## Invariants` leaves `invariants` absent, and no module code parses the clause | Unit | P0 | FR-004-AC-5, FR-004-CON-2, FR-005-AC-3 | ✅ |
| TC-020 | No file in the module or its test support writes a Markdown document, and the reference mapping opens every document read-only — enumerated over the tree, not sampled | Static | P2 | FR-004-CON-3 | ✅ |
| TC-021 | `mappings.yaml` validates against `mappings.schema.json`, names every model property exactly once with one of the six mapping kinds, names no undeclared property, matches locator `assert.columns`, and records `authority`, `round_trip`, per-property `lossless`, and the dropped frontmatter keys | Unit | P0 | FR-004-AC-1, FR-004-AC-7 | ✅ |
| TC-022 | Every level-2 section of every shipped skeleton is named by a mapping entry that fills a typed property or carries `prose_only: true` with a reason; a section named by neither fails naming the heading | Unit | P0 | FR-004-AC-2 | ✅ |
| TC-023 | Each skeleton maps to a record that validates against its model, and the six domain tables map to the typed row objects, `Test (TC-001)` splitting into method, annotation, and testRefs | Snapshot | P0 | FR-004-AC-3 | ✅ |
| TC-024 | An `<org>/<repo>#<Type>` cell maps to an `ImportedTypeRef` of exactly `module` and `type`, no imported field appears in the record, and an undeclared module or type fails naming the line, the module, and the type | Unit | P0 | FR-004-AC-4 | ✅ |
| TC-025 | A wrong-prefix row id, a row id repeated in one table, a duplicated H2, a non-`ix://` requirement target, and a section carrying both a table and a `sysml` fence each fail naming the line, all failures in one document are reported together, and no partial record is emitted | Unit | P0 | FR-004-AC-6 | ✅ |
| TC-026 | Every negative fixture declares `expect` and `because`, violates exactly one rule, is refused by the check it names, and the eight enumerated rules each have a fixture; an accepted fixture fails naming the fixture and the expectation | Unit | P0 | FR-005-AC-4, FR-005-AC-7, FR-005-CON-2 | ✅ |
| TC-027 | The module ships no `*.md.j2` file and no `template_ref` key anywhere in `manifest.yaml` | Static | P1 | FR-005-AC-6, FR-005-CON-3 | ✅ |
| TC-028 | Each artifact type ships a skeleton whose headings and table header rows match its asserts in both directions, and every skeleton passes `validate_document` | Unit | P0 | FR-005-AC-1 | ✅ |
| TC-029 | The `sysml`-fence skeleton declares the same field set in the same order as the typed-table skeleton, and both map to the same typed rows | Unit | P0 | FR-005-AC-2 | ✅ |
| TC-030 | Two consecutive `make schemas` runs on one tree produce byte-identical schemas, `toolchain.json`, and manifest digests | Snapshot | P1 | NFR-001 (metric 1) | ✅ |
| TC-031 | `make schemas-check` and `make test` exit 0 with the network namespace disabled after `npm ci`, `poetry install`, and `make dev-quire` | Manual | P2 | NFR-001 (metric 2) | 🚧 Manual offline gate |
| TC-032 | Every locator the change adds carries `required: false`, diffed against the branch point | Static | P1 | NFR-001 (metric 3) | ✅ |
| TC-033 | `make schemas-check` completes within 30 s on the reference machine | Benchmark | P3 | NFR-001 (metric 4) | ✅ |
| TC-034 | The module loads with every declared artifact type, every skeleton validates and extracts a record, the reference-form `data_schema` is reported verbatim, and the legacy-manifest fixture registers the same artifact types | Integration | P0 | IT-002-AC-1 | ✅ |
| TC-035 | `validate_document` and the reference mapping refuse every negative fixture by the check its `expect` frontmatter names | Integration | P0 | IT-002-AC-3 | ✅ |
| TC-036 | The manifest validates against the bundled FR-035 schema; neither the missing-library nor the missing-schema branch skips | Unit | P0 | FR-001-AC-1 | ✅ |
