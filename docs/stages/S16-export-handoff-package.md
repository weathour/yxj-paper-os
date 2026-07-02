# S16 Export and Handoff Package / 导出、仓库卫生与交接包

> Bilingual stage explainer for humans and controller agents. / 面向人类与主控 agent 的双语阶段说明。

## 1. Purpose / 目的

**EN.** S16 verifies upstream closure, build/readiness states, rendered surface, manifests, hashes, repository hygiene, handoff completeness, and feedback routes.

**中文。** S16 验证上游 closure、构建/就绪状态、渲染表面、manifest、hash、仓库卫生、交接完整性和反馈路线。

**Contract purpose / 契约原文目的。** Export a closed manuscript candidate into human-readable artifacts and prove delivery hygiene without claiming submission/publication readiness.

## 2. Position in the Paper Production Graph / 在论文生产图中的位置

```text
S12/S13/S14/S15 → S16 → owner review / feedback routing
```

**EN.** S16 makes the human-readable handoff clean. It can export and verify, but it still does not claim submission or publication readiness.

**中文。** S16 让人能看的交付物清洁可查。它可以导出和验证，但仍不能声称投稿或发表准备完成。

## 3. When the Controller Should Trigger This Stage / 主 agent 什么时候触发本环节

**中文触发条件：**

- S12 集成稿、S13 审查、S14/S15 修复闭环后需要导出时
- 需要 PDF/build/repository hygiene/hash manifest/handoff report 时
- 人类阅读 S16 输出后需要明确反馈回流路线时

**English triggers:**

- S12 candidate, S13 review, and S14/S15 repairs are closed and export is needed.
- PDF/build/repository hygiene/hash manifest/handoff report is needed.
- Human feedback after reading S16 output needs a route.

## 4. Inputs and Preconditions / 输入与前置条件

**Declared consumes / 契约声明输入：**

- `closed S12 integrated manuscript candidate`
- `S13 review closure evidence`
- `S14/S15 repair-complete status`
- `figures/captions/data availability bundle`
- `repository and build configuration state`

**What this stage analyzes or designs / 本环节具体分析或设计：**

**中文：**

- readiness state separation
- upstream closure check
- build/rendered surface
- export and file hash manifest
- figure/reference/data availability
- repository hygiene
- owner gate and feedback route

**English:**

- Readiness-state separation.
- Upstream-closure check.
- Build/rendered surface.
- Export and file-hash manifest.
- Figure/reference/data availability.
- Repository hygiene.
- Owner gate and feedback route.

If an input is missing, the controller should return to the nearest responsible upstream stage instead of letting the worker guess. / 如果输入缺失，主 agent 应回到最近责任上游环节，而不是让 worker 猜。

## 5. Task Packet or Controller Package / 任务包或主控包

- `S16` does not require a normal worker task packet / `S16` 不需要普通 worker 任务包 (`not_required`).

**Packet/material contract files / 任务包或控制包文件：**

- _Not applicable / 不适用_

The packet is not a prompt template for free generation. It is a bounded contract that fixes allowed inputs, allowed paths, forbidden routes, output schema, validators, and the no-completion authority boundary. / 任务包不是自由生成提示词，而是限定输入、路径、禁止路线、输出 schema、validator 和无完成权威边界的契约。

## 6. Execution Sequence / 执行顺序

**中文执行顺序：**

- 检查 S12/S13/S14/S15 closure
- 区分 content/build/render/repository/handoff/submission-gated 状态
- 运行 build/readiness/render checks
- 生成 export manifest 和 hash manifest
- 检查 figure/reference/data/supplement
- 分类 dirty worktree
- 生成 manager handoff 和 human feedback route

**English execution sequence:**

- Check S12/S13/S14/S15 closure.
- Separate content, build, render, repository, handoff, and submission-gated states.
- Run build/readiness/render checks.
- Produce export manifest and hash manifest.
- Check figures, references, data, and supplements.
- Classify dirty worktree.
- Produce manager handoff and human feedback route.

The controller may dispatch a producer and verifier lane when the contract requires worker evidence, but only the controller commits graph state. / 当契约要求 worker 证据时，主控可分派 producer 和 verifier，但只有主控能提交图状态。

## 7. Output Material / 输出物料

**Declared produces / 契约声明输出：**

- `export handoff package`
- `human-readable PDF/export manifest`
- `repository hygiene report`
- `manager/owner handoff report`

**Positive material fixtures / 正例物料样例：**

- [`examples/materials/phase10_s16_export_handoff_package.json`](../../examples/materials/phase10_s16_export_handoff_package.json)

**Payload modules / payload 模块：**

- `schema_version`
- `stage_id`
- `completion_boundary`
- `authority_boundary`
- `evidence_mode`
- `live_export_verification`
- `delivery_target`
- `readiness_state_separation`
- `upstream_closure_check`
- `build_readiness_check`
- `build_run_report`
- `rendered_surface_check`
- `export_manifest`
- `file_hash_manifest`
- `figure_file_checklist`
- `data_availability_statement_check`
- `supplement_manifest`
- `repository_hygiene_report`
- `manager_handoff_report`
- `owner_gate_report`
- `human_feedback_intake_route`
- `validator_report`
- `remaining_risks`

These fields are meant to be checked, consumed, and backflowed as structured graph materials rather than copied as prose. / 这些字段应作为结构化图物料被检查、消费和回流，而不是被复制成散文。


## Target delivery contract / 目标交付契约

S16 requires `payload.delivery_target`. A structurally valid export handoff is not automatically an initial/revised compiled PDF delivery. For `compiled_initial_draft` and `revised_compiled_pdf`, S16 must prove content-bearing PDF semantics, source-writeback evidence, post-writeback validation, and all critical readiness states `pass`; `content_ready: blocked`, template-only handoff, `Manuscript Not Started`, or placeholder-only evidence must fail and route back through S14/S15/S12/source-writeback as appropriate. See [`docs/TARGET_DELIVERY_CONTRACT.md`](../TARGET_DELIVERY_CONTRACT.md).

## 8. Validators and Failure Modes / Validator 与失败模式

**Validators / 验证器：**

- `S16_upstream_closure`
- `S16_readiness_state_separation`
- `S16_build_success`
- `S16_pdf_exists_and_surface`
- `S16_figures_captions_present`
- `S16_references_present`
- `S16_data_availability_alignment`
- `S16_export_manifest_hashes`
- `S16_dirty_worktree_classification`
- `S16_handoff_completeness`
- `S16_feedback_route_declared`
- `S16_projection_vs_live_export_boundary`
- `S16_template_only_handoff_boundary`
- `S16_pdf_semantic_surface`
- `S16_compiled_pdf_target_gate`
- `S16_delivery_target_binding`
- `S16_delivery_target_declared`
- `S16_no_submission_ready_overclaim`

**Negative fixtures cover / 负例覆盖：**

- `examples/materials/invalid-s16-export-handoff-authority-submitted.json`
- `examples/materials/invalid-s16-export-handoff-bad-readiness.json`
- `examples/materials/invalid-s16-export-handoff-build-failed.json`
- `examples/materials/invalid-s16-export-handoff-data-mismatch.json`
- `examples/materials/invalid-s16-export-handoff-feedback-misrouted.json`
- `examples/materials/invalid-s16-export-handoff-figure-failed.json`
- `examples/materials/invalid-s16-export-handoff-hash-mismatch.json`
- `examples/materials/invalid-s16-export-handoff-live-claimed-in-fixture.json`
- `examples/materials/invalid-s16-export-handoff-missing-handoff-manifest-entry.json`
- `examples/materials/invalid-s16-export-handoff-missing-hash.json`
- `examples/materials/invalid-s16-export-handoff-missing-human-output.json`
- `examples/materials/invalid-s16-export-handoff-missing-verifier-check.json`
- `examples/materials/invalid-s16-export-handoff-narrative-overclaim.json`
- `examples/materials/invalid-s16-export-handoff-negated-first-repeat-overclaim.json`
- `examples/materials/invalid-s16-export-handoff-owner-authorized.json`
- `examples/materials/invalid-s16-export-handoff-render-anomaly.json`
- `examples/materials/invalid-s16-export-handoff-submission-overclaim.json`
- `examples/materials/invalid-s16-export-handoff-unexpected-dirty.json`
- `examples/materials/invalid-s16-export-handoff-unrelated-negation-overclaim.json`
- `examples/materials/invalid-s16-export-handoff-unresolved-upstream.json`
- `examples/materials/invalid-s16-export-handoff-unsafe-export-path.json`

Run the focused verifier / 运行聚焦验证器：

```bash
python3 scripts/verify_s16_export_handoff_package.py
```

## 9. Downstream Handoffs / 下游交接

The output is only useful when downstream stages can consume it with traceable references. / 输出只有在下游能以可追踪引用消费时才有意义。

- It should name what is ready for downstream use. / 应说明哪些内容可供下游使用。
- It should name what is unresolved, rejected, owner-gated, stale, or missing. / 应说明哪些内容 unresolved、rejected、owner-gated、stale 或 missing。
- It should preserve the nearest-responsible-stage route for later backflow. / 应保留后续回流所需的最近责任阶段路线。

## 10. Authority and Misuse Boundaries / 权威边界与误用防线

**中文边界：**

- 不是投稿
- 不是 publication readiness claim
- 不能把 fixture projection 当成 live export proof
- 内容反馈应回 S14，导出卫生反馈才回 S16

**English boundaries:**

- It is not submission.
- It is not a publication-readiness claim.
- It must not treat fixture projection as live export proof.
- Content feedback routes to S14; export-hygiene feedback routes to S16.

Specialist agents and scripts may return candidates or evidence; they never own completion authority. / 专家 agent 和脚本只能返回候选或证据，不能拥有完成权威。

## 11. Implementation Map / 实现索引

- Stage id(s) / 阶段 ID：`S16`
- Stage contract(s) / 阶段契约：
- [`examples/stage-contracts/S16.stage-contract.json`](../../examples/stage-contracts/S16.stage-contract.json)
- Stage registry / 阶段注册表：[`runtime/stage_registry.json`](../../runtime/stage_registry.json)
- Phase validators / Phase 验证配置：[`runtime/phase10_content_validators.json`](../../runtime/phase10_content_validators.json)
- Material schema / 物料 schema：[`schemas/ppg-material-payloads.schema.json`](../../schemas/ppg-material-payloads.schema.json)
- Material validator / 物料验证器：[`scripts/validate_material.py`](../../scripts/validate_material.py)
- Focused verifier / 聚焦验证器：[`scripts/verify_s16_export_handoff_package.py`](../../scripts/verify_s16_export_handoff_package.py)

## 12. Plain-Language Summary / 通俗总结

**中文。** S16 让人能看的交付物清洁可查。它可以导出和验证，但仍不能声称投稿或发表准备完成。 它的作用是把本环节的判断变成可检查、可回流、可被下游安全消费的结构化物料，而不是让后续 agent 依赖印象或自由发挥。

**EN.** S16 makes the human-readable handoff clean. It can export and verify, but it still does not claim submission or publication readiness. Its role is to turn this stage's judgments into structured, checkable, backflow-ready materials that downstream agents can consume safely instead of relying on impressions or free-form improvisation.

## Failed compiled-target recovery loop

For `compiled_initial_draft` and `revised_compiled_pdf`, S16 failure is a routing signal, not a terminal handoff. The controller should preserve the failed package as evidence, create a finding with the deterministic error code, and route it as follows:

1. target missing/mismatch -> S00 or manager active-target authority, then regenerate S16;
2. missing source writeback -> S14 plan plus S15 source-writeback repair;
3. missing post-writeback validation -> S12 post-writeback integration consistency;
4. bad rendered/PDF text semantics -> S12/S13/S15 depending on whether the source, review, or export evidence is responsible;
5. export/hash/build-only hygiene -> S16 rerun.

Only after the repaired downstream flow reaches S16 with the same compiled `delivery_target` and all compiled gates passing may the controller claim an owner-readable compiled draft handoff.

### Rendered text sidecar boundary

For compiled targets, S16 consumes a rendered-text sidecar generated from the same output PDF by the build/export pipeline. The sidecar must be hash-listed and bound to `post_writeback_validation`; if it is absent, stale, generated from another PDF, or used to downcast an active compiled target to export hygiene, S16 fails and routes the finding back to the responsible writeback/integration/export step.
