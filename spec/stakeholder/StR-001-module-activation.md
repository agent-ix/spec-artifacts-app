---
id: StR-001
title: "Application composite specs"
artifact_type: StR
---
# [StR-001] Application composite specs

## Stakeholder

Filament platform / spec authors / agent CLI generators.

## Need

Multi-service applications need composite specs aggregating per-service requirements with master-requirements rollup.

## Acceptance Criteria

| ID | Criteria |
|----|----------|
| StR-001-AC-1 | A Module activation against filament-core registers the contents this module declares. |
| StR-001-AC-2 | Agent CLI generators (minijinja-cli) can produce valid artifacts using the templates and schemas this module ships. |

## Dependencies

- **Upstream**: filament-core-service FR-035 (Module Manifest Schema)
