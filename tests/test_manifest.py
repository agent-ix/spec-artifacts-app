"""The manifest and the semantic block.

Requirement ids live on the `trace` markers below, not here: a trace id on a
module docstring binds to nothing (quire-rs CR-061).
"""

from __future__ import annotations

import pytest

import spec_artifacts_app as pack
from tests.conftest import (
    MODEL_OF,
    SCHEMAS_DIR,
    artifact_types,
)

ADMITTED_SEMANTIC_KEYS = {
    "contract_version",
    "package",
    "exports",
    "imports",
    "import_types",
    "targets",
    "mappings",
    "compatibility_posture",
    "legacy_forms",
}


@pytest.mark.trace("TC-038", "FR-001-AC-5")
def test_pack_exposes_manifest_path() -> None:
    """The activation pipeline imports this package and reads `MANIFEST_PATH`."""
    assert pack.MANIFEST_PATH == pack.PACK_ROOT / "manifest.yaml"
    assert pack.MANIFEST_PATH.is_file()


@pytest.mark.trace("TC-011", "FR-003-AC-1")
def test_the_semantic_block_carries_the_admitted_keys(semantic_block):
    assert set(semantic_block) == ADMITTED_SEMANTIC_KEYS
    assert semantic_block["contract_version"] == "1.0.0"
    assert semantic_block["package"] == "agent-ix/spec-artifacts-app"
    assert semantic_block["exports"] == ["ApplicationSpec"]
    assert semantic_block["targets"] == ["json-schema", "markdown"]
    assert semantic_block["compatibility_posture"] == "additive"
    assert semantic_block["legacy_forms"] == "warning"
    assert "sweep_report" not in semantic_block, (
        "`sweep_report` is required only by `legacy_forms: error`; declaring it "
        "under `warning` would claim a sweep that never happened"
    )


@pytest.mark.trace("TC-012", "FR-003-AC-2", "FR-003-CON-2")
def test_every_export_carries_the_reference_form(semantic_block):
    referencing = []
    for entry in artifact_types():
        data_schema = entry["data_schema"]
        assert set(data_schema) == {"schema"}, (
            f"{entry['name']} carries an inline `data_schema`; the reference form "
            "is the only form (FR-003-CON-2)"
        )
        expected = f"schemas/{MODEL_OF[entry['name']]}.json"
        assert data_schema["schema"] == expected
        shipped = SCHEMAS_DIR / f"{MODEL_OF[entry['name']]}.json"
        assert shipped.is_file()
        referencing.append(entry["name"])
    assert sorted(semantic_block["exports"]) == sorted(referencing)


def _spelling(name: str) -> str:
    return name.replace("-", "").lower()


@pytest.mark.trace("TC-045", "FR-003-AC-9", "FR-003-CON-4")
def test_master_requirements_is_imported_from_iso_and_never_declared_here(
    manifest, semantic_block, mappings
):
    """PLAT-214: `master-requirements` has exactly one owner, the iso module."""
    own = {entry["name"] for entry in artifact_types()}
    assert not any(_spelling(name) == "masterrequirements" for name in own)
    assert not any(
        _spelling(name) == "masterrequirements" for name in semantic_block["exports"]
    )
    declared_kinds = set(manifest["doc_kinds"]) | {
        kind for grammar in manifest["grammars"] for kind in grammar["doc_kinds"]
    }
    assert not any(_spelling(kind) == "masterrequirements" for kind in declared_kinds)

    expected = {
        name
        for archetype in manifest["archetypes"]
        for name in archetype["composition"]["expected_artifacts"]
    }
    assert "master-requirements" in expected
    assert "agent-ix/spec-artifacts-iso" in semantic_block["imports"]
    assert "master-requirements" in (
        semantic_block["import_types"]["agent-ix/spec-artifacts-iso"]
    )
