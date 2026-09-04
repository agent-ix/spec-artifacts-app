---
id: MR-001
title: "Orders Platform master requirements"
type: MasterRequirements
status: DRAFT
relationships:
  - target: "ix://agent-ix/orders-platform/AS-001"
    type: "aggregates"
    cardinality: "1:1"
---
<!-- MasterRequirements authoring skeleton (spec-artifacts-app). Fill every
     section with substantive content. Contract (manifest body_extraction
     asserts):
     - Frontmatter MUST carry id (^[A-Z]{2,4}-[0-9]+$), title,
       type: MasterRequirements.
     - REQUIRED: the H1 title, and "## Purpose" (H2).
     - OPTIONAL (H2): Scope, System Overview, Structure,
       Requirements Architecture, References, Properties, Requirements,
       Invariants.
     - A MasterRequirements document is the front page of a specification, not
       a description of a running system: it declares no Boundaries,
       Capabilities, Actors, Interfaces, Data Dependencies, or UI Rendering
       Requirements. Those belong to ApplicationSpec.
     - "## Properties" is the typed field form, header exactly
       `Field | Type | Multiplicity | Constraints`; its alternate form is a
       single ```sysml``` fence under the same heading. One artifact carries
       ONE form.
     - "## Requirements" rows REFERENCE a requirement another module owns: the
       Source cell is `<org>/<repo>#<Type>` and must name a module and a type
       declared in the manifest's `semantic.imports`. The requirement's own
       fields belong to that module and are never copied here.
     - "## Invariants": one `### <clauseId>` per clause, each owning exactly
       one ```ocl``` fence; the text is carried verbatim, never parsed. -->
# [MR-001] Orders Platform master requirements

## Purpose

This document is the front page of the Orders Platform specification. It states
what the specification is for, which requirement sets it rolls up, and where the
authoritative text for each of them lives. It restates none of those
requirements: each row of `## Requirements` references the module that owns the
requirement's type.

## Scope

Covers the three order services and the contracts between them. Excludes the
Payments Platform and warehouse operations, which carry their own master
requirements documents.

## System Overview

The specification is organised per service, with this document as the roll-up.
Every requirement referenced here is authored once, in the service bundle that
owns it, and is read from there.

## Structure

- `services/*/spec/stakeholder/` — StR artifacts.
- `services/*/spec/functional/` — FR artifacts.
- `services/*/spec/non-functional/` — NFR artifacts.
- `services/*/spec/integration/` — IT artifacts.

## Requirements Architecture

Stakeholder needs live in `services/*/spec/stakeholder/`, are told as stories in
`usecase/`, and are made normative in `functional/` and `non-functional/`. This
document rolls them up; it introduces no requirement of its own.

## References

- ISO/IEC/IEEE 29148 — Requirements engineering.
- The three service bundles named in Structure.

## Properties

| Field | Type | Multiplicity | Constraints |
|---|---|---|---|
| specification_id | UUID | 1..1 | identity |
| slug | String | 1..1 | pattern: /^[a-z][a-z0-9-]*$/ |
| revision | Integer | 1..1 | min: 1 |
| approved_at | Timestamp | 0..1 | |

## Requirements

| ID | Kind | Source | Target |
|---|---|---|---|
| StR-001 | StR | agent-ix/spec-artifacts-iso#StR | ix://agent-ix/orders-platform/StR-001 |
| US-004 | US | agent-ix/spec-artifacts-iso#US | ix://agent-ix/orders-platform/US-004 |
| FR-014 | FR | agent-ix/spec-artifacts-iso#FR | ix://agent-ix/orders-platform/FR-014 |
| TC-021 | TC | agent-ix/spec-artifacts-iso#TC | ix://agent-ix/orders-platform/TC-021 |

## Invariants

The clauses this specification declaration enforces. Each clause owns one `ocl`
fence under its own `### <clauseId>` heading; the fence text is carried verbatim
and is never evaluated here.

### EveryReferencedRequirementNamesAnImportedType

```ocl
context MasterRequirements
inv EveryReferencedRequirementNamesAnImportedType:
  self.requirements->forAll(r | r.source.module->notEmpty() and r.source.type->notEmpty())
```
