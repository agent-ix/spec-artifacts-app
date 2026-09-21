"""The manifest, the semantic block, and the digest binding.

Requirement ids live on the `trace` markers below, not here: a trace id on a
module docstring binds to nothing (quire-rs CR-061).
"""

from __future__ import annotations

import pytest
import yaml

import spec_artifacts_app as pack
from tests.conftest import (
    LEGACY_MANIFEST_PATH,
    MODEL_OF,
    SCHEMAS_DIR,
    artifact_types,
    sha256_of,
)

ADMITTED_SEMANTIC_KEYS = {
    "contract_version",
    "semantic_core",
    "package",
    "exports",
    "imports",
    "targets",
    "mappings",
    "compatibility_posture",
    "legacy_forms",
}


@pytest.mark.trace("TC-038", "FR-001")
def test_pack_exposes_manifest_path() -> None:
    """The activation pipeline imports this package and reads `MANIFEST_PATH`."""
    assert pack.MANIFEST_PATH == pack.PACK_ROOT / "manifest.yaml"
    assert pack.MANIFEST_PATH.is_file()


@pytest.mark.trace("TC-011", "FR-003-AC-1", "FR-003-AC-7", "FR-003-CON-1")
def test_the_semantic_block_carries_the_nine_admitted_keys_and_adds_no_required_key(
    manifest, semantic_block
):
    assert set(semantic_block) == ADMITTED_SEMANTIC_KEYS
    assert semantic_block["contract_version"] == "1.0.0"
    assert semantic_block["semantic_core"] == "0.1.0"
    assert semantic_block["package"] == "agent-ix/spec-artifacts-app"
    assert semantic_block["exports"] == ["ApplicationSpec", "MasterRequirements"]
    assert semantic_block["imports"] == {"agent-ix/spec-artifacts-iso": "0.2.0"}
    assert semantic_block["targets"] == ["json-schema", "markdown"]
    assert semantic_block["compatibility_posture"] == "additive"
    assert semantic_block["legacy_forms"] == "warning"
    assert "sweep_report" not in semantic_block, (
        "`sweep_report` is required only by `legacy_forms: error`; declaring it "
        "under `warning` would claim a sweep that never happened"
    )

    # FR-003-CON-1 / AC-7: the manifest a consumer that predates the block would
    # see carries no root key and no artifact-type key this module added, and
    # declares the same artifact types. That it still *loads* is asserted against
    # the real engine in TC-034, which is the only oracle for it: no copy of the
    # module-manifest schema lives in this repository (PLAT-902).
    legacy = yaml.safe_load(LEGACY_MANIFEST_PATH.read_text())
    assert "semantic" not in legacy
    assert all("data_schema" not in entry for entry in legacy["artifact_types"])
    assert set(legacy) == set(manifest) - {"semantic"}
    assert [e["name"] for e in legacy["artifact_types"]] == [
        e["name"] for e in manifest["artifact_types"]
    ]


@pytest.mark.trace("TC-012", "FR-003-AC-2", "FR-003-CON-2")
def test_every_export_carries_the_reference_form_and_a_matching_digest(semantic_block):
    referencing = []
    for entry in artifact_types():
        data_schema = entry["data_schema"]
        assert set(data_schema) == {"schema", "digest"}, (
            f"{entry['name']} carries an inline `data_schema`; the reference form "
            "is the only form (FR-003-CON-2)"
        )
        expected = f"schemas/{MODEL_OF[entry['name']]}.json"
        assert data_schema["schema"] == expected
        shipped = SCHEMAS_DIR / f"{MODEL_OF[entry['name']]}.json"
        assert shipped.is_file()
        assert data_schema["digest"] == sha256_of(shipped), (
            f"{entry['name']}: recorded {data_schema['digest']}, "
            f"computed {sha256_of(shipped)}"
        )
        referencing.append(entry["name"])
    assert sorted(semantic_block["exports"]) == sorted(referencing)


@pytest.mark.trace("TC-012", "FR-003-AC-2")
def test_a_one_byte_schema_edit_breaks_the_digest_naming_both_values(tmp_path):
    """The digest binding is real: it moves when the bytes move."""
    victim = SCHEMAS_DIR / "ApplicationSpec.json"
    mutated = tmp_path / "ApplicationSpec.json"
    mutated.write_text(
        victim.read_text().replace("ApplicationSpec", "ApplicationSpeC", 1)
    )
    recorded = next(
        e["data_schema"]["digest"]
        for e in artifact_types()
        if e["name"] == "ApplicationSpec"
    )
    computed = sha256_of(mutated)
    assert (
        recorded != computed
    ), "a one-byte edit produced the same digest; the binding is a no-op"
