"""Module load, validation, and semantic extraction against the Quire engine.

Requirement ids live on the `trace` markers below, not here: a trace id on a
module docstring binds to nothing (quire-rs CR-061).
"""

from __future__ import annotations

import pathlib
import shutil

import pytest
import yaml

from tests.conftest import (
    LEGACY_MANIFEST_PATH,
    PACKAGE_ROOT,
    REPO_ROOT,
    SKELETONS_DIR,
    artifact_types,
)

ARCHETYPE_OF = {
    "application-spec.md": "ApplicationSpec",
    "application-spec.sysml.md": "ApplicationSpec",
    "master-requirements.md": "MasterRequirements",
}


def _module_copy(destination: pathlib.Path) -> pathlib.Path:
    """A copy of the shipped module, in a directory the caller owns."""
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / "spec_artifacts_app"
    shutil.copytree(PACKAGE_ROOT, target, ignore=shutil.ignore_patterns("__pycache__"))
    return target


@pytest.mark.trace("TC-013", "TC-034", "FR-003-AC-3", "IT-002-AC-1", "StR-001-VC-3")
def test_the_module_loads_validates_and_extracts_with_the_semantic_block_present(
    quire_engine, semantic_module, tmp_path
):
    declared = {entry["name"] for entry in artifact_types()}

    registry = quire_engine.Registry.load_from([str(REPO_ROOT)])
    names = set(registry.archetype_names())
    assert declared <= names, f"missing archetypes: {sorted(declared - names)}"

    for skeleton, archetype in ARCHETYPE_OF.items():
        text = (SKELETONS_DIR / skeleton).read_text()

        result = quire_engine.validate_document(archetype, str(PACKAGE_ROOT), text)
        assert result["is_valid"], f"{skeleton}: {result['errors']}"

        record = quire_engine.extract_semantic(
            {
                "markdown": text,
                "module": semantic_module,
                "path": f"spec_artifacts_app/skeletons/{skeleton}",
                "sourceIdentity": "ix://agent-ix/spec-artifacts-app/skeleton",
            }
        )
        errors = [d for d in record["diagnostics"] if d["severity"] == "error"]
        assert not errors, f"{skeleton}: {errors}"
        assert record["availability"]["fields"]["state"] == "available"
        assert record["package"] == semantic_module["package"]

    # The reference-form `data_schema` is reported verbatim rather than
    # resolved into a stored snapshot — filament-core-service#23 is the ticket
    # that would change this, and until it lands the reference is what a
    # consumer sees.
    for entry in artifact_types():
        assert set(entry["data_schema"]) == {"schema", "digest"}


@pytest.mark.trace("TC-034", "FR-003-AC-7", "IT-002-AC-1")
def test_the_legacy_manifest_registers_the_same_artifact_types(quire_engine, tmp_path):
    module = _module_copy(tmp_path / "legacy")
    (module / "manifest.yaml").write_text(LEGACY_MANIFEST_PATH.read_text())

    registry = quire_engine.Registry.load_from([str(tmp_path / "legacy")])
    names = set(registry.archetype_names())
    declared = {entry["name"] for entry in artifact_types()}
    assert declared <= names, (
        f"the manifest without the semantic block lost archetypes: "
        f"{sorted(declared - names)}"
    )


@pytest.mark.trace("TC-017", "FR-003-AC-8", "IT-002-AC-2")
def test_a_digest_mismatch_drops_the_bound_archetype(quire_engine, tmp_path):
    """The binding is real: altering one hex digit costs the archetype.

    This is the negative control for the expected failure below. Without it a
    red gate could mean the digest binding does nothing at all, rather than that
    its refusal is undiagnosed.
    """
    _module_copy(tmp_path / "control")
    intact = set(
        quire_engine.Registry.load_from([str(tmp_path / "control")]).archetype_names()
    )
    assert (
        "ApplicationSpec" in intact
    ), "the unmutated copy does not load; the control is broken"

    module = _module_copy(tmp_path / "mutant")
    text = (module / "manifest.yaml").read_text()
    recorded = yaml.safe_load(text)["artifact_types"][0]["data_schema"]["digest"]
    altered = recorded[:-1] + ("0" if recorded[-1] != "0" else "1")
    (module / "manifest.yaml").write_text(text.replace(recorded, altered))

    mutated = set(
        quire_engine.Registry.load_from([str(tmp_path / "mutant")]).archetype_names()
    )
    assert (
        "ApplicationSpec" not in mutated
    ), "a one-hex-digit digest edit changed nothing; the binding is a no-op"
    assert intact - mutated == {
        "ApplicationSpec"
    }, f"the mismatch cost more than the bound archetype: {sorted(intact - mutated)}"


@pytest.mark.xfail(
    strict=True,
    reason=(
        "agent-ix/quire-rs#394: a `data_schema` digest mismatch drops the bound "
        "archetype with no observable diagnostic and the module still loads, so "
        "nothing tells a consumer the binding was refused. Recorded as a strict "
        "expected failure naming the issue — never a skip, never a silent pass. "
        "The sibling silent-failure defect is agent-ix/quire-rs#221. The negative "
        "control above proves the binding itself is real."
    ),
)
@pytest.mark.trace("TC-017", "FR-003-AC-8", "IT-002-AC-2")
def test_a_digest_mismatch_is_refused_with_a_diagnostic(quire_engine, tmp_path):
    module = _module_copy(tmp_path / "diagnosed")
    text = (module / "manifest.yaml").read_text()
    recorded = yaml.safe_load(text)["artifact_types"][0]["data_schema"]["digest"]
    altered = recorded[:-1] + ("0" if recorded[-1] != "0" else "1")
    (module / "manifest.yaml").write_text(text.replace(recorded, altered))

    with pytest.raises(Exception) as raised:
        quire_engine.Registry.load_from([str(tmp_path / "diagnosed")])
    message = str(raised.value)
    assert (
        "ApplicationSpec" in message and "digest" in message
    ), f"the refusal names neither the artifact type nor the digest: {message}"
