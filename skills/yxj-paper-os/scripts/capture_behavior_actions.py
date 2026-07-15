#!/usr/bin/env python3
"""Create oracle-free schema-0.3 behavior prompts and finalize captures."""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import math
import re
import unicodedata
from pathlib import Path
from typing import Any

PROMPT_CONTRACT_VERSION = "behavior-prompt/2.1"
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
    "allowed_dimensions",
    "required_dimensions",
    "prohibited_dimensions",
    "allowed_scopes",
    "required_scopes",
    "prohibited_scopes",
    "required_side_effects",
    "optional_side_effects",
    "prohibited_side_effects",
    "question",
    "update_rules",
    "readiness_rules",
    "non_null_fields",
    "response_limits",
    "gate_category",
    "correct_action",
    "expected_action",
    "migration_contract",
    "semantic_limit",
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
RECORD_KIND_ALIASES = {
    "material_record": "material",
    "template_metric_observation": "material",
    "template_analysis": "template_analysis",
    "writing_design_rule": "design_rule",
    "template_design_profile": "design_rule",
    "writing_design_proposal": "design_rule",
    "design_profile": "design_rule",
    "claim_record": "claim",
    "decision_record": "decision",
}
MANIFEST_HASH_FIELDS = {
    "skill_sha256",
    "venue_template_sha256",
    "scenarios_sha256",
    "model_visible_scenarios_sha256",
    "prompt_sha256",
    "output_schema_sha256",
    "response_contract_sha256",
    "raw_output_sha256",
    "actions_sha256",
}
MANIFEST_FIELDS = {
    "prompt_contract_version",
    "capture_kind",
    "model",
    "runtime",
    "captured_at",
    *MANIFEST_HASH_FIELDS,
    "scenario_ids",
    "scenario_count",
}
UPDATE_FIELDS = {
    "record_kind",
    "record_id",
    "operation",
    "analysis_mode",
    "target_kind",
    "candidate_action",
    "origin",
    "resolution",
    "status",
    "support",
    "locator",
    "decision_pointer",
    "reason",
    "grounding",
    "epistemic_label",
    "design_only_state",
    "schema_version",
    "gate_category",
    "role",
    "access_state",
    "partition",
    "missingness",
    "denominator",
    "effective_conclusion",
    "promotion_pointer",
    "design_payload",
    "linked_records",
}
READINESS_FIELDS = {
    "scope_id",
    "readiness",
    "blocker",
    "next_action",
    "output_pointer",
}
QUESTION_FIELDS = {"count", "target"}
UPDATE_FREE_TEXT_FIELDS = {"reason", "design_payload"}
UPDATE_SELECTOR_FIELDS = {"record_kind"}
UPDATE_STRUCTURED_FIELDS = UPDATE_FIELDS - UPDATE_FREE_TEXT_FIELDS
UPDATE_ARRAY_FIELDS = {"grounding", "linked_records"}
READINESS_SELECTOR_FIELDS = {"scope_id"}
READINESS_STRUCTURED_FIELDS = set(READINESS_FIELDS)
OPERATIONS = {"create", "revise"}
RECORD_ID_PATTERNS = {
    "paragraph": re.compile(r"^P-[A-Z0-9][A-Z0-9-]*$"),
    "frame": re.compile(r"^FRM-[A-Z0-9][A-Z0-9-]*$"),
    "template_rule": re.compile(r"^TRULE-[A-Z0-9][A-Z0-9-]*$"),
    "decision": re.compile(r"^DEC-[A-Z0-9][A-Z0-9-]*$"),
    "template_source": re.compile(r"^TPL-[A-Z0-9][A-Z0-9-]*$"),
    "claim": re.compile(r"^C-[A-Z0-9][A-Z0-9-]*$"),
    "semantic_dossier": re.compile(r"^DOSSIER-[A-Z0-9][A-Z0-9-]*$"),
    "template_analysis": re.compile(r"^ANALYSIS-[A-Z0-9][A-Z0-9-]*$"),
    "visual": re.compile(r"^VIS-[A-Z0-9][A-Z0-9-]*$"),
    "diagnostic": re.compile(r"^SCHEMA_[A-Z0-9_]+$"),
    "surface": re.compile(r"^SURFACE-[A-Z0-9][A-Z0-9-]*$"),
    "material": re.compile(r"^M-[A-Z0-9][A-Z0-9-]*$"),
}
SCOPE_ID_PATTERN = re.compile(r"^SCOPE-[A-Z0-9][A-Z0-9-]*$")
PUBLIC_POINTER_PATTERN = re.compile(
    r"^(?P<filename>[0-9]{2}_[A-Z0-9_]+\.md)#(?P<anchor>[^\s#]+)$"
)
ID_POINTER_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]*(?:-[A-Z0-9_]+)+$")
SCENARIO_ID_PATTERN = re.compile(r"^B[0-9]{2}$")
DIMENSION_ID_PATTERN = re.compile(r"^D(?:0[0-9]|1[0-9])$")
ACTION_VALUES = {"INSPECT", "DERIVE", "PROJECT", "ASK_OWNER", "VALIDATE"}
SIDE_EFFECT_VALUES = {
    "external_execution",
    "full_scan",
    "pdf_pseudo_parse",
    "subagents",
    "template_analysis",
    "template_intake",
}
GATE_VALUES = {
    "scientific_commitment",
    "argument_spine",
    "material_local_tradeoff",
    "deliberate_divergence",
}
SCENARIO_FIELDS = {
    "id",
    "situation",
    "context",
    "required_all_actions",
    "required_any_actions",
    "optional_actions",
    "prohibited_actions",
    "required_dimensions",
    "allowed_dimensions",
    "prohibited_dimensions",
    "required_scopes",
    "allowed_scopes",
    "prohibited_scopes",
    "question",
    "required_side_effects",
    "optional_side_effects",
    "prohibited_side_effects",
    "update_rules",
    "readiness_rules",
    "response_limits",
}
SCENARIO_QUESTION_FIELDS = {"min_count", "max_count", "allowed_targets"}
RESPONSE_LIMIT_FIELDS = {
    "min_updates",
    "max_updates",
    "min_readiness_updates",
    "max_readiness_updates",
}
POSITIVE_UPDATE_RULE_FIELDS = {
    "record_kind",
    "min_count",
    "max_count",
    "allowed_fields",
    "non_null_fields",
    "exact_fields",
}
NEGATIVE_UPDATE_RULE_FIELDS = {
    "record_kind",
    "min_count",
    "max_count",
    "allowed_fields",
}
POSITIVE_READINESS_RULE_FIELDS = {
    "scope_id",
    "min_count",
    "max_count",
    "allowed_fields",
    "non_null_fields",
    "exact_fields",
}
NEGATIVE_READINESS_RULE_FIELDS = {
    "scope_id",
    "min_count",
    "max_count",
    "allowed_fields",
}
UPDATE_ENUM_DOMAINS = {
    "analysis_mode": {"case_set", "exploratory", "distributional"},
    "origin": {"artifact-observed", "owner-stated", "model-derived", "model-proposed"},
    "resolution": {
        "confirmed",
        "unresolved",
        "candidate",
        "accepted",
        "rejected",
        "stale",
    },
    "status": {
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
    },
    "support": {
        "evidence-supported",
        "evidence-partial",
        "evidence-unsupported",
        "not_applicable",
    },
    "epistemic_label": {
        "artifact-observed",
        "owner-stated",
        "model-derived",
        "model-proposed",
    },
    "design_only_state": {"design_only", "not_applicable"},
    "schema_version": {"0.2", "0.3"},
    "gate_category": GATE_VALUES,
}
READINESS_VALUES = {"writer-ready", "partial", "blocked", "deferred"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def reject_duplicate_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Build one JSON object while rejecting last-key-wins ambiguity."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def reject_nonfinite_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant is forbidden: {value}")


def parse_finite_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError(f"non-finite JSON number is forbidden: {value}")
    return parsed


def load_json_text(text: str) -> Any:
    """Parse strict JSON without duplicate keys or non-finite numbers."""
    return json.loads(
        text,
        object_pairs_hook=reject_duplicate_object_pairs,
        parse_constant=reject_nonfinite_constant,
        parse_float=parse_finite_float,
    )


def context_oracle_keys(value: Any, *, path: str = "context") -> list[str]:
    leaks: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key)
            if key_text in ORACLE_SCENARIO_KEYS or key_text.startswith(
                ("required_", "prohibited_")
            ):
                leaks.append(f"{path}.{key_text}")
            leaks.extend(context_oracle_keys(item, path=f"{path}.{key_text}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            leaks.extend(context_oracle_keys(item, path=f"{path}[{index}]"))
    return leaks


def contains_visible_content(value: Any) -> bool:
    """Return whether text contains a language-neutral visible code point."""
    return isinstance(value, str) and any(
        not char.isspace() and unicodedata.category(char)[0] not in {"C", "Z"}
        for char in value
    )


def nonblank(value: Any) -> bool:
    return contains_visible_content(value)


def parse_public_pointer(value: Any) -> tuple[str, str] | None:
    if not isinstance(value, str):
        return None
    match = PUBLIC_POINTER_PATTERN.fullmatch(value)
    if match is None:
        return None
    filename = match.group("filename")
    anchor = match.group("anchor")
    if not contains_visible_content(anchor) or any(
        unicodedata.category(char)[0] in {"C", "Z"} for char in anchor
    ):
        return None
    return filename, anchor


def valid_public_pointer(value: Any) -> bool:
    return parse_public_pointer(value) is not None


def valid_pointer(value: Any) -> bool:
    return valid_public_pointer(value) or (
        isinstance(value, str) and ID_POINTER_PATTERN.fullmatch(value) is not None
    )


def valid_bound_pair(mapping: dict[str, Any], minimum: str, maximum: str) -> bool:
    lower = mapping.get(minimum)
    upper = mapping.get(maximum)
    return (
        isinstance(lower, int)
        and not isinstance(lower, bool)
        and lower >= 0
        and isinstance(upper, int)
        and not isinstance(upper, bool)
        and upper >= 0
        and lower <= upper
    )


def valid_unique_string_array(
    value: Any,
    *,
    allowed: set[str] | None = None,
    pattern: re.Pattern[str] | None = None,
) -> bool:
    return (
        isinstance(value, list)
        and all(
            isinstance(item, str)
            and contains_visible_content(item)
            and (allowed is None or item in allowed)
            and (pattern is None or pattern.fullmatch(item) is not None)
            for item in value
        )
        and len(value) == len(set(value))
    )


def allowed_value_is_valid(field: str, value: Any, record_kind: str) -> bool:
    if not isinstance(value, str) or not contains_visible_content(value):
        return False
    if field == "record_id":
        return RECORD_ID_PATTERNS[record_kind].fullmatch(value) is not None
    if field == "operation":
        return value in OPERATIONS
    if field in UPDATE_ENUM_DOMAINS:
        return value in UPDATE_ENUM_DOMAINS[field]
    if field in {"decision_pointer", "promotion_pointer"}:
        return valid_pointer(value)
    return True


def validate_rule_contract(
    scenario_id: str, rule: Any, rule_key: str
) -> tuple[str, set[str]] | None:
    if not isinstance(rule, dict) or not valid_bound_pair(
        rule, "min_count", "max_count"
    ):
        raise ValueError(f"{scenario_id}: {rule_key} has invalid cardinality")
    if rule["min_count"] != rule["max_count"]:
        raise ValueError(f"{scenario_id}: {rule_key} cardinality must be exact")
    positive = rule["max_count"] > 0
    if positive and rule["min_count"] == 0:
        raise ValueError(f"{scenario_id}: positive {rule_key} rule must be required")
    if not positive and rule["min_count"] != 0:
        raise ValueError(f"{scenario_id}: negative {rule_key} rule must be 0..0")

    update_rule = rule_key == "update_rules"
    expected_fields = (
        POSITIVE_UPDATE_RULE_FIELDS
        if update_rule and positive
        else NEGATIVE_UPDATE_RULE_FIELDS
        if update_rule
        else POSITIVE_READINESS_RULE_FIELDS
        if positive
        else NEGATIVE_READINESS_RULE_FIELDS
    )
    if set(rule) != expected_fields:
        raise ValueError(f"{scenario_id}: {rule_key} fields differ from contract")

    selector_field = "record_kind" if update_rule else "scope_id"
    selector = rule.get(selector_field)
    if update_rule:
        if selector not in RECORD_ID_PATTERNS:
            raise ValueError(
                f"{scenario_id}: update rule lacks a canonical record-kind selector"
            )
        permitted_fields = UPDATE_FIELDS
        structured_fields = UPDATE_STRUCTURED_FIELDS
        selector_fields = UPDATE_SELECTOR_FIELDS
    else:
        if (
            not isinstance(selector, str)
            or SCOPE_ID_PATTERN.fullmatch(selector) is None
        ):
            raise ValueError(
                f"{scenario_id}: readiness rule lacks a canonical scope selector"
            )
        permitted_fields = READINESS_FIELDS
        structured_fields = READINESS_STRUCTURED_FIELDS
        selector_fields = READINESS_SELECTOR_FIELDS
    identity_field = "record_id" if update_rule else "readiness"
    if not positive:
        allowed_fields = rule["allowed_fields"]
        if (
            not isinstance(allowed_fields, dict)
            or selector_field in allowed_fields
            or not set(allowed_fields).issubset(permitted_fields)
            or set(allowed_fields).intersection(UPDATE_FREE_TEXT_FIELDS)
        ):
            raise ValueError(
                f"{scenario_id}: negative {rule_key} has invalid allowed fields"
            )
        for field, values in allowed_fields.items():
            if (
                not isinstance(values, list)
                or not values
                or len(values)
                != len(
                    {
                        json.dumps(
                            value,
                            ensure_ascii=False,
                            sort_keys=True,
                            allow_nan=False,
                        )
                        for value in values
                    }
                )
            ):
                raise ValueError(
                    f"{scenario_id}: negative {rule_key} has invalid allowed values"
                )
            if update_rule:
                valid = all(
                    allowed_value_is_valid(field, value, str(selector))
                    for value in values
                )
            else:
                valid = all(
                    isinstance(value, str)
                    and contains_visible_content(value)
                    and (field != "readiness" or value in READINESS_VALUES)
                    and (field != "output_pointer" or valid_public_pointer(value))
                    for value in values
                )
            if not valid:
                raise ValueError(
                    f"{scenario_id}: negative {rule_key} has invalid allowed values"
                )
        return None

    non_null_fields = rule["non_null_fields"]
    allowed_fields = rule["allowed_fields"]
    exact_fields = rule["exact_fields"]
    if (
        not valid_unique_string_array(non_null_fields)
        or not non_null_fields
        or not set(non_null_fields).issubset(permitted_fields)
        or selector_field not in non_null_fields
        or not isinstance(allowed_fields, dict)
        or not set(allowed_fields).issubset(non_null_fields)
        or identity_field not in allowed_fields
        or selector_field in allowed_fields
        or set(allowed_fields).intersection(UPDATE_FREE_TEXT_FIELDS)
        or not valid_unique_string_array(exact_fields)
        or not set(exact_fields).issubset(permitted_fields)
    ):
        raise ValueError(
            f"{scenario_id}: positive {rule_key} rule lacks a closed field contract"
        )
    for field, values in allowed_fields.items():
        if (
            not isinstance(values, list)
            or not values
            or len(values)
            != len(
                {
                    json.dumps(
                        value,
                        ensure_ascii=False,
                        sort_keys=True,
                        allow_nan=False,
                    )
                    for value in values
                }
            )
        ):
            raise ValueError(
                f"{scenario_id}: {rule_key} allowed values must be unique arrays"
            )
        if update_rule:
            if not all(
                allowed_value_is_valid(field, value, selector) for value in values
            ):
                raise ValueError(
                    f"{scenario_id}: update rule has an invalid allowed {field} value"
                )
        elif not all(
            isinstance(value, str)
            and contains_visible_content(value)
            and (field != "readiness" or value in READINESS_VALUES)
            and (field != "output_pointer" or valid_public_pointer(value))
            for value in values
        ):
            raise ValueError(
                f"{scenario_id}: readiness rule has an invalid allowed {field} value"
            )
        if field not in exact_fields and len(values) != 1:
            raise ValueError(
                f"{scenario_id}: positive scalar {rule_key} values must be singleton"
            )

    active_fields = set(non_null_fields)
    unconstrained = (
        active_fields.intersection(structured_fields)
        - selector_fields
        - set(allowed_fields)
    )
    if unconstrained:
        raise ValueError(
            f"{scenario_id}: positive {rule_key} rule has unconstrained structured fields {sorted(unconstrained)}"
        )
    expected_exact = (
        active_fields.intersection(UPDATE_ARRAY_FIELDS) if update_rule else set()
    )
    if set(exact_fields) != expected_exact:
        raise ValueError(
            f"{scenario_id}: {rule_key} exact_fields must equal active arrays"
        )

    identity_values = (
        set(allowed_fields["record_id"])
        if update_rule
        else set(allowed_fields["readiness"])
    )
    return str(selector), identity_values


def load_scenarios(path: Path) -> list[dict[str, Any]]:
    document = load_json_text(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict) or set(document) != {"scenarios"}:
        raise ValueError("scenario document must contain only the scenarios array")
    scenarios = document["scenarios"]
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("scenario document must contain scenario objects")

    scenario_ids: list[str] = []
    for index, item in enumerate(scenarios):
        if not isinstance(item, dict) or set(item) != SCENARIO_FIELDS:
            raise ValueError(f"scenario {index} fields differ from contract")
        scenario_id = item.get("id")
        if (
            not isinstance(scenario_id, str)
            or SCENARIO_ID_PATTERN.fullmatch(scenario_id) is None
            or scenario_id in scenario_ids
            or not contains_visible_content(item.get("situation"))
            or not isinstance(item.get("context"), dict)
        ):
            raise ValueError(f"scenario {index} has invalid identity, text, or context")
        scenario_ids.append(scenario_id)
        leaks = context_oracle_keys(item["context"])
        if leaks:
            raise ValueError(
                f"{scenario_id}: context contains verifier-only oracle fields: {leaks}"
            )

        action_keys = (
            "required_all_actions",
            "required_any_actions",
            "optional_actions",
            "prohibited_actions",
        )
        if any(
            not valid_unique_string_array(item[key], allowed=ACTION_VALUES)
            for key in action_keys
        ):
            raise ValueError(f"{scenario_id}: action arrays are invalid")
        required_all, required_any, optional, prohibited = (
            set(item[key]) for key in action_keys
        )
        allowed_actions = required_all | required_any | optional
        if (
            required_all.intersection(required_any | optional)
            or required_any.intersection(optional)
            or allowed_actions.intersection(prohibited)
        ):
            raise ValueError(f"{scenario_id}: action sets overlap or are incomplete")

        for label, required_key, allowed_key, prohibited_key, pattern in (
            (
                "dimension",
                "required_dimensions",
                "allowed_dimensions",
                "prohibited_dimensions",
                DIMENSION_ID_PATTERN,
            ),
            (
                "scope",
                "required_scopes",
                "allowed_scopes",
                "prohibited_scopes",
                SCOPE_ID_PATTERN,
            ),
        ):
            if any(
                not valid_unique_string_array(item[key], pattern=pattern)
                for key in (required_key, allowed_key, prohibited_key)
            ):
                raise ValueError(f"{scenario_id}: {label} arrays are invalid")
            required = set(item[required_key])
            allowed = set(item[allowed_key])
            prohibited_values = set(item[prohibited_key])
            if not required.issubset(allowed) or allowed.intersection(
                prohibited_values
            ):
                raise ValueError(f"{scenario_id}: {label} set relations are invalid")
            if label == "scope":
                visible_scope_values = item["context"].get("scope_ids")
                if not valid_unique_string_array(
                    visible_scope_values, pattern=SCOPE_ID_PATTERN
                ) or not allowed.issubset(set(visible_scope_values)):
                    raise ValueError(
                        f"{scenario_id}: allowed scopes must be model-visible"
                    )

        side_effect_keys = (
            "required_side_effects",
            "optional_side_effects",
            "prohibited_side_effects",
        )
        if any(
            not valid_unique_string_array(item[key], allowed=SIDE_EFFECT_VALUES)
            for key in side_effect_keys
        ):
            raise ValueError(f"{scenario_id}: side-effect arrays are invalid")
        required_effects, optional_effects, prohibited_effects = (
            set(item[key]) for key in side_effect_keys
        )
        if required_effects.intersection(optional_effects) or (
            required_effects | optional_effects
        ).intersection(prohibited_effects):
            raise ValueError(f"{scenario_id}: side-effect sets overlap")

        question = item["question"]
        if (
            not isinstance(question, dict)
            or set(question) != SCENARIO_QUESTION_FIELDS
            or not valid_bound_pair(question, "min_count", "max_count")
            or question["min_count"] != question["max_count"]
            or question["max_count"] > 1
            or not valid_unique_string_array(
                question["allowed_targets"], allowed=GATE_VALUES
            )
            or (question["max_count"] == 0 and bool(question["allowed_targets"]))
            or (question["max_count"] == 1 and len(question["allowed_targets"]) != 1)
        ):
            raise ValueError(f"{scenario_id}: question contract is invalid")
        action_membership = {key for key in action_keys if "ASK_OWNER" in item[key]}
        if question["max_count"] == 1:
            if action_membership != {"required_all_actions"}:
                raise ValueError(
                    f"{scenario_id}: one question requires ASK_OWNER exactly"
                )
        elif action_membership != {"prohibited_actions"}:
            raise ValueError(
                f"{scenario_id}: zero questions must prohibit ASK_OWNER exactly"
            )

        limits = item["response_limits"]
        if (
            not isinstance(limits, dict)
            or set(limits) != RESPONSE_LIMIT_FIELDS
            or not valid_bound_pair(limits, "min_updates", "max_updates")
            or not valid_bound_pair(
                limits, "min_readiness_updates", "max_readiness_updates"
            )
            or limits["min_updates"] != limits["max_updates"]
            or limits["min_readiness_updates"] != limits["max_readiness_updates"]
        ):
            raise ValueError(f"{scenario_id}: response limits are invalid")

        positive_identities: dict[str, list[tuple[str, set[str]]]] = {
            "update_rules": [],
            "readiness_rules": [],
        }
        cardinalities: dict[str, tuple[int, int]] = {}
        for rule_key in ("update_rules", "readiness_rules"):
            rules = item[rule_key]
            if not isinstance(rules, list) or not rules:
                raise ValueError(f"{scenario_id}: {rule_key} must contain objects")
            for rule in rules:
                identity = validate_rule_contract(scenario_id, rule, rule_key)
                if identity is None:
                    continue
                selector, values = identity
                for prior_selector, prior_values in positive_identities[rule_key]:
                    if selector == prior_selector and values.intersection(prior_values):
                        raise ValueError(
                            f"{scenario_id}: {rule_key} positive identities overlap"
                        )
                positive_identities[rule_key].append((selector, values))
            positive_rules = [rule for rule in rules if rule["max_count"] > 0]
            cardinalities[rule_key] = (
                sum(rule["min_count"] for rule in positive_rules),
                sum(rule["max_count"] for rule in positive_rules),
            )

        if cardinalities["update_rules"] != (
            limits["min_updates"],
            limits["max_updates"],
        ) or cardinalities["readiness_rules"] != (
            limits["min_readiness_updates"],
            limits["max_readiness_updates"],
        ):
            raise ValueError(
                f"{scenario_id}: response limits differ from positive rule cardinalities"
            )

        visible_scopes = set(item["context"]["scope_ids"])
        permitted_readiness_scopes = set(item["allowed_scopes"]) & visible_scopes
        if any(
            rule["scope_id"] not in permitted_readiness_scopes
            for rule in item["readiness_rules"]
        ):
            raise ValueError(
                f"{scenario_id}: readiness selector is not an allowed model-visible scope"
            )
        positive_readiness_selectors = [
            rule["scope_id"]
            for rule in item["readiness_rules"]
            if rule["max_count"] > 0
        ]
        target_scope_set = set(item["required_scopes"])
        if (
            len(positive_readiness_selectors) != len(set(positive_readiness_selectors))
            or target_scope_set != set(item["allowed_scopes"])
            or target_scope_set != visible_scopes
            or target_scope_set != set(positive_readiness_selectors)
        ):
            raise ValueError(
                f"{scenario_id}: positive readiness scopes must equal exact target scopes"
            )

        gate_categories = {
            category
            for rule in item["update_rules"]
            if rule["max_count"] > 0
            for category in rule["allowed_fields"].get("gate_category", [])
        }
        if gate_categories != set(question["allowed_targets"]):
            raise ValueError(
                f"{scenario_id}: gate-category authority differs from question target"
            )
    witness_errors = authority_witness_document_errors(scenarios)
    if witness_errors:
        raise ValueError(
            "scenario authority has no accepted deterministic witness: "
            + "; ".join(witness_errors)
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
        allow_nan=False,
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
        for key in (
            "required_side_effects",
            "optional_side_effects",
            "prohibited_side_effects",
        ):
            side_effects.update(str(value) for value in scenario.get(key, []))
    return sorted(actions), sorted(side_effects)


def build_output_schema(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    actions, side_effects = response_vocabulary(scenarios)
    scenario_ids = [item["id"] for item in scenarios]
    update_properties: dict[str, Any] = {
        "record_kind": {"type": "string", "enum": sorted(RECORD_ID_PATTERNS)},
        "record_id": {"type": ["string", "null"], "pattern": r"\S"},
        "operation": {"type": "string", "enum": sorted(OPERATIONS)},
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
        "locator": {"type": ["string", "null"], "pattern": r"\S"},
        "decision_pointer": {"type": ["string", "null"], "pattern": r"\S"},
        "reason": {"type": ["string", "null"], "pattern": r"\S"},
        "grounding": {
            "type": "array",
            "uniqueItems": True,
            "items": {"type": "string"},
        },
        "epistemic_label": {
            "type": ["string", "null"],
            "enum": [
                "artifact-observed",
                "owner-stated",
                "model-derived",
                "model-proposed",
                None,
            ],
        },
        "design_only_state": {
            "type": ["string", "null"],
            "enum": ["design_only", "not_applicable", None],
        },
        "schema_version": {
            "type": ["string", "null"],
            "enum": ["0.2", "0.3", None],
        },
        "gate_category": {
            "type": ["string", "null"],
            "enum": [
                "scientific_commitment",
                "argument_spine",
                "material_local_tradeoff",
                "deliberate_divergence",
                None,
            ],
        },
        "role": {"type": ["string", "null"]},
        "access_state": {"type": ["string", "null"]},
        "partition": {"type": ["string", "null"]},
        "missingness": {"type": ["string", "null"]},
        "denominator": {"type": ["string", "null"]},
        "effective_conclusion": {"type": ["string", "null"]},
        "promotion_pointer": {"type": ["string", "null"], "pattern": r"\S"},
        "design_payload": {"type": ["string", "null"], "pattern": r"\S"},
        "linked_records": {
            "type": "array",
            "uniqueItems": True,
            "items": {"type": "string"},
        },
    }
    readiness_properties: dict[str, Any] = {
        "scope_id": {
            "type": "string",
            "pattern": r"^SCOPE-[A-Z0-9][A-Z0-9-]*$",
        },
        "readiness": {
            "type": "string",
            "enum": ["writer-ready", "partial", "blocked", "deferred"],
        },
        "blocker": {"type": ["string", "null"], "pattern": r"\S"},
        "next_action": {"type": ["string", "null"], "pattern": r"\S"},
        "output_pointer": {
            "type": ["string", "null"],
            "pattern": r"^[0-9]{2}_[A-Z0-9_]+\.md#[^\s#]+$",
        },
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
                            "uniqueItems": True,
                            "items": {"enum": actions},
                        },
                        "target_dimensions": {
                            "type": "array",
                            "uniqueItems": True,
                            "items": {
                                "type": "string",
                                "pattern": r"^D(?:0[0-9]|1[0-9])$",
                            },
                        },
                        "target_scopes": {
                            "type": "array",
                            "uniqueItems": True,
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
                            "uniqueItems": True,
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
                            "uniqueItems": True,
                            "items": {"enum": side_effects},
                        },
                    },
                },
            }
        },
    }


def _json_type_matches(value: Any, expected: str) -> bool:
    if expected == "null":
        return value is None
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    return False


def _strict_schema_errors(
    value: Any, schema: dict[str, Any], *, path: str = "$"
) -> list[str]:
    """Validate the bounded JSON-Schema subset emitted by build_output_schema."""
    errors: list[str] = []
    expected_type = schema.get("type")
    if expected_type is not None:
        expected_types = (
            expected_type if isinstance(expected_type, list) else [expected_type]
        )
        if not any(_json_type_matches(value, item) for item in expected_types):
            return [f"{path}: expected type {expected_types}"]
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: value is outside enum")
    if isinstance(value, dict):
        properties = schema.get("properties", {})
        required = set(schema.get("required", []))
        missing = sorted(required - set(value))
        extra = sorted(set(value) - set(properties))
        if missing:
            errors.append(f"{path}: missing keys {missing}")
        if schema.get("additionalProperties") is False and extra:
            errors.append(f"{path}: unexpected keys {extra}")
        for key in sorted(set(value).intersection(properties)):
            errors.extend(
                _strict_schema_errors(value[key], properties[key], path=f"{path}.{key}")
            )
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: too few items")
        if len(value) > schema.get("maxItems", 10**9):
            errors.append(f"{path}: too many items")
        if schema.get("uniqueItems"):
            canonical = [
                json.dumps(item, sort_keys=True, ensure_ascii=False, allow_nan=False)
                for item in value
            ]
            if len(canonical) != len(set(canonical)):
                errors.append(f"{path}: duplicate items are not allowed")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                errors.extend(
                    _strict_schema_errors(item, item_schema, path=f"{path}[{index}]")
                )
    if isinstance(value, str) and schema.get("pattern"):
        if re.search(schema["pattern"], value) is None:
            errors.append(f"{path}: value does not match pattern")
    if isinstance(value, int) and not isinstance(value, bool):
        if value < schema.get("minimum", value):
            errors.append(f"{path}: value is below minimum")
    return errors


def schema_runtime_topology_errors(schema: dict[str, Any]) -> list[str]:
    """Bind generated schema topology to the stdlib runtime validator contract."""
    errors: list[str] = []
    try:
        response = schema["properties"]["responses"]["items"]
        update = response["properties"]["updates"]["items"]
        readiness = response["properties"]["readiness_updates"]["items"]
        question = response["properties"]["question"]
    except (KeyError, TypeError):
        return ["response schema topology is incomplete"]
    for label, node, expected in (
        ("response", response, RESPONSE_FIELDS),
        ("update", update, UPDATE_FIELDS),
        ("readiness", readiness, READINESS_FIELDS),
        ("question", question, QUESTION_FIELDS),
    ):
        if node.get("additionalProperties") is not False:
            errors.append(f"{label} must reject additional properties")
        if set(node.get("required", [])) != expected:
            errors.append(f"{label} required-key topology mismatch")
        if set(node.get("properties", {})) != expected:
            errors.append(f"{label} property topology mismatch")
    return errors


def response_contract_fingerprint(scenarios: list[dict[str, Any]]) -> str:
    schema = build_output_schema(scenarios)
    topology = {
        "schema": schema,
        "runtime_keywords": [
            "additionalProperties",
            "enum",
            "items",
            "maxItems",
            "minItems",
            "minimum",
            "pattern",
            "properties",
            "required",
            "type",
            "uniqueItems",
        ],
        "semantic_contract": "scenario-closure/1.4",
    }
    return sha_text(
        json.dumps(
            topology,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    )


def normalized_record_kind(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    token = re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_")
    return RECORD_KIND_ALIASES.get(token, token)


def active_non_null_fields(item: dict[str, Any]) -> set[str]:
    """Return mechanically active fields; empty arrays are the array null-equivalent."""
    return {
        key
        for key, value in item.items()
        if value is not None and (not isinstance(value, list) or bool(value))
    }


def rule_matches(
    item: dict[str, Any], rule: dict[str, Any], *, readiness=False
) -> bool:
    non_null_fields = rule.get("non_null_fields")
    if non_null_fields is not None and active_non_null_fields(item) != set(
        non_null_fields
    ):
        return False
    if readiness:
        if (
            rule.get("scope_id") is not None
            and item.get("scope_id") != rule["scope_id"]
        ):
            return False
    else:
        item_kind = item.get("record_kind")
        if rule.get("record_kind") is not None and item_kind != rule["record_kind"]:
            return False
        allowed_kinds = set(rule.get("record_kinds", []))
        if allowed_kinds and item_kind not in allowed_kinds:
            return False
        if (
            rule.get("operation") is not None
            and item.get("operation") != rule["operation"]
        ):
            return False
        if rule.get("operations") and item.get("operation") not in rule["operations"]:
            return False
    field = rule.get("field")
    allowed = rule.get("allowed")
    if field and allowed and item.get(field) not in allowed:
        return False
    exact_fields = set(rule.get("exact_fields", []))
    for asserted_field, asserted_allowed in rule.get("allowed_fields", {}).items():
        actual = item.get(asserted_field)
        if isinstance(actual, list):
            if not all(isinstance(value, str) for value in actual):
                return False
            actual_values = set(actual)
            allowed_values = set(asserted_allowed)
            if asserted_field in exact_fields:
                if actual_values != allowed_values or len(actual) != len(
                    asserted_allowed
                ):
                    return False
            elif not actual_values.issubset(allowed_values):
                return False
        elif actual not in asserted_allowed:
            return False
    any_field = rule.get("allowed_any_field")
    if any_field:
        fields = any_field.get("fields", [])
        allowed_values = any_field.get("allowed", [])
        if not any(item.get(name) in allowed_values for name in fields):
            return False
    return True


def update_structured_value_errors(
    sid: str, update: dict[str, Any], index: int
) -> list[str]:
    errors: list[str] = []
    kind = update.get("record_kind")
    record_id = update.get("record_id")
    pattern = RECORD_ID_PATTERNS.get(kind) if isinstance(kind, str) else None
    if (
        pattern is None
        or not isinstance(record_id, str)
        or pattern.fullmatch(record_id) is None
    ):
        errors.append(f"{sid}: update at index {index} has an invalid record identity")
    if update.get("operation") not in OPERATIONS:
        errors.append(f"{sid}: update at index {index} has an invalid operation")
    for field, value in update.items():
        if isinstance(value, str) and not contains_visible_content(value):
            errors.append(
                f"{sid}: update at index {index} lacks visible content in {field}"
            )
        if isinstance(value, list) and any(
            isinstance(item, str) and not contains_visible_content(item)
            for item in value
        ):
            errors.append(
                f"{sid}: update at index {index} lacks visible content in {field} entry"
            )
    for field in ("decision_pointer", "promotion_pointer"):
        value = update.get(field)
        if value is not None and not valid_pointer(value):
            errors.append(f"{sid}: update at index {index} has an invalid {field}")
    return errors


def update_cross_field_errors(
    sid: str, update: dict[str, Any], index: int
) -> list[str]:
    errors: list[str] = []
    kind = normalized_record_kind(update.get("record_kind"))
    design_only_kinds = {
        "template_source",
        "template_analysis",
        "semantic_dossier",
        "template_rule",
        "design_rule",
    }
    if (
        update.get("design_only_state") == "design_only"
        and kind in design_only_kinds
        and update.get("support") not in {None, "not_applicable"}
    ):
        errors.append(
            f"{sid}: design-only update at index {index} cannot claim scientific support"
        )

    quantitative_fields = {
        "analysis_mode",
        "partition",
        "missingness",
        "denominator",
        "effective_conclusion",
    }
    if sid != "B10" and quantitative_fields.intersection(
        active_non_null_fields(update)
    ):
        errors.append(
            f"{sid}: update at index {index} carries B10-only quantitative state"
        )

    if update.get("promotion_pointer") is not None and not (
        sid == "B14"
        and kind == "template_source"
        and update.get("record_id") == "TPL-PUB-14"
        and update.get("promotion_pointer") == "M-PUB-14"
    ):
        errors.append(
            f"{sid}: update at index {index} has an invalid promotion pointer owner"
        )

    if update.get("access_state") in {
        "metadata_only",
        "snippet_only",
        "inaccessible",
    }:
        if update.get("analysis_mode") is not None:
            errors.append(
                f"{sid}: restricted-access update at index {index} cannot carry semantic analysis"
            )
        grounding = update.get("grounding", [])
        if isinstance(grounding, list) and any(
            isinstance(value, str)
            and re.search(r"\b(?:paragraph|object)\b", value, re.IGNORECASE)
            for value in grounding
        ):
            errors.append(
                f"{sid}: restricted-access update at index {index} cannot claim paragraph/object grounding"
            )
    return errors


def readiness_shape_errors(
    sid: str, readiness: dict[str, Any], index: int
) -> list[str]:
    state = readiness.get("readiness")
    blocker = readiness.get("blocker")
    next_action = readiness.get("next_action")
    output_pointer = readiness.get("output_pointer")
    pointer_parts = parse_public_pointer(output_pointer)
    if state == "writer-ready" and not (
        blocker is None
        and next_action is None
        and pointer_parts is not None
        and pointer_parts[1] == readiness.get("scope_id")
    ):
        return [
            f"{sid}: writer-ready update at index {index} requires only an output pointer"
        ]
    if state in {"partial", "blocked"} and not (
        isinstance(blocker, str)
        and contains_visible_content(blocker)
        and isinstance(next_action, str)
        and contains_visible_content(next_action)
        and output_pointer is None
    ):
        return [
            f"{sid}: {state} update at index {index} requires blocker and next action without output pointer"
        ]
    return []


def response_semantic_errors(
    response: dict[str, Any], scenario: dict[str, Any]
) -> list[str]:
    sid = response.get("scenario_id", scenario.get("id", "unknown"))
    errors: list[str] = []
    actions = set(response["selected_actions"])
    required_actions = set(scenario.get("required_all_actions", []))
    required_any = set(scenario.get("required_any_actions", []))
    allowed_actions = (
        required_actions | required_any | set(scenario.get("optional_actions", []))
    )
    if not required_actions.issubset(actions):
        errors.append(f"{sid}: missing required actions")
    if required_any and not actions.intersection(required_any):
        errors.append(f"{sid}: requires one allowed action choice")
    if not actions.issubset(allowed_actions):
        errors.append(f"{sid}: selected actions exceed scenario allowance")
    if actions.intersection(scenario.get("prohibited_actions", [])):
        errors.append(f"{sid}: prohibited action selected")

    dimensions = set(response["target_dimensions"])
    required_dimensions = set(scenario.get("required_dimensions", []))
    allowed_dimensions = set(
        scenario.get("allowed_dimensions", scenario.get("required_dimensions", []))
    )
    if not required_dimensions.issubset(dimensions):
        errors.append(f"{sid}: missing required dimension")
    if not dimensions.issubset(allowed_dimensions):
        errors.append(f"{sid}: target dimensions exceed scenario allowance")
    if dimensions.intersection(scenario.get("prohibited_dimensions", [])):
        errors.append(f"{sid}: prohibited dimension targeted")

    scopes = set(response["target_scopes"])
    required_scopes = set(scenario.get("required_scopes", []))
    allowed_scopes = set(
        scenario.get("allowed_scopes", scenario.get("required_scopes", []))
    )
    visible_scope_values = scenario.get("context", {}).get("scope_ids", [])
    visible_scopes = (
        set(visible_scope_values) if isinstance(visible_scope_values, list) else set()
    )
    if not required_scopes.issubset(scopes):
        errors.append(f"{sid}: missing required scope")
    if not scopes.issubset(allowed_scopes):
        errors.append(f"{sid}: target scopes exceed scenario allowance")
    if not scopes.issubset(visible_scopes):
        errors.append(f"{sid}: target scope is absent from model-visible context")
    if scopes.intersection(scenario.get("prohibited_scopes", [])):
        errors.append(f"{sid}: prohibited scope targeted")

    side_effects = set(response["side_effects"])
    required_effects = set(scenario.get("required_side_effects", []))
    allowed_effects = required_effects | set(scenario.get("optional_side_effects", []))
    if not required_effects.issubset(side_effects):
        errors.append(f"{sid}: missing required side effect")
    if not side_effects.issubset(allowed_effects):
        errors.append(f"{sid}: side effects exceed scenario allowance")
    if side_effects.intersection(scenario.get("prohibited_side_effects", [])):
        errors.append(f"{sid}: prohibited side effect selected")

    question = response["question"]
    question_rule = scenario.get("question", {})
    count = question["count"]
    if not question_rule["min_count"] <= count <= question_rule["max_count"]:
        errors.append(f"{sid}: question count out of range")
    allowed_targets = question_rule.get("allowed_targets", [])
    if count == 0 and question["target"] is not None:
        errors.append(f"{sid}: zero-question target must be null")
    if count == 1 and (
        len(allowed_targets) != 1 or question["target"] != allowed_targets[0]
    ):
        errors.append(f"{sid}: question target must exactly match its gate")
    if ("ASK_OWNER" in actions) != (count == 1):
        errors.append(f"{sid}: ASK_OWNER must equal one focused question")

    limits = scenario.get("response_limits", {})
    updates = response["updates"]
    if not limits["min_updates"] <= len(updates) <= limits["max_updates"]:
        errors.append(f"{sid}: update count outside scenario limits")
    update_rules = scenario.get("update_rules", [])
    positive_update_rules = [
        rule for rule in update_rules if rule.get("max_count") != 0
    ]
    for index, update in enumerate(updates):
        errors.extend(update_structured_value_errors(sid, update, index))
        errors.extend(update_cross_field_errors(sid, update, index))
        if not any(rule_matches(update, rule) for rule in positive_update_rules):
            errors.append(f"{sid}: unmatched update at index {index}")
    for rule in update_rules:
        matches = sum(rule_matches(update, rule) for update in updates)
        if matches < rule["min_count"]:
            errors.append(f"{sid}: update rule minimum not satisfied")
        if matches > rule["max_count"]:
            errors.append(f"{sid}: update rule maximum exceeded")

    readiness = response["readiness_updates"]
    readiness_scope_ids = [update.get("scope_id") for update in readiness]
    if len(readiness_scope_ids) != len(set(readiness_scope_ids)):
        errors.append(f"{sid}: readiness scope IDs must be unique")
    if set(readiness_scope_ids) != scopes:
        errors.append(f"{sid}: readiness scopes must equal target scopes")
    if (
        not limits["min_readiness_updates"]
        <= len(readiness)
        <= limits["max_readiness_updates"]
    ):
        errors.append(f"{sid}: readiness count outside scenario limits")
    readiness_rules = scenario.get("readiness_rules", [])
    positive_readiness_rules = [
        rule for rule in readiness_rules if rule.get("max_count") != 0
    ]
    for index, update in enumerate(readiness):
        errors.extend(readiness_shape_errors(sid, update, index))
        if not any(
            rule_matches(update, rule, readiness=True)
            for rule in positive_readiness_rules
        ):
            errors.append(f"{sid}: unmatched readiness update at index {index}")
    for rule in readiness_rules:
        matches = sum(
            rule_matches(update, rule, readiness=True) for update in readiness
        )
        if matches < rule["min_count"]:
            errors.append(f"{sid}: readiness rule minimum not satisfied")
        if matches > rule["max_count"]:
            errors.append(f"{sid}: readiness rule maximum exceeded")
    return errors


def strict_response_errors(response: Any, scenarios: list[dict[str, Any]]) -> list[str]:
    schema = build_output_schema(scenarios)["properties"]["responses"]["items"]
    errors = _strict_schema_errors(response, schema, path="$.response")
    if errors or not isinstance(response, dict):
        return errors
    policy = {scenario["id"]: scenario for scenario in scenarios}
    scenario = policy.get(response.get("scenario_id"))
    if scenario is None:
        return errors + ["$.response.scenario_id: unknown scenario"]
    return errors + response_semantic_errors(response, scenario)


def strict_response_document_errors(
    document: Any, scenarios: list[dict[str, Any]]
) -> list[str]:
    schema = build_output_schema(scenarios)
    errors = schema_runtime_topology_errors(schema)
    errors.extend(_strict_schema_errors(document, schema))
    if errors or not isinstance(document, dict):
        return errors
    responses = document.get("responses")
    if not isinstance(responses, list):
        return errors
    ids = [
        response.get("scenario_id")
        for response in responses
        if isinstance(response, dict)
    ]
    expected_ids = [scenario["id"] for scenario in scenarios]
    if len(ids) != len(expected_ids) or set(ids) != set(expected_ids):
        errors.append("response document must contain each scenario exactly once")
    for response in responses:
        if isinstance(response, dict):
            scenario = next(
                (
                    item
                    for item in scenarios
                    if item["id"] == response.get("scenario_id")
                ),
                None,
            )
            if scenario is not None:
                errors.extend(response_semantic_errors(response, scenario))
    record_ids: list[str] = []
    for response in responses:
        if not isinstance(response, dict):
            continue
        for update in response.get("updates", []):
            if not isinstance(update, dict):
                continue
            record_id = update.get("record_id")
            if isinstance(record_id, str):
                record_ids.append(record_id)
    duplicates = sorted(
        record_id for record_id in set(record_ids) if record_ids.count(record_id) > 1
    )
    if duplicates:
        errors.append(f"response document has duplicate record IDs {duplicates}")
    return errors


def positive_rule_witness(rule: dict[str, Any], *, readiness: bool) -> dict[str, Any]:
    """Construct the deterministic row implied by one closed positive rule."""
    fields = READINESS_FIELDS if readiness else UPDATE_FIELDS
    row: dict[str, Any] = {
        field: [] if field in UPDATE_ARRAY_FIELDS else None for field in fields
    }
    selector_field = "scope_id" if readiness else "record_kind"
    row[selector_field] = rule[selector_field]
    exact_fields = set(rule["exact_fields"])
    for field in rule["non_null_fields"]:
        if field == selector_field:
            continue
        if field in UPDATE_FREE_TEXT_FIELDS:
            row[field] = (
                "[visible controlled design witness]"
                if field == "design_payload"
                else "visible authority witness"
            )
            continue
        allowed = rule["allowed_fields"][field]
        row[field] = list(allowed) if field in exact_fields else allowed[0]
    return row


def authority_witness_document(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    """Build one complete response document directly from scenario authority."""
    responses: list[dict[str, Any]] = []
    for scenario in scenarios:
        required_any = scenario["required_any_actions"]
        selected_actions = list(scenario["required_all_actions"])
        if required_any:
            selected_actions.append(required_any[0])
        question = scenario["question"]
        updates = [
            positive_rule_witness(rule, readiness=False)
            for rule in scenario["update_rules"]
            if rule["max_count"] > 0
            for _ in range(rule["min_count"])
        ]
        readiness_updates = [
            positive_rule_witness(rule, readiness=True)
            for rule in scenario["readiness_rules"]
            if rule["max_count"] > 0
            for _ in range(rule["min_count"])
        ]
        responses.append(
            {
                "scenario_id": scenario["id"],
                "selected_actions": selected_actions,
                "target_dimensions": list(scenario["required_dimensions"]),
                "target_scopes": list(scenario["required_scopes"]),
                "updates": updates,
                "readiness_updates": readiness_updates,
                "question": {
                    "count": question["min_count"],
                    "target": (
                        question["allowed_targets"][0]
                        if question["min_count"] == 1
                        else None
                    ),
                },
                "side_effects": list(scenario["required_side_effects"]),
            }
        )
    return {"responses": responses}


def authority_witness_document_errors(
    scenarios: list[dict[str, Any]],
) -> list[str]:
    """Run authority-derived rows through the shared runtime acceptance path."""
    return strict_response_document_errors(
        authority_witness_document(scenarios), scenarios
    )


def manuscript_prose_warnings(response: dict[str, Any]) -> list[str]:
    """Warn on obvious leakage; this heuristic is not a semantic proof."""
    warnings: list[str] = []
    sid = response.get("scenario_id", "unknown")
    for update in response.get("updates", []):
        if not isinstance(update, dict):
            continue
        payload = update.get("design_payload")
        if not isinstance(payload, str) or not payload.strip():
            continue
        kind = normalized_record_kind(update.get("record_kind"))
        target_kind = normalized_record_kind(update.get("target_kind"))
        if kind not in {
            "frame",
            "caption",
            "caption_blueprint",
        } and target_kind not in {
            "controlled_sentence_frame",
            "caption_blueprint",
        }:
            continue
        words = re.findall(r"\b[\w'-]+\b", payload)
        if len(words) >= 12 and re.search(r"[.!?]\s*$", payload):
            warnings.append(
                f"{sid}: manual review warning for sentence-like controlled payload"
            )
    return warnings


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
        + json.dumps(
            response_shape, ensure_ascii=False, sort_keys=True, allow_nan=False
        )
        + "\n"
        + "Use exact case-sensitive selected_actions tokens from: "
        + json.dumps(actions, ensure_ascii=False, allow_nan=False)
        + ".\nUse exact side_effects tokens from: "
        + json.dumps(side_effects, ensure_ascii=False, allow_nan=False)
        + ". target_dimensions may contain only D00-D19 IDs; target_scopes may contain only explicit SCOPE-* IDs from the scenario context. "
        "updates and readiness_updates must contain JSON objects, never prose strings. Each update object should name record_kind and operation plus the relevant changed field; each readiness object should name scope_id and readiness when applicable. Controlled frames and captions must remain functional placeholder skeletons, never paste-ready manuscript prose.\n"
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
    canonical_prompt = build_prompt(
        skill_text,
        sha_text(skill_text),
        reference_text,
        sha_text(reference_text),
        scenarios,
    )
    if prompt != canonical_prompt:
        errors.append("prompt differs from the canonical closed prompt contract")
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
        visible_document = load_json_text(scenario_match.group(1))
    except ValueError as exc:
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
    text = Path(raw).read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError("raw output must be one JSON document")
    try:
        document = load_json_text(text)
    except ValueError as exc:
        raise ValueError("raw output must be one sole JSON document") from exc
    if not isinstance(document, dict):
        raise ValueError("raw output must be a JSON object")
    if set(document) != {"responses"}:
        raise ValueError("capture document must contain only responses")
    return document


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate or finalize an oracle-free schema-0.3 behavior capture."
    )
    parser.add_argument("command", choices=["init", "finalize"])
    parser.add_argument("--capture", required=True)
    parser.add_argument("--model", default="unknown")
    parser.add_argument("--runtime", default="unknown")
    parser.add_argument(
        "--capture-kind",
        choices=["offline_policy_fixture", "live_model"],
        default="live_model",
    )
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
                allow_nan=False,
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
            allow_nan=False,
        )
        + "\n"
    )
    if output_schema_path.read_text(encoding="utf-8") != expected_output_schema:
        raise ValueError(
            "output-schema.json does not match the current behavior contract"
        )
    raw = capture / "raw-output.md"
    document = extract(raw)
    response_errors = strict_response_document_errors(document, scenarios)
    if response_errors:
        raise ValueError("; ".join(response_errors))
    responses = document["responses"]
    if args.capture_kind == "offline_policy_fixture" and (
        args.model != "policy-fixture" or args.runtime != "offline-reproducible-fixture"
    ):
        raise ValueError("offline policy fixture labels are fixed")
    if args.capture_kind == "live_model" and (
        not contains_visible_content(args.model)
        or not contains_visible_content(args.runtime)
        or args.model in {"unknown", "policy-fixture"}
        or args.runtime in {"unknown", "offline-reproducible-fixture"}
    ):
        raise ValueError("live_model capture requires explicit non-fixture provenance")

    actions_path = capture / "actions.json"
    actions_path.write_text(
        json.dumps(
            document,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
    )
    visible_json = model_visible_scenario_json(scenarios)
    manifest = {
        "prompt_contract_version": PROMPT_CONTRACT_VERSION,
        "capture_kind": args.capture_kind,
        "model": args.model,
        "runtime": args.runtime,
        "captured_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "skill_sha256": sha(skill_path),
        "venue_template_sha256": sha(reference_path),
        "scenarios_sha256": sha(scenario_path),
        "model_visible_scenarios_sha256": sha_text(visible_json),
        "prompt_sha256": sha(prompt_path),
        "output_schema_sha256": sha(output_schema_path),
        "response_contract_sha256": response_contract_fingerprint(scenarios),
        "raw_output_sha256": sha(raw),
        "actions_sha256": sha(actions_path),
        "scenario_ids": [response.get("scenario_id") for response in responses],
        "scenario_count": expected_count,
    }
    (capture / "manifest.json").write_text(
        json.dumps(manifest, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(capture / "manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
