"""Shared fixtures for the module's test suite.

Two policies live here and nowhere else:

* **The engine is a hard dependency of the semantic rows.** ``quire`` is not
  declared in ``pyproject.toml`` — no index a repository may commit against
  carries the 0.46.0 wheel exposing ``extract_semantic``, so it is provisioned
  by ``make dev-quire`` and ``agent-ix/quire-rs#392`` is the blocking issue.
  When it is absent the semantic tests **fail**; they never skip, because a
  skipped row is not coverage.
* **The emitted schemas are read from the committed tree**, and every ``$ref``
  resolves against the semantic-core package the pinned toolchain installs, so a
  record test validates against the real shipped bytes rather than a copy.
* **No copy of the module-manifest schema lives here.** That schema belongs to
  filament-core-service; a copy held in this repository could only be compared
  against itself, so it would stay green after the real schema moved. The
  consumers that read this manifest — the quire engine below, and quoin at
  install — are the oracle (PLAT-902).
"""

from __future__ import annotations

import hashlib
import json
import pathlib
from typing import Any

import pytest
import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PACKAGE_ROOT = REPO_ROOT / "spec_artifacts_app"
MANIFEST_PATH = PACKAGE_ROOT / "manifest.yaml"
MAPPINGS_PATH = PACKAGE_ROOT / "mappings.yaml"
MAPPINGS_SCHEMA_PATH = PACKAGE_ROOT / "mappings.schema.json"
SCHEMAS_DIR = PACKAGE_ROOT / "schemas"
SKELETONS_DIR = PACKAGE_ROOT / "skeletons"
TOOLCHAIN_PATH = SCHEMAS_DIR / "toolchain.json"
TYPESPEC_DIR = REPO_ROOT / "typespec"
FIXTURES = REPO_ROOT / "tests" / "fixtures"
NEGATIVE_DIR = FIXTURES / "negative"
BASELINE_DIR = FIXTURES / "baseline"
LEGACY_MANIFEST_PATH = FIXTURES / "manifest-legacy.yaml"
SEMANTIC_CORE_DIR = (
    REPO_ROOT
    / "node_modules"
    / "@agent-ix"
    / "semantic-core"
    / "generated"
    / "json-schema"
)

SEMANTIC_CORE_BASE = "https://schemas.agent-ix.org/semantic-core/0.1.0/"

#: Artifact type -> emitted model, the FR-002 export map.
MODEL_OF = {
    "ApplicationSpec": "ApplicationSpec",
    "MasterRequirements": "MasterRequirements",
}

QUIRE_MISSING = (
    "the Quire wheel exposing `extract_semantic` is not installed in this "
    "environment. Run `make dev-quire` (agent-ix/quire-rs#392 tracks publishing "
    "0.46.0 to an index this repository may depend on). The semantic tests fail "
    "rather than skip, because a skipped row is not coverage."
)


def load_manifest() -> dict[str, Any]:
    return yaml.safe_load(MANIFEST_PATH.read_text())


def load_mappings() -> dict[str, Any]:
    return yaml.safe_load(MAPPINGS_PATH.read_text())


def manifest_version() -> str:
    return load_manifest()["version"]


def module_base() -> str:
    """The `$id` base, read from the manifest version.

    Never hard-coded: a version bump must not need a test edit (FR-002-CON-5).
    """
    return (
        "https://schemas.agent-ix.org/agent-ix/spec-artifacts-app/"
        f"{manifest_version()}/"
    )


def artifact_types() -> list[dict[str, Any]]:
    return load_manifest()["artifact_types"]


def artifact_type(name: str) -> dict[str, Any]:
    return next(at for at in artifact_types() if at["name"] == name)


def locators(entry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    body = entry.get("body_extraction") or {}
    return ((body.get("yield_pattern") or {}).get("match")) or {}


def emitted_schema_names() -> list[str]:
    """The projections under `schemas/`.

    Neither `toolchain.json` nor the hand-authored frontmatter schemas, which
    live in the same directory and are not emitted from TypeSpec.
    """
    return sorted(
        p.name
        for p in SCHEMAS_DIR.glob("*.json")
        if p.name != "toolchain.json"
        and not p.name.endswith("-frontmatter.schema.json")
    )


def sha256_of(path: pathlib.Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def require_quire():
    """Import quire, or fail the test naming the provisioning path."""
    try:
        import quire
    except ImportError as error:  # pragma: no cover - environment guard
        pytest.fail(f"{QUIRE_MISSING} (import error: {error})")
    if not hasattr(quire, "extract_semantic"):  # pragma: no cover - environment guard
        pytest.fail(
            f"`extract_semantic` is missing from the installed quire: {QUIRE_MISSING}"
        )
    return quire


@pytest.fixture(scope="session")
def quire_engine():
    return require_quire()


@pytest.fixture(scope="session")
def manifest() -> dict[str, Any]:
    return load_manifest()


@pytest.fixture(scope="session")
def mappings() -> dict[str, Any]:
    return load_mappings()


@pytest.fixture(scope="session")
def semantic_block(manifest: dict[str, Any]) -> dict[str, Any]:
    return manifest["semantic"]


@pytest.fixture(scope="session")
def semantic_module(semantic_block: dict[str, Any]) -> dict[str, Any]:
    """The `module` block `extract_semantic` takes, derived from the manifest."""
    return {
        "contractVersion": semantic_block["contract_version"],
        "semanticCore": semantic_block["semantic_core"],
        "package": semantic_block["package"],
        "exports": semantic_block["exports"],
        "imports": semantic_block["imports"],
        "compatibilityPosture": semantic_block["compatibility_posture"],
        "legacyForms": semantic_block["legacy_forms"],
    }


@pytest.fixture(scope="session")
def skeletons() -> list[pathlib.Path]:
    return sorted(SKELETONS_DIR.glob("*.md"))


@pytest.fixture(scope="session")
def schema_registry():
    """A 2020-12 validator factory over the shipped schemas plus semantic-core.

    Every `$ref` resolves locally: module models from the committed `schemas/`
    directory, grammar models from the semantic-core package the pinned
    toolchain installs.
    """
    from referencing import Registry, Resource

    if not SEMANTIC_CORE_DIR.is_dir():  # pragma: no cover - environment guard
        pytest.fail(
            "@agent-ix/semantic-core is not installed, so `$ref`s to the grammar "
            "cannot resolve. Run `npm ci` (FR-002-CON-3: the repository carries no "
            "`.npmrc`, so `@agent-ix` resolves through the user-level npm config)."
        )
    resources = []
    for path in sorted(SCHEMAS_DIR.glob("*.json")):
        if path.name == "toolchain.json":
            continue
        schema = json.loads(path.read_text())
        if "$id" not in schema:
            continue
        resources.append((schema["$id"], Resource.from_contents(schema)))
    for path in sorted(SEMANTIC_CORE_DIR.glob("*.json")):
        schema = json.loads(path.read_text())
        uri = schema.get("$id") or f"{SEMANTIC_CORE_BASE}{path.name}"
        resources.append((uri, Resource.from_contents(schema)))
    registry = Registry().with_resources(resources)

    def validator_for(model: str):
        from jsonschema import Draft202012Validator

        schema = json.loads((SCHEMAS_DIR / f"{model}.json").read_text())
        return Draft202012Validator(schema, registry=registry)

    return validator_for


@pytest.fixture(scope="session")
def build_record(mappings: dict[str, Any], manifest: dict[str, Any]):
    """Build a record for `model` from a document, via the FR-004 reference mapping."""
    from tests.support.reference_mapping import ReferenceMapping

    def build(model: str, path: pathlib.Path, *, source_identity: str | None = None):
        return ReferenceMapping(mappings, manifest, model).build(
            path.read_text(),
            str(path.relative_to(REPO_ROOT)),
            source_identity=source_identity,
        )

    return build
