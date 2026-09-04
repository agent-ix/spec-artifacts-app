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
| Byte differences between two consecutive `make schemas` runs on one tree | 0 files | 0 files | Run `make schemas` twice and `git status --porcelain spec_artifacts_app/schemas spec_artifacts_app/manifest.yaml` |
| Network reads during `make schemas-check` and `make test` | 0 | 0 | Run with the network namespace disabled after `npm ci`, `poetry install`, and `make dev-quire`; both exit 0 |
| Locators added by this change that are required | 0 of the added set | 0 of the added set | Diff the manifest's locator set against the branch point and assert every added locator carries `required: false` |
| Wall time of `make schemas-check` | 10 s | 30 s | `time make schemas-check` on the reference machine |

## Verification

A test regenerates the bundle into a scratch directory and compares every file to
the committed one; a second test recomputes the `toolchain.json` digest and each
manifest `data_schema.digest`; a third diffs the locator set against the branch
point and asserts every added locator is optional. The offline run is a manual
gate of this repository, recorded in the release notes; no CI job is claimed by
this requirement.

## Dependencies

- **Upstream**: [FR-002](../functional/FR-002-semantic-data-schemas.md), [FR-003](../functional/FR-003-semantic-manifest-contract.md)
- **Downstream**: the release gauntlet of this module
