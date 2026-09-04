"""The negative fixtures, and the gate that fails when one is accepted.

Requirement ids live on the `trace` markers below, not here: a trace id on a
module docstring binds to nothing (quire-rs CR-061).
"""

from __future__ import annotations

import pathlib

import pytest

from tests.conftest import NEGATIVE_DIR, PACKAGE_ROOT, require_quire
from tests.support.reference_mapping import (
    MappingFailure,
    ReferenceMapping,
    split_frontmatter,
)

#: `expect` -> the surface that must refuse the fixture. The value dispatches,
#: rather than the test trying every surface and accepting any refusal: a
#: fixture refused by the wrong check is a fixture that proves nothing.
SURFACES = {"validate", "mapping"}

#: Fixtures whose rule the *mapping* also enforces, and the code it uses. A
#: fixture the archetype refuses is not thereby excused from the oracle: both
#: read the same document and both are supposed to know the rule, so dispatching
#: only to the surface named in `expect` would leave the oracle's branch
#: untested and its diagnostic dead.
ALSO_REFUSED_BY_THE_MAPPING = {
    "missing-required-section.md": "missing-required-section",
    "table-columns-mismatch.md": "table-columns-mismatch",
    "row-id-wrong-prefix.md": "row-id-pattern",
}


def _fixtures() -> list[pathlib.Path]:
    return sorted(NEGATIVE_DIR.glob("*.md"))


def _expectation(path: pathlib.Path) -> tuple[str, str, str]:
    front, _ = split_frontmatter(path.read_text())
    assert "expect" in front, f"{path.name} declares no `expect`"
    assert "because" in front, f"{path.name} declares no `because`"
    surface, _, code = str(front["expect"]).partition(".")
    assert (
        surface in SURFACES
    ), f"{path.name}: `expect` names an unknown surface {surface!r}"
    assert code, f"{path.name}: `expect` names no diagnostic"
    return surface, code, str(front["because"])


@pytest.mark.trace("TC-026", "FR-005-AC-4", "FR-005-AC-7", "FR-005-CON-2")
def test_the_negative_fixture_set_covers_the_eight_demonstrated_rules():
    names = {path.name for path in _fixtures()}
    assert names == {
        "missing-required-section.md",
        "table-columns-mismatch.md",
        "row-id-wrong-prefix.md",
        "row-id-repeated.md",
        "properties-both-forms.md",
        "imported-type-undeclared-module.md",
        "clause-owns-two-fences.md",
        "orphan-ocl-fence.md",
    }, f"the negative fixture set moved: {sorted(names)}"

    for path in _fixtures():
        surface, code, because = _expectation(path)
        assert because.strip(), f"{path.name}: `because` is empty"
        assert code, f"{path.name}: `expect` carries no diagnostic for {surface}"


@pytest.mark.trace("TC-026", "TC-035", "FR-005-AC-4", "IT-002-AC-3")
def test_every_negative_fixture_is_refused_by_the_check_it_names(mappings, manifest):
    """An accepted negative fixture is a gate that is not gating."""
    quire = require_quire()
    accepted: list[str] = []

    for path in _fixtures():
        surface, code, _ = _expectation(path)
        text = path.read_text()

        if surface == "validate":
            result = quire.validate_document("ApplicationSpec", str(PACKAGE_ROOT), text)
            if result["is_valid"]:
                accepted.append(f"{path.name} (expected validate.{code})")
                continue
            reasons = {error.get("reason") for error in result["errors"]}
            assert (
                code in reasons
            ), f"{path.name}: refused with {sorted(reasons)}, not {code!r}"
            # A `missing` refusal names no line by design — the section that
            # would carry one is the thing that is absent. An `assert` refusal
            # always does, and that is the case worth pinning.
            if code == "assert":
                assert all(
                    error.get("line") for error in result["errors"]
                ), f"{path.name}: an assert refusal names no line"
            continue

        try:
            ReferenceMapping(mappings, manifest, "ApplicationSpec").build(
                text, str(path)
            )
        except MappingFailure as failure:
            assert (
                code in failure.codes
            ), f"{path.name}: refused with {failure.codes}, not {code!r}"
            assert all(
                line > 0 for line in failure.lines
            ), f"{path.name}: a refusal names no line"
        else:
            accepted.append(f"{path.name} (expected mapping.{code})")

    assert not accepted, f"negative fixtures that were accepted: {accepted}"


@pytest.mark.trace("TC-026", "TC-035", "FR-005-AC-4")
def test_the_mapping_also_refuses_the_fixtures_whose_rule_it_knows(mappings, manifest):
    """Both surfaces read the same document, so both must know the same rules."""
    for name, code in ALSO_REFUSED_BY_THE_MAPPING.items():
        path = NEGATIVE_DIR / name
        with pytest.raises(MappingFailure) as raised:
            ReferenceMapping(mappings, manifest, "ApplicationSpec").build(
                path.read_text(), str(path)
            )
        assert set(raised.value.codes) == {code}, (
            f"{name}: the mapping refused with {sorted(set(raised.value.codes))}, "
            f"not {code!r}"
        )


@pytest.mark.trace("TC-026", "FR-005-CON-2")
def test_each_negative_fixture_violates_exactly_one_rule(mappings, manifest):
    """A fixture that breaks two rules cannot tell you which one the refusal found."""
    for path in _fixtures():
        surface, code, _ = _expectation(path)
        if surface != "mapping":
            continue
        try:
            ReferenceMapping(mappings, manifest, "ApplicationSpec").build(
                path.read_text(), str(path)
            )
        except MappingFailure as failure:
            assert set(failure.codes) == {code}, (
                f"{path.name} violates {sorted(set(failure.codes))}; a negative "
                "fixture violates exactly one rule"
            )
