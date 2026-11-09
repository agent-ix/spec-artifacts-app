---
id: SR-011
title: "Code review — app imports iso master-requirements (PLAT-214)"
type: SpecReview
analysis: code-review
scope: "agent-ix/spec-artifacts-app; git diff origin/main...59c325f (PR #28): README.md, package.json, pyproject.toml, scripts/build_mappings.py, spec/, spec_artifacts_app/, tests/, typespec/main.tsp"
review_set: subset
---
# SR-011: Code review — app imports iso master-requirements (PLAT-214)

## Summary

Ticket: PLAT-214. PR agent-ix/spec-artifacts-app#28 at `59c325f`, one commit.
The module drops its own `MasterRequirements` artifact type, export, data and
frontmatter schemas, skeleton, mapping entry, TypeSpec model and
`master-requirements` doc kinds, and references the iso type through
`composition.expected_artifacts` and `mappings.yaml` `imported_types`. New
criteria FR-003-AC-8 and FR-003-CON-4, backed by TC-045.

Checks made:

- No residual reference to the removed app-local type outside historical
  `spec/reviews/` and `reviews/` (case-insensitive grep over the tree).
- `master-requirements` is the exact spelling `spec-artifacts-iso` main exports
  and declares as an artifact type name; iso PR #68 pins that same spelling.
- `scripts/build_mappings.py --check` and `scripts/build_legacy_manifest.py --check`
  both pass. Neither generator needs semantic-core (pyyaml only).
- With semantic-core 0.3.3 linked in, the TypeSpec generator check reports only
  `ApplicationSpec.json` and `Provenance.json` as differing, and the byte diff is
  the semantic-core version digit (`2` vs `3`). No `MasterRequirements.json` is
  emitted and no support schema is missing, so the committed schema set matches
  `main.tsp`.
- No iso content is copied into this repo; the diff is deletions plus spec text.
- No other open PR in the repo, so no id collision with open work.

Focused tests (quire 0.52.1 wheel, no semantic-core installed): the same 7
tests fail on `origin/main` and on the PR head, all for missing semantic-core
0.3.2 `$ref`s. No failure is introduced by the PR.

## Verdict

Correct and complete for its purpose. One medium and two low findings, all
small edits inside this PR (the untagged FR-003-CON-4 is recorded in the
gap-analysis artifact, SR-012). `RequirementKind` staying `StR, US, FR, NFR, IT, TC`
is not a defect: the `## Requirements` table lists requirement rows by
`^(StR|US|FR|NFR|IT|TC)-\d+$` id, and a master-requirements document is the root
document, not a requirement row. `MasterRequirements` was never a
`RequirementKind` on `origin/main` either.

## Findings

| ID | Severity | Summary | Refs |
|----|----------|---------|------|
| FND-001 | medium | TC-045 does not test the `MasterRequirements` spelling for doc kinds. FR-003-CON-4 and FR-003-AC-8 forbid both spellings; the test normalises spelling for artifact types and exports but checks doc kinds with an exact `"master-requirements" not in declared_kinds`, so a `MasterRequirements` doc kind passes. | tests/test_manifest.py:84-87 |
| FND-002 | low | FR-003-AC-8 reuses a retired id. Committed reviews in this repo (`reviews/26-09-04-gap-analysis-3.md:175`, `spec/reviews/3-semantic-module-contract/*.md`) bind FR-003-AC-8 to the former digest-refusal expected-failure criterion (TC-017), so anyone mining by id conflates the two. The next unused id is FR-003-AC-9. | spec/functional/FR-003-semantic-manifest-contract.md:165 |
| FND-003 | low | Leftover plural wording after the de-duplication: "The model SHALL carry `purpose: Section` as their one required section". | spec/functional/FR-002-semantic-data-schemas.md:134 |
