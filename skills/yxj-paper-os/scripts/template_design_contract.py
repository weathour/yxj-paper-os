#!/usr/bin/env python3
"""Shared schema-0.3 template-design rule and lens-pointer contract."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path, PurePosixPath
import re
from typing import Any

TEMPLATE_RULE_INCOMPATIBLE = "TEMPLATE_RULE_INCOMPATIBLE"
ORDINARY_FRESHNESS = {
    "verified_local_current",
    "recorded_at_access",
    "stale",
    "unavailable",
}
FOUR_GATES = {
    "scientific_commitment",
    "argument_spine",
    "material_local_tradeoff",
    "deliberate_divergence",
}
ANALYZER_ACTION_TO_SUGGESTED_DISPOSITION = {
    "follow": "adopted",
    "adapt": "adapted",
    "deliberate_divergence": "deliberate_divergence",
    "not_applicable": "not_applicable",
}
FIXED_ANALYZER_OUTPUTS = {
    "manifest.json",
    "metric-registry.json",
    "paper-metrics.jsonl",
    "objects.jsonl",
    "corpus-summary.json",
    "design-profile.json",
    "extraction-warnings.json",
    "analysis-report.html",
}
GROUNDING_COMPATIBILITY: dict[str, dict[str, Any]] = {
    "official_constraint": {
        "rule_kinds": {"hard_constraint", "candidate_pattern"},
        "initial_origin": "artifact-observed",
        "freshness_domain": "ordinary",
    },
    "semantic_dossier": {
        "rule_kinds": {
            "candidate_pattern",
            "soft_band",
            "sequence",
            "presence",
            "watch_only",
        },
        "initial_origin": "model-proposed",
        "freshness_domain": "ordinary",
    },
    "quantitative_analysis": {
        "rule_kinds": {"soft_band", "sequence", "presence", "watch_only"},
        "initial_origin": "model-proposed",
        "freshness_domain": "ordinary",
    },
    "generic_fallback": {
        "rule_kinds": {"candidate_pattern"},
        "initial_origin": "model-proposed",
        "freshness_domain": "plugin",
    },
}


@dataclass(frozen=True)
class ContractDiagnostic:
    code: str
    message: str
    scopes: tuple[str, ...] = ()


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def load_lens_registry(
    registry_path: Path,
) -> tuple[dict[str, str], list[ContractDiagnostic]]:
    diagnostics: list[ContractDiagnostic] = []
    try:
        text = registry_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return {}, [
            ContractDiagnostic(
                TEMPLATE_RULE_INCOMPATIBLE, f"lens registry unavailable: {exc}"
            )
        ]
    match = re.search(r"^##\s+Lens Registry\s*$", text, re.M)
    if not match:
        return {}, [
            ContractDiagnostic(
                TEMPLATE_RULE_INCOMPATIBLE, "missing Lens Registry heading"
            )
        ]
    tail = text[match.end() :]
    next_heading = re.search(r"^##\s+", tail, re.M)
    body = tail[: next_heading.start()] if next_heading else tail
    lines = [line.strip() for line in body.splitlines() if line.strip().startswith("|")]
    if len(lines) < 2:
        return {}, [
            ContractDiagnostic(
                TEMPLATE_RULE_INCOMPATIBLE, "missing lens registry table"
            )
        ]
    header = _cells(lines[0])
    if header[:2] != ["Lens ID", "Module path"]:
        return {}, [
            ContractDiagnostic(
                TEMPLATE_RULE_INCOMPATIBLE,
                "lens registry must begin with Lens ID and Module path",
            )
        ]
    registry: dict[str, str] = {}
    used_paths: set[str] = set()
    root = registry_path.parent.resolve()
    for line in lines[2:]:
        row = _cells(line)
        if len(row) != len(header):
            diagnostics.append(
                ContractDiagnostic(
                    TEMPLATE_RULE_INCOMPATIBLE, "malformed lens registry row"
                )
            )
            continue
        lens_id, module_path = row[0], row[1]
        pure = PurePosixPath(module_path)
        if (
            not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", lens_id)
            or pure.is_absolute()
            or ".." in pure.parts
            or pure.suffix != ".md"
        ):
            diagnostics.append(
                ContractDiagnostic(
                    TEMPLATE_RULE_INCOMPATIBLE,
                    f"invalid lens registry mapping: {lens_id} -> {module_path}",
                )
            )
            continue
        resolved = (root / pure).resolve()
        if root not in resolved.parents or not resolved.is_file():
            diagnostics.append(
                ContractDiagnostic(
                    TEMPLATE_RULE_INCOMPATIBLE,
                    f"lens module does not resolve: {module_path}",
                )
            )
            continue
        if lens_id in registry or module_path in used_paths:
            diagnostics.append(
                ContractDiagnostic(
                    TEMPLATE_RULE_INCOMPATIBLE,
                    f"duplicate lens registry mapping: {lens_id} -> {module_path}",
                )
            )
            continue
        registry[lens_id] = module_path
        used_paths.add(module_path)
    return registry, diagnostics


def _validate_generic_pointer(
    pointer: str,
    freshness: str,
    registry_path: Path | None,
    plugin_version: str | None,
) -> str | None:
    if registry_path is None or plugin_version is None:
        return "generic fallback requires registry path and plugin version"
    registry, diagnostics = load_lens_registry(registry_path)
    if diagnostics:
        return diagnostics[0].message
    match = re.fullmatch(r"lens:([a-z0-9]+(?:-[a-z0-9]+)*)#([a-z0-9-]+)", pointer)
    if not match:
        return "generic fallback pointer has invalid grammar"
    lens_id, heading_slug = match.groups()
    module_name = registry.get(lens_id)
    if module_name is None:
        return f"unknown lens ID: {lens_id}"
    module = registry_path.parent / module_name
    try:
        module_bytes = module.read_bytes()
        module_text = module_bytes.decode("utf-8")
    except (OSError, UnicodeError) as exc:
        return f"lens module unavailable: {exc}"
    headings = {
        slugify(heading)
        for level, heading in re.findall(r"^(#{2,3})\s+(.+?)\s*$", module_text, re.M)
        if level in {"##", "###"}
    }
    if heading_slug not in headings:
        return f"lens heading does not resolve: {heading_slug}"
    expected = (
        f"plugin:{plugin_version}@sha256:" + hashlib.sha256(module_bytes).hexdigest()
    )
    if freshness != expected or not re.match(r"^0\.3\.", plugin_version):
        return "generic fallback freshness/version/hash mismatch"
    return None


def _present_official_pointer(value: Any) -> bool:
    return (
        isinstance(value, str)
        and bool(value.strip())
        and value.strip().lower() != "none"
    )


def validate_template_rule(
    rule: dict[str, Any],
    *,
    lens_registry_path: Path | None = None,
    plugin_version: str | None = None,
) -> list[ContractDiagnostic]:
    diagnostics: list[ContractDiagnostic] = []

    raw_scopes = rule.get("affected_scope_ids")
    if not isinstance(raw_scopes, list) or not all(
        isinstance(scope, str) for scope in raw_scopes
    ):
        scopes: tuple[str, ...] = ()
        diagnostics.append(
            ContractDiagnostic(
                TEMPLATE_RULE_INCOMPATIBLE,
                "affected_scope_ids must be a string array",
            )
        )
    else:
        scopes = tuple(sorted(set(raw_scopes)))

    def fail(message: str) -> None:
        diagnostics.append(
            ContractDiagnostic(TEMPLATE_RULE_INCOMPATIBLE, message, scopes)
        )

    kind = rule.get("grounding_kind")
    spec = GROUNDING_COMPATIBILITY.get(kind) if isinstance(kind, str) else None
    if spec is None:
        fail("unknown or mixed grounding kind")
        return diagnostics
    rule_kind = rule.get("rule_kind")
    if not isinstance(rule_kind, str) or rule_kind not in spec["rule_kinds"]:
        fail(f"{kind} cannot create rule kind {rule.get('rule_kind')}")
    if rule.get("origin") != spec["initial_origin"]:
        fail(f"{kind} has incompatible origin")

    pointers = rule.get("grounding_pointers")
    if (
        not isinstance(pointers, list)
        or not pointers
        or not all(isinstance(pointer, str) and pointer for pointer in pointers)
    ):
        fail("grounding pointers must be one nonempty typed list")
        pointers = []
    freshness = rule.get("freshness")
    if spec["freshness_domain"] == "ordinary":
        if not isinstance(freshness, str) or freshness not in ORDINARY_FRESHNESS:
            fail("ordinary grounding requires an ordinary freshness token")
    elif isinstance(freshness, str) and freshness in ORDINARY_FRESHNESS:
        fail("ordinary freshness is forbidden for generic fallback")

    if kind == "official_constraint":
        if len(pointers) != 1 or not re.fullmatch(
            r"M-[a-z0-9]+(?:-[a-z0-9]+)*", pointers[0]
        ):
            fail("official constraint requires one M-* pointer")
        source = rule.get("official_source")
        if not isinstance(source, dict) or not (
            isinstance(source.get("kind"), str)
            and source.get("kind") in {"source", "artifact"}
            and source.get("origin") == "artifact-observed"
            and source.get("status") == "available"
            and _present_official_pointer(source.get("locator"))
            and _present_official_pointer(source.get("grounding"))
        ):
            fail("official constraint lacks qualifying artifact-observed source")
        if rule.get("rule_kind") == "hard_constraint":
            if (
                rule.get("resolution") != "confirmed"
                or rule.get("disposition") != "adopted"
                or freshness != "verified_local_current"
            ):
                fail(
                    "official hard constraint requires confirmed/adopted/current state"
                )
    elif kind == "semantic_dossier":
        if not pointers or any(
            not re.fullmatch(
                r"\.yxj-paper-os/template-analysis/semantic-dossier\.json#TOBS-[a-z0-9]+(?:-[a-z0-9]+)*",
                pointer,
            )
            for pointer in pointers
        ):
            fail("semantic rule requires only semantic-dossier TOBS-* pointers")
    elif kind == "quantitative_analysis":
        pattern = re.compile(
            r"\.yxj-paper-os/template-analysis/([a-z0-9-]+\.(?:json|jsonl))#.+"
        )
        if not pointers:
            fail("quantitative rule requires an analyzer pointer")
        for pointer in pointers:
            match = pattern.fullmatch(pointer)
            if not match or match.group(1) not in FIXED_ANALYZER_OUTPUTS:
                fail("quantitative rule requires only fixed analyzer artifact pointers")
                break
    else:
        if len(pointers) != 1:
            fail("generic fallback requires exactly one lens pointer")
        elif message := _validate_generic_pointer(
            pointers[0], str(freshness), lens_registry_path, plugin_version
        ):
            fail(message)

    disposition = rule.get("disposition")
    resolution = rule.get("resolution")
    if disposition == "candidate" and resolution != "candidate":
        fail("candidate actual disposition must retain candidate resolution")
    elif disposition == "rejected" and resolution != "rejected":
        fail("rejected actual disposition requires rejected resolution")
    elif (
        isinstance(disposition, str)
        and disposition
        in {"adopted", "adapted", "not_applicable", "deliberate_divergence"}
        and resolution != "confirmed"
    ):
        fail("resolved actual disposition requires confirmed resolution")
    elif not isinstance(disposition, str) or disposition not in {
        "candidate",
        "adopted",
        "adapted",
        "rejected",
        "not_applicable",
        "deliberate_divergence",
    }:
        fail("invalid actual disposition")

    gate = rule.get("gate_category")
    decision = rule.get("decision_id")
    if gate == "not_applicable":
        if decision != "none":
            fail("routine rule must not carry a ceremonial decision")
    elif isinstance(gate, str) and gate in FOUR_GATES:
        if not isinstance(decision, str) or not re.fullmatch(
            r"DEC-[a-z0-9]+(?:-[a-z0-9]+)*", decision
        ):
            fail("triggered gate requires one DEC-* record")
    else:
        fail("invalid gate category")
    if disposition == "deliberate_divergence":
        if gate != "deliberate_divergence":
            fail("actual deliberate divergence requires its matching gate")
        if kind == "generic_fallback":
            fail("generic fallback cannot create deliberate divergence")
        if kind == "official_constraint" and rule.get("rule_kind") == "hard_constraint":
            fail(
                "active official hard constraint requires a route change, not divergence"
            )
    suggested = rule.get("suggested_disposition")
    if not isinstance(suggested, str) or suggested not in {
        "none",
        "candidate",
        "adopted",
        "adapted",
        "rejected",
        "deliberate_divergence",
        "not_applicable",
    }:
        fail("invalid suggested disposition")
    return diagnostics
