#!/usr/bin/env python3
"""Build ``spec_artifacts_app/mappings.yaml`` from the manifest (FR-004).

The mapping declaration says, per model property, which Markdown form fills it
and whether that form round-trips byte-for-byte. It is data the module ships,
not code it runs — but hand-maintaining it beside a manifest that owns the same
column lists is how the two drift, so the columns, locator names, and id
patterns are read out of ``manifest.yaml`` here and never retyped.

    poetry run python scripts/build_mappings.py           # rewrite
    poetry run python scripts/build_mappings.py --check    # fail on any drift

``--check`` writes nothing, so a stale mapping is a red gate rather than a
silent repair.
"""

from __future__ import annotations

import argparse
import pathlib
import sys
from typing import Any

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PACKAGE_ROOT = REPO_ROOT / "spec_artifacts_app"
MANIFEST_PATH = PACKAGE_ROOT / "manifest.yaml"
MAPPINGS_PATH = PACKAGE_ROOT / "mappings.yaml"

MODULE = "agent-ix/spec-artifacts-app"

KINDS = [
    "frontmatter",
    "section",
    "typed-table",
    "sysml-fence",
    "ocl-clause",
    "provenance",
]

#: Types this module references from each package ``semantic.imports`` pins.
#: The FR-035 contract has no place for a per-package type list
#: (agent-ix/quoin#339), so it lives here and the suite checks an
#: ``ImportedTypeRef`` against both: the package in the manifest, the type here.
IMPORTED_TYPES = {"agent-ix/spec-artifacts-iso": ["StR", "US", "FR", "NFR", "IT", "TC"]}

#: Frontmatter keys the mapping drops. The frontmatter schemas allow additional
#: keys and the emitted models are sealed, so an undeclared key cannot reach the
#: record; declaring the set is what makes the loss stated rather than silent.
DROPPED_FRONTMATTER_KEYS = [
    "component_type",
    "depends_on",
    "description",
    "implementation_language",
    "object",
    "okf_version",
    "org",
    "security_critical",
    "standards_alignment",
    "tags",
]

#: locator name -> (record property, heading, required)
SECTIONS = {
    "purpose": ("purpose", "Purpose", True),
    "scope": ("scope", "Scope", False),
    "system_overview": ("systemOverview", "System Overview", False),
    "structure": ("structure", "Structure", False),
    "requirements_architecture": (
        "requirementsArchitecture",
        "Requirements Architecture",
        False,
    ),
    "references": ("references", "References", False),
}

#: table locator name -> (record property, heading, row model, per-cell parse)
TABLES = {
    "boundaries_table": (
        "boundaries",
        "Boundaries",
        "Boundary",
        {"ID": "id", "Name": "text", "Kind": "enum", "Description": "text"},
    ),
    "capabilities_table": (
        "capabilities",
        "Capabilities",
        "Capability",
        {"ID": "id", "Name": "text", "Description": "text", "Actors": "id-list"},
    ),
    "actors_table": (
        "actors",
        "Actors",
        "Actor",
        {"ID": "id", "Name": "text", "Kind": "enum", "Description": "text"},
    ),
    "interfaces_table": (
        "interfaces",
        "Interfaces",
        "Interface",
        {
            "ID": "id",
            "Name": "text",
            "Kind": "enum",
            "Direction": "enum",
            "Contract": "text",
        },
    ),
    "data_dependencies_table": (
        "dataDependencies",
        "Data Dependencies",
        "DataDependency",
        {"ID": "id", "Name": "text", "Source": "imported-type-ref", "Access": "enum"},
    ),
    "rendering_requirements_table": (
        "renderingRequirements",
        "UI Rendering Requirements",
        "RenderingRequirement",
        {
            "ID": "id",
            "Surface": "text",
            "Requirement": "text",
            "Verification": "verification",
        },
    ),
    "requirements_table": (
        "requirements",
        "Requirements",
        "RequirementRef",
        {"ID": "id", "Kind": "enum", "Source": "imported-type-ref", "Target": "text"},
    ),
}

MODEL_OF = {
    "ApplicationSpec": "ApplicationSpec",
    "MasterRequirements": "MasterRequirements",
}


class NoAliasDumper(yaml.SafeDumper):
    """Dump repeated structures in full rather than as YAML anchors."""

    def ignore_aliases(self, data: Any) -> bool:  # noqa: D102
        return True


def load_manifest() -> dict[str, Any]:
    return yaml.safe_load(MANIFEST_PATH.read_text())


def locators(artifact_type: dict[str, Any]) -> dict[str, dict[str, Any]]:
    body = artifact_type.get("body_extraction") or {}
    return ((body.get("yield_pattern") or {}).get("match")) or {}


def properties_for(artifact_type: dict[str, Any]) -> dict[str, Any]:
    """Build the property map of one artifact type from its own locators."""
    match = locators(artifact_type)
    props: dict[str, Any] = {
        "id": {
            "kind": "frontmatter",
            "path": ["id"],
            "required": True,
            "lossless": False,
        },
        # The `title` locator asserts the document's H1 exists; the value the
        # record carries comes from frontmatter, which is the only place a
        # title is authoritative here. The locator is named so no locator is
        # left unmapped (FR-002-CON-1).
        "title": {
            "kind": "frontmatter",
            "path": ["title"],
            "locator": "title",
            "required": True,
            "lossless": False,
        },
        "type": {
            "kind": "frontmatter",
            "path": ["type"],
            "required": True,
            "lossless": False,
        },
        "status": {"kind": "frontmatter", "path": ["status"], "lossless": False},
        "relationships": {
            "kind": "frontmatter",
            "path": ["relationships"],
            "lossless": False,
        },
        "provenance": {"kind": "provenance", "lossless": False},
    }

    for locator, (prop, heading, required) in SECTIONS.items():
        if locator not in match:
            continue
        entry: dict[str, Any] = {
            "kind": "section",
            "heading": heading,
            "locator": locator,
            "lossless": True,
        }
        if required:
            entry["required"] = True
        props[prop] = entry

    if "properties_table" in match:
        columns = list(match["properties_table"]["assert"]["columns"])
        props["fields"] = {
            "kind": "typed-table",
            "heading": "Properties",
            "locator": "properties_table",
            "columns": columns,
            "row_model": "semantic-core FieldDecl",
            "cell_parses": {
                "Field": "text",
                "Type": "text",
                "Multiplicity": "multiplicity",
                "Constraints": "constraints",
            },
            "alternate_form": {
                "kind": "sysml-fence",
                "heading": "Properties",
                "language": "sysml",
                "locator": "properties_fence",
            },
            "lossless": False,
        }

    for locator, (prop, heading, row_model, parses) in TABLES.items():
        if locator not in match:
            continue
        assertion = match[locator]["assert"]
        props[prop] = {
            "kind": "typed-table",
            "heading": heading,
            "locator": locator,
            "columns": list(assertion["columns"]),
            "row_model": row_model,
            "id_pattern": assertion["id_pattern"],
            "cell_parses": dict(parses),
            "lossless": False,
        }

    if "invariants" in match:
        props["invariants"] = {
            "kind": "ocl-clause",
            "heading": "Invariants",
            "locator": "invariants",
            "language": "ocl",
            "lossless": True,
        }
    return props


def build() -> str:
    manifest = load_manifest()
    models: dict[str, Any] = {}
    for artifact_type in manifest["artifact_types"]:
        name = artifact_type["name"]
        model = MODEL_OF[name]
        models[model] = {
            "schema": f"schemas/{model}.json",
            "artifact_type": name,
            "authority": "markdown",
            "round_trip": "derived",
            "dropped_frontmatter_keys": list(DROPPED_FRONTMATTER_KEYS),
            "properties": properties_for(artifact_type),
        }

    document = {
        "mapping_version": "1.0.0",
        "module": MODULE,
        "kinds": list(KINDS),
        "imported_types": {k: list(v) for k, v in IMPORTED_TYPES.items()},
        "models": models,
    }
    return HEADER + yaml.dump(
        document,
        Dumper=NoAliasDumper,
        sort_keys=False,
        width=100,
        default_flow_style=False,
    )


HEADER = """# Markdown mapping declaration for spec-artifacts-app (FR-004).
#
# Markdown is the authority; the record is a derived projection. Every property
# of every exported model appears here exactly once, with the mapping kind that
# fills it, the Markdown form it reads, and whether that form round-trips
# byte-for-byte (`lossless`).
#
# `imported_types` says which types this module references from each package
# `manifest.yaml`'s `semantic.imports` pins. The FR-035 contract types `imports`
# as package -> exact semver and has no place for a per-package type list
# (agent-ix/quoin#339), so it is declared here, and the suite checks every
# `ImportedTypeRef` against both: the package in the manifest, the type here.
#
# GENERATED by `scripts/build_mappings.py` from `manifest.yaml`, so a column
# list, a locator name, or an id pattern is written once and cannot drift.
# Edit that script, not this file. `make mappings-check` fails on any drift.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="fail on drift; write nothing"
    )
    args = parser.parse_args()

    text = build()
    if args.check:
        current = MAPPINGS_PATH.read_text() if MAPPINGS_PATH.exists() else None
        if current != text:
            print(
                f"{MAPPINGS_PATH.relative_to(REPO_ROOT)} differs from the "
                "manifest it derives from; run `make schemas` and commit it.",
                file=sys.stderr,
            )
            return 1
        print(
            "mappings-check: "
            f"{MAPPINGS_PATH.relative_to(REPO_ROOT)} matches the manifest"
        )
        return 0
    MAPPINGS_PATH.write_text(text)
    print(f"mappings: wrote {MAPPINGS_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
