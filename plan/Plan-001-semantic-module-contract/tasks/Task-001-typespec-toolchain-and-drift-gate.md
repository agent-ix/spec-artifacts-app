---
id: Task-001
title: "FR-002 — TypeSpec toolchain, schema generator, drift gate and packaging"
type: Task
status: done
track: A
priority: P0
relationships:
  - target: ix://agent-ix/spec-artifacts-app/FR-002
    type: references
  - target: ix://agent-ix/spec-artifacts-app/NFR-001
    type: references
  - target: ix://agent-ix/spec-artifacts-app/TC-004
    type: verifies
  - target: ix://agent-ix/spec-artifacts-app/TC-006
    type: verifies
  - target: ix://agent-ix/spec-artifacts-app/TC-008
    type: verifies
  - target: ix://agent-ix/spec-artifacts-app/TC-030
    type: verifies
  - target: ix://agent-ix/spec-artifacts-app/TC-033
    type: verifies
---
# Task-001: FR-002 — TypeSpec toolchain, schema generator, drift gate and packaging

## Scope

Everything that turns a TypeSpec source into shipped schema bytes, and everything
that refuses a tree where source and bytes disagree. The models themselves are
Task-003; this task must work against a source that compiles.

## Subtasks

- [x] **Pin the toolchain.** `@typespec/compiler` 1.15.0, `@typespec/json-schema` 1.15.0 and `@agent-ix/semantic-core` 0.1.0 as exact `devDependencies`. No `.npmrc`, no `file:`/`link:`, no upper bound.
- [x] **Resolve the lockfile against public npm.** Everything but the `@agent-ix` scope resolves from `registry.npmjs.org`; only the scoped package carries an `npm.ix` URL, because that is the only registry serving it.
- [x] **Author the source shell.** `typespec/main.tsp`, namespace `AgentIx.SpecArtifactsApp`, `@jsonSchema` base embedding the manifest `version`; `typespec/tspconfig.yaml` with `seal-object-schemas: true`.
- [x] **Write `scripts/generate-schemas.mjs`.** Node built-ins only. Compile with `tsp compile`; keep the files whose `$id` starts with the module base and discard the re-emitted semantic-core files; rewrite any relative `$id`/`$ref`; record every rewrite in `toolchain.json`; render two-space JSON with a trailing newline.
- [x] **Leave the hand-authored frontmatter schemas alone.** `*-frontmatter.schema.json` lives in the same directory and is not a projection: the generator neither deletes it nor reports it stale.
- [x] **Fail loudly.** Exit non-zero without touching committed output when `tsp compile` fails, when no module model is emitted, when Node is older than 20, and when the `@jsonSchema` base version differs from the manifest `version` — naming both values.
- [x] **Digest rewrite.** Rewrite `manifest.yaml`'s `data_schema.digest` values textually so the file's comments and anchors survive.
- [x] **`--check` mode.** Writes no file. Exits non-zero naming each file that differs, is stale, or whose manifest digest disagrees with the shipped bytes.
- [x] **Wire the targets.** `make schemas` and `make schemas-check` as poe tasks.
- [x] **`.gitattributes`.** `*.json`, `*.tsp`, `*.yaml`, `*.md` marked `eol=lf`, so a checkout under `autocrlf` cannot change the digested bytes.
- [x] **Packaging.** `pyproject.toml` `include` and `package.json` `files` both name the whole payload — manifest, schemas, skeletons, mappings — and no toolchain file.

## Deliverables

- `typespec/tspconfig.yaml`, `typespec/main.tsp` (shell), `scripts/generate-schemas.mjs`, `.gitattributes`
- `package.json` / `package-lock.json` with the three exact pins
- `pyproject.toml` poe tasks `schemas`, `schemas-check`; `Makefile` targets
- Tests for TC-004, TC-006, TC-008, TC-030, TC-033

## Notes

- FR-002-CON-5: the `$id` base embeds the manifest `version` by intent, so a bump
  edits both in one commit and re-runs `make schemas`. No test hard-codes the
  version segment; every assertion reads it from `manifest.yaml`.
- `@agent-ix/semantic-core` resolves only from the registry the machine's npm
  config routes the scope to (agent-ix/filament-core-data#11), so `make schemas`
  runs locally rather than in CI. NFR-001 Scope records this as a precondition,
  not as a hidden assumption.
- Unblocks: Task-003 (a compiling source), and Gate 1.
