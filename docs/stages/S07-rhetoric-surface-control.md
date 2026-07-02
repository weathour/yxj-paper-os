# S07 Rhetoric and Surface Control / 术语、修辞与表层表达控制

> Bilingual stage explainer for humans and controller agents. / 面向人类与主控 agent 的双语阶段说明。

## 1. Purpose / 目的

**EN.** S07 compiles claim-safe terminology, paragraph jobs, rhetorical moves, flexible language controls, and forbidden-expression guards.

**中文。** S07 编译安全承载 claim 的术语、段落任务、修辞动作、灵活语言控制和禁用表达防线。

**Contract purpose / 契约原文目的。** Compile claim-safe rhetoric, terminology, paragraph jobs, flexible surface controls, forbidden expressions, coverage ledgers, and downstream handoffs without final prose or claim strengthening.

## 2. Position in the Paper Production Graph / 在论文生产图中的位置

```text
S02/S04/S05/S06 → S07 → S09/S10/S12
```

**EN.** S07 controls how the paper may sound without making it mechanically templated. It turns S02 language profiles into flexible constraints, not rigid sentence recipes.

**中文。** S07 控制论文“怎么说”，但不把语言变成机械模板。它把 S02 的语言画像转成灵活约束，而不是句子配方。

## 3. When the Controller Should Trigger This Stage / 主 agent 什么时候触发本环节

**中文触发条件：**

- 术语、语气、claim strength 或 internal ID 泄漏风险需要控制时
- 需要为 S10 提供段落功能和 rhetorical move 时
- 需要把语言统计转成灵活规则而非模板时

**English triggers:**

- Terminology, tone, claim strength, or internal-ID leakage must be controlled.
- S10 needs paragraph jobs and rhetorical moves.
- Language statistics must become flexible controls rather than templates.

## 4. Inputs and Preconditions / 输入与前置条件

**Declared consumes / 契约声明输入：**

- `object representation`
- `claim visibility`
- `evidence wording`

**What this stage analyzes or designs / 本环节具体分析或设计：**

**中文：**

- claim surface rules
- terminology register
- internal-id ban list
- paragraph job map
- rhetorical move matrix
- forbidden expression list

**English:**

- Claim-surface rules.
- Terminology register.
- Internal-ID ban list.
- Paragraph-job map.
- Rhetorical-move matrix.
- Forbidden-expression list.

If an input is missing, the controller should return to the nearest responsible upstream stage instead of letting the worker guess. / 如果输入缺失，主 agent 应回到最近责任上游环节，而不是让 worker 猜。

## 5. Task Packet or Controller Package / 任务包或主控包

- `S07` requires a strict worker task packet / `S07` 需要严格 worker 任务包: `examples/packets/phase10_s07_rhetoric_surface_control_packet.v1.yaml`.

**Packet/material contract files / 任务包或控制包文件：**

- [`examples/packets/phase10_s07_rhetoric_surface_control_packet.v1.yaml`](../../examples/packets/phase10_s07_rhetoric_surface_control_packet.v1.yaml)

The packet is not a prompt template for free generation. It is a bounded contract that fixes allowed inputs, allowed paths, forbidden routes, output schema, validators, and the no-completion authority boundary. / 任务包不是自由生成提示词，而是限定输入、路径、禁止路线、输出 schema、validator 和无完成权威边界的契约。

## 6. Execution Sequence / 执行顺序

**中文执行顺序：**

- input boundary and coverage check
- claim surface pass
- terminology pass
- internal-id leakage pass
- paragraph job pass
- rhetorical move pass
- language flexibility/misuse guard pass
- forbidden expression audit
- coverage/downstream handoff pass

**English execution sequence:**

- Input boundary and coverage check.
- Claim-surface pass.
- Terminology pass.
- Internal-ID leakage pass.
- Paragraph-job pass.
- Rhetorical-move pass.
- Language flexibility/misuse-guard pass.
- Forbidden-expression audit.
- Coverage/downstream handoff pass.

The controller may dispatch a producer and verifier lane when the contract requires worker evidence, but only the controller commits graph state. / 当契约要求 worker 证据时，主控可分派 producer 和 verifier，但只有主控能提交图状态。

## 7. Output Material / 输出物料

**Declared produces / 契约声明输出：**

- `construction matrix`
- `rhetorical matrix`
- `terminology register`
- `surface rules`

**Positive material fixtures / 正例物料样例：**

- [`examples/materials/phase10_s07_surface_control.yaml`](../../examples/materials/phase10_s07_surface_control.yaml)

**Payload modules / payload 模块：**

- `schema_version`
- `stage_id`
- `completion_boundary`
- `input_coverage_ledger`
- `claim_surface_rule_map`
- `terminology_surface_register`
- `internal_id_ban_list`
- `paragraph_job_map`
- `rhetorical_move_matrix`
- `flexible_language_control`
- `surface_rules`
- `forbidden_expression_list`
- `coverage_ledger`
- `unresolved_surface_control_report`
- `downstream_handoff`
- `surface_safety_audit`
- `candidate_return`

These fields are meant to be checked, consumed, and backflowed as structured graph materials rather than copied as prose. / 这些字段应作为结构化图物料被检查、消费和回流，而不是被复制成散文。

## 8. Validators and Failure Modes / Validator 与失败模式

**Validators / 验证器：**

- `S07_input_coverage`
- `S07_claim_surface_rule_map`
- `S07_terminology_surface_register`
- `S07_internal_id_ban_list`
- `S07_paragraph_job_map`
- `S07_rhetorical_move_matrix`
- `S07_language_flexibility_guard`
- `S07_surface_rules`
- `S07_forbidden_expression_list`
- `S07_coverage_ledger`
- `S07_unresolved_surface_control_report`
- `S07_downstream_handoff`
- `S07_no_new_claims_or_claim_strengthening`
- `S07_no_final_prose_or_completion_overclaim`

**Negative fixtures cover / 负例覆盖：**

- `examples/materials/invalid-s07-surface-control-claim-strengthening.yaml`
- `examples/materials/invalid-s07-surface-control-completion-overclaim.yaml`
- `examples/materials/invalid-s07-surface-control-final-prose.yaml`
- `examples/materials/invalid-s07-surface-control-missing-claim-surface-rules.yaml`
- `examples/materials/invalid-s07-surface-control-missing-coverage-ledger.yaml`
- `examples/materials/invalid-s07-surface-control-missing-downstream-handoff.yaml`
- `examples/materials/invalid-s07-surface-control-missing-flexible-language.yaml`
- `examples/materials/invalid-s07-surface-control-missing-forbidden-expressions.yaml`
- `examples/materials/invalid-s07-surface-control-missing-input-coverage.yaml`
- `examples/materials/invalid-s07-surface-control-missing-internal-id-ban.yaml`
- `examples/materials/invalid-s07-surface-control-missing-paragraph-jobs.yaml`
- `examples/materials/invalid-s07-surface-control-missing-rhetorical-moves.yaml`
- `examples/materials/invalid-s07-surface-control-missing-terminology.yaml`
- `examples/materials/invalid-s07-surface-control-new-claim.yaml`
- `examples/materials/invalid-s07-surface-control-rigid-language-rule.yaml`
- `examples/materials/invalid-s07-surface-control-rigid-template.yaml`

Run the focused verifier / 运行聚焦验证器：

```bash
python3 scripts/verify_s07_rhetoric_surface_control.py
```

## 9. Downstream Handoffs / 下游交接

The output is only useful when downstream stages can consume it with traceable references. / 输出只有在下游能以可追踪引用消费时才有意义。

- It should name what is ready for downstream use. / 应说明哪些内容可供下游使用。
- It should name what is unresolved, rejected, owner-gated, stale, or missing. / 应说明哪些内容 unresolved、rejected、owner-gated、stale 或 missing。
- It should preserve the nearest-responsible-stage route for later backflow. / 应保留后续回流所需的最近责任阶段路线。

## 10. Authority and Misuse Boundaries / 权威边界与误用防线

**中文边界：**

- 不能加强 claim
- 不能输出最终正文
- 不能把语言分布变成统一词数/句式硬规则
- 不能泄漏内部 ID

**English boundaries:**

- It must not strengthen claims.
- It must not output final prose.
- It must not turn language distributions into fixed word-count or syntax rules.
- It must not leak internal IDs.

Specialist agents and scripts may return candidates or evidence; they never own completion authority. / 专家 agent 和脚本只能返回候选或证据，不能拥有完成权威。

## 11. Implementation Map / 实现索引

- Stage id(s) / 阶段 ID：`S07`
- Stage contract(s) / 阶段契约：
- [`examples/stage-contracts/S07.stage-contract.json`](../../examples/stage-contracts/S07.stage-contract.json)
- Stage registry / 阶段注册表：[`runtime/stage_registry.json`](../../runtime/stage_registry.json)
- Phase validators / Phase 验证配置：[`runtime/phase10_content_validators.json`](../../runtime/phase10_content_validators.json)
- Material schema / 物料 schema：[`schemas/ppg-material-payloads.schema.json`](../../schemas/ppg-material-payloads.schema.json)
- Material validator / 物料验证器：[`scripts/validate_material.py`](../../scripts/validate_material.py)
- Focused verifier / 聚焦验证器：[`scripts/verify_s07_rhetoric_surface_control.py`](../../scripts/verify_s07_rhetoric_surface_control.py)

## 12. Plain-Language Summary / 通俗总结

**中文。** S07 控制论文“怎么说”，但不把语言变成机械模板。它把 S02 的语言画像转成灵活约束，而不是句子配方。 它的作用是把本环节的判断变成可检查、可回流、可被下游安全消费的结构化物料，而不是让后续 agent 依赖印象或自由发挥。

**EN.** S07 controls how the paper may sound without making it mechanically templated. It turns S02 language profiles into flexible constraints, not rigid sentence recipes. Its role is to turn this stage's judgments into structured, checkable, backflow-ready materials that downstream agents can consume safely instead of relying on impressions or free-form improvisation.
