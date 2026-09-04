"""Every diagnostic the reference mapping can emit, exercised at least once.

A diagnostic no test reaches is a diagnostic nobody has read the behaviour of.
The code review of this change found nine of them unexecuted; these tests exist
so the oracle's refusal set is measured rather than assumed, and so the coverage
gate over `tests/support` can be 100% and stay honest.

Requirement ids live on the `trace` markers, not in this docstring.
"""

from __future__ import annotations

import pytest

from tests.conftest import SKELETONS_DIR
from tests.support.reference_mapping import (
    MappingFailure,
    ReferenceMapping,
    _number_or_string,
    _split_row,
    fenced_blocks,
    parse_constraints,
    parse_imported_type_ref,
    parse_multiplicity,
    parse_verification,
    sections,
    split_frontmatter,
)

APP = "ApplicationSpec"


def _skeleton() -> str:
    return (SKELETONS_DIR / "application-spec.md").read_text()


def _build(mappings, manifest, text, model=APP):
    return ReferenceMapping(mappings, manifest, model).build(text, "fixture.md")


def _fails(mappings, manifest, text, model=APP) -> MappingFailure:
    with pytest.raises(MappingFailure) as raised:
        _build(mappings, manifest, text, model)
    return raised.value


@pytest.mark.trace("TC-039", "FR-004-AC-6")
def test_a_document_with_no_frontmatter_yields_an_empty_mapping_not_a_crash():
    front, body_start = split_frontmatter(
        "# [AS-001] No frontmatter\n\n## Purpose\n\nText.\n"
    )
    assert front == {}
    assert body_start == 1


@pytest.mark.trace("TC-039", "FR-004-AC-3")
def test_table_cells_survive_an_escaped_pipe_and_a_trailing_empty_cell():
    assert _split_row(r"| a \| b | c |") == [r"a \| b", "c"]
    assert _split_row("| a | b") == ["a", "b"]


@pytest.mark.trace("TC-039", "FR-004-AC-3")
def test_a_multiplicity_cell_outside_the_admitted_forms_is_not_a_multiplicity():
    assert parse_multiplicity("1..*") == {"lower": 1}
    assert parse_multiplicity("3") == {"lower": 3, "upper": 3}
    assert parse_multiplicity("many") is None
    assert parse_multiplicity("") is None


@pytest.mark.trace("TC-039", "FR-004-AC-3")
def test_a_verification_cell_with_no_parentheses_carries_the_method_alone():
    assert parse_verification("Inspection") == {"method": "Inspection", "testRefs": []}
    assert parse_verification("Test (TC-1, TC-2)")["testRefs"] == ["TC-1", "TC-2"]


@pytest.mark.trace("TC-039", "FR-004-AC-3")
def test_the_closed_constraint_vocabulary_admits_its_members_and_refuses_the_rest():
    admitted, identity, errors = parse_constraints(
        "identity, nonEmpty, unique, minLength: 1, maxLength: 9, min: 2, max: 3.5, "
        "enumValues: a|b, format: iso:date, pattern: /^x$/",
        7,
    )
    assert identity is True
    assert not errors
    keywords = [c["keyword"] for c in admitted]
    assert keywords == [
        "nonEmpty",
        "unique",
        "minLength",
        "maxLength",
        "min",
        "max",
        "enumValues",
        "format",
        "pattern",
    ]

    _, _, refused = parse_constraints("frobnicate: 3", 11)
    assert [e.code for e in refused] == ["unknown-constraint-keyword"]
    assert refused[0].line == 11

    # An unslashed pattern is not a pattern: the delimiters are what let a comma
    # live inside the regex without splitting the cell.
    _, _, unslashed = parse_constraints("pattern: ^x$", 12)
    assert [e.code for e in unslashed] == ["unknown-constraint-keyword"]


@pytest.mark.trace("TC-039", "FR-004-AC-3")
def test_a_constraint_value_is_read_as_a_number_where_it_is_one():
    assert _number_or_string("4") == 4
    assert _number_or_string("4.5") == 4.5
    assert _number_or_string("4.5.6") == "4.5.6"


@pytest.mark.trace("TC-040", "FR-004-AC-4")
def test_a_malformed_imported_type_cell_is_refused_before_the_declaration_check():
    value, errors = parse_imported_type_ref("not a reference", 3, {}, {})
    assert value is None
    assert [e.code for e in errors] == ["imported-type-malformed"]

    value, errors = parse_imported_type_ref(
        "agent-ix/spec-artifacts-iso#Glossary",
        4,
        {"agent-ix/spec-artifacts-iso": ["FR"]},
        {"agent-ix/spec-artifacts-iso": "0.2.0"},
    )
    assert value is None
    assert [e.code for e in errors] == ["undeclared-import-type"]


@pytest.mark.trace("TC-041", "FR-004-AC-6")
def test_a_table_row_with_the_wrong_cell_count_is_refused_naming_the_line(
    mappings, manifest
):
    text = _skeleton().replace(
        "| AS-001-CAP-1 | Submit an order |",
        "| AS-001-CAP-1 | Submit an order | extra |",
        1,
    )
    failure = _fails(mappings, manifest, text)
    assert "row-cell-count" in failure.codes
    assert all(line > 0 for line in failure.lines)


@pytest.mark.trace("TC-041", "FR-004-AC-3")
def test_a_properties_table_with_a_wrong_header_or_a_bad_row_is_refused(
    mappings, manifest
):
    renamed = _skeleton().replace(
        "| Field | Type | Multiplicity | Constraints |",
        "| Field | Type | Cardinality | Constraints |",
        1,
    )
    assert "table-columns-mismatch" in _fails(mappings, manifest, renamed).codes

    short = _skeleton().replace(
        "| application_id | UUID | 1..1 | identity |",
        "| application_id | UUID | 1..1 |",
        1,
    )
    assert "row-cell-count" in _fails(mappings, manifest, short).codes

    bad_multiplicity = _skeleton().replace(
        "| application_id | UUID | 1..1 | identity |",
        "| application_id | UUID | lots | identity |",
        1,
    )
    assert (
        "multiplicity-malformed" in _fails(mappings, manifest, bad_multiplicity).codes
    )


@pytest.mark.trace("TC-041", "FR-005-AC-2")
def test_a_sysml_declaration_that_is_not_a_field_is_refused_naming_the_line(
    mappings, manifest
):
    text = (
        (SKELETONS_DIR / "application-spec.sysml.md")
        .read_text()
        .replace(
            "attribute slug : String[1..1] { pattern: /^[a-z][a-z0-9-]*$/ }",
            "this line is not a declaration",
            1,
        )
    )
    failure = _fails(mappings, manifest, text)
    assert "sysml-declaration-malformed" in failure.codes


@pytest.mark.trace("TC-041", "FR-004-AC-5")
def test_an_unterminated_clause_fence_is_refused(mappings, manifest):
    text = _skeleton().rstrip("\n")
    text = text[: text.rfind("```")] + "context ApplicationSpec\ninv Unclosed: true\n"
    failure = _fails(mappings, manifest, text)
    assert "clause-fence-unterminated" in failure.codes

    blocks = fenced_blocks(sections(text)[0]["Invariants"])
    assert any(block["closed"] is False for block in blocks)


@pytest.mark.trace("TC-042", "FR-004-AC-1")
def test_an_absent_optional_frontmatter_key_and_an_absent_table_leave_the_field_absent(
    mappings, manifest
):
    text = _skeleton().replace("status: DRAFT\n", "", 1)
    record = _build(mappings, manifest, text)
    assert "status" not in record.data

    no_relationships = _skeleton()
    start = no_relationships.index("relationships:")
    end = no_relationships.index("---", start)
    record = _build(
        mappings, manifest, no_relationships[:start] + no_relationships[end:]
    )
    assert record.data["relationships"] == []

    # A section present but carrying no table maps to an absent field, never `[]`.
    prose_table = _skeleton()
    head = prose_table.index("\n## Boundaries\n")
    tail = prose_table.index("\n## Capabilities\n")
    prose_table = (
        prose_table[:head]
        + "\n## Boundaries\n\nStill prose; the table has not been written yet.\n"
        + prose_table[tail:]
    )
    record = _build(mappings, manifest, prose_table)
    assert "boundaries" not in record.data


@pytest.mark.trace("TC-042", "FR-004-AC-2")
def test_a_prose_only_mapping_entry_is_honoured_by_the_declaration(mappings, manifest):
    """`prose_only` is the explicit designation FR-004-AC-2 demands exist.

    No section of this module's own skeletons needs it — every one is typed —
    so the affordance is exercised here rather than left as an unreachable
    branch of the schema that nobody has ever validated a document against.
    """
    import copy
    import json

    from jsonschema import Draft202012Validator

    from tests.conftest import MAPPINGS_SCHEMA_PATH

    candidate = copy.deepcopy(mappings)
    candidate["models"]["ApplicationSpec"]["properties"]["scope"] = {
        "kind": "section",
        "heading": "Scope",
        "locator": "scope",
        "lossless": True,
        "prose_only": True,
        "reason": "narrative boundary statement with no typed form",
    }
    schema = json.loads(MAPPINGS_SCHEMA_PATH.read_text())
    assert not list(Draft202012Validator(schema).iter_errors(candidate))

    # And the schema refuses the designation without its reason: an unexplained
    # prose-only section is the thing the requirement exists to prevent.
    candidate["models"]["ApplicationSpec"]["properties"]["scope"].pop("reason")
    assert list(Draft202012Validator(schema).iter_errors(candidate))


@pytest.mark.trace("TC-042", "FR-004-AC-6")
def test_the_mapping_emits_no_record_when_any_failure_is_found(mappings, manifest):
    """No partial record: a caller must not be able to mistake one for good."""
    text = _skeleton().replace("| AS-001-CAP-1 |", "| AS-001-XYZ-1 |", 1)
    failure = _fails(mappings, manifest, text)
    assert failure.errors
    assert "1 mapping failure" in str(failure) or "mapping failure(s)" in str(failure)
    # `build` raises rather than returning, so there is no object to inspect —
    # which is the assertion: the only way to get a record is for it to be whole.
    with pytest.raises(MappingFailure):
        _build(mappings, manifest, text)


@pytest.mark.trace("TC-042", "FR-004-AC-3")
def test_a_properties_section_carrying_neither_form_leaves_fields_absent(
    mappings, manifest
):
    text = _skeleton()
    head = text.index("\n## Properties\n")
    tail = text.index("\n## Boundaries\n")
    stripped = (
        text[:head]
        + "\n## Properties\n\nThe fields this declares, still to be typed.\n"
        + text[tail:]
    )
    record = _build(mappings, manifest, stripped)
    assert "fields" not in record.data


@pytest.mark.trace("TC-042", "FR-005-AC-2")
def test_a_blank_line_inside_a_sysml_fence_is_not_a_declaration(mappings, manifest):
    text = (
        (SKELETONS_DIR / "application-spec.sysml.md")
        .read_text()
        .replace(
            "attribute owning_team : String[1..1] { nonEmpty }",
            "\nattribute owning_team : String[1..1] { nonEmpty }",
            1,
        )
    )
    record = _build(mappings, manifest, text)
    assert [field["name"] for field in record.data["fields"]] == [
        "application_id",
        "slug",
        "display_name",
        "owning_team",
        "launched_at",
    ]


@pytest.mark.trace("TC-042", "FR-004-AC-5")
def test_a_clause_heading_owning_no_fence_is_skipped_rather_than_refused(
    mappings, manifest
):
    """A heading with no fence is an unfinished clause, not a malformed one.

    Refusing it would make `## Invariants` un-draftable: an author who writes
    the heading before the clause would be unable to save the document.
    """
    text = _skeleton().replace(
        "### EveryCapabilityNamesAnActor\n",
        "### NotYetWritten\n\n### EveryCapabilityNamesAnActor\n",
        1,
    )
    record = _build(mappings, manifest, text)
    assert [clause["clauseId"] for clause in record.data["invariants"]] == [
        "EveryCapabilityNamesAnActor",
        "DeferredBoundaryCarriesNoInterface",
    ]
