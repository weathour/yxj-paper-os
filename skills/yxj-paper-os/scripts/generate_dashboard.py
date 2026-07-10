#!/usr/bin/env python3
"""Generate a static yxj-paper-os structural/template-analysis dashboard."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Avoid creating local __pycache__ when importing helper constants.
sys.dont_write_bytecode = True

# Keep bytecode disabled before importing the colocated validator helpers.
from verify_design_pack import (  # noqa: E402
    DIMENSION_COLUMNS,
    DIMENSION_INDEX,
    FINAL_PACK,
    REQUIRED_DIMENSION_IDS,
    REQUIRED_FILES,
    REQUIRED_HEADINGS,
    VALID_BLOCKS_VALUES,
    VALID_DIMENSION_STATUSES,
    first_present,
    has_placeholder,
    level_two_heading_slugs,
    parse_anchor,
    section_content,
    slugify,
    validate_workspace,
)


CACHE_DIR = ".yxj-paper-os"
OUTPUT_NAME = "dashboard.html"
MAX_FRAGMENT_CHARS = 6000
TEMPLATE_ANALYSIS_DIR = "template-analysis"
TEMPLATE_ANALYSIS_FILES = {
    "summary": "corpus-summary.json",
    "profile": "design-profile.json",
}
TEMPLATE_ANALYSIS_SCHEMAS = {
    "summary": "template-corpus-summary/1.0",
    "profile": "template-design-profile/1.0",
}
TEMPLATE_ANALYSIS_REQUIRED_KEYS = {
    "template-corpus-summary/1.0": {
        "analysis_id",
        "corpus_id",
        "analyzer_version",
        "groups",
        "sequences",
        "transitions",
        "lead_lag",
    },
    "template-design-profile/1.0": {
        "analysis_id",
        "corpus_id",
        "analyzer_version",
        "entries",
    },
}
TEMPLATE_ANALYSIS_IDENTITY_KEYS = (
    "analysis_id",
    "corpus_id",
    "analyzer_version",
)
MAX_ANALYSIS_BYTES = 8_000_000
MAX_ANALYSIS_PREVIEW_CHARS = 24_000
MAX_ANALYSIS_LIST_ITEMS = 80
MAX_ANALYSIS_DICT_ITEMS = 120
MAX_ANALYSIS_DEPTH = 7
MAX_ANALYSIS_METRICS_PER_GROUP = 10
ANALYSIS_PRIORITY_METRICS = (
    "text.body_words",
    "structure.section_count",
    "structure.paragraph_count",
    "object.figure_count",
    "object.table_count",
    "object.equation_count",
    "object.algorithm_count",
    "caption.missing_count",
    "callout.orphan_object_count",
    "citation.explicit_rate_per_kword",
)

STATUS_LABELS = {
    "filled": "已填写",
    "not_applicable": "不适用",
    "absent": "缺失",
    "deferred": "延后",
    "rejected": "拒绝",
}


@dataclass
class TableParseResult:
    header: list[str]
    rows: list[dict[str, Any]]
    warnings: list[str]


def warning(
    scope: str, message: str, dimension_id: str | None = None
) -> dict[str, str]:
    item = {"scope": scope, "message": message}
    if dimension_id:
        item["dimension_id"] = dimension_id
    return item


def truncate_fragment(text: str, warnings: list[dict[str, str]], scope: str) -> str:
    if len(text) <= MAX_FRAGMENT_CHARS:
        return text
    warnings.append(
        warning(scope, f"source fragment truncated at {MAX_FRAGMENT_CHARS} characters")
    )
    return text[:MAX_FRAGMENT_CHARS] + "\n\n[... truncated by dashboard generator ...]"


def load_workspace(workspace: Path) -> tuple[dict[str, str], list[dict[str, str]]]:
    warnings: list[dict[str, str]] = []
    if not workspace.exists():
        raise SystemExit(f"workspace does not exist: {workspace}")
    if not workspace.is_dir():
        raise SystemExit(f"workspace is not a directory: {workspace}")

    contents: dict[str, str] = {}
    for file_name in REQUIRED_FILES:
        path = workspace / file_name
        if not path.is_file():
            warnings.append(
                warning(file_name, f"missing required workspace file: {file_name}")
            )
            continue
        try:
            contents[file_name] = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            warnings.append(warning(file_name, f"cannot read as utf-8: {exc}"))
        except OSError as exc:
            warnings.append(warning(file_name, f"cannot read file: {exc}"))
    return contents, warnings


def bounded_json_value(value: Any, *, depth: int = 0) -> Any:
    """Return a JSON-safe bounded copy for embedding in the static dashboard."""
    if depth >= MAX_ANALYSIS_DEPTH:
        return "[depth truncated]"
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        if len(value) <= MAX_FRAGMENT_CHARS:
            return value
        return value[:MAX_FRAGMENT_CHARS] + " [... truncated ...]"
    if isinstance(value, list):
        items = [
            bounded_json_value(item, depth=depth + 1)
            for item in value[:MAX_ANALYSIS_LIST_ITEMS]
        ]
        if len(value) > MAX_ANALYSIS_LIST_ITEMS:
            items.append(f"[{len(value) - MAX_ANALYSIS_LIST_ITEMS} items truncated]")
        return items
    if isinstance(value, dict):
        bounded: dict[str, Any] = {}
        pairs = list(value.items())
        for key, item in pairs[:MAX_ANALYSIS_DICT_ITEMS]:
            bounded[str(key)[:256]] = bounded_json_value(item, depth=depth + 1)
        if len(pairs) > MAX_ANALYSIS_DICT_ITEMS:
            bounded["__truncated__"] = (
                f"{len(pairs) - MAX_ANALYSIS_DICT_ITEMS} keys truncated"
            )
        return bounded
    return str(value)[:MAX_FRAGMENT_CHARS]


def json_preview(value: Any) -> str:
    preview = json.dumps(
        bounded_json_value(value),
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
    )
    if len(preview) <= MAX_ANALYSIS_PREVIEW_CHARS:
        return preview
    return preview[:MAX_ANALYSIS_PREVIEW_CHARS] + "\n[preview truncated]"


def unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def reject_nonfinite_json(token: str) -> Any:
    raise ValueError(f"non-finite JSON token {token}")


def load_analysis_json(
    path: Path,
    *,
    analysis_dir: Path,
    label: str,
    expected_schema: str,
    warnings: list[dict[str, str]],
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "label": label,
        "path": str(path),
        "state": "absent",
        "schema": "unknown",
        "identity": {},
        "data": {},
        "preview": "",
    }
    if not path.exists():
        return result
    if path.is_symlink():
        message = f"refusing to read symlinked template-analysis artifact: {path.name}"
        warnings.append(warning("template-analysis", message))
        result.update(state="unsafe", preview=message)
        return result
    try:
        resolved = path.resolve(strict=True)
        resolved.relative_to(analysis_dir)
    except (OSError, ValueError) as exc:
        message = (
            f"template-analysis artifact escapes its directory: {path.name}: {exc}"
        )
        warnings.append(warning("template-analysis", message))
        result.update(state="unsafe", preview=message)
        return result
    if not resolved.is_file():
        message = f"template-analysis artifact is not a regular file: {path.name}"
        warnings.append(warning("template-analysis", message))
        result.update(state="malformed", preview=message)
        return result
    try:
        size = resolved.stat().st_size
    except OSError as exc:
        message = f"cannot stat template-analysis artifact {path.name}: {exc}"
        warnings.append(warning("template-analysis", message))
        result.update(state="malformed", preview=message)
        return result
    if size > MAX_ANALYSIS_BYTES:
        message = (
            f"template-analysis artifact {path.name} exceeds "
            f"{MAX_ANALYSIS_BYTES} bytes; not embedded"
        )
        warnings.append(warning("template-analysis", message))
        result.update(state="oversize", preview=message)
        return result
    try:
        raw = resolved.read_text(encoding="utf-8")
        parsed = json.loads(
            raw,
            object_pairs_hook=unique_json_object,
            parse_constant=reject_nonfinite_json,
        )
    except (
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
        ValueError,
        RecursionError,
    ) as exc:
        message = f"cannot read template-analysis artifact {path.name}: {exc}"
        warnings.append(warning("template-analysis", message))
        result.update(state="malformed", preview=message)
        return result
    if not isinstance(parsed, dict):
        message = f"template-analysis artifact {path.name} must be a JSON object"
        warnings.append(warning("template-analysis", message))
        result.update(state="malformed", preview=message)
        return result
    bounded = bounded_json_value(parsed)
    assert isinstance(bounded, dict)
    schema = parsed.get("schema", parsed.get("schema_id", "unknown"))
    if schema != expected_schema:
        message = (
            f"template-analysis artifact {path.name} has unsupported schema "
            f"{schema!r}; expected {expected_schema!r}"
        )
        warnings.append(warning("template-analysis", message))
        result.update(
            state="malformed",
            schema=str(schema)[:256],
            data=bounded,
            preview=json_preview(parsed),
        )
        return result
    missing_keys = sorted(
        TEMPLATE_ANALYSIS_REQUIRED_KEYS[expected_schema] - set(parsed)
    )
    invalid_identity_keys = [
        key
        for key in TEMPLATE_ANALYSIS_IDENTITY_KEYS
        if key in parsed
        and (not isinstance(parsed[key], str) or not parsed[key].strip())
    ]
    entries_invalid = expected_schema == TEMPLATE_ANALYSIS_SCHEMAS[
        "profile"
    ] and not isinstance(parsed.get("entries"), list)
    if missing_keys or invalid_identity_keys or entries_invalid:
        detail = (
            "missing keys " + ", ".join(missing_keys)
            if missing_keys
            else "invalid identity keys " + ", ".join(invalid_identity_keys)
            if invalid_identity_keys
            else "entries must be a list"
        )
        message = f"template-analysis artifact {path.name} is malformed: {detail}"
        warnings.append(warning("template-analysis", message))
        result.update(
            state="malformed",
            schema=str(schema)[:256],
            data=bounded,
            preview=json_preview(parsed),
        )
        return result
    result.update(
        state="available",
        schema=str(schema)[:256],
        identity={key: parsed[key] for key in TEMPLATE_ANALYSIS_IDENTITY_KEYS},
        data=bounded,
        preview=json_preview(parsed),
    )
    return result


def build_template_analysis(
    workspace: Path, warnings: list[dict[str, str]]
) -> dict[str, Any]:
    """Read optional analyzer outputs without modifying or trusting them semantically."""
    root = workspace / CACHE_DIR / TEMPLATE_ANALYSIS_DIR
    model: dict[str, Any] = {
        "state": "absent",
        "directory": str(root),
        "summary": {
            "label": "corpus summary",
            "path": str(root / TEMPLATE_ANALYSIS_FILES["summary"]),
            "state": "absent",
            "schema": "unknown",
            "identity": {},
            "data": {},
            "preview": "",
        },
        "profile": {
            "label": "design profile",
            "path": str(root / TEMPLATE_ANALYSIS_FILES["profile"]),
            "state": "absent",
            "schema": "unknown",
            "identity": {},
            "data": {},
            "preview": "",
        },
        "note": (
            "Optional hidden statistics guide writing design only; they are not D06/D11 "
            "scientific evidence, venue-fit scoring, or acceptance prediction."
        ),
    }
    if not root.exists():
        return model
    if root.is_symlink():
        message = "refusing to read symlinked .yxj-paper-os/template-analysis directory"
        warnings.append(warning("template-analysis", message))
        model.update(state="unsafe", note=message)
        return model
    try:
        resolved_workspace = workspace.resolve(strict=True)
        resolved_root = root.resolve(strict=True)
        resolved_root.relative_to(resolved_workspace)
    except (OSError, ValueError) as exc:
        message = f"template-analysis directory escapes workspace: {exc}"
        warnings.append(warning("template-analysis", message))
        model.update(state="unsafe", note=message)
        return model
    if not resolved_root.is_dir():
        message = "template-analysis path is not a directory"
        warnings.append(warning("template-analysis", message))
        model.update(state="malformed", note=message)
        return model

    model["summary"] = load_analysis_json(
        resolved_root / TEMPLATE_ANALYSIS_FILES["summary"],
        analysis_dir=resolved_root,
        label="corpus summary",
        expected_schema=TEMPLATE_ANALYSIS_SCHEMAS["summary"],
        warnings=warnings,
    )
    model["profile"] = load_analysis_json(
        resolved_root / TEMPLATE_ANALYSIS_FILES["profile"],
        analysis_dir=resolved_root,
        label="design profile",
        expected_schema=TEMPLATE_ANALYSIS_SCHEMAS["profile"],
        warnings=warnings,
    )
    if all(model[name]["state"] == "available" for name in ("summary", "profile")):
        summary_data = model["summary"].get("identity", {})
        profile_data = model["profile"].get("identity", {})
        summary_identity = tuple(
            summary_data.get(key) for key in TEMPLATE_ANALYSIS_IDENTITY_KEYS
        )
        profile_identity = tuple(
            profile_data.get(key) for key in TEMPLATE_ANALYSIS_IDENTITY_KEYS
        )
        if summary_identity != profile_identity:
            labels = ", ".join(TEMPLATE_ANALYSIS_IDENTITY_KEYS)
            message = (
                "template-analysis summary/profile identity mismatch for "
                f"{labels}; neither artifact was trusted"
            )
            warnings.append(warning("template-analysis", message))
            for name in ("summary", "profile"):
                model[name].update(
                    state="inconsistent",
                    data={},
                    preview=message,
                )
            model.update(state="degraded", note=message)
            return model
    states = {model["summary"]["state"], model["profile"]["state"]}
    if states == {"available"}:
        model["state"] = "available"
    elif states <= {"available", "absent"} and "available" in states:
        model["state"] = "partial"
    elif states == {"absent"}:
        model["state"] = "absent"
    else:
        model["state"] = "degraded"
    return model


def split_table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_separator_row(cells: list[str]) -> bool:
    if not cells:
        return False
    return all(
        bool(re.fullmatch(r":?-{3,}:?", cell.replace(" ", ""))) for cell in cells
    )


def table_blocks(section: str) -> list[list[str]]:
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in section.splitlines():
        stripped = line.strip()
        if stripped.startswith("|"):
            current.append(stripped)
            continue
        if current:
            blocks.append(current)
            current = []
    if current:
        blocks.append(current)
    return blocks


def parse_dashboard_table_lines(table_lines: list[str], scope: str) -> TableParseResult:
    warnings: list[str] = []
    if not table_lines:
        return TableParseResult([], [], warnings)
    if len(table_lines) == 1:
        return TableParseResult(
            split_table_cells(table_lines[0]),
            [],
            [f"{scope}: table header has no separator row"],
        )

    header = split_table_cells(table_lines[0])
    separator = split_table_cells(table_lines[1])
    if not is_separator_row(separator):
        warnings.append(f"{scope}: table separator row is malformed")
    if len(separator) != len(header):
        warnings.append(
            f"{scope}: table separator has {len(separator)} cells, expected {len(header)}"
        )

    rows: list[dict[str, Any]] = []
    for row_number, line in enumerate(table_lines[2:], start=1):
        cells = split_table_cells(line)
        row_warnings: list[str] = []
        if len(cells) != len(header):
            row_warnings.append(
                f"{scope}: row {row_number} has {len(cells)} cells, expected {len(header)}"
            )
            warnings.extend(row_warnings)
            if len(cells) < len(header):
                cells = cells + [""] * (len(header) - len(cells))
            else:
                cells = cells[: len(header) - 1] + [
                    " | ".join(cells[len(header) - 1 :])
                ]
        values = dict(zip(header, cells))
        rows.append({"values": values, "raw": line, "warnings": row_warnings})
    return TableParseResult(header, rows, warnings)


def parse_dashboard_table(section: str, scope: str) -> TableParseResult:
    blocks = table_blocks(section)
    if not blocks:
        return TableParseResult([], [], [])
    return parse_dashboard_table_lines(blocks[0], scope)


def parse_dashboard_tables(
    section: str, scope: str
) -> tuple[list[dict[str, Any]], list[str]]:
    blocks = table_blocks(section)
    tables: list[dict[str, Any]] = []
    warnings: list[str] = []
    for index, block in enumerate(blocks, start=1):
        table_scope = f"{scope} table {index}" if len(blocks) > 1 else scope
        table = parse_dashboard_table_lines(block, table_scope)
        warnings.extend(table.warnings)
        if table.header:
            tables.append(
                {
                    "title": f"表格 {index}",
                    "header": table.header,
                    "rows": table.rows,
                    "warnings": table.warnings,
                }
            )
    return tables, warnings


def parse_sections(contents: dict[str, str]) -> dict[str, list[dict[str, Any]]]:
    parsed: dict[str, list[dict[str, Any]]] = {}
    for file_name, text in contents.items():
        matches = list(re.finditer(r"^##\s+(.+?)\s*$", text, re.MULTILINE))
        sections: list[dict[str, Any]] = []
        for index, match in enumerate(matches):
            heading = match.group(1).strip()
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            body = text[start:end].strip()
            tables, table_warnings = parse_dashboard_tables(
                body, f"{file_name}#{heading}"
            )
            sections.append(
                {
                    "heading": heading,
                    "slug": slugify(heading),
                    "content": body,
                    "tables": tables,
                    "warnings": table_warnings,
                }
            )
        parsed[file_name] = sections
    return parsed


def resolve_pointer(
    pointer: str, contents: dict[str, str]
) -> tuple[dict[str, Any], list[str]]:
    file_name, anchor_slug, parse_error = parse_anchor(pointer, contents)
    if parse_error:
        return {
            "file": file_name,
            "section": None,
            "slug": anchor_slug,
            "fragment": None,
        }, [parse_error]
    if not file_name or file_name not in contents:
        return {
            "file": file_name,
            "section": None,
            "slug": anchor_slug,
            "fragment": None,
        }, ["referenced workspace file is missing"]
    if not anchor_slug:
        return {
            "file": file_name,
            "section": None,
            "slug": anchor_slug,
            "fragment": None,
        }, ["section anchor is missing"]
    slugs = level_two_heading_slugs(contents[file_name])
    heading = slugs.get(anchor_slug)
    if not heading:
        return {
            "file": file_name,
            "section": None,
            "slug": anchor_slug,
            "fragment": None,
        }, [f"section anchor not found in {file_name}: #{anchor_slug}"]
    return {
        "file": file_name,
        "section": heading,
        "slug": anchor_slug,
        "fragment": section_content(contents[file_name], heading) or "",
        "tables": [],
    }, []


def dimension_placeholder(dim_id: str, message: str) -> dict[str, Any]:
    return {
        "id": dim_id,
        "dimension": "缺失占位",
        "current_home": "",
        "status": "absent",
        "status_label": STATUS_LABELS["absent"],
        "reason": message,
        "pointer": "",
        "blocks": "yes",
        "raw": "",
        "source": None,
        "warnings": [message],
        "is_placeholder": True,
    }


def build_dimensions(
    contents: dict[str, str],
    warnings: list[dict[str, str]],
) -> list[dict[str, Any]]:
    rows_by_id: dict[str, dict[str, Any]] = {}
    index_text = contents.get(DIMENSION_INDEX, "")
    index_section = (
        section_content(index_text, "Dimension Status Index") if index_text else None
    )
    if index_section is None:
        warnings.append(warning(DIMENSION_INDEX, "missing ## Dimension Status Index"))
    else:
        table = parse_dashboard_table(
            index_section, f"{DIMENSION_INDEX}#Dimension Status Index"
        )
        for item in table.warnings:
            warnings.append(warning(DIMENSION_INDEX, item))
        if table.header != DIMENSION_COLUMNS:
            warnings.append(
                warning(
                    DIMENSION_INDEX,
                    "Dimension Status Index columns differ from required dashboard contract",
                )
            )
        seen: set[str] = set()
        for row_number, row_item in enumerate(table.rows, start=1):
            row = row_item["values"]
            dim_id = first_present(row, ["ID"])
            row_warnings = list(row_item["warnings"])
            if not dim_id:
                dim_id = f"ROW{row_number:02d}"
                row_warnings.append("dimension ID is missing")
            if dim_id in seen:
                row_warnings.append(f"duplicate dimension ID: {dim_id}")
            seen.add(dim_id)
            if dim_id not in REQUIRED_DIMENSION_IDS:
                row_warnings.append(f"unexpected dimension ID: {dim_id}")

            status = first_present(row, ["Status"]).lower()
            if status not in VALID_DIMENSION_STATUSES:
                row_warnings.append(f"invalid or missing status: {status or '(empty)'}")
            blocks = first_present(row, ["Blocks design pack?"]).lower()
            if blocks not in VALID_BLOCKS_VALUES:
                row_warnings.append("Blocks design pack? must be yes or no")

            for label, names in [
                ("Dimension", ["Dimension"]),
                ("Current home", ["Current home"]),
                ("Reason / owner note", ["Reason / owner note"]),
                ("Pointer or handoff", ["Pointer or handoff"]),
            ]:
                value = first_present(row, names)
                if not value or has_placeholder(value):
                    row_warnings.append(f"{label} is missing or placeholder")

            pointer = first_present(row, ["Pointer or handoff"])
            source: dict[str, Any] | None = None
            if pointer and not has_placeholder(pointer):
                source, pointer_warnings = resolve_pointer(pointer, contents)
                row_warnings.extend([f"pointer: {item}" for item in pointer_warnings])

            for item in row_warnings:
                warnings.append(
                    warning(
                        DIMENSION_INDEX,
                        item,
                        dim_id if dim_id.startswith("D") else None,
                    )
                )

            rows_by_id[dim_id] = {
                "id": dim_id,
                "dimension": first_present(row, ["Dimension"]),
                "current_home": first_present(row, ["Current home"]),
                "status": status or "absent",
                "status_label": STATUS_LABELS.get(status, status or "未知"),
                "reason": first_present(row, ["Reason / owner note"]),
                "pointer": pointer,
                "blocks": blocks,
                "raw": row_item["raw"],
                "source": source,
                "warnings": row_warnings,
                "is_placeholder": False,
            }

    dimensions: list[dict[str, Any]] = []
    for number in range(20):
        dim_id = f"D{number:02d}"
        if dim_id in rows_by_id:
            dimensions.append(rows_by_id[dim_id])
        else:
            message = f"{dim_id} missing from Dimension Status Index; warning placeholder inserted"
            warnings.append(warning(DIMENSION_INDEX, message, dim_id))
            dimensions.append(dimension_placeholder(dim_id, message))
    return dimensions


def collect_external_handoffs(
    contents: dict[str, str], warnings: list[dict[str, str]]
) -> list[dict[str, str]]:
    handoffs: list[dict[str, str]] = []
    targets = [
        (FINAL_PACK, "External Skill Handoff"),
        (FINAL_PACK, "Submission Blueprint"),
        (FINAL_PACK, "Semantic-Risk and Unresolved-Risk Notes"),
        (DIMENSION_INDEX, "Readiness Gate"),
        (DIMENSION_INDEX, "Owner Notes"),
    ]
    for file_name, heading in targets:
        text = contents.get(file_name)
        if not text:
            continue
        fragment = section_content(text, heading)
        if fragment is None:
            continue
        handoffs.append(
            {
                "file": file_name,
                "section": heading,
                "fragment": truncate_fragment(
                    fragment, warnings, f"{file_name}#{heading}"
                ),
            }
        )
    return handoffs


def attach_source_tables(
    dimensions: list[dict[str, Any]],
    sections: dict[str, list[dict[str, Any]]],
) -> None:
    sections_by_file_and_heading = {
        (file_name, parsed_section["heading"]): parsed_section
        for file_name, parsed_sections in sections.items()
        for parsed_section in parsed_sections
    }
    for item in dimensions:
        source = item.get("source")
        if not source:
            continue
        parsed_section = sections_by_file_and_heading.get(
            (source.get("file"), source.get("section"))
        )
        source["tables"] = (
            list(parsed_section.get("tables", [])) if parsed_section else []
        )
        source["section_warnings"] = (
            list(parsed_section.get("warnings", [])) if parsed_section else []
        )


def add_validator_warnings(workspace: Path, warnings: list[dict[str, str]]) -> None:
    try:
        validator_errors = validate_workspace(workspace)
    except Exception as exc:  # pragma: no cover - defensive non-blocking integration.
        warnings.append(warning("validator", f"validator could not complete: {exc}"))
        return
    for error in validator_errors:
        warnings.append(warning("validator", f"validator: {error}"))


def design_readiness(
    contents: dict[str, str],
    dimensions: list[dict[str, Any]],
    warnings: list[dict[str, str]],
) -> dict[str, Any]:
    blocking = [
        item["id"]
        for item in dimensions
        if item.get("blocks") == "yes"
        and item.get("status") not in {"filled", "not_applicable"}
    ]
    final_text = contents.get(FINAL_PACK, "")
    final_sections = (
        set(level_two_heading_slugs(final_text).values()) if final_text else set()
    )
    required_final = set(REQUIRED_HEADINGS.get(FINAL_PACK, []))
    missing_final = sorted(required_final - final_sections)
    if missing_final:
        warnings.append(
            warning(
                FINAL_PACK,
                "final design-pack missing structural sections: "
                + ", ".join(missing_final),
            )
        )
    has_structural_warnings = bool(warnings)
    if blocking or missing_final:
        label = "结构待处理"
    elif has_structural_warnings:
        label = "结构有警告"
    else:
        label = "结构就绪"
    return {
        "label": label,
        "blocking_dimensions": blocking,
        "missing_final_sections": missing_final,
        "note": "仅表示六文件结构和指针状态；不表示语义充分、论文质量或投稿就绪。",
    }


def build_file_inventory(
    contents: dict[str, str],
    sections: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = []
    for file_name in REQUIRED_FILES:
        file_sections = sections.get(file_name, [])
        missing_headings = []
        section_names = {item["heading"] for item in file_sections}
        for heading in REQUIRED_HEADINGS.get(file_name, []):
            if heading not in section_names:
                missing_headings.append(heading)
        inventory.append(
            {
                "file": file_name,
                "present": file_name in contents,
                "section_count": len(file_sections),
                "missing_headings": missing_headings,
            }
        )
    return inventory


def build_model(workspace: Path) -> dict[str, Any]:
    contents, global_warnings = load_workspace(workspace)
    add_validator_warnings(workspace, global_warnings)
    sections = parse_sections(contents)
    for file_name, parsed_sections in sections.items():
        for parsed_section in parsed_sections:
            for item in parsed_section["warnings"]:
                global_warnings.append(warning(file_name, item))
    dimensions = build_dimensions(contents, global_warnings)
    attach_source_tables(dimensions, sections)
    handoffs = collect_external_handoffs(contents, global_warnings)
    files = build_file_inventory(contents, sections)
    template_analysis = build_template_analysis(workspace, global_warnings)

    source_sections: dict[str, list[dict[str, Any]]] = {}
    for file_name, parsed_sections in sections.items():
        source_sections[file_name] = []
        for parsed_section in parsed_sections:
            source_sections[file_name].append(
                {
                    "heading": parsed_section["heading"],
                    "slug": parsed_section["slug"],
                    "content": truncate_fragment(
                        parsed_section["content"],
                        global_warnings,
                        f"{file_name}#{parsed_section['heading']}",
                    ),
                    "tables": parsed_section["tables"],
                    "warnings": parsed_section["warnings"],
                }
            )

    readiness = design_readiness(contents, dimensions, global_warnings)

    status_counts: dict[str, int] = {}
    for item in dimensions:
        status_counts[item["status"]] = status_counts.get(item["status"], 0) + 1

    return {
        "workspace": str(workspace),
        "artifact": str(workspace / CACHE_DIR / OUTPUT_NAME),
        "files": files,
        "dimensions": dimensions,
        "warnings": global_warnings,
        "warning_count": len(global_warnings),
        "readiness": readiness,
        "handoffs": handoffs,
        "source_sections": source_sections,
        "status_counts": status_counts,
        "template_analysis": template_analysis,
    }


def safe_json(data: Any) -> str:
    text = json.dumps(data, ensure_ascii=False, sort_keys=True)
    return (
        text.replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def compact_json_text(value: Any, limit: int = 1800) -> str:
    text = json.dumps(
        bounded_json_value(value), ensure_ascii=False, sort_keys=True, indent=2
    )
    if len(text) <= limit:
        return text
    return text[:limit] + "\n[section truncated]"


def iter_analysis_groups(group_data: Any) -> list[tuple[str, dict[str, Any]]]:
    if not isinstance(group_data, dict):
        return []
    groups: list[tuple[str, dict[str, Any]]] = []
    overall = group_data.get("overall")
    if isinstance(overall, dict):
        groups.append((str(overall.get("group_id", "overall")), overall))
    for family in (
        "by_partition",
        "by_article_type",
        "by_partition_article_type",
    ):
        collection = group_data.get(family, [])
        if isinstance(collection, dict):
            candidates = list(collection.values())
        elif isinstance(collection, (list, tuple)):
            candidates = collection
        else:
            continue
        for group in candidates:
            if isinstance(group, dict):
                groups.append((str(group.get("group_id", f"{family}:unknown")), group))
    return groups


def priority_group_metrics(metrics: Any) -> tuple[list[tuple[str, Any]], int]:
    if not isinstance(metrics, dict):
        return [], 0
    selected_ids = [
        metric_id for metric_id in ANALYSIS_PRIORITY_METRICS if metric_id in metrics
    ]
    if len(selected_ids) < MAX_ANALYSIS_METRICS_PER_GROUP:
        selected_set = set(selected_ids)
        selected_ids.extend(
            metric_id for metric_id in sorted(metrics) if metric_id not in selected_set
        )
    selected_ids = selected_ids[:MAX_ANALYSIS_METRICS_PER_GROUP]
    return [(metric_id, metrics[metric_id]) for metric_id in selected_ids], max(
        0, len(metrics) - len(selected_ids)
    )


def render_analysis_artifact(artifact: dict[str, Any], *, kind: str) -> str:
    state = str(artifact.get("state", "absent"))
    label = str(artifact.get("label", kind))
    path = str(artifact.get("path", ""))
    schema = str(artifact.get("schema", "unknown"))
    if state != "available":
        message = artifact.get("preview") or (
            "No generated artifact is present; template analysis remains optional."
            if state == "absent"
            else "Artifact is unavailable and was not trusted."
        )
        return (
            '<article class="analysis-artifact">'
            f"<h3>{html.escape(label)}</h3>"
            f'<p><span class="pill">{html.escape(state)}</span></p>'
            f'<p class="small">{html.escape(path)}</p>'
            f"<p>{html.escape(str(message))}</p>"
            "</article>"
        )

    data = artifact.get("data", {})
    if not isinstance(data, dict):
        data = {}
    blocks: list[str] = []
    if kind == "summary":
        group_data = data.get("groups", {})
        for group_name, group in iter_analysis_groups(group_data):
            document_count = group.get("document_count", "unknown")
            parsed_count = group.get("parsed_document_count", "unknown")
            failed_count = (
                document_count - parsed_count
                if isinstance(document_count, int) and isinstance(parsed_count, int)
                else "unknown"
            )
            selected_metrics, omitted_count = priority_group_metrics(
                group.get("metrics", {})
            )
            metric_rows: list[str] = []
            for metric_id, metric in selected_metrics:
                metric_record = (
                    metric if isinstance(metric, dict) else {"value": metric}
                )
                metric_rows.append(
                    "<tr>"
                    f"<td>{html.escape(str(metric_id))}</td>"
                    f"<td>{html.escape(str(metric_record.get('valid_n', 'unknown')))}</td>"
                    f"<td>{html.escape(compact_json_text(metric_record.get('missingness', 'unknown'), 300))}</td>"
                    f"<td>{html.escape(str(metric_record.get('median', metric_record.get('value', 'not summarized'))))}</td>"
                    f"<td>{html.escape(str(metric_record.get('p25', 'unknown')))}</td>"
                    f"<td>{html.escape(str(metric_record.get('p75', 'unknown')))}</td>"
                    "</tr>"
                )
            blocks.append(
                '<section class="analysis-group" '
                f'data-analysis-group="{html.escape(group_name)}">'
                f"<h4>{html.escape(group_name)}</h4>"
                '<p class="small">'
                f"Documents: {html.escape(str(document_count))}; "
                f"parsed: {html.escape(str(parsed_count))}; "
                f"failed: {html.escape(str(failed_count))}. "
                f"Priority metrics shown: {len(selected_metrics)}; "
                f"additional metrics omitted: {omitted_count}."
                "</p>"
                + (
                    '<div class="analysis-table-wrap"><table>'
                    "<thead><tr><th>Metric</th><th>valid_n</th><th>Missingness</th>"
                    "<th>Median/value</th><th>p25</th><th>p75</th></tr></thead>"
                    f"<tbody>{''.join(metric_rows)}</tbody></table></div>"
                    if metric_rows
                    else '<p class="small">No metrics available for this group.</p>'
                )
                + "</section>"
            )
        preferred = [
            "registry_version",
            "corpus",
            "analysis_mode",
            "mode",
            "groups",
            "overall",
            "by_partition",
            "by_article_type",
            "by_partition_article_type",
            "comparisons",
            "partitions",
            "partition_summaries",
            "paper_status",
            "document_status",
            "coverage",
            "extraction_coverage",
            "metrics",
            "missingness",
            "sequences",
            "transitions",
            "lead_lag",
            "annotations",
            "annotation_coverage",
            "warnings",
        ]
        for key in preferred:
            if key not in data:
                continue
            blocks.append(
                "<details>"
                f"<summary>{html.escape(key)}</summary>"
                f"<pre>{html.escape(compact_json_text(data[key]))}</pre>"
                "</details>"
            )
    else:
        entries = data.get("entries", data.get("rules", []))
        if isinstance(entries, list):
            rows: list[str] = []
            for entry in entries[:MAX_ANALYSIS_LIST_ITEMS]:
                if not isinstance(entry, dict):
                    continue
                rows.append(
                    "<tr>"
                    f"<td>{html.escape(str(entry.get('design_surface', entry.get('surface', 'unknown'))))}</td>"
                    f"<td>{html.escape(str(entry.get('target_kind', entry.get('strength', 'unknown'))))}</td>"
                    f"<td>{html.escape(str(entry.get('candidate_action', entry.get('action', 'candidate'))))}</td>"
                    f"<td>{html.escape(str(entry.get('partition', 'none')))}</td>"
                    f"<td>{html.escape(str(entry.get('source_type', 'unknown')))}</td>"
                    f"<td>{html.escape(str(entry.get('origin', 'unknown')))}</td>"
                    f"<td>{html.escape(compact_json_text(entry.get('observation', entry.get('message', '')), 600))}</td>"
                    f"<td>{html.escape(str(entry.get('valid_n', 'unknown')))}</td>"
                    f"<td>{html.escape(compact_json_text(entry.get('missingness', 'unknown'), 400))}</td>"
                    f"<td>{html.escape(compact_json_text(entry.get('uncertainty', 'unknown'), 400))}</td>"
                    f"<td>{html.escape(str(entry.get('boundary', 'writing design only')))}</td>"
                    f"<td>{html.escape(str(entry.get('source_pointer', 'unknown')))}</td>"
                    "</tr>"
                )
            if rows:
                blocks.append(
                    '<div class="analysis-table-wrap"><table>'
                    "<thead><tr><th>Surface</th><th>Rule</th><th>Disposition</th>"
                    "<th>Partition</th><th>Source type</th><th>Origin</th>"
                    "<th>Observation</th><th>valid_n</th>"
                    "<th>Missingness</th><th>Uncertainty</th><th>Boundary</th>"
                    "<th>Source</th></tr></thead>"
                    f"<tbody>{''.join(rows)}</tbody></table></div>"
                )
        for key in ("official_constraints", "deliberate_divergences", "warnings"):
            if key in data:
                blocks.append(
                    "<details>"
                    f"<summary>{html.escape(key)}</summary>"
                    f"<pre>{html.escape(compact_json_text(data[key]))}</pre>"
                    "</details>"
                )
    if not blocks:
        blocks.append(
            '<p class="small">No recognized compact fields; use the bounded raw preview below.</p>'
        )
    preview = str(artifact.get("preview", ""))
    return (
        '<article class="analysis-artifact">'
        f"<h3>{html.escape(label)}</h3>"
        f'<p><span class="pill">{html.escape(state)}</span> '
        f'<span class="pill">{html.escape(schema)}</span></p>'
        f'<p class="small">{html.escape(path)}</p>'
        + "".join(blocks)
        + "<details><summary>Bounded raw JSON preview</summary>"
        f"<pre>{html.escape(preview)}</pre></details>"
        "</article>"
    )


def render_html(model: dict[str, Any]) -> str:
    title = "yxj-paper-os 结构仪表盘"
    data = safe_json(model)
    warning_count = model["warning_count"]
    dimensions = model["dimensions"]
    rows_html = "\n".join(
        (
            f'<button class="dim-row" data-dimension="{html.escape(item["id"])}">'
            f'<span class="dim-id">{html.escape(item["id"])}</span>'
            f"<span>{html.escape(item['dimension'] or '未填写')}</span>"
            f'<span class="pill status-{html.escape(item["status"])}">{html.escape(item["status_label"])}</span>'
            f"<span>{html.escape(item['current_home'] or '无')}</span>"
            f'<span class="warn-count">{len(item["warnings"])} 警告</span>'
            "</button>"
        )
        for item in dimensions
    )
    file_html = "\n".join(
        (
            '<li class="' + ("ok" if item["present"] else "missing") + '">'
            f"<strong>{html.escape(item['file'])}</strong>"
            f"<span>{html.escape('存在' if item['present'] else '缺失')} / {item['section_count']} 个二级章节</span>"
            "</li>"
        )
        for item in model["files"]
    )
    warning_html = "\n".join(
        f"<li><strong>{html.escape(item.get('dimension_id', item['scope']))}</strong> "
        f"{html.escape(item['message'])}</li>"
        for item in model["warnings"][:80]
    )
    if not warning_html:
        warning_html = "<li>当前没有结构警告。</li>"
    template_analysis = model.get("template_analysis", {})
    summary_html = render_analysis_artifact(
        template_analysis.get("summary", {}), kind="summary"
    )
    profile_html = render_analysis_artifact(
        template_analysis.get("profile", {}), kind="profile"
    )
    analysis_html = summary_html + profile_html

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>
:root {{
  color-scheme: light;
  --bg: #f7f8f5;
  --panel: #ffffff;
  --ink: #1d2528;
  --muted: #657176;
  --line: #d9dfdd;
  --accent: #0f766e;
  --warn: #b45309;
  --bad: #b91c1c;
  --good: #15803d;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font: 14px/1.55 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}}
header {{
  padding: 24px 32px 18px;
  border-bottom: 1px solid var(--line);
  background: #eef4f1;
}}
h1 {{ margin: 0 0 8px; font-size: 28px; letter-spacing: 0; }}
h2 {{ margin: 0 0 12px; font-size: 18px; }}
h3 {{ margin: 18px 0 8px; font-size: 15px; }}
.contract {{ max-width: 980px; color: var(--muted); }}
.badge-line {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }}
.badge, .pill {{
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 4px 9px;
  background: #fff;
  color: var(--ink);
  white-space: nowrap;
}}
.layout {{
  display: grid;
  grid-template-columns: minmax(220px, 300px) minmax(420px, 1fr) minmax(340px, 520px);
  gap: 16px;
  padding: 16px;
}}
section {{
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 16px;
  min-width: 0;
}}
ul {{ margin: 0; padding-left: 18px; }}
li {{ margin: 6px 0; }}
.missing strong, .warning-list strong, .warn-count {{ color: var(--warn); }}
.dim-list {{ display: grid; gap: 8px; }}
.dim-row {{
  width: 100%;
  display: grid;
  grid-template-columns: 56px minmax(120px, 1fr) 92px minmax(120px, 1fr) 72px;
  gap: 10px;
  align-items: center;
  padding: 10px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fff;
  color: inherit;
  text-align: left;
  cursor: pointer;
}}
.dim-row:hover, .dim-row.active {{ border-color: var(--accent); box-shadow: inset 3px 0 0 var(--accent); }}
.dim-id {{ font-weight: 700; }}
.status-filled, .status-not_applicable {{ color: var(--good); }}
.status-absent, .status-deferred, .status-rejected {{ color: var(--bad); }}
.toolbar {{ display: grid; grid-template-columns: 1fr 150px; gap: 8px; margin-bottom: 12px; }}
input, select {{
  width: 100%;
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 9px 10px;
  font: inherit;
  background: #fff;
}}
pre {{
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  background: #f3f5f2;
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 12px;
  max-height: 360px;
  overflow: auto;
}}
.detail-kv {{
  display: grid;
  grid-template-columns: 120px minmax(0, 1fr);
  gap: 8px 12px;
}}
.detail-kv dt {{ color: var(--muted); }}
.detail-kv dd {{ margin: 0; overflow-wrap: anywhere; }}
.small {{ color: var(--muted); font-size: 12px; }}
.warning-list {{
  max-height: 280px;
  overflow: auto;
  border-top: 1px solid var(--line);
  padding-top: 8px;
}}
.analysis-panel {{ grid-column: 1 / -1; }}
.analysis-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }}
.analysis-artifact {{ border: 1px solid var(--line); border-radius: 8px; padding: 12px; min-width: 0; }}
.analysis-artifact h3 {{ margin-top: 0; }}
.analysis-table-wrap {{ overflow-x: auto; }}
table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
th, td {{ border: 1px solid var(--line); padding: 6px 8px; text-align: left; vertical-align: top; }}
th {{ background: #eef4f1; }}
details {{ margin: 8px 0; }}
summary {{ cursor: pointer; font-weight: 600; }}
@media (max-width: 1080px) {{
  .layout {{ grid-template-columns: 1fr; }}
  .dim-row {{ grid-template-columns: 52px minmax(0, 1fr); }}
  .dim-row span:nth-child(n+3) {{ grid-column: 2; }}
  .analysis-grid {{ grid-template-columns: 1fr; }}
}}
</style>
</head>
<body>
<header>
  <h1>{html.escape(title)}</h1>
  <p class="contract">结构化、只读、离线静态视图。它读取 yxj-paper-os 六个 Markdown 工作区文件，并在存在时安全降级读取隐藏的 corpus-summary/design-profile；只写 dashboard.html，不修改 Markdown 或分析产物，不做语义/期刊适配评分，也不声明论文或投稿就绪。</p>
  <div class="badge-line">
    <span class="badge">输出：{html.escape(model["artifact"])}</span>
    <span class="badge">结构状态：{html.escape(model["readiness"]["label"])}</span>
    <span class="badge">警告：{warning_count}</span>
  </div>
</header>
<main class="layout">
  <section>
    <h2>六文件清单</h2>
    <ul>{file_html}</ul>
    <h2 style="margin-top:18px;">结构状态</h2>
    <p>{html.escape(model["readiness"]["note"])}</p>
    <p class="small">阻塞维度：{html.escape(", ".join(model["readiness"]["blocking_dimensions"]) or "无")}</p>
    <h2 style="margin-top:18px;">警告中心</h2>
    <ul class="warning-list">{warning_html}</ul>
  </section>
  <section>
    <h2>D00-D19 维度矩阵</h2>
    <div class="toolbar">
      <input id="searchBox" type="search" placeholder="搜索 ID、文件、状态、说明">
      <select id="statusFilter">
        <option value="">全部状态</option>
        <option value="filled">filled</option>
        <option value="not_applicable">not_applicable</option>
        <option value="absent">absent</option>
        <option value="deferred">deferred</option>
        <option value="rejected">rejected</option>
      </select>
    </div>
    <div id="dimList" class="dim-list">{rows_html}</div>
  </section>
  <section>
    <h2>维度详情</h2>
    <div id="detail"></div>
  </section>
  <section class="analysis-panel">
    <h2>目标期刊 / 主题模板统计</h2>
    <p>{html.escape(str(template_analysis.get("note", "Optional writing-design analysis only.")))}</p>
    <p class="small">状态：{html.escape(str(template_analysis.get("state", "absent")))}。Malformed、stale、unsupported 或缺失产物仅降级显示，不会自动投影为写作规则。</p>
    <div class="analysis-grid">{analysis_html}</div>
  </section>
</main>
<script id="dashboard-data" type="application/json">{data}</script>
<script>
const model = JSON.parse(document.getElementById('dashboard-data').textContent);
const byId = new Map(model.dimensions.map((item) => [item.id, item]));
const detail = document.getElementById('detail');
const list = document.getElementById('dimList');
const searchBox = document.getElementById('searchBox');
const statusFilter = document.getElementById('statusFilter');

function esc(value) {{
  return String(value ?? '').replace(/[&<>"']/g, (ch) => ({{
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }}[ch]));
}}

function warningList(items) {{
  if (!items || !items.length) return '<li>无维度局部警告。</li>';
  return items.map((item) => `<li>${{esc(item)}}</li>`).join('');
}}

function sourceTables(tables) {{
  if (!tables || !tables.length) return '<p class="small">没有可显示的源表格。</p>';
  return tables.map((table, index) => {{
    const header = table.header || [];
    const rows = table.rows || [];
    const head = header.map((cell) => `<th>${{esc(cell)}}</th>`).join('');
    const body = rows.map((row) => {{
      const values = row.values || {{}};
      return `<tr>${{header.map((cell) => `<td>${{esc(values[cell] || '')}}</td>`).join('')}}</tr>`;
    }}).join('');
    const rowHtml = body || `<tr><td colspan="${{Math.max(header.length, 1)}}">没有表格数据行。</td></tr>`;
    const tableWarnings = table.warnings && table.warnings.length
      ? `<ul>${{table.warnings.map((item) => `<li>${{esc(item)}}</li>`).join('')}}</ul>`
      : '';
    return `
      <div class="source-table">
        <h4>${{esc(table.title || `表格 ${{index + 1}}`)}}</h4>
        <table><thead><tr>${{head}}</tr></thead><tbody>${{rowHtml}}</tbody></table>
        ${{tableWarnings}}
      </div>
    `;
  }}).join('');
}}

function showDimension(id) {{
  const item = byId.get(id) || model.dimensions[0];
  for (const row of list.querySelectorAll('.dim-row')) {{
    row.classList.toggle('active', row.dataset.dimension === item.id);
  }}
  const source = item.source || {{}};
  detail.innerHTML = `
    <h3>${{esc(item.id)}} · ${{esc(item.dimension || '未填写')}}</h3>
    <dl class="detail-kv">
      <dt>状态</dt><dd>${{esc(item.status)}} / ${{esc(item.status_label)}}</dd>
      <dt>阻塞设计包</dt><dd>${{esc(item.blocks || '未知')}}</dd>
      <dt>当前位置</dt><dd>${{esc(item.current_home || '无')}}</dd>
      <dt>指针/交接</dt><dd>${{esc(item.pointer || '无')}}</dd>
      <dt>解析目标</dt><dd>${{esc(source.file || '未解析')}}${{source.section ? ' # ' + esc(source.section) : ''}}</dd>
      <dt>说明</dt><dd>${{esc(item.reason || '无')}}</dd>
    </dl>
    <h3>局部警告</h3>
    <ul>${{warningList(item.warnings)}}</ul>
    <h3>索引原始行</h3>
    <pre>${{esc(item.raw || '无原始行；这是缺失 ID 的警告占位。')}}</pre>
    <h3>指针源片段</h3>
    <pre>${{esc(source.fragment || '没有可显示的指针源片段。')}}</pre>
    <h3>指针源表格</h3>
    ${{sourceTables(source.tables)}}
    <h3>外部交接片段</h3>
    <pre>${{esc(model.handoffs.map((h) => `[${{h.file}}#${{h.section}}]\\n${{h.fragment}}`).join('\\n\\n') || '无')}}</pre>
  `;
}}

function applyFilters() {{
  const query = searchBox.value.trim().toLowerCase();
  const status = statusFilter.value;
  for (const row of list.querySelectorAll('.dim-row')) {{
    const item = byId.get(row.dataset.dimension);
    const haystack = [item.id, item.dimension, item.current_home, item.status, item.reason, item.pointer, item.blocks]
      .join(' ').toLowerCase();
    row.hidden = Boolean(status && item.status !== status) || Boolean(query && !haystack.includes(query));
  }}
}}

list.addEventListener('click', (event) => {{
  const row = event.target.closest('[data-dimension]');
  if (row) showDimension(row.dataset.dimension);
}});
searchBox.addEventListener('input', applyFilters);
statusFilter.addEventListener('change', applyFilters);
showDimension(model.dimensions[0].id);
</script>
</body>
</html>
"""


def write_dashboard(workspace: Path, html_text: str) -> Path:
    resolved_workspace = workspace.resolve(strict=True)
    target_dir = resolved_workspace / CACHE_DIR
    if target_dir.is_symlink():
        raise RuntimeError(
            f"refusing to write dashboard through symlink cache directory: {target_dir}"
        )
    if target_dir.exists() and not target_dir.is_dir():
        raise RuntimeError(f"dashboard cache path is not a directory: {target_dir}")
    target_dir.mkdir(exist_ok=True)
    if target_dir.is_symlink():
        raise RuntimeError(
            f"refusing to write dashboard through symlink cache directory: {target_dir}"
        )
    resolved_target_dir = target_dir.resolve(strict=True)
    try:
        resolved_target_dir.relative_to(resolved_workspace)
    except ValueError as exc:
        raise RuntimeError(
            f"dashboard cache directory resolves outside workspace: {target_dir}"
        ) from exc

    target = target_dir / OUTPUT_NAME
    if target.is_symlink():
        raise RuntimeError(
            f"refusing to write dashboard through symlink output file: {target}"
        )
    resolved_target = target.resolve(strict=False)
    if resolved_target.parent != resolved_target_dir:
        raise RuntimeError(
            f"dashboard target resolves outside cache directory: {target}"
        )
    try:
        resolved_target.relative_to(resolved_target_dir)
    except ValueError as exc:
        raise RuntimeError(
            f"dashboard target resolves outside cache directory: {target}"
        ) from exc

    temp_path: Path | None = None
    fd: int | None = None
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    for counter in range(100):
        candidate = target_dir / f".{OUTPUT_NAME}.{os.getpid()}.{counter}.tmp"
        try:
            fd = os.open(candidate, flags, 0o666)
        except FileExistsError:
            continue
        except OSError as exc:
            raise RuntimeError(
                f"cannot create dashboard temp file safely: {candidate}: {exc}"
            ) from exc
        temp_path = candidate
        break
    if temp_path is None:
        raise RuntimeError(
            f"cannot allocate dashboard temp file in cache directory: {target_dir}"
        )
    assert fd is not None

    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(html_text)
        if target.is_symlink():
            raise RuntimeError(f"refusing to replace symlink output file: {target}")
        os.replace(temp_path, target)
        temp_path = None
    except OSError as exc:
        raise RuntimeError(
            f"cannot replace dashboard output safely: {target}: {exc}"
        ) from exc
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink()
            except FileNotFoundError:
                pass
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a read-only static yxj-paper-os dashboard from the six-file "
            "workspace and optional hidden template-analysis summaries."
        )
    )
    parser.add_argument(
        "paper_project",
        type=Path,
        help="Directory containing the six yxj-paper-os Markdown files",
    )
    args = parser.parse_args(argv)

    workspace = args.paper_project.resolve()
    model = build_model(workspace)
    try:
        target = write_dashboard(workspace, render_html(model))
    except RuntimeError as exc:
        print(f"Dashboard generation failed: {exc}", file=sys.stderr)
        return 1
    print(f"Generated structural dashboard: {target}")
    print(f"Warnings: {model['warning_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
