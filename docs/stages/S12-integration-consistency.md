# S12 Integration and Consistency / 集成候选稿与一致性审查

> Bilingual stage explainer for humans and controller agents. / 面向人类与主控 agent 的双语阶段说明。

## 1. Purpose / 目的

**EN.** S12 assembles structured S10/S11 candidates into an integrated manuscript candidate and audits consistency, traceability, stale nodes, and backflow needs.

**中文。** S12 把结构化 S10/S11 候选集成为 integrated manuscript candidate，并审查一致性、可追踪性、stale 节点和回流需求。

**Contract purpose / 契约原文目的。** Compile a structured integrated manuscript candidate package and run consistency/backflow audits without PDF export, final acceptance, or uncontrolled rewriting.

## 2. Position in the Paper Production Graph / 在论文生产图中的位置

```text
S10/S11/S04/S05/S07/S08 → S12 → S13/S14/S16
```

**EN.** S12 creates the machine-readable integrated candidate that later review can attack. It is not PDF compilation and not final acceptance.

**中文。** S12 生成后续可审查的结构化集成候选稿。它不是 PDF 编译，也不是最终接受。

## 3. When the Controller Should Trigger This Stage / 主 agent 什么时候触发本环节

**中文触发条件：**

- 正文和图表候选需要被组装为一份结构化候选稿时
- 需要检查 cross-section consistency、promise satisfaction、trace index 时
- 下游 S13 需要可攻击的审稿对象时

**English triggers:**

- Text and visual candidates must be assembled into one structured candidate.
- Cross-section consistency, promise satisfaction, and trace index must be checked.
- S13 needs a reviewable object.

## 4. Inputs and Preconditions / 输入与前置条件

**Declared consumes / 契约声明输入：**

- `candidate text modules`
- `figures/captions`
- `section move plan`
- `terminology register`
- `claim visibility`

**What this stage analyzes or designs / 本环节具体分析或设计：**

**中文：**

- module inventory
- assembly manifest
- integrated manuscript candidate
- trace index
- claim/promise/terminology/object/figure/surface consistency
- backflow queue

**English:**

- Module inventory.
- Assembly manifest.
- Integrated manuscript candidate.
- Trace index.
- Claim, promise, terminology, object, figure, and surface consistency.
- Backflow queue.

If an input is missing, the controller should return to the nearest responsible upstream stage instead of letting the worker guess. / 如果输入缺失，主 agent 应回到最近责任上游环节，而不是让 worker 猜。

## 5. Task Packet or Controller Package / 任务包或主控包

- `S12` requires a strict worker task packet / `S12` 需要严格 worker 任务包: `examples/packets/phase10_s12_integration_consistency_packet.v1.yaml`.

**Packet/material contract files / 任务包或控制包文件：**

- [`examples/packets/phase10_s12_integration_consistency_packet.v1.yaml`](../../examples/packets/phase10_s12_integration_consistency_packet.v1.yaml)

The packet is not a prompt template for free generation. It is a bounded contract that fixes allowed inputs, allowed paths, forbidden routes, output schema, validators, and the no-completion authority boundary. / 任务包不是自由生成提示词，而是限定输入、路径、禁止路线、输出 schema、validator 和无完成权威边界的契约。

## 6. Execution Sequence / 执行顺序

**中文执行顺序：**

- 收集 S10/S11 candidate returns
- 建立 module inventory 和 assembly manifest
- 组装 integrated candidate
- 建立 trace index
- 执行 claim/promise/consistency audits
- 识别 stale material 和 integration findings
- 生成 backflow queue 和 validator report

**English execution sequence:**

- Collect S10/S11 candidate returns.
- Build module inventory and assembly manifest.
- Assemble integrated candidate.
- Build trace index.
- Run claim, promise, and consistency audits.
- Identify stale material and integration findings.
- Produce backflow queue and validator report.

The controller may dispatch a producer and verifier lane when the contract requires worker evidence, but only the controller commits graph state. / 当契约要求 worker 证据时，主控可分派 producer 和 verifier，但只有主控能提交图状态。

## 7. Output Material / 输出物料

**Declared produces / 契约声明输出：**

- `integrated manuscript candidate`
- `consistency findings`
- `validator report`

**Positive material fixtures / 正例物料样例：**

- [`examples/materials/phase10_s12_integration_report.json`](../../examples/materials/phase10_s12_integration_report.json)

**Payload modules / payload 模块：**

- `schema_version`
- `stage_id`
- `completion_boundary`
- `authority_boundary`
- `module_inventory`
- `assembly_manifest`
- `integrated_manuscript_candidate`
- `trace_index`
- `claim_boundary_audit`
- `promise_satisfaction_report`
- `cross_section_consistency_report`
- `terminology_consistency_report`
- `object_granularity_consistency_report`
- `figure_text_alignment_report`
- `surface_consistency_report`
- `stale_material_report`
- `integration_findings`
- `backflow_queue`
- `validator_report`
- `candidate_artifact_return`
- `remaining_risks`

These fields are meant to be checked, consumed, and backflowed as structured graph materials rather than copied as prose. / 这些字段应作为结构化图物料被检查、消费和回流，而不是被复制成散文。

## 8. Validators and Failure Modes / Validator 与失败模式

**Validators / 验证器：**

- `S12_module_inventory`
- `S12_assembly_manifest`
- `S12_integrated_candidate_package`
- `S12_trace_index`
- `S12_claim_boundary_audit`
- `S12_promise_satisfaction`
- `S12_cross_section_consistency`
- `S12_terminology_consistency`
- `S12_object_granularity_consistency`
- `S12_figure_text_alignment`
- `S12_surface_consistency`
- `S12_stale_material_report`
- `S12_integration_findings`
- `S12_backflow_queue`
- `S12_no_pdf_export`
- `S12_no_final_claim`
- `S12_no_untracked_rewrite`
- `S12_candidate_return_complete`

**Negative fixtures cover / 负例覆盖：**

- `examples/materials/invalid-s12-integration-report-backflow-invalid-stage.json`
- `examples/materials/invalid-s12-integration-report-bad-candidate-return.json`
- `examples/materials/invalid-s12-integration-report-completion-overclaim.json`
- `examples/materials/invalid-s12-integration-report-cross-section-fail.json`
- `examples/materials/invalid-s12-integration-report-final-pdf-claimed.json`
- `examples/materials/invalid-s12-integration-report-finding-missing-route.json`
- `examples/materials/invalid-s12-integration-report-missing-module-inventory.json`
- `examples/materials/invalid-s12-integration-report-missing-trace-index.json`
- `examples/materials/invalid-s12-integration-report-overpromised.json`
- `examples/materials/invalid-s12-integration-report-ready-for-s16-export.json`
- `examples/materials/invalid-s12-integration-report-stale-recompile.json`
- `examples/materials/invalid-s12-integration-report-untraced-claim.json`
- `examples/materials/invalid-s12-integration-report-untracked-rewrite.json`
- `examples/materials/invalid-s12-integration-report-validator-blocks-s13.json`

Run the focused verifier / 运行聚焦验证器：

```bash
python3 scripts/verify_s12_integration_consistency.py
```

## 9. Downstream Handoffs / 下游交接

The output is only useful when downstream stages can consume it with traceable references. / 输出只有在下游能以可追踪引用消费时才有意义。

- It should name what is ready for downstream use. / 应说明哪些内容可供下游使用。
- It should name what is unresolved, rejected, owner-gated, stale, or missing. / 应说明哪些内容 unresolved、rejected、owner-gated、stale 或 missing。
- It should preserve the nearest-responsible-stage route for later backflow. / 应保留后续回流所需的最近责任阶段路线。

## 10. Authority and Misuse Boundaries / 权威边界与误用防线

**中文边界：**

- 不编译 PDF
- 不声称 ready for export
- 不做 uncontrolled rewrite
- 有问题应流向 S14/S15

**English boundaries:**

- It does not compile PDF.
- It does not claim export readiness.
- It must not perform uncontrolled rewrite.
- Problems should route to S14/S15.

Specialist agents and scripts may return candidates or evidence; they never own completion authority. / 专家 agent 和脚本只能返回候选或证据，不能拥有完成权威。

## 11. Implementation Map / 实现索引

- Stage id(s) / 阶段 ID：`S12`
- Stage contract(s) / 阶段契约：
- [`examples/stage-contracts/S12.stage-contract.json`](../../examples/stage-contracts/S12.stage-contract.json)
- Stage registry / 阶段注册表：[`runtime/stage_registry.json`](../../runtime/stage_registry.json)
- Phase validators / Phase 验证配置：[`runtime/phase10_content_validators.json`](../../runtime/phase10_content_validators.json)
- Material schema / 物料 schema：[`schemas/ppg-material-payloads.schema.json`](../../schemas/ppg-material-payloads.schema.json)
- Material validator / 物料验证器：[`scripts/validate_material.py`](../../scripts/validate_material.py)
- Focused verifier / 聚焦验证器：[`scripts/verify_s12_integration_consistency.py`](../../scripts/verify_s12_integration_consistency.py)

## 12. Plain-Language Summary / 通俗总结

**中文。** S12 生成后续可审查的结构化集成候选稿。它不是 PDF 编译，也不是最终接受。 它的作用是把本环节的判断变成可检查、可回流、可被下游安全消费的结构化物料，而不是让后续 agent 依赖印象或自由发挥。

**EN.** S12 creates the machine-readable integrated candidate that later review can attack. It is not PDF compilation and not final acceptance. Its role is to turn this stage's judgments into structured, checkable, backflow-ready materials that downstream agents can consume safely instead of relying on impressions or free-form improvisation.
