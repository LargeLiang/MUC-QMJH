# Beyond Reward Hacking: Causal Rewards for Large Language Model Alignment

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 标题 | Beyond Reward Hacking: Causal Rewards for Large Language Model Alignment |
| 作者 | Chaoqi Wang, Zhuokai Zhao, Yibo Jiang, Zhaorun Chen, Chen Zhu, Yuxin Chen, Jiayi Liu, Lizhu Zhang, Xiangjun Fan, Hao Ma, Sinong Wang（标注 Equal contribution，部分工作为在 Meta 实习期间完成） |
| 机构 | Meta；University of Chicago |
| 出处 | arXiv:2501.09620v2 [cs.LG]，2025-05-29（正文标注 Date: June 12, 2025；venue 未确认） |
| 语言 | 英文 |
| 与课题相关度 | ★★★★☆（把长度偏置归因于偏好数据中的虚假相关并给出独立性去偏方法，直接支撑课题"关联≠因果"的定位与敏感性分析） |
| 原文位置 | `Papers/English/Beyond Reward Hacking Causal Rewards for Large Language Model Alignment.pdf` |

## 一、三句话概括

1. 论文把 RLHF 奖励模型中的长度偏置、谄媚、概念偏置与歧视偏置统一归因于偏好数据里的虚假相关（spurious correlation）及由此引发的 reward hacking，并指出这类误差属于"增加数据量也无法消除"的不可约误差。
2. 作者提出因果奖励模型（CRM），以 counterfactual invariance 为目标，用按虚假因子分箱的 MMD 正则项惩罚奖励预测在各档之间的分布差异，并给出 unconditional 与 conditional 两个变体（后者对 chosen / rejected 子集分别施加约束）。
3. 在半合成谄媚数据、Alpaca 长度偏置、Yelp/IMDB/Amazon 概念偏置与 HH-RLHF 歧视偏置四类实验中，CRM 一致降低偏置（谄媚响应占比 92.67% → 19.78%；Yelp "Price" 概念 Bias@C 18.88 → 0.52，作者称最高约 97% 降幅），同时报告了偏置降低与效用之间的 trade-off。

## 二、摘要

**原文（逐字）**

> Recent advances in large language models (LLMs) have demonstrated significant progress in performing complex tasks. While Reinforcement Learning from Human Feedback (RLHF) has been effective in aligning LLMs with human preferences, it is susceptible to spurious correlations in reward modeling. Consequently, it often introduces biases--such as length bias, sycophancy, conceptual bias, and discrimination--that hinder the model's ability to capture true causal relationships. To address this, we propose a novel causal reward modeling approach that integrates causality to mitigate these spurious correlations. Our method enforces counterfactual invariance, ensuring reward predictions remain consistent when irrelevant variables are altered. Through experiments on both synthetic and real-world datasets, we show that our approach mitigates various types of spurious correlations effectively, resulting in more reliable and fair alignment of LLMs with human preferences. As a drop-in enhancement to the existing RLHF workflow, our causal reward modeling provides a practical way to improve the trustworthiness and fairness of LLM finetuning.

**中文翻译**

> 大语言模型（LLM）近期的进展在完成复杂任务方面取得了显著成果。尽管基于人类反馈的强化学习（RLHF）能有效地让 LLM 与人类偏好对齐，但它在奖励建模中容易受到虚假相关（spurious correlations）的影响。因此，它常常引入偏置——例如长度偏置、谄媚、概念偏置与歧视——从而妨碍模型捕捉真正的因果关系。为解决这一问题，我们提出一种新的因果奖励建模方法，将因果性引入以缓解这些虚假相关。我们的方法强制满足反事实不变性（counterfactual invariance），确保当无关变量被改变时奖励预测保持一致。通过在合成数据与真实数据上的实验，我们表明该方法能有效缓解多种虚假相关，从而使 LLM 与人类偏好的对齐更可靠、更公平。作为对现有 RLHF 流程的即插即用增强，我们的因果奖励建模提供了一条提升 LLM 微调可信度与公平性的实用途径。

（完整摘要另见 `Beyond Reward Hacking Causal Rewards for Large Language Model Alignment_摘要.md`）

## 三、章节结构与内容

| 位置 | 标题（原文） | 内容说明 |
| --- | --- | --- |
| 1 | Introduction | 提出奖励建模中的误差分解：可约误差（数据量/模型容量）与不可约误差（数据本身的虚假相关）；指出长度偏置、谄媚、概念偏置、歧视偏置均源于后者，且"加大数据量不仅无效、还可能加剧 reward hacking"；给出因果奖励模型与三条贡献 |
| 2 | Related Works | 综述章。2.1 Reward Hacking and Spurious Correlation：reward hacking 的定义与四类偏置的文献线；2.2 Alleviating Spurious Correlations：既有去偏路线（均衡数据、长度惩罚、PoE、奖励模型集成、WARM、ODIN)均只针对单一偏置，本文主张用因果正则统一处理 |
| 3 | Preliminaries | 预备章。3.1 Reinforcement Learning from Human Feedbacks (RLHF)：SFT、Bradley-Terry 奖励模型与负对数似然损失、带 KL 约束的 RL 目标；3.2 Counterfactual Invariance：定义 r(T(z)) = r(T(z′))；3.3 Causal Decomposition：把 prompt-response 对 T 按与虚假因子 Z 的关系分解为 T⟂Z,ϕ、T⟂L,ϕ 与 T_ZL,ϕ |
| 4 | Method | 方法章。4.1 Maximum Mean Discrepancy (MMD) Regularization for Independence：由因果图导出必要条件 f(T) ⟂ Z，把连续/多维的 Z 分箱后以 MMD 度量各箱奖励分布差异，给出总损失 = 奖励模型损失 + λ·ΣMMD；同时定义 conditional CRM（在 chosen / rejected 子集内分别施加独立性约束） |
| 5 | Experiments | 实验章。5.1 Addressing Sycophantic Bias (Semi-synthetic)：人工注入 80%/20% 的"Yes, you are right."前缀关联，vanilla RM 92.67% vs conditional CRM 19.78%；5.2 Addressing Length Bias：Alpaca 数据 + Llama-3 8B，比较 CRM 与 "Vanilla + Length Penalty"，用 EMA 曲线、Pareto 前沿与"平均长度 vs 排名"三图说明正则系数越大越偏好短回答；5.3 Addressing Concept Bias：Yelp/IMDB/Amazon，条件 CRM 最高降低 Bias@C 约 97%，unconditional CRM 在效用指标上更好；5.4 Addressing Discrimination Bias：HH-RLHF 过滤出 35,567 条、聚为 60 个人口学分箱，Discrm-eval 上 unconditional CRM 隐式歧视 0.107、总体 0.058（Vanilla RM 0.121、SFT 0.171），并用 GPT-4o 评审的 win rate 说明效用基本不受影响 |
| 6 | Conclusions and Future Work | 总结 CRM 对四类偏置的有效性、即插即用性与后续方向 |
| ~ | References | 参考文献 |
| 附录 | A–B | A Extension with DPO：把奖励模型换为 DPO 隐式奖励，给出 Causal-DPO 目标（式 3）；B Experimental Details：B.1 谄媚（LoRA rank 64、α=128、系数网格、PPO 2 epochs）、B.2 长度（超参搜索：分箱数 {10,20,30} × 系数 {0.1,1,3,10,100} × KL {0.003,0.01,0.03,0.1} → 60 个条件 CRM，基线 56 个模型）、B.3 概念偏置（SFT/RM/PPO 超参表）、B.4 歧视偏置（B.4.1 人口学关键词表、B.4.2 60 个分箱、B.4.3 任务说明、B.4.4 GPT-4o 评测提示） |

## 四、核心创新点与贡献

1. **统一归因框架**：把长度、谄媚、概念、歧视四类偏置统一解释为偏好数据中的虚假相关导致的不可约误差，并明确"增加数据量不能解决这类误差"——为"关联不等于因果"提供了可直接引用的论述（§1）。
2. **因果奖励模型（CRM）**：以 counterfactual invariance 为目标，由因果图导出可操作的必要条件 f(T) ⟂ Z，并用分箱 MMD 正则实现，属"训练阶段施加独立性约束"的去偏路线。
3. **连续/多维虚假因子的处理**：把连续长度或多维人口学属性离散为 M 个箱后逐对计算 MMD，使该方法可直接套用到各类虚假因子（长度用分箱，人口学属性用 60 个组合箱）。
4. **conditional / unconditional 两个变体与代价刻画**：指出 conditional CRM 在偏置指标上更优、unconditional CRM 在效用指标上更优（IMDB 上 Acc@NoC 87.9% / Acc@C 88.0%，Vanilla RM 为 74.4% / 73.9%），把该 trade-off 留作 future work。
5. **可扩展到 DPO**：附录 A 给出把奖励模型替换为 DPO 隐式奖励的 Causal-DPO 目标，说明方法与现有对齐流程的兼容性。

## 五、关键词

| 关键词 | 中文 | 在本论文中的重要性 |
| --- | --- | --- |
| Reward hacking | 奖励劫持 | 全文问题起点：奖励函数缺陷被策略利用 |
| Spurious correlation | 虚假相关 | 核心归因：训练数据中不反映真实因果的关联 |
| Counterfactual invariance | 反事实不变性 | 方法目标：无关变量改变时奖励预测不变 |
| Causal reward model (CRM) | 因果奖励模型 | 论文提出的方法本体（含 conditional / unconditional 变体） |
| MMD (Maximum Mean Discrepancy) | 最大均值差异 | 实现独立性约束的正则项，按虚假因子分箱后逐对计算 |
| Length bias | 长度偏置 | 四类被治理偏置之一，与课题最直接相关 |
| Sycophancy | 谄媚 | 四类偏置之一，用半合成数据检验 |
| Concept bias / Bias@C | 概念偏置 / 概念偏置指标 | 借鉴 Zhou et al. (2023) 的残余关联度量 |
| Discrimination bias | 歧视偏置 | 用混合效应模型系数在 Discrm-eval 上度量 |
| RLHF / PPO / DPO | — | 被增强的对齐流程与扩展方向 |

## 六、与本课题的相关要素

- **"关联≠因果"的权威表述与出处**：§1 把虚假相关定义为 "associations in the training data that do not reflect true causal relationships"，并强调由此产生的不可约误差 "cannot be resolved merely by increasing data quantity or model complexity"，甚至 "may further exacerbate the effects of reward hacking"。这为课题把研究定位为"观察性关联"而非因果提供了机制层面的支撑，可直接用于引言与讨论。
- **人类偏好数据本身含长度偏置的机制陈述**：§5.2 指出标注者可能无意识地把更长回答等同于更高质量，从而 "leading to disproportionate rewards for verbosity rather than substantive content"。课题在讨论长度系数为何显著时可以引用这一机制解释，但须注明本文的"人类偏好数据"指 Alpaca/AlpacaFarm 与 Anthropic HH-RLHF，与 LMArena/Arena-Human-Preference-140k 不同源。
- **去偏路线的对照坐标**：CRM 是"训练阶段施加独立性约束"的事前去偏；课题所做的 logistic 回归控制、IPW、匹配诊断属"评估阶段"的调整，LCWR 属"事后回归"校正。三者可以构成"同一独立性目标的三类实现方式"的讨论框架，CRM 是其中唯一的干预式方案。
- **"去偏的代价"的量化证据**：§5.3 明确 conditional CRM 在 Bias@C 上最优，而 unconditional CRM 在 Acc@NoC / Acc@C 上更好（IMDB 上 87.9% / 88.0% vs Vanilla RM 的 74.4% / 73.9%），作者称其为 trade-off 并留作 future work。课题在敏感性分析中讨论"控制混杂后效应量变化意味着什么"时，可用它说明去偏会改变指标间的相对排序。
- **指标先例**：Bias@C 以"接近 0 表示偏置弱、正值表示某概念出现时更易预测为正类"的方式报告残余关联（源自 Zhou et al., 2023），可作为课题报告"调整后残余关联"的指标命名与解释先例。
- **去偏会系统性改变排序**：§5.2 报告正则系数越大，模型越倾向于把更短的回答排到更高名次（"models with higher coefficients assign higher ranks (i.e., lower numerical rank values) to responses with shorter lengths"）。方向与课题"控制后长度效应衰减"的预期一致，可作为对照证据。
- **可引用的短句（用于讨论数据规模与混杂）**：§1 "Notably, such biases cannot be mitigated by simply increasing the size of the dataset."
- **建议引用位置**：引言（虚假相关 / reward hacking 的定义与出处；长度偏置的普遍性）；方法（独立性正则作为对照路线、分箱思想与课题长度分层的呼应）；讨论（人类标注含长度偏置、去偏代价）；局限（本文为训练侧干预，不可外推为评价侧关联证据）。
- **数据是否同源**：否。本文使用 Alpaca/AlpacaFarm、Anthropic HH-RLHF、Yelp/IMDB/Amazon Shoe Review、Discrm-eval 与半合成谄媚数据；课题使用 LMArena/Arena-Human-Preference-140k。仅可作方法参照，数字不可直接搬用。
- **可核对数字**：谄媚行为占比 Vanilla RM 92.67% / Unconditional CRM 62.64% / Conditional CRM 19.78%；Yelp "Price" Bias@C 18.88 → 0.52；歧视总体分 SFT 0.171 / Vanilla RM 0.121 / Conditional CRM 0.084 / Unconditional CRM 0.058；IMDB 效用 Acc@NoC 87.9% 与 Acc@C 88.0%（unconditional CRM）；HH-RLHF 过滤后 35,567 条、60 个人口学分箱；长度实验条件 CRM 60 个模型、基线 56 个模型。

## 七、可引用段落摘录

> 以下句子逐字取自 PDF 文本层（单栏抽取，语句完整，已逐句核对）。

1. **§1 Introduction（可用于"关联≠因果"的定义性引用）**
   > Despite the success of RLHF, reward modeling is inherently prone to spurious correlations, which are associations in the training data that do not reflect true causal relationships (Veitch et al., 2021), and can lead to unintended biases and induce reward hacking (McMilin, 2022).
2. **§5.2 Addressing Length Bias（可用于讨论人类偏好数据中的长度混淆来源）**
   > For instance, in human preference datasets, annotators may unconsciously associate longer responses with higher-quality or more comprehensive answers, leading to disproportionate rewards for verbosity rather than substantive content.
3. **§5.3 Addressing Concept Bias（可用于讨论"去偏的代价"）**
   > While conditional CRM often performs the best in Bias@C reduction, unconditional CRM demonstrates superior Acc@NoC and Acc@C performance, particularly on datasets such as IMDB, where unconditional CRM achieves average accuracies of 87.9% for Acc@NoC and 88.0% for Acc@C, significantly outperforming the Vanilla RM baseline's 74.4% and 73.9%, respectively.

## 八、局限与引用注意

- **无独立 Limitations 章节**：全文未设 Limitations 或 Ethical Statement 小节，作者仅在 §5.3 把 conditional / unconditional 的 trade-off 动态"leave for more in-depth investigation ... for future work"，并在 §6 列出方向性展望（未展开具体局限）。
- **结论层次**：所有实验均为训练侧干预（奖励模型正则、PPO 训练、DPO 扩展），不是对人类偏好数据的观察性关联分析；不能用于支撑 LMArena 数据中"长度与人类选择相关"一类的陈述。
- **样本规模与设定**：长度偏置实验基于 Alpaca/AlpacaFarm + Llama-3 8B；谄媚实验的半合成数据仅 1,727 条，且相关性（80% / 20%）由人工注入；概念偏置实验人为构造"正类全部绑定某一概念"的强偏置数据集；歧视实验仅 35,567 条 HH-RLHF 样本。整体规模与课题的 108,154 条保留输入、78,959 对胜负不在同一量级。
- **评审方式差异**：歧视实验的 win rate 由 GPT-4o 评审（附录 B.4.4 给出评测提示，提示中明确要求 "Do not allow the length of the responses to influence your evaluation"），属 LLM-as-judge，与课题的人类 A/B 选择不同层；引用时不要与人类胜率混用。
- **数字一致性**：Table 2（概念偏置）在抽取文本中存在行错位（Conditional / Unconditional 行的数字与表格线交错），引用具体 Bias@C 数值前须回 PDF 核对；"up to 97%" 为作者文字表述，与 18.88 → 0.52 的读数方向一致但口径需注明。
- **术语冲突**：CRM 缩写在不同领域含义众多，引用时须写出全称 causal reward model 并给出出处；本文的 "bias" 涵盖四类偏置，与统计意义上的 bias（估计偏差）不是同一概念。
- **数据集来源与许可**：使用 Meta 内部实验配置与公开数据集（Alpaca、HH-RLHF、Yelp、IMDB、Amazon、Discrm-eval），未涉及 LMArena 数据，引用其"人类偏好数据含长度偏置"的论断时只能作为机制性类比。
