# S08 Visual and Formal Plan / 图表与形式对象计划

> Bilingual stage explainer for humans and controller agents. / 面向人类与主控 agent 的双语阶段说明。

## 1. Purpose / 目的

**EN.** S08 plans visual/formal objects, figure/table/formal contracts, panel evidence maps, visual budgets, backend routes, and caption boundaries.

**中文。** S08 规划图表/形式对象、figure/table/formal contracts、panel evidence map、视觉预算、后端路线和 caption 边界。

**Contract purpose / 契约原文目的。** Compile reader questions, section/object budgets, claim/evidence boundaries, and source-data routes into visual/formal object contracts.

## 2. Position in the Paper Production Graph / 在论文生产图中的位置

```text
S01/S04/S05/S06/S07 → S08 → S09/S11/S12/S16
```

**EN.** S08 decides what should become a figure, table, formula, algorithm, or supplement before anyone draws it.

**中文。** S08 在真正画图前决定哪些内容应该成为图、表、公式、算法或补充材料。

## 3. When the Controller Should Trigger This Stage / 主 agent 什么时候触发本环节

**中文触发条件：**

- 论文需要图、表、公式、算法、schematic 或 supplement split 时
- 需要明确每个 panel 支持哪些 claim 时
- 需要避免 schematic 被误当作 evidence 时

**English triggers:**

- The paper needs figures, tables, formulas, algorithms, schematics, or supplement split.
- Each panel must be bound to supported claims.
- Schematics must not be mistaken for evidence.

## 4. Inputs and Preconditions / 输入与前置条件

**Declared consumes / 契约声明输入：**

- `reader spine`
- `section function budget`
- `claim evidence materials`

**What this stage analyzes or designs / 本环节具体分析或设计：**

**中文：**

- visual needs and budget
- figure/table/formal object contracts
- panel evidence map
- visual-claim binding
- backend route and caption brief
- accessibility/style constraints

**English:**

- Visual needs and budget.
- Figure/table/formal-object contracts.
- Panel evidence map.
- Visual-claim binding.
- Backend route and caption brief.
- Accessibility/style constraints.

If an input is missing, the controller should return to the nearest responsible upstream stage instead of letting the worker guess. / 如果输入缺失，主 agent 应回到最近责任上游环节，而不是让 worker 猜。

## 5. Task Packet or Controller Package / 任务包或主控包

- `S08` requires a strict worker task packet / `S08` 需要严格 worker 任务包: `examples/packets/phase10_s08_visual_formal_planning_packet.v1.yaml`.

**Packet/material contract files / 任务包或控制包文件：**

- [`examples/packets/phase10_s08_visual_formal_planning_packet.v1.yaml`](../../examples/packets/phase10_s08_visual_formal_planning_packet.v1.yaml)

The packet is not a prompt template for free generation. It is a bounded contract that fixes allowed inputs, allowed paths, forbidden routes, output schema, validators, and the no-completion authority boundary. / 任务包不是自由生成提示词，而是限定输入、路径、禁止路线、输出 schema、validator 和无完成权威边界的契约。

## 6. Execution Sequence / 执行顺序

**中文执行顺序：**

- input coverage and authority audit
- claim/evidence normalization
- visual need inventory
- candidate visual queue
- visual budget and main story path
- figure/table/formal object contracts
- panel/claim evidence maps
- backend route and caption brief
- accessibility/downstream handoff

**English execution sequence:**

- Input coverage and authority audit.
- Claim/evidence normalization.
- Visual-need inventory.
- Candidate visual queue.
- Visual budget and main-story path.
- Figure/table/formal-object contracts.
- Panel/claim evidence maps.
- Backend route and caption brief.
- Accessibility/downstream handoff.

The controller may dispatch a producer and verifier lane when the contract requires worker evidence, but only the controller commits graph state. / 当契约要求 worker 证据时，主控可分派 producer 和 verifier，但只有主控能提交图状态。

## 7. Output Material / 输出物料

**Declared produces / 契约声明输出：**

- `visual budget`
- `figure contract`
- `panel evidence map`
- `backend route`

**Positive material fixtures / 正例物料样例：**

- [`examples/materials/phase10_s08_visual_formal_plan.yaml`](../../examples/materials/phase10_s08_visual_formal_plan.yaml)

**Payload modules / payload 模块：**

- `schema_version`
- `stage_id`
- `completion_boundary`
- `authority_boundary_audit`
- `input_coverage_ledger`
- `source_data_inventory_projection`
- `normalized_claim_evidence_table`
- `visual_need_inventory`
- `formal_visual_need_map`
- `candidate_visual_object_queue`
- `visual_budget`
- `main_story_visual_path`
- `figure_contracts`
- `table_contracts`
- `formal_object_contracts`
- `panel_evidence_map`
- `visual_claim_evidence_map`
- `backend_route_map`
- `main_supplement_split_plan`
- `caption_legend_brief`
- `accessibility_and_style_constraints`
- `coverage_ledger`
- `unresolved_visual_object_report`
- `downstream_handoff`
- `visual_safety_audit`
- `candidate_return`

These fields are meant to be checked, consumed, and backflowed as structured graph materials rather than copied as prose. / 这些字段应作为结构化图物料被检查、消费和回流，而不是被复制成散文。

## 8. Validators and Failure Modes / Validator 与失败模式

**Validators / 验证器：**

- `S08_input_coverage`
- `S08_visual_need_inventory`
- `S08_candidate_visual_object_queue`
- `S08_visual_budget`
- `S08_main_story_visual_path`
- `S08_figure_contract_schema`
- `S08_table_contract_schema`
- `S08_formal_object_contract_schema`
- `S08_panel_evidence_map`
- `S08_visual_claim_evidence_binding`
- `S08_explanatory_vs_evidential_boundary`
- `S08_main_supplement_split`
- `S08_backend_route_map`
- `S08_caption_boundary`
- `S08_accessibility_constraints`
- `S08_coverage_ledger`
- `S08_unresolved_visual_object_report`
- `S08_downstream_handoff`
- `S08_no_new_claims_or_completion_overclaim`

**Negative fixtures cover / 负例覆盖：**

- `examples/materials/invalid-s08-visual-formal-plan-claim-strengthening.yaml`
- `examples/materials/invalid-s08-visual-formal-plan-completion-overclaim.yaml`
- `examples/materials/invalid-s08-visual-formal-plan-final-artifact.yaml`
- `examples/materials/invalid-s08-visual-formal-plan-hidden-unresolved.yaml`
- `examples/materials/invalid-s08-visual-formal-plan-missing-accessibility.yaml`
- `examples/materials/invalid-s08-visual-formal-plan-missing-backend-route.yaml`
- `examples/materials/invalid-s08-visual-formal-plan-missing-candidate-queue.yaml`
- `examples/materials/invalid-s08-visual-formal-plan-missing-caption-boundary.yaml`
- `examples/materials/invalid-s08-visual-formal-plan-missing-downstream-handoff.yaml`
- `examples/materials/invalid-s08-visual-formal-plan-missing-figure-contract.yaml`
- `examples/materials/invalid-s08-visual-formal-plan-missing-formal-object-contract.yaml`
- `examples/materials/invalid-s08-visual-formal-plan-missing-input-coverage.yaml`
- `examples/materials/invalid-s08-visual-formal-plan-missing-panel-evidence.yaml`
- `examples/materials/invalid-s08-visual-formal-plan-missing-table-contract.yaml`
- `examples/materials/invalid-s08-visual-formal-plan-missing-visual-budget.yaml`
- `examples/materials/invalid-s08-visual-formal-plan-missing-visual-claim-binding.yaml`
- `examples/materials/invalid-s08-visual-formal-plan-missing-visual-needs.yaml`
- `examples/materials/invalid-s08-visual-formal-plan-new-claim.yaml`
- `examples/materials/invalid-s08-visual-formal-plan-schematic-as-evidence.yaml`

Run the focused verifier / 运行聚焦验证器：

```bash
python3 scripts/verify_s08_visual_formal_plan.py
```

## 9. Downstream Handoffs / 下游交接

The output is only useful when downstream stages can consume it with traceable references. / 输出只有在下游能以可追踪引用消费时才有意义。

- It should name what is ready for downstream use. / 应说明哪些内容可供下游使用。
- It should name what is unresolved, rejected, owner-gated, stale, or missing. / 应说明哪些内容 unresolved、rejected、owner-gated、stale 或 missing。
- It should preserve the nearest-responsible-stage route for later backflow. / 应保留后续回流所需的最近责任阶段路线。

## 10. Authority and Misuse Boundaries / 权威边界与误用防线

**中文边界：**

- 不能生成最终图件
- 不能新增或加强 claim
- 不能把 explanatory schematic 当成 evidential result
- 不能越过后端数据路线

**English boundaries:**

- It must not generate final visual artifacts.
- It must not add or strengthen claims.
- It must not treat explanatory schematics as evidential results.
- It must not bypass backend data routes.

Specialist agents and scripts may return candidates or evidence; they never own completion authority. / 专家 agent 和脚本只能返回候选或证据，不能拥有完成权威。

## 11. Implementation Map / 实现索引

- Stage id(s) / 阶段 ID：`S08`
- Stage contract(s) / 阶段契约：
- [`examples/stage-contracts/S08.stage-contract.json`](../../examples/stage-contracts/S08.stage-contract.json)
- Stage registry / 阶段注册表：[`runtime/stage_registry.json`](../../runtime/stage_registry.json)
- Phase validators / Phase 验证配置：[`runtime/phase10_content_validators.json`](../../runtime/phase10_content_validators.json)
- Material schema / 物料 schema：[`schemas/ppg-material-payloads.schema.json`](../../schemas/ppg-material-payloads.schema.json)
- Material validator / 物料验证器：[`scripts/validate_material.py`](../../scripts/validate_material.py)
- Focused verifier / 聚焦验证器：[`scripts/verify_s08_visual_formal_plan.py`](../../scripts/verify_s08_visual_formal_plan.py)

## 12. Plain-Language Summary / 通俗总结

**中文。** S08 在真正画图前决定哪些内容应该成为图、表、公式、算法或补充材料。 它的作用是把本环节的判断变成可检查、可回流、可被下游安全消费的结构化物料，而不是让后续 agent 依赖印象或自由发挥。

**EN.** S08 decides what should become a figure, table, formula, algorithm, or supplement before anyone draws it. Its role is to turn this stage's judgments into structured, checkable, backflow-ready materials that downstream agents can consume safely instead of relying on impressions or free-form improvisation.
