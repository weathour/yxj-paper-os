# S13 Adversarial Review Report / 对抗性稿件审查报告

> Bilingual stage explainer for humans and controller agents. / 面向人类与主控 agent 的双语阶段说明。

## 1. Purpose / 目的

**EN.** S13 reviews the structured S12 candidate adversarially and returns actionable findings with severity, evidence, location, and nearest-stage routing.

**中文。** S13 对结构化 S12 候选稿做对抗性审查，返回带严重度、证据、位置和最近责任阶段路由的 actionable findings。

**Contract purpose / 契约原文目的。** Compile actionable adversarial loss signals over the structured S12 integrated candidate; do not rewrite, repair, review PDF as primary object, or claim completion.

## 2. Position in the Paper Production Graph / 在论文生产图中的位置

```text
S12 → S13 → S14/S15
```

**EN.** S13 is a critic, not a rewriter. It attacks the candidate so the controller can repair the right upstream material.

**中文。** S13 是批评者，不是改写者。它攻击候选稿，让主 agent 能修正确的上游物料。

## 3. When the Controller Should Trigger This Stage / 主 agent 什么时候触发本环节

**中文触发条件：**

- S12 integrated candidate 已存在且需要审查时
- 需要 desk reject、reader experience、claim/evidence、figure/caption 等损失信号时
- 需要 actionable finding 而不是全文重写时

**English triggers:**

- An S12 integrated candidate exists and needs review.
- Desk-reject, reader-experience, claim/evidence, or figure/caption loss signals are needed.
- Actionable findings are needed rather than whole-paper rewriting.

## 4. Inputs and Preconditions / 输入与前置条件

**Declared consumes / 契约声明输入：**

- `structured S12 integrated candidate package`
- `S12 trace and validator reports`
- `S10/S11 candidate traces`
- `S04-S08 upstream control materials`

**What this stage analyzes or designs / 本环节具体分析或设计：**

**中文：**

- review scope and object inventory
- reviewer panel report
- desk reject risk
- reader experience
- claim/evidence review
- figure/caption review
- review findings and actionability

**English:**

- Review scope and object inventory.
- Reviewer panel report.
- Desk-reject risk.
- Reader experience.
- Claim/evidence review.
- Figure/caption review.
- Review findings and actionability.

If an input is missing, the controller should return to the nearest responsible upstream stage instead of letting the worker guess. / 如果输入缺失，主 agent 应回到最近责任上游环节，而不是让 worker 猜。

## 5. Task Packet or Controller Package / 任务包或主控包

- `S13` requires a strict worker task packet / `S13` 需要严格 worker 任务包: `examples/packets/phase10_s13_adversarial_review_packet.v1.yaml`.

**Packet/material contract files / 任务包或控制包文件：**

- [`examples/packets/phase10_s13_adversarial_review_packet.v1.yaml`](../../examples/packets/phase10_s13_adversarial_review_packet.v1.yaml)

The packet is not a prompt template for free generation. It is a bounded contract that fixes allowed inputs, allowed paths, forbidden routes, output schema, validators, and the no-completion authority boundary. / 任务包不是自由生成提示词，而是限定输入、路径、禁止路线、输出 schema、validator 和无完成权威边界的契约。

## 6. Execution Sequence / 执行顺序

**中文执行顺序：**

- 确认 review object 是 S12 structured candidate
- 建立 reviewer panel
- 执行 desk reject 和 reader-experience scan
- 逐项检查 claim/evidence 和 figure/caption
- 记录 finding severity/evidence/location
- 路由 nearest responsible stage
- 输出 actionability report

**English execution sequence:**

- Confirm that the review object is the S12 structured candidate.
- Build reviewer panel.
- Run desk-reject and reader-experience scans.
- Check claims/evidence and figures/captions.
- Record finding severity, evidence, and location.
- Route nearest responsible stage.
- Output actionability report.

The controller may dispatch a producer and verifier lane when the contract requires worker evidence, but only the controller commits graph state. / 当契约要求 worker 证据时，主控可分派 producer 和 verifier，但只有主控能提交图状态。

## 7. Output Material / 输出物料

**Declared produces / 契约声明输出：**

- `adversarial review report`
- `severity-ranked review findings`
- `finding actionability report`
- `validator report`

**Positive material fixtures / 正例物料样例：**

- [`examples/materials/phase10_s13_adversarial_review_report.json`](../../examples/materials/phase10_s13_adversarial_review_report.json)

**Payload modules / payload 模块：**

- `schema_version`
- `stage_id`
- `completion_boundary`
- `authority_boundary`
- `review_scope`
- `review_object_inventory`
- `reviewer_panel_report`
- `desk_reject_risk_report`
- `reader_experience_report`
- `claim_evidence_review`
- `contribution_significance_review`
- `method_result_review`
- `figure_caption_review`
- `structure_argument_review`
- `surface_accessibility_review`
- `review_findings`
- `finding_actionability_report`
- `validator_report`
- `candidate_artifact_return`
- `verifier_evidence`
- `remaining_risks`

These fields are meant to be checked, consumed, and backflowed as structured graph materials rather than copied as prose. / 这些字段应作为结构化图物料被检查、消费和回流，而不是被复制成散文。

## 8. Validators and Failure Modes / Validator 与失败模式

**Validators / 验证器：**

- `S13_review_object_inventory`
- `S13_review_scope`
- `S13_reviewer_panel_report`
- `S13_desk_reject_risk_report`
- `S13_reader_experience_report`
- `S13_claim_evidence_review`
- `S13_figure_caption_review`
- `S13_review_findings_schema`
- `S13_finding_actionability`
- `S13_backflow_target_validity`
- `S13_no_uncontrolled_rewrite`
- `S13_no_pdf_primary_review`
- `S13_candidate_return_complete`
- `S13_verifier_evidence`

**Negative fixtures cover / 负例覆盖：**

- `examples/materials/invalid-s13-adversarial-review-actionability-missing-ready.json`
- `examples/materials/invalid-s13-adversarial-review-bad-candidate-return.json`
- `examples/materials/invalid-s13-adversarial-review-bypasses-s14.json`
- `examples/materials/invalid-s13-adversarial-review-completion-overclaim.json`
- `examples/materials/invalid-s13-adversarial-review-finding-missing-evidence.json`
- `examples/materials/invalid-s13-adversarial-review-finding-missing-location.json`
- `examples/materials/invalid-s13-adversarial-review-invalid-nearest-stage.json`
- `examples/materials/invalid-s13-adversarial-review-invalid-severity.json`
- `examples/materials/invalid-s13-adversarial-review-missing-object-inventory.json`
- `examples/materials/invalid-s13-adversarial-review-missing-review-mode.json`
- `examples/materials/invalid-s13-adversarial-review-missing-reviewer-role.json`
- `examples/materials/invalid-s13-adversarial-review-missing-verifier-check.json`
- `examples/materials/invalid-s13-adversarial-review-pdf-primary.json`
- `examples/materials/invalid-s13-adversarial-review-pdf-reviewed.json`
- `examples/materials/invalid-s13-adversarial-review-rewrite-performed.json`
- `examples/materials/invalid-s13-adversarial-review-uncontrolled-rewrite-scope.json`

Run the focused verifier / 运行聚焦验证器：

```bash
python3 scripts/verify_s13_adversarial_review_report.py
```

## 9. Downstream Handoffs / 下游交接

The output is only useful when downstream stages can consume it with traceable references. / 输出只有在下游能以可追踪引用消费时才有意义。

- It should name what is ready for downstream use. / 应说明哪些内容可供下游使用。
- It should name what is unresolved, rejected, owner-gated, stale, or missing. / 应说明哪些内容 unresolved、rejected、owner-gated、stale 或 missing。
- It should preserve the nearest-responsible-stage route for later backflow. / 应保留后续回流所需的最近责任阶段路线。

## 10. Authority and Misuse Boundaries / 权威边界与误用防线

**中文边界：**

- 不审 PDF 作为 primary object
- 不改写全文
- 不直接执行 repair
- 不能绕过 S14 路由

**English boundaries:**

- It does not review PDF as the primary object.
- It does not rewrite the paper.
- It does not execute repair.
- It must not bypass S14 routing.

Specialist agents and scripts may return candidates or evidence; they never own completion authority. / 专家 agent 和脚本只能返回候选或证据，不能拥有完成权威。

## 11. Implementation Map / 实现索引

- Stage id(s) / 阶段 ID：`S13`
- Stage contract(s) / 阶段契约：
- [`examples/stage-contracts/S13.stage-contract.json`](../../examples/stage-contracts/S13.stage-contract.json)
- Stage registry / 阶段注册表：[`runtime/stage_registry.json`](../../runtime/stage_registry.json)
- Phase validators / Phase 验证配置：[`runtime/phase10_content_validators.json`](../../runtime/phase10_content_validators.json)
- Material schema / 物料 schema：[`schemas/ppg-material-payloads.schema.json`](../../schemas/ppg-material-payloads.schema.json)
- Material validator / 物料验证器：[`scripts/validate_material.py`](../../scripts/validate_material.py)
- Focused verifier / 聚焦验证器：[`scripts/verify_s13_adversarial_review_report.py`](../../scripts/verify_s13_adversarial_review_report.py)

## 12. Plain-Language Summary / 通俗总结

**中文。** S13 是批评者，不是改写者。它攻击候选稿，让主 agent 能修正确的上游物料。 它的作用是把本环节的判断变成可检查、可回流、可被下游安全消费的结构化物料，而不是让后续 agent 依赖印象或自由发挥。

**EN.** S13 is a critic, not a rewriter. It attacks the candidate so the controller can repair the right upstream material. Its role is to turn this stage's judgments into structured, checkable, backflow-ready materials that downstream agents can consume safely instead of relying on impressions or free-form improvisation.
