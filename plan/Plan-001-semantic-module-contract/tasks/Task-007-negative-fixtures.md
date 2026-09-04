---
id: Task-007
title: "FR-005 — The eight negative fixtures and the accepted-fixture gate"
type: Task
status: pending
track: B
priority: P1
relationships:
  - target: ix://agent-ix/spec-artifacts-app/FR-005
    type: references
  - target: ix://agent-ix/spec-artifacts-app/TC-026
    type: verifies
  - target: ix://agent-ix/spec-artifacts-app/TC-035
    type: verifies
---
# Task-007: FR-005 — The eight negative fixtures and the accepted-fixture gate

## Scope

One fixture per rule the skeletons demonstrate, each violating exactly that rule,
and the gate that fails when one of them is accepted.

## Subtasks

- [ ] **Author the eight fixtures**, each declaring `expect` and `because` in frontmatter: a missing required section; a typed table with a wrong column header; a row id with the wrong prefix; a row id repeated in one table; a section carrying both a typed table and a `sysml` fence; an `ImportedTypeRef` naming an undeclared module; a `### <clauseId>` heading owning two fences; an `ocl` fence owned by no `###` heading.
- [ ] **One rule each.** A fixture that violates two rules cannot tell you which one the refusal identified.
- [ ] **The accepted-fixture gate.** A fixture the check its `expect` names does not refuse fails the suite naming the fixture and the expectation. A negative fixture that passes is a gate that is not gating.
- [ ] **Route each fixture to the right check.** Some are refused by `validate_document` (the locator asserts), some by the reference mapping, and one by the schema. The `expect` value says which, and the test dispatches on it rather than trying all three.

## Deliverables

- `tests/fixtures/negative/*.md` (eight files)
- Tests for TC-026, TC-035

## Notes

- The extra-property case is refused by the schema, and only because the models
  are sealed. Without `unevaluatedProperties` that fixture would pass and the
  gate would report green.
