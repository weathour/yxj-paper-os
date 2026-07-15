from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from analyze_template_corpus import OUTPUT_NAMES, write_bundle_transactional
from verify_semantic_dossier import (
    DOSSIER_FILENAME,
    DossierValidationError,
    rule_dependency_fingerprint,
    validate_schema_asset,
    validate_semantic_dossier,
    write_semantic_dossier,
)


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "assets" / "template-analysis" / "semantic-dossier.schema.json"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def codes(diagnostics):
    return {item.code for item in diagnostics}


class DossierWorkspace:
    def __init__(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        source = self.root / "sources" / "template.md"
        source.parent.mkdir(parents=True)
        source.write_text(
            "# Methods\n\nA bounded template passage.\n", encoding="utf-8"
        )
        source_sha = sha256_bytes(source.read_bytes())
        self.payload = {
            "schema": "yxj-template-semantic-dossier/1.0",
            "dossier_id": "TSD-fixture",
            "workspace_schema": "0.3",
            "design_question": "How should the method explanation stage its bounded contribution?",
            "scope_ids": ["SCOPE-main", "SCOPE-other"],
            "analysis_context": {
                "method": "model_semantic_deep_reading",
                "agent_identity": "codex-test-agent",
                "model_identity": "unavailable",
                "prompt_identity": "unavailable",
                "access_limitations": "Only the declared derivative was read.",
                "generic_knowledge_fallback": "not_used",
                "uncertainty_note": "Transfer remains a design proposal.",
            },
            "documents": [
                {
                    "template_source_id": "TPL-method",
                    "title": "方法模板示例",
                    "source_pointer": "sources/template.md",
                    "acquisition_provenance": "owner-supplied local derivative",
                    "role": "exemplar",
                    "design_question": "How should the method explanation stage its bounded contribution?",
                    "design_relevance": "Method paragraph sequencing only.",
                    "access_state": "owner_derivative",
                    "local_derivative_pointer": "sources/template.md",
                    "source_sha256": source_sha,
                    "accessed_at": "2026-07-15T00:00:00Z",
                    "access_copyright_limitation": "No full body is stored in the dossier.",
                    "freshness": "verified_local_current",
                    "semantic_reading_eligible": True,
                    "design_only_state": "design_only",
                    "analyzer_correlation": {
                        "analysis_id": "analysis-fixture",
                        "doc_id": "doc-method",
                        "source_sha256": source_sha,
                    },
                }
            ],
            "observations": [
                {
                    "observation_id": "TOBS-method-order",
                    "template_source_id": "TPL-method",
                    "locator": {"kind": "paragraph", "value": "Methods paragraph 2"},
                    "observed_pattern": "The paragraph states the bounded object before mechanism detail.",
                    "semantic_interpretation": "Object-first ordering reduces referent ambiguity.",
                    "uncertainty": "Observed in one eligible exemplar.",
                    "non_transfer_note": "Do not copy wording or infer scientific authority.",
                    "status": "model-derived",
                    "minimal_excerpt": "bounded object before mechanism detail",
                }
            ],
            "transfer_rules": [],
            "updated_at": "2026-07-15T00:00:00Z",
        }
        self.payload["transfer_rules"].append(
            {
                "rule_id": "TRULE-method-order",
                "observation_ids": ["TOBS-method-order"],
                "grounding_kind": "semantic_dossier",
                "rule_kind": "candidate_pattern",
                "candidate_transfer": "Place the bounded object before mechanism detail.",
                "suggested_disposition": "adopted",
                "origin": "model-proposed",
                "limitation": "Applies only to SCOPE-main method explanation.",
                "dependency_fingerprint": rule_dependency_fingerprint(
                    ["TOBS-method-order"],
                    self.payload["observations"],
                    self.payload["documents"],
                ),
                "source_freshness": "verified_local_current",
                "application_snapshot": {
                    "affected_scope_ids": ["SCOPE-main"],
                    "surface": "method paragraph sequence",
                    "resolution": "confirmed",
                    "disposition": "adopted",
                    "gate_category": "not_applicable",
                    "decision_id": "none",
                    "decision_pointer": "none",
                    "public_projection_pointer": "03_WRITING_STRUCTURE.md#Template Rule Projection",
                },
            }
        )
        self.write_projections()

    def close(self) -> None:
        self.temp.cleanup()

    def write_projections(self) -> None:
        doc_rows = []
        for doc in self.payload["documents"]:
            doc_rows.append(
                "| {template_source_id} | {role} | {design_question} | {source_pointer} | "
                "{access_state} | {local_derivative_pointer} | {source_sha256} | "
                ".yxj-paper-os/template-analysis/semantic-dossier.json#{template_source_id} | "
                "{design_only_state} | none |".format(**doc)
            )
        (self.root / "01_MATERIALS_INVENTORY.md").write_text(
            "# 01 Materials Inventory\n\n## Template Design Sources\n\n"
            "| Template source ID | Design role | Design question | Source/provenance pointer | Access state | Local derivative pointer | Source SHA-256 | Hidden dossier pointer | Design-only state | Scientific-source promotion pointer |\n"
            "|---|---|---|---|---|---|---|---|---|---|\n" + "\n".join(doc_rows) + "\n",
            encoding="utf-8",
        )
        rule_rows = []
        for rule in self.payload["transfer_rules"]:
            snap = rule["application_snapshot"]
            pointers = ";".join(
                f".yxj-paper-os/template-analysis/semantic-dossier.json#{oid}"
                for oid in rule["observation_ids"]
            )
            rule_rows.append(
                "| {rule_id} | semantic_dossier | {pointers} | {rule_kind} | {scopes} | "
                "{surface} | {candidate_transfer} | {suggested_disposition} | {origin} | "
                "{resolution} | {disposition} | {decision_id} | {limitation} | {freshness} |".format(
                    pointers=pointers,
                    scopes=";".join(snap["affected_scope_ids"]),
                    surface=snap["surface"],
                    resolution=snap["resolution"],
                    disposition=snap["disposition"],
                    decision_id=snap["decision_id"],
                    freshness=rule["source_freshness"],
                    **rule,
                )
            )
        (self.root / "03_WRITING_STRUCTURE.md").write_text(
            "# 03 Writing Structure\n\n## Template Rule Projection\n\n"
            "| Rule ID | Grounding kind | Grounding pointer(s) | Rule kind | Affected scope IDs | Surface | Candidate transfer | Suggested disposition | Origin | Resolution | Disposition | Decision ID | Limitation | Freshness |\n"
            "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n"
            + "\n".join(rule_rows)
            + "\n",
            encoding="utf-8",
        )


class SemanticDossierTests(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.ws = DossierWorkspace()

    def tearDown(self) -> None:
        self.ws.close()

    def assert_code(self, payload, expected: str, *, workspace=True):
        diagnostics = validate_semantic_dossier(
            payload, self.ws.root if workspace else None
        )
        self.assertIn(expected, codes(diagnostics), diagnostics)
        return diagnostics

    def test_schema_asset_and_minimal_local_projection_are_valid(self) -> None:
        self.assertTrue(SCHEMA.is_file())
        self.assertEqual(validate_schema_asset(SCHEMA), [])
        self.assertEqual(validate_semantic_dossier(self.ws.payload, self.ws.root), [])

    def test_positive_url_control_rejection_and_deliberate_divergence(self) -> None:
        payload = self.ws.payload
        remote_sha = "b" * 64
        payload["documents"].append(
            {
                "template_source_id": "TPL-control",
                "title": "Remote control exemplar",
                "source_pointer": "https://example.invalid/control",
                "acquisition_provenance": "agent-accessed full text",
                "role": "control",
                "design_question": payload["design_question"],
                "design_relevance": "Counterexample to universal transfer.",
                "access_state": "full_text",
                "local_derivative_pointer": "none",
                "source_sha256": remote_sha,
                "accessed_at": "2026-07-15T00:00:00Z",
                "access_copyright_limitation": "Remote source not copied locally.",
                "freshness": "recorded_at_access",
                "semantic_reading_eligible": True,
                "design_only_state": "design_only",
                "analyzer_correlation": {
                    "analysis_id": "analysis-control",
                    "doc_id": "doc-control",
                    "source_sha256": remote_sha,
                },
            }
        )
        payload["observations"].append(
            {
                "observation_id": "TOBS-control",
                "template_source_id": "TPL-control",
                "locator": {"kind": "section", "value": "Discussion"},
                "observed_pattern": "The control uses a different ordering.",
                "semantic_interpretation": "The candidate is not universal.",
                "uncertainty": "Remote state is recorded only at access.",
                "non_transfer_note": "Reject universal transfer.",
                "status": "model-derived",
            }
        )
        payload["transfer_rules"].append(
            {
                "rule_id": "TRULE-control-reject",
                "observation_ids": ["TOBS-control"],
                "grounding_kind": "semantic_dossier",
                "rule_kind": "candidate_pattern",
                "candidate_transfer": "Treat the order as universal.",
                "suggested_disposition": "rejected",
                "origin": "model-proposed",
                "limitation": "Counterexample defeats universal transfer.",
                "dependency_fingerprint": rule_dependency_fingerprint(
                    ["TOBS-control"], payload["observations"], payload["documents"]
                ),
                "source_freshness": "recorded_at_access",
                "application_snapshot": {
                    "affected_scope_ids": ["SCOPE-other"],
                    "surface": "discussion sequence",
                    "resolution": "rejected",
                    "disposition": "rejected",
                    "gate_category": "not_applicable",
                    "decision_id": "none",
                    "decision_pointer": "none",
                    "public_projection_pointer": "03_WRITING_STRUCTURE.md#Template Rule Projection",
                },
            }
        )
        divergent = copy.deepcopy(payload["transfer_rules"][0])
        divergent["rule_id"] = "TRULE-deliberate"
        divergent["application_snapshot"].update(
            {
                "resolution": "confirmed",
                "disposition": "deliberate_divergence",
                "gate_category": "deliberate_divergence",
                "decision_id": "DEC-diverge",
                "decision_pointer": "00_PROJECT_ROUTE.md#Decision Records",
            }
        )
        payload["transfer_rules"].append(divergent)
        self.ws.write_projections()
        self.assertEqual(validate_semantic_dossier(payload, self.ws.root), [])

    def test_invalid_shape_reference_access_freshness_and_firewall_cases(self) -> None:
        cases = []

        def case(name, code, mutate):
            payload = copy.deepcopy(self.ws.payload)
            mutate(payload)
            cases.append((name, code, payload))

        case(
            "missing design question",
            "DOSSIER_SCHEMA",
            lambda p: p.pop("design_question"),
        )
        case(
            "missing document identity",
            "DOSSIER_SCHEMA",
            lambda p: p["documents"][0].pop("template_source_id"),
        )
        case(
            "missing document provenance",
            "DOSSIER_SCHEMA",
            lambda p: p["documents"][0].pop("acquisition_provenance"),
        )
        case(
            "missing document access state",
            "DOSSIER_SCHEMA",
            lambda p: p["documents"][0].pop("access_state"),
        )
        case(
            "unknown document",
            "DOSSIER_REFERENCE",
            lambda p: p["observations"][0].update(template_source_id="TPL-missing"),
        )
        case(
            "empty locator",
            "DOSSIER_LOCATOR",
            lambda p: p["observations"][0]["locator"].update(value=""),
        )
        case(
            "metadata observation",
            "DOSSIER_ACCESS",
            lambda p: p["documents"][0].update(
                access_state="metadata_only",
                local_derivative_pointer="none",
                source_sha256="none",
                semantic_reading_eligible=False,
                freshness="unavailable",
            ),
        )
        case(
            "unknown observation",
            "DOSSIER_REFERENCE",
            lambda p: p["transfer_rules"][0].update(observation_ids=["TOBS-missing"]),
        )
        case(
            "unknown scope",
            "DOSSIER_REFERENCE",
            lambda p: p["transfer_rules"][0]["application_snapshot"].update(
                affected_scope_ids=["SCOPE-missing"]
            ),
        )
        case(
            "invalid disposition",
            "DOSSIER_SCHEMA",
            lambda p: p["transfer_rules"][0]["application_snapshot"].update(
                disposition="approved"
            ),
        )
        case(
            "divergence without decision",
            "DOSSIER_GATE",
            lambda p: p["transfer_rules"][0]["application_snapshot"].update(
                disposition="deliberate_divergence",
                gate_category="deliberate_divergence",
                decision_id="none",
                decision_pointer="none",
            ),
        )
        case(
            "missing projection",
            "DOSSIER_REFERENCE",
            lambda p: p["transfer_rules"][0]["application_snapshot"].update(
                public_projection_pointer="none"
            ),
        )
        case(
            "remote called current",
            "DOSSIER_FRESHNESS",
            lambda p: p["documents"][0].update(
                source_pointer="https://example.invalid/template",
                local_derivative_pointer="none",
                access_state="full_text",
                freshness="verified_local_current",
            ),
        )
        case(
            "snippet observation",
            "DOSSIER_ACCESS",
            lambda p: p["documents"][0].update(
                access_state="snippet_only",
                local_derivative_pointer="none",
                source_sha256="none",
                semantic_reading_eligible=False,
                freshness="unavailable",
            ),
        )
        case(
            "partial analyzer correlation",
            "DOSSIER_REFERENCE",
            lambda p: p["documents"][0]["analyzer_correlation"].pop("doc_id"),
        )
        case(
            "full text missing sha",
            "DOSSIER_FINGERPRINT",
            lambda p: p["documents"][0].update(
                access_state="full_text", source_sha256="none"
            ),
        )
        case(
            "derivative missing path",
            "DOSSIER_ACCESS",
            lambda p: p["documents"][0].update(local_derivative_pointer="none"),
        )
        case(
            "template claims evidence",
            "DOSSIER_FIREWALL",
            lambda p: p["documents"][0].update(design_only_state="scientific_evidence"),
        )
        case(
            "long copied text",
            "DOSSIER_COPY_BOUNDARY",
            lambda p: p["observations"][0].update(minimal_excerpt="x" * 501),
        )

        for name, expected, payload in cases:
            with self.subTest(name=name):
                self.assert_code(payload, expected)

    def test_malformed_json_types_are_bounded_schema_diagnostics(self) -> None:
        mutations = (
            lambda p: p.update(scope_ids=None),
            lambda p: p.update(scope_ids=["SCOPE-main", {}]),
            lambda p: p["analysis_context"].update(generic_knowledge_fallback={}),
            lambda p: p["documents"][0].update(role={}),
            lambda p: p["documents"][0].update(access_state=[]),
            lambda p: p["documents"][0].update(freshness={}),
            lambda p: p["observations"][0]["locator"].update(kind={}),
            lambda p: p["transfer_rules"][0].update(observation_ids=[{}]),
            lambda p: p["transfer_rules"][0]["application_snapshot"].update(
                affected_scope_ids=None
            ),
            lambda p: p["transfer_rules"][0]["application_snapshot"].update(
                affected_scope_ids=["SCOPE-main", {}]
            ),
            lambda p: p["transfer_rules"][0]["application_snapshot"].update(
                disposition={}
            ),
        )
        for index, mutate in enumerate(mutations):
            payload = copy.deepcopy(self.ws.payload)
            mutate(payload)
            with self.subTest(index=index):
                try:
                    diagnostics = validate_semantic_dossier(payload, self.ws.root)
                except Exception as exc:  # pragma: no cover - assertion reports escape
                    self.fail(
                        f"malformed JSON escaped validation: {type(exc).__name__}: {exc}"
                    )
                self.assertIn("DOSSIER_SCHEMA", codes(diagnostics), diagnostics)

    def test_every_nested_json_value_has_a_total_wrong_type_path(self) -> None:
        def paths(value, prefix=()):
            if isinstance(value, dict):
                for key, child in value.items():
                    child_path = prefix + (key,)
                    yield child_path, child
                    yield from paths(child, child_path)
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    child_path = prefix + (index,)
                    yield child_path, child
                    yield from paths(child, child_path)

        def replace(payload, path, value):
            cursor = payload
            for part in path[:-1]:
                cursor = cursor[part]
            cursor[path[-1]] = value

        for path, original in paths(self.ws.payload):
            wrong_type = (
                []
                if isinstance(original, dict)
                else None
                if isinstance(original, list)
                else {}
            )
            payload = copy.deepcopy(self.ws.payload)
            replace(payload, path, wrong_type)
            with self.subTest(path=path):
                try:
                    diagnostics = validate_semantic_dossier(payload, self.ws.root)
                except Exception as exc:  # pragma: no cover - assertion reports escape
                    self.fail(
                        f"wrong JSON type escaped at {path}: {type(exc).__name__}: {exc}"
                    )
                self.assertTrue(diagnostics, path)

    def test_runtime_enforces_sha_boolean_and_observation_copy_limits(self) -> None:
        for access in (
            "full_text",
            "owner_derivative",
            "metadata_only",
            "snippet_only",
            "inaccessible",
        ):
            payload = copy.deepcopy(self.ws.payload)
            readable = access in {"full_text", "owner_derivative"}
            payload["documents"][0].update(
                access_state=access,
                local_derivative_pointer=(
                    "sources/template.md" if readable else "none"
                ),
                source_sha256="not-a-sha",
                semantic_reading_eligible=readable,
                freshness=("verified_local_current" if readable else "unavailable"),
            )
            payload["documents"][0].pop("analyzer_correlation")
            diagnostics = validate_semantic_dossier(payload, self.ws.root)
            with self.subTest(access=access):
                self.assertTrue(
                    any(
                        item.code == "DOSSIER_SCHEMA"
                        and "source_sha256" in item.message
                        for item in diagnostics
                    ),
                    diagnostics,
                )

        unreadable = copy.deepcopy(self.ws.payload)
        unreadable["documents"][0].update(
            access_state="metadata_only",
            local_derivative_pointer="none",
            source_sha256="none",
            semantic_reading_eligible=0,
            freshness="unavailable",
        )
        diagnostics = validate_semantic_dossier(unreadable, self.ws.root)
        self.assertTrue(
            any(
                item.code == "DOSSIER_SCHEMA" and "must be boolean" in item.message
                for item in diagnostics
            ),
            diagnostics,
        )

        limits = {
            "observed_pattern": 2000,
            "semantic_interpretation": 2000,
            "uncertainty": 1000,
            "non_transfer_note": 1000,
            "minimal_excerpt": 500,
        }
        for field, limit in limits.items():
            payload = copy.deepcopy(self.ws.payload)
            payload["observations"][0][field] = "x" * limit
            with self.subTest(field=field, boundary="accepted"):
                self.assertEqual(validate_semantic_dossier(payload, self.ws.root), [])
            payload["observations"][0][field] = "x" * (limit + 1)
            with self.subTest(field=field, boundary="rejected"):
                self.assertIn(
                    "DOSSIER_COPY_BOUNDARY",
                    codes(validate_semantic_dossier(payload, self.ws.root)),
                )

    def test_schema_asset_detects_enum_pattern_type_and_limit_drift(self) -> None:
        original = json.loads(SCHEMA.read_text(encoding="utf-8"))
        mutations = (
            lambda d: d["$defs"]["document"]["properties"]["role"].update(
                enum=["bogus"]
            ),
            lambda d: d["$defs"]["sha_or_none"].update(pattern=".*"),
            lambda d: d["$defs"]["document"]["properties"][
                "semantic_reading_eligible"
            ].update(type="integer"),
            lambda d: d["$defs"]["observation"]["properties"][
                "observed_pattern"
            ].update(maxLength=1999),
        )
        for index, mutate in enumerate(mutations):
            changed = copy.deepcopy(original)
            mutate(changed)
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "schema.json"
                path.write_text(json.dumps(changed), encoding="utf-8")
                with self.subTest(index=index):
                    self.assertTrue(validate_schema_asset(path))

    def test_schema_asset_detects_ref_topology_and_top_property_drift(self) -> None:
        original = json.loads(SCHEMA.read_text(encoding="utf-8"))
        mutations = (
            lambda d: d["properties"]["documents"]["items"].update(
                {"$ref": "#/$defs/observation"}
            ),
            lambda d: d["$defs"]["document"]["properties"]["source_sha256"].update(
                {"$ref": "#/$defs/freshness"}
            ),
            lambda d: d["$defs"]["transfer_rule"]["properties"][
                "application_snapshot"
            ].update({"$ref": "#/$defs/document"}),
            lambda d: d["properties"].pop("updated_at"),
            lambda d: d["properties"].update(unexpected={"type": "string"}),
            lambda d: d.update(additionalProperties=True),
        )
        for index, mutate in enumerate(mutations):
            changed = copy.deepcopy(original)
            mutate(changed)
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "schema.json"
                path.write_text(json.dumps(changed), encoding="utf-8")
                with self.subTest(index=index):
                    self.assertTrue(validate_schema_asset(path))

    def test_optional_fields_are_presence_aware_for_null_and_wrong_types(self) -> None:
        absent = copy.deepcopy(self.ws.payload)
        absent["documents"][0].pop("analyzer_correlation")
        absent["observations"][0].pop("minimal_excerpt")
        self.assertEqual(validate_semantic_dossier(absent, self.ws.root), [])

        for value in (None, [], "", 0, False):
            payload = copy.deepcopy(self.ws.payload)
            payload["documents"][0]["analyzer_correlation"] = value
            with self.subTest(field="analyzer_correlation", value=value):
                diagnostics = validate_semantic_dossier(payload, self.ws.root)
                self.assertIn("DOSSIER_SCHEMA", codes(diagnostics), diagnostics)

            payload = copy.deepcopy(self.ws.payload)
            payload["observations"][0]["minimal_excerpt"] = value
            with self.subTest(field="minimal_excerpt", value=value):
                diagnostics = validate_semantic_dossier(payload, self.ws.root)
                self.assertIn("DOSSIER_COPY_BOUNDARY", codes(diagnostics), diagnostics)

    def test_public_mirror_normalization_and_utf8_text_exactness(self) -> None:
        materials = self.ws.root / "01_MATERIALS_INVENTORY.md"
        original_question = self.ws.payload["design_question"]
        exact_question = "方法段如何先界定对象，再说明受限贡献？"
        self.ws.payload["design_question"] = exact_question
        self.ws.payload["documents"][0]["design_question"] = exact_question
        normalized = materials.read_text(encoding="utf-8").replace(
            original_question, exact_question, 1
        )
        normalized = normalized.replace("| exemplar |", "| EXEMPLAR |", 1)
        normalized = normalized.replace(
            "| owner_derivative |", "| OWNER_DERIVATIVE |", 1
        )
        normalized = normalized.replace(
            self.ws.payload["documents"][0]["source_sha256"],
            self.ws.payload["documents"][0]["source_sha256"].upper(),
        )
        normalized = normalized.replace("sources/template.md", "./sources/template.md")
        materials.write_text(normalized, encoding="utf-8")
        self.assertEqual(validate_semantic_dossier(self.ws.payload, self.ws.root), [])

        materials.write_text(
            normalized.replace(
                exact_question, exact_question.replace("受限", "有限", 1), 1
            ),
            encoding="utf-8",
        )
        diagnostics = self.assert_code(self.ws.payload, "TEMPLATE_PROJECTION_MISMATCH")
        mismatches = [
            item for item in diagnostics if item.code == "TEMPLATE_PROJECTION_MISMATCH"
        ]
        self.assertTrue(all(item.scopes == ("SCOPE-main",) for item in mismatches))

    def test_public_free_text_decodes_only_canonical_markdown_cells(self) -> None:
        payload = self.ws.payload
        payload["design_question"] = "A | B\nC"
        payload["documents"][0]["design_question"] = "A | B\nC"
        payload["transfer_rules"][0]["candidate_transfer"] = "First | second\nthird."
        payload["transfer_rules"][0]["limitation"] = "Only | here\nnot elsewhere."
        self.ws.write_projections()

        materials = self.ws.root / "01_MATERIALS_INVENTORY.md"
        materials.write_text(
            materials.read_text(encoding="utf-8").replace(
                "A | B\nC", "A &#124; B<br>C", 1
            ),
            encoding="utf-8",
        )
        structure = self.ws.root / "03_WRITING_STRUCTURE.md"
        structure.write_text(
            structure.read_text(encoding="utf-8")
            .replace("First | second\nthird.", "First &#124; second<br>third.", 1)
            .replace(
                "Only | here\nnot elsewhere.", "Only &#124; here<br>not elsewhere.", 1
            ),
            encoding="utf-8",
        )
        self.assertEqual(validate_semantic_dossier(payload, self.ws.root), [])

        materials.write_text(
            materials.read_text(encoding="utf-8").replace(
                "A &#124; B<br>C", "A &#124; B<br>D", 1
            ),
            encoding="utf-8",
        )
        self.assert_code(payload, "TEMPLATE_PROJECTION_MISMATCH")

    def test_stale_active_rule_blocks_only_linked_scope(self) -> None:
        self.ws.payload["documents"][0]["freshness"] = "stale"
        self.ws.payload["transfer_rules"][0]["source_freshness"] = "stale"
        diagnostics = self.assert_code(self.ws.payload, "DOSSIER_FRESHNESS")
        freshness = [item for item in diagnostics if item.code == "DOSSIER_FRESHNESS"]
        self.assertTrue(freshness)
        self.assertTrue(all(item.scopes == ("SCOPE-main",) for item in freshness))
        self.assertNotIn("TEMPLATE_RULE_INCOMPATIBLE", codes(diagnostics))

    def test_contained_derivative_mismatch_cannot_hide_as_recorded_at_access(
        self,
    ) -> None:
        for declared in ("recorded_at_access", "stale"):
            self.ws.payload["documents"][0]["freshness"] = declared
            self.ws.payload["transfer_rules"][0]["source_freshness"] = declared
            self.ws.write_projections()
            (self.ws.root / "sources" / "template.md").write_text(
                "changed bytes\n", encoding="utf-8"
            )
            with self.subTest(declared=declared):
                diagnostics = self.assert_code(self.ws.payload, "DOSSIER_FINGERPRINT")
                mismatches = [
                    item
                    for item in diagnostics
                    if item.code in {"DOSSIER_FINGERPRINT", "DOSSIER_FRESHNESS"}
                ]
                self.assertTrue(
                    all(item.scopes == ("SCOPE-main",) for item in mismatches)
                )
                self.assertNotIn("TEMPLATE_RULE_INCOMPATIBLE", codes(diagnostics))

    def test_verified_current_requires_workspace_and_contained_derivative(self) -> None:
        diagnostics = validate_semantic_dossier(self.ws.payload, None)
        self.assertIn("DOSSIER_FRESHNESS", codes(diagnostics), diagnostics)

        payload = copy.deepcopy(self.ws.payload)
        payload["documents"][0].update(
            access_state="full_text",
            source_pointer="sources/missing.md",
            local_derivative_pointer="none",
            freshness="verified_local_current",
        )
        diagnostics = validate_semantic_dossier(payload, self.ws.root)
        self.assertIn("DOSSIER_FRESHNESS", codes(diagnostics), diagnostics)

    def test_projection_duplicates_are_order_independent_mismatches(self) -> None:
        cases = (
            ("01_MATERIALS_INVENTORY.md", "TPL-method", "| exemplar |", "| control |"),
            (
                "03_WRITING_STRUCTURE.md",
                "TRULE-method-order",
                "Place the bounded object before mechanism detail.",
                "A conflicting public transfer.",
            ),
        )
        for filename, record_id, original_token, conflicting_token in cases:
            path = self.ws.root / filename
            original_text = path.read_text(encoding="utf-8")
            row = next(
                line
                for line in original_text.splitlines()
                if f"| {record_id} |" in line
            )
            for variant_name, duplicate in (
                ("identical", row),
                ("conflicting", row.replace(original_token, conflicting_token, 1)),
            ):
                for order in ("before", "after"):
                    lines = original_text.splitlines()
                    index = lines.index(row)
                    lines.insert(index if order == "before" else index + 1, duplicate)
                    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
                    with self.subTest(file=filename, variant=variant_name, order=order):
                        diagnostics = self.assert_code(
                            self.ws.payload, "TEMPLATE_PROJECTION_MISMATCH"
                        )
                        mismatches = [
                            item
                            for item in diagnostics
                            if item.code == "TEMPLATE_PROJECTION_MISMATCH"
                        ]
                        self.assertTrue(
                            all(item.scopes == ("SCOPE-main",) for item in mismatches)
                        )
                    path.write_text(original_text, encoding="utf-8")

    def test_fingerprint_mismatch_and_selective_projection_mismatch(self) -> None:
        source = self.ws.root / "sources" / "template.md"
        source.write_text("changed bytes\n", encoding="utf-8")
        diagnostics = self.assert_code(self.ws.payload, "DOSSIER_FINGERPRINT")
        linked = [d for d in diagnostics if d.code == "DOSSIER_FINGERPRINT"]
        self.assertTrue(any(d.scopes == ("SCOPE-main",) for d in linked), linked)

        # Restore the source, then mutate only the 01 role projection.
        source.write_text(
            "# Methods\n\nA bounded template passage.\n", encoding="utf-8"
        )
        materials = self.ws.root / "01_MATERIALS_INVENTORY.md"
        materials.write_text(
            materials.read_text(encoding="utf-8").replace(
                "| exemplar |", "| control |", 1
            ),
            encoding="utf-8",
        )
        diagnostics = self.assert_code(self.ws.payload, "TEMPLATE_PROJECTION_MISMATCH")
        mismatches = [
            d for d in diagnostics if d.code == "TEMPLATE_PROJECTION_MISMATCH"
        ]
        self.assertTrue(mismatches)
        self.assertTrue(
            all(d.scopes == ("SCOPE-main",) for d in mismatches), mismatches
        )
        self.assertNotIn(
            "SCOPE-other", {scope for d in mismatches for scope in d.scopes}
        )

    def test_hidden_definition_and_application_snapshot_mismatches_are_selective(
        self,
    ) -> None:
        structure = self.ws.root / "03_WRITING_STRUCTURE.md"
        original = structure.read_text(encoding="utf-8")
        mutations = (
            original.replace(
                "Place the bounded object before mechanism detail.",
                "Different public candidate transfer.",
                1,
            ),
            original.replace("| confirmed | adopted |", "| confirmed | adapted |", 1),
        )
        for index, text in enumerate(mutations):
            with self.subTest(index=index):
                structure.write_text(text, encoding="utf-8")
                diagnostics = self.assert_code(
                    self.ws.payload, "TEMPLATE_PROJECTION_MISMATCH"
                )
                mismatch = [
                    d for d in diagnostics if d.code == "TEMPLATE_PROJECTION_MISMATCH"
                ]
                self.assertTrue(mismatch)
                self.assertTrue(all(d.scopes == ("SCOPE-main",) for d in mismatch))
                structure.write_text(original, encoding="utf-8")

    def test_analyzer_bundle_writer_preserves_semantic_dossier(self) -> None:
        output = self.ws.root / ".yxj-paper-os" / "template-analysis"
        output.mkdir(parents=True)
        dossier = output / DOSSIER_FILENAME
        original = b'{"owner":"semantic dossier"}\n'
        dossier.write_bytes(original)
        payloads = {name: f"fixed:{name}\n".encode() for name in OUTPUT_NAMES}
        write_bundle_transactional(output, payloads)
        self.assertEqual(dossier.read_bytes(), original)

    def test_bounded_dossier_writer_preserves_fixed_outputs_and_annotations(
        self,
    ) -> None:
        output = self.ws.root / ".yxj-paper-os" / "template-analysis"
        output.mkdir(parents=True)
        protected = {}
        for name in OUTPUT_NAMES:
            path = output / name
            path.write_bytes(f"fixed:{name}\n".encode())
            protected[path] = sha256_bytes(path.read_bytes())
        annotations = output / "accepted-annotations.json"
        annotations.write_text(
            '{"schema":"template-annotations/1.0","annotations":[]}\n',
            encoding="utf-8",
        )
        protected[annotations] = sha256_bytes(annotations.read_bytes())
        write_semantic_dossier(self.ws.root, self.ws.payload)
        self.assertTrue((output / DOSSIER_FILENAME).is_file())
        self.assertEqual(
            {path: sha256_bytes(path.read_bytes()) for path in protected}, protected
        )

    def test_dossier_writer_rejects_invalid_payload_without_writeback(self) -> None:
        output = self.ws.root / ".yxj-paper-os" / "template-analysis"
        output.mkdir(parents=True)
        protected = {}
        for name in OUTPUT_NAMES:
            path = output / name
            path.write_bytes(f"fixed:{name}\n".encode())
            protected[path] = sha256_bytes(path.read_bytes())
        annotations = output / "accepted-annotations.json"
        annotations.write_text(
            '{"schema":"template-annotations/1.0","annotations":[]}\n',
            encoding="utf-8",
        )
        protected[annotations] = sha256_bytes(annotations.read_bytes())
        payload = copy.deepcopy(self.ws.payload)
        payload["observations"][0]["observed_pattern"] = "x" * 2001
        with self.assertRaises(DossierValidationError):
            write_semantic_dossier(self.ws.root, payload)
        self.assertFalse((output / DOSSIER_FILENAME).exists())
        self.assertEqual(
            {path: sha256_bytes(path.read_bytes()) for path in protected}, protected
        )

    def test_dossier_writer_rejects_explicit_null_optional_fields(self) -> None:
        output = self.ws.root / ".yxj-paper-os" / "template-analysis"
        output.mkdir(parents=True)
        fixed = output / "manifest.json"
        fixed.write_bytes(b"fixed manifest\n")
        annotations = output / "accepted-annotations.json"
        annotations.write_text(
            '{"schema":"template-annotations/1.0","annotations":[]}\n',
            encoding="utf-8",
        )
        protected = {
            fixed: sha256_bytes(fixed.read_bytes()),
            annotations: sha256_bytes(annotations.read_bytes()),
        }
        for field in ("analyzer_correlation", "minimal_excerpt"):
            payload = copy.deepcopy(self.ws.payload)
            if field == "analyzer_correlation":
                payload["documents"][0][field] = None
            else:
                payload["observations"][0][field] = None
            with self.subTest(field=field):
                with self.assertRaises(DossierValidationError):
                    write_semantic_dossier(self.ws.root, payload)
                self.assertFalse((output / DOSSIER_FILENAME).exists())
                self.assertEqual(
                    {path: sha256_bytes(path.read_bytes()) for path in protected},
                    protected,
                )

    def test_dossier_writer_rejects_aliases_and_symlink_escape(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            outside = root / "outside"
            outside.mkdir()
            sentinel = outside / "sentinel"
            sentinel.write_bytes(b"outside unchanged\n")
            sentinel_hash = sha256_bytes(sentinel.read_bytes())

            workspace_alias = root / "workspace-alias"
            workspace_alias.symlink_to(self.ws.root, target_is_directory=True)
            with self.assertRaises(ValueError):
                write_semantic_dossier(workspace_alias, self.ws.payload)

            with self.assertRaises(ValueError):
                write_semantic_dossier(self.ws.root / "child" / "..", self.ws.payload)

            for component in (".yxj-paper-os", "template-analysis"):
                hidden = self.ws.root / ".yxj-paper-os"
                analysis = hidden / "template-analysis"
                if analysis.is_symlink():
                    analysis.unlink()
                elif analysis.exists():
                    for child in analysis.iterdir():
                        child.unlink()
                    analysis.rmdir()
                if hidden.is_symlink():
                    hidden.unlink()
                elif hidden.exists() and component == ".yxj-paper-os":
                    hidden.rmdir()
                if component == ".yxj-paper-os":
                    hidden.symlink_to(outside, target_is_directory=True)
                else:
                    hidden.mkdir(exist_ok=True)
                    analysis.symlink_to(outside, target_is_directory=True)
                with self.subTest(component=component):
                    with self.assertRaises(ValueError):
                        write_semantic_dossier(self.ws.root, self.ws.payload)
                    self.assertFalse((outside / DOSSIER_FILENAME).exists())
                    self.assertEqual(sha256_bytes(sentinel.read_bytes()), sentinel_hash)

            hidden = self.ws.root / ".yxj-paper-os"
            if hidden.is_symlink():
                hidden.unlink()
            hidden.mkdir(exist_ok=True)
            analysis = hidden / "template-analysis"
            if analysis.is_symlink():
                analysis.unlink()
            analysis.mkdir(exist_ok=True)
            destination = analysis / DOSSIER_FILENAME
            destination.symlink_to(sentinel)
            with self.assertRaises(ValueError):
                write_semantic_dossier(self.ws.root, self.ws.payload)
            self.assertEqual(sha256_bytes(sentinel.read_bytes()), sentinel_hash)

    def test_validator_has_no_network_or_writeback_side_effect(self) -> None:
        before = {
            path: sha256_bytes(path.read_bytes())
            for path in self.ws.root.rglob("*")
            if path.is_file()
        }
        self.assertEqual(validate_semantic_dossier(self.ws.payload, self.ws.root), [])
        after = {
            path: sha256_bytes(path.read_bytes())
            for path in self.ws.root.rglob("*")
            if path.is_file()
        }
        self.assertEqual(after, before)
        source = (
            Path(__file__)
            .with_name("verify_semantic_dossier.py")
            .read_text(encoding="utf-8")
        )
        self.assertNotRegex(source, r"urllib|requests|socket|http\.client")


if __name__ == "__main__":
    unittest.main(verbosity=2)
