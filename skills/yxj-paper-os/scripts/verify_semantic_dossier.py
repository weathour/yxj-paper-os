#!/usr/bin/env python3
"""Bounded stdlib validator/writer for the hidden semantic dossier contract."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import tempfile
from typing import Any, Iterable

from template_design_contract import validate_template_rule

DOSSIER_FILENAME = "semantic-dossier.json"
SCHEMA_NAME = "yxj-template-semantic-dossier/1.0"
WORKSPACE_SCHEMA = "0.3"
TOP_REQUIRED = {
    "schema",
    "dossier_id",
    "workspace_schema",
    "design_question",
    "scope_ids",
    "analysis_context",
    "documents",
    "observations",
    "transfer_rules",
    "updated_at",
}
CONTEXT_REQUIRED = {
    "method",
    "agent_identity",
    "model_identity",
    "prompt_identity",
    "access_limitations",
    "generic_knowledge_fallback",
    "uncertainty_note",
}
DOCUMENT_REQUIRED = {
    "template_source_id",
    "title",
    "source_pointer",
    "acquisition_provenance",
    "role",
    "design_question",
    "design_relevance",
    "access_state",
    "local_derivative_pointer",
    "source_sha256",
    "accessed_at",
    "access_copyright_limitation",
    "freshness",
    "semantic_reading_eligible",
    "design_only_state",
}
DOCUMENT_OPTIONAL = {"analyzer_correlation"}
OBSERVATION_REQUIRED = {
    "observation_id",
    "template_source_id",
    "locator",
    "observed_pattern",
    "semantic_interpretation",
    "uncertainty",
    "non_transfer_note",
    "status",
}
OBSERVATION_OPTIONAL = {"minimal_excerpt"}
RULE_REQUIRED = {
    "rule_id",
    "observation_ids",
    "grounding_kind",
    "rule_kind",
    "candidate_transfer",
    "suggested_disposition",
    "origin",
    "limitation",
    "dependency_fingerprint",
    "source_freshness",
    "application_snapshot",
}
SNAPSHOT_REQUIRED = {
    "affected_scope_ids",
    "surface",
    "resolution",
    "disposition",
    "gate_category",
    "decision_id",
    "decision_pointer",
    "public_projection_pointer",
}
ID_PATTERNS = {
    "dossier": re.compile(r"^TSD-[a-z0-9]+(?:-[a-z0-9]+)*$"),
    "document": re.compile(r"^TPL-[a-z0-9]+(?:-[a-z0-9]+)*$"),
    "observation": re.compile(r"^TOBS-[a-z0-9]+(?:-[a-z0-9]+)*$"),
    "rule": re.compile(r"^TRULE-[a-z0-9]+(?:-[a-z0-9]+)*$"),
    "scope": re.compile(r"^SCOPE-[a-z0-9]+(?:-[a-z0-9]+)*$"),
    "decision": re.compile(r"^DEC-[a-z0-9]+(?:-[a-z0-9]+)*$"),
}
ROLES = {
    "official_venue",
    "target_topic",
    "article_form",
    "time_cohort",
    "control",
    "exemplar",
}
ACCESS_STATES = {
    "full_text",
    "owner_derivative",
    "metadata_only",
    "snippet_only",
    "inaccessible",
}
FRESHNESS = {"verified_local_current", "recorded_at_access", "stale", "unavailable"}
LOCATOR_KINDS = {
    "section",
    "paragraph",
    "figure",
    "table",
    "caption",
    "document",
    "metadata",
}
RULE_KINDS = {"candidate_pattern", "soft_band", "sequence", "presence", "watch_only"}
DISPOSITIONS = {
    "candidate",
    "adopted",
    "adapted",
    "rejected",
    "deliberate_divergence",
    "not_applicable",
}
SUGGESTED = DISPOSITIONS | {"none"}
RESOLUTIONS = {"confirmed", "candidate", "unresolved", "conflicted", "rejected"}
GATES = {
    "scientific_commitment",
    "argument_spine",
    "material_local_tradeoff",
    "deliberate_divergence",
    "not_applicable",
}
ACTIVE_DISPOSITIONS = {"adopted", "adapted", "deliberate_divergence"}
PUBLIC_FILES = {
    "00_DIMENSION_INDEX.md",
    "00_PROJECT_ROUTE.md",
    "01_MATERIALS_INVENTORY.md",
    "02_CLAIM_EVIDENCE_BOUNDARY.md",
    "03_WRITING_STRUCTURE.md",
    "04_WRITING_DESIGN_PACK.md",
}
BANNED_COPY_FIELDS = {
    "document_body",
    "full_text",
    "copied_body",
    "paper_text",
    "long_excerpt",
}
OBSERVATION_TEXT_LIMITS = {
    "observed_pattern": 2000,
    "semantic_interpretation": 2000,
    "uncertainty": 1000,
    "non_transfer_note": 1000,
    "minimal_excerpt": 500,
}
SCHEMA_CANONICAL_SHA256 = (
    "8ddc79507be647a3fe080cd8f6d0270a3819b4d63a130414e2ed53d3f7d47aee"
)


@dataclass(frozen=True)
class DossierDiagnostic:
    code: str
    message: str
    scopes: tuple[str, ...] = ()


class DossierValidationError(ValueError):
    def __init__(self, diagnostics: list[DossierDiagnostic]):
        self.diagnostics = diagnostics
        super().__init__(
            "; ".join(f"{item.code}: {item.message}" for item in diagnostics)
        )


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _is_nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_enum(value: Any, allowed: set[str]) -> bool:
    return isinstance(value, str) and value in allowed


def _valid_unique_string_list(
    value: Any, pattern: re.Pattern[str] | None = None
) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(
            isinstance(item, str)
            and (pattern is None or pattern.fullmatch(item) is not None)
            for item in value
        )
        and len(value) == len(set(value))
    )


def _normal_path(value: str) -> str | None:
    if value == "none":
        return value
    if re.match(r"^[a-z][a-z0-9+.-]*://", value, re.I):
        return value
    if "\\" in value:
        return None
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts:
        return None
    parts = [part for part in pure.parts if part not in {"", "."}]
    return "/".join(parts) if parts else None


def _public_pointer(value: Any) -> bool:
    if not isinstance(value, str) or "#" not in value:
        return False
    filename, heading = value.split("#", 1)
    return filename in PUBLIC_FILES and bool(heading.strip())


def _decode_public_free_text(value: str) -> str:
    return value.replace("&#124;", "|").replace("<br>", "\n")


def _table(text: str, heading: str) -> tuple[list[str], list[dict[str, str]]]:
    match = re.search(rf"^##\s+{re.escape(heading)}\s*$", text, re.M)
    if not match:
        return [], []
    tail = text[match.end() :]
    next_heading = re.search(r"^##\s+", tail, re.M)
    body = tail[: next_heading.start()] if next_heading else tail
    lines = [line.strip() for line in body.splitlines() if line.strip().startswith("|")]
    if len(lines) < 2:
        return [], []

    def cells(line: str) -> list[str]:
        return [cell.strip() for cell in line.strip().strip("|").split("|")]

    header = cells(lines[0])
    rows = []
    for line in lines[2:]:
        values = cells(line)
        if len(values) == len(header):
            rows.append(dict(zip(header, values)))
    return header, rows


def rule_dependency_fingerprint(
    observation_ids: Iterable[str],
    observations: list[dict[str, Any]],
    documents: list[dict[str, Any]],
) -> str:
    observation_ids = (
        observation_ids if isinstance(observation_ids, (list, tuple)) else []
    )
    by_observation = {
        item.get("observation_id"): item
        for item in observations
        if isinstance(item, dict) and isinstance(item.get("observation_id"), str)
    }
    by_document = {
        item.get("template_source_id"): item
        for item in documents
        if isinstance(item, dict) and isinstance(item.get("template_source_id"), str)
    }
    parts = []
    for observation_id in observation_ids:
        if not isinstance(observation_id, str):
            continue
        observation = by_observation.get(observation_id, {})
        document_id = observation.get("template_source_id", "missing")
        source_sha = (
            by_document.get(document_id, {}).get("source_sha256", "missing")
            if isinstance(document_id, str)
            else "missing"
        )
        parts.append(f"{observation_id}:{document_id}:{source_sha}")
    return _sha256("\n".join(parts).encode("utf-8"))


def validate_schema_asset(path: Path) -> list[str]:
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"schema asset is unreadable: {exc}"]
    if not isinstance(schema, dict):
        return ["schema asset must be one JSON object"]
    errors = []
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        errors.append("schema asset must use JSON Schema 2020-12")
    if (
        schema.get("type") != "object"
        or schema.get("additionalProperties") is not False
    ):
        errors.append("top-level schema must be a closed object")
    top_required = schema.get("required")
    if (
        not isinstance(top_required, list)
        or not all(isinstance(item, str) for item in top_required)
        or set(top_required) != TOP_REQUIRED
    ):
        errors.append("top-level required fields differ from the dossier contract")
    definitions = schema.get("$defs")
    definitions = definitions if isinstance(definitions, dict) else {}
    definition_contracts = {
        "analysis_context": CONTEXT_REQUIRED,
        "analyzer_correlation": {"analysis_id", "doc_id", "source_sha256"},
        "document": DOCUMENT_REQUIRED | DOCUMENT_OPTIONAL,
        "locator": {"kind", "value"},
        "observation": OBSERVATION_REQUIRED | OBSERVATION_OPTIONAL,
        "transfer_rule": RULE_REQUIRED,
        "application_snapshot": SNAPSHOT_REQUIRED,
    }
    required_contracts = {
        "analysis_context": CONTEXT_REQUIRED,
        "analyzer_correlation": {"analysis_id", "doc_id", "source_sha256"},
        "document": DOCUMENT_REQUIRED,
        "locator": {"kind", "value"},
        "observation": OBSERVATION_REQUIRED,
        "transfer_rule": RULE_REQUIRED,
        "application_snapshot": SNAPSHOT_REQUIRED,
    }
    for name, properties in definition_contracts.items():
        definition = definitions.get(name)
        if not isinstance(definition, dict):
            errors.append(f"missing schema definition: {name}")
            continue
        if (
            definition.get("type") != "object"
            or definition.get("additionalProperties") is not False
        ):
            errors.append(f"schema definition must be a closed object: {name}")
        definition_properties = definition.get("properties")
        if (
            not isinstance(definition_properties, dict)
            or set(definition_properties) != properties
        ):
            errors.append(f"schema definition properties differ from contract: {name}")
        definition_required = definition.get("required")
        if (
            not isinstance(definition_required, list)
            or not all(isinstance(item, str) for item in definition_required)
            or set(definition_required) != required_contracts[name]
        ):
            errors.append(
                f"schema definition required fields differ from contract: {name}"
            )
    top_properties = schema.get("properties")
    schema_property = (
        top_properties.get("schema") if isinstance(top_properties, dict) else None
    )
    if (
        not isinstance(schema_property, dict)
        or schema_property.get("const") != SCHEMA_NAME
    ):
        errors.append("dossier schema discriminator changed")
    canonical_hash = _sha256(
        json.dumps(
            schema,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )
    if canonical_hash != SCHEMA_CANONICAL_SHA256:
        errors.append(
            "canonical schema content/topology differs from the shipped contract"
        )
    return errors


def _linked_scopes_for_document(
    document_id: str,
    observations: list[dict[str, Any]],
    rules: list[dict[str, Any]],
) -> tuple[str, ...]:
    observation_ids = {
        item.get("observation_id")
        for item in observations
        if isinstance(item, dict)
        and item.get("template_source_id") == document_id
        and isinstance(item.get("observation_id"), str)
    }
    scopes: set[str] = set()
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        linked_observations = rule.get("observation_ids")
        if not isinstance(linked_observations, list) or not all(
            isinstance(item, str) for item in linked_observations
        ):
            continue
        if not observation_ids.intersection(linked_observations):
            continue
        snapshot = rule.get("application_snapshot")
        affected = (
            snapshot.get("affected_scope_ids") if isinstance(snapshot, dict) else None
        )
        if isinstance(affected, list):
            scopes.update(scope for scope in affected if isinstance(scope, str))
    return tuple(sorted(scopes))


def _validate_projection(
    payload: dict[str, Any], workspace: Path
) -> list[DossierDiagnostic]:
    diagnostics: list[DossierDiagnostic] = []
    documents = payload.get("documents", [])
    rules = payload.get("transfer_rules", [])
    try:
        materials_text = (workspace / "01_MATERIALS_INVENTORY.md").read_text(
            encoding="utf-8"
        )
    except OSError:
        materials_text = ""
    _, material_rows = _table(materials_text, "Template Design Sources")
    material_rows_by_id: dict[str, list[dict[str, str]]] = {}
    for row in material_rows:
        material_rows_by_id.setdefault(row.get("Template source ID", ""), []).append(
            row
        )

    for document in documents:
        if not isinstance(document, dict):
            continue
        document_id = str(document.get("template_source_id", ""))
        scopes = _linked_scopes_for_document(
            document_id, payload.get("observations", []), rules
        )
        matching_rows = material_rows_by_id.get(document_id, [])
        expected = {
            "Template source ID": document_id,
            "Design role": str(document.get("role", "")).lower(),
            "Design question": document.get("design_question", ""),
            "Source/provenance pointer": _normal_path(
                str(document.get("source_pointer", ""))
            )
            or "<invalid>",
            "Access state": str(document.get("access_state", "")).lower(),
            "Local derivative pointer": _normal_path(
                str(document.get("local_derivative_pointer", ""))
            )
            or "<invalid>",
            "Source SHA-256": str(document.get("source_sha256", "")).lower(),
            "Hidden dossier pointer": f".yxj-paper-os/template-analysis/semantic-dossier.json#{document_id}",
            "Design-only state": "design_only",
        }
        if len(matching_rows) != 1:
            diagnostics.append(
                DossierDiagnostic(
                    "TEMPLATE_PROJECTION_MISMATCH",
                    f"expected exactly one 01 projection for {document_id}; found {len(matching_rows)}",
                    scopes,
                )
            )
            continue
        row = matching_rows[0]
        normalized = dict(row)
        for key in (
            "Design role",
            "Access state",
            "Source SHA-256",
            "Design-only state",
        ):
            normalized[key] = normalized.get(key, "").strip().lower()
        for key in ("Source/provenance pointer", "Local derivative pointer"):
            normalized[key] = (
                _normal_path(normalized.get(key, "").strip()) or "<invalid>"
            )
        normalized["Design question"] = _decode_public_free_text(
            normalized.get("Design question", "").strip()
        )
        if any(
            normalized.get(key, "").strip() != str(value)
            for key, value in expected.items()
        ):
            diagnostics.append(
                DossierDiagnostic(
                    "TEMPLATE_PROJECTION_MISMATCH",
                    f"01 projection differs from hidden {document_id}",
                    scopes,
                )
            )

    try:
        structure_text = (workspace / "03_WRITING_STRUCTURE.md").read_text(
            encoding="utf-8"
        )
    except OSError:
        structure_text = ""
    _, rule_rows = _table(structure_text, "Template Rule Projection")
    public_rows_by_id: dict[str, list[dict[str, str]]] = {}
    for row in rule_rows:
        public_rows_by_id.setdefault(row.get("Rule ID", ""), []).append(row)
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        rule_id = str(rule.get("rule_id", ""))
        snapshot = rule.get("application_snapshot")
        snapshot = snapshot if isinstance(snapshot, dict) else {}
        affected = snapshot.get("affected_scope_ids")
        affected = (
            [scope for scope in affected if isinstance(scope, str)]
            if isinstance(affected, list)
            else []
        )
        scopes = tuple(sorted(set(affected)))
        matching_rows = public_rows_by_id.get(rule_id, [])
        observation_ids = rule.get("observation_ids")
        observation_ids = (
            [item for item in observation_ids if isinstance(item, str)]
            if isinstance(observation_ids, list)
            else []
        )
        pointers = ";".join(
            f".yxj-paper-os/template-analysis/semantic-dossier.json#{item}"
            for item in observation_ids
        )
        expected = {
            "Rule ID": rule_id,
            "Grounding kind": "semantic_dossier",
            "Grounding pointer(s)": pointers,
            "Rule kind": rule.get("rule_kind", ""),
            "Affected scope IDs": ";".join(affected),
            "Surface": snapshot.get("surface", ""),
            "Candidate transfer": rule.get("candidate_transfer", ""),
            "Suggested disposition": rule.get("suggested_disposition", ""),
            "Origin": rule.get("origin", ""),
            "Resolution": snapshot.get("resolution", ""),
            "Disposition": snapshot.get("disposition", ""),
            "Decision ID": snapshot.get("decision_id", ""),
            "Limitation": rule.get("limitation", ""),
            "Freshness": rule.get("source_freshness", ""),
        }
        if len(matching_rows) != 1:
            diagnostics.append(
                DossierDiagnostic(
                    "TEMPLATE_PROJECTION_MISMATCH",
                    f"expected exactly one 03 projection for {rule_id}; found {len(matching_rows)}",
                    scopes,
                )
            )
            continue
        row = dict(matching_rows[0])
        for key in ("Surface", "Candidate transfer", "Limitation"):
            row[key] = _decode_public_free_text(row.get(key, "").strip())
        if any(
            row.get(key, "").strip() != str(value) for key, value in expected.items()
        ):
            diagnostics.append(
                DossierDiagnostic(
                    "TEMPLATE_PROJECTION_MISMATCH",
                    f"03 projection differs from hidden/application state for {rule_id}",
                    scopes,
                )
            )
    return diagnostics


def validate_semantic_dossier(
    payload: Any, workspace: Path | None = None
) -> list[DossierDiagnostic]:
    diagnostics: list[DossierDiagnostic] = []

    def add(code: str, message: str, scopes: Iterable[str] = ()) -> None:
        diagnostics.append(DossierDiagnostic(code, message, tuple(sorted(set(scopes)))))

    if not isinstance(payload, dict):
        return [DossierDiagnostic("DOSSIER_SCHEMA", "dossier must be one JSON object")]
    extra_top = set(payload) - TOP_REQUIRED
    missing_top = TOP_REQUIRED - set(payload)
    if missing_top or extra_top:
        add(
            "DOSSIER_SCHEMA",
            f"top-level fields mismatch: missing={sorted(missing_top)} extra={sorted(extra_top)}",
        )
    if (
        payload.get("schema") != SCHEMA_NAME
        or payload.get("workspace_schema") != WORKSPACE_SCHEMA
    ):
        add(
            "DOSSIER_SCHEMA",
            "schema discriminators must be semantic-dossier/1.0 and workspace 0.3",
        )
    if not ID_PATTERNS["dossier"].fullmatch(str(payload.get("dossier_id", ""))):
        add("DOSSIER_SCHEMA", "invalid dossier ID")
    if not _is_nonempty(payload.get("design_question")) or not _is_nonempty(
        payload.get("updated_at")
    ):
        add("DOSSIER_SCHEMA", "design question and updated_at are required")

    scope_values = payload.get("scope_ids")
    if not _valid_unique_string_list(scope_values, ID_PATTERNS["scope"]):
        add("DOSSIER_SCHEMA", "scope_ids must be unique canonical SCOPE-* values")
        scope_ids: set[str] = (
            {
                value
                for value in scope_values or []
                if isinstance(value, str) and ID_PATTERNS["scope"].fullmatch(value)
            }
            if isinstance(scope_values, list)
            else set()
        )
    else:
        assert isinstance(scope_values, list)
        scope_ids = {value for value in scope_values if isinstance(value, str)}

    context = payload.get("analysis_context")
    if not isinstance(context, dict) or set(context) != CONTEXT_REQUIRED:
        add("DOSSIER_SCHEMA", "analysis_context fields differ from contract")
    else:
        if context.get("method") != "model_semantic_deep_reading":
            add(
                "DOSSIER_SCHEMA",
                "analysis_context method must be model_semantic_deep_reading",
            )
        if not _is_enum(
            context.get("generic_knowledge_fallback"), {"used", "not_used"}
        ):
            add("DOSSIER_SCHEMA", "generic fallback declaration is invalid")
        if any(
            not _is_nonempty(context.get(key))
            for key in CONTEXT_REQUIRED - {"method", "generic_knowledge_fallback"}
        ):
            add(
                "DOSSIER_SCHEMA",
                "analysis_context text fields must be explicit; use unavailable when necessary",
            )

    documents = payload.get("documents")
    observations = payload.get("observations")
    rules = payload.get("transfer_rules")
    if (
        not isinstance(documents, list)
        or not isinstance(observations, list)
        or not isinstance(rules, list)
    ):
        add(
            "DOSSIER_SCHEMA",
            "documents, observations, and transfer_rules must be arrays",
        )
        return diagnostics

    document_by_id: dict[str, dict[str, Any]] = {}
    for index, document in enumerate(documents):
        if not isinstance(document, dict):
            add("DOSSIER_SCHEMA", f"document {index} must be an object")
            continue
        if BANNED_COPY_FIELDS.intersection(document):
            add("DOSSIER_COPY_BOUNDARY", f"document {index} embeds copied body content")
        missing = DOCUMENT_REQUIRED - set(document)
        extra = set(document) - DOCUMENT_REQUIRED - DOCUMENT_OPTIONAL
        if missing or extra:
            add(
                "DOSSIER_SCHEMA",
                f"document {index} fields mismatch: missing={sorted(missing)} extra={sorted(extra)}",
            )
        document_id = str(document.get("template_source_id", ""))
        if (
            not ID_PATTERNS["document"].fullmatch(document_id)
            or document_id in document_by_id
        ):
            add(
                "DOSSIER_SCHEMA",
                f"invalid or duplicate template source ID: {document_id}",
            )
        else:
            document_by_id[document_id] = document
        for key in (
            "title",
            "source_pointer",
            "acquisition_provenance",
            "design_question",
            "design_relevance",
            "accessed_at",
            "access_copyright_limitation",
        ):
            if not _is_nonempty(document.get(key)):
                add("DOSSIER_SCHEMA", f"{document_id or index} lacks {key}")
        role = document.get("role")
        access = document.get("access_state")
        freshness = document.get("freshness")
        if not (
            _is_enum(role, ROLES)
            and _is_enum(access, ACCESS_STATES)
            and _is_enum(freshness, FRESHNESS)
        ):
            add(
                "DOSSIER_SCHEMA",
                f"{document_id or index} has invalid role/access/freshness enum",
            )
        if document.get("design_only_state") != "design_only":
            add("DOSSIER_FIREWALL", f"{document_id or index} is not design_only")
        if document.get("design_question") != payload.get("design_question"):
            add(
                "DOSSIER_SCHEMA",
                f"{document_id or index} design question differs from dossier",
            )
        source_pointer = _normal_path(str(document.get("source_pointer", "")))
        local_pointer = _normal_path(str(document.get("local_derivative_pointer", "")))
        if source_pointer is None or local_pointer is None:
            add(
                "DOSSIER_ACCESS",
                f"{document_id or index} has an unsafe or non-POSIX pointer",
            )
        raw_source_sha = document.get("source_sha256")
        source_sha = raw_source_sha if isinstance(raw_source_sha, str) else ""
        if not isinstance(raw_source_sha, str) or not re.fullmatch(
            r"(?:none|[0-9a-f]{64})", source_sha
        ):
            add("DOSSIER_SCHEMA", f"{document_id or index} has invalid source_sha256")
        readable = isinstance(access, str) and access in {
            "full_text",
            "owner_derivative",
        }
        if readable and not re.fullmatch(r"[0-9a-f]{64}", source_sha):
            add(
                "DOSSIER_FINGERPRINT",
                f"{document_id or index} readable source lacks lowercase SHA-256",
            )
        if access == "owner_derivative" and local_pointer == "none":
            add(
                "DOSSIER_ACCESS",
                f"{document_id or index} owner derivative lacks local path",
            )
        eligibility = document.get("semantic_reading_eligible")
        if not isinstance(eligibility, bool):
            add(
                "DOSSIER_SCHEMA",
                f"{document_id or index} semantic_reading_eligible must be boolean",
            )
        elif readable != eligibility:
            add(
                "DOSSIER_ACCESS",
                f"{document_id or index} semantic eligibility contradicts access state",
            )
        scopes = _linked_scopes_for_document(document_id, observations, rules)
        verified_contained_derivative = False
        if local_pointer not in {None, "none"}:
            if workspace is None:
                if freshness == "verified_local_current":
                    add(
                        "DOSSIER_FRESHNESS",
                        f"{document_id} verified current requires workspace rehash context",
                        scopes,
                    )
            else:
                root = workspace.resolve()
                assert isinstance(local_pointer, str)
                candidate = workspace / local_pointer
                try:
                    resolved = candidate.resolve(strict=True)
                    if (
                        candidate.is_symlink()
                        or root not in resolved.parents
                        or not resolved.is_file()
                    ):
                        raise OSError(
                            "derivative escapes workspace or is not a regular file"
                        )
                    actual_sha = _sha256(resolved.read_bytes())
                    if actual_sha != source_sha:
                        add(
                            "DOSSIER_FINGERPRINT",
                            f"{document_id} derivative hash mismatch",
                            scopes,
                        )
                        add(
                            "DOSSIER_FRESHNESS",
                            f"{document_id} contained derivative is stale",
                            scopes,
                        )
                    else:
                        verified_contained_derivative = True
                        if freshness == "stale":
                            add(
                                "DOSSIER_FRESHNESS",
                                f"{document_id} declares stale despite matching local bytes",
                                scopes,
                            )
                except OSError as exc:
                    add(
                        "DOSSIER_ACCESS",
                        f"{document_id} derivative unavailable: {exc}",
                        scopes,
                    )
        if freshness == "verified_local_current" and not verified_contained_derivative:
            add(
                "DOSSIER_FRESHNESS",
                f"{document_id} verified current requires a contained non-symlink derivative",
                scopes,
            )
        is_url = isinstance(source_pointer, str) and bool(
            re.match(r"^[a-z][a-z0-9+.-]*://", source_pointer, re.I)
        )
        if is_url and local_pointer == "none" and freshness != "recorded_at_access":
            add(
                "DOSSIER_FRESHNESS",
                f"{document_id} remote-only source cannot be mechanically current",
                scopes,
            )
        if "analyzer_correlation" in document:
            correlation = document["analyzer_correlation"]
            if (
                not isinstance(correlation, dict)
                or set(correlation) != {"analysis_id", "doc_id", "source_sha256"}
                or any(
                    not _is_nonempty(correlation.get(key))
                    for key in ("analysis_id", "doc_id")
                )
                or not isinstance(correlation.get("source_sha256"), str)
                or not re.fullmatch(
                    r"[0-9a-f]{64}", correlation.get("source_sha256", "")
                )
            ):
                add(
                    "DOSSIER_SCHEMA",
                    f"{document_id} analyzer correlation differs from schema",
                )
                add(
                    "DOSSIER_REFERENCE",
                    f"{document_id} analyzer correlation must contain exact analysis_id/doc_id/source_sha256",
                )
            elif correlation["source_sha256"] != source_sha:
                add(
                    "DOSSIER_REFERENCE",
                    f"{document_id} analyzer correlation hash differs from the source",
                )

    observation_by_id: dict[str, dict[str, Any]] = {}
    for index, observation in enumerate(observations):
        if not isinstance(observation, dict):
            add("DOSSIER_SCHEMA", f"observation {index} must be an object")
            continue
        missing = OBSERVATION_REQUIRED - set(observation)
        extra = set(observation) - OBSERVATION_REQUIRED - OBSERVATION_OPTIONAL
        if missing or extra:
            code = (
                "DOSSIER_COPY_BOUNDARY"
                if BANNED_COPY_FIELDS.intersection(extra)
                else "DOSSIER_SCHEMA"
            )
            add(
                code,
                f"observation {index} fields mismatch: missing={sorted(missing)} extra={sorted(extra)}",
            )
        observation_id = str(observation.get("observation_id", ""))
        if (
            not ID_PATTERNS["observation"].fullmatch(observation_id)
            or observation_id in observation_by_id
        ):
            add(
                "DOSSIER_SCHEMA",
                f"invalid or duplicate observation ID: {observation_id}",
            )
        else:
            observation_by_id[observation_id] = observation
        document_id = observation.get("template_source_id")
        document = (
            document_by_id.get(document_id) if isinstance(document_id, str) else None
        )
        if document is None:
            add(
                "DOSSIER_REFERENCE",
                f"{observation_id or index} references unknown document",
            )
        elif (
            not isinstance(document.get("access_state"), str)
            or document.get("access_state")
            in {"metadata_only", "snippet_only", "inaccessible"}
            or not document.get("semantic_reading_eligible")
        ):
            add(
                "DOSSIER_ACCESS",
                f"{observation_id} is grounded by a non-readable source",
            )
        locator = observation.get("locator")
        if (
            not isinstance(locator, dict)
            or set(locator) != {"kind", "value"}
            or not _is_enum(locator.get("kind"), LOCATOR_KINDS)
            or not _is_nonempty(locator.get("value"))
        ):
            add(
                "DOSSIER_SCHEMA",
                f"{observation_id or index} locator differs from schema",
            )
            add("DOSSIER_LOCATOR", f"{observation_id or index} lacks a precise locator")
        if observation.get("status") != "model-derived":
            add(
                "DOSSIER_SCHEMA",
                f"{observation_id or index} must retain model-derived status",
            )
        for key in (
            "observed_pattern",
            "semantic_interpretation",
            "uncertainty",
            "non_transfer_note",
        ):
            if not _is_nonempty(observation.get(key)):
                add("DOSSIER_SCHEMA", f"{observation_id or index} lacks {key}")
            elif len(observation[key]) > OBSERVATION_TEXT_LIMITS[key]:
                add(
                    "DOSSIER_COPY_BOUNDARY",
                    f"{observation_id or index} {key} exceeds the {OBSERVATION_TEXT_LIMITS[key]}-character boundary",
                )
        if "minimal_excerpt" in observation:
            excerpt = observation["minimal_excerpt"]
            if (
                not _is_nonempty(excerpt)
                or len(excerpt) > OBSERVATION_TEXT_LIMITS["minimal_excerpt"]
            ):
                add(
                    "DOSSIER_COPY_BOUNDARY",
                    f"{observation_id or index} excerpt exceeds the {OBSERVATION_TEXT_LIMITS['minimal_excerpt']}-character boundary",
                )

    rule_ids: set[str] = set()
    for index, rule in enumerate(rules):
        if not isinstance(rule, dict):
            add("DOSSIER_SCHEMA", f"rule {index} must be an object")
            continue
        missing = RULE_REQUIRED - set(rule)
        extra = set(rule) - RULE_REQUIRED
        if missing or extra:
            add(
                "DOSSIER_SCHEMA",
                f"rule {index} fields mismatch: missing={sorted(missing)} extra={sorted(extra)}",
            )
        rule_id = str(rule.get("rule_id", ""))
        snapshot_value = rule.get("application_snapshot")
        snapshot: dict[str, Any] = (
            snapshot_value if isinstance(snapshot_value, dict) else {}
        )
        affected = snapshot.get("affected_scope_ids", [])
        scopes = (
            tuple(sorted(set(scope for scope in affected if isinstance(scope, str))))
            if isinstance(affected, list)
            else ()
        )
        if not ID_PATTERNS["rule"].fullmatch(rule_id) or rule_id in rule_ids:
            add(
                "DOSSIER_SCHEMA",
                f"invalid or duplicate transfer rule ID: {rule_id}",
                scopes,
            )
        else:
            rule_ids.add(rule_id)
        observation_ids_value = rule.get("observation_ids")
        if not _valid_unique_string_list(
            observation_ids_value, ID_PATTERNS["observation"]
        ):
            add(
                "DOSSIER_SCHEMA",
                f"{rule_id or index} requires unique observation IDs",
                scopes,
            )
            observation_ids: list[str] = []
        else:
            assert isinstance(observation_ids_value, list)
            observation_ids = [
                item for item in observation_ids_value if isinstance(item, str)
            ]
        if any(item not in observation_by_id for item in observation_ids):
            add(
                "DOSSIER_REFERENCE",
                f"{rule_id or index} references unknown observation",
                scopes,
            )
        if rule.get("grounding_kind") != "semantic_dossier" or not _is_enum(
            rule.get("rule_kind"), RULE_KINDS
        ):
            add(
                "DOSSIER_SCHEMA",
                f"{rule_id or index} is not a valid semantic rule",
                scopes,
            )
        if rule.get("origin") != "model-proposed" or not _is_enum(
            rule.get("suggested_disposition"), SUGGESTED
        ):
            add(
                "DOSSIER_SCHEMA",
                f"{rule_id or index} has invalid epistemic state",
                scopes,
            )
        for key in ("candidate_transfer", "limitation"):
            if not _is_nonempty(rule.get(key)):
                add("DOSSIER_SCHEMA", f"{rule_id or index} lacks {key}", scopes)
        if not _is_enum(rule.get("source_freshness"), FRESHNESS):
            add(
                "DOSSIER_SCHEMA",
                f"{rule_id or index} has invalid source freshness",
                scopes,
            )
        expected_fingerprint = rule_dependency_fingerprint(
            observation_ids, observations, documents
        )
        if rule.get("dependency_fingerprint") != expected_fingerprint:
            add(
                "DOSSIER_FINGERPRINT",
                f"{rule_id or index} dependency fingerprint mismatch",
                scopes,
            )
        if not isinstance(snapshot, dict) or set(snapshot) != SNAPSHOT_REQUIRED:
            add(
                "DOSSIER_SCHEMA",
                f"{rule_id or index} application_snapshot fields differ from contract",
                scopes,
            )
            continue
        if not _valid_unique_string_list(affected, ID_PATTERNS["scope"]):
            add(
                "DOSSIER_SCHEMA",
                f"{rule_id or index} affected scopes have invalid shape",
                scopes,
            )
        elif any(scope not in scope_ids for scope in affected):
            add(
                "DOSSIER_REFERENCE",
                f"{rule_id or index} references unknown scope",
                scopes,
            )
        if not _is_nonempty(snapshot.get("surface")):
            add("DOSSIER_SCHEMA", f"{rule_id or index} lacks applied surface", scopes)
        resolution = snapshot.get("resolution")
        disposition = snapshot.get("disposition")
        gate = snapshot.get("gate_category")
        decision_id = snapshot.get("decision_id")
        decision_pointer = snapshot.get("decision_pointer")
        application_state_valid = (
            _is_enum(resolution, RESOLUTIONS)
            and _is_enum(disposition, DISPOSITIONS)
            and _is_enum(gate, GATES)
        )
        if not application_state_valid:
            add(
                "DOSSIER_SCHEMA",
                f"{rule_id or index} has invalid application epistemic state",
                scopes,
            )
        if gate == "not_applicable":
            if decision_id != "none" or decision_pointer != "none":
                add(
                    "DOSSIER_GATE",
                    f"{rule_id or index} routine decision must not carry owner gate",
                    scopes,
                )
        elif (
            isinstance(gate, str)
            and gate in GATES
            and (
                not ID_PATTERNS["decision"].fullmatch(str(decision_id))
                or not _public_pointer(decision_pointer)
            )
        ):
            add(
                "DOSSIER_GATE",
                f"{rule_id or index} triggered gate lacks DEC-* and public pointer",
                scopes,
            )
        if (
            snapshot.get("public_projection_pointer")
            != "03_WRITING_STRUCTURE.md#Template Rule Projection"
        ):
            add(
                "DOSSIER_REFERENCE",
                f"{rule_id or index} lacks active public projection pointer",
                scopes,
            )
        compatibility_rule = {
            "rule_id": rule_id,
            "grounding_kind": "semantic_dossier",
            "grounding_pointers": [
                f".yxj-paper-os/template-analysis/semantic-dossier.json#{item}"
                for item in observation_ids
            ],
            "rule_kind": rule.get("rule_kind"),
            "affected_scope_ids": affected,
            "suggested_disposition": rule.get("suggested_disposition"),
            "origin": rule.get("origin"),
            "resolution": resolution,
            "disposition": disposition,
            "gate_category": gate,
            "decision_id": decision_id,
            "freshness": rule.get("source_freshness"),
        }
        if application_state_valid:
            for item in validate_template_rule(compatibility_rule):
                add(item.code, item.message, item.scopes)
        source_states: set[str] = set()
        for obs_id in observation_ids:
            document_key = observation_by_id.get(obs_id, {}).get("template_source_id")
            document = (
                document_by_id.get(document_key)
                if isinstance(document_key, str)
                else None
            )
            state = document.get("freshness") if isinstance(document, dict) else None
            if isinstance(state, str):
                source_states.add(state)
        expected_state = (
            "stale"
            if "stale" in source_states
            else "unavailable"
            if "unavailable" in source_states
            else "recorded_at_access"
            if "recorded_at_access" in source_states
            else "verified_local_current"
        )
        if rule.get("source_freshness") != expected_state:
            add(
                "DOSSIER_FRESHNESS",
                f"{rule_id or index} freshness differs from grounded documents",
                scopes,
            )
        if (
            isinstance(disposition, str)
            and disposition in ACTIVE_DISPOSITIONS
            and expected_state in {"stale", "unavailable"}
        ):
            add(
                "DOSSIER_FRESHNESS",
                f"{rule_id or index} active rule uses stale/unavailable source",
                scopes,
            )

    # Global identity uniqueness across record classes.
    all_ids = (
        [str(payload.get("dossier_id", ""))]
        + list(document_by_id)
        + list(observation_by_id)
        + list(rule_ids)
    )
    if len(all_ids) != len(set(all_ids)):
        add("DOSSIER_SCHEMA", "record IDs must be globally unique")

    if workspace is not None:
        diagnostics.extend(_validate_projection(payload, workspace))
    return diagnostics


def write_semantic_dossier(workspace: Path, payload: dict[str, Any]) -> None:
    """Write only the dossier derived from one canonical, non-symlink workspace."""
    workspace = Path(workspace)
    normalized = Path(os.path.normpath(os.fspath(workspace)))
    if not workspace.is_absolute() or normalized != workspace or workspace.is_symlink():
        raise ValueError("workspace must be one canonical absolute directory")
    try:
        resolved_workspace = workspace.resolve(strict=True)
    except OSError as exc:
        raise ValueError(f"workspace is unavailable: {exc}") from exc
    if resolved_workspace != workspace or not workspace.is_dir():
        raise ValueError("workspace aliases and symlinks are forbidden")

    hidden = workspace / ".yxj-paper-os"
    output = hidden / "template-analysis"
    path = output / DOSSIER_FILENAME
    for component in (hidden, output):
        if component.is_symlink():
            raise ValueError(f"writer path component is a symlink: {component.name}")
        if component.exists() and not component.is_dir():
            raise ValueError(
                f"writer path component is not a directory: {component.name}"
            )
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise ValueError(
            "semantic dossier destination must be a regular non-symlink file"
        )

    diagnostics = validate_semantic_dossier(payload, workspace)
    if diagnostics:
        raise DossierValidationError(diagnostics)

    for component in (hidden, output):
        component.mkdir(exist_ok=True)
        if component.is_symlink() or component.resolve(strict=True) != component:
            raise ValueError(
                f"writer path component is not canonical: {component.name}"
            )
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise ValueError("semantic dossier destination changed during validation")
    data = (
        json.dumps(
            payload, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False
        )
        + "\n"
    ).encode("utf-8")
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temp_path = Path(temporary)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        if hidden.is_symlink() or output.is_symlink() or path.is_symlink():
            raise ValueError("writer path changed before atomic replacement")
        os.replace(temp_path, path)
    finally:
        temp_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate one hidden semantic dossier without writeback"
    )
    parser.add_argument("dossier", type=Path)
    parser.add_argument("--workspace", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.dossier.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"DOSSIER_SCHEMA: {exc}")
        return 1
    diagnostics = validate_semantic_dossier(payload, args.workspace)
    if diagnostics:
        for item in diagnostics:
            scope_text = ",".join(item.scopes) if item.scopes else "none"
            print(f"{item.code} [{scope_text}]: {item.message}")
        return 1
    print("Semantic dossier validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
