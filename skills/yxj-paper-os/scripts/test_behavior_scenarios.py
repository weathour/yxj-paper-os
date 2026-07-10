from __future__ import annotations
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from capture_behavior_actions import (
    ORACLE_SCENARIO_KEYS,
    REFERENCE_END,
    REFERENCE_START,
    SCENARIOS_END,
    SCENARIOS_START,
    SKILL_END,
    SKILL_START,
    build_output_schema,
    load_scenarios,
    prompt_contract_errors,
)
from verify_behavior_scenarios import validate_response

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "assets/fixtures/behavior"
SCENARIOS = json.loads((FIXTURES / "scenarios.json").read_text())["scenarios"]
GOOD = json.loads((FIXTURES / "good.json").read_text())["responses"]
BAD = json.loads((FIXTURES / "bad.json").read_text())["responses"]
FRESH = json.loads((FIXTURES / "fresh.json").read_text())["responses"]
POLICY = {x["id"]: x for x in SCENARIOS}
CANONICAL_SCENARIOS = json.loads(
    (ROOT / "assets/evals/behavior-scenarios.json").read_text()
)["scenarios"]
CAPTURE = Path(__file__).resolve().parent / "capture_behavior_actions.py"
VERIFY = Path(__file__).resolve().parent / "verify_behavior_scenarios.py"
SKILL = ROOT / "SKILL.md"
VENUE_TEMPLATE = ROOT / "references/lenses/venue-template.md"
CANONICAL_SCENARIO_PATH = ROOT / "assets/evals/behavior-scenarios.json"
CURRENT_CAPTURE = (
    ROOT / "evals/recorded/fixture-current/capture-20260710-template-analysis"
)


class BehaviorScenarioTests(unittest.TestCase):
    def run_cmd(self, *args: object) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *map(str, args)],
            cwd=ROOT.parents[1],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_dynamic_scenario_count_and_good_records(self):
        self.assertEqual(len(POLICY), len(SCENARIOS))
        self.assertEqual(CANONICAL_SCENARIOS, SCENARIOS)
        self.assertEqual({r["scenario_id"] for r in GOOD}, set(POLICY))
        for record in GOOD:
            self.assertEqual(
                validate_response(record, POLICY), [], record["scenario_id"]
            )

    def test_bad_records_are_rejected(self):
        self.assertGreaterEqual(len(BAD), len(POLICY))
        for record in BAD:
            self.assertTrue(validate_response(record, POLICY), record["scenario_id"])

    def test_fresh_fixture_covers_current_policy(self):
        self.assertEqual({r["scenario_id"] for r in FRESH}, set(POLICY))
        for record in FRESH:
            self.assertEqual(
                validate_response(record, POLICY), [], record["scenario_id"]
            )

    def test_b01_requires_record_and_b14_stays_lightweight(self):
        self.assertEqual(
            POLICY["B01"]["required_all_actions"], ["INSPECT", "RECORD_OBSERVATION"]
        )
        self.assertTrue(
            {
                "subagents",
                "full_scan",
                "template_intake",
                "template_analysis",
                "pdf_pseudo_parse",
                "external_execution",
            }.issubset(POLICY["B14"]["prohibited_side_effects"])
        )
        self.assertIn("RECORD_OBSERVATION", POLICY["B14"]["required_all_actions"])

    def test_b15_to_b20_lock_template_analysis_boundaries(self):
        self.assertEqual(
            {f"B{index:02d}" for index in range(15, 21)},
            {scenario_id for scenario_id in POLICY if scenario_id >= "B15"},
        )
        self.assertIn("template_analysis", POLICY["B15"]["required_side_effects"])
        self.assertIn("pdf_pseudo_parse", POLICY["B18"]["prohibited_side_effects"])
        self.assertIn("KEEP_CLAIM_INACTIVE", POLICY["B19"]["required_all_actions"])
        self.assertIn("DEPENDENCY_RECHECK", POLICY["B20"]["required_all_actions"])
        methods_rule = next(
            rule
            for rule in POLICY["B18"]["readiness_rules"]
            if rule["scope_id"] == "SCOPE-METHODS"
        )
        self.assertEqual(methods_rule["allowed"], ["writer-ready"])
        schema = build_output_schema(CANONICAL_SCENARIOS)
        readiness_enum = schema["properties"]["responses"]["items"]["properties"][
            "readiness_updates"
        ]["items"]["properties"]["readiness"]["enum"]
        self.assertIn("writer-ready", readiness_enum)
        self.assertNotIn("ready", readiness_enum)

    def test_capture_prompt_embeds_full_skill_but_no_policy_oracle(self):
        with tempfile.TemporaryDirectory() as directory:
            capture = Path(directory) / "capture"
            result = self.run_cmd(
                CAPTURE,
                "init",
                "--capture",
                capture,
                "--skill",
                SKILL,
                "--scenarios",
                CANONICAL_SCENARIO_PATH,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            prompt = (capture / "prompt.md").read_text(encoding="utf-8")
            skill_text = SKILL.read_text(encoding="utf-8")
            reference_text = VENUE_TEMPLATE.read_text(encoding="utf-8")
            self.assertIn(f"{SKILL_START}\n{skill_text}", prompt)
            self.assertIn(SKILL_END, prompt)
            self.assertIn(f"{REFERENCE_START}\n{reference_text}", prompt)
            self.assertIn(REFERENCE_END, prompt)
            self.assertEqual(
                prompt_contract_errors(
                    prompt, skill_text, reference_text, CANONICAL_SCENARIOS
                ),
                [],
            )
            match = re.search(
                re.escape(SCENARIOS_START) + r"\n(.*?)\n" + re.escape(SCENARIOS_END),
                prompt,
                re.DOTALL,
            )
            self.assertIsNotNone(match)
            assert match is not None
            visible = json.loads(match.group(1))["scenarios"]
            self.assertEqual(len(visible), len(CANONICAL_SCENARIOS))
            for scenario in visible:
                self.assertEqual(set(scenario), {"id", "situation", "context"})
                self.assertFalse(set(scenario) & ORACLE_SCENARIO_KEYS)

    def test_prompt_contract_rejects_oracle_field_in_visible_projection(self):
        with tempfile.TemporaryDirectory() as directory:
            capture = Path(directory) / "capture"
            result = self.run_cmd(
                CAPTURE,
                "init",
                "--capture",
                capture,
                "--skill",
                SKILL,
                "--scenarios",
                CANONICAL_SCENARIO_PATH,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            prompt_path = capture / "prompt.md"
            prompt = prompt_path.read_text(encoding="utf-8")
            prompt = prompt.replace(
                '"context": null,',
                '"context": null,\n      "required_all_actions": ["INSPECT"],',
                1,
            )
            errors = prompt_contract_errors(
                prompt,
                SKILL.read_text(encoding="utf-8"),
                VENUE_TEMPLATE.read_text(encoding="utf-8"),
                CANONICAL_SCENARIOS,
            )
            self.assertTrue(errors)
            self.assertTrue(any("oracle" in error for error in errors))

    def test_scenario_context_cannot_nest_policy_oracle(self):
        with tempfile.TemporaryDirectory() as directory:
            scenario_path = Path(directory) / "scenarios.json"
            scenario_path.write_text(
                json.dumps(
                    {
                        "scenarios": [
                            {
                                "id": "B01",
                                "situation": "safe surface",
                                "context": {
                                    "nested": {"required_all_actions": ["INSPECT"]}
                                },
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "oracle"):
                load_scenarios(scenario_path)

    def test_current_recorded_capture_uses_oracle_free_prompt_contract(self):
        result = self.run_cmd(
            VERIFY,
            CANONICAL_SCENARIO_PATH,
            "--capture",
            CURRENT_CAPTURE,
            "--skill",
            SKILL,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
