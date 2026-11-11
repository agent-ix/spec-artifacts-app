---
id: SR-013
title: "Code review — import_types and the iso $ref (PLAT-1391)"
type: SpecReview
analysis: code-review
scope: "agent-ix/spec-artifacts-app; git diff origin/main...6680e0f (PR #30): scripts/build_mappings.py, spec_artifacts_app/, tests/, typespec/main.tsp"
review_set: subset
---
# SR-013: Code review — import_types and the iso $ref (PLAT-1391)

## Summary

Ticket: PLAT-1391. PR agent-ix/spec-artifacts-app#30 at `6680e0f`, one commit.
The manifest gains `semantic.import_types`, `RequirementRef.source` becomes
`ImportedTypeRef | IsoRequirement` where `IsoRequirement` is an `anyOf` of `$ref`s
to six iso types, the `imported_types` workaround leaves `mappings.yaml`, its
schema and its generator, and three engine-boundary tests shell out to the
`quire` CLI.

Evidence gathered:

- Acceptance, quire CLI 0.40.0 (engine 0.56.0): `quire validate --module <PR
  spec_artifacts_app> --module ~/.ix/filament/modules/spec-artifacts-iso doc.md`
  prints no `semantic.unused-import` and no `semantic.unknown-import-type`. The
  same command over the `origin/main` module prints
  `semantic.unused-import: import agent-ix/spec-artifacts-iso is referenced by no
  $ref of the module's data schemas`.
- Engine logic (quire-rs `src/loader/mod.rs` 1896-1950 at origin/main): each
  `import_types` name is checked against the provider's `exports`; a listed name
  with no `$ref` produces no diagnostic. `$ref` type names come from the URL file
  stem (`resolver.rs` `type_name_of`). So listing `master-requirements` (an iso
  export) with no `$ref` is silent and correct, and omitting
  `MasterRequirements.json` from the `anyOf` is necessary: a `$ref` to it would be
  named `MasterRequirements`, which iso does not export.
- The six `$ref` URLs match the `$id` of iso's own schemas on
  spec-artifacts-iso `origin/main` and in the installed 0.3.0 module exactly.
- `{module, type}` data still validates: Python `jsonschema` `anyOf`
  short-circuits on the `ImportedTypeRef` arm.
- `node scripts/generate-schemas.mjs --check` (offline npm install from the
  local cache, scratch copy): 39 schemas match the committed output.
- Full suite with the quire 0.56.0 wheel from internal-pypi on PYTHONPATH, in a
  scratch copy with node_modules: 70 passed, 1 deselected
  (`test_the_wheel_the_sdist_and_the_npm_tarball_carry_the_same_payload`, which
  needs `poetry run poe build` in a poetry env; not run).
- The negative test (a module copy with the one `$ref` removed) and the shipped
  module together give the ticket's used/no-warning and unused/warning pair.

## Verdict

The engine-side intent is met: the warning is gone, nothing new is reported,
and the `$ref` form matches iso's `$id`s. Not mergeable as is: the repo's own
locked quire bindings cannot load the changed module (FND-001), and the new
engine tests fail in the repo's CI (FND-003). FND-002 is a real schema-shape
defect that is latent today because the engine does not validate artifact-type
records.

## Findings

| ID | Severity | Summary | Refs |
|----|----------|---------|------|
| FND-001 | high | `pyproject.toml` pins `quire = ^0.50.0` and `poetry.lock` locks 0.50.0. Bindings before 0.56.0 refuse the PR module: with quire 0.53.0, `Registry.load_from` returns `[]` for the PR module and `['Application Spec', 'ApplicationSpec']` for `origin/main`. With `import_types` removed, 0.53.0 still drops `ApplicationSpec`, so both the new key and the cross-package `$ref` need the newer engine. `import_types` landed in quire-rs f618683 (#638), first tagged v0.56.0, and the quire 0.56.0 wheel is on internal-pypi. With it the suite passes (70 passed). The PR must bump the pin to `^0.56.0` and regenerate the lock. | pyproject.toml:36; poetry.lock:934-935 |
| FND-002 | medium | `IsoRequirement` is emitted as a sealed empty object (`type: object`, `properties: {}`, `unevaluatedProperties: {not: {}}`) around the `anyOf`. The engine strips every `$ref` under an import base to an accept-anything subschema (quire-rs `resolver.rs` `without_import_refs`), so with no evaluated properties the engine's validator accepts only `{}`. As a result `RequirementRef.source` admits `{}` (on main it required `module` and `type`) and rejects any real ISO requirement record. In the repo's Python harness a malformed `source` raises `Unresolvable: .../spec-artifacts-iso/StR.json` instead of a validation error. The "opaque subschema" claim does not hold for this shape. | spec_artifacts_app/schemas/IsoRequirement.json:4-8; spec_artifacts_app/schemas/RequirementRef.json:12-20; typespec/main.tsp:315-332 |
| FND-003 | medium | The three new engine tests need `quire` on PATH and spec-artifacts-iso installed at `~/.ix/filament/modules`. If the iso module is missing they `pytest.fail`, and a missing `quire` raises FileNotFoundError. agent-ix/python-service-actions `semantic-module-ci.yml` installs the quire CLI but not the iso module, so these tests fail in the repo's CI. They also read the machine's installed module root, which FR-003 forbids for the import graph because the result depends on what a developer has installed. Resolve iso from a declared dependency (internal-pypi carries `spec-artifacts-iso`) at the pinned manifest version. | tests/test_engine_boundary.py:127-160 |
| FND-004 | low | The new comment `#: The one model that carries a $ref into an imported package (FR-002-AC-10).` produces a new `quire matrix` warning: `[trace-id-outside-marker] FR-002-AC-10 is written in a comment ... at tests/test_schema_emission.py:37`. | tests/test_schema_emission.py:37 |
