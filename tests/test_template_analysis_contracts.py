from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "yxj-paper-os"
ANALYSIS_ASSETS = SKILL_ROOT / "assets" / "template-analysis"


class TemplateAnalysisContractTests(unittest.TestCase):
    def test_registry_uses_non_gating_sample_size_label(self) -> None:
        registry = json.loads(
            (ANALYSIS_ASSETS / "metric-registry.json").read_text(encoding="utf-8")
        )
        aggregation = registry["aggregation_contract"]
        self.assertNotIn("sample_strength", aggregation)
        label = aggregation["sample_size_label"]
        self.assertEqual(label["purpose"], "descriptive paper-count context only")
        self.assertIn("corpus_sufficiency", label["not_a_gate_for"])
        self.assertIn("venue fit", label["not_a_gate_for"])

    def test_proxy_registry_definitions_match_declared_surface_contract(self) -> None:
        registry = json.loads(
            (ANALYSIS_ASSETS / "metric-registry.json").read_text(encoding="utf-8")
        )
        metrics = {item["metric_id"]: item for item in registry["metrics"]}

        algorithm = metrics["algorithm.marker_count"]
        self.assertEqual(algorithm["extraction_mode"], "heuristic")
        self.assertEqual(algorithm["supported_formats"], ["markdown", "html", "jats"])
        self.assertIn("Input", algorithm["definition"])
        self.assertIn("return", algorithm["definition"])

        for metric_id in (
            "marker.repro_code_link_count",
            "marker.repro_data_link_count",
        ):
            item = metrics[metric_id]
            self.assertIn("URL/URI", item["definition"])
            self.assertIn("parsed paragraphs", item["definition"])
            self.assertIn("not fetched or verified", item["definition"])
            self.assertEqual(item["extraction_mode"], "heuristic")

        for metric_id in (
            "caption.figure_panel_label_count_proxy",
            "caption.figure_uncertainty_marker_count",
            "caption.table_uncertainty_marker_count",
        ):
            item = metrics[metric_id]
            self.assertEqual(item["entity"], "document")
            self.assertIn("event", item["definition"])
            self.assertEqual(item["extraction_mode"], "heuristic")

    def test_manifest_requires_design_question_and_grounded_exception(self) -> None:
        schema = json.loads(
            (ANALYSIS_ASSETS / "manifest.schema.json").read_text(encoding="utf-8")
        )
        self.assertIn("design_question", schema["required"])
        self.assertIn("design_metric_ids", schema["required"])
        self.assertIn(
            "requested",
            schema["properties"]["analysis_mode"]["description"].lower(),
        )
        exception = schema["$defs"]["document"]["properties"]["inclusion_exception"]
        self.assertEqual(exception["type"], "object")
        self.assertEqual(
            set(exception["required"]),
            {"reason", "origin", "resolution", "decision_pointer"},
        )
        self.assertEqual(exception["properties"]["origin"]["const"], "owner-stated")
        self.assertEqual(exception["properties"]["resolution"]["const"], "confirmed")


if __name__ == "__main__":
    unittest.main(verbosity=2)
