#!/usr/bin/env python3
"""Create oracle-free model prompts and finalize behavior captures."""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
from pathlib import Path
from typing import Any

PROMPT_CONTRACT_VERSION = "behavior-prompt/1.3"
SKILL_START = "<!-- BEHAVIOR_CAPTURE_SKILL_START -->"
SKILL_END = "<!-- BEHAVIOR_CAPTURE_SKILL_END -->"
REFERENCE_START = "<!-- BEHAVIOR_CAPTURE_VENUE_TEMPLATE_START -->"
REFERENCE_END = "<!-- BEHAVIOR_CAPTURE_VENUE_TEMPLATE_END -->"
SCENARIOS_START = "<!-- MODEL_VISIBLE_SCENARIOS_START -->"
SCENARIOS_END = "<!-- MODEL_VISIBLE_SCENARIOS_END -->"
MODEL_VISIBLE_SCENARIO_KEYS = {"id", "situation", "context"}
ORACLE_SCENARIO_KEYS = {
    "required_all_actions",
    "required_any_actions",
    "optional_actions",
    "prohibited_actions",
    "required_dimensions",
    "prohibited_dimensions",
    "required_scopes",
    "prohibited_scopes",
    "required_side_effects",
    "prohibited_side_effects",
    "question",
    "update_rules",
    "readiness_rules",
}
RESPONSE_FIELDS = {
    "scenario_id",
    "selected_actions",
    "target_dimensions",
    "target_scopes",
    "updates",
    "readiness_updates",
    "question",
    "side_effects",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def context_oracle_keys(value: Any, *, path: str = "context") -> list[str]:
    leaks: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key)
            if (
                key_text in ORACLE_SCENARIO_KEYS
                or key_text.startswith("required_")
                or key_text.startswith("prohibited_")
            ):
                leaks.append(f"{path}.{key_text}")
            leaks.extend(context_oracle_keys(item, path=f"{path}.{key_text}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            leaks.extend(context_oracle_keys(item, path=f"{path}[{index}]"))
    return leaks


def load_scenarios(path: Path) -> list[dict[str, Any]]:
    document = json.loads(path.read_text(encoding="utf-8"))
    scenarios = (
        document
        if isinstance(document, list)
        else document.get("scenarios", [])
        if isinstance(document, dict)
        else []
    )
    if not isinstance(scenarios, list) or not all(
        isinstance(item, dict)
        and isinstance(item.get("id"), str)
        and item["id"]
        and isinstance(item.get("situation"), str)
        and item["situation"]
        for item in scenarios
    ):
        raise ValueError(
            "scenario document must contain scenario objects with IDs and situations"
        )
    scenario_ids = [item["id"] for item in scenarios]
    if len(set(scenario_ids)) != len(scenario_ids):
        raise ValueError("scenario IDs must be unique")
    for item in scenarios:
        leaks = context_oracle_keys(item.get("context"))
        if leaks:
            raise ValueError(
                f"{item['id']}: context contains verifier-only oracle fields: {leaks}"
            )
    return scenarios


def model_visible_scenarios(
    scenarios: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "id": item["id"],
            "situation": item["situation"],
            "context": item.get("context"),
        }
        for item in scenarios
    ]


def model_visible_scenario_json(scenarios: list[dict[str, Any]]) -> str:
    return json.dumps(
        {"scenarios": model_visible_scenarios(scenarios)},
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
    )


def response_vocabulary(scenarios: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    actions: set[str] = set()
    side_effects: set[str] = set()
    for scenario in scenarios:
        for key in (
            "required_all_actions",
            "required_any_actions",
            "optional_actions",
            "prohibited_actions",
        ):
            actions.update(str(value) for value in scenario.get(key, []))
        for key in ("required_side_effects", "prohibited_side_effects"):
            side_effects.update(str(value) for value in scenario.get(key, []))
    return sorted(actions), sorted(side_effects)


def build_output_schema(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    actions, side_effects = response_vocabulary(scenarios)
    scenario_ids = [item["id"] for item in scenarios]
    update_properties: dict[str, Any] = {
        "record_kind": {"type": "string"},
        "record_id": {"type": ["string", "null"]},
        "operation": {"type": "string"},
        "analysis_mode": {
            "type": ["string", "null"],
            "enum": ["case_set", "exploratory", "distributional", None],
        },
        "target_kind": {"type": ["string", "null"]},
        "candidate_action": {"type": ["string", "null"]},
        "origin": {
            "type": ["string", "null"],
            "enum": [
                "artifact-observed",
                "owner-stated",
                "model-derived",
                "model-proposed",
                None,
            ],
        },
        "resolution": {
            "type": ["string", "null"],
            "enum": [
                "confirmed",
                "unresolved",
                "candidate",
                "accepted",
                "rejected",
                "stale",
                None,
            ],
        },
        "status": {
            "type": ["string", "null"],
            "enum": [
                "active",
                "inactive",
                "candidate",
                "blocked",
                "ready",
                "partial",
                "unsupported",
                "stale",
                "confirmed",
                "deferred",
                "rejected",
                None,
            ],
        },
        "support": {
            "type": ["string", "null"],
            "enum": [
                "evidence-supported",
                "evidence-partial",
                "evidence-unsupported",
                "not_applicable",
                None,
            ],
        },
        "locator": {"type": ["string", "null"]},
        "decision_pointer": {"type": ["string", "null"]},
        "reason": {"type": ["string", "null"]},
        "grounding": {"type": "array", "items": {"type": "string"}},
    }
    readiness_properties: dict[str, Any] = {
        "scope_id": {"type": "string"},
        "readiness": {
            "type": "string",
            "enum": ["writer-ready", "partial", "blocked", "deferred"],
        },
        "blocker": {"type": ["string", "null"]},
        "next_action": {"type": ["string", "null"]},
        "output_pointer": {"type": ["string", "null"]},
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "required": ["responses"],
        "properties": {
            "responses": {
                "type": "array",
                "minItems": len(scenario_ids),
                "maxItems": len(scenario_ids),
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": sorted(RESPONSE_FIELDS),
                    "properties": {
                        "scenario_id": {"enum": scenario_ids},
                        "selected_actions": {
                            "type": "array",
                            "items": {"enum": actions},
                        },
                        "target_dimensions": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "pattern": r"^D(?:0[0-9]|1[0-9])$",
                            },
                        },
                        "target_scopes": {
                            "type": "array",
                            "items": {"type": "string", "pattern": r"^SCOPE-"},
                        },
                        "updates": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "required": sorted(update_properties),
                                "properties": update_properties,
                            },
                        },
                        "readiness_updates": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "required": sorted(readiness_properties),
                                "properties": readiness_properties,
                            },
                        },
                        "question": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["count", "target"],
                            "properties": {
                                "count": {"type": "integer", "minimum": 0},
                                "target": {"type": ["string", "null"]},
                            },
                        },
                        "side_effects": {
                            "type": "array",
                            "items": {"enum": side_effects},
                        },
                    },
                },
            }
        },
    }


def marker_block(start: str, body: str, end: str) -> str:
    separator = "" if body.endswith("\n") else "\n"
    return f"{start}\n{body}{separator}{end}"


def build_prompt(
    skill_text: str,
    skill_sha256: str,
    reference_text: str,
    reference_sha256: str,
    scenarios: list[dict[str, Any]],
) -> str:
    expected_count = len(scenarios)
    actions, side_effects = response_vocabulary(scenarios)
    response_shape = {
        "scenario_id": "B00",
        "selected_actions": [],
        "target_dimensions": [],
        "target_scopes": [],
        "updates": [],
        "readiness_updates": [],
        "question": {"count": 0, "target": None},
        "side_effects": [],
    }
    return (
        f"Behavior capture contract: {PROMPT_CONTRACT_VERSION}\n"
        "Evaluate each model-visible scenario using the complete skill below. "
        "Return only one JSON object with exactly "
        f'{expected_count} response objects: {{"responses":[...]}}.\n'
        "Each response must use this structural shape; empty arrays are permitted:\n"
        + json.dumps(response_shape, ensure_ascii=False, sort_keys=True)
        + "\n"
        + "Use exact case-sensitive selected_actions tokens from: "
        + json.dumps(actions, ensure_ascii=False)
        + ".\nUse exact side_effects tokens from: "
        + json.dumps(side_effects, ensure_ascii=False)
        + ". target_dimensions may contain only D00-D19 IDs; target_scopes may contain only explicit SCOPE-* IDs from the scenario context. "
        "updates and readiness_updates must contain JSON objects, never prose strings. Each update object should name record_kind and operation plus the relevant changed field; each readiness object should name scope_id and readiness when applicable.\n"
        "The output schema requires every update/readiness object key; use null or an empty grounding array for non-applicable values rather than omitting keys.\n"
        f"SKILL SHA-256: {skill_sha256}\n"
        + marker_block(SKILL_START, skill_text, SKILL_END)
        + "\n"
        f"VENUE-TEMPLATE REFERENCE SHA-256: {reference_sha256}\n"
        + marker_block(REFERENCE_START, reference_text, REFERENCE_END)
        + "\n"
        "The following projection is the entire model-visible scenario payload. "
        "Policy requirements and prohibited-answer oracle fields are intentionally absent.\n"
        + marker_block(
            SCENARIOS_START,
            model_visible_scenario_json(scenarios),
            SCENARIOS_END,
        )
        + "\n"
    )


def prompt_contract_errors(
    prompt: str,
    skill_text: str,
    reference_text: str,
    scenarios: list[dict[str, Any]],
) -> list[str]:
    errors: list[str] = []
    expected_skill_block = marker_block(SKILL_START, skill_text, SKILL_END)
    if expected_skill_block not in prompt:
        errors.append("prompt does not contain the complete current SKILL.md body")
    expected_skill_hash = sha_text(skill_text)
    if f"SKILL SHA-256: {expected_skill_hash}" not in prompt:
        errors.append("prompt SKILL SHA-256 does not match the embedded skill body")
    expected_reference_block = marker_block(
        REFERENCE_START, reference_text, REFERENCE_END
    )
    if expected_reference_block not in prompt:
        errors.append(
            "prompt does not contain the complete current venue-template reference"
        )
    expected_reference_hash = sha_text(reference_text)
    if f"VENUE-TEMPLATE REFERENCE SHA-256: {expected_reference_hash}" not in prompt:
        errors.append(
            "prompt venue-template SHA-256 does not match the embedded reference"
        )
    scenario_match = re.search(
        re.escape(SCENARIOS_START) + r"\n(.*?)\n" + re.escape(SCENARIOS_END),
        prompt,
        re.DOTALL,
    )
    if not scenario_match:
        errors.append("prompt model-visible scenario block is missing")
        return errors
    try:
        visible_document = json.loads(scenario_match.group(1))
    except json.JSONDecodeError as exc:
        errors.append(f"prompt model-visible scenario JSON is invalid: {exc}")
        return errors
    expected_visible = model_visible_scenarios(scenarios)
    visible = (
        visible_document.get("scenarios")
        if isinstance(visible_document, dict)
        else None
    )
    if visible != expected_visible:
        errors.append("prompt model-visible scenarios do not match current projection")
    if not isinstance(visible, list):
        errors.append("prompt model-visible scenarios must be an array")
        return errors
    for item in visible:
        if not isinstance(item, dict):
            errors.append("prompt model-visible scenario must be an object")
            continue
        leaked = set(item) & ORACLE_SCENARIO_KEYS
        unexpected = set(item) - MODEL_VISIBLE_SCENARIO_KEYS
        missing = MODEL_VISIBLE_SCENARIO_KEYS - set(item)
        if leaked:
            errors.append(f"prompt leaks scenario oracle fields: {sorted(leaked)}")
        if unexpected:
            errors.append(
                f"prompt exposes unexpected scenario fields: {sorted(unexpected)}"
            )
        if missing:
            errors.append(
                f"prompt omits model-visible scenario fields: {sorted(missing)}"
            )
    return errors


def extract(raw: str | Path) -> dict[str, Any]:
    text = Path(raw).read_text(encoding="utf-8")
    match = re.search(r'\{\s*"responses"\s*:\s*\[.*\]\s*\}', text, re.DOTALL)
    if not match:
        raise ValueError("raw output must contain top-level responses JSON")
    document = json.loads(match.group(0))
    if set(document) != {"responses"}:
        raise ValueError("capture document must contain only responses")
    return document


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["init", "finalize"])
    parser.add_argument("--capture", required=True)
    parser.add_argument("--model", default="unknown")
    parser.add_argument("--runtime", default="unknown")
    parser.add_argument("--skill", default="skills/yxj-paper-os/SKILL.md")
    parser.add_argument(
        "--scenarios",
        default="skills/yxj-paper-os/assets/evals/behavior-scenarios.json",
    )
    args = parser.parse_args()

    capture = Path(args.capture)
    capture.mkdir(parents=True, exist_ok=True)
    skill_path = Path(args.skill)
    reference_path = skill_path.parent / "references/lenses/venue-template.md"
    scenario_path = Path(args.scenarios)
    skill_text = skill_path.read_text(encoding="utf-8")
    reference_text = reference_path.read_text(encoding="utf-8")
    scenarios = load_scenarios(scenario_path)
    scenario_ids = [item["id"] for item in scenarios]
    expected_count = len(scenario_ids)
    prompt_path = capture / "prompt.md"
    output_schema_path = capture / "output-schema.json"

    if args.command == "init":
        prompt_path.write_text(
            build_prompt(
                skill_text,
                sha(skill_path),
                reference_text,
                sha(reference_path),
                scenarios,
            ),
            encoding="utf-8",
        )
        output_schema_path.write_text(
            json.dumps(
                build_output_schema(scenarios),
                ensure_ascii=False,
                sort_keys=True,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print(prompt_path)
        return 0

    prompt_errors = prompt_contract_errors(
        prompt_path.read_text(encoding="utf-8"),
        skill_text,
        reference_text,
        scenarios,
    )
    if prompt_errors:
        raise ValueError("; ".join(prompt_errors))
    expected_output_schema = (
        json.dumps(
            build_output_schema(scenarios),
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        )
        + "\n"
    )
    if output_schema_path.read_text(encoding="utf-8") != expected_output_schema:
        raise ValueError(
            "output-schema.json does not match the current behavior contract"
        )
    raw = capture / "raw-output.md"
    document = extract(raw)
    responses = document.get("responses")
    if (
        not isinstance(responses, list)
        or len(responses) != expected_count
        or {
            response.get("scenario_id")
            for response in responses
            if isinstance(response, dict)
        }
        != set(scenario_ids)
    ):
        raise ValueError(
            f"capture must contain exactly {expected_count} unique response records matching scenario IDs"
        )
    if any(
        not isinstance(response, dict) or not RESPONSE_FIELDS.issubset(response)
        for response in responses
    ):
        raise ValueError("every response must match the response schema")

    actions_path = capture / "actions.json"
    actions_path.write_text(
        json.dumps(document, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    visible_json = model_visible_scenario_json(scenarios)
    manifest = {
        "prompt_contract_version": PROMPT_CONTRACT_VERSION,
        "model": args.model,
        "runtime": args.runtime,
        "captured_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "skill_sha256": sha(skill_path),
        "venue_template_sha256": sha(reference_path),
        "scenarios_sha256": sha(scenario_path),
        "model_visible_scenarios_sha256": sha_text(visible_json),
        "prompt_sha256": sha(prompt_path),
        "output_schema_sha256": sha(output_schema_path),
        "raw_output_sha256": sha(raw),
        "actions_sha256": sha(actions_path),
        "scenario_ids": [response.get("scenario_id") for response in responses],
        "scenario_count": expected_count,
    }
    (capture / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(capture / "manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
