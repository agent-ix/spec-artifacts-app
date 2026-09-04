---
id: AS-900
title: "Negative fixture"
type: ApplicationSpec
expect: validate.missing
because: "the ApplicationSpec archetype requires '## Purpose'"
---
<!-- Violates exactly one rule: the required `## Purpose` section is absent. Everything else is the skeleton. -->
# [AS-900] Orders Platform

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

| Field | Type | Multiplicity | Constraints |
|---|---|---|---|
| application_id | UUID | 1..1 | identity |
| slug | String | 1..1 | pattern: /^[a-z][a-z0-9-]*$/ |
| display_name | String | 1..1 | minLength: 1, maxLength: 120 |
| owning_team | String | 1..1 | nonEmpty |
| launched_at | Timestamp | 0..1 | |

## Boundaries

| ID | Name | Kind | Description |
|---|---|---|---|
| AS-900-BND-1 | Order lifecycle | owned | Intake, pricing, reservation, and handoff are specified and operated by this platform. |
| AS-900-BND-2 | Payment capture | consumed | Called synchronously at checkout; specified by the Payments Platform. |
| AS-900-BND-3 | Carrier rate lookup | external | A third-party rate service with its own availability contract. |
| AS-900-BND-4 | Returns | deferred | Named so its absence is deliberate; no requirement here covers it. |

## Capabilities

| ID | Name | Description | Actors |
|---|---|---|---|
| AS-900-CAP-1 | Submit an order | Accept an order from the storefront or the partner API and persist it as submitted. | AS-900-ACT-1, AS-900-ACT-3 |
| AS-900-CAP-2 | Price and reserve | Price a submitted order and reserve its lines against inventory. | AS-900-ACT-2 |
| AS-900-CAP-3 | Hand off to fulfilment | Publish an accepted order to the fulfilment topic exactly once. | AS-900-ACT-4 |

## Actors

| ID | Name | Kind | Description |
|---|---|---|---|
| AS-900-ACT-1 | Shopper | human | Places orders through the storefront. |
| AS-900-ACT-2 | Inventory service | service | Holds and releases reservations against stock. |
| AS-900-ACT-3 | Partner integration | external_system | Submits orders on a partner's behalf over the partner API. |
| AS-900-ACT-4 | Nightly reconciler | scheduler | Re-drives orders stuck between reservation and handoff. |

## Interfaces

| ID | Name | Kind | Direction | Contract |
|---|---|---|---|---|
| AS-900-IFC-1 | Storefront order API | http_api | inbound | POST /api/v1/orders |
| AS-900-IFC-2 | Inventory reservation API | http_api | outbound | POST /api/v1/reservations |
| AS-900-IFC-3 | Fulfilment topic | event_stream | outbound | orders.accepted.v1 |
| AS-900-IFC-4 | Operator console | ui | inbound | /console/orders |

## Data Dependencies

| ID | Name | Source | Access |
|---|---|---|---|
| AS-900-DAT-1 | Stakeholder requirements rolled up | agent-ix/spec-artifacts-iso#StR | read |
| AS-900-DAT-2 | Functional requirements rolled up | agent-ix/spec-artifacts-iso#FR | read |
| AS-900-DAT-3 | Integration tests rolled up | agent-ix/spec-artifacts-iso#IT | read |

## UI Rendering Requirements

| ID | Surface | Requirement | Verification |
|---|---|---|---|
| AS-900-UI-1 | web | The order detail view shall render every line item with its reserved quantity. | Test (TC-101) |
| AS-900-UI-2 | web | The order list shall render a reservation-failed order with its failure reason visible without opening the order. | Test (TC-102) |
| AS-900-UI-3 | cli | `orders show <id>` shall print the same lifecycle state the web view renders. | Demonstration |

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
