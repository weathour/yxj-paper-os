---
title: "Target Global Delivery Contract Design"
tags: ["yxj-paper-os", "delivery-target", "s16", "design"]
created: 2026-07-02T16:46:35.221Z
updated: 2026-07-02T16:46:35.221Z
sources: []
links: []
category: decision
confidence: medium
schemaVersion: 1
---

# Target Global Delivery Contract Design

# Target Global Delivery Contract Design

## 决策

为 yxj-paper-os 增加 target-global delivery contract。Stage validator 仍负责本阶段结构与权限边界；delivery contract 负责回答“本次运行目标是否允许这种终态”。

## delivery_target.kind

- `template_only_handoff`: 允许模板/构建卫生 handoff；必须明确不是初稿 PDF。
- `compiled_initial_draft`: 初稿 PDF 目标；不允许 template-only，不允许 `content_ready=blocked`。
- `revised_compiled_pdf`: 修订后 PDF 目标；同样不允许 blocked/template-only。
- `materials_only`: 只生成材料/任务包；不得声称 PDF 目标达成。

## 编译稿目标的必须字段

当 `kind in {compiled_initial_draft, revised_compiled_pdf}`：

- `requires_content_bearing_pdf = true`
- `requires_source_writeback = true`
- `allows_template_only_handoff = false`
- `allows_candidate_only_completion = false`
- `requires_post_writeback_s12 = true`
- `requires_final_s16_content_ready_pass = true`
- `readiness_state_separation.content_ready/build_ready/render_clean/repository_clean/handoff_ready = pass`
- `rendered_surface_check.placeholder_text_absent = true`
- `rendered_surface_check.manuscript_not_started_absent = true`
- `rendered_surface_check.body_paragraphs_present = true`
- `rendered_surface_check.actual_bibliography_rendered = true`，除非有显式 owner/deferred reason 且目标允许。

## 失败回流

若 S16 目标门失败，不能把 S16 失败直接当作“结束”。Controller 应生成补充包：

1. 定位 blocker：source_writeback 缺失、S12 post-writeback 缺失、S15 repair 未真正应用、PDF semantic evidence 缺失等。
2. 归因到最近负责 stage。
3. 形成 backflow/repair task packet。
4. 从归因 stage 重新流向 S16：例如 S15 -> S12(post_writeback_source) -> S13(optional post-writeback review) -> S16(live_export)。

## 与 OMX/YXJ paper auto 的关系

`yxj-paper-os` 作为 standalone graph runtime，不依赖 OMX；OMX/yxj-paper-auto 可以读取这些字段作为个人调度适配器。个人工作流若目标是“初稿 PDF”，必须以 delivery contract 而不是单一 stage-local `VALID` 作为终局依据。
