#!/usr/bin/env python3
"""Deterministic target-journal/template corpus analysis for yxj-paper-os.

The analyzer is intentionally standard-library only. It accepts owner-supplied
Markdown, semantic HTML, JATS XML, and plain-text derivatives; PDF bytes are a
hard boundary. Results are descriptive writing-design observations, never
scientific evidence or venue/acceptance scores.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import os
import random
import re
import shutil
import statistics
import sys
import tempfile
import unicodedata
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable, Sequence

SCHEMA = "template-corpus/1.0"
PAPER_SCHEMA = "template-paper-metrics/1.0"
OBJECT_SCHEMA = "template-object/1.0"
SUMMARY_SCHEMA = "template-corpus-summary/1.0"
PROFILE_SCHEMA = "template-design-profile/1.0"
WARNINGS_SCHEMA = "template-extraction-warnings/1.0"
ANALYZER_VERSION = "1.0.0"
MAX_SOURCE_BYTES = 50 * 1024 * 1024
FORMATS = {"markdown", "html", "jats", "txt"}
PARTITIONS = {"primary_match", "venue_control", "topic_control", "exemplar"}
MISSING_STATUSES = {
    "ok",
    "not_present",
    "not_applicable",
    "source_missing",
    "unsupported_format",
    "unsupported_language",
    "parse_failed",
    "ambiguous",
    "denominator_zero",
    "excluded",
}
OUTPUT_NAMES = (
    "manifest.json",
    "metric-registry.json",
    "paper-metrics.jsonl",
    "objects.jsonl",
    "corpus-summary.json",
    "design-profile.json",
    "extraction-warnings.json",
    "analysis-report.html",
)
OBJECT_TYPES = ("figure", "table", "equation", "algorithm")
ANNOTATION_ROLES = {
    "overview",
    "architecture",
    "workflow",
    "formulation",
    "method-detail",
    "main-result",
    "comparison",
    "ablation",
    "sensitivity",
    "robustness",
    "efficiency",
    "interpretability",
    "failure-analysis",
    "case-study",
    "limitation",
    "uncertainty",
    "data",
    "other",
}
ANNOTATION_ENCODINGS = {
    "line",
    "bar",
    "scatter",
    "box",
    "violin",
    "heatmap",
    "map",
    "network",
    "image",
    "diagram",
    "flowchart",
    "table",
    "error-bar",
    "uncertainty-band",
    "raw-points",
    "other",
}

WORD_RE = re.compile(
    r"[A-Za-z0-9]+(?:['’\-][A-Za-z0-9]+)*|"
    r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]|"
    r"[\u3040-\u30ff\uac00-\ud7af]"
)
SENTENCE_RE = re.compile(r"(?<=[.!?。！？])(?:[\"'’”）\]]+)?\s+")
CALL_OUT_RE = re.compile(
    r"\b(?P<kind>fig(?:ure)?|table|eq(?:uation)?|algorithm)\.?\s*"
    r"(?:\(|\[)?(?P<number>\d+)(?:\)|\])?",
    re.IGNORECASE,
)
CITATION_RE = re.compile(
    r"(?:\[[0-9][0-9,;\-–\s]*\]|\([A-Z][A-Za-z'’\-]+(?:\s+et\s+al\.)?,?\s+(?:19|20)\d{2}[a-z]?\))"
)
REFERENCE_HEADING_RE = re.compile(
    r"^(references|bibliography|literature cited|参考文献)$", re.IGNORECASE
)

LEXICAL_PATTERNS: dict[str, tuple[str, ...]] = {
    "lexical.hedge_rate_per_kword": (
        "may",
        "might",
        "could",
        "suggest",
        "suggests",
        "likely",
        "approximately",
        "possible",
        "possibly",
    ),
    "lexical.booster_rate_per_kword": (
        "clearly",
        "demonstrate",
        "demonstrates",
        "strongly",
        "indeed",
        "obviously",
    ),
    "lexical.modal_rate_per_kword": (
        "can",
        "could",
        "may",
        "might",
        "must",
        "should",
        "will",
        "would",
    ),
    "lexical.first_person_rate_per_kword": ("we", "our", "ours", "us", "i"),
    "lexical.transition_rate_per_kword": (
        "however",
        "therefore",
        "moreover",
        "furthermore",
        "nevertheless",
        "consequently",
        "thus",
    ),
    "marker.gap_rate_per_kword": (
        "however",
        "remains unclear",
        "has not been",
        "little attention",
        "gap",
    ),
    "marker.contribution_rate_per_kword": (
        "we propose",
        "we present",
        "our contribution",
        "this work introduces",
    ),
    "marker.limitation_rate_per_kword": (
        "limitation",
        "limitations",
        "future work",
        "cannot",
    ),
    "marker.comparison_rate_per_kword": (
        "compared with",
        "compared to",
        "outperform",
        "baseline",
        "versus",
    ),
}


class ContractError(ValueError):
    """Manifest or containment violation that must not create output."""


@dataclass
class Block:
    kind: str
    text: str = ""
    level: int | None = None
    explicit_id: str | None = None
    label: str | None = None
    caption: str = ""
    section_path: list[str] = field(default_factory=list)
    source_char_start: int = 0
    features: dict[str, Any] = field(default_factory=dict)
    callout_targets: list[str] = field(default_factory=list)
    citation_targets: list[str] = field(default_factory=list)
    external_links: list[str] = field(default_factory=list)
    body_word_offset: int = 0
    source_block_index: int = 0


@dataclass
class ParsedDocument:
    title: str = ""
    abstract: str = ""
    abstract_paragraphs: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    blocks: list[Block] = field(default_factory=list)
    reference_entries: int = 0
    warnings: list[str] = field(default_factory=list)
    capability: dict[str, bool] = field(default_factory=dict)


@dataclass
class LoadedDocument:
    spec: dict[str, Any]
    path: Path
    relative_path: str
    raw: bytes
    source_sha256: str
    annotation_path: Path | None = None
    annotation_relative_path: str | None = None
    annotation_sha256: str | None = None


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def reject_nonfinite_json(token: str) -> Any:
    raise ValueError(f"non-finite JSON token {token}")


def canonical_json(value: Any, *, pretty: bool = True) -> bytes:
    if pretty:
        text = json.dumps(
            value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False
        )
    else:
        text = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    return (text + "\n").encode("utf-8")


def canonical_jsonl(rows: Iterable[dict[str, Any]]) -> bytes:
    return b"".join(canonical_json(row, pretty=False) for row in rows)


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temp_path = Path(temporary)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    finally:
        temp_path.unlink(missing_ok=True)


def write_bundle_transactional(output_dir: Path, payloads: dict[str, bytes]) -> None:
    """Install the fixed bundle with rollback on every ordinary write failure."""
    expected: set[str] = set(OUTPUT_NAMES)
    if set(payloads) != expected:
        raise OSError(
            "bundle payload mismatch: "
            f"missing={sorted(expected - set(payloads))}, "
            f"extra={sorted(set(payloads) - expected)}"
        )
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    if output_dir.is_symlink() or (output_dir.exists() and not output_dir.is_dir()):
        raise OSError(f"output bundle root is not a real directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    for name in OUTPUT_NAMES:
        destination = output_dir / name
        if destination.is_symlink() or (
            destination.exists() and not destination.is_file()
        ):
            raise OSError(f"fixed output target is not a regular file: {destination}")

    stage = Path(
        tempfile.mkdtemp(prefix=".template-analysis-stage-", dir=output_dir.parent)
    )
    backup = Path(
        tempfile.mkdtemp(prefix=".template-analysis-backup-", dir=output_dir.parent)
    )
    backed_up: list[str] = []
    installed: list[str] = []
    try:
        for name in OUTPUT_NAMES:
            atomic_write(stage / name, payloads[name])
        try:
            for name in OUTPUT_NAMES:
                destination = output_dir / name
                if destination.exists():
                    os.replace(destination, backup / name)
                    backed_up.append(name)
            for name in OUTPUT_NAMES:
                os.replace(stage / name, output_dir / name)
                installed.append(name)
            try:
                directory_fd = os.open(output_dir, os.O_RDONLY | os.O_DIRECTORY)
            except (AttributeError, OSError):
                directory_fd = None
            if directory_fd is not None:
                try:
                    os.fsync(directory_fd)
                finally:
                    os.close(directory_fd)
        except BaseException:
            for name in reversed(installed):
                (output_dir / name).unlink(missing_ok=True)
            for name in reversed(backed_up):
                os.replace(backup / name, output_dir / name)
            raise
    finally:
        shutil.rmtree(stage, ignore_errors=True)
        shutil.rmtree(backup, ignore_errors=True)


def tokenize(text: str) -> list[str]:
    """yxj-unicode-word-v1: Latin/number spans plus individual CJK units."""
    return WORD_RE.findall(unicodedata.normalize("NFKC", text))


def word_count(text: str) -> int:
    return len(tokenize(text))


def sentence_count(text: str) -> int:
    return len(split_sentences(text))


def split_sentences(text: str) -> list[str]:
    """Auditable sentence proxy for spaced Latin and unspaced CJK punctuation."""
    stripped = text.strip()
    if not stripped:
        return []
    parts = re.split(r"(?<=[。！？])|(?<=[.!?])\s+", stripped)
    return [part.strip() for part in parts if part.strip()]


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract_explicit_id(text: str) -> str | None:
    match = re.search(r"\{#([A-Za-z0-9_.:\-]+)\}", text)
    if match:
        return match.group(1)
    match = re.search(r"\\label\{([^}]+)\}", text)
    return match.group(1) if match else None


def label_number(label: str | None) -> int | None:
    if not label:
        return None
    match = re.search(r"\d+", label)
    return int(match.group()) if match else None


def object_prefix(kind: str) -> str:
    return {"figure": "fig", "table": "table", "equation": "eq", "algorithm": "alg"}[
        kind
    ]


def ensure_inside(root: Path, relative: str, *, field_name: str) -> Path:
    candidate_text = Path(relative)
    if candidate_text.is_absolute():
        raise ContractError(f"{field_name} must be manifest-relative: {relative}")
    candidate = (root / candidate_text).resolve()
    resolved_root = root.resolve()
    try:
        candidate.relative_to(resolved_root)
    except ValueError as exc:
        raise ContractError(f"{field_name} escapes manifest root: {relative}") from exc
    return candidate


def read_bounded(path: Path, *, field_name: str) -> bytes:
    if not path.is_file():
        raise ContractError(f"{field_name} is not a file: {path}")
    size = path.stat().st_size
    if size > MAX_SOURCE_BYTES:
        raise ContractError(
            f"{field_name} exceeds {MAX_SOURCE_BYTES} byte safety limit: {path}"
        )
    return path.read_bytes()


def normalize_format(value: Any, path: str) -> str:
    if value not in FORMATS:
        raise ContractError(f"unsupported document format: {value!r}")
    return str(value)


def normalize_manifest(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ContractError("manifest must be a JSON object")
    if raw.get("schema") != SCHEMA:
        raise ContractError(f"manifest schema must be {SCHEMA}")
    allowed_manifest_fields = {
        "schema",
        "corpus_id",
        "target",
        "analysis_mode",
        "design_question",
        "design_metric_ids",
        "documents",
        "official_constraints",
    }
    unknown_manifest_fields = sorted(set(raw) - allowed_manifest_fields)
    if unknown_manifest_fields:
        raise ContractError(
            f"unknown manifest fields: {', '.join(unknown_manifest_fields)}"
        )
    corpus_id = raw.get("corpus_id")
    if not isinstance(corpus_id, str) or not corpus_id.strip():
        raise ContractError("corpus_id must be a non-empty string")
    target = raw.get("target", {})
    if not isinstance(target, dict):
        raise ContractError("target must be an object")
    analysis_mode_declared = "analysis_mode" in raw
    analysis_mode = raw.get("analysis_mode", "case_set")
    if analysis_mode not in {"case_set", "exploratory", "distributional"}:
        raise ContractError(
            "analysis_mode must be case_set, exploratory, or distributional"
        )
    design_question = raw.get("design_question")
    if not isinstance(design_question, str) or not design_question.strip():
        raise ContractError("design_question must be an explicit non-empty string")
    design_metric_ids = raw.get("design_metric_ids")
    if (
        not isinstance(design_metric_ids, list)
        or not design_metric_ids
        or not all(
            isinstance(metric_id, str) and metric_id.strip()
            for metric_id in design_metric_ids
        )
        or len(set(design_metric_ids)) != len(design_metric_ids)
    ):
        raise ContractError(
            "design_metric_ids must be a non-empty array of unique metric IDs"
        )
    documents = raw.get("documents")
    if not isinstance(documents, list) or not documents:
        raise ContractError("documents must be a non-empty array")
    normalized_documents: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(documents):
        if not isinstance(item, dict):
            raise ContractError(f"documents[{index}] must be an object")
        allowed_document_fields = {
            "doc_id",
            "path",
            "format",
            "partition",
            "venue",
            "topic_tags",
            "article_type",
            "year",
            "language",
            "supplement_of",
            "annotations",
            "derivative_of",
            "extractor",
            "inclusion_exception",
        }
        unknown_document_fields = sorted(set(item) - allowed_document_fields)
        if unknown_document_fields:
            raise ContractError(
                f"documents[{index}] unknown fields: {', '.join(unknown_document_fields)}"
            )
        doc_id = item.get("doc_id")
        if not isinstance(doc_id, str) or not doc_id.strip():
            raise ContractError(f"documents[{index}].doc_id must be non-empty")
        if any(character in doc_id for character in ("/", "\\", "#", "\x00")):
            raise ContractError(f"documents[{index}].doc_id contains unsafe characters")
        if doc_id in seen:
            raise ContractError(f"duplicate doc_id: {doc_id}")
        seen.add(doc_id)
        path = item.get("path")
        if not isinstance(path, str) or not path.strip():
            raise ContractError(f"{doc_id}: path must be non-empty")
        source_format = normalize_format(item.get("format"), path)
        partition = item.get("partition")
        if partition not in PARTITIONS:
            raise ContractError(f"{doc_id}: invalid partition {partition!r}")
        language = item.get("language", "und")
        if not isinstance(language, str) or not language.strip():
            raise ContractError(f"{doc_id}: language must be non-empty")
        topic_tags = item.get("topic_tags", [])
        if not isinstance(topic_tags, list) or not all(
            isinstance(tag, str) and tag.strip() for tag in topic_tags
        ):
            raise ContractError(f"{doc_id}: topic_tags must be strings")
        for field_name in ("venue", "article_type"):
            value = item.get(field_name, "unknown")
            if not isinstance(value, str):
                raise ContractError(f"{doc_id}: {field_name} must be a string")
        year = item.get("year")
        if year is not None and (not isinstance(year, int) or isinstance(year, bool)):
            raise ContractError(f"{doc_id}: year must be an integer or null")
        for field_name in (
            "supplement_of",
            "annotations",
            "derivative_of",
            "extractor",
        ):
            value = item.get(field_name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ContractError(
                    f"{doc_id}: {field_name} must be a non-empty string"
                )
        inclusion_exception = item.get("inclusion_exception")
        if inclusion_exception is not None:
            required_exception_fields = {
                "reason",
                "origin",
                "resolution",
                "decision_pointer",
            }
            if not isinstance(inclusion_exception, dict):
                raise ContractError(
                    f"{doc_id}: inclusion_exception must be an owner-grounded object"
                )
            if set(inclusion_exception) != required_exception_fields:
                raise ContractError(
                    f"{doc_id}: inclusion_exception fields must be "
                    "reason, origin, resolution, decision_pointer"
                )
            if inclusion_exception.get("origin") != "owner-stated":
                raise ContractError(
                    f"{doc_id}: inclusion_exception.origin must be owner-stated"
                )
            if inclusion_exception.get("resolution") != "confirmed":
                raise ContractError(
                    f"{doc_id}: inclusion_exception.resolution must be confirmed"
                )
            for field_name in ("reason", "decision_pointer"):
                value = inclusion_exception.get(field_name)
                if not isinstance(value, str) or not value.strip():
                    raise ContractError(
                        f"{doc_id}: inclusion_exception.{field_name} must be non-empty"
                    )
        normalized = {
            "doc_id": doc_id,
            "path": path,
            "format": source_format,
            "partition": partition,
            "venue": item.get("venue", "unknown"),
            "topic_tags": topic_tags,
            "article_type": item.get("article_type", "unknown"),
            "year": year,
            "language": language,
        }
        for optional in (
            "supplement_of",
            "annotations",
            "derivative_of",
            "extractor",
            "inclusion_exception",
        ):
            if item.get(optional) is not None:
                normalized[optional] = item[optional]
        normalized_documents.append(normalized)
    ids = {item["doc_id"] for item in normalized_documents}
    documents_by_id = {item["doc_id"]: item for item in normalized_documents}
    for item in normalized_documents:
        supplement_of = item.get("supplement_of")
        if supplement_of is not None and (
            supplement_of not in ids or supplement_of == item["doc_id"]
        ):
            raise ContractError(
                f"{item['doc_id']}: supplement_of must name another document"
            )
        if (
            supplement_of is not None
            and documents_by_id[supplement_of].get("supplement_of") is not None
        ):
            raise ContractError(
                f"{item['doc_id']}: supplement_of must point directly to a main document"
            )
    constraints = raw.get("official_constraints", [])
    if not isinstance(constraints, list):
        raise ContractError("official_constraints must be an array")
    normalized_constraints: list[dict[str, Any]] = []
    constraint_ids: set[str] = set()
    required_constraint_fields = (
        "constraint_id",
        "source_path",
        "locator",
        "statement",
        "design_surface",
        "affected_dimensions",
        "affected_scopes",
    )
    for index, constraint in enumerate(constraints):
        if not isinstance(constraint, dict):
            raise ContractError(f"official_constraints[{index}] must be an object")
        missing = [key for key in required_constraint_fields if key not in constraint]
        if missing:
            raise ContractError(
                f"official_constraints[{index}] missing fields: {', '.join(missing)}"
            )
        unknown_constraint_fields = sorted(
            set(constraint) - set(required_constraint_fields)
        )
        if unknown_constraint_fields:
            raise ContractError(
                "official_constraints"
                f"[{index}] unknown fields: {', '.join(unknown_constraint_fields)}"
            )
        constraint_id = constraint["constraint_id"]
        if not isinstance(constraint_id, str) or not constraint_id.strip():
            raise ContractError("constraint_id must be non-empty")
        if constraint_id in constraint_ids:
            raise ContractError(f"duplicate constraint_id: {constraint_id}")
        constraint_ids.add(constraint_id)
        if not all(
            isinstance(constraint[key], str) and constraint[key].strip()
            for key in ("source_path", "locator", "statement", "design_surface")
        ):
            raise ContractError(
                f"{constraint_id}: constraint text fields must be non-empty"
            )
        if not all(
            isinstance(constraint[key], list)
            and all(isinstance(value, str) and value for value in constraint[key])
            for key in ("affected_dimensions", "affected_scopes")
        ):
            raise ContractError(
                f"{constraint_id}: affected fields must be string arrays"
            )
        if any(
            not re.fullmatch(r"D(?:0\d|1\d)", dimension)
            for dimension in constraint["affected_dimensions"]
        ):
            raise ContractError(
                f"{constraint_id}: affected_dimensions must use D00-D19"
            )
        normalized_constraints.append({key: constraint[key] for key in constraint})
    return {
        "schema": SCHEMA,
        "corpus_id": corpus_id,
        "target": target,
        "analysis_mode": analysis_mode,
        "analysis_mode_source": (
            "manifest_declared" if analysis_mode_declared else "conservative_default"
        ),
        "design_question": design_question,
        "design_metric_ids": design_metric_ids,
        "documents": normalized_documents,
        "official_constraints": normalized_constraints,
    }


def load_inputs(
    manifest_path: Path,
) -> tuple[dict[str, Any], list[LoadedDocument], list[dict[str, Any]], bytes]:
    manifest_bytes = read_bounded(manifest_path, field_name="manifest")
    try:
        raw_manifest = json.loads(
            manifest_bytes.decode("utf-8"), parse_constant=reject_nonfinite_json
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ContractError(f"manifest is not valid UTF-8 JSON: {exc}") from exc
    manifest = normalize_manifest(raw_manifest)
    root = manifest_path.parent.resolve()
    loaded: list[LoadedDocument] = []
    for spec in manifest["documents"]:
        path = ensure_inside(root, spec["path"], field_name=f"{spec['doc_id']}.path")
        data = read_bounded(path, field_name=f"{spec['doc_id']}.path")
        if b"%PDF-" in data[:1024]:
            raise ContractError(
                f"{spec['doc_id']}: PDF bytes are unsupported; supply a traceable text/HTML/JATS derivative"
            )
        annotation_path: Path | None = None
        annotation_relative: str | None = None
        annotation_hash: str | None = None
        annotations = spec.get("annotations")
        if annotations is not None:
            if not isinstance(annotations, str) or not annotations:
                raise ContractError(f"{spec['doc_id']}.annotations must be a path")
            annotation_path = ensure_inside(
                root, annotations, field_name=f"{spec['doc_id']}.annotations"
            )
            annotation_bytes = read_bounded(
                annotation_path, field_name=f"{spec['doc_id']}.annotations"
            )
            annotation_relative = annotations
            annotation_hash = sha256_bytes(annotation_bytes)
        loaded.append(
            LoadedDocument(
                spec=spec,
                path=path,
                relative_path=spec["path"],
                raw=data,
                source_sha256=sha256_bytes(data),
                annotation_path=annotation_path,
                annotation_relative_path=annotation_relative,
                annotation_sha256=annotation_hash,
            )
        )
    source_hash_owner: dict[str, str] = {}
    for document in loaded:
        previous = source_hash_owner.get(document.source_sha256)
        if previous is not None:
            raise ContractError(
                f"duplicate source bytes for {previous} and {document.spec['doc_id']}; "
                "one paper cannot contribute twice to the independent-paper sample"
            )
        source_hash_owner[document.source_sha256] = document.spec["doc_id"]
    constraints: list[dict[str, Any]] = []
    for constraint in manifest["official_constraints"]:
        source_path = ensure_inside(
            root,
            constraint["source_path"],
            field_name=f"{constraint['constraint_id']}.source_path",
        )
        source_bytes = read_bounded(
            source_path, field_name=f"{constraint['constraint_id']}.source_path"
        )
        try:
            source_text = source_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ContractError(
                f"{constraint['constraint_id']}: official constraint source must be a UTF-8 text derivative"
            ) from exc
        locator_match = re.fullmatch(r"line:(\d+)", constraint["locator"])
        if locator_match is None:
            raise ContractError(
                f"{constraint['constraint_id']}: verified hard constraints require locator line:N"
            )
        line_number = int(locator_match.group(1))
        source_lines = source_text.splitlines()
        if line_number < 1 or line_number > len(source_lines):
            raise ContractError(
                f"{constraint['constraint_id']}: locator {constraint['locator']} is outside the source"
            )
        raw_located_text = clean_text(source_lines[line_number - 1])
        rendered_located_text = clean_text(
            re.sub(r"<[^>]+>", " ", source_lines[line_number - 1])
        )
        statement = clean_text(constraint["statement"])
        if statement not in raw_located_text and statement not in rendered_located_text:
            raise ContractError(
                f"{constraint['constraint_id']}: statement does not match the located source line"
            )
        normalized = dict(constraint)
        normalized["source_sha256"] = sha256_bytes(source_bytes)
        constraints.append(normalized)
    return manifest, loaded, constraints, manifest_bytes


def markdown_table_features(lines: list[str]) -> dict[str, Any]:
    rows = [line for line in lines if line.strip().startswith("|")]
    cells = [
        [cell.strip() for cell in line.strip().strip("|").split("|")] for line in rows
    ]
    columns = max((len(row) for row in cells), default=0)
    separator_present = len(cells) > 1 and all(
        re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells[1]
    )
    data_rows = max(0, len(cells) - (2 if separator_present else 1))
    data_cells = [
        cell for row in cells[(2 if separator_present else 1) :] for cell in row if cell
    ]
    numeric_cells = sum(
        1
        for cell in data_cells
        if re.fullmatch(r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?%?", cell)
    )
    return {
        "row_count": len(cells) - (1 if separator_present else 0),
        "column_count": columns,
        "header_row_count": 1 if cells else 0,
        "data_row_count": data_rows,
        "numeric_cell_count": numeric_cells,
        "data_nonempty_cell_count": len(data_cells),
        "footnote_count": 0,
        "has_rowspan": False,
        "has_colspan": False,
    }


def markdown_citation_targets(text: str) -> list[str]:
    targets: list[str] = []
    for target in re.findall(r"\[[^\]]+\]\(#([A-Za-z0-9_.:\-]+)\)", text):
        if re.match(r"^(?:ref|bib|cite)", target, re.IGNORECASE):
            targets.append(target)
    for group in re.findall(r"\\cite\w*\{([^}]+)\}", text):
        targets.extend(value.strip() for value in group.split(",") if value.strip())
    targets.extend(re.findall(r"@([A-Za-z][A-Za-z0-9_.:\-]+)", text))
    return targets


def surface_links(text: str) -> list[str]:
    """Return explicit URL/URI surfaces without treating ordinary words as links."""
    links = re.findall(
        r"(?:https?://[^\s<>()\]]+|doi:\s*10\.\d{4,9}/[^\s<>()\]]+)",
        text,
        re.IGNORECASE,
    )
    links.extend(
        target
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text)
        if re.match(r"^(?:https?://|doi:)", target.strip(), re.IGNORECASE)
    )
    return [value.rstrip(".,;:") for value in links]


def parse_markdown(text: str) -> ParsedDocument:
    document = ParsedDocument(
        capability={
            "structure": True,
            "objects": True,
            "citations": True,
            "callouts": True,
        }
    )
    lines = text.splitlines()
    line_offsets: list[int] = []
    cursor = 0
    for line in lines:
        line_offsets.append(cursor)
        cursor += len(line) + 1

    index = 0
    if lines and lines[0].strip() == "---":
        end = 1
        while end < len(lines) and lines[end].strip() != "---":
            match = re.match(r"^title:\s*(.+)$", lines[end], re.IGNORECASE)
            if match:
                document.title = match.group(1).strip().strip("\"'")
            end += 1
        index = min(len(lines), end + 1)

    section_path: list[str] = []
    in_references = False
    in_abstract = False
    pending_caption: tuple[str, str, str, str | None] | None = None
    paragraph_lines: list[str] = []
    paragraph_start = 0

    def flush_paragraph() -> None:
        nonlocal paragraph_lines, paragraph_start, pending_caption
        if not paragraph_lines:
            return
        value = clean_text(" ".join(paragraph_lines))
        value = re.sub(r"\{#[^}]+\}", "", value).strip()
        if value and in_abstract:
            document.abstract_paragraphs.append(value)
            document.abstract = clean_text(" ".join(document.abstract_paragraphs))
        elif value:
            document.blocks.append(
                Block(
                    kind="paragraph",
                    text=value,
                    section_path=list(section_path),
                    source_char_start=paragraph_start,
                    callout_targets=re.findall(r"\(#([A-Za-z0-9_.:\-]+)\)", value),
                    citation_targets=markdown_citation_targets(value),
                    external_links=surface_links(value),
                )
            )
        paragraph_lines = []
        if value:
            pending_caption = None

    while index < len(lines):
        raw_line = lines[index]
        stripped = raw_line.strip()
        offset = line_offsets[index]

        heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", stripped)
        if heading:
            flush_paragraph()
            pending_caption = None
            level = len(heading.group(1))
            heading_text = re.sub(r"\s*\{#[^}]+\}\s*$", "", heading.group(2)).strip()
            if heading_text.lower() == "abstract":
                in_abstract = True
                index += 1
                continue
            in_abstract = False
            in_references = bool(REFERENCE_HEADING_RE.fullmatch(heading_text))
            if in_references:
                document.reference_entries = sum(
                    1
                    for future in lines[index + 1 :]
                    if re.match(r"^\s*(?:\[?\d+\]?\.?|[-*])\s+", future)
                )
                break
            section_path = section_path[: level - 1]
            while len(section_path) < level - 1:
                section_path.append("untitled")
            section_path.append(heading_text)
            is_document_title = (
                level == 1
                and len(document.blocks) == 0
                and (
                    not document.title
                    or clean_text(document.title).casefold()
                    == clean_text(heading_text).casefold()
                )
            )
            document.blocks.append(
                Block(
                    kind="heading",
                    text=heading_text,
                    level=level,
                    explicit_id=extract_explicit_id(heading.group(2)),
                    section_path=list(section_path),
                    source_char_start=offset,
                    features={"is_document_title": is_document_title},
                )
            )
            if is_document_title and not document.title:
                document.title = heading_text
            index += 1
            continue
        if in_references:
            index += 1
            continue

        keyword_match = re.match(
            r"^(?:\*\*)?(?:keywords?|index terms)(?:\*\*)?\s*[:—-]\s*(.+)$",
            stripped,
            re.IGNORECASE,
        )
        if keyword_match:
            flush_paragraph()
            document.keywords.extend(
                value.strip()
                for value in re.split(r"[,;]", keyword_match.group(1))
                if value.strip()
            )
            index += 1
            continue

        # Fenced algorithm/pseudocode; ordinary code is excluded from body/callouts.
        fence = re.match(r"^```\s*([A-Za-z0-9_-]*)", stripped)
        if fence:
            flush_paragraph()
            language = fence.group(1).lower()
            end = index + 1
            code_lines: list[str] = []
            while end < len(lines) and not lines[end].strip().startswith("```"):
                code_lines.append(lines[end])
                end += 1
            if end >= len(lines):
                raise ValueError("unclosed Markdown fenced block")
            if language in {"algorithm", "pseudocode"}:
                caption = ""
                explicit_id = None
                label = None
                if pending_caption and pending_caption[0] == "algorithm":
                    caption, label, explicit_id = (
                        pending_caption[1],
                        pending_caption[2],
                        pending_caption[3],
                    )
                code = "\n".join(code_lines).strip()
                lower = code.lower()
                document.blocks.append(
                    Block(
                        kind="algorithm",
                        text=code,
                        caption=caption,
                        label=label,
                        explicit_id=explicit_id,
                        section_path=list(section_path),
                        source_char_start=offset,
                        features={
                            "line_count": len(
                                [line for line in code_lines if line.strip()]
                            ),
                            "has_input": bool(re.search(r"\binput\s*:", lower)),
                            "has_output": bool(re.search(r"\boutput\s*:", lower)),
                            "has_initialize": "initial" in lower,
                            "has_loop": bool(
                                re.search(r"\b(for|while|repeat)\b", lower)
                            ),
                            "has_branch": bool(re.search(r"\b(if|else|case)\b", lower)),
                            "has_return": bool(re.search(r"\breturn\b", lower)),
                        },
                    )
                )
            pending_caption = None
            index = min(len(lines), end + 1)
            continue

        # Display mathematics.
        single_line_dollars = (
            stripped.startswith("$$") and stripped.endswith("$$") and len(stripped) > 4
        )
        if (
            stripped == "$$"
            or single_line_dollars
            or stripped.startswith("\\[")
            or re.match(r"^\\begin\{(?:equation|align|gather|multline)\*?\}", stripped)
        ):
            flush_paragraph()
            end = index + 1
            equation_lines: list[str] = []
            if single_line_dollars:
                equation_lines.append(stripped[2:-2])
                end = index
            elif stripped == "$$":
                while end < len(lines) and lines[end].strip() != "$$":
                    equation_lines.append(lines[end])
                    end += 1
                if end >= len(lines):
                    raise ValueError("unclosed Markdown $$ display-math block")
            elif stripped.startswith("\\["):
                if "\\]" in stripped[2:]:
                    equation_lines.append(stripped[2:].split("\\]", 1)[0])
                    end = index
                else:
                    equation_lines.append(stripped[2:])
                    while end < len(lines) and "\\]" not in lines[end]:
                        equation_lines.append(lines[end])
                        end += 1
                    if end >= len(lines):
                        raise ValueError("unclosed Markdown \\[ display-math block")
                    equation_lines.append(lines[end].split("\\]", 1)[0])
            else:
                env_match = re.match(r"^\\begin\{([^}]+)\}", stripped)
                env = env_match.group(1) if env_match else "equation"
                equation_lines.append(raw_line)
                while end < len(lines) and f"\\end{{{env}}}" not in lines[end]:
                    equation_lines.append(lines[end])
                    end += 1
                if end >= len(lines):
                    raise ValueError(f"unclosed Markdown {env} environment")
                equation_lines.append(lines[end])
            equation = "\n".join(equation_lines).strip()
            explicit_id = extract_explicit_id(equation)
            tag = re.search(r"\\tag\{([^}]+)\}", equation)
            label = f"Eq. ({tag.group(1)})" if tag else None
            document.blocks.append(
                Block(
                    kind="equation",
                    text=equation,
                    explicit_id=explicit_id,
                    label=label,
                    section_path=list(section_path),
                    source_char_start=offset,
                    features={
                        "numbered": bool(tag or explicit_id),
                        "display_line_count": max(
                            1, len([line for line in equation_lines if line.strip()])
                        ),
                    },
                )
            )
            index = min(len(lines), end + 1)
            continue

        # Caption lines are associated with the immediately following object.
        caption_match = re.match(
            r"^(Figure|Fig\.?|Table|Algorithm)\s+(\d+)\s*[:.]\s*(.*?)\s*(\{#[^}]+\})?\s*$",
            stripped,
            re.IGNORECASE,
        )
        if caption_match:
            flush_paragraph()
            raw_kind = caption_match.group(1).lower()
            kind = (
                "figure"
                if raw_kind.startswith("fig")
                else "table"
                if raw_kind == "table"
                else "algorithm"
            )
            caption_text = caption_match.group(3).strip()
            label = f"{kind.title()} {caption_match.group(2)}"
            explicit_id = extract_explicit_id(stripped)
            pending_caption = (kind, caption_text, label, explicit_id)
            index += 1
            continue

        if re.match(r"^<figure\b", stripped, re.IGNORECASE):
            flush_paragraph()
            end = index
            figure_lines: list[str] = []
            closed = False
            while end < len(lines):
                figure_lines.append(lines[end])
                if re.search(r"</figure\s*>", lines[end], re.IGNORECASE):
                    closed = True
                    break
                end += 1
            if not closed:
                raise ValueError("unclosed raw HTML figure in Markdown")
            fragment_parser = SemanticHTMLParser(has_primary=False)
            fragment_parser.feed("\n".join(figure_lines))
            fragment_parser.close()
            figures = [
                block
                for block in fragment_parser.document.blocks
                if block.kind == "figure"
            ]
            if not figures:
                raise ValueError("raw HTML figure in Markdown could not be parsed")
            for figure in figures:
                figure.section_path = list(section_path)
                figure.source_char_start = offset
                if pending_caption and pending_caption[0] == "figure":
                    figure.caption = pending_caption[1] or figure.caption
                    figure.label = pending_caption[2] or figure.label
                    figure.explicit_id = pending_caption[3] or figure.explicit_id
                document.blocks.append(figure)
            pending_caption = None
            index = end + 1
            continue

        images = list(re.finditer(r"!\[([^\]]*)\]\([^)]*\)\s*(\{#[^}]+\})?", raw_line))
        if images:
            flush_paragraph()
            surrounding_text = clean_text(
                re.sub(
                    r"!\[[^\]]*\]\([^)]*\)\s*(?:\{#[^}]+\})?",
                    " ",
                    raw_line,
                )
            )
            if surrounding_text:
                document.warnings.append(
                    "inline Markdown image and prose share a line; relative word position is approximate"
                )
                document.blocks.append(
                    Block(
                        kind="paragraph",
                        text=surrounding_text,
                        section_path=list(section_path),
                        source_char_start=offset,
                        callout_targets=re.findall(
                            r"\(#([A-Za-z0-9_.:\-]+)\)", surrounding_text
                        ),
                        citation_targets=markdown_citation_targets(surrounding_text),
                        external_links=surface_links(surrounding_text),
                    )
                )
            for image_index, image in enumerate(images):
                caption = clean_text(image.group(1))
                explicit_id = extract_explicit_id(image.group(0))
                label = None
                if (
                    image_index == 0
                    and pending_caption
                    and pending_caption[0] == "figure"
                ):
                    caption = pending_caption[1] or caption
                    label = pending_caption[2]
                    explicit_id = pending_caption[3] or explicit_id
                document.blocks.append(
                    Block(
                        kind="figure",
                        caption=caption,
                        label=label,
                        explicit_id=explicit_id,
                        section_path=list(section_path),
                        source_char_start=offset + image.start(),
                        features={
                            "image_count": 1,
                            "alt_text_present": bool(image.group(1)),
                        },
                    )
                )
            pending_caption = None
            index += 1
            continue

        # GFM table: header plus separator and rows.
        if (
            stripped.startswith("|")
            and index + 1 < len(lines)
            and lines[index + 1].strip().startswith("|")
            and all(
                re.fullmatch(r":?-{3,}:?", cell.strip().replace(" ", ""))
                for cell in lines[index + 1].strip().strip("|").split("|")
            )
        ):
            flush_paragraph()
            end = index
            table_lines: list[str] = []
            while end < len(lines) and lines[end].strip().startswith("|"):
                table_lines.append(lines[end])
                end += 1
            caption = ""
            label = None
            explicit_id = None
            if pending_caption and pending_caption[0] == "table":
                caption, label, explicit_id = (
                    pending_caption[1],
                    pending_caption[2],
                    pending_caption[3],
                )
            document.blocks.append(
                Block(
                    kind="table",
                    text="\n".join(table_lines),
                    caption=caption,
                    label=label,
                    explicit_id=explicit_id,
                    section_path=list(section_path),
                    source_char_start=offset,
                    features=markdown_table_features(table_lines),
                )
            )
            pending_caption = None
            index = end
            continue

        if not stripped:
            flush_paragraph()
            pending_caption = (
                None if pending_caption and index + 1 >= len(lines) else pending_caption
            )
            index += 1
            continue
        if not paragraph_lines:
            paragraph_start = offset
        paragraph_lines.append(stripped)
        index += 1

    flush_paragraph()
    return document


class SemanticHTMLParser(HTMLParser):
    VOID_TAGS = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }

    def __init__(self, *, has_primary: bool) -> None:
        super().__init__(convert_charrefs=True)
        self.document = ParsedDocument(
            capability={
                "structure": True,
                "objects": True,
                "citations": True,
                "callouts": True,
            }
        )
        self.has_primary = has_primary
        self.primary_depth = 0 if not has_primary else -1
        self.excluded_stack: list[tuple[str, int]] = []
        self.reference_containers: list[tuple[str, int]] = []
        self.reference_tail = False
        self.stack: list[str] = []
        self.section_path: list[str] = []
        self.capture_kind: str | None = None
        self.capture_tag: str | None = None
        self.capture_depth = 0
        self.capture_text: list[str] = []
        self.capture_attrs: dict[str, str] = {}
        self.capture_features: dict[str, Any] = {}
        self.capture_callouts: list[str] = []
        self.capture_citations: list[str] = []
        self.capture_links: list[str] = []
        self.object_context: dict[str, Any] | None = None
        self.abstract_depth: int | None = None
        self.abstract_tag: str | None = None
        self.abstract_text: list[str] = []
        self.abstract_paragraph_depth: int | None = None
        self.abstract_paragraph_text: list[str] = []
        self.event_index = 0

    def _attrs(self, attrs: list[tuple[str, str | None]]) -> dict[str, str]:
        return {key.lower(): value or "" for key, value in attrs}

    def _active(self) -> bool:
        return (
            self.primary_depth >= 0
            and not self.excluded_stack
            and not self.reference_tail
        )

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attributes = self._attrs(attrs)
        # HTML void elements never emit an end tag. Putting them on the stack
        # would shift every later depth and prevent enclosing objects closing.
        if tag not in self.VOID_TAGS:
            self.stack.append(tag)
        self.event_index += 1
        classes = set(attributes.get("class", "").lower().split())

        if tag == "meta" and attributes.get("name", "").strip().lower() in {
            "keywords",
            "citation_keywords",
        }:
            self.document.keywords.extend(
                value.strip()
                for value in re.split(r"[,;]", attributes.get("content", ""))
                if value.strip()
            )

        if self.has_primary and tag in {"article", "main"} and self.primary_depth < 0:
            self.primary_depth = len(self.stack)
        is_reference_container = tag in {"section", "div", "ol", "ul"} and (
            "references" in classes
            or attributes.get("role", "").lower() == "doc-bibliography"
        )
        if self.primary_depth >= 0 and is_reference_container:
            self.reference_containers.append((tag, len(self.stack)))
        if (self.reference_containers or self.reference_tail) and (
            tag == "li" or attributes.get("role", "").lower() == "doc-biblioentry"
        ):
            self.document.reference_entries += 1
        excluded = self.primary_depth >= 0 and (
            tag in {"nav", "footer", "header", "aside", "script", "style"}
            or is_reference_container
        )
        if excluded:
            self.excluded_stack.append((tag, len(self.stack)))
        if not self._active():
            return

        if self.abstract_depth is not None:
            if tag == "p" and self.abstract_paragraph_depth is None:
                self.abstract_paragraph_depth = len(self.stack)
                self.abstract_paragraph_text = []
            return
        is_abstract = tag in {"section", "div"} and (
            "abstract" in classes
            or attributes.get("id", "").strip().lower() == "abstract"
            or attributes.get("role", "").strip().lower() == "doc-abstract"
        )
        if is_abstract:
            self.abstract_depth = len(self.stack)
            self.abstract_tag = tag
            self.abstract_text = []
            self.abstract_paragraph_depth = None
            self.abstract_paragraph_text = []
            return

        # Nested counters for a captured table/object.
        if self.object_context is not None:
            context = self.object_context
            if context["kind"] == "table":
                if tag == "tr":
                    context["current_row"] = []
                    context["rows"].append(context["current_row"])
                elif tag in {"th", "td"}:
                    if context.get("current_row") is None:
                        context["current_row"] = []
                        context["rows"].append(context["current_row"])
                    context["current_cell"] = {
                        "kind": tag,
                        "depth": len(self.stack),
                        "text": [],
                    }
                    if "rowspan" in attributes:
                        context["features"]["has_rowspan"] = True
                    if "colspan" in attributes:
                        context["features"]["has_colspan"] = True
            if tag == "figcaption" or (context["kind"] == "table" and tag == "caption"):
                context["caption_depth"] = len(self.stack)
            if context.get("caption_depth"):
                return

        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._begin_capture("heading", tag, attributes)
            return
        if tag == "p" and self.object_context is None:
            self._begin_capture("paragraph", tag, attributes)
            return
        if tag == "figure" and self.object_context is None:
            self.object_context = {
                "kind": "figure",
                "tag": tag,
                "depth": len(self.stack),
                "attrs": attributes,
                "text": [],
                "caption": [],
                "caption_depth": 0,
                "features": {"image_count": 0, "alt_text_present": False},
                "source": self.event_index,
            }
            return
        if tag == "table" and self.object_context is None:
            if attributes.get("role", "").lower() == "presentation":
                self.excluded_stack.append((tag, len(self.stack)))
                return
            self.object_context = {
                "kind": "table",
                "tag": tag,
                "depth": len(self.stack),
                "attrs": attributes,
                "text": [],
                "caption": [],
                "caption_depth": 0,
                "features": {
                    "footnote_count": 0,
                    "has_rowspan": False,
                    "has_colspan": False,
                },
                "rows": [],
                "current_row": None,
                "current_cell": None,
                "source": self.event_index,
            }
            return
        is_display_math = (
            tag in {"div", "span"}
            and any("disp-formula" in value or "equation" == value for value in classes)
        ) or (tag == "math" and attributes.get("display", "").lower() == "block")
        if is_display_math and self.object_context is None:
            self.object_context = {
                "kind": "equation",
                "tag": tag,
                "depth": len(self.stack),
                "attrs": attributes,
                "text": [],
                "caption": [],
                "caption_depth": 0,
                "features": {
                    "numbered": bool(attributes.get("id")),
                    "display_line_count": 1,
                },
                "source": self.event_index,
            }
            return
        if (
            tag == "pre"
            and self.object_context is None
            and ("algorithm" in classes or "pseudocode" in classes)
        ):
            self.object_context = {
                "kind": "algorithm",
                "tag": tag,
                "depth": len(self.stack),
                "attrs": attributes,
                "text": [],
                "caption": [],
                "caption_depth": 0,
                "features": {},
                "source": self.event_index,
            }
            return
        if self.object_context and tag == "img":
            self.object_context["features"]["image_count"] += 1
            self.object_context["features"]["alt_text_present"] = bool(
                attributes.get("alt")
            )
        if tag == "a" and self.capture_kind == "paragraph":
            href = attributes.get("href", "")
            if href.startswith("#"):
                target = href[1:]
                if (
                    attributes.get("role", "").lower() == "doc-biblioref"
                    or "citation" in classes
                    or re.match(r"^(?:ref|bib|cite)", target, re.IGNORECASE)
                ):
                    self.capture_citations.append(target)
                else:
                    self.capture_callouts.append(target)
            elif re.match(r"^(?:https?://|doi:)", href, re.IGNORECASE):
                self.capture_links.append(href)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag.lower() not in self.VOID_TAGS:
            self.handle_endtag(tag)

    def _begin_capture(self, kind: str, tag: str, attrs: dict[str, str]) -> None:
        self.capture_kind = kind
        self.capture_tag = tag
        self.capture_depth = len(self.stack)
        self.capture_text = []
        self.capture_attrs = attrs
        self.capture_callouts = []
        self.capture_citations = []
        self.capture_links = []

    def handle_data(self, data: str) -> None:
        if not self._active():
            return
        if self.abstract_depth is not None:
            self.abstract_text.append(data)
            if self.abstract_paragraph_depth is not None:
                self.abstract_paragraph_text.append(data)
            return
        if self.object_context is not None:
            if self.object_context.get("current_cell") is not None:
                self.object_context["current_cell"]["text"].append(data)
            if self.object_context.get("caption_depth"):
                self.object_context["caption"].append(data)
            else:
                self.object_context["text"].append(data)
        elif self.capture_kind:
            self.capture_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in self.VOID_TAGS:
            return
        depth = len(self.stack)
        handled_abstract = False
        if self._active() and self.abstract_depth is not None:
            handled_abstract = True
            if self.abstract_paragraph_depth == depth and tag == "p":
                paragraph = clean_text("".join(self.abstract_paragraph_text))
                if paragraph:
                    self.document.abstract_paragraphs.append(paragraph)
                self.abstract_paragraph_depth = None
                self.abstract_paragraph_text = []
            if self.abstract_depth == depth and self.abstract_tag == tag:
                abstract = clean_text("".join(self.abstract_text))
                if abstract and not self.document.abstract_paragraphs:
                    self.document.abstract_paragraphs.append(abstract)
                self.document.abstract = clean_text(
                    " ".join(self.document.abstract_paragraphs)
                )
                self.abstract_depth = None
                self.abstract_tag = None
                self.abstract_text = []
                self.abstract_paragraph_depth = None
                self.abstract_paragraph_text = []
        if self._active() and not handled_abstract:
            if self.object_context is not None:
                context = self.object_context
                current_cell = context.get("current_cell")
                if (
                    context["kind"] == "table"
                    and current_cell is not None
                    and current_cell.get("depth") == depth
                    and tag in {"th", "td"}
                ):
                    current_cell["text"] = clean_text(
                        "".join(current_cell.get("text", []))
                    )
                    context["current_row"].append(current_cell)
                    context["current_cell"] = None
                if context["kind"] == "table" and tag == "tr":
                    context["current_row"] = None
                if context.get("caption_depth") == depth and tag in {
                    "figcaption",
                    "caption",
                }:
                    context["caption_depth"] = 0
                if context["depth"] == depth and context["tag"] == tag:
                    self._finish_object(context)
                    self.object_context = None
            elif (
                self.capture_kind
                and self.capture_depth == depth
                and self.capture_tag == tag
            ):
                self._finish_capture()
        if self.excluded_stack and self.excluded_stack[-1] == (tag, depth):
            self.excluded_stack.pop()
        if self.reference_containers and self.reference_containers[-1] == (tag, depth):
            self.reference_containers.pop()
        if (
            self.has_primary
            and self.primary_depth == depth
            and tag in {"article", "main"}
        ):
            self.primary_depth = -1
            self.reference_tail = False
        if self.stack:
            self.stack.pop()

    def _finish_capture(self) -> None:
        value = clean_text("".join(self.capture_text))
        if value:
            if self.capture_kind == "heading":
                level = int(self.capture_tag[-1]) if self.capture_tag else 1
                if REFERENCE_HEADING_RE.fullmatch(value):
                    self.reference_tail = True
                else:
                    self.section_path = self.section_path[: level - 1]
                    while len(self.section_path) < level - 1:
                        self.section_path.append("untitled")
                    self.section_path.append(value)
                    is_document_title = (
                        level == 1
                        and not self.document.blocks
                        and (
                            not self.document.title
                            or clean_text(self.document.title).casefold()
                            == clean_text(value).casefold()
                        )
                    )
                    self.document.blocks.append(
                        Block(
                            kind="heading",
                            text=value,
                            level=level,
                            explicit_id=self.capture_attrs.get("id") or None,
                            section_path=list(self.section_path),
                            source_char_start=self.event_index,
                            features={"is_document_title": is_document_title},
                        )
                    )
                    if is_document_title and not self.document.title:
                        self.document.title = value
            else:
                self.document.blocks.append(
                    Block(
                        kind="paragraph",
                        text=value,
                        section_path=list(self.section_path),
                        source_char_start=self.event_index,
                        callout_targets=list(self.capture_callouts),
                        citation_targets=list(self.capture_citations),
                        external_links=list(self.capture_links),
                    )
                )
        self.capture_kind = None
        self.capture_tag = None
        self.capture_text = []
        self.capture_attrs = {}
        self.capture_callouts = []
        self.capture_citations = []
        self.capture_links = []

    def _finish_object(self, context: dict[str, Any]) -> None:
        kind = context["kind"]
        text = clean_text("".join(context["text"]))
        caption = clean_text("".join(context["caption"]))
        features = dict(context["features"])
        if kind == "table":
            rows = [row for row in context.get("rows", []) if row]
            data_cells = [
                cell
                for row in rows
                for cell in row
                if cell.get("kind") == "td" and cell.get("text")
            ]
            features["row_count"] = len(rows)
            features["column_count"] = max((len(row) for row in rows), default=0)
            features["header_row_count"] = sum(
                bool(row) and all(cell.get("kind") == "th" for cell in row)
                for row in rows
            )
            features["data_row_count"] = sum(
                any(cell.get("kind") == "td" for cell in row) for row in rows
            )
            features["numeric_cell_count"] = sum(
                bool(
                    re.fullmatch(
                        r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?%?",
                        str(cell.get("text", "")),
                    )
                )
                for cell in data_cells
            )
            features["data_nonempty_cell_count"] = len(data_cells)
        if kind == "algorithm":
            lines = [
                line for line in "".join(context["text"]).splitlines() if line.strip()
            ]
            lower = text.lower()
            features = {
                "line_count": len(lines),
                "has_input": bool(re.search(r"\binput\s*:", lower)),
                "has_output": bool(re.search(r"\boutput\s*:", lower)),
                "has_initialize": "initial" in lower,
                "has_loop": bool(re.search(r"\b(for|while|repeat)\b", lower)),
                "has_branch": bool(re.search(r"\b(if|else|case)\b", lower)),
                "has_return": bool(re.search(r"\breturn\b", lower)),
            }
        explicit_id = context["attrs"].get("id") or None
        label_match = re.search(
            r"\b(?:Figure|Fig\.?|Table|Eq(?:uation)?\.?|Algorithm)\s*\(?\d+\)?",
            caption or text,
            re.IGNORECASE,
        )
        label = label_match.group(0) if label_match else None
        self.document.blocks.append(
            Block(
                kind=kind,
                text=text,
                caption=caption,
                explicit_id=explicit_id,
                label=label,
                section_path=list(self.section_path),
                source_char_start=context["source"],
                features=features,
            )
        )


def parse_html(text: str) -> ParsedDocument:
    has_primary = bool(re.search(r"<(?:article|main)\b", text, re.IGNORECASE))
    parser = SemanticHTMLParser(has_primary=has_primary)
    title = re.search(r"<title\b[^>]*>(.*?)</title>", text, re.IGNORECASE | re.DOTALL)
    if title:
        parser.document.title = clean_text(re.sub(r"<[^>]+>", " ", title.group(1)))
    parser.feed(text)
    parser.close()
    if not has_primary:
        parser.document.warnings.append(
            "semantic article/main container absent; body fallback used"
        )
    return parser.document


def element_text(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return clean_text(" ".join(part for part in element.itertext()))


def find_first_local(element: ET.Element, name: str) -> ET.Element | None:
    for child in element.iter():
        if local_name(child.tag) == name:
            return child
    return None


def jats_table_features(element: ET.Element) -> dict[str, Any]:
    rows = [node for node in element.iter() if local_name(node.tag) == "tr"]
    header_cells = [node for node in element.iter() if local_name(node.tag) == "th"]
    data_cells = [node for node in element.iter() if local_name(node.tag) == "td"]
    nonempty_data_cells = [cell for cell in data_cells if element_text(cell)]
    numeric_cells = sum(
        1
        for cell in nonempty_data_cells
        if re.fullmatch(r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?%?", element_text(cell))
    )
    row_widths = [
        sum(1 for child in row if local_name(child.tag) in {"th", "td"}) for row in rows
    ]
    return {
        "row_count": len(rows),
        "column_count": max(row_widths, default=0),
        "header_row_count": 1 if header_cells else 0,
        "data_row_count": max(0, len(rows) - (1 if header_cells else 0)),
        "numeric_cell_count": numeric_cells,
        "data_nonempty_cell_count": len(nonempty_data_cells),
        "footnote_count": sum(
            1
            for node in element.iter()
            if local_name(node.tag) in {"fn", "table-wrap-foot"}
        ),
        "has_rowspan": any("rowspan" in node.attrib for node in element.iter()),
        "has_colspan": any("colspan" in node.attrib for node in element.iter()),
    }


def parse_jats(text: str) -> ParsedDocument:
    if re.search(r"<!\s*(?:DOCTYPE|ENTITY)\b", text, re.IGNORECASE):
        raise ValueError("DOCTYPE/ENTITY declarations are unsupported for XML safety")
    root = ET.fromstring(text)
    document = ParsedDocument(
        capability={
            "structure": True,
            "objects": True,
            "citations": True,
            "callouts": True,
        }
    )
    title = find_first_local(root, "article-title")
    document.title = element_text(title)
    abstract = find_first_local(root, "abstract")
    document.abstract = element_text(abstract)
    if abstract is not None:
        document.abstract_paragraphs = [
            value
            for node in abstract.iter()
            if local_name(node.tag) == "p" and (value := element_text(node))
        ]
        if document.abstract and not document.abstract_paragraphs:
            document.abstract_paragraphs = [document.abstract]
    for node in root.iter():
        if local_name(node.tag) in {"kwd", "keyword"}:
            value = element_text(node)
            if value:
                document.keywords.append(value)
    body = next((node for node in root.iter() if local_name(node.tag) == "body"), None)
    if body is None:
        raise ValueError("JATS body element is missing")

    def walk(element: ET.Element, section_path: list[str], depth: int = 0) -> None:
        if depth > 256:
            raise ValueError("JATS nesting exceeds the 256-level safety limit")
        for child in list(element):
            name = local_name(child.tag)
            if name == "sec":
                title_node = next(
                    (node for node in list(child) if local_name(node.tag) == "title"),
                    None,
                )
                heading_text = element_text(title_node) or "untitled"
                level = len(section_path) + 1
                new_path = section_path + [heading_text]
                document.blocks.append(
                    Block(
                        kind="heading",
                        text=heading_text,
                        level=level,
                        explicit_id=child.attrib.get("id"),
                        section_path=new_path,
                    )
                )
                walk(child, new_path, depth + 1)
            elif name in {"title", "label", "caption", "alternatives", "graphic"}:
                continue
            elif name == "p":
                value = element_text(child)
                targets = [
                    node.attrib.get("rid", "")
                    for node in child.iter()
                    if local_name(node.tag) == "xref"
                    and node.attrib.get("rid")
                    and node.attrib.get("ref-type", "").lower() != "bibr"
                ]
                citation_targets = [
                    node.attrib.get("rid", "")
                    for node in child.iter()
                    if local_name(node.tag) == "xref"
                    and node.attrib.get("rid")
                    and node.attrib.get("ref-type", "").lower() == "bibr"
                ]
                external_links: list[str] = []
                for node in child.iter():
                    if local_name(node.tag) not in {"ext-link", "uri"}:
                        continue
                    candidates = [
                        attr_value
                        for attr_name, attr_value in node.attrib.items()
                        if local_name(attr_name) == "href"
                    ]
                    candidates.append(element_text(node))
                    external_links.extend(
                        candidate
                        for candidate in candidates
                        if re.match(
                            r"^(?:https?://|doi:)", candidate or "", re.IGNORECASE
                        )
                    )
                if value:
                    document.blocks.append(
                        Block(
                            kind="paragraph",
                            text=value,
                            section_path=list(section_path),
                            callout_targets=targets,
                            citation_targets=citation_targets,
                            external_links=external_links,
                        )
                    )
            elif name == "fig-group":
                for figure in child.iter():
                    if figure is not child and local_name(figure.tag) == "fig":
                        add_jats_object(figure, "figure", section_path)
            elif name == "fig":
                add_jats_object(child, "figure", section_path)
            elif name == "table-wrap-group":
                for wrapper in list(child):
                    if local_name(wrapper.tag) == "table-wrap":
                        add_jats_object(wrapper, "table", section_path)
            elif name == "table-wrap":
                add_jats_object(child, "table", section_path)
            elif name == "disp-formula":
                add_jats_object(child, "equation", section_path)
            elif name in {"boxed-text", "code"} and (
                child.attrib.get("content-type", "").lower() == "algorithm"
                or child.attrib.get("code-type", "").lower()
                in {"algorithm", "pseudocode"}
            ):
                add_jats_object(child, "algorithm", section_path)
            elif name in {"ref-list", "back"}:
                continue
            else:
                walk(child, section_path, depth + 1)

    def add_jats_object(
        element: ET.Element, kind: str, section_path: list[str]
    ) -> None:
        caption_node = next(
            (node for node in list(element) if local_name(node.tag) == "caption"), None
        )
        label_node = next(
            (node for node in list(element) if local_name(node.tag) == "label"), None
        )
        caption = element_text(caption_node)
        label = element_text(label_node) or None
        full_text = element_text(element)
        features: dict[str, Any]
        if kind == "figure":
            direct_graphics = sum(
                1
                for node in list(element)
                if local_name(node.tag) in {"graphic", "media"}
            )
            alternative_graphic = any(
                local_name(node.tag) in {"graphic", "media"}
                for alternative in element.iter()
                if local_name(alternative.tag) == "alternatives"
                for node in alternative.iter()
            )
            graphics = direct_graphics or (1 if alternative_graphic else 0)
            features = {"image_count": graphics, "alt_text_present": False}
        elif kind == "table":
            features = jats_table_features(element)
        elif kind == "equation":
            features = {
                "numbered": bool(label or element.attrib.get("id")),
                "display_line_count": max(1, full_text.count("\\\\") + 1),
            }
        else:
            code_node = next(
                (node for node in element.iter() if local_name(node.tag) == "code"),
                None,
            )
            code_text = (
                "".join(code_node.itertext()) if code_node is not None else full_text
            )
            lower = code_text.lower()
            features = {
                "line_count": len(
                    [line for line in code_text.splitlines() if line.strip()]
                ),
                "has_input": bool(re.search(r"\binput\s*:", lower)),
                "has_output": bool(re.search(r"\boutput\s*:", lower)),
                "has_initialize": "initial" in lower,
                "has_loop": bool(re.search(r"\b(for|while|repeat)\b", lower)),
                "has_branch": bool(re.search(r"\b(if|else|case)\b", lower)),
                "has_return": bool(re.search(r"\breturn\b", lower)),
            }
        document.blocks.append(
            Block(
                kind=kind,
                text=full_text,
                caption=caption,
                label=label,
                explicit_id=element.attrib.get("id"),
                section_path=list(section_path),
                features=features,
            )
        )

    walk(body, [], 0)
    ref_list = next(
        (node for node in root.iter() if local_name(node.tag) == "ref-list"), None
    )
    if ref_list is not None:
        document.reference_entries = sum(
            1 for node in ref_list.iter() if local_name(node.tag) == "ref"
        )
    return document


def parse_txt(text: str) -> ParsedDocument:
    document = ParsedDocument(
        capability={
            "structure": False,
            "objects": False,
            "citations": True,
            "callouts": False,
        }
    )
    paragraphs = [
        clean_text(part) for part in re.split(r"\n\s*\n", text) if clean_text(part)
    ]
    for index, paragraph in enumerate(paragraphs):
        document.blocks.append(
            Block(kind="paragraph", text=paragraph, source_char_start=index)
        )
    return document


def parse_document(source_format: str, raw: bytes) -> ParsedDocument:
    text = raw.decode("utf-8")
    if source_format == "markdown":
        return parse_markdown(text)
    if source_format == "html":
        return parse_html(text)
    if source_format == "jats":
        return parse_jats(text)
    if source_format == "txt":
        return parse_txt(text)
    raise ValueError(f"unsupported format {source_format}")


def metric(
    value: Any,
    *,
    status: str = "ok",
    unit: str = "count",
    method: str = "deterministic",
    numerator: int | float | None = None,
    denominator: int | float | None = None,
) -> dict[str, Any]:
    if status not in MISSING_STATUSES:
        raise ValueError(f"invalid metric status: {status}")
    return {
        "status": status,
        "value": value,
        "numerator": numerator,
        "denominator": denominator,
        "unit": unit,
        "method": method,
    }


def canonical_section_label(value: str) -> str | None:
    normalized = re.sub(r"[^a-z]+", " ", value.lower()).strip()
    choices = {
        "introduction": ("introduction", "background"),
        "related_work": ("related work", "literature review"),
        "methods": ("method", "methods", "methodology", "materials and methods"),
        "results": ("result", "results", "experiments", "experimental results"),
        "discussion": ("discussion",),
        "conclusion": ("conclusion", "conclusions"),
        "limitations": ("limitation", "limitations"),
    }
    for label, variants in choices.items():
        if normalized in variants:
            return label
    return None


def language_profile(value: Any) -> str:
    normalized = str(value or "und").strip().lower().replace("_", "-")
    return normalized.split("-", 1)[0] or "und"


def mattr50(tokens: list[str]) -> float | None:
    lowered = [token.lower() for token in tokens]
    if not lowered:
        return None
    if len(lowered) < 50:
        return len(set(lowered)) / len(lowered)
    return statistics.fmean(
        len(set(lowered[index : index + 50])) / 50 for index in range(len(lowered) - 49)
    )


def assign_positions(document: ParsedDocument) -> tuple[str, int]:
    body_parts: list[str] = []
    cursor = 0
    for index, block in enumerate(document.blocks):
        block.source_block_index = index
        block.body_word_offset = cursor
        if block.kind == "paragraph":
            body_parts.append(block.text)
            cursor += word_count(block.text)
    return "\n".join(body_parts), cursor


def build_objects(
    doc_id: str, source_sha256: str, document: ParsedDocument, body_words: int
) -> list[dict[str, Any]]:
    counters: Counter[str] = Counter()
    objects: list[dict[str, Any]] = []
    seen_object_ids: set[str] = set()
    block_to_object: dict[int, dict[str, Any]] = {}
    target_map: dict[str, dict[str, Any]] = {}
    number_map: dict[tuple[str, int], dict[str, Any]] = {}

    for block in document.blocks:
        if block.kind not in OBJECT_TYPES:
            continue
        counters[block.kind] += 1
        ordinal = counters[block.kind]
        prefix = object_prefix(block.kind)
        explicit_id = block.explicit_id
        identifier = explicit_id or f"{prefix}-{ordinal}"
        object_id = f"{doc_id}#{identifier}"
        if object_id in seen_object_ids:
            raise ValueError(f"duplicate explicit object ID: {object_id}")
        seen_object_ids.add(object_id)
        label = block.label or (
            f"Eq. ({ordinal})"
            if block.kind == "equation"
            else f"{block.kind.title()} {ordinal}"
        )
        caption_text = clean_text(block.caption)
        normalized_position = (
            min(1.0, max(0.0, block.body_word_offset / body_words))
            if body_words
            else 0.0
        )
        fingerprint_source = {
            "doc_id": doc_id,
            "object_type": block.kind,
            "ordinal": ordinal,
            "explicit_id": explicit_id,
            "label": label,
            "caption": caption_text,
            "section_path": block.section_path,
            "features": block.features,
        }
        fingerprint = sha256_bytes(
            canonical_json(fingerprint_source, pretty=False).rstrip(b"\n")
        )
        item: dict[str, Any] = {
            "schema": OBJECT_SCHEMA,
            "doc_id": doc_id,
            "source_sha256": source_sha256,
            "object_id": object_id,
            "object_fingerprint": f"sha256:{fingerprint}",
            "object_type": block.kind,
            "ordinal": ordinal,
            "explicit_id": explicit_id,
            "label": label,
            "section_path": list(block.section_path),
            "position": {
                "source_block_index": block.source_block_index,
                "source_char_start": block.source_char_start,
                "body_word_offset": block.body_word_offset,
                "normalized_word_position": normalized_position,
            },
            "caption": {
                "present": bool(caption_text),
                "text": caption_text,
                "word_count": word_count(caption_text),
                "sentence_count": sentence_count(caption_text),
                "panel_label_proxy": len(
                    re.findall(
                        r"(?:^|[.;])\s*\(?[a-z]\)\s*", caption_text, re.IGNORECASE
                    )
                ),
                "uncertainty_marker_proxy": len(
                    re.findall(
                        r"\b(?:confidence interval|error bar|uncertainty|standard deviation|s\.?d\.?)\b",
                        caption_text,
                        re.IGNORECASE,
                    )
                ),
            },
            "features": block.features,
            "callouts": [],
            "annotation": None,
        }
        objects.append(item)
        block_to_object[block.source_block_index] = item
        target_map[identifier.lower()] = item
        target_map[object_id.lower()] = item
        number = label_number(label) or ordinal
        number_map[(block.kind, number)] = item

    kind_alias = {
        "fig": "figure",
        "figure": "figure",
        "table": "table",
        "eq": "equation",
        "equation": "equation",
        "algorithm": "algorithm",
    }
    for block in document.blocks:
        if block.kind != "paragraph":
            continue
        paragraph_words = word_count(block.text)
        paragraph_position = block.body_word_offset / body_words if body_words else 0.0
        resolved: list[tuple[dict[str, Any], str]] = []
        for target in block.callout_targets:
            target_item = target_map.get(target.lower())
            if target_item:
                resolved.append((target_item, f"#{target}"))
        for match in CALL_OUT_RE.finditer(block.text):
            kind = kind_alias[match.group("kind").lower().rstrip(".")]
            numbered_item = number_map.get((kind, int(match.group("number"))))
            if numbered_item:
                resolved.append((numbered_item, match.group(0)))
        seen: set[str] = set()
        for item, surface in resolved:
            if item["object_id"] in seen:
                continue
            seen.add(item["object_id"])
            lead_lag = block.body_word_offset - item["position"]["body_word_offset"]
            item["callouts"].append(
                {
                    "source_block_index": block.source_block_index,
                    "surface": surface,
                    "paragraph_word_count": paragraph_words,
                    "normalized_word_position": min(1.0, max(0.0, paragraph_position)),
                    "lead_lag_words": lead_lag,
                }
            )
    return objects


def load_annotations(path: Path) -> list[dict[str, Any]]:
    try:
        raw = json.loads(
            path.read_text(encoding="utf-8"), parse_constant=reject_nonfinite_json
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"annotation file is not valid UTF-8 JSON: {exc}") from exc
    if not isinstance(raw, dict) or raw.get("schema") != "template-annotations/1.0":
        raise ValueError("annotation schema must be template-annotations/1.0")
    if set(raw) != {"schema", "annotations"}:
        raise ValueError("annotation document fields must be schema and annotations")
    annotations = raw.get("annotations")
    if not isinstance(annotations, list) or not all(
        isinstance(item, dict) for item in annotations
    ):
        raise ValueError("annotations must be an object array")
    return annotations


def annotation_contract_error(annotation: dict[str, Any]) -> str | None:
    allowed_fields = {
        "doc_id",
        "object_id",
        "object_fingerprint",
        "source_sha256",
        "origin",
        "resolution",
        "role",
        "panels",
        "encoding",
    }
    unknown_fields = sorted(set(annotation) - allowed_fields)
    if unknown_fields:
        return f"unknown annotation fields: {', '.join(unknown_fields)}"
    if not isinstance(annotation.get("doc_id"), str) or not annotation["doc_id"]:
        return "missing annotation doc_id"
    if not isinstance(annotation.get("object_id"), str) or not annotation["object_id"]:
        return "missing annotation object_id"
    if annotation.get("origin") not in {
        "artifact-observed",
        "owner-stated",
        "model-derived",
        "model-proposed",
    }:
        return "unknown annotation origin"
    if annotation.get("resolution") not in {"accepted", "candidate", "rejected"}:
        return "unknown annotation resolution"
    if annotation.get("resolution") == "accepted" and not (
        annotation.get("source_sha256") or annotation.get("object_fingerprint")
    ):
        return "accepted annotation requires source_sha256 or object_fingerprint"
    source_hash = annotation.get("source_sha256")
    if source_hash is not None and (
        not isinstance(source_hash, str)
        or re.fullmatch(r"[0-9a-f]{64}", source_hash) is None
    ):
        return "source_sha256 must be a lowercase SHA-256 digest"
    fingerprint = annotation.get("object_fingerprint")
    if fingerprint is not None and (
        not isinstance(fingerprint, str)
        or re.fullmatch(r"sha256:[0-9a-f]{64}", fingerprint) is None
    ):
        return "object_fingerprint must be sha256:<lowercase digest>"
    role = annotation.get("role")
    if not isinstance(role, dict) or role.get("primary") not in ANNOTATION_ROLES:
        return "unknown or missing primary role"
    if set(role) - {"primary", "secondary"}:
        return "unknown role fields"
    secondary = role.get("secondary", [])
    if not isinstance(secondary, list) or any(
        value not in ANNOTATION_ROLES for value in secondary
    ):
        return "unknown secondary role"
    if len(secondary) != len(set(secondary)):
        return "secondary roles must be unique"
    panels = annotation.get("panels", [])
    if not isinstance(panels, list):
        return "panels must be an array"
    for panel in panels:
        if not isinstance(panel, dict):
            return "panel must be an object"
        if set(panel) != {"panel_id", "order", "role", "encodings"}:
            return "panel fields must be panel_id, order, role, encodings"
        if not isinstance(panel.get("panel_id"), str) or not panel["panel_id"]:
            return "panel_id must be non-empty"
        if (
            not isinstance(panel.get("order"), int)
            or isinstance(panel.get("order"), bool)
            or panel["order"] < 1
        ):
            return "panel order must be a positive integer"
        if panel.get("role") not in ANNOTATION_ROLES:
            return "panel has unknown role"
        encodings = panel.get("encodings", [])
        if not isinstance(encodings, list) or any(
            value not in ANNOTATION_ENCODINGS for value in encodings
        ):
            return "panel has unknown encoding"
        if len(encodings) != len(set(encodings)):
            return "panel encodings must be unique"
    if "encoding" in annotation and not isinstance(annotation["encoding"], dict):
        return "encoding must be an object"
    return None


def apply_annotations(
    loaded: LoadedDocument,
    objects: list[dict[str, Any]],
    warnings: list[dict[str, Any]],
) -> dict[str, Any]:
    states: Counter[str] = Counter()
    roles: Counter[str] = Counter()
    if loaded.annotation_path is None:
        return {"states": {}, "accepted_roles": {}}
    try:
        annotations = load_annotations(loaded.annotation_path)
    except ValueError as exc:
        warnings.append(
            {
                "doc_id": loaded.spec["doc_id"],
                "code": "annotation_parse_failed",
                "message": str(exc),
            }
        )
        return {"states": {"parse_failed": 1}, "accepted_roles": {}}
    by_id = {item["object_id"]: item for item in objects}
    relevant = [
        annotation
        for annotation in annotations
        if annotation.get("doc_id") == loaded.spec["doc_id"]
    ]
    annotation_counts = Counter(annotation.get("object_id") for annotation in relevant)
    conflicts = {
        object_id for object_id, count in annotation_counts.items() if count > 1
    }
    for object_id in sorted(str(value) for value in conflicts):
        states["conflict"] += 1
        warnings.append(
            {
                "doc_id": loaded.spec["doc_id"],
                "object_id": object_id,
                "code": "annotation_conflict",
                "message": "multiple annotations target the same object; all were excluded",
            }
        )
    for annotation in relevant:
        if annotation.get("object_id") in conflicts:
            continue
        contract_error = annotation_contract_error(annotation)
        if contract_error:
            states["invalid"] += 1
            warnings.append(
                {
                    "doc_id": loaded.spec["doc_id"],
                    "object_id": annotation.get("object_id"),
                    "code": "annotation_invalid",
                    "message": contract_error,
                }
            )
            continue
        object_id = annotation.get("object_id")
        if object_id not in by_id:
            states["unknown_object"] += 1
            warnings.append(
                {
                    "doc_id": loaded.spec["doc_id"],
                    "code": "annotation_unknown_object",
                    "message": f"annotation target is absent: {object_id}",
                }
            )
            continue
        resolution = annotation.get("resolution")
        item = by_id[object_id]
        if resolution == "accepted":
            if annotation.get("origin") not in {"artifact-observed", "owner-stated"}:
                states["requires_owner_confirmation"] += 1
                warnings.append(
                    {
                        "doc_id": loaded.spec["doc_id"],
                        "object_id": object_id,
                        "code": "annotation_requires_owner_confirmation",
                        "message": "model-derived/model-proposed annotations cannot be accepted in place",
                    }
                )
                continue
            source_match = annotation.get("source_sha256") == loaded.source_sha256
            fingerprint_match = (
                annotation.get("object_fingerprint") == item["object_fingerprint"]
            )
            if not (source_match or fingerprint_match):
                states["stale"] += 1
                warnings.append(
                    {
                        "doc_id": loaded.spec["doc_id"],
                        "object_id": object_id,
                        "code": "annotation_stale",
                        "message": "accepted annotation has no matching source hash or object fingerprint",
                    }
                )
                continue
            item["annotation"] = {
                key: annotation[key]
                for key in ("origin", "resolution", "role", "panels", "encoding")
                if key in annotation
            }
            states["accepted"] += 1
            role = annotation.get("role", {}).get("primary")
            if isinstance(role, str):
                roles[role] += 1
        elif resolution == "candidate":
            item["annotation"] = {
                key: annotation[key]
                for key in ("origin", "resolution", "role", "panels", "encoding")
                if key in annotation
            }
            states["candidate"] += 1
        elif resolution == "rejected":
            states["rejected"] += 1
        else:
            states["invalid_resolution"] += 1
            warnings.append(
                {
                    "doc_id": loaded.spec["doc_id"],
                    "object_id": object_id,
                    "code": "annotation_invalid_resolution",
                    "message": f"unsupported annotation resolution: {resolution!r}",
                }
            )
    return {
        "states": dict(sorted(states.items())),
        "accepted_roles": dict(sorted(roles.items())),
    }


def rate_metric(
    numerator: int | float,
    denominator_words: int,
    *,
    unit: str,
    method: str = "deterministic",
) -> dict[str, Any]:
    if denominator_words == 0:
        return metric(
            None,
            status="denominator_zero",
            unit=unit,
            method=method,
            numerator=numerator,
            denominator=denominator_words,
        )
    return metric(
        numerator * 1000 / denominator_words,
        unit=unit,
        method=method,
        numerator=numerator,
        denominator=denominator_words,
    )


def count_phrases(text: str, phrases: Sequence[str]) -> int:
    lowered = text.lower()
    count = 0
    for phrase in sorted(phrases, key=len, reverse=True):
        if " " in phrase or phrase.endswith("reproduc"):
            count += len(re.findall(re.escape(phrase), lowered))
        else:
            count += len(re.findall(rf"\b{re.escape(phrase)}\b", lowered))
    return count


def contextual_link_count(paragraphs: Sequence[Block], context_pattern: str) -> int:
    matched_links: set[str] = set()
    for block in paragraphs:
        links = list(dict.fromkeys(block.external_links + surface_links(block.text)))
        if links and re.search(context_pattern, block.text, re.IGNORECASE):
            matched_links.update(link.strip() for link in links)
    return len(matched_links)


def document_entities(document: ParsedDocument, body_words: int) -> dict[str, Any]:
    section_values: dict[tuple[str, ...], dict[str, Any]] = {}
    paragraphs: list[dict[str, Any]] = []
    for block in document.blocks:
        if block.kind != "paragraph":
            continue
        key = tuple(block.section_path) or ("unsectioned",)
        section = section_values.setdefault(
            key,
            {
                "section_path": list(key),
                "word_count": 0,
                "paragraph_count": 0,
                "start_word_offset": block.body_word_offset,
                "end_word_offset": block.body_word_offset,
            },
        )
        count = word_count(block.text)
        section["word_count"] += count
        section["paragraph_count"] += 1
        section["end_word_offset"] = block.body_word_offset + count
        paragraphs.append(
            {
                "paragraph_id": f"p-{len(paragraphs) + 1}",
                "section_path": list(block.section_path),
                "word_count": count,
                "sentence_proxy_count": sentence_count(block.text),
                "start_word_offset": block.body_word_offset,
                "normalized_word_position": (
                    block.body_word_offset / body_words if body_words else 0.0
                ),
            }
        )
    sections: list[dict[str, Any]] = []
    for value in section_values.values():
        value["word_share"] = value["word_count"] / body_words if body_words else None
        value["start_normalized_position"] = (
            value["start_word_offset"] / body_words if body_words else 0.0
        )
        value["end_normalized_position"] = (
            value["end_word_offset"] / body_words if body_words else 0.0
        )
        canonical_path_labels = [
            label
            for heading in value["section_path"]
            if (label := canonical_section_label(heading)) is not None
        ]
        value["canonical_path_labels"] = list(dict.fromkeys(canonical_path_labels))
        value["canonical_label_proxy"] = (
            canonical_path_labels[-1] if canonical_path_labels else None
        )
        sections.append(value)
    return {"sections": sections, "paragraphs": paragraphs}


def compute_metrics(
    loaded: LoadedDocument,
    document: ParsedDocument,
    body_text: str,
    body_words: int,
    objects: list[dict[str, Any]],
    registry: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    paragraphs = [block for block in document.blocks if block.kind == "paragraph"]
    headings = [block for block in document.blocks if block.kind == "heading"]
    explicit_sections = [
        block for block in headings if not block.features.get("is_document_title")
    ]
    paragraph_counts = [word_count(block.text) for block in paragraphs]
    sentences = [
        sentence for block in paragraphs for sentence in split_sentences(block.text)
    ]
    sentence_words = [word_count(sentence) for sentence in sentences]
    object_counts = Counter(item["object_type"] for item in objects)
    caption_missing = sum(1 for item in objects if not item["caption"]["present"])
    all_callouts = [callout for item in objects for callout in item["callouts"]]
    explicit_citation_targets = [
        target for block in paragraphs for target in block.citation_targets
    ]
    citation_surfaces = CITATION_RE.findall(body_text)
    citation_targets = set(explicit_citation_targets)
    citation_clusters = sum(
        bool(re.search(r"[,;\-–]", surface)) for surface in citation_surfaces
    )
    citation_year_markers = len(re.findall(r"\b(?:19|20)\d{2}[a-z]?\b", body_text))
    tokens = tokenize(body_text)
    lower_tokens = [token.lower() for token in tokens]
    entities = document_entities(document, body_words)
    canonical_heading_sequence = [
        label
        for block in explicit_sections
        if (label := canonical_section_label(block.text)) is not None
    ]
    section_shares = [
        section["word_share"]
        for section in entities["sections"]
        if section["word_share"] is not None
    ]

    metrics: dict[str, dict[str, Any]] = {
        "text.body_words": metric(body_words, unit="word"),
        "text.body_characters": metric(len(body_text), unit="character"),
        "structure.paragraph_count": metric(len(paragraphs), unit="paragraph"),
        "structure.heading_count": metric(len(headings), unit="heading"),
        "structure.max_heading_depth": metric(
            max((block.level or 0 for block in headings), default=0), unit="level"
        ),
        "structure.section_count": metric(len(explicit_sections), unit="section"),
        "structure.section_word_share": metric(
            section_shares,
            unit="proportion",
            method="deterministic_per_section",
        ),
        "structure.median_paragraph_words": metric(
            statistics.median(paragraph_counts) if paragraph_counts else 0,
            unit="word_per_paragraph",
        ),
        "structure.raw_heading_sequence": metric(
            [block.text for block in headings], unit="heading_sequence"
        ),
        "structure.section_words": metric(
            [section["word_count"] for section in entities["sections"]], unit="word"
        ),
        "structure.section_start_position_norm": metric(
            [section["start_normalized_position"] for section in entities["sections"]],
            unit="ratio",
        ),
        "structure.section_end_position_norm": metric(
            [section["end_normalized_position"] for section in entities["sections"]],
            unit="ratio",
        ),
        "structure.paragraph_words": metric(paragraph_counts, unit="word"),
        "front.title_words": metric(
            word_count(document.title) if document.title else 0,
            status="ok" if document.title else "not_present",
            unit="word",
        ),
        "front.abstract_words": metric(
            word_count(document.abstract) if document.abstract else 0,
            status="ok" if document.abstract else "not_present",
            unit="word",
        ),
        "front.abstract_paragraph_count": metric(
            len(document.abstract_paragraphs) if document.abstract else 0,
            status="ok" if document.abstract else "not_present",
            unit="paragraph",
        ),
        "front.keyword_count": metric(
            len(document.keywords) if document.keywords else 0,
            status="ok" if document.keywords else "not_present",
            unit="keyword",
        ),
        "front.title_colon_present": metric(
            ":" in document.title if document.title else None,
            status="ok" if document.title else "not_present",
            unit="boolean",
            method="heuristic_title_surface_v1",
        ),
        "front.title_question_present": metric(
            bool(re.search(r"[?？]", document.title)) if document.title else None,
            status="ok" if document.title else "not_present",
            unit="boolean",
            method="heuristic_title_surface_v1",
        ),
        "front.title_numeric_present": metric(
            bool(re.search(r"\d", document.title)) if document.title else None,
            status="ok" if document.title else "not_present",
            unit="boolean",
            method="heuristic_title_surface_v1",
        ),
        "front.title_acronym_present": metric(
            bool(re.search(r"\b[A-Z]{2,}\b", document.title))
            if document.title
            else None,
            status="ok" if document.title else "not_present",
            unit="boolean",
            method="heuristic_title_surface_v1",
        ),
        "citation.explicit_event_count": metric(
            len(explicit_citation_targets), unit="citation_event"
        ),
        "citation.explicit_rate_per_kword": rate_metric(
            len(explicit_citation_targets),
            body_words,
            unit="citation_event_per_1000_words",
        ),
        "citation.unique_target_count": metric(
            len(citation_targets), unit="citation_target"
        ),
        "citation.cluster_count_proxy": metric(
            citation_clusters,
            unit="citation_cluster_proxy",
            method="heuristic_citation_surface_v1",
        ),
        "citation.reference_year_marker_count_proxy": metric(
            citation_year_markers,
            unit="year_marker_proxy",
            method="heuristic_citation_surface_v1",
        ),
        "reference.entry_count": metric(
            document.reference_entries, unit="reference_entry"
        ),
        "text.sentence_proxy_count": metric(
            sum(sentence_count(block.text) for block in paragraphs),
            unit="sentence_proxy",
            method="heuristic_sentence_proxy_v1",
        ),
        "text.median_sentence_words": metric(
            statistics.median(sentence_words) if sentence_words else 0,
            unit="word_per_sentence_proxy",
            method="heuristic_sentence_proxy_v1",
        ),
        "structure.canonical_section_count": metric(
            len(canonical_heading_sequence),
            unit="section",
            method="heuristic_label_map_v1",
        ),
        "caption.missing_count": metric(caption_missing, unit="caption"),
        "object.total_count": metric(len(objects), unit="object"),
        "callout.explicit_total_count": metric(len(all_callouts), unit="callout"),
        "sequence.object_type_order": metric(
            [item["object_type"] for item in objects], unit="object_type_sequence"
        ),
        "transition.object_type_pair_count": metric(
            max(0, len(objects) - 1), unit="adjacent_transition"
        ),
        "callout.orphan_object_count": metric(
            sum(1 for item in objects if not item["callouts"]), unit="object"
        ),
    }

    structured_supported = loaded.spec["format"] != "txt"
    if not structured_supported:
        for metric_id, unit in (
            ("structure.raw_heading_sequence", "heading_sequence"),
            ("object.total_count", "object"),
            ("caption.missing_count", "caption"),
            ("callout.explicit_total_count", "callout"),
            ("callout.orphan_object_count", "object"),
            ("sequence.object_type_order", "object_type_sequence"),
            ("transition.object_type_pair_count", "adjacent_transition"),
        ):
            metrics[metric_id] = metric(None, status="unsupported_format", unit=unit)
    for kind in OBJECT_TYPES:
        count_id = f"object.{kind}_count"
        if structured_supported:
            metrics[count_id] = metric(object_counts[kind], unit=kind)
        else:
            metrics[count_id] = metric(None, status="unsupported_format", unit=kind)
        rate_id = f"object.{kind}_rate_per_kword"
        if structured_supported:
            metrics[rate_id] = rate_metric(
                object_counts[kind], body_words, unit=f"{kind}_per_1000_words"
            )
        else:
            metrics[rate_id] = metric(
                None,
                status="unsupported_format",
                unit=f"{kind}_per_1000_words",
                numerator=None,
                denominator=body_words,
            )
        callout_id = f"callout.{kind}_count"
        if structured_supported:
            metrics[callout_id] = metric(
                sum(
                    len(item["callouts"])
                    for item in objects
                    if item["object_type"] == kind
                ),
                unit="callout",
            )
        else:
            metrics[callout_id] = metric(
                None, status="unsupported_format", unit="callout"
            )

    # Per-object structural features remain auditable document-level vectors/sums.
    tables = [item for item in objects if item["object_type"] == "table"]
    equations = [item for item in objects if item["object_type"] == "equation"]
    algorithms = [item for item in objects if item["object_type"] == "algorithm"]
    figures = [item for item in objects if item["object_type"] == "figure"]
    captioned_figures = [item for item in figures if item["caption"]["present"]]
    captioned_tables = [item for item in tables if item["caption"]["present"]]
    figure_callouts = [callout for item in figures for callout in item["callouts"]]
    table_callouts = [callout for item in tables for callout in item["callouts"]]
    equation_callouts = [callout for item in equations for callout in item["callouts"]]
    algorithm_callouts = [
        callout for item in algorithms for callout in item["callouts"]
    ]
    canonical_sequence = canonical_heading_sequence
    feature_metrics = {
        "table.rows": [item["features"].get("row_count", 0) for item in tables],
        "table.columns": [item["features"].get("column_count", 0) for item in tables],
        "table.numeric_cell_share_proxy": [
            (
                item["features"].get("numeric_cell_count", 0)
                / item["features"].get("data_nonempty_cell_count", 0)
            )
            for item in tables
            if item["features"].get("data_nonempty_cell_count", 0) > 0
        ],
        "equation.numbered_count": sum(
            bool(item["features"].get("numbered")) for item in equations
        ),
        "equation.referenced_count": sum(bool(item["callouts"]) for item in equations),
        "equation.display_line_count": [
            item["features"].get("display_line_count", 1) for item in equations
        ],
        "algorithm.line_count": [
            item["features"].get("line_count", 0) for item in algorithms
        ],
        "algorithm.marker_count": sum(
            sum(
                bool(item["features"].get(key))
                for key in (
                    "has_input",
                    "has_output",
                    "has_initialize",
                    "has_loop",
                    "has_branch",
                    "has_return",
                )
            )
            for item in algorithms
        ),
        "algorithm.input_marker_count": sum(
            bool(item["features"].get("has_input")) for item in algorithms
        ),
        "algorithm.output_marker_count": sum(
            bool(item["features"].get("has_output")) for item in algorithms
        ),
        "algorithm.initialization_marker_count": sum(
            bool(item["features"].get("has_initialize")) for item in algorithms
        ),
        "algorithm.loop_marker_count": sum(
            bool(item["features"].get("has_loop")) for item in algorithms
        ),
        "algorithm.branch_marker_count": sum(
            bool(item["features"].get("has_branch")) for item in algorithms
        ),
        "algorithm.return_marker_count": sum(
            bool(item["features"].get("has_return")) for item in algorithms
        ),
        "object.figure_position_norm": [
            item["position"]["normalized_word_position"] for item in figures
        ],
        "object.table_position_norm": [
            item["position"]["normalized_word_position"] for item in tables
        ],
        "object.equation_position_norm": [
            item["position"]["normalized_word_position"] for item in equations
        ],
        "object.algorithm_position_norm": [
            item["position"]["normalized_word_position"] for item in algorithms
        ],
        "caption.figure_words": [
            item["caption"]["word_count"] for item in captioned_figures
        ],
        "caption.table_words": [
            item["caption"]["word_count"] for item in captioned_tables
        ],
        "caption.figure_sentence_proxy_count": [
            item["caption"]["sentence_count"] for item in captioned_figures
        ],
        "caption.table_sentence_proxy_count": [
            item["caption"]["sentence_count"] for item in captioned_tables
        ],
        "caption.figure_panel_label_count_proxy": sum(
            item["caption"]["panel_label_proxy"] for item in figures
        ),
        "caption.figure_uncertainty_marker_count": sum(
            item["caption"]["uncertainty_marker_proxy"] for item in figures
        ),
        "caption.table_uncertainty_marker_count": sum(
            item["caption"]["uncertainty_marker_proxy"] for item in tables
        ),
        "lead_lag.figure_callout_words": [
            item["lead_lag_words"] for item in figure_callouts
        ],
        "lead_lag.table_callout_words": [
            item["lead_lag_words"] for item in table_callouts
        ],
        "lead_lag.equation_callout_words": [
            item["lead_lag_words"] for item in equation_callouts
        ],
        "lead_lag.algorithm_callout_words": [
            item["lead_lag_words"] for item in algorithm_callouts
        ],
        "sequence.section_order_proxy": canonical_sequence,
        "transition.section_pair_count_proxy": max(0, len(canonical_sequence) - 1),
    }
    for metric_id, value in feature_metrics.items():
        status = (
            "unsupported_format"
            if not structured_supported
            else "not_present"
            if isinstance(value, list) and not value
            else "ok"
        )
        metrics[metric_id] = metric(
            value if structured_supported else None,
            status=status,
            unit="vector" if isinstance(value, list) else "count",
            method=(
                "heuristic_algorithm_surface_v1"
                if metric_id == "algorithm.marker_count"
                else "heuristic_caption_surface_v1"
                if metric_id
                in {
                    "caption.figure_panel_label_count_proxy",
                    "caption.figure_uncertainty_marker_count",
                    "caption.table_uncertainty_marker_count",
                }
                else "heuristic_surface_proxy"
                if "proxy" in metric_id
                else "deterministic"
            ),
        )
    empty_data_tables = sum(
        item["features"].get("data_nonempty_cell_count", 0) == 0 for item in tables
    )
    if tables and empty_data_tables == len(tables):
        metrics["table.numeric_cell_share_proxy"] = metric(
            None,
            status="denominator_zero",
            unit="ratio",
            method="heuristic_numeric_cell_surface_v1",
            numerator=sum(
                item["features"].get("numeric_cell_count", 0) for item in tables
            ),
            denominator=0,
        )
    elif empty_data_tables:
        metrics["table.numeric_cell_share_proxy"]["excluded_entity_n"] = (
            empty_data_tables
        )
    if not algorithms:
        metrics["algorithm.marker_count"] = metric(
            None,
            status="not_present",
            unit="algorithm_feature_presence_proxy",
            method="heuristic_algorithm_surface_v1",
        )
    if not figures:
        for metric_id in (
            "caption.figure_panel_label_count_proxy",
            "caption.figure_uncertainty_marker_count",
        ):
            metrics[metric_id] = metric(
                None,
                status="not_present",
                unit="caption_event_proxy",
                method="heuristic_caption_surface_v1",
            )
    if not tables:
        metrics["caption.table_uncertainty_marker_count"] = metric(
            None,
            status="not_present",
            unit="caption_event_proxy",
            method="heuristic_caption_surface_v1",
        )
    if tables and any(
        item["features"].get("has_rowspan") or item["features"].get("has_colspan")
        for item in tables
    ):
        for metric_id in (
            "table.rows",
            "table.columns",
            "table.numeric_cell_share_proxy",
        ):
            metrics[metric_id] = metric(
                None,
                status="ambiguous",
                unit="table_shape",
                method="span_expansion_not_supported",
            )

    language = loaded.spec.get("language", "und").lower()
    english = language == "en" or language.startswith("en-")
    if not english:
        for metric_id in (
            "structure.canonical_section_count",
            "sequence.section_order_proxy",
        ):
            metrics[metric_id] = metric(
                None,
                status="unsupported_language",
                unit="section"
                if metric_id.endswith("count")
                else "canonical_section_sequence",
                method="heuristic_english_section_map_v1",
            )
    for metric_id, phrases in LEXICAL_PATTERNS.items():
        if not english:
            metrics[metric_id] = metric(
                None,
                status="unsupported_language",
                unit="marker_per_1000_words",
                method="heuristic_english_lexicon_v1",
            )
            continue
        count = count_phrases(body_text, phrases)
        metrics[metric_id] = rate_metric(
            count,
            body_words,
            unit="marker_per_1000_words",
            method="heuristic_english_lexicon_v1",
        )
    if english:
        numeric_count = sum(bool(re.search(r"\d", token)) for token in tokens)
        acronym_tokens = [
            token for token in tokens if re.fullmatch(r"[A-Z]{2,}(?:s)?", token)
        ]
        acronym_count = len(acronym_tokens)
        acronym_definitions = re.findall(
            r"\b[A-Za-z][A-Za-z\- ]{2,}\s+\(([A-Z]{2,})\)", body_text
        )
        metrics["lexical.numeric_token_rate_per_kword"] = rate_metric(
            numeric_count,
            body_words,
            unit="token_per_1000_words",
            method="heuristic_token_surface_v1",
        )
        metrics["lexical.acronym_token_rate_per_kword"] = rate_metric(
            acronym_count,
            body_words,
            unit="token_per_1000_words",
            method="heuristic_token_surface_v1",
        )
        if len(lower_tokens) < 50:
            metrics["lexical.mattr50"] = metric(
                None,
                status="not_applicable",
                unit="proportion",
                method="heuristic_mattr50_v1",
                denominator=len(lower_tokens),
            )
        else:
            metrics["lexical.mattr50"] = metric(
                mattr50(lower_tokens),
                unit="proportion",
                method="heuristic_mattr50_v1",
                denominator=len(lower_tokens),
            )
        metrics["lexical.acronym_definition_count_proxy"] = metric(
            len(acronym_definitions),
            unit="acronym_definition_proxy",
            method="heuristic_acronym_surface_v1",
        )
        defined = set(acronym_definitions)
        metrics["lexical.undefined_acronym_use_count_proxy"] = metric(
            sum(token.rstrip("s") not in defined for token in acronym_tokens),
            unit="undefined_acronym_proxy",
            method="heuristic_acronym_surface_v1",
        )
        marker_patterns = {
            "marker.stats_ci_count": r"\b(?:\d+(?:\.\d+)?%\s*)?(?:CI|confidence interval)\b",
            "marker.stats_pvalue_count": r"\bp\s*[<=>]\s*0?\.\d+",
            "marker.stats_effect_size_count": r"\b(?:Cohen'?s? d|odds ratio|risk ratio|effect size|Cliff'?s delta)\b",
            "marker.stats_uncertainty_count": r"\b(?:uncertainty|standard error|error bar|confidence band)\b",
        }
        for metric_id, pattern in marker_patterns.items():
            metrics[metric_id] = metric(
                len(re.findall(pattern, body_text, re.IGNORECASE)),
                unit="marker",
                method="heuristic_surface_regex_v1",
            )
        metrics["marker.repro_code_link_count"] = metric(
            contextual_link_count(
                paragraphs,
                r"\b(?:code|source\s+code|repository|implementation|github|gitlab)\b",
            ),
            unit="link",
            method="heuristic_url_context_window_v1",
        )
        metrics["marker.repro_data_link_count"] = metric(
            contextual_link_count(
                paragraphs,
                r"\b(?:data|dataset|repository|archive|zenodo|figshare|dryad)\b",
            ),
            unit="link",
            method="heuristic_url_context_window_v1",
        )
    else:
        for metric_id in (
            "lexical.numeric_token_rate_per_kword",
            "lexical.acronym_token_rate_per_kword",
            "lexical.mattr50",
            "lexical.acronym_definition_count_proxy",
            "lexical.undefined_acronym_use_count_proxy",
            "marker.stats_ci_count",
            "marker.stats_pvalue_count",
            "marker.stats_effect_size_count",
            "marker.stats_uncertainty_count",
            "marker.repro_code_link_count",
            "marker.repro_data_link_count",
        ):
            metrics[metric_id] = metric(
                None,
                status="unsupported_language",
                unit="marker",
                method="heuristic_english_surface_v1",
            )

    # Every registered metric is explicit; unsupported/not-implemented is never zero.
    registry_by_id = {item["metric_id"]: item for item in registry.get("metrics", [])}
    for metric_id, definition in registry_by_id.items():
        supported = loaded.spec["format"] in definition.get("supported_formats", [])
        if not supported:
            metrics[metric_id] = metric(
                None,
                status="unsupported_format",
                unit=str(definition.get("unit", "unknown")),
                method="adapter_capability_gate",
            )
        elif metric_id in metrics:
            entry = metrics[metric_id]
            entry["unit"] = str(definition.get("unit", "unknown"))
            value = entry.get("value")
            if isinstance(value, list) and definition.get("value_type") != "sequence":
                entity_values = [
                    item
                    for item in value
                    if isinstance(item, (int, float))
                    and not isinstance(item, bool)
                    and math.isfinite(float(item))
                ]
                entry["entity_values"] = value
                entry["observation_n"] = len(entity_values)
                entry["reduction"] = "within_paper_median"
                if entity_values:
                    entry["value"] = float(statistics.median(entity_values))
                else:
                    entry["value"] = None
                    if entry.get("status") == "ok":
                        entry["status"] = "not_present"
        else:
            raise ContractError(
                f"registry/analyzer incompatibility: implemented metric missing: {metric_id}"
            )
    return dict(sorted(metrics.items())), entities


def quantile(values: Sequence[float], probability: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("quantile requires values")
    if len(ordered) == 1:
        return float(ordered[0])
    index = (len(ordered) - 1) * probability
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return float(ordered[lower])
    fraction = index - lower
    return float(ordered[lower] * (1 - fraction) + ordered[upper] * fraction)


def paper_numeric_value(entry: dict[str, Any]) -> float | None:
    if entry.get("status") not in {"ok", "not_present"}:
        return None
    value = entry.get("value")
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return float(value)
    return None


def numeric_summary(
    points: list[tuple[str, float]], entries: list[dict[str, Any]], total_n: int
) -> dict[str, Any]:
    values = [value for _, value in points]
    median = float(statistics.median(values))
    p25 = quantile(values, 0.25)
    p75 = quantile(values, 0.75)
    deviations = [abs(value - median) for value in values]
    numerators = [entry.get("numerator") for entry in entries]
    denominators = [entry.get("denominator") for entry in entries]
    numeric_numerators = [
        float(value)
        for value in numerators
        if isinstance(value, (int, float)) and not isinstance(value, bool)
    ]
    numeric_denominators = [
        float(value)
        for value in denominators
        if isinstance(value, (int, float)) and not isinstance(value, bool)
    ]
    pooled_rate: float | None = None
    if len(numeric_numerators) == len(entries) and len(numeric_denominators) == len(
        entries
    ):
        denominator_sum = sum(numeric_denominators)
        if denominator_sum:
            pooled_rate = sum(numeric_numerators) / denominator_sum
            # per-kword metric entries use raw word denominators.
            if any("1000" in str(entry.get("unit", "")) for entry in entries):
                pooled_rate *= 1000
    bootstrap_interval: list[float] | None = None
    if len(values) >= 5:
        seed_material = canonical_json(sorted(values), pretty=False).rstrip(b"\n")
        seed = int.from_bytes(hashlib.sha256(seed_material).digest()[:8], "big")
        generator = random.Random(seed)
        resampled_medians = sorted(
            float(
                statistics.median(
                    values[generator.randrange(len(values))] for _ in range(len(values))
                )
            )
            for _ in range(1000)
        )
        bootstrap_interval = [
            quantile(resampled_medians, 0.025),
            quantile(resampled_medians, 0.975),
        ]
    return {
        "valid_n": len(values),
        "eligible_n": total_n,
        "raw_points": [{"doc_id": doc_id, "value": value} for doc_id, value in points],
        "median": median,
        "iqr": p75 - p25,
        "mad": float(statistics.median(deviations)),
        "p10": quantile(values, 0.10),
        "p25": p25,
        "p50": median,
        "p75": p75,
        "p90": quantile(values, 0.90),
        "min": min(values),
        "max": max(values),
        "mean": float(statistics.fmean(values)),
        "std": float(statistics.stdev(values)) if len(values) > 1 else 0.0,
        "bootstrap_95_ci": bootstrap_interval,
        "bootstrap_statistic": "median",
        "bootstrap_resamples": 1000 if bootstrap_interval is not None else 0,
        "zero_prevalence": sum(value == 0 for value in values) / len(values),
        "median_per_paper_rate": median
        if any("1000" in str(entry.get("unit", "")) for entry in entries)
        else None,
        "pooled_rate": pooled_rate,
    }


def sample_size_label(n: int) -> str:
    if n < 5:
        return "case_set"
    if n < 20:
        return "exploratory"
    return "distributional"


def wilson_interval(
    successes: int, total: int, z: float = 1.959963984540054
) -> list[float] | None:
    if total <= 0:
        return None
    proportion = successes / total
    denominator = 1 + z * z / total
    center = (proportion + z * z / (2 * total)) / denominator
    half_width = (
        z
        * math.sqrt(proportion * (1 - proportion) / total + z * z / (4 * total * total))
        / denominator
    )
    return [max(0.0, center - half_width), min(1.0, center + half_width)]


def group_sequences(
    rows: list[dict[str, Any]], objects: list[dict[str, Any]]
) -> dict[str, Any]:
    object_sequence_rows = [
        row
        for row in rows
        if row.get("status") == "ok"
        and row.get("metrics", {}).get("sequence.object_type_order", {}).get("status")
        == "ok"
    ]
    doc_ids = {row["doc_id"] for row in object_sequence_rows}
    by_document: list[dict[str, Any]] = []
    transition_counter: Counter[tuple[str, str]] = Counter()
    lead_lag: list[dict[str, Any]] = []
    for doc_id in sorted(doc_ids):
        doc_objects = sorted(
            (item for item in objects if item["doc_id"] == doc_id),
            key=lambda item: (
                item["position"]["source_block_index"],
                item["object_id"],
            ),
        )
        sequence = [item["object_type"] for item in doc_objects]
        by_document.append({"doc_id": doc_id, "sequence": sequence})
        transition_counter.update(zip(sequence, sequence[1:]))
        for item in doc_objects:
            for callout in item["callouts"]:
                lead_lag.append(
                    {
                        "doc_id": doc_id,
                        "object_id": item["object_id"],
                        "object_type": item["object_type"],
                        "lead_lag_words": callout["lead_lag_words"],
                    }
                )
    sequence_counter = Counter(tuple(item["sequence"]) for item in by_document)
    expected = sum(max(0, len(item["sequence"]) - 1) for item in by_document)
    observed = sum(transition_counter.values())
    section_by_document: list[dict[str, Any]] = []
    section_transition_counter: Counter[tuple[str, str]] = Counter()
    section_sequence_rows = [
        row
        for row in rows
        if row.get("status") == "ok"
        and row.get("metrics", {}).get("sequence.section_order_proxy", {}).get("status")
        == "ok"
    ]
    for row in sorted(section_sequence_rows, key=lambda item: item["doc_id"]):
        value = row["metrics"]["sequence.section_order_proxy"].get("value", [])
        sequence = (
            [item for item in value if isinstance(item, str)]
            if isinstance(value, list)
            else []
        )
        section_by_document.append({"doc_id": row["doc_id"], "sequence": sequence})
        section_transition_counter.update(zip(sequence, sequence[1:]))
    section_sequence_counter = Counter(
        tuple(item["sequence"]) for item in section_by_document
    )
    section_expected = sum(
        max(0, len(item["sequence"]) - 1) for item in section_by_document
    )
    lead_lag_by_document: dict[str, list[int]] = defaultdict(list)
    for observation in lead_lag:
        lead_lag_by_document[observation["doc_id"]].append(
            observation["lead_lag_words"]
        )
    per_paper_lead_lag = [
        float(statistics.median(values))
        for _, values in sorted(lead_lag_by_document.items())
        if values
    ]
    return {
        "document_sequences": by_document,
        "top_sequences": [
            {"sequence": list(sequence), "paper_count": count}
            for sequence, count in sorted(
                sequence_counter.items(), key=lambda item: (-item[1], item[0])
            )
        ],
        "transitions": {
            "expected_total": expected,
            "observed_total": observed,
            "invariant_holds": expected == observed,
            "edges": [
                {"from": source, "to": target, "raw_count": count}
                for (source, target), count in sorted(transition_counter.items())
            ],
        },
        "section_sequence": {
            "document_sequences": section_by_document,
            "top_sequences": [
                {"sequence": list(sequence), "paper_count": count}
                for sequence, count in sorted(
                    section_sequence_counter.items(),
                    key=lambda item: (-item[1], item[0]),
                )
            ],
            "transitions": {
                "expected_total": section_expected,
                "observed_total": sum(section_transition_counter.values()),
                "invariant_holds": section_expected
                == sum(section_transition_counter.values()),
                "edges": [
                    {"from": source, "to": target, "raw_count": count}
                    for (source, target), count in sorted(
                        section_transition_counter.items()
                    )
                ],
            },
        },
        "lead_lag": {
            "observations": lead_lag,
            "valid_n": len(per_paper_lead_lag),
            "observation_n": len(lead_lag),
            "median": (
                float(statistics.median(per_paper_lead_lag))
                if per_paper_lead_lag
                else None
            ),
            "orphan_object_count": sum(
                1
                for item in objects
                if item["doc_id"] in doc_ids and not item["callouts"]
            ),
        },
    }


def summarize_section_labels(
    rows: list[dict[str, Any]], *, canonical: bool
) -> list[dict[str, Any]]:
    eligible_rows = [
        row
        for row in rows
        if row.get("status") == "ok"
        and row.get("source", {}).get("format") != "txt"
        and (
            not canonical
            or str(row.get("source", {}).get("language", "und")).lower()
            in {"en", "en-us", "en-gb"}
            or str(row.get("source", {}).get("language", "und"))
            .lower()
            .startswith("en-")
        )
    ]
    per_label: dict[str, dict[str, dict[str, float]]] = defaultdict(dict)
    for row in eligible_rows:
        per_document: dict[str, dict[str, float]] = {}
        for section in row.get("entities", {}).get("sections", []):
            if not isinstance(section, dict):
                continue
            labels = (
                section.get("canonical_path_labels", [])
                if canonical
                else [" > ".join(section.get("section_path") or ["unsectioned"])]
            )
            for label in labels:
                if not isinstance(label, str) or not label.strip():
                    continue
                accumulator = per_document.setdefault(
                    label,
                    {
                        "word_count": 0.0,
                        "word_share": 0.0,
                        "paragraph_count": 0.0,
                        "start_position_norm": 1.0,
                        "end_position_norm": 0.0,
                    },
                )
                accumulator["word_count"] += float(section.get("word_count", 0))
                accumulator["word_share"] += float(section.get("word_share", 0))
                accumulator["paragraph_count"] += float(
                    section.get("paragraph_count", 0)
                )
                accumulator["start_position_norm"] = min(
                    accumulator["start_position_norm"],
                    float(section.get("start_normalized_position", 0)),
                )
                accumulator["end_position_norm"] = max(
                    accumulator["end_position_norm"],
                    float(section.get("end_normalized_position", 0)),
                )
        for label, values in per_document.items():
            per_label[label][row["doc_id"]] = values

    output: list[dict[str, Any]] = []
    for label, documents in sorted(per_label.items()):
        metrics: dict[str, Any] = {}
        for field_name, unit in (
            ("word_count", "word"),
            ("word_share", "proportion"),
            ("paragraph_count", "paragraph"),
            ("start_position_norm", "ratio"),
            ("end_position_norm", "ratio"),
        ):
            points = [
                (doc_id, float(values[field_name]))
                for doc_id, values in sorted(documents.items())
            ]
            entries = [{"unit": unit} for _ in points]
            item = numeric_summary(points, entries, len(eligible_rows))
            item["missingness"] = len(eligible_rows) - len(points)
            metrics[field_name] = item
        output.append(
            {
                "label": label,
                "label_kind": "canonical_proxy" if canonical else "raw_heading",
                "eligible_n": len(eligible_rows),
                "valid_n": len(documents),
                "metrics": metrics,
            }
        )
    return output


def summarize_group(
    group_id: str,
    rows: list[dict[str, Any]],
    objects: list[dict[str, Any]],
    filters: dict[str, Any],
) -> dict[str, Any]:
    ok_rows = [row for row in rows if row.get("status") == "ok"]
    metric_ids = sorted(
        {metric_id for row in rows for metric_id in row.get("metrics", {})}
    )
    metric_summaries: dict[str, Any] = {}
    for metric_id in metric_ids:
        statuses: Counter[str] = Counter()
        points: list[tuple[str, float]] = []
        valid_entries: list[dict[str, Any]] = []
        boolean_values: list[bool] = []
        for row in rows:
            entry = row.get("metrics", {}).get(metric_id)
            if not isinstance(entry, dict):
                statuses["source_missing"] += 1
                continue
            statuses[str(entry.get("status", "source_missing"))] += 1
            value = paper_numeric_value(entry)
            if value is not None:
                points.append((row["doc_id"], value))
                valid_entries.append(entry)
                if isinstance(entry.get("value"), bool):
                    boolean_values.append(entry["value"])
        missing_count = len(rows) - len(points)
        item: dict[str, Any] = {
            "valid_n": len(points),
            "eligible_n": len(rows),
            "missingness": missing_count,
            "missingness_by_status": dict(sorted(statuses.items())),
            "sample_size_label": sample_size_label(len(points)),
            "sample_size_label_is_gate": False,
        }
        if points:
            item.update(numeric_summary(points, valid_entries, len(rows)))
        if boolean_values and len(boolean_values) == len(points):
            positive = sum(boolean_values)
            item["category"] = {
                "positive_n": positive,
                "valid_n": len(boolean_values),
                "proportion": positive / len(boolean_values),
                "wilson_95": wilson_interval(positive, len(boolean_values)),
            }
        metric_summaries[metric_id] = item
    sequence_summary = group_sequences(ok_rows, objects)
    partitions = sorted({row["partition"] for row in rows})
    article_types = sorted(
        {str(row.get("source", {}).get("article_type", "unknown")) for row in rows}
    )
    venues = sorted(
        {str(row.get("source", {}).get("venue", "unknown")) for row in ok_rows}
    )
    languages = sorted(
        {str(row.get("source", {}).get("language", "und")) for row in ok_rows}
    )
    language_profiles = sorted({language_profile(value) for value in languages})
    source_formats = sorted(
        {str(row.get("source", {}).get("format", "unknown")) for row in ok_rows}
    )
    years = sorted(
        {
            int(row["source"]["year"])
            for row in ok_rows
            if isinstance(row.get("source", {}).get("year"), int)
            and not isinstance(row["source"]["year"], bool)
        }
    )
    inclusion_exception_count = sum(
        bool(row.get("source", {}).get("inclusion_exception")) for row in ok_rows
    )
    comparability_reasons: list[str] = []
    if len(partitions) > 1:
        comparability_reasons.append("mixed_partitions")
    if len(article_types) > 1:
        comparability_reasons.append("mixed_article_types")
    if len(venues) > 1:
        comparability_reasons.append("mixed_venues")
    if len(language_profiles) > 1:
        comparability_reasons.append("mixed_languages")
    if inclusion_exception_count:
        comparability_reasons.append("owner_inclusion_exception_present")
    comparable = not comparability_reasons
    return {
        "group_id": group_id,
        "filters": filters,
        "document_count": len(rows),
        "parsed_document_count": len(ok_rows),
        "sample_size_label": sample_size_label(len(ok_rows)),
        "sample_size_label_is_gate": False,
        "strata": {
            "partitions": partitions,
            "article_types": article_types,
            "venues": venues,
            "languages": languages,
            "language_profiles": language_profiles,
            "source_formats": source_formats,
            "year_min": min(years) if years else None,
            "year_max": max(years) if years else None,
            "inclusion_exception_count": inclusion_exception_count,
            "comparable": comparable,
            "comparability_reasons": comparability_reasons,
            "mixed": not comparable,
        },
        "metrics": metric_summaries,
        "section_label_metrics": {
            "canonical": summarize_section_labels(rows, canonical=True),
            "raw": summarize_section_labels(rows, canonical=False),
        },
        "object_sequence": sequence_summary,
    }


def cliffs_delta(left: Sequence[float], right: Sequence[float]) -> float:
    greater = sum(a > b for a in left for b in right)
    lesser = sum(a < b for a in left for b in right)
    return (greater - lesser) / (len(left) * len(right))


def delta_magnitude(value: float) -> str:
    absolute = abs(value)
    if absolute < 0.147:
        return "negligible"
    if absolute < 0.33:
        return "small"
    if absolute < 0.474:
        return "medium"
    return "large"


def comparisons(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_partition_type: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if (
            row.get("status") == "ok"
            and not row.get("source", {}).get("supplement_of")
            and not row.get("source", {}).get("inclusion_exception")
        ):
            article_type = str(row.get("source", {}).get("article_type", "unknown"))
            by_partition_type[(row["partition"], article_type)].append(row)
    output: list[dict[str, Any]] = []
    for other_partition in ("venue_control", "topic_control"):
        article_types = sorted(
            article_type
            for partition, article_type in by_partition_type
            if partition == "primary_match"
            and (other_partition, article_type) in by_partition_type
        )
        for article_type in article_types:
            primary = by_partition_type[("primary_match", article_type)]
            other = by_partition_type[(other_partition, article_type)]
            primary_languages = sorted(
                {
                    language_profile(row.get("source", {}).get("language"))
                    for row in primary
                }
            )
            other_languages = sorted(
                {
                    language_profile(row.get("source", {}).get("language"))
                    for row in other
                }
            )
            language_comparable = (
                len(primary_languages) == 1
                and len(other_languages) == 1
                and primary_languages == other_languages
            )
            metric_ids = sorted(
                {
                    metric_id
                    for row in primary + other
                    for metric_id in row.get("metrics", {})
                }
            )
            for metric_id in metric_ids:
                left = [
                    value
                    for row in primary
                    if (value := paper_numeric_value(row["metrics"].get(metric_id, {})))
                    is not None
                ]
                right = [
                    value
                    for row in other
                    if (value := paper_numeric_value(row["metrics"].get(metric_id, {})))
                    is not None
                ]
                if not left and not right:
                    continue
                base = {
                    "comparison_id": f"{metric_id}:primary_match:{other_partition}:{article_type}",
                    "metric_id": metric_id,
                    "partition_a": "primary_match",
                    "partition_b": other_partition,
                    "article_type": article_type,
                    "language_profiles_a": primary_languages,
                    "language_profiles_b": other_languages,
                    "n_a": len(left),
                    "n_b": len(right),
                    "median_a": float(statistics.median(left)) if left else None,
                    "median_b": float(statistics.median(right)) if right else None,
                }
                if not language_comparable:
                    base.update(
                        {
                            "status": "incomparable_language_strata",
                            "median_difference": None,
                            "hodges_lehmann_shift": None,
                            "cliffs_delta": None,
                            "magnitude": None,
                        }
                    )
                elif len(left) < 5 or len(right) < 5:
                    base.update(
                        {
                            "status": "side_by_side_case_set",
                            "median_difference": None,
                            "hodges_lehmann_shift": None,
                            "cliffs_delta": None,
                            "magnitude": None,
                        }
                    )
                else:
                    delta = cliffs_delta(left, right)
                    pair_differences = [a - b for a in left for b in right]
                    base.update(
                        {
                            "status": "descriptive_effect_size",
                            "median_difference": float(statistics.median(left))
                            - float(statistics.median(right)),
                            "hodges_lehmann_shift": float(
                                statistics.median(pair_differences)
                            ),
                            "cliffs_delta": delta,
                            "magnitude": delta_magnitude(delta),
                        }
                    )
                output.append(base)
    return output


def build_summary(
    corpus_id: str,
    requested_analysis_mode: str,
    analysis_mode_source: str,
    design_question: str,
    design_metric_ids: list[str],
    rows: list[dict[str, Any]],
    objects: list[dict[str, Any]],
    annotation_states: list[dict[str, Any]],
) -> dict[str, Any]:
    main_rows = [row for row in rows if not row.get("source", {}).get("supplement_of")]
    supplement_rows = [
        row for row in rows if row.get("source", {}).get("supplement_of")
    ]
    overall = summarize_group("overall", main_rows, objects, {"supplement": False})
    supplement = summarize_group(
        "supplement", supplement_rows, objects, {"supplement": True}
    )
    by_partition: list[dict[str, Any]] = []
    for partition in sorted({row["partition"] for row in main_rows}):
        selected = [row for row in main_rows if row["partition"] == partition]
        by_partition.append(
            summarize_group(
                f"partition:{partition}", selected, objects, {"partition": partition}
            )
        )
    by_article_type: list[dict[str, Any]] = []
    for article_type in sorted(
        {str(row.get("source", {}).get("article_type", "unknown")) for row in main_rows}
    ):
        selected = [
            row
            for row in main_rows
            if str(row.get("source", {}).get("article_type", "unknown")) == article_type
        ]
        by_article_type.append(
            summarize_group(
                f"article_type:{article_type}",
                selected,
                objects,
                {"article_type": article_type},
            )
        )
    by_partition_article_type: list[dict[str, Any]] = []
    keys = sorted(
        {
            (
                row["partition"],
                str(row.get("source", {}).get("article_type", "unknown")),
            )
            for row in main_rows
        }
    )
    for partition, article_type in keys:
        selected = [
            row
            for row in main_rows
            if row["partition"] == partition
            and str(row.get("source", {}).get("article_type", "unknown"))
            == article_type
        ]
        by_partition_article_type.append(
            summarize_group(
                f"partition:{partition}|article_type:{article_type}",
                selected,
                objects,
                {"partition": partition, "article_type": article_type},
            )
        )
    sequence = overall["object_sequence"]
    primary_group = next(
        (
            group
            for group in by_partition
            if group.get("filters", {}).get("partition") == "primary_match"
        ),
        None,
    )
    design_group = primary_group or overall
    comparable_stratum = not design_group.get("strata", {}).get("mixed", False)
    distribution_ready_metric_count = sum(
        1
        for metric_id, item in design_group.get("metrics", {}).items()
        if metric_id in design_metric_ids
        if isinstance(item, dict)
        and item.get("valid_n", 0) >= 5
        and item.get("valid_n", 0) / max(1, item.get("eligible_n", 0)) >= 0.8
        and item.get("bootstrap_95_ci") is not None
        and comparable_stratum
    )
    design_metric_readiness: dict[str, Any] = {}
    for metric_id in design_metric_ids:
        item = design_group.get("metrics", {}).get(metric_id, {})
        valid_n = int(item.get("valid_n", 0)) if isinstance(item, dict) else 0
        status_ok_n = (
            int(item.get("missingness_by_status", {}).get("ok", 0))
            if isinstance(item, dict)
            else 0
        )
        observed_n = max(valid_n, status_ok_n)
        eligible_n = (
            int(item.get("eligible_n", design_group["document_count"]))
            if isinstance(item, dict)
            else design_group["document_count"]
        )
        coverage = valid_n / max(1, eligible_n)
        design_metric_readiness[metric_id] = {
            "valid_n": valid_n,
            "observed_n": observed_n,
            "eligible_n": eligible_n,
            "valid_coverage": coverage,
            "sample_size_label": sample_size_label(valid_n),
            "bootstrap_95_ci": item.get("bootstrap_95_ci")
            if isinstance(item, dict)
            else None,
            "missingness_by_status": item.get("missingness_by_status", {})
            if isinstance(item, dict)
            else {},
            "distribution_ready": bool(
                valid_n >= 5
                and coverage >= 0.8
                and isinstance(item, dict)
                and item.get("bootstrap_95_ci") is not None
                and comparable_stratum
            ),
        }
    design_parsed_n = int(design_group.get("parsed_document_count", 0))
    observed_design_metric_count = sum(
        item["observed_n"] > 0 for item in design_metric_readiness.values()
    )
    all_design_metrics_distribution_ready = bool(design_metric_ids) and all(
        item["distribution_ready"] for item in design_metric_readiness.values()
    )
    if requested_analysis_mode == "distributional":
        effective_analysis_mode = (
            "distributional"
            if all_design_metrics_distribution_ready
            else "exploratory"
            if design_parsed_n >= 5 and observed_design_metric_count
            else "case_set"
        )
    elif requested_analysis_mode == "exploratory":
        effective_analysis_mode = (
            "exploratory"
            if design_parsed_n >= 5 and observed_design_metric_count
            else "case_set"
        )
    else:
        effective_analysis_mode = "case_set"
    mode_downgrade_reason = None
    if effective_analysis_mode != requested_analysis_mode:
        mode_downgrade_reason = (
            "requested mode was downgraded because the selected main-paper design "
            "stratum lacks the paper-level n, coverage, bootstrap uncertainty, or "
            "stratum comparability required for that mode"
        )
    annotation_state_counter: Counter[str] = Counter()
    role_counter: Counter[str] = Counter()
    for item in annotation_states:
        annotation_state_counter.update(item.get("states", {}))
        role_counter.update(item.get("accepted_roles", {}))
    return {
        "schema": SUMMARY_SCHEMA,
        "analyzer_version": ANALYZER_VERSION,
        "corpus_id": corpus_id,
        "analysis_unit": "paper",
        "analysis_mode": effective_analysis_mode,
        "requested_analysis_mode": requested_analysis_mode,
        "effective_analysis_mode": effective_analysis_mode,
        "design_question": design_question,
        "design_metric_ids": design_metric_ids,
        "analysis_mode_source": analysis_mode_source,
        "analysis_mode_downgrade_reason": mode_downgrade_reason,
        "distribution_ready_metric_count": distribution_ready_metric_count,
        "all_design_metrics_distribution_ready": all_design_metrics_distribution_ready,
        "design_metric_readiness": design_metric_readiness,
        "document_count": len(rows),
        "parsed_document_count": sum(row.get("status") == "ok" for row in rows),
        "supplement_document_count": len(supplement_rows),
        "venues": sorted(
            {str(row.get("source", {}).get("venue", "unknown")) for row in rows}
        ),
        "groups": {
            "overall": overall,
            "supplement": supplement,
            "by_partition": by_partition,
            "by_article_type": by_article_type,
            "by_partition_article_type": by_partition_article_type,
        },
        "comparisons": comparisons(main_rows),
        "sequences": {
            "by_document": sequence["document_sequences"],
            "top_sequences": sequence["top_sequences"],
        },
        "transitions": sequence["transitions"],
        "lead_lag": sequence["lead_lag"],
        "section_sequences": sequence["section_sequence"],
        "annotations": {
            "states": dict(sorted(annotation_state_counter.items())),
            "accepted_roles": dict(sorted(role_counter.items())),
        },
        "boundaries": [
            "Descriptive writing/presentation patterns only.",
            "Paper is the independent aggregation unit; nested objects are reduced per paper.",
            "No quality, novelty, venue-fit, acceptance, claim-truth, citation-authority, or statistical-correctness score.",
            "Supplement documents are reported in groups.supplement and are excluded from main-paper overall distributions and comparisons.",
            "Owner-confirmed inclusion exceptions remain visible in descriptive groups, mark the stratum non-comparable, and are excluded from partition effect comparisons.",
        ],
    }


def build_design_profile(
    corpus_id: str,
    summary: dict[str, Any],
    constraints: list[dict[str, Any]],
    registry: dict[str, Any],
) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for constraint in constraints:
        entries.append(
            {
                "profile_id": f"official:{constraint['constraint_id']}",
                "source_type": "official_constraints",
                "partition": "official_guidance",
                "metric_ids": [],
                "observation": constraint["statement"],
                "valid_n": 1,
                "missingness": 0,
                "uncertainty": {
                    "kind": "source_locator",
                    "locator": constraint["locator"],
                },
                "design_surface": constraint["design_surface"],
                "target_kind": "hard_constraint",
                "candidate_action": "follow",
                "affected_dimensions": constraint["affected_dimensions"],
                "affected_scopes": constraint["affected_scopes"],
                "boundary": "Hard only as an artifact-observed official presentation constraint; never scientific evidence.",
                "source_pointer": f"{constraint['source_path']}#{constraint['locator']}",
                "source_hash": constraint["source_sha256"],
                "origin": "artifact-observed",
                "resolution": "confirmed",
            }
        )
    overall = summary["groups"]["overall"]
    primary_group = next(
        (
            group
            for group in summary["groups"].get("by_partition", [])
            if group.get("filters", {}).get("partition") == "primary_match"
        ),
        None,
    )
    design_group = primary_group or overall
    design_partition = "primary_match" if primary_group else "overall"
    summary_pointer = (
        "groups.by_partition[primary_match]" if primary_group else "groups.overall"
    )
    known_design_metrics = {
        "text.body_words": ("manuscript-length", ["D09", "D15", "D17", "D19"]),
        "structure.paragraph_count": ("paragraph-rhythm", ["D15", "D17", "D19"]),
        "structure.section_count": ("section-architecture", ["D09", "D17", "D19"]),
        "object.figure_count": ("figure-plan", ["D18", "D19"]),
        "object.table_count": ("table-plan", ["D18", "D19"]),
        "object.equation_count": ("equation-plan", ["D17", "D18", "D19"]),
        "object.algorithm_count": ("algorithm-plan", ["D17", "D18", "D19"]),
        "citation.explicit_rate_per_kword": ("citation-density", ["D14", "D15", "D19"]),
    }
    mode = summary["effective_analysis_mode"]
    requested_mode = summary["requested_analysis_mode"]
    group_size_label = design_group["sample_size_label"]
    registry_by_id = {item["metric_id"]: item for item in registry["metrics"]}

    def metric_design(metric_id: str) -> tuple[str, list[str]]:
        if metric_id in known_design_metrics:
            return known_design_metrics[metric_id]
        definition = registry_by_id[metric_id]
        surfaces = definition.get("design_surfaces", [])
        surface = surfaces[0] if surfaces else "template-observation"
        prefix = metric_id.split(".", 1)[0]
        if prefix in {"citation", "reference"}:
            dimensions = ["D14", "D15", "D19"]
        elif prefix in {
            "object",
            "caption",
            "table",
            "equation",
            "algorithm",
            "callout",
            "lead_lag",
            "sequence",
            "transition",
        }:
            dimensions = ["D17", "D18", "D19"]
        else:
            dimensions = ["D09", "D15", "D17", "D19"]
        return surface, dimensions

    sequence_metric_ids = {
        metric_id
        for metric_id in summary["design_metric_ids"]
        if registry_by_id[metric_id].get("value_type") == "sequence"
    }
    for metric_id in summary["design_metric_ids"]:
        if metric_id in sequence_metric_ids:
            continue
        surface, dimensions = metric_design(metric_id)
        metric_summary = design_group["metrics"].get(metric_id)
        if not metric_summary or not metric_summary.get("valid_n"):
            entries.append(
                {
                    "profile_id": f"corpus:{metric_id}",
                    "source_type": "corpus",
                    "partition": design_partition,
                    "metric_ids": [metric_id],
                    "observation": "no-conclusion",
                    "valid_n": 0,
                    "missingness": metric_summary.get(
                        "missingness", summary["document_count"]
                    )
                    if metric_summary
                    else summary["document_count"],
                    "uncertainty": {
                        "analysis_mode": mode,
                        "requested_analysis_mode": requested_mode,
                        "effective_analysis_mode": mode,
                        "metric_effective_analysis_mode": "case_set",
                        "sample_size_label": "case_set",
                        "sample_size_label_is_gate": False,
                    },
                    "design_surface": surface,
                    "target_kind": "watch_only",
                    "candidate_action": "not_applicable",
                    "affected_dimensions": dimensions,
                    "affected_scopes": [],
                    "boundary": "Unavailable template metric; do not infer or block unrelated scopes.",
                    "source_pointer": f".yxj-paper-os/template-analysis/corpus-summary.json#{summary_pointer}.metrics.{metric_id}",
                    "origin": "model-proposed",
                    "resolution": "candidate",
                }
            )
            continue
        coverage = metric_summary["valid_n"] / max(
            1, metric_summary.get("eligible_n", design_group["document_count"])
        )
        comparable_stratum = not design_group.get("strata", {}).get("mixed", False)
        distribution_supported = (
            requested_mode == "distributional"
            and metric_summary["valid_n"] >= 5
            and coverage >= 0.8
            and metric_summary.get("bootstrap_95_ci") is not None
            and comparable_stratum
        )
        metric_effective_mode = (
            "distributional"
            if distribution_supported
            else "exploratory"
            if requested_mode in {"exploratory", "distributional"}
            and metric_summary["valid_n"] >= 5
            else "case_set"
        )
        target_kind = "soft_band" if distribution_supported else "watch_only"
        metric_size_label = metric_summary.get(
            "sample_size_label", sample_size_label(metric_summary["valid_n"])
        )
        observation = (
            f"available-paper median={metric_summary.get('median')}; "
            f"p25={metric_summary.get('p25')}; p75={metric_summary.get('p75')}"
        )
        entries.append(
            {
                "profile_id": f"corpus:{metric_id}",
                "source_type": "corpus",
                "partition": design_partition,
                "metric_ids": [metric_id],
                "observation": observation,
                "valid_n": metric_summary["valid_n"],
                "missingness": metric_summary["missingness"],
                "uncertainty": {
                    "analysis_mode": mode,
                    "requested_analysis_mode": requested_mode,
                    "effective_analysis_mode": mode,
                    "metric_effective_analysis_mode": metric_effective_mode,
                    "sample_size_label": metric_size_label,
                    "sample_size_label_is_gate": False,
                    "iqr": metric_summary.get("iqr"),
                    "mad": metric_summary.get("mad"),
                    "selection_boundary": "owner-supplied non-random corpus",
                    "valid_coverage": coverage,
                    "comparable_stratum": comparable_stratum,
                    "distribution_supported": distribution_supported,
                },
                "design_surface": surface,
                "target_kind": target_kind,
                "candidate_action": "adapt",
                "affected_dimensions": dimensions,
                "affected_scopes": [],
                "boundary": "Candidate descriptive writing-design pattern only; not a venue rule, optimum, or scientific evidence.",
                "source_pointer": f".yxj-paper-os/template-analysis/corpus-summary.json#{summary_pointer}.metrics.{metric_id}",
                "origin": "model-proposed",
                "resolution": "candidate",
            }
        )
    for metric_id in sorted(sequence_metric_ids):
        surface, dimensions = metric_design(metric_id)
        if metric_id == "sequence.object_type_order":
            sequence_summary = design_group["object_sequence"]
            pointer_suffix = "object_sequence"
        elif metric_id == "sequence.section_order_proxy":
            sequence_summary = design_group["object_sequence"]["section_sequence"]
            pointer_suffix = "object_sequence.section_sequence"
        else:
            sequence_summary = {"document_sequences": [], "top_sequences": []}
            pointer_suffix = f"metrics.{metric_id}"
        sequence_documents = sequence_summary.get("document_sequences", [])
        sequence_valid_n = sum(isinstance(item, dict) for item in sequence_documents)
        top_sequences = [
            item
            for item in sequence_summary.get("top_sequences", [])
            if isinstance(item, dict) and item.get("sequence")
        ]
        sequence_effective_mode = (
            "exploratory"
            if requested_mode in {"exploratory", "distributional"}
            and sequence_valid_n >= 5
            else "case_set"
        )
        entries.append(
            {
                "profile_id": f"corpus:{metric_id}",
                "source_type": "corpus",
                "partition": design_partition,
                "metric_ids": [metric_id],
                "observation": top_sequences[0] if top_sequences else "no-conclusion",
                "valid_n": sequence_valid_n,
                "missingness": design_group["document_count"] - sequence_valid_n,
                "uncertainty": {
                    "analysis_mode": mode,
                    "requested_analysis_mode": requested_mode,
                    "effective_analysis_mode": mode,
                    "metric_effective_analysis_mode": sequence_effective_mode,
                    "sample_size_label": sample_size_label(sequence_valid_n)
                    if sequence_valid_n
                    else group_size_label,
                    "sample_size_label_is_gate": False,
                },
                "design_surface": surface,
                "target_kind": "sequence" if top_sequences else "watch_only",
                "candidate_action": "adapt" if top_sequences else "not_applicable",
                "affected_dimensions": dimensions,
                "affected_scopes": [],
                "boundary": "Observed sequence is descriptive and may reflect extraction/source conventions.",
                "source_pointer": f".yxj-paper-os/template-analysis/corpus-summary.json#{summary_pointer}.{pointer_suffix}",
                "origin": "model-proposed",
                "resolution": "candidate",
            }
        )
    return {
        "schema": PROFILE_SCHEMA,
        "analyzer_version": ANALYZER_VERSION,
        "corpus_id": corpus_id,
        "design_question": summary["design_question"],
        "design_metric_ids": summary["design_metric_ids"],
        "entries": entries,
        "forbidden_uses": [
            "scientific claim support",
            "quality or novelty scoring",
            "venue-fit or acceptance prediction",
            "automatic owner decision",
        ],
    }


def build_report(
    corpus_id: str,
    summary: dict[str, Any],
    profile: dict[str, Any],
) -> str:
    def escape(value: Any) -> str:
        return html.escape(str(value), quote=True)

    overall = summary["groups"]["overall"]
    rows: list[str] = []
    for metric_id in summary["design_metric_ids"]:
        item = overall["metrics"].get(metric_id, {})
        rows.append(
            "<tr>"
            f"<td>{escape(metric_id)}</td>"
            f"<td>{escape(item.get('valid_n', 0))}</td>"
            f"<td>{escape(item.get('median', 'no-conclusion'))}</td>"
            f"<td>{escape(item.get('p25', '—'))}</td>"
            f"<td>{escape(item.get('p75', '—'))}</td>"
            f"<td>{escape(item.get('missingness', 0))}</td>"
            "</tr>"
        )
    profile_items = "".join(
        "<li>"
        f"<strong>{escape(item.get('design_surface'))}</strong>: "
        f"{escape(item.get('observation'))} "
        f"<span class='tag'>{escape(item.get('target_kind'))}</span>"
        "</li>"
        for item in profile["entries"]
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="yxj-analysis-id" content="{escape(summary.get("analysis_id", "unknown"))}">
<title>Template corpus analysis — {escape(corpus_id)}</title>
<style>
:root{{--ink:#17202a;--muted:#5d6d7e;--line:#d5d8dc;--paper:#fff;--wash:#f4f6f7;--accent:#245a73}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--wash);color:var(--ink);font:15px/1.55 system-ui,sans-serif}}
main{{max-width:1100px;margin:32px auto;padding:28px;background:var(--paper);border:1px solid var(--line)}}
h1,h2{{line-height:1.2}}table{{width:100%;border-collapse:collapse}}th,td{{padding:8px;border:1px solid var(--line);text-align:left}}
.tag{{display:inline-block;padding:1px 6px;border:1px solid var(--accent);color:var(--accent);border-radius:999px}}.boundary{{padding:12px;border-left:4px solid var(--accent);background:#eef6f8}}
</style></head><body><main>
<h1>Template corpus analysis</h1><p><strong>Corpus:</strong> {escape(corpus_id)}</p>
<p><strong>Venues represented:</strong> {escape(", ".join(summary.get("venues", [])))}</p>
<p><strong>Analysis ID:</strong> {escape(summary.get("analysis_id", "unknown"))}</p>
<p><strong>Paper-level sample:</strong> {summary["parsed_document_count"]} parsed of {summary["document_count"]} supplied; <strong>requested mode:</strong> {escape(summary["requested_analysis_mode"])}; <strong>effective mode:</strong> {escape(summary["effective_analysis_mode"])}; <strong>count context:</strong> {escape(overall["sample_size_label"])} (not a gate).</p>
<div class="boundary">Descriptive text/structure/presentation evidence only. This report does not score quality, novelty, scientific validity, venue fit, or acceptance probability.</div>
<h2>Declared design metrics at paper level</h2>
<table><thead><tr><th>Metric</th><th>valid n</th><th>median</th><th>p25</th><th>p75</th><th>missing</th></tr></thead><tbody>{"".join(rows)}</tbody></table>
<h2>Candidate design profile</h2><ul>{profile_items}</ul>
<h2>Object-order invariant</h2><p>Expected transitions: {summary["transitions"]["expected_total"]}; observed: {summary["transitions"]["observed_total"]}; invariant: {escape(summary["transitions"]["invariant_holds"])}.</p>
</main></body></html>
"""


def parse_registry(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = read_bounded(path, field_name="metric registry")
    try:
        registry = json.loads(raw.decode("utf-8"), parse_constant=reject_nonfinite_json)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ContractError(f"metric registry is invalid: {exc}") from exc
    if (
        not isinstance(registry, dict)
        or registry.get("schema") != "template-metric-registry/1.0"
    ):
        raise ContractError(
            "metric registry schema must be template-metric-registry/1.0"
        )
    metrics = registry.get("metrics")
    if not isinstance(metrics, list) or not metrics:
        raise ContractError("metric registry must contain metrics")
    identifiers = [item.get("metric_id") for item in metrics if isinstance(item, dict)]
    if len(identifiers) != len(metrics) or len(set(identifiers)) != len(identifiers):
        raise ContractError("metric registry IDs must be present and unique")
    return registry, raw


def compute_analysis_id(
    manifest: dict[str, Any],
    manifest_bytes: bytes,
    registry_bytes: bytes,
    loaded_documents: list[LoadedDocument],
    constraints: list[dict[str, Any]],
) -> str:
    preimage = {
        "schema": "template-analysis-bundle-preimage/1.0",
        "analyzer_version": ANALYZER_VERSION,
        "corpus_id": manifest["corpus_id"],
        "source_manifest_sha256": sha256_bytes(manifest_bytes),
        "metric_registry_sha256": sha256_bytes(registry_bytes),
        "documents": [
            {
                "doc_id": document.spec["doc_id"],
                "source_sha256": document.source_sha256,
                "annotation_sha256": document.annotation_sha256,
            }
            for document in loaded_documents
        ],
        "official_constraints": [
            {
                "constraint_id": constraint["constraint_id"],
                "source_sha256": constraint["source_sha256"],
            }
            for constraint in constraints
        ],
    }
    digest = sha256_bytes(canonical_json(preimage, pretty=False).rstrip(b"\n"))
    return f"sha256:{digest}"


def failed_paper_row(
    loaded: LoadedDocument, message: str, registry: dict[str, Any]
) -> dict[str, Any]:
    return {
        "schema": PAPER_SCHEMA,
        "doc_id": loaded.spec["doc_id"],
        "partition": loaded.spec["partition"],
        "status": "parse_failed",
        "source": {
            "path": loaded.relative_path,
            "format": loaded.spec["format"],
            "sha256": loaded.source_sha256,
            "article_type": loaded.spec.get("article_type", "unknown"),
            "venue": loaded.spec.get("venue", "unknown"),
            "topic_tags": loaded.spec.get("topic_tags", []),
            "year": loaded.spec.get("year"),
            "language": loaded.spec.get("language", "und"),
            "supplement_of": loaded.spec.get("supplement_of"),
            "inclusion_exception": loaded.spec.get("inclusion_exception"),
        },
        "parse": {
            "adapter": loaded.spec["format"],
            "analyzer_version": ANALYZER_VERSION,
            "status": "parse_failed",
            "message": message,
        },
        "metrics": {
            item["metric_id"]: metric(
                None,
                status="parse_failed",
                unit=str(item.get("unit", "unknown")),
                method="not_computed",
            )
            for item in registry["metrics"]
        },
        "entities": {"sections": [], "paragraphs": []},
    }


def analyze(
    manifest_path: Path,
    output_dir: Path,
    registry_path: Path,
) -> tuple[int, dict[str, Any]]:
    manifest, loaded_documents, constraints, manifest_bytes = load_inputs(manifest_path)
    registry, registry_bytes = parse_registry(registry_path)
    registry_metric_ids = {item["metric_id"] for item in registry["metrics"]}
    unknown_design_metrics = sorted(
        set(manifest["design_metric_ids"]) - registry_metric_ids
    )
    if unknown_design_metrics:
        raise ContractError(
            "design_metric_ids are absent from the metric registry: "
            + ", ".join(unknown_design_metrics)
        )
    analysis_id = compute_analysis_id(
        manifest,
        manifest_bytes,
        registry_bytes,
        loaded_documents,
        constraints,
    )
    resolved_output = output_dir.resolve()
    input_paths = [manifest_path.resolve(), registry_path.resolve()]
    input_paths.extend(document.path.resolve() for document in loaded_documents)
    input_paths.extend(
        document.annotation_path.resolve()
        for document in loaded_documents
        if document.annotation_path is not None
    )
    input_paths.extend(
        ensure_inside(
            manifest_path.parent.resolve(),
            constraint["source_path"],
            field_name=f"{constraint['constraint_id']}.source_path",
        )
        for constraint in constraints
    )
    for input_path in input_paths:
        try:
            input_path.relative_to(resolved_output)
        except ValueError:
            continue
        raise ContractError(
            f"input/output overlap is forbidden: {input_path} is below {resolved_output}"
        )
    warnings: list[dict[str, Any]] = []
    paper_rows: list[dict[str, Any]] = []
    all_objects: list[dict[str, Any]] = []
    annotation_states: list[dict[str, Any]] = []
    normalized_documents: list[dict[str, Any]] = []

    for loaded in loaded_documents:
        parse_status = "ok"
        parse_message = "ok"
        try:
            document = parse_document(loaded.spec["format"], loaded.raw)
            body_text, body_words = assign_positions(document)
            if body_words == 0:
                raise ValueError("body text region is empty")
            objects = build_objects(
                loaded.spec["doc_id"], loaded.source_sha256, document, body_words
            )
            annotation_state = apply_annotations(loaded, objects, warnings)
            annotation_states.append(annotation_state)
            metrics, entities = compute_metrics(
                loaded, document, body_text, body_words, objects, registry
            )
            paper_rows.append(
                {
                    "schema": PAPER_SCHEMA,
                    "doc_id": loaded.spec["doc_id"],
                    "partition": loaded.spec["partition"],
                    "status": "ok",
                    "source": {
                        "path": loaded.relative_path,
                        "format": loaded.spec["format"],
                        "sha256": loaded.source_sha256,
                        "article_type": loaded.spec.get("article_type", "unknown"),
                        "venue": loaded.spec.get("venue", "unknown"),
                        "topic_tags": loaded.spec.get("topic_tags", []),
                        "year": loaded.spec.get("year"),
                        "language": loaded.spec.get("language", "und"),
                        "supplement_of": loaded.spec.get("supplement_of"),
                        "inclusion_exception": loaded.spec.get("inclusion_exception"),
                    },
                    "parse": {
                        "adapter": loaded.spec["format"],
                        "analyzer_version": ANALYZER_VERSION,
                        "status": "ok",
                        "capability": document.capability,
                        "warnings": document.warnings,
                    },
                    "metrics": metrics,
                    "entities": entities,
                }
            )
            all_objects.extend(objects)
            for message in document.warnings:
                warnings.append(
                    {
                        "doc_id": loaded.spec["doc_id"],
                        "code": "adapter_warning",
                        "message": message,
                    }
                )
        except (UnicodeDecodeError, ET.ParseError, ValueError, RecursionError) as exc:
            parse_status = "parse_failed"
            parse_message = str(exc)
            paper_rows.append(failed_paper_row(loaded, parse_message, registry))
            annotation_states.append({"states": {}, "accepted_roles": {}})
            warnings.append(
                {
                    "doc_id": loaded.spec["doc_id"],
                    "code": "parse_failed",
                    "message": parse_message,
                }
            )
        normalized_document = dict(loaded.spec)
        normalized_document.update(
            {
                "source_sha256": loaded.source_sha256,
                "source_bytes": len(loaded.raw),
                "parse_status": parse_status,
                "parse_message": parse_message,
            }
        )
        if loaded.annotation_relative_path:
            normalized_document["annotation_sha256"] = loaded.annotation_sha256
        normalized_documents.append(normalized_document)

    for row in paper_rows:
        row["analysis_id"] = analysis_id
        row["corpus_id"] = manifest["corpus_id"]
    for item in all_objects:
        item["analysis_id"] = analysis_id
        item["corpus_id"] = manifest["corpus_id"]

    summary = build_summary(
        manifest["corpus_id"],
        manifest["analysis_mode"],
        manifest["analysis_mode_source"],
        manifest["design_question"],
        manifest["design_metric_ids"],
        paper_rows,
        all_objects,
        annotation_states,
    )
    profile = build_design_profile(
        manifest["corpus_id"], summary, constraints, registry
    )
    summary["analysis_id"] = analysis_id
    profile["analysis_id"] = analysis_id
    normalized_manifest = {
        "schema": "template-corpus-normalized/1.0",
        "analyzer_version": ANALYZER_VERSION,
        "analysis_id": analysis_id,
        "corpus_id": manifest["corpus_id"],
        "target": manifest.get("target", {}),
        "analysis_mode": summary["effective_analysis_mode"],
        "requested_analysis_mode": manifest["analysis_mode"],
        "effective_analysis_mode": summary["effective_analysis_mode"],
        "analysis_mode_source": manifest["analysis_mode_source"],
        "analysis_mode_downgrade_reason": summary["analysis_mode_downgrade_reason"],
        "design_question": manifest["design_question"],
        "design_metric_ids": manifest["design_metric_ids"],
        "source_manifest_sha256": sha256_bytes(manifest_bytes),
        "metric_registry_sha256": sha256_bytes(registry_bytes),
        "documents": normalized_documents,
        "official_constraints": constraints,
    }
    warning_output = {
        "schema": WARNINGS_SCHEMA,
        "analyzer_version": ANALYZER_VERSION,
        "analysis_id": analysis_id,
        "corpus_id": manifest["corpus_id"],
        "warnings": warnings,
        "warning_count": len(warnings),
    }
    report = build_report(manifest["corpus_id"], summary, profile).encode("utf-8")
    registry_output = dict(registry)
    registry_output["analysis_id"] = analysis_id
    registry_output["corpus_id"] = manifest["corpus_id"]
    registry_output["analyzer_version"] = ANALYZER_VERSION
    payloads = {
        "manifest.json": canonical_json(normalized_manifest),
        "metric-registry.json": canonical_json(registry_output),
        "paper-metrics.jsonl": canonical_jsonl(paper_rows),
        "objects.jsonl": canonical_jsonl(all_objects),
        "corpus-summary.json": canonical_json(summary),
        "design-profile.json": canonical_json(profile),
        "extraction-warnings.json": canonical_json(warning_output),
        "analysis-report.html": report,
    }
    write_bundle_transactional(output_dir, payloads)
    parsed_count = sum(row["status"] == "ok" for row in paper_rows)
    return (0 if parsed_count else 1), {
        "output_dir": str(output_dir),
        "analysis_id": analysis_id,
        "document_count": len(paper_rows),
        "parsed_document_count": parsed_count,
        "warning_count": len(warnings),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze a target-journal/template corpus into deterministic hidden artifacts."
    )
    parser.add_argument("manifest_positional", nargs="?", metavar="MANIFEST")
    parser.add_argument("--manifest", dest="manifest_flag")
    parser.add_argument("--output", "--output-dir", dest="output_dir")
    parser.add_argument("--registry")
    parser.add_argument("--force", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--pretty", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    candidates = [
        value for value in (args.manifest_positional, args.manifest_flag) if value
    ]
    if len(candidates) != 1:
        parser.error(
            "provide exactly one manifest path, positionally or with --manifest"
        )
    args.manifest = candidates[0]
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    manifest_path = Path(args.manifest).expanduser().resolve()
    manifest_root = manifest_path.parent.resolve()
    cache_path = manifest_root / ".yxj-paper-os"
    hidden_path = cache_path / "template-analysis"
    if cache_path.is_symlink() or hidden_path.is_symlink():
        print(
            "error: .yxj-paper-os and template-analysis must not be symlinks",
            file=sys.stderr,
        )
        return 2
    cache_root = cache_path.resolve()
    hidden_root = hidden_path.resolve()
    output_dir = (
        Path(args.output_dir).expanduser().resolve() if args.output_dir else hidden_root
    )
    try:
        cache_root.relative_to(manifest_root)
        hidden_root.relative_to(cache_root)
        hidden_root.relative_to(manifest_root)
        if output_dir != hidden_root:
            raise ValueError("output must equal canonical hidden root")
    except ValueError:
        print(
            "error: output must equal the non-escaping canonical path "
            f"{manifest_root / '.yxj-paper-os' / 'template-analysis'}",
            file=sys.stderr,
        )
        return 2
    default_registry = (
        Path(__file__).resolve().parent.parent
        / "assets"
        / "template-analysis"
        / "metric-registry.json"
    )
    registry_path = (
        Path(args.registry).expanduser().resolve()
        if args.registry
        else default_registry
    )
    try:
        exit_code, result = analyze(manifest_path, output_dir, registry_path)
    except (ContractError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
