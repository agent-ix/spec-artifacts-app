---
id: NFR-001
title: "Schema projection is reproducible, offline, and additively compatible"
type: NFR
quality_attribute: maintainability
relationships:
  - target: "ix://agent-ix/spec-artifacts-app/FR-002"
    type: "constrains"
  - target: "ix://agent-ix/spec-artifacts-app/FR-003"
    type: "constrains"
  - target: "ix://agent-ix/spec-artifacts-app/FR-005"
    type: "constrains"
---
# NFR-001: Schema projection is reproducible, offline, and additively compatible

## Statement

The module SHALL reproduce its emitted schema bundle byte-for-byte from the
committed TypeSpec source and lockfile on any machine that satisfies the
toolchain and npm-configuration preconditions of Scope, SHALL resolve every
`$ref` of that bundle with no network read, and SHALL change no artifact type in
a way that invalidates a document valid before the change.

## Scope

- Applies to: `make schemas`, `make schemas-check`, the `data_schema.digest`
  values in `manifest.yaml`, every `$ref` resolution the test suite performs, and
  every locator the change adds.
- Operational context: a clean clone with `npm ci` and `poetry install`, and the
  quire wheel provisioned by `make dev-quire`; the only network access is the
  package install itself.
- Toolchain preconditions: Node 20 or later (`@typespec/compiler` 1.15.0
  requires it) and Python 3.13. `make dev-quire` installs `quire >= 0.46.0`,
  the first wheel exposing `extract_semantic`, from the local `pypi.ix` index;
  publishing it to an index a repository may commit against is
  agent-ix/quire-rs#392, which is why it is a documented target and not a
  declared dependency.
- Reference machine: the machine that recorded the release notes for the
  version under test, whose Node, Python, and CPU are named there. Metric 4 is a
  bound on that machine, not a portable number.
- npm-configuration precondition: `@agent-ix/semantic-core` 0.1.0 resolves only
  from the registry the developer's npm configuration routes the `@agent-ix`
  scope to — today the local npm.ix registry. The repository carries no `.npmrc`
  (FR-002-CON-3), so the scope routing is the machine's and not the
  repository's, and a machine whose npm configuration does not route the scope
  cannot reproduce the bundle at all.
- Engine floor: the semantic rows run against the quire wheel exposing
  `extract_semantic`. No index a repository may commit against carries it
  (agent-ix/quire-rs#392), so it is provisioned by `make dev-quire` and the
  semantic rows fail rather than skip when it is absent.
- Line endings: the repository pins LF via `.gitattributes`, so the emitted
  bundle and every `manifest.yaml` digest are checkout-independent — the digests
  are computed over bytes with no line-ending normalization, and a CRLF checkout
  would change every one of them.

## Rationale

The manifest binds each artifact type to a digest. If the projection drifted with
the machine that produced it, every consumer would see a different digest for the
same source and the binding would mean nothing. Offline resolution is the
FR-073-CON-1 boundary quoin and quire both enforce. Additive compatibility is
what lets a module that already has documents in the corpus adopt the contract at
all: the acceptance criterion "existing valid application specs remain readable"
is this requirement's, measured rather than asserted.

## Measurement and Evaluation

| Metric | Target | Threshold | Method |
|--------|--------|-----------|--------|
| Byte differences between two consecutive `make schemas` runs on one tree | 0 files | 0 files | Test (two `make schemas` runs compared byte-for-byte) |
| Network reads during `make schemas-check` and `make test` | 0 | 0 | Demonstration (both targets run with the network namespace disabled) |
| Locators added by this change that are required | 0 of the added set | 0 of the added set | Analysis (locator set diffed against the branch point) |
| Wall time of `make schemas-check` | 10 s | 30 s | Test (performance benchmark: `time make schemas-check` on the reference machine) |

## Verification

A test regenerates the bundle into a scratch directory and compares every file to
the committed one; a second test recomputes the `toolchain.json` digest and each
manifest `data_schema.digest`; a third diffs the locator set against the branch
point and asserts every added locator is optional. The offline run is a manual
gate of this repository, recorded in the release notes; no CI job is claimed by
this requirement.

## Acceptance Criteria

<!-- This NFR is measurable, so the Measurement table above carries the
     obligations. The criteria below exist because each metric needs an
     addressable id for the Test Matrix to trace to and for `quire coverage` to
     bind a test symbol against; each row restates one metric's pass condition
     and nothing else. -->

| ID | Criteria | Verification |
|----|----------|--------------|
| NFR-001-AC-1 | Two consecutive `make schemas` runs on one tree leave `spec_artifacts_app/schemas` and `spec_artifacts_app/manifest.yaml` byte-identical — `git status --porcelain` over both reports zero files. | Test (TC-030) |
| NFR-001-AC-2 | `make schemas-check` and `make test` both exit 0 with the network namespace disabled after `npm ci`, `poetry install`, and `make dev-quire`. | Demonstration (TC-031) |
| NFR-001-AC-3 | Every `body_extraction` locator this change adds, diffed against the branch point, carries `required: false`, except `title` and `purpose`, which the pre-change document already carries. | Analysis (TC-032) |
| NFR-001-AC-4 | `make schemas-check` completes within 30 s on the reference machine. | Test (TC-033) |

## Dependencies

- **Upstream**: [FR-002](../functional/FR-002-semantic-data-schemas.md), [FR-003](../functional/FR-003-semantic-manifest-contract.md), [FR-005](../functional/FR-005-executable-skeletons.md) (whose locators metric 3 measures)
- **Downstream**: the release gauntlet of this module
