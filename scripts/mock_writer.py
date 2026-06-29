#!/usr/bin/env python3
"""Deterministic Phase 7 mock writer for strict TaskPacket fixtures."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Any

try:
    from ppg_validate_common import ValidationIssue, load_document
    from validate_candidate_return import validate as validate_candidate_return
    from validate_packet import validate as validate_packet
    from validate_section_draft import validate as validate_section_draft
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ppg_validate_common import ValidationIssue, load_document  # type: ignore  # noqa: E402
    from validate_candidate_return import validate as validate_candidate_return  # type: ignore  # noqa: E402
    from validate_packet import validate as validate_packet  # type: ignore  # noqa: E402
    from validate_section_draft import validate as validate_section_draft  # type: ignore  # noqa: E402

RETURN_KEY_ORDER = [
    "schema_version",
    "return_id",
    "status",
    "packet_id",
    "output_artifact_path",
    "evidence",
    "validator_expectations",
    "remaining_risks",
    "graph_completion_claimed",
    "recursive_dispatch_requested",
    "writes_outside_allowed_paths",
]


def _yaml_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    text = str(value)
    if text == "" or text.strip() != text or ":" in text or text.startswith(("[", "{", "#", "-")):
        escaped = text.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return text


def _emit_yaml_value(key: str, value: Any, lines: list[str], indent: int) -> None:
    prefix = " " * indent
    if isinstance(value, dict):
        lines.append(f"{prefix}{key}:")
        for nested_key, nested_value in value.items():
            _emit_yaml_value(str(nested_key), nested_value, lines, indent + 2)
    elif isinstance(value, list):
        lines.append(f"{prefix}{key}:")
        for item in value:
            item_prefix = " " * (indent + 2)
            if isinstance(item, dict):
                lines.append(f"{item_prefix}-")
                for nested_key, nested_value in item.items():
                    _emit_yaml_value(str(nested_key), nested_value, lines, indent + 4)
            else:
                lines.append(f"{item_prefix}- {_yaml_scalar(item)}")
    else:
        lines.append(f"{prefix}{key}: {_yaml_scalar(value)}")


def _write_yaml(path: Path, payload: dict[str, Any], key_order: list[str]) -> None:
    lines: list[str] = []
    emitted: set[str] = set()
    for key in key_order:
        if key in payload:
            _emit_yaml_value(key, payload[key], lines, 0)
            emitted.add(key)
    for key in payload:
        if key not in emitted:
            _emit_yaml_value(key, payload[key], lines, 0)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _print_issues(label: str, issues: list[ValidationIssue]) -> int:
    print(f"INVALID {label}", file=sys.stderr)
    for validation_issue in issues:
        print(f"- {validation_issue.code}: {validation_issue.message}", file=sys.stderr)
    return 1


def _draft_text(packet: dict[str, Any]) -> str:
    source_materials = packet.get("input_materials")
    evidence_anchors = packet.get("evidence_anchors")
    if not isinstance(source_materials, list) or not all(isinstance(item, str) for item in source_materials):
        raise ValueError("packet input_materials must be a list of strings")
    if not isinstance(evidence_anchors, list) or not all(isinstance(item, str) for item in evidence_anchors):
        raise ValueError("packet evidence_anchors must be a list of strings")
    source_lines = "\n".join(f"  - {item}" for item in source_materials)
    evidence_lines = "\n".join(f"  - {item}" for item in evidence_anchors)
    packet_id = str(packet.get("packet_id"))
    return f"""---
schema_version: ppg-section-draft/v0.1
draft_id: intro_draft_v2
status: candidate
section_id: intro
packet_id: {packet_id}
source_materials:
{source_lines}
evidence_anchors:
{evidence_lines}
graph_completion_claimed: false
recursive_dispatch_requested: false
---
# Introduction

When fresh V2X authority loses force, the controller should not treat suspicious messages as repaired truth. The active evidence supports a bounded authority-allocation claim: fresh V2X, trusted short memory, local sensing, and physical dynamics each retain only the control authority justified by the current evidence inventory.

This candidate introduction therefore frames the paper around graceful authority degradation rather than a universal safety promise. It remains a draft artifact until the main runtime validates and ingests it.
"""


def _candidate_return(packet: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "ppg-candidate-return/v0.1",
        "return_id": "intro_candidate_return_phase7",
        "status": "candidate",
        "packet_id": packet["packet_id"],
        "output_artifact_path": packet["output_artifact_path"],
        "evidence": [
            "mock_writer consumed strict intro_writing_packet_v2",
            "mock_writer wrote only the packet output_artifact_path",
            "section draft keeps bounded authority wording and evidence anchors",
        ],
        "validator_expectations": [
            "validate_section_draft.py must pass on the candidate markdown",
            "validate_candidate_return.py must pass against the originating packet",
            "main agent remains responsible for graph ingestion and delivery gating",
        ],
        "remaining_risks": [
            "semantic quality remains candidate-only until reviewer closure and delivery gate pass",
        ],
        "graph_completion_claimed": False,
        "recursive_dispatch_requested": False,
        "writes_outside_allowed_paths": False,
    }


def write_candidate(packet_path: Path, return_out: Path) -> int:
    packet, load_errors = load_document(packet_path)
    if load_errors:
        return _print_issues(str(packet_path), load_errors)
    packet_errors = validate_packet(packet)
    if packet_errors:
        return _print_issues(str(packet_path), packet_errors)
    assert isinstance(packet, dict)
    if packet.get("packet_id") != "intro_writing_packet_v2":
        return _print_issues(str(packet_path), [ValidationIssue("E_MOCK_WRITER_UNSUPPORTED_PACKET", "mock writer supports intro_writing_packet_v2 only")])
    if packet.get("expected_output_schema") != "ppg-section-draft/v0.1":
        return _print_issues(str(packet_path), [ValidationIssue("E_MOCK_WRITER_UNSUPPORTED_SCHEMA", "mock writer requires ppg-section-draft/v0.1 output schema")])

    output_path = Path(str(packet.get("output_artifact_path")))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_draft_text(packet), encoding="utf-8")

    section_errors = validate_section_draft(output_path)
    if section_errors:
        return _print_issues(str(output_path), section_errors)

    return_payload = _candidate_return(packet)
    return_errors = validate_candidate_return(return_payload, packet)
    if return_errors:
        return _print_issues(str(return_out), return_errors)
    _write_yaml(return_out, return_payload, RETURN_KEY_ORDER)

    return_data, return_load_errors = load_document(return_out)
    if return_load_errors:
        return _print_issues(str(return_out), return_load_errors)
    written_errors = validate_candidate_return(return_data, packet)
    if written_errors:
        return _print_issues(str(return_out), written_errors)

    print("MOCK_WRITER_OK")
    print(f"packet_id: {packet['packet_id']}")
    print(f"wrote: {output_path}")
    print(f"return: {return_out}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run deterministic Phase7 mock writer against a strict TaskPacket.")
    parser.add_argument("--packet", required=True, type=Path)
    parser.add_argument("--return-out", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return write_candidate(args.packet, args.return_out)


if __name__ == "__main__":
    raise SystemExit(main())
