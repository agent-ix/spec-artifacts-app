"""The manifest, the semantic block, and the digest binding.

Requirement ids live on the `trace` markers below, not here: a trace id on a
module docstring binds to nothing (quire-rs CR-061).
"""

from __future__ import annotations

import pytest
import yaml

import spec_artifacts_app as pack
from tests.conftest import (
    FR035_SCHEMA_DIGEST,
    FR035_SCHEMA_PATH,
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


def _validator(schema: dict):
    from jsonschema import Draft202012Validator

    return Draft202012Validator(schema)


def test_pack_exposes_manifest_path() -> None:
    assert pack.MANIFEST_PATH == pack.PACK_ROOT / "manifest.yaml"
    assert pack.MANIFEST_PATH.is_file()


@pytest.mark.trace("TC-036", "FR-001-AC-1")
def test_the_manifest_validates_against_the_bundled_fr035_schema(
    manifest, fr035_schema
):
    """Neither the missing-library nor the missing-schema branch skips.

    A gate that reports "passed" because it could not run is the failure mode
    this module's own history paid for: both preconditions are asserted, so an
    environment that cannot run the check fails it.
    """
    assert (
        FR035_SCHEMA_PATH.is_file()
    ), "the FR-035 schema is not bundled with the tests"
    errors = list(_validator(fr035_schema).iter_errors(manifest))
    assert not errors, [
        f"{'.'.join(str(p) for p in e.absolute_path)}: {e.message}" for e in errors
    ]


@pytest.mark.trace("TC-011", "FR-003-AC-1", "FR-003-AC-7", "FR-003-CON-1")
def test_the_semantic_block_carries_the_nine_admitted_keys_and_adds_no_required_key(
    manifest, semantic_block, fr035_schema
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

    # FR-003-CON-1 / AC-7: the same schema accepts the manifest a consumer that
    # predates the block would see.
    legacy = yaml.safe_load(LEGACY_MANIFEST_PATH.read_text())
    assert "semantic" not in legacy
    assert all("data_schema" not in entry for entry in legacy["artifact_types"])
    errors = list(_validator(fr035_schema).iter_errors(legacy))
    assert not errors, [
        f"{'.'.join(str(p) for p in e.absolute_path)}: {e.message}" for e in errors
    ]
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


@pytest.mark.trace("TC-016", "FR-003-AC-6")
def test_the_bundled_fr035_schema_rejects_the_four_malformed_forms(
    manifest, fr035_schema
):
    """The schema half of AC-6; its engine half is an expected failure below."""
    assert sha256_of(FR035_SCHEMA_PATH) == FR035_SCHEMA_DIGEST, (
        "the vendored FR-035 schema is not the revision this suite pins; a silent "
        "divergence from upstream is a failing test, not an assumption"
    )
    validator = _validator(fr035_schema)

    def rejected(mutate) -> list[str]:
        import copy

        candidate = copy.deepcopy(manifest)
        mutate(candidate)
        return [
            ".".join(str(p) for p in error.absolute_path) or "<root>"
            for error in validator.iter_errors(candidate)
        ]

    unknown_key = rejected(lambda m: m["semantic"].update(foo=1))
    assert unknown_key, "an unknown `semantic` key was accepted"
    assert any("semantic" in path for path in unknown_key)

    bad_package = rejected(lambda m: m["semantic"].update(package="ix://agent-ix/x"))
    assert bad_package, "a `package` that is not `<org>/<repo>` was accepted"

    bad_target = rejected(lambda m: m["semantic"].update(targets=["go"]))
    assert bad_target, "an unregistered `targets` value was accepted"


@pytest.mark.xfail(
    strict=True,
    reason=(
        'agent-ix/quoin#341: `ArtifactTypeEntry.data_schema` is typed `{"type": '
        '"object"}` in the FR-035 schema, while `ObjectTypeEntry.data_schema` '
        "carries the FR-073 `oneOf`. An ambiguous reference form on an artifact "
        "type is therefore accepted. Recorded as a strict expected failure so the "
        "fix announces itself, never worked around by relaxing this module's own "
        "manifest."
    ),
)
@pytest.mark.trace("TC-016", "FR-003-AC-6")
def test_the_fr035_schema_rejects_an_ambiguous_artifact_type_data_schema(
    manifest, fr035_schema
):
    import copy

    candidate = copy.deepcopy(manifest)
    candidate["artifact_types"][0]["data_schema"]["type"] = "object"
    errors = list(_validator(fr035_schema).iter_errors(candidate))
    assert (
        errors
    ), "a `data_schema` mixing the reference form with another key was accepted"
