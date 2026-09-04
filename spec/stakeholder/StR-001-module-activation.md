---
id: StR-001
title: "Application composite specs"
type: StR
---
# StR-001: Application composite specs

## Stakeholder Need

The Filament platform, spec authors, and agent CLI generators require that
the Filament platform **shall** register, validate, and serve composite specs that
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


| ID | Criteria | Validation |
|----|----------|------------|
| StR-001-VC-1 | Activating this Module against filament-core registers the contents it declares. | Demonstration |
| StR-001-VC-2 | An author starting from a skeleton this Module ships produces an artifact that `validate_document` accepts for its artifact type. | Test (TC-028) |
| StR-001-VC-3 | A consumer reads an application composite as a typed record, bound to the exact schema bytes the Module ships, without re-parsing the document's prose. | Test (TC-034) |

VC-1 is judged by demonstrating activation against a running filament-core
instance, which this package's suite does not stand up. VC-2 and VC-3 are
discharged here, by the suite that validates every shipped skeleton and by the
one that reads a composite as a record bound to the shipped schema bytes.

## Dependencies

Relationships at the stakeholder level. **Upstream**: filament-core-service [FR-035](ix://agent-ix/filament-core-service/FR-035)
(Module Manifest Schema), which defines the activation contract this need relies
on. **Downstream**: the functional requirement covering manifest activation and the
integration test that verifies it end to end.
