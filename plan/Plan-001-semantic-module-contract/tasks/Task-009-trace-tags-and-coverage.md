---
id: Task-009
title: "FR-001 re-verification, trace tags, and coverage reconciliation"
type: Task
status: pending
track: C
priority: P1
relationships:
  - target: ix://agent-ix/spec-artifacts-app/FR-001
    type: references
  - target: ix://agent-ix/spec-artifacts-app/NFR-001
    type: references
  - target: ix://agent-ix/spec-artifacts-app/TC-031
    type: verifies
  - target: ix://agent-ix/spec-artifacts-app/TC-036
    type: verifies
---
# Task-009: FR-001 re-verification, trace tags, and coverage reconciliation

## Scope

The rows that were already there, the tags that bind the new ones, and the number
that says whether any of it landed.

## Subtasks

- [ ] **FR-001 at 0.2.0.** The manifest still validates against the bundled FR-035 schema with the block and the references present. Neither the missing-library nor the missing-schema branch skips: a gate that reports "passed" because it could not run is not a gate.
- [ ] **Trace tags on every test.** `@pytest.mark.trace("TC-0NN", "<criterion>")` directly above the test function, and the `trace` marker registered so `filterwarnings = ["error"]` does not turn an unregistered marker into a failure.
- [ ] **Check the three ways a tag binds to nothing.** A `black`-wrapped marker binds nothing silently; a tag on a module docstring or a plain helper binds nothing; and a bare `TC-` id in a comment binds to the *next* symbol, so a comment explaining an untagged test mints the very trace it disclaims. Grep for all three before opening the PR.
- [ ] **Reconcile the numbers.** Run `quire coverage` and state what its headline counts against what `spec/tests.md` counts — they are different populations, and saying so is the point.
- [ ] **Record the manual offline gate.** NFR-001 metric 2 is a manual run; it is recorded as such and no CI job is claimed for it.

## Deliverables

- Trace markers across the whole suite
- `pyproject.toml` `markers` entry for `trace`
- Tests for TC-031, TC-036

## Notes

- Three ways a written tag binds to nothing have all been seen in this program.
  Grepping for them is cheaper than discovering a green matrix backed by nothing.
