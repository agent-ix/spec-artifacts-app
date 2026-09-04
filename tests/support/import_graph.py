"""The FR-003 import checks: missing, over-declared, self-referential, cyclic.

Four distinct diagnostics, deliberately. A cycle reported as a missing import
sends the reader to the wrong file, and an over-declared import reported as
nothing at all is a pin nobody can retire.

The graph is built from a **fixed set of manifests handed in by the caller** —
this module's own, plus dynamic-module fixtures a test synthesizes into a
temporary directory. It is never read from the machine's installed Filament
module root: a graph whose nodes depend on what a developer happens to have
installed is not reproducible, and NFR-001 says the suite is.
"""

from __future__ import annotations

import dataclasses
import pathlib
from typing import Any, Iterable

import yaml


@dataclasses.dataclass(frozen=True)
class ImportDiagnostic:
    code: str
    message: str
    modules: tuple[str, ...] = ()


def load_graph(roots: Iterable[pathlib.Path]) -> dict[str, list[str]]:
    """Build the import graph by reading `manifest.yaml` under each root.

    The caller hands in the roots — this module's own directory, plus whatever
    dynamic-module fixtures a test synthesized. Nothing here discovers a module
    on its own, and in particular nothing reads the machine's installed Filament
    module root: a graph whose nodes depend on what a developer happens to have
    installed is not reproducible, and NFR-001 says the suite is.

    A root with no `manifest.yaml`, or one whose manifest declares no `semantic`
    block, contributes no node — an unrelated directory in a fixture tree is not
    a module.
    """
    graph: dict[str, list[str]] = {}
    for root in roots:
        manifest_path = pathlib.Path(root) / "manifest.yaml"
        if not manifest_path.is_file():
            continue
        manifest = yaml.safe_load(manifest_path.read_text()) or {}
        if not manifest.get("semantic"):
            continue
        graph[package_of(manifest)] = sorted(imports_of(manifest))
    return graph


def imports_of(manifest: dict[str, Any]) -> dict[str, str]:
    return ((manifest.get("semantic") or {}).get("imports")) or {}


def package_of(manifest: dict[str, Any]) -> str:
    return ((manifest.get("semantic") or {}).get("package")) or manifest.get("name", "")


def check_self_import(manifest: dict[str, Any]) -> list[ImportDiagnostic]:
    """A module importing itself is the degenerate one-node cycle."""
    package = package_of(manifest)
    if package and package in imports_of(manifest):
        return [
            ImportDiagnostic(
                "semantic.self-import",
                f"{package} imports itself",
                (package,),
            )
        ]
    return []


def check_over_declared(
    manifest: dict[str, Any], referenced_modules: Iterable[str]
) -> list[ImportDiagnostic]:
    """A pinned package nothing reaches is a pin nobody can retire."""
    referenced = set(referenced_modules)
    return [
        ImportDiagnostic(
            "semantic.over-declared-import",
            f"{module} is pinned in semantic.imports but referenced by nothing",
            (module,),
        )
        for module in sorted(set(imports_of(manifest)) - referenced)
    ]


def check_reference(
    module: str,
    type_name: str,
    manifest: dict[str, Any],
    imported_types: dict[str, list[str]],
) -> list[ImportDiagnostic]:
    """Two distinct failures: the package is not pinned, or the type is not listed."""
    if module not in imports_of(manifest):
        return [
            ImportDiagnostic(
                "semantic.undeclared-import-module",
                f"module {module!r} (type {type_name!r}) is not pinned "
                "in semantic.imports",
                (module,),
            )
        ]
    if type_name not in imported_types.get(module, []):
        return [
            ImportDiagnostic(
                "semantic.undeclared-import-type",
                f"type {type_name!r} is not listed under imported_types for {module!r}",
                (module,),
            )
        ]
    return []


def find_cycles(graph: dict[str, Iterable[str]]) -> list[ImportDiagnostic]:
    """Every elementary cycle, each reported once, in deterministic order.

    Traversal starts from the lowest-sorting module on a cycle so the reported
    order does not depend on dict insertion order. A cycle that does not reach
    this module is reported the same way: the check is a property of the graph,
    not of any one module's position in it.
    """
    edges = {node: sorted(set(targets)) for node, targets in graph.items()}
    for targets in list(edges.values()):
        for target in targets:
            edges.setdefault(target, [])

    found: set[tuple[str, ...]] = set()

    def walk(node: str, path: list[str]) -> None:
        for target in edges[node]:
            if target == path[0]:
                found.add(_canonical(path))
            elif target not in path and target > path[0]:
                walk(target, path + [target])

    for start in sorted(edges):
        walk(start, [start])

    return [
        ImportDiagnostic(
            "semantic.import-cycle",
            "import cycle: " + " -> ".join(cycle + (cycle[0],)),
            cycle,
        )
        for cycle in sorted(found)
    ]


def _canonical(path: list[str]) -> tuple[str, ...]:
    """Rotate a cycle so it starts at its lowest-sorting module."""
    pivot = path.index(min(path))
    return tuple(path[pivot:] + path[:pivot])
