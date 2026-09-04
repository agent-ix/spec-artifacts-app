---
id: AS-001
title: "Orders Platform"
type: ApplicationSpec
status: DRAFT
relationships:
  - target: "ix://agent-ix/orders-platform/StR-001"
    type: "references"
    cardinality: "1:N"
---
<!-- ApplicationSpec authoring skeleton, ALTERNATE Properties form. Declares
     exactly the same fields as application-spec.md, in the same order,
     authored as one `sysml` fence instead of the typed table (FR-005-AC-2).
     One artifact carries one form; the alternate is a separate file, never a
     second block in the same artifact. Every other section is identical.
     Fill every section with substantive content. Contract (manifest body_extraction asserts):
     - Frontmatter MUST carry id (^[A-Z]{2,4}-[0-9]+$), title, type: ApplicationSpec.
     - REQUIRED: the H1 title, and "## Purpose" (H2).
     - OPTIONAL (H2): Scope, System Overview, Structure,
       Requirements Architecture, References, Properties, Boundaries,
       Capabilities, Actors, Interfaces, Data Dependencies,
       UI Rendering Requirements, Requirements, Invariants.
     - "## Properties" here is the single ```sysml``` fence form. Its
       counterpart is the typed table, header exactly
       `Field | Type | Multiplicity | Constraints` — see application-spec.md.
       One artifact carries ONE form.
     - Each domain table's header row and its ID column pattern are fixed by
       the archetype; ids are scoped to this document's id (AS-001-CAP-1).
     - "## Requirements" rows REFERENCE a requirement another module owns:
       the Source cell is `<org>/<repo>#<Type>` and must name a module and a
       type declared in the manifest's `semantic.imports`. The requirement's
       own fields belong to that module and are never copied here.
     - "## Invariants": one `### <clauseId>` per clause, each owning exactly
       one ```ocl``` fence. The clause text is carried verbatim, never parsed. -->
# [AS-001] Orders Platform

## Purpose

The Orders Platform accepts customer orders from the storefront and the partner
API, prices and reserves them against inventory, and hands accepted orders to
fulfilment. This document is the composite specification for the platform as a
whole: it names what the platform owns, who uses it, what it talks to, and which
per-service requirements it rolls up.

## Scope

In scope: order intake, pricing, reservation, and the handoff to fulfilment.
Out of scope: payment capture, which the Payments Platform owns and this
platform only calls; and warehouse operations downstream of the handoff.

## System Overview

Three services sit behind one HTTP gateway. `order-intake` validates and
persists submissions, `order-pricing` prices and reserves them, and
`order-handoff` publishes accepted orders to the fulfilment topic. The three
share one Postgres cluster and one event bus, and none is reachable from outside
the gateway.

## Structure

- `services/order-intake/spec/` — intake requirements.
- `services/order-pricing/spec/` — pricing and reservation requirements.
- `services/order-handoff/spec/` — handoff requirements.
- `spec/tests.md` — the platform-level test matrix.

## Requirements Architecture

Stakeholder needs live in `services/*/spec/stakeholder/`, are told as stories in
`usecase/`, and are made normative in `functional/` and `non-functional/`. This
document rolls them up; it introduces no requirement of its own.

## References

- ISO/IEC/IEEE 29148 — Requirements engineering.
- The three service bundles named in Structure.

## Properties

```sysml
attribute application_id : UUID[1..1] { identity }
attribute slug : String[1..1] { pattern: /^[a-z][a-z0-9-]*$/ }
attribute display_name : String[1..1] { minLength: 1, maxLength: 120 }
attribute owning_team : String[1..1] { nonEmpty }
attribute launched_at : Timestamp[0..1]
```

## Boundaries

| ID | Name | Kind | Description |
|---|---|---|---|
| AS-001-BND-1 | Order lifecycle | owned | Intake, pricing, reservation, and handoff are specified and operated by this platform. |
| AS-001-BND-2 | Payment capture | consumed | Called synchronously at checkout; specified by the Payments Platform. |
| AS-001-BND-3 | Carrier rate lookup | external | A third-party rate service with its own availability contract. |
| AS-001-BND-4 | Returns | deferred | Named so its absence is deliberate; no requirement here covers it. |

## Capabilities

| ID | Name | Description | Actors |
|---|---|---|---|
| AS-001-CAP-1 | Submit an order | Accept an order from the storefront or the partner API and persist it as submitted. | AS-001-ACT-1, AS-001-ACT-3 |
| AS-001-CAP-2 | Price and reserve | Price a submitted order and reserve its lines against inventory. | AS-001-ACT-2 |
| AS-001-CAP-3 | Hand off to fulfilment | Publish an accepted order to the fulfilment topic exactly once. | AS-001-ACT-4 |

## Actors

| ID | Name | Kind | Description |
|---|---|---|---|
| AS-001-ACT-1 | Shopper | human | Places orders through the storefront. |
| AS-001-ACT-2 | Inventory service | service | Holds and releases reservations against stock. |
| AS-001-ACT-3 | Partner integration | external_system | Submits orders on a partner's behalf over the partner API. |
| AS-001-ACT-4 | Nightly reconciler | scheduler | Re-drives orders stuck between reservation and handoff. |

## Interfaces

| ID | Name | Kind | Direction | Contract |
|---|---|---|---|---|
| AS-001-IFC-1 | Storefront order API | http_api | inbound | POST /api/v1/orders |
| AS-001-IFC-2 | Inventory reservation API | http_api | outbound | POST /api/v1/reservations |
| AS-001-IFC-3 | Fulfilment topic | event_stream | outbound | orders.accepted.v1 |
| AS-001-IFC-4 | Operator console | ui | inbound | /console/orders |

## Data Dependencies

| ID | Name | Source | Access |
|---|---|---|---|
| AS-001-DAT-1 | Stakeholder requirements rolled up | agent-ix/spec-artifacts-iso#StR | read |
| AS-001-DAT-2 | Functional requirements rolled up | agent-ix/spec-artifacts-iso#FR | read |
| AS-001-DAT-3 | Integration tests rolled up | agent-ix/spec-artifacts-iso#IT | read |

## UI Rendering Requirements

| ID | Surface | Requirement | Verification |
|---|---|---|---|
| AS-001-UI-1 | web | The order detail view shall render every line item with its reserved quantity. | Test (TC-101) |
| AS-001-UI-2 | web | The order list shall render a reservation-failed order with its failure reason visible without opening the order. | Test (TC-102) |
| AS-001-UI-3 | cli | `orders show <id>` shall print the same lifecycle state the web view renders. | Demonstration |

## Requirements

| ID | Kind | Source | Target |
|---|---|---|---|
| StR-001 | StR | agent-ix/spec-artifacts-iso#StR | ix://agent-ix/orders-platform/StR-001 |
| FR-014 | FR | agent-ix/spec-artifacts-iso#FR | ix://agent-ix/orders-platform/FR-014 |
| NFR-003 | NFR | agent-ix/spec-artifacts-iso#NFR | ix://agent-ix/orders-platform/NFR-003 |
| IT-002 | IT | agent-ix/spec-artifacts-iso#IT | ix://agent-ix/orders-platform/IT-002 |

## Invariants

The clauses this application declaration enforces. Each clause owns one `ocl`
fence under its own `### <clauseId>` heading; the fence text is carried verbatim
and is never evaluated here.

### EveryCapabilityNamesAnActor

```ocl
context ApplicationSpec
inv EveryCapabilityNamesAnActor:
  self.capabilities->forAll(c | c.actors->notEmpty())
```

### DeferredBoundaryCarriesNoInterface

```ocl
context ApplicationSpec
inv DeferredBoundaryCarriesNoInterface:
  self.boundaries->select(b | b.kind = BoundaryKind::deferred)->forAll(b | self.interfaces->isEmpty() or true)
```
