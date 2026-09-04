# =============================================================================
# spec-artifacts-app Makefile
# =============================================================================
# All tasks are defined in pyproject.toml using poethepoet.
# Run `poe --help` to see available tasks, or use Make targets below.
# =============================================================================

POETRY = poetry
POE = $(POETRY) run poe

.PHONY: help
help:
	@echo "Available targets (via poe):"
	@echo "  make install        - Install dependencies"
	@echo "  make test           - Run tests"
	@echo "  make lint           - Run linters (ruff + black)"
	@echo "  make schemas        - Emit the JSON Schemas from TypeSpec and refresh the derived files"
	@echo "  make schemas-check  - Fail when the committed schemas, digests or mappings drift"
	@echo "  make semantic-install - npm ci for the pinned TypeSpec toolchain"
	@echo "  make dev-quire      - Install the Quire wheel the semantic tests need"
	@echo "  make format         - Format code (black + ruff --fix)"
	@echo "  make build          - Build distribution"
	@echo "  make clean          - Clean build artifacts"
	@echo "  make version        - Show computed version"
	@echo "  make info           - Show git and version info"
	@echo "  make shell          - Open poetry shell"
	@echo ""
	@echo "Package management:"
	@echo "  make update-lock            - Update poetry.lock"
	@echo "  make update-packages        - Update deps (keep major)"
	@echo "  make update-packages-latest - Update deps (latest)"
	@echo "  make add-package p=<name>   - Add production dependency"
	@echo "  make add-dev-package p=<name> - Add dev dependency"
	@echo "  make use-local p=<name>     - Switch dep to local registry"
	@echo "  make use-upstream p=<name>  - Switch dep to upstream"

# =============================================================================
# Environment
# =============================================================================

.PHONY: install
install:
	$(POETRY) install

.PHONY: shell
shell:
	$(POETRY) shell

# =============================================================================
# Tasks (delegated to poe)
# =============================================================================

.PHONY: test
test:
	$(POE) test

# There is no `tests_integration/` tree in this module and no cluster to run one
# against: the integration this module has is the Quire engine boundary, and that
# runs in the ordinary suite (IT-002). The target is kept so the Makefile matches
# its siblings, and says so rather than failing with a bare "no such directory".
.PHONY: test-integrations test-it
test-integrations test-it:
	@echo "No cluster integration suite in this module. The engine-boundary tests"
	@echo "(IT-002) run under \`make test\`; \`make dev-quire\` provisions the wheel.

.PHONY: lint
lint:
	$(POE) lint

# =============================================================================
# Semantic data schemas (FR-002): TypeSpec -> JSON Schema projection
# =============================================================================
# The TypeSpec source lives in typespec/ (npm, lockfile committed). `make
# schemas` regenerates spec_artifacts_app/schemas/, rewrites the manifest
# data_schema digests, and rebuilds the derived mappings.yaml and legacy-manifest
# fixture. `make schemas-check` fails on any byte drift and writes nothing.
#
# `@agent-ix/semantic-core` resolves only from the registry the machine's npm
# configuration routes the `@agent-ix` scope to; the repository carries no
# `.npmrc` (FR-002-CON-3), so these run locally rather than in CI until
# agent-ix/filament-core-data#11 publishes the package.

.PHONY: semantic-install
semantic-install:
	npm ci

.PHONY: schemas
schemas:
	$(POE) schemas

.PHONY: schemas-check
schemas-check:
	$(POE) schemas-check

# The Quire wheel exposing `extract_semantic` is on no index this repository may
# commit against (agent-ix/quire-rs#392), so it is provisioned here rather than
# declared. The semantic tests fail — never skip — when it is absent.
.PHONY: dev-quire
dev-quire:
	$(POE) dev-quire

.PHONY: format
format:
	$(POE) format

.PHONY: build
build:
	$(POE) build

.PHONY: build-dist
build-dist: build

.PHONY: clean
clean:
	$(POE) clean

.PHONY: version
version:
	$(POE) version

.PHONY: info
info:
	$(POE) info

# =============================================================================
# Package Management
# =============================================================================

.PHONY: update-lock
update-lock:
	$(POETRY) lock

.PHONY: update-packages
update-packages:
	$(POE) update-deps

.PHONY: update-packages-latest
update-packages-latest:
	$(POE) update-deps-latest

.PHONY: add-package
add-package:
	package=$(p) $(POE) add-dep

.PHONY: add-dev-package
add-dev-package:
	package=$(p) $(POE) add-dev-dep

.PHONY: use-local
use-local:
	package=$(p) $(POE) use-local-dep

.PHONY: use-upstream
use-upstream:
	package=$(p) $(POE) use-upstream-dep

# =============================================================================
# Publishing
# =============================================================================

LOCAL_PYPI_URL ?= http://pypi.ix/root/dev/+simple/

.PHONY: local-publish
local-publish: build
	@echo "📦 Publishing to local PyPI ($(LOCAL_PYPI_URL))..."
	@export PATH="$$HOME/.local/bin:$$PATH"; \
	VERSION=$$($(POE) version); \
	echo "  Full version: $$VERSION"; \
	devpi use $(LOCAL_PYPI_URL); \
	devpi login root --password=''; \
	devpi upload --from-dir dist/; \
	echo "✅ Published $$VERSION"
