---
id: IT-001
title: "Manifest activation roundtrip against filament-core"
type: IT
relationships:
  - target: "ix://agent-ix/spec-artifacts-app/FR-001"
    type: "verifies"
---
# [IT-001] Manifest activation roundtrip

## Objective

Verify the integration boundary between this Module's manifest and a clean
filament-core-service instance: activating `spec_artifacts_app/manifest.yaml`
against `POST /api/v1/modules/activate` shall create the Module row and land every
declared contribution (archetypes, object_types, grammars, artifact_types) in the
database, and re-activating the same manifest shall be an idempotent no-op. This
exercises [FR-001](../functional/FR-001-module-manifest-activates.md) acceptance criteria AC-2, AC-3 and AC-4.

## Target Integration

The component under test is this Module's published manifest; the external
dependency is filament-core-service, reached over its HTTP module-activation and
read APIs. The integration type exercised is an HTTP client call posting the
manifest to `/api/v1/modules/activate`, followed by read-back calls to
`/api/v1/archetypes`, `/api/v1/object-types`, `/api/v1/grammars`, and
`/api/v1/artifact-types`.

## Preconditions

A filament-core-service instance is deployed and reachable on a clean cluster (or
the kind dev cluster) with an empty `modules` table, so that the absence and later
presence of the Module row are both meaningful. The current
`spec_artifacts_app/manifest.yaml` is built and available to post.

## Inputs

The single input is `spec_artifacts_app/manifest.yaml` from this repo's package,
posted to `POST /api/v1/modules/activate`. The same manifest bytes are reused
unchanged for the re-activation step so the content hash is identical.

## Test Procedure

Each step performs one discrete action and has its own success criterion.

1. Deploy filament-core-service to a clean cluster (or use the kind dev cluster).
   - IT-001-SC-01: the service is reachable and the `modules` table is empty.
2. POST `spec_artifacts_app/manifest.yaml` to `/api/v1/modules/activate`.
   - IT-001-SC-02: the endpoint returns 200 OK and a Module row is created.
3. GET `/api/v1/archetypes`, `/api/v1/object-types`, `/api/v1/grammars`, and
   `/api/v1/artifact-types`.
   - IT-001-SC-03: each item declared by the manifest is present with the correct
     attributes.
4. Re-POST the identical manifest to `/api/v1/modules/activate`.
   - IT-001-SC-04: the re-activation is an idempotent no-op — the same
     `modules.id` and SHA-256 content hash, with no row duplication.

## Expected Results

Activation against a clean filament-core succeeds with 200 OK and creates the
Module row; every declared archetype, object_type, grammar, and artifact_type
appears in its corresponding table with the correct attributes; and re-activation
of the identical manifest is a no-op producing the same `modules.id` and SHA-256
content hash with no duplicated rows. The test passes only when every per-step
success criterion holds.

## Acceptance Criteria

| ID | Criteria |
|----|----------|
| IT-001-AC-1 | All assertions in test-procedure steps 2-4 pass |
| IT-001-AC-2 | Re-activation produces the same SHA-256 content hash |
