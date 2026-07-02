# Graph Report - .  (2026-07-03)

## Corpus Check
- 86 files · ~1,101,006 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1063 nodes · 3173 edges · 55 communities detected
- Extraction: 80% EXTRACTED · 20% INFERRED · 0% AMBIGUOUS · INFERRED: 632 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]

## God Nodes (most connected - your core abstractions)
1. `issue()` - 211 edges
2. `_require_mapping()` - 87 edges
3. `read_text()` - 62 edges
4. `is_non_empty_string()` - 58 edges
5. `_require_mapping_fields()` - 49 edges
6. `load_document()` - 40 edges
7. `GraphStore` - 33 edges
8. `_require_string_list()` - 32 edges
9. `_require_s09_list()` - 29 edges
10. `is_non_empty_mapping_list()` - 27 edges

## Surprising Connections (you probably didn't know these)
- `load_freq_prior_data()` --calls--> `load()`  [INFERRED]
  third_party/nature-figure/assets/figures4papers/figure_FPGM/plot_freq_prior.py → scripts/verify_lifecycle_contract.py
- `update()` --calls--> `_validate_s04_result_boundaries()`  [INFERRED]
  docs/runtime-viewer/app.js → scripts/validate_material.py
- `update()` --calls--> `_validate_s06_cross_maps()`  [INFERRED]
  docs/runtime-viewer/app.js → scripts/validate_material.py
- `update()` --calls--> `_validate_s08_contracts()`  [INFERRED]
  docs/runtime-viewer/app.js → scripts/validate_material.py
- `update()` --calls--> `_collect_s16_required_manifest_paths()`  [INFERRED]
  docs/runtime-viewer/app.js → scripts/validate_material.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (203): as_mapping(), is_non_empty_mapping_list(), is_non_empty_string(), _collect_s16_required_manifest_paths(), _contains_forbidden_key(), _find_s16_narrative_overclaim(), _has_non_empty_payload_value(), _normalize_s16_text() (+195 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (98): build_candidate_placeholder(), build_run_task_packet(), compute_source_snapshot(), ensure_output_file_safe(), ensure_run_root_safe(), ensure_source_snapshot_no_runtime_artifacts(), generate(), is_relative_to() (+90 more)

### Community 2 - "Community 2"
Cohesion: 0.05
Nodes (76): _active_material_node(), build_parser(), compile_backflow(), _graph_issues(), main(), _mapping_label(), MappingRule, _material_version_handle() (+68 more)

### Community 3 - "Community 3"
Cohesion: 0.07
Nodes (54): read_text(), fail(), main(), _node_label(), Only runtime fixture artifact handles are forced to exist.      Current examples, _relative_to_repo(), _requires_runtime_artifact_check(), validate() (+46 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (42): activatePreset(), appendCardList(), appendEmpty(), appendKeyValue(), appendList(), appendPath(), appendStateSection(), applyZoom() (+34 more)

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (53): backup_targets(), copy_from_candidate(), diff_snapshots(), ensure_under_root(), format_commit_message(), git_commit_after_validation(), local_apply_policy(), main() (+45 more)

### Community 6 - "Community 6"
Cohesion: 0.09
Nodes (48): as_sequence(), is_non_empty(), is_non_empty_string_list(), issue(), lint_paper_facing_terms(), load_document(), _parse_block(), _parse_key_value() (+40 more)

### Community 7 - "Community 7"
Cohesion: 0.09
Nodes (47): sha256_bytes(), sha256_file(), sha256_text(), ensure_output_safe(), extract_claim_boundary(), fail(), file_fingerprint(), is_relative_to() (+39 more)

### Community 8 - "Community 8"
Cohesion: 0.18
Nodes (23): _active_material_handle(), _apply_nature_overlay(), _base_packet(), build_parser(), _claim_repair_packet(), _clear_file_output(), _compile_for_target(), compile_task_packet() (+15 more)

### Community 9 - "Community 9"
Cohesion: 0.26
Nodes (22): approx_same(), boundary_line_allowed(), existing_file(), is_regular_file_no_symlink(), issue(), load_json_file(), load_jsonl_file(), main() (+14 more)

### Community 10 - "Community 10"
Cohesion: 0.24
Nodes (22): boundary_line_allowed(), check_no_overclaim(), is_regular_file_no_symlink(), jsonl_events(), load_json_file(), main(), rel(), run_owned_existing_file() (+14 more)

### Community 11 - "Community 11"
Cohesion: 0.23
Nodes (21): build_artifact(), build_graph(), build_run(), build_summary(), consumed_materials(), ensure_output_file_safe(), ensure_output_files_safe(), ensure_pilot_root_safe() (+13 more)

### Community 12 - "Community 12"
Cohesion: 0.21
Nodes (17): Exception, load_freq_prior_data(), assert_repair_authority_ref(), canonical_stages(), ContractError, load(), main(), normalize_material() (+9 more)

### Community 13 - "Community 13"
Cohesion: 0.26
Nodes (17): _fail(), _load_json(), main(), _run_validate(), _verify_fixtures(), _verify_phase10(), _verify_schema(), _verify_stage_contracts() (+9 more)

### Community 14 - "Community 14"
Cohesion: 0.22
Nodes (11): FancyArrowPatch, Arrow3D, draw_geodesic(), nice_axes(), pairwise_sqdist(), plot_angular_spread(), plot_l2_repel(), plot_orthogonalization() (+3 more)

### Community 15 - "Community 15"
Cohesion: 0.31
Nodes (13): build_parser(), _closure_payload(), _emit_yaml_value(), finding_payload(), _gate_payload(), _has_overclaim(), main(), _print_issues() (+5 more)

### Community 16 - "Community 16"
Cohesion: 0.36
Nodes (12): _active_authority_route_detected(), canonical_stage_ids(), issue(), load_json(), main(), Reject active self-managing route semantics without rejecting explanatory prose., run_fixture_matrix(), stage_by_id() (+4 more)

### Community 17 - "Community 17"
Cohesion: 0.51
Nodes (10): _fail(), _load_json(), _load_yaml(), main(), _run(), _verify_fixtures(), _verify_packet(), _verify_phase10() (+2 more)

### Community 18 - "Community 18"
Cohesion: 0.49
Nodes (10): _fail(), _load_json(), _load_yaml(), main(), _run(), _verify_fixtures(), _verify_phase10(), _verify_s09b_packet() (+2 more)

### Community 19 - "Community 19"
Cohesion: 0.51
Nodes (10): _fail(), _load_json(), _load_yaml(), main(), _run(), _verify_fixtures(), _verify_packet(), _verify_phase10() (+2 more)

### Community 20 - "Community 20"
Cohesion: 0.51
Nodes (10): _fail(), _load_json(), _load_yaml(), main(), _run(), _verify_fixtures(), _verify_packet(), _verify_phase10() (+2 more)

### Community 21 - "Community 21"
Cohesion: 0.51
Nodes (10): _fail(), _load_json(), _load_yaml(), main(), _run(), _verify_fixtures(), _verify_packet(), _verify_phase10() (+2 more)

### Community 22 - "Community 22"
Cohesion: 0.44
Nodes (10): find_stage(), find_validator(), issue(), load_json(), main(), validate_material_fixture(), verify_payload_schema_vocab(), verify_positive_and_negative_fixtures() (+2 more)

### Community 23 - "Community 23"
Cohesion: 0.51
Nodes (10): _fail(), _load_json(), _load_yaml(), main(), _run(), _verify_fixtures(), _verify_packet(), _verify_phase10() (+2 more)

### Community 24 - "Community 24"
Cohesion: 0.51
Nodes (10): _fail(), _load_json(), _load_yaml(), main(), _run(), _verify_fixtures(), _verify_packet(), _verify_phase10() (+2 more)

### Community 25 - "Community 25"
Cohesion: 0.51
Nodes (10): _fail(), _load_json(), _load_yaml(), main(), _run(), _verify_fixtures(), _verify_packet(), _verify_phase10() (+2 more)

### Community 26 - "Community 26"
Cohesion: 0.53
Nodes (8): fail(), load_doc(), load_json(), main(), run(), verify_fixtures(), verify_registry_phase(), verify_schema_packet_material()

### Community 27 - "Community 27"
Cohesion: 0.53
Nodes (8): fail(), load_doc(), load_json(), main(), run(), verify_fixtures(), verify_registry_phase(), verify_schema_packet()

### Community 28 - "Community 28"
Cohesion: 0.5
Nodes (8): fail(), load_doc(), load_json(), main(), run(), verify_fixtures(), verify_registry_phase(), verify_schema_material()

### Community 29 - "Community 29"
Cohesion: 0.53
Nodes (8): is_relative_to(), issue(), load_json(), main(), scoped_repo_path(), validate_contract(), validate_lane_policy(), validate_schema_contract()

### Community 30 - "Community 30"
Cohesion: 0.61
Nodes (7): is_safe_manifest_path(), issue(), load_json(), main(), validate_latex_profile(), validate_manifest(), validate_role_paths()

### Community 31 - "Community 31"
Cohesion: 0.67
Nodes (6): issue(), load_registry(), main(), run_negative_cases(), validate_lane_policy(), validate_registry()

### Community 32 - "Community 32"
Cohesion: 0.6
Nodes (4): mark_events(), month_year_list(), plot_curve(), # NOTE: Use `*` to move the label up in the annotation. Each `*` moves it up a b

### Community 33 - "Community 33"
Cohesion: 0.5
Nodes (4): plot_radar(), Benchmark = part after the first newline (e.g. 'Qwen2.5-VL-7B\\nMathVista' -> 'M, Single radar chart. Each axis = one subtask; one curve per method.     Each benc, _task_suffix()

### Community 34 - "Community 34"
Cohesion: 0.67
Nodes (0): 

### Community 35 - "Community 35"
Cohesion: 0.67
Nodes (0): 

### Community 36 - "Community 36"
Cohesion: 1.0
Nodes (0): 

### Community 37 - "Community 37"
Cohesion: 1.0
Nodes (0): 

### Community 38 - "Community 38"
Cohesion: 1.0
Nodes (0): 

### Community 39 - "Community 39"
Cohesion: 1.0
Nodes (0): 

### Community 40 - "Community 40"
Cohesion: 1.0
Nodes (0): 

### Community 41 - "Community 41"
Cohesion: 1.0
Nodes (0): 

### Community 42 - "Community 42"
Cohesion: 1.0
Nodes (0): 

### Community 43 - "Community 43"
Cohesion: 1.0
Nodes (0): 

### Community 44 - "Community 44"
Cohesion: 1.0
Nodes (0): 

### Community 45 - "Community 45"
Cohesion: 1.0
Nodes (0): 

### Community 46 - "Community 46"
Cohesion: 1.0
Nodes (0): 

### Community 47 - "Community 47"
Cohesion: 1.0
Nodes (0): 

### Community 48 - "Community 48"
Cohesion: 1.0
Nodes (0): 

### Community 49 - "Community 49"
Cohesion: 1.0
Nodes (0): 

### Community 50 - "Community 50"
Cohesion: 1.0
Nodes (0): 

### Community 51 - "Community 51"
Cohesion: 1.0
Nodes (0): 

### Community 52 - "Community 52"
Cohesion: 1.0
Nodes (0): 

### Community 53 - "Community 53"
Cohesion: 1.0
Nodes (0): 

### Community 54 - "Community 54"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **12 isolated node(s):** `# NOTE: Use `*` to move the label up in the annotation. Each `*` moves it up a b`, `Benchmark = part after the first newline (e.g. 'Qwen2.5-VL-7B\\nMathVista' -> 'M`, `Single radar chart. Each axis = one subtask; one curve per method.     Each benc`, `Reject source-contained or write-through pilot roots before writes.`, `Resolve a logical material id or exact material node id.          Logical materi` (+7 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 36`** (2 nodes): `is_dark()`, `plot_comparison.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (2 nodes): `is_dark()`, `plot_ablation.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (2 nodes): `function()`, `plot_hole_manifold.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (2 nodes): `function()`, `plot_manifold.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (2 nodes): `plot_heatmap()`, `plot_composition.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (2 nodes): `decode_ablation()`, `plot_bars.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 42`** (2 nodes): `plot_curves()`, `plot_posttraining.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (1 nodes): `plot_brute_force.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (1 nodes): `plot_correctness_by_category.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (1 nodes): `plot_rewriting.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (1 nodes): `plot_correctness_by_subcategory.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (1 nodes): `plot_selfcorrection_math.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (1 nodes): `plot_sweep.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (1 nodes): `plot_comparison.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (1 nodes): `raw_data.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (1 nodes): `plot_comparison_Ablation.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (1 nodes): `plot_comparison_GeneRegulatory.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (1 nodes): `plot_comparison_Trajectory.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 54`** (1 nodes): `runtime-graph-data.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `read_text()` connect `Community 3` to `Community 1`, `Community 2`, `Community 5`, `Community 6`, `Community 7`, `Community 8`, `Community 9`, `Community 10`, `Community 11`, `Community 12`, `Community 13`, `Community 15`, `Community 16`, `Community 17`, `Community 18`, `Community 19`, `Community 20`, `Community 21`, `Community 22`, `Community 23`, `Community 24`, `Community 25`, `Community 26`, `Community 27`, `Community 28`, `Community 29`, `Community 30`, `Community 31`?**
  _High betweenness centrality (0.336) - this node is a cross-community bridge._
- **Why does `issue()` connect `Community 0` to `Community 10`, `Community 2`, `Community 5`, `Community 6`?**
  _High betweenness centrality (0.279) - this node is a cross-community bridge._
- **Why does `load_document()` connect `Community 6` to `Community 1`, `Community 2`, `Community 3`, `Community 5`, `Community 7`, `Community 8`, `Community 10`, `Community 12`, `Community 13`, `Community 15`, `Community 16`, `Community 17`, `Community 18`, `Community 19`, `Community 20`, `Community 21`, `Community 22`, `Community 23`, `Community 24`, `Community 25`, `Community 26`, `Community 27`, `Community 28`, `Community 29`?**
  _High betweenness centrality (0.140) - this node is a cross-community bridge._
- **Are the 192 inferred relationships involving `issue()` (e.g. with `compile_backflow()` and `_payload()`) actually correct?**
  _`issue()` has 192 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `_require_mapping()` (e.g. with `as_mapping()` and `issue()`) actually correct?**
  _`_require_mapping()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 60 inferred relationships involving `read_text()` (e.g. with `load_json()` and `_load_json()`) actually correct?**
  _`read_text()` has 60 INFERRED edges - model-reasoned connections that need verification._
- **Are the 55 inferred relationships involving `is_non_empty_string()` (e.g. with `_validate_evidence_inventory()` and `_validate_claim_boundary_map()`) actually correct?**
  _`is_non_empty_string()` has 55 INFERRED edges - model-reasoned connections that need verification._