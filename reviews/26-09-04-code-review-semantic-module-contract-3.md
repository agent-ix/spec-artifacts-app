---
id: SR-009
title: "Code review — semantic module contract for the application artifact types (#3)"
type: SpecReview
analysis: code-review
scope: "typespec/, scripts/generate-schemas.mjs, scripts/build_mappings.py, scripts/build_legacy_manifest.py, spec_artifacts_app/, tests/, spec/, plan/Plan-001-semantic-module-contract/, Makefile, pyproject.toml, package.json, package-lock.json"
review_set: subset
---
# SR-008: Code review — semantic module contract (#3)

## Summary

Reviewed the whole `spec/3-semantic-module-contract` branch against `origin/main`
(5 commits, 122 files): the TypeSpec source and its generator, the 39 emitted
JSON Schemas and `toolchain.json`, the 0.2.0 manifest with its FR-070 semantic
block and reference-form `data_schema`, the two derived-data scripts, the
`mappings.yaml`/`mappings.schema.json` pair, the three skeletons, the eight
negative fixtures, and the 44-case test suite, with an implementation-gap pass
over FR-001..FR-005, NFR-001, IT-002 and the Test Matrix. Every gate was run
rather than assumed.

One high finding: the branch rewrote `spec/tests.md`'s traceability tables with
a `Coverage Status` header while the engine's configured status column is
`Status`, so `quire coverage` reports `status-column-matches-nothing` and
**skips status classification entirely** — 59 of the 63 rows the branch marks
`✅ Complete` are unverifiable by the tool, and three of them (FR-004-AC-2,
FR-002-AC-8, FR-004-AC-6) are in fact only half-discharged. On `origin/main` the
column was `Status` and the diagnostic did not fire, so this change turned the
check off.

The mediums are the familiar "looks like evidence and is not" class the two
sibling migrations paid for: nine of the twenty diagnostics in the 938-line
mapping oracle are never executed, three negative fixtures that would exercise
two of them are dispatched away from the oracle by their own `expect` key, the
`prose_only` designation FR-004-AC-2 demands exists in the schema and in two
tests but in no data, and the 100% coverage gate measures four statements.

Nothing in this review was changed on the branch: the review reports, it does
not fix.

## Verdict

**FAIL** — one high finding (status classification silently disabled by the
matrix rewrite, with three overstated `✅ Complete` rows behind it). Gates at
the time of writing: `make lint` green (ruff + black, 17 files); `make
schemas-check` green (39 schemas, mappings and legacy fixture all match);
`poetry run pytest -q` 42 passed / 2 xfailed, coverage 100% over four
statements; `quire validate --scope . "spec/**/*.md" "plan/**/*.md"` zero
errors, nine EARS/quality grammar warnings in FR-003 and FR-004; `quire coverage
--scope .` 77/81 rows backed with the status column unread.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | high | The rewritten traceability tables head their status column `Coverage Status`, but the `functional-coverage` declaration's configured column is `Status`, so `quire coverage` emits `status-column-matches-nothing` and skips status classification — a row marked `✅ Complete` that is unbacked cannot be caught in either the 51-row functional table or the 8-row stakeholder/integration table. `origin/main`'s matrix used `Status` and the diagnostic did not fire, so the change disabled the check. The NFR table in the same document still uses `Status`, so the document is inconsistent with itself. FND-004, FND-005 and FND-006 are three `✅ Complete` rows this would have flagged. | spec/tests.md:73, spec/tests.md:161 |
| FND-002 | medium | Nine of the twenty diagnostics in the mapping oracle are never executed by any test (91% line coverage; 45 uncovered lines): `missing-required-section`, `table-columns-mismatch` (both copies), `row-cell-count` (both copies), `multiplicity-malformed`, `sysml-declaration-malformed`, `imported-type-malformed`, `undeclared-import-type`, `clause-fence-unterminated`, and `unknown-constraint-keyword`. These are the paths that decide whether a defect is reported or swallowed, and the closed constraint vocabulary's rejection branch is among them. | tests/support/reference_mapping.py:356, tests/support/reference_mapping.py:385, tests/support/reference_mapping.py:404, tests/support/reference_mapping.py:576, tests/support/reference_mapping.py:619, tests/support/reference_mapping.py:631, tests/support/reference_mapping.py:643, tests/support/reference_mapping.py:675, tests/support/reference_mapping.py:717, tests/support/reference_mapping.py:736, tests/support/reference_mapping.py:896 |
| FND-003 | medium | `missing-required-section.md`, `table-columns-mismatch.md` and `row-id-wrong-prefix.md` declare `expect: validate.*`, and the fixture test dispatches on that key, so those three documents are never handed to the mapping oracle. Running the oracle over them during this review shows each is refused with exactly one code — `missing-required-section`, `table-columns-mismatch`, `row-id-pattern` — so two of FND-002's dead branches already have a fixture that exercises them and nothing calls it. `test_each_negative_fixture_violates_exactly_one_rule` also skips those three, so FR-005-CON-2 is checked for five of the eight fixtures. | tests/test_negative_fixtures.py:64, tests/test_negative_fixtures.py:107 |
| FND-004 | medium | `prose_only` is declared in `mappings.schema.json` with a conditional that requires a `reason`, and two tests read it, but `scripts/build_mappings.py` never emits it, so no property of `mappings.yaml` carries it. FR-004-AC-2's "or carries `prose_only: true` with a reason" half, TC-022's stated title, and the schema conditional are all unreachable; both tests compute an empty `prose_only` set. Nor does any negative case prove the other half — "a section named by neither fails the suite naming the heading" — since the checks only iterate the shipped skeletons. The row reads `✅ Complete`. | spec_artifacts_app/mappings.schema.json:134, scripts/build_mappings.py:150, tests/test_mappings.py:107, tests/test_skeletons.py:67 |
| FND-005 | medium | FR-002-AC-8 requires the Python validator to "reject every negative fixture that produces a record at all"; TC-009 only mutates a good record with an undeclared `deployedAt` key. No negative fixture is ever passed through `schema_registry`. The clause is in fact vacuous — every fixture is refused before a record exists (FND-003) — but the criterion is written as a live obligation and the matrix marks it `✅ Complete`, so the reader is told evidence exists that does not. | tests/test_schema_emission.py:352, spec/functional/FR-002-semantic-data-schemas.md:245 |
| FND-006 | medium | FR-004-AC-6 requires each of the five defects to "fail the mapping naming the line **and yield no record**"; TC-025 asserts the codes, the positive line numbers, that three independent defects are reported together, and that the lines are ordered — nothing binds the no-partial-record half. This is the defect class SR-012 FND-002 fixed in `spec-artifacts-iso`: the "no record" claim needs a result name bound before the call and asserted to have stayed unbound, or it is prose. | tests/test_mappings.py:239, spec/functional/FR-004-markdown-mappings-and-imports.md:190 |
| FND-007 | medium | The 100% coverage gate measures `spec_artifacts_app` only — four statements in `__init__.py`. The 938-line mapping oracle, the 129-line import graph, `scripts/build_mappings.py` and `scripts/build_legacy_manifest.py` sit outside any coverage gate, which is why FND-002 was invisible until measured by hand. A separate, lower threshold over `tests/support/` and `scripts/` would be worth more than raising the existing one, which is calibrated for a four-statement package. | pyproject.toml:118 |
| FND-008 | medium | Five SpecReviews on the branch share `id: SR-001` (`base.md`, `ears-conformance.md`, `failure-domain.md`, `integrity.md`) and two share `SR-003` (`dependency.md`, `scope-boundary.md`). Ids are the addressable handle a disposition or a trace uses, so `SR-001` names four different documents and cannot be cited. `quire validate` does not check id uniqueness across a corpus, so nothing caught it. | spec/reviews/3-semantic-module-contract/base.md:2, spec/reviews/3-semantic-module-contract/integrity.md:2 |
| FND-009 | medium | `make schemas-check` runs in no automated gate. `make lint` is ruff + black only (the sibling `spec-artifacts-iso` folds `schemas-check` into lint), the pytest suite never invokes `build_mappings.py` or `build_legacy_manifest.py`, and `ci.yml` is `workflow_dispatch` delegating to the shared lib-CI. Neither derived-data script has a single test, so drift of `mappings.yaml` or the legacy fixture is caught only by a human remembering the target. TC-021 and TC-001 cover part of it by comparing `mappings.yaml` to the emitted schemas, but not the header, the id patterns, or the fixture. | Makefile:73, pyproject.toml:96 |
| FND-010 | low | Four `# pragma: no cover` comments sit in the test tree. Coverage is measured over `spec_artifacts_app/` only, so they suppress nothing — but a pragma that reads as "this is allowed to be uncovered" is the habit the integrity rule forbids, and it was removed from `spec-objects-business` for exactly this reason (SR-009 FND-006). | tests/conftest.py:130, tests/conftest.py:132, tests/conftest.py:193, tests/support/reference_mapping.py:516 |
| FND-011 | low | The committed header of `mappings.yaml` tells the reader that "`make mappings-check` fails on any drift". No such Make target exists; the target is `make schemas-check`. A reader following the file's own instruction gets "No rule to make target". | scripts/build_mappings.py:257, spec_artifacts_app/mappings.yaml:16 |
| FND-012 | low | `test_the_bundled_fr035_schema_rejects_the_four_malformed_forms` asserts three refusals, not four; the fourth is the separate strict xfail below it. Its unknown-key assertion is `any("semantic" in path for path in unknown_key)`, which checks the error's JSON path, not that the message names the offending key `foo` — while FR-003-AC-6 says "rejects `semantic: {…, foo: 1}` **naming `foo`**". | tests/test_manifest.py:146, spec/functional/FR-003-semantic-manifest-contract.md:174 |
| FND-013 | low | TC-007 discharges FR-002-AC-2 by comparing `toolchain.json`'s `files` to a directory listing of the same generated tree. Both are outputs of one `make schemas` run, so a model dropped from `main.tsp` disappears from both and the comparison still passes. The 39 support models and scalars FR-002 Outputs enumerates by name are never checked against the emitted set; only the two artifact-type models are. | tests/test_schema_emission.py:299, spec/functional/FR-002-semantic-data-schemas.md:239 |
| FND-014 | low | In the cycle test the `module()` helper writes a `manifest.yaml` into `tmp_path` for every synthesized module, and nothing ever reads those files — `graph_of` builds the graph from the returned dicts. The docstring nonetheless says the fixtures are "written to a temporary directory ... and read from here rather than from the machine's module root", so the test describes an isolation property it does not exercise. | tests/test_imports.py:112, tests/test_imports.py:130 |
| FND-015 | low | Dead and redundant test-module symbols: `H2` and `_table_headers` in `tests/test_skeletons.py` are defined and never used (the module builds its own inline scanner instead), and `test_an_undeclared_module_and_an_undeclared_type_fail_distinctly` closes with `module_gap[0].code != type_gap[0].code`, comparing two values that the two exact-equality assertions above already pinned to different literals — it cannot fail unless one of those has failed first. | tests/test_skeletons.py:33, tests/test_skeletons.py:37, tests/test_imports.py:96 |
| FND-016 | low | The `sysml-fence` alternate form is declared for `MasterRequirements` (`properties_fence` locator plus `alternate_form` in `mappings.yaml`) but no MasterRequirements `sysml` skeleton exists, TC-029 compares the two forms for `ApplicationSpec` only, and TC-028's forward check explicitly `continue`s past `properties_fence` for any skeleton not named `*.sysml.md`. The declared form is unexercised for one of the two exported models. | spec_artifacts_app/manifest.yaml:266, tests/test_skeletons.py:80, tests/test_skeletons.py:118 |
| FND-017 | low | `generate-schemas.mjs` reads the emitter scratch directory with a flat `readdirSync` and no `Dirent` check, so an emitter that ever writes into a subdirectory would silently drop files from both the shipped bundle and the recorded digest rather than fail. This is the `spec-artifacts-iso` SR-012 FND-013 defect, unfixed here; the `mine.length === 0` guard catches only the total-loss case. | scripts/generate-schemas.mjs:170 |
| FND-018 | low | The matrix states that the six criteria needing a running `filament-core-service` "are the whole of the `quire coverage` unbacked set". The engine reports six different entries — three `spec/tests.md` FR-001 rows plus `FR-001-AC-2/3/4` — and does not report `StR-001-VC-1`, `IT-001-AC-1` or `IT-001-AC-2` at all, because the Stakeholder and Integration Coverage table mints no rows. Three of the six named rows are therefore outside coverage entirely rather than unbacked within it. | spec/tests.md:56, spec/tests.md:157 |
| FND-019 | low | `quire` reports `DuplicateModuleName: 'spec-artifacts-app' declared at 2 path(s); first-wins` in this environment: the worktree at 0.2.0 and the installed module at `~/.ix/filament/modules/spec-artifacts-app` at 0.1.0. The ticket's own gate command, `quire validate --scope . "spec/**/*.md"`, may therefore validate this repository's documents against the pre-change archetype. The test suite is immune because every `validate_document` and `Registry.load_from` call names `PACKAGE_ROOT` or a copy of it explicitly; the command-line gate is not. | tests/conftest.py:29, tests/test_skeletons.py:106 |

## Gates Run

| Gate | Result |
| --- | --- |
| `make lint` | pass — ruff all checks passed, black 17 files unchanged |
| `make schemas-check` | pass — 39 schemas match, `mappings.yaml` matches the manifest, legacy fixture matches |
| `poetry run pytest -q` | pass — 42 passed, 2 xfailed (both strict, both naming an upstream issue); coverage 100% over four statements |
| `quire validate --scope . "spec/**/*.md" "plan/**/*.md"` | pass — zero errors; nine grammar warnings (`ears:non-singular`, `ears:unclassifiable`, `ears:missing-subject`, `quality:agentless-passive`) in FR-003 and FR-004 |
| `quire coverage --scope .` | 77/81 rows backed (95%); `status-column-matches-nothing` on `spec/tests.md` (FND-001) |
| `node scripts/generate-schemas.mjs --check` | pass on the committed tree |
| Oracle coverage over `tests/support/` (measured for this review) | `import_graph.py` 100%, `reference_mapping.py` 91% (45 lines, FND-002) |
| Lockfile registry audit | 74 of 75 packages resolve from `registry.npmjs.org`; only `@agent-ix/semantic-core` from `npm.ix` — the `spec-artifacts-iso` SR-012 FND-001 high does **not** recur here |

## Language Dispatch

Python (`pyproject.toml`, `tests/*.py`, two `scripts/*.py`) plus one Node build
script and one TypeSpec source. No Rust and no React in the change, so those
lanes do not apply. The repo idiom — module-level `test_*` functions carrying
`@pytest.mark.trace(...)`, not `TestFeature` classes — is followed consistently
and outranks the generic "leverage test classes" rule.

## Test Standards and Mock Compliance

- **No mocks anywhere.** No `unittest.mock`, no `@patch`, no `mocker` in the
  change. Every test drives the real generator, the real TypeSpec emitter, the
  real 2020-12 validator, the real Quire engine, or the committed bytes, so the
  mock-boundary rules are vacuously satisfied and no test can pass against a
  hollow stub. The engine boundary is exercised, not simulated: `Registry.load_from`,
  `validate_document` and `extract_semantic` all run for real.
- **No skips.** Zero `pytest.mark.skip` and zero `pytest.skip`. `require_quire`
  and the `schema_registry` fixture **fail** with a provisioning message rather
  than skipping when the wheel or `node_modules` is absent — the policy the
  conftest docstring states and keeps.
- **Two expected failures, both `strict=True`,** each naming its upstream issue
  (`agent-ix/quoin#341`, `agent-ix/quire-rs#394`) so a fixed engine turns the
  gate red rather than quietly passing. TC-017 carries a negative control
  proving the digest binding itself is real, which is what keeps the xfail from
  meaning "the binding does nothing".
- **No database, no network read**; the only subprocesses are `node` and
  `git show`. Every destructive generator test runs in a throwaway copy of the
  tree with `node_modules` symlinked, so no test can corrupt the committed
  schemas or the manifest.
- **Tracking tags.** Every test but `test_pack_exposes_manifest_path` (which
  predates the change) carries a single-line `@pytest.mark.trace(...)`, the
  marker is registered in `pyproject.toml`, and `quire coverage` binds 43 of 44
  candidate symbols — the multi-line-marker trap `spec-objects-business` hit
  (SR-009 FND-001) does not recur.

## Completeness

No `TODO`, `FIXME`, or `XXX` in any authored file. No `pass` placeholder, no
stub module, no empty class, no placeholder return, no import-only test. Every
test function contains an `assert` or a `pytest.raises`. No test asserts only
`is not None` or `isinstance`. The weaknesses found are of omission — a
criterion half without an assertion (FND-004, FND-005, FND-006) — not of
hollowness.

## Spec-Code Faithfulness

Checked against what the branch does, not what it claims:

- **FR-002** — `make schemas` runs the official `@typespec/json-schema` emitter
  through `tsp compile` into a scratch directory; `--check` is read-only by
  construction and writes nothing; the 39 emitted files match the names FR-002
  Outputs enumerates exactly; every `$ref` resolves to a shipped sibling or to
  a file that exists in the installed semantic-core 0.1.0 bundle (TC-003
  resolves them, which closes the generator's normalization fallback that
  `spec-objects-business` SR-009 FND-003 had to fix); all nine free-text
  properties declare themselves and the set is pinned. FND-013 is the one
  weak discharge.
- **FR-003** — the `semantic` block carries exactly the nine admitted keys, both
  exports use the reference form only, and both digests equal the SHA-256 of the
  shipped bytes. The digest binding is proved live: a one-hex-digit edit costs
  exactly the bound archetype and nothing else, with an unmutated control.
- **FR-004** — the mapping declaration is generated from the manifest rather
  than hand-maintained, so the column lists and id patterns cannot drift; the
  oracle reports every failure in one pass in document order. FND-002, FND-003,
  FND-004 and FND-006 are its gaps.
- **FR-005** — all three skeletons validate under the real engine, the `sysml`
  alternate produces a field list identical to the typed table for
  `ApplicationSpec`, and all eight negative fixtures are refused, each by
  exactly one rule at the mapping layer (verified independently for this
  review). The row-id-prefix criterion is correctly attributed to the locator
  layer rather than to the schema, avoiding the `spec-artifacts-iso` SR-012
  FND-006 misattribution: the emitted `CapabilityId` pattern is deliberately
  artifact-anchored and the doc comment says so.
- **NFR-001** — two consecutive generator runs are byte-identical and the
  committed bytes are what a fresh run produces; `.gitattributes` pins LF; the
  offline gate is recorded honestly as a manual procedure with an automated
  check that no workflow claims to run it, which is the right shape for a gate
  a test cannot perform.

## Gap Analysis

Discovery over the change surfaced four unstated requirements:

1. **A status column the engine can read is part of the matrix contract.**
   Nothing said so, and the rewrite silently traded the check away (FND-001).
   The lesson generalises: a matrix header is instrumentation, not prose.
2. **A declared-but-uninstantiated designation is not a designation.**
   `prose_only` passes schema validation, passes both tests, and describes
   nothing (FND-004). A vocabulary entry with zero instances and zero negative
   fixtures should be treated as unimplemented.
3. **A fixture's `expect` key routes evidence away as well as toward it.**
   Dispatching on `expect` is right — a fixture refused by the wrong check
   proves nothing — but it silently removed three documents from the oracle's
   evidence set (FND-003). A fixture should be run through every surface that
   has an opinion, asserting the expected one and recording the others.
4. **A coverage gate calibrated for a four-statement package measures nothing
   of a 1,100-line test-support tree** (FND-007). This is the same follow-up
   `spec-artifacts-iso` left open as SR-012 FND-018 and it has now cost this
   repository nine unexercised diagnostics.

## Edge Case & Logic Review

- **Input validation.** The generator reads the manifest version and the
  `@jsonSchema` base with anchored regexes rather than a YAML round trip, so
  anchors and comments survive the digest rewrite; a manifest with no top-level
  `version` fails naming the file; a base/version disagreement exits non-zero
  naming both values without touching committed output (proved byte-for-byte).
- **Failure policy.** `tsp compile` failure, zero emitted module schemas, Node
  older than 20, a missing dependency, and a manifest referencing an unemitted
  schema each exit non-zero before any write.
- **Determinism.** `NoAliasDumper` keeps the derived YAML free of anchors, the
  emitted JSON is rendered with a fixed `JSON.stringify(…, 2)` plus newline, and
  `.gitattributes` pins `eol=lf`, so digests are checkout-independent.
- **Isolation.** Every mutating test copies the tree into `tmp_path` and
  symlinks `node_modules`; the legacy-manifest and digest-mutation tests write
  only into copies. No test mutates the operator's machine.
- **Traversal and paths.** The mapping oracle never joins a document-supplied
  string onto a filesystem path, and no code in the module or its support tree
  writes a Markdown document (enumerated over the tree by TC-020, not sampled).
- **Recursion bounds.** `_is_constrained` carries an explicit depth cap of 12
  and `find_cycles` prunes on `target > path[0]`, so neither can run away on a
  malformed bundle.
