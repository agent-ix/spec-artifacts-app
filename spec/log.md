---
type: log
title: "Update Log"
description: "Chronological log of structural changes to this bundle."
---
# Update Log

## History

* **2026-06-15** — Adopted OKF-compatible bundle structure with directory indexes.
* **2026-09-04** — Adopted the Wave 4 semantic-module contract (agent-ix/spec-artifacts-app#3). Added US-001, FR-002..FR-005, NFR-001 and IT-002; extended `spec.md` with a deliberate Out of Scope naming every upstream blocker; rebuilt `tests.md` as a validated Test Matrix over TC-001..TC-036. Eight review analyses were run in parallel and their dispositions applied: `semantic.imports` moved to the package-to-version shape the FR-035 contract actually admits, the typed `## Properties` declaration was added, the FR dependency cycle was flattened into a chain, and four upstream gaps were filed rather than worked around (agent-ix/quoin#338, #339, #341).
