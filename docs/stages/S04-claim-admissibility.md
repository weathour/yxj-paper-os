# S04 Claim Admissibility / 主张—证据准入

> Bilingual stage explainer for humans and controller agents. / 面向人类与主控 agent 的双语阶段说明。

## 1. Purpose / 目的

**EN.** S04 decomposes claim candidates, binds evidence anchors, assigns support strength, and derives allowed/forbidden wording boundaries.

**中文。** S04 拆解候选主张、绑定证据锚点、判定支持强度，并推导允许/禁止措辞边界。

**Contract purpose / 契约原文目的。** Admit, weaken, reject, or backflow every claim-bearing unit against evidence anchors, support strength, allowed wording, forbidden wording, and result-package boundaries.

## 2. Position in the Paper Production Graph / 在论文生产图中的位置

```text
S03/S01/S00 → S04 → S05/S07/S10/S12/S13
```

**EN.** S04 is the “can we say this?” gate. It turns ideas into admitted, weakened, rejected, or backflowed claim capsules.

**中文。** S04 是“这句话能不能说”的关口。它把想法变成 admitted、weakened、rejected 或 backflowed 的 claim capsule。

## 3. When the Controller Should Trigger This Stage / 主 agent 什么时候触发本环节

**中文触发条件：**

- 有贡献选项或写作意图但还没有证据准入判断时
- 结果、方法、novelty、安全性、泛化性说法需要边界时
- 后续正文或 caption 需要 allowed/forbidden wording 时

**English triggers:**

- Contribution options or writing intent exist but evidence admissibility is not decided.
- Method, novelty, result, safety, or generalization claims need boundaries.
- Later prose or captions need allowed/forbidden wording.

## 4. Inputs and Preconditions / 输入与前置条件

**Declared consumes / 契约声明输入：**

- `evidence bank`
- `citation bank`
- `result artifacts`
- `contribution options`

**What this stage analyzes or designs / 本环节具体分析或设计：**

**中文：**

- claim-bearing unit
- atomic claim 类型
- 证据锚点与 locator
- support strength、allowed wording、forbidden wording、downstream permission

**English:**

- Claim-bearing units.
- Atomic claim types.
- Evidence anchors and locators.
- Support strength, allowed wording, forbidden wording, and downstream permission.

If an input is missing, the controller should return to the nearest responsible upstream stage instead of letting the worker guess. / 如果输入缺失，主 agent 应回到最近责任上游环节，而不是让 worker 猜。

## 5. Task Packet or Controller Package / 任务包或主控包

- `S04` requires a strict worker task packet / `S04` 需要严格 worker 任务包: `examples/packets/phase10_s04_evidence_claim_admissibility_packet.v1.yaml`.

**Packet/material contract files / 任务包或控制包文件：**

- [`examples/packets/phase10_s04_evidence_claim_admissibility_packet.v1.yaml`](../../examples/packets/phase10_s04_evidence_claim_admissibility_packet.v1.yaml)

The packet is not a prompt template for free generation. It is a bounded contract that fixes allowed inputs, allowed paths, forbidden routes, output schema, validators, and the no-completion authority boundary. / 任务包不是自由生成提示词，而是限定输入、路径、禁止路线、输出 schema、validator 和无完成权威边界的契约。

## 6. Execution Sequence / 执行顺序

**中文执行顺序：**

- claim-bearing unit extraction
- atomic claim decomposition
- evidence anchor lookup
- support-strength classification
- wording boundary derivation
- result-package boundary pass
- downstream handoff/backflow pass
- independent verifier pass

**English execution sequence:**

- Claim-bearing unit extraction.
- Atomic claim decomposition.
- Evidence-anchor lookup.
- Support-strength classification.
- Wording-boundary derivation.
- Result-package boundary pass.
- Downstream handoff/backflow pass.
- Independent verifier pass.

The controller may dispatch a producer and verifier lane when the contract requires worker evidence, but only the controller commits graph state. / 当契约要求 worker 证据时，主控可分派 producer 和 verifier，但只有主控能提交图状态。

## 7. Output Material / 输出物料

**Declared produces / 契约声明输出：**

- `claim citation capsules`
- `result packages`
- `claim evidence visibility`
- `data availability plan`

**Positive material fixtures / 正例物料样例：**

- [`examples/materials/phase10_s04_claim_admissibility.yaml`](../../examples/materials/phase10_s04_claim_admissibility.yaml)

**Payload modules / payload 模块：**

- `schema_version`
- `stage_id`
- `completion_boundary`
- `claim_queue`
- `claim_unit_decomposition`
- `atomic_claim_register`
- `claim_capsules`
- `support_strength_map`
- `evidence_anchor_map`
- `allowed_wording_map`
- `forbidden_wording_map`
- `result_package_boundary_matrix`
- `claim_transformation_log`
- `data_availability_plan`
- `downstream_handoffs`
- `claim_coverage_ledger`
- `unsupported_claim_backflow_register`
- `evidence_locator_coverage`
- `downstream_use_permission_matrix`
- `unresolved_backflow_register`
- `candidate_return`

These fields are meant to be checked, consumed, and backflowed as structured graph materials rather than copied as prose. / 这些字段应作为结构化图物料被检查、消费和回流，而不是被复制成散文。

## 8. Validators and Failure Modes / Validator 与失败模式

**Validators / 验证器：**

- `S04_claim_queue`
- `S04_atomic_claim_register`
- `S04_claim_capsules`
- `S04_claim_coverage_ledger`
- `S04_support_strength_map`
- `S04_evidence_anchor_visibility`
- `S04_allowed_forbidden_wording`
- `S04_result_package_boundary`
- `S04_claim_transformation_log`
- `S04_downstream_handoff_coverage`
- `S04_no_final_prose_or_completion_overclaim`

**Negative fixtures cover / 负例覆盖：**

- `examples/materials/invalid-s04-claim-admissibility-completion-overclaim.yaml`
- `examples/materials/invalid-s04-claim-admissibility-final-prose.yaml`
- `examples/materials/invalid-s04-claim-admissibility-invalid-support-strength.yaml`
- `examples/materials/invalid-s04-claim-admissibility-missing-allowed-wording.yaml`
- `examples/materials/invalid-s04-claim-admissibility-missing-claim-queue.yaml`
- `examples/materials/invalid-s04-claim-admissibility-missing-coverage-ledger.yaml`
- `examples/materials/invalid-s04-claim-admissibility-missing-data-availability.yaml`
- `examples/materials/invalid-s04-claim-admissibility-missing-downstream-handoff.yaml`
- `examples/materials/invalid-s04-claim-admissibility-missing-downstream-permission.yaml`
- `examples/materials/invalid-s04-claim-admissibility-missing-evidence-anchor.yaml`
- `examples/materials/invalid-s04-claim-admissibility-missing-forbidden-wording.yaml`
- `examples/materials/invalid-s04-claim-admissibility-missing-result-boundary.yaml`
- `examples/materials/invalid-s04-claim-admissibility-missing-transformation-log.yaml`
- `examples/materials/invalid-s04-claim-admissibility-missing-unresolved-backflow.yaml`
- `examples/materials/invalid-s04-claim-admissibility-unsupported-admitted.yaml`

Run the focused verifier / 运行聚焦验证器：

```bash
python3 scripts/verify_s04_claim_admissibility.py
```

## 9. Downstream Handoffs / 下游交接

The output is only useful when downstream stages can consume it with traceable references. / 输出只有在下游能以可追踪引用消费时才有意义。

- It should name what is ready for downstream use. / 应说明哪些内容可供下游使用。
- It should name what is unresolved, rejected, owner-gated, stale, or missing. / 应说明哪些内容 unresolved、rejected、owner-gated、stale 或 missing。
- It should preserve the nearest-responsible-stage route for later backflow. / 应保留后续回流所需的最近责任阶段路线。

## 10. Authority and Misuse Boundaries / 权威边界与误用防线

**中文边界：**

- 不能输出最终正文
- 不能允许 unsupported claim 进入下游
- 不能把 support strength 夸大

**English boundaries:**

- It must not output final prose.
- It must not allow unsupported claims downstream.
- It must not inflate support strength.

Specialist agents and scripts may return candidates or evidence; they never own completion authority. / 专家 agent 和脚本只能返回候选或证据，不能拥有完成权威。

## 11. Implementation Map / 实现索引

- Stage id(s) / 阶段 ID：`S04`
- Stage contract(s) / 阶段契约：
- [`examples/stage-contracts/S04.stage-contract.json`](../../examples/stage-contracts/S04.stage-contract.json)
- Stage registry / 阶段注册表：[`runtime/stage_registry.json`](../../runtime/stage_registry.json)
- Phase validators / Phase 验证配置：[`runtime/phase10_content_validators.json`](../../runtime/phase10_content_validators.json)
- Material schema / 物料 schema：[`schemas/ppg-material-payloads.schema.json`](../../schemas/ppg-material-payloads.schema.json)
- Material validator / 物料验证器：[`scripts/validate_material.py`](../../scripts/validate_material.py)
- Focused verifier / 聚焦验证器：[`scripts/verify_s04_claim_admissibility.py`](../../scripts/verify_s04_claim_admissibility.py)

## 12. Plain-Language Summary / 通俗总结

**中文。** S04 是“这句话能不能说”的关口。它把想法变成 admitted、weakened、rejected 或 backflowed 的 claim capsule。 它的作用是把本环节的判断变成可检查、可回流、可被下游安全消费的结构化物料，而不是让后续 agent 依赖印象或自由发挥。

**EN.** S04 is the “can we say this?” gate. It turns ideas into admitted, weakened, rejected, or backflowed claim capsules. Its role is to turn this stage's judgments into structured, checkable, backflow-ready materials that downstream agents can consume safely instead of relying on impressions or free-form improvisation.
