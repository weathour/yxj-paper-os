# 发表论文中的图组与阅读里程碑

按当前的论证困难选读。这里讨论主图各自承担什么、为何在此出现、读者经过它能判断什么。具体编码与构图转到[绘图技能](../../thesis-figure-skill/SKILL.md)。案例保留实际查看的主图顺序、重点图及正文上下文。

以下13条路线选自[54篇图设计阅读综合](/home/weathour/文档/yxj-wiki/refs/analyses/clusters/scientific-figure-design.md)；完整主图次序、原图及类内比较沿该入口查阅。

## P1 先让读者认清状态，再解释状态的范围

**Shaping active matter from crystalline solids to active turbulence。** [来源](https://www.nature.com/articles/s41467-024-46520-4)；[完整分析](/home/weathour/文档/yxj-wiki/refs/analyses/source-cards/yang2024shaping-active-matter.md)。

主图先给状态实例与相应统计，再把这些状态放进参数域，随后用固定条件切片辨认更细的变化。三个里程碑分别是认得对象、知道出现条件、理解区分依据。地图具有总体性，却不必成为第一张；陌生状态先被解释，地图上的类别才有实质含义。

适合读者尚不熟悉状态身份的论文。若对象已是领域常识，或主要增量恰好是新边界，可以从区域进入。保留实例的理由是它帮助判断类别，而不是作者手头已有一组好看的快照。

## P2 测量如何改变认识，应贯通到派生用途

**Nonlinearity of the post-spinel transition。** [来源](https://www.nature.com/articles/s41467-025-56231-z)；[完整分析](/home/weathour/文档/yxj-wiki/refs/analyses/source-cards/dong2025post-spinel-transition.md)。

先说明相态怎样被读出，再呈现新增测量覆盖及其对边界拟合的影响，最后讨论条件斜率和地理后果。读者依次知道“测到了什么”“为什么新覆盖重要”“新边界改变哪项判断”。用途不需要占据开篇全部篇幅，测量细节也不必独立成为一条故事。

当派生结果吸引眼球时，主文仍应保留产生它的关键比较。反过来，不必逐项报告所有测量记录；决定边界认识的覆盖和估计含义值得主图空间。原文区间定义的差异仍须保留在来源判断中，不能借这条漂亮图序扩大结果保证。

## P3 设计方法需要贯通方案、搜索收益与选择后果

**A self-driving laboratory advances the Pareto front for material properties。** [来源](https://www.nature.com/articles/s41467-022-28580-6)；[完整分析](/home/weathour/文档/yxj-wiki/refs/analyses/source-cards/macleod2022self-driving-laboratory-pareto.md)。

先提出性能权衡并说明自动测量，继而展示实际输入覆盖和经验前沿；搜索收益有自己的比较，选中配方进入另一制造过程后再报告重复结果及成本。读者不仅看到优化器运行，还能判断它发现了什么方案、怎样推进选择、选后有什么结果。

输入空间、性能前沿、算法收益与制造结果可以围绕同一设计问题分工，不必同等篇幅。Fig.3把目标轴、前沿和输入来源接在一起：低温与高温预算可以对应不同配方，有限采样支持经验前沿。Fig.4另比较策略，以无噪声对应点评价有噪声信息下选中的结果，使“决策受噪声影响”与“评价读数受扰动”分开。Fig.6的重复样品再检验新工艺，保留配方同时变化的条件。

这项贡献保留权衡而改变可交付的答案；不同预算的选择信息值得主要图空间。模拟样本收益和实际制造结果互补，不能合成工业耗时。若自己的论文只证明算法性质，就让支持对应那个对象，不必人为补出未经检验的落地结尾。完整贯通分析见源卡的[#contradiction-to-validation](/home/weathour/文档/yxj-wiki/refs/analyses/source-cards/macleod2022self-driving-laboratory-pareto.md#contradiction-to-validation)。

## P4 能力先出现，方法与消融随后解释它

**Learning high-speed flight in the wild。** [来源](https://doi.org/10.1126/scirobotics.abg5810)；[完整分析及accepted版本范围](/home/weathour/文档/yxj-wiki/refs/analyses/source-cards/loquercio2021high-speed-flight.md)。

主图先给实际及模拟行为，使读者认清需要解释的能力；随后比较感知表示，说明训练与执行的信息关系，并用消融回到关键方法选择。方法图在较后位置，仍承担核心职责：解释已经看见的能力如何实现，哪些选择有证据支持。

当能力容易理解、机制需要技术准备时，这种顺序有价值。若能力只有在指标或对象定义后才可理解，则应先给必要准备。不要从“方法图通常第一张”的习惯决定出场，也不要把所有实现模块逐一升级成主图。

## P5 总览作出的承诺，应由不同证据分别回答

**CellRank for directed single-cell fate mapping。** [来源](https://www.nature.com/articles/s41592-021-01346-6)；[完整分析](/home/weathour/文档/yxj-wiki/refs/analyses/source-cards/lange2022cellrank.md)。

总览建立局部转移、状态识别与细胞命运之间的关系。后续预测图、实际谱系和组织层面的检查回到这个问题，让读者分别判断推断对象、对应关系及生物学解释。总览因此有后文可兑现的功能，而不只是章节目录。

相似的安排可对读[MultiVI](https://www.nature.com/articles/s41592-023-01909-9)：跨模态混合、同细胞对应、插补准确性与不确定性是不同评价。图组应让这些判断分别可找到；不能用一个总体性能图或漂亮嵌入同时代替它们。前置框架是否保留，取决于它能否让这些后续证据的关系更容易理解。

## P6 实体、观测、结构分析与模型解释各有职责

**Catalytic reaction chaos。** [来源](https://www.nature.com/articles/s41467-023-36434-y)；[完整分析](/home/weathour/文档/yxj-wiki/refs/analyses/source-cards/raab2023catalytic-reaction-chaos.md)。

首图建立真实表面和观测视野的对应；第二图把局部时间信号与频率行为接回这个对象；第三图分析同步组织并回到空间位置；第四图通过简化耦合模型和扰动比较解释机制。四个节点分别让读者认对象、看现象、理解集体结构、检验一种解释。

真实空间注册若缺失，后续矩阵容易成为抽象图案；模型若过早占主位，实验中需要解释的关系又会退到背景。保留两者的来源身份，让模型解释它实际保留的关系。它们可以互相支持，无需被画成实验结果必然推出模型真值的串行链。

## P7 最后的改变应使用前面已经解释的机制

**Flow interactions lead to self-organized flight formations disrupted by self-amplifying waves。** [来源](https://www.nature.com/articles/s41467-024-47525-9)；[完整分析](/home/weathour/文档/yxj-wiki/refs/analyses/source-cards/newbolt2024flow-interactions-flight-formations.md)。

Fig.1负责对象入口；Fig.2将原坐标、领航相对位置和归一化间隙置于同一时间窗，使平均有序与波动放大并存的关系可见。Fig.3把局部恢复与受迫动态放在同一问题下；Fig.4以模型对照时间、DC和AC关系，并保留下一次改变使用的位置；Fig.5再改变空位或相位。末图因此使用前面已说明的机制，不另开独立用途。

这种安排适合从局部恢复与整链动态的张力走向有条件的可操控关系。保留Fig.5b完整成员剖面，让空位后未立即改善的成员4可见；周期回授是持续扰动，空位也改变其量级，解释需面对这个条件。模型相位与实物空位分支仍有各自对象。结尾若要声称指导改变，应指出具体使用的前一结果及新证据；没有干预证据时，机制解释也可完整收束。完整贯通分析和本轮实际图范围见源卡的[#contradiction-to-validation](/home/weathour/文档/yxj-wiki/refs/analyses/source-cards/newbolt2024flow-interactions-flight-formations.md#contradiction-to-validation)。

## P8 小例子先让信息损失可核对，真实语境再增加判断

**Flow stability for dynamic community detection。** [来源](https://www.science.org/doi/10.1126/sciadv.abj3063)；[完整分析](/home/weathour/文档/yxj-wiki/refs/analyses/source-cards/bovet2022flow-stability.md)。

Fig.1–2以同一事件骨架和固定节点次序，显示跨时状态与同步轨迹问的是不同关系，两个分区的定义先于优化优势。Fig.3区分对植入层级的符合度、重复优化的一致性与计算近似；学校小时日程、鼠群组成和合作网络支持集再分别提供解释语境。扩散速度、时间窗与采样分辨率不能合成一个尺度。

小例子的价值是使关键关系能够被理解和核对。学校两端摘要仍需小时或分窗视图定位中间变化，聚合有其实际任务；不必强迫它输掉每次比较。多数据集各增加什么，应比“我们还测试了三组数据”更早进入正文；没有不同判断的重复结果可以压缩。实际完整段落、原图和条件见源卡的[#contradiction-to-validation](/home/weathour/文档/yxj-wiki/refs/analyses/source-cards/bovet2022flow-stability.md#contradiction-to-validation)。

## P9 模型进入时，应解释已经建立的观测关系

**Touch-evoked traveling waves establish a translaminar spacetime code。** [来源](https://www.science.org/doi/10.1126/sciadv.adr4038)；[完整分析](/home/weathour/文档/yxj-wiki/refs/analyses/source-cards/gonzales2025touch-waves.md)。

Fig. 1–2先建立观测覆盖、单波传播和事件总体；Fig. 3–5联系行为、频段深度和细胞集合；Fig. 6的模型解释宏观波与局部放电现象如何共存，Fig. 7再用扰动约束输入和跨层关系。方法、模型和实验因而围绕同一待解释关系出场。

跨尺度材料不必各自成为独立章节。让每个测量层增加需要解释的一项事实，再让模型承担恰当的解释任务。进一步实验若改变机制判断，就应得到相应主文位置；仅作计算一致性核对的材料则可降低权重。模型图的复杂程度不能替代这项论证职责。

## P10 分组差异从当前解释进入后续投影

**Global climate migration is a story of who and not just how many。** [来源](https://www.nature.com/articles/s41467-025-62969-3)；[完整分析](/home/weathour/文档/yxj-wiki/refs/analyses/source-cards/benveniste2025climate-migration-heterogeneity.md)。

数据覆盖之后，模型性能和人口组响应共同说明总体汇总为何不够；特定气候区的分析深化这种区别，长期条件投影再回答这些群体差异怎样进入未来判断。末图延续前文建立的区别，同时保留组内走廊差异。

当异质性是主问题时，分组图应改变读者对总体结论的理解，而非作为“也考虑了异质性”的补充。后续情景图要使用已经建立的关系，并说明采用的模型与对象；不能让历史估计区间自动变成未来预测保证。群体结构在图组中保持可追踪，比增加许多彼此独立的分布图更有作用。

## P11 实验顺序用于区分原因，而非报出最好设置

**Minion与Saye的高阶时间积分研究。** [来源](https://doi.org/10.1016/j.jcp.2018.08.054)；[完整分析](/home/weathour/文档/yxj-wiki/refs/analyses/source-cards/minion2018higher-order-temporal-navier-stokes.md)。

先分清末节点、末步平均与重算压力，再以充分迭代的周期/边界诊断检查collocation输出；辅助变量导数图显示兼容性困难，固定M的扫数比较与同圆域2M/3M再问有限迭代。读者能判断形式阶对应哪个输出、失阶在哪些条件出现、增加迭代在本例改变什么。

诊断系列和条件对照各有任务，跨不同解析解、黏度或终时的例子不能自动成为严格单因素试验。只保最好的曲线会删掉决定方法范围的失阶与空间平台；不同输出、单步与终时误差也不能接成同一条改进曲线。当前证据支持误差与迭代判断，运行时间优势需要另有成本数据。完整发表单元和原刊不一致的范围见源卡的[#contradiction-to-validation](/home/weathour/文档/yxj-wiki/refs/analyses/source-cards/minion2018higher-order-temporal-navier-stokes.md#contradiction-to-validation)。

## P12 表示转换必须回到可检验的真实对象

**CLEM-Reg。** [来源](https://www.nature.com/articles/s41592-025-02794-0)；[完整分析](/home/weathour/文档/yxj-wiki/refs/analyses/source-cards/krentzel2025clem-reg.md)。

双仪器与框架先建立任务，分割与点云解释怎样获得共同表示；多个数据集的整体叠加之后，未用于求变换的通道对象承担量化检查，最后回到真实标记结构。求对齐、验证和结构解释由不同对象完成，后文逐步兑现方法图的用途。

方法论文的最后实例可以回答新结构怎样被看见，但不能替代中间的误差检查。反过来，只有配准分数也难以说明新表示的科学用途。将两种证据各放在需要它的位置，比一张很大的算法框架或一组漂亮叠加图更完整。

## P13 机制图在证据积累后汇合

**A midbrain circuit mechanism for noise-induced negative valence coding。** [来源](https://www.nature.com/articles/s41467-025-59956-z)；[完整分析](/home/weathour/文档/yxj-wiki/refs/analyses/source-cards/zhou2025midbrain-noise-valence.md)。

主图从表型进入细胞响应，再建立连接与生理作用；并列的局部阻断和下游干预之后，才汇成不同条件下的工作模型。最终箭头的方向和边界因此有前文证据可追，读者也能看见哪些干预回答同一关系的不同方面。

机制示意不必从开篇起就承担全部解释。证据逐渐确立关系时，结尾的综合图可以成为阅读里程碑；若读者需要先认对象，则可另给紧凑背景示意。两图即便使用同一骨架，也应分别承担定位与综合职责，避免把尚待检验的关系提前呈现为既定答案。

使用这些案例时，先说本稿读者当前缺少哪项理解，再选能解决它的顺序。图数、章节数和原文篇幅都不是模板。正文引出应建立比较，解释段应交代推断根据，图注使对象、条件和符号足以恢复；同一句主要结论无需在三处逐字重复。
