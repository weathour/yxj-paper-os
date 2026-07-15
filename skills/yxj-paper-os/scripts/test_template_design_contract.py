from __future__ import annotations

import copy
import hashlib
import tempfile
import unittest
from pathlib import Path

from template_design_contract import (
    ANALYZER_ACTION_TO_SUGGESTED_DISPOSITION,
    TEMPLATE_RULE_INCOMPATIBLE,
    load_lens_registry,
    validate_template_rule,
)


ROOT = Path(__file__).resolve().parents[1]
LENSES = ROOT / "references" / "lenses"


def codes(items):
    return {item.code for item in items}


class TemplateDesignCompatibilityTests(unittest.TestCase):
    def base_rule(self, kind: str) -> dict:
        base = {
            "rule_id": f"TRULE-{kind.replace('_', '-')}",
            "grounding_kind": kind,
            "grounding_pointers": [],
            "rule_kind": "candidate_pattern",
            "affected_scope_ids": ["SCOPE-main"],
            "suggested_disposition": "adopted",
            "origin": "model-proposed",
            "resolution": "candidate",
            "disposition": "candidate",
            "gate_category": "not_applicable",
            "decision_id": "none",
            "freshness": "verified_local_current",
        }
        if kind == "official_constraint":
            base.update(
                grounding_pointers=["M-official"],
                origin="artifact-observed",
                suggested_disposition="none",
                official_source={
                    "kind": "source",
                    "origin": "artifact-observed",
                    "status": "available",
                    "locator": "official/current-guidance.md",
                    "grounding": "official/current-guidance.md#Format",
                },
            )
        elif kind == "semantic_dossier":
            base["grounding_pointers"] = [
                ".yxj-paper-os/template-analysis/semantic-dossier.json#TOBS-method"
            ]
        elif kind == "quantitative_analysis":
            base.update(
                grounding_pointers=[
                    ".yxj-paper-os/template-analysis/design-profile.json#entries.length"
                ],
                rule_kind="soft_band",
            )
        return base

    def test_positive_compatibility_rows_and_official_branches(self) -> None:
        official_hard = self.base_rule("official_constraint")
        official_hard.update(
            rule_kind="hard_constraint",
            resolution="confirmed",
            disposition="adopted",
            freshness="verified_local_current",
        )
        official_candidate = self.base_rule("official_constraint")
        semantic = self.base_rule("semantic_dossier")
        quantitative = self.base_rule("quantitative_analysis")
        for rule in (official_hard, official_candidate, semantic, quantitative):
            with self.subTest(kind=rule["grounding_kind"], rule=rule["rule_kind"]):
                self.assertEqual(validate_template_rule(rule), [])

    def test_incompatible_combination_per_grounding_kind(self) -> None:
        mutations = []
        official = self.base_rule("official_constraint")
        official["grounding_pointers"] = [
            ".yxj-paper-os/template-analysis/semantic-dossier.json#TOBS-method"
        ]
        mutations.append(official)
        semantic = self.base_rule("semantic_dossier")
        semantic["rule_kind"] = "hard_constraint"
        mutations.append(semantic)
        quantitative = self.base_rule("quantitative_analysis")
        quantitative["rule_kind"] = "candidate_pattern"
        mutations.append(quantitative)
        for rule in mutations:
            with self.subTest(rule=rule):
                self.assertIn(
                    TEMPLATE_RULE_INCOMPATIBLE, codes(validate_template_rule(rule))
                )

    def test_cross_kind_freshness_and_mixed_pointer_are_rejected(self) -> None:
        semantic = self.base_rule("semantic_dossier")
        semantic["freshness"] = "plugin:0.3.0+codex.test@sha256:" + "a" * 64
        self.assertIn(
            TEMPLATE_RULE_INCOMPATIBLE, codes(validate_template_rule(semantic))
        )
        mixed = self.base_rule("semantic_dossier")
        mixed["grounding_pointers"].append(
            ".yxj-paper-os/template-analysis/design-profile.json#entries.length"
        )
        self.assertIn(TEMPLATE_RULE_INCOMPATIBLE, codes(validate_template_rule(mixed)))

    def test_ordinary_stale_and_unavailable_are_type_compatible(self) -> None:
        for kind in (
            "official_constraint",
            "semantic_dossier",
            "quantitative_analysis",
        ):
            for freshness in ("stale", "unavailable"):
                rule = self.base_rule(kind)
                rule["freshness"] = freshness
                with self.subTest(kind=kind, freshness=freshness):
                    self.assertNotIn(
                        TEMPLATE_RULE_INCOMPATIBLE,
                        codes(validate_template_rule(rule)),
                    )

        official_hard = self.base_rule("official_constraint")
        official_hard.update(
            rule_kind="hard_constraint",
            resolution="confirmed",
            disposition="adopted",
            freshness="stale",
        )
        self.assertIn(
            TEMPLATE_RULE_INCOMPATIBLE,
            codes(validate_template_rule(official_hard)),
        )

    def test_malformed_rule_types_return_bounded_diagnostics(self) -> None:
        for value in (None, "SCOPE-main", ["SCOPE-main", {}]):
            rule = self.base_rule("semantic_dossier")
            rule["affected_scope_ids"] = value
            with self.subTest(value=value):
                diagnostics = validate_template_rule(rule)
                self.assertIn(TEMPLATE_RULE_INCOMPATIBLE, codes(diagnostics))

    def test_official_source_requires_real_locator_and_grounding(self) -> None:
        for field in ("locator", "grounding"):
            for value in ("none", "", "   "):
                rule = self.base_rule("official_constraint")
                rule.update(
                    rule_kind="hard_constraint",
                    resolution="confirmed",
                    disposition="adopted",
                )
                rule["official_source"][field] = value
                with self.subTest(field=field, value=value):
                    self.assertIn(
                        TEMPLATE_RULE_INCOMPATIBLE,
                        codes(validate_template_rule(rule)),
                    )

    def test_gate_and_analyzer_suggestion_rules(self) -> None:
        semantic = self.base_rule("semantic_dossier")
        semantic.update(
            disposition="deliberate_divergence",
            resolution="confirmed",
            gate_category="deliberate_divergence",
            decision_id="none",
        )
        self.assertIn(
            TEMPLATE_RULE_INCOMPATIBLE, codes(validate_template_rule(semantic))
        )
        semantic["decision_id"] = "DEC-diverge"
        self.assertEqual(validate_template_rule(semantic), [])
        self.assertEqual(
            ANALYZER_ACTION_TO_SUGGESTED_DISPOSITION,
            {
                "follow": "adopted",
                "adapt": "adapted",
                "deliberate_divergence": "deliberate_divergence",
                "not_applicable": "not_applicable",
            },
        )
        quantitative = self.base_rule("quantitative_analysis")
        quantitative.update(disposition="adopted", resolution="candidate")
        self.assertIn(
            TEMPLATE_RULE_INCOMPATIBLE, codes(validate_template_rule(quantitative))
        )

    def test_product_lens_registry_is_unique_and_every_entry_resolves(self) -> None:
        registry, diagnostics = load_lens_registry(LENSES / "README.md")
        self.assertEqual(diagnostics, [])
        self.assertEqual(len(registry), 7)
        for lens_id, module in registry.items():
            self.assertTrue((LENSES / module).is_file(), lens_id)

    def test_generic_fallback_registry_pointer_and_fingerprint(self) -> None:
        registry, diagnostics = load_lens_registry(LENSES / "README.md")
        self.assertEqual(diagnostics, [])
        module = LENSES / registry["argument-language-visual"]
        version = "0.3.0+codex.test"
        freshness = (
            f"plugin:{version}@sha256:"
            + hashlib.sha256(module.read_bytes()).hexdigest()
        )
        rule = self.base_rule("generic_fallback")
        rule.update(
            grounding_pointers=["lens:argument-language-visual#sufficiency-predicates"],
            freshness=freshness,
        )
        self.assertEqual(
            validate_template_rule(
                rule,
                lens_registry_path=LENSES / "README.md",
                plugin_version=version,
            ),
            [],
        )
        negative = {
            "bad-id": "lens:missing#sufficiency-predicates",
            "bad-slug": "lens:argument-language-visual#missing-heading",
            "h1-only": "lens:argument-language-visual#playbook-argument-language-and-visual",
        }
        for name, pointer in negative.items():
            mutated = copy.deepcopy(rule)
            mutated["grounding_pointers"] = [pointer]
            with self.subTest(name=name):
                self.assertIn(
                    TEMPLATE_RULE_INCOMPATIBLE,
                    codes(
                        validate_template_rule(
                            mutated,
                            lens_registry_path=LENSES / "README.md",
                            plugin_version=version,
                        )
                    ),
                )
        for name, value in (
            ("version", freshness.replace(version, "0.3.1+codex.test")),
            ("hash", freshness[:-64] + "0" * 64),
            ("ordinary", "verified_local_current"),
        ):
            mutated = copy.deepcopy(rule)
            mutated["freshness"] = value
            with self.subTest(name=name):
                self.assertIn(
                    TEMPLATE_RULE_INCOMPATIBLE,
                    codes(
                        validate_template_rule(
                            mutated,
                            lens_registry_path=LENSES / "README.md",
                            plugin_version=version,
                        )
                    ),
                )

    def test_generic_fallback_malformed_utf8_is_a_stable_diagnostic(self) -> None:
        rule = self.base_rule("generic_fallback")
        rule.update(
            grounding_pointers=["lens:test-lens#usable-heading"],
            freshness="plugin:0.3.0+codex.test@sha256:" + "0" * 64,
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = root / "README.md"
            module = root / "test-lens.md"
            for surface in ("registry", "module"):
                with self.subTest(surface=surface):
                    registry.write_text(
                        "## Lens Registry\n\n"
                        "| Lens ID | Module path | Primary focus | Typical activation |\n"
                        "|---|---|---|---|\n"
                        "| test-lens | test-lens.md | test | test |\n",
                        encoding="utf-8",
                    )
                    module.write_text("## Usable Heading\n", encoding="utf-8")
                    (registry if surface == "registry" else module).write_bytes(b"\xff")
                    diagnostics = validate_template_rule(
                        rule,
                        lens_registry_path=registry,
                        plugin_version="0.3.0+codex.test",
                    )
                    self.assertEqual(codes(diagnostics), {TEMPLATE_RULE_INCOMPATIBLE})
                    self.assertIn(f"lens {surface} unavailable", diagnostics[0].message)


if __name__ == "__main__":
    unittest.main(verbosity=2)
