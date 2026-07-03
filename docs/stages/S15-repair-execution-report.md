# S15 Repair Execution Report / 局部修复执行报告

> Bilingual stage explainer for humans and controller agents. / 面向人类与主控 agent 的双语阶段说明。

## 1. Purpose / 目的

**EN.** S15 executes bounded repairs from S14, records diff locality, revised candidates, downstream regeneration, stale resolution, and no-new-risk evidence.

**中文。** S15 执行 S14 的受限修复，记录 diff locality、修订候选、下游再生成、stale 解决和无新增风险证据。

**Contract purpose / 契约原文目的。** Execute S14-authorized scoped repairs and regenerate only affected downstream outputs, returning candidate evidence without graph commit or export readiness claims.

## 2. Position in the Paper Production Graph / 在论文生产图中的位置

```text
S14 → S15 → S12/S13/S16
```

**EN.** S15 repairs only what S14 authorized. It proves that the fix was local and did not damage unrelated graph nodes.

**中文。** S15 只修 S14 授权的范围，并证明修复是局部的、没有破坏无关图节点。

## 3. When the Controller Should Trigger This Stage / 主 agent 什么时候触发本环节

**中文触发条件：**

- S14 已编译 bounded repair packet 时
- 需要局部修改 material/text/figure/task packet 时
- 需要证明 finding 已解决且未引入新高风险时

**English triggers:**

- S14 has compiled a bounded repair packet.
- A local material/text/figure/task-packet change is required.
- Evidence is needed that the finding is resolved without new high risk.

## 4. Inputs and Preconditions / 输入与前置条件

**Declared consumes / 契约声明输入：**

- `strict S14 repair task packet`
- `target material base version`
- `affected downstream stale set`
- `protected unrelated node list`

**What this stage analyzes or designs / 本环节具体分析或设计：**

**中文：**

- repair task ack
- pre-repair snapshot
- target material diff
- revised material candidate
- downstream regeneration log
- stale resolution
- unrelated node preservation
- new risk scan

**English:**

- Repair-task acknowledgement.
- Pre-repair snapshot.
- Target-material diff.
- Revised material candidate.
- Downstream-regeneration log.
- Stale resolution.
- Unrelated-node preservation.
- New-risk scan.

If an input is missing, the controller should return to the nearest responsible upstream stage instead of letting the worker guess. / 如果输入缺失，主 agent 应回到最近责任上游环节，而不是让 worker 猜。

## 5. Task Packet or Controller Package / 任务包或主控包

- `S15` requires a strict worker task packet / `S15` 需要严格 worker 任务包: `examples/packets/phase10_s15_scoped_repair_packet.v1.yaml`.

**Packet/material contract files / 任务包或控制包文件：**

- [`examples/packets/phase10_s15_scoped_repair_packet.v1.yaml`](../../examples/packets/phase10_s15_scoped_repair_packet.v1.yaml)

The packet is not a prompt template for free generation. It is a bounded contract that fixes allowed inputs, allowed paths, forbidden routes, output schema, validators, and the no-completion authority boundary. / 任务包不是自由生成提示词，而是限定输入、路径、禁止路线、输出 schema、validator 和无完成权威边界的契约。

## 6. Execution Sequence / 执行顺序

**中文执行顺序：**

- ACK repair packet
- 记录 pre-repair snapshot
- 执行局部 diff
- 生成 revised material/text/figure candidate
- 按需要再生成 affected downstream outputs
- 证明 unrelated nodes unchanged
- 验证 finding resolution 和 no-new-high-risk

**English execution sequence:**

- Acknowledge the repair packet.
- Record pre-repair snapshot.
- Apply local diff.
- Produce revised material/text/figure candidate.
- Regenerate affected downstream outputs when needed.
- Prove unrelated nodes unchanged.
- Verify finding resolution and no-new-high-risk.

The controller may dispatch a producer and verifier lane when the contract requires worker evidence, but only the controller commits graph state. / 当契约要求 worker 证据时，主控可分派 producer 和 verifier，但只有主控能提交图状态。

## 7. Output Material / 输出物料

**Declared produces / 契约声明输出：**

- `repair execution report`
- `revised material candidate`
- `regenerated affected outputs`
- `updated validator report`

**Positive material fixtures / 正例物料样例：**

- [`examples/materials/phase10_s15_repair_execution_report.json`](../../examples/materials/phase10_s15_repair_execution_report.json)

**Payload modules / payload 模块：**

- `schema_version`
- `stage_id`
- `completion_boundary`
- `authority_boundary`
- `repair_task_ack`
- `pre_repair_snapshot`
- `target_material_diff`
- `revised_material_candidate`
- `regenerated_task_packets`
- `regenerated_text_or_figure_candidates`
- `local_candidate_excerpt`
- `affected_downstream_regeneration_log`
- `stale_resolution_report`
- `unrelated_node_preservation_report`
- `finding_resolution_evidence`
- `updated_validator_report`
- `new_risk_scan`
- `candidate_artifact_return`
- `missing_material_report`
- `verifier_evidence`
- `remaining_risks`

These fields are meant to be checked, consumed, and backflowed as structured graph materials rather than copied as prose. / 这些字段应作为结构化图物料被检查、消费和回流，而不是被复制成散文。

## 8. Validators and Failure Modes / Validator 与失败模式

**Validators / 验证器：**

- `S15_strict_packet_ack`
- `S15_missing_material_report`
- `S15_diff_locality`
- `S15_unrelated_nodes_unchanged`
- `S15_stale_propagation`
- `S15_finding_resolution`
- `S15_no_new_high_severity`
- `S15_overlay_clause_preserved`
- `S15_candidate_return_schema`
- `S15_no_completion_claim`

**Negative fixtures cover / 负例覆盖：**

- `examples/materials/invalid-s15-repair-execution-authority-exported.json`
- `examples/materials/invalid-s15-repair-execution-bad-candidate-return.json`
- `examples/materials/invalid-s15-repair-execution-bad-claim-impact.json`
- `examples/materials/invalid-s15-repair-execution-bad-downstream-action.json`
- `examples/materials/invalid-s15-repair-execution-bad-resolution-status.json`
- `examples/materials/invalid-s15-repair-execution-bad-task-kind.json`
- `examples/materials/invalid-s15-repair-execution-bare-s09-packet.json`
- `examples/materials/invalid-s15-repair-execution-blocked-missing-material.json`
- `examples/materials/invalid-s15-repair-execution-completion-overclaim.json`
- `examples/materials/invalid-s15-repair-execution-global-rewrite.json`
- `examples/materials/invalid-s15-repair-execution-missing-artifact.json`
- `examples/materials/invalid-s15-repair-execution-missing-preservation.json`
- `examples/materials/invalid-s15-repair-execution-missing-task-ack.json`
- `examples/materials/invalid-s15-repair-execution-missing-verifier-check.json`
- `examples/materials/invalid-s15-repair-execution-new-high-risk.json`
- `examples/materials/invalid-s15-repair-execution-stale-unresolved.json`
- `examples/materials/invalid-s15-repair-execution-unsafe-diff-path.json`
- `examples/materials/invalid-s15-repair-execution-validator-failed.json`

Run the focused verifier / 运行聚焦验证器：

```bash
python3 scripts/verify_s15_repair_execution_report.py
```

## 9. Downstream Handoffs / 下游交接

The output is only useful when downstream stages can consume it with traceable references. / 输出只有在下游能以可追踪引用消费时才有意义。

- It should name what is ready for downstream use. / 应说明哪些内容可供下游使用。
- It should name what is unresolved, rejected, owner-gated, stale, or missing. / 应说明哪些内容 unresolved、rejected、owner-gated、stale 或 missing。
- It should preserve the nearest-responsible-stage route for later backflow. / 应保留后续回流所需的最近责任阶段路线。

## 10. Authority and Misuse Boundaries / 权威边界与误用防线

**中文边界：**

- 不能提交 graph completion
- 不能做 export/submission
- 不能执行 global rewrite
- 不能使用 bare S09 packet

**English boundaries:**

- It must not claim graph completion.
- It must not export or submit.
- It must not perform global rewrite.
- It must not use bare S09 packets.

Specialist agents and scripts may return candidates or evidence; they never own completion authority. / 专家 agent 和脚本只能返回候选或证据，不能拥有完成权威。

## 11. Implementation Map / 实现索引

- Stage id(s) / 阶段 ID：`S15`
- Stage contract(s) / 阶段契约：
- [`examples/stage-contracts/S15.stage-contract.json`](../../examples/stage-contracts/S15.stage-contract.json)
- Stage registry / 阶段注册表：[`runtime/stage_registry.json`](../../runtime/stage_registry.json)
- Phase validators / Phase 验证配置：[`runtime/phase10_content_validators.json`](../../runtime/phase10_content_validators.json)
- Material schema / 物料 schema：[`schemas/ppg-material-payloads.schema.json`](../../schemas/ppg-material-payloads.schema.json)
- Material validator / 物料验证器：[`scripts/validate_material.py`](../../scripts/validate_material.py)
- Focused verifier / 聚焦验证器：[`scripts/verify_s15_repair_execution_report.py`](../../scripts/verify_s15_repair_execution_report.py)

## 12. Plain-Language Summary / 通俗总结

**中文。** S15 只修 S14 授权的范围，并证明修复是局部的、没有破坏无关图节点。 它的作用是把本环节的判断变成可检查、可回流、可被下游安全消费的结构化物料，而不是让后续 agent 依赖印象或自由发挥。

**EN.** S15 repairs only what S14 authorized. It proves that the fix was local and did not damage unrelated graph nodes. Its role is to turn this stage's judgments into structured, checkable, backflow-ready materials that downstream agents can consume safely instead of relying on impressions or free-form improvisation.

## Source-writeback repairs for compiled delivery

S15 repair execution can be candidate-only for ordinary graph repairs, but S16 compiled targets require source-writeback when the PDF source is not content-bearing. The S15 repair report should include or reference the LatexWritebackPlan, patchset, apply report, source-tree-after snapshot, claim-boundary audit, and template-compatibility check when resolving an S16 delivery gap.

If S15 returns only a revised candidate while the compiled target requires source writeback, S16 must continue to fail with `E_S16_SOURCE_WRITEBACK_REQUIRED` and route back through S14/S15 instead of accepting a template-only PDF.

## Stage-quality upgrade contract / 阶段质量升级合同

**EN.** S15 executes only S14-authorized local repairs. Producer packets must include the strict repair task, base version, affected downstream stale set, protected unrelated nodes, and validation plan. The return must include `repair_task_ack`, `pre_repair_snapshot`, `target_material_diff`, revised candidate, `affected_downstream_regeneration_log`, `stale_resolution_report`, `unrelated_node_preservation_report`, `finding_resolution_evidence`, updated validator report, no-new-risk scan, CandidateArtifactReturn, and verifier evidence. S15 returns evidence and candidates; it does not commit graph state or claim export readiness.

**中文。** S15 只执行 S14 授权的局部修复。Producer 包必须包含 strict repair task、base version、affected downstream stale set、protected unrelated nodes 和 validation plan。返回必须包含 `repair_task_ack`、`pre_repair_snapshot`、`target_material_diff`、修订候选、`affected_downstream_regeneration_log`、`stale_resolution_report`、`unrelated_node_preservation_report`、`finding_resolution_evidence`、updated validator report、no-new-risk scan、CandidateArtifactReturn 和 verifier evidence。S15 只返回证据和候选，不提交图状态，也不声称 export readiness。

Stage-quality focus / 阶段质量焦点：strict repair scope, diff locality, stale propagation, unrelated-node preservation, and no graph/export overclaim.
