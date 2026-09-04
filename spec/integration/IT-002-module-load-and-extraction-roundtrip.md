---
id: IT-002
title: "Module load and semantic extraction roundtrip against the Quire engine"
type: IT
relationships:
  - target: "ix://agent-ix/spec-artifacts-app/FR-003"
    type: "verifies"
  - target: "ix://agent-ix/spec-artifacts-app/FR-005"
    type: "verifies"
---
# IT-002: Module load and semantic extraction roundtrip

## Objective

Verify the integration boundary between this Module and the Quire engine: with
the `semantic` block and the reference-form `data_schema` values present, the
engine loads the Module with every declared artifact type, validates each shipped
skeleton, and extracts a semantic record from it — and the two known engine
defects that would otherwise hide a refusal are recorded as expected failures
rather than passed over. This exercises
[FR-003](../functional/FR-003-semantic-manifest-contract.md) AC-3 and AC-8 and
[FR-005](../functional/FR-005-executable-skeletons.md) AC-1.

## Target Integration

The system under test is the Quire engine consuming this Module. The integration
exercised is `quire.Registry.load_from` against the Module's parent directory,
followed by `validate_document` and `extract_semantic` over each shipped
skeleton, so that the Module's `body_extraction` asserts and its `semantic` block
drive load, validation, and extraction from one declaration.

## Preconditions

A quire wheel exposing `extract_semantic` is installed in the test environment
(`make dev-quire`; agent-ix/quire-rs#392 tracks publishing it to an index this
repository may commit against), and this Module's `spec_artifacts_app/` source
tree — manifest, schemas, skeletons, mappings — is present. When the wheel is
absent the rows **fail**; they never skip, because a skipped row is not coverage.

## Inputs

The Module source tree; each shipped skeleton under
`spec_artifacts_app/skeletons/`; the negative fixtures under
`tests/fixtures/negative/`; a copy of the Module whose `ApplicationSpec`
`data_schema.digest` is altered by one hex digit; and the legacy-manifest fixture
carrying neither the `semantic` block nor any `data_schema`.

## Test Procedure

Each step performs one discrete action and has its own success criterion.

1. Load the Module via `quire.Registry.load_from` over the Module's parent
   directory.
   - IT-002-SC-01: the Module loads with every artifact type the manifest
     declares registered.
2. Run `validate_document` over each shipped skeleton for its artifact type.
   - IT-002-SC-02: `is_valid == true` with no errors for every skeleton.
3. Run `extract_semantic` over each shipped skeleton and inspect the returned
   record.
   - IT-002-SC-03: a record is returned for every skeleton, and the Module's
     reference-form `data_schema` is reported verbatim rather than resolved into
     a stored snapshot (filament-core-service#23).
4. Load the legacy-manifest fixture, which carries neither the `semantic` block
   nor any `data_schema`.
   - IT-002-SC-04: the same artifact types are registered, so adding the block
     breaks no consumer that ignores it.
5. Load the copy whose `data_schema.digest` is altered by one hex digit.
   - IT-002-SC-05: the load is refused and the refusal names the artifact type
     and the path. Recorded as a strict expected failure naming
     agent-ix/quire-rs#394 (the digest mismatch drops the type with no
     diagnostic) and agent-ix/quire-rs#221 (an unknown manifest key empties the
     model silently).
6. Run `validate_document` and the FR-004 reference mapping over each negative
   fixture.
   - IT-002-SC-06: each fixture is refused by the check its `expect` frontmatter
     names, and no fixture is accepted.

## Expected Results

The Module loads with every declared artifact type; every skeleton validates and
extracts; the legacy-manifest fixture registers the same artifact types; every
negative fixture is refused by the check it names; and the digest-mismatch
refusal of step 5 is reported as a strict expected failure naming its blocking
issues, so the arrival of an engine that diagnoses it is announced by the gate
itself rather than discovered later.

## Metadata

- Priority: High
- Target Integration: Quire engine module loader, validator, and semantic
  extraction surface
- Automation: Automated, except step 5 which is a strict expected failure until
  agent-ix/quire-rs#394 lands

## Acceptance Criteria

| ID | Criteria |
|----|----------|
| IT-002-AC-1 | Steps 1-4 pass with the `semantic` block and the `data_schema` references present |
| IT-002-AC-2 | Step 5 is recorded as a strict expected failure naming agent-ix/quire-rs#394 — never a skip and never a silent pass |
| IT-002-AC-3 | Step 6 refuses every negative fixture by the check its `expect` frontmatter names |

## Dependencies

**Upstream**: [FR-003](../functional/FR-003-semantic-manifest-contract.md) and
[FR-005](../functional/FR-005-executable-skeletons.md), whose criteria this test
discharges at the engine boundary. **Downstream**: none.

## Traceability

This integration test verifies the manifest semantic contract and the executable
skeletons, and exercises the stakeholder need for application composite specs
that consumers can read consistently.
