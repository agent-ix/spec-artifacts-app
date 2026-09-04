---
id: FR-005
title: "Skeletons are executable typed fixtures with negative counterparts"
type: FR
relationships:
  - target: "ix://agent-ix/spec-artifacts-app/US-001"
    type: "implements"
  - target: "ix://agent-ix/spec-artifacts-app/FR-002"
    type: "depends_on"
  - target: "ix://agent-ix/quoin/FR-071"
    type: "implements"
  - target: "ix://agent-ix/quoin/FR-072"
    type: "implements"
---
# FR-005: Skeletons are executable typed fixtures with negative counterparts

## Description

The module SHALL ship, for each declared artifact type, an authoring skeleton
that is a conformant fixture: it validates against the artifact type's
`body_extraction` locators, maps to a record under
[FR-004](./FR-004-markdown-mappings-and-imports.md), and that record validates
against the artifact type's emitted schema.

Each skeleton SHALL author its typed declarations in the typed `## Properties`
table form (`Field | Type | Multiplicity | Constraints`) as the default, with a
a `sysml`-tagged fence shown as the alternate form of the same declarations in
a separate file, and its clauses as `ocl`-tagged fences under `## Invariants`.

The module SHALL ship, for each rule a skeleton demonstrates, a negative
counterpart fixture that violates exactly that rule and declares in its
frontmatter what it expects to be refused and why.

## Inputs

- The artifact types declared by `spec_artifacts_app/manifest.yaml`
  (`ApplicationSpec`, `MasterRequirements`).
- The emitted models of [FR-002](./FR-002-semantic-data-schemas.md).
- The quoin `Properties` / `Invariants` conventions (quoin FR-071, FR-072).
- `spec/spec.md` as committed at the branch point, the one existing
  `ApplicationSpec` document in this repository, which the added locators must
  keep admitting.

## Outputs

- `spec_artifacts_app/skeletons/application-spec.md` and
  `spec_artifacts_app/skeletons/master-requirements.md`, the typed-table form.
- `spec_artifacts_app/skeletons/application-spec.sysml.md`, the alternate
  `sysml`-fence form of the same declarations.
- `body_extraction` locators on both artifact types, added to a manifest that
  today declares none. On both types: `title` (H1) and `purpose` (`## Purpose`)
  required, and `scope`, `system_overview`, `structure`, `properties_table`,
  `properties_fence`, `requirements_table`, and `invariants` optional. On
  `ApplicationSpec` only, and all optional: `boundaries_table`,
  `capabilities_table`, `actors_table`, `interfaces_table`,
  `data_dependencies_table`, and `rendering_requirements_table` — a
  `MasterRequirements` document describes no running system, so it declares
  none of them.
- Negative fixtures under `tests/fixtures/negative/`, one per demonstrated rule.
- `spec/spec.md` extended to author the sections the skeleton demonstrates, so
  that this repository's own application spec is an instance of the contract it
  publishes.

## Behavior

- Every added locator SHALL be `required: false` except `title` and `purpose`,
  which the existing document already carries, so that an application spec valid
  before this change stays valid after it.
- Each skeleton SHALL carry frontmatter satisfying its artifact type's
  `frontmatter_schema_ref`, including `id` matching `^[A-Z]{2,4}-[0-9]+$` and
  `type` equal to the artifact-type name.
- Each skeleton's `## Properties` table SHALL use the header row
  `Field | Type | Multiplicity | Constraints` exactly, and each domain table
  (`## Capabilities`, `## Actors`, `## Interfaces`, `## Data Dependencies`,
  `## UI Rendering Requirements`, `## Requirements`, `## Boundaries`) SHALL use
  the header row the locator's `assert.columns` declares.
- Each skeleton SHALL carry at least one `### <clauseId>` heading under
  `## Invariants`, each owning exactly one `ocl`-tagged fence.
- The `sysml`-fence skeleton SHALL declare the same fields as its typed-table
  counterpart, in the same order, so that the two forms are provably alternates.
- One artifact SHALL carry one form; the alternate is a separate file, never a
  second block in the same artifact.
- Each negative fixture SHALL declare, in frontmatter, `expect` (the diagnostic
  it is authored to provoke) and `because` (the rule it violates), and SHALL
  violate exactly that one rule.
- If a negative fixture is accepted by the check it names, then the suite SHALL
  fail naming the fixture and the expectation, because a negative fixture that
  passes is a gate that is not gating.
- The skeleton set and the locator set SHALL agree in both directions: every
  asserted heading exists in the skeleton at the asserted level, every asserted
  table's header row is present in the skeleton, and every level-2 heading of the
  skeleton is either asserted or declared prose-only in `mappings.yaml`.

## Constraints

| ID | Constraint | Type | Validation |
|----|------------|------|------------|
| FR-005-CON-1 | Every locator added by this change SHALL be optional, except `title` and `purpose`, which the pre-change document already carries. | Compatibility | Test (TC-018) |
| FR-005-CON-2 | A negative fixture SHALL violate exactly one rule, so that a refusal identifies the rule. | Integrity | Test (TC-026) |
| FR-005-CON-3 | The module SHALL ship no `.md.j2` template and no `template_ref`; skeletons are the authoring source. | Scope | Test (TC-027) |

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-005-AC-1 | Each declared artifact type ships a skeleton under `spec_artifacts_app/skeletons/` whose headings and table header rows match its `body_extraction` asserts in both directions, and every skeleton passes `validate_document` for its artifact type. | Test (TC-028) |
| FR-005-AC-2 | The `application-spec.sysml.md` skeleton declares the same field set, in the same order, as the typed `## Properties` table of `application-spec.md`, and both map to the same typed rows under FR-004. | Test (TC-029) |
| FR-005-AC-3 | Each skeleton carries at least one `### <clauseId>` heading under `## Invariants` owning exactly one `ocl`-tagged fence, and the record built from it carries one `ClauseRef` per heading. | Test (TC-019) |
| FR-005-AC-4 | Each negative fixture declares `expect` and `because` in frontmatter, is refused by the check it names, and the refusal names the rule; a negative fixture that is accepted fails the suite naming the fixture and the expectation. | Test (TC-026) |
| FR-005-AC-5 | The `ApplicationSpec` locators added by this change are all optional except `title` and `purpose`, and `spec/spec.md` as committed at the branch point validates unchanged under the new manifest. | Test (TC-018) |
| FR-005-AC-6 | The module ships no file matching `*.md.j2` and no `template_ref` key anywhere in `manifest.yaml`. | Test (TC-027) |
| FR-005-AC-7 | The negative fixture set covers, one fixture each: a missing required section, a typed table with a wrong column header, a row id with the wrong prefix, a row id repeated in one table, a section carrying both a typed table and a `sysml` fence, an `ImportedTypeRef` naming an undeclared module, a `### <clauseId>` heading owning two fences, and an `ocl` fence owned by no `###` heading. | Test (TC-026) |

## Dependencies

- **Upstream**: [FR-002](./FR-002-semantic-data-schemas.md), [FR-004](./FR-004-markdown-mappings-and-imports.md), quoin FR-071/FR-072
- **Downstream**: [IT-002](../integration/IT-002-module-load-and-extraction-roundtrip.md), agent-ix/quire-contract-ir#52
