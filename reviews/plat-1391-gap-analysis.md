---
id: SR-014
title: "Gap analysis — import_types and the iso $ref (PLAT-1391)"
type: SpecReview
analysis: gap-analysis
scope: "agent-ix/spec-artifacts-app; git diff origin/main...6680e0f (PR #30): spec/functional/FR-002, FR-003, FR-004, spec/tests.md, spec_artifacts_app/, tests/, typespec/main.tsp"
review_set: subset
---
# SR-014: Gap analysis — import_types and the iso $ref (PLAT-1391)

## Summary

Ticket: PLAT-1391. Planless gap analysis of PR agent-ix/spec-artifacts-app#30
at `6680e0f`, scoped to the diff. Plan completion: not assessed.

`quire matrix --scope .` (quire 0.40.0, engine 0.56.0) on the PR head:

- FR-003-AC-4: tagged by `test_every_import_types_entry_is_exported_by_its_provider`,
  `test_the_shipped_module_loads_without_an_unused_import_diagnostic`,
  `test_an_import_no_data_schema_references_is_reported_unused` (new) and the two
  existing `tests/test_imports.py` tests. Each new clause of the rewritten AC
  (each import type exported, a `$ref` present, no `semantic.unused-import`) has a
  test that would fail without it.
- FR-002-AC-10: tagged by `test_no_cross_module_ref_and_no_imported_field_is_duplicated`,
  which now admits a cross-module `$ref` only from `IsoRequirement` and only to a
  listed import type.
- FR-002-CON-2 / TC-003: `test_exported_schemas_carry_the_stable_id_and_every_ref_resolves_offline`
  admits a `$ref` under a pinned import's base, matching the relaxed constraint.
- FR-003-AC-9: tagged by `test_master_requirements_is_imported_from_iso_and_never_declared_here`,
  which now reads `semantic.import_types`.

Code with no owning requirement: none. `IsoRequirement` is owned by
FR-002-AC-10 and FR-003-AC-4, and `semantic.import_types` by FR-003-AC-4 and
AC-9. No stubs and no coverage inflation in the new tests. The FR-003-AC-1 text
no longer matches its test; that is recorded in the spec-review artifact
(SR-015), not here.

## Verdict

The AC-to-test chain for the change is intact. No gaps.

## Findings

| ID | Severity | Summary | Refs |
|----|----------|---------|------|
| FND-001 | low | No findings (placeholder) | - |
