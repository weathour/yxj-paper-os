#!/usr/bin/env python3
"""Mechanical validator for behavior policy fixtures and recorded captures."""

from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

from capture_behavior_actions import (
    PROMPT_CONTRACT_VERSION,
    build_output_schema,
    load_scenarios,
    model_visible_scenario_json,
    prompt_contract_errors,
    sha_text,
)

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
SIDE_EFFECTS = {
    "subagents",
    "full_scan",
    "template_intake",
    "template_analysis",
    "pdf_pseudo_parse",
    "external_execution",
}
RECORD_KIND_ALIASES = {
    "material_record": "material",
    "template_metric_observation": "material",
    "template_analysis": "material",
    "writing_design_rule": "design_rule",
    "template_design_profile": "design_rule",
    "writing_design_proposal": "design_rule",
    "design_profile": "design_rule",
    "claim_record": "claim",
    "decision_record": "decision",
}


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


def normalized_record_kind(value):
    if not isinstance(value, str):
        return value
    token = re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_")
    return RECORD_KIND_ALIASES.get(token, token)


def rule_matches(item, rule, *, readiness=False):
    """Match semantic policy rules without overfitting model-chosen record labels."""
    if readiness:
        if rule.get("scope_id") is not None and item.get("scope_id") != rule.get(
            "scope_id"
        ):
            return False
    else:
        item_kind = normalized_record_kind(item.get("record_kind"))
        if rule.get("record_kind") is not None and item_kind != normalized_record_kind(
            rule.get("record_kind")
        ):
            return False
        allowed_kinds = {
            normalized_record_kind(value) for value in rule.get("record_kinds", [])
        }
        if allowed_kinds and item_kind not in allowed_kinds:
            return False
        if rule.get("operation") is not None and item.get("operation") != rule.get(
            "operation"
        ):
            return False
        if rule.get("operations") and item.get("operation") not in rule["operations"]:
            return False
    field = rule.get("field")
    allowed = rule.get("allowed")
    if field and allowed and item.get(field) not in allowed:
        return False
    for asserted_field, asserted_allowed in rule.get("allowed_fields", {}).items():
        if item.get(asserted_field) not in asserted_allowed:
            return False
    any_field = rule.get("allowed_any_field")
    if any_field:
        fields = any_field.get("fields", [])
        allowed_values = any_field.get("allowed", [])
        if not any(item.get(name) in allowed_values for name in fields):
            return False
    return True


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
    selected_actions = r.get("selected_actions", [])
    if not isinstance(selected_actions, list):
        e.append(f"{sid}: selected_actions must be an array")
        selected_actions = []
    acts = set(selected_actions)
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
    target_dimensions = r.get("target_dimensions", [])
    if not isinstance(target_dimensions, list):
        e.append(f"{sid}: target_dimensions must be an array")
        target_dimensions = []
    dims = set(target_dimensions)
    for d in s.get("required_dimensions", []):
        if d not in dims:
            e.append(f"{sid}: missing dimension {d}")
    for d in s.get("prohibited_dimensions", []):
        if d in dims:
            e.append(f"{sid}: prohibited dimension {d}")
    target_scopes = r.get("target_scopes", [])
    if not isinstance(target_scopes, list):
        e.append(f"{sid}: target_scopes must be an array")
        target_scopes = []
    scopes = set(target_scopes)
    for scope in s.get("required_scopes", []):
        if scope not in scopes:
            e.append(f"{sid}: missing scope {scope}")
    for scope in s.get("prohibited_scopes", []):
        if scope in scopes:
            e.append(f"{sid}: prohibited scope {scope}")
    side_effect_values = r.get("side_effects", [])
    if not isinstance(side_effect_values, list):
        e.append(f"{sid}: side_effects must be an array")
        side_effect_values = []
    response_side_effects = set(side_effect_values)
    for x in response_side_effects:
        if x not in SIDE_EFFECTS:
            e.append(f"{sid}: unknown side effect {x}")
        if x in s.get("prohibited_side_effects", []):
            e.append(f"{sid}: prohibited side effect {x}")
    for x in s.get("required_side_effects", []):
        if x not in response_side_effects:
            e.append(f"{sid}: missing side effect {x}")
    q = r.get("question", {})
    if not isinstance(q, dict):
        e.append(f"{sid}: question must be an object")
        q = {}
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
    raw_updates = r.get("updates", [])
    if not isinstance(raw_updates, list):
        e.append(f"{sid}: updates must be an array")
        raw_updates = []
    if any(not isinstance(item, dict) for item in raw_updates):
        e.append(f"{sid}: updates must contain objects")
    updates = [item for item in raw_updates if isinstance(item, dict)]
    for rule in s.get("update_rules", []):
        matches = [u for u in updates if rule_matches(u, rule)]
        if len(matches) < rule.get("min_count", 0):
            e.append(f"{sid}: update rule not satisfied")
    raw_readiness = r.get("readiness_updates", [])
    if not isinstance(raw_readiness, list):
        e.append(f"{sid}: readiness_updates must be an array")
        raw_readiness = []
    if any(not isinstance(item, dict) for item in raw_readiness):
        e.append(f"{sid}: readiness_updates must contain objects")
    readiness_updates = [item for item in raw_readiness if isinstance(item, dict)]
    for rule in s.get("readiness_rules", []):
        matches = [
            u for u in readiness_updates if rule_matches(u, rule, readiness=True)
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
        default=None,
    )
    a = ap.parse_args()
    p = Path(a.path)
    scenario_hash_path = Path(a.scenarios) if a.scenarios else p
    try:
        scenarios = load_scenarios(p)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"behavior scenario document is invalid: {exc}")
        return 1
    policy = {x["id"]: x for x in scenarios}
    errs = []
    if len(policy) != len(scenarios):
        errs.append("scenario IDs must be unique")
    if a.capture:
        c = Path(a.capture)
        prompt_path = c / "prompt.md"
        skill_path = Path(a.skill)
        reference_path = skill_path.parent / "references/lenses/venue-template.md"
        try:
            prompt_text = prompt_path.read_text(encoding="utf-8")
            skill_text = skill_path.read_text(encoding="utf-8")
            reference_text = reference_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            errs.append(f"cannot read capture prompt, skill, or reference: {exc}")
            prompt_text = ""
            skill_text = ""
            reference_text = ""
        if prompt_text and skill_text and reference_text:
            errs.extend(
                prompt_contract_errors(
                    prompt_text, skill_text, reference_text, scenarios
                )
            )
        output_schema_path = c / "output-schema.json"
        expected_output_schema = (
            json.dumps(
                build_output_schema(scenarios),
                ensure_ascii=False,
                sort_keys=True,
                indent=2,
            )
            + "\n"
        )
        try:
            if output_schema_path.read_text(encoding="utf-8") != expected_output_schema:
                errs.append(
                    "output-schema.json does not match current behavior contract"
                )
        except (OSError, UnicodeDecodeError) as exc:
            errs.append(f"cannot read output-schema.json: {exc}")
        acts = load(c / "actions.json")
        extracted = extract_capture(c / "raw-output.md")
        if extracted is None or json.dumps(
            extracted, sort_keys=True, ensure_ascii=False
        ) != json.dumps(acts, sort_keys=True, ensure_ascii=False):
            errs.append("raw-output/actions normalized equality failed")
        rs = acts.get("responses", acts if isinstance(acts, list) else [])
        expected_ids = set(policy)
        response_ids = [r.get("scenario_id") for r in rs if isinstance(r, dict)]
        if len(rs) != len(expected_ids) or set(response_ids) != expected_ids:
            errs.append(
                f"capture must contain exactly {len(expected_ids)} responses matching scenario IDs"
            )
        for index, r in enumerate(rs):
            if not isinstance(r, dict):
                errs.append(f"capture response {index} is not an object")
                continue
            errs.extend(validate_response(r, policy))
        man = load(c / "manifest.json")
        if man.get("prompt_contract_version") != PROMPT_CONTRACT_VERSION:
            errs.append("manifest prompt_contract_version is missing or stale")
        expected_visible_hash = sha_text(model_visible_scenario_json(scenarios))
        if man.get("model_visible_scenarios_sha256") != expected_visible_hash:
            errs.append("hash mismatch model-visible scenario projection")
        if man.get("scenario_ids") != [r.get("scenario_id") for r in rs]:
            errs.append("manifest scenario_ids do not match actions")
        if man.get("scenario_count") != len(expected_ids):
            errs.append("manifest scenario_count does not match current policy")
        if man.get("skill_sha256") and man["skill_sha256"] != sha(Path(a.skill)):
            errs.append("hash mismatch SKILL.md")
        if man.get("venue_template_sha256") != sha(reference_path):
            errs.append("hash mismatch venue-template.md")
        if man.get("scenarios_sha256") and man["scenarios_sha256"] != sha(
            scenario_hash_path
        ):
            errs.append("hash mismatch behavior-scenarios.json")
        for key, file in [
            ("skill_sha256", "SKILL.md"),
            ("scenarios_sha256", "behavior-scenarios.json"),
            ("prompt_sha256", "prompt.md"),
            ("output_schema_sha256", "output-schema.json"),
            ("raw_output_sha256", "raw-output.md"),
            ("actions_sha256", "actions.json"),
        ]:
            if (
                key in man
                and file
                in {
                    "prompt.md",
                    "output-schema.json",
                    "raw-output.md",
                    "actions.json",
                }
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
