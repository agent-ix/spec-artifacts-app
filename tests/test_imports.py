"""Imports, imported types, and the four import diagnostics.

Requirement ids live on the `trace` markers below, not here: a trace id on a
module docstring binds to nothing (quire-rs CR-061).
"""

from __future__ import annotations

import re

import pytest
import yaml

from tests.conftest import (
    NEGATIVE_DIR,
    SKELETONS_DIR,
    load_mappings,
)
from tests.support.import_graph import (
    check_over_declared,
    check_reference,
    check_self_import,
    find_cycles,
    imports_of,
    package_of,
)
from tests.support.reference_mapping import MappingFailure, ReferenceMapping

IMPORTED_CELL = re.compile(
    r"([a-z0-9][a-z0-9._-]*/[a-z0-9][a-z0-9._-]*)#([A-Za-z][A-Za-z0-9_-]*)"
)


def _referenced_pairs() -> set[tuple[str, str]]:
    """Every `<org>/<repo>#<Type>` this module authors, across every surface."""
    pairs: set[tuple[str, str]] = set()
    for path in sorted(SKELETONS_DIR.glob("*.md")):
        pairs |= set(IMPORTED_CELL.findall(path.read_text()))
    mappings = load_mappings()
    for module, types in mappings["imported_types"].items():
        pairs |= {(module, type_name) for type_name in types}
    return pairs


@pytest.mark.trace("TC-014", "FR-003-AC-4", "FR-003-CON-3")
def test_imports_are_pinned_by_version_and_every_reference_is_declared(
    manifest, mappings
):
    imports = imports_of(manifest)
    assert imports == {"agent-ix/spec-artifacts-iso": "0.2.0"}
    for module, version in imports.items():
        assert re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version), (
            f"{module} is pinned to {version!r}, which is not an exact version; "
            "FR-035 admits no other shape here"
        )
    assert mappings["imported_types"] == {
        "agent-ix/spec-artifacts-iso": ["StR", "US", "FR", "NFR", "IT", "TC"]
    }

    for module, type_name in sorted(_referenced_pairs()):
        assert not check_reference(
            module, type_name, manifest, mappings["imported_types"]
        ), f"{module}#{type_name} is referenced but not declared"

    # No self-import.
    assert not check_self_import(manifest)
    assert package_of(manifest) not in imports

    # No over-declared import: every pinned package is reached by something.
    reached = {module for module, _ in _referenced_pairs()}
    reached |= {
        "agent-ix/spec-artifacts-iso"
        for entry in manifest["archetypes"]
        for _ in (entry.get("composition") or {}).get("expected_artifacts", [])
    }
    assert not check_over_declared(manifest, reached)


@pytest.mark.trace("TC-014", "FR-003-AC-4")
def test_an_undeclared_module_and_an_undeclared_type_fail_distinctly(
    manifest, mappings
):
    imported_types = mappings["imported_types"]

    module_gap = check_reference(
        "agent-ix/not-imported", "StR", manifest, imported_types
    )
    assert [d.code for d in module_gap] == ["semantic.undeclared-import-module"]
    assert "agent-ix/not-imported" in module_gap[0].message

    type_gap = check_reference(
        "agent-ix/spec-artifacts-iso", "Glossary", manifest, imported_types
    )
    assert [d.code for d in type_gap] == ["semantic.undeclared-import-type"]
    assert "Glossary" in type_gap[0].message

    assert (
        module_gap[0].code != type_gap[0].code
    ), "a missing package and a missing type must be distinguishable"


@pytest.mark.trace("TC-014", "FR-003-CON-3")
def test_a_self_import_and_an_over_declared_import_each_have_their_own_diagnostic(
    manifest,
):
    import copy

    selfish = copy.deepcopy(manifest)
    selfish["semantic"]["imports"][package_of(manifest)] = "0.2.0"
    diagnostics = check_self_import(selfish)
    assert [d.code for d in diagnostics] == ["semantic.self-import"]
    assert diagnostics[0].modules == (package_of(manifest),)

    over = check_over_declared(manifest, referenced_modules=[])
    assert [d.code for d in over] == ["semantic.over-declared-import"]
    assert over[0].modules == ("agent-ix/spec-artifacts-iso",)


@pytest.mark.trace("TC-015", "FR-003-AC-5")
def test_cycles_are_found_over_synthesized_fixtures_in_deterministic_order(tmp_path):
    """Dynamic-module fixtures, written to a temporary directory by this test.

    They are synthesized rather than committed so a cycle fixture cannot be
    installed by accident, and read from here rather than from the machine's
    module root so the graph is the same on every machine.
    """

    def module(name: str, imports: dict[str, str]) -> dict:
        manifest = {
            "manifest_version": "1.0.0",
            "name": name.split("/")[-1],
            "version": "0.1.0",
            "semantic": {
                "contract_version": "1.0.0",
                "semantic_core": "0.1.0",
                "package": name,
                "imports": imports,
            },
        }
        path = tmp_path / name.replace("/", "__")
        path.mkdir(parents=True, exist_ok=True)
        (path / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False))
        return manifest

    def graph_of(*manifests: dict) -> dict[str, list[str]]:
        return {package_of(m): list(imports_of(m)) for m in manifests}

    # Acyclic: this must pass, or the check proves nothing about the cycles.
    acyclic = graph_of(
        module("agent-ix/app", {"agent-ix/iso": "0.2.0"}),
        module("agent-ix/iso", {}),
    )
    assert find_cycles(acyclic) == []

    two = graph_of(
        module("agent-ix/two-a", {"agent-ix/two-b": "0.1.0"}),
        module("agent-ix/two-b", {"agent-ix/two-a": "0.1.0"}),
    )
    found = find_cycles(two)
    assert [d.code for d in found] == ["semantic.import-cycle"]
    assert found[0].modules == ("agent-ix/two-a", "agent-ix/two-b")

    three = graph_of(
        module("agent-ix/three-c", {"agent-ix/three-a": "0.1.0"}),
        module("agent-ix/three-a", {"agent-ix/three-b": "0.1.0"}),
        module("agent-ix/three-b", {"agent-ix/three-c": "0.1.0"}),
    )
    found = find_cycles(three)
    assert [d.code for d in found] == ["semantic.import-cycle"]
    assert found[0].modules == (
        "agent-ix/three-a",
        "agent-ix/three-b",
        "agent-ix/three-c",
    ), (
        "the cycle is not reported starting from its lowest-sorting module, so the "
        "order depends on traversal accident"
    )
    assert (
        "agent-ix/three-a -> agent-ix/three-b -> agent-ix/three-c -> agent-ix/three-a"
        in (found[0].message)
    )

    # A cycle that does not reach this module is reported the same way.
    detached = graph_of(
        module("agent-ix/app2", {"agent-ix/iso2": "0.2.0"}),
        module("agent-ix/iso2", {}),
        module("agent-ix/x", {"agent-ix/y": "0.1.0"}),
        module("agent-ix/y", {"agent-ix/x": "0.1.0"}),
    )
    found = find_cycles(detached)
    assert [d.modules for d in found] == [("agent-ix/x", "agent-ix/y")]

    # A cycle is never reported as a missing import.
    assert all(d.code == "semantic.import-cycle" for d in find_cycles(three))


@pytest.mark.trace("TC-024", "FR-004-AC-4")
def test_an_imported_type_cell_maps_to_a_reference_and_an_undeclared_one_fails(
    manifest, mappings, build_record
):
    record = build_record("ApplicationSpec", SKELETONS_DIR / "application-spec.md")
    for row in record.data["dataDependencies"]:
        assert set(row["source"]) == {"module", "type"}, (
            "an ImportedTypeRef carries the reference pair and nothing else; a "
            "reference that grows fields has started duplicating"
        )
        assert row["source"]["module"] in imports_of(manifest)

    fixture = NEGATIVE_DIR / "imported-type-undeclared-module.md"
    with pytest.raises(MappingFailure) as raised:
        ReferenceMapping(mappings, manifest, "ApplicationSpec").build(
            fixture.read_text(), str(fixture)
        )
    assert "undeclared-import-module" in raised.value.codes
    message = raised.value.errors[0].message
    assert (
        "agent-ix/not-imported" in message and "StR" in message
    ), f"the failure names neither the module nor the type: {message}"
    assert all(line > 0 for line in raised.value.lines)
