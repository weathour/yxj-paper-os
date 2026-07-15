{
  "responses": [
    {
      "question": {
        "count": 0,
        "target": null
      },
      "readiness_updates": [
        {
          "blocker": null,
          "next_action": null,
          "output_pointer": "04_WRITING_DESIGN_PACK.md#SCOPE-RESULTS",
          "readiness": "writer-ready",
          "scope_id": "SCOPE-RESULTS"
        }
      ],
      "scenario_id": "B01",
      "selected_actions": [
        "INSPECT",
        "DERIVE",
        "PROJECT",
        "VALIDATE"
      ],
      "side_effects": [],
      "target_dimensions": [
        "D05",
        "D06",
        "D09",
        "D15"
      ],
      "target_scopes": [
        "SCOPE-RESULTS"
      ],
      "updates": [
        {
          "access_state": null,
          "analysis_mode": null,
          "candidate_action": null,
          "decision_pointer": null,
          "denominator": null,
          "design_only_state": "not_applicable",
          "design_payload": null,
          "effective_conclusion": null,
          "epistemic_label": "model-derived",
          "gate_category": null,
          "grounding": [
            "M-EXP-01",
            "C-RES-01"
          ],
          "linked_records": [],
          "locator": null,
          "missingness": null,
          "operation": "create",
          "origin": "model-derived",
          "partition": null,
          "promotion_pointer": null,
          "reason": "Function, reader-state, payload boundary, qualification and output promise",
          "record_id": "P-RESULT-01",
          "record_kind": "paragraph",
          "resolution": "confirmed",
          "role": null,
          "schema_version": "0.3",
          "status": "ready",
          "support": "not_applicable",
          "target_kind": "paragraph_function"
        },
        {
          "access_state": null,
          "analysis_mode": null,
          "candidate_action": null,
          "decision_pointer": null,
          "denominator": null,
          "design_only_state": "not_applicable",
          "design_payload": null,
          "effective_conclusion": null,
          "epistemic_label": "model-derived",
          "gate_category": null,
          "grounding": [
            "LIM-01",
            "FIG-01"
          ],
          "linked_records": [],
          "locator": null,
          "missingness": null,
          "operation": "create",
          "origin": "model-derived",
          "partition": null,
          "promotion_pointer": null,
          "reason": "Adverse-case function and forbidden overclaim",
          "record_id": "P-RESULT-02",
          "record_kind": "paragraph",
          "resolution": "confirmed",
          "role": null,
          "schema_version": "0.3",
          "status": "ready",
          "support": "not_applicable",
          "target_kind": "paragraph_function"
        }
      ]
    },
    {
      "question": {
        "count": 0,
        "target": null
      },
      "readiness_updates": [
        {
          "blocker": null,
          "next_action": null,
          "output_pointer": "04_WRITING_DESIGN_PACK.md#SCOPE-DISCUSSION",
          "readiness": "writer-ready",
          "scope_id": "SCOPE-DISCUSSION"
        }
      ],
      "scenario_id": "B02",
      "selected_actions": [
        "INSPECT",
        "DERIVE",
        "PROJECT",
        "VALIDATE"
      ],
      "side_effects": [],
      "target_dimensions": [
        "D05",
        "D09",
        "D15",
        "D17"
      ],
      "target_scopes": [
        "SCOPE-DISCUSSION"
      ],
      "updates": [
        {
          "access_state": null,
          "analysis_mode": null,
          "candidate_action": null,
          "decision_pointer": null,
          "denominator": null,
          "design_only_state": "not_applicable",
          "design_payload": "[bounded context] -> [observed limitation + M-ROBUST-03] -> [qualified bridge to C-BOUND-02]",
          "effective_conclusion": null,
          "epistemic_label": "model-derived",
          "gate_category": null,
          "grounding": [
            "P-DISC-03",
            "M-ROBUST-03",
            "C-BOUND-02"
          ],
          "linked_records": [],
          "locator": null,
          "missingness": null,
          "operation": "create",
          "origin": "model-derived",
          "partition": null,
          "promotion_pointer": null,
          "reason": "Clause-order and hedge contract; no prose realization",
          "record_id": "FRM-DISC-03-01",
          "record_kind": "frame",
          "resolution": "confirmed",
          "role": null,
          "schema_version": "0.3",
          "status": "ready",
          "support": "not_applicable",
          "target_kind": "controlled_sentence_frame"
        }
      ]
    },
    {
      "question": {
        "count": 0,
        "target": null
      },
      "readiness_updates": [
        {
          "blocker": null,
          "next_action": null,
          "output_pointer": "04_WRITING_DESIGN_PACK.md#SCOPE-INTRO",
          "readiness": "writer-ready",
          "scope_id": "SCOPE-INTRO"
        }
      ],
      "scenario_id": "B03",
      "selected_actions": [
        "INSPECT",
        "DERIVE",
        "PROJECT",
        "VALIDATE"
      ],
      "side_effects": [],
      "target_dimensions": [
        "D05",
        "D09",
        "D15"
      ],
      "target_scopes": [
        "SCOPE-INTRO"
      ],
      "updates": [
        {
          "access_state": null,
          "analysis_mode": null,
          "candidate_action": "adapt",
          "decision_pointer": null,
          "denominator": null,
          "design_only_state": "design_only",
          "design_payload": null,
          "effective_conclusion": null,
          "epistemic_label": "model-derived",
          "gate_category": null,
          "grounding": [
            "TPL-EXEMPLAR-01#Introduction paragraphs 2-4"
          ],
          "linked_records": [],
          "locator": null,
          "missingness": null,
          "operation": "create",
          "origin": "model-derived",
          "partition": null,
          "promotion_pointer": null,
          "reason": "Routine reversible adaptation of local paragraph order",
          "record_id": "TRULE-INTRO-ORDER",
          "record_kind": "template_rule",
          "resolution": "accepted",
          "role": null,
          "schema_version": "0.3",
          "status": "active",
          "support": "not_applicable",
          "target_kind": null
        }
      ]
    },
    {
      "question": {
        "count": 1,
        "target": "scientific_commitment"
      },
      "readiness_updates": [
        {
          "blocker": "GATE-scientific_commitment",
          "next_action": "owner decision",
          "output_pointer": null,
          "readiness": "blocked",
          "scope_id": "SCOPE-CLAIM"
        }
      ],
      "scenario_id": "B04",
      "selected_actions": [
        "INSPECT",
        "DERIVE",
        "ASK_OWNER"
      ],
      "side_effects": [],
      "target_dimensions": [
        "D06",
        "D11"
      ],
      "target_scopes": [
        "SCOPE-CLAIM"
      ],
      "updates": [
        {
          "access_state": null,
          "analysis_mode": null,
          "candidate_action": null,
          "decision_pointer": null,
          "denominator": null,
          "design_only_state": "not_applicable",
          "design_payload": null,
          "effective_conclusion": null,
          "epistemic_label": "model-proposed",
          "gate_category": "scientific_commitment",
          "grounding": [
            "Whether C-SAFETY-02 remains a bounded association or becomes a causal claim"
          ],
          "linked_records": [],
          "locator": null,
          "missingness": null,
          "operation": "create",
          "origin": "model-proposed",
          "partition": null,
          "promotion_pointer": null,
          "reason": "Focused scientific_commitment choice affects only SCOPE-CLAIM",
          "record_id": "DEC-B04",
          "record_kind": "decision",
          "resolution": "unresolved",
          "role": null,
          "schema_version": "0.3",
          "status": "candidate",
          "support": "not_applicable",
          "target_kind": null
        }
      ]
    },
    {
      "question": {
        "count": 1,
        "target": "argument_spine"
      },
      "readiness_updates": [
        {
          "blocker": "GATE-argument_spine",
          "next_action": "owner decision",
          "output_pointer": null,
          "readiness": "blocked",
          "scope_id": "SCOPE-PAPER"
        }
      ],
      "scenario_id": "B05",
      "selected_actions": [
        "INSPECT",
        "DERIVE",
        "ASK_OWNER"
      ],
      "side_effects": [],
      "target_dimensions": [
        "D05",
        "D07",
        "D09"
      ],
      "target_scopes": [
        "SCOPE-PAPER"
      ],
      "updates": [
        {
          "access_state": null,
          "analysis_mode": null,
          "candidate_action": null,
          "decision_pointer": null,
          "denominator": null,
          "design_only_state": "not_applicable",
          "design_payload": null,
          "effective_conclusion": null,
          "epistemic_label": "model-proposed",
          "gate_category": "argument_spine",
          "grounding": [
            "Whether mechanism or security-state evidence leads the contribution sequence"
          ],
          "linked_records": [],
          "locator": null,
          "missingness": null,
          "operation": "create",
          "origin": "model-proposed",
          "partition": null,
          "promotion_pointer": null,
          "reason": "Focused argument_spine choice affects only SCOPE-PAPER",
          "record_id": "DEC-B05",
          "record_kind": "decision",
          "resolution": "unresolved",
          "role": null,
          "schema_version": "0.3",
          "status": "candidate",
          "support": "not_applicable",
          "target_kind": null
        }
      ]
    },
    {
      "question": {
        "count": 1,
        "target": "material_local_tradeoff"
      },
      "readiness_updates": [
        {
          "blocker": "GATE-material_local_tradeoff",
          "next_action": "owner decision",
          "output_pointer": null,
          "readiness": "blocked",
          "scope_id": "SCOPE-DISCUSSION"
        }
      ],
      "scenario_id": "B06",
      "selected_actions": [
        "INSPECT",
        "DERIVE",
        "ASK_OWNER"
      ],
      "side_effects": [],
      "target_dimensions": [
        "D05",
        "D09",
        "D15"
      ],
      "target_scopes": [
        "SCOPE-DISCUSSION"
      ],
      "updates": [
        {
          "access_state": null,
          "analysis_mode": null,
          "candidate_action": null,
          "decision_pointer": null,
          "denominator": null,
          "design_only_state": "not_applicable",
          "design_payload": null,
          "effective_conclusion": null,
          "epistemic_label": "model-proposed",
          "gate_category": "material_local_tradeoff",
          "grounding": [
            "Whether the adverse finding is framed before or after the aggregate benefit"
          ],
          "linked_records": [],
          "locator": null,
          "missingness": null,
          "operation": "create",
          "origin": "model-proposed",
          "partition": null,
          "promotion_pointer": null,
          "reason": "Focused material_local_tradeoff choice affects only SCOPE-DISCUSSION",
          "record_id": "DEC-B06",
          "record_kind": "decision",
          "resolution": "unresolved",
          "role": null,
          "schema_version": "0.3",
          "status": "candidate",
          "support": "not_applicable",
          "target_kind": null
        }
      ]
    },
    {
      "question": {
        "count": 1,
        "target": "deliberate_divergence"
      },
      "readiness_updates": [
        {
          "blocker": "GATE-deliberate_divergence",
          "next_action": "owner decision",
          "output_pointer": null,
          "readiness": "blocked",
          "scope_id": "SCOPE-INTRO"
        }
      ],
      "scenario_id": "B07",
      "selected_actions": [
        "INSPECT",
        "DERIVE",
        "ASK_OWNER"
      ],
      "side_effects": [],
      "target_dimensions": [
        "D09",
        "D15",
        "D19"
      ],
      "target_scopes": [
        "SCOPE-INTRO"
      ],
      "updates": [
        {
          "access_state": null,
          "analysis_mode": null,
          "candidate_action": null,
          "decision_pointer": null,
          "denominator": null,
          "design_only_state": "not_applicable",
          "design_payload": null,
          "effective_conclusion": null,
          "epistemic_label": "model-proposed",
          "gate_category": "deliberate_divergence",
          "grounding": [
            "Whether to retain the deliberate two-paragraph divergence from TRULE-INTRO-ORDER"
          ],
          "linked_records": [],
          "locator": null,
          "missingness": null,
          "operation": "create",
          "origin": "model-proposed",
          "partition": null,
          "promotion_pointer": null,
          "reason": "Focused deliberate_divergence choice affects only SCOPE-INTRO",
          "record_id": "DEC-B07",
          "record_kind": "decision",
          "resolution": "unresolved",
          "role": null,
          "schema_version": "0.3",
          "status": "candidate",
          "support": "not_applicable",
          "target_kind": null
        }
      ]
    },
    {
      "question": {
        "count": 0,
        "target": null
      },
      "readiness_updates": [
        {
          "blocker": "CLAIM-EVIDENCE-MISSING",
          "next_action": "retain inactive claim",
          "output_pointer": null,
          "readiness": "partial",
          "scope_id": "SCOPE-TEMPLATE-CLAIM"
        }
      ],
      "scenario_id": "B08",
      "selected_actions": [
        "INSPECT",
        "DERIVE",
        "PROJECT",
        "VALIDATE"
      ],
      "side_effects": [],
      "target_dimensions": [
        "D01",
        "D06",
        "D09",
        "D11"
      ],
      "target_scopes": [
        "SCOPE-TEMPLATE-CLAIM"
      ],
      "updates": [
        {
          "access_state": "full_text",
          "analysis_mode": null,
          "candidate_action": null,
          "decision_pointer": null,
          "denominator": null,
          "design_only_state": "design_only",
          "design_payload": null,
          "effective_conclusion": null,
          "epistemic_label": "artifact-observed",
          "gate_category": null,
          "grounding": [],
          "linked_records": [],
          "locator": "https://example.org/target-paper",
          "missingness": null,
          "operation": "create",
          "origin": "artifact-observed",
          "partition": null,
          "promotion_pointer": null,
          "reason": "External exemplar restricted to writing design",
          "record_id": "TPL-EXT-08",
          "record_kind": "template_source",
          "resolution": "confirmed",
          "role": "target_topic",
          "schema_version": "0.3",
          "status": "active",
          "support": "not_applicable",
          "target_kind": null
        },
        {
          "access_state": null,
          "analysis_mode": null,
          "candidate_action": null,
          "decision_pointer": null,
          "denominator": null,
          "design_only_state": "not_applicable",
          "design_payload": null,
          "effective_conclusion": null,
          "epistemic_label": "model-derived",
          "gate_category": null,
          "grounding": [],
          "linked_records": [],
          "locator": null,
          "missingness": null,
          "operation": "create",
          "origin": "model-derived",
          "partition": null,
          "promotion_pointer": null,
          "reason": "Template material cannot support scientific novelty",
          "record_id": "C-NOVELTY-01",
          "record_kind": "claim",
          "resolution": "confirmed",
          "role": null,
          "schema_version": "0.3",
          "status": "inactive",
          "support": "evidence-unsupported",
          "target_kind": null
        }
      ]
    },
    {
      "question": {
        "count": 0,
        "target": null
      },
      "readiness_updates": [
        {
          "blocker": null,
          "next_action": null,
          "output_pointer": "04_WRITING_DESIGN_PACK.md#SCOPE-INTRO-SEMANTIC",
          "readiness": "writer-ready",
          "scope_id": "SCOPE-INTRO-SEMANTIC"
        }
      ],
      "scenario_id": "B09",
      "selected_actions": [
        "INSPECT",
        "DERIVE",
        "PROJECT",
        "VALIDATE"
      ],
      "side_effects": [],
      "target_dimensions": [
        "D01",
        "D05",
        "D09",
        "D15",
        "D19"
      ],
      "target_scopes": [
        "SCOPE-INTRO-SEMANTIC"
      ],
      "updates": [
        {
          "access_state": "full_text",
          "analysis_mode": null,
          "candidate_action": null,
          "decision_pointer": null,
          "denominator": null,
          "design_only_state": "design_only",
          "design_payload": null,
          "effective_conclusion": null,
          "epistemic_label": "artifact-observed",
          "gate_category": null,
          "grounding": [
            "TPL-SEM-01"
          ],
          "linked_records": [],
          "locator": ".yxj-paper-os/template-analysis/semantic-dossier.json",
          "missingness": null,
          "operation": "create",
          "origin": "artifact-observed",
          "partition": null,
          "promotion_pointer": null,
          "reason": "Fresh full-text semantic observations with locators",
          "record_id": "DOSSIER-SEM-09",
          "record_kind": "semantic_dossier",
          "resolution": "confirmed",
          "role": null,
          "schema_version": "0.3",
          "status": "confirmed",
          "support": "not_applicable",
          "target_kind": null
        },
        {
          "access_state": null,
          "analysis_mode": null,
          "candidate_action": null,
          "decision_pointer": "DOSSIER-SEM-09",
          "denominator": null,
          "design_only_state": "design_only",
          "design_payload": null,
          "effective_conclusion": null,
          "epistemic_label": "model-derived",
          "gate_category": null,
          "grounding": [
            "TPL-SEM-01#Introduction paragraphs 1-3"
          ],
          "linked_records": [],
          "locator": null,
          "missingness": null,
          "operation": "create",
          "origin": "model-derived",
          "partition": null,
          "promotion_pointer": null,
          "reason": "Semantic-primary design projection",
          "record_id": "TRULE-SEM-01",
          "record_kind": "template_rule",
          "resolution": "confirmed",
          "role": null,
          "schema_version": "0.3",
          "status": "active",
          "support": "not_applicable",
          "target_kind": null
        }
      ]
    },
    {
      "question": {
        "count": 0,
        "target": null
      },
      "readiness_updates": [
        {
          "blocker": null,
          "next_action": null,
          "output_pointer": "04_WRITING_DESIGN_PACK.md#SCOPE-RESULTS-QUANT",
          "readiness": "writer-ready",
          "scope_id": "SCOPE-RESULTS-QUANT"
        }
      ],
      "scenario_id": "B10",
      "selected_actions": [
        "INSPECT",
        "DERIVE",
        "PROJECT",
        "VALIDATE"
      ],
      "side_effects": [
        "template_analysis"
      ],
      "target_dimensions": [
        "D09",
        "D15",
        "D18",
        "D19"
      ],
      "target_scopes": [
        "SCOPE-RESULTS-QUANT"
      ],
      "updates": [
        {
          "access_state": null,
          "analysis_mode": "distributional",
          "candidate_action": null,
          "decision_pointer": null,
          "denominator": "15 eligible;13 valid;2 missing supported object locator",
          "design_only_state": "design_only",
          "design_payload": null,
          "effective_conclusion": "descriptive design distribution only; no semantic, causal, venue-fit, or acceptance conclusion",
          "epistemic_label": "artifact-observed",
          "gate_category": null,
          "grounding": [
            "object.figure_position_norm"
          ],
          "linked_records": [],
          "locator": ".yxj-paper-os/template-analysis/design-profile.json",
          "missingness": "2 missing supported object locator",
          "operation": "create",
          "origin": "artifact-observed",
          "partition": "target_topic versus control",
          "promotion_pointer": null,
          "reason": "Optional metric-backed answer with partition and missingness boundaries",
          "record_id": "ANALYSIS-10",
          "record_kind": "template_analysis",
          "resolution": "confirmed",
          "role": null,
          "schema_version": "0.3",
          "status": "active",
          "support": "not_applicable",
          "target_kind": "figure_position_design"
        }
      ]
    },
    {
      "question": {
        "count": 0,
        "target": null
      },
      "readiness_updates": [
        {
          "blocker": "STALE-M-RESULT-A",
          "next_action": "recompile linked records",
          "output_pointer": null,
          "readiness": "partial",
          "scope_id": "SCOPE-RESULT-A"
        },
        {
          "blocker": null,
          "next_action": null,
          "output_pointer": "04_WRITING_DESIGN_PACK.md#SCOPE-RESULT-B",
          "readiness": "writer-ready",
          "scope_id": "SCOPE-RESULT-B"
        }
      ],
      "scenario_id": "B11",
      "selected_actions": [
        "INSPECT",
        "DERIVE",
        "PROJECT",
        "VALIDATE"
      ],
      "side_effects": [],
      "target_dimensions": [
        "D03",
        "D05",
        "D09",
        "D15",
        "D18",
        "D19"
      ],
      "target_scopes": [
        "SCOPE-RESULT-A",
        "SCOPE-RESULT-B"
      ],
      "updates": [
        {
          "access_state": null,
          "analysis_mode": null,
          "candidate_action": null,
          "decision_pointer": null,
          "denominator": null,
          "design_only_state": "not_applicable",
          "design_payload": null,
          "effective_conclusion": null,
          "epistemic_label": "model-derived",
          "gate_category": null,
          "grounding": [],
          "linked_records": [
            "M-RESULT-A"
          ],
          "locator": null,
          "missingness": null,
          "operation": "revise",
          "origin": "model-derived",
          "partition": null,
          "promotion_pointer": null,
          "reason": "Direct M-RESULT-A dependency changed",
          "record_id": "P-RESULT-A2",
          "record_kind": "paragraph",
          "resolution": "confirmed",
          "role": null,
          "schema_version": "0.3",
          "status": "stale",
          "support": "not_applicable",
          "target_kind": null
        },
        {
          "access_state": null,
          "analysis_mode": null,
          "candidate_action": null,
          "decision_pointer": null,
          "denominator": null,
          "design_only_state": "not_applicable",
          "design_payload": "[updated result + M-RESULT-A] -> [bounded interpretation]",
          "effective_conclusion": null,
          "epistemic_label": "model-derived",
          "gate_category": null,
          "grounding": [],
          "linked_records": [
            "M-RESULT-A"
          ],
          "locator": null,
          "missingness": null,
          "operation": "revise",
          "origin": "model-derived",
          "partition": null,
          "promotion_pointer": null,
          "reason": "Direct M-RESULT-A payload changed",
          "record_id": "FRM-RESULT-A2-01",
          "record_kind": "frame",
          "resolution": "confirmed",
          "role": null,
          "schema_version": "0.3",
          "status": "stale",
          "support": "not_applicable",
          "target_kind": "controlled_sentence_frame"
        },
        {
          "access_state": null,
          "analysis_mode": null,
          "candidate_action": null,
          "decision_pointer": null,
          "denominator": null,
          "design_only_state": "not_applicable",
          "design_payload": null,
          "effective_conclusion": null,
          "epistemic_label": "model-derived",
          "gate_category": null,
          "grounding": [],
          "linked_records": [
            "M-RESULT-A"
          ],
          "locator": null,
          "missingness": null,
          "operation": "revise",
          "origin": "model-derived",
          "partition": null,
          "promotion_pointer": null,
          "reason": "Direct M-RESULT-A visual payload changed",
          "record_id": "VIS-RESULT-A",
          "record_kind": "visual",
          "resolution": "confirmed",
          "role": null,
          "schema_version": "0.3",
          "status": "stale",
          "support": "not_applicable",
          "target_kind": null
        },
        {
          "access_state": null,
          "analysis_mode": null,
          "candidate_action": null,
          "decision_pointer": null,
          "denominator": null,
          "design_only_state": "design_only",
          "design_payload": null,
          "effective_conclusion": null,
          "epistemic_label": "model-derived",
          "gate_category": null,
          "grounding": [],
          "linked_records": [
            "M-RESULT-A"
          ],
          "locator": null,
          "missingness": null,
          "operation": "revise",
          "origin": "model-derived",
          "partition": null,
          "promotion_pointer": null,
          "reason": "Application snapshot links to changed paragraph",
          "record_id": "TRULE-RESULT-A",
          "record_kind": "template_rule",
          "resolution": "confirmed",
          "role": null,
          "schema_version": "0.3",
          "status": "stale",
          "support": "not_applicable",
          "target_kind": null
        }
      ]
    },
    {
      "question": {
        "count": 0,
        "target": null
      },
      "readiness_updates": [
        {
          "blocker": "SCHEMA_LEGACY_02",
          "next_action": "agent-led 0.2-to-0.3 recompilation",
          "output_pointer": null,
          "readiness": "partial",
          "scope_id": "SCOPE-LEGACY"
        }
      ],
      "scenario_id": "B12",
      "selected_actions": [
        "INSPECT",
        "VALIDATE"
      ],
      "side_effects": [],
      "target_dimensions": [
        "D00",
        "D19"
      ],
      "target_scopes": [
        "SCOPE-LEGACY"
      ],
      "updates": [
        {
          "access_state": null,
          "analysis_mode": null,
          "candidate_action": null,
          "decision_pointer": null,
          "denominator": null,
          "design_only_state": "not_applicable",
          "design_payload": null,
          "effective_conclusion": null,
          "epistemic_label": "model-derived",
          "gate_category": null,
          "grounding": [],
          "linked_records": [],
          "locator": null,
          "missingness": null,
          "operation": "create",
          "origin": "model-derived",
          "partition": null,
          "promotion_pointer": null,
          "reason": "Legacy detailed-readiness migration required; preserve and recompile non-destructively",
          "record_id": "SCHEMA_LEGACY_02",
          "record_kind": "diagnostic",
          "resolution": "confirmed",
          "role": null,
          "schema_version": "0.2",
          "status": "partial",
          "support": "not_applicable",
          "target_kind": null
        }
      ]
    },
    {
      "question": {
        "count": 0,
        "target": null
      },
      "readiness_updates": [
        {
          "blocker": null,
          "next_action": null,
          "output_pointer": "04_WRITING_DESIGN_PACK.md#SCOPE-FULL-03",
          "readiness": "writer-ready",
          "scope_id": "SCOPE-FULL-03"
        }
      ],
      "scenario_id": "B13",
      "selected_actions": [
        "INSPECT",
        "DERIVE",
        "PROJECT",
        "VALIDATE"
      ],
      "side_effects": [],
      "target_dimensions": [
        "D00",
        "D05",
        "D09",
        "D15",
        "D18",
        "D19"
      ],
      "target_scopes": [
        "SCOPE-FULL-03"
      ],
      "updates": [
        {
          "access_state": null,
          "analysis_mode": null,
          "candidate_action": null,
          "decision_pointer": null,
          "denominator": null,
          "design_only_state": "not_applicable",
          "design_payload": null,
          "effective_conclusion": null,
          "epistemic_label": "model-derived",
          "gate_category": null,
          "grounding": [],
          "linked_records": [],
          "locator": null,
          "missingness": null,
          "operation": "create",
          "origin": "model-derived",
          "partition": null,
          "promotion_pointer": null,
          "reason": "Declared paragraph_function coverage resolves to 03 authority",
          "record_id": "SURFACE-01",
          "record_kind": "surface",
          "resolution": "confirmed",
          "role": null,
          "schema_version": "0.3",
          "status": "ready",
          "support": "not_applicable",
          "target_kind": "paragraph_function"
        },
        {
          "access_state": null,
          "analysis_mode": null,
          "candidate_action": null,
          "decision_pointer": null,
          "denominator": null,
          "design_only_state": "not_applicable",
          "design_payload": null,
          "effective_conclusion": null,
          "epistemic_label": "model-derived",
          "gate_category": null,
          "grounding": [],
          "linked_records": [],
          "locator": null,
          "missingness": null,
          "operation": "create",
          "origin": "model-derived",
          "partition": null,
          "promotion_pointer": null,
          "reason": "Declared controlled_frame coverage resolves to 03 authority",
          "record_id": "SURFACE-02",
          "record_kind": "surface",
          "resolution": "confirmed",
          "role": null,
          "schema_version": "0.3",
          "status": "ready",
          "support": "not_applicable",
          "target_kind": "controlled_frame"
        },
        {
          "access_state": null,
          "analysis_mode": null,
          "candidate_action": null,
          "decision_pointer": null,
          "denominator": null,
          "design_only_state": "not_applicable",
          "design_payload": null,
          "effective_conclusion": null,
          "epistemic_label": "model-derived",
          "gate_category": null,
          "grounding": [],
          "linked_records": [],
          "locator": null,
          "missingness": null,
          "operation": "create",
          "origin": "model-derived",
          "partition": null,
          "promotion_pointer": null,
          "reason": "Declared language_contract coverage resolves to 03 authority",
          "record_id": "SURFACE-03",
          "record_kind": "surface",
          "resolution": "confirmed",
          "role": null,
          "schema_version": "0.3",
          "status": "ready",
          "support": "not_applicable",
          "target_kind": "language_contract"
        },
        {
          "access_state": null,
          "analysis_mode": null,
          "candidate_action": null,
          "decision_pointer": null,
          "denominator": null,
          "design_only_state": "not_applicable",
          "design_payload": null,
          "effective_conclusion": null,
          "epistemic_label": "model-derived",
          "gate_category": null,
          "grounding": [],
          "linked_records": [],
          "locator": null,
          "missingness": null,
          "operation": "create",
          "origin": "model-derived",
          "partition": null,
          "promotion_pointer": null,
          "reason": "Declared visual_caption coverage resolves to 03 authority",
          "record_id": "SURFACE-04",
          "record_kind": "surface",
          "resolution": "confirmed",
          "role": null,
          "schema_version": "0.3",
          "status": "ready",
          "support": "not_applicable",
          "target_kind": "visual_caption"
        },
        {
          "access_state": null,
          "analysis_mode": null,
          "candidate_action": null,
          "decision_pointer": null,
          "denominator": null,
          "design_only_state": "not_applicable",
          "design_payload": null,
          "effective_conclusion": null,
          "epistemic_label": "model-derived",
          "gate_category": null,
          "grounding": [],
          "linked_records": [],
          "locator": null,
          "missingness": null,
          "operation": "create",
          "origin": "model-derived",
          "partition": null,
          "promotion_pointer": null,
          "reason": "Declared cross_surface_traceability coverage resolves to 03 authority",
          "record_id": "SURFACE-05",
          "record_kind": "surface",
          "resolution": "confirmed",
          "role": null,
          "schema_version": "0.3",
          "status": "ready",
          "support": "not_applicable",
          "target_kind": "cross_surface_traceability"
        },
        {
          "access_state": null,
          "analysis_mode": null,
          "candidate_action": null,
          "decision_pointer": null,
          "denominator": null,
          "design_only_state": "not_applicable",
          "design_payload": null,
          "effective_conclusion": null,
          "epistemic_label": "model-derived",
          "gate_category": null,
          "grounding": [],
          "linked_records": [],
          "locator": null,
          "missingness": null,
          "operation": "create",
          "origin": "model-derived",
          "partition": null,
          "promotion_pointer": null,
          "reason": "Declared template_rule_provenance coverage resolves to 03 authority",
          "record_id": "SURFACE-06",
          "record_kind": "surface",
          "resolution": "confirmed",
          "role": null,
          "schema_version": "0.3",
          "status": "ready",
          "support": "not_applicable",
          "target_kind": "template_rule_provenance"
        },
        {
          "access_state": null,
          "analysis_mode": null,
          "candidate_action": null,
          "decision_pointer": null,
          "denominator": null,
          "design_only_state": "not_applicable",
          "design_payload": null,
          "effective_conclusion": null,
          "epistemic_label": "model-derived",
          "gate_category": null,
          "grounding": [],
          "linked_records": [],
          "locator": null,
          "missingness": null,
          "operation": "create",
          "origin": "model-derived",
          "partition": null,
          "promotion_pointer": null,
          "reason": "Declared soft_budget coverage resolves to 03 authority",
          "record_id": "SURFACE-07",
          "record_kind": "surface",
          "resolution": "confirmed",
          "role": null,
          "schema_version": "0.3",
          "status": "ready",
          "support": "not_applicable",
          "target_kind": "soft_budget"
        }
      ]
    },
    {
      "question": {
        "count": 0,
        "target": null
      },
      "readiness_updates": [
        {
          "blocker": null,
          "next_action": null,
          "output_pointer": "04_WRITING_DESIGN_PACK.md#SCOPE-DUAL-ROLE",
          "readiness": "writer-ready",
          "scope_id": "SCOPE-DUAL-ROLE"
        }
      ],
      "scenario_id": "B14",
      "selected_actions": [
        "INSPECT",
        "DERIVE",
        "PROJECT",
        "VALIDATE"
      ],
      "side_effects": [],
      "target_dimensions": [
        "D01",
        "D06",
        "D09",
        "D11"
      ],
      "target_scopes": [
        "SCOPE-DUAL-ROLE"
      ],
      "updates": [
        {
          "access_state": null,
          "analysis_mode": null,
          "candidate_action": null,
          "decision_pointer": null,
          "denominator": null,
          "design_only_state": "design_only",
          "design_payload": null,
          "effective_conclusion": null,
          "epistemic_label": "artifact-observed",
          "gate_category": null,
          "grounding": [],
          "linked_records": [],
          "locator": "doi:10.0000/example.14",
          "missingness": null,
          "operation": "create",
          "origin": "artifact-observed",
          "partition": null,
          "promotion_pointer": "M-PUB-14",
          "reason": "Separate design-only publication role",
          "record_id": "TPL-PUB-14",
          "record_kind": "template_source",
          "resolution": "confirmed",
          "role": "template_exemplar",
          "schema_version": "0.3",
          "status": "active",
          "support": "not_applicable",
          "target_kind": null
        },
        {
          "access_state": null,
          "analysis_mode": null,
          "candidate_action": null,
          "decision_pointer": "02_CLAIM_EVIDENCE_BOUNDARY.md#M-PUB-14",
          "denominator": null,
          "design_only_state": "not_applicable",
          "design_payload": null,
          "effective_conclusion": null,
          "epistemic_label": "artifact-observed",
          "gate_category": null,
          "grounding": [],
          "linked_records": [],
          "locator": "doi:10.0000/example.14",
          "missingness": null,
          "operation": "create",
          "origin": "artifact-observed",
          "partition": null,
          "promotion_pointer": null,
          "reason": "Separate scientific-source evaluation role",
          "record_id": "M-PUB-14",
          "record_kind": "material",
          "resolution": "confirmed",
          "role": "scientific_source",
          "schema_version": "0.3",
          "status": "active",
          "support": "not_applicable",
          "target_kind": null
        }
      ]
    },
    {
      "question": {
        "count": 0,
        "target": null
      },
      "readiness_updates": [
        {
          "blocker": "FULL_TEXT_UNAVAILABLE",
          "next_action": "retain metadata-only status",
          "output_pointer": null,
          "readiness": "partial",
          "scope_id": "SCOPE-EXTERNAL-META"
        }
      ],
      "scenario_id": "B15",
      "selected_actions": [
        "INSPECT",
        "PROJECT",
        "VALIDATE"
      ],
      "side_effects": [],
      "target_dimensions": [
        "D01",
        "D09"
      ],
      "target_scopes": [
        "SCOPE-EXTERNAL-META"
      ],
      "updates": [
        {
          "access_state": "metadata_only",
          "analysis_mode": null,
          "candidate_action": null,
          "decision_pointer": null,
          "denominator": null,
          "design_only_state": "design_only",
          "design_payload": null,
          "effective_conclusion": null,
          "epistemic_label": "artifact-observed",
          "gate_category": null,
          "grounding": [],
          "linked_records": [],
          "locator": "https://example.org/inaccessible-paper",
          "missingness": null,
          "operation": "create",
          "origin": "artifact-observed",
          "partition": null,
          "promotion_pointer": null,
          "reason": "Metadata inventory only; no semantic observation",
          "record_id": "TPL-META-15",
          "record_kind": "template_source",
          "resolution": "confirmed",
          "role": null,
          "schema_version": "0.3",
          "status": "active",
          "support": "not_applicable",
          "target_kind": "metadata_only"
        }
      ]
    }
  ]
}
