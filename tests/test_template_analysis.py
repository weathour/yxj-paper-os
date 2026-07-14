from __future__ import annotations

import hashlib
import html
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "yxj-paper-os"
SCRIPT = SKILL_ROOT / "scripts" / "analyze_template_corpus.py"
FIXTURES = SKILL_ROOT / "assets" / "fixtures" / "template-analysis"
PUBLIC_TEMPLATE_DIR = SKILL_ROOT / "assets" / "templates"

OUTPUT_NAMES = {
    "manifest.json",
    "metric-registry.json",
    "paper-metrics.jsonl",
    "objects.jsonl",
    "corpus-summary.json",
    "design-profile.json",
    "extraction-warnings.json",
    "analysis-report.html",
}
PUBLIC_NAMES = {
    "00_DIMENSION_INDEX.md",
    "00_PROJECT_ROUTE.md",
    "01_MATERIALS_INVENTORY.md",
    "02_CLAIM_EVIDENCE_BOUNDARY.md",
    "03_WRITING_STRUCTURE.md",
    "04_WRITING_DESIGN_PACK.md",
}
DEFAULT_DESIGN_METRIC_IDS = [
    "text.body_words",
    "structure.paragraph_count",
    "structure.section_count",
    "object.figure_count",
    "object.table_count",
    "object.equation_count",
    "object.algorithm_count",
    "citation.explicit_rate_per_kword",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise AssertionError(f"{path}:{line_number} is not a JSON object")
        rows.append(value)
    return rows


def nested_values(value: Any, key: str) -> list[Any]:
    found: list[Any] = []
    if isinstance(value, dict):
        for current_key, current_value in value.items():
            if current_key == key:
                found.append(current_value)
            found.extend(nested_values(current_value, key))
    elif isinstance(value, list):
        for item in value:
            found.extend(nested_values(item, key))
    return found


def metric_value(row: dict[str, Any], *metric_ids: str) -> Any:
    """Read either canonical metric dictionaries or metric-record arrays."""
    metrics = row.get("metrics", row)
    if isinstance(metrics, dict):
        for metric_id in metric_ids:
            if metric_id in metrics:
                value = metrics[metric_id]
                if isinstance(value, dict) and "value" in value:
                    return value["value"]
                return value
    if isinstance(metrics, list):
        for item in metrics:
            if not isinstance(item, dict):
                continue
            if item.get("metric_id") in metric_ids or item.get("id") in metric_ids:
                return item.get("value")
    raise AssertionError(
        f"none of {metric_ids!r} are present in paper metric row {row!r}"
    )


def metric_entry(row: dict[str, Any], *metric_ids: str) -> dict[str, Any]:
    metrics = row.get("metrics")
    if isinstance(metrics, dict):
        for metric_id in metric_ids:
            value = metrics.get(metric_id)
            if isinstance(value, dict):
                return value
    if isinstance(metrics, list):
        for item in metrics:
            if not isinstance(item, dict):
                continue
            if item.get("metric_id") in metric_ids or item.get("id") in metric_ids:
                return item
    raise AssertionError(f"none of {metric_ids!r} have a metric entry in {row!r}")


class CorpusWorkspace:
    def __init__(self) -> None:
        self._temp = tempfile.TemporaryDirectory(prefix="yxj-template-analysis-")
        self.root = Path(self._temp.name)
        self.corpus_dir = self.root / "corpus"
        self.corpus_dir.mkdir()
        for fixture in FIXTURES.iterdir():
            if fixture.is_file():
                shutil.copy2(fixture, self.corpus_dir / fixture.name)
        for name in PUBLIC_NAMES:
            shutil.copy2(PUBLIC_TEMPLATE_DIR / name, self.root / name)
        self.manifest = self.root / "corpus.json"
        self.output = self.root / ".yxj-paper-os" / "template-analysis"

    def close(self) -> None:
        self._temp.cleanup()

    def write_manifest(
        self,
        documents: list[dict[str, Any]],
        *,
        official_constraints: list[dict[str, Any]] | None = None,
        corpus_id: str = "fixture-corpus",
        analysis_mode: str = "case_set",
        design_question: str = "Which extracted writing-design surfaces are structurally measurable in this fixture corpus?",
        design_metric_ids: list[str] | None = None,
    ) -> Path:
        payload: dict[str, Any] = {
            "schema": "template-corpus/1.0",
            "corpus_id": corpus_id,
            "analysis_mode": analysis_mode,
            "design_question": design_question,
            "design_metric_ids": design_metric_ids or DEFAULT_DESIGN_METRIC_IDS,
            "documents": documents,
        }
        if official_constraints is not None:
            payload["official_constraints"] = official_constraints
        self.manifest.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return self.manifest

    @staticmethod
    def document(
        doc_id: str,
        filename: str,
        source_format: str,
        *,
        annotations: str | None = None,
        language: str = "en",
    ) -> dict[str, Any]:
        document: dict[str, Any] = {
            "doc_id": doc_id,
            "path": f"corpus/{filename}",
            "format": source_format,
            "partition": "primary_match",
            "venue": "Fixture Journal",
            "topic_tags": ["transport", "artificial-intelligence"],
            "article_type": "research-article",
            "year": 2026,
            "language": language,
        }
        if annotations is not None:
            document["annotations"] = f"corpus/{annotations}"
        return document


class TemplateAnalysisTests(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        if not SCRIPT.is_file():
            raise unittest.SkipTest(
                f"template analysis engine is not present: {SCRIPT}"
            )

    def setUp(self) -> None:
        self.workspace = CorpusWorkspace()

    def tearDown(self) -> None:
        self.workspace.close()

    def run_engine(
        self,
        *,
        positional: bool = False,
        output_flag: str | None = None,
        output_path: Path | None = None,
        expect_success: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, str(SCRIPT)]
        if positional:
            command.append(str(self.workspace.manifest))
        else:
            command.extend(["--manifest", str(self.workspace.manifest)])
        if output_flag is not None:
            self.assertIsNotNone(output_path)
            command.extend([output_flag, str(output_path)])
        result = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if expect_success and result.returncode != 0:
            self.fail(
                f"template analysis failed ({result.returncode})\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )
        if not expect_success and result.returncode == 0:
            self.fail(f"template analysis unexpectedly succeeded\n{result.stdout}")
        return result

    def assert_fixed_outputs(self) -> None:
        self.assertTrue(self.workspace.output.is_dir())
        present = {
            path.name for path in self.workspace.output.iterdir() if path.is_file()
        }
        self.assertTrue(OUTPUT_NAMES <= present, OUTPUT_NAMES - present)

    def test_markdown_html_and_jats_extract_objects_callouts_and_sequences(
        self,
    ) -> None:
        documents = [
            self.workspace.document("md-rich", "article.md", "markdown"),
            self.workspace.document("html-rich", "article.html", "html"),
            self.workspace.document("jats-rich", "article.xml", "jats"),
        ]
        self.workspace.write_manifest(documents)
        self.run_engine(positional=True)
        self.assert_fixed_outputs()

        normalized_manifest = read_json(self.workspace.output / "manifest.json")
        normalized_docs = normalized_manifest["documents"]
        self.assertEqual(
            {item["doc_id"] for item in normalized_docs},
            {"md-rich", "html-rich", "jats-rich"},
        )
        self.assertEqual(
            {item["partition"] for item in normalized_docs},
            {"primary_match"},
        )

        objects = read_jsonl(self.workspace.output / "objects.jsonl")
        self.assertEqual(len({item["object_id"] for item in objects}), len(objects))
        expected_types = {"figure", "table", "equation", "algorithm"}
        for doc_id in ("md-rich", "html-rich", "jats-rich"):
            doc_objects = [item for item in objects if item["doc_id"] == doc_id]
            self.assertEqual(
                {item["object_type"] for item in doc_objects},
                expected_types,
                doc_id,
            )
            self.assertEqual(len(doc_objects), 4, doc_id)
            ordered = sorted(
                doc_objects,
                key=lambda item: (
                    item["position"]["source_block_index"],
                    item["position"].get("source_char_start", 0),
                    item["object_id"],
                ),
            )
            self.assertEqual(
                [item["object_type"] for item in ordered],
                ["figure", "equation", "algorithm", "table"],
            )
            for item in doc_objects:
                self.assertTrue(item["callouts"], item["object_id"])
                self.assertGreaterEqual(item["position"]["normalized_word_position"], 0)
                self.assertLessEqual(item["position"]["normalized_word_position"], 1)

        summary = read_json(self.workspace.output / "corpus-summary.json")
        serialized = json.dumps(summary, ensure_ascii=False)
        self.assertIn("sequences", summary)
        self.assertIn("transitions", summary)
        self.assertIn("lead_lag", summary)
        self.assertNotIn("Fig. 99", serialized)
        self.assertNotIn("Table 99", serialized)

        def assert_transition_invariant(sequence_summary: dict[str, Any]) -> None:
            transitions = sequence_summary["transitions"]
            independently_expected = sum(
                max(len(item["sequence"]) - 1, 0)
                for item in sequence_summary["document_sequences"]
            )
            observed_from_edges = sum(
                edge["raw_count"] for edge in transitions["edges"]
            )
            self.assertEqual(transitions["expected_total"], independently_expected)
            self.assertEqual(transitions["observed_total"], observed_from_edges)
            self.assertEqual(independently_expected, observed_from_edges)
            self.assertTrue(transitions["invariant_holds"])

        overall_sequence = summary["groups"]["overall"]["object_sequence"]
        assert_transition_invariant(overall_sequence)
        self.assertEqual(summary["transitions"], overall_sequence["transitions"])
        for grouping in (
            "by_partition",
            "by_article_type",
            "by_partition_article_type",
        ):
            for group in summary["groups"][grouping]:
                assert_transition_invariant(group["object_sequence"])

        paper_rows = read_jsonl(self.workspace.output / "paper-metrics.jsonl")
        self.assertEqual(len(paper_rows), 3)
        for row in paper_rows:
            self.assertTrue(
                {
                    "schema",
                    "doc_id",
                    "partition",
                    "status",
                    "source",
                    "parse",
                    "metrics",
                    "entities",
                }
                <= row.keys()
            )
            self.assertEqual(row["partition"], "primary_match")
            self.assertIn("sections", row["entities"])
            self.assertIn("paragraphs", row["entities"])

    def test_html_abstract_and_presentation_regions_do_not_shift_body_objects(
        self,
    ) -> None:
        source = self.workspace.corpus_dir / "html-boundaries.html"
        source.write_text(
            """<!doctype html><html><head><title>Boundary title</title></head><body>
<article><section class="abstract"><h2>Abstract</h2><p>Abstract words stay outside the body.</p></section>
<table role="presentation"><tr><td>layout only</td></tr></table>
<h1>Results</h1><p>See <a href="#fig-1">Fig. 1</a>.</p>
<figure id="fig-1"><img src="x.svg" /><figcaption>Figure 1. Result.</figcaption></figure>
</article><footer><figure id="footer-fig"><img src="x.svg"></figure></footer></body></html>""",
            encoding="utf-8",
        )
        self.workspace.write_manifest(
            [self.workspace.document("html-boundaries", source.name, "html")]
        )
        self.run_engine()
        objects = read_jsonl(self.workspace.output / "objects.jsonl")
        self.assertEqual(
            [item["object_id"] for item in objects], ["html-boundaries#fig-1"]
        )
        self.assertTrue(objects[0]["callouts"])
        row = read_jsonl(self.workspace.output / "paper-metrics.jsonl")[0]
        self.assertGreater(metric_value(row, "front.abstract_words"), 0)
        self.assertEqual(metric_value(row, "front.title_words"), 2)

    def test_metric_registry_is_versioned_unique_and_design_bounded(self) -> None:
        self.workspace.write_manifest(
            [self.workspace.document("md-rich", "article.md", "markdown")]
        )
        self.run_engine()
        registry = read_json(self.workspace.output / "metric-registry.json")
        self.assertIn("schema", registry)
        self.assertIn("version", registry)
        self.assertIn("tokenizer", registry)
        self.assertIn("normalization", registry)
        self.assertIsInstance(registry["tokenizer"], dict)
        self.assertIsInstance(registry["normalization"], dict)

        metrics = registry["metrics"]
        self.assertIsInstance(metrics, list)
        self.assertTrue(metrics)
        metric_ids = [item["metric_id"] for item in metrics]
        self.assertEqual(len(metric_ids), len(set(metric_ids)))

        required_fields = {
            "priority",
            "extraction_mode",
            "entity",
            "value_type",
            "unit",
            "eligibility",
            "supported_formats",
            "missing_statuses",
            "aggregation",
            "design_surfaces",
            "definition",
        }
        for item in metrics:
            self.assertTrue(required_fields <= item.keys(), item["metric_id"])
            self.assertIn(item["priority"], {"P0", "P1"})
            self.assertTrue(item["supported_formats"])
            self.assertTrue(item["missing_statuses"])
            self.assertTrue(item["design_surfaces"])

        registry_ids = "\n".join(metric_ids).lower().replace("-", "_").replace(".", "_")
        for required_family in (
            "figure",
            "table",
            "equation",
            "algorithm",
            "caption",
            "callout",
            "sequence",
            "transition",
            "lead_lag",
        ):
            self.assertIn(required_family, registry_ids)

        for item in metrics:
            metric_id = item["metric_id"].lower().replace("-", "_")
            unit = str(item["unit"]).lower()
            if (
                "density" in metric_id
                or "per_" in metric_id
                or unit.startswith("per_")
                or "per 1000" in unit
                or "/1000" in unit
            ):
                self.assertIn("numerator", item, item["metric_id"])
                self.assertIn("denominator", item, item["metric_id"])
                self.assertTrue(item["numerator"])
                self.assertTrue(item["denominator"])

        forbidden_score_ids = {
            "quality_score",
            "novelty_score",
            "acceptance_score",
            "venue_fit_score",
            "venuefit_score",
        }
        for metric_id in metric_ids:
            normalized = metric_id.lower().replace("-", "_").replace(".", "_")
            self.assertFalse(
                any(forbidden in normalized for forbidden in forbidden_score_ids),
                metric_id,
            )
        paper_rows = read_jsonl(self.workspace.output / "paper-metrics.jsonl")
        self.assertEqual(set(paper_rows[0]["metrics"]), set(metric_ids))

        manifest_schema = read_json(
            SKILL_ROOT / "assets" / "template-analysis" / "manifest.schema.json"
        )
        annotation_schema = read_json(
            SKILL_ROOT / "assets" / "template-analysis" / "annotations.schema.json"
        )
        self.assertEqual(
            manifest_schema["properties"]["schema"]["const"],
            "template-corpus/1.0",
        )
        self.assertEqual(
            annotation_schema["properties"]["schema"]["const"],
            "template-annotations/1.0",
        )

    def test_zero_counts_missing_caption_limited_txt_and_unicode_status(self) -> None:
        documents = [
            self.workspace.document("zero", "zero-objects.md", "markdown"),
            self.workspace.document("uncaptioned", "missing-caption.md", "markdown"),
            self.workspace.document("plain-text", "article.txt", "txt"),
            self.workspace.document("chinese", "chinese.md", "markdown", language="zh"),
        ]
        self.workspace.write_manifest(documents)
        self.run_engine()
        self.assert_fixed_outputs()

        objects = read_jsonl(self.workspace.output / "objects.jsonl")
        self.assertFalse([item for item in objects if item["doc_id"] == "zero"])
        uncaptioned = [item for item in objects if item["doc_id"] == "uncaptioned"]
        self.assertEqual(len(uncaptioned), 1)
        self.assertEqual(uncaptioned[0]["object_type"], "figure")
        self.assertFalse(uncaptioned[0]["caption"]["present"])
        self.assertEqual(uncaptioned[0]["callouts"], [])

        papers = {
            item["doc_id"]: item
            for item in read_jsonl(self.workspace.output / "paper-metrics.jsonl")
        }
        self.assertEqual(metric_value(papers["zero"], "object.figure_count"), 0)
        self.assertEqual(metric_value(papers["zero"], "object.table_count"), 0)
        for metric_ids in (
            ("object.figure_count",),
            ("object.table_count",),
        ):
            zero_metric = metric_entry(papers["zero"], *metric_ids)
            self.assertEqual(zero_metric["value"], 0)
            self.assertNotIn(
                zero_metric["status"],
                {"missing", "unsupported_format", "not_applicable"},
            )
        for metric_id in (
            "algorithm.marker_count",
            "caption.figure_panel_label_count_proxy",
            "caption.figure_uncertainty_marker_count",
            "caption.table_uncertainty_marker_count",
        ):
            self.assertEqual(
                metric_entry(papers["zero"], metric_id)["status"], "not_present"
            )
        self.assertEqual(
            metric_entry(papers["uncaptioned"], "caption.figure_sentence_proxy_count")[
                "status"
            ],
            "not_present",
        )
        self.assertGreater(
            metric_value(
                papers["chinese"],
                "text.body_words",
            ),
            1,
        )
        for lexical_metric in (
            "lexical.hedge_rate_per_kword",
            "lexical.mattr50",
        ):
            entry = metric_entry(papers["chinese"], lexical_metric)
            self.assertEqual(entry["status"], "unsupported_language")
            self.assertIsNone(entry["value"])
        self.assertGreater(
            metric_value(
                papers["plain-text"],
                "text.body_words",
            ),
            1,
        )
        plain_text_serialized = json.dumps(papers["plain-text"], ensure_ascii=False)
        self.assertTrue(
            "unsupported_format" in plain_text_serialized
            or "not_applicable" in plain_text_serialized
        )
        self.assertNotEqual(papers["plain-text"].get("status"), "parse_failed")
        for metric_id in (
            "sequence.section_order_proxy",
            "transition.section_pair_count_proxy",
        ):
            self.assertEqual(
                metric_entry(papers["plain-text"], metric_id)["status"],
                "unsupported_format",
            )
        for metric_ids in (
            ("object.figure_count",),
            ("object.table_count",),
            ("object.equation_count",),
            ("object.algorithm_count",),
        ):
            self.assertIn(
                metric_entry(papers["plain-text"], *metric_ids)["status"],
                {"unsupported_format", "not_applicable"},
            )
        summary = read_json(self.workspace.output / "corpus-summary.json")
        missingness_values = [
            value
            for value in nested_values(summary, "missingness")
            if isinstance(value, (int, float)) and not isinstance(value, bool)
        ]
        self.assertTrue(missingness_values)
        self.assertTrue(any(value > 0 for value in missingness_values))

    def test_txt_exact_bibliography_inventory_and_layout_are_independent(self) -> None:
        source = self.workspace.corpus_dir / "exact-bibliography.txt"
        overlong_target = "9" * 5000
        source.write_text(
            f"""1 Introduction
Evidence [1,2-3] is explicit; mixed targets [1,99] are rejected.
The overlong target [{overlong_target}] is also rejected atomically.

2 Method
The method follows [2].

3 Results
Results contain no citation group.

References
[1] First reference entry.
[2] Second reference entry.
[3] Third reference entry.
""",
            encoding="utf-8",
        )
        self.workspace.write_manifest(
            [self.workspace.document("exact-bibliography", source.name, "txt")],
            design_metric_ids=["reference.entry_count"],
        )
        self.run_engine()
        first = {
            name: (self.workspace.output / name).read_bytes() for name in OUTPUT_NAMES
        }
        self.run_engine(output_flag="--output-dir", output_path=self.workspace.output)
        self.assertEqual(
            first,
            {name: (self.workspace.output / name).read_bytes() for name in OUTPUT_NAMES},
        )
        self.assertEqual(
            {path.name for path in self.workspace.output.iterdir() if path.is_file()},
            OUTPUT_NAMES,
        )

        row = read_jsonl(self.workspace.output / "paper-metrics.jsonl")[0]
        bibliography = row["entities"]["bibliography"]
        self.assertEqual(row["status"], "ok")
        self.assertEqual(bibliography["inventory"]["status"], "ok")
        self.assertEqual(bibliography["layout"]["status"], "ok")
        self.assertEqual(
            bibliography["inventory"]["entries"],
            [
                {"number": 1, "raw_text": "First reference entry."},
                {"number": 2, "raw_text": "Second reference entry."},
                {"number": 3, "raw_text": "Third reference entry."},
            ],
        )
        observations = {
            item["canonical_section"]: item
            for item in bibliography["layout"]["observations"]
        }
        self.assertEqual(observations["introduction"]["citation_event_count"], 3)
        self.assertEqual(observations["introduction"]["unique_targets"], [1, 2, 3])
        self.assertEqual(observations["methods"]["citation_event_count"], 1)
        self.assertEqual(observations["results"]["citation_event_count"], 0)
        self.assertEqual(len(bibliography["layout"]["invalid_groups"]), 2)
        self.assertEqual(metric_value(row, "reference.entry_count"), 3)
        self.assertEqual(metric_value(row, "citation.explicit_event_count"), 4)
        self.assertEqual(metric_value(row, "citation.unique_target_count"), 3)
        entity_keys = set(nested_values(bibliography, "year"))
        self.assertFalse(entity_keys)
        serialized = json.dumps(bibliography, sort_keys=True)
        for excluded in ("source_form", "citation_function", "doi", "shared_work"):
            self.assertNotIn(excluded, serialized.lower())
        profile = read_json(self.workspace.output / "design-profile.json")
        self.assertTrue(
            any(item.get("metric_ids") == ["reference.entry_count"] for item in profile["entries"])
        )

        unsupported = self.workspace.corpus_dir / "unsupported-layout.txt"
        unsupported.write_text(
            "Body prose without an explicit numbered section.\n\nReferences\n[1] Only entry.\n",
            encoding="utf-8",
        )
        self.workspace.write_manifest(
            [self.workspace.document("unsupported-layout", unsupported.name, "txt")],
            design_metric_ids=["text.body_words"],
        )
        self.run_engine()
        row = read_jsonl(self.workspace.output / "paper-metrics.jsonl")[0]
        bibliography = row["entities"]["bibliography"]
        self.assertEqual(bibliography["inventory"]["status"], "ok")
        self.assertEqual(bibliography["layout"]["status"], "unsupported_format")
        self.assertEqual(metric_value(row, "reference.entry_count"), 1)
        self.assertIsNone(metric_value(row, "citation.explicit_event_count"))
        self.assertEqual(
            metric_entry(row, "citation.explicit_event_count")["status"],
            "unsupported_format",
        )
        profile = read_json(self.workspace.output / "design-profile.json")
        self.assertFalse(
            any(
                metric_id.startswith(("reference.", "citation."))
                for item in profile["entries"]
                for metric_id in item.get("metric_ids", [])
            )
        )

        conflicting = self.workspace.corpus_dir / "conflicting-layout.txt"
        conflicting.write_text(
            "1 Introduction\nFirst body [1].\n\n2 Introduction\nSecond body [1].\n\nReferences\n[1] Entry.\n",
            encoding="utf-8",
        )
        self.workspace.write_manifest(
            [self.workspace.document("conflicting-layout", conflicting.name, "txt")]
        )
        self.run_engine()
        row = read_jsonl(self.workspace.output / "paper-metrics.jsonl")[0]
        self.assertEqual(row["entities"]["bibliography"]["inventory"]["status"], "ok")
        self.assertEqual(row["entities"]["bibliography"]["layout"]["status"], "ambiguous")

        ambiguous = self.workspace.corpus_dir / "ambiguous-references.txt"
        ambiguous.write_text(
            "1 Introduction\nBody [1].\n\nReferences\n[1] First.\n[3] Third.\n",
            encoding="utf-8",
        )
        self.workspace.write_manifest(
            [self.workspace.document("ambiguous-references", ambiguous.name, "txt")]
        )
        self.run_engine()
        row = read_jsonl(self.workspace.output / "paper-metrics.jsonl")[0]
        self.assertEqual(row["entities"]["bibliography"]["inventory"]["status"], "ambiguous")
        self.assertEqual(metric_entry(row, "reference.entry_count")["status"], "ambiguous")
        self.assertIsNone(metric_value(row, "reference.entry_count"))
        self.assertNotEqual(row["entities"]["bibliography"]["layout"]["status"], "ok")

        two_column = self.workspace.corpus_dir / "two-column-references.txt"
        two_column.write_text(
            "1 Introduction\nBody [1].\n\n[3] Third entry.\n[4] Fourth entry.\n[5] Fifth entry.\nReferences\n[1] First entry.\n[2] Second entry.\n",
            encoding="utf-8",
        )
        self.workspace.write_manifest(
            [self.workspace.document("two-column-references", two_column.name, "txt")]
        )
        self.run_engine()
        row = read_jsonl(self.workspace.output / "paper-metrics.jsonl")[0]
        inventory = row["entities"]["bibliography"]["inventory"]
        self.assertEqual([entry["number"] for entry in inventory["entries"]], [1, 2, 3, 4, 5])
        self.assertEqual(metric_value(row, "reference.entry_count"), 5)
        self.assertEqual(metric_value(row, "citation.explicit_event_count"), 1)

        self.workspace.write_manifest(
            [self.workspace.document("invalid-source", "invalid-utf8.md", "markdown")]
        )
        self.run_engine(expect_success=False)
        row = read_jsonl(self.workspace.output / "paper-metrics.jsonl")[0]
        bibliography = row["entities"]["bibliography"]
        for entity_name, array_names in (
            ("inventory", ("entries", "diagnostics")),
            ("layout", ("observations", "invalid_groups")),
        ):
            self.assertEqual(bibliography[entity_name]["status"], "parse_failed")
            self.assertEqual(bibliography[entity_name]["method"], "not_computed")
            for array_name in array_names:
                self.assertEqual(bibliography[entity_name][array_name], [])

        self.workspace.write_manifest(
            [self.workspace.document("markdown-regression", "article.md", "markdown")]
        )
        self.run_engine()
        row = read_jsonl(self.workspace.output / "paper-metrics.jsonl")[0]
        self.assertEqual(row["entities"]["bibliography"]["inventory"]["status"], "unsupported_format")
        self.assertEqual(row["entities"]["bibliography"]["layout"]["status"], "unsupported_format")

    def test_accepted_candidate_and_stale_annotations_remain_distinct(self) -> None:
        annotation_fixture = read_json(self.workspace.corpus_dir / "annotations.json")
        accepted_figure = annotation_fixture["annotations"][0]
        self.assertEqual(
            accepted_figure["source_sha256"],
            sha256(self.workspace.corpus_dir / "article.md"),
        )
        documents = [
            self.workspace.document(
                "md-rich", "article.md", "markdown", annotations="annotations.json"
            )
        ]
        self.workspace.write_manifest(documents)
        self.run_engine()

        objects = {
            item["object_id"]: item
            for item in read_jsonl(self.workspace.output / "objects.jsonl")
        }
        figure = objects["md-rich#fig-1"]
        self.assertEqual(figure["annotation"]["resolution"], "accepted")
        self.assertEqual(figure["annotation"]["role"]["primary"], "architecture")
        self.assertEqual(len(figure["annotation"]["panels"]), 2)

        table = objects["md-rich#table-1"]
        if table.get("annotation") is not None:
            self.assertEqual(table["annotation"]["resolution"], "candidate")

        equation = objects["md-rich#eq-1"]
        self.assertIsNone(equation.get("annotation"))

        summary = read_json(self.workspace.output / "corpus-summary.json")
        summary_text = json.dumps(summary, ensure_ascii=False).lower()
        self.assertIn("accepted", summary_text)
        self.assertIn("candidate", summary_text)
        self.assertIn("stale", summary_text)
        self.assertIn("architecture", summary_text)

        warnings_text = json.dumps(
            read_json(self.workspace.output / "extraction-warnings.json"),
            ensure_ascii=False,
        ).lower()
        self.assertIn("stale", warnings_text)
        self.assertIn("eq-1", warnings_text)

    def test_repeat_run_is_byte_identical_and_inputs_are_immutable(self) -> None:
        documents = [self.workspace.document("md-rich", "article.md", "markdown")]
        self.workspace.write_manifest(documents)
        source_paths = [
            self.workspace.corpus_dir / "article.md",
            self.workspace.manifest,
        ]
        public_paths = [self.workspace.root / name for name in PUBLIC_NAMES]
        before_inputs = {path: sha256(path) for path in source_paths + public_paths}

        self.workspace.output.mkdir(parents=True)
        sentinel = self.workspace.output / "unknown-operator-note.txt"
        sentinel.write_text("preserve me\n", encoding="utf-8")
        self.run_engine()
        first = {
            name: (self.workspace.output / name).read_bytes() for name in OUTPUT_NAMES
        }
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "preserve me\n")

        self.run_engine(output_flag="--output-dir", output_path=self.workspace.output)
        second = {
            name: (self.workspace.output / name).read_bytes() for name in OUTPUT_NAMES
        }
        self.assertEqual(first, second)
        self.assertEqual(
            before_inputs,
            {path: sha256(path) for path in source_paths + public_paths},
        )
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "preserve me\n")

    def test_source_and_output_path_containment(self) -> None:
        outside = self.workspace.root.parent / f"{self.workspace.root.name}-outside.md"
        outside.write_text("# Outside\n\n![Do not read](x.svg)\n", encoding="utf-8")
        self.addCleanup(lambda: outside.unlink(missing_ok=True))
        before = sha256(outside)

        bad_document = self.workspace.document("escape", "article.md", "markdown")
        bad_document["path"] = f"../{outside.name}"
        self.workspace.write_manifest([bad_document])
        self.run_engine(expect_success=False)
        self.assertEqual(sha256(outside), before)
        self.assertFalse(self.workspace.output.exists())

        self.workspace.write_manifest(
            [self.workspace.document("md-rich", "article.md", "markdown")]
        )
        invalid_output = self.workspace.root / "not-the-hidden-output"
        self.run_engine(
            output_flag="--output", output_path=invalid_output, expect_success=False
        )
        self.assertFalse(invalid_output.exists())

        outside_output = (
            self.workspace.root.parent / f"{self.workspace.root.name}-output"
        )
        self.addCleanup(lambda: shutil.rmtree(outside_output, ignore_errors=True))
        self.run_engine(
            output_flag="--output", output_path=outside_output, expect_success=False
        )
        self.assertFalse(outside_output.exists())

    def test_manifest_rejects_duplicate_ids_invalid_partitions_and_supplements(
        self,
    ) -> None:
        first = self.workspace.document("duplicate", "article.md", "markdown")
        second = self.workspace.document("duplicate", "zero-objects.md", "markdown")
        self.workspace.write_manifest([first, second])
        self.run_engine(expect_success=False)
        self.assertFalse(self.workspace.output.exists())

        self.workspace.write_manifest(
            [self.workspace.document("unknown-metric", "article.md", "markdown")],
            design_metric_ids=["quality_score"],
        )
        self.run_engine(expect_success=False)
        self.assertFalse(self.workspace.output.exists())

        duplicate_source_a = self.workspace.document(
            "source-a", "article.md", "markdown"
        )
        duplicate_source_b = self.workspace.document(
            "source-b", "article.md", "markdown"
        )
        self.workspace.write_manifest([duplicate_source_a, duplicate_source_b])
        self.run_engine(expect_success=False)
        self.assertFalse(self.workspace.output.exists())

        invalid_partition = self.workspace.document(
            "invalid-partition", "article.md", "markdown"
        )
        invalid_partition["partition"] = "target-journal-target-topic"
        self.workspace.write_manifest([invalid_partition])
        self.run_engine(expect_success=False)
        self.assertFalse(self.workspace.output.exists())

        invalid_supplement = self.workspace.document(
            "supplement", "article.md", "markdown"
        )
        invalid_supplement["supplement_of"] = "missing-main"
        self.workspace.write_manifest([invalid_supplement])
        self.run_engine(expect_success=False)
        self.assertFalse(self.workspace.output.exists())

        invalid_exception = self.workspace.document(
            "invalid-exception", "article.md", "markdown"
        )
        invalid_exception["inclusion_exception"] = "owner-approved"
        self.workspace.write_manifest([invalid_exception])
        self.run_engine(expect_success=False)
        self.assertFalse(self.workspace.output.exists())

        self.workspace.write_manifest(
            [self.workspace.document("missing-question", "article.md", "markdown")]
        )
        payload = read_json(self.workspace.manifest)
        del payload["design_question"]
        self.workspace.manifest.write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8"
        )
        self.run_engine(expect_success=False)
        self.assertFalse(self.workspace.output.exists())

        self.workspace.write_manifest(
            [self.workspace.document("missing-metrics", "article.md", "markdown")]
        )
        payload = read_json(self.workspace.manifest)
        del payload["design_metric_ids"]
        self.workspace.manifest.write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8"
        )
        self.run_engine(expect_success=False)
        self.assertFalse(self.workspace.output.exists())

    def test_symlink_escape_is_rejected(self) -> None:
        outside = self.workspace.root.parent / f"{self.workspace.root.name}-target.md"
        outside.write_text("# Escaped source\n", encoding="utf-8")
        self.addCleanup(lambda: outside.unlink(missing_ok=True))
        link = self.workspace.corpus_dir / "linked.md"
        try:
            link.symlink_to(outside)
        except OSError as error:
            self.skipTest(f"symlinks unavailable: {error}")

        self.workspace.write_manifest(
            [self.workspace.document("symlink", "linked.md", "markdown")]
        )
        self.run_engine(expect_success=False)

    def test_hidden_output_root_symlink_escape_is_rejected(self) -> None:
        outside = self.workspace.root.parent / f"{self.workspace.root.name}-hidden"
        outside.mkdir()
        self.addCleanup(lambda: shutil.rmtree(outside, ignore_errors=True))
        cache_link = self.workspace.root / ".yxj-paper-os"
        try:
            cache_link.symlink_to(outside, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"symlinks unavailable: {error}")
        self.workspace.write_manifest(
            [self.workspace.document("md-rich", "article.md", "markdown")]
        )
        self.run_engine(expect_success=False)
        self.assertFalse((outside / "template-analysis").exists())

    def test_pdf_magic_is_rejected_even_when_declared_markdown(self) -> None:
        self.workspace.write_manifest(
            [self.workspace.document("fake-pdf", "fake.pdf", "markdown")]
        )
        self.run_engine(expect_success=False)
        self.assertFalse((self.workspace.output / "objects.jsonl").exists())

    def test_annotation_and_official_constraint_paths_are_contained(self) -> None:
        outside_annotations = (
            self.workspace.root.parent / f"{self.workspace.root.name}-annotations.json"
        )
        outside_annotations.write_text(
            '{"schema":"template-annotations/1.0","annotations":[]}\n',
            encoding="utf-8",
        )
        outside_guidance = (
            self.workspace.root.parent / f"{self.workspace.root.name}-guidance.txt"
        )
        outside_guidance.write_text("External constraint.\n", encoding="utf-8")
        self.addCleanup(lambda: outside_annotations.unlink(missing_ok=True))
        self.addCleanup(lambda: outside_guidance.unlink(missing_ok=True))

        document = self.workspace.document("md-rich", "article.md", "markdown")
        document["annotations"] = f"../{outside_annotations.name}"
        self.workspace.write_manifest([document])
        self.run_engine(expect_success=False)
        self.assertFalse(self.workspace.output.exists())

        document.pop("annotations")
        constraints = [
            {
                "constraint_id": "escaped-source",
                "source_path": f"../{outside_guidance.name}",
                "locator": "line:1",
                "statement": "External constraint.",
                "design_surface": "figure-caption",
                "affected_dimensions": ["D18"],
                "affected_scopes": ["SCOPE-RESULTS"],
            }
        ]
        self.workspace.write_manifest([document], official_constraints=constraints)
        self.run_engine(expect_success=False)
        self.assertFalse(self.workspace.output.exists())

    def test_all_parse_failed_documents_fail_but_mixed_corpus_continues(self) -> None:
        self.workspace.write_manifest(
            [
                self.workspace.document("malformed-jats", "malformed.xml", "jats"),
                self.workspace.document("invalid-utf8", "invalid-utf8.md", "markdown"),
            ]
        )
        self.run_engine(expect_success=False)

        shutil.rmtree(self.workspace.output, ignore_errors=True)
        self.workspace.write_manifest(
            [
                self.workspace.document("malformed-jats", "malformed.xml", "jats"),
                self.workspace.document("invalid-utf8", "invalid-utf8.md", "markdown"),
                self.workspace.document("md-rich", "article.md", "markdown"),
            ]
        )
        self.run_engine()
        self.assert_fixed_outputs()
        papers = {
            item["doc_id"]: item
            for item in read_jsonl(self.workspace.output / "paper-metrics.jsonl")
        }
        self.assertIn("malformed-jats", papers)
        self.assertIn("invalid-utf8", papers)
        self.assertIn("md-rich", papers)
        for failed_id in ("malformed-jats", "invalid-utf8"):
            self.assertIn(
                papers[failed_id].get("status"),
                {"parse_failed", "failed"},
            )

    def test_design_profile_keeps_official_hard_and_corpus_soft(self) -> None:
        documents = [
            self.workspace.document("md-rich", "article.md", "markdown"),
            self.workspace.document("zero", "zero-objects.md", "markdown"),
        ]
        constraints = [
            {
                "constraint_id": "official-caption-required",
                "source_path": "corpus/guidelines.txt",
                "locator": "line:1",
                "statement": "Figure captions are required for every submitted figure.",
                "design_surface": "figure-caption",
                "affected_dimensions": ["D18", "D19"],
                "affected_scopes": ["SCOPE-RESULTS"],
            }
        ]
        self.workspace.write_manifest(documents, official_constraints=constraints)
        self.run_engine(output_flag="--output", output_path=self.workspace.output)

        profile = read_json(self.workspace.output / "design-profile.json")
        self.assertEqual(profile["schema"], "template-design-profile/1.0")
        entries = profile["entries"]
        official = [
            item for item in entries if item["source_type"] == "official_constraints"
        ]
        corpus = [item for item in entries if item["source_type"] == "corpus"]
        self.assertEqual(len(official), 1)
        self.assertEqual(official[0]["target_kind"], "hard_constraint")
        self.assertEqual(official[0]["origin"], "artifact-observed")
        self.assertTrue("source_hash" in official[0] or "source_sha256" in official[0])
        self.assertTrue(corpus)
        self.assertTrue(
            all(
                item["target_kind"]
                in {"soft_band", "sequence", "presence", "watch_only"}
                for item in corpus
            )
        )
        self.assertFalse(
            any(item["target_kind"] == "hard_constraint" for item in corpus)
        )
        for item in entries:
            for required in (
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
            ):
                self.assertIn(required, item)

    def test_official_hard_constraint_requires_matching_line_locator(self) -> None:
        document = self.workspace.document("md-rich", "article.md", "markdown")
        invented = [
            {
                "constraint_id": "invented",
                "source_path": "corpus/guidelines.txt",
                "locator": "line:999",
                "statement": "An invented requirement.",
                "design_surface": "figure-caption",
                "affected_dimensions": ["D18"],
                "affected_scopes": ["SCOPE-RESULTS"],
            }
        ]
        self.workspace.write_manifest([document], official_constraints=invented)
        self.run_engine(expect_success=False)
        self.assertFalse(self.workspace.output.exists())

    def test_supplements_are_reported_but_not_double_counted_as_main_papers(
        self,
    ) -> None:
        main = self.workspace.document("main", "article.md", "markdown")
        supplement = self.workspace.document(
            "main-supplement", "zero-objects.md", "markdown"
        )
        supplement["supplement_of"] = "main"
        self.workspace.write_manifest([main, supplement])
        self.run_engine()
        summary = read_json(self.workspace.output / "corpus-summary.json")
        self.assertEqual(summary["document_count"], 2)
        self.assertEqual(summary["supplement_document_count"], 1)
        self.assertEqual(summary["groups"]["overall"]["document_count"], 1)
        self.assertEqual(summary["groups"]["supplement"]["document_count"], 1)
        self.assertEqual(
            summary["groups"]["supplement"]["metrics"]["text.body_words"]["valid_n"],
            1,
        )
        self.assertEqual(
            summary["groups"]["overall"]["metrics"]["text.body_words"]["valid_n"],
            1,
        )

    def test_comparison_gate_uses_paper_counts_not_object_counts(self) -> None:
        def copied_document(
            doc_id: str, source_name: str, partition: str
        ) -> dict[str, Any]:
            destination_name = f"{doc_id}.md"
            shutil.copy2(
                self.workspace.corpus_dir / source_name,
                self.workspace.corpus_dir / destination_name,
            )
            with (self.workspace.corpus_dir / destination_name).open(
                "a", encoding="utf-8"
            ) as handle:
                handle.write(f"\n\nIndependent fixture marker: {doc_id}.\n")
            document = self.workspace.document(doc_id, destination_name, "markdown")
            document["partition"] = partition
            return document

        small_documents = [
            copied_document(f"small-primary-{index}", "article.md", "primary_match")
            for index in range(2)
        ] + [
            copied_document(f"small-venue-{index}", "zero-objects.md", "venue_control")
            for index in range(2)
        ]
        self.workspace.write_manifest(small_documents)
        self.run_engine()
        small_summary = read_json(self.workspace.output / "corpus-summary.json")
        small_comparisons = small_summary["comparisons"]
        self.assertTrue(small_comparisons)
        for comparison in small_comparisons:
            self.assertEqual(comparison["status"], "side_by_side_case_set")
            self.assertLess(comparison["n_a"], 5)
            self.assertLess(comparison["n_b"], 5)
            for effect_field in (
                "median_difference",
                "hodges_lehmann_shift",
                "cliffs_delta",
                "magnitude",
            ):
                self.assertIsNone(comparison[effect_field])

        shutil.rmtree(self.workspace.output)
        large_documents = (
            [
                copied_document(f"large-primary-{index}", "article.md", "primary_match")
                for index in range(5)
            ]
            + [
                copied_document(
                    f"large-venue-{index}", "zero-objects.md", "venue_control"
                )
                for index in range(5)
            ]
            + [
                copied_document(
                    f"large-topic-{index}", "missing-caption.md", "topic_control"
                )
                for index in range(5)
            ]
        )
        self.workspace.write_manifest(large_documents)
        self.run_engine()
        large_summary = read_json(self.workspace.output / "corpus-summary.json")
        large_comparisons = large_summary["comparisons"]
        computed = [
            item for item in large_comparisons if item["cliffs_delta"] is not None
        ]
        self.assertTrue(computed)
        for comparison in computed:
            self.assertGreaterEqual(comparison["n_a"], 5)
            self.assertGreaterEqual(comparison["n_b"], 5)
            self.assertIsNotNone(comparison["median_difference"])
            self.assertIsNotNone(comparison["hodges_lehmann_shift"])
            self.assertIsNotNone(comparison["cliffs_delta"])
            self.assertIsNotNone(comparison["magnitude"])

        groups = large_summary["groups"]

        def assert_group_valid_n(group: Any, maximum: int) -> None:
            values = [
                value
                for value in nested_values(group, "valid_n")
                if isinstance(value, int) and not isinstance(value, bool)
            ]
            self.assertTrue(values)
            self.assertTrue(all(value <= maximum for value in values), values)

        assert_group_valid_n(groups["overall"], 15)
        for group in (
            groups["by_partition"].values()
            if isinstance(groups["by_partition"], dict)
            else groups["by_partition"]
        ):
            assert_group_valid_n(group, 5)
        for group in (
            groups["by_article_type"].values()
            if isinstance(groups["by_article_type"], dict)
            else groups["by_article_type"]
        ):
            assert_group_valid_n(group, 15)
        for group in (
            groups["by_partition_article_type"].values()
            if isinstance(groups["by_partition_article_type"], dict)
            else groups["by_partition_article_type"]
        ):
            assert_group_valid_n(group, 5)

        overall_metrics = groups["overall"]["metrics"]
        body_words = overall_metrics["text.body_words"]
        self.assertEqual(body_words["bootstrap_resamples"], 1000)
        self.assertEqual(len(body_words["bootstrap_95_ci"]), 2)
        title_colon = overall_metrics["front.title_colon_present"]["category"]
        self.assertEqual(title_colon["valid_n"], 15)
        self.assertEqual(len(title_colon["wilson_95"]), 2)

    def test_cross_language_partition_effects_are_incomparable(self) -> None:
        documents: list[dict[str, Any]] = []
        for index in range(5):
            english = self.workspace.corpus_dir / f"english-{index}.md"
            english.write_text(
                f"# Results\n\nEnglish result words for paper {index}.\n",
                encoding="utf-8",
            )
            documents.append(
                self.workspace.document(f"english-{index}", english.name, "markdown")
            )
            chinese = self.workspace.corpus_dir / f"chinese-{index}.md"
            chinese.write_text(
                f"# 结果\n\n这是第{index}篇中文结果文本，用于不可比语言分层测试。\n",
                encoding="utf-8",
            )
            item = self.workspace.document(
                f"chinese-{index}", chinese.name, "markdown", language="zh"
            )
            item["partition"] = "venue_control"
            documents.append(item)
        self.workspace.write_manifest(
            documents,
            analysis_mode="distributional",
            design_metric_ids=["text.body_words"],
        )
        self.run_engine()
        summary = read_json(self.workspace.output / "corpus-summary.json")
        comparison = next(
            item
            for item in summary["comparisons"]
            if item["metric_id"] == "text.body_words"
        )
        self.assertEqual(comparison["status"], "incomparable_language_strata")
        self.assertIsNone(comparison["cliffs_delta"])
        self.assertEqual(comparison["language_profiles_a"], ["en"])
        self.assertEqual(comparison["language_profiles_b"], ["zh"])

    def test_bundle_identity_is_consistent_and_transaction_rolls_back(self) -> None:
        self.workspace.write_manifest(
            [self.workspace.document("md-rich", "article.md", "markdown")]
        )
        self.run_engine()
        analysis_id = read_json(self.workspace.output / "manifest.json")["analysis_id"]
        self.assertTrue(analysis_id.startswith("sha256:"))
        for name in (
            "metric-registry.json",
            "corpus-summary.json",
            "design-profile.json",
            "extraction-warnings.json",
        ):
            self.assertEqual(
                read_json(self.workspace.output / name)["analysis_id"], analysis_id
            )
        for name in ("paper-metrics.jsonl", "objects.jsonl"):
            for row in read_jsonl(self.workspace.output / name):
                self.assertEqual(row["analysis_id"], analysis_id)
        self.assertIn(
            html.escape(analysis_id),
            (self.workspace.output / "analysis-report.html").read_text(
                encoding="utf-8"
            ),
        )
        self.run_engine()
        self.assertEqual(
            read_json(self.workspace.output / "manifest.json")["analysis_id"],
            analysis_id,
        )

        spec = importlib.util.spec_from_file_location(
            "yxj_template_analyzer_transaction_test", SCRIPT
        )
        if spec is None or spec.loader is None:
            self.fail("could not load analyzer module for transactional test")
        loader = spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        self.addCleanup(lambda: sys.modules.pop(spec.name, None))
        loader.exec_module(module)
        transaction_root = self.workspace.root / "transaction"
        transaction_root.mkdir()
        original = {name: f"old:{name}".encode() for name in module.OUTPUT_NAMES}
        for name, payload in original.items():
            (transaction_root / name).write_bytes(payload)
        unknown = transaction_root / "owner-note.txt"
        unknown.write_text("preserve", encoding="utf-8")
        replacement = {name: f"new:{name}".encode() for name in module.OUTPUT_NAMES}
        real_replace = module.os.replace
        failed = False

        def fail_mid_install(source: Any, destination: Any) -> None:
            nonlocal failed
            source_path = Path(source)
            destination_path = Path(destination)
            if (
                not failed
                and source_path.parent.name.startswith(".template-analysis-stage-")
                and destination_path.parent == transaction_root
                and destination_path.name == "objects.jsonl"
            ):
                failed = True
                raise OSError("injected install failure")
            real_replace(source, destination)

        with mock.patch.object(module.os, "replace", side_effect=fail_mid_install):
            with self.assertRaises(OSError):
                module.write_bundle_transactional(transaction_root, replacement)
        self.assertTrue(failed)
        self.assertEqual(unknown.read_text(encoding="utf-8"), "preserve")
        for name, payload in original.items():
            self.assertEqual((transaction_root / name).read_bytes(), payload)

    def test_dom_abstract_preserves_paragraphs_and_exact_class_tokens(self) -> None:
        source = self.workspace.corpus_dir / "abstract-exact.html"
        source.write_text(
            """<html><head><meta name="keywords" content="design; statistics"></head><body><article>
<section class="not-abstract"><p>Body control words remain measurable.</p></section>
<section class="lead abstract feature"><h2>Abstract</h2>
<p>First <strong>nested</strong> abstract paragraph.</p><p>Second paragraph.</p></section>
<h1>Results</h1><p>Main result words cite <a role="doc-biblioref" href="#B1">Alpha</a>.</p>
<section role="doc-bibliography"><ol><li id="B1">Alpha source.</li><li>Beta source.</li></ol></section>
</article></body></html>""",
            encoding="utf-8",
        )
        self.workspace.write_manifest(
            [self.workspace.document("abstract-exact", source.name, "html")]
        )
        self.run_engine()
        row = read_jsonl(self.workspace.output / "paper-metrics.jsonl")[0]
        self.assertEqual(metric_value(row, "front.abstract_paragraph_count"), 2)
        self.assertEqual(metric_value(row, "front.abstract_words"), 6)
        self.assertEqual(metric_value(row, "text.body_words"), 10)
        self.assertEqual(metric_value(row, "front.keyword_count"), 2)
        self.assertEqual(metric_value(row, "citation.explicit_event_count"), 1)
        self.assertEqual(metric_value(row, "reference.entry_count"), 2)

    def test_markdown_multi_image_raw_figure_and_unclosed_blocks(self) -> None:
        source = self.workspace.corpus_dir / "markdown-edge.md"
        source.write_text(
            """# Results

Body words remain available.

![A](a.svg) ![B](b.svg)

<figure id="raw-figure"><img src="c.svg" alt="C"><figcaption>Figure 3. Raw figure.</figcaption></figure>
""",
            encoding="utf-8",
        )
        self.workspace.write_manifest(
            [self.workspace.document("markdown-edge", source.name, "markdown")]
        )
        self.run_engine()
        objects = read_jsonl(self.workspace.output / "objects.jsonl")
        self.assertEqual(len(objects), 3)
        self.assertIn(
            "markdown-edge#raw-figure", {item["object_id"] for item in objects}
        )

        source.write_text(
            "# Results\n\nBody before math.\n\n$$\nx = 1\n", encoding="utf-8"
        )
        self.workspace.write_manifest(
            [self.workspace.document("unclosed", source.name, "markdown")]
        )
        result = self.run_engine(expect_success=False)
        self.assertEqual(result.returncode, 1)
        warnings = read_json(self.workspace.output / "extraction-warnings.json")
        self.assertIn("unclosed Markdown", json.dumps(warnings))

    def test_table_cells_are_normalized_across_markdown_html_and_jats(self) -> None:
        markdown = self.workspace.corpus_dir / "same-table.md"
        markdown.write_text(
            "# Results\n\nBody paragraph.\n\n| A | B |\n|---|---|\n|1|2|\n|x|4|\n",
            encoding="utf-8",
        )
        html_source = self.workspace.corpus_dir / "same-table.html"
        html_source.write_text(
            "<article><h1>Results</h1><p>Body paragraph.</p><table><tr><th>A</th><th>B</th></tr><tr><td>1</td><td>2</td></tr><tr><td>x</td><td>4</td></tr></table></article>",
            encoding="utf-8",
        )
        jats = self.workspace.corpus_dir / "same-table.xml"
        jats.write_text(
            """<article><front><article-meta><title-group><article-title>Title</article-title></title-group></article-meta></front><body><sec><title>Results</title><p>Body paragraph.</p><table-wrap id="t1"><table><tr><th>A</th><th>B</th></tr><tr><td>1</td><td>2</td></tr><tr><td>x</td><td>4</td></tr></table></table-wrap></sec></body></article>""",
            encoding="utf-8",
        )
        self.workspace.write_manifest(
            [
                self.workspace.document("table-md", markdown.name, "markdown"),
                self.workspace.document("table-html", html_source.name, "html"),
                self.workspace.document("table-jats", jats.name, "jats"),
            ]
        )
        self.run_engine()
        rows = {
            row["doc_id"]: row
            for row in read_jsonl(self.workspace.output / "paper-metrics.jsonl")
        }
        for row in rows.values():
            self.assertEqual(metric_value(row, "table.rows"), 3.0)
            self.assertEqual(metric_value(row, "table.columns"), 2.0)
            self.assertEqual(metric_value(row, "table.numeric_cell_share_proxy"), 0.75)

        span_source = self.workspace.corpus_dir / "span-table.html"
        span_source.write_text(
            '<article><p>Body text.</p><table><tr><th colspan="2">Header</th></tr>'
            "<tr><td>1</td><td>2</td></tr></table></article>",
            encoding="utf-8",
        )
        self.workspace.write_manifest(
            [self.workspace.document("span-table", span_source.name, "html")]
        )
        self.run_engine()
        row = read_jsonl(self.workspace.output / "paper-metrics.jsonl")[0]
        for metric_id in (
            "table.rows",
            "table.columns",
            "table.numeric_cell_share_proxy",
        ):
            self.assertEqual(metric_entry(row, metric_id)["status"], "ambiguous")

        empty_source = self.workspace.corpus_dir / "empty-data-table.html"
        empty_source.write_text(
            "<article><p>Body text.</p><table><tr><th>Header</th></tr></table></article>",
            encoding="utf-8",
        )
        self.workspace.write_manifest(
            [self.workspace.document("empty-table", empty_source.name, "html")]
        )
        self.run_engine()
        row = read_jsonl(self.workspace.output / "paper-metrics.jsonl")[0]
        numeric_share = metric_entry(row, "table.numeric_cell_share_proxy")
        self.assertEqual(numeric_share["status"], "denominator_zero")
        self.assertIsNone(numeric_share["value"])

    def test_explicit_citations_annotations_and_entity_reductions_are_grounded(
        self,
    ) -> None:
        source = self.workspace.corpus_dir / "citation-and-objects.md"
        source.write_text(
            """# Results

Source [Alpha](#ref-alpha) is explicit; the surface [9] is not target-grounded.

![Architecture](a.svg){#fig-a}

![Result](b.svg){#fig-b}
""",
            encoding="utf-8",
        )
        source_hash = sha256(source)
        annotation = self.workspace.corpus_dir / "annotation-conflict.json"
        base_role = {"primary": "architecture", "secondary": []}
        annotation.write_text(
            json.dumps(
                {
                    "schema": "template-annotations/1.0",
                    "annotations": [
                        {
                            "doc_id": "grounded",
                            "object_id": "grounded#fig-a",
                            "origin": "owner-stated",
                            "resolution": "accepted",
                            "source_sha256": source_hash,
                            "role": base_role,
                            "panels": [],
                        },
                        {
                            "doc_id": "grounded",
                            "object_id": "grounded#fig-a",
                            "origin": "artifact-observed",
                            "resolution": "candidate",
                            "role": base_role,
                            "panels": [],
                        },
                        {
                            "doc_id": "grounded",
                            "object_id": "grounded#fig-b",
                            "origin": "model-proposed",
                            "resolution": "accepted",
                            "source_sha256": source_hash,
                            "role": {"primary": "main-result", "secondary": []},
                            "panels": [],
                        },
                    ],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        self.workspace.write_manifest(
            [
                self.workspace.document(
                    "grounded", source.name, "markdown", annotations=annotation.name
                )
            ]
        )
        self.run_engine()
        row = read_jsonl(self.workspace.output / "paper-metrics.jsonl")[0]
        self.assertEqual(metric_value(row, "citation.explicit_event_count"), 1)
        positions = metric_entry(row, "object.figure_position_norm")
        self.assertIsInstance(positions["value"], float)
        self.assertEqual(positions["observation_n"], 2)
        self.assertEqual(len(positions["entity_values"]), 2)
        objects = {
            item["object_id"]: item
            for item in read_jsonl(self.workspace.output / "objects.jsonl")
        }
        self.assertIsNone(objects["grounded#fig-a"]["annotation"])
        self.assertIsNone(objects["grounded#fig-b"]["annotation"])
        warning_text = json.dumps(
            read_json(self.workspace.output / "extraction-warnings.json")
        )
        self.assertIn("annotation_conflict", warning_text)
        self.assertIn("annotation_requires_owner_confirmation", warning_text)

    def test_requested_distributional_mode_is_downgraded_without_evidence(self) -> None:
        self.workspace.write_manifest(
            [self.workspace.document("single", "article.md", "markdown")],
            analysis_mode="distributional",
        )
        self.run_engine()
        summary = read_json(self.workspace.output / "corpus-summary.json")
        self.assertEqual(summary["requested_analysis_mode"], "distributional")
        self.assertEqual(summary["effective_analysis_mode"], "case_set")
        self.assertIsNotNone(summary["analysis_mode_downgrade_reason"])
        profile = read_json(self.workspace.output / "design-profile.json")
        corpus_entries = [
            item for item in profile["entries"] if item["source_type"] == "corpus"
        ]
        self.assertNotIn("soft_band", {item["target_kind"] for item in corpus_entries})

    def test_nested_section_aggregation_and_stratum_comparability_gate(self) -> None:
        documents: list[dict[str, Any]] = []
        for index in range(5):
            source = self.workspace.corpus_dir / f"nested-{index}.md"
            source.write_text(
                f"""---
title: Nested paper {index}
---

# Methods

## Data collection

Nested method words remain attributed to the parent method section.

# Results

Result words remain measurable.
"""
                + f"\nUnique paper marker {index}.\n",
                encoding="utf-8",
            )
            documents.append(
                self.workspace.document(f"nested-{index}", source.name, "markdown")
            )
        self.workspace.write_manifest(documents, analysis_mode="distributional")
        self.run_engine()
        summary = read_json(self.workspace.output / "corpus-summary.json")
        self.assertEqual(summary["effective_analysis_mode"], "distributional")
        primary = next(
            group
            for group in summary["groups"]["by_partition"]
            if group["filters"]["partition"] == "primary_match"
        )
        self.assertEqual(primary["metrics"]["structure.section_count"]["median"], 3)
        canonical = {
            item["label"]: item
            for item in primary["section_label_metrics"]["canonical"]
        }
        self.assertEqual(canonical["methods"]["valid_n"], 5)
        self.assertGreater(canonical["methods"]["metrics"]["word_count"]["median"], 0)
        self.assertTrue(primary["strata"]["comparable"])

        self.workspace.write_manifest(
            documents,
            analysis_mode="distributional",
            design_question="What numeric-cell share should result tables use?",
            design_metric_ids=["table.numeric_cell_share_proxy"],
        )
        self.run_engine()
        summary = read_json(self.workspace.output / "corpus-summary.json")
        self.assertEqual(summary["effective_analysis_mode"], "case_set")
        self.assertEqual(summary["distribution_ready_metric_count"], 0)
        profile = read_json(self.workspace.output / "design-profile.json")
        corpus_entries = [
            item for item in profile["entries"] if item["source_type"] == "corpus"
        ]
        self.assertEqual(
            [item["metric_ids"] for item in corpus_entries],
            [["table.numeric_cell_share_proxy"]],
        )
        self.assertEqual(corpus_entries[0]["observation"], "no-conclusion")

        documents[-1]["venue"] = "Different Journal"
        documents[-1]["inclusion_exception"] = {
            "reason": "Owner retains a declared cross-venue historical comparator.",
            "origin": "owner-stated",
            "resolution": "confirmed",
            "decision_pointer": "00_PROJECT_ROUTE.md#Decision Records",
        }
        self.workspace.write_manifest(documents, analysis_mode="distributional")
        self.run_engine()
        summary = read_json(self.workspace.output / "corpus-summary.json")
        self.assertEqual(summary["effective_analysis_mode"], "exploratory")
        primary = next(
            group
            for group in summary["groups"]["by_partition"]
            if group["filters"]["partition"] == "primary_match"
        )
        self.assertFalse(primary["strata"]["comparable"])
        self.assertIn("mixed_venues", primary["strata"]["comparability_reasons"])
        self.assertIn(
            "owner_inclusion_exception_present",
            primary["strata"]["comparability_reasons"],
        )
        profile = read_json(self.workspace.output / "design-profile.json")
        self.assertNotIn(
            "soft_band",
            {
                item["target_kind"]
                for item in profile["entries"]
                if item["source_type"] == "corpus"
            },
        )

    def test_parser_security_failures_are_isolated_and_duplicate_ids_fail(self) -> None:
        deep = self.workspace.corpus_dir / "deep.xml"
        nested = "".join(
            f'<sec id="s{index}"><title>S{index}</title>' for index in range(260)
        )
        nested += "<p>Deep body text.</p>" + "</sec>" * 260
        deep.write_text(f"<article><body>{nested}</body></article>", encoding="utf-8")
        valid = self.workspace.corpus_dir / "valid-unique.md"
        valid.write_text("# Results\n\nValid body text.\n", encoding="utf-8")
        self.workspace.write_manifest(
            [
                self.workspace.document("deep", deep.name, "jats"),
                self.workspace.document("valid", valid.name, "markdown"),
            ]
        )
        self.run_engine()
        rows = {
            row["doc_id"]: row
            for row in read_jsonl(self.workspace.output / "paper-metrics.jsonl")
        }
        self.assertEqual(rows["deep"]["status"], "parse_failed")
        self.assertEqual(rows["valid"]["status"], "ok")
        self.assertIn("nesting exceeds", rows["deep"]["parse"]["message"])

        duplicate = self.workspace.corpus_dir / "duplicate-object.md"
        duplicate.write_text(
            "# Results\n\nBody text.\n\n![A](a.svg){#same}\n\n![B](b.svg){#same}\n",
            encoding="utf-8",
        )
        self.workspace.write_manifest(
            [self.workspace.document("duplicate-object", duplicate.name, "markdown")]
        )
        result = self.run_engine(expect_success=False)
        self.assertEqual(result.returncode, 1)
        row = read_jsonl(self.workspace.output / "paper-metrics.jsonl")[0]
        self.assertIn("duplicate explicit object ID", row["parse"]["message"])

        unsafe = self.workspace.corpus_dir / "late-doctype.xml"
        unsafe.write_text(
            " " * 9000
            + '<!DOCTYPE article [<!ENTITY x "unsafe">]><article><body><p>&x;</p></body></article>',
            encoding="utf-8",
        )
        self.workspace.write_manifest(
            [self.workspace.document("unsafe", unsafe.name, "jats")]
        )
        result = self.run_engine(expect_success=False)
        self.assertEqual(result.returncode, 1)
        row = read_jsonl(self.workspace.output / "paper-metrics.jsonl")[0]
        self.assertIn("DOCTYPE/ENTITY", row["parse"]["message"])

    def test_input_output_overlap_and_hidden_child_symlink_are_rejected(self) -> None:
        self.workspace.output.mkdir(parents=True)
        overlapping = self.workspace.output / "objects.jsonl"
        overlapping.write_text("ORIGINAL\n", encoding="utf-8")
        document = self.workspace.document("overlap", "article.md", "markdown")
        document["path"] = ".yxj-paper-os/template-analysis/objects.jsonl"
        self.workspace.write_manifest([document])
        self.run_engine(expect_success=False)
        self.assertEqual(overlapping.read_text(encoding="utf-8"), "ORIGINAL\n")

        shutil.rmtree(self.workspace.output)
        self.workspace.output.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.workspace.output.symlink_to("..", target_is_directory=True)
        except OSError as error:
            self.skipTest(f"symlinks unavailable: {error}")
        self.workspace.write_manifest(
            [self.workspace.document("md-rich", "article.md", "markdown")]
        )
        self.run_engine(expect_success=False)
        self.assertFalse((self.workspace.root / "objects.jsonl").exists())

    def test_html_report_is_offline_and_escapes_untrusted_text(self) -> None:
        malicious_statement = '<img src=x onerror="alert(1)"> captions are required.'
        source = self.workspace.corpus_dir / "malicious-guidelines.txt"
        source.write_text(malicious_statement + "\n", encoding="utf-8")
        constraints = [
            {
                "constraint_id": "escaped-metric-text",
                "source_path": "corpus/malicious-guidelines.txt",
                "locator": "line:1",
                "statement": malicious_statement,
                "design_surface": "figure-caption",
                "affected_dimensions": ["D18"],
                "affected_scopes": ["SCOPE-RESULTS"],
            }
        ]
        self.workspace.write_manifest(
            [self.workspace.document("md-rich", "article.md", "markdown")],
            official_constraints=constraints,
        )
        self.run_engine()
        report = (self.workspace.output / "analysis-report.html").read_text(
            encoding="utf-8"
        )
        report_lower = report.lower()
        self.assertNotIn("<script src=", report_lower)
        self.assertNotRegex(report_lower, r"<link\b[^>]*\bhref\s*=\s*['\"]?http")
        self.assertNotIn("http://", report_lower)
        self.assertNotIn("https://", report_lower)
        self.assertNotIn(malicious_statement, report)
        self.assertIn(html.escape(malicious_statement), report)


if __name__ == "__main__":
    unittest.main(verbosity=2)
