"""The FR-004 reference mapping: build a record from an authored document.

This is the test oracle, not module code. `quire.validate_document` validates a
*declaration* record and never reaches an artifact-type record
(agent-ix/quire-rs#393), so until an engine-side extractor exists this
implementation is what proves `mappings.yaml`, the emitted schemas, and the
shipped skeletons agree.

Two rules shape the whole file:

* **Markdown is the authority.** Nothing here writes a document. Every file is
  opened read-only, and no function derives Markdown from a record
  (FR-004-CON-3).
* **Every failure in one pass.** A malformed document yields *all* its failures
  and *no* record — never the first failure, and never a partial record a caller
  could mistake for a good one (FR-004 Behavior).
"""

from __future__ import annotations

import dataclasses
import hashlib
import re
from typing import Any

import yaml

DEFAULT_SOURCE_IDENTITY = "ix://local/scope/spec"

_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
_H2 = re.compile(r"^## (.+?)\s*$")
_H3 = re.compile(r"^### (.+?)\s*$")
_FENCE = re.compile(r"^```([A-Za-z0-9_+-]*)\s*$")
_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_TEST_REF = re.compile(r"TC-[0-9]+")
_IMPORTED_TYPE = re.compile(
    r"^([a-z0-9][a-z0-9._-]*/[a-z0-9][a-z0-9._-]*)#([A-Za-z][A-Za-z0-9_-]*)$"
)
_MULTIPLICITY = re.compile(r"^(\d+)(?:\.\.(\d+|\*))?$")
_SYSML_FIELD = re.compile(
    r"^\s*(?:attribute|ref\s+item|item|ref)\s+([A-Za-z_][A-Za-z0-9_]*)\s*:\s*"
    r"([A-Za-z_][A-Za-z0-9_]*)\s*(?:\[([^\]]*)\])?\s*(?:\{(.*)\})?\s*$"
)


class MappingFailure(Exception):
    """Every failure found in one document, reported together."""

    def __init__(self, errors: list["MappingError"]) -> None:
        self.errors = errors
        detail = "\n".join(f"  line {e.line}: [{e.code}] {e.message}" for e in errors)
        super().__init__(f"{len(errors)} mapping failure(s):\n{detail}")

    @property
    def codes(self) -> list[str]:
        return [e.code for e in self.errors]

    @property
    def lines(self) -> list[int]:
        return [e.line for e in self.errors]


@dataclasses.dataclass(frozen=True)
class MappingError:
    line: int
    code: str
    message: str


@dataclasses.dataclass(frozen=True)
class Advisory:
    line: int
    code: str
    message: str


@dataclasses.dataclass(frozen=True)
class Section:
    """A level-2 section: its heading line, its byte-exact body, its span."""

    heading: str
    heading_line: int
    start_line: int
    end_line: int
    text: str
    lines: list[str]


@dataclasses.dataclass
class Record:
    """What the mapping produced: the record, the clause text, the advisories."""

    data: dict[str, Any]
    invariants_text: list[dict[str, Any]]
    advisories: list[Advisory]


# ---------------------------------------------------------------------------
# Document decomposition
# ---------------------------------------------------------------------------


def split_frontmatter(markdown: str) -> tuple[dict[str, Any], int]:
    """Return the parsed frontmatter and the 1-based line the body starts on."""
    match = _FRONTMATTER.match(markdown)
    if not match:
        return {}, 1
    front = yaml.safe_load(match.group(1)) or {}
    body_start = markdown[: match.end()].count("\n") + 1
    return front, body_start


def _fence_mask(lines: list[str]) -> list[bool]:
    """True for every line inside a fenced block, so a `##` in code is not a heading."""
    inside = False
    mask = []
    for line in lines:
        if _FENCE.match(line):
            mask.append(True)
            inside = not inside
            continue
        mask.append(inside)
    return mask


def sections(markdown: str) -> tuple[dict[str, Section], list[MappingError]]:
    """Every level-2 section, keyed by heading. A repeated heading is a failure."""
    lines = markdown.split("\n")
    masked = _fence_mask(lines)
    found: list[tuple[str, int]] = []
    for index, line in enumerate(lines):
        if masked[index]:
            continue
        heading = _H2.match(line)
        if heading:
            found.append((heading.group(1), index + 1))

    errors: list[MappingError] = []
    seen: dict[str, int] = {}
    out: dict[str, Section] = {}
    for position, (heading, heading_line) in enumerate(found):
        if heading in seen:
            errors.append(
                MappingError(
                    heading_line,
                    "duplicated-heading",
                    f"level-2 heading {heading!r} appears again "
                    f"(first at line {seen[heading]})",
                )
            )
            continue
        seen[heading] = heading_line
        end = found[position + 1][1] - 1 if position + 1 < len(found) else len(lines)
        body = lines[heading_line:end]
        while body and not body[0].strip():
            body.pop(0)
            heading_line += 0
        start = heading_line + 1
        # Trim trailing blank lines from the body but keep the span honest.
        text_lines = lines[heading_line:end]
        while text_lines and not text_lines[-1].strip():
            text_lines.pop()
            end -= 1
        while text_lines and not text_lines[0].strip():
            text_lines.pop(0)
            start += 1
        out[heading] = Section(
            heading=heading,
            heading_line=seen[heading],
            start_line=start,
            end_line=max(end, start),
            text="\n".join(text_lines),
            lines=text_lines,
        )
    return out, errors


def _split_row(row: str) -> list[str]:
    """Split a table row on unescaped pipes, dropping the leading/trailing empties."""
    cells: list[str] = []
    current = ""
    escaped = False
    for char in row.strip():
        if escaped:
            current += char
            escaped = False
            continue
        if char == "\\":
            escaped = True
            current += char
            continue
        if char == "|":
            cells.append(current)
            current = ""
            continue
        current += char
    cells.append(current)
    if cells and not cells[0].strip():
        cells.pop(0)
    if cells and not cells[-1].strip():
        cells.pop()
    return [cell.strip() for cell in cells]


def _is_delimiter(row: str) -> bool:
    cells = _split_row(row)
    return bool(cells) and all(re.fullmatch(r":?-{1,}:?", cell) for cell in cells)


def table_rows(section: Section) -> tuple[list[str], list[tuple[int, list[str]]]]:
    """The header cells and the data rows (1-based line, cells) of a section's table."""
    header: list[str] = []
    rows: list[tuple[int, list[str]]] = []
    line_no = section.start_line
    state = "before"
    for line in section.lines:
        stripped = line.strip()
        if state == "before":
            if stripped.startswith("|"):
                header = _split_row(stripped)
                state = "delimiter"
        elif state == "delimiter":
            state = "body" if _is_delimiter(stripped) else "before"
        elif state == "body":
            if not stripped.startswith("|"):
                break
            rows.append((line_no, _split_row(stripped)))
        line_no += 1
    return header, rows


def fenced_blocks(section: Section) -> list[dict[str, Any]]:
    """Every fenced block in a section: language, span, body, and whether it closed."""
    blocks: list[dict[str, Any]] = []
    open_block: dict[str, Any] | None = None
    line_no = section.start_line
    for line in section.lines:
        fence = _FENCE.match(line)
        if fence and open_block is None:
            open_block = {
                "language": fence.group(1),
                "startLine": line_no,
                "body": [],
                "closed": False,
            }
        elif fence and open_block is not None:
            open_block["endLine"] = line_no
            open_block["closed"] = True
            open_block["body"] = "\n".join(open_block["body"])
            blocks.append(open_block)
            open_block = None
        elif open_block is not None:
            open_block["body"].append(line)
        line_no += 1
    if open_block is not None:
        open_block["endLine"] = line_no - 1
        open_block["body"] = "\n".join(open_block["body"])
        blocks.append(open_block)
    return blocks


# ---------------------------------------------------------------------------
# Cell parses
# ---------------------------------------------------------------------------


def parse_verification(cell: str) -> dict[str, Any]:
    """Split `<method> (<annotation>)`, losing no byte of the cell."""
    open_paren = cell.find("(")
    close_paren = cell.rfind(")")
    if open_paren == -1 or close_paren < open_paren:
        return {"method": cell.strip(), "testRefs": []}
    annotation = cell[open_paren + 1 : close_paren]
    return {
        "method": cell[:open_paren].strip(),
        "testRefs": _TEST_REF.findall(annotation),
        "annotation": annotation,
    }


def parse_multiplicity(cell: str) -> dict[str, Any] | None:
    """`1..1`, `0..1`, `1..*`, `3` -> a semantic-core `Multiplicity`."""
    match = _MULTIPLICITY.match(cell.strip())
    if not match:
        return None
    lower = int(match.group(1))
    upper_token = match.group(2)
    if upper_token is None:
        return {"lower": lower, "upper": lower}
    if upper_token == "*":
        return {"lower": lower}
    return {"lower": lower, "upper": int(upper_token)}


def _split_constraints(cell: str) -> list[str]:
    """Split on commas outside a `/…/` pattern, as the engine does."""
    items: list[str] = []
    current = ""
    in_pattern = False
    for index, char in enumerate(cell):
        if in_pattern:
            current += char
            if char == "/":
                rest = cell[index + 1 :]
                head = rest.split(",", 1)[0]
                if "/" not in head:
                    in_pattern = False
            continue
        if char == ",":
            items.append(current.strip())
            current = ""
            continue
        current += char
        if char == "/" and current.lstrip().startswith("pattern"):
            in_pattern = True
    if current.strip():
        items.append(current.strip())
    return [item for item in items if item]


def parse_constraints(
    cell: str, line: int
) -> tuple[list[dict[str, Any]], bool, list[MappingError]]:
    """The closed semantic-core keyword vocabulary. Anything else is a failure."""
    out: list[dict[str, Any]] = []
    identity = False
    errors: list[MappingError] = []
    for item in _split_constraints(cell):
        keyword, _, value = item.partition(":")
        keyword, value = keyword.strip(), value.strip()
        if keyword == "identity" and not value:
            identity = True
        elif keyword in {"nonEmpty", "unique"} and not value:
            out.append({"keyword": keyword})
        elif keyword in {"minLength", "maxLength"} and value.isdigit():
            out.append({"keyword": keyword, "value": int(value)})
        elif keyword in {"min", "max", "exclusiveMin", "exclusiveMax"} and value:
            out.append({"keyword": keyword, "value": _number_or_string(value)})
        elif keyword == "pattern" and value.startswith("/") and value.rfind("/") > 0:
            out.append(
                {
                    "keyword": "pattern",
                    "regex": value[1 : value.rfind("/")],
                    "dialect": "ecma-262",
                }
            )
        elif keyword == "enumValues" and value:
            out.append(
                {
                    "keyword": "enumValues",
                    "values": [_number_or_string(v.strip()) for v in value.split("|")],
                }
            )
        elif keyword == "format" and ":" in item[item.index(":") + 1 :]:
            out.append({"keyword": "format", "name": value})
        else:
            errors.append(
                MappingError(
                    line,
                    "unknown-constraint-keyword",
                    f"constraint {item!r} uses a keyword outside the closed set",
                )
            )
    return out, identity, errors


def _number_or_string(text: str) -> Any:
    try:
        return int(text)
    except ValueError:
        pass
    try:
        value = float(text)
    except ValueError:
        return text
    return value


def parse_imported_type_ref(
    cell: str, line: int, imported_types: dict[str, list[str]], imports: dict[str, str]
) -> tuple[dict[str, str] | None, list[MappingError]]:
    """`<org>/<repo>#<Type>` -> `{module, type}`, checked against both declarations."""
    match = _IMPORTED_TYPE.match(cell.strip())
    if not match:
        return None, [
            MappingError(
                line,
                "imported-type-malformed",
                f"cell {cell!r} is not `<org>/<repo>#<Type>`",
            )
        ]
    module, type_name = match.group(1), match.group(2)
    errors: list[MappingError] = []
    if module not in imports:
        errors.append(
            MappingError(
                line,
                "undeclared-import-module",
                f"module {module!r} (type {type_name!r}) is not named in "
                "manifest semantic.imports",
            )
        )
    elif type_name not in imported_types.get(module, []):
        errors.append(
            MappingError(
                line,
                "undeclared-import-type",
                f"type {type_name!r} is not named in mappings.yaml "
                f"imported_types for module {module!r}",
            )
        )
    if errors:
        return None, errors
    return {"module": module, "type": type_name}, []


# ---------------------------------------------------------------------------
# The mapping itself
# ---------------------------------------------------------------------------

_ENUM_CELL_PROPERTY = {
    "Kind": "kind",
    "Direction": "direction",
    "Access": "access",
    "Surface": "surface",
}


def _column_property(column: str) -> str:
    """`Data Dependencies` column header -> row property name."""
    head, *rest = column.split()
    return head.lower() + "".join(word.capitalize() for word in rest)


def _row_property(column: str, row_model: str) -> str:
    if column == "ID":
        return "id"
    if row_model == "RequirementRef" and column == "Kind":
        return "kind"
    if column == "Source":
        return "source"
    if column == "Verification":
        return "verification"
    return _column_property(column)


class ReferenceMapping:
    """Builds a record for one model, from `mappings.yaml` and the manifest."""

    def __init__(
        self,
        mappings: dict[str, Any],
        manifest: dict[str, Any],
        model_name: str,
    ) -> None:
        self.model_name = model_name
        self.model = mappings["models"][model_name]
        self.properties: dict[str, Any] = self.model["properties"]
        self.imported_types: dict[str, list[str]] = mappings["imported_types"]
        self.imports: dict[str, str] = (manifest.get("semantic") or {}).get(
            "imports"
        ) or {}
        artifact_type = next(
            at
            for at in manifest["artifact_types"]
            if at["name"] == self.model["artifact_type"]
        )
        self.locators: dict[str, Any] = (
            (
                (artifact_type.get("body_extraction") or {}).get("yield_pattern") or {}
            ).get("match")
        ) or {}

    # -- public -------------------------------------------------------------

    def build(
        self,
        markdown: str,
        path: str,
        *,
        source_identity: str | None = None,
    ) -> Record:
        errors: list[MappingError] = []
        advisories: list[Advisory] = []
        front, _ = split_frontmatter(markdown)
        found, section_errors = sections(markdown)
        errors.extend(section_errors)

        record: dict[str, Any] = {}
        invariants_text: list[dict[str, Any]] = []

        for name, entry in self.properties.items():
            kind = entry["kind"]
            if kind == "frontmatter":
                self._fill_frontmatter(record, name, entry, front)
            elif kind == "provenance":
                record["provenance"] = self._provenance(markdown, path, source_identity)
            elif kind == "section":
                self._fill_section(record, name, entry, found, errors)
            elif kind == "typed-table":
                if name == "fields":
                    self._fill_fields(record, entry, found, front, errors)
                else:
                    self._fill_table(record, name, entry, found, front, errors)
            elif kind == "ocl-clause":
                self._fill_clauses(
                    record,
                    entry,
                    found,
                    path,
                    source_identity,
                    invariants_text,
                    errors,
                    advisories,
                )
            else:  # pragma: no cover - the schema admits no other kind
                raise AssertionError(f"unhandled mapping kind {kind!r}")

        if errors:
            raise MappingFailure(sorted(errors, key=lambda e: (e.line, e.code)))
        return Record(
            data=record, invariants_text=invariants_text, advisories=advisories
        )

    # -- per-kind -----------------------------------------------------------

    def _fill_frontmatter(
        self,
        record: dict[str, Any],
        name: str,
        entry: dict[str, Any],
        front: dict[str, Any],
    ) -> None:
        value: Any = front
        for key in entry["path"]:
            if not isinstance(value, dict) or key not in value:
                value = None
                break
            value = value[key]
        if value is None:
            if name == "relationships":
                record[name] = []
            return
        if name == "relationships":
            record[name] = [
                {
                    k: v
                    for k, v in item.items()
                    if k in {"target", "type", "cardinality"}
                }
                for item in value
            ]
            return
        record[name] = value

    def _provenance(
        self, markdown: str, path: str, source_identity: str | None
    ) -> dict[str, Any]:
        digest = hashlib.sha256(markdown.encode("utf-8")).hexdigest()
        provenance: dict[str, Any] = {"path": path, "digest": f"sha256:{digest}"}
        if source_identity is not None:
            provenance["sourceIdentity"] = source_identity
        return provenance

    def _fill_section(
        self,
        record: dict[str, Any],
        name: str,
        entry: dict[str, Any],
        found: dict[str, Section],
        errors: list[MappingError],
    ) -> None:
        section = found.get(entry["heading"])
        if section is None:
            if entry.get("required"):
                errors.append(
                    MappingError(
                        1,
                        "missing-required-section",
                        f"required section '## {entry['heading']}' is absent",
                    )
                )
            return
        record[name] = {
            "text": section.text,
            "startLine": section.start_line,
            "endLine": section.end_line,
        }

    def _fill_fields(
        self,
        record: dict[str, Any],
        entry: dict[str, Any],
        found: dict[str, Section],
        front: dict[str, Any],
        errors: list[MappingError],
    ) -> None:
        section = found.get(entry["heading"])
        if section is None:
            return
        header, rows = table_rows(section)
        blocks = [b for b in fenced_blocks(section) if b["language"] == "sysml"]
        if rows and blocks:
            errors.append(
                MappingError(
                    section.heading_line,
                    "both-property-forms",
                    "'## Properties' carries both a typed table and a `sysml` fence; "
                    "one artifact carries one form",
                )
            )
            return
        if blocks:
            record["fields"] = self._fields_from_fence(blocks[0], errors)
            return
        if not rows:
            return
        if header != entry["columns"]:
            errors.append(
                MappingError(
                    section.start_line,
                    "table-columns-mismatch",
                    f"'## {entry['heading']}' header {header} "
                    f"is not {entry['columns']}",
                )
            )
            return
        fields = []
        for line, cells in rows:
            if len(cells) != len(header):
                errors.append(
                    MappingError(
                        line,
                        "row-cell-count",
                        f"row has {len(cells)} of {len(header)} cells",
                    )
                )
                continue
            name, type_name, multiplicity_cell, constraints_cell = cells
            field: dict[str, Any] = {"name": name, "type": {"target": type_name}}
            multiplicity = parse_multiplicity(multiplicity_cell)
            if multiplicity_cell and multiplicity is None:
                errors.append(
                    MappingError(
                        line,
                        "multiplicity-malformed",
                        f"{multiplicity_cell!r} is not a multiplicity",
                    )
                )
            elif multiplicity is not None:
                field["type"]["multiplicity"] = multiplicity
            constraints, identity, constraint_errors = parse_constraints(
                constraints_cell, line
            )
            errors.extend(constraint_errors)
            if identity:
                field["identity"] = True
            if constraints:
                field["constraints"] = constraints
            fields.append(field)
        if fields:
            record["fields"] = fields

    def _fields_from_fence(
        self, block: dict[str, Any], errors: list[MappingError]
    ) -> list[dict[str, Any]]:
        fields = []
        line = block["startLine"]
        for raw in block["body"].split("\n"):
            line += 1
            if not raw.strip():
                continue
            match = _SYSML_FIELD.match(raw)
            if not match:
                errors.append(
                    MappingError(
                        line,
                        "sysml-declaration-malformed",
                        f"{raw.strip()!r} is not a field declaration",
                    )
                )
                continue
            name, type_name, multiplicity_cell, constraints_cell = match.groups()
            field: dict[str, Any] = {"name": name, "type": {"target": type_name}}
            multiplicity = parse_multiplicity(multiplicity_cell or "")
            if multiplicity is not None:
                field["type"]["multiplicity"] = multiplicity
            constraints, identity, constraint_errors = parse_constraints(
                constraints_cell or "", line
            )
            errors.extend(constraint_errors)
            if identity:
                field["identity"] = True
            if constraints:
                field["constraints"] = constraints
            fields.append(field)
        return fields

    def _fill_table(
        self,
        record: dict[str, Any],
        name: str,
        entry: dict[str, Any],
        found: dict[str, Section],
        front: dict[str, Any],
        errors: list[MappingError],
    ) -> None:
        section = found.get(entry["heading"])
        if section is None:
            return
        header, rows = table_rows(section)
        if not rows:
            # A section present but carrying no table maps to an absent field,
            # never to `[]`: an empty list would claim the author declared none.
            return
        if header != entry["columns"]:
            errors.append(
                MappingError(
                    section.start_line,
                    "table-columns-mismatch",
                    f"'## {entry['heading']}' header {header} "
                    f"is not {entry['columns']}",
                )
            )
            return
        pattern = entry["id_pattern"].replace(
            "{id}", re.escape(str(front.get("id", "")))
        )
        compiled = re.compile(pattern)
        parses = entry["cell_parses"]
        row_model = entry["row_model"]
        out: list[dict[str, Any]] = []
        seen_ids: dict[str, int] = {}
        for line, cells in rows:
            if len(cells) != len(header):
                errors.append(
                    MappingError(
                        line,
                        "row-cell-count",
                        f"row has {len(cells)} of {len(header)} cells",
                    )
                )
                continue
            row: dict[str, Any] = {"line": line}
            for column, cell in zip(header, cells):
                parse = parses[column]
                target = _row_property(column, row_model)
                if parse == "id":
                    if not compiled.fullmatch(cell):
                        errors.append(
                            MappingError(
                                line,
                                "row-id-pattern",
                                f"id cell {cell!r} does not match /{pattern}/",
                            )
                        )
                    elif cell in seen_ids:
                        errors.append(
                            MappingError(
                                line,
                                "row-id-repeated",
                                f"id {cell!r} already used at line "
                                f"{seen_ids[cell]} in this table",
                            )
                        )
                    else:
                        seen_ids[cell] = line
                    row[target] = cell
                elif parse == "verification":
                    row[target] = parse_verification(cell)
                elif parse == "imported-type-ref":
                    value, ref_errors = parse_imported_type_ref(
                        cell, line, self.imported_types, self.imports
                    )
                    errors.extend(ref_errors)
                    if value is not None:
                        row[target] = value
                elif parse == "id-list":
                    row[target] = [
                        item.strip() for item in cell.split(",") if item.strip()
                    ]
                else:
                    row[target] = cell
            if row_model == "RequirementRef" and not str(
                row.get("target", "")
            ).startswith("ix://"):
                errors.append(
                    MappingError(
                        line,
                        "requirement-target-not-identity",
                        f"target {row.get('target')!r} is not an `ix://` identity",
                    )
                )
            out.append(row)
        if out:
            record[name] = out

    def _fill_clauses(
        self,
        record: dict[str, Any],
        entry: dict[str, Any],
        found: dict[str, Section],
        path: str,
        source_identity: str | None,
        invariants_text: list[dict[str, Any]],
        errors: list[MappingError],
        advisories: list[Advisory],
    ) -> None:
        section = found.get(entry["heading"])
        if section is None:
            return
        blocks = fenced_blocks(section)
        if not blocks:
            # A prose `## Invariants` leaves `invariants` absent and does not fail.
            return

        identity = source_identity
        if identity is None:
            identity = DEFAULT_SOURCE_IDENTITY
            advisories.append(
                Advisory(
                    section.heading_line,
                    "semantic.source-identity-defaulted",
                    "no source identity supplied; spans carry "
                    f"{DEFAULT_SOURCE_IDENTITY}",
                )
            )

        headings: list[tuple[str, int]] = []
        line_no = section.start_line
        for raw, inside in zip(section.lines, _fence_mask(section.lines)):
            heading = _H3.match(raw)
            if heading and not inside:
                headings.append((heading.group(1), line_no))
            line_no += 1

        owner_of: dict[int, tuple[str, int]] = {}
        for block in blocks:
            owning = [h for h in headings if h[1] < block["startLine"]]
            if not owning:
                errors.append(
                    MappingError(
                        block["startLine"],
                        "orphan-fence",
                        "fenced block under '## Invariants' is owned by no "
                        "`###` heading",
                    )
                )
                continue
            owner_of[block["startLine"]] = owning[-1]

        by_heading: dict[int, list[dict[str, Any]]] = {}
        for block in blocks:
            owner = owner_of.get(block["startLine"])
            if owner is None:
                continue
            by_heading.setdefault(owner[1], []).append(block)

        clauses: list[dict[str, Any]] = []
        seen: dict[str, int] = {}
        for clause_id, heading_line in headings:
            owned = by_heading.get(heading_line, [])
            if not owned:
                continue
            if len(owned) > 1:
                errors.append(
                    MappingError(
                        owned[1]["startLine"],
                        "clause-owns-two-fences",
                        f"clause {clause_id!r} owns {len(owned)} fences; "
                        "it must own exactly one",
                    )
                )
                continue
            block = owned[0]
            if not _IDENTIFIER.match(clause_id):
                errors.append(
                    MappingError(
                        heading_line,
                        "clause-id-not-identifier",
                        f"clause heading {clause_id!r} is not an Identifier",
                    )
                )
                continue
            if block["language"] != entry["language"]:
                errors.append(
                    MappingError(
                        block["startLine"],
                        "clause-fence-language",
                        f"clause {clause_id!r} owns a `{block['language']}` "
                        f"fence, not `{entry['language']}`",
                    )
                )
                continue
            if not block["closed"]:
                errors.append(
                    MappingError(
                        block["startLine"],
                        "clause-fence-unterminated",
                        f"clause {clause_id!r} owns an unterminated fence",
                    )
                )
                continue
            if clause_id in seen:
                errors.append(
                    MappingError(
                        heading_line,
                        "clause-id-repeated",
                        f"clause id {clause_id!r} already used at "
                        f"line {seen[clause_id]}",
                    )
                )
                continue
            seen[clause_id] = heading_line
            clauses.append(
                {
                    "language": entry["language"],
                    "clauseId": clause_id,
                    "sourceSpan": {
                        "sourceIdentity": identity,
                        "path": path,
                        "startLine": block["startLine"],
                        "startColumn": 1,
                        "endLine": block["endLine"],
                        "endColumn": len("```") + 1,
                    },
                }
            )
            invariants_text.append(
                {
                    "clauseId": clause_id,
                    "startLine": block["startLine"],
                    "endLine": block["endLine"],
                    "text": block["body"],
                }
            )
        if clauses:
            record["invariants"] = clauses
