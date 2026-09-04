"""The skeletons, the locators they agree with, and additive compatibility.

Requirement ids live on the `trace` markers below, not here: a trace id on a
module docstring binds to nothing (quire-rs CR-061).
"""

from __future__ import annotations

import re
import subprocess

import pytest
import yaml

from tests.conftest import (
    BASELINE_DIR,
    MANIFEST_PATH,
    MODEL_OF,
    PACKAGE_ROOT,
    REPO_ROOT,
    SKELETONS_DIR,
    artifact_types,
    load_mappings,
    locators,
    require_quire,
)

SKELETON_OF = {
    "ApplicationSpec": ["application-spec.md", "application-spec.sysml.md"],
    "MasterRequirements": ["master-requirements.md"],
}

H2 = re.compile(r"^## (.+?)\s*$", re.MULTILINE)


def _headings(text: str) -> list[str]:
    """Level-2 headings outside fenced blocks and outside the leading comment."""
    body = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    out: list[str] = []
    inside = False
    for line in body.split("\n"):
        if line.startswith("```"):
            inside = not inside
            continue
        if inside:
            continue
        match = re.match(r"^## (.+?)\s*$", line)
        if match:
            out.append(match.group(1))
    return out


def _table_headers(text: str) -> set[str]:
    return {
        line.strip()
        for line in text.split("\n")
        if line.strip().startswith("|") and "---" not in line
    }


@pytest.mark.trace("TC-028", "FR-005-AC-1")
def test_each_artifact_type_ships_a_skeleton_agreeing_with_its_asserts_both_ways():
    mappings = load_mappings()
    for entry in artifact_types():
        match = locators(entry)
        properties = mappings["models"][MODEL_OF[entry["name"]]]["properties"]
        prose_only = {
            spec["heading"] for spec in properties.values() if spec.get("prose_only")
        }
        for name in SKELETON_OF[entry["name"]]:
            text = (SKELETONS_DIR / name).read_text()
            headings = _headings(text)
            assert len(headings) == len(
                set(headings)
            ), f"{name}: a level-2 heading repeats"

            # Forward: every asserted heading exists in the skeleton.
            for locator, spec in match.items():
                heading = spec.get("after_heading") or spec.get("under_section")
                if heading is None:
                    continue
                if locator == "properties_fence" and name.endswith(".sysml.md"):
                    assert (
                        heading in headings
                    ), f"{name}: '## {heading}' is asserted but absent"
                    continue
                if locator == "properties_fence":
                    continue
                assert (
                    heading in headings
                ), f"{name}: '## {heading}' is asserted but absent"

            # Reverse: every skeleton heading is asserted or declared prose-only.
            asserted = {
                spec.get("after_heading") or spec.get("under_section")
                for spec in match.values()
            } - {None}
            for heading in headings:
                assert heading in asserted or heading in prose_only, (
                    f"{name}: '## {heading}' is neither asserted by a locator nor "
                    "declared prose-only in mappings.yaml"
                )


@pytest.mark.trace("TC-028", "FR-005-AC-1", "StR-001-VC-2")
def test_validate_document_passes_every_shipped_skeleton():
    quire = require_quire()
    for artifact_type, names in SKELETON_OF.items():
        for name in names:
            result = quire.validate_document(
                artifact_type, str(PACKAGE_ROOT), (SKELETONS_DIR / name).read_text()
            )
            assert result["is_valid"], f"{name}: {result['errors']}"
            assert not result["errors"]


@pytest.mark.trace("TC-029", "FR-005-AC-2")
def test_the_sysml_alternate_declares_the_same_fields_in_the_same_order(build_record):
    table = build_record("ApplicationSpec", SKELETONS_DIR / "application-spec.md")
    fence = build_record("ApplicationSpec", SKELETONS_DIR / "application-spec.sysml.md")
    assert table.data["fields"] == fence.data["fields"], (
        "the typed table and the `sysml` fence are supposed to be two forms of "
        "one declaration; they produced different field lists"
    )
    assert [f["name"] for f in table.data["fields"]] == [
        "application_id",
        "slug",
        "display_name",
        "owning_team",
        "launched_at",
    ]


@pytest.mark.trace("TC-027", "FR-005-AC-6", "FR-005-CON-3")
def test_the_module_ships_no_template_and_no_template_ref():
    templates = list(PACKAGE_ROOT.rglob("*.md.j2"))
    assert not templates, f"the module ships templates: {templates}"
    assert "template_ref" not in MANIFEST_PATH.read_text(), (
        "the manifest still references a render template; render was removed "
        "ecosystem-wide and skeletons are the authoring source"
    )


@pytest.mark.trace("TC-018", "TC-032", "FR-005-AC-5", "FR-005-CON-1", "NFR-001-AC-3")
def test_every_locator_this_change_adds_is_optional():
    """Additive compatibility, measured against the branch point.

    Diffed rather than asserted: a claim that the change is additive is only
    worth what the comparison behind it is worth.
    """
    baseline = subprocess.run(
        ["git", "show", "origin/main:spec_artifacts_app/manifest.yaml"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    before = yaml.safe_load(baseline)
    before_locators = {
        entry["name"]: set(locators(entry)) for entry in before["artifact_types"]
    }
    added = 0
    for entry in artifact_types():
        previous = before_locators.get(entry["name"], set())
        for name, spec in locators(entry).items():
            if name in previous:
                continue
            added += 1
            if name in {"title", "purpose"}:
                assert spec["required"] is True, (
                    f"{entry['name']}.{name} is one of the two the pre-change "
                    "document already carries and must stay required"
                )
                continue
            assert spec["required"] is False, (
                f"{entry['name']}.{name} is a new required locator; every locator "
                "this change adds must be optional (FR-005-CON-1)"
            )
    assert (
        added > 0
    ), "no locator was added; the skeletons' sections would not be asserted"


@pytest.mark.trace("TC-018", "FR-004-AC-8", "FR-005-AC-5")
def test_the_pre_change_application_spec_still_validates_and_maps(
    build_record, schema_registry
):
    """The one existing ApplicationSpec document in this repository, unchanged."""
    baseline = BASELINE_DIR / "spec.md"
    assert baseline.is_file(), "the pre-change baseline is not committed"

    quire = require_quire()
    result = quire.validate_document(
        "ApplicationSpec", str(PACKAGE_ROOT), baseline.read_text()
    )
    assert result[
        "is_valid"
    ], f"the pre-change document no longer validates: {result['errors']}"

    record = build_record("ApplicationSpec", baseline)
    errors = list(schema_registry("ApplicationSpec").iter_errors(record.data))
    assert not errors, [
        ("/".join(str(p) for p in e.absolute_path), e.message) for e in errors
    ]


@pytest.mark.trace("TC-028", "FR-005-AC-1", "FR-005-AC-5")
def test_this_repositorys_own_application_spec_is_an_instance_of_the_contract(
    build_record, schema_registry
):
    """Dogfooding, and the only end-to-end case that is not a fixture.

    `spec/spec.md` is a real authored document, not a skeleton written to pass:
    it omits `## UI Rendering Requirements` because this module renders nothing,
    which is exactly the optionality FR-005-CON-1 exists to preserve. If the
    contract this module publishes cannot describe this module, it describes
    nothing.
    """
    document = REPO_ROOT / "spec" / "spec.md"

    quire = require_quire()
    result = quire.validate_document(
        "ApplicationSpec", str(PACKAGE_ROOT), document.read_text()
    )
    assert result["is_valid"], result["errors"]

    record = build_record("ApplicationSpec", document)
    errors = list(schema_registry("ApplicationSpec").iter_errors(record.data))
    assert not errors, [
        ("/".join(str(p) for p in e.absolute_path), e.message) for e in errors
    ]

    assert "renderingRequirements" not in record.data, (
        "the module authored a UI rendering table; it renders nothing, and the "
        "absent section is the point"
    )
    assert {row["source"]["module"] for row in record.data["requirements"]} == {
        "agent-ix/spec-artifacts-iso"
    }
