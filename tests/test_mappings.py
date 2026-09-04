"""The mapping declaration, the reference oracle, and the failure discipline.

Requirement ids live on the `trace` markers below, not here: a trace id on a
module docstring binds to nothing (quire-rs CR-061).
"""

from __future__ import annotations

import json
import re

import pytest

from tests.conftest import (
    MAPPINGS_SCHEMA_PATH,
    MODEL_OF,
    PACKAGE_ROOT,
    REPO_ROOT,
    SCHEMAS_DIR,
    SKELETONS_DIR,
    artifact_types,
    locators,
)
from tests.support.reference_mapping import (
    DEFAULT_SOURCE_IDENTITY,
    MappingFailure,
    ReferenceMapping,
)

KINDS = {
    "frontmatter",
    "section",
    "typed-table",
    "sysml-fence",
    "ocl-clause",
    "provenance",
}
LOSSLESS_KINDS = {"section", "ocl-clause"}


def _mutate(text: str, *replacements: tuple[str, str]) -> str:
    for old, new in replacements:
        assert old in text, f"fixture text does not contain {old!r}"
        text = text.replace(old, new, 1)
    return text


def _build(mappings, manifest, model, text, path="fixture.md", **kwargs):
    return ReferenceMapping(mappings, manifest, model).build(text, path, **kwargs)


@pytest.mark.trace("TC-021", "FR-004-AC-1", "FR-004-AC-7")
def test_mappings_validates_and_declares_every_property_exactly_once(
    mappings, manifest, semantic_block
):
    from jsonschema import Draft202012Validator

    schema = json.loads(MAPPINGS_SCHEMA_PATH.read_text())
    errors = list(Draft202012Validator(schema).iter_errors(mappings))
    assert not errors, [
        ("/".join(str(p) for p in e.absolute_path), e.message) for e in errors
    ]

    assert set(mappings["kinds"]) == KINDS
    assert (
        set(semantic_block["mappings"]) == KINDS
    ), "the manifest's `semantic.mappings` and `mappings.yaml`'s `kinds` disagree"

    for entry in artifact_types():
        model = MODEL_OF[entry["name"]]
        declared = mappings["models"][model]
        emitted = json.loads((SCHEMAS_DIR / f"{model}.json").read_text())["properties"]
        assert set(declared["properties"]) == set(
            emitted
        ), f"{model}: mapping entries and emitted properties differ"
        assert declared["authority"] == "markdown"
        assert declared["round_trip"] == "derived"
        assert declared[
            "dropped_frontmatter_keys"
        ], f"{model} declares no dropped frontmatter keys; the loss must be stated"

        # `fields` is ONE entry with two forms, never two entries.
        fields = declared["properties"]["fields"]
        assert fields["kind"] == "typed-table"
        assert fields["alternate_form"]["kind"] == "sysml-fence"

        match = locators(entry)
        for name, spec in declared["properties"].items():
            assert spec["kind"] in KINDS
            assert spec["lossless"] is (
                spec["kind"] in LOSSLESS_KINDS
            ), f"{model}.{name}: `lossless` disagrees with its mapping kind"
            if spec["kind"] == "typed-table":
                assert (
                    spec["columns"] == match[spec["locator"]]["assert"]["columns"]
                ), f"{model}.{name}: column list differs from the locator's asserts"


@pytest.mark.trace("TC-022", "FR-004-AC-2")
def test_every_level_two_section_of_every_skeleton_is_typed_or_declared_prose_only(
    mappings,
):
    for entry in artifact_types():
        model = MODEL_OF[entry["name"]]
        properties = mappings["models"][model]["properties"]
        headed = {spec["heading"] for spec in properties.values() if "heading" in spec}
        prose_only = {
            spec["heading"] for spec in properties.values() if spec.get("prose_only")
        }
        names = (
            ["application-spec.md", "application-spec.sysml.md"]
            if entry["name"] == "ApplicationSpec"
            else ["master-requirements.md"]
        )
        for name in names:
            text = re.sub(
                r"<!--.*?-->", "", (SKELETONS_DIR / name).read_text(), flags=re.DOTALL
            )
            inside = False
            for line in text.split("\n"):
                if line.startswith("```"):
                    inside = not inside
                    continue
                if inside:
                    continue
                match = re.match(r"^## (.+?)\s*$", line)
                if not match:
                    continue
                heading = match.group(1)
                assert heading in headed or heading in prose_only, (
                    f"{name}: '## {heading}' fills no typed property and is not "
                    "declared prose-only"
                )


@pytest.mark.trace("TC-023", "FR-004-AC-3")
def test_each_skeleton_maps_to_a_record_that_validates_and_carries_the_typed_rows(
    build_record, schema_registry
):
    record = build_record("ApplicationSpec", SKELETONS_DIR / "application-spec.md")
    data = record.data
    assert not list(schema_registry("ApplicationSpec").iter_errors(data))

    assert data["fields"][0] == {
        "name": "application_id",
        "type": {"target": "UUID", "multiplicity": {"lower": 1, "upper": 1}},
        "identity": True,
    }
    assert data["boundaries"][0]["kind"] == "owned"
    assert data["capabilities"][0]["actors"] == ["AS-001-ACT-1", "AS-001-ACT-3"]
    assert data["actors"][3]["kind"] == "scheduler"
    assert data["interfaces"][0]["direction"] == "inbound"
    assert data["dataDependencies"][0]["source"] == {
        "module": "agent-ix/spec-artifacts-iso",
        "type": "StR",
    }
    assert data["renderingRequirements"][0]["verification"] == {
        "method": "Test",
        "testRefs": ["TC-101"],
        "annotation": "TC-101",
    }
    assert data["renderingRequirements"][2]["verification"] == {
        "method": "Demonstration",
        "testRefs": [],
    }
    assert data["requirements"][0]["kind"] == "StR"
    assert data["requirements"][0]["target"].startswith("ix://")

    other = build_record("MasterRequirements", SKELETONS_DIR / "master-requirements.md")
    assert not list(schema_registry("MasterRequirements").iter_errors(other.data))


@pytest.mark.trace("TC-019", "FR-004-AC-5", "FR-004-CON-2", "FR-005-AC-3")
def test_the_invariants_clauses_map_to_clause_refs_and_five_malformed_forms_fail(
    mappings, manifest, build_record
):
    path = SKELETONS_DIR / "application-spec.md"
    text = path.read_text()

    with_identity = build_record(
        "ApplicationSpec",
        path,
        source_identity="ix://agent-ix/spec-artifacts-app/AS-001",
    )
    clause = with_identity.data["invariants"][0]
    assert clause["language"] == "ocl"
    assert clause["clauseId"] == "EveryCapabilityNamesAnActor"
    assert (
        clause["sourceSpan"]["sourceIdentity"]
        == "ix://agent-ix/spec-artifacts-app/AS-001"
    )
    assert clause["sourceSpan"]["startLine"] < clause["sourceSpan"]["endLine"]
    assert not with_identity.advisories

    without = build_record("ApplicationSpec", path)
    assert without.data["invariants"][0]["sourceSpan"]["sourceIdentity"] == (
        DEFAULT_SOURCE_IDENTITY
    )
    assert [a.code for a in without.advisories] == [
        "semantic.source-identity-defaulted"
    ]

    # The clause text is carried verbatim beside the record, never inside it.
    entry = without.invariants_text[0]
    assert entry["clauseId"] == "EveryCapabilityNamesAnActor"
    lines = text.split("\n")
    fence_body = "\n".join(lines[entry["startLine"] : entry["endLine"] - 1])
    assert entry["text"] == fence_body
    assert "clauseText" not in without.data
    assert all("text" not in c for c in without.data["invariants"])

    malformed = {
        "clause-id-not-identifier": (
            "### EveryCapabilityNamesAnActor",
            "### not-an-identifier",
        ),
        "clause-fence-language": (
            "```ocl\ncontext ApplicationSpec\ninv EveryCapability",
            "```tla\ncontext ApplicationSpec\ninv EveryCapability",
        ),
        "clause-id-repeated": (
            "### DeferredBoundaryCarriesNoInterface",
            "### EveryCapabilityNamesAnActor",
        ),
    }
    for code, replacement in malformed.items():
        with pytest.raises(MappingFailure) as raised:
            _build(mappings, manifest, "ApplicationSpec", _mutate(text, replacement))
        assert code in raised.value.codes, f"expected {code}, got {raised.value.codes}"
        assert all(line > 0 for line in raised.value.lines)

    # A second fence under one heading.
    two_fences = text + "\n```ocl\ncontext ApplicationSpec\ninv Second: true\n```\n"
    with pytest.raises(MappingFailure) as raised:
        _build(mappings, manifest, "ApplicationSpec", two_fences)
    assert "clause-owns-two-fences" in raised.value.codes

    # A fence owned by no `###` heading.
    orphaned = text.replace(
        "## Invariants\n",
        "## Invariants\n\n```ocl\ncontext ApplicationSpec\ninv Orphan: true\n```\n",
        1,
    )
    with pytest.raises(MappingFailure) as raised:
        _build(mappings, manifest, "ApplicationSpec", orphaned)
    assert "orphan-fence" in raised.value.codes

    # A prose `## Invariants` leaves `invariants` absent and does not fail.
    prose = text[: text.index("\n## Invariants\n")] + (
        "\n## Invariants\n\nThe clauses this would enforce, still in prose.\n"
    )
    record = _build(mappings, manifest, "ApplicationSpec", prose)
    assert "invariants" not in record.data


@pytest.mark.trace("TC-025", "FR-004-AC-6")
def test_five_document_defects_each_fail_naming_the_line_and_are_reported_together(
    mappings, manifest
):
    text = (SKELETONS_DIR / "application-spec.md").read_text()

    cases = {
        "row-id-pattern": ("| AS-001-CAP-1 |", "| AS-001-XYZ-1 |"),
        "row-id-repeated": ("| AS-001-CAP-3 |", "| AS-001-CAP-2 |"),
        "duplicated-heading": ("## Actors\n", "## Capabilities\n"),
        "requirement-target-not-identity": (
            "| ix://agent-ix/orders-platform/StR-001 |",
            "| orders-platform/StR-001 |",
        ),
    }
    for code, replacement in cases.items():
        with pytest.raises(MappingFailure) as raised:
            _build(mappings, manifest, "ApplicationSpec", _mutate(text, replacement))
        assert code in raised.value.codes, f"expected {code}, got {raised.value.codes}"
        assert all(line > 0 for line in raised.value.lines), "a failure names no line"

    # Both `## Properties` forms in one artifact.
    both = text.replace(
        "\n## Boundaries\n",
        "\n```sysml\nattribute application_id : UUID[1..1] { identity }\n```\n"
        "\n## Boundaries\n",
        1,
    )
    with pytest.raises(MappingFailure) as raised:
        _build(mappings, manifest, "ApplicationSpec", both)
    assert "both-property-forms" in raised.value.codes

    # Every failure in one pass, and no record when any is found. The three are
    # deliberately independent: a defect that shadows another (renaming a
    # heading whose table also carries a bad row) would prove only that one
    # failure was found.
    three = _mutate(
        text,
        ("| AS-001-CAP-1 |", "| AS-001-XYZ-1 |"),
        ("| AS-001-ACT-1 |", "| AS-001-QQQ-1 |"),
        ("## Structure\n", "## Scope\n"),
    )
    with pytest.raises(MappingFailure) as raised:
        _build(mappings, manifest, "ApplicationSpec", three)
    assert len(raised.value.errors) >= 3, (
        f"only {len(raised.value.errors)} of three defects reported: "
        f"{raised.value.codes}"
    )
    assert raised.value.lines == sorted(
        raised.value.lines
    ), "failures are not reported in document order"


@pytest.mark.trace("TC-020", "FR-004-CON-3")
def test_nothing_in_the_module_or_its_support_writes_a_markdown_document():
    """Enumerated over the tree, never sampled: one unenumerated writer is the lie."""
    writers = re.compile(
        r"""\.write_text\(|\.write_bytes\(|open\([^)]*['"][wa]\+?b?['"]|shutil\.copy"""
    )
    offenders: list[str] = []
    roots = [PACKAGE_ROOT, REPO_ROOT / "tests" / "support"]
    for root in roots:
        for path in sorted(root.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            if writers.search(path.read_text()):
                offenders.append(str(path.relative_to(REPO_ROOT)))
    assert not offenders, (
        f"these files can write a document: {offenders}. The module ships data and "
        "the oracle reads Markdown; neither derives Markdown from a record."
    )
    # The module itself ships no Python beyond the resource entrypoint.
    module_sources = [
        p for p in PACKAGE_ROOT.rglob("*.py") if "__pycache__" not in p.parts
    ]
    assert [p.name for p in module_sources] == ["__init__.py"]
