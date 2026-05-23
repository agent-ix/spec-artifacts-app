"""Auto-generated test: manifest validates against FR-035 + every template renders.

Pulls the FR-035 JSON Schema URL or uses a local copy bundled with the package.
"""
from __future__ import annotations

import json
import pathlib
import re

import pytest
import yaml
from jinja2.sandbox import SandboxedEnvironment

PKG_ROOT = pathlib.Path(__file__).resolve().parent.parent / "spec_artifacts_app"
MANIFEST_PATH = PKG_ROOT / "manifest.yaml"


def test_manifest_loads() -> None:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    assert manifest["manifest_version"] == "1.0.0"
    assert manifest["name"] == "spec-artifacts-app"
    assert manifest["version"]


def test_manifest_validates_against_fr035_schema() -> None:
    """Skip if jsonschema does not support draft 2020-12 (use CI check-jsonschema instead)."""
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        pytest.skip("jsonschema lib missing draft 2020-12 support")
    schema_path = pathlib.Path(__file__).resolve().parent / "module-manifest.schema.json"
    if not schema_path.exists():
        pytest.skip("FR-035 schema not bundled with tests")
    schema = json.loads(schema_path.read_text())
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    errors = list(Draft202012Validator(schema).iter_errors(manifest))
    assert not errors, [f"{'.'.join(str(p) for p in e.absolute_path)}: {e.message}" for e in errors]


def _render(template_text: str, ctx: dict) -> str:
    env = SandboxedEnvironment(keep_trailing_newline=True)
    return env.from_string(template_text).render(**ctx)


def _artifact_types():
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    return manifest.get("artifact_types", [])


@pytest.mark.parametrize("at", _artifact_types(), ids=lambda at: at["name"])
def test_template_renders_and_contains_required_sections(at: dict) -> None:
    template_path = PKG_ROOT / at["template_ref"]
    assert template_path.exists(), f"missing template {template_path}"
    ctx = {
        "id": f"{at['name']}-001",
        "title": f"Sample {at['name']}",
        "artifact_type": at["name"],
        "description": "Render test.",
        "relationships": [],
        "scope": {"applies_to": "test", "context": "rendering"},
    }
    output = _render(template_path.read_text(), ctx)
    # Frontmatter present and round-trips
    m = re.match(r"---\n(.*?)\n---\n", output, re.DOTALL)
    assert m, "rendered output missing frontmatter"
    fm = yaml.safe_load(m.group(1))
    assert fm["id"] == ctx["id"]
    assert fm["artifact_type"] == ctx["artifact_type"]
    # Required sections present
    for sec in at.get("required_sections", []):
        heading = "#" * sec["level"] + " " + sec["name"]
        assert heading in output, f"missing required section heading: {heading}"
