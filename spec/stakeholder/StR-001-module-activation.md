---
id: StR-001
title: "Application composite specs"
type: StR
---
# [StR-001] Application composite specs

## Stakeholder Need

The Filament platform, spec authors, and agent CLI generators require that
multi-service applications **shall** be able to express composite specs that
aggregate per-service requirements into a master-requirements rollup, so that an
application's contributions are declared once and consumed consistently across the
platform.

## Rationale

Multi-service applications today have no single, authoritative way to roll up the
requirements of their constituent services. Without an aggregating composite spec,
authors must duplicate and manually reconcile per-service requirements, and agent
generators have no canonical source to read from. A composite spec with a
master-requirements rollup removes that duplication and gives every consumer one
trustworthy view of what the application declares.

## Validation Criteria

This need is considered satisfied when activating this Module against
filament-core registers the contents it declares, and when agent CLI generators
(minijinja-cli) can produce valid artifacts using the templates and schemas this
Module ships. Satisfaction is judged by demonstrating both outcomes against a
filament-core instance.

## Dependencies

Relationships at the stakeholder level. **Upstream**: filament-core-service FR-035
(Module Manifest Schema), which defines the activation contract this need relies
on. **Downstream**: the functional requirement covering manifest activation and the
integration test that verifies it end to end.
