---
id: IT-001
title: "Manifest activation roundtrip against filament-core"
artifact_type: IT
relationships:
  - target: "ix://agent-ix/spec-artifacts-app/FR-001"
    type: "verifies"
---
# [IT-001] Manifest activation roundtrip

## Scenario

Activate this Module's manifest against a clean filament-core-service instance and verify all declared contributions land in the database.

## Steps

1. Deploy filament-core-service to a clean cluster (or use kind dev cluster).
2. POST `spec_artifacts_app/manifest.yaml` to `/api/v1/modules/activate`.
3. Assert 200 OK and Module row created.
4. GET `/api/v1/archetypes`, `/api/v1/object-types`, `/api/v1/grammars`, `/api/v1/artifact-types`.
5. Assert each declared item is present with correct attributes.
6. Re-POST the same manifest; assert idempotent no-op (same `modules.id`, no row duplication).

## Acceptance Criteria

| ID | Criteria |
|----|----------|
| IT-001-AC-1 | All assertions in steps 3-6 pass |
| IT-001-AC-2 | Re-activation produces the same SHA-256 content hash |
