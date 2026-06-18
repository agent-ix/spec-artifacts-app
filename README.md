# spec-artifacts-app

> Filament Module: application/composite spec artifact templates (ApplicationSpec, MasterRequirements) — absorbed spec-master-requirements

Agent-IX Filament module loaded by [`quire-cli`](https://github.com/agent-ix/quire-cli) and [`ix-spec`](https://github.com/agent-ix/ix-spec).

## Installing quire-cli

This module is consumed by the `quire` binary from [`quire-cli`](https://github.com/agent-ix/quire-cli), published on the public npm registry, so no auth or registry config is needed:

```bash
npm install -g @agent-ix/quire-cli
```

See https://github.com/agent-ix/quire-cli#install for details.

## Artifact types provided

| Kind | ID pattern | Description |
|------|-----------|-------------|
| `ApplicationSpec` | `ApplicationSpec-{next:03d}` | Doc-backed composite application spec (`app-spec` grammar); frontmatter requires `id`/`title`/`type`; links via `contains`, `depends_on`, `references`. |
| `MasterRequirements` | `MasterRequirements-{next:03d}` | Master requirements artifact under the `app-spec` grammar (absorbed from `spec-master-requirements`); frontmatter requires `id`/`title`/`type`; links via `aggregates`, `depends_on`, `references`. |

This module also defines the `Application Spec` archetype (kind `application-spec`): a doc-backed, membership-supporting composite that expects `MasterRequirements`, `StR`, `FR`, and `NFR` artifacts.

## How this module is used

### With ix-spec (recommended)

```bash
ix-spec plugin install path:../spec-artifacts-app
ix-spec catalog list
ix-spec catalog show ApplicationSpec
ix-spec write . --types ApplicationSpec
ix-spec review
```

See https://github.com/agent-ix/ix-spec.

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
make test             # run pytest
make lint             # ruff + black check
make format           # ruff + black format
make build            # build wheel + sdist under dist/
make local-publish    # build and publish to local PyPI (pypi.ix)
make update-lock      # update poetry.lock
```

CI requires the `GCP_SERVICE_ACCOUNT_KEY` secret plus `GCP_REGION`, `GCP_PROJECT_NAME`, and `GCP_PYPI` variables for Artifact Registry publishing.
