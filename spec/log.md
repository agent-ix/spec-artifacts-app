---
type: log
title: "Update Log"
description: "Chronological log of structural changes to this bundle."
---
# Update Log

## History

* **2026-06-15** — Adopted OKF-compatible bundle structure with directory indexes.
* **2026-09-04** — Adopted the Wave 4 semantic-module contract (agent-ix/spec-artifacts-app#3). Added US-001, FR-002..FR-005, NFR-001 and IT-002; extended `spec.md` with a deliberate Out of Scope naming every upstream blocker; rebuilt `tests.md` as a validated Test Matrix over TC-001..TC-036. Eight review analyses were run in parallel and their dispositions applied: `semantic.imports` moved to the package-to-version shape the FR-035 contract actually admits, the typed `## Properties` declaration was added, the FR dependency cycle was flattened into a chain, and four upstream gaps were filed rather than worked around (agent-ix/quoin#338, #339, #341).
* **2026-09-22** — PLAT-974: CI off the dev-only mirrors. `agent-ix/quire-rs#392` is resolved — `quire` 0.47.1 is declared as a `pyproject.toml` dev dependency pinned to the `internal-pypi` source, `make dev-quire` and the `local-pypi` poetry source are deleted, and `spec.md`, FR-002, FR-003, NFR-001, IT-002 and `tests.md` drop the `pypi.ix`/`make dev-quire`/quire-rs#392 blocker language accordingly. `@agent-ix/semantic-core` resolves from GitHub Packages rather than the dev-only `npm.ix` mirror (FR-002, NFR-001); `ci.yml`'s `ci:` job now runs `semantic-module-ci.yml`, which installs both toolchains before the suite runs. No functional or test-matrix change: all four gates were already green under quire 0.47.1 and no fixture, locator, or xfail needed a code change.
