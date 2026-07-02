# S06 Object Granularity / 对象、机制变量与解释颗粒度

> Bilingual stage explainer for humans and controller agents. / 面向人类与主控 agent 的双语阶段说明。

## 1. Purpose / 目的

**EN.** S06 designs object representations, mechanism-variable cards, section load budgets, granularity progression, and explanation ladders.

**中文。** S06 设计对象表示、机制变量卡、章节负载预算、颗粒度递进和解释阶梯。

**Contract purpose / 契约原文目的。** Design complete object and mechanism-variable representation, granularity progression, section/load budgets, explanation ladders, and downstream handoffs without adding claims or drafting prose.

## 2. Position in the Paper Production Graph / 在论文生产图中的位置

```text
S05/S04/S02 → S06 → S07/S08/S10
```

**EN.** S06 prevents a paper from repeatedly explaining the same object at the wrong level. It decides what must be named, simplified, deferred, or expanded.

**中文。** S06 防止论文在错误层级反复解释同一对象。它决定哪些对象必须命名、简化、延后或展开。

## 3. When the Controller Should Trigger This Stage / 主 agent 什么时候触发本环节

**中文触发条件：**

- 论文涉及多个对象、机制、变量、系统组件或层级时
- 读者可能因对象粒度不一致而困惑时
- 正文/图表需要统一术语对象和解释顺序时

**English triggers:**

- The paper contains multiple objects, mechanisms, variables, components, or abstraction levels.
- Readers may be confused by inconsistent object granularity.
- Text and figures need aligned object vocabulary and explanation order.

## 4. Inputs and Preconditions / 输入与前置条件

**Declared consumes / 契约声明输入：**

- `reader spine`
- `reviewer question map`
- `template profile`
- `claim visibility`

**What this stage analyzes or designs / 本环节具体分析或设计：**

**中文：**

- object inventory
- mechanism-variable inventory
- P0/P1/P2 object cards
- claim-object/question-object/section-object maps
- cognitive load and explanation ladder

**English:**

- Object inventory.
- Mechanism-variable inventory.
- P0/P1/P2 object cards.
- Claim-object, question-object, and section-object maps.
- Cognitive load and explanation ladder.

If an input is missing, the controller should return to the nearest responsible upstream stage instead of letting the worker guess. / 如果输入缺失，主 agent 应回到最近责任上游环节，而不是让 worker 猜。

## 5. Task Packet or Controller Package / 任务包或主控包

- `S06` requires a strict worker task packet / `S06` 需要严格 worker 任务包: `examples/packets/phase10_s06_object_granularity_design_packet.v1.yaml`.

**Packet/material contract files / 任务包或控制包文件：**

- [`examples/packets/phase10_s06_object_granularity_design_packet.v1.yaml`](../../examples/packets/phase10_s06_object_granularity_design_packet.v1.yaml)

The packet is not a prompt template for free generation. It is a bounded contract that fixes allowed inputs, allowed paths, forbidden routes, output schema, validators, and the no-completion authority boundary. / 任务包不是自由生成提示词，而是限定输入、路径、禁止路线、输出 schema、validator 和无完成权威边界的契约。

## 6. Execution Sequence / 执行顺序

**中文执行顺序：**

- object inventory extraction
- mechanism and variable inventory
- object cards
- mechanism variable cards
- cross maps
- granularity and load design
- repetition/completeness check
- downstream handoff

**English execution sequence:**

- Object inventory extraction.
- Mechanism and variable inventory.
- Object cards.
- Mechanism-variable cards.
- Cross maps.
- Granularity and load design.
- Repetition/completeness check.
- Downstream handoff.

The controller may dispatch a producer and verifier lane when the contract requires worker evidence, but only the controller commits graph state. / 当契约要求 worker 证据时，主控可分派 producer 和 verifier，但只有主控能提交图状态。

## 7. Output Material / 输出物料

**Declared produces / 契约声明输出：**

- `object representation matrix`
- `section function budget`
- `load budget`
- `explanation ladder`

**Positive material fixtures / 正例物料样例：**

- [`examples/materials/phase10_s06_object_granularity.yaml`](../../examples/materials/phase10_s06_object_granularity.yaml)

**Payload modules / payload 模块：**

- `schema_version`
- `stage_id`
- `completion_boundary`
- `object_inventory`
- `mechanism_variable_inventory`
- `object_cards`
- `mechanism_variable_cards`
- `cross_maps`
- `granularity_progression_map`
- `section_function_budget`
- `cognitive_load_budget`
- `explanation_ladder`
- `repetition_risk_register`
- `coverage_ledger`
- `unresolved_object_report`
- `handoff_to_s07`
- `handoff_to_s08`
- `handoff_to_s10`
- `coherence_and_boundary_audit`
- `candidate_return`

These fields are meant to be checked, consumed, and backflowed as structured graph materials rather than copied as prose. / 这些字段应作为结构化图物料被检查、消费和回流，而不是被复制成散文。

## 8. Validators and Failure Modes / Validator 与失败模式

**Validators / 验证器：**

- `S06_object_inventory_coverage`
- `S06_mechanism_variable_coverage`
- `S06_object_cards_for_P0_P1_P2`
- `S06_mechanism_variable_cards`
- `S06_claim_object_mapping`
- `S06_reader_question_object_mapping`
- `S06_object_section_mapping`
- `S06_granularity_progression`
- `S06_section_function_budget`
- `S06_cognitive_load_budget`
- `S06_explanation_ladder`
- `S06_no_flat_repetition`
- `S06_coverage_ledger`
- `S06_unresolved_object_report`
- `S06_downstream_handoff`
- `S06_no_new_claims_or_final_prose`
- `S06_no_completion_overclaim`

**Negative fixtures cover / 负例覆盖：**

- `examples/materials/invalid-s06-object-granularity-completion-overclaim.yaml`
- `examples/materials/invalid-s06-object-granularity-final-prose.yaml`
- `examples/materials/invalid-s06-object-granularity-hidden-unresolved.yaml`
- `examples/materials/invalid-s06-object-granularity-missing-coverage-ledger.yaml`
- `examples/materials/invalid-s06-object-granularity-missing-downstream-handoff.yaml`
- `examples/materials/invalid-s06-object-granularity-missing-explanation-ladder.yaml`
- `examples/materials/invalid-s06-object-granularity-missing-granularity-map.yaml`
- `examples/materials/invalid-s06-object-granularity-missing-load-budget.yaml`
- `examples/materials/invalid-s06-object-granularity-missing-object-cards.yaml`
- `examples/materials/invalid-s06-object-granularity-missing-object-inventory.yaml`
- `examples/materials/invalid-s06-object-granularity-missing-reader-question-map.yaml`
- `examples/materials/invalid-s06-object-granularity-missing-section-budget.yaml`
- `examples/materials/invalid-s06-object-granularity-missing-variable-cards.yaml`
- `examples/materials/invalid-s06-object-granularity-missing-variable-inventory.yaml`
- `examples/materials/invalid-s06-object-granularity-new-claim.yaml`

Run the focused verifier / 运行聚焦验证器：

```bash
python3 scripts/verify_s06_object_granularity.py
```

## 9. Downstream Handoffs / 下游交接

The output is only useful when downstream stages can consume it with traceable references. / 输出只有在下游能以可追踪引用消费时才有意义。

- It should name what is ready for downstream use. / 应说明哪些内容可供下游使用。
- It should name what is unresolved, rejected, owner-gated, stale, or missing. / 应说明哪些内容 unresolved、rejected、owner-gated、stale 或 missing。
- It should preserve the nearest-responsible-stage route for later backflow. / 应保留后续回流所需的最近责任阶段路线。

## 10. Authority and Misuse Boundaries / 权威边界与误用防线

**中文边界：**

- 不能新增 claim
- 不能写最终正文
- 不能遗漏对象后假装已覆盖
- 不能把所有对象压成同一粒度

**English boundaries:**

- It must not add claims.
- It must not write final prose.
- It must not silently omit objects.
- It must not flatten all objects to one granularity.

Specialist agents and scripts may return candidates or evidence; they never own completion authority. / 专家 agent 和脚本只能返回候选或证据，不能拥有完成权威。

## 11. Implementation Map / 实现索引

- Stage id(s) / 阶段 ID：`S06`
- Stage contract(s) / 阶段契约：
- [`examples/stage-contracts/S06.stage-contract.json`](../../examples/stage-contracts/S06.stage-contract.json)
- Stage registry / 阶段注册表：[`runtime/stage_registry.json`](../../runtime/stage_registry.json)
- Phase validators / Phase 验证配置：[`runtime/phase10_content_validators.json`](../../runtime/phase10_content_validators.json)
- Material schema / 物料 schema：[`schemas/ppg-material-payloads.schema.json`](../../schemas/ppg-material-payloads.schema.json)
- Material validator / 物料验证器：[`scripts/validate_material.py`](../../scripts/validate_material.py)
- Focused verifier / 聚焦验证器：[`scripts/verify_s06_object_granularity.py`](../../scripts/verify_s06_object_granularity.py)

## 12. Plain-Language Summary / 通俗总结

**中文。** S06 防止论文在错误层级反复解释同一对象。它决定哪些对象必须命名、简化、延后或展开。 它的作用是把本环节的判断变成可检查、可回流、可被下游安全消费的结构化物料，而不是让后续 agent 依赖印象或自由发挥。

**EN.** S06 prevents a paper from repeatedly explaining the same object at the wrong level. It decides what must be named, simplified, deferred, or expanded. Its role is to turn this stage's judgments into structured, checkable, backflow-ready materials that downstream agents can consume safely instead of relying on impressions or free-form improvisation.
