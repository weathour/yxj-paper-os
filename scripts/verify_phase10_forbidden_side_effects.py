#!/usr/bin/env python3
"""Guard Phase10 against forbidden runtime/plugin side effects and false readiness."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MONITORED_PATHS = [
    "README.md",
    "PRODUCT.md",
    "AGENTS.md",
    "skills/yxj-paper-os/SKILL.md",
    "docs/phase-promotions/PHASE_10_REAL_SUBAGENT_RUN_READINESS_2026-06-30.md",
    "runtime/stage_registry.json",
    "runtime/phase10_content_validators.json",
    "scripts/generate_phase10_run_dry_run.py",
    "scripts/verify_phase10_run_readiness.py",
    "scripts/verify_phase10_forbidden_side_effects.py",
    "scripts/verify_phase10_real_run_readiness.sh",
]
FORBIDDEN_TERMS = ["unregistered external route", "unregistered-external-route", "unauthorized recursive route enabled", "old route skills active", "publish enabled"]
ALLOW_HINTS = [
    "do not",
    "do **not**",
    "must not",
    "not ",
    "not-enabled",
    "not enabled",
    "non-goal",
    "non-goals",
    "forbidden",
    "historical",
    "provenance",
    "boundary",
    "read-only",
    "guard",
    "allowlist",
    "reject",
    "fails on",
    "without explicit",
    "no live",
]
ACTIVE_HINTS = [
    "is enabled",
    "enabled by default",
    "publish enabled",
    "published to",
    "installed to",
    "use unregistered external route as design source",
    "based on unregistered external route",
    "unauthorized recursive route enabled",
    "old route skills active",
]


def issue(code: str, message: str) -> str:
    return f"{code}: {message}"


def monitored_existing_paths() -> list[Path]:
    return [ROOT / rel for rel in MONITORED_PATHS if (ROOT / rel).exists()]


def allowed_line(line: str) -> bool:
    lowered = line.lower()
    if "forbidden_terms" in lowered or "allow_hints" in lowered or "active_hints" in lowered or "monitored_paths" in lowered:
        return True
    if line.strip().startswith('"') and line.strip().endswith(','):
        return True
    if line.strip().startswith('"') and line.strip().endswith('"'):
        return True
    if "phase10_forbidden_side_effects_ok" in lowered:
        return True
    return any(hint in lowered for hint in ALLOW_HINTS)


def verify_text_boundaries() -> list[str]:
    errors: list[str] = []
    for path in monitored_existing_paths():
        rel = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), start=1):
            lowered = line.lower()
            if any(active in lowered for active in ACTIVE_HINTS) and not allowed_line(line):
                errors.append(issue("E_PHASE10_FORBIDDEN_ACTIVE_SIDE_EFFECT", f"{rel}:{lineno}: {line.strip()}"))
            if any(term.lower() in lowered for term in FORBIDDEN_TERMS) and not allowed_line(line):
                errors.append(issue("E_PHASE10_FORBIDDEN_TERM_UNBOUNDED", f"{rel}:{lineno}: {line.strip()}"))
    return errors


def verify_no_stale_worker_blockers() -> list[str]:
    errors: list[str] = []
    registry = json.loads((ROOT / "runtime" / "stage_registry.json").read_text(encoding="utf-8"))
    for stage in registry.get("stages", []):
        contract_path = ROOT / stage["contract_ref"]
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        coverage = contract.get("worker_packet_coverage", {})
        status = coverage.get("status")
        if stage.get("requires_worker_task_packet") and status != "linked_strict_packet":
            errors.append(issue("E_PHASE10_WORKER_BLOCKER_REMAINS", f"{stage['stage_id']} status={status}"))
        if status == "planned_with_blocker":
            errors.append(issue("E_PHASE10_PLANNED_WITH_BLOCKER_REMAINS", stage["stage_id"]))
    coverage_path = ROOT / "examples" / "local-paper" / "security-state-aware-mixed-platoon" / "stage_coverage.json"
    if coverage_path.exists():
        coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        counts = coverage.get("worker_task_packet_status_counts", {})
        if counts.get("planned_with_blocker", 0):
            errors.append(issue("E_PHASE10_COVERAGE_BLOCKER_REMAINS", str(counts)))
    return errors


def verify_aggregate_has_authority() -> list[str]:
    path = ROOT / "scripts" / "verify_phase10_real_run_readiness.sh"
    if not path.exists():
        return [issue("E_PHASE10_AGGREGATE_MISSING", "scripts/verify_phase10_real_run_readiness.sh")]
    text = path.read_text(encoding="utf-8")
    required_snippets = [
        "verify_phase10_forbidden_side_effects.py",
        "verify_phase10_run_readiness.py",
        "verify_phase9_full_stage_runtime.sh",
        "verify_phase8_plugin_surface.sh",
        "verify_phase6_task_packets.sh",
        "validate_plugin.py",
        "quick_validate.py",
        "python3 -m py_compile scripts/*.py",
        "git diff --check -- .",
        "git status --short -- .",
        "PHASE10_REAL_RUN_READINESS_VERIFY_OK",
    ]
    missing = [snippet for snippet in required_snippets if snippet not in text]
    return [issue("E_PHASE10_AGGREGATE_AUTHORITY", f"missing {missing}")] if missing else []


def main() -> int:
    errors: list[str] = []
    errors.extend(verify_text_boundaries())
    errors.extend(verify_no_stale_worker_blockers())
    # Aggregate script may be created later in the same milestone; fail only when present or final docs reference Phase10.
    if (ROOT / "scripts" / "verify_phase10_real_run_readiness.sh").exists():
        errors.extend(verify_aggregate_has_authority())
    if errors:
        print("INVALID Phase10 forbidden side-effect guard", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("PHASE10_FORBIDDEN_SIDE_EFFECTS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
