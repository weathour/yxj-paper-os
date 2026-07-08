# yxj-paper-os 分支理念

状态：当前分支设计文档
分支：`yxj-paper-os-slot-skill-redesign`
记录日期：2026-07-04

## 1. 为什么清空重建

本分支面向交通、计算机、AI 论文的前置写作规划。医学、临床和 medical-AI 专用路线不作为默认目标。

旧版 `yxj-paper-os` 试图把论文生产管理为完整 runtime：阶段注册、物料图、任务包、候选输出、验证器、回流、修复、导出和复盘全部内建。这个设计完整但过重，实际会带来三类问题：

1. 用户和 Codex 都要理解太多内部状态。
2. 阶段、validator、worker 输出容易漂移。
3. 真正需要的常常只是把已有目标、材料、证据和 claim 边界整理成可交给写作模块的设计包。

因此当前分支的原则是：

```text
保留上游判断力，删除生产 runtime。
```

## 2. 一句话定义

`yxj-paper-os` 是一个 Codex 原生 paper-planning plugin。

它不直接写论文，而是像填表一样引导用户补齐信息，生成：

```text
04_WRITING_DESIGN_PACK.md
```

然后由外部写作、图件、引用、润色或审稿模块读取这个 design pack。

## 3. MVP 架构

```text
Single Skill, Five Internal Playbooks, Six Workspace Files
```

公开 skill 只有一个：

```text
skills/yxj-paper-os/SKILL.md
```

内部 playbook 只有五个：

```text
skills/yxj-paper-os/references/
  00-project-route.md
  01-materials-inventory.md
  02-claim-evidence-boundary.md
  03-writing-structure.md
  04-design-pack-compiler.md
```

对应用户项目中的六个 Markdown 文件：

```text
paper_project/
  00_DIMENSION_INDEX.md
  00_PROJECT_ROUTE.md
  01_MATERIALS_INVENTORY.md
  02_CLAIM_EVIDENCE_BOUNDARY.md
  03_WRITING_STRUCTURE.md
  04_WRITING_DESIGN_PACK.md
```

这个结构是当前公共契约：二十个信息维度以 `D00-D19` 行收敛在 `00_DIMENSION_INDEX.md` 中，实际内容仍写入五个内容文件。不要把退役的多文件/阶段 runtime 或多 public skill 体系作为 MVP 用户界面。

## 4. 真正需要的是什么

按照奥卡姆剃刀，第一版只需要三件事：

1. **知道要问什么。** 通过内部 playbooks 规定必填维度。
2. **知道什么时候不能继续。** 缺硬阻塞信息时停止生成 design pack，并让 Codex 继续追问。
3. **知道如何交接。** 把已补齐的信息整理成 `04_WRITING_DESIGN_PACK.md`。

下一层交互契约仍然保持这个简化原则：

```text
D00-D19 rubric → question card → user answer → workspace write → index update → compile gate
```

用户看到的是五个阶段：

```text
Route → Materials → Claim/Evidence → Writing Structure → Handoff
```

问题卡是交互格式，不是 runtime。若当前环境有 `omx question`，可以把同一张卡渲染成结构化选择题；若没有，就使用 Markdown 问题卡。两者写入同一组六文件，不引入 OMX 作为插件依赖。

不需要：

- runtime graph；
- stage registry；
- worker orchestration；
- large validator matrix；
- native citation search；
- manuscript drafting；
- external skill execution。

## 5. 六个硬阻塞项

生成 `04_WRITING_DESIGN_PACK.md` 前必须补齐：

| Blocker | 最低要求 |
|---|---|
| `project-route` | 目标期刊/会议/venue family、论文类型、主题、交通/计算机定位 |
| `core-materials` | 实验、结果、图表、数据、代码、baseline、metric 的位置或明确缺失说明 |
| `core-contribution` | 问题、对象、方法/系统/模型、一句话贡献 |
| `claim-evidence` | 每个核心 claim 的证据锚点、支持强度、禁止措辞边界 |
| `writing-structure` | reader spine、章节任务、图表故事线 |
| `external-route` | 推荐下游写作路线/skill 类别和 handoff 约束 |

缺任何一项时，Codex 应继续追问；不能输出带 TODO 的最终 design pack。

## 6. 原生责任边界

`yxj-paper-os` 原生负责：

- 项目路线判断；
- 材料和证据盘点；
- contribution 与 claim 边界；
- allowed / forbidden wording；
- reader spine 与写作结构；
- 下游 handoff 约束。

`yxj-paper-os` 不负责：

- 正文起草；
- 投稿级图件生成；
- 文献检索和 BibTeX 自动补全；
- reviewer simulation；
- LaTeX 模板适配和最终导出；
- 投稿、上传、发表、接收状态判断。

## 7. 外部仓库与 skill 的处理

当前参考仓库固定在 `references/external/`，只作为参考，不作为 runtime dependency。

已记录的参考方向包括：

| 仓库 / 项目 | 角色 |
|---|---|
| `nature-skills` | Nature 风格写作、润色、图件、引用、审稿流程参考 |
| `research-paper-writing-skills` | ML/CV/NLP/算法论文写作参考 |
| `academic-research-skills-codex` | Codex-native academic research/write/review workflow 参考 |
| `paperdebugger` | 编辑器/Overleaf 式审稿反馈参考 |
| `pantheonos` | 多智能体论文写作/图件团队设计参考 |

规则：

1. 不自动执行外部 skill。
2. 不把外部仓库 vendoring 进插件运行面。
3. 外部模块只能读取 `04_WRITING_DESIGN_PACK.md`。
4. 外部模块不能加强 claim、伪造 citation、绕过 limitation/risk 或声明投稿/发表完成。

## 8. 后续扩展规则

只有在 MVP 使用中反复证明某个内部 playbook 过大、过复杂、需要独立触发时，才把它拆成 public skill。

拆分前的默认答案始终是：

```text
保持一个 public skill。
```
