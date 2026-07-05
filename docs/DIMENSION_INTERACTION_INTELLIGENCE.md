# Dimension Interaction Intelligence — D00-D19 深层理解与问题卡设计依据

状态：下一轮 `$ralplan` 前的研究/开发依据  
分支：`yxj-paper-os-slot-skill-redesign`  
记录日期：2026-07-05  
来源：五组 subagent 只读调研 + 当前仓库规则 + yxj-backend capsule-first 查询 + 外部权威写作/问卷/引用资料

## 0. 用途

本文不是新的 public workspace 文件，也不是新的 runtime 契约。它是后续开发用的**内部设计依据**：帮助 `yxj-paper-os` agent 更深地理解 D00-D19 每一维到底要问清什么、问到什么程度、如何给选项、如何更新六文件工作区、何时阻塞 `04_WRITING_DESIGN_PACK.md`。

后续 PRD 应把本文压缩落实到：

1. `SKILL.md` 的交互与判定规则；
2. 五个 internal playbooks 的问题卡模板；
3. `00-dimension-rubric.md` 的维度充分性说明；
4. 必要的模板说明文字；
5. 轻量结构检查器。

保持边界：不新增 public 文件、不新增 public skill、不改 `00_DIMENSION_INDEX.md` schema/status、不引入 runtime graph/stage/backflow/worker、不做语义评分器、不写正文、不搜引用、不执行外部 writing/citation skills。

---

## 1. 总体模型

### 1.1 认知层与交互层分离

```text
Dimension Rubric  →  Question Card  →  User Answer
      ↓                    ↓                ↓
Sufficiency Gate  →  Workspace Write →  Index Update → Compile Gate
```

- **Dimension Rubric 是认知层**：定义每一维的本质、minimum/standard/ideal、owner confirmation、agent proposal、常见误判、write target。
- **Question Card 是交互层**：把 rubric 的判断转成用户可回答的选项卡。
- **Compile Gate 是判定层**：判断是否可编译 `04_WRITING_DESIGN_PACK.md`。

问题卡不能替代维度理解。Agent 先根据 rubric 判断缺口，再选择问题卡类型。

### 1.2 用户面对五个阶段，不面对二十个文件

用户初始交互不应被 D00-D19 全量表格压倒。面向用户展示五个阶段：

| 用户阶段 | 内部维度 | 主要目标 |
|---|---|---|
| Route | D01, D03, D04 | 目标路线、主题、owner 禁区 |
| Materials | D05, D06, D07, D08 | 真实材料、证据锚点、来源边界、研究语境 |
| Claim / Evidence | D10, D11, D12, D13, claim-side D16/D17 | 贡献、claim、证据强度、措辞边界、风险 |
| Writing Structure | D09, D14, D15, primary D16/D17, D18 | 文体、reader spine、outline、对象粒度、视觉叙事 |
| Handoff | D00, D02, D19 | 工作区身份、新鲜度、最终 design pack |

D 编号保留在状态报告、写入证据、验证报告中。

### 1.3 交互模式

Agent 自动选择模式并说明理由。

| 模式 | 适用情况 | 输出方式 |
|---|---|---|
| `focused-question` | 一个 owner-gated 决策会决定后续分支 | 单个高杠杆问题，2-5 个选项 |
| `quick-form` | 空白工作区、多个低风险字段可一起收集 | 8-12 项短表单，不能隐藏重大分支 |
| `candidate-confirmation` | Agent 可根据已确认材料提出候选结构 | 给 2-3 个候选，用户确认/修改/拒绝 |
| `reconciliation` | 跨文件冲突，如 D16/D17 不一致 | 显示冲突，要求选择 authoritative version |
| `stale-alert` | D02 检测到上游变更 | 警报式问题卡：重编译/暂缓/owner 风险确认 |

### 1.4 `omx question` 可选适配

`yxj-paper-os` 保持 standalone：公共默认是 Markdown 问题卡。若当前环境存在 `omx question` 或等价结构化问答 UI，agent 可把同一张卡渲染为结构化选择题。

公共语义：

```text
Question Card = canonical semantic layer
omx question = optional renderer
Markdown card = fallback renderer
```

推荐 canonical 字段：

```yaml
id: Dxx-card-name
dimension: Dxx
title: short title
purpose: why this question is needed
mode: focused-question | quick-form | candidate-confirmation | reconciliation | stale-alert
question: user-facing question
options:
  - label: A
    value: stable-value
    consequence: what will be written / blocked / deferred
allow_other: true|false
write_target: file#section
index_update: Dxx status/reason/pointer expectation
if_unanswered: defer/absent/rejected consequence
```

OMX 映射：

- 单一决策：`type: "single-answerable"`
- 多个同时成立的约束/缺项：`type: "multi-answerable"`
- 精确路径/名称：Markdown 中给输入槽；若 UI 支持 text input，可映射为文本输入。

Markdown fallback 示例：

```md
### 问题卡：D16 对象粒度

为什么问：需要确认研究对象边界，避免 claim 漂移。

请选择一个：
A. method — 后续 claim 以方法贡献为主
B. system — 后续 claim 以系统/架构为主
C. model — 后续 claim 以模型能力为主
D. dataset / benchmark — 后续 claim 以数据或评测贡献为主
E. application / analysis object — 后续 claim 以应用/分析对象为主
F. deferred — 可以继续整理材料，但 final design pack 前需确认

回答后我会更新：03_WRITING_STRUCTURE.md#Object Granularity 与 D16 行。
```

---

## 2. 编译判定总表

| 条件 | 判定 |
|---|---|
| D00-D19 有缺行 | block：修复 `00_DIMENSION_INDEX.md` |
| status 非 `filled/not_applicable/absent/deferred/rejected` | block |
| reason/pointer/handoff 是 TODO/TBD/UNKNOWN/REPLACE_ME | block |
| 非 critical 维度达到 minimum，且有明确 reason/handoff | 可通过该维度 |
| critical-standard 维度只有 minimum | 继续问；不得编译 final design pack |
| owner-gated 事实/路线/claim/evidence/source/forbidden wording 未确认 | 只能 candidate/deferred；不得标 standard |
| agent-designable structure 基于已确认材料且有 rationale | 可提议；可在确认边界内达到 standard |
| D16/D17 主写入与 claim-side 内容冲突 | block：进入 reconciliation card |
| D04 route deferred | 可继续上游整理；final pack 前必须 owner 确认 venue family / paper type / audience expectation，或明确接受 final-route deferral 的后果 |
| D18 无图表 | 可通过 only if 有明确 no-visual rationale、替代 storyline、claim 不依赖视觉证据 |
| D19 final pack 有 TODO/TBD/UNKNOWN/REPLACE_ME | invalid |
| 外部 writing/citation skill 尚未执行 | 不阻塞；yxj-paper-os 只 handoff，不执行 |

Critical-standard 精确集合：

```text
D04,D05,D06,D10,D11,D12,D13,D14,D15,D16,D17,D18
```

`Blocks design pack?` 的语义必须保持原样：

```text
Blocks design pack? = yes
```

表示“该维度若未处理就是 readiness-critical”，不表示“该维度在有效处理后仍然当前阻塞”。不要改列名，不要新增 `currently_blocking`、`tier` 或其他 public schema 字段；如需表达当前状态，只能通过 `Status`、`Reason / owner note`、`Pointer or handoff` 和 readiness note 说明。

---

## 3. D00-D19 维度理解与问题卡设计

### D00 — Workspace metadata / `00_META.md`

**本质**：工作区身份与就绪度元数据。它回答“我正在操作哪个项目状态”，不是论文内容。

**用户要搞明白**：项目 slug/名字、更新时间、当前 readiness、最近一次 design pack 后是否有影响内容的变更。

| 档次 | 具体形态 |
|---|---|
| minimum | slug/date/readiness 可识别或可从工作区安全推断 |
| standard | 元数据足够 handoff；项目身份或 route 歧义已解决或明确 deferred |
| ideal | 有 run/date/provenance 说明，记录重大 intake 变化 |

**Agent 可提议**：规范化 slug、日期、readiness 摘要。  
**必须用户确认**：项目身份歧义、owner 决策影响身份时。

**问题卡**：metadata confirmation card。

选项形态：确认当前身份 / 改名 / 暂缓确认 / 指定 changed materials。

**常见误判**：把旧 metadata 当当前状态；编造 owner identity；看到项目名就假设内容已同步。

**写入**：`00_DIMENSION_INDEX.md#Workspace Metadata`。  
**handoff**：只作为项目身份和 validation note，不作为 paper claim。

---

### D01 — Owner decisions / `OWNER_DECISIONS.md`

**本质**：owner-gated 决策与禁区登记簿。它记录哪些 route/claim/citation/handoff 不能由 agent 擅自推断。

**用户要搞明白**：哪些决策必须由 owner 定；哪些路线看似诱人但必须排除；哪些决定影响后续 claim/evidence/handoff。

| 档次 | 具体形态 |
|---|---|
| minimum | 至少一个 owner decision，或明确“无特殊 owner gate” |
| standard | 与 route/claim/evidence/handoff 相关的 owner-gated choices 和 forbidden routes 明确 |
| ideal | 有 rationale 和 tempting-but-rejected examples |

**Agent 可提议**：候选决策类别，如 venue route、contribution type、claim strength、citation boundary、downstream route。  
**必须用户确认**：所有最终 owner decision。

**问题卡**：owner decision gate card。

选项形态：route gate / claim gate / citation gate / downstream gate / no special gate / deferred。

**常见误判**：把 agent 推荐当 owner 决策；不记录 forbidden routes；默认填未确认决策。

**写入**：`00_PROJECT_ROUTE.md#Owner Decisions` + `00_DIMENSION_INDEX.md#Owner Notes`。  
**handoff**：下游必须保留，不得润色掉。

---

### D02 — Stale flags / `STALE_FLAGS.md`

**本质**：design pack 新鲜度与过期门闸。它回答上游内容变更后，现有 design pack 是否仍可用。

**用户要搞明白**：哪些维度在上次 pack 后变了；是否需要 recompile；是否 owner 决定暂时忽略 stale risk。

| 档次 | 具体形态 |
|---|---|
| minimum | stale/readiness 状态显式存在，即使是 `not assessed yet` |
| standard | 变更维度和 required recompile/handoff action 被点名 |
| ideal | 有 stale-dependency note，说明材料/claim/structure 联动 |

**Agent 可提议**：根据本地文件改动推断 stale flags。  
**必须用户确认**：是否忽略 stale flag。

**问题卡**：stale alert / recompile decision card。

选项形态：recompile now / continue intake but block handoff / owner accepts risk / mark deferred。

**常见误判**：继续使用旧 pack；只看时间戳；忽略 upstream critical changes。

**写入**：`00_DIMENSION_INDEX.md#Readiness Gate`。  
**handoff**：stale 未解时下游写作应暂停。

---

### D03 — Project brief / `00_project_brief.md`

**本质**：项目简报。它说明项目 topic、domain positioning、research object、working thesis。不是摘要，不是 contribution 宣传语。

**用户要搞明白**：项目在交通/计算机/AI 中的位置；研究对象；工作性 thesis；为什么属于该路线。

| 档次 | 具体形态 |
|---|---|
| minimum | 一句话 topic/project brief |
| standard | brief 含 domain positioning、research object、working thesis，且不 hype |
| ideal | 补充为何适合当前交通/计算机/AI route |

**Agent 可提议**：2-3 个 brief normalization 候选。  
**必须用户确认**：推断 brief 或改变 claim boundary 时。

**问题卡**：brief normalization card。

选项形态：版本 A/B/C / 保留原句 / 修改 / deferred。

**常见误判**：写成宣传摘要；把领域当贡献；用空泛 thesis。

**写入**：`00_PROJECT_ROUTE.md#Project Brief`。  
**handoff**：planning input，不可直接当正文。

---

### D04 — Target route / `01_target_journal_profile.md`

**本质**：目标 venue/family、paper type、目标读者和审稿期待。它决定写作路线，不是保证投稿成功。

**用户要搞明白**：venue/family；paper type；audience/reviewer expectation；forbidden route；是否暂时 route deferral。

| 档次 | 具体形态 |
|---|---|
| minimum | 有 venue family 或明确 deferred route |
| standard | venue/family、paper type、audience/reviewer expectation、forbidden routes 均 owner-confirmed |
| ideal | 说明 rejected/deferred alternatives 与 tradeoffs |

**Agent 可提议**：2-4 个候选 route、优缺点、风险、推荐候选。  
**必须用户确认**：最终 route、paper type、owner-gated route boundary。

**问题卡**：route selection card / paper type card / audience card / forbidden route card。

选项形态：venue family A/B/C / method-system-benchmark-application-survey / defer / reject route。

**常见误判**：把期刊名气当 route；未经 owner 许可切换领域；把 working target 写成 guarantee。

**写入**：`00_PROJECT_ROUTE.md#Target Route` + `#Audience and Reviewer Expectation` + `#Forbidden Routes`。  
**handoff**：约束 downstream writing route，但不执行外部 skill。

---

### D05 — Material inventory / `02_material_inventory.md`

**本质**：真实材料账本。先回答有什么真实结果、图表、数据、代码、baseline、metric，在哪里，状态如何。

**用户要搞明白**：主结果路径；图表位置；数据/代码状态；baseline/metric；哪些只是计划；哪些明确缺失；provenance。

| 档次 | 具体形态 |
|---|---|
| minimum | 按类别列出材料，或明确 absences |
| standard | 核心 result/figure/table/data/code/baseline/metric 可定位，或 absent/deferred 且有后果说明 |
| ideal | 有 provenance、质量备注、材料能支持哪些 claim |

**Agent 可提议**：分类用户给的路径/文件；标出缺口和后果。  
**必须用户确认**：材料存在性、位置、是否可作为最终结果、缺失状态。

**问题卡**：material inventory card / path card / missing-material status card。

选项形态：path / description-only / planned-deferred / absent-limits-claim / not applicable。

**常见误判**：把 planned experiment 当 completed evidence；把“应该有图”当已有图；材料类别混淆。

**写入**：`01_MATERIALS_INVENTORY.md` 的 results/figures/data/code/baselines/metrics/explicit absences。  
**handoff**：进入 `04_WRITING_DESIGN_PACK.md#Material Boundary`。

---

### D06 — Evidence inventory / `03_evidence_inventory.md`

**本质**：把 D05 材料转成可追溯证据锚点。它回答哪一个 artifact 支持哪一个 claim，支持强度如何。

**用户要搞明白**：每个核心 claim 的 evidence anchor；anchor type/location；supported claim/dimension；support strength；status。

| 档次 | 具体形态 |
|---|---|
| minimum | 至少一个 evidence table，或 evidence absence 明确 |
| standard | 每个核心 claim 有 anchor，且 anchor 有 type/location/supported claim/status |
| ideal | 有 strength note、figure/result cross-links、wording implications |

**Agent 可提议**：E1/E2 anchor ID；从 supplied material 归类到 claim；建议 support strength。  
**必须用户确认**：anchor 是否支撑 claim；证据强度；更强 wording 是否禁止。

**问题卡**：evidence anchor card / support strength card / claim-binding card。

选项形态：result/figure/table/log/code/baseline/metric/statistical output；strong/moderate/weak/deferred/rejected。

**常见误判**：用“实验表明”替代 anchor；把 D05 目录当 D06 evidence chain；把 weak 包装成 strong。

**写入**：`01_MATERIALS_INVENTORY.md#Evidence Inventory` + `02_CLAIM_EVIDENCE_BOUNDARY.md#Claim-Evidence Map`。  
**handoff**：D06 是 D11/D12 的上游。

---

### D07 — Source and citation bank / `04_source_and_citation_bank.md`

**本质**：用户已知/已提供来源候选银行。不是检索器，不自动补 BibTeX。

**用户要搞明白**：已有来源；source role；缺失 citation needs；哪些来源可候选、哪些仅待查。

| 档次 | 具体形态 |
|---|---|
| minimum | supplied / absent / deferred，并有 no-invention note |
| standard | 已知来源与缺失/deferred citation work 分开，无 invented BibTeX |
| ideal | 有 source role、downstream lookup needs、候选/最终边界 |

**Agent 可提议**：整理 supplied sources 的角色。  
**必须用户确认**：来源真实存在、是否纳入、支持哪个 claim。

**问题卡**：source role card / citation status card / source gap card。

选项形态：background / baseline / method / dataset / standard / exemplar / absent / deferred。

**常见误判**：把相关当可引用；凭记忆生成文献；把 D07 变成文献综述任务。

**写入**：`01_MATERIALS_INVENTORY.md#Source and Citation Bank`。  
**handoff**：`04_WRITING_DESIGN_PACK.md#Source / Citation Boundary`，下游不得假装 bibliography 完成。

---

### D08 — Research dossier / `10_research_dossier.md`

**本质**：已有研究语境、相关工作 notes、样例、gap、缺失项的备忘录。不是文献搜索。

**用户要搞明白**：已有 related-work notes；exemplar/style clues；known gaps；unresolved source needs；这些如何影响 venue/claim boundary。

| 档次 | 具体形态 |
|---|---|
| minimum | research notes 存在，或 absent/deferred 明确 |
| standard | 按 related work / exemplar / gap notes / unresolved sources 组织 |
| ideal | 连接到 venue expectations 与 claim boundary |

**Agent 可提议**：分类、归档、重组用户提供 notes。  
**必须用户确认**：来源性判断、研究缺口结论。

**问题卡**：dossier gap card。

选项形态：known related work / exemplar clues / gap notes / unresolved sources / absent / deferred。

**常见误判**：当成文献搜索模块；用 missing notes 推出“论文很新”；把 related-work guesses 当 citation facts。

**写入**：`01_MATERIALS_INVENTORY.md#Research Dossier` + design pack research notes。  
**handoff**：无 dossier 时明确 downstream 只能用 owner-supplied notes。

---

### D09 — Exemplar language profile / `11_exemplar_language_profile.md`

**本质**：写作风格/语言画像。控制语气、组织方式、术语密度、句法节奏；无 exemplar 时退化为 generic route constraints。

**用户要搞明白**：是否有 exemplar papers；想保留哪些风格特征；想避免哪些风格；是否 defer。

| 档次 | 具体形态 |
|---|---|
| minimum | 有 exemplar，或 absent/deferred 明确 |
| standard | 有 exemplar 时抽成可执行风格约束；无 exemplar 时写 generic route constraints |
| ideal | 有正/负样例和可复用 sentence patterns |

**Agent 可提议**：通用路线一致的风格约束。  
**必须用户确认**：具体 exemplar/source 命名和归属判断。

**问题卡**：style profile card。

选项形态：supplied exemplars / no exemplar use generic route constraints / defer / avoid style X。

**常见误判**：伪造 exemplar；把摘要润色当 D09；把个例当 genre 规则。

**写入**：`03_WRITING_STRUCTURE.md#Exemplar Language Profile`。  
**handoff**：作为 writing structure / external handoff 约束。

---

### D10 — Contribution options / `12_contribution_options.md`

**本质**：贡献 frame 选择。先决定论文主打 method/system/model/dataset/benchmark/application/analysis 哪一种，而不是先写成果口号。

**用户要搞明白**：问题；研究对象；主贡献 frame；哪些 tempting frames reject/defer；主次关系。

| 档次 | 具体形态 |
|---|---|
| minimum | 至少一个候选贡献选项，或 deferred |
| standard | selected/rejected/deferred contribution options owner-confirmed，且绑定材料/证据依赖 |
| ideal | 不同 framing tradeoff 清楚，如 method vs system、benchmark vs application |

**Agent 可提议**：候选 option set 和利弊。  
**必须用户确认**：最终主贡献 frame、reject 哪些 tempting options。

**问题卡**：contribution decision card。

选项形态：method / system / model / dataset / benchmark / application / analysis / defer / reject。

**常见误判**：多个贡献都做主贡献；frame 比证据更大；先写正文再倒推贡献。

**写入**：`02_CLAIM_EVIDENCE_BOUNDARY.md#Contribution Options`。  
**handoff**：进入 `04_WRITING_DESIGN_PACK.md#Core Contribution`；D10 是 D11/D12/D17 上游。

---

### D11 — Claim-evidence map / `13_claim_evidence_map.md`

**本质**：每条核心主张绑定 evidence anchor、support strength、status、forbidden wording。Claim 必须可审查、可降级、可拒绝。

**用户要搞明白**：核心 claims；每条 claim 的 anchor；support strength；claim status；禁用措辞。

| 档次 | 具体形态 |
|---|---|
| minimum | claim list 存在，或 deferred/rejected 明确 |
| standard | 每条 active core claim 有 owner-confirmed wording、evidence anchor、support strength、status |
| ideal | 有 claim hierarchy、downgrade reasons、rejected claim reasons |

**Agent 可提议**：保守 claim 候选并匹配已有 evidence。  
**必须用户确认**：哪些 claim 写入论文；anchor 绑定关系。

**问题卡**：claim row card。

字段：claim / evidence anchors / support strength / status / forbidden wording。

Support strength 建议语义：

| strength | 语义 | 写作动作 |
|---|---|---|
| strong | 直接、重复、锚点清晰 | 可较直接，但仍绑定范围 |
| moderate | 部分间接/局部限制 | 更谨慎、更限定 |
| weak | 薄弱或间接支持 | 降级、移到 limitation 或 defer |
| deferred | 暂无 anchor | 不进主结论 |
| rejected | 证据不足/冲突 | 删除或明确不采纳 |

**常见误判**：用主观强弱替代证据；无 anchor 写 supported；deferred 偷升 supported。

**写入**：`02_CLAIM_EVIDENCE_BOUNDARY.md#Claim-Evidence Map`。  
**handoff**：D11 是 D12/D13 的直接上游。

---

### D12 — Wording boundary / `14_wording_boundary.md`

**本质**：claim 的许可词表与禁用词表。不是润色，而是防 overclaim。

**用户要搞明白**：claim 证据强度；能否普遍化；哪些词安全；哪些词危险；wording 是否改变 route/contribution。

| 档次 | 具体形态 |
|---|---|
| minimum | 至少有 allowed/forbidden boundary，或 deferred |
| standard | allowed/forbidden/overclaim boundary 与 evidence strength 绑定，core claims owner-confirmed |
| ideal | 有按 claim strength 分层的 safe wording examples |

**Agent 可提议**：strong/medium/weak wording 版本、safe/unsafe 对照。  
**必须用户确认**：最终 forbidden wording、会抬高贡献或改 route 的措辞。

**问题卡**：safe/unsafe wording pair card。

选项形态：safe wording / unsafe wording / strong-medium-weak / supported-unsupported-deferred。

**常见误判**：局部实验写成普遍规律；相关性写因果；hedge 过度导致 claim 虚化。

**写入**：`02_CLAIM_EVIDENCE_BOUNDARY.md#Allowed Wording` + `#Forbidden Wording`。  
**handoff**：进入 design pack allowed/forbidden wording。

---

### D13 — Limitations and risks / `15_limitation_and_risk_matrix.md`

**本质**：把必须保留的限制、风险、约束系统化。它防止 downstream writing 把边界抹掉。

**用户要搞明白**：数据/baseline/metric/deployment/generalization/citation gap；哪些风险来自证据缺口、route、rejected claims；哪些必须显式保留。

| 档次 | 具体形态 |
|---|---|
| minimum | 至少一个 limitation/risk，或 owner 给出“暂无已知限制”的理由 |
| standard | limitation/risk 与材料缺口、证据强度、route expectation 或 rejected claim 绑定 |
| ideal | 每个主要限制带 mitigation/handoff note |

**Agent 可提议**：从缺失材料反推候选风险，分类 risk。  
**必须用户确认**：哪些 risk 是 material；哪些必须正文可见；“暂无限制”是否成立。

**问题卡**：risk visibility card。

选项形态：data scope / baseline scope / metric scope / deployment / generalization / citation gap / none-known-with-rationale。

**常见误判**：写 no limitations；把 limitation 只当 future work；caveat 和证据边界无关。

**写入**：`02_CLAIM_EVIDENCE_BOUNDARY.md#Limitations and Risks`。  
**handoff**：D13 是 D14/D15 的边界输入。

---

### D14 — Reader spine / `20_reader_spine.md`

**本质**：读者问答路径。它不是 section list，而是论文从问题到证据到限制的论证路径。

**用户要搞明白**：读者第一问；问题→缺口→贡献→证据→限制的路径；每步获得什么；是否与 route/claim/evidence 一致。

| 档次 | 具体形态 |
|---|---|
| minimum | 粗略 reader question sequence |
| standard | spine 与 confirmed route、contribution、claim-evidence、limitations 对齐 |
| ideal | 有 rejected alternative spine 及其理由 |

**Agent 可提议**：2-3 条 spine 候选，标明依赖的 claim/evidence/limitation。  
**必须用户确认**：spine 改变 claim/route 强调时。

**问题卡**：reader-spine choice card。

选项形态：problem-first / gap-first / contribution-first / evidence-first / limitation-first。

**常见误判**：用 unsupported claim 驱动开头；只排 section 不写问题链；把 limitation 当附属。

**写入**：`03_WRITING_STRUCTURE.md#Reader Spine`。  
**handoff**：进入 design pack Reader Spine；D11-D13 不稳时只能 candidate。

---

### D15 — Manuscript outline / section jobs / `21_manuscript_outline.md`

**本质**：把 reader spine 落到 section-level job map。不是目录草稿，更不是正文。

**用户要搞明白**：paper type；每个 major section 的 job；哪个 evidence 由哪个 section 承担；哪些 claim 不能偷渡。

| 档次 | 具体形态 |
|---|---|
| minimum | section list，或 outline deferred |
| standard | outline + section jobs 与 paper type、route、reader spine、evidence、limitations 对齐 |
| ideal | 有 paragraph/function map 和 section-level evidence responsibility |

**Agent 可提议**：按 paper type 给 outline variants、section job cards。  
**必须用户确认**：实质不同 paper type、改变贡献定义或 route 的 outline。

**问题卡**：section job card。

字段：section / job / allowed content / forbidden content / evidence owner。

**常见误判**：generic IMRaD 脱离证据；直接写段落；Intro 偷做 Results 工作。

**写入**：`03_WRITING_STRUCTURE.md#Manuscript Outline` + `#Section Jobs`。  
**handoff**：进入 design pack Writing Structure。

---

### D16 — Object granularity / `22_object_granularity.md`

**本质**：研究对象边界。贡献附着在哪个对象上：method/system/model/dataset/benchmark/application/analysis object。

**用户要搞明白**：精确研究对象；inside/outside；哪些词会说歪；对象边界是否改变贡献、证据、叙述顺序。

| 档次 | 具体形态 |
|---|---|
| minimum | 对象类型被命名，或 deferred |
| standard | 对象粒度足够绑定 claims、evidence、outline、wording |
| ideal | 有 object/non-object 区分和 too-broad 反例 |

**Agent 可提议**：从材料推 candidate object boundary。  
**必须用户确认**：影响 claim/contribution 的对象边界。

**问题卡**：object boundary card。

选项形态：method / system / model / dataset-benchmark / application-analysis object / custom / deferred。

**常见误判**：method/system/application 混淆；把贡献当对象；对象太宽使 evidence 无法绑定。

**写入**：primary `03_WRITING_STRUCTURE.md#Object Granularity`；secondary `02_CLAIM_EVIDENCE_BOUNDARY.md#Object Granularity`。  
**handoff**：后续写作不得擅自扩展对象边界。

---

### D17 — Surface control / `23_surface_control.md`

**本质**：语言表面护栏：术语、语气、句式、词强度、禁止表达。不是文风美化。

**用户要搞明白**：安全/过强词；必须避开的表达；语气；术语与对象粒度是否一致。

| 档次 | 具体形态 |
|---|---|
| minimum | 有基本 tone/term 控制，或 deferred |
| standard | surface control 与 route、evidence strength、forbidden wording、object granularity 对齐 |
| ideal | 有 safe phrases、banned phrases、语气例子 |

**Agent 可提议**：保守术语、推荐语气、候选 safe wording。  
**必须用户确认**：最终 forbidden overclaims、领域敏感术语、绝对禁用表达。

**问题卡**：surface guardrail card。

选项形态：conservative / neutral-technical / strong-only-if-supported；禁用类别多选。

**常见误判**：当成润色；允许 optimal/universal/guaranteed 等超证据词；术语和对象边界不一致。

**写入**：primary `03_WRITING_STRUCTURE.md#Surface Control`；secondary `02_CLAIM_EVIDENCE_BOUNDARY.md#Allowed Wording` / `#Forbidden Wording`。  
**handoff**：下游必须把它当 guardrails，不是建议。

---

### D18 — Visual plan / `24_visual_plan.md`

**本质**：图表如何讲故事。不是“有图了”，而是图表顺序、证据角色、缺图和视觉 handoff 约束。

**用户要搞明白**：已有 figures/tables；主线顺序；哪些视觉材料只是需要；新增图是否改变 scope/evidence claim。

| 档次 | 具体形态 |
|---|---|
| minimum | 已有/需要的图表列出，或 deferred/no-visual rationale |
| standard | 视觉叙事把图表与 reader spine、claims、materials 连接起来 |
| ideal | 有 visual order、缺图清单、figure-skill handoff 约束 |

**Agent 可提议**：基于现有材料给 figure/table order 与 storyline。  
**必须用户确认**：新增图是否改 scope 或证据主张。

**问题卡**：visual inventory/storyline card。

选项形态：overview figure / method flow / main result / comparison table / no visual with rationale / needed not existing。

**常见误判**：发明不存在图；把 visual plan 当图已产出；图表讲 unsupported story。

**写入**：`03_WRITING_STRUCTURE.md#Visual Plan` + `#Figure / Table Storyline`；关联 `01_MATERIALS_INVENTORY.md`。  
**handoff**：figure 模块只能按计划执行，不能反向改证据边界。

---

### D19 — Writing design pack / `25_WRITING_DESIGN_PACK.md`

**本质**：最终编译动作。它收束 D00-D18 到 `04_WRITING_DESIGN_PACK.md`，不是正文生成。

**用户要搞明白**：所有硬阻塞是否已处理；是否可安全 handoff；哪些信息仍 absent/deferred/rejected。

| 档次 | 具体形态 |
|---|---|
| minimum | D19 deferred，等待上游 |
| standard | design pack 覆盖 route/material/source/claims/wording/risks/structure/visuals/handoff，且 D00-D18 已处理 |
| ideal | 有 downstream route 建议，但不执行外部 skill |

**Agent 可提议**：编译 design pack、建议下游 writing/figure/citation route。  
**必须用户确认**：未解决 owner-gated assumption。

**问题卡**：final compile readiness card。

选项形态：compile now / blocker remains / recompile due stale / choose downstream handoff route / defer。

**常见误判**：以为 design pack 是论文正文；留 TODO 硬编译；执行外部 writing skill；把 deferred 伪装 supported。

**写入**：`04_WRITING_DESIGN_PACK.md#Dimension Coverage Summary` 及所有必需 section。  
**handoff**：只交接，不提交、不发表、不声称 final paper。

---

## 4. 跨维度链路

### 4.1 Route → Materials → Evidence → Claim → Wording

```text
D04 route
  → D05 material inventory
  → D06 evidence anchors
  → D10 contribution frame
  → D11 claim-evidence map
  → D12 wording boundary
  → D13 limitations/risks
```

若 D05/D06 不稳，D11 不能 standard；若 D11 不稳，D12/D13/D14-D18 都只能 candidate/deferred。

### 4.2 Object / Surface / Visual chain

```text
D16 object granularity
  → D17 surface control
  → D18 visual storyline
  → D19 design pack compile
```

D16 是 claim、outline、surface、visual 的共同上游。D17 是语言安全阀。D18 依赖 D05 真实材料，不能凭空造图。

### 4.3 D16/D17 primary-secondary write rule

- D16 primary：`03_WRITING_STRUCTURE.md#Object Granularity`
- D16 secondary：`02_CLAIM_EVIDENCE_BOUNDARY.md#Object Granularity`
- D17 primary：`03_WRITING_STRUCTURE.md#Surface Control`
- D17 secondary：`02_CLAIM_EVIDENCE_BOUNDARY.md#Allowed Wording` / `#Forbidden Wording`
- 若 primary 和 secondary 冲突，block compile，进入 reconciliation card。

### 4.4 D07/D08 缺失不等于失败

D07/D08 不是 native search。没有来源或 research dossier 时，应显式 absent/deferred，并写清 downstream handoff。不得编造 bibliography 或 research context。

### 4.5 D04 deferred 的允许边界

D04 可临时 deferred 以继续材料整理；但 final pack 前至少需要 owner 确认 venue family / paper type / audience expectation，或明确接受 final-route deferral 的后果。

### 4.6 D18 no-visual 的允许边界

无图/表可以通过，但必须说明：

1. 为什么无图表合理；
2. 替代 visual storyline 的组织方式；
3. 哪些 claims 不依赖图表；
4. 下游不得虚构 figure。

---

## 5. 问题卡族

| 卡族 | 典型维度 | 模式 | 目的 |
|---|---|---|---|
| metadata confirmation | D00 | candidate-confirmation | 确认工作区身份 |
| owner decision gate | D01 | focused-question / multi-answerable | 锁定禁区和 owner-gated 决策 |
| stale alert | D02 | stale-alert | 防止旧 pack 被误用 |
| brief normalization | D03 | candidate-confirmation | 归一化 topic/brief |
| route selection | D04 | focused-question | 选择 venue family/paper type |
| material inventory | D05 | quick-form | 收集材料类别与路径 |
| evidence anchor | D06 | focused-question / table row | 材料→claim 证据绑定 |
| source boundary | D07 | focused-question | 记录 source status，防止造引用 |
| dossier gap | D08 | quick-form / focused-question | 组织已有 research notes 和缺口 |
| style profile | D09 | focused-question | 确认 exemplar/generic style constraints |
| contribution decision | D10 | focused-question | 选择贡献 frame |
| claim row | D11 | focused-question | 逐条 claim 绑定 evidence |
| wording pair | D12 | focused-question | allowed/forbidden wording |
| risk visibility | D13 | multi-answerable | limitation/risk 分类 |
| reader spine | D14 | candidate-confirmation | 选择论证路径 |
| section job | D15 | candidate-confirmation | outline 与 section jobs |
| object boundary | D16 | focused-question | 研究对象粒度 |
| surface guardrail | D17 | focused-question/multi | 术语和语气护栏 |
| visual storyline | D18 | quick-form/focused | 图表主线和缺图 |
| compile readiness | D19 | focused-question | 最终编译/handoff |

---

## 6. 开发落地建议

下一轮 PRD 应避免写成“补更多说明”。它应指定可验证的实现面：

1. 在 `SKILL.md` 增加 first-run interaction contract 与 mode selection rule。
2. 在 `00-dimension-rubric.md` 中把本文的 D00-D19 认知要点压缩成更清晰的 agent 判断规则。
3. 在五个 playbooks 中增加对应阶段的问题卡模板，不复制全部二十维长文。
4. 在 `04-design-pack-compiler.md` 增加 compile decision table。
5. 在模板中只加解释性 prose，不改 schema。
6. 扩展结构检查器，检查：phase names、question-card presence、compile decision table、D16/D17 rules、Blocks semantics、public surface/schema invariants。
7. 明确：如果 `omx question` 环境存在，可以用它渲染问题卡；否则输出 Markdown 问题卡。

---

## 7. 资料与依据

### 本仓库依据

- `skills/yxj-paper-os/SKILL.md`
- `skills/yxj-paper-os/references/00-dimension-rubric.md`
- `skills/yxj-paper-os/references/00-project-route.md`
- `skills/yxj-paper-os/references/01-materials-inventory.md`
- `skills/yxj-paper-os/references/02-claim-evidence-boundary.md`
- `skills/yxj-paper-os/references/03-writing-structure.md`
- `skills/yxj-paper-os/references/04-design-pack-compiler.md`
- `skills/yxj-paper-os/assets/templates/*.md`
- `skills/yxj-paper-os/scripts/verify_design_pack.py`
- `docs/BRANCH_PHILOSOPHY.md`

### yxj-backend / yxj-wiki 只读依据

本轮遵守 yxj-backend capsule-first 规则。查询结果主要作为概念参照，不作为外部发表决策或 publication-grade evidence。关键边界：

- capsule/source cards/cluster packets 不是 reviewed publication evidence；
- 不 blind scan `raw/`；
- 不 hand-edit refs/truth/generated artifacts；
- yxj-wiki 不维护仓库外部投稿/发表/批准决策。

### 外部权威/参考资料

- Nature Support — Find the right journal for your manuscript: <https://support.nature.com/en/support/solutions/articles/6000134500-find-the-right-journal-for-your-manuscript>
- Elsevier Researcher Academy — How to find the right journal: <https://researcheracademy.elsevier.com/system/files/workshop/2026-02/How%20to%20the%20find%20the%20right%20journal%20Feb%202026.pdf>
- ICMJE Recommendations / manuscript preparation: <https://www.icmje.org/recommendations/browse/manuscript-preparation/preparing-for-submission.html>
- NIH Data Management and Sharing Plan guidance: <https://grants.nih.gov/policy-and-compliance/policy-topics/sharing-policies/dms/writing-dms-plan>
- NSF DMREF Data Management and Sharing Plans: <https://www.nsf.gov/mps/dmref-data-management-sharing-plans>
- Crossref citation resources: <https://www.crossref.org/categories/citation/>
- EQUATOR Network reporting guidelines: <https://www.equator-network.org/reporting-guidelines/>
- UNC Writing Center — Literature Reviews: <https://writingcenter.unc.edu/tips-and-tools/literature-reviews/>
- UNC Writing Center — Qualifiers: <https://writingcenter.unc.edu/tips-and-tools/qualifiers/>
- UNC Writing Center — Figures and Charts: <https://writingcenter.unc.edu/tips-and-tools/figures-and-charts/>
- Purdue OWL — CARS / organization model: <https://owl.purdue.edu/owl/general_writing/the_writing_process/organization_CARS_Model.html>
- Purdue OWL — Genre Analysis & Reverse Outlining: <https://owl.purdue.edu/owl/graduate_writing/thesis_and_dissertation/genre_analysis_reverse_outline.html>
- USC Writing Guide — Introduction/CARS/Results/Discussion/Limitations: <https://libguides.usc.edu/writingguide>
- CHI 2026 — Contributions to CHI: <https://chi2026.acm.org/contributions-to-chi/>
- Cochrane Handbook — Grading certainty of evidence: <https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-14>
- Microsoft Writing Style Guide: <https://learn.microsoft.com/en-us/style-guide/welcome/>
- Pew Research Center — Writing Survey Questions: <https://www.pewresearch.org/writing-survey-questions/>
- U.S. Census Bureau — Questionnaire Testing and Evaluation Methods: <https://www.census.gov/about/policies/quality/standards/appendixa2.html>
- CDC CCQDER: <https://www.cdc.gov/nchs/ccqder/index.html>
