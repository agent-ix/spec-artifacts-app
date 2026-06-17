---
id: AS-001
title: "spec-artifacts-app application spec"
type: ApplicationSpec
---
# Specification: spec-artifacts-app

## Purpose

Multi-service applications need composite specs aggregating per-service requirements with master-requirements rollup.

## Module Summary

Module contributes the `application-spec` archetype, `app-spec` grammar, and 2 artifact_types (ApplicationSpec, MasterRequirements). Absorbs the retired spec-master-requirements package.

## Structure

- `stakeholder/` — StR-XXX stakeholder requirements
- `functional/` — FR-XXX functional requirements
- `integration/` — IT-XXX integration tests
- `tests.md` — test matrix
