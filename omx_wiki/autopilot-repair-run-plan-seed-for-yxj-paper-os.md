---
title: "Autopilot Repair Run Plan Seed for YXJ Paper OS"
tags: ["autopilot", "ralplan", "ultragoal", "yxj-paper-os"]
created: 2026-07-02T16:46:35.405Z
updated: 2026-07-02T16:46:35.405Z
sources: []
links: []
category: session-log
confidence: medium
schemaVersion: 1
---

# Autopilot Repair Run Plan Seed for YXJ Paper OS

# Autopilot Repair Run Plan Seed for YXJ Paper OS

## 目标

按 Autopilot 严格链执行：deep-interview gate → ralplan consensus → ultragoal implementation → code-review → ultraqa → final commit/push。

## deep-interview gate 处理

本任务边界已经由用户明确给出：修复 `$yxj-paper-os` 中所有暴露出的阶段验收/目标门问题，尤其是“凡是目标为初稿 PDF，不接受 `content_ready: blocked` 或 `template_only` 的 S16”。缺失的 ChatGPT share 原文已验证不可读取；不会阻止执行，因为当前对话和本地失败样本足以确定首轮修复范围。

## 里程碑

1. M0 文档化证据与问题地图，并提交。
2. M1 增加 target-global delivery contract 文档、schema/fixture 字段、registry/contract 声明，并提交。
3. M2 强化 S16 validator 与负向 fixtures：compiled target 下 blocked/template-only 不可通过，并提交。
4. M3 强化 live export semantic verifier：PDF 文本/placeholder/Manuscript Not Started 检查，并提交。
5. M4 将 S12/S15/S14 的 source-writeback/backflow 责任写入阶段文档/validator surfaces，并提交。
6. M5 全量验证、code-review、ultraqa、最终修补提交并推送 main。

## 成功停止条件

- 旧失败样本或等价 fixture 在 compiled target 下失败。
- template-only handoff 只能在显式 `template_only_handoff` 目标下被视为结构合格。
- 所有相关 verifier 与 fixture suite 通过。
- code-review final recommendation 为 APPROVE 且 architectural status CLEAR。
- ultraqa 通过或有明确适用性 skip evidence。
