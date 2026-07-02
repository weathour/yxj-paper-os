# S09 Control Selection and Task-Packet Assembly / 控制材料选择与任务包编译

> Bilingual stage explainer for humans and controller agents. / 面向人类与主控 agent 的双语阶段说明。

## 1. Purpose / 目的

**EN.** S09 is an umbrella stage: S09A selects rich controls for a target unit, and S09B compiles those controls into a bounded worker TaskPacket.

**中文。** S09 是总括环节：S09A 为目标单元选择丰富控制材料，S09B 把这些控制材料编译成受限 worker TaskPacket。

**Contract purpose / 契约原文目的。** Select a target-specific, context-rich, priority-ordered control bundle without compiling worker packets or granting content-generation authority. / Compile one bounded, authority-safe per-unit TaskPacket from an S09A selected control bundle.

## 2. Position in the Paper Production Graph / 在论文生产图中的位置

```text
S04/S05/S06/S07/S08 → S09A → S09B → S10/S11/S12/S15
```

**EN.** S09 is the adapter between planning and production. It prevents S10/S11 workers from receiving vague “write this” prompts.

**中文。** S09 是规划与生产之间的适配器。它防止 S10/S11 worker 收到模糊的“写一下这个”提示。

## 3. When the Controller Should Trigger This Stage / 主 agent 什么时候触发本环节

**中文触发条件：**

- 要让 worker 生成某个正文单元或图表 artifact 前
- 需要把 claim、读者、对象、语言、视觉控制合并给一个目标单元时
- 需要编译 allowed paths、forbidden routes、return format 和 validators 时

**English triggers:**

- Before a worker generates a text unit or visual artifact.
- Claim, reader, object, surface, and visual controls must be merged for one target unit.
- Allowed paths, forbidden routes, return format, and validators must be compiled.

## 4. Inputs and Preconditions / 输入与前置条件

**Declared consumes / 契约声明输入：**

- `claim controls`
- `spine controls`
- `granularity controls`
- `surface rules`
- `target unit`
- `selected control bundle`
- `evidence anchors`
- `validator refs`
- `return format`

**What this stage analyzes or designs / 本环节具体分析或设计：**

**中文：**

- S09A 选择目标单元所需的 hard constraints、local/global context、positive/negative controls
- S09B 编译 packet identity、allowed read/write、worker boot clause、single-writer lock、return format

**English:**

- S09A selects hard constraints, local/global context, and positive/negative controls for a target unit.
- S09B compiles packet identity, allowed reads/writes, worker boot clause, single-writer lock, and return format.

If an input is missing, the controller should return to the nearest responsible upstream stage instead of letting the worker guess. / 如果输入缺失，主 agent 应回到最近责任上游环节，而不是让 worker 猜。

## 5. Task Packet or Controller Package / 任务包或主控包

- `S09A` does not require a normal worker task packet / `S09A` 不需要普通 worker 任务包 (`not_required`).
- `S09B` does not require a normal worker task packet / `S09B` 不需要普通 worker 任务包 (`not_required`).

**Packet/material contract files / 任务包或控制包文件：**

- [`examples/materials/phase10_s09b_task_packet_assembly.yaml`](../../examples/materials/phase10_s09b_task_packet_assembly.yaml)

The packet is not a prompt template for free generation. It is a bounded contract that fixes allowed inputs, allowed paths, forbidden routes, output schema, validators, and the no-completion authority boundary. / 任务包不是自由生成提示词，而是限定输入、路径、禁止路线、输出 schema、validator 和无完成权威边界的契约。

## 6. Execution Sequence / 执行顺序

**中文执行顺序：**

- S09A: target unit profile
- S09A: rich control selection and conflict resolution
- S09A: context usage and freshness check
- S09A: downstream packet requirements
- S09B: packet identity and target
- S09B: allowed paths and forbidden routes
- S09B: selected controls propagation
- S09B: emitted task packet validation

**English execution sequence:**

- S09A: target-unit profile.
- S09A: rich control selection and conflict resolution.
- S09A: context usage and freshness check.
- S09A: downstream packet requirements.
- S09B: packet identity and target.
- S09B: allowed paths and forbidden routes.
- S09B: selected-control propagation.
- S09B: emitted TaskPacket validation.

The controller may dispatch a producer and verifier lane when the contract requires worker evidence, but only the controller commits graph state. / 当契约要求 worker 证据时，主控可分派 producer 和 verifier，但只有主控能提交图状态。

## 7. Output Material / 输出物料

**Declared produces / 契约声明输出：**

- `selected control bundle`
- `control priority map`
- `missing control report`
- `task packet`
- `section move plan`
- `single-writer lock`
- `missing material report`

**Positive material fixtures / 正例物料样例：**

- [`examples/materials/phase10_s09a_rich_control_bundle.yaml`](../../examples/materials/phase10_s09a_rich_control_bundle.yaml)
- [`examples/materials/phase10_s09b_task_packet_assembly.yaml`](../../examples/materials/phase10_s09b_task_packet_assembly.yaml)

**Payload modules / payload 模块：**

- `phase10_s09a_rich_control_bundle.yaml:schema_version`
- `phase10_s09a_rich_control_bundle.yaml:stage_id`
- `phase10_s09a_rich_control_bundle.yaml:completion_boundary`
- `phase10_s09a_rich_control_bundle.yaml:authority_boundary_audit`
- `phase10_s09a_rich_control_bundle.yaml:target_unit_profile`
- `phase10_s09a_rich_control_bundle.yaml:hard_constraints`
- `phase10_s09a_rich_control_bundle.yaml:local_context`
- `phase10_s09a_rich_control_bundle.yaml:adjacent_context`
- `phase10_s09a_rich_control_bundle.yaml:global_orientation`
- `phase10_s09a_rich_control_bundle.yaml:claim_control_bundle`
- `phase10_s09a_rich_control_bundle.yaml:reader_context_bundle`
- `phase10_s09a_rich_control_bundle.yaml:object_context_bundle`
- `phase10_s09a_rich_control_bundle.yaml:surface_control_bundle`
- `phase10_s09a_rich_control_bundle.yaml:visual_formal_control_bundle`
- `phase10_s09a_rich_control_bundle.yaml:evidence_anchor_bundle`
- `phase10_s09a_rich_control_bundle.yaml:negative_control_bundle`
- `phase10_s09a_rich_control_bundle.yaml:conflict_resolution_log`
- `phase10_s09a_rich_control_bundle.yaml:control_priority_map`
- `phase10_s09a_rich_control_bundle.yaml:context_usage_instructions`
- `phase10_s09a_rich_control_bundle.yaml:excluded_or_deferred_controls`
- `phase10_s09a_rich_control_bundle.yaml:freshness_check`
- `phase10_s09a_rich_control_bundle.yaml:missing_control_report`
- `phase10_s09a_rich_control_bundle.yaml:coverage_ledger`
- `phase10_s09a_rich_control_bundle.yaml:downstream_packet_requirements`
- `phase10_s09a_rich_control_bundle.yaml:candidate_return`
- `phase10_s09b_task_packet_assembly.yaml:schema_version`
- `phase10_s09b_task_packet_assembly.yaml:stage_id`
- `phase10_s09b_task_packet_assembly.yaml:completion_boundary`
- `phase10_s09b_task_packet_assembly.yaml:packet_identity`
- `phase10_s09b_task_packet_assembly.yaml:target_unit`
- `phase10_s09b_task_packet_assembly.yaml:selected_control_bundle_ref`
- `phase10_s09b_task_packet_assembly.yaml:control_digest`
- `phase10_s09b_task_packet_assembly.yaml:task_mission`
- `phase10_s09b_task_packet_assembly.yaml:allowed_read_paths`
- `phase10_s09b_task_packet_assembly.yaml:allowed_write_paths`
- `phase10_s09b_task_packet_assembly.yaml:forbidden_routes`
- `phase10_s09b_task_packet_assembly.yaml:worker_boot_clause`
- `phase10_s09b_task_packet_assembly.yaml:section_or_unit_move_plan`
- `phase10_s09b_task_packet_assembly.yaml:claim_boundary_controls`
- `phase10_s09b_task_packet_assembly.yaml:reader_spine_controls`
- `phase10_s09b_task_packet_assembly.yaml:object_granularity_controls`
- `phase10_s09b_task_packet_assembly.yaml:terminology_surface_controls`
- `phase10_s09b_task_packet_assembly.yaml:visual_formal_controls`
- `phase10_s09b_task_packet_assembly.yaml:negative_controls`
- `phase10_s09b_task_packet_assembly.yaml:context_usage_instructions`
- `phase10_s09b_task_packet_assembly.yaml:validators`
- `phase10_s09b_task_packet_assembly.yaml:return_format`
- `phase10_s09b_task_packet_assembly.yaml:single_writer_lock`
- `phase10_s09b_task_packet_assembly.yaml:stale_material_policy`
- `phase10_s09b_task_packet_assembly.yaml:missing_material_report`
- `phase10_s09b_task_packet_assembly.yaml:packet_authority_boundary`
- `phase10_s09b_task_packet_assembly.yaml:emitted_task_packet`
- `phase10_s09b_task_packet_assembly.yaml:candidate_return`

These fields are meant to be checked, consumed, and backflowed as structured graph materials rather than copied as prose. / 这些字段应作为结构化图物料被检查、消费和回流，而不是被复制成散文。

## 8. Validators and Failure Modes / Validator 与失败模式

**Validators / 验证器：**

- `S09A_target_unit_profile`
- `S09A_hard_constraints_present`
- `S09A_rich_context_layering`
- `S09A_claim_control_selection`
- `S09A_reader_context_selection`
- `S09A_object_context_selection`
- `S09A_surface_control_selection`
- `S09A_visual_formal_control_selection`
- `S09A_negative_controls`
- `S09A_conflict_resolution`
- `S09A_context_usage_instructions`
- `S09A_freshness_check`
- `S09A_missing_control_report`
- `S09A_coverage_ledger`
- `S09A_downstream_packet_requirements`
- `S09A_no_bare_S09`
- `S09A_no_task_packet_or_final_content`
- `S09B_packet_identity`
- `S09B_allowed_read_paths`
- `S09B_allowed_write_paths`
- `S09B_forbidden_routes`
- `S09B_worker_boot_clause`
- `S09B_completion_forbidden`
- `S09B_no_recursive_orchestration`
- `S09B_single_writer_lock`
- `S09B_unit_move_plan`
- `S09B_selected_controls_propagated`
- `S09B_context_usage_preserved`
- `S09B_background_not_claim_authority`
- `S09B_return_format`
- `S09B_missing_material_report`
- `S09B_authority_boundary`
- `S09B_emitted_packet_validates`
- `S09B_no_bare_S09`

**Negative fixtures cover / 负例覆盖：**

- `examples/materials/invalid-s09a-rich-control-blocking-missing-control.yaml`
- `examples/materials/invalid-s09a-rich-control-completion-overclaim.yaml`
- `examples/materials/invalid-s09a-rich-control-final-content.yaml`
- `examples/materials/invalid-s09a-rich-control-missing-conflict-resolution.yaml`
- `examples/materials/invalid-s09a-rich-control-missing-context-usage.yaml`
- `examples/materials/invalid-s09a-rich-control-missing-downstream-requirements.yaml`
- `examples/materials/invalid-s09a-rich-control-missing-hard-constraints.yaml`
- `examples/materials/invalid-s09a-rich-control-missing-local-context.yaml`
- `examples/materials/invalid-s09a-rich-control-missing-target-unit.yaml`
- `examples/materials/invalid-s09a-rich-control-missing-visual-controls.yaml`
- `examples/materials/invalid-s09a-rich-control-stale-freshness.yaml`
- `examples/materials/invalid-s09b-task-packet-assembly-authority-expansion.yaml`
- `examples/materials/invalid-s09b-task-packet-assembly-candidate-content.yaml`
- `examples/materials/invalid-s09b-task-packet-assembly-completion-overclaim.yaml`
- `examples/materials/invalid-s09b-task-packet-assembly-missing-context-usage.yaml`
- `examples/materials/invalid-s09b-task-packet-assembly-missing-emitted-packet.yaml`
- `examples/materials/invalid-s09b-task-packet-assembly-missing-forbidden-route.yaml`
- `examples/materials/invalid-s09b-task-packet-assembly-missing-identity.yaml`
- `examples/materials/invalid-s09b-task-packet-assembly-missing-move-plan.yaml`
- `examples/materials/invalid-s09b-task-packet-assembly-missing-return-format.yaml`
- `examples/materials/invalid-s09b-task-packet-assembly-missing-single-writer-lock.yaml`
- `examples/materials/invalid-s09b-task-packet-assembly-unsafe-write-path.yaml`
- `examples/materials/invalid-s09b-task-packet-assembly-weak-boot-clause.yaml`

Run the focused verifier / 运行聚焦验证器：

```bash
python3 scripts/verify_s09_control_packet_assembly.py
```

## 9. Downstream Handoffs / 下游交接

The output is only useful when downstream stages can consume it with traceable references. / 输出只有在下游能以可追踪引用消费时才有意义。

- It should name what is ready for downstream use. / 应说明哪些内容可供下游使用。
- It should name what is unresolved, rejected, owner-gated, stale, or missing. / 应说明哪些内容 unresolved、rejected、owner-gated、stale 或 missing。
- It should preserve the nearest-responsible-stage route for later backflow. / 应保留后续回流所需的最近责任阶段路线。

## 10. Authority and Misuse Boundaries / 权威边界与误用防线

**中文边界：**

- 禁止 bare S09
- S09A 不产出 worker packet 或最终内容
- S09B 不产出候选正文/图件，只产出任务包
- 不能扩大 worker 权限

**English boundaries:**

- Bare S09 is forbidden.
- S09A does not produce a worker packet or final content.
- S09B does not produce prose/visual candidates; it produces a TaskPacket.
- It must not expand worker authority.

Specialist agents and scripts may return candidates or evidence; they never own completion authority. / 专家 agent 和脚本只能返回候选或证据，不能拥有完成权威。

## 11. Implementation Map / 实现索引

- Stage id(s) / 阶段 ID：`S09A/S09B`
- Stage contract(s) / 阶段契约：
- [`examples/stage-contracts/S09A.stage-contract.json`](../../examples/stage-contracts/S09A.stage-contract.json)
- [`examples/stage-contracts/S09B.stage-contract.json`](../../examples/stage-contracts/S09B.stage-contract.json)
- Stage registry / 阶段注册表：[`runtime/stage_registry.json`](../../runtime/stage_registry.json)
- Phase validators / Phase 验证配置：[`runtime/phase10_content_validators.json`](../../runtime/phase10_content_validators.json)
- Material schema / 物料 schema：[`schemas/ppg-material-payloads.schema.json`](../../schemas/ppg-material-payloads.schema.json)
- Material validator / 物料验证器：[`scripts/validate_material.py`](../../scripts/validate_material.py)
- Focused verifier / 聚焦验证器：[`scripts/verify_s09_control_packet_assembly.py`](../../scripts/verify_s09_control_packet_assembly.py)

## 12. Plain-Language Summary / 通俗总结

**中文。** S09 是规划与生产之间的适配器。它防止 S10/S11 worker 收到模糊的“写一下这个”提示。 它的作用是把本环节的判断变成可检查、可回流、可被下游安全消费的结构化物料，而不是让后续 agent 依赖印象或自由发挥。

**EN.** S09 is the adapter between planning and production. It prevents S10/S11 workers from receiving vague “write this” prompts. Its role is to turn this stage's judgments into structured, checkable, backflow-ready materials that downstream agents can consume safely instead of relying on impressions or free-form improvisation.
