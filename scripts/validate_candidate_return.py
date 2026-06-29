#!/usr/bin/env python3
"""Validate Phase 6 packet-aware CandidateArtifactReturn fixtures."""
from __future__ import annotations

import argparse
from pathlib import Path, PurePosixPath
import sys
from typing import Any

try:
    from ppg_validate_common import (
        ValidationIssue,
        issue,
        is_non_empty_string,
        is_non_empty_string_list,
        load_document,
        print_result,
        require_mapping_document,
        require_string_fields,
    )
    from validate_packet import validate as validate_packet
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ppg_validate_common import (  # type: ignore  # noqa: E402
        ValidationIssue,
        issue,
        is_non_empty_string,
        is_non_empty_string_list,
        load_document,
        print_result,
        require_mapping_document,
        require_string_fields,
    )
    from validate_packet import validate as validate_packet  # type: ignore  # noqa: E402

ALLOWED_RETURN_FIELDS = {
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
}


def _path_is_within(path: str, allowed: str) -> bool:
    if not _is_safe_repo_relative_path(path) or not _is_safe_repo_relative_path(allowed):
        return False
    normalized = PurePosixPath(path)
    allowed_normalized = PurePosixPath(allowed)
    if normalized == allowed_normalized:
        return True
    try:
        normalized.relative_to(allowed_normalized)
    except ValueError:
        return False
    return True


def _is_safe_repo_relative_path(path: str) -> bool:
    if path.strip() != path or "\\" in path:
        return False
    if any(ord(char) < 32 for char in path):
        return False
    if path.startswith("~") or (len(path) >= 2 and path[1] == ":"):
        return False
    if path.strip() in {"", ".", "./", "..", "../", "/"}:
        return False
    parsed = PurePosixPath(path)
    if parsed.is_absolute() or not parsed.suffix:
        return False
    return not any(part in {"", ".", ".."} for part in path.split("/"))


def validate(data: Any, packet: dict[str, Any]) -> list[ValidationIssue]:
    errors = require_mapping_document(data)
    if errors:
        return errors
    assert isinstance(data, dict)
    unknown_fields = sorted(set(data) - ALLOWED_RETURN_FIELDS)
    if unknown_fields:
        errors.append(issue("E_RETURN_UNKNOWN_FIELD", f"unknown CandidateArtifactReturn fields are not allowed: {', '.join(unknown_fields)}"))
    errors.extend(require_string_fields(data, ["schema_version", "return_id", "status", "packet_id", "output_artifact_path"], "E_RETURN_FIELD_REQUIRED"))
    if data.get("schema_version") and data.get("schema_version") != "ppg-candidate-return/v0.1":
        errors.append(issue("E_RETURN_FIELD_REQUIRED", "schema_version must be ppg-candidate-return/v0.1"))
    if data.get("status") != "candidate":
        errors.append(issue("E_RETURN_STATUS_REQUIRED", "status must be candidate"))
    if data.get("packet_id") != packet.get("packet_id"):
        errors.append(issue("E_RETURN_PACKET_ID_MISMATCH", f"return packet_id {data.get('packet_id')} must match packet {packet.get('packet_id')}"))
    if data.get("graph_completion_claimed") is not False:
        errors.append(issue("E_RETURN_GRAPH_COMPLETION_FORBIDDEN", "graph_completion_claimed must be false"))
    if data.get("recursive_dispatch_requested") is not False:
        errors.append(issue("E_RETURN_RECURSIVE_DISPATCH_FORBIDDEN", "recursive_dispatch_requested must be false"))
    if data.get("writes_outside_allowed_paths") is not False:
        errors.append(issue("E_RETURN_WRITE_ESCAPE_FORBIDDEN", "writes_outside_allowed_paths must be false"))
    for field_name, code in (
        ("evidence", "E_RETURN_EVIDENCE_REQUIRED"),
        ("validator_expectations", "E_RETURN_VALIDATOR_EXPECTATIONS_REQUIRED"),
        ("remaining_risks", "E_RETURN_REMAINING_RISKS_REQUIRED"),
    ):
        if not is_non_empty_string_list(data.get(field_name)):
            errors.append(issue(code, f"{field_name} must be a non-empty list of strings"))
    output = data.get("output_artifact_path")
    packet_output = packet.get("output_artifact_path")
    if is_non_empty_string(output) and is_non_empty_string(packet_output) and output != packet_output:
        errors.append(issue("E_RETURN_OUTPUT_PATH_MISMATCH", "output_artifact_path must match originating packet output_artifact_path"))
    allowed_write_paths = packet.get("allowed_write_paths")
    if (
        is_non_empty_string(output)
        and isinstance(allowed_write_paths, list)
        and all(is_non_empty_string(path) for path in allowed_write_paths)
    ):
        if not any(_path_is_within(str(output), str(path)) for path in allowed_write_paths):
            errors.append(issue("E_RETURN_OUTPUT_OUTSIDE_PACKET_ALLOWED_WRITES", "output_artifact_path must be within originating packet allowed_write_paths"))
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate a packet-aware CandidateArtifactReturn fixture.")
    parser.add_argument("return_fixture", type=Path)
    parser.add_argument("--packet", required=True, type=Path, help="Originating strict TaskPacket fixture")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    packet_data, packet_load_errors = load_document(args.packet)
    if packet_load_errors:
        return print_result(args.packet, packet_load_errors)
    packet_errors = validate_packet(packet_data)
    if packet_errors:
        return print_result(args.packet, packet_errors)
    assert isinstance(packet_data, dict)

    return_data, errors = load_document(args.return_fixture)
    if errors:
        return print_result(args.return_fixture, errors)
    return print_result(args.return_fixture, validate(return_data, packet_data))


if __name__ == "__main__":
    raise SystemExit(main())
