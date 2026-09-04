---
id: FR-004
title: "Markdown mappings and imported-type references for the application records"
type: FR
relationships:
  - target: "ix://agent-ix/spec-artifacts-app/US-001"
    type: "implements"
  - target: "ix://agent-ix/spec-artifacts-app/FR-002"
    type: "depends_on"
  - target: "ix://agent-ix/quoin/FR-071"
    type: "uses"
  - target: "ix://agent-ix/quoin/FR-072"
    type: "uses"
---
# FR-004: Markdown mappings and imported-type references for the application records

## Description

The module SHALL publish, for every [FR-002](./FR-002-semantic-data-schemas.md)
model, a machine-readable mapping from the authored Markdown to each field of the
record.

Every structured section of an application artifact SHALL carry either a typed
mapping entry or an explicit prose-only designation, so that no section is left
undeclared.

The mapping SHALL declare the round-trip policy: Markdown is the sole authority
and the record is a derived projection, so that every consumer builds the same
record from the same document.

## Inputs

- `spec_artifacts_app/mappings.yaml`: per model, the authority and round-trip
  policy, the frontmatter keys the mapping drops, and per property the mapping
  kind, its source, and the cell-level parse rule the kind applies.
- `spec_artifacts_app/mappings.schema.json`: the JSON Schema `mappings.yaml`
  itself validates against, so a malformed mapping is a schema error rather than
  a reader's surprise.
- The shipped skeletons of [FR-005](./FR-005-executable-skeletons.md).
- The emitted schemas of [FR-002](./FR-002-semantic-data-schemas.md), which fix
  the property set every mapping entry must name.
- The `semantic.imports` block of
  [FR-003](./FR-003-semantic-manifest-contract.md), which fixes the modules and
  types an `ImportedTypeRef` may name.
- The quoin mapping conventions for typed tables and clauses (quoin FR-071,
  FR-072) and the quire-rs extraction semantics for section content (quire-rs
  FR-008: byte-exact slices).

## Outputs

- `spec_artifacts_app/mappings.yaml` and
  `spec_artifacts_app/mappings.schema.json`, both shipped with the module in the
  sdist, the wheel, and the npm payload.
- A reference mapping implementation in the module's test support (Python), used
  by the suite to build records from Markdown. It is a test oracle, not module
  code; the module ships data only.

## Behavior

Mapping kinds:

- The mapping SHALL use exactly the six mapping kinds the manifest declares —
  `frontmatter`, `section`, `typed-table`, `sysml-fence`, `ocl-clause`, and
  `provenance`.
- A `frontmatter` mapping SHALL name a frontmatter key path and the record
  property it fills (`id`, `title`, `type`, `status`, `relationships`).
- A `frontmatter` mapping SHALL drop every frontmatter key it does not name, and
  `mappings.yaml` SHALL record the dropped key set per model, so the loss is
  declared rather than silent.
- A `section` mapping SHALL name a level-2 heading and fill a `Section` property
  with the heading's byte-exact content and its 1-based start and end lines.
- A `section` mapping that fills no typed property SHALL carry `prose_only: true`
  and a reason, which is the explicit designation a structured section takes when
  it has no typed form.
- A `typed-table` mapping SHALL name a section and a column list equal to the
  `assert.columns` of the corresponding locator, and fill an array with one
  object per data row in authored order, cells trimmed of leading and trailing
  whitespace (`\r` included), with the row's 1-based line on each row.
- A `typed-table` mapping SHALL parse an id cell into the row `id`, a
  verification cell into `Verification { method, testRefs, annotation? }`, an
  `<org>/<repo>#<Type>` cell into an `ImportedTypeRef { module, type }`, and a
  comma-separated id cell into the row's id list.
- For a verification cell `<method> (<annotation>)`, the mapping SHALL set
  `method` to the text before the first `(` trimmed, `annotation` to the text
  between the first `(` and the last `)` verbatim, and `testRefs` to the
  `TC-[0-9]+` tokens found in `annotation`, in order; for a cell without
  parentheses the mapping SHALL set `method` alone with `testRefs: []` and no
  `annotation`. The mapping SHALL drop no byte of the cell.
- A `sysml-fence` mapping SHALL fill the same property a `typed-table` mapping
  fills, from a single fenced block tagged `sysml` under the same heading, so
  that the two forms are alternates of one declaration.
- If one section carries both a typed table and a `sysml` fence, then the mapping
  SHALL fail naming the section's heading line, because one artifact carries one
  form.
- An `ocl-clause` mapping SHALL map each `### <clauseId>` heading under
  `## Invariants` that owns exactly one fenced block tagged `ocl` to a
  semantic-core `ClauseRef { language: ocl, clauseId, sourceSpan? }`.
- The mapping SHALL carry the clause text verbatim beside the record, in the
  sidecar array `invariantsText`, one entry per `ClauseRef` in the same order,
  each recording the fence's `startLine`, `endLine`, and body bytes. The record
  itself never carries the clause text, and no code in this module parses it.
- The mapping SHALL emit `sourceSpan` only when the caller supplies a
  `sourceIdentity`, because semantic-core `SourceLocus` requires
  `sourceIdentity`, `path`, `startLine`, and `startColumn`.
- If a `## Invariants` section carries no fenced block, then the mapping SHALL
  leave `invariants` absent and SHALL NOT fail.
- If a `### <clauseId>` heading is not an `Identifier`
  (`^[A-Za-z_][A-Za-z0-9_]*$`), owns a fence tagged with another language, owns
  more than one fence, owns an unterminated fence, or repeats a `clauseId`
  already used in the same document, then the mapping SHALL fail naming the line.
- If a fenced `ocl` block under `## Invariants` is owned by no `###` heading,
  then the mapping SHALL fail naming the fence's opening line.
- A `provenance` mapping SHALL fill `provenance.path` from the document's
  corpus-relative path and `provenance.digest` from the document bytes as read,
  with no line-ending normalization; it SHALL fill `provenance.sourceIdentity`
  from the caller and SHALL leave it absent when the caller supplies none, and
  SHALL NOT synthesize one.

Imported types:

- Where a cell is mapped to an `ImportedTypeRef`, the author SHALL write it as
  `<org>/<repo>#<Type>`, the mapping SHALL split it into `module` and `type`, and
  the mapping SHALL NOT copy any field of the imported type into the record.
- If a cell mapped to an `ImportedTypeRef` names a module or a type that
  `semantic.imports` does not declare, then the mapping SHALL fail naming the
  line, the module, and the type.

Failure discipline:

- If a document carries a typed-table row whose id does not match the locator's
  `id_pattern`, a row id repeated within one table, a heading the mapping names
  twice, or a `requirements` row whose `target` is not an `ix://` identity, then
  the mapping SHALL fail naming the line.
- The mapping SHALL report every such failure it finds in one pass, not only the
  first, and SHALL emit no record when any failure is found.
- The mapping SHALL NOT validate the record against the model; the suite reports
  a mapping failure and a schema failure separately.

Round-trip policy:

- `mappings.yaml` SHALL record `authority: markdown` and `round_trip: derived`
  per model.
- `mappings.yaml` SHALL record `lossless: true` on `section` and `ocl-clause`
  properties, whose text is the byte-exact slice.
- `mappings.yaml` SHALL record `lossless: false` on `typed-table`,
  `sysml-fence`, and `frontmatter` properties, because cell whitespace, column
  alignment, fence formatting, and the order of frontmatter keys are not
  preserved.
- The module SHALL contain no code that derives Markdown from a record, so
  nothing in this module can present a record as the authority.

## Constraints

| ID | Constraint | Type | Validation |
|----|------------|------|------------|
| FR-004-CON-1 | The mapping SHALL keep every existing heading and column order the corpus already uses; the forms it adds are the optional sections FR-005 introduces. | Compatibility | Test (TC-018) |
| FR-004-CON-2 | The mapping SHALL carry clause text under `## Invariants` as opaque bytes; no code in this module tokenizes, typechecks, or evaluates it. | Boundary | Test (TC-019) |
| FR-004-CON-3 | The mapping SHALL read Markdown and write nothing back; no file in the module derives Markdown from a record. | Boundary | Inspection (TC-020) |

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-004-AC-1 | `mappings.yaml` validates against `mappings.schema.json`, declares every property of both exported models exactly once, names no undeclared property, uses only the six mapping kinds the manifest lists, and each `typed-table` column list equals the locator's `assert.columns`. | Test (TC-021) |
| FR-004-AC-2 | Every level-2 section of every shipped skeleton is named by a mapping entry that either fills a typed property or carries `prose_only: true` with a reason; a section named by neither fails the suite naming the heading. | Test (TC-022) |
| FR-004-AC-3 | For each shipped skeleton the reference mapping produces a record that validates against its model's schema, and the `## Capabilities`, `## Actors`, `## Interfaces`, `## Data Dependencies`, `## UI Rendering Requirements`, and `## Requirements` rows map to the typed row objects FR-002 declares, `Test (TC-001)` splitting into `method: Test`, `annotation: TC-001`, `testRefs: [TC-001]`. | Test (TC-023) |
| FR-004-AC-4 | An `<org>/<repo>#<Type>` cell maps to an `ImportedTypeRef` carrying exactly `module` and `type`, no field of the imported type appears in the record, and a cell naming a module or a type absent from `semantic.imports` fails naming the line, the module, and the type. | Test (TC-024) |
| FR-004-AC-5 | The `## Invariants` clause of the `ApplicationSpec` skeleton maps to a `ClauseRef` with `language: ocl` and `clauseId` equal to the `###` heading; with a caller-supplied `sourceIdentity` it also carries a `sourceSpan` whose `startLine`/`endLine` are the fence lines, and without one it carries no `sourceSpan`; the `invariantsText` entry equals the fence body byte-for-byte; a `### not-an-identifier` heading, a `tla`-tagged fence, a second fence under one heading, a repeated `clauseId`, and a fence owned by no `###` heading each fail naming the line; a prose `## Invariants` with no fence leaves `invariants` absent and does not fail. | Test (TC-019) |
| FR-004-AC-6 | A row id with the wrong prefix, a row id repeated in one table, a duplicated level-2 heading, a `requirements` row whose `target` is not `ix://`, and a section carrying both a typed table and a `sysml` fence each fail the mapping naming the line and yield no record, and all failures present in one document are reported together. | Test (TC-025) |
| FR-004-AC-7 | `section` and `ocl-clause` properties carry `lossless: true` and `typed-table`, `sysml-fence`, and `frontmatter` properties carry `lossless: false` in `mappings.yaml`; every model records `authority: markdown` and `round_trip: derived`; and every model records the frontmatter keys its mapping drops. | Test (TC-021) |
| FR-004-AC-8 | The `ApplicationSpec` document committed in this repository before this change (`spec/spec.md` at the branch point) maps to a record that validates against the new schema, so an existing valid application spec remains readable. | Test (TC-018) |

## Dependencies

- **Upstream**: [FR-002](./FR-002-semantic-data-schemas.md), [FR-003](./FR-003-semantic-manifest-contract.md) (the declared imports), [FR-005](./FR-005-executable-skeletons.md) (the locators and skeletons), quoin FR-071/FR-072, quire-rs FR-008
- **Downstream**: agent-ix/quire-contract-ir#52, agent-ix/filament-core-data#36
