#!/usr/bin/env python3
"""Mechanical sparse-schema validator for a yxj-paper-os workspace."""

from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

REQUIRED_FILES = [
    "00_DIMENSION_INDEX.md",
    "00_PROJECT_ROUTE.md",
    "01_MATERIALS_INVENTORY.md",
    "02_CLAIM_EVIDENCE_BOUNDARY.md",
    "03_WRITING_STRUCTURE.md",
    "04_WRITING_DESIGN_PACK.md",
]
DIMENSION_INDEX = REQUIRED_FILES[0]
FINAL_PACK = REQUIRED_FILES[-1]
REQUIRED_DIMENSION_IDS = [f"D{i:02d}" for i in range(20)]
DIMENSION_COLUMNS = [
    "ID",
    "Dimension",
    "Current home",
    "Status",
    "Reason / owner note",
    "Pointer or handoff",
    "Blocks design pack?",
]
VALID_DIMENSION_STATUSES = {
    "filled",
    "not_applicable",
    "absent",
    "deferred",
    "rejected",
}
VALID_BLOCKS_VALUES = {"yes", "no"}
REQUIRED_HEADINGS = {name: [] for name in REQUIRED_FILES}
SPARSE_TABLES = {
    (DIMENSION_INDEX, "Writing Scopes"): [
        "Scope ID",
        "Writing surface",
        "Intended output",
        "Readiness",
        "Available inputs",
        "Required requirement IDs",
        "Remaining blocker",
        "Next action",
        "Output pointer",
    ],
    (DIMENSION_INDEX, "Active Calibration Lenses"): [
        "Lens ID",
        "Activation basis",
        "Affected scopes",
    ],
    (DIMENSION_INDEX, "Conditional Requirements"): [
        "Requirement ID",
        "Lens ID",
        "Requirement",
        "Affected scopes",
        "Handling",
        "Evidence / decision pointer",
    ],
    (DIMENSION_INDEX, "Dependency Recheck"): [
        "Changed record",
        "Affected D IDs / scopes",
        "Disposition",
        "Resolution or next action",
    ],
    ("00_PROJECT_ROUTE.md", "Decision Records"): [
        "Decision ID",
        "Issue",
        "Decision or live options",
        "Affected scopes",
        "Origin",
        "Resolution",
        "Grounding",
    ],
    ("01_MATERIALS_INVENTORY.md", "Material Records"): [
        "Record ID",
        "Kind",
        "Content / role",
        "Locator",
        "Scope / conditions",
        "Status",
        "Origin",
        "Resolution",
        "Grounding",
    ],
    ("02_CLAIM_EVIDENCE_BOUNDARY.md", "Claim Records"): [
        "Claim ID",
        "Claim",
        "Evidence record IDs",
        "Warrant / support relation",
        "Scope / conditions",
        "Directness",
        "Uncertainty / counterevidence",
        "Allowed wording",
        "Forbidden wording",
        "Status",
        "Origin",
        "Support",
        "Resolution",
        "Grounding",
    ],
    ("03_WRITING_STRUCTURE.md", "Scoped Writing Plan"): [
        "Scope ID",
        "Reader / section job",
        "Input record IDs",
        "Output responsibility",
        "Drafting boundary",
        "Output pointer",
    ],
    (FINAL_PACK, "Scoped Handoff"): [
        "Scope ID",
        "Writing surface",
        "Intended output",
        "Readiness",
        "Available inputs",
        "Required requirement IDs",
        "Remaining blocker",
        "Next action",
        "Output pointer",
    ],
}
ID_RE = re.compile(r"^(?:SCOPE|REQ|DEC|M|C)-[a-z0-9]+(?:-[a-z0-9]+)*$")
D_RE = re.compile(r"^D(?:0[0-9]|1[0-9])$")
READINESS = {"writer-ready", "partial", "blocked", "deferred"}
REQ_STATE = {"satisfied", "blocked", "deferred", "not_applicable"}
DISPOSITION = {
    "current",
    "rechecked",
    "stale",
    "candidate",
    "blocked",
    "not_applicable",
}
MATERIAL_STATUS = {"available", "partial", "planned", "unavailable", "rejected"}
CLAIM_STATUS = {"active", "downgraded", "deferred", "rejected"}
ORIGIN = {"artifact-observed", "owner-stated", "model-derived", "model-proposed"}
SUPPORT = {
    "evidence-supported",
    "evidence-partial",
    "evidence-unsupported",
    "not_applicable",
}
RESOLUTION = {"confirmed", "candidate", "unresolved", "conflicted", "rejected"}
LENS_IDS = {
    "method-algorithm",
    "system-software",
    "benchmark-dataset-resource",
    "empirical-application",
    "survey-review",
    "theory-formal",
    "human-study-mixed-methods",
    "research-design-validity",
    "evidence-results-statistics",
    "literature-differentiation",
    "reproducibility-governance",
    "argument-language-visual",
    "venue-template",
}
NONE_ALLOWED = {
    (DIMENSION_INDEX, "Writing Scopes"): {
        "Available inputs",
        "Required requirement IDs",
        "Remaining blocker",
        "Next action",
        "Output pointer",
    },
    (DIMENSION_INDEX, "Active Calibration Lenses"): {"Affected scopes"},
    (DIMENSION_INDEX, "Conditional Requirements"): {
        "Affected scopes",
        "Evidence / decision pointer",
    },
    (DIMENSION_INDEX, "Dependency Recheck"): {
        "Affected D IDs / scopes",
        "Resolution or next action",
    },
    ("00_PROJECT_ROUTE.md", "Decision Records"): {
        "Decision or live options",
        "Affected scopes",
        "Grounding",
    },
    ("01_MATERIALS_INVENTORY.md", "Material Records"): {
        "Locator",
        "Scope / conditions",
        "Grounding",
    },
    ("02_CLAIM_EVIDENCE_BOUNDARY.md", "Claim Records"): {
        "Evidence record IDs",
        "Warrant / support relation",
        "Scope / conditions",
        "Directness",
        "Uncertainty / counterevidence",
        "Allowed wording",
        "Forbidden wording",
        "Grounding",
    },
    ("03_WRITING_STRUCTURE.md", "Scoped Writing Plan"): {
        "Input record IDs",
        "Output pointer",
    },
    (FINAL_PACK, "Scoped Handoff"): {
        "Available inputs",
        "Required requirement IDs",
        "Remaining blocker",
        "Next action",
        "Output pointer",
    },
}


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def has_placeholder(text: str) -> bool:
    return bool(re.search(r"(?m)^\s*(?:TODO|TBD)\s*$", text))


def level_two_heading_slugs(text: str) -> dict[str, str]:
    return {
        slugify(m.group(1)): m.group(1).strip()
        for m in re.finditer(r"^##\s+(.+?)\s*$", text, re.M)
    }


def section_content(text: str, heading: str) -> str | None:
    match = re.search(rf"^##\s+{re.escape(heading)}\s*$", text, re.M)
    if not match:
        return None
    tail = text[match.end() :]
    next_heading = re.search(r"^##\s+", tail, re.M)
    return tail[: next_heading.start()] if next_heading else tail


def parse_anchor(
    value: str, contents: dict[str, str] | None = None
) -> tuple[str, str, str | None]:
    if "#" not in value:
        return "", "", "pointer must use file#heading syntax"
    name, anchor = value.split("#", 1)
    if not name:
        return (name, slugify(anchor), "pointer file name is missing")
    return name, slugify(anchor), None


def first_present(*values):
    if (
        len(values) == 2
        and isinstance(values[1], (list, tuple))
        and isinstance(values[0], dict)
    ):
        return (
            next(
                (
                    values[0].get(key)
                    for key in values[1]
                    if values[0].get(key) not in (None, "")
                ),
                "",
            )
            or ""
        )
    return next((v for v in values if v not in (None, "")), "")


def _table(text: str, heading: str) -> tuple[list[str] | None, list[list[str]]]:
    section = section_content(text, heading)
    if section is None:
        return None, []
    lines = [x.strip() for x in section.splitlines() if x.strip().startswith("|")]
    if len(lines) < 2:
        return None, []

    def cells(x: str) -> list[str]:
        return [c.strip() for c in x.strip().strip("|").split("|")]

    header = cells(lines[0])
    rows = []
    for line in lines[1:]:
        if re.fullmatch(r"\|?\s*:?-+:?\s*(?:\|\s*:?-+:?\s*)+\|?", line):
            continue
        rows.append(cells(line))
    return header, rows


def parse_first_table(text: str, heading: str):
    header, rows = _table(text, heading)
    return header or [], [
        dict(zip(header or [], row)) for row in rows if len(row) == len(header or [])
    ]


def _records(
    file_name: str, heading: str, text: str, workspace: Path, errors: list[str]
) -> list[dict[str, str]]:
    expected = SPARSE_TABLES[(file_name, heading)]
    header, rows = _table(text, heading)
    if header is None:
        return []
    if header != expected:
        errors.append(
            f"{file_name}#{heading}: columns must be exactly: " + " | ".join(expected)
        )
        return []
    out = []
    for row in rows:
        if len(row) != len(expected):
            errors.append(f"{file_name}#{heading}: wrong cell count")
            continue
        if any(not c or c == "TODO" for c in row):
            errors.append(f"{file_name}#{heading}: populated row contains blank/TODO")
            continue
        for column, value in zip(expected, row):
            if value == "none" and column not in NONE_ALLOWED[(file_name, heading)]:
                errors.append(f"{file_name}#{heading}: none is not allowed in {column}")
        out.append(dict(zip(expected, row)))
    return out


def _valid_ref(value: str, workspace: Path, allow_none: bool = True) -> bool:
    if value == "none":
        return allow_none
    if ID_RE.match(value) or D_RE.match(value):
        return True
    if value.startswith("path:"):
        return (workspace / value[5:].split("#", 1)[0]).is_file()
    if "#" in value:
        name, heading = value.split("#", 1)
        path = workspace / name
        return (
            path.is_file()
            and section_content(path.read_text(encoding="utf-8"), heading) is not None
        )
    return False


def _validate_dimension_index(text: str, errors: list[str]) -> None:
    header, rows = _table(text, "Dimension Status Index")
    if header != DIMENSION_COLUMNS:
        errors.append("00_DIMENSION_INDEX.md: public index columns changed")
    seen = []
    for row in rows:
        if len(row) < 7:
            continue
        seen.append(row[0])
        if row[0] in REQUIRED_DIMENSION_IDS and row[3] not in VALID_DIMENSION_STATUSES:
            errors.append(f"invalid dimension status {row[3]!r}")
        if row[0] in REQUIRED_DIMENSION_IDS and row[6] not in VALID_BLOCKS_VALUES:
            errors.append(f"invalid Blocks design pack? value {row[6]!r}")
    if seen != REQUIRED_DIMENSION_IDS:
        errors.append("D00-D19 must appear exactly once and in order")


def validate_workspace(workspace: Path, require_handoff: bool = False) -> list[str]:
    errors = []
    if not workspace.is_dir():
        return [f"workspace not found: {workspace}"]
    required = set(REQUIRED_FILES)
    present = {p.name for p in workspace.glob("*.md")}
    errors += [
        f"unexpected public Markdown file: {x}" for x in sorted(present - required)
    ]
    errors += [f"missing required file: {x}" for x in sorted(required - present)]
    contents = {
        n: (workspace / n).read_text(encoding="utf-8") for n in required & present
    }
    idx = contents.get(DIMENSION_INDEX, "")
    if idx and "Workspace schema version: 0.2" not in idx:
        return errors + [
            "legacy workspace: expected Workspace schema version: 0.2; normalize metadata first"
        ]
    if idx:
        _validate_dimension_index(idx, errors)
    scopes = []
    table_rows = {}
    for (file_name, heading), _ in SPARSE_TABLES.items():
        if file_name not in contents:
            continue
        rows = _records(file_name, heading, contents[file_name], workspace, errors)
        table_rows[(file_name, heading)] = rows
        if heading == "Writing Scopes":
            scopes = rows
            for r in rows:
                if r["Readiness"] not in READINESS:
                    errors.append(f"invalid scope readiness {r['Readiness']!r}")
                if r["Readiness"] == "writer-ready":
                    if (
                        r["Remaining blocker"] != "none"
                        or r["Next action"] != "none"
                        or r["Output pointer"] == "none"
                    ):
                        errors.append(
                            "writer-ready scope requires blocker/next none and output pointer"
                        )
                elif r["Remaining blocker"] == "none" or r["Next action"] == "none":
                    errors.append("non-ready scope requires blocker and next action")
        elif heading == "Conditional Requirements":
            for r in rows:
                if r["Handling"] not in REQ_STATE:
                    errors.append(f"invalid requirement handling {r['Handling']!r}")
                if (
                    r["Handling"] in {"satisfied", "blocked"}
                    and r["Evidence / decision pointer"] == "none"
                ):
                    errors.append(
                        "satisfied/blocked requirement needs evidence or decision pointer"
                    )
        elif heading == "Dependency Recheck":
            for r in rows:
                if r["Disposition"] not in DISPOSITION:
                    errors.append(
                        f"invalid dependency disposition {r['Disposition']!r}"
                    )
                if (
                    r["Disposition"] in {"stale", "candidate", "blocked"}
                    and r["Resolution or next action"] == "none"
                ):
                    errors.append(
                        "stale/candidate/blocked dependency needs next action"
                    )
        elif heading == "Material Records":
            for r in rows:
                if (
                    not r["Record ID"].startswith("M-")
                    or r["Status"] not in MATERIAL_STATUS
                    or r["Origin"] not in ORIGIN
                    or r["Resolution"] not in RESOLUTION
                ):
                    errors.append("invalid material record enum or ID")
                if (
                    r["Status"] in {"available", "partial"}
                    and r["Kind"] in {"artifact", "result", "evidence"}
                    and r["Locator"] == "none"
                ):
                    errors.append(
                        "available/partial artifact, result, or evidence needs locator"
                    )
                if (
                    r["Origin"] in {"model-derived", "model-proposed"}
                    and r["Grounding"] == "none"
                ):
                    errors.append(
                        "model-derived/model-proposed material needs grounding"
                    )
                if r["Locator"] != "none" and not _valid_ref(
                    r["Locator"], workspace, allow_none=False
                ):
                    errors.append("material has invalid locator")
                if r["Grounding"] != "none" and any(
                    not _valid_ref(token, workspace, allow_none=False)
                    for token in r["Grounding"].split("; ")
                ):
                    errors.append("material has invalid grounding reference")
        elif heading == "Claim Records":
            for r in rows:
                if (
                    not r["Claim ID"].startswith("C-")
                    or r["Status"] not in CLAIM_STATUS
                    or r["Origin"] not in ORIGIN
                    or r["Support"] not in SUPPORT
                    or r["Resolution"] not in RESOLUTION
                ):
                    errors.append("invalid claim record enum or ID")
                if r["Status"] in {"active", "downgraded"} and any(
                    r[k] == "none"
                    for k in (
                        "Evidence record IDs",
                        "Warrant / support relation",
                        "Scope / conditions",
                        "Directness",
                        "Uncertainty / counterevidence",
                        "Allowed wording",
                        "Forbidden wording",
                    )
                ):
                    errors.append("active/downgraded claim lacks evidence boundary")
                if r["Status"] in {"active", "downgraded"} and r["Support"] not in {
                    "evidence-supported",
                    "evidence-partial",
                }:
                    errors.append("active/downgraded claim needs evidence support")
                if r["Status"] in {"active", "downgraded"} and r["Resolution"] in {
                    "unresolved",
                    "conflicted",
                }:
                    errors.append("unresolved/conflicted claim cannot be active")
                if r["Origin"] == "model-proposed" and r["Status"] in {
                    "active",
                    "downgraded",
                }:
                    errors.append(
                        "model-proposed claim must be superseded by a new record"
                    )
                if (
                    r["Origin"] in {"model-derived", "model-proposed"}
                    and r["Grounding"] == "none"
                ):
                    errors.append("model-derived/model-proposed claim needs grounding")
    scope_ids = {r["Scope ID"] for r in scopes}
    for row in table_rows.get((DIMENSION_INDEX, "Active Calibration Lenses"), []):
        if row["Lens ID"] not in LENS_IDS:
            errors.append(f"unknown lens ID {row['Lens ID']}")
        if row["Affected scopes"] != "none":
            for token in row["Affected scopes"].split("; "):
                if token not in scope_ids:
                    errors.append(f"lens references unknown scope {token}")
    req_rows = table_rows.get((DIMENSION_INDEX, "Conditional Requirements"), [])
    req_ids = {r["Requirement ID"] for r in req_rows}
    req_by_id = {r["Requirement ID"]: r for r in req_rows}
    active_lens_ids = {
        r["Lens ID"]
        for r in table_rows.get((DIMENSION_INDEX, "Active Calibration Lenses"), [])
    }
    for row in req_rows:
        if row["Lens ID"] not in active_lens_ids:
            errors.append(f"requirement references inactive lens {row['Lens ID']}")
    for row in scopes:
        if (
            row["Readiness"] == "writer-ready"
            and row["Required requirement IDs"] != "none"
        ):
            for token in row["Required requirement IDs"].split("; "):
                if token in req_by_id and req_by_id[token]["Handling"] not in {
                    "satisfied",
                    "not_applicable",
                }:
                    errors.append(
                        f"writer-ready scope references unsatisfied requirement {token}"
                    )
    material_rows = table_rows.get(
        ("01_MATERIALS_INVENTORY.md", "Material Records"), []
    )
    material_ids = {r["Record ID"] for r in material_rows}
    material_by_id = {r["Record ID"]: r for r in material_rows}
    claim_rows = table_rows.get(("02_CLAIM_EVIDENCE_BOUNDARY.md", "Claim Records"), [])
    for row in scopes:
        refs = (
            []
            if row["Required requirement IDs"] == "none"
            else row["Required requirement IDs"].split("; ")
        )
        for token in refs:
            if token not in req_ids:
                errors.append(f"scope references unknown requirement {token}")
    for row in req_rows:
        refs = (
            []
            if row["Affected scopes"] == "none"
            else row["Affected scopes"].split("; ")
        )
        for token in refs:
            if token not in scope_ids:
                errors.append(f"requirement references unknown scope {token}")
        if not _valid_ref(
            row["Evidence / decision pointer"],
            workspace,
            allow_none=row["Handling"] in {"deferred", "not_applicable"},
        ):
            errors.append("requirement has invalid evidence/decision pointer")
    for row in claim_rows:
        refs = (
            []
            if row["Evidence record IDs"] == "none"
            else row["Evidence record IDs"].split("; ")
        )
        for token in refs:
            if token not in material_ids:
                errors.append(f"claim references unknown material record {token}")
            elif row["Status"] in {"active", "downgraded"} and material_by_id[token][
                "Status"
            ] not in {"available", "partial"}:
                errors.append(
                    f"active claim references unavailable material record {token}"
                )
        if row["Grounding"] != "none" and any(
            not _valid_ref(token, workspace, allow_none=False)
            for token in row["Grounding"].split("; ")
        ):
            errors.append("claim has invalid grounding reference")
    dep_rows = table_rows.get((DIMENSION_INDEX, "Dependency Recheck"), [])
    decision_rows = table_rows.get(("00_PROJECT_ROUTE.md", "Decision Records"), [])
    for row in decision_rows:
        if (
            not row["Decision ID"].startswith("DEC-")
            or row["Origin"] not in ORIGIN
            or row["Resolution"] not in RESOLUTION
        ):
            errors.append("invalid decision record enum or ID")
    valid_changed = (
        material_ids
        | {r["Claim ID"] for r in claim_rows}
        | {r["Decision ID"] for r in decision_rows}
        | set(REQUIRED_DIMENSION_IDS)
    )
    for row in dep_rows:
        if row["Changed record"] not in valid_changed:
            errors.append(
                f"dependency references unknown changed record {row['Changed record']}"
            )
        if row["Affected D IDs / scopes"] != "none":
            for token in row["Affected D IDs / scopes"].split("; "):
                if token not in scope_ids and token not in REQUIRED_DIMENSION_IDS:
                    errors.append(
                        f"dependency references unknown affected scope {token}"
                    )
    blocked_scopes = {
        token
        for row in dep_rows
        if row["Disposition"] in {"stale", "candidate", "blocked"}
        and row["Affected D IDs / scopes"] != "none"
        for token in row["Affected D IDs / scopes"].split("; ")
        if token.startswith("SCOPE-")
    }
    for row in scopes:
        if row["Readiness"] == "writer-ready" and row["Scope ID"] in blocked_scopes:
            errors.append(
                f"writer-ready scope {row['Scope ID']} is affected by stale/candidate/blocked dependency"
            )
    for row in table_rows.get(("03_WRITING_STRUCTURE.md", "Scoped Writing Plan"), []):
        if row["Scope ID"] not in scope_ids:
            errors.append(f"writing plan references unknown scope {row['Scope ID']}")
        if row["Output pointer"] != "none" and not _valid_ref(
            row["Output pointer"], workspace, allow_none=False
        ):
            errors.append("writing plan has invalid output pointer")
    for row in decision_rows:
        if row["Affected scopes"] != "none":
            for token in row["Affected scopes"].split("; "):
                if token not in scope_ids:
                    errors.append(f"decision references unknown scope {token}")
        if row["Grounding"] != "none" and any(
            not _valid_ref(token, workspace, allow_none=False)
            for token in row["Grounding"].split("; ")
        ):
            errors.append("decision has invalid grounding reference")
    handoff_rows = table_rows.get((FINAL_PACK, "Scoped Handoff"), [])
    if handoff_rows:
        authoritative = {r["Scope ID"]: r for r in scopes}
        if {r["Scope ID"] for r in handoff_rows} != set(authoritative):
            errors.append("Scoped Handoff scope IDs must exactly mirror Writing Scopes")
        for row in handoff_rows:
            source = authoritative.get(row["Scope ID"])
            if source is None:
                errors.append(f"handoff references unknown scope {row['Scope ID']}")
            elif any(
                row[key] != source[key]
                for key in ("Readiness", "Remaining blocker", "Next action")
            ):
                errors.append(
                    f"handoff readiness disagrees with authoritative scope {row['Scope ID']}"
                )
    if require_handoff and (
        not scopes or not _table(contents.get(FINAL_PACK, ""), "Scoped Handoff")[1]
    ):
        errors.append(
            "--require-handoff requires Writing Scopes and Scoped Handoff rows"
        )
    for name, text in contents.items():
        if re.search(
            r"(?i)\b(?:claims?|promises?|provides?|ensures?|achieves?|guarantees?)\s+(?:research|manuscript|submission|publication|semantic)\s+readiness\b",
            text,
        ):
            errors.append(f"{name}: forbidden readiness promise")
        if re.search(r"(?i)external skill.{0,40}(?:executed|run|completed)", text):
            errors.append(f"{name}: external execution claim")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Validate sparse yxj-paper-os workspace contract"
    )
    ap.add_argument("workspace", nargs="?", type=Path, default=Path.cwd())
    ap.add_argument("--require-handoff", action="store_true")
    args = ap.parse_args()
    errors = validate_workspace(args.workspace, args.require_handoff)
    if errors:
        print("Design pack validation failed:", file=sys.stderr)
        print("\n".join("- " + e for e in errors), file=sys.stderr)
        return 1
    print(f"Structural design-pack validation passed: {args.workspace}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
