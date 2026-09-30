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


@pytest.mark.trace(
    "TC-013",
    "TC-034",
    "FR-003-AC-1",
    "FR-003-AC-3",
    "IT-002-AC-1",
    "StR-001-VC-3",
)
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
        assert set(entry["data_schema"]) == {"schema"}


@pytest.mark.trace("TC-034", "FR-003-AC-7", "FR-003-CON-1", "IT-002-AC-1")
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


@pytest.mark.trace("TC-016", "FR-003-AC-6")
@pytest.mark.parametrize(
    ("label", "mutate"),
    [
        ("unknown-key", lambda block: block.update(foo=1)),
        ("bad-package", lambda block: block.update(package="ix://agent-ix/x")),
        ("unregistered-target", lambda block: block.update(targets=["go"])),
    ],
)
def test_a_manifest_the_contract_forbids_is_refused_at_load(
    quire_engine, tmp_path, label, mutate
):
    """FR-003-AC-6 against the engine that reads the manifest.

    quire applies the FR-035 module-manifest schema to the `semantic` block at
    load, so a form the contract forbids costs the module its archetypes. The
    oracle is the consumer, never a copy of the schema held here (PLAT-902).
    """
    control = _module_copy(tmp_path / f"{label}-control").parent
    assert quire_engine.Registry.load_from(
        [str(control)]
    ).archetype_names(), "the unmutated copy does not load; the control is broken"

    module = _module_copy(tmp_path / label)
    data = yaml.safe_load((module / "manifest.yaml").read_text())
    mutate(data["semantic"])
    (module / "manifest.yaml").write_text(yaml.safe_dump(data, sort_keys=False))
    loaded = quire_engine.Registry.load_from([str(tmp_path / label)]).archetype_names()
    assert not loaded, f"{label} loaded anyway: {sorted(loaded)}"
