---
description: Node.js Library Local Development
---

# Dockerized Environment

This repository uses a dockerized environment to ensure a consistent development environment and to avoid polluting the host system.

**Do not run `npm`, `pnpm`, or `node` commands directly on the host.**

Instead, verify usage instructions in the `README.md` and use the provided `Makefile` to run common tasks such as building, testing, and formatting.

Common commands usually include:
- `make docker-build`
- `make test`
- `make format`
