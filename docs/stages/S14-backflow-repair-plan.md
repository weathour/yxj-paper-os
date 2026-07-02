# S14 Backflow Repair Plan / 回流归因与修复计划

> Bilingual stage explainer for humans and controller agents. / 面向人类与主控 agent 的双语阶段说明。

## 1. Purpose / 目的

**EN.** S14 converts review/integration findings into nearest-responsible-stage backflow plans, repair scopes, task packets, priorities, and validation plans.

**中文。** S14 把审查/集成发现转换为最近责任阶段回流计划、修复范围、任务包、优先级和验证计划。

**Contract purpose / 契约原文目的。** Normalize accepted review/loss findings into nearest-responsible, owner-gated, bounded repair plans without executing repair.

## 2. Position in the Paper Production Graph / 在论文生产图中的位置

```text
S12/S13/human feedback → S14 → S15 or upstream stages
```

**EN.** S14 decides where to repair, not how to repair everything. It prevents global rewrites by routing each finding to the nearest responsible material.

**中文。** S14 决定“修哪里”，不是全篇乱修。它把每个 finding 路由到最近责任物料，防止全局重写。

## 3. When the Controller Should Trigger This Stage / 主 agent 什么时候触发本环节

**中文触发条件：**

- S12/S13 发现需要修复计划时
- 人类反馈需要归因到 stage/material 时
- 需要生成 bounded repair task 而不是立即执行时

**English triggers:**

- S12/S13 findings require a repair plan.
- Human feedback must be attributed to stage/material.
- Bounded repair tasks are needed before execution.

## 4. Inputs and Preconditions / 输入与前置条件

**Declared consumes / 契约声明输入：**

- `accepted S13/S16/validator findings`
- `validator reports`
- `affected material graph slice`
- `owner gate policy`

**What this stage analyzes or designs / 本环节具体分析或设计：**

**中文：**

- finding intake ledger
- nearest responsible stage map
- affected material graph slice
- repair scope plan
- repair task packets
- owner gate and validation plan

**English:**

- Finding intake ledger.
- Nearest-responsible-stage map.
- Affected material graph slice.
- Repair-scope plan.
- Repair task packets.
- Owner gate and validation plan.

If an input is missing, the controller should return to the nearest responsible upstream stage instead of letting the worker guess. / 如果输入缺失，主 agent 应回到最近责任上游环节，而不是让 worker 猜。

## 5. Task Packet or Controller Package / 任务包或主控包

- `S14` does not require a normal worker task packet / `S14` 不需要普通 worker 任务包 (`not_required`).

**Packet/material contract files / 任务包或控制包文件：**

- _Not applicable / 不适用_

The packet is not a prompt template for free generation. It is a bounded contract that fixes allowed inputs, allowed paths, forbidden routes, output schema, validators, and the no-completion authority boundary. / 任务包不是自由生成提示词，而是限定输入、路径、禁止路线、输出 schema、validator 和无完成权威边界的契约。

## 6. Execution Sequence / 执行顺序

**中文执行顺序：**

- 归一化 findings
- 去重或拒绝不可执行 finding
- 判定 failure type
- 选择最近责任 stage/material
- 定义局部 repair scope 和 protected nodes
- 编译 S15 或上游 repair task
- 制定 priority 和 validation plan

**English execution sequence:**

- Normalize findings.
- Deduplicate or reject non-actionable findings.
- Classify failure type.
- Select nearest responsible stage/material.
- Define local repair scope and protected nodes.
- Compile S15 or upstream repair tasks.
- Define priority and validation plan.

The controller may dispatch a producer and verifier lane when the contract requires worker evidence, but only the controller commits graph state. / 当契约要求 worker 证据时，主控可分派 producer 和 verifier，但只有主控能提交图状态。

## 7. Output Material / 输出物料

**Declared produces / 契约声明输出：**

- `normalized backflow repair plan`
- `nearest responsible stage map`
- `bounded repair task plan`
- `response action map`

**Positive material fixtures / 正例物料样例：**

- [`examples/materials/phase10_s14_backflow_repair_plan.json`](../../examples/materials/phase10_s14_backflow_repair_plan.json)

**Payload modules / payload 模块：**

- `schema_version`
- `stage_id`
- `completion_boundary`
- `authority_boundary`
- `finding_intake_ledger`
- `finding_normalization_table`
- `nearest_responsible_stage_map`
- `affected_material_graph_slice`
- `repair_scope_plan`
- `repair_task_packets`
- `control_reselection_tasks`
- `response_action_map`
- `priority_schedule`
- `owner_gate_report`
- `validation_plan`
- `unresolved_or_ambiguous_findings`
- `validator_report`
- `remaining_risks`

These fields are meant to be checked, consumed, and backflowed as structured graph materials rather than copied as prose. / 这些字段应作为结构化图物料被检查、消费和回流，而不是被复制成散文。

## 8. Validators and Failure Modes / Validator 与失败模式

**Validators / 验证器：**

- `S14_finding_intake_coverage`
- `S14_duplicate_and_rejection_reason`
- `S14_failure_type_classification`
- `S14_nearest_responsible_stage`
- `S14_no_bare_S09_route`
- `S14_repair_locality`
- `S14_affected_downstream_nodes`
- `S14_protected_unrelated_nodes`
- `S14_owner_gate_status`
- `S14_task_packet_compile`
- `S14_no_execution`
- `S14_no_completion_claim`

**Negative fixtures cover / 负例覆盖：**

- `examples/materials/invalid-s14-backflow-plan-authority-repair-executed.json`
- `examples/materials/invalid-s14-backflow-plan-bare-s09-route.json`
- `examples/materials/invalid-s14-backflow-plan-completion-overclaim.json`
- `examples/materials/invalid-s14-backflow-plan-global-rewrite-scope.json`
- `examples/materials/invalid-s14-backflow-plan-intake-coverage-gap.json`
- `examples/materials/invalid-s14-backflow-plan-invalid-failure-type.json`
- `examples/materials/invalid-s14-backflow-plan-missing-intake-ledger.json`
- `examples/materials/invalid-s14-backflow-plan-missing-route-rationale.json`
- `examples/materials/invalid-s14-backflow-plan-missing-stale-nodes.json`
- `examples/materials/invalid-s14-backflow-plan-missing-task-for-finding.json`
- `examples/materials/invalid-s14-backflow-plan-owner-gate-disabled.json`
- `examples/materials/invalid-s14-backflow-plan-response-missing-evidence.json`
- `examples/materials/invalid-s14-backflow-plan-task-executed.json`
- `examples/materials/invalid-s14-backflow-plan-validation-missing-stale.json`

Run the focused verifier / 运行聚焦验证器：

```bash
python3 scripts/verify_s14_backflow_repair_plan.py
```

## 9. Downstream Handoffs / 下游交接

The output is only useful when downstream stages can consume it with traceable references. / 输出只有在下游能以可追踪引用消费时才有意义。

- It should name what is ready for downstream use. / 应说明哪些内容可供下游使用。
- It should name what is unresolved, rejected, owner-gated, stale, or missing. / 应说明哪些内容 unresolved、rejected、owner-gated、stale 或 missing。
- It should preserve the nearest-responsible-stage route for later backflow. / 应保留后续回流所需的最近责任阶段路线。

## 10. Authority and Misuse Boundaries / 权威边界与误用防线

**中文边界：**

- 不执行修复
- 不允许 bare S09 route
- 不允许 global rewrite scope
- 不能关闭 owner gate

**English boundaries:**

- It does not execute repairs.
- Bare S09 routes are forbidden.
- Global rewrite scope is forbidden.
- Owner gates must not be disabled.

Specialist agents and scripts may return candidates or evidence; they never own completion authority. / 专家 agent 和脚本只能返回候选或证据，不能拥有完成权威。

## 11. Implementation Map / 实现索引

- Stage id(s) / 阶段 ID：`S14`
- Stage contract(s) / 阶段契约：
- [`examples/stage-contracts/S14.stage-contract.json`](../../examples/stage-contracts/S14.stage-contract.json)
- Stage registry / 阶段注册表：[`runtime/stage_registry.json`](../../runtime/stage_registry.json)
- Phase validators / Phase 验证配置：[`runtime/phase10_content_validators.json`](../../runtime/phase10_content_validators.json)
- Material schema / 物料 schema：[`schemas/ppg-material-payloads.schema.json`](../../schemas/ppg-material-payloads.schema.json)
- Material validator / 物料验证器：[`scripts/validate_material.py`](../../scripts/validate_material.py)
- Focused verifier / 聚焦验证器：[`scripts/verify_s14_backflow_repair_plan.py`](../../scripts/verify_s14_backflow_repair_plan.py)

## 12. Plain-Language Summary / 通俗总结

**中文。** S14 决定“修哪里”，不是全篇乱修。它把每个 finding 路由到最近责任物料，防止全局重写。 它的作用是把本环节的判断变成可检查、可回流、可被下游安全消费的结构化物料，而不是让后续 agent 依赖印象或自由发挥。

**EN.** S14 decides where to repair, not how to repair everything. It prevents global rewrites by routing each finding to the nearest responsible material. Its role is to turn this stage's judgments into structured, checkable, backflow-ready materials that downstream agents can consume safely instead of relying on impressions or free-form improvisation.
