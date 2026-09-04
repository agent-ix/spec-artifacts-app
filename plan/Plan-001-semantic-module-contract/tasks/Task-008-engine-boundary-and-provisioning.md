---
id: Task-008
title: "IT-002 — Quire provisioning, the no-vacuous-skip policy, and the engine boundary"
type: Task
status: pending
track: C
priority: P0
relationships:
  - target: ix://agent-ix/spec-artifacts-app/IT-002
    type: references
  - target: ix://agent-ix/spec-artifacts-app/FR-003
    type: references
  - target: ix://agent-ix/spec-artifacts-app/TC-013
    type: verifies
  - target: ix://agent-ix/spec-artifacts-app/TC-017
    type: verifies
  - target: ix://agent-ix/spec-artifacts-app/TC-034
    type: verifies
---
# Task-008: IT-002 — Quire provisioning, the no-vacuous-skip policy, and the engine boundary

## Scope

The Quire engine boundary, and the environment policy that decides what happens
when the engine is not there.

## Subtasks

- [ ] **`make dev-quire`.** Installs `quire >= 0.46.0` — the first wheel exposing `extract_semantic` — from the local `pypi.ix` index. `quire` is *not* a declared dependency: no index a repository may commit against carries it, and agent-ix/quire-rs#392 is the blocking issue.
- [ ] **Fail, never skip.** When the engine is absent the semantic tests fail, naming the provisioning command and the blocking issue. A skipped row is not coverage, and a suite that reports green because a gate could not run is the failure mode this whole ticket exists to remove.
- [ ] **The schema registry fixture.** A 2020-12 validator factory over the committed `schemas/` directory plus the semantic-core package the pinned toolchain installs, so every `$ref` resolves locally and a record test validates against the real shipped bytes.
- [ ] **Load, validate, extract.** `Registry.load_from` lists every declared artifact type; `validate_document` passes every skeleton; `extract_semantic` returns a record for each with zero error diagnostics.
- [ ] **The legacy-manifest load.** The fixture with no block and no `data_schema` registers the same artifact types.
- [ ] **The digest-refusal row as a strict expected failure.** One hex digit altered in a `data_schema.digest` should refuse the load. Recorded `xfail(strict=True)` naming agent-ix/quire-rs#394 and agent-ix/quire-rs#221 — never a skip, never a silent pass. A strict expected failure that starts passing fails the suite, so a fixed engine announces itself.

## Deliverables

- `tests/conftest.py` (provisioning policy, schema registry, module fixtures)
- `pyproject.toml` poe task `dev-quire`; `Makefile` target
- Tests for TC-013, TC-017, TC-034

## Notes

- Measured, not assumed: the engine at 0.46.0 does load this module, does validate
  all three skeletons, and does extract five `FieldDecl` rows from both the table
  and the fence form. What it does *not* do is validate the artifact-type record
  against `data_schema` (agent-ix/quire-rs#393), which is why this module's own
  suite is the record oracle.
