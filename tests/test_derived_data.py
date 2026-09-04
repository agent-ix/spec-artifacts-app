"""The two generators that keep the shipped data files honest, and the payload.

`mappings.yaml` and the legacy-manifest fixture are derived from the manifest so
a column list, a locator name, an id pattern or an artifact-type entry is
written once and cannot drift. That is only true while their `--check` mode
actually fails on drift; an unexercised drift gate is a drift gate that has
never fired.

Requirement ids live on the `trace` markers, not in this docstring.
"""

from __future__ import annotations

import glob
import pathlib
import shutil
import subprocess
import tarfile
import zipfile

import pytest

from tests.conftest import LEGACY_MANIFEST_PATH, MAPPINGS_PATH, REPO_ROOT

#: What `scripts/stage-npm.mjs` copies to the repo root at `prepack`.
STAGED = (
    "manifest.yaml",
    "mappings.yaml",
    "mappings.schema.json",
    "schemas",
    "skeletons",
)

SCRIPTS = {
    "mappings": REPO_ROOT / "scripts" / "build_mappings.py",
    "legacy": REPO_ROOT / "scripts" / "build_legacy_manifest.py",
}
TARGET = {"mappings": MAPPINGS_PATH, "legacy": LEGACY_MANIFEST_PATH}


def _worktree(destination: pathlib.Path) -> pathlib.Path:
    shutil.copytree(
        REPO_ROOT,
        destination,
        ignore=shutil.ignore_patterns(
            ".git",
            ".worktrees",
            "node_modules",
            "__pycache__",
            ".pytest_cache",
            ".ruff_cache",
            "dist",
        ),
    )
    return destination


def _run(
    script: pathlib.Path, *args: str, cwd: pathlib.Path
) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["python", str(cwd / "scripts" / script.name), *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )


@pytest.mark.parametrize("name", sorted(SCRIPTS))
@pytest.mark.trace("TC-043", "FR-004-AC-1", "FR-003-AC-7")
def test_each_derived_file_matches_its_source_and_check_writes_nothing(name):
    result = _run(SCRIPTS[name], "--check", cwd=REPO_ROOT)
    assert result.returncode == 0, result.stderr
    assert "matches the manifest" in result.stdout


@pytest.mark.parametrize("name", sorted(SCRIPTS))
@pytest.mark.trace("TC-043", "FR-004-AC-1", "FR-003-AC-7")
def test_check_fails_on_drift_naming_the_file_and_writes_nothing(name, tmp_path):
    work = _worktree(tmp_path / "repo")
    target = work / TARGET[name].relative_to(REPO_ROOT)
    before = target.read_text()
    assert "spec-artifacts-app" in before
    target.write_text(before.replace("spec-artifacts-app", "spec-artifacts-apq", 1))
    drifted = target.read_text()

    result = _run(SCRIPTS[name], "--check", cwd=work)

    assert result.returncode != 0, "a drifted derived file passed its own gate"
    assert (
        TARGET[name].name in result.stderr
    ), f"the failure does not name the file: {result.stderr}"
    assert target.read_text() == drifted, "`--check` wrote to the file it was checking"


@pytest.mark.parametrize("name", sorted(SCRIPTS))
@pytest.mark.trace("TC-043", "FR-004-AC-1")
def test_regenerating_restores_the_committed_bytes(name, tmp_path):
    work = _worktree(tmp_path / "repo")
    target = work / TARGET[name].relative_to(REPO_ROOT)
    target.write_text("# clobbered\n")

    assert _run(SCRIPTS[name], cwd=work).returncode == 0
    assert (
        target.read_text() == TARGET[name].read_text()
    ), "regenerating did not reproduce the committed bytes"


@pytest.mark.trace("TC-044", "FR-002-AC-12")
def test_the_wheel_the_sdist_and_the_npm_tarball_carry_the_same_payload(tmp_path):
    """One payload, three packages.

    A file in two of them is a file two consumers disagree about.
    """
    work = _worktree(tmp_path / "repo")

    build = subprocess.run(
        ["poetry", "run", "poe", "build"], cwd=str(work), capture_output=True, text=True
    )
    assert build.returncode == 0, build.stderr

    wheel = sorted(glob.glob(str(work / "dist" / "*.whl")))[-1]
    wheel_payload = {
        name[len("spec_artifacts_app/") :]
        for name in zipfile.ZipFile(wheel).namelist()
        if name.startswith("spec_artifacts_app/") and not name.endswith("/")
    } - {"__init__.py"}

    sdist = sorted(glob.glob(str(work / "dist" / "*.tar.gz")))[-1]
    with tarfile.open(sdist) as archive:
        sdist_payload = {
            member.name.split("spec_artifacts_app/", 1)[1]
            for member in archive.getmembers()
            if member.isfile() and "/spec_artifacts_app/" in member.name
        } - {"__init__.py"}

    stage = subprocess.run(
        ["node", "scripts/stage-npm.mjs"], cwd=str(work), capture_output=True, text=True
    )
    assert stage.returncode == 0, stage.stderr
    npm_payload = {
        str(path.relative_to(work))
        for item in (
            "manifest.yaml",
            "mappings.yaml",
            "mappings.schema.json",
            "schemas",
            "skeletons",
        )
        for path in (
            [work / item] if (work / item).is_file() else (work / item).rglob("*")
        )
        if path.is_file()
    }
    clean = subprocess.run(
        ["node", "scripts/stage-npm.mjs", "--clean"],
        cwd=str(work),
        capture_output=True,
        text=True,
    )
    assert clean.returncode == 0, clean.stderr
    for item in (
        "manifest.yaml",
        "mappings.yaml",
        "mappings.schema.json",
        "schemas",
        "skeletons",
    ):
        assert not (work / item).exists(), (
            f"`--clean` left {item} staged at the repo root; the tree now has two "
            "copies of the payload and no statement of which is authoritative"
        )

    assert wheel_payload == sdist_payload, (
        f"wheel-only={sorted(wheel_payload - sdist_payload)}, "
        f"sdist-only={sorted(sdist_payload - wheel_payload)}"
    )
    assert wheel_payload == npm_payload, (
        f"wheel-only={sorted(wheel_payload - npm_payload)}, "
        f"npm-only={sorted(npm_payload - wheel_payload)}"
    )
    assert "manifest.yaml" in wheel_payload and "mappings.yaml" in wheel_payload
    assert any(name.startswith("schemas/") for name in wheel_payload)
    assert any(name.startswith("skeletons/") for name in wheel_payload)

    # The TypeSpec toolchain is a build input and never ships.
    toolchain = {
        name
        for name in wheel_payload | sdist_payload | npm_payload
        if name.startswith(("typespec/", "node_modules/"))
        or name.endswith((".tsp", "tspconfig.yaml"))
    }
    assert not toolchain, f"the payload carries build inputs: {sorted(toolchain)}"
