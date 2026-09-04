"""The emitted JSON Schema bundle, its toolchain record, and its drift gates.

Every requirement id lives on a test's `trace` marker, never in this docstring:
a trace id written on a module binds to nothing and is reported unbacked,
indistinguishable from a test nobody wrote (quire-rs CR-061).
"""

from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import time

import pytest

from tests.conftest import (
    MODEL_OF,
    REPO_ROOT,
    SCHEMAS_DIR,
    SEMANTIC_CORE_BASE,
    SKELETONS_DIR,
    TOOLCHAIN_PATH,
    artifact_types,
    emitted_schema_names,
    load_mappings,
    locators,
    manifest_version,
    module_base,
)

GENERATOR = REPO_ROOT / "scripts" / "generate-schemas.mjs"

#: FR-002-AC-4: the closed set of properties allowed to be free text. Every other
#: property must be constrained after following `$ref`. The list is the
#: requirement's, restated here so a new free-text property is a failing test
#: rather than a silent widening.
FREE_TEXT = {
    ("Section", "text"),
    ("Provenance", "path"),
    ("Verification", "method"),
    ("Verification", "annotation"),
    ("Boundary", "description"),
    ("Capability", "description"),
    ("Actor", "description"),
    ("Interface", "contract"),
    ("RenderingRequirement", "requirement"),
}

#: FR-002-CON-4: an application declaration and a deployed application's runtime
#: state stay distinct.
RUNTIME_STATE = {
    "deployed",
    "running",
    "health",
    "uptime",
    "instanceCount",
    "lastDeployedAt",
}

CONSTRAINING = {
    "pattern",
    "minLength",
    "minimum",
    "enum",
    "const",
    "format",
    "minValue",
}


def _declares_free_text(node) -> bool:
    """A property a model deliberately leaves free text, and says so."""
    return isinstance(node, dict) and "free text:" in node.get("description", "")


def _schemas() -> dict[str, dict]:
    return {
        name[: -len(".json")]: json.loads((SCHEMAS_DIR / name).read_text())
        for name in emitted_schema_names()
    }


def _run_generator(
    *args: str, cwd: pathlib.Path | None = None
) -> subprocess.CompletedProcess:
    """Run the generator *of the tree under test* — never this repo's copy.

    A scratch tree exists to be mutated; running the committed script against it
    would read the committed repo root instead and report on the wrong tree.
    """
    root = cwd or REPO_ROOT
    return subprocess.run(
        ["node", str(root / "scripts" / "generate-schemas.mjs"), *args],
        cwd=str(root),
        capture_output=True,
        text=True,
    )


def _refs(node) -> list[str]:
    out: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "$ref" and isinstance(value, str):
                out.append(value)
            else:
                out.extend(_refs(value))
    elif isinstance(node, list):
        for item in node:
            out.extend(_refs(item))
    return out


def _resolve(ref: str, schemas: dict[str, dict]) -> dict | None:
    """Follow a `$ref` into this bundle. A semantic-core ref resolves elsewhere."""
    if ref.startswith(SEMANTIC_CORE_BASE):
        return None
    name = ref.rsplit("/", 1)[-1][: -len(".json")]
    return schemas.get(name)


def _is_constrained(node, schemas: dict[str, dict], depth: int = 0) -> bool:
    """A property is constrained when it, or what it `$ref`s, bottoms out in a rule."""
    if depth > 12 or not isinstance(node, dict):
        return False
    if CONSTRAINING & set(node):
        return True
    if node.get("type") in {"boolean", "null"}:
        return True
    if "$ref" in node:
        target = _resolve(node["$ref"], schemas)
        if target is None:
            # semantic-core owns its own constraints; the grammar is not this
            # module's to re-assert.
            return True
        return _is_constrained(target, schemas, depth + 1)
    if node.get("type") == "array":
        return _is_constrained(node.get("items", {}), schemas, depth + 1)
    if node.get("type") == "object" and node.get("properties"):
        return all(
            _is_constrained(value, schemas, depth + 1) or _declares_free_text(value)
            for value in node["properties"].values()
        )
    for key in ("anyOf", "oneOf", "allOf"):
        if key in node:
            return all(_is_constrained(item, schemas, depth + 1) for item in node[key])
    return False


@pytest.mark.trace("TC-001", "FR-002-CON-1")
def test_every_locator_output_has_a_model_property_and_the_reverse():
    """Both directions: no locator output without a field, no field without a source."""
    mappings = load_mappings()
    for entry in artifact_types():
        model = MODEL_OF[entry["name"]]
        properties = mappings["models"][model]["properties"]
        declared = set(
            json.loads((SCHEMAS_DIR / f"{model}.json").read_text())["properties"]
        )

        assert (
            set(properties) == declared
        ), f"{model}: mappings.yaml and the emitted schema declare different properties"

        mapped_locators = {
            spec["locator"] for spec in properties.values() if "locator" in spec
        }
        mapped_locators |= {
            spec["alternate_form"]["locator"]
            for spec in properties.values()
            if "alternate_form" in spec
        }
        assert mapped_locators == set(locators(entry)), (
            f"{entry['name']}: locators and mapping entries disagree; "
            f"unmapped={set(locators(entry)) - mapped_locators}, "
            f"phantom={mapped_locators - set(locators(entry))}"
        )


@pytest.mark.trace("TC-002", "FR-002-AC-4", "FR-002-CON-1")
def test_every_property_is_constrained_and_free_text_is_declared_not_defaulted():
    """Two halves of FR-002-AC-4, which are different claims.

    *Constrained*: every property, after following `$ref`, bottoms out in a
    `pattern`, `minLength`, `minimum`, `enum`, `const`, or `format`. Free text
    here is still `NonEmptyText`, so this half admits no exception at all.

    *Declared*: the properties whose meaning is nonetheless open — a prose cell
    no vocabulary owns — say `free text:` and why, and the set of them is
    exactly the closed list the requirement fixes. A tenth free-text property
    fails this test, which is the point: widening the set is a decision, not a
    side effect.
    """
    schemas = _schemas()
    declared_free: set[tuple[str, str]] = set()
    for model, schema in schemas.items():
        for name, node in (schema.get("properties") or {}).items():
            assert _is_constrained(
                node, schemas
            ), f"{model}.{name} bottoms out in no constraint"
            if _declares_free_text(node):
                assert node["description"].startswith(
                    "free text:"
                ), f"{model}.{name} mentions free text without leading with it"
                declared_free.add((model, name))
    assert declared_free == FREE_TEXT, (
        f"the free-text set moved: unexpected={sorted(declared_free - FREE_TEXT)}, "
        f"no longer free={sorted(FREE_TEXT - declared_free)}"
    )


@pytest.mark.trace("TC-003", "FR-002-AC-1", "FR-002-AC-3", "FR-002-CON-2")
def test_exported_schemas_carry_the_versioned_id_and_every_ref_resolves_offline():
    base = module_base()
    schemas = _schemas()
    for entry in artifact_types():
        model = MODEL_OF[entry["name"]]
        schema = schemas[model]
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert schema["$id"] == f"{base}{model}.json"
        assert schema["properties"]["type"]["const"] == entry["name"]

    shipped = {f"{base}{name}" for name in emitted_schema_names()}
    semantic_core = {
        f"{SEMANTIC_CORE_BASE}{p.name}"
        for p in (
            REPO_ROOT / "node_modules/@agent-ix/semantic-core/generated/json-schema"
        ).glob("*.json")
    }
    for model, schema in schemas.items():
        for ref in _refs(schema):
            assert ref in shipped or ref in semantic_core, (
                f"{model}: `$ref` {ref} resolves to neither a shipped sibling nor "
                "the semantic-core 0.1.0 bundle"
            )


@pytest.mark.trace("TC-004", "FR-002-AC-11", "FR-002-CON-3")
def test_the_toolchain_is_pinned_exactly_with_a_committed_lockfile_and_no_npmrc():
    package = json.loads((REPO_ROOT / "package.json").read_text())
    assert package["devDependencies"] == {
        "@agent-ix/semantic-core": "0.1.0",
        "@typespec/compiler": "1.15.0",
        "@typespec/json-schema": "1.15.0",
    }
    lock = REPO_ROOT / "package-lock.json"
    assert lock.is_file(), "package-lock.json is not committed"
    assert not (REPO_ROOT / ".npmrc").exists(), (
        "the repository carries an .npmrc; the `@agent-ix` scope routing is the "
        "machine's, not the repository's (FR-002-CON-3)"
    )
    text = lock.read_text()
    assert (
        '"file:' not in text and '"link:' not in text
    ), "the lockfile carries a local reference"


@pytest.mark.trace("TC-005", "FR-002-AC-6", "FR-002-CON-4")
def test_no_property_models_runtime_state():
    for model, schema in _schemas().items():
        offending = RUNTIME_STATE & set(schema.get("properties") or {})
        assert (
            not offending
        ), f"{model} declares runtime-state properties {sorted(offending)}"
    description = _schemas()["ApplicationSpec"]["description"]
    assert "runtime state (deployment, health, uptime) is not modelled" in description


@pytest.mark.trace("TC-006", "FR-002-AC-9", "FR-002-CON-5")
def test_a_base_version_mismatch_fails_the_generator_and_writes_nothing(tmp_path):
    """The `$id` base embeds the manifest version; a disagreement is a hard stop."""
    work = tmp_path / "repo"
    shutil.copytree(
        REPO_ROOT,
        work,
        ignore=shutil.ignore_patterns(
            ".git",
            ".worktrees",
            "node_modules",
            "__pycache__",
            ".pytest_cache",
            ".ruff_cache",
        ),
    )
    os.symlink(REPO_ROOT / "node_modules", work / "node_modules")
    source = work / "typespec" / "main.tsp"
    source.write_text(source.read_text().replace(f"/{manifest_version()}/", "/9.9.9/"))
    before = {
        p.name: p.read_bytes()
        for p in (work / "spec_artifacts_app" / "schemas").glob("*.json")
    }

    result = _run_generator(cwd=work)

    assert result.returncode != 0, "a base/manifest version mismatch was accepted"
    assert (
        "9.9.9" in result.stderr and manifest_version() in result.stderr
    ), f"the failure names neither value: {result.stderr}"
    after = {
        p.name: p.read_bytes()
        for p in (work / "spec_artifacts_app" / "schemas").glob("*.json")
    }
    assert after == before, "the generator wrote output on a failing run"


@pytest.mark.trace("TC-007", "FR-002-AC-2", "FR-002-AC-7")
def test_the_emitted_set_equals_toolchain_json_and_its_digest_recomputes():
    import hashlib

    toolchain = json.loads(TOOLCHAIN_PATH.read_text())
    assert toolchain["files"] == emitted_schema_names()
    assert toolchain["base"] == module_base()

    for entry in artifact_types():
        assert (
            f"{MODEL_OF[entry['name']]}.json" in toolchain["files"]
        ), f"{entry['name']} has no emitted model"

    digest = hashlib.sha256()
    for name in toolchain["files"]:
        digest.update(f"{name}\n".encode())
        digest.update((SCHEMAS_DIR / name).read_bytes())
    assert toolchain["digest"] == f"sha256:{digest.hexdigest()}"

    # `toolchain.json` and the directory listing are both products of the same
    # run, so comparing them to each other proves only that the run was
    # self-consistent. The independent claim is reachability: every emitted file
    # must be reachable from one of the two exported models by following `$ref`,
    # and every reachable name must be emitted. That catches an orphan the
    # emitter left behind and a model the bundle references but does not ship —
    # neither of which a self-comparison can see.
    schemas = _schemas()
    reachable: set[str] = set()
    frontier = [MODEL_OF[entry["name"]] for entry in artifact_types()]
    while frontier:
        model = frontier.pop()
        if model in reachable:
            continue
        reachable.add(model)
        for ref in _refs(schemas[model]):
            if ref.startswith(SEMANTIC_CORE_BASE):
                continue
            target = ref.rsplit("/", 1)[-1][: -len(".json")]
            assert (
                target in schemas
            ), f"{model} references {target}.json, which is not shipped"
            frontier.append(target)
    emitted = {name[: -len(".json")] for name in emitted_schema_names()}
    assert reachable == emitted, (
        f"orphans nothing reaches={sorted(emitted - reachable)}, "
        f"referenced but unshipped={sorted(reachable - emitted)}"
    )


@pytest.mark.trace("TC-008", "FR-002-AC-5")
def test_schemas_check_passes_on_the_tree_and_fails_after_a_one_byte_edit(tmp_path):
    assert (
        _run_generator("--check").returncode == 0
    ), "the committed tree does not match its source"

    work = tmp_path / "repo"
    shutil.copytree(
        REPO_ROOT,
        work,
        ignore=shutil.ignore_patterns(
            ".git",
            ".worktrees",
            "node_modules",
            "__pycache__",
            ".pytest_cache",
            ".ruff_cache",
        ),
    )
    os.symlink(REPO_ROOT / "node_modules", work / "node_modules")
    victim = work / "spec_artifacts_app" / "schemas" / "Section.json"
    victim.write_text(victim.read_text().replace("free text:", "free text.", 1))

    result = _run_generator("--check", cwd=work)
    assert result.returncode != 0, "a one-byte schema edit passed the drift gate"
    assert (
        "Section.json" in result.stderr
    ), f"the failure does not name the file: {result.stderr}"


@pytest.mark.trace("TC-009", "FR-002-AC-8")
def test_object_schemas_are_inline_and_sealed_and_the_validator_agrees(
    schema_registry, build_record
):
    schemas = _schemas()
    for model, schema in schemas.items():
        if schema.get("type") != "object":
            continue
        for keyword in ("allOf", "oneOf", "anyOf", "$ref"):
            assert (
                keyword not in schema
            ), f"{model} declares {keyword} at the object's top level"
        assert schema.get("unevaluatedProperties") == {
            "not": {}
        }, f"{model} is not sealed"

    for path in sorted(SKELETONS_DIR.glob("*.md")):
        model = "MasterRequirements" if "master" in path.name else "ApplicationSpec"
        record = build_record(model, path)
        errors = list(schema_registry(model).iter_errors(record.data))
        assert not errors, [
            ("/".join(str(p) for p in e.absolute_path), e.message) for e in errors
        ]

    # A record carrying a property no model declares is refused, and only
    # because the models are sealed.
    record = build_record("ApplicationSpec", SKELETONS_DIR / "application-spec.md")
    mutated = dict(record.data, deployedAt="2026-09-04")
    assert list(
        schema_registry("ApplicationSpec").iter_errors(mutated)
    ), "an undeclared property was accepted; the schema is not sealed"


@pytest.mark.trace("TC-010", "FR-002-AC-10")
def test_no_cross_module_ref_and_no_imported_field_is_duplicated():
    schemas = _schemas()
    base = module_base()
    for model, schema in schemas.items():
        for ref in _refs(schema):
            assert ref.startswith(base) or ref.startswith(
                SEMANTIC_CORE_BASE
            ), f"{model}: `$ref` {ref} names a base this module cannot resolve offline"
    imported = schemas["ImportedTypeRef"]
    assert set(imported["properties"]) == {"module", "type"}, (
        "ImportedTypeRef carries more than the module/type reference pair; a "
        "reference that grows fields is a duplication"
    )
    assert imported.get("unevaluatedProperties") == {"not": {}}


@pytest.mark.trace("TC-030", "NFR-001-AC-1")
def test_two_consecutive_generator_runs_produce_byte_identical_output(tmp_path):
    work = tmp_path / "repo"
    shutil.copytree(
        REPO_ROOT,
        work,
        ignore=shutil.ignore_patterns(
            ".git",
            ".worktrees",
            "node_modules",
            "__pycache__",
            ".pytest_cache",
            ".ruff_cache",
        ),
    )
    os.symlink(REPO_ROOT / "node_modules", work / "node_modules")

    def snapshot() -> dict[str, bytes]:
        files = {
            p.name: p.read_bytes()
            for p in (work / "spec_artifacts_app" / "schemas").glob("*.json")
        }
        files["manifest.yaml"] = (
            work / "spec_artifacts_app" / "manifest.yaml"
        ).read_bytes()
        files["mappings.yaml"] = (
            work / "spec_artifacts_app" / "mappings.yaml"
        ).read_bytes()
        return files

    assert _run_generator(cwd=work).returncode == 0
    first = snapshot()
    assert _run_generator(cwd=work).returncode == 0
    second = snapshot()
    assert first == second, "two consecutive runs on one tree disagree"
    # And the committed tree is what a fresh run produces.
    for name, content in second.items():
        if name in {"manifest.yaml", "mappings.yaml"}:
            continue
        assert (SCHEMAS_DIR / name).read_bytes() == content


@pytest.mark.trace("TC-033", "NFR-001-AC-4")
def test_schemas_check_completes_within_the_threshold():
    """Metric 4's 30 s threshold, measured on whatever machine runs the suite.

    The target (10 s) is the reference machine's; the threshold is the bound the
    requirement sets, and a run that exceeds it is a real regression rather than
    a slow laptop.
    """
    started = time.monotonic()
    result = _run_generator("--check")
    elapsed = time.monotonic() - started
    assert result.returncode == 0
    assert (
        elapsed < 30.0
    ), f"`schemas-check` took {elapsed:.1f}s, over the 30 s threshold"
