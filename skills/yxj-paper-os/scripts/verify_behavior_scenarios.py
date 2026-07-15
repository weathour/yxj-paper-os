#!/usr/bin/env python3
"""Strict stdlib validator for schema-0.3 behavior fixtures and captures."""

from __future__ import annotations

import argparse
import datetime
import json
import re
from pathlib import Path
from typing import Any

from capture_behavior_actions import (
    MANIFEST_FIELDS,
    MANIFEST_HASH_FIELDS,
    PROMPT_CONTRACT_VERSION,
    build_output_schema,
    contains_visible_content,
    extract,
    load_json_text,
    load_scenarios,
    manuscript_prose_warnings,
    model_visible_scenario_json,
    prompt_contract_errors,
    response_contract_fingerprint,
    sha,
    sha_text,
    strict_response_document_errors,
    strict_response_errors,
)

ACTIONS = {"INSPECT", "DERIVE", "PROJECT", "ASK_OWNER", "VALIDATE"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def load(path: Path) -> Any:
    return load_json_text(path.read_text(encoding="utf-8"))


def validate_response(response: Any, policy: dict[str, dict[str, Any]]) -> list[str]:
    """Compatibility wrapper used by tests; structural and semantic checks are shared."""
    return strict_response_errors(response, list(policy.values()))


def validate_response_warnings(response: dict[str, Any]) -> list[str]:
    return manuscript_prose_warnings(response)


def manifest_errors(
    manifest: Any,
    *,
    capture: Path,
    skill_path: Path,
    reference_path: Path,
    scenario_path: Path,
    scenarios: list[dict[str, Any]],
    actions: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    if not isinstance(manifest, dict):
        return ["manifest must be an object"]
    missing = sorted(MANIFEST_FIELDS - set(manifest))
    extra = sorted(set(manifest) - MANIFEST_FIELDS)
    if missing:
        errors.append(f"manifest missing fields {missing}")
    if extra:
        errors.append(f"manifest unexpected fields {extra}")
    if missing or extra:
        return errors

    for field in (
        "prompt_contract_version",
        "capture_kind",
        "model",
        "runtime",
        "captured_at",
    ):
        if not contains_visible_content(manifest[field]):
            errors.append(f"manifest {field} must be a non-empty string")
    if manifest["prompt_contract_version"] != PROMPT_CONTRACT_VERSION:
        errors.append("manifest prompt_contract_version is stale")
    if manifest["capture_kind"] not in ("offline_policy_fixture", "live_model"):
        errors.append("manifest capture_kind is invalid")
    if manifest["capture_kind"] == "offline_policy_fixture":
        if manifest["model"] != "policy-fixture":
            errors.append("offline fixture model label is invalid")
        if manifest["runtime"] != "offline-reproducible-fixture":
            errors.append("offline fixture runtime label is invalid")
    if manifest["capture_kind"] == "live_model":
        if not contains_visible_content(manifest["model"]) or manifest["model"] in (
            "unknown",
            "policy-fixture",
        ):
            errors.append("live capture model provenance is invalid")
        if not contains_visible_content(manifest["runtime"]) or manifest["runtime"] in (
            "unknown",
            "offline-reproducible-fixture",
        ):
            errors.append("live capture runtime provenance is invalid")
    if (
        "fixture-current" in capture.parts
        and manifest["capture_kind"] != "offline_policy_fixture"
    ):
        errors.append("fixture-current must use offline_policy_fixture provenance")
    try:
        captured_at = datetime.datetime.fromisoformat(manifest["captured_at"])
        if captured_at.tzinfo is None:
            errors.append("manifest captured_at must include a timezone")
    except (TypeError, ValueError):
        errors.append("manifest captured_at is not ISO-8601")

    for field in MANIFEST_HASH_FIELDS:
        if not isinstance(manifest[field], str) or not SHA256_RE.fullmatch(
            manifest[field]
        ):
            errors.append(f"manifest {field} must be lowercase SHA-256")
    if not isinstance(manifest["scenario_count"], int) or isinstance(
        manifest["scenario_count"], bool
    ):
        errors.append("manifest scenario_count must be an integer")
    if not isinstance(manifest["scenario_ids"], list) or not all(
        isinstance(value, str) for value in manifest["scenario_ids"]
    ):
        errors.append("manifest scenario_ids must be a string array")

    expected_ids = [response["scenario_id"] for response in actions["responses"]]
    expected = {
        "skill_sha256": sha(skill_path),
        "venue_template_sha256": sha(reference_path),
        "scenarios_sha256": sha(scenario_path),
        "model_visible_scenarios_sha256": sha_text(
            model_visible_scenario_json(scenarios)
        ),
        "prompt_sha256": sha(capture / "prompt.md"),
        "output_schema_sha256": sha(capture / "output-schema.json"),
        "response_contract_sha256": response_contract_fingerprint(scenarios),
        "raw_output_sha256": sha(capture / "raw-output.md"),
        "actions_sha256": sha(capture / "actions.json"),
        "scenario_ids": expected_ids,
        "scenario_count": len(expected_ids),
    }
    for field, expected_value in expected.items():
        if manifest.get(field) != expected_value:
            errors.append(f"manifest mismatch {field}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate schema-0.3 behavior policy fixtures or a recorded capture."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="skills/yxj-paper-os/assets/evals/behavior-scenarios.json",
    )
    parser.add_argument("--capture")
    parser.add_argument("--skill", default="skills/yxj-paper-os/SKILL.md")
    args = parser.parse_args()

    scenario_path = Path(args.path)
    try:
        scenarios = load_scenarios(scenario_path)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"behavior scenario document is invalid: {exc}")
        return 1
    if not args.capture:
        print("behavior scenarios valid")
        return 0

    errors: list[str] = []
    warnings: list[str] = []
    capture = Path(args.capture)
    skill_path = Path(args.skill)
    reference_path = skill_path.parent / "references/lenses/venue-template.md"
    try:
        prompt_text = (capture / "prompt.md").read_text(encoding="utf-8")
        skill_text = skill_path.read_text(encoding="utf-8")
        reference_text = reference_path.read_text(encoding="utf-8")
        errors.extend(
            prompt_contract_errors(prompt_text, skill_text, reference_text, scenarios)
        )
        expected_schema = (
            json.dumps(
                build_output_schema(scenarios),
                ensure_ascii=False,
                sort_keys=True,
                indent=2,
                allow_nan=False,
            )
            + "\n"
        )
        if (capture / "output-schema.json").read_text(
            encoding="utf-8"
        ) != expected_schema:
            errors.append("output-schema.json does not match current behavior contract")
        actions = load(capture / "actions.json")
        raw_document = extract(capture / "raw-output.md")
        if raw_document != actions:
            errors.append("raw-output/actions normalized equality failed")
        errors.extend(strict_response_document_errors(actions, scenarios))
        if isinstance(actions, dict) and isinstance(actions.get("responses"), list):
            for response in actions["responses"]:
                if isinstance(response, dict):
                    warnings.extend(manuscript_prose_warnings(response))
        manifest = load(capture / "manifest.json")
        errors.extend(
            manifest_errors(
                manifest,
                capture=capture,
                skill_path=skill_path,
                reference_path=reference_path,
                scenario_path=scenario_path,
                scenarios=scenarios,
                actions=actions,
            )
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        errors.append(f"cannot validate capture: {exc}")

    if errors:
        print("\n".join(errors))
        return 1
    for warning in warnings:
        print(f"warning: {warning}")
    print("behavior scenarios valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
