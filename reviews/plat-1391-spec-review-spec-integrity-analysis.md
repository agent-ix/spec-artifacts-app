---
id: SR-015
title: "Spec integrity — import_types and the iso $ref (PLAT-1391)"
type: SpecReview
analysis: integrity
scope: "agent-ix/spec-artifacts-app; git diff origin/main...6680e0f (PR #30): spec/functional/FR-002-semantic-data-schemas.md, spec/functional/FR-003-semantic-manifest-contract.md, spec/functional/FR-004-markdown-mappings-and-imports.md, spec/spec.md, spec/tests.md"
review_set: subset
---
# SR-015: Spec integrity — import_types and the iso $ref (PLAT-1391)

## Summary

Ticket: PLAT-1391. Consistency review of the spec edits in PR
agent-ix/spec-artifacts-app#30 at `6680e0f`.

- `quire validate` on the five changed files gives the same result as on
  `origin/main`: the same EARS warnings shifted by four lines and the existing
  `tests.md` `functional_coverage` column assertion. No new diagnostic.
- No requirement, AC or TC id was added, removed or renumbered. The edited rows
  are FR-002-CON-2, FR-002-AC-10, FR-003-AC-4, FR-003-AC-9, TC-010 and TC-045.
- FR-002-AC-10, FR-002-CON-2 and TC-010 agree with each other and with the
  emitted schemas: the only cross-module `$ref` is in `IsoRequirement`, under the
  pinned iso base, naming listed types.
- FR-003-AC-9 and TC-045 agree with the manifest.
- FR-004 Inputs and the `spec.md` Out of Scope removal are consistent with the
  move of the type list into the manifest.

## Verdict

One high finding: FR-003 still fixes the `semantic` block at eight keys, and the
manifest and its test now have nine. One low wording leftover.

## Findings

| ID | Severity | Summary | Refs |
|----|----------|---------|------|
| FND-001 | high | FR-003 still fixes the `semantic` block at eight keys. Behavior says "exactly the eight keys listed in Outputs", Outputs does not name `import_types`, FR-003-AC-1 reads "key set equals exactly `{contract_version, package, exports, imports, targets, mappings, compatibility_posture, legacy_forms}`", and TC-011 says "exactly the eight declared keys". The PR adds `import_types` to the manifest, and `tests/test_manifest.py` `ADMITTED_SEMANTIC_KEYS`, which is bound to FR-003-AC-1, now asserts nine keys. The AC contradicts both the code and its own test. | spec/functional/FR-003-semantic-manifest-contract.md:50,70,162; spec/tests.md:169; tests/test_manifest.py:18-27 |
| FND-002 | low | FR-003 Behavior still says "If a shipped skeleton, negative fixture, or `mappings.yaml` entry names an `ImportedTypeRef` ...". FR-003-AC-4 dropped `mappings.yaml` from that list, and `mappings.yaml` no longer carries import references. | spec/functional/FR-003-semantic-manifest-contract.md:111 |
