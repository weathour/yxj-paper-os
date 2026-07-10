from __future__ import annotations
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from verify_behavior_scenarios import validate_response

ROOT = Path(__file__).resolve().parent.parent
SCENARIOS = json.loads((ROOT / "assets/evals/behavior-scenarios.json").read_text())[
    "scenarios"
]
RESPONSES = json.loads((ROOT / "assets/evals/behavior-responses.json").read_text())
POLICY = {x["id"]: x for x in SCENARIOS}


class BehaviorScenarioTests(unittest.TestCase):
    def test_fourteen_scenarios_and_good_records(self):
        self.assertEqual(len(POLICY), 14)
        self.assertEqual({r["scenario_id"] for r in RESPONSES["good"]}, set(POLICY))
        for record in RESPONSES["good"]:
            self.assertEqual(
                validate_response(record, POLICY), [], record["scenario_id"]
            )

    def test_bad_records_are_rejected(self):
        bad = RESPONSES["bad"]
        self.assertGreaterEqual(len(bad), 14)
        for record in bad:
            self.assertTrue(validate_response(record, POLICY), record["scenario_id"])

    def test_b01_requires_record_and_b14_stays_lightweight(self):
        self.assertEqual(
            POLICY["B01"]["required_all_actions"], ["INSPECT", "RECORD_OBSERVATION"]
        )
        self.assertEqual(
            POLICY["B14"]["prohibited_side_effects"],
            ["subagents", "full_scan", "template_intake", "external_execution"],
        )
        self.assertIn("RECORD_OBSERVATION", POLICY["B14"]["required_all_actions"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
