#!/usr/bin/env python3
"""Mechanical validator for behavior policy fixtures and recorded captures."""

from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

ACTIONS = {
    "INSPECT",
    "RECORD_OBSERVATION",
    "DERIVE",
    "PROPOSE",
    "RECONCILE",
    "ASK_OWNER",
    "DEPENDENCY_RECHECK",
    "COMPILE_SCOPED_HANDOFF",
    "KEEP_CLAIM_INACTIVE",
    "INITIALIZE_WORKSPACE",
}
SIDE_EFFECTS = {"subagents", "full_scan", "template_intake", "external_execution"}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def extract_capture(raw: Path):
    match = re.search(
        r'\{\s*"responses"\s*:\s*\[.*\]\s*\}', raw.read_text(encoding="utf-8"), re.S
    )
    if not match:
        return None
    return json.loads(match.group(0))


def validate_response(r, policy):
    e = []
    sid = r.get("scenario_id")
    s = policy.get(sid)
    if not s:
        return [f"unknown scenario {sid}"]
    required = {
        "scenario_id",
        "selected_actions",
        "target_dimensions",
        "target_scopes",
        "updates",
        "readiness_updates",
        "question",
        "side_effects",
    }
    missing = sorted(required - set(r))
    if missing:
        return [f"{sid}: missing response fields {missing}"]
    acts = set(r.get("selected_actions", []))
    bad = acts - set(ACTIONS)
    if bad:
        e.append(f"{sid}: unknown actions {sorted(bad)}")
    for a in s.get("required_all_actions", []):
        if a not in acts:
            e.append(f"{sid}: missing action {a}")
    anyr = s.get("required_any_actions", [])
    if anyr and not acts.intersection(anyr):
        e.append(f"{sid}: requires one of {anyr}")
    for a in s.get("prohibited_actions", []):
        if a in acts:
            e.append(f"{sid}: prohibited action {a}")
    dims = set(r.get("target_dimensions", []))
    for d in s.get("required_dimensions", []):
        if d not in dims:
            e.append(f"{sid}: missing dimension {d}")
    for d in s.get("prohibited_dimensions", []):
        if d in dims:
            e.append(f"{sid}: prohibited dimension {d}")
    for x in r.get("side_effects", []):
        if x not in SIDE_EFFECTS:
            e.append(f"{sid}: unknown side effect {x}")
        if x in s.get("prohibited_side_effects", []):
            e.append(f"{sid}: prohibited side effect {x}")
    q = r.get("question", {})
    qr = s.get("question", {})
    if q.get("count", 0) < qr.get("min_count", 0) or q.get("count", 0) > qr.get(
        "max_count", 10**9
    ):
        e.append(f"{sid}: question count out of range")
    if (
        q.get("count", 0)
        and qr.get("allowed_targets")
        and q.get("target") not in qr["allowed_targets"]
    ):
        e.append(f"{sid}: question target is not allowed")
    for rule in s.get("update_rules", []):
        matches = [
            u
            for u in r.get("updates", [])
            if u.get("record_kind") == rule.get("record_kind")
            and u.get("operation") == rule.get("operation")
        ]
        if len(matches) < rule.get("min_count", 0):
            e.append(f"{sid}: update rule not satisfied")
        if (
            rule.get("field")
            and rule.get("allowed")
            and any(u.get(rule["field"]) not in rule["allowed"] for u in matches)
        ):
            e.append(f"{sid}: update field has disallowed value")
    for rule in s.get("readiness_rules", []):
        matches = [
            u
            for u in r.get("readiness_updates", [])
            if u.get("scope_id") == rule.get("scope_id")
        ]
        if len(matches) < rule.get("min_count", 0):
            e.append(f"{sid}: readiness rule not satisfied")
    return e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "path",
        nargs="?",
        default="skills/yxj-paper-os/assets/evals/behavior-scenarios.json",
    )
    ap.add_argument("--capture")
    ap.add_argument("--skill", default="skills/yxj-paper-os/SKILL.md")
    ap.add_argument(
        "--scenarios",
        default="skills/yxj-paper-os/assets/evals/behavior-scenarios.json",
    )
    a = ap.parse_args()
    p = Path(a.path)
    data = load(p)
    scenarios = data.get("scenarios", data if isinstance(data, list) else [])
    policy = {x["id"]: x for x in scenarios}
    errs = []
    if len(policy) != 14:
        errs.append(f"expected 14 scenarios, found {len(policy)}")
    if a.capture:
        c = Path(a.capture)
        acts = load(c / "actions.json")
        extracted = extract_capture(c / "raw-output.md")
        if extracted is None or json.dumps(
            extracted, sort_keys=True, ensure_ascii=False
        ) != json.dumps(acts, sort_keys=True, ensure_ascii=False):
            errs.append("raw-output/actions normalized equality failed")
        rs = acts.get("responses", acts if isinstance(acts, list) else [])
        if len(rs) != 14 or len({r.get("scenario_id") for r in rs}) != 14:
            errs.append("capture must contain 14 responses")
        for r in rs:
            errs.extend(validate_response(r, policy))
        man = load(c / "manifest.json")
        if man.get("scenario_ids") != [r.get("scenario_id") for r in rs]:
            errs.append("manifest scenario_ids do not match actions")
        if man.get("skill_sha256") and man["skill_sha256"] != sha(Path(a.skill)):
            errs.append("hash mismatch SKILL.md")
        if man.get("scenarios_sha256") and man["scenarios_sha256"] != sha(
            Path(a.scenarios)
        ):
            errs.append("hash mismatch behavior-scenarios.json")
        for key, file in [
            ("skill_sha256", "SKILL.md"),
            ("scenarios_sha256", "behavior-scenarios.json"),
            ("prompt_sha256", "prompt.md"),
            ("raw_output_sha256", "raw-output.md"),
            ("actions_sha256", "actions.json"),
        ]:
            if (
                key in man
                and file in {"prompt.md", "raw-output.md", "actions.json"}
                and sha(c / file) != man[key]
            ):
                errs.append(f"hash mismatch {file}")
    if errs:
        print("\n".join(errs))
        return 1
    print("behavior scenarios valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
