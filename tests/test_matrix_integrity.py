"""The check `quire coverage` cannot run here, run locally instead.

The `TestMatrix` archetype asserts a `Coverage Status` column; the ecosystem's
`traceability.status.column` is `Status`. They disagree, so the engine skips
status classification and reports it:

    [status-column-matches-nothing] ... Status classification was skipped, so
    complete-but-unbacked rows could not be checked.

That is exactly the check that stops a matrix claiming coverage it does not
have, and it is off for every repository in the ecosystem — the disagreement is
inside one upstream manifest and no module can fix it locally (renaming the
column and adding a fifth both fail the archetype's exact-column assert).
agent-ix/quoin#343 is the fix.

Until it lands, a green matrix here would be an unchecked claim. These tests are
the local substitute: every `✅` row must name test cases that exist, and every
test case must be carried by a marker on a real test function.
"""

from __future__ import annotations

import ast
import re

import pytest

from tests.conftest import REPO_ROOT

MATRIX = REPO_ROOT / "spec" / "tests.md"
TESTS_DIR = REPO_ROOT / "tests"
TC_ID = re.compile(r"\b(TC-[0-9]+)\b")


def _rows(section: str) -> list[list[str]]:
    """The data rows of the table under a level-2 or level-3 heading."""
    lines = MATRIX.read_text().split("\n")
    start = next(
        i
        for i, line in enumerate(lines)
        if re.fullmatch(rf"#{{2,3}} {re.escape(section)}", line)
    )
    rows: list[list[str]] = []
    state = "before"
    for line in lines[start + 1 :]:
        stripped = line.strip()
        if re.match(r"^#{2,3} ", line):
            break
        if state == "before":
            if stripped.startswith("|"):
                state = "delimiter"
        elif state == "delimiter":
            state = "body" if set(stripped) <= set("|-: ") else "before"
        elif state == "body":
            if not stripped.startswith("|"):
                break
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            rows.append(cells)
    return rows


def _marked_test_ids() -> dict[str, set[str]]:
    """`TC-NNN` -> the test functions whose `trace` marker carries it.

    Parsed from the AST rather than grepped, so a marker that a formatter
    wrapped onto its own lines still binds here — and a bare id in a comment or
    docstring does not, which is the trap that mints a trace for a test that
    disclaims one.
    """
    bound: dict[str, set[str]] = {}
    for path in sorted(TESTS_DIR.glob("test_*.py")):
        tree = ast.parse(path.read_text())
        for node in tree.body:
            if not isinstance(node, ast.FunctionDef) or not node.name.startswith(
                "test_"
            ):
                continue
            for decorator in node.decorator_list:
                if not isinstance(decorator, ast.Call):
                    continue
                target = decorator.func
                attribute = ".".join(
                    reversed(
                        [
                            part.attr if isinstance(part, ast.Attribute) else part.id
                            for part in _attribute_chain(target)
                        ]
                    )
                )
                if not attribute.endswith("mark.trace"):
                    continue
                for argument in decorator.args:
                    if isinstance(argument, ast.Constant) and isinstance(
                        argument.value, str
                    ):
                        bound.setdefault(argument.value, set()).add(
                            f"{path.name}::{node.name}"
                        )
    return bound


def _attribute_chain(node: ast.AST) -> list[ast.AST]:
    chain: list[ast.AST] = []
    while isinstance(node, ast.Attribute):
        chain.append(node)
        node = node.value
    if isinstance(node, ast.Name):
        chain.append(node)
    return chain


@pytest.mark.trace("TC-037", "FR-002-CON-1")
def test_every_complete_matrix_row_names_test_cases_that_exist_and_bind():
    summary = {row[0] for row in _rows("Test Case Summary")}
    bound = _marked_test_ids()

    unbacked: list[str] = []
    dangling: list[str] = []
    for section in (
        "Functional Requirement Coverage",
        "Non-Functional Requirement Coverage",
        "Stakeholder and Integration Coverage",
    ):
        for row in _rows(section):
            status = row[-1]
            cases = TC_ID.findall(row[-2])
            if not status.startswith("✅"):
                continue
            if not cases:
                unbacked.append(
                    f"{section}: {row[0]} / {row[1]} is ✅ but names no test case"
                )
                continue
            for case in cases:
                if case not in summary:
                    dangling.append(f"{row[1]}: {case} is in no Test Case Summary row")
                elif case not in bound:
                    unbacked.append(f"{row[1]}: {case} is carried by no trace marker")

    assert not dangling, dangling
    assert not unbacked, unbacked


@pytest.mark.trace("TC-037", "FR-002-CON-1")
def test_every_test_case_summary_row_is_carried_by_a_trace_marker():
    bound = _marked_test_ids()
    missing = [row[0] for row in _rows("Test Case Summary") if row[0] not in bound]
    assert (
        not missing
    ), f"these Test Case Summary rows are carried by no `@pytest.mark.trace`: {missing}"


@pytest.mark.trace("TC-037", "FR-002-CON-1")
def test_no_trace_marker_names_a_test_case_the_matrix_does_not_declare():
    summary = {row[0] for row in _rows("Test Case Summary")}
    phantom = sorted(
        tc for tc in _marked_test_ids() if tc.startswith("TC-") and tc not in summary
    )
    assert (
        not phantom
    ), f"these trace markers name test cases the matrix does not declare: {phantom}"


@pytest.mark.trace("TC-037")
def test_every_test_function_carries_a_trace_marker():
    """A tagged suite with one untagged test is a suite with one invisible test."""
    untagged: list[str] = []
    for path in sorted(TESTS_DIR.glob("test_*.py")):
        tree = ast.parse(path.read_text())
        for node in tree.body:
            if not isinstance(node, ast.FunctionDef) or not node.name.startswith(
                "test_"
            ):
                continue
            has_trace = any(
                isinstance(d, ast.Call)
                and ".".join(
                    reversed(
                        [
                            p.attr if isinstance(p, ast.Attribute) else p.id
                            for p in _attribute_chain(d.func)
                        ]
                    )
                ).endswith("mark.trace")
                for d in node.decorator_list
            )
            if not has_trace:
                untagged.append(f"{path.name}::{node.name}")
    assert not untagged, f"untagged tests: {untagged}"
