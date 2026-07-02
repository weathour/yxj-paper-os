# S11 Figure Caption Artifact Bundle / 图表、caption 与形式 artifact 候选包

> Bilingual stage explainer for humans and controller agents. / 面向人类与主控 agent 的双语阶段说明。

## 1. Purpose / 目的

**EN.** S11 produces contract-bound visual/formal artifacts and captions with source-data trace, panel-claim trace, visual polish, accessibility, and export evidence.

**中文。** S11 根据契约生成图表/形式对象和 caption 候选，并提供源数据、panel-claim、视觉润色、可访问性和导出证据。

**Contract purpose / 契约原文目的。** Produce contract-bound candidate figures, captions, tables, algorithms, formulas, render plans, and export bundles without changing proof role, evidence meaning, or claim boundaries.

## 2. Position in the Paper Production Graph / 在论文生产图中的位置

```text
S08/S09B/S04/S07 → S11 → S12/S13/S16
```

**EN.** S11 is not “make it pretty.” It preserves proof role, source data, claim boundaries, and accessibility while producing visual candidates.

**中文。** S11 不是简单“美化”。它在生成视觉候选时保留 proof role、源数据、claim 边界和可访问性。

## 3. When the Controller Should Trigger This Stage / 主 agent 什么时候触发本环节

**中文触发条件：**

- S08 已给出 figure/table/formal object contract 时
- 需要生成 caption 或图件候选时
- 需要检查视觉润色是否改变含义或 proof role 时

**English triggers:**

- S08 has provided a figure/table/formal-object contract.
- A caption or visual artifact candidate is needed.
- Visual polish must be checked for meaning or proof-role changes.

## 4. Inputs and Preconditions / 输入与前置条件

**Declared consumes / 契约声明输入：**

- `figure contracts`
- `panel evidence packages`
- `source data locators`
- `caption brief`

**What this stage analyzes or designs / 本环节具体分析或设计：**

**中文：**

- figure contract compliance
- generated artifacts and editable sources
- source data trace
- panel/caption claim trace
- visual polish policy/report
- accessibility/export manifest

**English:**

- Figure-contract compliance.
- Generated artifacts and editable sources.
- Source-data trace.
- Panel/caption claim trace.
- Visual-polish policy/report.
- Accessibility and export manifest.

If an input is missing, the controller should return to the nearest responsible upstream stage instead of letting the worker guess. / 如果输入缺失，主 agent 应回到最近责任上游环节，而不是让 worker 猜。

## 5. Task Packet or Controller Package / 任务包或主控包

- `S11` requires a strict worker task packet / `S11` 需要严格 worker 任务包: `examples/packets/phase10_s11_figure_caption_artifact_packet.v1.yaml`.

**Packet/material contract files / 任务包或控制包文件：**

- [`examples/packets/phase10_s11_figure_caption_artifact_packet.v1.yaml`](../../examples/packets/phase10_s11_figure_caption_artifact_packet.v1.yaml)

The packet is not a prompt template for free generation. It is a bounded contract that fixes allowed inputs, allowed paths, forbidden routes, output schema, validators, and the no-completion authority boundary. / 任务包不是自由生成提示词，而是限定输入、路径、禁止路线、输出 schema、validator 和无完成权威边界的契约。

## 6. Execution Sequence / 执行顺序

**中文执行顺序：**

- ACK S11 packet
- 读取 S08 contract 和 source data package
- 生成或规划 visual artifact
- 编写 caption/legend draft
- 检查 panel/caption claim boundary
- 记录 image integrity 与 polish report
- 执行 accessibility/export manifest 检查
- 返回 candidate artifact bundle

**English execution sequence:**

- Acknowledge the S11 packet.
- Read S08 contract and source-data package.
- Generate or plan visual artifacts.
- Draft caption/legend.
- Check panel/caption claim boundary.
- Record image integrity and polish report.
- Run accessibility/export-manifest checks.
- Return candidate artifact bundle.

The controller may dispatch a producer and verifier lane when the contract requires worker evidence, but only the controller commits graph state. / 当契约要求 worker 证据时，主控可分派 producer 和 verifier，但只有主控能提交图状态。

## 7. Output Material / 输出物料

**Declared produces / 契约声明输出：**

- `figure statistics`
- `image integrity record`
- `caption brief`
- `figure export bundle`

**Positive material fixtures / 正例物料样例：**

- [`examples/materials/phase10_s11_figure_caption_artifact_bundle.json`](../../examples/materials/phase10_s11_figure_caption_artifact_bundle.json)

**Payload modules / payload 模块：**

- `schema_version`
- `stage_id`
- `completion_boundary`
- `authority_boundary`
- `packet_compliance_report`
- `figure_contract_compliance`
- `generated_artifacts`
- `editable_source_bundle`
- `render_plan_if_not_rendered`
- `source_data_trace`
- `panel_claim_trace`
- `caption_legend_draft`
- `caption_claim_trace`
- `image_integrity_record`
- `visual_polish_policy`
- `visual_polish_report`
- `figure_statistics`
- `accessibility_check`
- `export_manifest`
- `coverage_ledger`
- `candidate_artifact_return`
- `verifier_evidence`
- `remaining_risks`
- `missing_material_report`

These fields are meant to be checked, consumed, and backflowed as structured graph materials rather than copied as prose. / 这些字段应作为结构化图物料被检查、消费和回流，而不是被复制成散文。

## 8. Validators and Failure Modes / Validator 与失败模式

**Validators / 验证器：**

- `S11_packet_compliance`
- `S11_figure_contract_compliance`
- `S11_source_data_provenance`
- `S11_panel_claim_trace`
- `S11_caption_claim_boundary`
- `S11_explanatory_vs_evidential_boundary`
- `S11_editable_source_present`
- `S11_render_or_render_plan_present`
- `S11_image_integrity_record`
- `S11_visual_polish_policy`
- `S11_visual_polish_report`
- `S11_accessibility_check`
- `S11_export_manifest`
- `S11_candidate_return_complete`
- `S11_verifier_evidence`
- `S11_authority_boundary`

**Negative fixtures cover / 负例覆盖：**

- `examples/materials/invalid-s11-figure-caption-artifact-accessibility-fail.json`
- `examples/materials/invalid-s11-figure-caption-artifact-bad-candidate-return.json`
- `examples/materials/invalid-s11-figure-caption-artifact-blocked-missing-material.json`
- `examples/materials/invalid-s11-figure-caption-artifact-caption-claim-violation.json`
- `examples/materials/invalid-s11-figure-caption-artifact-completion-overclaim.json`
- `examples/materials/invalid-s11-figure-caption-artifact-final-export-claimed.json`
- `examples/materials/invalid-s11-figure-caption-artifact-missing-contract.json`
- `examples/materials/invalid-s11-figure-caption-artifact-missing-panel-trace.json`
- `examples/materials/invalid-s11-figure-caption-artifact-missing-render-plan.json`
- `examples/materials/invalid-s11-figure-caption-artifact-missing-source-trace.json`
- `examples/materials/invalid-s11-figure-caption-artifact-missing-verifier-evidence.json`
- `examples/materials/invalid-s11-figure-caption-artifact-polish-meaning-change.json`
- `examples/materials/invalid-s11-figure-caption-artifact-polish-policy-gap.json`
- `examples/materials/invalid-s11-figure-caption-artifact-proof-role-changed.json`
- `examples/materials/invalid-s11-figure-caption-artifact-unresolved-coverage.json`
- `examples/materials/invalid-s11-figure-caption-artifact-unsafe-path.json`

Run the focused verifier / 运行聚焦验证器：

```bash
python3 scripts/verify_s11_figure_caption_artifact_bundle.py
```

## 9. Downstream Handoffs / 下游交接

The output is only useful when downstream stages can consume it with traceable references. / 输出只有在下游能以可追踪引用消费时才有意义。

- It should name what is ready for downstream use. / 应说明哪些内容可供下游使用。
- It should name what is unresolved, rejected, owner-gated, stale, or missing. / 应说明哪些内容 unresolved、rejected、owner-gated、stale 或 missing。
- It should preserve the nearest-responsible-stage route for later backflow. / 应保留后续回流所需的最近责任阶段路线。

## 10. Authority and Misuse Boundaries / 权威边界与误用防线

**中文边界：**

- 不能最终导出或投稿
- 不能改变 proof role
- 不能让视觉美化改变主张含义
- 不能把 caption 写成 unsupported claim

**English boundaries:**

- It must not perform final export or submission.
- It must not change proof role.
- Visual polish must not alter claim meaning.
- Captions must not introduce unsupported claims.

Specialist agents and scripts may return candidates or evidence; they never own completion authority. / 专家 agent 和脚本只能返回候选或证据，不能拥有完成权威。

## 11. Implementation Map / 实现索引

- Stage id(s) / 阶段 ID：`S11`
- Stage contract(s) / 阶段契约：
- [`examples/stage-contracts/S11.stage-contract.json`](../../examples/stage-contracts/S11.stage-contract.json)
- Stage registry / 阶段注册表：[`runtime/stage_registry.json`](../../runtime/stage_registry.json)
- Phase validators / Phase 验证配置：[`runtime/phase10_content_validators.json`](../../runtime/phase10_content_validators.json)
- Material schema / 物料 schema：[`schemas/ppg-material-payloads.schema.json`](../../schemas/ppg-material-payloads.schema.json)
- Material validator / 物料验证器：[`scripts/validate_material.py`](../../scripts/validate_material.py)
- Focused verifier / 聚焦验证器：[`scripts/verify_s11_figure_caption_artifact_bundle.py`](../../scripts/verify_s11_figure_caption_artifact_bundle.py)

## 12. Plain-Language Summary / 通俗总结

**中文。** S11 不是简单“美化”。它在生成视觉候选时保留 proof role、源数据、claim 边界和可访问性。 它的作用是把本环节的判断变成可检查、可回流、可被下游安全消费的结构化物料，而不是让后续 agent 依赖印象或自由发挥。

**EN.** S11 is not “make it pretty.” It preserves proof role, source data, claim boundaries, and accessibility while producing visual candidates. Its role is to turn this stage's judgments into structured, checkable, backflow-ready materials that downstream agents can consume safely instead of relying on impressions or free-form improvisation.
