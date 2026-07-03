# S10 Candidate Text Return / 正文候选生成与返回

> Bilingual stage explainer for humans and controller agents. / 面向人类与主控 agent 的双语阶段说明。

## 1. Purpose / 目的

**EN.** S10 produces bounded main-text candidates from S09B packets with traceable claim, evidence, move, terminology, object, and visual-callout evidence.

**中文。** S10 根据 S09B 任务包生成受限正文候选，并返回 claim、evidence、move、terminology、object 和 visual callout 追踪证据。

**Contract purpose / 契约原文目的。** Produce packet-bounded, claim-safe candidate prose units from validated S09B task packets with traceable controls and mandatory verifier evidence.

## 2. Position in the Paper Production Graph / 在论文生产图中的位置

```text
S09B → S10 → S12/S13/S14
```

**EN.** S10 is the writing worker stage, but it is not free writing. It writes only within the packet and returns a candidate, not an accepted manuscript.

**中文。** S10 是写作 worker 环节，但不是自由写作。它只能按任务包写，并返回候选稿，不代表稿件已接受。

## 3. When the Controller Should Trigger This Stage / 主 agent 什么时候触发本环节

**中文触发条件：**

- S09B 已为某个正文单元编译严格任务包时
- 需要生成局部 main-text candidate 时
- 需要 worker evidence 和 verifier evidence 才能进入集成时

**English triggers:**

- S09B has compiled a strict packet for a text unit.
- A local main-text candidate is needed.
- Writer evidence and verifier evidence are required before integration.

## 4. Inputs and Preconditions / 输入与前置条件

**Declared consumes / 契约声明输入：**

- `S09B task packet`
- `construction matrix`
- `terminology register`
- `claim visibility`

**What this stage analyzes or designs / 本环节具体分析或设计：**

**中文：**

- packet compliance
- section/unit skeleton
- rhetorical moves
- claim-evidence trace
- terminology/object/visual callout trace
- forbidden expression scan

**English:**

- Packet compliance.
- Section/unit skeleton.
- Rhetorical moves.
- Claim-evidence trace.
- Terminology/object/visual-callout trace.
- Forbidden-expression scan.

If an input is missing, the controller should return to the nearest responsible upstream stage instead of letting the worker guess. / 如果输入缺失，主 agent 应回到最近责任上游环节，而不是让 worker 猜。

## 5. Task Packet or Controller Package / 任务包或主控包

- `S10` requires a strict worker task packet / `S10` 需要严格 worker 任务包: `examples/packets/phase10_s09b_s10_intro_callout_packet.v1.yaml`.

**Packet/material contract files / 任务包或控制包文件：**

- [`examples/packets/phase10_s09b_s10_intro_callout_packet.v1.yaml`](../../examples/packets/phase10_s09b_s10_intro_callout_packet.v1.yaml)

The packet is not a prompt template for free generation. It is a bounded contract that fixes allowed inputs, allowed paths, forbidden routes, output schema, validators, and the no-completion authority boundary. / 任务包不是自由生成提示词，而是限定输入、路径、禁止路线、输出 schema、validator 和无完成权威边界的契约。

## 6. Execution Sequence / 执行顺序

**中文执行顺序：**

- ACK task packet
- 检查 allowed read/write 和 forbidden routes
- 按 move plan 生成候选文本
- 逐 claim 绑定 evidence trace
- 检查术语、对象颗粒度和 visual callout
- 运行 forbidden expression scan
- 返回 candidate artifact 和风险

**English execution sequence:**

- Acknowledge the TaskPacket.
- Check allowed reads/writes and forbidden routes.
- Generate candidate text according to the move plan.
- Bind each claim to evidence trace.
- Check terminology, object granularity, and visual callouts.
- Run forbidden-expression scan.
- Return candidate artifact and risks.

The controller may dispatch a producer and verifier lane when the contract requires worker evidence, but only the controller commits graph state. / 当契约要求 worker 证据时，主控可分派 producer 和 verifier，但只有主控能提交图状态。

## 7. Output Material / 输出物料

**Declared produces / 契约声明输出：**

- `candidate text unit`
- `CandidateArtifactReturn`

**Positive material fixtures / 正例物料样例：**

- [`examples/materials/phase10_s10_candidate_text_return.json`](../../examples/materials/phase10_s10_candidate_text_return.json)

**Payload modules / payload 模块：**

- `schema_version`
- `stage_id`
- `completion_boundary`
- `authority_boundary`
- `packet_compliance_report`
- `candidate_text_unit`
- `section_or_unit_skeleton`
- `move_trace`
- `claim_evidence_trace`
- `terminology_trace`
- `object_granularity_trace`
- `visual_callout_trace`
- `forbidden_expression_scan`
- `coverage_ledger`
- `candidate_artifact_return`
- `writer_execution_evidence`
- `verifier_evidence`
- `remaining_risks`
- `missing_material_report`

These fields are meant to be checked, consumed, and backflowed as structured graph materials rather than copied as prose. / 这些字段应作为结构化图物料被检查、消费和回流，而不是被复制成散文。

## 8. Validators and Failure Modes / Validator 与失败模式

**Validators / 验证器：**

- `S10_packet_compliance`
- `S10_candidate_text_schema`
- `S10_allowed_write_path`
- `S10_claim_evidence_trace`
- `S10_claim_boundary_preserved`
- `S10_no_new_claims`
- `S10_no_claim_strengthening`
- `S10_move_trace`
- `S10_terminology_trace`
- `S10_internal_id_leakage`
- `S10_object_granularity_trace`
- `S10_visual_callout_trace`
- `S10_forbidden_expression_scan`
- `S10_coverage_ledger`
- `S10_candidate_return_complete`
- `S10_writer_evidence`
- `S10_verifier_evidence`
- `S10_authority_boundary`

**Negative fixtures cover / 负例覆盖：**

- `examples/materials/invalid-s10-candidate-text-return-bad-candidate-return.json`
- `examples/materials/invalid-s10-candidate-text-return-blocked-missing-material.json`
- `examples/materials/invalid-s10-candidate-text-return-completion-overclaim.json`
- `examples/materials/invalid-s10-candidate-text-return-final-acceptance.json`
- `examples/materials/invalid-s10-candidate-text-return-forbidden-body.json`
- `examples/materials/invalid-s10-candidate-text-return-internal-id-leakage.json`
- `examples/materials/invalid-s10-candidate-text-return-missing-claim-trace.json`
- `examples/materials/invalid-s10-candidate-text-return-missing-packet-compliance.json`
- `examples/materials/invalid-s10-candidate-text-return-missing-verifier-evidence.json`
- `examples/materials/invalid-s10-candidate-text-return-missing-writer-evidence.json`
- `examples/materials/invalid-s10-candidate-text-return-object-granularity.json`
- `examples/materials/invalid-s10-candidate-text-return-scan-not-clean.json`
- `examples/materials/invalid-s10-candidate-text-return-unresolved-coverage.json`
- `examples/materials/invalid-s10-candidate-text-return-unsafe-write-path.json`
- `examples/materials/invalid-s10-candidate-text-return-visual-misuse.json`

Run the focused verifier / 运行聚焦验证器：

```bash
python3 scripts/verify_s10_candidate_text_return.py
```

## 9. Downstream Handoffs / 下游交接

The output is only useful when downstream stages can consume it with traceable references. / 输出只有在下游能以可追踪引用消费时才有意义。

- It should name what is ready for downstream use. / 应说明哪些内容可供下游使用。
- It should name what is unresolved, rejected, owner-gated, stale, or missing. / 应说明哪些内容 unresolved、rejected、owner-gated、stale 或 missing。
- It should preserve the nearest-responsible-stage route for later backflow. / 应保留后续回流所需的最近责任阶段路线。

## 10. Authority and Misuse Boundaries / 权威边界与误用防线

**中文边界：**

- 不能声称 graph/manuscript 完成
- 不能写出任务包外内容
- 不能新增/加强 claim
- 不能泄漏 internal ID 或越权写路径

**English boundaries:**

- It must not claim graph or manuscript completion.
- It must not write outside the packet.
- It must not add or strengthen claims.
- It must not leak internal IDs or write outside allowed paths.

Specialist agents and scripts may return candidates or evidence; they never own completion authority. / 专家 agent 和脚本只能返回候选或证据，不能拥有完成权威。

## 11. Implementation Map / 实现索引

- Stage id(s) / 阶段 ID：`S10`
- Stage contract(s) / 阶段契约：
- [`examples/stage-contracts/S10.stage-contract.json`](../../examples/stage-contracts/S10.stage-contract.json)
- Stage registry / 阶段注册表：[`runtime/stage_registry.json`](../../runtime/stage_registry.json)
- Phase validators / Phase 验证配置：[`runtime/phase10_content_validators.json`](../../runtime/phase10_content_validators.json)
- Material schema / 物料 schema：[`schemas/ppg-material-payloads.schema.json`](../../schemas/ppg-material-payloads.schema.json)
- Material validator / 物料验证器：[`scripts/validate_material.py`](../../scripts/validate_material.py)
  - S10 candidate returns must be validated with `--packet <S09B-emitted S10 TaskPacket>` so hydration/read receipts are checked against packet obligations.
- Focused verifier / 聚焦验证器：[`scripts/verify_s10_candidate_text_return.py`](../../scripts/verify_s10_candidate_text_return.py)

## 12. Plain-Language Summary / 通俗总结

**中文。** S10 是写作 worker 环节，但不是自由写作。它只能按任务包写，并返回候选稿，不代表稿件已接受。 它的作用是把本环节的判断变成可检查、可回流、可被下游安全消费的结构化物料，而不是让后续 agent 依赖印象或自由发挥。

**EN.** S10 is the writing worker stage, but it is not free writing. It writes only within the packet and returns a candidate, not an accepted manuscript. Its role is to turn this stage's judgments into structured, checkable, backflow-ready materials that downstream agents can consume safely instead of relying on impressions or free-form improvisation.

## 12. Material Hydration and Read-Receipt Gate / 物料水合与阅读回执门控

**EN.** S10 must hydrate the required material closure before drafting. A worker acknowledgement that it used `allowed_read_paths` is not sufficient. S10 must return structured evidence that every required current-authority material and selector was read or that drafting was blocked by a MissingMaterialReport.

**中文。** S10 在写作前必须先完成必需物料闭包的水合。仅声明使用了 `allowed_read_paths` 不足够。S10 必须返回结构化证据，证明每个必需的当前权威物料和 selector 已被读取，或者因缺失而以 MissingMaterialReport 阻断写作。

Canonical S10 modules / 标准模块：

```text
material_hydration_report
material_read_receipt_ledger
```

Required semantics / 必须语义：

- `material_hydration_report.status` is `pass` only when all required materials are hydrated and no blocking material is missing.
- `material_hydration_report.required_materials` must exactly match the S09B packet `material_read_obligations.required_materials`.
- `material_hydration_report.hydrated_materials` must exactly match the same set: no missing required material and no extra material outside the S09B packet obligations.
- `required_selectors_by_material` and `hydrated_selectors_by_material` must exactly match the S09B packet selector obligations.
- `material_read_receipt_ledger.receipts[]` records `material_ref`, `selectors_read`, `source_packet_obligation`, and `receipt_status: read`; receipt material refs must exactly match the S09B packet obligations and `missing_receipts` must be empty.
- If hydration or read receipts are blocked or diverge from packet obligations, S10 must not emit `candidate_text_unit.status: candidate`; it must return a MissingMaterialReport routed to the nearest responsible stage.

Blocked-output conflict rule / 阻断输出冲突规则：

```text
material_hydration_report.status != pass
OR missing_materials / missing_receipts non-empty
OR hydration/read-receipt materials or selectors diverge from S09B packet obligations
=> candidate_text_unit.status=candidate is invalid.
```
