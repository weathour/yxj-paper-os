from __future__ import annotations

import copy
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from capture_behavior_actions import (  # noqa: E402
    MANIFEST_FIELDS,
    ORACLE_SCENARIO_KEYS,
    REFERENCE_END,
    REFERENCE_START,
    SCENARIOS_END,
    SCENARIOS_START,
    SKILL_END,
    SKILL_START,
    UPDATE_FREE_TEXT_FIELDS,
    authority_witness_document,
    build_output_schema,
    load_scenarios,
    model_visible_scenario_json,
    parse_public_pointer,
    prompt_contract_errors,
    response_contract_fingerprint,
    rule_matches,
    schema_runtime_topology_errors,
    sha,
    strict_response_document_errors,
)
from verify_behavior_scenarios import (  # noqa: E402
    ACTIONS,
    validate_response,
    validate_response_warnings,
)

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "assets/fixtures/behavior"
AUTHORITATIVE_PATH = ROOT / "assets/evals/behavior-responses.json"
AUTHORITATIVE = json.loads(AUTHORITATIVE_PATH.read_text())
GOOD = AUTHORITATIVE["good"]
BAD = AUTHORITATIVE["bad"]
GOOD_BY_ID = {item["scenario_id"]: item for item in GOOD}
SCENARIOS = json.loads((ROOT / "assets/evals/behavior-scenarios.json").read_text())[
    "scenarios"
]
POLICY = {item["id"]: item for item in SCENARIOS}
CAPTURE = Path(__file__).resolve().parent / "capture_behavior_actions.py"
VERIFY = Path(__file__).resolve().parent / "verify_behavior_scenarios.py"
SKILL = ROOT / "SKILL.md"
VENUE_TEMPLATE = ROOT / "references/lenses/venue-template.md"
CANONICAL_SCENARIO_PATH = ROOT / "assets/evals/behavior-scenarios.json"
CURRENT_CAPTURE = (
    ROOT / "evals/recorded/fixture-current/capture-20260710-template-analysis"
)
FOUR_GATES = {
    "scientific_commitment",
    "argument_spine",
    "material_local_tradeoff",
    "deliberate_divergence",
}
SIX_CAPTURE_HASHES = {
    "skill_sha256",
    "scenarios_sha256",
    "prompt_sha256",
    "output_schema_sha256",
    "raw_output_sha256",
    "actions_sha256",
}


class BehaviorScenarioTests(unittest.TestCase):
    def run_cmd(self, *args: object) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *map(str, args)],
            cwd=ROOT.parents[1],
            text=True,
            capture_output=True,
            check=False,
        )

    @staticmethod
    def alternate_structured_value(field: str, current: object) -> object:
        candidates: dict[str, list[object]] = {
            "record_kind": ["paragraph", "frame", "template_source", "claim"],
            "operation": ["create", "revise"],
            "analysis_mode": ["case_set", "exploratory", "distributional"],
            "target_kind": ["paragraph_function", "caption_blueprint", "metadata_only"],
            "candidate_action": ["adapt", "reject"],
            "origin": [
                "artifact-observed",
                "owner-stated",
                "model-derived",
                "model-proposed",
            ],
            "resolution": [
                "confirmed",
                "unresolved",
                "candidate",
                "accepted",
                "rejected",
                "stale",
            ],
            "status": [
                "active",
                "inactive",
                "candidate",
                "blocked",
                "ready",
                "partial",
                "unsupported",
                "stale",
                "confirmed",
                "deferred",
                "rejected",
            ],
            "support": [
                "evidence-supported",
                "evidence-partial",
                "evidence-unsupported",
                "not_applicable",
            ],
            "locator": ["https://example.org/alternate-source"],
            "decision_pointer": ["DEC-ALT-99"],
            "grounding": [["ALT-GROUNDING-99"]],
            "epistemic_label": [
                "artifact-observed",
                "owner-stated",
                "model-derived",
                "model-proposed",
            ],
            "design_only_state": ["design_only", "not_applicable"],
            "schema_version": ["0.2", "0.3"],
            "gate_category": [
                "scientific_commitment",
                "argument_spine",
                "material_local_tradeoff",
                "deliberate_divergence",
            ],
            "role": ["alternate_role"],
            "access_state": ["full_text", "metadata_only", "snippet_only"],
            "partition": ["alternate partition"],
            "missingness": ["alternate missingness"],
            "denominator": ["1 eligible"],
            "effective_conclusion": ["alternate bounded conclusion"],
            "promotion_pointer": ["M-ALT-99"],
            "linked_records": [["M-ALT-99"]],
            "scope_id": ["SCOPE-ALT-99"],
            "readiness": ["writer-ready", "partial", "blocked", "deferred"],
            "blocker": ["ALT-BLOCKER-99"],
            "next_action": ["alternate bounded action"],
            "output_pointer": ["04_WRITING_DESIGN_PACK.md#SCOPE-ALT-99"],
        }
        if field == "record_id":
            assert isinstance(current, str)
            return (
                "SCHEMA_ALT_99"
                if current.startswith("SCHEMA_")
                else f"{current.split('-', 1)[0]}-ALT-99"
            )
        for candidate in candidates[field]:
            if candidate != current:
                return candidate
        raise AssertionError(f"no alternate structured value for {field}={current}")

    def assert_document_rejected_by_both(
        self, document: dict[str, object], label: str
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            capture = Path(directory) / "fixture-current" / "capture"
            shutil.copytree(CURRENT_CAPTURE, capture)
            normalized = (
                json.dumps(document, ensure_ascii=False, sort_keys=True, indent=2)
                + "\n"
            )
            (capture / "actions.json").write_text(normalized, encoding="utf-8")
            (capture / "raw-output.md").write_text(normalized, encoding="utf-8")
            manifest_path = capture / "manifest.json"
            manifest = json.loads(manifest_path.read_text())
            manifest["actions_sha256"] = sha(capture / "actions.json")
            manifest["raw_output_sha256"] = sha(capture / "raw-output.md")
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            verify = self.run_cmd(
                VERIFY,
                CANONICAL_SCENARIO_PATH,
                "--capture",
                capture,
                "--skill",
                SKILL,
            )
            self.assertNotEqual(verify.returncode, 0, f"verifier accepted {label}")

        with tempfile.TemporaryDirectory() as directory:
            capture = Path(directory) / "capture"
            init = self.run_cmd(
                CAPTURE,
                "init",
                "--capture",
                capture,
                "--skill",
                SKILL,
                "--scenarios",
                CANONICAL_SCENARIO_PATH,
            )
            self.assertEqual(init.returncode, 0, init.stderr)
            (capture / "raw-output.md").write_text(
                json.dumps(document, ensure_ascii=False), encoding="utf-8"
            )
            finalize = self.run_cmd(
                CAPTURE,
                "finalize",
                "--capture",
                capture,
                "--capture-kind",
                "offline_policy_fixture",
                "--model",
                "policy-fixture",
                "--runtime",
                "offline-reproducible-fixture",
                "--skill",
                SKILL,
                "--scenarios",
                CANONICAL_SCENARIO_PATH,
            )
            self.assertNotEqual(finalize.returncode, 0, f"finalizer accepted {label}")
            self.assertFalse((capture / "manifest.json").exists())

    def assert_scenario_text_rejected_by_verifier_and_init(
        self, scenario_text: str, label: str
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scenarios.json"
            path.write_text(scenario_text, encoding="utf-8")
            verify = self.run_cmd(VERIFY, path)
            self.assertNotEqual(verify.returncode, 0, f"verifier accepted {label}")
            capture = Path(directory) / "capture"
            init = self.run_cmd(
                CAPTURE,
                "init",
                "--capture",
                capture,
                "--skill",
                SKILL,
                "--scenarios",
                path,
            )
            self.assertNotEqual(init.returncode, 0, f"capture init accepted {label}")
            self.assertFalse((capture / "prompt.md").exists())

    def assert_raw_text_rejected_by_both(self, raw_text: str, label: str) -> None:
        with tempfile.TemporaryDirectory() as directory:
            capture = Path(directory) / "capture"
            shutil.copytree(CURRENT_CAPTURE, capture)
            (capture / "raw-output.md").write_text(raw_text, encoding="utf-8")
            manifest_path = capture / "manifest.json"
            manifest = json.loads(manifest_path.read_text())
            manifest["raw_output_sha256"] = sha(capture / "raw-output.md")
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            verify = self.run_cmd(
                VERIFY,
                CANONICAL_SCENARIO_PATH,
                "--capture",
                capture,
                "--skill",
                SKILL,
            )
            self.assertNotEqual(verify.returncode, 0, f"verifier accepted {label}")

        with tempfile.TemporaryDirectory() as directory:
            capture = Path(directory) / "capture"
            init = self.run_cmd(
                CAPTURE,
                "init",
                "--capture",
                capture,
                "--skill",
                SKILL,
                "--scenarios",
                CANONICAL_SCENARIO_PATH,
            )
            self.assertEqual(init.returncode, 0, init.stderr)
            (capture / "raw-output.md").write_text(raw_text, encoding="utf-8")
            finalize = self.run_cmd(
                CAPTURE,
                "finalize",
                "--capture",
                capture,
                "--capture-kind",
                "offline_policy_fixture",
                "--model",
                "policy-fixture",
                "--runtime",
                "offline-reproducible-fixture",
                "--skill",
                SKILL,
                "--scenarios",
                CANONICAL_SCENARIO_PATH,
            )
            self.assertNotEqual(finalize.returncode, 0, f"finalizer accepted {label}")
            self.assertFalse((capture / "manifest.json").exists())

    def test_authoritative_responses_own_exact_mirrors_and_current_actions(self):
        self.assertEqual(
            json.loads((FIXTURES / "good.json").read_text())["responses"], GOOD
        )
        self.assertEqual(
            json.loads((FIXTURES / "bad.json").read_text())["responses"], BAD
        )
        self.assertEqual(
            json.loads((FIXTURES / "scenarios.json").read_text())["scenarios"],
            SCENARIOS,
        )
        self.assertFalse((FIXTURES / "fresh.json").exists())
        self.assertEqual(
            json.loads((CURRENT_CAPTURE / "actions.json").read_text())["responses"],
            GOOD,
        )

    def test_current_policy_has_fifteen_cases_for_twelve_scenario_groups(self):
        self.assertEqual(list(POLICY), [f"B{index:02d}" for index in range(1, 16)])
        self.assertEqual({item["scenario_id"] for item in GOOD}, set(POLICY))
        self.assertEqual(len(BAD), len(POLICY))
        for scenario in SCENARIOS:
            self.assertEqual(
                set(scenario["required_scopes"]), set(scenario["allowed_scopes"])
            )
            self.assertEqual(
                set(scenario["required_dimensions"]),
                set(scenario["allowed_dimensions"]),
            )
            self.assertIn("optional_side_effects", scenario)

    def test_action_contract_is_five_unordered_families(self):
        self.assertEqual(
            ACTIONS, {"INSPECT", "DERIVE", "PROJECT", "ASK_OWNER", "VALIDATE"}
        )
        schema = build_output_schema(SCENARIOS)
        action_enum = schema["properties"]["responses"]["items"]["properties"][
            "selected_actions"
        ]["items"]["enum"]
        self.assertEqual(set(action_enum), ACTIONS)
        for response in GOOD:
            self.assertEqual(validate_response(response, POLICY), [])

    def test_authoritative_good_document_passes_and_each_bad_record_fails(self):
        self.assertEqual(
            strict_response_document_errors({"responses": GOOD}, SCENARIOS), []
        )
        for record in BAD:
            self.assertTrue(validate_response(record, POLICY), record["scenario_id"])

    def test_strict_schema_rejects_extra_keys_and_boolean_integer(self):
        mutations = []
        top = copy.deepcopy(GOOD_BY_ID["B01"])
        top["oracle"] = True
        mutations.append(top)
        update = copy.deepcopy(GOOD_BY_ID["B01"])
        update["updates"][0]["oracle"] = True
        mutations.append(update)
        readiness = copy.deepcopy(GOOD_BY_ID["B01"])
        readiness["readiness_updates"][0]["oracle"] = True
        mutations.append(readiness)
        question = copy.deepcopy(GOOD_BY_ID["B04"])
        question["question"]["oracle"] = True
        mutations.append(question)
        boolean_count = copy.deepcopy(GOOD_BY_ID["B04"])
        boolean_count["question"]["count"] = True
        mutations.append(boolean_count)
        for mutation in mutations:
            with self.subTest(scenario=mutation["scenario_id"], keys=mutation.keys()):
                self.assertTrue(validate_response(mutation, POLICY))
        document = {"responses": copy.deepcopy(GOOD), "oracle": True}
        self.assertTrue(strict_response_document_errors(document, SCENARIOS))

    def test_strict_schema_rejects_enum_pattern_nullable_and_array_shape(self):
        mutations = []
        unknown_action = copy.deepcopy(GOOD_BY_ID["B01"])
        unknown_action["selected_actions"][0] = "UNKNOWN"
        mutations.append(unknown_action)
        invalid_dimension = copy.deepcopy(GOOD_BY_ID["B01"])
        invalid_dimension["target_dimensions"][0] = "D20"
        mutations.append(invalid_dimension)
        wrong_array = copy.deepcopy(GOOD_BY_ID["B01"])
        wrong_array["target_scopes"] = "SCOPE-RESULTS"
        mutations.append(wrong_array)
        wrong_nullable = copy.deepcopy(GOOD_BY_ID["B01"])
        wrong_nullable["updates"][0]["promotion_pointer"] = 1
        mutations.append(wrong_nullable)
        wrong_array_item = copy.deepcopy(GOOD_BY_ID["B11"])
        wrong_array_item["updates"][0]["linked_records"] = ["M-RESULT-A", 1]
        mutations.append(wrong_array_item)
        for mutation in mutations:
            with self.subTest(scenario=mutation["scenario_id"]):
                self.assertTrue(validate_response(mutation, POLICY))

    def test_semantic_closure_rejects_extra_action_scope_update_and_identity(self):
        extra_action = copy.deepcopy(GOOD_BY_ID["B01"])
        extra_action["selected_actions"].append("ASK_OWNER")
        extra_scope = copy.deepcopy(GOOD_BY_ID["B11"])
        extra_scope["target_scopes"].append("SCOPE-NOT-IN-CONTEXT")
        extra_link = copy.deepcopy(GOOD_BY_ID["B11"])
        extra_link["updates"][0]["linked_records"].append("M-RESULT-B")
        wrong_origin = copy.deepcopy(GOOD_BY_ID["B15"])
        wrong_origin["updates"][0]["origin"] = "owner-stated"
        unmatched_update = copy.deepcopy(GOOD_BY_ID["B01"])
        unmatched_update["updates"].append(
            copy.deepcopy(GOOD_BY_ID["B15"]["updates"][0])
        )
        for mutation in (
            extra_action,
            extra_scope,
            extra_link,
            wrong_origin,
            unmatched_update,
        ):
            with self.subTest(scenario=mutation["scenario_id"]):
                self.assertTrue(validate_response(mutation, POLICY))

    def test_routine_cases_do_not_ask_and_only_four_gates_ask_once(self):
        asking = {
            sid
            for sid, response in GOOD_BY_ID.items()
            if "ASK_OWNER" in response["selected_actions"]
        }
        self.assertEqual(asking, {"B04", "B05", "B06", "B07"})
        self.assertEqual(
            {GOOD_BY_ID[sid]["question"]["target"] for sid in asking}, FOUR_GATES
        )
        for sid, response in GOOD_BY_ID.items():
            self.assertEqual(response["question"]["count"], 1 if sid in asking else 0)

    def test_prose_heuristic_is_warning_only_and_not_a_semantic_proof(self):
        frame = GOOD_BY_ID["B02"]["updates"][0]
        self.assertIn("[bounded context]", frame["design_payload"])
        self.assertEqual(validate_response_warnings(GOOD_BY_ID["B02"]), [])
        leaked = copy.deepcopy(GOOD_BY_ID["B02"])
        leaked["updates"][0]["design_payload"] = (
            "[C-BOUND-02] The bounded evidence clearly demonstrates a robust "
            "contribution that substantially improves the state of the art."
        )
        self.assertEqual(validate_response(leaked, POLICY), [])
        self.assertTrue(validate_response_warnings(leaked))
        revised_reason = copy.deepcopy(GOOD_BY_ID["B01"])
        revised_reason["updates"][0]["reason"] = (
            "Alternative nonblank functional rationale remains free text"
        )
        self.assertEqual(validate_response(revised_reason, POLICY), [])
        revised_reason["updates"][0]["reason"] = " "
        self.assertTrue(validate_response(revised_reason, POLICY))

    def test_scenario_loader_requires_complete_structured_value_contracts(self):
        mutation = copy.deepcopy({"scenarios": SCENARIOS})
        mutation["scenarios"][0]["update_rules"][0]["allowed_fields"].pop("operation")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scenarios.json"
            path.write_text(json.dumps(mutation), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unconstrained structured fields"):
                load_scenarios(path)

        mutation = copy.deepcopy({"scenarios": SCENARIOS})
        mutation["scenarios"][0]["update_rules"][0]["record_kind"] = "paragraph_record"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scenarios.json"
            path.write_text(json.dumps(mutation), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "canonical record-kind selector"):
                load_scenarios(path)

    def test_round4_duplicate_rows_fail_through_both_entrypoints(self):
        insertions = (
            ("B01-update", 0, "updates", 0),
            ("B01-readiness", 0, "readiness_updates", 0),
            ("B02-readiness", 1, "readiness_updates", 0),
            ("B10-readiness", 9, "readiness_updates", 0),
        )
        for label, response_index, item_key, item_index in insertions:
            with self.subTest(mutation=label):
                document = {"responses": copy.deepcopy(GOOD)}
                row = copy.deepcopy(
                    document["responses"][response_index][item_key][item_index]
                )
                document["responses"][response_index][item_key].append(row)
                self.assert_document_rejected_by_both(document, label)

    def test_round4_format_only_text_fails_through_both_entrypoints(self):
        mutations = (
            ("reason-u200b", 0, "reason", "\u200b"),
            ("reason-u2060", 0, "reason", "\u2060"),
            ("reason-ufeff", 0, "reason", "\ufeff"),
            ("payload-u200b", 1, "design_payload", "\u200b"),
        )
        for label, response_index, field, value in mutations:
            with self.subTest(mutation=label):
                document = {"responses": copy.deepcopy(GOOD)}
                document["responses"][response_index]["updates"][0][field] = value
                self.assert_document_rejected_by_both(document, label)

    def test_round4_raw_envelope_is_one_sole_json_document(self):
        canonical = (CURRENT_CAPTURE / "raw-output.md").read_text().strip()
        variants = {
            "prefix": f"EXTRA-PREFIX\n{canonical}",
            "suffix": f"{canonical}\nEXTRA-SUFFIX",
            "multiple": f'{canonical}\n{{"responses":[]}}',
            "duplicate-key": (
                '{"responses":[],"responses":'
                + json.dumps(GOOD, ensure_ascii=False)
                + "}"
            ),
        }
        for label, raw_text in variants.items():
            with (
                self.subTest(entrypoint="verifier", mutation=label),
                tempfile.TemporaryDirectory() as directory,
            ):
                capture = Path(directory) / "fixture-current" / "capture"
                shutil.copytree(CURRENT_CAPTURE, capture)
                (capture / "raw-output.md").write_text(raw_text, encoding="utf-8")
                manifest_path = capture / "manifest.json"
                manifest = json.loads(manifest_path.read_text())
                manifest["raw_output_sha256"] = sha(capture / "raw-output.md")
                manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
                verify = self.run_cmd(
                    VERIFY,
                    CANONICAL_SCENARIO_PATH,
                    "--capture",
                    capture,
                    "--skill",
                    SKILL,
                )
                self.assertNotEqual(verify.returncode, 0)

            with (
                self.subTest(entrypoint="finalizer", mutation=label),
                tempfile.TemporaryDirectory() as directory,
            ):
                capture = Path(directory) / "capture"
                init = self.run_cmd(
                    CAPTURE,
                    "init",
                    "--capture",
                    capture,
                    "--skill",
                    SKILL,
                    "--scenarios",
                    CANONICAL_SCENARIO_PATH,
                )
                self.assertEqual(init.returncode, 0, init.stderr)
                (capture / "raw-output.md").write_text(raw_text, encoding="utf-8")
                finalize = self.run_cmd(
                    CAPTURE,
                    "finalize",
                    "--capture",
                    capture,
                    "--capture-kind",
                    "offline_policy_fixture",
                    "--model",
                    "policy-fixture",
                    "--runtime",
                    "offline-reproducible-fixture",
                    "--skill",
                    SKILL,
                    "--scenarios",
                    CANONICAL_SCENARIO_PATH,
                )
                self.assertNotEqual(finalize.returncode, 0)
                self.assertFalse((capture / "manifest.json").exists())

    def test_round4_authority_relations_fail_verifier_and_init(self):
        def response_limit_mismatch(document):
            document[0]["response_limits"]["min_updates"] += 1
            document[0]["response_limits"]["max_updates"] += 1

        def inexact_rule_cardinality(document):
            document[0]["update_rules"][0]["max_count"] += 1

        def inexact_question_cardinality(document):
            document[0]["question"]["max_count"] = 1

        def ask_owner_is_optional(document):
            document[3]["required_all_actions"].remove("ASK_OWNER")
            document[3]["optional_actions"].append("ASK_OWNER")

        def allowed_scope_is_hidden(document):
            document[0]["allowed_scopes"].append("SCOPE-HIDDEN-99")

        def readiness_selector_is_not_allowed(document):
            document[0]["context"]["scope_ids"].append("SCOPE-ALT-99")
            document[0]["readiness_rules"][0]["scope_id"] = "SCOPE-ALT-99"

        def gate_differs_from_question(document):
            document[3]["update_rules"][0]["allowed_fields"]["gate_category"] = [
                "argument_spine"
            ]

        for mutate in (
            response_limit_mismatch,
            inexact_rule_cardinality,
            inexact_question_cardinality,
            ask_owner_is_optional,
            allowed_scope_is_hidden,
            readiness_selector_is_not_allowed,
            gate_differs_from_question,
        ):
            with (
                self.subTest(mutation=mutate.__name__),
                tempfile.TemporaryDirectory() as directory,
            ):
                scenarios = copy.deepcopy(SCENARIOS)
                mutate(scenarios)
                path = Path(directory) / "scenarios.json"
                path.write_text(json.dumps({"scenarios": scenarios}), encoding="utf-8")
                verify = self.run_cmd(VERIFY, path)
                self.assertNotEqual(verify.returncode, 0)
                capture = Path(directory) / "capture"
                init = self.run_cmd(
                    CAPTURE,
                    "init",
                    "--capture",
                    capture,
                    "--skill",
                    SKILL,
                    "--scenarios",
                    path,
                )
                self.assertNotEqual(init.returncode, 0)
                self.assertFalse((capture / "prompt.md").exists())

    def test_round4_duplicate_json_keys_fail_scenario_and_manifest_loaders(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scenarios.json"
            path.write_text(
                '{"scenarios":[],"scenarios":'
                + json.dumps(SCENARIOS, ensure_ascii=False)
                + "}",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "duplicate JSON object key"):
                load_scenarios(path)
            self.assertNotEqual(self.run_cmd(VERIFY, path).returncode, 0)
            capture = Path(directory) / "capture"
            init = self.run_cmd(
                CAPTURE,
                "init",
                "--capture",
                capture,
                "--skill",
                SKILL,
                "--scenarios",
                path,
            )
            self.assertNotEqual(init.returncode, 0)
            self.assertFalse((capture / "prompt.md").exists())

        with tempfile.TemporaryDirectory() as directory:
            capture = Path(directory) / "fixture-current" / "capture"
            shutil.copytree(CURRENT_CAPTURE, capture)
            manifest_path = capture / "manifest.json"
            manifest_text = manifest_path.read_text(encoding="utf-8")
            manifest_path.write_text(
                manifest_text.replace("{", '{\n  "model": "ambiguous",', 1),
                encoding="utf-8",
            )
            verify = self.run_cmd(
                VERIFY,
                CANONICAL_SCENARIO_PATH,
                "--capture",
                capture,
                "--skill",
                SKILL,
            )
            self.assertNotEqual(verify.returncode, 0)

    def test_round4_seven_malformed_authorities_fail_verifier_and_init(self):
        def update_selector_in_allowed(document):
            document[0]["update_rules"][0]["allowed_fields"]["record_kind"] = [
                "paragraph",
                "frame",
            ]

        def readiness_selector_in_allowed(document):
            document[0]["readiness_rules"][0]["allowed_fields"]["scope_id"] = [
                "SCOPE-RESULTS",
                "SCOPE-ALT-99",
            ]

        def duplicate_exact_field(document):
            document[0]["update_rules"][0]["exact_fields"].append("grounding")

        def boolean_minimum(document):
            document[0]["update_rules"][0]["min_count"] = True

        def negative_minimum(document):
            document[0]["update_rules"][0]["min_count"] = -1

        def inverted_bounds(document):
            document[0]["update_rules"][0]["min_count"] = 2
            document[0]["update_rules"][0]["max_count"] = 1

        def duplicate_positive_rule(document):
            document[0]["readiness_rules"].append(
                copy.deepcopy(document[0]["readiness_rules"][0])
            )

        for mutate in (
            update_selector_in_allowed,
            readiness_selector_in_allowed,
            duplicate_exact_field,
            boolean_minimum,
            negative_minimum,
            inverted_bounds,
            duplicate_positive_rule,
        ):
            with (
                self.subTest(mutation=mutate.__name__),
                tempfile.TemporaryDirectory() as directory,
            ):
                scenarios = copy.deepcopy(SCENARIOS)
                mutate(scenarios)
                path = Path(directory) / "scenarios.json"
                path.write_text(json.dumps({"scenarios": scenarios}), encoding="utf-8")
                verify = self.run_cmd(VERIFY, path)
                self.assertNotEqual(verify.returncode, 0)
                capture = Path(directory) / "capture"
                init = self.run_cmd(
                    CAPTURE,
                    "init",
                    "--capture",
                    capture,
                    "--skill",
                    SKILL,
                    "--scenarios",
                    path,
                )
                self.assertNotEqual(init.returncode, 0)
                self.assertFalse((capture / "prompt.md").exists())

    def test_round4_question_limits_and_topology_are_bounded(self):
        mutations = []
        for value in (True, -1):
            mutation = copy.deepcopy(SCENARIOS)
            mutation[0]["question"]["min_count"] = value
            mutations.append(mutation)
            mutation = copy.deepcopy(SCENARIOS)
            mutation[0]["response_limits"]["min_updates"] = value
            mutations.append(mutation)
        mutation = copy.deepcopy(SCENARIOS)
        mutation[0]["question"]["min_count"] = 1
        mutation[0]["question"]["max_count"] = 0
        mutations.append(mutation)
        mutation = copy.deepcopy(SCENARIOS)
        mutation[0]["response_limits"]["min_updates"] = 3
        mutation[0]["response_limits"]["max_updates"] = 2
        mutations.append(mutation)
        mutation = copy.deepcopy(SCENARIOS)
        mutation[0]["unexpected"] = True
        mutations.append(mutation)
        for index, scenarios in enumerate(mutations):
            with (
                self.subTest(mutation=index),
                tempfile.TemporaryDirectory() as directory,
            ):
                path = Path(directory) / "scenarios.json"
                path.write_text(json.dumps({"scenarios": scenarios}), encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_scenarios(path)

    def test_round5_authority_witness_rejects_all_reported_unsatisfiable_rules(self):
        def add_second_readiness_state(document):
            document[0]["readiness_rules"].append(
                {
                    "scope_id": "SCOPE-RESULTS",
                    "min_count": 1,
                    "max_count": 1,
                    "allowed_fields": {
                        "readiness": ["partial"],
                        "blocker": ["visible blocker"],
                        "next_action": ["visible next action"],
                    },
                    "non_null_fields": [
                        "scope_id",
                        "readiness",
                        "blocker",
                        "next_action",
                    ],
                    "exact_fields": [],
                }
            )
            limits = document[0]["response_limits"]
            limits["min_readiness_updates"] = 2
            limits["max_readiness_updates"] = 2

        def duplicate_id_across_scenarios(document):
            document[1]["update_rules"][0]["allowed_fields"]["record_id"] = [
                "FRM-RESULT-A2-01"
            ]

        def add_negative_required_update(document):
            document[0]["update_rules"].append(
                {
                    "record_kind": "paragraph",
                    "min_count": 0,
                    "max_count": 0,
                    "allowed_fields": {"record_id": ["P-RESULT-01"]},
                }
            )

        def force_partial_with_writer_ready_topology(document):
            document[0]["readiness_rules"][0]["allowed_fields"]["readiness"] = [
                "partial"
            ]

        def force_design_only_scientific_support(document):
            document[7]["update_rules"][0]["allowed_fields"]["support"] = [
                "evidence-supported"
            ]

        def add_negative_required_readiness(document):
            document[0]["readiness_rules"].append(
                {
                    "scope_id": "SCOPE-RESULTS",
                    "min_count": 0,
                    "max_count": 0,
                    "allowed_fields": {"readiness": ["writer-ready"]},
                }
            )

        def require_two_updates_from_one_id(document):
            document[1]["update_rules"][0]["min_count"] = 2
            document[1]["update_rules"][0]["max_count"] = 2
            document[1]["response_limits"]["min_updates"] = 2
            document[1]["response_limits"]["max_updates"] = 2

        def require_two_readiness_rows_for_one_scope(document):
            document[1]["readiness_rules"][0]["min_count"] = 2
            document[1]["readiness_rules"][0]["max_count"] = 2
            limits = document[1]["response_limits"]
            limits["min_readiness_updates"] = 2
            limits["max_readiness_updates"] = 2

        def use_record_pointer_as_output_pointer(document):
            document[0]["readiness_rules"][0]["allowed_fields"]["output_pointer"] = [
                "DEC-B04"
            ]

        def allow_multiple_scalar_values(document):
            document[0]["update_rules"][0]["allowed_fields"]["origin"].append(
                "owner-stated"
            )

        probes = (
            ("architect-same-scope-two-states", add_second_readiness_state),
            ("architect-global-duplicate-id", duplicate_id_across_scenarios),
            ("architect-negative-update", add_negative_required_update),
            (
                "architect-readiness-shape",
                force_partial_with_writer_ready_topology,
            ),
            ("architect-design-firewall", force_design_only_scientific_support),
            ("critic-negative-update", add_negative_required_update),
            ("critic-negative-readiness", add_negative_required_readiness),
            ("critic-count-two-one-id", require_two_updates_from_one_id),
            (
                "critic-count-two-one-scope",
                require_two_readiness_rows_for_one_scope,
            ),
            ("critic-two-states-one-scope", add_second_readiness_state),
            ("critic-record-output-pointer", use_record_pointer_as_output_pointer),
            ("singleton-scalar-authority", allow_multiple_scalar_values),
        )
        for label, mutate in probes:
            with self.subTest(probe=label):
                scenarios = copy.deepcopy(SCENARIOS)
                mutate(scenarios)
                self.assert_scenario_text_rejected_by_verifier_and_init(
                    json.dumps(
                        {"scenarios": scenarios},
                        ensure_ascii=False,
                        allow_nan=False,
                    ),
                    label,
                )

    def test_round5_canonical_authority_has_a_shared_runtime_witness(self):
        scenarios = load_scenarios(CANONICAL_SCENARIO_PATH)
        witness = authority_witness_document(scenarios)
        self.assertEqual(strict_response_document_errors(witness, scenarios), [])
        self.assertEqual(
            [item["scenario_id"] for item in witness["responses"]],
            [item["id"] for item in scenarios],
        )

    def test_round5_scope_and_public_pointer_relations_are_exact(self):
        def detached_readiness_authority(document):
            document[0]["context"]["scope_ids"].append("SCOPE-ALT-99")
            document[0]["allowed_scopes"].append("SCOPE-ALT-99")
            document[0]["readiness_rules"][0]["scope_id"] = "SCOPE-ALT-99"

        def format_only_anchor_authority(document):
            document[0]["readiness_rules"][0]["allowed_fields"]["output_pointer"] = [
                "04_WRITING_DESIGN_PACK.md#\u200b"
            ]

        def detached_pointer_anchor_authority(document):
            document[0]["readiness_rules"][0]["allowed_fields"]["output_pointer"] = [
                "04_WRITING_DESIGN_PACK.md#SCOPE-ALT-99"
            ]

        for mutate in (
            detached_readiness_authority,
            format_only_anchor_authority,
            detached_pointer_anchor_authority,
        ):
            with self.subTest(authority=mutate.__name__):
                scenarios = copy.deepcopy(SCENARIOS)
                mutate(scenarios)
                self.assert_scenario_text_rejected_by_verifier_and_init(
                    json.dumps(
                        {"scenarios": scenarios},
                        ensure_ascii=False,
                        allow_nan=False,
                    ),
                    mutate.__name__,
                )

        detached = {"responses": copy.deepcopy(GOOD)}
        detached["responses"][0]["readiness_updates"][0]["scope_id"] = "SCOPE-ALT-99"
        format_anchor = {"responses": copy.deepcopy(GOOD)}
        format_anchor["responses"][0]["readiness_updates"][0]["output_pointer"] = (
            "04_WRITING_DESIGN_PACK.md#\u200b"
        )
        wrong_anchor = {"responses": copy.deepcopy(GOOD)}
        wrong_anchor["responses"][0]["readiness_updates"][0]["output_pointer"] = (
            "04_WRITING_DESIGN_PACK.md#SCOPE-ALT-99"
        )
        for label, document in (
            ("detached-readiness-response", detached),
            ("format-only-pointer-anchor", format_anchor),
            ("wrong-scope-pointer-anchor", wrong_anchor),
        ):
            with self.subTest(response=label):
                self.assert_document_rejected_by_both(document, label)

        self.assertEqual(
            parse_public_pointer("04_WRITING_DESIGN_PACK.md#结果范围"),
            ("04_WRITING_DESIGN_PACK.md", "结果范围"),
        )
        self.assertIsNone(
            parse_public_pointer("04_WRITING_DESIGN_PACK.md#结果\u2060范围")
        )

    def test_round5_strict_json_rejects_nonfinite_contract_surfaces(self):
        scenario_document = json.dumps(
            {"scenarios": SCENARIOS}, ensure_ascii=False, allow_nan=False
        )
        canonical_raw = (CURRENT_CAPTURE / "raw-output.md").read_text()
        canonical_prompt = (CURRENT_CAPTURE / "prompt.md").read_text()
        skill_text = SKILL.read_text(encoding="utf-8")
        reference_text = VENUE_TEMPLATE.read_text(encoding="utf-8")
        for constant in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(surface="scenario", constant=constant):
                scenario_text = scenario_document.replace(
                    '"context": {',
                    f'"context": {{"opaque_numeric": {constant}, ',
                    1,
                )
                self.assert_scenario_text_rejected_by_verifier_and_init(
                    scenario_text, f"scenario-{constant}"
                )

            with self.subTest(surface="raw", constant=constant):
                raw_text = re.sub(
                    r'"reason": "[^"]+"',
                    f'"reason": {constant}',
                    canonical_raw,
                    count=1,
                )
                self.assert_raw_text_rejected_by_both(raw_text, f"raw-{constant}")

            with self.subTest(surface="prompt", constant=constant):
                visible_start = canonical_prompt.index(SCENARIOS_START)
                context_start = canonical_prompt.index('"context": {', visible_start)
                prompt = (
                    canonical_prompt[:context_start]
                    + f'"context": {{"opaque_numeric": {constant}, '
                    + canonical_prompt[context_start + len('"context": {') :]
                )
                errors = prompt_contract_errors(
                    prompt, skill_text, reference_text, SCENARIOS
                )
                self.assertTrue(
                    any("scenario JSON is invalid" in error for error in errors),
                    errors,
                )

            for surface in ("actions", "manifest"):
                with (
                    self.subTest(surface=surface, constant=constant),
                    tempfile.TemporaryDirectory() as directory,
                ):
                    capture = Path(directory) / "capture"
                    shutil.copytree(CURRENT_CAPTURE, capture)
                    path = capture / f"{surface}.json"
                    text = path.read_text(encoding="utf-8")
                    if surface == "actions":
                        text = re.sub(
                            r'"reason": "[^"]+"',
                            f'"reason": {constant}',
                            text,
                            count=1,
                        )
                        path.write_text(text, encoding="utf-8")
                        manifest_path = capture / "manifest.json"
                        manifest = json.loads(manifest_path.read_text())
                        manifest["actions_sha256"] = sha(path)
                        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
                    else:
                        path.write_text(
                            text.replace(
                                '"scenario_count": 15',
                                f'"scenario_count": {constant}',
                                1,
                            ),
                            encoding="utf-8",
                        )
                    verify = self.run_cmd(
                        VERIFY,
                        CANONICAL_SCENARIO_PATH,
                        "--capture",
                        capture,
                        "--skill",
                        SKILL,
                    )
                    self.assertNotEqual(verify.returncode, 0)

        overflow = scenario_document.replace(
            '"context": {', '"context": {"opaque_numeric": 1e400, ', 1
        )
        self.assert_scenario_text_rejected_by_verifier_and_init(
            overflow, "scenario-overflow"
        )
        in_memory = copy.deepcopy(SCENARIOS)
        in_memory[0]["context"]["opaque_numeric"] = float("nan")
        with self.assertRaises(ValueError):
            model_visible_scenario_json(in_memory)

    def test_round5_live_provenance_requires_visible_labels(self):
        invalid_labels = (
            ("\u200b", "codex-cli"),
            ("test-model", "\u2060"),
        )
        for model, runtime in invalid_labels:
            with (
                self.subTest(entrypoint="finalizer", model=model, runtime=runtime),
                tempfile.TemporaryDirectory() as directory,
            ):
                capture = Path(directory) / "capture"
                init = self.run_cmd(
                    CAPTURE,
                    "init",
                    "--capture",
                    capture,
                    "--skill",
                    SKILL,
                    "--scenarios",
                    CANONICAL_SCENARIO_PATH,
                )
                self.assertEqual(init.returncode, 0, init.stderr)
                shutil.copy(CURRENT_CAPTURE / "raw-output.md", capture)
                finalize = self.run_cmd(
                    CAPTURE,
                    "finalize",
                    "--capture",
                    capture,
                    "--capture-kind",
                    "live_model",
                    "--model",
                    model,
                    "--runtime",
                    runtime,
                    "--skill",
                    SKILL,
                    "--scenarios",
                    CANONICAL_SCENARIO_PATH,
                )
                self.assertNotEqual(finalize.returncode, 0)
                self.assertFalse((capture / "manifest.json").exists())

            with (
                self.subTest(entrypoint="verifier", model=model, runtime=runtime),
                tempfile.TemporaryDirectory() as directory,
            ):
                capture = Path(directory) / "live-capture"
                shutil.copytree(CURRENT_CAPTURE, capture)
                manifest_path = capture / "manifest.json"
                manifest = json.loads(manifest_path.read_text())
                manifest["capture_kind"] = "live_model"
                manifest["model"] = model
                manifest["runtime"] = runtime
                manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
                verify = self.run_cmd(
                    VERIFY,
                    CANONICAL_SCENARIO_PATH,
                    "--capture",
                    capture,
                    "--skill",
                    SKILL,
                )
                self.assertNotEqual(verify.returncode, 0)

        with tempfile.TemporaryDirectory() as directory:
            capture = Path(directory) / "live-capture"
            init = self.run_cmd(
                CAPTURE,
                "init",
                "--capture",
                capture,
                "--skill",
                SKILL,
                "--scenarios",
                CANONICAL_SCENARIO_PATH,
            )
            self.assertEqual(init.returncode, 0, init.stderr)
            shutil.copy(CURRENT_CAPTURE / "raw-output.md", capture)
            finalize = self.run_cmd(
                CAPTURE,
                "finalize",
                "--capture",
                capture,
                "--capture-kind",
                "live_model",
                "--model",
                "test-model",
                "--runtime",
                "test-runtime",
                "--skill",
                SKILL,
                "--scenarios",
                CANONICAL_SCENARIO_PATH,
            )
            self.assertEqual(finalize.returncode, 0, finalize.stderr)
            verify = self.run_cmd(
                VERIFY,
                CANONICAL_SCENARIO_PATH,
                "--capture",
                capture,
                "--skill",
                SKILL,
            )
            self.assertEqual(verify.returncode, 0, verify.stdout + verify.stderr)

    def test_b10_preserves_denominator_missingness_and_conclusion_ceiling(self):
        analysis = GOOD_BY_ID["B10"]["updates"][0]
        self.assertEqual(
            analysis["denominator"],
            "15 eligible;13 valid;2 missing supported object locator",
        )
        self.assertEqual(analysis["missingness"], "2 missing supported object locator")
        self.assertEqual(
            analysis["effective_conclusion"],
            "descriptive design distribution only; no semantic, causal, venue-fit, or acceptance conclusion",
        )
        for field, value in (
            ("denominator", None),
            ("missingness", "none"),
            ("effective_conclusion", "proves semantic quality and venue fit"),
        ):
            mutation = copy.deepcopy(GOOD_BY_ID["B10"])
            mutation["updates"][0][field] = value
            with self.subTest(field=field):
                self.assertTrue(validate_response(mutation, POLICY))

    def test_new_quantitative_and_promotion_fields_are_null_elsewhere(self):
        for response in GOOD:
            for update in response["updates"]:
                is_b10 = response["scenario_id"] == "B10"
                is_b14_template = (
                    response["scenario_id"] == "B14"
                    and update["record_id"] == "TPL-PUB-14"
                )
                if not is_b10:
                    self.assertIsNone(update["denominator"])
                    self.assertIsNone(update["effective_conclusion"])
                if not is_b14_template:
                    self.assertIsNone(update["promotion_pointer"])

    def test_b14_requires_separate_identity_and_explicit_promotion_pointer(self):
        updates = GOOD_BY_ID["B14"]["updates"]
        template = next(item for item in updates if item["record_id"] == "TPL-PUB-14")
        material = next(item for item in updates if item["record_id"] == "M-PUB-14")
        self.assertEqual(template["promotion_pointer"], "M-PUB-14")
        self.assertIsNone(material["promotion_pointer"])
        self.assertNotIn("ASK_OWNER", GOOD_BY_ID["B14"]["selected_actions"])
        for value in (None, "TPL-PUB-14", "M-PUB-14;TPL-PUB-14"):
            mutation = copy.deepcopy(GOOD_BY_ID["B14"])
            next(
                item
                for item in mutation["updates"]
                if item["record_id"] == "TPL-PUB-14"
            )["promotion_pointer"] = value
            with self.subTest(pointer=value):
                self.assertTrue(validate_response(mutation, POLICY))

    def test_b08_to_b15_positive_rules_constrain_epistemic_identity(self):
        for sid in (f"B{index:02d}" for index in range(8, 16)):
            scenario = POLICY[sid]
            for rule in scenario["update_rules"]:
                if rule.get("max_count") == 0:
                    continue
                fields = rule.get("allowed_fields", {})
                self.assertIn("origin", fields, f"{sid}: {rule}")
                self.assertIn("epistemic_label", fields, f"{sid}: {rule}")

    def test_schema_runtime_topology_and_fingerprint_are_bound(self):
        schema = build_output_schema(SCENARIOS)
        self.assertEqual(schema_runtime_topology_errors(schema), [])
        fingerprint = response_contract_fingerprint(SCENARIOS)
        self.assertRegex(fingerprint, r"^[0-9a-f]{64}$")
        mutated = copy.deepcopy(schema)
        mutated["properties"]["responses"]["items"]["properties"]["updates"]["items"][
            "additionalProperties"
        ] = True
        self.assertTrue(schema_runtime_topology_errors(mutated))

    def test_capture_prompt_embeds_current_contract_but_no_scenario_oracle(self):
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
                prompt_contract_errors(prompt, skill_text, reference_text, SCENARIOS),
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
            self.assertEqual(len(visible), len(SCENARIOS))
            for scenario in visible:
                self.assertEqual(set(scenario), {"id", "situation", "context"})
                self.assertFalse(set(scenario) & ORACLE_SCENARIO_KEYS)

    def test_prompt_context_rejects_nested_oracle_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            scenario_path = Path(directory) / "scenarios.json"
            mutation = copy.deepcopy(SCENARIOS)
            mutation[0]["context"]["nested"] = {"required_all_actions": ["INSPECT"]}
            scenario_path.write_text(
                json.dumps({"scenarios": mutation}),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "oracle"):
                load_scenarios(scenario_path)

    def test_closed_prompt_rejects_marker_external_oracle_in_both_entrypoints(self):
        oracle = (
            "\nVERIFIER-ONLY ORACLE: B01 required_all_actions = "
            "INSPECT,DERIVE,PROJECT,VALIDATE\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            capture = Path(directory) / "capture"
            init = self.run_cmd(
                CAPTURE,
                "init",
                "--capture",
                capture,
                "--skill",
                SKILL,
                "--scenarios",
                CANONICAL_SCENARIO_PATH,
            )
            self.assertEqual(init.returncode, 0, init.stderr)
            with (capture / "prompt.md").open("a", encoding="utf-8") as handle:
                handle.write(oracle)
            (capture / "raw-output.md").write_text(
                json.dumps({"responses": GOOD}), encoding="utf-8"
            )
            finalize = self.run_cmd(
                CAPTURE,
                "finalize",
                "--capture",
                capture,
                "--capture-kind",
                "offline_policy_fixture",
                "--model",
                "policy-fixture",
                "--runtime",
                "offline-reproducible-fixture",
                "--skill",
                SKILL,
                "--scenarios",
                CANONICAL_SCENARIO_PATH,
            )
            self.assertNotEqual(finalize.returncode, 0)
            self.assertIn("canonical closed prompt contract", finalize.stderr)
            self.assertFalse((capture / "manifest.json").exists())

        with tempfile.TemporaryDirectory() as directory:
            capture = Path(directory) / "fixture-current" / "capture"
            shutil.copytree(CURRENT_CAPTURE, capture)
            with (capture / "prompt.md").open("a", encoding="utf-8") as handle:
                handle.write(oracle)
            manifest_path = capture / "manifest.json"
            manifest = json.loads(manifest_path.read_text())
            manifest["prompt_sha256"] = sha(capture / "prompt.md")
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            verify = self.run_cmd(
                VERIFY,
                CANONICAL_SCENARIO_PATH,
                "--capture",
                capture,
                "--skill",
                SKILL,
            )
            self.assertNotEqual(verify.returncode, 0)
            self.assertIn("canonical closed prompt contract", verify.stdout)

    def test_verifier_rejects_removed_scenario_override(self):
        with tempfile.TemporaryDirectory() as directory:
            unrelated = Path(directory) / "unrelated.json"
            unrelated.write_text('{"not":"the scenarios used"}', encoding="utf-8")
            result = self.run_cmd(
                VERIFY,
                CANONICAL_SCENARIO_PATH,
                "--scenarios",
                unrelated,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unrecognized arguments: --scenarios", result.stderr)

    def test_finalize_rejects_schema_and_semantic_violations(self):
        invalid_documents = []
        unexpected = {"responses": copy.deepcopy(GOOD)}
        unexpected["responses"][0]["oracle"] = True
        invalid_documents.append(unexpected)
        extra_scope = {"responses": copy.deepcopy(GOOD)}
        extra_scope["responses"][10]["target_scopes"].append("SCOPE-NOT-IN-CONTEXT")
        invalid_documents.append(extra_scope)
        for invalid in invalid_documents:
            with tempfile.TemporaryDirectory() as directory:
                capture = Path(directory) / "capture"
                init = self.run_cmd(
                    CAPTURE,
                    "init",
                    "--capture",
                    capture,
                    "--skill",
                    SKILL,
                    "--scenarios",
                    CANONICAL_SCENARIO_PATH,
                )
                self.assertEqual(init.returncode, 0, init.stderr)
                (capture / "raw-output.md").write_text(
                    json.dumps(invalid), encoding="utf-8"
                )
                finalize = self.run_cmd(
                    CAPTURE,
                    "finalize",
                    "--capture",
                    capture,
                    "--capture-kind",
                    "offline_policy_fixture",
                    "--model",
                    "policy-fixture",
                    "--runtime",
                    "offline-reproducible-fixture",
                    "--skill",
                    SKILL,
                    "--scenarios",
                    CANONICAL_SCENARIO_PATH,
                )
                self.assertNotEqual(finalize.returncode, 0)
                self.assertFalse((capture / "manifest.json").exists())

    def test_verifier_rejects_exact_critic_mutations_after_hash_recompute(self):
        def extra_response_key(document):
            document["responses"][0]["oracle"] = True

        def bool_question(document):
            document["responses"][3]["question"]["count"] = True

        def extra_scope(document):
            document["responses"][10]["target_scopes"].append("SCOPE-NOT-IN-CONTEXT")

        def extra_link(document):
            document["responses"][10]["updates"][0]["linked_records"].append(
                "M-RESULT-B"
            )

        def wrong_origin(document):
            document["responses"][14]["updates"][0]["origin"] = "owner-stated"

        for mutate in (
            extra_response_key,
            bool_question,
            extra_scope,
            extra_link,
            wrong_origin,
        ):
            with (
                self.subTest(mutation=mutate.__name__),
                tempfile.TemporaryDirectory() as directory,
            ):
                capture = Path(directory) / "fixture-current" / "capture"
                shutil.copytree(CURRENT_CAPTURE, capture)
                document = json.loads((capture / "actions.json").read_text())
                mutate(document)
                (capture / "actions.json").write_text(
                    json.dumps(document, ensure_ascii=False, sort_keys=True, indent=2)
                    + "\n",
                    encoding="utf-8",
                )
                (capture / "raw-output.md").write_text(
                    json.dumps(document, ensure_ascii=False, sort_keys=True, indent=2)
                    + "\n",
                    encoding="utf-8",
                )
                manifest_path = capture / "manifest.json"
                manifest = json.loads(manifest_path.read_text())
                manifest["actions_sha256"] = sha(capture / "actions.json")
                manifest["raw_output_sha256"] = sha(capture / "raw-output.md")
                manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
                result = self.run_cmd(
                    VERIFY,
                    CANONICAL_SCENARIO_PATH,
                    "--capture",
                    capture,
                    "--skill",
                    SKILL,
                )
                self.assertNotEqual(result.returncode, 0)

    def test_closed_update_and_readiness_surfaces_reject_round2_mutations(self):
        def b08_scientific_support(document):
            document["responses"][7]["updates"][0]["support"] = "evidence-supported"

        def b10_scientific_support(document):
            document["responses"][9]["updates"][0]["support"] = "evidence-supported"

        def b14_reverse_promotion(document):
            document["responses"][13]["updates"][1]["promotion_pointer"] = "TPL-PUB-14"

        def b15_paragraph_grounding(document):
            document["responses"][14]["updates"][0]["grounding"] = ["paragraph 9"]

        def b15_semantic_analysis(document):
            document["responses"][14]["updates"][0]["analysis_mode"] = "case_set"

        def b01_contradictory_blocker(document):
            document["responses"][0]["readiness_updates"][0]["blocker"] = (
                "CONTRADICTORY_BLOCKER"
            )

        def b01_missing_output(document):
            document["responses"][0]["readiness_updates"][0]["output_pointer"] = None

        def b04_missing_consequence(document):
            document["responses"][3]["readiness_updates"][0]["blocker"] = None
            document["responses"][3]["readiness_updates"][0]["next_action"] = None

        def b01_quantitative_leak(document):
            document["responses"][0]["updates"][0]["denominator"] = "999 eligible"

        mutations = (
            (b08_scientific_support, "cannot claim scientific support"),
            (b10_scientific_support, "cannot claim scientific support"),
            (b14_reverse_promotion, "invalid promotion pointer owner"),
            (b15_paragraph_grounding, "paragraph/object grounding"),
            (b15_semantic_analysis, "B10-only quantitative state"),
            (b01_contradictory_blocker, "requires only an output pointer"),
            (b01_missing_output, "requires only an output pointer"),
            (b04_missing_consequence, "requires blocker and next action"),
            (b01_quantitative_leak, "B10-only quantitative state"),
        )
        for mutate, expected in mutations:
            with (
                self.subTest(entrypoint="verifier", mutation=mutate.__name__),
                tempfile.TemporaryDirectory() as directory,
            ):
                capture = Path(directory) / "fixture-current" / "capture"
                shutil.copytree(CURRENT_CAPTURE, capture)
                document = json.loads((capture / "actions.json").read_text())
                mutate(document)
                normalized = (
                    json.dumps(document, ensure_ascii=False, sort_keys=True, indent=2)
                    + "\n"
                )
                (capture / "actions.json").write_text(normalized, encoding="utf-8")
                (capture / "raw-output.md").write_text(normalized, encoding="utf-8")
                manifest_path = capture / "manifest.json"
                manifest = json.loads(manifest_path.read_text())
                manifest["actions_sha256"] = sha(capture / "actions.json")
                manifest["raw_output_sha256"] = sha(capture / "raw-output.md")
                manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
                result = self.run_cmd(
                    VERIFY,
                    CANONICAL_SCENARIO_PATH,
                    "--capture",
                    capture,
                    "--skill",
                    SKILL,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stdout + result.stderr)

            with (
                self.subTest(entrypoint="finalizer", mutation=mutate.__name__),
                tempfile.TemporaryDirectory() as directory,
            ):
                capture = Path(directory) / "capture"
                init = self.run_cmd(
                    CAPTURE,
                    "init",
                    "--capture",
                    capture,
                    "--skill",
                    SKILL,
                    "--scenarios",
                    CANONICAL_SCENARIO_PATH,
                )
                self.assertEqual(init.returncode, 0, init.stderr)
                document = {"responses": copy.deepcopy(GOOD)}
                mutate(document)
                (capture / "raw-output.md").write_text(
                    json.dumps(document), encoding="utf-8"
                )
                finalize = self.run_cmd(
                    CAPTURE,
                    "finalize",
                    "--capture",
                    capture,
                    "--capture-kind",
                    "offline_policy_fixture",
                    "--model",
                    "policy-fixture",
                    "--runtime",
                    "offline-reproducible-fixture",
                    "--skill",
                    SKILL,
                    "--scenarios",
                    CANONICAL_SCENARIO_PATH,
                )
                self.assertNotEqual(finalize.returncode, 0)
                self.assertIn(expected, finalize.stdout + finalize.stderr)
                self.assertFalse((capture / "manifest.json").exists())

    def test_round3_reported_value_mutations_fail_through_both_entrypoints(self):
        def b03_wrong_epistemic(document):
            document["responses"][2]["updates"][0]["epistemic_label"] = "owner-stated"

        def b02_wrong_origin(document):
            document["responses"][1]["updates"][0]["origin"] = "owner-stated"

        def b04_wrong_origin(document):
            document["responses"][3]["updates"][0]["origin"] = "owner-stated"

        def b01_wrong_target(document):
            document["responses"][0]["updates"][0]["target_kind"] = "caption_blueprint"

        def b01_delete(document):
            document["responses"][0]["updates"][0]["operation"] = "delete"

        def b01_rejected(document):
            document["responses"][0]["updates"][0]["resolution"] = "rejected"

        def b08_claim_identity(document):
            document["responses"][7]["updates"][0]["record_id"] = "C-NOVELTY-01"

        def b15_blank_locator(document):
            document["responses"][14]["updates"][0]["locator"] = ""

        def b01_blank_output(document):
            document["responses"][0]["readiness_updates"][0]["output_pointer"] = " "

        def b04_blank_consequence(document):
            document["responses"][3]["readiness_updates"][0]["blocker"] = " "
            document["responses"][3]["readiness_updates"][0]["next_action"] = " "

        probes = (
            b03_wrong_epistemic,
            b02_wrong_origin,
            b04_wrong_origin,
            b01_wrong_target,
            b01_delete,
            b01_rejected,
            b08_claim_identity,
            b15_blank_locator,
            b01_blank_output,
            b04_blank_consequence,
        )
        for mutate in probes:
            with (
                self.subTest(entrypoint="verifier", mutation=mutate.__name__),
                tempfile.TemporaryDirectory() as directory,
            ):
                capture = Path(directory) / "fixture-current" / "capture"
                shutil.copytree(CURRENT_CAPTURE, capture)
                document = json.loads((capture / "actions.json").read_text())
                mutate(document)
                normalized = (
                    json.dumps(document, ensure_ascii=False, sort_keys=True, indent=2)
                    + "\n"
                )
                (capture / "actions.json").write_text(normalized, encoding="utf-8")
                (capture / "raw-output.md").write_text(normalized, encoding="utf-8")
                manifest_path = capture / "manifest.json"
                manifest = json.loads(manifest_path.read_text())
                manifest["actions_sha256"] = sha(capture / "actions.json")
                manifest["raw_output_sha256"] = sha(capture / "raw-output.md")
                manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
                result = self.run_cmd(
                    VERIFY,
                    CANONICAL_SCENARIO_PATH,
                    "--capture",
                    capture,
                    "--skill",
                    SKILL,
                )
                self.assertNotEqual(result.returncode, 0)

            with (
                self.subTest(entrypoint="finalizer", mutation=mutate.__name__),
                tempfile.TemporaryDirectory() as directory,
            ):
                capture = Path(directory) / "capture"
                init = self.run_cmd(
                    CAPTURE,
                    "init",
                    "--capture",
                    capture,
                    "--skill",
                    SKILL,
                    "--scenarios",
                    CANONICAL_SCENARIO_PATH,
                )
                self.assertEqual(init.returncode, 0, init.stderr)
                document = {"responses": copy.deepcopy(GOOD)}
                mutate(document)
                (capture / "raw-output.md").write_text(
                    json.dumps(document), encoding="utf-8"
                )
                finalize = self.run_cmd(
                    CAPTURE,
                    "finalize",
                    "--capture",
                    capture,
                    "--capture-kind",
                    "offline_policy_fixture",
                    "--model",
                    "policy-fixture",
                    "--runtime",
                    "offline-reproducible-fixture",
                    "--skill",
                    SKILL,
                    "--scenarios",
                    CANONICAL_SCENARIO_PATH,
                )
                self.assertNotEqual(finalize.returncode, 0)
                self.assertFalse((capture / "manifest.json").exists())

    def test_every_active_structured_value_is_closed_through_both_entrypoints(self):
        response_indexes = {
            response["scenario_id"]: index for index, response in enumerate(GOOD)
        }
        mutation_specs: list[tuple[str, str, int, str, object]] = []
        for scenario in SCENARIOS:
            sid = scenario["id"]
            response = GOOD_BY_ID[sid]
            for rule_key, item_key, readiness in (
                ("update_rules", "updates", False),
                ("readiness_rules", "readiness_updates", True),
            ):
                for rule_index, rule in enumerate(scenario[rule_key]):
                    if rule.get("max_count") == 0:
                        continue
                    matches = [
                        index
                        for index, item in enumerate(response[item_key])
                        if rule_matches(item, rule, readiness=readiness)
                    ]
                    self.assertEqual(
                        len(matches),
                        1,
                        f"{sid} {rule_key}[{rule_index}] must identify one row",
                    )
                    item_index = matches[0]
                    item = response[item_key][item_index]
                    for field in sorted(
                        set(rule["non_null_fields"]) - UPDATE_FREE_TEXT_FIELDS
                    ):
                        mutation_specs.append(
                            (
                                sid,
                                item_key,
                                item_index,
                                field,
                                self.alternate_structured_value(field, item[field]),
                            )
                        )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            initialized = root / "initialized"
            init = self.run_cmd(
                CAPTURE,
                "init",
                "--capture",
                initialized,
                "--skill",
                SKILL,
                "--scenarios",
                CANONICAL_SCENARIO_PATH,
            )
            self.assertEqual(init.returncode, 0, init.stderr)

            for counter, (sid, item_key, item_index, field, replacement) in enumerate(
                mutation_specs
            ):
                label = f"{sid}:{item_key}[{item_index}].{field}"
                document = {"responses": copy.deepcopy(GOOD)}
                response = document["responses"][response_indexes[sid]]
                response[item_key][item_index][field] = replacement

                with self.subTest(entrypoint="verifier", mutation=label):
                    capture = (
                        root / f"verifier-{counter}" / "fixture-current" / "capture"
                    )
                    shutil.copytree(CURRENT_CAPTURE, capture)
                    normalized = (
                        json.dumps(
                            document,
                            ensure_ascii=False,
                            sort_keys=True,
                            indent=2,
                        )
                        + "\n"
                    )
                    (capture / "actions.json").write_text(normalized, encoding="utf-8")
                    (capture / "raw-output.md").write_text(normalized, encoding="utf-8")
                    manifest_path = capture / "manifest.json"
                    manifest = json.loads(manifest_path.read_text())
                    manifest["actions_sha256"] = sha(capture / "actions.json")
                    manifest["raw_output_sha256"] = sha(capture / "raw-output.md")
                    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
                    result = self.run_cmd(
                        VERIFY,
                        CANONICAL_SCENARIO_PATH,
                        "--capture",
                        capture,
                        "--skill",
                        SKILL,
                    )
                    self.assertNotEqual(result.returncode, 0, label)

                with self.subTest(entrypoint="finalizer", mutation=label):
                    capture = root / f"finalizer-{counter}"
                    shutil.copytree(initialized, capture)
                    (capture / "raw-output.md").write_text(
                        json.dumps(document), encoding="utf-8"
                    )
                    finalize = self.run_cmd(
                        CAPTURE,
                        "finalize",
                        "--capture",
                        capture,
                        "--capture-kind",
                        "offline_policy_fixture",
                        "--model",
                        "policy-fixture",
                        "--runtime",
                        "offline-reproducible-fixture",
                        "--skill",
                        SKILL,
                        "--scenarios",
                        CANONICAL_SCENARIO_PATH,
                    )
                    self.assertNotEqual(finalize.returncode, 0, label)
                    self.assertFalse((capture / "manifest.json").exists())

        self.assertGreaterEqual(len(mutation_specs), 380)

    def test_manifest_requires_exact_fields_labels_and_six_hash_families(self):
        original = json.loads((CURRENT_CAPTURE / "manifest.json").read_text())
        self.assertEqual(set(original), MANIFEST_FIELDS)
        self.assertEqual(original["capture_kind"], "offline_policy_fixture")
        self.assertEqual(original["model"], "policy-fixture")
        self.assertEqual(original["runtime"], "offline-reproducible-fixture")
        self.assertEqual(
            original["response_contract_sha256"],
            response_contract_fingerprint(SCENARIOS),
        )
        with tempfile.TemporaryDirectory() as directory:
            capture = Path(directory) / "fixture-current" / "capture"
            shutil.copytree(CURRENT_CAPTURE, capture)
            manifest_path = capture / "manifest.json"
            for field in SIX_CAPTURE_HASHES:
                with self.subTest(field=field, mutation="missing"):
                    mutation = copy.deepcopy(original)
                    mutation.pop(field)
                    manifest_path.write_text(json.dumps(mutation), encoding="utf-8")
                    result = self.run_cmd(
                        VERIFY,
                        CANONICAL_SCENARIO_PATH,
                        "--capture",
                        capture,
                        "--skill",
                        SKILL,
                    )
                    self.assertNotEqual(result.returncode, 0)
                with self.subTest(field=field, mutation="mismatch"):
                    mutation = copy.deepcopy(original)
                    mutation[field] = "0" * 64
                    manifest_path.write_text(json.dumps(mutation), encoding="utf-8")
                    result = self.run_cmd(
                        VERIFY,
                        CANONICAL_SCENARIO_PATH,
                        "--capture",
                        capture,
                        "--skill",
                        SKILL,
                    )
                    self.assertNotEqual(result.returncode, 0)
            mutation = copy.deepcopy(original)
            mutation["unexpected"] = True
            manifest_path.write_text(json.dumps(mutation), encoding="utf-8")
            result = self.run_cmd(
                VERIFY,
                CANONICAL_SCENARIO_PATH,
                "--capture",
                capture,
                "--skill",
                SKILL,
            )
            self.assertNotEqual(result.returncode, 0)
            for field, value in (
                ("scenario_count", True),
                ("captured_at", "2026-07-15T12:00:00"),
            ):
                mutation = copy.deepcopy(original)
                mutation[field] = value
                manifest_path.write_text(json.dumps(mutation), encoding="utf-8")
                result = self.run_cmd(
                    VERIFY,
                    CANONICAL_SCENARIO_PATH,
                    "--capture",
                    capture,
                    "--skill",
                    SKILL,
                )
                self.assertNotEqual(result.returncode, 0)
            mutation = copy.deepcopy(original)
            mutation["capture_kind"] = "live_model"
            manifest_path.write_text(json.dumps(mutation), encoding="utf-8")
            result = self.run_cmd(
                VERIFY,
                CANONICAL_SCENARIO_PATH,
                "--capture",
                capture,
                "--skill",
                SKILL,
            )
            self.assertNotEqual(result.returncode, 0)

    def test_current_recorded_fixture_uses_strict_oracle_free_contract(self):
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
