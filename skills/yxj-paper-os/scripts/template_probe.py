#!/usr/bin/env python3
"""Print small, factual cues from Markdown/plain-text template derivatives."""

from __future__ import annotations

import argparse
import re
import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence


TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*|[\u4e00-\u9fff]")
SENTENCE_RE = re.compile(r"[^.!?。！？]+[.!?。！？]?")
MARKDOWN_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
NUMBERED_HEADING_RE = re.compile(r"^(\d+(?:\.\d+)*)[.)]?\s+(.{2,100})$")
# ponytail: numbered plain-text headings are a cue; use Markdown headings when a
# numbered bibliography creates false positives.
COMMON_HEADING_RE = re.compile(
    r"^(abstract|introduction|background|related work|literature review|"
    r"method(?:s|ology)?|system model|problem formulation|experiments?|results?|"
    r"discussion|limitations?|conclusions?|references|appendix)$",
    re.IGNORECASE,
)
CITATION_PATTERNS = (
    re.compile(r"\[(?:\d+[a-z]?(?:\s*[-–,;]\s*\d+[a-z]?)*?)\]"),
    re.compile(r"\\cite\w*\{[^}]+\}"),
    re.compile(r"\([A-Z][A-Za-z'’-]+(?:\s+et\s+al\.)?,?\s+\d{4}[a-z]?\)"),
)
# ponytail: citation markers are cues, not a citation parser; extend only for a
# demonstrated template style that changes a design decision.
OBJECT_PATTERNS = {
    "figure": re.compile(r"\b(?:fig(?:ure)?s?\.?)\s*\d+", re.IGNORECASE),
    "table": re.compile(r"\btables?\s*\d+", re.IGNORECASE),
    "equation": re.compile(r"\b(?:eq(?:uation)?s?\.?)\s*\(?\d+", re.IGNORECASE),
    "algorithm": re.compile(r"\balgorithms?\s*\d+", re.IGNORECASE),
}
CAPTION_RE = re.compile(
    r"^(?:fig(?:ure)?|table|algorithm)\s*\d+\s*[:.\-–]?\s*(.*)$",
    re.IGNORECASE,
)
MARKERS = {
    "first person": re.compile(r"\b(?:we|our|ours|us|i|my|mine)\b", re.IGNORECASE),
    "hedge/modal": re.compile(
        r"\b(?:may|might|could|can|suggests?|appears?|likely|possibly|"
        r"approximately|generally|typically)\b",
        re.IGNORECASE,
    ),
    "transition": re.compile(
        r"\b(?:however|therefore|thus|moreover|nevertheless|consequently|"
        r"in contrast|by contrast|accordingly)\b",
        re.IGNORECASE,
    ),
}
MAX_BYTES = 10 * 1024 * 1024


@dataclass
class Mention:
    kind: str
    line: int
    section: str


@dataclass
class Section:
    title: str
    level: int
    line: int
    lines: list[str] = field(default_factory=list)
    paragraphs: list[str] = field(default_factory=list)


@dataclass
class Document:
    path: Path
    sections: list[Section]
    mentions: list[Mention]
    caption_lengths: list[int]
    table_shapes: list[tuple[int, int]]


def words(text: str) -> list[str]:
    return TOKEN_RE.findall(text)


def count_citations(text: str) -> int:
    return sum(len(pattern.findall(text)) for pattern in CITATION_PATTERNS)


def heading(line: str, *, plain_text: bool) -> tuple[int, str] | None:
    match = MARKDOWN_HEADING_RE.match(line)
    if match:
        return len(match.group(1)), match.group(2).strip()
    if not plain_text:
        return None
    match = NUMBERED_HEADING_RE.match(line)
    if match:
        return match.group(1).count(".") + 1, match.group(2).strip()
    if COMMON_HEADING_RE.match(line.strip()):
        return 1, line.strip()
    return None


def is_table_start(lines: Sequence[str], index: int) -> bool:
    if index + 1 >= len(lines) or "|" not in lines[index]:
        return False
    separator = lines[index + 1].strip().strip("|")
    cells = [cell.strip() for cell in separator.split("|")]
    return len(cells) >= 2 and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def table_shape(lines: Sequence[str]) -> tuple[int, int]:
    rows = [line for line in lines if line.strip()]
    columns = max((len(line.strip().strip("|").split("|")) for line in rows), default=0)
    return max(len(rows) - 2, 0), columns


def parse(path: Path) -> Document:
    if path.suffix.lower() not in {".md", ".markdown", ".txt"}:
        raise ValueError(f"unsupported input type: {path} (use .md or .txt)")
    if path.stat().st_size > MAX_BYTES:
        raise ValueError(f"input exceeds {MAX_BYTES} bytes: {path}")
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    sections = [Section("Front matter", 0, 1)]
    mentions: list[Mention] = []
    caption_lengths: list[int] = []
    table_shapes: list[tuple[int, int]] = []
    current = sections[0]
    paragraph: list[str] = []
    in_fence = False

    def flush_paragraph() -> None:
        if paragraph:
            current.paragraphs.append(" ".join(paragraph))
            paragraph.clear()

    index = 0
    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            flush_paragraph()
            in_fence = not in_fence
            index += 1
            continue
        if in_fence:
            index += 1
            continue

        found_heading = heading(stripped, plain_text=path.suffix.lower() == ".txt")
        if found_heading:
            flush_paragraph()
            current = Section(found_heading[1], found_heading[0], index + 1)
            sections.append(current)
            index += 1
            continue

        if is_table_start(lines, index):
            flush_paragraph()
            table_lines = [raw, lines[index + 1]]
            end = index + 2
            while end < len(lines) and "|" in lines[end] and lines[end].strip():
                table_lines.append(lines[end])
                end += 1
            current.lines.extend(table_lines)
            table_shapes.append(table_shape(table_lines))
            mentions.append(Mention("table", index + 1, current.title))
            index = end
            continue

        current.lines.append(raw)
        for kind, pattern in OBJECT_PATTERNS.items():
            for _ in pattern.finditer(stripped):
                mentions.append(Mention(kind, index + 1, current.title))
        caption = CAPTION_RE.match(stripped)
        if caption:
            caption_lengths.append(len(words(caption.group(1))))

        if stripped:
            paragraph.append(stripped)
        else:
            flush_paragraph()
        index += 1

    flush_paragraph()
    return Document(path, sections, mentions, caption_lengths, table_shapes)


def median(values: Iterable[int]) -> str:
    materialized = list(values)
    if not materialized:
        return "0"
    value = statistics.median(materialized)
    return str(int(value)) if float(value).is_integer() else f"{value:.1f}"


def safe_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render(document: Document) -> str:
    body = "\n".join(line for section in document.sections for line in section.lines)
    paragraphs = [paragraph for section in document.sections for paragraph in section.paragraphs]
    sentences = [
        sentence.strip()
        for paragraph in paragraphs
        for sentence in SENTENCE_RE.findall(paragraph)
        if sentence.strip()
    ]
    output = [
        f"## `{document.path.as_posix()}`",
        "",
        "### Document summary",
        "",
        "| Fact | Value |",
        "|---|---:|",
        f"| Words | {len(words(body))} |",
        f"| Sections/headings | {max(len(document.sections) - 1, 0)} |",
        f"| Paragraphs | {len(paragraphs)} |",
        f"| Median sentence words | {median(len(words(item)) for item in sentences)} |",
        f"| Median paragraph words | {median(len(words(item)) for item in paragraphs)} |",
        f"| Citation markers | {count_citations(body)} |",
        f"| Object mentions | {len(document.mentions)} |",
        f"| Median caption words | {median(document.caption_lengths)} |",
        "",
        "### Section sequence",
        "",
        "| # | Level | Section | Words | Paragraphs | Citations | Figure | Table | Equation | Algorithm |",
        "|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    visible_sections = [
        section
        for section in document.sections
        if section.title != "Front matter" or any(line.strip() for line in section.lines)
    ]
    for number, section in enumerate(visible_sections, 1):
        text = "\n".join(section.lines)
        counts = {
            kind: sum(1 for item in document.mentions if item.section == section.title and item.kind == kind)
            for kind in OBJECT_PATTERNS
        }
        output.append(
            "| "
            + " | ".join(
                map(
                    safe_cell,
                    (
                        number,
                        section.level,
                        section.title,
                        len(words(text)),
                        len(section.paragraphs),
                        count_citations(text),
                        counts["figure"],
                        counts["table"],
                        counts["equation"],
                        counts["algorithm"],
                    ),
                )
            )
            + " |"
        )

    output.extend(["", "### Object order", ""])
    if document.mentions:
        for number, item in enumerate(document.mentions, 1):
            output.append(f"{number}. {item.kind} — line {item.line} — {item.section}")
    else:
        output.append("None detected.")

    output.extend(["", "### Language markers", "", "| Marker | Count |", "|---|---:|"])
    for label, pattern in MARKERS.items():
        output.append(f"| {label} | {len(pattern.findall(body))} |")

    output.extend(["", "### Recognized table shapes", ""])
    output.append(
        ", ".join(f"{rows} data row(s) × {columns} column(s)" for rows, columns in document.table_shapes)
        if document.table_shapes
        else "None detected."
    )
    return "\n".join(output)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Print factual writing cues from local Markdown/plain-text template derivatives."
    )
    parser.add_argument("paths", nargs="+", type=Path, help="one or more .md/.txt files")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    reports: list[str] = []
    for path in args.paths:
        try:
            reports.append(render(parse(path.resolve())))
        except (OSError, UnicodeError, ValueError) as error:
            print(f"template_probe: {error}", file=sys.stderr)
            return 2
    print("# Template probe\n\n> Factual cues only; interpret them against the science and selected exemplar role.\n")
    print("\n\n".join(reports))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
