# spec-artifacts-app

> Filament Module: application/composite spec artifact templates (ApplicationSpec, MasterRequirements) — absorbed spec-master-requirements

Agent-IX Filament module loaded by [`quire-cli`](https://github.com/agent-ix/quire-cli) and [`quoin`](https://github.com/agent-ix/quoin).

## Installing quire-cli

`@agent-ix` packages are published to public npm. Install the CLI globally:

```bash
npm install -g @agent-ix/quire-cli
```

See https://github.com/agent-ix/quire-cli#install for details.

## Install this module via npm

This module is also published as a config-only npm package: `@agent-ix/spec-artifacts-app`.
The package root **is** the Filament module (`manifest.yaml` + schemas/skeletons),
so it works directly as a `--module` target or via quoin's `package:` source.

```bash
npm install @agent-ix/spec-artifacts-app
```

```bash
# quoin — resolve the module from npm by name
quoin plugin install package:@agent-ix/spec-artifacts-app

# or point any tool at the installed package root
quire validate spec/**/*.md --module node_modules/@agent-ix/spec-artifacts-app
```

## The semantic contract

Since 0.2.0 this module declares a **semantic data model per artifact type**, so a
consumer can read an application composite as a typed record instead of
re-parsing its prose:

- `typespec/main.tsp` is the source, importing `@agent-ix/semantic-core` 0.1.0.
- `schemas/<Model>.json` is the emitted JSON Schema 2020-12 bundle (39 files),
  with `schemas/toolchain.json` recording the projection's provenance.
- `manifest.yaml` carries the quoin FR-070 `semantic` block, and every artifact
  type references its schema by path and SHA-256 digest.
- `mappings.yaml` declares, per record property, which Markdown form fills it and
  whether that form round-trips byte-for-byte.
- `skeletons/` are executable fixtures: a typed `## Properties` table, a `sysml`
  fence as its alternate form, and `ocl` clauses under `## Invariants`.

An application composite **references** what other modules own rather than
restating it: an aggregated requirement or a data source is an
`{module, type}` pair plus an id, never a copy of the imported type's fields.

## What's in this module

This module gives you the top-level document kinds for specifying a whole application — the documents that gather requirements together and describe the system as a whole. They sit above the individual requirement artifacts (`StR`, `FR`, `NFR`, …) and tie them into one specification.

| Kind | Type | What it's for |
|:-----|:-----|:--------------|
| `ApplicationSpec` | Application Spec | The top-level document for an application — describes the system as a whole and gathers together the requirements and specs that make it up. |
| `MasterRequirements` | Master Requirements | The front page of a specification — its purpose, scope, and the set of requirements it rolls up. |


## How this module is used

### With quoin (recommended)

```bash
quoin plugin install path:../spec-artifacts-app
quoin catalog list
quoin catalog show ApplicationSpec
quoin write . --types ApplicationSpec
quoin review
```

See https://github.com/agent-ix/quoin.

### With quire-cli directly

```bash
quire schema ApplicationSpec --module ./spec_artifacts_app
quire validate spec/**/*.md --module ./spec_artifacts_app
quire extract <DOC> --module ./spec_artifacts_app --archetype ApplicationSpec
```

See https://github.com/agent-ix/quire-cli#usage-instructions.

## Development

- **Library:** `spec_artifacts_app` (flat layout, Python 3.13+, [Poetry](https://python-poetry.org/))
- **Build/CI:** GitHub Actions; dynamic Git-tag-based versioning; publishes wheel + sdist to Google Artifact Registry via `twine upload -r internal-pypi`.

```bash
make install          # install deps in Poetry venv
make semantic-install # npm ci for the pinned TypeSpec toolchain
make dev-quire        # install the Quire wheel the semantic tests need
make schemas          # emit the JSON Schemas and refresh the derived files
make schemas-check    # fail when the committed schemas or digests drift
make test             # run pytest
make lint             # ruff + black check
make format           # ruff + black format
make build            # build wheel + sdist under dist/
make local-publish    # build and publish to local PyPI (pypi.ix)
make update-lock      # update poetry.lock
```

Two environment preconditions, both deliberate and both recorded in NFR-001:

- `@agent-ix/semantic-core` resolves only from the registry your npm
  configuration routes the `@agent-ix` scope to. The repository carries no
  `.npmrc`, so the routing is your machine's; `agent-ix/filament-core-data#11`
  tracks the public publish.
- The Quire wheel exposing `extract_semantic` is on no index this repository may
  commit against (`agent-ix/quire-rs#392`), so `make dev-quire` provisions it.
  The semantic tests **fail** rather than skip when it is absent, because a
  skipped row is not coverage.

The offline, no-network gate is a manual procedure: see
[docs/offline-gate.md](docs/offline-gate.md).

CI requires the `GCP_SERVICE_ACCOUNT_KEY` secret plus `GCP_REGION`, `GCP_PROJECT_NAME`, and `GCP_PYPI` variables for Artifact Registry publishing.
