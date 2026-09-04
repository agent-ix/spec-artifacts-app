---
id: US-001
title: "Consume application composite specs as typed semantic records"
type: US
relationships:
  - target: "ix://agent-ix/spec-artifacts-app/StR-001"
    type: "traces_to"
  - target: "ix://agent-ix/spec-artifacts-app/FR-002"
    type: "exercises"
  - target: "ix://agent-ix/spec-artifacts-app/FR-003"
    type: "exercises"
  - target: "ix://agent-ix/spec-artifacts-app/FR-004"
    type: "exercises"
  - target: "ix://agent-ix/spec-artifacts-app/FR-005"
    type: "exercises"
---
# US-001: Consume application composite specs as typed semantic records

## Story

**As a** semantic consumer of application composite specs (the quire-contract-ir
frontends, the filament-core-data code generators, and the Filament extraction
API)
**I want** each application artifact type this module declares to publish a typed
data schema, an explicit Markdown mapping, and a declared set of imported module
types it references
**So that** I can read an application's identity, boundaries, capabilities,
actors, interfaces, data dependencies, UI rendering requirements, and the
requirements it rolls up as one record, instead of re-parsing composite-spec
prose in every consumer and guessing which other module owns each referenced
type.

## Context

The module contributes two artifact types, `ApplicationSpec` and
`MasterRequirements`, and today declares neither `body_extraction` locators nor a
data schema for either. A consumer that receives an application spec receives
Markdown; everything the document says about which services it composes, which
requirements it aggregates, and which UI surfaces it demands is prose to be
re-parsed. Wave 4 of the semantic program (agent-ix/quoin#286) introduced a module
contract in which an artifact type references its emitted JSON Schema by path and
digest (quoin FR-073), Markdown forms map to semantic-core declarations (quoin
FR-071, FR-072), and a module declares what it imports from other modules
(quoin FR-070).

An application spec is a *composite*. Most of what it rolls up — a stakeholder
requirement, a functional requirement, an integration test — is already modelled
by another module (`spec-artifacts-iso`). Restating those fields here would give
the ecosystem two disagreeing definitions of a functional requirement, which is
the outcome this story exists to avoid.

## Acceptance Examples (Illustrative)

These examples clarify the consumer's expectations. They are illustrative only,
not test cases and not verification criteria.

### US-001-EX-1: Capabilities arrive as rows

- **Given** an application spec whose `## Capabilities` table has four rows
- **When** the consumer reads its record
- **Then** it sees four capability objects, each with an id, a name, a
  description, the actors it serves, and the line it was authored on

### US-001-EX-2: An aggregated requirement is a reference, not a copy

- **Given** an application spec that rolls up `FR-014` of another repository
- **When** the consumer reads its record
- **Then** it sees a reference naming the owning module, the imported type, and
  the requirement id — and no copy of that requirement's own fields

### US-001-EX-3: An unchanged application spec keeps validating

- **Given** an application spec that validated before this change
- **When** the module publishes the data schemas and the added locators
- **Then** the document still validates and its record carries the sections it
  already authored

## Options (Exploratory)

Approaches discussed during discovery, none of which imply commitment on this
story: hand-authored JSON Schema per artifact type; a TypeSpec source compiled to
JSON Schema; embedding the imported modules' schemas into this module's bundle;
referencing imported types by name and module rather than by `$ref`. The
functional requirements select among them.

## Constraints (Contextual)

Consumers read the emitted schemas offline from the installed module; nothing may
require a network fetch of `https://schemas.agent-ix.org`. This context is carried
into the requirements as a constraint rather than restated as a story.

## Dependencies (Contextual)

Upstream: `@agent-ix/semantic-core` 0.1.0 (agent-ix/filament-core-data#35) and the
closed constraint IR vocabulary (agent-ix/filament-core-data#34); the quoin
semantic module contract (agent-ix/quoin#293); the quire-rs semantic extraction
surface (agent-ix/quire-rs#388).

Downstream: agent-ix/filament-core-data#36 and agent-ix/quire-contract-ir#52,
which consume this module's schemas and skeletons as fixtures.

## Priority and Risk (Informative)

P1 on the Wave 4 Track A sequence, after agent-ix/quoin#293 and
agent-ix/quire-rs#388. The risk if unmet is that the composite layer stays
untyped while the artifact layer beneath it is typed, so an application spec
becomes the one place in the corpus where a consumer must still guess.

## Notes (Informative)

Open question raised in discovery and deliberately left to the functional
requirements: whether an aggregated requirement reference should carry a
resolution status (`resolved`, `dangling`). Resolution needs the whole installed
module set, which a single document's record does not have.

## Traceability (Informative)

Traces to StR-001 (application composite specs) and is exercised by FR-002,
FR-003, FR-004, and FR-005.
