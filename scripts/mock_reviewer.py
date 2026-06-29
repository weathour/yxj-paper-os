#!/usr/bin/env python3
"""Deterministic Phase 7 mock reviewer for the overclaim vertical slice."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Any

try:
    from ppg_validate_common import ValidationIssue, load_document
    from validate_delivery_gate import validate as validate_delivery_gate
    from validate_review_finding import validate as validate_review_finding
    from validate_section_draft import FORBIDDEN_OVERCLAIM_PHRASES, validate as validate_section_draft
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ppg_validate_common import ValidationIssue, load_document  # type: ignore  # noqa: E402
    from validate_delivery_gate import validate as validate_delivery_gate  # type: ignore  # noqa: E402
    from validate_review_finding import validate as validate_review_finding  # type: ignore  # noqa: E402
    from validate_section_draft import FORBIDDEN_OVERCLAIM_PHRASES, validate as validate_section_draft  # type: ignore  # noqa: E402

FINDING_KEY_ORDER = [
    "schema_version",
    "finding_id",
    "status",
    "failure_type",
    "severity",
    "target",
    "summary",
    "payload",
]
CLOSURE_KEY_ORDER = ["schema_version", "closure_id", "status", "finding_id", "evidence"]
GATE_KEY_ORDER = ["schema_version", "gate_id", "status", "closures", "unresolved_blockers"]


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


def _read_body(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            return parts[2]
    return text


def _has_overclaim(path: Path) -> bool:
    body = _read_body(path).lower()
    return any(phrase in body for phrase in FORBIDDEN_OVERCLAIM_PHRASES)


def finding_payload() -> dict[str, Any]:
    return {
        "schema_version": "ppg-review-finding/v0.1",
        "finding_id": "phase7_overclaim_review_finding_v1",
        "status": "validated",
        "failure_type": "claim_overreach",
        "severity": "high",
        "target": "claim_boundary_map_v1",
        "summary": "Phase7 mock reviewer found an overstrong universal safety claim in the stale introduction draft.",
        "payload": {
            "claim_text": "The platoon controller guarantees universal safety under V2X authority loss.",
            "recommended_target": "claim_boundary_map",
            "source_draft": "examples/manuscript/intro.v1.md",
        },
    }


def write_finding(draft: Path, out: Path) -> int:
    if not draft.exists():
        return _print_issues(str(draft), [ValidationIssue("E_MOCK_REVIEWER_DRAFT_MISSING", "draft path does not exist")])
    if not _has_overclaim(draft):
        return _print_issues(str(draft), [ValidationIssue("E_MOCK_REVIEWER_NO_OVERCLAIM", "finding mode requires a draft with forbidden overclaim wording")])
    payload = finding_payload()
    errors = validate_review_finding(payload)
    if errors:
        return _print_issues(str(out), errors)
    _write_yaml(out, payload, FINDING_KEY_ORDER)
    written, load_errors = load_document(out)
    if load_errors:
        return _print_issues(str(out), load_errors)
    written_errors = validate_review_finding(written)
    if written_errors:
        return _print_issues(str(out), written_errors)
    print("MOCK_REVIEWER_FINDING_OK")
    print(f"draft: {draft}")
    print(f"finding: {out}")
    return 0


def _closure_payload(status: str, evidence: list[str]) -> dict[str, Any]:
    return {
        "schema_version": "ppg-review-closure/v0.1",
        "closure_id": "phase7_overclaim_closure_v1",
        "status": status,
        "finding_id": "phase7_overclaim_review_finding_v1",
        "evidence": evidence,
    }


def _gate_payload(status: str, blockers: list[str]) -> dict[str, Any]:
    return {
        "schema_version": "ppg-delivery-gate/v0.1",
        "gate_id": "phase7_delivery_gate_v1",
        "status": status,
        "closures": ["phase7_overclaim_closure_v1"],
        "unresolved_blockers": blockers,
    }


def write_closure(draft: Path, closure_out: Path, gate_out: Path) -> int:
    section_errors = validate_section_draft(draft)
    overclaim = _has_overclaim(draft) if draft.exists() else False
    if section_errors or overclaim:
        evidence = [f"blocked_by:{validation_issue.code}" for validation_issue in section_errors]
        if overclaim:
            evidence.append("blocked_by:E_SECTION_FORBIDDEN_OVERCLAIM")
        closure = _closure_payload("blocked", evidence or ["blocked_by:unknown_draft_error"])
        gate = _gate_payload("blocked", ["section_draft_not_valid_for_closure"])
        _write_yaml(closure_out, closure, CLOSURE_KEY_ORDER)
        _write_yaml(gate_out, gate, GATE_KEY_ORDER)
        closure_errors = validate_delivery_gate(closure)
        gate_errors = validate_delivery_gate(gate)
        if closure_errors or gate_errors:
            return _print_issues("mock_reviewer_blocked_outputs", [*closure_errors, *gate_errors])
        print("MOCK_REVIEWER_CLOSURE_BLOCKED")
        print(f"draft: {draft}")
        print(f"closure: {closure_out}")
        print(f"gate: {gate_out}")
        return 1

    closure = _closure_payload(
        "validated",
        [
            "candidate intro draft validates as ppg-section-draft/v0.1",
            "forbidden universal safety wording is absent",
            "bounded authority framing is present with active evidence anchors",
        ],
    )
    gate = _gate_payload("pass", [])
    closure_errors = validate_delivery_gate(closure)
    gate_errors = validate_delivery_gate(gate)
    if closure_errors or gate_errors:
        return _print_issues("mock_reviewer_closure_outputs", [*closure_errors, *gate_errors])
    _write_yaml(closure_out, closure, CLOSURE_KEY_ORDER)
    _write_yaml(gate_out, gate, GATE_KEY_ORDER)
    print("MOCK_REVIEWER_CLOSURE_OK")
    print(f"draft: {draft}")
    print(f"closure: {closure_out}")
    print(f"gate: {gate_out}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run deterministic Phase7 mock reviewer.")
    parser.add_argument("--mode", required=True, choices=["finding", "closure"])
    parser.add_argument("--draft", required=True, type=Path)
    parser.add_argument("--out", type=Path, help="ReviewFinding output path for finding mode")
    parser.add_argument("--closure-out", type=Path, help="ReviewClosure output path for closure mode")
    parser.add_argument("--gate-out", type=Path, help="DeliveryGate output path for closure mode")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.mode == "finding":
        if args.out is None:
            print("--out is required for finding mode", file=sys.stderr)
            return 2
        return write_finding(args.draft, args.out)
    if args.closure_out is None or args.gate_out is None:
        print("--closure-out and --gate-out are required for closure mode", file=sys.stderr)
        return 2
    return write_closure(args.draft, args.closure_out, args.gate_out)


if __name__ == "__main__":
    raise SystemExit(main())
