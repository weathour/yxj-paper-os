window.PPG_RUNTIME_GRAPH = (() => {
  const meta = {
    title: 'PPG Runtime 人工把握视图',
    subtitle: 'Paper OS runtime state surface：显式物料图、stage-local Nature overlay、前沿、stale/backflow 与交付门可见',
    status: {
      baseline: 'Paper OS runtime surface：adapter、stage coverage 与 Nature overlay 绑定同源',
      scope: '当前视图同时展示 stage taxonomy、deterministic fixture-backed runtime state、readiness evidence 与 stage-local overlay；仍不代表已 install/publish/submission ready',
      next: '后续真实论文生产运行仍由主 Agent 按 StageContract、TaskPacket、overlay validator 与 owner gate 调度；安装/marketplace 需额外授权',
    },
    canvas: { width: 2260, height: 1680 },
  };
  const legend = {
    material: '物料正向流',
    dispatch: '主 Agent 派发',
    validation: '验证与门控',
    graph: '图状态读写',
    backflow: '审核回流',
    governance: '治理与 sidecar',
  };
  const defaultVisibleKinds = ['material', 'dispatch', 'validation', 'graph', 'backflow', 'governance'];
  const layers = [
    { id: 'L0', y: 30, h: 280, title: 'L0 控制面', subtitle: '人类授权、主 Agent、物料图、验证器、任务包总线', tone: 'control' },
    { id: 'L1', y: 335, h: 170, title: 'L1 基础材料', subtitle: '需求语义契约与来源/证据盘点', tone: 'source' },
    { id: 'L2', y: 535, h: 170, title: 'L2 研究与 claim 准入', subtitle: '场景/SOTA、贡献选项、证据到主张的门控', tone: 'research' },
    { id: 'L3', y: 735, h: 170, title: 'L3 论文结构设计', subtitle: '主脊、对象颗粒度、术语修辞、图表形式计划', tone: 'design' },
    { id: 'L4', y: 935, h: 170, title: 'L4 写作与形式产出', subtitle: '正文任务包、文本单元、图表/caption/形式对象', tone: 'production' },
    { id: 'L5', y: 1135, h: 170, title: 'L5 集成、审核、回流', subtitle: '集成候选稿、对抗审核、回流任务、局部再生成', tone: 'review' },
    { id: 'L6', y: 1335, h: 200, title: 'L6 导出与论文后派生', subtitle: '交付包、最终论文产物、PPT/专利/期刊 profile 等派生 sidecar', tone: 'delivery' },
  ];
  const nodeRows = [
    ['OWNER','control','control',210,82,250,92,'Human owner','人类作者/语义权威','提供需求、边界、审稿偏好和关键取舍，批准会改变论文核心语义的决策。',['真实写作需求','目标期刊或读者','可接受风险','核心禁区'],['语义授权','重大决策','边界修订','最终接受或退回'],['是否涉及核心语义改变'],['S00']],
    ['CTRL','controller','control',520,72,400,112,'Main Agent / Runtime Controller','主 Agent / Runtime 控制器','观察物料图，选择前沿节点，编译任务包，调度 subagent 或程序，收集候选产物，执行验证和提交。',['Owner 决策','物料图状态','验证报告','回流任务'],['TaskPacket','MaterialBundle','调度命令','提交或回滚决策'],['只有主 Agent 可以宣布图节点完成'],['任意 stale 节点']],
    ['GRAPH','graph','control',980,72,360,112,'Versioned Material Graph / Ledger','版本化物料图 / Ledger','保存节点、边、版本、依赖、验证器、来源锚点、stale 传播和 sidecar 状态。',['候选产物','验证结果','依赖变化','回流标记'],['可执行前沿','物料版本','stale 集合','可视化数据'],['schema 校验','依赖完整性校验','版本一致性校验'],['CTRL']],
    ['VALIDATORS','validator','control',1400,72,330,112,'Validator Registry','验证器注册表','集中管理 schema、证据、引用、stage-local overlay、审稿体验、渲染、导出和仓库卫生检查。',['候选物料','目标节点契约','期刊模板','证据锚点'],['通过/失败','错误定位','严重度','回流建议'],['主 Agent 选择并解释验证器'],['S14']],
    ['G01','sidecar','governance',1785,72,300,112,'Runtime governance sidecar','G01 Runtime 治理 sidecar','保存权限、技能、路线元数据、路线记录和状态控制，不直接进入正文认知链。',['state','permissions','route metadata'],['skill registry','route/governance records','state controls','authority limits'],['是否越权','是否污染写作物料'],['CTRL']],
    ['BUS','bus','control',520,212,1210,70,'TaskPacket + Structured MaterialBundle Bus','任务包 + 结构化物料包总线','把大上下文变成结构化包，而不是压缩成摘要。每个环节只负责一个有边界的产物。',['任务目标','强制控制项','Nature stage-local overlay clause','证据和来源锚点','局部上下文','可选背景','禁用路线','验证器','返回格式'],['可派发任务包','subagent 输入包','程序转换输入'],['字段完整性','上下文边界','禁止路线存在性'],['CTRL']],

    ['S00','stage','root',210,360,300,126,'Owner semantic contract','S00 人类需求与语义契约','把人的真实写作目的转成论文 runtime 可执行的约束，确定什么能自动推进，什么必须回到人类。',['human need','paper profile','evidence summary'],['profile','motivation','core decisions','blocked routes'],['目标具体','禁用路线显式','证据足以进入后续阶段'],['OWNER']],
    ['S01','stage','inventory',560,360,300,126,'Source/citation/evidence inventory','S01 来源、引用、证据盘点','建立论文能够使用的真实材料边界，防止后续写作脱离证据。',['files','BibTeX','result dirs','locators'],['source map','citation bank','evidence bank','Nature source inventory'],['路径可访问','引用字段完整','证据可追溯'],['S00']],

    ['S02','analysis','research',210,560,300,126,'Research / scene / template / SOTA','S02 研究场景、模板、SOTA 分析','把材料放入读者、期刊模板、领域争论和相关工作的位置中。',['source map','venue','exemplars'],['research dossier','reader package','search strategy','template or journal profile'],['场景覆盖读者问题','模板约束可执行','SOTA 可引用'],['S01']],
    ['S03','analysis','research',560,560,300,126,'Novelty / contribution options','S03 新颖性与贡献选项','产生可选贡献路线，但必须经过证据可承载性门控；不能绕过 S04 直接进入写作主脊。',['research','evidence','SOTA','motivation'],['contribution options','evidence-readiness','risk list'],['贡献可被证据支持','风险显式','避免过度声明'],['S02','S04']],
    ['S04','gate','claim',910,560,300,126,'Evidence-to-claim admissibility','S04 证据到主张的准入门','把贡献候选、实验、引用和观察变成可写入论文的 claim capsule，确定哪些话能说、说到什么强度。',['evidence bank','citations','results','contribution options'],['claim capsules','result packages','claim visibility','data availability','admitted contribution scope'],['每个 claim 有证据锚点','结论强度不过载','数据可用性明确'],['S01','S03','S00']],

    ['S05','design','spine',210,760,300,126,'Paper spine / reader questions','S05 论文主脊与读者问题','形成论文从问题到贡献到证据的主线，定义读者每一节需要得到的答案。',['motivation','contribution','template','claims'],['reader spine','reviewer question map','rationale matrix'],['章节问题递进','主线单一','读者疑问被覆盖'],['S03','S04']],
    ['S06','design','spine',560,760,300,126,'Object / granularity design','S06 对象表示与颗粒度设计','决定论文里哪些对象、变量、机制、图表和术语要出现到什么细度。',['spine','questions','template','claim visibility'],['object representation','section budget','load budget','explanation ladder'],['概念层级不混乱','读者负荷可控','支撑 claim 可见性'],['S05']],
    ['S07','design','surface',910,760,300,126,'Rhetoric / terminology / surface controls','S07 修辞、术语与表层控制','控制语气、术语、句式、段落组织和论文表面，防止概念正确但表达失焦。',['object design','claim visibility','evidence wording'],['construction matrix','rhetorical matrix','terminology register','surface rules'],['术语一致','claim 强度匹配','表层贴近目标期刊'],['S06','S04']],
    ['S08','design','visual',1260,760,300,126,'Visual / formal planning','S08 图表与形式对象规划','为图、表、公式、算法、补充材料建立契约；必须同时吃主脊、章节功能预算和 claim/evidence。',['reader spine','section/function budget','claims/evidence'],['visual budget','figure contract','aesthetic profile','panel evidence','backend route'],['图有论证功能','panel 绑定证据','导出路径明确'],['S05','S06','S04']],

    ['S09A','packet','writing',210,960,300,126,'Control-material selection','S09A 控制物料选择','从 claim、主脊、颗粒度和表层规则中选择当前目标单元必需的控制物料，避免把全部上下文倒进写作包。',['claim control','spine control','granularity control','surface rules','target unit'],['selected control bundle','control priority map','missing-control report'],['控制项足够且不过载','冲突优先级明确','缺失物料显式'],['S04','S05','S06','S07']],
    ['S09B','packet','writing',560,960,300,126,'Per-unit task packet assembly','S09B 单元任务包组装','把选定控制物料、证据锚点和返回格式编译成可派发给单个 subagent 的 WritingTaskPacket。',['selected control bundle','evidence anchors','target unit','return format'],['task packet','section move plan','single-writer lock'],['任务包字段完整','目标小节有边界','completion_forbidden 为真'],['S09A','S14','S15']],
    ['S10','production','writing',910,960,300,126,'Main-text production','S10 正文产出','基于 S09B 任务包写出候选文本单元，不能自行宣布最终完成。',['task packet','construction','terminology','claim/evidence'],['candidate text units'],['claim 有锚点','术语一致','段落功能满足任务包'],['S09B','S07']],
    ['S11','production','visual',1260,960,300,126,'Figure / caption / formal production','S11 图表、caption 与形式对象产出','生成图、表、caption、算法或公式相关产物；数据/证据必须来自 S01/S04，不能由图表 agent 自造。',['figure contract','panel evidence','source data locators','result package','caption constraints'],['figure stats','image integrity','caption brief','figure export bundle','artifacts'],['图像可打开','caption 承接 claim','数据可追踪'],['S08','S04','S01']],

    ['S12','integration','integration',210,1160,300,126,'Integration / consistency pass','S12 集成与一致性检查','合并正文和图表，检查术语、claim、引用、图文关系和章节递进。',['candidate modules','figures','terminology','claims'],['integrated manuscript candidate','consistency findings'],['跨章节术语一致','图文互相引用','claim 不漂移'],['S10','S11','S07']],
    ['S13','review','review',560,1160,300,126,'Adversarial review / loss','S13 对抗审核与损失信号','审核器只产生 findings 和 loss，不直接重写全文。',['manuscript','evidence','narrative','figures/export'],['review reports','reader surface report','rendered gate','validator report'],['审稿人视角问题','证据断裂','表层和模板问题','导出问题'],['S14']],
    ['S14','review','backflow',910,1160,300,126,'Backflow compilation','S14 回流任务编译','把审核 findings 映射到最近责任物料，而不是从头重写整篇论文；必要时先回到 S09A 重选控制物料。',['findings','graph state','affected materials'],['narrative backflow task','repair packets','polishing/response plans'],['定位最近责任节点','标记影响下游','修复任务足够小'],['S04','S07','S09A','S09B','S15']],
    ['S15','repair','backflow',1260,1160,300,126,'Repair / local regeneration','S15 局部修复与再生成','只重写受影响的物料、文本或图表，并重新触发必要验证；文本修复优先回到 S09B 再生成任务包。',['backflow task','target material','stale downstream set'],['revised material/text/figure','regenerated task packet when needed','updated validator report'],['目标修复通过','下游 stale 清理','未破坏无关部分'],['S04','S07','S09B','S10','S12']],

    ['S16','delivery','delivery',560,1378,300,126,'Export / handoff / delivery','S16 导出、交付与交接','只接收已通过集成/审核闭合或局部修复闭合的交付包，完成论文、图表、补充材料、仓库卫生和交接报告。',['clean final candidate','review closure','repair-complete delivery package','figures','repository state'],['export manifest','repository hygiene report','manager handoff reports'],['导出可打开','引用和图表路径完整','仓库风险明确'],['S12','S13','S15']],
    ['FINAL','final','delivery',910,1378,420,126,'Final Paper Artifact','最终论文产物','正文、图表、补充材料、证据链、导出清单和给人的交接说明。',['S16 delivery package'],['manuscript','figures','supplement','provenance','owner handoff'],['人类最终验收'],['S13','S00']],
    ['G02','sidecar','derivative',1410,1378,330,126,'Derivative/post-paper sidecar','G02 论文后派生 sidecar','稳定论文之后再派生 PPT、专利边界或期刊 profile 包等，不干扰当前论文完成。',['stable paper','owner request'],['presentation plan','patent boundary','profile-specific derivative package'],['是否晚于论文稳定点','是否不回写污染正文'],['S16']],
  ];
  const nodes = nodeRows.map(([id,type,phase,x,y,w,h,title,titleZh,description,inputs,outputs,validators,backflowTargets]) => ({ id,type,phase,x,y,w,h,title,titleZh,description,inputs,outputs,validators,backflowTargets }));
  const edges = [
    ['c1','governance','OWNER','CTRL','需求/决策'], ['c2','graph','CTRL','GRAPH','读写物料图'], ['c3','validation','GRAPH','VALIDATORS','验证请求'], ['c4','validation','VALIDATORS','CTRL','验证报告'], ['c5','dispatch','CTRL','BUS','编译任务包'],
    ['m00','material','S00','S01','profile -> inventory'], ['m01','material','S01','S02','source map'], ['m02','material','S02','S03','research dossier'], ['m03','material','S01','S04','evidence bank'], ['m04','material','S03','S04','contribution options -> claim gate'], ['m05','material','S04','S05','admitted claim/contribution capsules'], ['m06','material','S05','S06','reader spine'], ['m07','material','S06','S07','object design'], ['m08','material','S05','S08','spine to figures'], ['m08b','material','S06','S08','section/function budget'], ['m09','material','S04','S09A','claim control'], ['m10','material','S05','S09A','spine control'], ['m11','material','S06','S09A','granularity control'], ['m12','material','S07','S09A','surface control'], ['m13','material','S08','S11','figure contract'], ['m13a','material','S01','S11','source data locators'], ['m13b','material','S04','S11','panel evidence/result package'], ['m14','material','S09A','S09B','selected control bundle'], ['m14b','material','S09B','S10','text task packet'], ['m15','material','S10','S12','candidate text'], ['m16','material','S11','S12','figure bundle'], ['m17','material','S12','S13','integrated candidate'], ['m18','material','S13','S14','findings/loss'], ['m19','material','S14','S15','repair packets'], ['m20','material','S15','S16','repair-complete delivery package'], ['m20b','material','S12','S16','clean final candidate'], ['m20c','material','S13','S16','review closure'], ['m21','material','S16','FINAL','final artifact'],
    ['v1','validation','S04','VALIDATORS','claim/evidence gate','rightRail'], ['v2','validation','S12','VALIDATORS','consistency gate','rightRail'], ['v3','validation','S13','VALIDATORS','review gate','rightRail'], ['v4','validation','S16','VALIDATORS','export gate','rightRail'],
    ['b1','backflow','S14','S07','L1-L2 表层/术语','leftRail'], ['b2','backflow','S14','S04','L3 claim/evidence','leftRail'], ['b3','backflow','S14','S00','L4 语义重置','leftRail'], ['b4','backflow','S15','S10','局部文本再生成'], ['b5','backflow','S15','S12','重新集成验证'], ['b6','backflow','S14','S09A','修复范围重选控制物料'], ['b7','backflow','S15','S09B','再生成任务包'],
    ['g1','governance','G01','CTRL','权限/路线控制'], ['g2','governance','G01','GRAPH','状态控制'], ['g3','governance','S16','G02','论文后派生'],
  ].map(([id,kind,source,target,label,route]) => ({ id,kind,source,target,label,route }));
  nodes.filter((node) => node.id.startsWith('S')).forEach((node, index) => edges.push({ id: `d${String(index).padStart(2,'0')}`, kind: 'dispatch', source: 'BUS', target: node.id, label: 'dispatch' }));

  const roadmap = {
    canvas: { width: 1760, height: 1260 },
    lanes: [
      { id: 'R0', y: 24, h: 150, title: '控制闭环', subtitle: '人类授权 -> 主 Agent -> 任务包 -> 验证器/物料图', tone: 'control' },
      { id: 'R1', y: 210, h: 130, title: '1 基础材料', subtitle: '把人的需求和证据边界变成可执行材料', tone: 'source' },
      { id: 'R2', y: 370, h: 130, title: '2 研究与 claim', subtitle: '从研究场景到可被证据支持的主张', tone: 'research' },
      { id: 'R3', y: 530, h: 130, title: '3 论文设计', subtitle: '组织读者路线、概念颗粒度、术语表层和图表契约', tone: 'design' },
      { id: 'R4', y: 690, h: 130, title: '4 内容生产', subtitle: '正文任务包、正文产出、图表产出汇入集成稿', tone: 'production' },
      { id: 'R5', y: 850, h: 150, title: '5 审核回流', subtitle: '审核只产生 loss，回流到最近责任物料并局部再生成', tone: 'review' },
      { id: 'R6', y: 1040, h: 150, title: '6 交付派生', subtitle: '最终交付和论文稳定后的外部派生', tone: 'delivery' },
    ],
    nodes: [
      ['OWNER',190,60,180,78], ['CTRL',420,60,210,78], ['BUS',680,60,230,78], ['VALIDATORS',960,60,210,78], ['GRAPH',1220,60,210,78], ['G01',1480,60,210,78],
      ['S00',190,236,220,78], ['S01',500,236,220,78],
      ['S02',190,396,220,78], ['S03',500,396,220,78], ['S04',810,396,220,78],
      ['S05',190,556,220,78], ['S06',500,556,220,78], ['S07',810,556,220,78], ['S08',1120,556,220,78],
      ['S09A',190,716,200,78], ['S09B',430,716,200,78], ['S10',670,716,200,78], ['S11',910,716,200,78], ['S12',1150,716,200,78],
      ['S13',190,882,220,78], ['S14',500,882,220,78], ['S15',810,882,220,78],
      ['S16',500,1080,220,78], ['FINAL',810,1080,260,78], ['G02',1160,1080,230,78],
    ].map(([id,x,y,w,h]) => ({ id,x,y,w,h })),
    edges: [
      ['r-c1','OWNER','CTRL','需求/批准','governance'], ['r-c2','CTRL','BUS','编译任务包','dispatch'], ['r-c3','BUS','VALIDATORS','验证规则','validation'], ['r-c4','VALIDATORS','GRAPH','验证报告','validation'], ['r-c5','GRAPH','CTRL','图状态','graph'], ['r-c6','G01','CTRL','治理边界','governance'],
      ['r-01','S00','S01','profile / blocked routes','material'], ['r-02','S01','S02','source map','material'], ['r-03','S02','S03','research dossier','material'], ['r-04','S03','S04','贡献候选进入证据门','material'], ['r-05','S04','S05','可写 claim','material'], ['r-06','S05','S06','reader spine','material'], ['r-07','S06','S07','对象与颗粒度','material'], ['r-08','S07','S09A','表层控制进入控制选择','material'], ['r-09','S09A','S09B','选定控制物料','material'], ['r-10','S09B','S10','正文任务包','material'], ['r-11','S10','S12','候选文本','material'], ['r-12','S12','S13','集成候选稿','material'], ['r-clean','S13','S16','review closure / clean export','material'], ['r-15','S16','FINAL','最终论文包','material'],
      ['r-repair1','S13','S14','findings / loss','material'], ['r-repair2','S14','S15','repair packets','material'], ['r-repair3','S15','S16','repair-complete delivery-ready','material'],
      ['r-b0','S06','S08','section/function budget','material'], ['r-b1','S05','S08','图表/形式计划','material'], ['r-b1a','S04','S08','claim/evidence to visual plan','material'], ['r-b2a','S01','S11','source data locators','material'], ['r-b2b','S04','S11','panel evidence/result package','material'], ['r-b2','S08','S11','figure contract','material'], ['r-b3','S11','S12','图表与 caption','material'], ['r-f1','S04','S09A','claim control','material'], ['r-f2','S05','S09A','spine control','material'], ['r-f3','S06','S09A','granularity control','material'],
      ['r-v1','S04','VALIDATORS','claim gate','validation','rightRail'], ['r-v2','S12','VALIDATORS','consistency gate','validation','rightRail'], ['r-v3','S13','VALIDATORS','review gate','validation','rightRail'], ['r-v4','S16','VALIDATORS','export gate','validation','rightRail'],
      ['r-r1','S14','S04','claim/evidence 回流','backflow','backRail'], ['r-r2','S14','S07','术语/表层回流','backflow','backRail'], ['r-r3','S15','S10','局部文本再生成','backflow'], ['r-r4','S15','S12','重新集成','backflow'], ['r-r5','S15','S04','必要时重开 claim 门','backflow','backRail'], ['r-r6','S14','S09A','重选控制物料','backflow'], ['r-r7','S15','S09B','再生成任务包','backflow'],
      ['r-d1','S16','G02','论文后派生','governance'],
    ].map(([id,source,target,label,kind,route]) => ({ id,source,target,label,kind,route })),
  };

  const presets = [
    { id: 'all', label: '全流程', nodes: ['OWNER','CTRL','GRAPH','VALIDATORS','BUS','G01','S00','S01','S02','S03','S04','S05','S06','S07','S08','S09A','S09B','S10','S11','S12','S13','S14','S15','S16','FINAL','G02'] },
    { id: 'spine', label: '论文主线', nodes: ['S00','S01','S02','S03','S04','S05','S06','S07','S08','S09A','S09B','S10','S11','S12','S13','S14','S15','S16','FINAL'] },
    { id: 'writing', label: '写作汇入', nodes: ['S04','S05','S06','S07','S08','S09A','S09B','S10','S11','S12'] },
    { id: 'figures', label: '图表支路', nodes: ['S01','S04','S05','S06','S08','S11','S12'] },
    { id: 'review', label: '审核回流', nodes: ['S12','S13','S14','S15','S04','S07','S09A','S09B','S10'] },
    { id: 'control', label: '控制面', nodes: ['OWNER','CTRL','GRAPH','VALIDATORS','BUS','G01'] },
    { id: 'runtime-core', label: '执行核心', nodes: ['CTRL','GRAPH','VALIDATORS','BUS','S09A','S09B','S13','S14','S15','S16'] },
  ];
  const runtimeState = {
    "active_versions": [
        {
            "active_node": "claim_boundary_map_v2",
            "artifact_path": "examples/materials/claim_boundary_map.v2.yaml",
            "material_id": "claim_boundary_map",
            "status": "committed",
            "version": "v2"
        },
        {
            "active_node": "evidence_inventory_v1",
            "artifact_path": "examples/materials/evidence_inventory.v1.yaml",
            "material_id": "evidence_inventory",
            "status": "committed",
            "version": "v1"
        },
        {
            "active_node": "reader_spine_v1",
            "artifact_path": "examples/materials/reader_spine.v1.yaml",
            "material_id": "reader_spine",
            "status": "committed",
            "version": "v1"
        }
    ],
    "backflow_tasks": [
        {
            "artifact_path": "examples/backflow_tasks/phase7_overclaim_repair.compiled.v1.yaml",
            "id": "phase7_overclaim_review_finding_v1_backflow_v1",
            "label": "Overclaim backflow task v1",
            "node_type": "backflow_task",
            "source_findings": [
                "phase7_overclaim_review_finding_v1"
            ],
            "status": "planned",
            "summary": "Compiled local backflow task that maps claim_overreach to active ClaimBoundaryMap repair target.",
            "targets": [],
            "version": "v1"
        },
        {
            "id": "repair_claim_boundary_task_v1",
            "label": "Repair ClaimBoundaryMap task v1",
            "node_type": "backflow_task",
            "source_findings": [
                "finding_overclaim_v1"
            ],
            "status": "validated",
            "summary": "Backflow task that creates claim_boundary_map_v2.",
            "targets": [
                "claim_boundary_map_v2",
                "claim_boundary_map_candidate_v3"
            ],
            "version": "v1"
        }
    ],
    "candidate_materials": [
        {
            "artifact_path": "examples/materials/claim_boundary_map.v3-candidate.yaml",
            "candidate_for": "claim_boundary_map",
            "id": "claim_boundary_map_candidate_v3",
            "label": "ClaimBoundaryMap v3 candidate",
            "material_id": "claim_boundary_map",
            "node_type": "material",
            "status": "candidate",
            "summary": "Candidate future revision; not active.",
            "version": "v3-candidate"
        }
    ],
    "closed_review_findings": [
        {
            "artifact_path": "examples/review_findings/phase7_overclaim.v1.yaml",
            "classified_repair": true,
            "closed_by": [
                "phase7_overclaim_closure_v1"
            ],
            "closure_status": "closed",
            "failure_type": "claim_overreach",
            "id": "phase7_overclaim_review_finding_v1",
            "invalidates": [
                "claim_boundary_map_v1"
            ],
            "label": "Finding: intro overclaim v1",
            "node_type": "review_finding",
            "primary_target": "claim_boundary_map_v1",
            "repair_tasks": [
                "phase7_overclaim_review_finding_v1_backflow_v1"
            ],
            "status": "validated",
            "summary": "Mock reviewer found universal safety overclaim in intro_draft_v1.",
            "version": "v1"
        }
    ],
    "completion_blockers": [
        "candidate claim_boundary_map_candidate_v3 cannot commit: candidate status must be validated before commit; candidate must declare supersedes=claim_boundary_map_v2; candidate must have supersedes edge claim_boundary_map_candidate_v3 -> claim_boundary_map_v2; candidate-specific validator edge is required; candidate-specific validation report reference is required"
    ],
    "delivery_gates": [
        {
            "artifact_path": "examples/delivery/phase7_delivery_gate.pass.yaml",
            "id": "phase7_delivery_gate_v1",
            "label": "DeliveryGate v1",
            "node_type": "validation_report",
            "report_id": "phase7_delivery_gate_v1",
            "reported_by": [],
            "status": "validated",
            "summary": "DeliveryGate pass for the deterministic intro overclaim repair vertical slice.",
            "validates": [],
            "version": "v1"
        }
    ],
    "graph": {
        "edge_count": 31,
        "graph_id": "phase2-overclaim-material-graph",
        "node_count": 22,
        "source_path": "examples/runtime/overclaim-loop.phase7-after.json",
        "title": "Deterministic Overclaim Repair Vertical Slice"
    },
    "next_frontier": {
        "id": "claim_boundary_map_candidate_v3",
        "kind": "material",
        "priority": 5,
        "reason": "candidate_material_awaiting_validation_or_commit_plan"
    },
    "open_review_findings": [
        {
            "classified_repair": true,
            "closed_by": [],
            "closure_status": "open",
            "failure_type": "claim_overreach",
            "id": "finding_overclaim_v1",
            "invalidates": [
                "claim_boundary_map_v1"
            ],
            "label": "Finding: overclaim v1",
            "node_type": "review_finding",
            "primary_target": "claim_boundary_map_v1",
            "repair_tasks": [
                "repair_claim_boundary_task_v1"
            ],
            "status": "candidate",
            "summary": "Draft states stronger guarantee than evidence supports.",
            "version": "v1"
        }
    ],
    "owner_decisions": [],
    "review_closures": [
        {
            "artifact_path": "examples/delivery/phase7_overclaim_closure.v1.yaml",
            "id": "phase7_overclaim_closure_v1",
            "label": "Overclaim ReviewClosure v1",
            "node_type": "validation_report",
            "report_id": "phase7_overclaim_closure_v1",
            "reported_by": [
                "phase7_mock_reviewer_closure_v1"
            ],
            "status": "validated",
            "summary": "ReviewClosure proving the intro overclaim finding is locally repaired.",
            "validates": [
                "phase7_overclaim_review_finding_v1",
                "phase7_delivery_gate_v1"
            ],
            "version": "v1"
        }
    ],
    "schema_version": "ppg-runtime-state-report/v0.1",
    "stale_materials": [
        {
            "artifact_path": "examples/materials/claim_boundary_map.v1.yaml",
            "historical_superseded_by_active": true,
            "id": "claim_boundary_map_v1",
            "label": "ClaimBoundaryMap v1",
            "material_id": "claim_boundary_map",
            "node_type": "material",
            "on_active_control_path": false,
            "stale_reason": "Superseded by claim_boundary_map_v2 after overclaim review finding.",
            "status": "stale",
            "summary": "Superseded claim boundary version preserved for provenance.",
            "version": "v1"
        }
    ]
};

  const stageCoverage = {
    "active_stage_overlays": [
        "nature_expert_writing"
    ],
    "canonical_stage_count": 20,
    "completion_boundary": "all canonical stages have PilotStageRun coverage; this is not a final manuscript/submission claim",
    "coverage_kind_counts": {
        "fixture_generated": 4,
        "owner_gated_deferred": 1,
        "script_checked": 5,
        "source_projected": 10
    },
    "exercise_level_counts": {
        "deferred_with_gate": 1,
        "full_stage_exercised": 19
    },
    "graph_ref": "graph.json",
    "pilot_root": "examples/local-paper/sample-paper-workspace",
    "pilot_stage_run_count": 20,
    "project_slug": "sample-paper-workspace",
    "schema_version": "ppg-local-paper-full-pilot/v0.1",
    "stage_overlay_binding_counts": {
        "nature_bound": 20
    },
    "stage_overlay_registry_ref": "runtime/stage_overlay_registry.json",
    "stage_runs": [
        {
            "contract_ref": "examples/stage-contracts/S00.stage-contract.json",
            "coverage_kind": "source_projected",
            "exercise_level": "full_stage_exercised",
            "run_ref": "stage-runs/S00.pilot-stage-run.json",
            "stage_id": "S00",
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "light",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S00",
                    "validator_ref": "stage_overlay:nature_expert_writing:S00"
                }
            ],
            "stage_name": "Owner semantic contract",
            "status": "validated",
            "worker_packet_status": "not_required"
        },
        {
            "contract_ref": "examples/stage-contracts/S01.stage-contract.json",
            "coverage_kind": "source_projected",
            "exercise_level": "full_stage_exercised",
            "run_ref": "stage-runs/S01.pilot-stage-run.json",
            "stage_id": "S01",
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "light",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S01",
                    "validator_ref": "stage_overlay:nature_expert_writing:S01"
                }
            ],
            "stage_name": "Source citation evidence inventory",
            "status": "validated",
            "worker_packet_status": "not_required"
        },
        {
            "contract_ref": "examples/stage-contracts/S02.stage-contract.json",
            "coverage_kind": "source_projected",
            "exercise_level": "full_stage_exercised",
            "run_ref": "stage-runs/S02.pilot-stage-run.json",
            "stage_id": "S02",
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "primary",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S02",
                    "validator_ref": "stage_overlay:nature_expert_writing:S02"
                }
            ],
            "stage_name": "Research scene exemplar SOTA analysis",
            "status": "validated",
            "worker_packet_status": "linked_strict_packet"
        },
        {
            "contract_ref": "examples/stage-contracts/S03.stage-contract.json",
            "coverage_kind": "source_projected",
            "exercise_level": "full_stage_exercised",
            "run_ref": "stage-runs/S03.pilot-stage-run.json",
            "stage_id": "S03",
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "support",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S03",
                    "validator_ref": "stage_overlay:nature_expert_writing:S03"
                }
            ],
            "stage_name": "Novelty and contribution option analysis",
            "status": "validated",
            "worker_packet_status": "linked_strict_packet"
        },
        {
            "contract_ref": "examples/stage-contracts/S04.stage-contract.json",
            "coverage_kind": "source_projected",
            "exercise_level": "full_stage_exercised",
            "run_ref": "stage-runs/S04.pilot-stage-run.json",
            "stage_id": "S04",
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "primary",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S04",
                    "validator_ref": "stage_overlay:nature_expert_writing:S04"
                }
            ],
            "stage_name": "Evidence-to-claim admissibility",
            "status": "validated",
            "worker_packet_status": "linked_strict_packet"
        },
        {
            "contract_ref": "examples/stage-contracts/S05.stage-contract.json",
            "coverage_kind": "source_projected",
            "exercise_level": "full_stage_exercised",
            "run_ref": "stage-runs/S05.pilot-stage-run.json",
            "stage_id": "S05",
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "primary",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S05",
                    "validator_ref": "stage_overlay:nature_expert_writing:S05"
                }
            ],
            "stage_name": "Paper spine and reader-question synthesis",
            "status": "validated",
            "worker_packet_status": "linked_strict_packet"
        },
        {
            "contract_ref": "examples/stage-contracts/S06.stage-contract.json",
            "coverage_kind": "source_projected",
            "exercise_level": "full_stage_exercised",
            "run_ref": "stage-runs/S06.pilot-stage-run.json",
            "stage_id": "S06",
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "primary",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S06",
                    "validator_ref": "stage_overlay:nature_expert_writing:S06"
                }
            ],
            "stage_name": "Object representation and granularity design",
            "status": "validated",
            "worker_packet_status": "linked_strict_packet"
        },
        {
            "contract_ref": "examples/stage-contracts/S07.stage-contract.json",
            "coverage_kind": "fixture_generated",
            "exercise_level": "full_stage_exercised",
            "run_ref": "stage-runs/S07.pilot-stage-run.json",
            "stage_id": "S07",
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "primary",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S07",
                    "validator_ref": "stage_overlay:nature_expert_writing:S07"
                }
            ],
            "stage_name": "Rhetoric terminology and surface-control synthesis",
            "status": "validated",
            "worker_packet_status": "linked_strict_packet"
        },
        {
            "contract_ref": "examples/stage-contracts/S08.stage-contract.json",
            "coverage_kind": "source_projected",
            "exercise_level": "full_stage_exercised",
            "run_ref": "stage-runs/S08.pilot-stage-run.json",
            "stage_id": "S08",
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "primary",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S08",
                    "validator_ref": "stage_overlay:nature_expert_writing:S08"
                }
            ],
            "stage_name": "Visual and formal object planning",
            "status": "validated",
            "worker_packet_status": "linked_strict_packet"
        },
        {
            "contract_ref": "examples/stage-contracts/S09A.stage-contract.json",
            "coverage_kind": "script_checked",
            "exercise_level": "full_stage_exercised",
            "run_ref": "stage-runs/S09A.pilot-stage-run.json",
            "stage_id": "S09A",
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "primary",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S09A",
                    "validator_ref": "stage_overlay:nature_expert_writing:S09A"
                }
            ],
            "stage_name": "Control-material selection",
            "status": "validated",
            "worker_packet_status": "not_required"
        },
        {
            "contract_ref": "examples/stage-contracts/S09B.stage-contract.json",
            "coverage_kind": "script_checked",
            "exercise_level": "full_stage_exercised",
            "run_ref": "stage-runs/S09B.pilot-stage-run.json",
            "stage_id": "S09B",
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "primary",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S09B",
                    "validator_ref": "stage_overlay:nature_expert_writing:S09B"
                }
            ],
            "stage_name": "Per-unit task packet assembly",
            "status": "validated",
            "worker_packet_status": "not_required"
        },
        {
            "contract_ref": "examples/stage-contracts/S10.stage-contract.json",
            "coverage_kind": "source_projected",
            "exercise_level": "full_stage_exercised",
            "run_ref": "stage-runs/S10.pilot-stage-run.json",
            "stage_id": "S10",
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "primary",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S10",
                    "validator_ref": "stage_overlay:nature_expert_writing:S10"
                }
            ],
            "stage_name": "Main-text production",
            "status": "validated",
            "worker_packet_status": "linked_strict_packet"
        },
        {
            "contract_ref": "examples/stage-contracts/S11.stage-contract.json",
            "coverage_kind": "source_projected",
            "exercise_level": "full_stage_exercised",
            "run_ref": "stage-runs/S11.pilot-stage-run.json",
            "stage_id": "S11",
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "primary",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S11",
                    "validator_ref": "stage_overlay:nature_expert_writing:S11"
                }
            ],
            "stage_name": "Figure caption formal artifact production",
            "status": "validated",
            "worker_packet_status": "linked_strict_packet"
        },
        {
            "contract_ref": "examples/stage-contracts/S12.stage-contract.json",
            "coverage_kind": "fixture_generated",
            "exercise_level": "full_stage_exercised",
            "run_ref": "stage-runs/S12.pilot-stage-run.json",
            "stage_id": "S12",
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "primary",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S12",
                    "validator_ref": "stage_overlay:nature_expert_writing:S12"
                }
            ],
            "stage_name": "Integration and consistency pass",
            "status": "validated",
            "worker_packet_status": "linked_strict_packet"
        },
        {
            "contract_ref": "examples/stage-contracts/S13.stage-contract.json",
            "coverage_kind": "fixture_generated",
            "exercise_level": "full_stage_exercised",
            "run_ref": "stage-runs/S13.pilot-stage-run.json",
            "stage_id": "S13",
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "primary",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S13",
                    "validator_ref": "stage_overlay:nature_expert_writing:S13"
                }
            ],
            "stage_name": "Adversarial manuscript review",
            "status": "validated",
            "worker_packet_status": "linked_strict_packet"
        },
        {
            "contract_ref": "examples/stage-contracts/S14.stage-contract.json",
            "coverage_kind": "script_checked",
            "exercise_level": "full_stage_exercised",
            "run_ref": "stage-runs/S14.pilot-stage-run.json",
            "stage_id": "S14",
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "primary",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S14",
                    "validator_ref": "stage_overlay:nature_expert_writing:S14"
                }
            ],
            "stage_name": "Backflow compilation and repair planning",
            "status": "validated",
            "worker_packet_status": "not_required"
        },
        {
            "contract_ref": "examples/stage-contracts/S15.stage-contract.json",
            "coverage_kind": "fixture_generated",
            "exercise_level": "full_stage_exercised",
            "run_ref": "stage-runs/S15.pilot-stage-run.json",
            "stage_id": "S15",
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "primary",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S15",
                    "validator_ref": "stage_overlay:nature_expert_writing:S15"
                }
            ],
            "stage_name": "Repair execution and local regeneration",
            "status": "validated",
            "worker_packet_status": "linked_strict_packet"
        },
        {
            "contract_ref": "examples/stage-contracts/S16.stage-contract.json",
            "coverage_kind": "script_checked",
            "exercise_level": "full_stage_exercised",
            "run_ref": "stage-runs/S16.pilot-stage-run.json",
            "stage_id": "S16",
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "primary",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "S16",
                    "validator_ref": "stage_overlay:nature_expert_writing:S16"
                }
            ],
            "stage_name": "Export repository hygiene and handoff",
            "status": "validated",
            "worker_packet_status": "not_required"
        },
        {
            "contract_ref": "examples/stage-contracts/G01.stage-contract.json",
            "coverage_kind": "script_checked",
            "exercise_level": "full_stage_exercised",
            "run_ref": "stage-runs/G01.pilot-stage-run.json",
            "stage_id": "G01",
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "governance",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "G01",
                    "validator_ref": "stage_overlay:nature_expert_writing:G01"
                }
            ],
            "stage_name": "Runtime governance registry",
            "status": "validated",
            "worker_packet_status": "not_required"
        },
        {
            "contract_ref": "examples/stage-contracts/G02.stage-contract.json",
            "coverage_kind": "owner_gated_deferred",
            "exercise_level": "deferred_with_gate",
            "run_ref": "stage-runs/G02.pilot-stage-run.json",
            "stage_id": "G02",
            "stage_local_overlays": [
                {
                    "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                    "binding_strength": "derivative",
                    "overlay_id": "nature_expert_writing",
                    "registry_ref": "runtime/stage_overlay_registry.json",
                    "stage_id": "G02",
                    "validator_ref": "stage_overlay:nature_expert_writing:G02"
                }
            ],
            "stage_name": "Derivative and post-paper outputs",
            "status": "owner_gated",
            "worker_packet_status": "not_required"
        }
    ],
    "worker_task_packet_status_counts": {
        "linked_strict_packet": 12,
        "not_required": 8
    }
};

  const stageRunDetails = {
    "S00": {
        "stage_id": "S00",
        "stage_name": "Owner semantic contract",
        "status": "validated",
        "coverage_kind": "source_projected",
        "exercise_level": "full_stage_exercised",
        "execution_mode": "owner_gated",
        "recommended_agent_type": "main",
        "contract_ref": "examples/stage-contracts/S00.stage-contract.json",
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "contract": {
            "purpose": "Convert human need into bounded paper commitments and owner decisions.",
            "activation_policy": "activate when owner motivation, venue, claim scope, or private-source policy is unclear",
            "completion_gate": "confirmed owner decision or recorded owner-gated assumption; no worker may silently change this stage",
            "consumes": [
                "human need",
                "paper profile",
                "evidence summary"
            ],
            "produces": [
                "paper-profile",
                "motivation",
                "decisions",
                "blocked routes"
            ],
            "validators": [
                "owner confirmation",
                "blocked route check",
                "owner decision trace",
                "claim scope boundary",
                "source/privacy policy boundary",
                "external action boundary",
                "no worker semantic change",
                "downstream stale/backflow effects",
                "no completion or submission overclaim"
            ],
            "backflow_targets": [
                "owner"
            ],
            "requires_worker_task_packet": false,
            "worker_packet_coverage": {
                "blocker": "Stage is owner-gated, script-generated, or main-controller assembly; fake worker packets are forbidden.",
                "packet_ref": null,
                "return_contract_ref": null,
                "status": "not_required"
            },
            "subagent_lane_policy": {
                "policy": "conditional_double",
                "default_lane_count": 1,
                "producer_agent_type": "main",
                "verifier_agent_type": "verifier",
                "escalate_to_double_when": [
                    "owner semantic contract changes",
                    "venue or claim-scope freeze",
                    "owner requests independent challenge"
                ],
                "rationale": "Owner semantics are controller-owned; a second lane is needed only when commitments change or freeze."
            },
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            }
        },
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s00_declared_input_1",
                "ref": "human need"
            },
            {
                "kind": "contract_declared",
                "material_id": "s00_declared_input_2",
                "ref": "paper profile"
            },
            {
                "kind": "contract_declared",
                "material_id": "s00_declared_input_3",
                "ref": "evidence summary"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s00_source_ref_readme-md",
                "ref": "README.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s00_source_ref_handoff-md",
                "ref": "HANDOFF.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s00_source_ref_project-status-md",
                "ref": "PROJECT_STATUS.md"
            }
        ],
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s00_declared_input_1",
                "ref": "human need"
            },
            {
                "kind": "contract_declared",
                "material_id": "s00_declared_input_2",
                "ref": "paper profile"
            },
            {
                "kind": "contract_declared",
                "material_id": "s00_declared_input_3",
                "ref": "evidence summary"
            }
        ],
        "upstream_inputs": [],
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s00_source_ref_readme-md",
                "ref": "README.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s00_source_ref_handoff-md",
                "ref": "HANDOFF.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s00_source_ref_project-status-md",
                "ref": "PROJECT_STATUS.md"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s00_pilot_output",
                "artifact_path": "artifacts/S00-owner-semantic-contract.json",
                "artifact_type": "owner_gate_projection",
                "description": "paper-profile; motivation; decisions; blocked routes",
                "payload": {
                    "artifact_kind": "owner_gate_projection",
                    "purpose": "Convert human need into bounded paper commitments and owner decisions.",
                    "projected_outputs": [
                        "paper-profile",
                        "motivation",
                        "decisions",
                        "blocked routes"
                    ],
                    "consumed_ref_count": 6,
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "light",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S00",
                            "validator_ref": "stage_overlay:nature_expert_writing:S00"
                        }
                    ]
                }
            }
        ],
        "handoff_consumers": [
            {
                "stage_id": "S01",
                "stage_name": "Source citation evidence inventory",
                "material_id": "s00_pilot_output",
                "ref": "artifacts/S00-owner-semantic-contract.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S00 links to examples/stage-contracts/S00.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=source_projected; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S00 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": "Stage is owner-gated, script-generated, or main-controller assembly; fake worker packets are forbidden.",
            "packet_ref": null,
            "required": false,
            "return_contract_ref": null,
            "status": "not_required"
        },
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "light",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S00",
                "validator_ref": "stage_overlay:nature_expert_writing:S00"
            }
        ],
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        }
    },
    "S01": {
        "stage_id": "S01",
        "stage_name": "Source citation evidence inventory",
        "status": "validated",
        "coverage_kind": "source_projected",
        "exercise_level": "full_stage_exercised",
        "execution_mode": "hybrid_generated",
        "recommended_agent_type": "explore",
        "contract_ref": "examples/stage-contracts/S01.stage-contract.json",
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "contract": {
            "purpose": "Make raw paper inputs locatable and support-safe.",
            "activation_policy": "activate when source or evidence inventory is missing/stale",
            "completion_gate": "claim-relevant sources are locator-backed or explicitly unresolved",
            "consumes": [
                "initial files",
                "result dirs",
                "BibTeX",
                "source locators"
            ],
            "produces": [
                "source map",
                "citation bank",
                "evidence bank"
            ],
            "validators": [
                "source locator resolution",
                "privacy boundary check",
                "evidence path check",
                "S01_read_only_boundary",
                "S01_root_coverage",
                "S01_source_locator_resolution",
                "S01_bibtex_key_coverage",
                "S01_evidence_artifact_locator",
                "S01_figure_source_data_locator",
                "S01_supplement_inventory",
                "S01_privacy_boundary",
                "S01_freshness_hash_report",
                "S01_no_claim_admissibility",
                "S01_unresolved_locator_register",
                "S01_no_completion_overclaim"
            ],
            "backflow_targets": [
                "S00",
                "S04"
            ],
            "requires_worker_task_packet": false,
            "worker_packet_coverage": {
                "blocker": "S01 uses read-only inventory briefs only; fake graph-mutation worker packets are forbidden.",
                "packet_ref": null,
                "return_contract_ref": null,
                "status": "not_required"
            },
            "subagent_lane_policy": {
                "policy": "conditional_double",
                "default_lane_count": 1,
                "producer_agent_type": "explore",
                "verifier_agent_type": "verifier",
                "escalate_to_double_when": [
                    "new source family is admitted",
                    "citation/evidence support is uncertain",
                    "pre-writing inventory freeze"
                ],
                "rationale": "Inventory work is mostly structural but needs independent verification when source support or evidence admissibility is uncertain."
            },
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true,
                "source_write_forbidden": true,
                "inventory_candidate_only": true,
                "claim_admissibility_forbidden": true
            }
        },
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s01_declared_input_1",
                "ref": "initial files"
            },
            {
                "kind": "contract_declared",
                "material_id": "s01_declared_input_2",
                "ref": "result dirs"
            },
            {
                "kind": "contract_declared",
                "material_id": "s01_declared_input_3",
                "ref": "BibTeX"
            },
            {
                "kind": "contract_declared",
                "material_id": "s01_declared_input_4",
                "ref": "source locators"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s01_source_ref_readme-md",
                "ref": "README.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s01_source_ref_handoff-md",
                "ref": "HANDOFF.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s01_source_ref_docs-current-plan-md",
                "ref": "docs/CURRENT_PLAN.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s01_source_ref_docs-latest-sync-brief-md",
                "ref": "docs/LATEST_SYNC_BRIEF.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s01_source_ref_paper-os-materials-current-material-index-json",
                "ref": "paper-os/materials/current-material-index.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s00_pilot_output",
                "producer_stage_id": "S00",
                "ref": "artifacts/S00-owner-semantic-contract.json"
            }
        ],
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s01_declared_input_1",
                "ref": "initial files"
            },
            {
                "kind": "contract_declared",
                "material_id": "s01_declared_input_2",
                "ref": "result dirs"
            },
            {
                "kind": "contract_declared",
                "material_id": "s01_declared_input_3",
                "ref": "BibTeX"
            },
            {
                "kind": "contract_declared",
                "material_id": "s01_declared_input_4",
                "ref": "source locators"
            }
        ],
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s00_pilot_output",
                "producer_stage_id": "S00",
                "ref": "artifacts/S00-owner-semantic-contract.json"
            }
        ],
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s01_source_ref_readme-md",
                "ref": "README.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s01_source_ref_handoff-md",
                "ref": "HANDOFF.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s01_source_ref_docs-current-plan-md",
                "ref": "docs/CURRENT_PLAN.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s01_source_ref_docs-latest-sync-brief-md",
                "ref": "docs/LATEST_SYNC_BRIEF.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s01_source_ref_paper-os-materials-current-material-index-json",
                "ref": "paper-os/materials/current-material-index.json"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s01_pilot_output",
                "artifact_path": "artifacts/S01-source-citation-evidence-inventory.json",
                "artifact_type": "analysis_material_projection",
                "description": "source map; citation bank; evidence bank",
                "payload": {
                    "artifact_kind": "analysis_material_projection",
                    "purpose": "Make raw paper inputs locatable and support-safe.",
                    "projected_outputs": [
                        "source map",
                        "citation bank",
                        "evidence bank"
                    ],
                    "consumed_ref_count": 10,
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "light",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S01",
                            "validator_ref": "stage_overlay:nature_expert_writing:S01"
                        }
                    ]
                }
            }
        ],
        "handoff_consumers": [
            {
                "stage_id": "S02",
                "stage_name": "Research scene exemplar SOTA analysis",
                "material_id": "s01_pilot_output",
                "ref": "artifacts/S01-source-citation-evidence-inventory.json"
            },
            {
                "stage_id": "S04",
                "stage_name": "Evidence-to-claim admissibility",
                "material_id": "s01_pilot_output",
                "ref": "artifacts/S01-source-citation-evidence-inventory.json"
            },
            {
                "stage_id": "S11",
                "stage_name": "Figure caption formal artifact production",
                "material_id": "s01_pilot_output",
                "ref": "artifacts/S01-source-citation-evidence-inventory.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S01 links to examples/stage-contracts/S01.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=source_projected; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S01 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": "S01 uses read-only inventory briefs only; fake graph-mutation worker packets are forbidden.",
            "packet_ref": null,
            "required": false,
            "return_contract_ref": null,
            "status": "not_required"
        },
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "light",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S01",
                "validator_ref": "stage_overlay:nature_expert_writing:S01"
            }
        ],
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        }
    },
    "S02": {
        "stage_id": "S02",
        "stage_name": "Research scene exemplar SOTA analysis",
        "status": "validated",
        "coverage_kind": "source_projected",
        "exercise_level": "full_stage_exercised",
        "execution_mode": "agent_generated",
        "recommended_agent_type": "researcher",
        "contract_ref": "examples/stage-contracts/S02.stage-contract.json",
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "contract": {
            "purpose": "Understand field scene, template expectations, exemplar structure, and related-work positioning.",
            "activation_policy": "activate when field/template/SOTA is uncertain",
            "completion_gate": "research dossier and template/profile outputs are source-located and safe to consume",
            "consumes": [
                "source map",
                "citation bank",
                "venue route",
                "exemplar locators"
            ],
            "produces": [
                "research dossier",
                "reader package",
                "template profile",
                "citation verification report"
            ],
            "validators": [
                "S02_source_coverage_ledger",
                "S02_sota_family_coverage_ledger",
                "S02_template_language_profile",
                "S02_descriptive_not_prescriptive",
                "S02_template_copying_boundary",
                "S02_unresolved_backflow_register",
                "S02_downstream_handoff_coverage",
                "S02_no_claim_or_completion_freeze"
            ],
            "backflow_targets": [
                "S01",
                "S00"
            ],
            "requires_worker_task_packet": true,
            "worker_packet_coverage": {
                "blocker": null,
                "packet_ref": "examples/packets/phase10_s02_sota_analysis_packet.v1.yaml",
                "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
                "status": "linked_strict_packet"
            },
            "subagent_lane_policy": {
                "policy": "mandatory_double",
                "default_lane_count": 2,
                "producer_agent_type": "researcher",
                "verifier_agent_type": "verifier",
                "escalate_to_double_when": [
                    "always for normal paper-facing production",
                    "full-flow QA mode",
                    "milestone or freeze gate"
                ],
                "rationale": "Research/SOTA materials shape all downstream claims, so producer output must be independently checked before commit."
            },
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            }
        },
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s02_declared_input_1",
                "ref": "source map"
            },
            {
                "kind": "contract_declared",
                "material_id": "s02_declared_input_2",
                "ref": "citation bank"
            },
            {
                "kind": "contract_declared",
                "material_id": "s02_declared_input_3",
                "ref": "venue route"
            },
            {
                "kind": "contract_declared",
                "material_id": "s02_declared_input_4",
                "ref": "exemplar locators"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s02_source_ref_references-readme-md",
                "ref": "references/README.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s02_source_ref_references-citation-workspace-map-md",
                "ref": "references/citation-workspace-map.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s02_source_ref_docs-current-plan-md",
                "ref": "docs/CURRENT_PLAN.md"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s01_pilot_output",
                "producer_stage_id": "S01",
                "ref": "artifacts/S01-source-citation-evidence-inventory.json"
            }
        ],
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s02_declared_input_1",
                "ref": "source map"
            },
            {
                "kind": "contract_declared",
                "material_id": "s02_declared_input_2",
                "ref": "citation bank"
            },
            {
                "kind": "contract_declared",
                "material_id": "s02_declared_input_3",
                "ref": "venue route"
            },
            {
                "kind": "contract_declared",
                "material_id": "s02_declared_input_4",
                "ref": "exemplar locators"
            }
        ],
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s01_pilot_output",
                "producer_stage_id": "S01",
                "ref": "artifacts/S01-source-citation-evidence-inventory.json"
            }
        ],
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s02_source_ref_references-readme-md",
                "ref": "references/README.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s02_source_ref_references-citation-workspace-map-md",
                "ref": "references/citation-workspace-map.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s02_source_ref_docs-current-plan-md",
                "ref": "docs/CURRENT_PLAN.md"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s02_pilot_output",
                "artifact_path": "artifacts/S02-research-scene-exemplar-sota-analysis.json",
                "artifact_type": "analysis_material_projection",
                "description": "research dossier; reader package; template profile; citation verification report",
                "payload": {
                    "artifact_kind": "analysis_material_projection",
                    "purpose": "Understand field scene, template expectations, exemplar structure, and related-work positioning.",
                    "projected_outputs": [
                        "research dossier",
                        "reader package",
                        "template profile",
                        "citation verification report"
                    ],
                    "consumed_ref_count": 8,
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "primary",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S02",
                            "validator_ref": "stage_overlay:nature_expert_writing:S02"
                        }
                    ]
                }
            }
        ],
        "handoff_consumers": [
            {
                "stage_id": "S03",
                "stage_name": "Novelty and contribution option analysis",
                "material_id": "s02_pilot_output",
                "ref": "artifacts/S02-research-scene-exemplar-sota-analysis.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S02 links to examples/stage-contracts/S02.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=source_projected; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S02 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": null,
            "packet_ref": "examples/packets/phase10_s02_sota_analysis_packet.v1.yaml",
            "required": true,
            "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
            "status": "linked_strict_packet"
        },
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "primary",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S02",
                "validator_ref": "stage_overlay:nature_expert_writing:S02"
            }
        ],
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        }
    },
    "S03": {
        "stage_id": "S03",
        "stage_name": "Novelty and contribution option analysis",
        "status": "validated",
        "coverage_kind": "source_projected",
        "exercise_level": "full_stage_exercised",
        "execution_mode": "agent_generated",
        "recommended_agent_type": "critic",
        "contract_ref": "examples/stage-contracts/S03.stage-contract.json",
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "contract": {
            "purpose": "Identify viable contribution framings without treating speculation as evidence.",
            "activation_policy": "activate when contribution is unstable or weak",
            "completion_gate": "viable options are classified as supported, owner-gated, or rejected",
            "consumes": [
                "research dossier",
                "evidence inventory",
                "motivation",
                "SOTA map"
            ],
            "produces": [
                "contribution options",
                "novelty readiness",
                "risk list"
            ],
            "validators": [
                "S03_contribution_option_queue",
                "S03_option_coverage_ledger",
                "S03_sota_contrast_matrix",
                "S03_evidence_readiness_classifier",
                "S03_rejected_option_register",
                "S03_owner_gated_option_register",
                "S03_reviewer_attack_map",
                "S03_s04_handoff_coverage",
                "S03_no_claim_admissibility_or_final_wording",
                "S03_no_completion_overclaim"
            ],
            "backflow_targets": [
                "S00",
                "S02",
                "S04"
            ],
            "requires_worker_task_packet": true,
            "worker_packet_coverage": {
                "blocker": null,
                "packet_ref": "examples/packets/phase10_s03_novelty_analysis_packet.v1.yaml",
                "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
                "status": "linked_strict_packet"
            },
            "subagent_lane_policy": {
                "policy": "mandatory_double",
                "default_lane_count": 2,
                "producer_agent_type": "critic",
                "verifier_agent_type": "verifier",
                "escalate_to_double_when": [
                    "always for normal paper-facing production",
                    "full-flow QA mode",
                    "milestone or freeze gate"
                ],
                "rationale": "Novelty framing is high-risk and speculative by nature; independent challenge prevents unsupported contribution claims."
            },
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            }
        },
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s03_declared_input_1",
                "ref": "research dossier"
            },
            {
                "kind": "contract_declared",
                "material_id": "s03_declared_input_2",
                "ref": "evidence inventory"
            },
            {
                "kind": "contract_declared",
                "material_id": "s03_declared_input_3",
                "ref": "motivation"
            },
            {
                "kind": "contract_declared",
                "material_id": "s03_declared_input_4",
                "ref": "SOTA map"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s03_source_ref_readme-md",
                "ref": "README.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s03_source_ref_handoff-md",
                "ref": "HANDOFF.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s03_source_ref_project-status-md",
                "ref": "PROJECT_STATUS.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s03_source_ref_manuscript-sections-01-introduction-tex",
                "ref": "manuscript/sections/01_introduction.tex"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s02_pilot_output",
                "producer_stage_id": "S02",
                "ref": "artifacts/S02-research-scene-exemplar-sota-analysis.json"
            }
        ],
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s03_declared_input_1",
                "ref": "research dossier"
            },
            {
                "kind": "contract_declared",
                "material_id": "s03_declared_input_2",
                "ref": "evidence inventory"
            },
            {
                "kind": "contract_declared",
                "material_id": "s03_declared_input_3",
                "ref": "motivation"
            },
            {
                "kind": "contract_declared",
                "material_id": "s03_declared_input_4",
                "ref": "SOTA map"
            }
        ],
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s02_pilot_output",
                "producer_stage_id": "S02",
                "ref": "artifacts/S02-research-scene-exemplar-sota-analysis.json"
            }
        ],
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s03_source_ref_readme-md",
                "ref": "README.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s03_source_ref_handoff-md",
                "ref": "HANDOFF.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s03_source_ref_project-status-md",
                "ref": "PROJECT_STATUS.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s03_source_ref_manuscript-sections-01-introduction-tex",
                "ref": "manuscript/sections/01_introduction.tex"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s03_pilot_output",
                "artifact_path": "artifacts/S03-novelty-and-contribution-option-analysis.json",
                "artifact_type": "analysis_material_projection",
                "description": "contribution options; novelty readiness; risk list",
                "payload": {
                    "artifact_kind": "analysis_material_projection",
                    "purpose": "Identify viable contribution framings without treating speculation as evidence.",
                    "projected_outputs": [
                        "contribution options",
                        "novelty readiness",
                        "risk list"
                    ],
                    "consumed_ref_count": 9,
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "support",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S03",
                            "validator_ref": "stage_overlay:nature_expert_writing:S03"
                        }
                    ]
                }
            }
        ],
        "handoff_consumers": [
            {
                "stage_id": "S04",
                "stage_name": "Evidence-to-claim admissibility",
                "material_id": "s03_pilot_output",
                "ref": "artifacts/S03-novelty-and-contribution-option-analysis.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S03 links to examples/stage-contracts/S03.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=source_projected; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S03 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": null,
            "packet_ref": "examples/packets/phase10_s03_novelty_analysis_packet.v1.yaml",
            "required": true,
            "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
            "status": "linked_strict_packet"
        },
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "support",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S03",
                "validator_ref": "stage_overlay:nature_expert_writing:S03"
            }
        ],
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        }
    },
    "S04": {
        "stage_id": "S04",
        "stage_name": "Evidence-to-claim admissibility",
        "status": "validated",
        "coverage_kind": "source_projected",
        "exercise_level": "full_stage_exercised",
        "execution_mode": "hybrid_generated",
        "recommended_agent_type": "verifier",
        "contract_ref": "examples/stage-contracts/S04.stage-contract.json",
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "contract": {
            "purpose": "Admit, weaken, reject, or backflow every claim-bearing unit against evidence anchors, support strength, allowed wording, forbidden wording, and result-package boundaries.",
            "activation_policy": "activate before claim-bearing writing or review",
            "completion_gate": "every claim-bearing unit is admitted, weakened, rejected, owner-gated, or backflowed with support strength, evidence anchor, allowed wording, forbidden wording, result boundary, and downstream permission",
            "consumes": [
                "evidence bank",
                "citation bank",
                "result artifacts",
                "contribution options"
            ],
            "produces": [
                "claim citation capsules",
                "result packages",
                "claim evidence visibility",
                "data availability plan"
            ],
            "validators": [
                "S04_claim_queue",
                "S04_atomic_claim_register",
                "S04_claim_capsules",
                "S04_claim_coverage_ledger",
                "S04_support_strength_map",
                "S04_evidence_anchor_visibility",
                "S04_allowed_forbidden_wording",
                "S04_result_package_boundary",
                "S04_claim_transformation_log",
                "S04_downstream_handoff_coverage",
                "S04_no_final_prose_or_completion_overclaim"
            ],
            "backflow_targets": [
                "S01",
                "S03",
                "S00"
            ],
            "requires_worker_task_packet": true,
            "worker_packet_coverage": {
                "blocker": null,
                "packet_ref": "examples/packets/phase10_s04_evidence_claim_admissibility_packet.v1.yaml",
                "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
                "status": "linked_strict_packet"
            },
            "subagent_lane_policy": {
                "policy": "mandatory_double",
                "default_lane_count": 2,
                "producer_agent_type": "verifier",
                "verifier_agent_type": "verifier",
                "escalate_to_double_when": [
                    "always for normal paper-facing production",
                    "full-flow QA mode",
                    "milestone or freeze gate"
                ],
                "rationale": "Claim-evidence admissibility is a safety-critical gate; production and verification must remain separate."
            },
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            }
        },
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s04_declared_input_1",
                "ref": "evidence bank"
            },
            {
                "kind": "contract_declared",
                "material_id": "s04_declared_input_2",
                "ref": "citation bank"
            },
            {
                "kind": "contract_declared",
                "material_id": "s04_declared_input_3",
                "ref": "result artifacts"
            },
            {
                "kind": "contract_declared",
                "material_id": "s04_declared_input_4",
                "ref": "contribution options"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s04_source_ref_paper-os-materials-current-material-index-json",
                "ref": "paper-os/materials/current-material-index.json"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s04_source_ref_claims-readme-md",
                "ref": "claims/README.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s04_source_ref_experiments-results-l3-method-faithful-unified-s",
                "ref": "experiments/results/L3_method_faithful_unified_scene_20260625/manifest.json"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s04_source_ref_manuscript-sections-05-experiments-tex",
                "ref": "manuscript/sections/05_experiments.tex"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s01_pilot_output",
                "producer_stage_id": "S01",
                "ref": "artifacts/S01-source-citation-evidence-inventory.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s03_pilot_output",
                "producer_stage_id": "S03",
                "ref": "artifacts/S03-novelty-and-contribution-option-analysis.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s14_pilot_output",
                "producer_stage_id": "S14",
                "ref": "artifacts/S14-backflow-compilation-and-repair-planning.json"
            }
        ],
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s04_declared_input_1",
                "ref": "evidence bank"
            },
            {
                "kind": "contract_declared",
                "material_id": "s04_declared_input_2",
                "ref": "citation bank"
            },
            {
                "kind": "contract_declared",
                "material_id": "s04_declared_input_3",
                "ref": "result artifacts"
            },
            {
                "kind": "contract_declared",
                "material_id": "s04_declared_input_4",
                "ref": "contribution options"
            }
        ],
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s01_pilot_output",
                "producer_stage_id": "S01",
                "ref": "artifacts/S01-source-citation-evidence-inventory.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s03_pilot_output",
                "producer_stage_id": "S03",
                "ref": "artifacts/S03-novelty-and-contribution-option-analysis.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s14_pilot_output",
                "producer_stage_id": "S14",
                "ref": "artifacts/S14-backflow-compilation-and-repair-planning.json"
            }
        ],
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s04_source_ref_paper-os-materials-current-material-index-json",
                "ref": "paper-os/materials/current-material-index.json"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s04_source_ref_claims-readme-md",
                "ref": "claims/README.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s04_source_ref_experiments-results-l3-method-faithful-unified-s",
                "ref": "experiments/results/L3_method_faithful_unified_scene_20260625/manifest.json"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s04_source_ref_manuscript-sections-05-experiments-tex",
                "ref": "manuscript/sections/05_experiments.tex"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s04_pilot_output",
                "artifact_path": "artifacts/S04-evidence-to-claim-admissibility.json",
                "artifact_type": "analysis_material_projection",
                "description": "claim citation capsules; result packages; claim evidence visibility; data availability plan",
                "payload": {
                    "artifact_kind": "analysis_material_projection",
                    "purpose": "Admit, weaken, reject, or backflow every claim-bearing unit against evidence anchors, support strength, allowed wording, forbidden wording, and result-package boundaries.",
                    "projected_outputs": [
                        "claim citation capsules",
                        "result packages",
                        "claim evidence visibility",
                        "data availability plan"
                    ],
                    "consumed_ref_count": 11,
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "primary",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S04",
                            "validator_ref": "stage_overlay:nature_expert_writing:S04"
                        }
                    ]
                }
            }
        ],
        "handoff_consumers": [
            {
                "stage_id": "S05",
                "stage_name": "Paper spine and reader-question synthesis",
                "material_id": "s04_pilot_output",
                "ref": "artifacts/S04-evidence-to-claim-admissibility.json"
            },
            {
                "stage_id": "S08",
                "stage_name": "Visual and formal object planning",
                "material_id": "s04_pilot_output",
                "ref": "artifacts/S04-evidence-to-claim-admissibility.json"
            },
            {
                "stage_id": "S09A",
                "stage_name": "Control-material selection",
                "material_id": "s04_pilot_output",
                "ref": "artifacts/S04-evidence-to-claim-admissibility.json"
            },
            {
                "stage_id": "S11",
                "stage_name": "Figure caption formal artifact production",
                "material_id": "s04_pilot_output",
                "ref": "artifacts/S04-evidence-to-claim-admissibility.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S04 links to examples/stage-contracts/S04.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=source_projected; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S04 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": null,
            "packet_ref": "examples/packets/phase10_s04_evidence_claim_admissibility_packet.v1.yaml",
            "required": true,
            "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
            "status": "linked_strict_packet"
        },
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "primary",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S04",
                "validator_ref": "stage_overlay:nature_expert_writing:S04"
            }
        ],
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        }
    },
    "S05": {
        "stage_id": "S05",
        "stage_name": "Paper spine and reader-question synthesis",
        "status": "validated",
        "coverage_kind": "source_projected",
        "exercise_level": "full_stage_exercised",
        "execution_mode": "agent_generated",
        "recommended_agent_type": "architect",
        "contract_ref": "examples/stage-contracts/S05.stage-contract.json",
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "contract": {
            "purpose": "Build a claim-bounded reader-question spine from S04-admitted claim capsules, with coverage ledgers and downstream S06/S07/S08 handoffs; no new claims or final prose.",
            "activation_policy": "activate for new section or major rewrite",
            "completion_gate": "S05ReaderSpine validates every S04 intake claim, reader question, section placement, promise payoff, owner decision, and S06/S07/S08 handoff without new claims or final prose",
            "consumes": [
                "motivation",
                "contribution options",
                "template profile",
                "claim materials"
            ],
            "produces": [
                "reader spine",
                "reviewer question map",
                "rationale matrix"
            ],
            "validators": [
                "S05_admitted_claim_intake_ledger",
                "S05_reader_question_inventory",
                "S05_reader_question_coverage_ledger",
                "S05_reader_question_progression",
                "S05_claim_to_section_spine",
                "S05_claim_section_coverage_ledger",
                "S05_front_half_promise_coverage",
                "S05_reviewer_question_map",
                "S05_rationale_matrix",
                "S05_owner_decision_log",
                "S05_s06_s07_s08_handoff_coverage",
                "S05_coherence_overpromise_audit",
                "S05_no_new_claims_or_final_prose",
                "S05_no_completion_overclaim"
            ],
            "backflow_targets": [
                "S00",
                "S03",
                "S04"
            ],
            "requires_worker_task_packet": true,
            "worker_packet_coverage": {
                "blocker": null,
                "packet_ref": "examples/packets/phase10_s05_paper_spine_synthesis_packet.v1.yaml",
                "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
                "status": "linked_strict_packet"
            },
            "subagent_lane_policy": {
                "policy": "mandatory_double",
                "default_lane_count": 2,
                "producer_agent_type": "architect",
                "verifier_agent_type": "verifier",
                "escalate_to_double_when": [
                    "always for normal paper-facing production",
                    "full-flow QA mode",
                    "milestone or freeze gate"
                ],
                "rationale": "The paper spine controls global argument order; independent challenge catches incoherent or unsupported reader paths."
            },
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            }
        },
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s05_declared_input_1",
                "ref": "motivation"
            },
            {
                "kind": "contract_declared",
                "material_id": "s05_declared_input_2",
                "ref": "contribution options"
            },
            {
                "kind": "contract_declared",
                "material_id": "s05_declared_input_3",
                "ref": "template profile"
            },
            {
                "kind": "contract_declared",
                "material_id": "s05_declared_input_4",
                "ref": "claim materials"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s05_source_ref_manuscript-sections-01-introduction-tex",
                "ref": "manuscript/sections/01_introduction.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s05_source_ref_manuscript-sections-03-problem-formulation-tex",
                "ref": "manuscript/sections/03_problem_formulation.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s05_source_ref_manuscript-sections-04-method-tex",
                "ref": "manuscript/sections/04_method.tex"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s04_pilot_output",
                "producer_stage_id": "S04",
                "ref": "artifacts/S04-evidence-to-claim-admissibility.json"
            }
        ],
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s05_declared_input_1",
                "ref": "motivation"
            },
            {
                "kind": "contract_declared",
                "material_id": "s05_declared_input_2",
                "ref": "contribution options"
            },
            {
                "kind": "contract_declared",
                "material_id": "s05_declared_input_3",
                "ref": "template profile"
            },
            {
                "kind": "contract_declared",
                "material_id": "s05_declared_input_4",
                "ref": "claim materials"
            }
        ],
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s04_pilot_output",
                "producer_stage_id": "S04",
                "ref": "artifacts/S04-evidence-to-claim-admissibility.json"
            }
        ],
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s05_source_ref_manuscript-sections-01-introduction-tex",
                "ref": "manuscript/sections/01_introduction.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s05_source_ref_manuscript-sections-03-problem-formulation-tex",
                "ref": "manuscript/sections/03_problem_formulation.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s05_source_ref_manuscript-sections-04-method-tex",
                "ref": "manuscript/sections/04_method.tex"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s05_pilot_output",
                "artifact_path": "artifacts/S05-paper-spine-and-reader-question-synthesis.json",
                "artifact_type": "analysis_material_projection",
                "description": "reader spine; reviewer question map; rationale matrix",
                "payload": {
                    "artifact_kind": "analysis_material_projection",
                    "purpose": "Build a claim-bounded reader-question spine from S04-admitted claim capsules, with coverage ledgers and downstream S06/S07/S08 handoffs; no new claims or final prose.",
                    "projected_outputs": [
                        "reader spine",
                        "reviewer question map",
                        "rationale matrix"
                    ],
                    "consumed_ref_count": 8,
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "primary",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S05",
                            "validator_ref": "stage_overlay:nature_expert_writing:S05"
                        }
                    ]
                }
            }
        ],
        "handoff_consumers": [
            {
                "stage_id": "S06",
                "stage_name": "Object representation and granularity design",
                "material_id": "s05_pilot_output",
                "ref": "artifacts/S05-paper-spine-and-reader-question-synthesis.json"
            },
            {
                "stage_id": "S08",
                "stage_name": "Visual and formal object planning",
                "material_id": "s05_pilot_output",
                "ref": "artifacts/S05-paper-spine-and-reader-question-synthesis.json"
            },
            {
                "stage_id": "S09A",
                "stage_name": "Control-material selection",
                "material_id": "s05_pilot_output",
                "ref": "artifacts/S05-paper-spine-and-reader-question-synthesis.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S05 links to examples/stage-contracts/S05.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=source_projected; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S05 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": null,
            "packet_ref": "examples/packets/phase10_s05_paper_spine_synthesis_packet.v1.yaml",
            "required": true,
            "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
            "status": "linked_strict_packet"
        },
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "primary",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S05",
                "validator_ref": "stage_overlay:nature_expert_writing:S05"
            }
        ],
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        }
    },
    "S06": {
        "stage_id": "S06",
        "stage_name": "Object representation and granularity design",
        "status": "validated",
        "coverage_kind": "source_projected",
        "exercise_level": "full_stage_exercised",
        "execution_mode": "agent_generated",
        "recommended_agent_type": "architect",
        "contract_ref": "examples/stage-contracts/S06.stage-contract.json",
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "contract": {
            "purpose": "Design complete object and mechanism-variable representation, granularity progression, section/load budgets, explanation ladders, and downstream handoffs without adding claims or drafting prose.",
            "activation_policy": "activate for full paper route or when object repetition risk exists",
            "completion_gate": "S06ObjectGranularity validates object/variable coverage, cards, cross maps, granularity/load budgets, explanation ladders, repetition checks, unresolved objects, and S07/S08/S10 handoffs without new claims or final prose",
            "consumes": [
                "reader spine",
                "reviewer question map",
                "template profile",
                "claim visibility"
            ],
            "produces": [
                "object representation matrix",
                "section function budget",
                "load budget",
                "explanation ladder"
            ],
            "validators": [
                "S06_object_inventory_coverage",
                "S06_mechanism_variable_coverage",
                "S06_object_cards_for_P0_P1_P2",
                "S06_mechanism_variable_cards",
                "S06_claim_object_mapping",
                "S06_reader_question_object_mapping",
                "S06_object_section_mapping",
                "S06_granularity_progression",
                "S06_section_function_budget",
                "S06_cognitive_load_budget",
                "S06_explanation_ladder",
                "S06_no_flat_repetition",
                "S06_coverage_ledger",
                "S06_unresolved_object_report",
                "S06_downstream_handoff",
                "S06_no_new_claims_or_final_prose",
                "S06_no_completion_overclaim"
            ],
            "backflow_targets": [
                "S05",
                "S04"
            ],
            "requires_worker_task_packet": true,
            "worker_packet_coverage": {
                "blocker": null,
                "packet_ref": "examples/packets/phase10_s06_object_granularity_design_packet.v1.yaml",
                "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
                "status": "linked_strict_packet"
            },
            "subagent_lane_policy": {
                "policy": "conditional_double",
                "default_lane_count": 1,
                "producer_agent_type": "architect",
                "verifier_agent_type": "verifier",
                "escalate_to_double_when": [
                    "new object family or granularity ladder is introduced",
                    "multi-section object reuse is planned",
                    "pre-writing design freeze"
                ],
                "rationale": "Object/granularity design is reusable control material; single production is enough unless it changes multi-section semantics."
            },
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            }
        },
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s06_declared_input_1",
                "ref": "reader spine"
            },
            {
                "kind": "contract_declared",
                "material_id": "s06_declared_input_2",
                "ref": "reviewer question map"
            },
            {
                "kind": "contract_declared",
                "material_id": "s06_declared_input_3",
                "ref": "template profile"
            },
            {
                "kind": "contract_declared",
                "material_id": "s06_declared_input_4",
                "ref": "claim visibility"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s06_source_ref_manuscript-sections-03-problem-formulation-tex",
                "ref": "manuscript/sections/03_problem_formulation.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s06_source_ref_manuscript-sections-04-method-tex",
                "ref": "manuscript/sections/04_method.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s06_source_ref_manuscript-sections-06-results-discussion-tex",
                "ref": "manuscript/sections/06_results_discussion.tex"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s05_pilot_output",
                "producer_stage_id": "S05",
                "ref": "artifacts/S05-paper-spine-and-reader-question-synthesis.json"
            }
        ],
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s06_declared_input_1",
                "ref": "reader spine"
            },
            {
                "kind": "contract_declared",
                "material_id": "s06_declared_input_2",
                "ref": "reviewer question map"
            },
            {
                "kind": "contract_declared",
                "material_id": "s06_declared_input_3",
                "ref": "template profile"
            },
            {
                "kind": "contract_declared",
                "material_id": "s06_declared_input_4",
                "ref": "claim visibility"
            }
        ],
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s05_pilot_output",
                "producer_stage_id": "S05",
                "ref": "artifacts/S05-paper-spine-and-reader-question-synthesis.json"
            }
        ],
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s06_source_ref_manuscript-sections-03-problem-formulation-tex",
                "ref": "manuscript/sections/03_problem_formulation.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s06_source_ref_manuscript-sections-04-method-tex",
                "ref": "manuscript/sections/04_method.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s06_source_ref_manuscript-sections-06-results-discussion-tex",
                "ref": "manuscript/sections/06_results_discussion.tex"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s06_pilot_output",
                "artifact_path": "artifacts/S06-object-representation-and-granularity-design.json",
                "artifact_type": "analysis_material_projection",
                "description": "object representation matrix; section function budget; load budget; explanation ladder",
                "payload": {
                    "artifact_kind": "analysis_material_projection",
                    "purpose": "Design complete object and mechanism-variable representation, granularity progression, section/load budgets, explanation ladders, and downstream handoffs without adding claims or drafting prose.",
                    "projected_outputs": [
                        "object representation matrix",
                        "section function budget",
                        "load budget",
                        "explanation ladder"
                    ],
                    "consumed_ref_count": 8,
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "primary",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S06",
                            "validator_ref": "stage_overlay:nature_expert_writing:S06"
                        }
                    ]
                }
            }
        ],
        "handoff_consumers": [
            {
                "stage_id": "S07",
                "stage_name": "Rhetoric terminology and surface-control synthesis",
                "material_id": "s06_pilot_output",
                "ref": "artifacts/S06-object-representation-and-granularity-design.json"
            },
            {
                "stage_id": "S08",
                "stage_name": "Visual and formal object planning",
                "material_id": "s06_pilot_output",
                "ref": "artifacts/S06-object-representation-and-granularity-design.json"
            },
            {
                "stage_id": "S09A",
                "stage_name": "Control-material selection",
                "material_id": "s06_pilot_output",
                "ref": "artifacts/S06-object-representation-and-granularity-design.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S06 links to examples/stage-contracts/S06.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=source_projected; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S06 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": null,
            "packet_ref": "examples/packets/phase10_s06_object_granularity_design_packet.v1.yaml",
            "required": true,
            "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
            "status": "linked_strict_packet"
        },
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "primary",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S06",
                "validator_ref": "stage_overlay:nature_expert_writing:S06"
            }
        ],
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        }
    },
    "S07": {
        "stage_id": "S07",
        "stage_name": "Rhetoric terminology and surface-control synthesis",
        "status": "validated",
        "coverage_kind": "fixture_generated",
        "exercise_level": "full_stage_exercised",
        "execution_mode": "hybrid_generated",
        "recommended_agent_type": "writer",
        "contract_ref": "examples/stage-contracts/S07.stage-contract.json",
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "contract": {
            "purpose": "Compile claim-safe rhetoric, terminology, paragraph jobs, flexible surface controls, forbidden expressions, coverage ledgers, and downstream handoffs without final prose or claim strengthening.",
            "activation_policy": "activate before writing execution",
            "completion_gate": "S07RhetoricSurfaceControl validates claim surface rules, terminology coverage, internal-id bans, paragraph jobs, flexible language controls, forbidden expressions, coverage ledger, and S09/S10/S12/S13 handoffs without new claims or final prose",
            "consumes": [
                "object representation",
                "claim visibility",
                "evidence wording"
            ],
            "produces": [
                "construction matrix",
                "rhetorical matrix",
                "terminology register",
                "surface rules"
            ],
            "validators": [
                "S07_input_coverage",
                "S07_claim_surface_rule_map",
                "S07_terminology_surface_register",
                "S07_internal_id_ban_list",
                "S07_paragraph_job_map",
                "S07_rhetorical_move_matrix",
                "S07_language_flexibility_guard",
                "S07_surface_rules",
                "S07_forbidden_expression_list",
                "S07_coverage_ledger",
                "S07_unresolved_surface_control_report",
                "S07_downstream_handoff",
                "S07_no_new_claims_or_claim_strengthening",
                "S07_no_final_prose_or_completion_overclaim"
            ],
            "backflow_targets": [
                "S06",
                "S04",
                "S05"
            ],
            "requires_worker_task_packet": true,
            "worker_packet_coverage": {
                "blocker": null,
                "packet_ref": "examples/packets/phase10_s07_rhetoric_surface_control_packet.v1.yaml",
                "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
                "status": "linked_strict_packet"
            },
            "subagent_lane_policy": {
                "policy": "conditional_double",
                "default_lane_count": 1,
                "producer_agent_type": "writer",
                "verifier_agent_type": "verifier",
                "escalate_to_double_when": [
                    "terminology affects claim strength",
                    "surface rules govern multiple writing units",
                    "pre-writing expression freeze"
                ],
                "rationale": "Surface and terminology controls are broad but usually locally checkable; escalate when they constrain claims across sections."
            },
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            }
        },
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s07_declared_input_1",
                "ref": "object representation"
            },
            {
                "kind": "contract_declared",
                "material_id": "s07_declared_input_2",
                "ref": "claim visibility"
            },
            {
                "kind": "contract_declared",
                "material_id": "s07_declared_input_3",
                "ref": "evidence wording"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s07_source_ref_manuscript-main-tex",
                "ref": "manuscript/main.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s07_source_ref_manuscript-sections-01-introduction-tex",
                "ref": "manuscript/sections/01_introduction.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s07_source_ref_manuscript-sections-07-conclusion-tex",
                "ref": "manuscript/sections/07_conclusion.tex"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s06_pilot_output",
                "producer_stage_id": "S06",
                "ref": "artifacts/S06-object-representation-and-granularity-design.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s14_pilot_output",
                "producer_stage_id": "S14",
                "ref": "artifacts/S14-backflow-compilation-and-repair-planning.json"
            }
        ],
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s07_declared_input_1",
                "ref": "object representation"
            },
            {
                "kind": "contract_declared",
                "material_id": "s07_declared_input_2",
                "ref": "claim visibility"
            },
            {
                "kind": "contract_declared",
                "material_id": "s07_declared_input_3",
                "ref": "evidence wording"
            }
        ],
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s06_pilot_output",
                "producer_stage_id": "S06",
                "ref": "artifacts/S06-object-representation-and-granularity-design.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s14_pilot_output",
                "producer_stage_id": "S14",
                "ref": "artifacts/S14-backflow-compilation-and-repair-planning.json"
            }
        ],
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s07_source_ref_manuscript-main-tex",
                "ref": "manuscript/main.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s07_source_ref_manuscript-sections-01-introduction-tex",
                "ref": "manuscript/sections/01_introduction.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s07_source_ref_manuscript-sections-07-conclusion-tex",
                "ref": "manuscript/sections/07_conclusion.tex"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s07_pilot_output",
                "artifact_path": "artifacts/S07-rhetoric-terminology-and-surface-control-synthesis.json",
                "artifact_type": "analysis_material_projection",
                "description": "construction matrix; rhetorical matrix; terminology register; surface rules",
                "payload": {
                    "artifact_kind": "analysis_material_projection",
                    "purpose": "Compile claim-safe rhetoric, terminology, paragraph jobs, flexible surface controls, forbidden expressions, coverage ledgers, and downstream handoffs without final prose or claim strengthening.",
                    "projected_outputs": [
                        "construction matrix",
                        "rhetorical matrix",
                        "terminology register",
                        "surface rules"
                    ],
                    "consumed_ref_count": 8,
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "primary",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S07",
                            "validator_ref": "stage_overlay:nature_expert_writing:S07"
                        }
                    ]
                }
            }
        ],
        "handoff_consumers": [
            {
                "stage_id": "S09A",
                "stage_name": "Control-material selection",
                "material_id": "s07_pilot_output",
                "ref": "artifacts/S07-rhetoric-terminology-and-surface-control-synthesis.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S07 links to examples/stage-contracts/S07.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=fixture_generated; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S07 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": null,
            "packet_ref": "examples/packets/phase10_s07_rhetoric_surface_control_packet.v1.yaml",
            "required": true,
            "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
            "status": "linked_strict_packet"
        },
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "primary",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S07",
                "validator_ref": "stage_overlay:nature_expert_writing:S07"
            }
        ],
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        }
    },
    "S08": {
        "stage_id": "S08",
        "stage_name": "Visual and formal object planning",
        "status": "validated",
        "coverage_kind": "source_projected",
        "exercise_level": "full_stage_exercised",
        "execution_mode": "hybrid_generated",
        "recommended_agent_type": "designer",
        "contract_ref": "examples/stage-contracts/S08.stage-contract.json",
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "contract": {
            "purpose": "Compile reader questions, section/object budgets, claim/evidence boundaries, and source-data routes into visual/formal object contracts.",
            "activation_policy": "activate before any figure/table/algorithm/formula becomes paper-facing or when S05/S06/S04 imply a visual/formal object need",
            "completion_gate": "S08VisualFormalPlan validates visual needs, candidates, visual budget, figure/table/formal contracts, panel evidence maps, claim bindings, backend routes, caption boundaries, accessibility constraints, coverage ledger, and S10/S11/S12/S13 handoffs without final figures, final captions, new claims, or completion overclaim",
            "consumes": [
                "reader spine",
                "section function budget",
                "claim evidence materials"
            ],
            "produces": [
                "visual budget",
                "figure contract",
                "panel evidence map",
                "backend route"
            ],
            "validators": [
                "S08_input_coverage",
                "S08_visual_need_inventory",
                "S08_candidate_visual_object_queue",
                "S08_visual_budget",
                "S08_main_story_visual_path",
                "S08_figure_contract_schema",
                "S08_table_contract_schema",
                "S08_formal_object_contract_schema",
                "S08_panel_evidence_map",
                "S08_visual_claim_evidence_binding",
                "S08_explanatory_vs_evidential_boundary",
                "S08_main_supplement_split",
                "S08_backend_route_map",
                "S08_caption_boundary",
                "S08_accessibility_constraints",
                "S08_coverage_ledger",
                "S08_unresolved_visual_object_report",
                "S08_downstream_handoff",
                "S08_no_new_claims_or_completion_overclaim"
            ],
            "backflow_targets": [
                "S05",
                "S04",
                "S06"
            ],
            "requires_worker_task_packet": true,
            "worker_packet_coverage": {
                "blocker": null,
                "packet_ref": "examples/packets/phase10_s08_visual_formal_planning_packet.v1.yaml",
                "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
                "status": "linked_strict_packet"
            },
            "subagent_lane_policy": {
                "policy": "conditional_double",
                "default_lane_count": 1,
                "producer_agent_type": "designer",
                "verifier_agent_type": "verifier",
                "escalate_to_double_when": [
                    "figure/table/formula object will be paper-facing",
                    "visual claim support is uncertain",
                    "pre-export visual-plan freeze"
                ],
                "rationale": "Visual/formal planning is often design-led and evidence-linked; escalate before paper-facing visual commitments freeze."
            },
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            }
        },
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s08_declared_input_1",
                "ref": "reader spine"
            },
            {
                "kind": "contract_declared",
                "material_id": "s08_declared_input_2",
                "ref": "section function budget"
            },
            {
                "kind": "contract_declared",
                "material_id": "s08_declared_input_3",
                "ref": "claim evidence materials"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s08_source_ref_figures-readme-md",
                "ref": "figures/README.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s08_source_ref_experiments-results-l3-method-faithful-unified-s",
                "ref": "experiments/results/L3_method_faithful_unified_scene_20260625_non_text_supplements/artifact_manifest.json"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s08_source_ref_manuscript-sections-05-experiments-tex",
                "ref": "manuscript/sections/05_experiments.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s08_source_ref_manuscript-sections-06-results-discussion-tex",
                "ref": "manuscript/sections/06_results_discussion.tex"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s04_pilot_output",
                "producer_stage_id": "S04",
                "ref": "artifacts/S04-evidence-to-claim-admissibility.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s05_pilot_output",
                "producer_stage_id": "S05",
                "ref": "artifacts/S05-paper-spine-and-reader-question-synthesis.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s06_pilot_output",
                "producer_stage_id": "S06",
                "ref": "artifacts/S06-object-representation-and-granularity-design.json"
            }
        ],
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s08_declared_input_1",
                "ref": "reader spine"
            },
            {
                "kind": "contract_declared",
                "material_id": "s08_declared_input_2",
                "ref": "section function budget"
            },
            {
                "kind": "contract_declared",
                "material_id": "s08_declared_input_3",
                "ref": "claim evidence materials"
            }
        ],
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s04_pilot_output",
                "producer_stage_id": "S04",
                "ref": "artifacts/S04-evidence-to-claim-admissibility.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s05_pilot_output",
                "producer_stage_id": "S05",
                "ref": "artifacts/S05-paper-spine-and-reader-question-synthesis.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s06_pilot_output",
                "producer_stage_id": "S06",
                "ref": "artifacts/S06-object-representation-and-granularity-design.json"
            }
        ],
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s08_source_ref_figures-readme-md",
                "ref": "figures/README.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s08_source_ref_experiments-results-l3-method-faithful-unified-s",
                "ref": "experiments/results/L3_method_faithful_unified_scene_20260625_non_text_supplements/artifact_manifest.json"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s08_source_ref_manuscript-sections-05-experiments-tex",
                "ref": "manuscript/sections/05_experiments.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s08_source_ref_manuscript-sections-06-results-discussion-tex",
                "ref": "manuscript/sections/06_results_discussion.tex"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s08_pilot_output",
                "artifact_path": "artifacts/S08-visual-and-formal-object-planning.json",
                "artifact_type": "analysis_material_projection",
                "description": "visual budget; figure contract; panel evidence map; backend route",
                "payload": {
                    "artifact_kind": "analysis_material_projection",
                    "purpose": "Compile reader questions, section/object budgets, claim/evidence boundaries, and source-data routes into visual/formal object contracts.",
                    "projected_outputs": [
                        "visual budget",
                        "figure contract",
                        "panel evidence map",
                        "backend route"
                    ],
                    "consumed_ref_count": 10,
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "primary",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S08",
                            "validator_ref": "stage_overlay:nature_expert_writing:S08"
                        }
                    ]
                }
            }
        ],
        "handoff_consumers": [
            {
                "stage_id": "S11",
                "stage_name": "Figure caption formal artifact production",
                "material_id": "s08_pilot_output",
                "ref": "artifacts/S08-visual-and-formal-object-planning.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S08 links to examples/stage-contracts/S08.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=source_projected; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S08 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": null,
            "packet_ref": "examples/packets/phase10_s08_visual_formal_planning_packet.v1.yaml",
            "required": true,
            "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
            "status": "linked_strict_packet"
        },
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "primary",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S08",
                "validator_ref": "stage_overlay:nature_expert_writing:S08"
            }
        ],
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        }
    },
    "S09A": {
        "stage_id": "S09A",
        "stage_name": "Control-material selection",
        "status": "validated",
        "coverage_kind": "script_checked",
        "exercise_level": "full_stage_exercised",
        "execution_mode": "hybrid_generated",
        "recommended_agent_type": "planner",
        "contract_ref": "examples/stage-contracts/S09A.stage-contract.json",
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "contract": {
            "purpose": "Select a target-specific, context-rich, priority-ordered control bundle without compiling worker packets or granting content-generation authority.",
            "activation_policy": "activate before per-unit packet assembly",
            "completion_gate": "S09ARichControlBundle is layered, priority-ordered, freshness-checked, conflict-resolved, and ready for S09B without worker guessing",
            "consumes": [
                "claim controls",
                "spine controls",
                "granularity controls",
                "surface rules",
                "target unit"
            ],
            "produces": [
                "selected control bundle",
                "control priority map",
                "missing control report"
            ],
            "validators": [
                "S09A_target_unit_profile",
                "S09A_hard_constraints_present",
                "S09A_rich_context_layering",
                "S09A_claim_control_selection",
                "S09A_reader_context_selection",
                "S09A_object_context_selection",
                "S09A_surface_control_selection",
                "S09A_visual_formal_control_selection",
                "S09A_negative_controls",
                "S09A_conflict_resolution",
                "S09A_context_usage_instructions",
                "S09A_freshness_check",
                "S09A_missing_control_report",
                "S09A_coverage_ledger",
                "S09A_downstream_packet_requirements",
                "S09A_no_bare_S09",
                "S09A_no_task_packet_or_final_content"
            ],
            "backflow_targets": [
                "S04",
                "S05",
                "S06",
                "S07",
                "S08"
            ],
            "requires_worker_task_packet": false,
            "worker_packet_coverage": {
                "blocker": "Stage is owner-gated, script-generated, or main-controller assembly; fake worker packets are forbidden.",
                "packet_ref": null,
                "return_contract_ref": null,
                "status": "not_required"
            },
            "subagent_lane_policy": {
                "policy": "single_with_deterministic_validation",
                "default_lane_count": 1,
                "producer_agent_type": "planner",
                "verifier_agent_type": null,
                "escalate_to_double_when": [
                    "owner requests audit of control selection",
                    "full-flow QA mode",
                    "control selection changes high-risk claim inputs"
                ],
                "rationale": "Control-material selection is a controller/script-like routing step and is primarily proven by deterministic validation."
            },
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            }
        },
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s09a_declared_input_1",
                "ref": "claim controls"
            },
            {
                "kind": "contract_declared",
                "material_id": "s09a_declared_input_2",
                "ref": "spine controls"
            },
            {
                "kind": "contract_declared",
                "material_id": "s09a_declared_input_3",
                "ref": "granularity controls"
            },
            {
                "kind": "contract_declared",
                "material_id": "s09a_declared_input_4",
                "ref": "surface rules"
            },
            {
                "kind": "contract_declared",
                "material_id": "s09a_declared_input_5",
                "ref": "target unit"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s09a_source_ref_examples-local-paper-sample-paper-workspace-mate",
                "ref": "examples/local-paper/sample-paper-workspace/materials/owner_contract.json"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s09a_source_ref_examples-local-paper-sample-paper-workspace-mate",
                "ref": "examples/local-paper/sample-paper-workspace/materials/source_inventory.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s04_pilot_output",
                "producer_stage_id": "S04",
                "ref": "artifacts/S04-evidence-to-claim-admissibility.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s05_pilot_output",
                "producer_stage_id": "S05",
                "ref": "artifacts/S05-paper-spine-and-reader-question-synthesis.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s06_pilot_output",
                "producer_stage_id": "S06",
                "ref": "artifacts/S06-object-representation-and-granularity-design.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s07_pilot_output",
                "producer_stage_id": "S07",
                "ref": "artifacts/S07-rhetoric-terminology-and-surface-control-synthesis.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s14_pilot_output",
                "producer_stage_id": "S14",
                "ref": "artifacts/S14-backflow-compilation-and-repair-planning.json"
            }
        ],
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s09a_declared_input_1",
                "ref": "claim controls"
            },
            {
                "kind": "contract_declared",
                "material_id": "s09a_declared_input_2",
                "ref": "spine controls"
            },
            {
                "kind": "contract_declared",
                "material_id": "s09a_declared_input_3",
                "ref": "granularity controls"
            },
            {
                "kind": "contract_declared",
                "material_id": "s09a_declared_input_4",
                "ref": "surface rules"
            },
            {
                "kind": "contract_declared",
                "material_id": "s09a_declared_input_5",
                "ref": "target unit"
            }
        ],
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s04_pilot_output",
                "producer_stage_id": "S04",
                "ref": "artifacts/S04-evidence-to-claim-admissibility.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s05_pilot_output",
                "producer_stage_id": "S05",
                "ref": "artifacts/S05-paper-spine-and-reader-question-synthesis.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s06_pilot_output",
                "producer_stage_id": "S06",
                "ref": "artifacts/S06-object-representation-and-granularity-design.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s07_pilot_output",
                "producer_stage_id": "S07",
                "ref": "artifacts/S07-rhetoric-terminology-and-surface-control-synthesis.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s14_pilot_output",
                "producer_stage_id": "S14",
                "ref": "artifacts/S14-backflow-compilation-and-repair-planning.json"
            }
        ],
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s09a_source_ref_examples-local-paper-sample-paper-workspace-mate",
                "ref": "examples/local-paper/sample-paper-workspace/materials/owner_contract.json"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s09a_source_ref_examples-local-paper-sample-paper-workspace-mate",
                "ref": "examples/local-paper/sample-paper-workspace/materials/source_inventory.json"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s09a_pilot_output",
                "artifact_path": "artifacts/S09A-control-material-selection.json",
                "artifact_type": "analysis_material_projection",
                "description": "selected control bundle; control priority map; missing control report",
                "payload": {
                    "artifact_kind": "analysis_material_projection",
                    "purpose": "Select a target-specific, context-rich, priority-ordered control bundle without compiling worker packets or granting content-generation authority.",
                    "projected_outputs": [
                        "selected control bundle",
                        "control priority map",
                        "missing control report"
                    ],
                    "consumed_ref_count": 12,
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "primary",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S09A",
                            "validator_ref": "stage_overlay:nature_expert_writing:S09A"
                        }
                    ]
                }
            }
        ],
        "handoff_consumers": [
            {
                "stage_id": "S09B",
                "stage_name": "Per-unit task packet assembly",
                "material_id": "s09a_pilot_output",
                "ref": "artifacts/S09A-control-material-selection.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S09A links to examples/stage-contracts/S09A.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=script_checked; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S09A has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": "Stage is owner-gated, script-generated, or main-controller assembly; fake worker packets are forbidden.",
            "packet_ref": null,
            "required": false,
            "return_contract_ref": null,
            "status": "not_required"
        },
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "primary",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S09A",
                "validator_ref": "stage_overlay:nature_expert_writing:S09A"
            }
        ],
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        }
    },
    "S09B": {
        "stage_id": "S09B",
        "stage_name": "Per-unit task packet assembly",
        "status": "validated",
        "coverage_kind": "script_checked",
        "exercise_level": "full_stage_exercised",
        "execution_mode": "script_generated",
        "recommended_agent_type": "main",
        "contract_ref": "examples/stage-contracts/S09B.stage-contract.json",
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "contract": {
            "purpose": "Compile one bounded, authority-safe per-unit TaskPacket from an S09A selected control bundle.",
            "activation_policy": "activate when a worker needs a section/unit packet",
            "completion_gate": "S09BTaskPacketAssembly emits a validate_packet-clean, single-writer, completion-forbidden, non-recursive packet with S09A usage labels preserved",
            "consumes": [
                "selected control bundle",
                "evidence anchors",
                "target unit",
                "validator refs",
                "return format"
            ],
            "produces": [
                "task packet",
                "section move plan",
                "single-writer lock",
                "missing material report"
            ],
            "validators": [
                "S09B_packet_identity",
                "S09B_allowed_read_paths",
                "S09B_allowed_write_paths",
                "S09B_forbidden_routes",
                "S09B_worker_boot_clause",
                "S09B_completion_forbidden",
                "S09B_no_recursive_orchestration",
                "S09B_single_writer_lock",
                "S09B_unit_move_plan",
                "S09B_selected_controls_propagated",
                "S09B_context_usage_preserved",
                "S09B_background_not_claim_authority",
                "S09B_return_format",
                "S09B_missing_material_report",
                "S09B_authority_boundary",
                "S09B_emitted_packet_validates",
                "S09B_no_bare_S09"
            ],
            "backflow_targets": [
                "S09A",
                "S14",
                "S15"
            ],
            "requires_worker_task_packet": false,
            "worker_packet_coverage": {
                "blocker": "Stage is owner-gated, script-generated, or main-controller assembly; fake worker packets are forbidden.",
                "packet_ref": null,
                "return_contract_ref": null,
                "status": "not_required"
            },
            "subagent_lane_policy": {
                "policy": "single_with_deterministic_validation",
                "default_lane_count": 1,
                "producer_agent_type": "main",
                "verifier_agent_type": null,
                "escalate_to_double_when": [
                    "packet compiler or authority-boundary code changes",
                    "full-flow QA mode",
                    "owner requests task-packet audit"
                ],
                "rationale": "Task-packet assembly is an authority-boundary compiler step and is primarily proven by deterministic validation."
            },
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            }
        },
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s09b_declared_input_1",
                "ref": "selected control bundle"
            },
            {
                "kind": "contract_declared",
                "material_id": "s09b_declared_input_2",
                "ref": "evidence anchors"
            },
            {
                "kind": "contract_declared",
                "material_id": "s09b_declared_input_3",
                "ref": "target unit"
            },
            {
                "kind": "contract_declared",
                "material_id": "s09b_declared_input_4",
                "ref": "validator refs"
            },
            {
                "kind": "contract_declared",
                "material_id": "s09b_declared_input_5",
                "ref": "return format"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s09b_source_ref_examples-packets-intro-writing-packet-v2-yaml",
                "ref": "examples/packets/intro_writing_packet.v2.yaml"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s09b_source_ref_examples-packets-claim-repair-packet-v1-yaml",
                "ref": "examples/packets/claim_repair_packet.v1.yaml"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s09a_pilot_output",
                "producer_stage_id": "S09A",
                "ref": "artifacts/S09A-control-material-selection.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s15_pilot_output",
                "producer_stage_id": "S15",
                "ref": "artifacts/S15-repair-execution-and-local-regeneration.json"
            }
        ],
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s09b_declared_input_1",
                "ref": "selected control bundle"
            },
            {
                "kind": "contract_declared",
                "material_id": "s09b_declared_input_2",
                "ref": "evidence anchors"
            },
            {
                "kind": "contract_declared",
                "material_id": "s09b_declared_input_3",
                "ref": "target unit"
            },
            {
                "kind": "contract_declared",
                "material_id": "s09b_declared_input_4",
                "ref": "validator refs"
            },
            {
                "kind": "contract_declared",
                "material_id": "s09b_declared_input_5",
                "ref": "return format"
            }
        ],
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s09a_pilot_output",
                "producer_stage_id": "S09A",
                "ref": "artifacts/S09A-control-material-selection.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s15_pilot_output",
                "producer_stage_id": "S15",
                "ref": "artifacts/S15-repair-execution-and-local-regeneration.json"
            }
        ],
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s09b_source_ref_examples-packets-intro-writing-packet-v2-yaml",
                "ref": "examples/packets/intro_writing_packet.v2.yaml"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s09b_source_ref_examples-packets-claim-repair-packet-v1-yaml",
                "ref": "examples/packets/claim_repair_packet.v1.yaml"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s09b_pilot_output",
                "artifact_path": "artifacts/S09B-per-unit-task-packet-assembly.json",
                "artifact_type": "script_check_output",
                "description": "task packet; section move plan; single-writer lock; missing material report",
                "payload": {
                    "artifact_kind": "script_check_output",
                    "purpose": "Compile one bounded, authority-safe per-unit TaskPacket from an S09A selected control bundle.",
                    "projected_outputs": [
                        "task packet",
                        "section move plan",
                        "single-writer lock",
                        "missing material report"
                    ],
                    "consumed_ref_count": 9,
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "primary",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S09B",
                            "validator_ref": "stage_overlay:nature_expert_writing:S09B"
                        }
                    ]
                }
            }
        ],
        "handoff_consumers": [
            {
                "stage_id": "S10",
                "stage_name": "Main-text production",
                "material_id": "s09b_pilot_output",
                "ref": "artifacts/S09B-per-unit-task-packet-assembly.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S09B links to examples/stage-contracts/S09B.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=script_checked; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S09B has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": "Stage is owner-gated, script-generated, or main-controller assembly; fake worker packets are forbidden.",
            "packet_ref": null,
            "required": false,
            "return_contract_ref": null,
            "status": "not_required"
        },
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "primary",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S09B",
                "validator_ref": "stage_overlay:nature_expert_writing:S09B"
            }
        ],
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        }
    },
    "S10": {
        "stage_id": "S10",
        "stage_name": "Main-text production",
        "status": "validated",
        "coverage_kind": "source_projected",
        "exercise_level": "full_stage_exercised",
        "execution_mode": "agent_generated",
        "recommended_agent_type": "writer",
        "contract_ref": "examples/stage-contracts/S10.stage-contract.json",
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "contract": {
            "purpose": "Produce packet-bounded, claim-safe candidate prose units from validated S09B task packets with traceable controls and mandatory verifier evidence.",
            "activation_policy": "activate when writing execution is needed",
            "completion_gate": "S10CandidateTextReturn validates candidate prose, packet compliance, trace ledgers, CandidateArtifactReturn, writer/verifier evidence, and authority boundary; controller owns acceptance and completion",
            "consumes": [
                "S09B task packet",
                "construction matrix",
                "terminology register",
                "claim visibility"
            ],
            "produces": [
                "candidate text unit",
                "CandidateArtifactReturn"
            ],
            "validators": [
                "S10_packet_compliance",
                "S10_candidate_text_schema",
                "S10_allowed_write_path",
                "S10_claim_evidence_trace",
                "S10_claim_boundary_preserved",
                "S10_no_new_claims",
                "S10_no_claim_strengthening",
                "S10_move_trace",
                "S10_terminology_trace",
                "S10_internal_id_leakage",
                "S10_object_granularity_trace",
                "S10_visual_callout_trace",
                "S10_forbidden_expression_scan",
                "S10_coverage_ledger",
                "S10_candidate_return_complete",
                "S10_writer_evidence",
                "S10_verifier_evidence",
                "S10_authority_boundary"
            ],
            "backflow_targets": [
                "S09B",
                "S09A",
                "S07",
                "S06",
                "S05",
                "S04",
                "S08",
                "S15"
            ],
            "requires_worker_task_packet": true,
            "worker_packet_coverage": {
                "status": "linked_strict_packet",
                "packet_ref": "examples/packets/phase10_s09b_s10_intro_callout_packet.v1.yaml",
                "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
                "blocker": null
            },
            "subagent_lane_policy": {
                "policy": "mandatory_double",
                "default_lane_count": 2,
                "producer_agent_type": "writer",
                "verifier_agent_type": "verifier",
                "escalate_to_double_when": [
                    "always for normal paper-facing production",
                    "full-flow QA mode",
                    "milestone or freeze gate"
                ],
                "rationale": "Main-text production is paper-facing semantic output; independent verification is mandatory before controller acceptance."
            },
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            }
        },
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s10_declared_input_1",
                "ref": "S09B task packet"
            },
            {
                "kind": "contract_declared",
                "material_id": "s10_declared_input_2",
                "ref": "construction matrix"
            },
            {
                "kind": "contract_declared",
                "material_id": "s10_declared_input_3",
                "ref": "terminology register"
            },
            {
                "kind": "contract_declared",
                "material_id": "s10_declared_input_4",
                "ref": "claim visibility"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s10_source_ref_manuscript-sections-01-introduction-tex",
                "ref": "manuscript/sections/01_introduction.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s10_source_ref_manuscript-sections-04-method-tex",
                "ref": "manuscript/sections/04_method.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s10_source_ref_manuscript-sections-06-results-discussion-tex",
                "ref": "manuscript/sections/06_results_discussion.tex"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s09b_pilot_output",
                "producer_stage_id": "S09B",
                "ref": "artifacts/S09B-per-unit-task-packet-assembly.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s15_pilot_output",
                "producer_stage_id": "S15",
                "ref": "artifacts/S15-repair-execution-and-local-regeneration.json"
            }
        ],
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s10_declared_input_1",
                "ref": "S09B task packet"
            },
            {
                "kind": "contract_declared",
                "material_id": "s10_declared_input_2",
                "ref": "construction matrix"
            },
            {
                "kind": "contract_declared",
                "material_id": "s10_declared_input_3",
                "ref": "terminology register"
            },
            {
                "kind": "contract_declared",
                "material_id": "s10_declared_input_4",
                "ref": "claim visibility"
            }
        ],
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s09b_pilot_output",
                "producer_stage_id": "S09B",
                "ref": "artifacts/S09B-per-unit-task-packet-assembly.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s15_pilot_output",
                "producer_stage_id": "S15",
                "ref": "artifacts/S15-repair-execution-and-local-regeneration.json"
            }
        ],
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s10_source_ref_manuscript-sections-01-introduction-tex",
                "ref": "manuscript/sections/01_introduction.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s10_source_ref_manuscript-sections-04-method-tex",
                "ref": "manuscript/sections/04_method.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s10_source_ref_manuscript-sections-06-results-discussion-tex",
                "ref": "manuscript/sections/06_results_discussion.tex"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s10_pilot_output",
                "artifact_path": "artifacts/S10-main-text-production.json",
                "artifact_type": "candidate_or_repair_projection",
                "description": "candidate text unit; CandidateArtifactReturn",
                "payload": {
                    "artifact_kind": "candidate_or_repair_projection",
                    "purpose": "Produce packet-bounded, claim-safe candidate prose units from validated S09B task packets with traceable controls and mandatory verifier evidence.",
                    "projected_outputs": [
                        "candidate text unit",
                        "CandidateArtifactReturn"
                    ],
                    "consumed_ref_count": 9,
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "primary",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S10",
                            "validator_ref": "stage_overlay:nature_expert_writing:S10"
                        }
                    ]
                }
            }
        ],
        "handoff_consumers": [
            {
                "stage_id": "S12",
                "stage_name": "Integration and consistency pass",
                "material_id": "s10_pilot_output",
                "ref": "artifacts/S10-main-text-production.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S10 links to examples/stage-contracts/S10.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=source_projected; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S10 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": null,
            "packet_ref": "examples/packets/phase10_s09b_s10_intro_callout_packet.v1.yaml",
            "required": true,
            "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
            "status": "linked_strict_packet"
        },
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "primary",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S10",
                "validator_ref": "stage_overlay:nature_expert_writing:S10"
            }
        ],
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        }
    },
    "S11": {
        "stage_id": "S11",
        "stage_name": "Figure caption formal artifact production",
        "status": "validated",
        "coverage_kind": "source_projected",
        "exercise_level": "full_stage_exercised",
        "execution_mode": "hybrid_generated",
        "recommended_agent_type": "executor",
        "contract_ref": "examples/stage-contracts/S11.stage-contract.json",
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "contract": {
            "purpose": "Produce contract-bound candidate figures, captions, tables, algorithms, formulas, render plans, and export bundles without changing proof role, evidence meaning, or claim boundaries.",
            "activation_policy": "activate when figure/caption/formal artifacts are touched",
            "completion_gate": "S11FigureCaptionArtifactBundle validates S08 contract compliance, source-data trace, panel/caption claim traces, image integrity, visual polish policy/report, accessibility, export manifest, CandidateArtifactReturn, and authority boundary without final export or completion claims",
            "consumes": [
                "figure contracts",
                "panel evidence packages",
                "source data locators",
                "caption brief"
            ],
            "produces": [
                "figure statistics",
                "image integrity record",
                "caption brief",
                "figure export bundle"
            ],
            "validators": [
                "S11_packet_compliance",
                "S11_figure_contract_compliance",
                "S11_source_data_provenance",
                "S11_panel_claim_trace",
                "S11_caption_claim_boundary",
                "S11_explanatory_vs_evidential_boundary",
                "S11_editable_source_present",
                "S11_render_or_render_plan_present",
                "S11_image_integrity_record",
                "S11_visual_polish_policy",
                "S11_visual_polish_report",
                "S11_accessibility_check",
                "S11_export_manifest",
                "S11_candidate_return_complete",
                "S11_verifier_evidence",
                "S11_authority_boundary",
                "S11_nature_figure_vendor_present",
                "S11_nature_figure_parity_manifest",
                "S11_nature_figure_backend_gate",
                "S11_nature_figure_direct_call_mapping",
                "S11_no_cross_backend_rendering",
                "S11_no_mock_data_for_evidential_figure",
                "S11_exemplar_boundary_and_similarity_report"
            ],
            "backflow_targets": [
                "S08",
                "S04",
                "S01",
                "S07",
                "S09B",
                "S15"
            ],
            "requires_worker_task_packet": true,
            "worker_packet_coverage": {
                "status": "linked_strict_packet",
                "packet_ref": "examples/packets/phase10_s11_figure_caption_artifact_packet.v1.yaml",
                "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
                "blocker": null
            },
            "subagent_lane_policy": {
                "policy": "conditional_double",
                "default_lane_count": 1,
                "producer_agent_type": "executor",
                "verifier_agent_type": "verifier",
                "escalate_to_double_when": [
                    "artifact is paper-facing or data-backed",
                    "caption makes a claim",
                    "pre-export figure/caption freeze"
                ],
                "rationale": "Artifact production is often deterministic but paper-facing; independent QA is required when it becomes final/export-facing."
            },
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            }
        },
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s11_declared_input_1",
                "ref": "figure contracts"
            },
            {
                "kind": "contract_declared",
                "material_id": "s11_declared_input_2",
                "ref": "panel evidence packages"
            },
            {
                "kind": "contract_declared",
                "material_id": "s11_declared_input_3",
                "ref": "source data locators"
            },
            {
                "kind": "contract_declared",
                "material_id": "s11_declared_input_4",
                "ref": "caption brief"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s11_source_ref_figures-readme-md",
                "ref": "figures/README.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s11_source_ref_experiments-results-l3-method-faithful-unified-s",
                "ref": "experiments/results/L3_method_faithful_unified_scene_20260625_non_text_supplements/artifact_manifest.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s01_pilot_output",
                "producer_stage_id": "S01",
                "ref": "artifacts/S01-source-citation-evidence-inventory.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s04_pilot_output",
                "producer_stage_id": "S04",
                "ref": "artifacts/S04-evidence-to-claim-admissibility.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s08_pilot_output",
                "producer_stage_id": "S08",
                "ref": "artifacts/S08-visual-and-formal-object-planning.json"
            }
        ],
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s11_declared_input_1",
                "ref": "figure contracts"
            },
            {
                "kind": "contract_declared",
                "material_id": "s11_declared_input_2",
                "ref": "panel evidence packages"
            },
            {
                "kind": "contract_declared",
                "material_id": "s11_declared_input_3",
                "ref": "source data locators"
            },
            {
                "kind": "contract_declared",
                "material_id": "s11_declared_input_4",
                "ref": "caption brief"
            }
        ],
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s01_pilot_output",
                "producer_stage_id": "S01",
                "ref": "artifacts/S01-source-citation-evidence-inventory.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s04_pilot_output",
                "producer_stage_id": "S04",
                "ref": "artifacts/S04-evidence-to-claim-admissibility.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s08_pilot_output",
                "producer_stage_id": "S08",
                "ref": "artifacts/S08-visual-and-formal-object-planning.json"
            }
        ],
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s11_source_ref_figures-readme-md",
                "ref": "figures/README.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s11_source_ref_experiments-results-l3-method-faithful-unified-s",
                "ref": "experiments/results/L3_method_faithful_unified_scene_20260625_non_text_supplements/artifact_manifest.json"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s11_pilot_output",
                "artifact_path": "artifacts/S11-figure-caption-formal-artifact-production.json",
                "artifact_type": "candidate_or_repair_projection",
                "description": "figure statistics; image integrity record; caption brief; figure export bundle",
                "payload": {
                    "artifact_kind": "candidate_or_repair_projection",
                    "purpose": "Produce contract-bound candidate figures, captions, tables, algorithms, formulas, render plans, and export bundles without changing proof role, evidence meaning, or claim boundaries.",
                    "projected_outputs": [
                        "figure statistics",
                        "image integrity record",
                        "caption brief",
                        "figure export bundle"
                    ],
                    "consumed_ref_count": 9,
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "primary",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S11",
                            "validator_ref": "stage_overlay:nature_expert_writing:S11"
                        }
                    ]
                }
            }
        ],
        "handoff_consumers": [
            {
                "stage_id": "S12",
                "stage_name": "Integration and consistency pass",
                "material_id": "s11_pilot_output",
                "ref": "artifacts/S11-figure-caption-formal-artifact-production.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S11 links to examples/stage-contracts/S11.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=source_projected; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S11 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": null,
            "packet_ref": "examples/packets/phase10_s11_figure_caption_artifact_packet.v1.yaml",
            "required": true,
            "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
            "status": "linked_strict_packet"
        },
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "primary",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S11",
                "validator_ref": "stage_overlay:nature_expert_writing:S11"
            }
        ],
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        }
    },
    "S12": {
        "stage_id": "S12",
        "stage_name": "Integration and consistency pass",
        "status": "validated",
        "coverage_kind": "fixture_generated",
        "exercise_level": "full_stage_exercised",
        "execution_mode": "hybrid_generated",
        "recommended_agent_type": "verifier",
        "contract_ref": "examples/stage-contracts/S12.stage-contract.json",
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "contract": {
            "purpose": "Compile a structured integrated manuscript candidate package and run consistency/backflow audits without PDF export, final acceptance, or uncontrolled rewriting.",
            "activation_policy": "activate when multiple modules are integrated",
            "completion_gate": "S12IntegrationConsistencyReport validates module inventory, assembly manifest, structured integrated candidate, trace index, audits, findings/backflow queue, validator report, CandidateArtifactReturn, and no PDF/final/untracked rewrite boundary",
            "consumes": [
                "candidate text modules",
                "figures/captions",
                "section move plan",
                "terminology register",
                "claim visibility"
            ],
            "produces": [
                "integrated manuscript candidate",
                "consistency findings",
                "validator report"
            ],
            "validators": [
                "S12_module_inventory",
                "S12_assembly_manifest",
                "S12_integrated_candidate_package",
                "S12_trace_index",
                "S12_claim_boundary_audit",
                "S12_promise_satisfaction",
                "S12_cross_section_consistency",
                "S12_terminology_consistency",
                "S12_object_granularity_consistency",
                "S12_figure_text_alignment",
                "S12_surface_consistency",
                "S12_stale_material_report",
                "S12_integration_findings",
                "S12_backflow_queue",
                "S12_no_pdf_export",
                "S12_no_final_claim",
                "S12_no_untracked_rewrite",
                "S12_candidate_return_complete"
            ],
            "backflow_targets": [
                "S04",
                "S05",
                "S06",
                "S07",
                "S08",
                "S09A",
                "S09B",
                "S10",
                "S11",
                "S14",
                "S15"
            ],
            "requires_worker_task_packet": true,
            "worker_packet_coverage": {
                "status": "linked_strict_packet",
                "packet_ref": "examples/packets/phase10_s12_integration_consistency_packet.v1.yaml",
                "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
                "blocker": null
            },
            "subagent_lane_policy": {
                "policy": "mandatory_double",
                "default_lane_count": 2,
                "producer_agent_type": "verifier",
                "verifier_agent_type": "verifier",
                "escalate_to_double_when": [
                    "always for normal paper-facing production",
                    "full-flow QA mode",
                    "milestone or freeze gate"
                ],
                "rationale": "Integration can create cross-section contradictions, so independent consistency verification is mandatory."
            },
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            }
        },
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s12_declared_input_1",
                "ref": "candidate text modules"
            },
            {
                "kind": "contract_declared",
                "material_id": "s12_declared_input_2",
                "ref": "figures/captions"
            },
            {
                "kind": "contract_declared",
                "material_id": "s12_declared_input_3",
                "ref": "section move plan"
            },
            {
                "kind": "contract_declared",
                "material_id": "s12_declared_input_4",
                "ref": "terminology register"
            },
            {
                "kind": "contract_declared",
                "material_id": "s12_declared_input_5",
                "ref": "claim visibility"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s12_source_ref_manuscript-main-tex",
                "ref": "manuscript/main.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s12_source_ref_manuscript-sections-01-introduction-tex",
                "ref": "manuscript/sections/01_introduction.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s12_source_ref_manuscript-sections-06-results-discussion-tex",
                "ref": "manuscript/sections/06_results_discussion.tex"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s10_pilot_output",
                "producer_stage_id": "S10",
                "ref": "artifacts/S10-main-text-production.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s11_pilot_output",
                "producer_stage_id": "S11",
                "ref": "artifacts/S11-figure-caption-formal-artifact-production.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s15_pilot_output",
                "producer_stage_id": "S15",
                "ref": "artifacts/S15-repair-execution-and-local-regeneration.json"
            }
        ],
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s12_declared_input_1",
                "ref": "candidate text modules"
            },
            {
                "kind": "contract_declared",
                "material_id": "s12_declared_input_2",
                "ref": "figures/captions"
            },
            {
                "kind": "contract_declared",
                "material_id": "s12_declared_input_3",
                "ref": "section move plan"
            },
            {
                "kind": "contract_declared",
                "material_id": "s12_declared_input_4",
                "ref": "terminology register"
            },
            {
                "kind": "contract_declared",
                "material_id": "s12_declared_input_5",
                "ref": "claim visibility"
            }
        ],
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s10_pilot_output",
                "producer_stage_id": "S10",
                "ref": "artifacts/S10-main-text-production.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s11_pilot_output",
                "producer_stage_id": "S11",
                "ref": "artifacts/S11-figure-caption-formal-artifact-production.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s15_pilot_output",
                "producer_stage_id": "S15",
                "ref": "artifacts/S15-repair-execution-and-local-regeneration.json"
            }
        ],
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s12_source_ref_manuscript-main-tex",
                "ref": "manuscript/main.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s12_source_ref_manuscript-sections-01-introduction-tex",
                "ref": "manuscript/sections/01_introduction.tex"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s12_source_ref_manuscript-sections-06-results-discussion-tex",
                "ref": "manuscript/sections/06_results_discussion.tex"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s12_pilot_output",
                "artifact_path": "artifacts/S12-integration-and-consistency-pass.json",
                "artifact_type": "analysis_material_projection",
                "description": "integrated manuscript candidate; consistency findings; validator report",
                "payload": {
                    "artifact_kind": "analysis_material_projection",
                    "purpose": "Compile a structured integrated manuscript candidate package and run consistency/backflow audits without PDF export, final acceptance, or uncontrolled rewriting.",
                    "projected_outputs": [
                        "integrated manuscript candidate",
                        "consistency findings",
                        "validator report"
                    ],
                    "consumed_ref_count": 11,
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "primary",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S12",
                            "validator_ref": "stage_overlay:nature_expert_writing:S12"
                        }
                    ]
                }
            }
        ],
        "handoff_consumers": [
            {
                "stage_id": "S13",
                "stage_name": "Adversarial manuscript review",
                "material_id": "s12_pilot_output",
                "ref": "artifacts/S12-integration-and-consistency-pass.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S12 links to examples/stage-contracts/S12.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=fixture_generated; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S12 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": null,
            "packet_ref": "examples/packets/phase10_s12_integration_consistency_packet.v1.yaml",
            "required": true,
            "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
            "status": "linked_strict_packet"
        },
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "primary",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S12",
                "validator_ref": "stage_overlay:nature_expert_writing:S12"
            }
        ],
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        }
    },
    "S13": {
        "stage_id": "S13",
        "stage_name": "Adversarial manuscript review",
        "status": "validated",
        "coverage_kind": "fixture_generated",
        "exercise_level": "full_stage_exercised",
        "execution_mode": "agent_generated",
        "recommended_agent_type": "critic",
        "contract_ref": "examples/stage-contracts/S13.stage-contract.json",
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "contract": {
            "purpose": "Compile actionable adversarial loss signals over the structured S12 integrated candidate; do not rewrite, repair, review PDF as primary object, or claim completion.",
            "activation_policy": "activate when candidate manuscript/module exists",
            "completion_gate": "S13AdversarialReviewReport validates structured S12 review object inventory, review scope, reviewer-panel and desk-risk reports, actionable severity/evidence/location findings, S14 routing, CandidateArtifactReturn, verifier evidence, and no rewrite/PDF-primary-review/repair/completion boundary",
            "consumes": [
                "structured S12 integrated candidate package",
                "S12 trace and validator reports",
                "S10/S11 candidate traces",
                "S04-S08 upstream control materials"
            ],
            "produces": [
                "adversarial review report",
                "severity-ranked review findings",
                "finding actionability report",
                "validator report"
            ],
            "validators": [
                "S13_review_object_inventory",
                "S13_review_scope",
                "S13_reviewer_panel_report",
                "S13_desk_reject_risk_report",
                "S13_reader_experience_report",
                "S13_claim_evidence_review",
                "S13_figure_caption_review",
                "S13_review_findings_schema",
                "S13_finding_actionability",
                "S13_backflow_target_validity",
                "S13_no_uncontrolled_rewrite",
                "S13_no_pdf_primary_review",
                "S13_candidate_return_complete",
                "S13_verifier_evidence"
            ],
            "backflow_targets": [
                "S14"
            ],
            "requires_worker_task_packet": true,
            "worker_packet_coverage": {
                "blocker": null,
                "packet_ref": "examples/packets/phase10_s13_adversarial_review_packet.v1.yaml",
                "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
                "status": "linked_strict_packet"
            },
            "subagent_lane_policy": {
                "policy": "mandatory_double",
                "default_lane_count": 2,
                "producer_agent_type": "critic",
                "verifier_agent_type": "verifier",
                "escalate_to_double_when": [
                    "always for normal paper-facing production",
                    "full-flow QA mode",
                    "milestone or freeze gate"
                ],
                "rationale": "Adversarial review itself produces loss signals that must be independently validated for actionability and routing."
            },
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            }
        },
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s13_declared_input_1",
                "ref": "structured S12 integrated candidate package"
            },
            {
                "kind": "contract_declared",
                "material_id": "s13_declared_input_2",
                "ref": "S12 trace and validator reports"
            },
            {
                "kind": "contract_declared",
                "material_id": "s13_declared_input_3",
                "ref": "S10/S11 candidate traces"
            },
            {
                "kind": "contract_declared",
                "material_id": "s13_declared_input_4",
                "ref": "S04-S08 upstream control materials"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s13_source_ref_project-status-md",
                "ref": "PROJECT_STATUS.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s13_source_ref_handoff-md",
                "ref": "HANDOFF.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s13_source_ref_manuscript-main-tex",
                "ref": "manuscript/main.tex"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s12_pilot_output",
                "producer_stage_id": "S12",
                "ref": "artifacts/S12-integration-and-consistency-pass.json"
            }
        ],
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s13_declared_input_1",
                "ref": "structured S12 integrated candidate package"
            },
            {
                "kind": "contract_declared",
                "material_id": "s13_declared_input_2",
                "ref": "S12 trace and validator reports"
            },
            {
                "kind": "contract_declared",
                "material_id": "s13_declared_input_3",
                "ref": "S10/S11 candidate traces"
            },
            {
                "kind": "contract_declared",
                "material_id": "s13_declared_input_4",
                "ref": "S04-S08 upstream control materials"
            }
        ],
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s12_pilot_output",
                "producer_stage_id": "S12",
                "ref": "artifacts/S12-integration-and-consistency-pass.json"
            }
        ],
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s13_source_ref_project-status-md",
                "ref": "PROJECT_STATUS.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s13_source_ref_handoff-md",
                "ref": "HANDOFF.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s13_source_ref_manuscript-main-tex",
                "ref": "manuscript/main.tex"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s13_pilot_output",
                "artifact_path": "artifacts/S13-adversarial-manuscript-review.json",
                "artifact_type": "review_backflow_projection",
                "description": "adversarial review report; severity-ranked review findings; finding actionability report; validator report",
                "payload": {
                    "artifact_kind": "review_backflow_projection",
                    "purpose": "Compile actionable adversarial loss signals over the structured S12 integrated candidate; do not rewrite, repair, review PDF as primary object, or claim completion.",
                    "projected_outputs": [
                        "adversarial review report",
                        "severity-ranked review findings",
                        "finding actionability report",
                        "validator report"
                    ],
                    "consumed_ref_count": 8,
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "primary",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S13",
                            "validator_ref": "stage_overlay:nature_expert_writing:S13"
                        }
                    ]
                }
            }
        ],
        "handoff_consumers": [
            {
                "stage_id": "S14",
                "stage_name": "Backflow compilation and repair planning",
                "material_id": "s13_pilot_output",
                "ref": "artifacts/S13-adversarial-manuscript-review.json"
            },
            {
                "stage_id": "S16",
                "stage_name": "Export repository hygiene and handoff",
                "material_id": "s13_pilot_output",
                "ref": "artifacts/S13-adversarial-manuscript-review.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S13 links to examples/stage-contracts/S13.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=fixture_generated; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S13 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": null,
            "packet_ref": "examples/packets/phase10_s13_adversarial_review_packet.v1.yaml",
            "required": true,
            "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
            "status": "linked_strict_packet"
        },
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "primary",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S13",
                "validator_ref": "stage_overlay:nature_expert_writing:S13"
            }
        ],
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        }
    },
    "S14": {
        "stage_id": "S14",
        "stage_name": "Backflow compilation and repair planning",
        "status": "validated",
        "coverage_kind": "script_checked",
        "exercise_level": "full_stage_exercised",
        "execution_mode": "hybrid_generated",
        "recommended_agent_type": "planner",
        "contract_ref": "examples/stage-contracts/S14.stage-contract.json",
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "contract": {
            "purpose": "Normalize accepted review/loss findings into nearest-responsible, owner-gated, bounded repair plans without executing repair.",
            "activation_policy": "activate when review finding exists",
            "completion_gate": "S14BackflowRepairPlan validates that every accepted finding is normalized, routed to a nearest responsible concrete stage/material, assigned a bounded local repair task, stale/protected nodes are explicit, owner gates are preserved, and no repair/completion is claimed",
            "consumes": [
                "accepted S13/S16/validator findings",
                "validator reports",
                "affected material graph slice",
                "owner gate policy"
            ],
            "produces": [
                "normalized backflow repair plan",
                "nearest responsible stage map",
                "bounded repair task plan",
                "response action map"
            ],
            "validators": [
                "S14_finding_intake_coverage",
                "S14_duplicate_and_rejection_reason",
                "S14_failure_type_classification",
                "S14_nearest_responsible_stage",
                "S14_no_bare_S09_route",
                "S14_repair_locality",
                "S14_affected_downstream_nodes",
                "S14_protected_unrelated_nodes",
                "S14_owner_gate_status",
                "S14_task_packet_compile",
                "S14_no_execution",
                "S14_no_completion_claim"
            ],
            "backflow_targets": [
                "S04",
                "S05",
                "S06",
                "S07",
                "S08",
                "S09A",
                "S09B",
                "S10",
                "S11",
                "S12",
                "S15",
                "S16",
                "owner"
            ],
            "requires_worker_task_packet": false,
            "worker_packet_coverage": {
                "blocker": "Stage is owner-gated, script-generated, or main-controller assembly; fake worker packets are forbidden.",
                "packet_ref": null,
                "return_contract_ref": null,
                "status": "not_required"
            },
            "subagent_lane_policy": {
                "policy": "conditional_double",
                "default_lane_count": 1,
                "producer_agent_type": "planner",
                "verifier_agent_type": "verifier",
                "escalate_to_double_when": [
                    "repair changes upstream claim/spine/material semantics",
                    "review finding severity is high",
                    "repair plan affects multiple downstream nodes"
                ],
                "rationale": "Backflow planning is controller-owned routing; single planner lane is enough unless severe or multi-node repairs are involved."
            },
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            }
        },
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s14_declared_input_1",
                "ref": "accepted S13/S16/validator findings"
            },
            {
                "kind": "contract_declared",
                "material_id": "s14_declared_input_2",
                "ref": "validator reports"
            },
            {
                "kind": "contract_declared",
                "material_id": "s14_declared_input_3",
                "ref": "affected material graph slice"
            },
            {
                "kind": "contract_declared",
                "material_id": "s14_declared_input_4",
                "ref": "owner gate policy"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s14_source_ref_examples-backflow-tasks-phase7-overclaim-repair-",
                "ref": "examples/backflow_tasks/phase7_overclaim_repair.compiled.v1.yaml"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s14_source_ref_examples-review-findings-phase7-overclaim-v1-yam",
                "ref": "examples/review_findings/phase7_overclaim.v1.yaml"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s13_pilot_output",
                "producer_stage_id": "S13",
                "ref": "artifacts/S13-adversarial-manuscript-review.json"
            }
        ],
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s14_declared_input_1",
                "ref": "accepted S13/S16/validator findings"
            },
            {
                "kind": "contract_declared",
                "material_id": "s14_declared_input_2",
                "ref": "validator reports"
            },
            {
                "kind": "contract_declared",
                "material_id": "s14_declared_input_3",
                "ref": "affected material graph slice"
            },
            {
                "kind": "contract_declared",
                "material_id": "s14_declared_input_4",
                "ref": "owner gate policy"
            }
        ],
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s13_pilot_output",
                "producer_stage_id": "S13",
                "ref": "artifacts/S13-adversarial-manuscript-review.json"
            }
        ],
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s14_source_ref_examples-backflow-tasks-phase7-overclaim-repair-",
                "ref": "examples/backflow_tasks/phase7_overclaim_repair.compiled.v1.yaml"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s14_source_ref_examples-review-findings-phase7-overclaim-v1-yam",
                "ref": "examples/review_findings/phase7_overclaim.v1.yaml"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s14_pilot_output",
                "artifact_path": "artifacts/S14-backflow-compilation-and-repair-planning.json",
                "artifact_type": "review_backflow_projection",
                "description": "normalized backflow repair plan; nearest responsible stage map; bounded repair task plan; response action map",
                "payload": {
                    "artifact_kind": "review_backflow_projection",
                    "purpose": "Normalize accepted review/loss findings into nearest-responsible, owner-gated, bounded repair plans without executing repair.",
                    "projected_outputs": [
                        "normalized backflow repair plan",
                        "nearest responsible stage map",
                        "bounded repair task plan",
                        "response action map"
                    ],
                    "consumed_ref_count": 7,
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "primary",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S14",
                            "validator_ref": "stage_overlay:nature_expert_writing:S14"
                        }
                    ]
                }
            }
        ],
        "handoff_consumers": [
            {
                "stage_id": "S04",
                "stage_name": "Evidence-to-claim admissibility",
                "material_id": "s14_pilot_output",
                "ref": "artifacts/S14-backflow-compilation-and-repair-planning.json"
            },
            {
                "stage_id": "S07",
                "stage_name": "Rhetoric terminology and surface-control synthesis",
                "material_id": "s14_pilot_output",
                "ref": "artifacts/S14-backflow-compilation-and-repair-planning.json"
            },
            {
                "stage_id": "S09A",
                "stage_name": "Control-material selection",
                "material_id": "s14_pilot_output",
                "ref": "artifacts/S14-backflow-compilation-and-repair-planning.json"
            },
            {
                "stage_id": "S15",
                "stage_name": "Repair execution and local regeneration",
                "material_id": "s14_pilot_output",
                "ref": "artifacts/S14-backflow-compilation-and-repair-planning.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S14 links to examples/stage-contracts/S14.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=script_checked; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S14 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": "Stage is owner-gated, script-generated, or main-controller assembly; fake worker packets are forbidden.",
            "packet_ref": null,
            "required": false,
            "return_contract_ref": null,
            "status": "not_required"
        },
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "primary",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S14",
                "validator_ref": "stage_overlay:nature_expert_writing:S14"
            }
        ],
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        }
    },
    "S15": {
        "stage_id": "S15",
        "stage_name": "Repair execution and local regeneration",
        "status": "validated",
        "coverage_kind": "fixture_generated",
        "exercise_level": "full_stage_exercised",
        "execution_mode": "hybrid_generated",
        "recommended_agent_type": "executor",
        "contract_ref": "examples/stage-contracts/S15.stage-contract.json",
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "contract": {
            "purpose": "Execute S14-authorized scoped repairs and regenerate only affected downstream outputs, returning candidate evidence without graph commit or export readiness claims.",
            "activation_policy": "activate when repair task exists",
            "completion_gate": "S15RepairExecutionReport validates strict packet acknowledgement, local diff scope, unrelated-node preservation, stale downstream regeneration/revalidation, finding-resolution evidence, no-new-high-severity scan, CandidateArtifactReturn, verifier evidence, and candidate-only/no-completion boundary",
            "consumes": [
                "strict S14 repair task packet",
                "target material base version",
                "affected downstream stale set",
                "protected unrelated node list"
            ],
            "produces": [
                "repair execution report",
                "revised material candidate",
                "regenerated affected outputs",
                "updated validator report"
            ],
            "validators": [
                "S15_strict_packet_ack",
                "S15_missing_material_report",
                "S15_diff_locality",
                "S15_unrelated_nodes_unchanged",
                "S15_stale_propagation",
                "S15_finding_resolution",
                "S15_no_new_high_severity",
                "S15_overlay_clause_preserved",
                "S15_candidate_return_schema",
                "S15_no_completion_claim"
            ],
            "backflow_targets": [
                "S09B",
                "S10",
                "S11",
                "S12",
                "S15"
            ],
            "requires_worker_task_packet": true,
            "worker_packet_coverage": {
                "blocker": null,
                "packet_ref": "examples/packets/phase10_s15_scoped_repair_packet.v1.yaml",
                "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
                "status": "linked_strict_packet"
            },
            "subagent_lane_policy": {
                "policy": "mandatory_double",
                "default_lane_count": 2,
                "producer_agent_type": "executor",
                "verifier_agent_type": "verifier",
                "escalate_to_double_when": [
                    "always for normal paper-facing production",
                    "full-flow QA mode",
                    "milestone or freeze gate"
                ],
                "rationale": "Repair execution changes accepted materials; independent verification is mandatory to prove the finding is resolved without regressions."
            },
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            }
        },
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s15_declared_input_1",
                "ref": "strict S14 repair task packet"
            },
            {
                "kind": "contract_declared",
                "material_id": "s15_declared_input_2",
                "ref": "target material base version"
            },
            {
                "kind": "contract_declared",
                "material_id": "s15_declared_input_3",
                "ref": "affected downstream stale set"
            },
            {
                "kind": "contract_declared",
                "material_id": "s15_declared_input_4",
                "ref": "protected unrelated node list"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s15_source_ref_examples-packets-claim-repair-packet-v1-yaml",
                "ref": "examples/packets/claim_repair_packet.v1.yaml"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s15_source_ref_examples-candidate-returns-intro-candidate-retur",
                "ref": "examples/candidate_returns/intro_candidate_return.phase7.yaml"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s14_pilot_output",
                "producer_stage_id": "S14",
                "ref": "artifacts/S14-backflow-compilation-and-repair-planning.json"
            }
        ],
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s15_declared_input_1",
                "ref": "strict S14 repair task packet"
            },
            {
                "kind": "contract_declared",
                "material_id": "s15_declared_input_2",
                "ref": "target material base version"
            },
            {
                "kind": "contract_declared",
                "material_id": "s15_declared_input_3",
                "ref": "affected downstream stale set"
            },
            {
                "kind": "contract_declared",
                "material_id": "s15_declared_input_4",
                "ref": "protected unrelated node list"
            }
        ],
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s14_pilot_output",
                "producer_stage_id": "S14",
                "ref": "artifacts/S14-backflow-compilation-and-repair-planning.json"
            }
        ],
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s15_source_ref_examples-packets-claim-repair-packet-v1-yaml",
                "ref": "examples/packets/claim_repair_packet.v1.yaml"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s15_source_ref_examples-candidate-returns-intro-candidate-retur",
                "ref": "examples/candidate_returns/intro_candidate_return.phase7.yaml"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s15_pilot_output",
                "artifact_path": "artifacts/S15-repair-execution-and-local-regeneration.json",
                "artifact_type": "candidate_or_repair_projection",
                "description": "repair execution report; revised material candidate; regenerated affected outputs; updated validator report",
                "payload": {
                    "artifact_kind": "candidate_or_repair_projection",
                    "purpose": "Execute S14-authorized scoped repairs and regenerate only affected downstream outputs, returning candidate evidence without graph commit or export readiness claims.",
                    "projected_outputs": [
                        "repair execution report",
                        "revised material candidate",
                        "regenerated affected outputs",
                        "updated validator report"
                    ],
                    "consumed_ref_count": 7,
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "primary",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S15",
                            "validator_ref": "stage_overlay:nature_expert_writing:S15"
                        }
                    ]
                }
            }
        ],
        "handoff_consumers": [
            {
                "stage_id": "S09B",
                "stage_name": "Per-unit task packet assembly",
                "material_id": "s15_pilot_output",
                "ref": "artifacts/S15-repair-execution-and-local-regeneration.json"
            },
            {
                "stage_id": "S10",
                "stage_name": "Main-text production",
                "material_id": "s15_pilot_output",
                "ref": "artifacts/S15-repair-execution-and-local-regeneration.json"
            },
            {
                "stage_id": "S12",
                "stage_name": "Integration and consistency pass",
                "material_id": "s15_pilot_output",
                "ref": "artifacts/S15-repair-execution-and-local-regeneration.json"
            },
            {
                "stage_id": "S16",
                "stage_name": "Export repository hygiene and handoff",
                "material_id": "s15_pilot_output",
                "ref": "artifacts/S15-repair-execution-and-local-regeneration.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S15 links to examples/stage-contracts/S15.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=fixture_generated; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S15 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": null,
            "packet_ref": "examples/packets/phase10_s15_scoped_repair_packet.v1.yaml",
            "required": true,
            "return_contract_ref": "schemas/ppg-candidate-return.schema.json",
            "status": "linked_strict_packet"
        },
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "primary",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S15",
                "validator_ref": "stage_overlay:nature_expert_writing:S15"
            }
        ],
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        }
    },
    "S16": {
        "stage_id": "S16",
        "stage_name": "Export repository hygiene and handoff",
        "status": "validated",
        "coverage_kind": "script_checked",
        "exercise_level": "full_stage_exercised",
        "execution_mode": "hybrid_generated",
        "recommended_agent_type": "verifier",
        "contract_ref": "examples/stage-contracts/S16.stage-contract.json",
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "contract": {
            "purpose": "Export a closed manuscript candidate into human-readable artifacts and prove delivery hygiene without claiming submission/publication readiness.",
            "activation_policy": "activate when PDF/export, owner preview, handoff, or pre-submission hygiene evidence is requested",
            "completion_gate": "S16ExportHandoffPackage proves explicit delivery target, target binding, upstream closure, separated readiness states, successful human-readable export/build, rendered-surface and semantic text checks, manifest hashes, repository hygiene classification, handoff completeness, feedback routing, and owner-gated/no-submission-publication boundary; compiled PDF targets require content-bearing PDF/source-writeback evidence and cannot be template-only or blocked; compiled semantic surface evidence must include body citation anchors, rendered reference entries, visual/formal artifact coverage, internal-lexicon absence, unresolved-risk leakage absence, and semantic-failure attribution routes.",
            "consumes": [
                "closed S12 integrated manuscript candidate",
                "S13 review closure evidence",
                "S14/S15 repair-complete status",
                "figures/captions/data availability bundle",
                "repository and build configuration state"
            ],
            "produces": [
                "export handoff package",
                "human-readable PDF/export manifest",
                "repository hygiene report",
                "manager/owner handoff report"
            ],
            "validators": [
                "S16_upstream_closure",
                "S16_readiness_state_separation",
                "S16_build_success",
                "S16_pdf_exists_and_surface",
                "S16_figures_captions_present",
                "S16_references_present",
                "S16_data_availability_alignment",
                "S16_export_manifest_hashes",
                "S16_dirty_worktree_classification",
                "S16_handoff_completeness",
                "S16_feedback_route_declared",
                "S16_projection_vs_live_export_boundary",
                "S16_template_only_handoff_boundary",
                "S16_pdf_semantic_surface",
                "S16_body_citation_anchors_present",
                "S16_reference_entries_present",
                "S16_visual_formal_artifacts_present",
                "S16_internal_lexicon_absent",
                "S16_unresolved_risk_leakage_absent",
                "S16_semantic_failure_attribution",
                "S16_compiled_pdf_target_gate",
                "S16_delivery_target_binding",
                "S16_delivery_target_declared",
                "S16_no_submission_ready_overclaim"
            ],
            "backflow_targets": [
                "S12",
                "S13",
                "S14",
                "S15",
                "S16",
                "owner"
            ],
            "requires_worker_task_packet": false,
            "worker_packet_coverage": {
                "status": "not_required",
                "packet_ref": null,
                "return_contract_ref": null,
                "blocker": "S16 is a controller-owned deterministic export/hygiene/handoff verifier; verifier subagents may report checklist evidence but fake worker task packets are forbidden."
            },
            "subagent_lane_policy": {
                "policy": "conditional_double",
                "default_lane_count": 1,
                "producer_agent_type": "verifier",
                "verifier_agent_type": "verifier",
                "escalate_to_double_when": [
                    "handoff/export is owner-facing",
                    "dirty-worktree or build hygiene is ambiguous",
                    "release/submission boundary is near"
                ],
                "rationale": "Export/handoff is mostly deterministic hygiene; escalate when the output is owner-facing or boundary-sensitive."
            },
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            }
        },
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "s16_declared_input_1",
                "ref": "closed S12 integrated manuscript candidate"
            },
            {
                "kind": "contract_declared",
                "material_id": "s16_declared_input_2",
                "ref": "S13 review closure evidence"
            },
            {
                "kind": "contract_declared",
                "material_id": "s16_declared_input_3",
                "ref": "S14/S15 repair-complete status"
            },
            {
                "kind": "contract_declared",
                "material_id": "s16_declared_input_4",
                "ref": "figures/captions/data availability bundle"
            },
            {
                "kind": "contract_declared",
                "material_id": "s16_declared_input_5",
                "ref": "repository and build configuration state"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s16_source_ref_project-status-md",
                "ref": "PROJECT_STATUS.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s16_source_ref_handoff-md",
                "ref": "HANDOFF.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s16_source_ref_manuscript-main-tex",
                "ref": "manuscript/main.tex"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s13_pilot_output",
                "producer_stage_id": "S13",
                "ref": "artifacts/S13-adversarial-manuscript-review.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s15_pilot_output",
                "producer_stage_id": "S15",
                "ref": "artifacts/S15-repair-execution-and-local-regeneration.json"
            }
        ],
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "s16_declared_input_1",
                "ref": "closed S12 integrated manuscript candidate"
            },
            {
                "kind": "contract_declared",
                "material_id": "s16_declared_input_2",
                "ref": "S13 review closure evidence"
            },
            {
                "kind": "contract_declared",
                "material_id": "s16_declared_input_3",
                "ref": "S14/S15 repair-complete status"
            },
            {
                "kind": "contract_declared",
                "material_id": "s16_declared_input_4",
                "ref": "figures/captions/data availability bundle"
            },
            {
                "kind": "contract_declared",
                "material_id": "s16_declared_input_5",
                "ref": "repository and build configuration state"
            }
        ],
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s13_pilot_output",
                "producer_stage_id": "S13",
                "ref": "artifacts/S13-adversarial-manuscript-review.json"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s15_pilot_output",
                "producer_stage_id": "S15",
                "ref": "artifacts/S15-repair-execution-and-local-regeneration.json"
            }
        ],
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s16_source_ref_project-status-md",
                "ref": "PROJECT_STATUS.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s16_source_ref_handoff-md",
                "ref": "HANDOFF.md"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "s16_source_ref_manuscript-main-tex",
                "ref": "manuscript/main.tex"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "s16_pilot_output",
                "artifact_path": "artifacts/S16-export-repository-hygiene-and-handoff.json",
                "artifact_type": "analysis_material_projection",
                "description": "export handoff package; human-readable PDF/export manifest; repository hygiene report; manager/owner handoff report",
                "payload": {
                    "artifact_kind": "analysis_material_projection",
                    "purpose": "Export a closed manuscript candidate into human-readable artifacts and prove delivery hygiene without claiming submission/publication readiness.",
                    "projected_outputs": [
                        "export handoff package",
                        "human-readable PDF/export manifest",
                        "repository hygiene report",
                        "manager/owner handoff report"
                    ],
                    "consumed_ref_count": 10,
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "primary",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "S16",
                            "validator_ref": "stage_overlay:nature_expert_writing:S16"
                        }
                    ]
                }
            }
        ],
        "handoff_consumers": [
            {
                "stage_id": "G02",
                "stage_name": "Derivative and post-paper outputs",
                "material_id": "s16_pilot_output",
                "ref": "artifacts/S16-export-repository-hygiene-and-handoff.json"
            }
        ],
        "validator_evidence": [
            {
                "evidence": "S16 links to examples/stage-contracts/S16.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=script_checked; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "S16 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": "S16 is a controller-owned deterministic export/hygiene/handoff verifier; verifier subagents may report checklist evidence but fake worker task packets are forbidden.",
            "packet_ref": null,
            "required": false,
            "return_contract_ref": null,
            "status": "not_required"
        },
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "primary",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "S16",
                "validator_ref": "stage_overlay:nature_expert_writing:S16"
            }
        ],
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        }
    },
    "G01": {
        "stage_id": "G01",
        "stage_name": "Runtime governance registry",
        "status": "validated",
        "coverage_kind": "script_checked",
        "exercise_level": "full_stage_exercised",
        "execution_mode": "script_generated",
        "recommended_agent_type": "verifier",
        "contract_ref": "examples/stage-contracts/G01.stage-contract.json",
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "contract": {
            "purpose": "Define permissions, route governance, and state controls before automation.",
            "activation_policy": "activate before automation/permissions/state changes",
            "completion_gate": "governance constraints are recorded and cannot inject route metadata into paper-facing cognition",
            "consumes": [
                "state",
                "permissions",
                "skill registry"
            ],
            "produces": [
                "route governance records",
                "state controls",
                "manager boot checklist"
            ],
            "validators": [
                "permission boundary",
                "route registry",
                "state integrity"
            ],
            "backflow_targets": [
                "S00",
                "S16"
            ],
            "requires_worker_task_packet": false,
            "worker_packet_coverage": {
                "blocker": "Stage is owner-gated, script-generated, or main-controller assembly; fake worker packets are forbidden.",
                "packet_ref": null,
                "return_contract_ref": null,
                "status": "not_required"
            },
            "subagent_lane_policy": {
                "policy": "single_with_deterministic_validation",
                "default_lane_count": 1,
                "producer_agent_type": "verifier",
                "verifier_agent_type": null,
                "escalate_to_double_when": [
                    "runtime governance registry or validator semantics change",
                    "full-flow QA mode",
                    "owner requests governance audit"
                ],
                "rationale": "Governance records are registry/validator-controlled and should default to deterministic validation rather than extra agents."
            },
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            }
        },
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "g01_declared_input_1",
                "ref": "state"
            },
            {
                "kind": "contract_declared",
                "material_id": "g01_declared_input_2",
                "ref": "permissions"
            },
            {
                "kind": "contract_declared",
                "material_id": "g01_declared_input_3",
                "ref": "skill registry"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "g01_source_ref_runtime-stage-registry-json",
                "ref": "runtime/stage_registry.json"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "g01_source_ref_examples-stage-contracts",
                "ref": "examples/stage-contracts"
            }
        ],
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "g01_declared_input_1",
                "ref": "state"
            },
            {
                "kind": "contract_declared",
                "material_id": "g01_declared_input_2",
                "ref": "permissions"
            },
            {
                "kind": "contract_declared",
                "material_id": "g01_declared_input_3",
                "ref": "skill registry"
            }
        ],
        "upstream_inputs": [],
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "g01_source_ref_runtime-stage-registry-json",
                "ref": "runtime/stage_registry.json"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "g01_source_ref_examples-stage-contracts",
                "ref": "examples/stage-contracts"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "g01_pilot_output",
                "artifact_path": "artifacts/G01-runtime-governance-registry.json",
                "artifact_type": "script_check_output",
                "description": "route governance records; state controls; manager boot checklist",
                "payload": {
                    "artifact_kind": "script_check_output",
                    "purpose": "Define permissions, route governance, and state controls before automation.",
                    "projected_outputs": [
                        "route governance records",
                        "state controls",
                        "manager boot checklist"
                    ],
                    "consumed_ref_count": 5,
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "governance",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "G01",
                            "validator_ref": "stage_overlay:nature_expert_writing:G01"
                        }
                    ]
                }
            }
        ],
        "handoff_consumers": [],
        "validator_evidence": [
            {
                "evidence": "G01 links to examples/stage-contracts/G01.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=script_checked; exercise_level=full_stage_exercised; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "G01 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": "Stage is owner-gated, script-generated, or main-controller assembly; fake worker packets are forbidden.",
            "packet_ref": null,
            "required": false,
            "return_contract_ref": null,
            "status": "not_required"
        },
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "governance",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "G01",
                "validator_ref": "stage_overlay:nature_expert_writing:G01"
            }
        ],
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        }
    },
    "G02": {
        "stage_id": "G02",
        "stage_name": "Derivative and post-paper outputs",
        "status": "owner_gated",
        "coverage_kind": "owner_gated_deferred",
        "exercise_level": "deferred_with_gate",
        "execution_mode": "owner_gated",
        "recommended_agent_type": "planner",
        "contract_ref": "examples/stage-contracts/G02.stage-contract.json",
        "completion_claim": "pilot_stage_validated_only: contract wiring and local-paper material projection exercised; no final manuscript completion, submission readiness, or publication claim is made",
        "contract": {
            "purpose": "Manage presentation, patent, profile-specific derivative packages, or other post-paper outputs after paper stability or explicit owner request.",
            "activation_policy": "activate only after paper content stability or explicit derivative request",
            "completion_gate": "only explicit owner request can activate derivative output; otherwise recorded not-applicable/deferred",
            "consumes": [
                "stable paper",
                "owner request"
            ],
            "produces": [
                "presentation plan",
                "patent boundary",
                "profile-specific derivative package"
            ],
            "validators": [
                "owner authorization",
                "derivative boundary",
                "no premature submission claim"
            ],
            "backflow_targets": [
                "owner",
                "S16"
            ],
            "requires_worker_task_packet": false,
            "worker_packet_coverage": {
                "blocker": "Stage is owner-gated, script-generated, or main-controller assembly; fake worker packets are forbidden.",
                "packet_ref": null,
                "return_contract_ref": null,
                "status": "not_required"
            },
            "subagent_lane_policy": {
                "policy": "single_with_deterministic_validation",
                "default_lane_count": 1,
                "producer_agent_type": "planner",
                "verifier_agent_type": null,
                "escalate_to_double_when": [
                    "post-paper derivative output is owner-facing",
                    "external-use boundary changes",
                    "owner requests derivative audit"
                ],
                "rationale": "Derivative outputs are outside the main paper cognition path and should stay single-lane until an owner-facing derivative is active."
            },
            "worker_authority_boundary": {
                "completion_forbidden": true,
                "controller_owned_completion": true,
                "no_recursive_orchestration": true
            }
        },
        "consumed_materials": [
            {
                "kind": "contract_declared",
                "material_id": "g02_declared_input_1",
                "ref": "stable paper"
            },
            {
                "kind": "contract_declared",
                "material_id": "g02_declared_input_2",
                "ref": "owner request"
            },
            {
                "kind": "source_or_runtime_ref",
                "material_id": "g02_source_ref_project-status-md",
                "ref": "PROJECT_STATUS.md"
            },
            {
                "kind": "upstream_stage_output",
                "material_id": "s16_pilot_output",
                "producer_stage_id": "S16",
                "ref": "artifacts/S16-export-repository-hygiene-and-handoff.json"
            }
        ],
        "declared_inputs": [
            {
                "kind": "contract_declared",
                "material_id": "g02_declared_input_1",
                "ref": "stable paper"
            },
            {
                "kind": "contract_declared",
                "material_id": "g02_declared_input_2",
                "ref": "owner request"
            }
        ],
        "upstream_inputs": [
            {
                "kind": "upstream_stage_output",
                "material_id": "s16_pilot_output",
                "producer_stage_id": "S16",
                "ref": "artifacts/S16-export-repository-hygiene-and-handoff.json"
            }
        ],
        "source_refs": [
            {
                "kind": "source_or_runtime_ref",
                "material_id": "g02_source_ref_project-status-md",
                "ref": "PROJECT_STATUS.md"
            }
        ],
        "produced_artifacts": [
            {
                "artifact_id": "g02_pilot_output",
                "artifact_path": "artifacts/G02-derivative-and-post-paper-outputs.json",
                "artifact_type": "owner_gate_projection",
                "description": "presentation plan; patent boundary; profile-specific derivative package",
                "payload": {
                    "artifact_kind": "owner_gate_projection",
                    "purpose": "Manage presentation, patent, profile-specific derivative packages, or other post-paper outputs after paper stability or explicit owner request.",
                    "projected_outputs": [
                        "presentation plan",
                        "patent boundary",
                        "profile-specific derivative package"
                    ],
                    "consumed_ref_count": 4,
                    "claim_boundary_snapshot": {
                        "active_method": null,
                        "evidence_spine": "experiments/results/L3_method_faithful_unified_scene_20260625/",
                        "forbidden_overclaim_boundary": "no manuscript claim is active until a fresh S00/S01/S04 intake promotes evidence and claim wording",
                        "manuscript_state": "not_started"
                    },
                    "pilot_note": "Deterministic local-paper pilot projection. It validates stage wiring and material boundaries without mutating or claiming completion of the source manuscript.",
                    "stage_local_overlays": [
                        {
                            "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                            "binding_strength": "derivative",
                            "overlay_id": "nature_expert_writing",
                            "registry_ref": "runtime/stage_overlay_registry.json",
                            "stage_id": "G02",
                            "validator_ref": "stage_overlay:nature_expert_writing:G02"
                        }
                    ]
                }
            }
        ],
        "handoff_consumers": [],
        "validator_evidence": [
            {
                "evidence": "G02 links to examples/stage-contracts/G02.stage-contract.json with completion_gate present",
                "status": "pass",
                "validator": "stage_contract_link"
            },
            {
                "evidence": "source git status and selected fingerprints are unchanged before/after pilot import",
                "status": "pass",
                "validator": "source_read_only_fingerprint"
            },
            {
                "evidence": "coverage_kind=owner_gated_deferred; exercise_level=deferred_with_gate; no source manuscript write claimed",
                "status": "pass",
                "validator": "coverage_boundary"
            },
            {
                "evidence": "G02 has Nature expert-writing overlay binding as stage-local metadata only",
                "status": "pass",
                "validator": "stage_local_overlay_binding"
            }
        ],
        "worker_task_packet_evidence": {
            "blocker": "Stage is owner-gated, script-generated, or main-controller assembly; fake worker packets are forbidden.",
            "packet_ref": null,
            "required": false,
            "return_contract_ref": null,
            "status": "not_required"
        },
        "stage_local_overlays": [
            {
                "authority_boundary": "stage-local overlay only; controller-only routing; controller retains completion authority",
                "binding_strength": "derivative",
                "overlay_id": "nature_expert_writing",
                "registry_ref": "runtime/stage_overlay_registry.json",
                "stage_id": "G02",
                "validator_ref": "stage_overlay:nature_expert_writing:G02"
            }
        ],
        "source_projection_boundary": {
            "projection_scope": "stage wiring/material projection only; source manuscript and evidence directories remain read-only pilot inputs",
            "read_only_source": true,
            "runtime_output_root": "examples/local-paper/sample-paper-workspace",
            "runtime_output_under_source": false,
            "selected_source_fingerprints_unchanged": true,
            "source_git_status_after": "",
            "source_git_status_before": "",
            "source_root": "examples/sample-paper-workspace",
            "source_status_unchanged": true,
            "writes_to_source_allowed": false
        }
    }
};


  return { meta, legend, defaultVisibleKinds, layers, nodes, edges, presets, roadmap, runtimeState, stageCoverage, stageRunDetails };
})();
