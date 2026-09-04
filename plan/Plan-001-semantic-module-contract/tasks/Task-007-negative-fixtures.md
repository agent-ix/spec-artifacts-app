---
id: Task-007
title: "FR-005 — The eight negative fixtures and the accepted-fixture gate"
type: Task
status: done
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

- [x] **Author the eight fixtures**, each declaring `expect` and `because` in frontmatter: a missing required section; a typed table with a wrong column header; a row id with the wrong prefix; a row id repeated in one table; a section carrying both a typed table and a `sysml` fence; an `ImportedTypeRef` naming an undeclared module; a `### <clauseId>` heading owning two fences; an `ocl` fence owned by no `###` heading.
- [x] **One rule each.** A fixture that violates two rules cannot tell you which one the refusal identified.
- [x] **The accepted-fixture gate.** A fixture the check its `expect` names does not refuse fails the suite naming the fixture and the expectation. A negative fixture that passes is a gate that is not gating.
- [x] **Route each fixture to the right check.** Each fixture's `expect` names the surface that must refuse it — `validate.*` for the archetype's locator asserts, `mapping.*` for the reference mapping — and the test dispatches on that rather than trying both and accepting either. Where the mapping *also* knows the rule, it is asserted separately: a fixture the archetype catches is not thereby excused from the oracle, and dispatching only on `expect` is what left nine of the oracle's diagnostics unexecuted until the code review counted them.

## Deliverables

- `tests/fixtures/negative/*.md` (eight files)
- Tests for TC-026, TC-035

## Notes

- The extra-property case has **no fixture**, and deliberately so: the mapping
  builds a record from the properties it declares, so no authored document can
  produce an undeclared one. It is exercised by mutating a good record instead
  (TC-009), and it is still the sealing that refuses it — without
  `unevaluatedProperties` the mutation would pass and the gate would report
  green.
