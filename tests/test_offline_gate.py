"""The offline, no-network run, recorded as the manual gate it is.

Requirement ids live on the `trace` marker below, not here: a trace id on a
module docstring binds to nothing (quire-rs CR-061).
"""

from __future__ import annotations

import pytest

from tests.conftest import REPO_ROOT

RELEASE_NOTES = REPO_ROOT / "docs" / "offline-gate.md"


@pytest.mark.trace("TC-031", "NFR-001-AC-2")
def test_the_offline_gate_is_recorded_as_a_manual_procedure_with_no_ci_claim():
    """The gate itself is a human run; what is automated is that it stays honest.

    NFR-001-AC-2 asks for `make schemas-check` and `make test` to exit 0 with the
    network namespace disabled. Nothing here can disable a namespace, and a test
    that pretended to would be worse than none — it would report green for a
    check that did not run. So this test asserts the two things that *can* be
    checked automatically: that the procedure is written down where a person can
    follow it, and that no CI workflow claims to run it.
    """
    assert RELEASE_NOTES.is_file(), (
        f"{RELEASE_NOTES.relative_to(REPO_ROOT)} is missing; a manual gate nobody "
        "wrote down is a gate nobody runs"
    )
    text = RELEASE_NOTES.read_text()
    for command in (
        "npm ci",
        "poetry install",
        "make dev-quire",
        "make schemas-check",
        "make test",
    ):
        assert command in text, f"the offline procedure does not name `{command}`"

    workflows = sorted((REPO_ROOT / ".github" / "workflows").glob("*.yml"))
    for workflow in workflows:
        content = workflow.read_text()
        assert "unshare" not in content and "network namespace" not in content, (
            f"{workflow.name} appears to claim the offline gate; NFR-001 claims no "
            "CI job for it, and a job that claimed it would need to be specified first"
        )
