#!/usr/bin/env python3
"""Generate a static yxj-paper-os structural/template-analysis dashboard."""

from __future__ import annotations

import argparse
import ast
from contextlib import suppress
import hashlib
import html
import json
import math
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent

# Avoid creating local __pycache__ when importing helper constants.
sys.dont_write_bytecode = True

# Keep bytecode disabled before importing the colocated validator helpers.
from verify_design_pack import (  # noqa: E402
    ANALYZER_ACTION_TO_SUGGESTED_DISPOSITION,
    CANONICAL_SURFACES,
    DIMENSION_COLUMNS,
    DIMENSION_INDEX,
    FINAL_PACK,
    FOUR_GATES,
    REQUIRED_DIMENSION_IDS,
    REQUIRED_FILES,
    REQUIRED_HEADINGS,
    TEMPLATE_MODES,
    VALID_BLOCKS_VALUES,
    VALID_DIMENSION_STATUSES,
    first_present,
    has_placeholder,
    level_two_heading_slugs,
    parse_anchor,
    section_content,
    slugify,
    validate_workspace_report,
)
from verify_semantic_dossier import validate_semantic_dossier  # noqa: E402


CACHE_DIR = ".yxj-paper-os"
OUTPUT_NAME = "dashboard.html"
MAX_FRAGMENT_CHARS = 6000
TEMPLATE_ANALYSIS_DIR = "template-analysis"
TRUSTED_METRIC_REGISTRY = (
    SKILL_DIR / "assets" / "template-analysis" / "metric-registry.json"
)
ANALYZER_REQUIRED_FILES = {
    "manifest": ("manifest.json", "template-corpus-normalized/1.0"),
    "registry": ("metric-registry.json", "template-metric-registry/1.0"),
    "summary": ("corpus-summary.json", "template-corpus-summary/1.0"),
    "profile": ("design-profile.json", "template-design-profile/1.0"),
}
TEMPLATE_ANALYSIS_IDENTITY_KEYS = (
    "analysis_id",
    "corpus_id",
    "analyzer_version",
)
MAX_ANALYSIS_BYTES = 8_000_000
MAX_ANALYSIS_LIST_ITEMS = 80
ANALYZER_MODES = {"case_set", "exploratory", "distributional"}
ANALYZER_TOP_LEVEL_KEYS = {
    "manifest": {
        "schema",
        "analyzer_version",
        "analysis_id",
        "corpus_id",
        "target",
        "analysis_mode",
        "requested_analysis_mode",
        "effective_analysis_mode",
        "analysis_mode_source",
        "analysis_mode_downgrade_reason",
        "design_question",
        "design_metric_ids",
        "source_manifest_sha256",
        "metric_registry_sha256",
        "documents",
        "official_constraints",
    },
    "registry": {
        "schema",
        "analysis_id",
        "corpus_id",
        "analyzer_version",
        "version",
        "registry_version",
        "tokenizer",
        "tokenizer_profile",
        "normalization",
        "normalization_profile",
        "missingness",
        "limits",
        "input_formats",
        "aggregation_contract",
        "annotation_acceptance",
        "design_translation_contract",
        "prohibited_semantic_outputs",
        "metrics",
    },
    "summary": {
        "schema",
        "analyzer_version",
        "analysis_id",
        "corpus_id",
        "analysis_unit",
        "analysis_mode",
        "requested_analysis_mode",
        "effective_analysis_mode",
        "design_question",
        "design_metric_ids",
        "analysis_mode_source",
        "analysis_mode_downgrade_reason",
        "distribution_ready_metric_count",
        "all_design_metrics_distribution_ready",
        "design_metric_readiness",
        "document_count",
        "parsed_document_count",
        "supplement_document_count",
        "venues",
        "groups",
        "comparisons",
        "sequences",
        "transitions",
        "lead_lag",
        "section_sequences",
        "annotations",
        "boundaries",
    },
    "profile": {
        "schema",
        "analyzer_version",
        "analysis_id",
        "corpus_id",
        "design_question",
        "design_metric_ids",
        "entries",
        "forbidden_uses",
    },
}
ANALYZER_REGISTRY_METRIC_KEYS = {
    "metric_id",
    "aggregation",
    "default_aggregation",
    "definition",
    "denominator",
    "design_surfaces",
    "eligibility",
    "entity",
    "extraction_mode",
    "introduced_in",
    "implementation_method",
    "missing_statuses",
    "numerator",
    "priority",
    "paper_reduction",
    "supported_formats",
    "unit",
    "value_type",
    "zero_semantics",
}
ANALYZER_PROFILE_ENTRY_KEYS = {
    "profile_id",
    "source_type",
    "partition",
    "metric_ids",
    "observation",
    "valid_n",
    "missingness",
    "uncertainty",
    "design_surface",
    "target_kind",
    "candidate_action",
    "affected_dimensions",
    "affected_scopes",
    "boundary",
    "source_pointer",
    "source_hash",
    "source_sha256",
    "origin",
    "resolution",
}
ANALYZER_UNCERTAINTY_KEYS = {
    "kind",
    "locator",
    "analysis_mode",
    "requested_analysis_mode",
    "effective_analysis_mode",
    "metric_effective_analysis_mode",
    "sample_size_label",
    "sample_size_label_is_gate",
    "iqr",
    "mad",
    "selection_boundary",
    "valid_coverage",
    "comparable_stratum",
    "distribution_supported",
}
ANALYZER_METRIC_SUMMARY_KEYS = {
    "valid_n",
    "eligible_n",
    "missingness",
    "missingness_by_status",
    "sample_size_label",
    "sample_size_label_is_gate",
    "raw_points",
    "median",
    "iqr",
    "mad",
    "p10",
    "p25",
    "p50",
    "p75",
    "p90",
    "min",
    "max",
    "mean",
    "std",
    "bootstrap_95_ci",
    "bootstrap_statistic",
    "bootstrap_resamples",
    "zero_prevalence",
    "median_per_paper_rate",
    "pooled_rate",
    "category",
}
ANALYZER_VISIBLE_METRIC_FIELDS = (
    "valid_n",
    "eligible_n",
    "missingness",
    "median",
    "p25",
    "p75",
    "iqr",
    "mad",
    "bootstrap_95_ci",
    "sample_size_label",
)
SUSPICIOUS_ANALYZER_KEY_RE = re.compile(
    r"(?i)(?:prompt|oracle|secret|copied[_-]?body|quality|completeness|"
    r"(?:^|[_-])score(?:$|[_-])|venue[_-]?fit|novelty|acceptance|semantic[_-]?claim)"
)
FORBIDDEN_METRIC_ID_RE = re.compile(
    r"(?i)(?:score|quality|completeness|novel|acceptance|claim|semantic|"
    r"(?:^|[._-])fit(?:$|[._-]))"
)
FORBIDDEN_OBSERVATION_RE = re.compile(
    r"(?i)\b(?:novel|scientifically?\s+adequate|quality\s+score|venue\s*fit|"
    r"acceptance\s+(?:score|prediction)|claim\s+truth)\b"
)
SAFE_SUSPICIOUS_ANALYZER_KEYS = {
    "annotation_acceptance",
    "prohibited_semantic_outputs",
    "zero_semantics",
}
CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f\ud800-\udfff]")
SAFE_ANALYZER_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}\Z")
SAFE_METRIC_ID_RE = re.compile(r"[a-z][a-z0-9_]*(?:\.[a-z0-9_]+)+\Z")
SAFE_PARTITION_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,63}\Z")
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
ANALYSIS_MODE_SOURCES = {"manifest_declared", "conservative_default"}

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


def sanitize_untrusted_text(
    value: str, *, scope: str, warnings: list[dict[str, str]]
) -> str:
    matches = CONTROL_CHAR_RE.findall(value)
    if not matches:
        return value
    warnings.append(
        warning(
            scope,
            f"sanitized {len(matches)} NUL/control/lone-surrogate character(s)",
        )
    )
    return CONTROL_CHAR_RE.sub("�", value)


def parse_finite_float(token: str) -> float:
    value = float(token)
    if not math.isfinite(value):
        raise ValueError(f"non-finite JSON number {token}")
    return value


def json_safety_issue(value: Any, *, path: str = "$") -> str | None:
    if isinstance(value, float) and not math.isfinite(value):
        return f"{path} contains a non-finite number"
    if isinstance(value, str) and CONTROL_CHAR_RE.search(value):
        return f"{path} contains NUL/control/lone-surrogate text"
    if isinstance(value, list):
        for index, item in enumerate(value):
            issue = json_safety_issue(item, path=f"{path}[{index}]")
            if issue:
                return issue
    elif isinstance(value, dict):
        for key, item in value.items():
            if CONTROL_CHAR_RE.search(str(key)):
                return f"{path} contains an unsafe object key"
            issue = json_safety_issue(item, path=f"{path}.{key}")
            if issue:
                return issue
    return None


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
            text = path.read_text(encoding="utf-8")
            contents[file_name] = sanitize_untrusted_text(
                text, scope=file_name, warnings=warnings
            )
        except UnicodeDecodeError as exc:
            warnings.append(warning(file_name, f"cannot read as utf-8: {exc}"))
        except OSError as exc:
            warnings.append(warning(file_name, f"cannot read file: {exc}"))
    return contents, warnings


def unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def reject_nonfinite_json(token: str) -> Any:
    raise ValueError(f"non-finite JSON token {token}")


def read_analyzer_json(
    path: Path, analysis_dir: Path
) -> tuple[dict[str, Any] | None, str | None]:
    if not path.exists():
        return None, "required analyzer artifact is absent"
    if path.is_symlink():
        return None, "required analyzer artifact is a symlink"
    try:
        resolved = path.resolve(strict=True)
        resolved.relative_to(analysis_dir)
        if not resolved.is_file() or resolved.stat().st_size > MAX_ANALYSIS_BYTES:
            raise ValueError("artifact is not a bounded regular file")
        parsed = json.loads(
            resolved.read_text(encoding="utf-8"),
            object_pairs_hook=unique_json_object,
            parse_constant=reject_nonfinite_json,
            parse_float=parse_finite_float,
        )
    except (
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
        ValueError,
        RecursionError,
    ):
        # Do not echo parser details: duplicate keys and malformed tokens are
        # attacker-controlled and can otherwise become a hidden-body exfiltration
        # channel through the dashboard warning center.
        return None, "required analyzer artifact is unreadable or unsafe"
    if not isinstance(parsed, dict):
        return None, "required analyzer artifact must be one JSON object"
    issue = json_safety_issue(parsed)
    if issue:
        return None, issue
    return parsed, None


def has_suspicious_analyzer_key(value: Any) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            if (
                key not in SAFE_SUSPICIOUS_ANALYZER_KEYS
                and SUSPICIOUS_ANALYZER_KEY_RE.search(key)
            ):
                return True
            if has_suspicious_analyzer_key(item):
                return True
    elif isinstance(value, list):
        return any(has_suspicious_analyzer_key(item) for item in value)
    return False


def _string_list(value: Any) -> list[str] | None:
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(item, str) and item for item in value)
        or len(value) != len(set(value))
    ):
        return None
    return list(value)


def _safe_analyzer_id(value: Any) -> bool:
    return (
        isinstance(value, str)
        and bool(SAFE_ANALYZER_ID_RE.fullmatch(value))
        and not SUSPICIOUS_ANALYZER_KEY_RE.search(value)
    )


def _safe_metric_value(field: str, value: Any) -> bool:
    def finite_number(item: Any) -> bool:
        return (
            isinstance(item, int)
            and not isinstance(item, bool)
            or isinstance(item, float)
            and math.isfinite(item)
        )

    if value is None:
        return True
    if field in {"valid_n", "eligible_n", "missingness"}:
        return isinstance(value, int) and not isinstance(value, bool) and value >= 0
    if field == "sample_size_label":
        return value in ANALYZER_MODES
    if field == "bootstrap_95_ci":
        return (
            isinstance(value, list)
            and len(value) == 2
            and all(finite_number(item) for item in value)
        )
    return finite_number(value)


def load_trusted_metric_registry() -> tuple[set[str], str, str | None]:
    """Read the shipped registry as the metric-vocabulary trust anchor."""

    try:
        trusted_root = SKILL_DIR.resolve(strict=True)
        if TRUSTED_METRIC_REGISTRY.is_symlink():
            raise ValueError("trusted registry is a symlink")
        resolved = TRUSTED_METRIC_REGISTRY.resolve(strict=True)
        resolved.relative_to(trusted_root)
        if not resolved.is_file() or resolved.stat().st_size > MAX_ANALYSIS_BYTES:
            raise ValueError("trusted registry is not a bounded regular file")
        payload_bytes = resolved.read_bytes()
        payload = json.loads(
            payload_bytes.decode("utf-8"),
            object_pairs_hook=unique_json_object,
            parse_constant=reject_nonfinite_json,
            parse_float=parse_finite_float,
        )
        if (
            not isinstance(payload, dict)
            or payload.get("schema") != "template-metric-registry/1.0"
            or json_safety_issue(payload)
        ):
            raise ValueError("trusted registry contract is invalid")
        rows = payload.get("metrics")
        if not isinstance(rows, list) or not rows:
            raise ValueError("trusted registry metric rows are absent")
        metric_ids: set[str] = set()
        for row in rows:
            if isinstance(row, dict) and isinstance(row.get("metric_id"), str):
                metric_ids.add(row["metric_id"])
        if len(metric_ids) != len(rows) or not all(
            isinstance(metric_id, str)
            and SAFE_METRIC_ID_RE.fullmatch(metric_id)
            and not SUSPICIOUS_ANALYZER_KEY_RE.search(metric_id)
            for metric_id in metric_ids
        ):
            raise ValueError("trusted registry metric identity is invalid")
        return metric_ids, hashlib.sha256(payload_bytes).hexdigest(), None
    except (
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
        ValueError,
        RecursionError,
    ):
        return set(), "unknown", "shipped metric registry is unavailable or invalid"


def build_template_analysis(
    workspace: Path, warnings: list[dict[str, str]]
) -> dict[str, Any]:
    """Validate a complete analyzer bundle and retain only allowlisted mechanics."""
    root = workspace / CACHE_DIR / TEMPLATE_ANALYSIS_DIR
    model: dict[str, Any] = {
        "state": "absent",
        "directory": str(root),
        "artifacts": {
            key: {
                "label": key,
                "path": str(root / filename),
                "state": "absent",
                "schema": schema,
            }
            for key, (filename, schema) in ANALYZER_REQUIRED_FILES.items()
        },
        "identity": {},
        "provenance": {},
        "selected_metric_ids": [],
        "metric_summaries": [],
        "candidates": [],
        "violations": [],
        "note": (
            "Strict allowlist projection of a complete optional analyzer bundle; no "
            "raw parsed tree, preview, semantic observation, score, prompt, or oracle "
            "content is retained in dashboard data."
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

    parsed: dict[str, dict[str, Any]] = {}
    violations: list[str] = []

    def reject(code: str, message: str) -> None:
        if code not in violations:
            violations.append(code)
        warnings.append(warning("template-analysis", message))

    for key, (filename, expected_schema) in ANALYZER_REQUIRED_FILES.items():
        payload, error = read_analyzer_json(resolved_root / filename, resolved_root)
        artifact = model["artifacts"][key]
        if error:
            artifact["state"] = (
                "absent" if not (resolved_root / filename).exists() else "malformed"
            )
            reject("ANALYZER_BUNDLE", f"{filename}: {error}")
            continue
        assert payload is not None
        parsed[key] = payload
        if payload.get("schema") != expected_schema:
            artifact["state"] = "malformed"
            reject("ANALYZER_SCHEMA", f"{filename}: unsupported analyzer schema")
            continue
        artifact["state"] = "validated"
        extra_top = set(payload) - ANALYZER_TOP_LEVEL_KEYS[key]
        if extra_top:
            reject(
                "ANALYZER_EXTRA_FIELD",
                f"{filename}: disallowed extra analyzer fields were omitted",
            )
        if has_suspicious_analyzer_key(payload):
            reject(
                "ANALYZER_FORBIDDEN_FIELD",
                f"{filename}: forbidden prompt/oracle/score-like fields were omitted",
            )

    if set(parsed) != set(ANALYZER_REQUIRED_FILES):
        model["state"] = "degraded"
        model["violations"] = violations
        return model

    identities: list[tuple[Any, ...]] = []
    for key, payload in parsed.items():
        identity = tuple(payload.get(name) for name in TEMPLATE_ANALYSIS_IDENTITY_KEYS)
        if not all(_safe_analyzer_id(value) for value in identity):
            reject("ANALYZER_IDENTITY", f"{key}: analyzer identity is incomplete")
        identities.append(identity)
    if len(set(identities)) != 1:
        reject("ANALYZER_MIXED_IDENTITY", "analyzer bundle identity is mixed")
    else:
        model["identity"] = dict(zip(TEMPLATE_ANALYSIS_IDENTITY_KEYS, identities[0]))
    if {
        "ANALYZER_IDENTITY",
        "ANALYZER_MIXED_IDENTITY",
    }.intersection(violations):
        # Never combine even mechanically allowlisted values across an incomplete or
        # mixed identity boundary.  The artifact status is still useful, but the
        # bundle itself has no trusted projection.
        model["state"] = (
            "mixed" if "ANALYZER_MIXED_IDENTITY" in violations else "degraded"
        )
        model["violations"] = violations
        return model

    manifest = parsed["manifest"]
    registry = parsed["registry"]
    summary = parsed["summary"]
    profile = parsed["profile"]
    trusted_registry_ids, trusted_registry_sha, trusted_registry_error = (
        load_trusted_metric_registry()
    )
    if trusted_registry_error:
        reject("ANALYZER_TRUST_ANCHOR", trusted_registry_error)
    if manifest.get("metric_registry_sha256") != trusted_registry_sha:
        reject(
            "ANALYZER_REGISTRY_DIGEST",
            "analyzer registry digest does not match the shipped trust anchor",
        )
    selected = _string_list(manifest.get("design_metric_ids"))
    if selected is None or not all(
        SAFE_METRIC_ID_RE.fullmatch(metric)
        and not FORBIDDEN_METRIC_ID_RE.search(metric)
        and not SUSPICIOUS_ANALYZER_KEY_RE.search(metric)
        for metric in selected
    ):
        reject("ANALYZER_METRICS", "analyzer selected metric identity is invalid")
        selected = []
    effective_mode = manifest.get("effective_analysis_mode")
    if effective_mode not in ANALYZER_MODES:
        reject("ANALYZER_MODE", "analyzer effective mode is invalid")
        effective_mode = "unknown"
    for payload in (summary, profile):
        if payload.get("design_metric_ids") != selected:
            reject("ANALYZER_METRICS", "analyzer selected metrics differ across bundle")
    if summary.get("effective_analysis_mode") != effective_mode:
        reject("ANALYZER_MODE", "summary effective mode differs from manifest")

    registry_rows = registry.get("metrics")
    registry_ids: set[str] = set()
    if not isinstance(registry_rows, list) or not registry_rows:
        reject("ANALYZER_REGISTRY", "metric registry rows are missing")
        registry_rows = []
    for row in registry_rows:
        if not isinstance(row, dict):
            reject(
                "ANALYZER_EXTRA_FIELD", "metric registry contains disallowed row fields"
            )
            continue
        metric_id = row.get("metric_id")
        if isinstance(metric_id, str) and (
            FORBIDDEN_METRIC_ID_RE.search(metric_id)
            or SUSPICIOUS_ANALYZER_KEY_RE.search(metric_id)
        ):
            reject(
                "ANALYZER_FORBIDDEN_METRIC", "forbidden score-like metric was omitted"
            )
            continue
        if set(row) - ANALYZER_REGISTRY_METRIC_KEYS:
            reject(
                "ANALYZER_EXTRA_FIELD", "metric registry contains disallowed row fields"
            )
            continue
        if (
            not isinstance(metric_id, str)
            or not SAFE_METRIC_ID_RE.fullmatch(metric_id)
            or SUSPICIOUS_ANALYZER_KEY_RE.search(metric_id)
            or metric_id in registry_ids
        ):
            reject("ANALYZER_REGISTRY", "metric registry IDs are invalid or duplicated")
            continue
        if metric_id not in trusted_registry_ids:
            reject(
                "ANALYZER_UNSUPPORTED_METRIC",
                "workspace registry contains a metric outside the shipped registry",
            )
            continue
        registry_ids.add(metric_id)
    if any(
        metric not in registry_ids
        or metric not in trusted_registry_ids
        or FORBIDDEN_METRIC_ID_RE.search(metric)
        for metric in selected
    ):
        reject("ANALYZER_UNSUPPORTED_METRIC", "selected unsupported metric was omitted")
    model["selected_metric_ids"] = [
        metric
        for metric in selected
        if metric in registry_ids and metric in trusted_registry_ids
    ]

    groups = summary.get("groups")
    overall = groups.get("overall") if isinstance(groups, dict) else None
    metrics = overall.get("metrics") if isinstance(overall, dict) else None
    if not isinstance(metrics, dict):
        reject("ANALYZER_SUMMARY", "summary overall metric map is missing")
        metrics = {}
    for metric_id, metric in metrics.items():
        if (
            not isinstance(metric_id, str)
            or metric_id not in registry_ids
            or metric_id not in trusted_registry_ids
            or FORBIDDEN_METRIC_ID_RE.search(metric_id)
        ):
            reject(
                "ANALYZER_UNSUPPORTED_METRIC", "summary unsupported metric was omitted"
            )
            continue
        if not isinstance(metric, dict) or set(metric) - ANALYZER_METRIC_SUMMARY_KEYS:
            reject("ANALYZER_EXTRA_FIELD", "summary metric has disallowed fields")
            continue
        if metric_id not in selected:
            continue
        projection: dict[str, Any] = {"metric_id": metric_id}
        metric_is_safe = True
        for field in ANALYZER_VISIBLE_METRIC_FIELDS:
            value = metric.get(field)
            if not _safe_metric_value(field, value):
                metric_is_safe = False
                reject(
                    "ANALYZER_METRIC_VALUE",
                    "summary metric contains a non-mechanical or invalid value",
                )
                break
            projection[field] = value
        if metric_is_safe:
            model["metric_summaries"].append(projection)

    entries = profile.get("entries")
    if not isinstance(entries, list):
        reject("ANALYZER_PROFILE", "design profile entries are missing")
        entries = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            reject("ANALYZER_PROFILE", "design profile contains a non-object entry")
            continue
        if set(entry) - ANALYZER_PROFILE_ENTRY_KEYS:
            reject(
                "ANALYZER_EXTRA_FIELD",
                "design profile contains disallowed entry fields",
            )
        observation = entry.get("observation")
        if isinstance(observation, str) and FORBIDDEN_OBSERVATION_RE.search(
            observation
        ):
            reject("ANALYZER_SEMANTIC_CLAIM", "semantic-claim observation was omitted")
        source_type = entry.get("source_type")
        metric_ids = entry.get("metric_ids")
        if not isinstance(metric_ids, list) or not all(
            isinstance(metric, str) for metric in metric_ids
        ):
            reject("ANALYZER_PROFILE", "candidate metric identity is invalid")
            metric_ids = []
        candidate_metrics_supported = not (
            source_type == "corpus"
            and (
                not metric_ids
                or any(
                    metric not in selected
                    or metric not in registry_ids
                    or metric not in trusted_registry_ids
                    for metric in metric_ids
                )
            )
        )
        if not candidate_metrics_supported:
            reject("ANALYZER_UNSUPPORTED_METRIC", "candidate uses an unselected metric")
        elif source_type not in {"corpus", "official_constraints"}:
            reject("ANALYZER_PROFILE", "candidate source type is invalid")
        valid_n = entry.get("valid_n")
        missingness = entry.get("missingness")
        if (
            not isinstance(valid_n, int)
            or isinstance(valid_n, bool)
            or valid_n < 0
            or not isinstance(missingness, int)
            or isinstance(missingness, bool)
            or missingness < 0
            or valid_n + missingness <= 0
        ):
            reject(
                "ANALYZER_DENOMINATOR", "candidate denominator/missingness is invalid"
            )
        action = entry.get("candidate_action")
        action_is_known = action in ANALYZER_ACTION_TO_SUGGESTED_DISPOSITION
        if not action_is_known:
            reject("ANALYZER_UNKNOWN_ACTION", "candidate action is unknown")
        uncertainty = entry.get("uncertainty")
        if not isinstance(uncertainty, dict):
            reject("ANALYZER_UNCERTAINTY", "candidate uncertainty is missing")
            uncertainty = {}
        elif set(uncertainty) - ANALYZER_UNCERTAINTY_KEYS:
            reject(
                "ANALYZER_EXTRA_FIELD", "candidate uncertainty has disallowed fields"
            )
        item_mode = uncertainty.get("effective_analysis_mode")
        metric_mode = uncertainty.get("metric_effective_analysis_mode")
        if source_type == "corpus" and (
            item_mode != effective_mode or metric_mode not in ANALYZER_MODES
        ):
            reject("ANALYZER_MODE", "candidate effective-mode boundary is invalid")
        comparable = uncertainty.get("comparable_stratum")
        comparable_state = (
            "comparable"
            if comparable is True
            else "incomparable"
            if comparable is False
            else "N/A"
        )
        candidate_id = entry.get("profile_id")
        if not _safe_analyzer_id(candidate_id):
            reject("ANALYZER_PROFILE", "candidate identity is invalid")
            candidate_id = f"entry-{index + 1}"
        partition = entry.get("partition")
        if (
            not isinstance(partition, str)
            or not SAFE_PARTITION_RE.fullmatch(partition)
            or SUSPICIOUS_ANALYZER_KEY_RE.search(partition)
        ):
            reject("ANALYZER_PROFILE", "candidate partition is invalid")
            partition = "unknown"
        affected_scopes = entry.get("affected_scopes")
        if not isinstance(affected_scopes, list) or not all(
            isinstance(scope, str) and SCOPE_ID_RE.fullmatch(scope)
            for scope in affected_scopes
        ):
            reject("ANALYZER_PROFILE", "candidate affected scopes are invalid")
            affected_scopes = []
        if not candidate_metrics_supported:
            continue
        model["candidates"].append(
            {
                "candidate_id": candidate_id,
                "source_type": source_type
                if source_type in {"corpus", "official_constraints"}
                else "unknown",
                "partition": partition,
                "metric_ids": [
                    metric
                    for metric in metric_ids
                    if metric in model["selected_metric_ids"]
                ],
                "valid_n": valid_n if isinstance(valid_n, int) else "invalid",
                "missingness": missingness
                if isinstance(missingness, int)
                else "invalid",
                "effective_analysis_mode": item_mode
                if item_mode in ANALYZER_MODES
                else "N/A",
                "metric_effective_analysis_mode": metric_mode
                if metric_mode in ANALYZER_MODES
                else "N/A",
                "comparability": comparable_state,
                "candidate_action": str(action) if action_is_known else "unknown",
                "affected_scopes": affected_scopes,
            }
        )

    mode_source = manifest.get("analysis_mode_source")
    source_manifest_sha = manifest.get("source_manifest_sha256")
    registry_sha = manifest.get("metric_registry_sha256")
    if mode_source not in ANALYSIS_MODE_SOURCES:
        reject("ANALYZER_PROVENANCE", "analysis mode source is invalid")
        mode_source = "unknown"
    if not isinstance(source_manifest_sha, str) or not SHA256_RE.fullmatch(
        source_manifest_sha
    ):
        reject("ANALYZER_PROVENANCE", "source manifest digest is invalid")
        source_manifest_sha = "unknown"
    if registry_sha != trusted_registry_sha:
        reject("ANALYZER_PROVENANCE", "metric registry digest is invalid")
        registry_sha = "unknown"
    model["provenance"] = {
        "effective_analysis_mode": effective_mode,
        "analysis_mode_source": mode_source,
        "source_manifest_sha256": source_manifest_sha,
        "metric_registry_sha256": registry_sha,
    }
    model["violations"] = violations
    if "ANALYZER_MIXED_IDENTITY" in violations:
        model["state"] = "mixed"
    elif "ANALYZER_UNKNOWN_ACTION" in violations:
        model["state"] = "unknown_action"
    elif violations:
        model["state"] = "degraded"
    elif any(item["comparability"] == "incomparable" for item in model["candidates"]):
        model["state"] = "incomparable"
    else:
        model["state"] = "current"
    return model


def load_semantic_dossier(
    workspace: Path, warnings: list[dict[str, str]]
) -> dict[str, Any]:
    """Project the hidden semantic dossier without exposing semantic body text."""

    path = workspace / CACHE_DIR / TEMPLATE_ANALYSIS_DIR / "semantic-dossier.json"
    model: dict[str, Any] = {
        "state": "absent",
        "path": str(path),
        "schema": "unknown",
        "dossier_id": "none",
        "updated_at": "none",
        "counts": {"documents": 0, "observations": 0, "rules": 0},
        "documents": [],
        "rules": [],
        "freshness": [],
        "limitations": [],
        "projection_state": "absent",
        "diagnostics": [],
        "note": (
            "Hidden model-semantic design provenance only; no prompt/oracle body, "
            "scientific authority, or semantic-completeness score is displayed."
        ),
    }
    if not path.exists():
        return model
    if path.is_symlink():
        message = "refusing to read symlinked semantic-dossier.json"
        warnings.append(warning("semantic-dossier", message))
        model.update(state="unsafe", projection_state="untrusted")
        model["diagnostics"] = [message]
        return model
    try:
        root = workspace.resolve(strict=True)
        resolved = path.resolve(strict=True)
        resolved.relative_to(root)
        if not resolved.is_file() or resolved.stat().st_size > MAX_ANALYSIS_BYTES:
            raise ValueError("dossier is not a bounded regular file")
        payload = json.loads(
            resolved.read_text(encoding="utf-8"),
            object_pairs_hook=unique_json_object,
            parse_constant=reject_nonfinite_json,
            parse_float=parse_finite_float,
        )
    except (
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
        ValueError,
        RecursionError,
    ):
        message = "cannot read semantic-dossier.json: unreadable or unsafe input"
        warnings.append(warning("semantic-dossier", message))
        model.update(state="malformed", projection_state="untrusted")
        model["diagnostics"] = [message]
        return model
    if not isinstance(payload, dict):
        message = "semantic-dossier.json must be one JSON object"
        warnings.append(warning("semantic-dossier", message))
        model.update(state="malformed", projection_state="untrusted")
        model["diagnostics"] = [message]
        return model
    safety_issue = json_safety_issue(payload)
    if safety_issue:
        message = f"cannot trust semantic-dossier.json: {safety_issue}"
        warnings.append(warning("semantic-dossier", message))
        model.update(state="malformed", projection_state="untrusted")
        model["diagnostics"] = [message]
        return model

    diagnostics = validate_semantic_dossier(payload, workspace)
    diagnostic_text = [
        f"{item.code}: {item.message}"
        + (f" [{';'.join(item.scopes)}]" if item.scopes else "")
        for item in diagnostics[:MAX_ANALYSIS_LIST_ITEMS]
    ]
    for message in diagnostic_text:
        warnings.append(warning("semantic-dossier", message))

    raw_documents = payload.get("documents")
    raw_observations = payload.get("observations")
    raw_rules = payload.get("transfer_rules")
    documents = raw_documents if isinstance(raw_documents, list) else []
    observations = raw_observations if isinstance(raw_observations, list) else []
    rules = raw_rules if isinstance(raw_rules, list) else []
    projected_documents: list[dict[str, str]] = []
    freshness: set[str] = set()
    limitations: list[str] = []
    for document in documents[:MAX_ANALYSIS_LIST_ITEMS]:
        if not isinstance(document, dict):
            continue
        item = {
            "template_source_id": str(document.get("template_source_id", "unknown")),
            "role": str(document.get("role", "unknown")),
            "source_pointer": str(document.get("source_pointer", "unknown")),
            "acquisition_provenance": str(
                document.get("acquisition_provenance", "unknown")
            ),
            "access_state": str(document.get("access_state", "unknown")),
            "source_sha256": str(document.get("source_sha256", "unknown")),
            "freshness": str(document.get("freshness", "unknown")),
            "copyright_limitation": str(
                document.get("access_copyright_limitation", "unknown")
            ),
            "design_only_state": str(document.get("design_only_state", "unknown")),
        }
        projected_documents.append(item)
        freshness.add(item["freshness"])
        limitations.append(item["copyright_limitation"])

    projected_rules: list[dict[str, str]] = []
    for rule in rules[:MAX_ANALYSIS_LIST_ITEMS]:
        if not isinstance(rule, dict):
            continue
        snapshot_value = rule.get("application_snapshot")
        snapshot: dict[str, Any] = (
            snapshot_value if isinstance(snapshot_value, dict) else {}
        )
        item = {
            "rule_id": str(rule.get("rule_id", "unknown")),
            "source_freshness": str(rule.get("source_freshness", "unknown")),
            "surface": str(snapshot.get("surface", "unknown")),
            "resolution": str(snapshot.get("resolution", "unknown")),
            "disposition": str(snapshot.get("disposition", "unknown")),
            "gate_category": str(snapshot.get("gate_category", "unknown")),
            "public_projection_pointer": str(
                snapshot.get("public_projection_pointer", "unknown")
            ),
            "limitation": str(rule.get("limitation", "unknown")),
        }
        projected_rules.append(item)
        freshness.add(item["source_freshness"])
        limitations.append(item["limitation"])

    codes = {item.code for item in diagnostics}
    stale_values = {"stale", "unavailable"}.intersection(freshness)
    if "TEMPLATE_PROJECTION_MISMATCH" in codes:
        state = "projection_mismatch"
        projection_state = "mismatch"
    elif "DOSSIER_SCHEMA" in codes:
        state = "malformed"
        projection_state = "untrusted"
    elif stale_values or {"DOSSIER_FRESHNESS", "DOSSIER_FINGERPRINT"}.intersection(
        codes
    ):
        state = "stale"
        projection_state = "degraded"
    elif diagnostics:
        state = "degraded"
        projection_state = "degraded"
    else:
        state = "current"
        projection_state = "current"

    context = payload.get("analysis_context")
    if isinstance(context, dict):
        for key in ("access_limitations", "uncertainty_note"):
            value = context.get(key)
            if isinstance(value, str) and value:
                limitations.append(value)
    model.update(
        state=state,
        schema=str(payload.get("schema", "unknown")),
        dossier_id=str(payload.get("dossier_id", "unknown")),
        updated_at=str(payload.get("updated_at", "unknown")),
        counts={
            "documents": len(documents),
            "observations": len(observations),
            "rules": len(rules),
        },
        documents=projected_documents,
        rules=projected_rules,
        freshness=sorted(freshness),
        limitations=limitations[:MAX_ANALYSIS_LIST_ITEMS],
        projection_state=projection_state,
        diagnostics=diagnostic_text,
    )
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


def add_validator_warnings(
    workspace: Path, warnings: list[dict[str, str]]
) -> dict[str, list[str]]:
    try:
        report = validate_workspace_report(workspace)
    except Exception as exc:  # pragma: no cover - defensive non-blocking integration.
        message = sanitize_untrusted_text(
            f"validator could not complete: {exc}",
            scope="validator",
            warnings=warnings,
        )
        warnings.append(warning("validator", message))
        return {"errors": [message], "warnings": []}
    errors = [
        sanitize_untrusted_text(str(error), scope="validator", warnings=warnings)
        for error in report.errors
    ]
    validator_warnings = [
        sanitize_untrusted_text(str(item), scope="validator-warning", warnings=warnings)
        for item in report.warnings
    ]
    for error in errors:
        warnings.append(warning("validator", f"validator: {error}"))
    for item in validator_warnings:
        warnings.append(warning("validator-warning", f"validator warning: {item}"))
    return {"errors": errors, "warnings": validator_warnings}


def build_schema_projection(
    contents: dict[str, str], validation: dict[str, list[str]]
) -> dict[str, Any]:
    """Expose schema/migration state without treating legacy readiness as current."""

    text = contents.get(DIMENSION_INDEX, "")
    match = re.search(r"(?im)^\s*-?\s*Workspace schema version\s*:\s*([^\s]+)", text)
    version = match.group(1).strip() if match else "missing"
    codes = {item.split(":", 1)[0] for item in validation["errors"]}
    if "SCHEMA_LEGACY_02" in codes or version == "0.2":
        state = "legacy_migration_required"
        message = (
            "Legacy detailed-readiness migration required: schema 0.2 cannot be "
            "displayed as a current ready state."
        )
    elif "SCHEMA_MISSING" in codes:
        state = "missing"
        message = (
            "Workspace schema marker is missing; detailed readiness is unavailable."
        )
    elif "SCHEMA_INVALID" in codes:
        state = "invalid"
        message = (
            "Workspace schema marker is invalid; detailed readiness is unavailable."
        )
    elif "SCHEMA_UNSUPPORTED" in codes:
        state = "unsupported"
        message = f"Workspace schema {version} is unsupported."
    elif version == "0.3":
        state = "current"
        message = "Schema 0.3 detailed-design projection is available."
    else:
        state = "unknown"
        message = "Workspace schema could not be established."
    return {
        "version": version,
        "state": state,
        "message": message,
        "allows_current_detailed_readiness": state == "current",
    }


def project_public_table(
    contents: dict[str, str],
    filename: str,
    heading: str,
    warnings: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Return a non-authoritative, escaped-at-render table projection."""

    text = contents.get(filename)
    if text is None:
        return []
    fragment = section_content(text, heading)
    if fragment is None:
        warnings.append(
            warning(filename, f"dashboard projection missing heading: {heading}")
        )
        return []
    parsed = parse_dashboard_table(fragment, f"{filename}#{heading}")
    for item in parsed.warnings:
        warnings.append(warning(filename, item))
    return [
        {str(key): str(value) for key, value in row["values"].items()}
        for row in parsed.rows
    ]


def _split_ids(value: str) -> list[str]:
    if not value or value.strip().lower() == "none":
        return []
    return sorted(
        {
            item.strip()
            for item in re.split(r"[;,]", value)
            if item.strip() and item.strip().lower() != "none"
        }
    )


TYPED_RECORD_ID_RE = re.compile(
    r"\b(?:REQ|DEC|M|C|TPL|TRULE|SEC|PAR|FRM|LANG|VIS|EDGE|BUD)-[a-z0-9]+(?:-[a-z0-9]+)*\b"
)
DECISION_ID_RE = re.compile(r"DEC-[a-z0-9]+(?:-[a-z0-9]+)*\Z")
SCOPE_ID_RE = re.compile(r"\bSCOPE-[a-z0-9]+(?:-[a-z0-9]+)*\b")
SCOPE_SUBJECT_RE = re.compile(r"(?<![A-Za-z0-9_-])SCOPE-(?:(?!SCOPE-)[^/|:\s])*")
SCOPE_COLUMNS = {
    "Scope ID",
    "Affected scopes",
    "Affected scope IDs",
    "Scope / conditions",
}


def extract_scope_subjects(message: str) -> set[str]:
    """Capture explicit scope-like subjects without redefining valid scope IDs."""

    trailing_syntax = "\"'`.,;!?)]}"
    if message.startswith("OWNER_GATE:"):
        # OWNER_GATE mixes 04 row subjects with authoritative DEC/PAR/rule records.
        # Its stable 04 grammar is handled before this generic extractor; every
        # other OWNER_GATE diagnostic must remain eligible for record ownership.
        return set()
    return {
        token
        for match in SCOPE_SUBJECT_RE.finditer(message)
        if (token := match.group(0).rstrip(trailing_syntax))
    }


def extract_04_row_subject(code: str, payload: str) -> str | None:
    """Return a complete subject only for stable 04 row diagnostic grammars."""

    if code == "OWNER_GATE":
        for suffix in (
            " owner-gate summary has invalid blockers",
            " owner-gate blockers differ from authoritative 00 scope row",
        ):
            if payload.endswith(suffix):
                return payload[: -len(suffix)]
        duplicate_prefix = "duplicate owner-gate summary key "
        if payload.startswith(duplicate_prefix):
            key = payload[len(duplicate_prefix) :]
            subject, slash, decision_id = key.rpartition("/")
            if (
                slash
                and decision_id
                and not any(
                    character.isspace() or character == "/" for character in decision_id
                )
            ):
                return subject
            return None
        head, separator, _ = payload.rpartition(" summary")
        subject, slash, decision_id = head.rpartition("/")
        if (
            separator
            and slash
            and decision_id
            and not any(
                character.isspace() or character == "/" for character in decision_id
            )
        ):
            return subject
        return None

    if code == "MANIFEST_UNRESOLVED":
        suffixes = (
            " has invalid unresolved record IDs",
            " unresolved IDs differ from authoritative 00 blockers",
        )
    elif code == "TEMPLATE_FIREWALL":
        suffixes = (" template handling is not design_only",)
    elif code == "TEMPLATE_RULE_INCOMPATIBLE":
        suffixes = (
            " combined mode must state semantic reading remains primary",
            " template handling has invalid blocker IDs",
        )
    elif code == "SCOPE_CONTRACT":
        suffixes = (
            " template handling blockers differ from authoritative 00 scope row",
        )
    elif code == "ABSENCE_CONTRACT":
        suffixes = (
            " unresolved row lacks consequence/prohibition",
            " handoff needs substantive prohibition and note",
        )
    else:
        suffixes = ()
    for suffix in suffixes:
        if payload.endswith(suffix):
            return payload[: -len(suffix)]

    if code == "DETAILED_SURFACE_COVERAGE":
        summary_prefix = "summary references unknown "
        if payload.startswith(summary_prefix):
            return payload[len(summary_prefix) :]
        row_prefix = "unknown scope/surface row "
        if payload.startswith(row_prefix):
            encoded_key = payload[len(row_prefix) :]
            if len(encoded_key) > MAX_FRAGMENT_CHARS:
                return None
            try:
                key = ast.literal_eval(encoded_key)
            except (MemoryError, RecursionError, SyntaxError, ValueError):
                return None
            if (
                isinstance(key, tuple)
                and len(key) == 2
                and all(isinstance(item, str) for item in key)
            ):
                return key[0]
    return None


def extract_owner_gate_declared_scope_subject(
    payload: str, declared_scope_ids: set[str]
) -> str | None:
    """Return a strict declared scope only for authoritative OWNER_GATE grammars."""

    missing_suffix = " lacks an Owner Gate Resolution Summary row"
    if payload.endswith(missing_suffix):
        candidate = payload[: -len(missing_suffix)]
    else:
        absent_suffix = " is absent from the 04 owner-gate summary"
        if not payload.endswith(absent_suffix):
            return None
        key = payload[: -len(absent_suffix)]
        candidate, slash, decision_id = key.rpartition("/")
        if not slash or DECISION_ID_RE.fullmatch(decision_id) is None:
            return None
    if candidate not in declared_scope_ids or SCOPE_ID_RE.fullmatch(candidate) is None:
        return None
    return candidate


def build_record_scope_index(
    contents: dict[str, str], scope_ids: set[str]
) -> dict[str, set[str]]:
    """Index typed records through exact scope columns, never prose inference."""

    index: dict[str, set[str]] = {}
    for filename, text in contents.items():
        if filename == FINAL_PACK:
            # 04 is a compact mirror/handoff surface, never a record-to-scope
            # authority for assigning validator diagnostics.
            continue
        headings = [
            match.group(1).strip()
            for match in re.finditer(r"^##\s+(.+?)\s*$", text, re.MULTILINE)
        ]
        for heading in headings:
            fragment = section_content(text, heading)
            if fragment is None:
                continue
            table = parse_dashboard_table(fragment, heading)
            for row in table.rows:
                values = row["values"]
                row_scopes: set[str] = set()
                for column in SCOPE_COLUMNS.intersection(values):
                    row_scopes.update(SCOPE_ID_RE.findall(str(values[column])))
                row_scopes.intersection_update(scope_ids)
                if not row_scopes:
                    continue
                for value in values.values():
                    for record_id in TYPED_RECORD_ID_RE.findall(str(value)):
                        index.setdefault(record_id, set()).update(row_scopes)
    return index


def build_validation_projection(
    errors: list[str],
    contents: dict[str, str],
    scope_ids: set[str],
    known_orphan_scope_ids: set[str],
    cardinality_attribution: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    record_scopes = build_record_scope_index(contents, scope_ids)
    diagnostics: list[dict[str, Any]] = []
    by_scope = {scope_id: [] for scope_id in sorted(scope_ids)}
    global_ids: list[str] = []
    orphan_ids: list[str] = []
    for index, message in enumerate(errors, 1):
        diagnostic_id = f"VDIAG-{index:03d}"
        code, _, payload = message.partition(":")
        payload = payload.removeprefix(" ")
        policy = cardinality_attribution.get(code, {})
        policy_orphans = set(policy.get("orphan_scope_ids", []))
        row_subject = extract_04_row_subject(code, payload)
        typed_orphan = (
            row_subject
            if row_subject is not None and row_subject in known_orphan_scope_ids
            else None
        )
        authoritative_scope_subject = (
            extract_owner_gate_declared_scope_subject(payload, scope_ids)
            if code == "OWNER_GATE" and row_subject is None
            else None
        )
        typed_declared = (
            row_subject
            if row_subject is not None and row_subject in scope_ids
            else authoritative_scope_subject
        )
        explicit_subjects: set[str] = set()
        affected = {typed_declared} if typed_declared is not None else set()
        unknown_scopes = {typed_orphan} if typed_orphan is not None else set()
        is_orphan_only = typed_orphan is not None
        if typed_orphan is None and typed_declared is None:
            if code != "OWNER_GATE" and (
                explicit_subjects := extract_scope_subjects(message)
            ):
                affected.update(explicit_subjects.intersection(scope_ids))
                unknown_scopes.update(explicit_subjects - scope_ids)
                is_orphan_only = bool(unknown_scopes) and not affected
            elif policy.get("global"):
                affected = set()
            elif policy.get("affected_scope_ids"):
                affected = set(policy["affected_scope_ids"]).intersection(scope_ids)
            elif policy.get("orphan_only"):
                is_orphan_only = True
                unknown_scopes.update(policy_orphans)
            else:
                for record_id in TYPED_RECORD_ID_RE.findall(message):
                    affected.update(record_scopes.get(record_id, set()))
        # Only a code-aware stable 04 row subject can activate the orphan inventory.
        # Record-only OWNER_GATE and ordinary prose never scan that inventory.
        has_explicit_identity = bool(
            typed_orphan is not None or typed_declared is not None or explicit_subjects
        )
        is_global = (
            bool(policy.get("global")) if not has_explicit_identity else False
        ) or (not affected and not unknown_scopes and not is_orphan_only)
        item = {
            "diagnostic_id": diagnostic_id,
            "code": code,
            "affected_scope_ids": sorted(affected),
            "global": is_global,
            "orphan_scope_ids": sorted(unknown_scopes),
        }
        diagnostics.append(item)
        if is_global:
            global_ids.append(diagnostic_id)
        elif (unknown_scopes or is_orphan_only) and not affected:
            orphan_ids.append(diagnostic_id)
        for scope_id in affected:
            by_scope[scope_id].append(diagnostic_id)
    return {
        "diagnostics": diagnostics,
        "by_scope": by_scope,
        "global_diagnostic_ids": global_ids,
        "orphan_diagnostic_ids": orphan_ids,
    }


def build_design_pack_projection(
    contents: dict[str, str],
    schema: dict[str, Any],
    validation: dict[str, list[str]],
    warnings: list[dict[str, str]],
) -> dict[str, Any]:
    """Project 00/03 authority and label 04 strictly as a non-authority mirror."""

    table_specs = {
        "scope": (DIMENSION_INDEX, "Writing Scopes"),
        "decisions": ("00_PROJECT_ROUTE.md", "Decision Records"),
        "coverage": (FINAL_PACK, "Detailed Surface Coverage"),
        "summary": (FINAL_PACK, "Detailed Coverage Summary"),
        "gates": (FINAL_PACK, "Owner Gate Resolution Summary"),
        "handling": (FINAL_PACK, "Template Analysis Handling"),
        "unresolved": (FINAL_PACK, "Unresolved and Downstream Prohibitions"),
        "handoff": (FINAL_PACK, "Scoped Handoff"),
    }
    tables = {
        key: project_public_table(contents, filename, heading, warnings)
        for key, (filename, heading) in table_specs.items()
    }
    scope_ids = sorted(
        {row.get("Scope ID", "") for row in tables["scope"] if row.get("Scope ID")}
    )
    scope_id_set = set(scope_ids)
    mirror_table_keys = tuple(
        key for key, (filename, _) in table_specs.items() if filename == FINAL_PACK
    )
    known_orphan_scope_ids = {
        row_scope
        for key in mirror_table_keys
        for row in tables[key]
        if (row_scope := row.get("Scope ID", "")) and row_scope not in scope_id_set
    }
    for key in mirror_table_keys:
        for row in tables[key]:
            row_scope = row.get("Scope ID", "")
            if row_scope and row_scope not in scope_id_set:
                warnings.append(
                    warning(
                        FINAL_PACK,
                        f"orphan 04 mirror row ignored for undeclared scope {row_scope}",
                    )
                )
    cardinality_attribution: dict[str, dict[str, Any]] = {}
    final_pack_text = contents.get(FINAL_PACK, "")
    for key, code in (
        ("handling", "TEMPLATE_HANDLING_CARDINALITY"),
        ("handoff", "HANDOFF_SCOPE_CARDINALITY"),
        ("unresolved", "MANIFEST_UNRESOLVED"),
    ):
        heading = table_specs[key][1]
        heading_count = len(
            re.findall(
                rf"^##\s+{re.escape(heading)}\s*$", final_pack_text, re.MULTILINE
            )
        )
        declared_counts = {
            scope_id: sum(row.get("Scope ID") == scope_id for row in tables[key])
            for scope_id in scope_ids
        }
        orphan_scope_ids = {
            row.get("Scope ID", "")
            for row in tables[key]
            if row.get("Scope ID") and row.get("Scope ID") not in scope_id_set
        }
        affected_scope_ids = {
            scope_id for scope_id, count in declared_counts.items() if count != 1
        }
        cardinality_attribution[code] = {
            "global": heading_count != 1,
            "affected_scope_ids": sorted(affected_scope_ids),
            "orphan_only": bool(orphan_scope_ids) and not affected_scope_ids,
            "orphan_scope_ids": sorted(orphan_scope_ids),
        }
    validation_projection = build_validation_projection(
        validation["errors"],
        contents,
        scope_id_set,
        known_orphan_scope_ids,
        cardinality_attribution,
    )
    decision_by_id = {
        row.get("Decision ID", ""): row
        for row in tables["decisions"]
        if row.get("Decision ID")
    }
    scopes: list[dict[str, Any]] = []
    for scope_id in scope_ids:
        scope_row = next(
            (row for row in tables["scope"] if row.get("Scope ID") == scope_id), {}
        )
        coverage_by_surface = {
            row.get("Surface", ""): row
            for row in tables["coverage"]
            if row.get("Scope ID") == scope_id
        }
        coverage = []
        for surface in sorted(CANONICAL_SURFACES):
            row = coverage_by_surface.get(surface)
            if row is None:
                row = {
                    "Surface": surface,
                    "Scope ID": scope_id,
                    "Handling (`satisfied&#124;not_applicable`)": "missing",
                    "Record count": "0",
                    "Authoritative pointer": "none",
                    "Rationale/blocker": "coverage row missing",
                }
            coverage.append(row)
        summary = next(
            (row for row in tables["summary"] if row.get("Scope ID") == scope_id), {}
        )
        authoritative_gates = [
            row
            for row in tables["decisions"]
            if scope_id in _split_ids(row.get("Affected scopes", ""))
        ]
        gate_mirrors: list[dict[str, str]] = []
        authoritative_blockers = _split_ids(scope_row.get("Remaining blocker", ""))
        for row in tables["gates"]:
            if row.get("Scope ID") != scope_id:
                continue
            decision = decision_by_id.get(row.get("Decision ID", ""))
            mirror_valid = bool(
                decision
                and decision.get("Gate category") == row.get("Gate category")
                and decision.get("Resolution") == row.get("Resolution")
                and scope_id in _split_ids(decision.get("Affected scopes", ""))
                and _split_ids(row.get("Active blocker IDs", ""))
                == authoritative_blockers
            )
            projected = dict(row)
            projected["Mirror state"] = (
                "valid_mirror" if mirror_valid else "invalid_mirror"
            )
            gate_mirrors.append(projected)
            if not mirror_valid:
                warnings.append(
                    warning(
                        FINAL_PACK,
                        f"invalid_mirror: 04 owner-gate row disagrees with 00 authority for {scope_id}",
                    )
                )
        handling = next(
            (row for row in tables["handling"] if row.get("Scope ID") == scope_id), {}
        )
        unresolved = next(
            (row for row in tables["unresolved"] if row.get("Scope ID") == scope_id), {}
        )
        handoff = next(
            (row for row in tables["handoff"] if row.get("Scope ID") == scope_id), {}
        )
        local_diagnostics = validation_projection["by_scope"].get(scope_id, [])
        global_diagnostics = validation_projection["global_diagnostic_ids"]
        declared = scope_row.get("Readiness", "missing")
        if not schema["allows_current_detailed_readiness"]:
            effective = "migration_required"
        elif global_diagnostics or local_diagnostics:
            effective = "mechanically_blocked"
        else:
            effective = declared
        scopes.append(
            {
                "scope_id": scope_id,
                "writing_surface": scope_row.get("Writing surface", "unknown"),
                "intended_output": scope_row.get("Intended output", "unknown"),
                "declared_readiness": declared,
                "dashboard_readiness": effective,
                "current_detailed_ready": (
                    effective == "writer-ready" and schema["state"] == "current"
                ),
                "blocker_ids": authoritative_blockers,
                "mechanical_diagnostic_ids": [
                    *global_diagnostics,
                    *local_diagnostics,
                ],
                "coverage": coverage,
                "summary": summary,
                "gates": authoritative_gates,
                "gate_mirrors": gate_mirrors,
                "template_handling": handling,
                "unresolved": unresolved,
                "handoff": handoff,
            }
        )
    gate_rows = []
    for category in sorted(FOUR_GATES):
        matching = [
            row for row in tables["decisions"] if row.get("Gate category") == category
        ]
        gate_rows.append(
            {
                "category": category,
                "state": (
                    "active"
                    if any(
                        row.get("Resolution") not in {"confirmed", "rejected"}
                        for row in matching
                    )
                    else "resolved"
                    if matching
                    else "not_declared"
                ),
                "rows": matching,
            }
        )
    return {
        "authority_note": (
            "Declared structural coverage only; 00 owns readiness, 03 owns detailed "
            "design, and 04 is a pointer-only non-authority manifest."
        ),
        "surface_names": sorted(CANONICAL_SURFACES),
        "owner_gate_categories": sorted(FOUR_GATES),
        "owner_gates": gate_rows,
        "validation_projection": validation_projection,
        "template_modes": sorted(TEMPLATE_MODES),
        "scopes": scopes,
    }


def build_analyzer_projection(
    template_analysis: dict[str, Any], _warnings: list[dict[str, str]]
) -> dict[str, Any]:
    """Expose only the analyzer bundle's approved mechanical status projection."""

    candidates = template_analysis.get("candidates", [])
    modes = {
        str(item.get("effective_analysis_mode"))
        for item in candidates
        if isinstance(item, dict)
        and item.get("effective_analysis_mode") not in {None, "N/A"}
    }
    provenance = template_analysis.get("provenance", {})
    if isinstance(provenance, dict) and provenance.get("effective_analysis_mode"):
        modes.add(str(provenance["effective_analysis_mode"]))
    comparability = {
        str(item.get("comparability"))
        for item in candidates
        if isinstance(item, dict) and item.get("comparability")
    }
    actions = {
        str(item.get("candidate_action"))
        for item in candidates
        if isinstance(item, dict) and item.get("candidate_action")
    }
    return {
        "state": str(template_analysis.get("state", "absent")),
        "identity": template_analysis.get("identity", {}),
        "effective_modes": sorted(modes),
        "comparability": sorted(comparability) or ["N/A"],
        "candidate_actions": sorted(actions) or ["N/A"],
        "selected_metric_ids": template_analysis.get("selected_metric_ids", []),
        "metric_summaries": template_analysis.get("metric_summaries", []),
        "candidates": candidates,
        "provenance": provenance,
        "violations": template_analysis.get("violations", []),
        "note": (
            "Optional allowlisted analyzer mechanics only; N/A is neutral, raw trees "
            "are never retained, and this remains separate from semantic provenance."
        ),
    }


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
    validation = add_validator_warnings(workspace, global_warnings)
    schema = build_schema_projection(contents, validation)
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
    analyzer_projection = build_analyzer_projection(template_analysis, global_warnings)
    semantic_dossier = load_semantic_dossier(workspace, global_warnings)
    design_pack = build_design_pack_projection(
        contents, schema, validation, global_warnings
    )

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
        "validation": validation,
        "schema": schema,
        "design_pack": design_pack,
        "semantic_dossier": semantic_dossier,
        "analyzer_projection": analyzer_projection,
        "template_analysis": template_analysis,
    }


def safe_json(data: Any) -> str:
    text = json.dumps(data, ensure_ascii=False, sort_keys=True, allow_nan=False)
    return (
        text.replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def render_analyzer_bundle_details(model: dict[str, Any]) -> str:
    analysis = model.get("template_analysis", {})
    artifact_rows = "".join(
        "<tr>"
        f"<td>{html.escape(str(item.get('label', 'unknown')))}</td>"
        f"<td>{html.escape(str(item.get('state', 'absent')))}</td>"
        f"<td>{html.escape(str(item.get('schema', 'unknown')))}</td>"
        f"<td>{html.escape(str(item.get('path', 'unknown')))}</td>"
        "</tr>"
        for item in analysis.get("artifacts", {}).values()
    )
    metric_rows = (
        "".join(
            "<tr>"
            f"<td>{html.escape(str(item.get('metric_id', 'unknown')))}</td>"
            f"<td>{html.escape(str(item.get('valid_n', 'N/A')))}</td>"
            f"<td>{html.escape(str(item.get('eligible_n', 'N/A')))}</td>"
            f"<td>{html.escape(str(item.get('missingness', 'N/A')))}</td>"
            f"<td>{html.escape(str(item.get('median', 'N/A')))}</td>"
            f"<td>{html.escape(str(item.get('p25', 'N/A')))}</td>"
            f"<td>{html.escape(str(item.get('p75', 'N/A')))}</td>"
            "</tr>"
            for item in analysis.get("metric_summaries", [])
        )
        or '<tr><td colspan="7">No approved registered metric summary.</td></tr>'
    )
    candidate_rows = (
        "".join(
            "<tr>"
            f"<td>{html.escape(str(item.get('candidate_id', 'unknown')))}</td>"
            f"<td>{html.escape(', '.join(item.get('metric_ids', [])) or 'N/A')}</td>"
            f"<td>{html.escape(str(item.get('partition', 'unknown')))}</td>"
            f"<td>{html.escape(str(item.get('valid_n', 'N/A')))}</td>"
            f"<td>{html.escape(str(item.get('missingness', 'N/A')))}</td>"
            f"<td>{html.escape(str(item.get('metric_effective_analysis_mode', 'N/A')))}</td>"
            f"<td>{html.escape(str(item.get('comparability', 'N/A')))}</td>"
            f"<td>{html.escape(str(item.get('candidate_action', 'N/A')))}</td>"
            "</tr>"
            for item in analysis.get("candidates", [])
        )
        or '<tr><td colspan="8">No approved candidate mechanics.</td></tr>'
    )
    return (
        '<div class="analysis-grid">'
        '<article class="analysis-artifact"><h3>Required analyzer bundle</h3>'
        '<div class="analysis-table-wrap"><table><thead><tr>'
        "<th>Artifact</th><th>State</th><th>Schema</th><th>Path</th>"
        f"</tr></thead><tbody>{artifact_rows}</tbody></table></div></article>"
        '<article class="analysis-artifact"><h3>Registered selected metrics</h3>'
        '<div class="analysis-table-wrap"><table><thead><tr>'
        "<th>Metric</th><th>valid_n</th><th>eligible_n</th><th>Missing</th>"
        "<th>Median</th><th>p25</th><th>p75</th>"
        f"</tr></thead><tbody>{metric_rows}</tbody></table></div></article>"
        '<article class="analysis-artifact"><h3>Candidate mechanical states</h3>'
        '<div class="analysis-table-wrap"><table><thead><tr>'
        "<th>ID</th><th>Metrics</th><th>Partition</th><th>valid_n</th>"
        "<th>Missing</th><th>Effective mode</th><th>Comparability</th><th>Action</th>"
        f"</tr></thead><tbody>{candidate_rows}</tbody></table></div></article>"
        "</div>"
    )


def _row_value(row: dict[str, Any], prefix: str, default: str = "unknown") -> str:
    for key, value in row.items():
        if str(key).startswith(prefix):
            return str(value)
    return default


def render_design_pack_projection(model: dict[str, Any]) -> str:
    pack = model.get("design_pack", {})
    scope_blocks: list[str] = []
    for scope in pack.get("scopes", []):
        summary = scope.get("summary", {})
        summary_fields = [
            ("Sections", "Section count"),
            ("Paragraphs", "Paragraph count"),
            ("Important paragraphs", "Important paragraph count"),
            ("Frames", "Frame count"),
            ("Language", "Language count"),
            ("Visuals", "Visual count"),
            ("Edges", "Edge count"),
            ("Rules", "Rule count"),
            ("Budgets", "Budget count"),
        ]
        counts = " · ".join(
            f"{label}: {html.escape(str(summary.get(key, 'missing')))}"
            for label, key in summary_fields
        )
        coverage_rows = "".join(
            "<tr>"
            f"<td>{html.escape(str(row.get('Surface', 'unknown')))}</td>"
            f"<td>{html.escape(_row_value(row, 'Handling', 'missing'))}</td>"
            f"<td>{html.escape(str(row.get('Record count', '0')))}</td>"
            f"<td>{html.escape(str(row.get('Authoritative pointer', 'none')))}</td>"
            f"<td>{html.escape(str(row.get('Rationale/blocker', 'none')))}</td>"
            "</tr>"
            for row in scope.get("coverage", [])
        )
        gate_rows = (
            "".join(
                "<tr>"
                f"<td>{html.escape(str(row.get('Gate category', 'unknown')))}</td>"
                f"<td>{html.escape(str(row.get('Resolution', 'unknown')))}</td>"
                f"<td>{html.escape(str(row.get('Decision ID', 'none')))}</td>"
                f"<td>{html.escape(str(row.get('Affected scopes', 'none')))}</td>"
                "</tr>"
                for row in scope.get("gates", [])
            )
            or '<tr><td colspan="4">No scope-specific owner-gate row declared.</td></tr>'
        )
        mirror_rows = (
            "".join(
                "<tr>"
                f"<td>{html.escape(str(row.get('Mirror state', 'invalid_mirror')))}</td>"
                f"<td>{html.escape(str(row.get('Gate category', 'unknown')))}</td>"
                f"<td>{html.escape(str(row.get('Resolution', 'unknown')))}</td>"
                f"<td>{html.escape(str(row.get('Decision ID', 'none')))}</td>"
                f"<td>{html.escape(str(row.get('Active blocker IDs', 'none')))}</td>"
                "</tr>"
                for row in scope.get("gate_mirrors", [])
            )
            or '<tr><td colspan="5">No 04 owner-gate mirror row.</td></tr>'
        )
        handling = scope.get("template_handling", {})
        current_badge = (
            '<span class="pill status-filled">current detailed-ready</span>'
            if scope.get("current_detailed_ready")
            else ""
        )
        scope_blocks.append(
            '<article class="scope-card">'
            f"<h3>{html.escape(str(scope.get('scope_id', 'unknown')))} · "
            f"{html.escape(str(scope.get('writing_surface', 'unknown')))}</h3>"
            '<div class="badge-line">'
            f'<span class="pill">declared: {html.escape(str(scope.get("declared_readiness", "missing")))}</span>'
            f'<span class="pill">dashboard: {html.escape(str(scope.get("dashboard_readiness", "unknown")))}</span>'
            f"{current_badge}</div>"
            f"<p><strong>Scope blockers:</strong> {html.escape(', '.join(scope.get('blocker_ids', [])) or 'none')}</p>"
            f"<p><strong>Mechanical diagnostics:</strong> {html.escape(', '.join(scope.get('mechanical_diagnostic_ids', [])) or 'none')}</p>"
            f'<p class="small">{counts}</p>'
            '<div class="analysis-table-wrap"><table><thead><tr>'
            "<th>Detailed surface</th><th>Handling</th><th>Records</th>"
            "<th>03 authority pointer</th><th>Rationale/blocker</th>"
            f"</tr></thead><tbody>{coverage_rows}</tbody></table></div>"
            "<h4>Owner-gate rows for this scope</h4>"
            '<div class="analysis-table-wrap"><table><thead><tr>'
            "<th>Category</th><th>Resolution</th><th>Decision</th><th>Affected scopes</th>"
            f"</tr></thead><tbody>{gate_rows}</tbody></table></div>"
            "<h4>04 owner-gate mirror provenance</h4>"
            '<div class="analysis-table-wrap"><table><thead><tr>'
            "<th>Mirror state</th><th>Category</th><th>Resolution</th><th>Decision</th><th>Mirrored blockers</th>"
            f"</tr></thead><tbody>{mirror_rows}</tbody></table></div>"
            "<h4>Template-analysis handling</h4>"
            f'<p><span class="pill">{html.escape(str(handling.get("Mode", "missing")))}</span> '
            f"firewall: {html.escape(str(handling.get('Firewall state', 'unknown')))}</p>"
            f'<p class="small">{html.escape(str(handling.get("Rationale", "No handling row.")))}</p>'
            "</article>"
        )
    if not scope_blocks:
        scope_blocks.append(
            '<p class="small">No readable scope projection is available; inspect local warnings and the six public files.</p>'
        )
    gate_legend = "".join(
        "<tr>"
        f"<td>{html.escape(str(item.get('category', 'unknown')))}</td>"
        f"<td>{html.escape(str(item.get('state', 'unknown')))}</td>"
        f"<td>{len(item.get('rows', []))}</td>"
        "</tr>"
        for item in pack.get("owner_gates", [])
    )
    modes = " · ".join(str(item) for item in pack.get("template_modes", []))
    return (
        '<section class="design-pack-panel">'
        "<h2>Declared structural coverage / 声明式结构覆盖</h2>"
        f"<p>{html.escape(str(pack.get('authority_note', 'Non-authoritative projection.')))}</p>"
        '<p class="small">This dashboard reports contract presence and declared counts; '
        "it does not assign a quality, venue-fit, completeness, or acceptance score.</p>"
        "<h3>Four owner-gate categories</h3>"
        '<div class="analysis-table-wrap"><table><thead><tr>'
        "<th>Category</th><th>Projected state</th><th>Declared rows</th>"
        f"</tr></thead><tbody>{gate_legend}</tbody></table></div>"
        f'<p class="small">Exact handling modes: {html.escape(modes)}</p>'
        + "".join(scope_blocks)
        + "</section>"
    )


def render_semantic_dossier(model: dict[str, Any]) -> str:
    dossier = model.get("semantic_dossier", {})
    counts = dossier.get("counts", {})
    document_rows = (
        "".join(
            "<tr>"
            f"<td>{html.escape(str(item.get('template_source_id', 'unknown')))}</td>"
            f"<td>{html.escape(str(item.get('role', 'unknown')))}</td>"
            f"<td>{html.escape(str(item.get('source_pointer', 'unknown')))}</td>"
            f"<td>{html.escape(str(item.get('acquisition_provenance', 'unknown')))}</td>"
            f"<td>{html.escape(str(item.get('access_state', 'unknown')))}</td>"
            f"<td>{html.escape(str(item.get('freshness', 'unknown')))}</td>"
            f"<td>{html.escape(str(item.get('copyright_limitation', 'unknown')))}</td>"
            "</tr>"
            for item in dossier.get("documents", [])
        )
        or '<tr><td colspan="7">No trusted semantic document projection.</td></tr>'
    )
    rule_rows = (
        "".join(
            "<tr>"
            f"<td>{html.escape(str(item.get('rule_id', 'unknown')))}</td>"
            f"<td>{html.escape(str(item.get('source_freshness', 'unknown')))}</td>"
            f"<td>{html.escape(str(item.get('surface', 'unknown')))}</td>"
            f"<td>{html.escape(str(item.get('resolution', 'unknown')))}</td>"
            f"<td>{html.escape(str(item.get('disposition', 'unknown')))}</td>"
            f"<td>{html.escape(str(item.get('gate_category', 'unknown')))}</td>"
            f"<td>{html.escape(str(item.get('public_projection_pointer', 'unknown')))}</td>"
            "</tr>"
            for item in dossier.get("rules", [])
        )
        or '<tr><td colspan="7">No trusted rule projection.</td></tr>'
    )
    limitations = (
        "".join(
            f"<li>{html.escape(str(item))}</li>"
            for item in dossier.get("limitations", [])
        )
        or "<li>N/A</li>"
    )
    diagnostics = (
        "".join(
            f"<li>{html.escape(str(item))}</li>"
            for item in dossier.get("diagnostics", [])
        )
        or "<li>none</li>"
    )
    return (
        '<section class="analysis-panel">'
        "<h2>Semantic dossier provenance / 语义档案来源</h2>"
        f"<p>{html.escape(str(dossier.get('note', 'Design-only hidden dossier projection.')))}</p>"
        '<div class="badge-line">'
        f'<span class="pill">state: {html.escape(str(dossier.get("state", "absent")))}</span>'
        f'<span class="pill">projection: {html.escape(str(dossier.get("projection_state", "absent")))}</span>'
        f'<span class="pill">schema: {html.escape(str(dossier.get("schema", "unknown")))}</span>'
        f'<span class="pill">freshness: {html.escape(", ".join(dossier.get("freshness", [])) or "N/A")}</span>'
        "</div>"
        f"<p>Documents: {html.escape(str(counts.get('documents', 0)))} · "
        f"Observations: {html.escape(str(counts.get('observations', 0)))} · "
        f"Rules: {html.escape(str(counts.get('rules', 0)))}</p>"
        '<div class="analysis-table-wrap"><table><thead><tr>'
        "<th>Source ID</th><th>Role</th><th>Pointer</th><th>Acquisition provenance</th>"
        "<th>Access</th><th>Freshness</th><th>Copyright/access limitation</th>"
        f"</tr></thead><tbody>{document_rows}</tbody></table></div>"
        '<div class="analysis-table-wrap"><table><thead><tr>'
        "<th>Rule</th><th>Freshness</th><th>Surface</th><th>Resolution</th>"
        "<th>Disposition</th><th>Gate</th><th>Public projection pointer</th>"
        f"</tr></thead><tbody>{rule_rows}</tbody></table></div>"
        f"<details><summary>Limitations</summary><ul>{limitations}</ul></details>"
        f"<details><summary>Local dossier warnings</summary><ul>{diagnostics}</ul></details>"
        "</section>"
    )


def render_analyzer_projection(model: dict[str, Any]) -> str:
    analyzer = model.get("analyzer_projection", {})
    identity = analyzer.get("identity", {})
    identity_text = " · ".join(
        f"{key}={identity.get(key, 'N/A')}" for key in TEMPLATE_ANALYSIS_IDENTITY_KEYS
    )
    return (
        '<section class="analysis-panel">'
        "<h2>Optional analyzer status / 可选分析器状态</h2>"
        f"<p>{html.escape(str(analyzer.get('note', 'Optional and separate.')))}</p>"
        '<div class="badge-line">'
        f'<span class="pill">state: {html.escape(str(analyzer.get("state", "absent")))}</span>'
        f'<span class="pill">effective mode: {html.escape(", ".join(analyzer.get("effective_modes", [])) or "N/A")}</span>'
        f'<span class="pill">comparability: {html.escape(", ".join(analyzer.get("comparability", ["N/A"])))}</span>'
        f'<span class="pill">action: {html.escape(", ".join(analyzer.get("candidate_actions", ["N/A"])))}</span>'
        "</div>"
        f'<p class="small">Identity: {html.escape(identity_text)}</p>'
        "</section>"
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
    analysis_html = render_analyzer_bundle_details(model)
    schema = model.get("schema", {})
    schema_html = (
        '<section class="schema-panel">'
        "<h2>Schema and migration status</h2>"
        '<div class="badge-line">'
        f'<span class="pill">schema: {html.escape(str(schema.get("version", "unknown")))}</span>'
        f'<span class="pill">state: {html.escape(str(schema.get("state", "unknown")))}</span>'
        "</div>"
        f"<p><strong>{html.escape(str(schema.get('message', 'Schema status unavailable.')))}</strong></p>"
        "</section>"
    )
    design_pack_html = render_design_pack_projection(model)
    dossier_html = render_semantic_dossier(model)
    analyzer_status_html = render_analyzer_projection(model)

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
.schema-panel, .design-pack-panel {{ grid-column: 1 / -1; }}
.scope-card {{ border-top: 1px solid var(--line); margin-top: 16px; padding-top: 4px; }}
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
  <p class="contract">结构化、只读、离线静态视图。它读取 yxj-paper-os 六个 Markdown 工作区文件，并仅在完整同身份 analyzer bundle 存在时显示严格白名单机械投影；只写 dashboard.html，不修改 Markdown 或分析产物，不做语义/期刊适配评分，也不声明论文或投稿就绪。</p>
  <div class="badge-line">
    <span class="badge">输出：{html.escape(model["artifact"])}</span>
    <span class="badge">结构状态：{html.escape(model["readiness"]["label"])}</span>
    <span class="badge">警告：{warning_count}</span>
  </div>
</header>
<main class="layout">
  {schema_html}
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
  {design_pack_html}
  {dossier_html}
  {analyzer_status_html}
  <section class="analysis-panel">
    <h2>目标期刊 / 主题模板统计</h2>
    <p>{html.escape(str(template_analysis.get("note", "Optional writing-design analysis only.")))}</p>
    <p class="small">状态：{html.escape(str(template_analysis.get("state", "absent")))}。Malformed、stale、unsupported 或缺失产物仅降级显示，不会自动投影为写作规则。</p>
    {analysis_html}
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
    except (OSError, UnicodeError) as exc:
        raise RuntimeError(
            f"cannot write/replace dashboard output safely: {target}: {exc}"
        ) from exc
    finally:
        if temp_path is not None:
            with suppress(FileNotFoundError):
                temp_path.unlink()
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
