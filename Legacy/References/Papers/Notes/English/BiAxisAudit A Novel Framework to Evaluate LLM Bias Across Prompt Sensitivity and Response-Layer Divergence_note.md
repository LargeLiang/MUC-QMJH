# BiAxisAudit: A Novel Framework to Evaluate LLM Bias Across Prompt Sensitivity and Response-Layer Divergence

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 标题 | BiAxisAudit: A Novel Framework to Evaluate LLM Bias Across Prompt Sensitivity and Response-Layer Divergence |
| 作者 | Jialing Gan*, Junhao Dong, Songze Li*（带 * 者为通讯作者；逐人机构对应关系在文本层未标明，未确认） |
| 机构 | Southeast University, China；Nanyang Technological University, Singapore |
| 出处 | arXiv:2605.09041v1 [cs.CL]，2026-05-09（预印本；正文提到拟提交 NDSS Artifact Evaluation track，实际 venue 未确认） |
| 语言 | 英文 |
| 与课题相关度 | ★★★★☆（用因子实验量化"提示/格式一变、测量结论就变"以及"交互项大于主效应、跨配置平均会把方向相反的错误合并"，与课题的格式混淆、稳健性与敏感性分析层高度可对话） |
| 原文位置 | `Papers/English/BiAxisAudit A Novel Framework to Evaluate LLM Bias Across Prompt Sensitivity and Response-Layer Divergence.pdf` |

## 一、三句话概括

1. 论文把 LLM 偏见审计重新定义为"测量可靠性"问题：现有基准把提示模板当作固定的中性仪器、把回答压成一个标表层标签，于是留下两个结构性独立的盲点，厂商只需"挑提示词/挑编码层"就能在不改任何模型权重的情况下通过合规审查。
2. 为此提出 BiAxisAudit——横轴把 task、perspective、role、sentiment 四个提示维度作为实验变量（OAT 网格 21 个条件、401 个模板）并报告分布而非点估计；纵轴用 Split Coding 把 Selection 与 Elaboration 两层独立编码，用 Inconsistency Rate（IR）与 Divergence Net Imbalance（DNI）刻画分歧的幅度与方向。
3. 在 8 个模型、每个模型 80,200 条编码响应上，任务格式解释的方差份额与"模型身份"相当（0.395）、平均 IR 为 17.6%（约每五条就有一条与自身表层标签矛盾）、提示维度交互项超过相应主效应，"跨配置平均"并未消除误差而是把方向相反的错误合并成一个看似校准的分数。

## 二、摘要

**原文（逐字）**

> Bias auditing of large language models is increasingly shaped by voluntary governance frameworks such as the NIST AI RMF and binding regulatory regimes such as the EU AI Act. Consequently, benchmark reliability has become a security property in its own right. Yet existing benchmarks often reduce bias to a single scalar derived from a fixed prompt format and a single surface-level label, leaving two blind spots that a vendor can exploit without modifying any model weights. These blind spots are structurally independent (correcting one leaves the other unconstrained) and compound in practice rather than cancel. Across prompts, meaning-preserving format changes shift bias endorsement by more than 0.7 on a fixed statement pool. Within a single response, the discrete Selection and the free-text Elaboration can express opposing stances, so a clean aggregate can mask widespread internal inconsistency (a "cancellation trap"). Consequently, selection-only and elaboration-only rankings are nearly uncorrelated across eight LLMs (Spearman ρ = 0.238, p = 0.570): LLaMA3-70B ranks mid-pack under selection-only yet highest under elaboration-only on the same responses. We introduce BIAXISAUDIT, a protocol that pairs every bias score with a reliability estimate along two orthogonal axes. The across-prompt axis presents each statement under a factorial grid of task format, perspective, role, and sentiment, reporting bias as a distribution rather than a point estimate. The within-response axis applies Split Coding to recover Selection and Elaboration as independent signals, quantified by the Inconsistency Rate and Divergence Net Imbalance. Across eight LLMs with 80,200 coded responses each, task format alone explains as much variance in bias scores as the choice of model; 63.6% of bias signals in the pooled audit (up to 85.2% per model) appear in only one coding layer and prompt-dimension interactions exceed main effects, which together rule out any single-axis report as a reliable audit. The same instrument also distinguishes genuine bias reductions from apparent ones caused by cross-layer redistribution: some prompt configurations reduce both BER and IR simultaneously, while others suppress only the selection-layer score, leaving the elaboration-layer bias intact, a pattern that single-scalar audits cannot detect.

**中文翻译**

> 大语言模型的偏见审计正日益受到自愿性治理框架（如 NIST AI RMF）与具有约束力的监管制度（如 EU AI Act）的塑造。因此，基准的可靠性本身已成为一种安全属性。然而现有基准往往把偏见压缩成由固定提示格式与单一表层标签导出的一个标量，留下两个厂商无需修改任何模型权重即可利用的盲点。这两个盲点在结构上相互独立（修正其一并不约束其二），在实践中会叠加而非相互抵消。就提示而言，在固定陈述池上，保持语义不变的格式变化可使偏见认同率变动超过 0.7。在单条回答内部，离散的 Selection 与自由文本的 Elaboration 可以表达相反的立场，因此一个干净的汇总值可能掩盖广泛的内部不一致（"抵消陷阱"）。于是，仅按 Selection 与仅按 Elaboration 得到的模型排名在八个 LLM 上几乎不相关（Spearman ρ = 0.238，p = 0.570）：在同一批回答上，LLaMA3-70B 在 selection-only 下处于中游，却在 elaboration-only 下排在最前。我们提出 BIAXISAUDIT：该协议为每一个偏见分数配一个沿两条正交轴的可靠性估计。跨提示轴把每条陈述置于 task format、perspective、role 与 sentiment 的因子网格下，把偏见报告为分布而非点估计。回答内轴用 Split Coding 把 Selection 与 Elaboration 还原为独立信号，并以 Inconsistency Rate 与 Divergence Net Imbalance 加以量化。在八个 LLM、每个模型 80,200 条编码回答上，仅任务格式一项对偏见分数方差的解释力就与模型选择相当；汇总审计中有 63.6% 的偏见信号（单模型最高 85.2%）只出现在一个编码层，且提示维度之间的交互项超过主效应——这些共同排除了以任何单轴报告作为可靠审计的可能。同一工具还能区分真实的偏见下降与由跨层重分配造成的表面下降：某些提示配置同时降低 BER 与 IR，另一些则只压低 selection 层的分数、让 elaboration 层的偏见原封不动，而这种模式是单标量审计无法察觉的。

（完整摘要另见 `BiAxisAudit A Novel Framework to Evaluate LLM Bias Across Prompt Sensitivity and Response-Layer Divergence_摘要.md`）

## 三、章节结构与内容

| 位置 | 标题（原文） | 内容说明 |
| --- | --- | --- |
| I | INTRODUCTION | 以"同一权重、不同提示模板得到 0.06 与 0.78 两个分数"的思想实验提出问题，列出三种失败模式（format warps the verdict / labels betray the stance / errors cancel silently）、四个 RQ 与四条贡献 |
| II | RELATED WORK | II.A Bias Auditing as a Pre-Deployment Control：偏见审计已成为合规控制，CrowS-Pairs/StereoSet/BBQ/CEB/F2Bench/CLEAR-Bias/BVF 都以固定模板 + 单标签为前提；II.B Prompt Sensitivity and Audit-Score Stability：提示扰动会大幅改变测量，既有工作把敏感性归于模型属性而非仪器属性；II.C Response-Level Divergence between Selection and Reasoning：思维链忠实性与 LLM-as-judge 研究表明标签编码本身不可靠 |
| III | PROBLEM FORMULATION | 形式化章。给出威胁模型（厂商 V 用不同模板分别通过 EU 与 NIST 两套报送）、威胁为"测量面"威胁；III.A Label Space：五类立场标度；III.B Split Coding and the BER Family：定义 BERsel/BERelab/BERcor/BERunion 与 OED/UED；III.C Divergence Metrics；III.D Inconsistency Rate and Divergence Net Imbalance：定义 IR 与有符号的 DNI；III.E Two-Axis Reliability：给出 Proposition 3（两轴不可互推） |
| IV | BIAXISAUDIT DESIGN | 设计章。IV.A Design Goals；IV.B Stereotype Statement Pool：200 条刻板印象陈述、10 个社会维度、改编自 CLEAR-Bias；IV.C Prompt Dimensions and Main-Effects Instrumentation：四个维度共 21 个 OAT 条件、401 个模板、64 = 1,296 的全因子为上界；IV.D Two-Layer Response Coding：selection 层由正则确定性抽取（不达标时才升级给 LLM judge 解析）、elaboration 层由三名评委多数票编码 |
| V | EVALUATION | 实验章。V.A Setup recap and judge validation：8 个模型（5 闭源 3 开源）、80,200 条/模型、8,016 条一致性样本、elaboration 层 Cohen's κ 均值 0.74、selection 层 0.99，选 Qwen Plus + Gemini 3 Flash + GPT-5.4 组成 vote-3 评委团；V.B RQ1：任务格式的方差解释份额 0.395，任务均值跨模型 0.07–0.56，DeepSeek-V3 从 CTO 的 0.784 到 BJ 的 0.064；V.C RQ2：DeepSeek-V3 的 (BERcor, BERsel, BERelab, BERunion) = (0.172, 0.377, 0.248, 0.453)，(IR, DNI) = (0.282, +0.129)，全模型 IR 均值 0.176、5 个 DNI>0 3 个 DNI<0；V.D RQ3：3×2×2×2 子因子（24 格、各 n≥1,027），skeptical 使 CTO 的 BERsel 降 26 pp 却使 SC 升 6 pp，task×sentiment 交互份额 0.043；V.E Threats to validity：评委团与被审模型同源、各模型 divergence-eligible 基数极不均衡 |
| VI | LIGHTWEIGHT BIAS MITIGATION AT INFERENCE TIME | 把两条轴当作防御工具。VI.A Two-axis verdicts diverge from single-scalar verdicts：task reformulation（CTO→BJ，BERsel 0.675→0.104）两轴同降是真降；free-response 任务 BERsel 结构性为 0 而 elaboration 层偏见仍在 0.10，属"仅表层重分配"；role conditioning 五个角色都降（ai_ethicist 降 83%）；negative sentiment 反而使 BERsel 升 22.2 pp；VI.B Pareto-optimal configuration and non-additive interaction：BJ × ai_ethicist × neutral 使 BERsel=0.024（相对 CTO 基线降 96%），BJ+ai_ethicist 联合降幅 68.7 pp 低于可加预期 72.0 pp |
| VII | DISCUSSION AND LIMITATIONS | Discussion：审计链条（基准→模型卡→合规证据）继承了"提示格式偏见中性"这一未经检验的前提；A. Two-axis verdicts / Same instrument, opposite vantage：同一批提示维度既是厂商操纵杠杆也是防御杠杆；Limitations and responsible use：自述局限（见第八节） |
| VIII | CONCLUSION | 总结三种测量失败与两轴工具的"可复用仪器"定位 |
| — | ETHICS CONSIDERATIONS | 刻板印象内容的再伤害防护、LLM-as-judge 的有效性声明、artifact 发布计划（Apache-2.0 代码 / CC-BY-4.0 数据、拟投 NDSS AE） |
| — | REFERENCES | 参考文献 |
| 附录 | APPENDIX A–F | A 陈述池分布（Table V）；B 指标定义与分母约定（Table VI）；C 补充 BER 结果与编码不对称（QE 只存在于 elaboration 层的语言学依据，折叠后 |IR| 变动 <1 pp）；D 与既有工作的三点区分；E 三个单条回答的失败模式案例（含完整编码链路走查）；F 推理期缓解的扩展结果（实验设计、四个维度的完整分解、配置配方、定性案例） |

## 四、核心创新点与贡献

1. **把偏见审计重构为测量可靠性 / 安全控制问题**：提出"prompt-shopping"威胁（不改权重、只改审计仪器即可让有偏模型通过合规审查），并主张基准分数的稳定性应作为可审计属性一并报告。
2. **两轴工具**：横轴把提示格式当实验变量（4 维、21 个 OAT 条件、401 个模板）报告分布；纵轴用 Split Coding 把 Selection 与 Elaboration 分离，得到 BER 家族与可靠性对 (IR, DNI)。
3. **"抵消陷阱"（cancellation trap）这一诊断概念**：当两层分歧方向相反时，DNI≈0 会让一个有问题的审计看起来"平衡"，单标量无法识别。
4. **因子实验证据**：任务格式的方差解释份额（0.395）与模型身份相当，且提示维度交互项大于相应主效应，说明"跨提示配置平均"不是去噪而是合并方向相反的错误。
5. **同一工具可区分"真降偏"与"重分配"**：co-reducing（BER 与 IR 同降）与 layer-rerouting（只压一层）可被区分；Pareto 配置在 BERsel 上相对 CTO 基线降 96%，并暴露单轴看不见的 task×role 非可加交互。

## 五、关键词

| 关键词 | 中文 | 在本论文中的重要性 |
| --- | --- | --- |
| Bias auditing | 偏见审计 | 研究对象，被重构为合规链上的测量控制 |
| Prompt sensitivity | 提示敏感性 | 横轴问题的来源；同一模型可给出差异极大的分数 |
| Split Coding | 分层编码 | 纵轴方法：把 Selection 与 Elaboration 独立编码 |
| BER (Bias Endorsement Rate) | 偏见认同率 | 主指标族（BERsel / BERelab / BERcor / BERunion） |
| Inconsistency Rate (IR) | 不一致率 | 两编码层分歧的幅度，审计不可靠性的量化指标 |
| Divergence Net Imbalance (DNI) | 分歧净不平衡 | 分歧的有符号方向，用于区分高估与低估 |
| Cancellation trap | 抵消陷阱 | 方向相反的错误在汇总中相互抵消的危险情形 |
| Prompt-shopping | 挑提示词 | 论文命名的新攻击面：不改权重只选模板 |
| Factorial / OAT design | 因子设计 / 单因素扫描 | 实验方法骨干（21 条件 OAT 网格、3×2×2×2 子因子） |
| LLM-as-a-judge | 以 LLM 为评委 | elaboration 层编码方式（vote-3 多数票），也是其有效性风险来源 |

## 六、与本课题的相关要素

- **结论方向（对课题构成方法论挑战与警示）**：本文证明"测量结论高度依赖提示/任务格式"——任务格式对偏见分数的方差解释份额与模型身份相当，且提示维度交互项大于相应主效应。课题的 Arena 数据同样包含高度异质的提示（任务类别与 7 种提示词属性），这提示"长度/格式与选择的关联"很可能也随提示维度变化，应在讨论中明确"关联是在给定提示分布下估计的"。
- **可直接借用的概念与措辞**：`cancellation trap`（方向相反的错误在汇总中抵消，使指标看似校准）、`prompt-shopping`（不改权重只换仪器）、"averaging across prompt configurations ... combines structurally opposed errors"、`(IR, DNI)` 这种"分数 + 可靠性对"的并列报告方式。课题可类比地报告"长度效应与格式效应在子样本中的符号差异"，以及"跨子集平均可能掩盖方向相反的子群效应"。
- **方法可借鉴处**：① 单因素扫描（OAT）+ 因子设计分离主效应与交互项——课题在稳健性/敏感性分析中已做子集分层，可补一句"格式与长度交互"的检验；② 把测量可靠性作为与主指标并列的第二输出；③ 对"分歧方向"建档（有符号差值），而不是只报绝对值；④ 把"修正一个盲点不约束另一个"（两轴相互独立）的论证方式，用于说明课题的"控制在任务类别/模型身份后仍需控制格式"。
- **可引用数字（均来自原文）**：任务格式方差解释份额 0.395 vs 其余三维度各 0.014；跨模型任务均值 0.07–0.56；DeepSeek-V3 BERunion CTO=0.784 与 BJ=0.064；Claude Sonnet 4.6 的最大/最小分比 175×；IR 均值 0.176（范围 0.026–0.318），pooled IR=0.184；pooled BERsel 0.236 vs BERunion 0.290；单层信号占比均值 63.6%（最高 85.2%）；task×sentiment 交互 0.043 对 sentiment 主效应 0.009；CTO→BJ 使 BERsel 由 0.675 降至 0.104；ai_ethicist 使 BERsel 由 0.138 降至 0.024；negative sentiment 使 BERsel 升 22.2 pp（p<0.001）；200 条陈述 / 401 模板 / 80,200 条每模型 / 641,600 条总实例 / 38,400 条子因子实例。
- **建议引用位置**：引言（"格式/提示改变测量结论"的旁证与出处，注意本文语境是偏见审计而非人类偏好）；方法（交互项设定、把可靠性指标与主指标并列报告）；讨论（"平均不消除误差""分数依赖仪器选择"）；局限（明确本文对象是 LLM 审计而非人类选择）。
- **数据是否同源**：否。自建 200 条刻板印象陈述 × 401 模板 × 8 个英文文本模型（RQ1/RQ2 每模型 80,200 条，共 641,600 条；RQ3 子因子 38,400 条），与 Arena-Human-Preference-140k 不同源、任务不同（立场编码 vs 人类 A/B 选择）。

## 七、可引用段落摘录

> 以下句子逐字取自 PDF 文本层（该文双栏排版且图注与正文存在逐行交错，已按句子顺序重组；仅去除换行连字符）。

1. **§III PROBLEM FORMULATION（Threat Model；可用于"仪器选择即可改变结论"）**
   > The attack reduces to prompt-shopping: by selecting the prompt subset, task format, or coding scheme under which a model scores most favourably, the vendor can induce a score difference exceeding 0.7 between audit instruments evaluated on an identical model, causing a biased model to pass a compliance review through instrument selection rather than genuine alignment.
2. **§VII DISCUSSION AND LIMITATIONS（可用于讨论"关联只在给定测量条件下成立"）**
   > A model that passes a single-format audit has therefore not been shown to be unbiased, only unbiased against the auditor's prompt choice.
3. **§V EVALUATION, RQ1（可用于"结论依赖测量条件"与稳健性论证）**
   > In sum, BERunion is not a stable property of a model but of the prompt-model pair, and prompt choice alone shifts the measured score by an order of magnitude.

## 八、局限与引用注意

- **作者自述局限（§VII Limitations and responsible use）**：BiAxisAudit 刻画的是测量方差而非社会危害的全空间；范围限于 200 条陈述、10 个偏见类别、8 个英文纯文本模型与 401 个模板，多模态、多语言与纵向部署留作未来工作；Split Coding 依赖 LLM 评委，可能带有自身偏见，作者只报告一致性并明确"不主张 LLM 评委等同于受过训练的人类标注者"；BER 与 (IR, DNI) 是审计仪器而非公平性认证（高认同率不蕴含下游危害、低认同率不蕴含安全）；论文只量化"审计可能错报多少"，不主张确有厂商择优。
- **样本规模与统计力**：作者自己承认 n=8 太小，既不足以确立独立也不足以确立相关（leave-one-out 范围 [−0.143, 0.429]）；3×2×2×2 是非平衡子因子而非全因子，作者指出平衡全因子估计可能重加权结论；divergence-eligible 基数在模型间极不均衡（GPT-OSS 20B n=1,583、GPT-5.4 n=2,648，其余六个 9k–13k），且过度代表 CTO/SC 等会产出阐释的任务。
- **数字一致性（引用前须核对原文）**：§VI.A 写 "Switching from CTO to BJ reduces mean BERsel from 0.675 to 0.104 (-57.3 pp, ...)"，但 0.675 − 0.104 = 57.1 pp，与文中 57.3 pp 不一致；另 §VII 引述 "lowers endorsement by 26 pp on one task while raising it on another" 与 §V.D 的 26 pp / 6 pp 一致，引用时以 §V.D 为准。
- **分类与命名前后不一致**：§V.A 把 DeepSeek V3 归为 open-source（"3 open-source: DeepSeek V3, LLaMA-3 70B, GPT-OSS 20B"），而 Figure 8 图注写 "closed-source (top 6 ...) vs. open-source (bottom 2 ...)"；模型名亦混用 "LLaMA3-70B" 与 "LLaMA-3 70B"、"Gemini 3 Flash" 与 "Gemini-3F"。
- **文本层符号缺失**：PDF 文本层丢失了 χ²、ρ、κ 等希腊字母与部分上标。本笔记中"方差解释份额"（原文写作 χ² 类符号，如 2=0.395）与摘要中的 Spearman ρ 均为按上下文恢复，**引用符号前必须回 PDF 核对**。
- **结论层次**：本文的对照物是"权重不变、只换审计模板"的 LLM 偏见审计场景，与课题"人类 A/B 选择的观察性关联"在对象、任务与数据上均不同源；其数字不可直接搬来支撑课题关于长度/格式与人类选择的结论，只宜作为方法论警示与措辞来源。
