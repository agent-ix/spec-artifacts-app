---
id: SR-012
title: "Gap analysis — app imports iso master-requirements (PLAT-214)"
type: SpecReview
analysis: gap-analysis
scope: "agent-ix/spec-artifacts-app; git diff origin/main...59c325f (PR #28): spec/functional/FR-002, FR-003, FR-005, spec/tests.md, spec_artifacts_app/manifest.yaml, spec_artifacts_app/mappings.yaml, typespec/main.tsp, tests/"
review_set: subset
---
# SR-012: Gap analysis — app imports iso master-requirements (PLAT-214)

## Summary

Ticket: PLAT-214. Planless gap analysis of PR agent-ix/spec-artifacts-app#28 at
`59c325f`, scoped to the diff. Plan completion: not assessed.

The computed matrix (`quoin matrix --json`, quoin 0.29.1) was taken on
`origin/main` and on the PR head and compared per criterion:

- FR-003-AC-8 (new): tagged by
  `test_master_requirements_is_imported_from_iso_and_never_declared_here`.
- FR-003-CON-4 (new): untagged (FND-001).
- FR-005-AC-2 (TC-029): loses the removed
  `test_the_sysml_alternate_form_works_for_master_requirements_too` and stays
  tagged by three tests, among them
  `test_the_sysml_alternate_declares_the_same_fields_in_the_same_order`, the
  TC-029 ApplicationSpec case. The removed test covered the MasterRequirements
  half of the old criterion, which the PR rewrote to ApplicationSpec only.
- No other criterion's binder set changed, so no removed test leaves a
  requirement untraced. The remaining untagged Test-method criteria
  (FR-003-AC-3, NFR-001-M-1, NFR-001-M-2) are untagged on `origin/main` too.

Code with no owning requirement: none added. The new
`IMPORTED_TYPES` entry and the manifest composition change are owned by
FR-003-AC-8. No stub or coverage inflation in the new test.

## Verdict

One medium gap, fixed by adding one id to an existing trace marker. Otherwise
the AC-to-test chain for the change is intact.

## Findings

| ID | Severity | Summary | Refs |
|----|----------|---------|------|
| FND-001 | medium | FR-003-CON-4 is untagged. The TC-045 test is marked `trace("TC-045", "FR-003-AC-8")` only, so `quoin matrix` reports FR-003-CON-4 `untagged` while `spec/tests.md` marks it Complete via TC-045. | tests/test_manifest.py:74, spec/tests.md:112 |
