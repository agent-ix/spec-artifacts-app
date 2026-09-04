import "@typespec/json-schema";
import "@agent-ix/semantic-core";

using TypeSpec.JsonSchema;
using AgentIx.Semantic.Core;

/**
 * Semantic data models of the spec-artifacts-app module
 * (agent-ix/spec-artifacts-app#3, FR-002).
 *
 * One model per declared artifact type — `ApplicationSpec` and
 * `MasterRequirements` — plus every support model and scalar they reference.
 * Each model is the typed form of the record the artifact type's
 * `body_extraction` locators extract, together with the frontmatter identity,
 * the relationships, and the document's provenance. Markdown is the authority
 * and the record is a derived projection (FR-004).
 *
 * An application composite *references* what other modules own; it never
 * restates it. A requirement this application rolls up, or a data source it
 * depends on, is carried as an `ImportedTypeRef` plus an id — never as a copy of
 * the imported type's fields (FR-002-AC-10). No `$ref` in this bundle names
 * another module's base, because a cross-module `$ref` cannot resolve offline
 * from this module's shipped bytes (FR-002-CON-2).
 *
 * Every field carries a constraint. Where a field is free text the doc comment
 * says `free text:` and why (FR-002-AC-4).
 *
 * The `$id` base embeds the manifest `version` by intent (FR-002-CON-5): one
 * schema URL names exactly one immutable byte sequence. A bump edits this base
 * and `manifest.yaml`'s `version` in one commit and re-runs `make schemas`.
 */
@jsonSchema("https://schemas.agent-ix.org/agent-ix/spec-artifacts-app/0.2.0/")
namespace AgentIx.SpecArtifactsApp;

// ---------------------------------------------------------------------------
// Scalars
// ---------------------------------------------------------------------------

/** A non-empty string; the base of every prose cell and every name. */
@minLength(1)
scalar NonEmptyText extends string;

/**
 * Artifact id as the frontmatter schemas of this module already pin it:
 * a 2..4 letter prefix and a number (`AS-001`, `MR-001`).
 */
@pattern("^[A-Z]{2,4}-[0-9]+$")
scalar ArtifactId extends string;

/** Capability row id, `<document id>-CAP-N`; anchored on the artifact type, not the document. */
@pattern("^[A-Z]{2,4}-[0-9]+-CAP-[0-9]+$")
scalar CapabilityId extends string;

/** Actor row id, `<document id>-ACT-N`. */
@pattern("^[A-Z]{2,4}-[0-9]+-ACT-[0-9]+$")
scalar ActorId extends string;

/** Boundary row id, `<document id>-BND-N`. */
@pattern("^[A-Z]{2,4}-[0-9]+-BND-[0-9]+$")
scalar BoundaryId extends string;

/** Interface row id, `<document id>-IFC-N`. */
@pattern("^[A-Z]{2,4}-[0-9]+-IFC-[0-9]+$")
scalar InterfaceId extends string;

/** Data-dependency row id, `<document id>-DAT-N`. */
@pattern("^[A-Z]{2,4}-[0-9]+-DAT-[0-9]+$")
scalar DataDependencyId extends string;

/** UI rendering-requirement row id, `<document id>-UI-N`. */
@pattern("^[A-Z]{2,4}-[0-9]+-UI-[0-9]+$")
scalar RenderingRequirementId extends string;

/** An aggregated requirement's own id, in the ISO artifact-type forms. */
@pattern("^(StR|US|FR|NFR|IT|TC)-[0-9]+$")
scalar RequirementRefId extends string;

/** A test-case reference annotated in a verification cell, `Test (TC-035)`. */
@pattern("^TC-[0-9]+$")
scalar TestCaseRef extends string;

/** A relationship verb from the module's edge vocabulary. */
@pattern("^[a-z][a-z0-9_]*$")
scalar EdgeVerb extends string;

/** A relationship target: an `ix://` identity, as the frontmatter schemas require. */
@pattern("^ix://.+$")
scalar IxTarget extends string;

/**
 * Relationship cardinality as authored: each side is a number, a letter token,
 * or `*`, optionally a `..` range (`1:1`, `1:N`, `0..1`).
 */
@pattern("^[0-9A-Za-z*]+(\\.\\.[0-9A-Za-z*]+)?(:[0-9A-Za-z*]+(\\.\\.[0-9A-Za-z*]+)?)?$")
scalar Cardinality extends string;

/** SHA-256 over the document bytes, `sha256:<64 hex>` (the quoin FR-073 digest form). */
@pattern("^sha256:[0-9a-f]{64}$")
scalar Sha256Digest extends string;

/** A 1-based document line number. */
@minValue(1)
scalar LineNumber extends int32;

/**
 * Lifecycle status from frontmatter `status`. The value set is deliberately
 * open: closing it is a vocabulary sweep-and-report, not a side effect of this
 * schema set (spec.md Out of Scope).
 */
@pattern("^[A-Za-z][A-Za-z_-]*$")
scalar ArtifactStatus extends string;

/** A module reference, `<org>/<repo>`; the key form of `semantic.imports`. */
@pattern("^[a-z][a-z0-9-]*/[a-z][a-z0-9-]*$")
scalar ModuleRef extends string;

/** A type name exported by a module (`FR`, `master-requirements`, `Entity`). */
@pattern("^[A-Za-z][A-Za-z0-9_-]*$")
scalar TypeName extends string;

/**
 * A UI surface an application renders on (`web`, `cli`, `ide-panel`).
 * Deliberately open: the surface vocabulary belongs to the applications, not to
 * this module, and closing it here would reject the corpus it describes.
 */
@pattern("^[a-z][a-z0-9-]*$")
scalar UiSurface extends string;

// ---------------------------------------------------------------------------
// Closed vocabularies
// ---------------------------------------------------------------------------

/** What kind of actor interacts with the application. */
enum ActorKind {
  human,
  service,
  agent,
  external_system,
  scheduler,
}

/** The shape of an interface the application exposes or consumes. */
enum InterfaceKind {
  http_api,
  grpc,
  cli,
  event_stream,
  ui,
  library,
  file,
}

/** Which way an interface faces relative to the application. */
enum InterfaceDirection {
  inbound,
  outbound,
  bidirectional,
}

/** How the application touches a data dependency. */
enum DataAccessMode {
  read,
  write,
  read_write,
}

/** How a named area sits relative to the application's boundary. */
enum BoundaryKind {
  owned,
  consumed,
  external,
  deferred,
}

/** The ISO artifact type of an aggregated requirement. */
enum RequirementKind {
  StR,
  US,
  FR,
  NFR,
  IT,
  TC,
}

// ---------------------------------------------------------------------------
// Support models
// ---------------------------------------------------------------------------

/** A level-2 section as extracted: byte-exact content and its 1-based line span. */
model Section {
  /** free text: authored prose; its sentence grammar is an advisory lint, not a schema. */
  text: NonEmptyText;

  startLine: LineNumber;
  endLine: LineNumber;
}

/** Where the record came from. `sourceIdentity` is never synthesized (FR-004). */
model Provenance {
  /** free text: a corpus-relative filesystem path, whose shape is the checkout's, not this module's. */
  path: NonEmptyText;

  sourceIdentity?: SemanticId;
  digest: Sha256Digest;
}

/** A typed frontmatter edge. Exactly three properties; annotation keys are dropped (FR-004). */
model Relationship {
  target: IxTarget;
  type: EdgeVerb;
  cardinality?: Cardinality;
}

/**
 * A verification cell split into its parts. For `<method> (<annotation>)`,
 * `method` is the text before the first `(`, `annotation` the text between the
 * first `(` and the last `)` verbatim, and `testRefs` the `TC-N` tokens found
 * in `annotation`, in order. No byte of the cell is dropped.
 */
model Verification {
  /** free text: an ISO 29148 method name whose vocabulary is an advisory lint rule, not a schema. */
  method: NonEmptyText;

  testRefs: TestCaseRef[];

  /** free text: the parenthesized remainder of the cell, carried verbatim so no byte is lost. */
  annotation?: NonEmptyText;
}

/**
 * A reference to a type another module owns. The reference form this module
 * publishes: a module and a type name, never a copy of the imported type's
 * fields, and never a cross-module `$ref` (FR-002-AC-10).
 */
model ImportedTypeRef {
  module: ModuleRef;
  type: TypeName;
}

/** One row of `## Boundaries`: a named area and how it sits relative to the application. */
model Boundary {
  id: BoundaryId;
  name: NonEmptyText;
  kind: BoundaryKind;

  /** free text: authored prose describing the area; no closed vocabulary describes an application's areas. */
  description: NonEmptyText;

  line: LineNumber;
}

/** One row of `## Capabilities`: what the application does, and for whom. */
model Capability {
  id: CapabilityId;
  name: NonEmptyText;

  /** free text: authored prose stating the capability; the requirements beneath it carry the normative form. */
  description: NonEmptyText;

  actors: ActorId[];
  line: LineNumber;
}

/** One row of `## Actors`: who or what interacts with the application. */
model Actor {
  id: ActorId;
  name: NonEmptyText;
  kind: ActorKind;

  /** free text: authored prose describing the actor's role. */
  description: NonEmptyText;

  line: LineNumber;
}

/** One row of `## Interfaces`: a surface the application exposes or consumes. */
model Interface {
  id: InterfaceId;
  name: NonEmptyText;
  kind: InterfaceKind;
  direction: InterfaceDirection;

  /** free text: how the contract is named — an OpenAPI path, a topic, a command; no one vocabulary spans them. */
  contract: NonEmptyText;

  line: LineNumber;
}

/** One row of `## Data Dependencies`: a typed source the application reads or writes. */
model DataDependency {
  id: DataDependencyId;
  name: NonEmptyText;
  source: ImportedTypeRef;
  access: DataAccessMode;
  line: LineNumber;
}

/** One row of `## UI Rendering Requirements`: what a surface must render. */
model RenderingRequirement {
  id: RenderingRequirementId;
  surface: UiSurface;

  /** free text: the authored rendering obligation; its EARS grammar is an advisory lint, not a schema. */
  requirement: NonEmptyText;

  verification: Verification;
  line: LineNumber;
}

/**
 * One row of `## Requirements`: a requirement this composite rolls up. The
 * requirement's own fields belong to the module that owns its type; this record
 * carries only the reference.
 */
model RequirementRef {
  id: RequirementRefId;
  kind: RequirementKind;
  source: ImportedTypeRef;
  target: IxTarget;
  line: LineNumber;
}

// ---------------------------------------------------------------------------
// Exported artifact-type models
// ---------------------------------------------------------------------------

/**
 * The record of an `ApplicationSpec` document: an application's identity, its
 * boundaries, capabilities, actors, interfaces, data dependencies, UI rendering
 * requirements, and the requirements it aggregates.
 *
 * This model describes an application *declaration*. runtime state (deployment,
 * health, uptime) is not modelled: a deployed instance's condition belongs to
 * the platform that runs it, never to the document that specifies it
 * (FR-002-CON-4).
 */
model ApplicationSpec {
  id: ArtifactId;
  title: NonEmptyText;
  type: "ApplicationSpec";
  status?: ArtifactStatus;
  relationships: Relationship[];
  provenance: Provenance;

  purpose: Section;
  scope?: Section;
  systemOverview?: Section;
  structure?: Section;
  requirementsArchitecture?: Section;
  references?: Section;

  /**
   * The application's identity attributes, declared as one typed row per field
   * in `## Properties` (`Field | Type | Multiplicity | Constraints`) or, as the
   * alternate form of the same declarations, as one `sysml` fence under the
   * same heading. Each row is a semantic-core `FieldDecl`; no field of it is
   * redeclared here (quoin FR-071).
   */
  @minItems(1)
  fields?: FieldDecl[];

  boundaries?: Boundary[];
  capabilities?: Capability[];
  actors?: Actor[];
  interfaces?: Interface[];
  dataDependencies?: DataDependency[];
  renderingRequirements?: RenderingRequirement[];
  requirements?: RequirementRef[];

  @minItems(1)
  invariants?: ClauseRef[];
}

/**
 * The record of a `MasterRequirements` document: the front page of a
 * specification — its purpose, scope, and the set of requirements it rolls up.
 *
 * Like `ApplicationSpec`, it references the requirements it aggregates rather
 * than restating them, so the module that owns a requirement type stays the one
 * definition of it.
 */
model MasterRequirements {
  id: ArtifactId;
  title: NonEmptyText;
  type: "MasterRequirements";
  status?: ArtifactStatus;
  relationships: Relationship[];
  provenance: Provenance;

  purpose: Section;
  scope?: Section;
  systemOverview?: Section;
  structure?: Section;
  requirementsArchitecture?: Section;
  references?: Section;

  /**
   * The specification's identity attributes, declared as one typed row per
   * field in `## Properties`, or as the alternate `sysml` fence form of the
   * same declarations (quoin FR-071).
   */
  @minItems(1)
  fields?: FieldDecl[];

  requirements?: RequirementRef[];

  @minItems(1)
  invariants?: ClauseRef[];
}
