# S00 Owner Semantic Contract / 作者意图语义契约

> Bilingual stage explainer for humans and controller agents. / 面向人类与主控 agent 的双语阶段说明。

## 1. Purpose / 目的

**EN.** S00 turns the owner's human need, venue route, contribution boundary, and forbidden routes into the first authoritative semantic contract.

**中文。** S00 把作者的真实需求、目标路线、贡献边界和禁止路线转成第一份具有权威性的语义契约。

**Contract purpose / 契约原文目的。** Convert human need into bounded paper commitments and owner decisions.

## 2. Position in the Paper Production Graph / 在论文生产图中的位置

```text
S00 → S01/S03/S04/S16 owner-gated decisions
```

**EN.** S00 is the “do not misunderstand the owner” gate. It does not ask a worker to write; it records what the paper is allowed to become and what it must not silently turn into.

**中文。** S00 是“不要误解作者”的关口。它不让 worker 写作，而是记录这篇论文允许变成什么、不能悄悄变成什么。

## 3. When the Controller Should Trigger This Stage / 主 agent 什么时候触发本环节

**中文触发条件：**

- 新论文、换题、换期刊或 owner intent 不清楚时
- 贡献边界、投稿边界、外部行动边界可能被误读时
- 后续 stage 需要知道哪些语义变化必须回问 owner 时

**English triggers:**

- A new paper, route change, venue change, or unclear owner intent appears.
- Contribution scope, submission boundary, or external-action boundary may be misread.
- Downstream stages need to know which semantic shifts require owner confirmation.

## 4. Inputs and Preconditions / 输入与前置条件

**Declared consumes / 契约声明输入：**

- `human need`
- `paper profile`
- `evidence summary`

**What this stage analyzes or designs / 本环节具体分析或设计：**

**中文：**

- 作者真正要解决的问题
- 目标论文路线和不可走路线
- 贡献范围偏好和证据政策
- 哪些改动属于 owner-level semantic shift

**English:**

- The owner's actual paper need.
- The intended route and forbidden routes.
- Contribution-scope preferences and source policy.
- Which changes are owner-level semantic shifts.

If an input is missing, the controller should return to the nearest responsible upstream stage instead of letting the worker guess. / 如果输入缺失，主 agent 应回到最近责任上游环节，而不是让 worker 猜。

## 5. Task Packet or Controller Package / 任务包或主控包

- `S00` does not require a normal worker task packet / `S00` 不需要普通 worker 任务包 (`not_required`).

**Packet/material contract files / 任务包或控制包文件：**

- _Not applicable / 不适用_

The packet is not a prompt template for free generation. It is a bounded contract that fixes allowed inputs, allowed paths, forbidden routes, output schema, validators, and the no-completion authority boundary. / 任务包不是自由生成提示词，而是限定输入、路径、禁止路线、输出 schema、validator 和无完成权威边界的契约。

## 6. Execution Sequence / 执行顺序

**中文执行顺序：**

- 收集原始请求和上下文
- 冻结 paper route / venue / contribution boundary
- 记录 source policy 与外部行动边界
- 列出 blocked routes 与 unresolved owner questions
- 向下游传播 owner gate

**English execution sequence:**

- Collect the original request and context.
- Freeze paper route, venue, and contribution boundary.
- Record source policy and external-action boundary.
- List blocked routes and unresolved owner questions.
- Propagate owner gates downstream.

The controller may dispatch a producer and verifier lane when the contract requires worker evidence, but only the controller commits graph state. / 当契约要求 worker 证据时，主控可分派 producer 和 verifier，但只有主控能提交图状态。

## 7. Output Material / 输出物料

**Declared produces / 契约声明输出：**

- `paper-profile`
- `motivation`
- `decisions`
- `blocked routes`

**Positive material fixtures / 正例物料样例：**

- [`examples/materials/s00_owner_intake.v1.yaml`](../../examples/materials/s00_owner_intake.v1.yaml)
- [`examples/materials/s00_owner_semantic_contract.v1.yaml`](../../examples/materials/s00_owner_semantic_contract.v1.yaml)

**Payload modules / payload 模块：**

- `s00_owner_intake.v1.yaml:schema_version`
- `s00_owner_intake.v1.yaml:stage_id`
- `s00_owner_intake.v1.yaml:activation_reason`
- `s00_owner_intake.v1.yaml:human_need`
- `s00_owner_intake.v1.yaml:paper_route`
- `s00_owner_intake.v1.yaml:owner_constraints`
- `s00_owner_intake.v1.yaml:claim_scope_preferences`
- `s00_owner_intake.v1.yaml:evidence_summary`
- `s00_owner_intake.v1.yaml:decision_status`
- `s00_owner_semantic_contract.v1.yaml:schema_version`
- `s00_owner_semantic_contract.v1.yaml:stage_id`
- `s00_owner_semantic_contract.v1.yaml:completion_boundary`
- `s00_owner_semantic_contract.v1.yaml:paper_profile`
- `s00_owner_semantic_contract.v1.yaml:motivation_contract`
- `s00_owner_semantic_contract.v1.yaml:owner_decisions`
- `s00_owner_semantic_contract.v1.yaml:claim_scope_boundary`
- `s00_owner_semantic_contract.v1.yaml:source_policy`
- `s00_owner_semantic_contract.v1.yaml:external_action_boundary`
- `s00_owner_semantic_contract.v1.yaml:blocked_routes`
- `s00_owner_semantic_contract.v1.yaml:downstream_effects_if_changed`
- `s00_owner_semantic_contract.v1.yaml:unresolved_owner_questions`

These fields are meant to be checked, consumed, and backflowed as structured graph materials rather than copied as prose. / 这些字段应作为结构化图物料被检查、消费和回流，而不是被复制成散文。

## 8. Validators and Failure Modes / Validator 与失败模式

**Validators / 验证器：**

- `owner confirmation`
- `blocked route check`
- `owner decision trace`
- `claim scope boundary`
- `source/privacy policy boundary`
- `external action boundary`
- `no worker semantic change`
- `downstream stale/backflow effects`
- `no completion or submission overclaim`

**Negative fixtures cover / 负例覆盖：**

- `examples/materials/invalid-s00-owner-contract-missing-blocked-routes.yaml`
- `examples/materials/invalid-s00-owner-contract-submission-allowed.yaml`
- `examples/materials/invalid-s00-owner-intake-missing-original-request.yaml`

Run the focused verifier / 运行聚焦验证器：

```bash
python3 scripts/verify_s00_owner_semantic_contract.py
```

## 9. Downstream Handoffs / 下游交接

The output is only useful when downstream stages can consume it with traceable references. / 输出只有在下游能以可追踪引用消费时才有意义。

- It should name what is ready for downstream use. / 应说明哪些内容可供下游使用。
- It should name what is unresolved, rejected, owner-gated, stale, or missing. / 应说明哪些内容 unresolved、rejected、owner-gated、stale 或 missing。
- It should preserve the nearest-responsible-stage route for later backflow. / 应保留后续回流所需的最近责任阶段路线。

## 10. Authority and Misuse Boundaries / 权威边界与误用防线

**中文边界：**

- 不能代表 owner 做投稿或出版决定
- 不能把 worker 的建议当成 owner intent
- 不能跳过 blocked route / owner question

**English boundaries:**

- It must not make submission or publication decisions for the owner.
- It must not treat worker suggestions as owner intent.
- It must not bypass blocked routes or owner questions.

Specialist agents and scripts may return candidates or evidence; they never own completion authority. / 专家 agent 和脚本只能返回候选或证据，不能拥有完成权威。

## 11. Implementation Map / 实现索引

- Stage id(s) / 阶段 ID：`S00`
- Stage contract(s) / 阶段契约：
- [`examples/stage-contracts/S00.stage-contract.json`](../../examples/stage-contracts/S00.stage-contract.json)
- Stage registry / 阶段注册表：[`runtime/stage_registry.json`](../../runtime/stage_registry.json)
- Phase validators / Phase 验证配置：[`runtime/phase10_content_validators.json`](../../runtime/phase10_content_validators.json)
- Material schema / 物料 schema：[`schemas/ppg-material-payloads.schema.json`](../../schemas/ppg-material-payloads.schema.json)
- Material validator / 物料验证器：[`scripts/validate_material.py`](../../scripts/validate_material.py)
- Focused verifier / 聚焦验证器：[`scripts/verify_s00_owner_semantic_contract.py`](../../scripts/verify_s00_owner_semantic_contract.py)

## 12. Plain-Language Summary / 通俗总结

**中文。** S00 是“不要误解作者”的关口。它不让 worker 写作，而是记录这篇论文允许变成什么、不能悄悄变成什么。 它的作用是把本环节的判断变成可检查、可回流、可被下游安全消费的结构化物料，而不是让后续 agent 依赖印象或自由发挥。

**EN.** S00 is the “do not misunderstand the owner” gate. It does not ask a worker to write; it records what the paper is allowed to become and what it must not silently turn into. Its role is to turn this stage's judgments into structured, checkable, backflow-ready materials that downstream agents can consume safely instead of relying on impressions or free-form improvisation.

## Stage-quality upgrade contract / 阶段质量升级合同

**EN.** This stage must not be accepted only because its artifact exists. It must preserve enough upstream authority and design force for downstream stages to execute without guessing. Producer packets may include all relevant source, owner, profile, evidence, and design materials; audit/verifier packets inherit the same inputs and add stricter sufficiency checks.

**中文。** 本阶段不能因为产物存在就算完成。它必须为下游保留足够的权威、证据和设计约束。生产包可以给足所有相关输入；审核包必须继承生产包全部输入，并追加更严格的充分性检查。

Stage-quality focus / 阶段质量焦点：`owner quality and authority gate`.

Required extraction examples / 必须抽取示例：owner_quality_goal, active_venue_or_route_profile, claim_scope_boundary, owner_gate_register, downstream_stale_policy.

Downstream design force / 下游设计力：all downstream stages inherit quality ambition and owner boundaries; S02/S05/S09/S13/rendered gate can consume owner targets.

Blocking or major failures must name the nearest responsible stage and affected downstream nodes instead of defaulting to whole-paper rewrite. MINOR/WATCH findings do not force a full downstream rerun by default.

