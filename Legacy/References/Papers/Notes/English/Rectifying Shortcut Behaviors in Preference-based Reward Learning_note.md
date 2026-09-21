# Rectifying Shortcut Behaviors in Preference-based Reward Learning

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 标题 | Rectifying Shortcut Behaviors in Preference-based Reward Learning |
| 作者 | Wenqian Ye（弗吉尼亚大学）；Guangtao Zheng（Accenture）；Aidong Zhang（弗吉尼亚大学） |
| 机构 | University of Virginia；Accenture（论文注明工作完成于 University of Virginia） |
| 出处 | 第 39 届 Conference on Neural Information Processing Systems（NeurIPS 2025）；arXiv:2510.19050v1 [cs.AI]，2025-10-21 |
| 语言 | 英文 |
| 与课题相关度 | ★★★★☆（把长度/语气/谄媚统一为"捷径特征"，提供"偏好标签中的虚假相关"这一因果语言的权威表述与去偏方法；但对象是奖励模型，不涉及人类 A/B 选择的观察性关联） |
| 原文位置 | `Papers/English/Rectifying Shortcut Behaviors in Preference-based Reward Learning.pdf` |

## 一、三句话概括

1. 论文把奖励模型的 reward hacking 重新表述为"捷径行为"：模型利用响应冗长度、语气、谄媚等与人类偏好标签虚假相关的表层特征，而非真正反映人类意图的目标特征。
2. 作者受核方法中的不变量理论启发提出 PRISM，把各类捷径变换建模为群作用、把捷径特征建模为群不变核，并用随机特征映射给出闭式学习目标，在 Bradley-Terry 排序损失上加入核距离正则项。
3. 实验表明 PRISM 在 RewardBench 与 RM-Bench 等分布外评测上稳定优于基线，并在 RM-Bench 上把奖励分数与长度、语气、谄媚三类捷径的 Pearson 相关系数压到接近零，同时诱导出胜率更高、长度适中的下游策略模型。

## 二、摘要

**原文（逐字）**

> In reinforcement learning from human feedback, preference-based reward models play a central role in aligning large language models to human-aligned behavior. However, recent studies show that these models are prone to reward hacking and often fail to generalize well due to over-optimization. They achieve high reward scores by exploiting shortcuts, that is, exploiting spurious features (e.g., response verbosity, agreeable tone, or sycophancy) that correlate with human preference labels in the training data rather than genuinely reflecting the intended objectives. In this paper, instead of probing these issues one at a time, we take a broader view of the reward hacking problem as shortcut behaviors and introduce a principled yet flexible approach to mitigate shortcut behaviors in preference-based reward learning. Inspired by the invariant theory in the kernel perspective, we propose Preference-based Reward Invariance for Shortcut Mitigation (PRISM), which learns group-invariant kernels with feature maps in a closed-form learning objective. Experimental results in several benchmarks show that our method consistently improves the accuracy of the reward model on diverse out-of-distribution tasks and reduces the dependency on shortcuts in downstream policy models, establishing a robust framework for preference-based alignment.

**中文翻译**

> 在基于人类反馈的强化学习（RLHF）中，基于偏好的奖励模型在让大语言模型对齐人类期望行为方面起核心作用。然而近期研究表明，这类模型容易发生奖励劫持（reward hacking），并常因过度优化而泛化不佳。它们通过利用捷径来获得高奖励分数，即利用与训练数据中人类偏好标签相关、但并未真正反映预期目标的虚假特征（如响应冗长、讨好的语气或谄媚）。本文不去逐个探查这些问题，而是把奖励劫持问题更宏观地视为捷径行为，并提出一种有原则且灵活的方法来缓解基于偏好的奖励学习中的捷径行为。受核视角下不变量理论的启发，我们提出 PRISM（Preference-based Reward Invariance for Shortcut Mitigation），它通过闭式学习目标用特征映射学习群不变核。多项基准上的实验结果表明，我们的方法持续提升奖励模型在多样分布外任务上的准确率，并降低下游策略模型对捷径的依赖，为基于偏好的对齐建立了一个稳健框架。

（完整摘要另见 `Rectifying Shortcut Behaviors in Preference-based Reward Learning_摘要.md`）

## 三、章节结构与内容

| 位置 | 标题（原文） | 内容说明 |
| --- | --- | --- |
| 1 | Introduction | 以 RLHF 与奖励模型为背景，指出 reward hacking / over-optimization 会让奖励模型依赖偏好数据中的虚假属性（谄媚、冗长等），提出统一问题"如何以统一方式矫正 RLHF 中的捷径学习"；给出三条贡献（统一框架、PRISM 方法、理论与实证保证） |
| 2 | Preliminaries | 形式化偏好数据 (x, y_w, y_l)、Bradley-Terry 奖励建模损失、显式/隐式奖励的对齐目标（含 DPO），以及"捷径学习"的潜特征分解（虚假空间 Z_s 与可泛化空间 Z_g）；给出分布外排名准确率下降的表达式（式 (5)） |
| 3 | PRISM: Preference-based Reward Invariance for Shortcut Mitigation | 方法章。3.1 Learning Shortcut Behaviors as Group-invariant Kernels：把捷径变换建模为群作用，用 Haar 积分组合多个群不变核以获得整体不变性；3.2 Approximating Expected Kernel with Feature Maps：用随机特征映射（模板 + 分箱）近似期望核，并以核距离度量"轨道"距离；3.3 Learning Objective and Theoretical Guarantee：给出 PRISM 训练目标（BT 排序损失 + 全局去相关正则 + 边距正则）并证明泛化界 |
| 4 | Experiments | 4.1 Experimental Setup：训练数据为 RLHFlow 混合的 8 个开源偏好数据集，不使用其细粒度属性；捷径特征用规则式（长度=字符数、词汇多样性=TTR）与 LLM-as-a-Judge（GPT-4o 评谄媚/创造力/有用性，0–10 分）提取；实现基于 HuggingFace + DeepSpeed，8 张 NVIDIA A6000，学习率 2e-6，正则权重按课程从 0.01→0.1→0.06；4.2 Main Results：RewardBench 上 PRISM 总分 87.8（同基座 Bradley-Terry 83.6），RM-Bench 上平均 71.0 为最优；相关性分析显示 BT 模型与长度强相关，PRISM 与长度、语气、谄媚的 Pearson 系数均接近零；下游策略（best-of-N 与 DPO）在 AlpacaEval-2 上 WR/LC 胜率更高、长度更短 |
| 5 | Related Works | 两段：RLHF/DPO 脉络；reward hacking 与 shortcut learning 脉络（奖励惩罚、集成、多目标方法与不变表示学习、DRO 等），强调 PRISM 无需属性标注、可同时处理多种捷径 |
| 6 | Conclusion | 总结 PRISM 的统一视角、理论与实证效果，展望捷径感知正则化研究 |
| — | Acknowledgements | 致谢 |
| 附录 | A–F | A 记号表；B 更广泛影响（社会与技术影响）；C 局限（见第八节）；D 理论结果证明（D.1 命题 1 等）；E 训练数据构成（RLHFlow 八个子集及各自样本数）；F 提示工程（谄媚/语气/创造力/有用性的 LLM 评判模板与回退算法） |

## 四、核心创新点与贡献

1. **统一问题框架**：把冗长、语气、谄媚等分散的 reward hacking 现象统一重构为"捷径学习"，与分类任务中利用背景/纹理等虚假特征的经典捷径学习问题对应。
2. **PRISM 方法**：用群作用刻画捷径变换、用群不变核刻画捷径特征，并以随机特征映射近似期望核，得到可闭式训练的显式目标（BT 损失 + 核距离正则），无需细粒度属性标注。
3. **理论保证**：证明 PRISM 目标在温和假设下满足风险/泛化界（附录 D 给出证明）。
4. **多捷径联合去偏**：在 RewardBench 与 RM-Bench 上同时改善 Chat Hard、Safety、Reasoning 等困难类别，优于单捷径惩罚类方法。
5. **相关性与下游验证**：以 Pearson 相关系数直接量化奖励分数与捷径的关联（BT 强相关 → PRISM 近零），并证明去偏奖励模型诱导的策略胜率更高、长度更克制。

## 五、关键词

| 关键词 | 中文 | 在本论文中的重要性 |
| --- | --- | --- |
| Shortcut learning / shortcut behaviors | 捷径学习 / 捷径行为 | 全文统一视角，涵盖长度、语气、谄媚等 |
| Reward hacking / over-optimization | 奖励劫持 / 过度优化 | 被重新解释为捷径的 RLHF 问题 |
| Spurious features / spurious correlation | 虚假特征 / 虚假相关 | 与偏好标签相关但不反映人类意图的属性；长度偏置的核心解释 |
| Preference-based reward model | 基于偏好的奖励模型 | 论文的处理对象 |
| PRISM | — | 作者提出的群不变核去偏方法 |
| Group-invariant kernel | 群不变核 | 理论工具：把捷径变换视为群作用 |
| Random feature map | 随机特征映射 | 把不变核近似成可闭式训练的目标 |
| Pearson Correlation Coefficient (PCC) | 皮尔逊相关系数 | 量化奖励分数与捷径（长度/语气/谄媚）的关联强度 |
| RLHFlow / Preference datasets | — | 训练数据来源（8 个开源偏好数据集混合） |
| RewardBench / RM-Bench | — | 分布外评测基准；RM-Bench 通过风格与语义微扰制造捷径陷阱 |

## 六、与本课题的相关要素

- **结论方向：为"长度等表层特征与偏好标签的关联是虚假相关"提供因果语言的权威表述**。论文明确把 response verbosity 列为 shortcut/spurious feature，指出奖励模型偏爱更长回答源于"长度与理想特质之间在偏好数据中的强虚假相关"；这正是课题在讨论"观察性关联≠因果"时可引用的同向论述（对象为奖励模型，需注明）。
- **与课题的接口方式**：课题的 logistic 回归在**调整后**仍显著的长度/格式系数，可借本文语言解释为"调整了已观测混淆后仍存在的关联，可能对应奖励/偏好数据中的捷径特征"；本文的相关性诊断（PCC）与课题的调整关联、敏感性分析同属"关联强度量化"家族。
- **方法可借鉴处**：(1) 以回归/相关系数直接量化"分数 × 捷径特征"的关联（课题的 logistic 系数可类比其 PCC 诊断的直觉）；(2) 用随机特征映射把多种虚假属性放入同一度量空间联合处理，对应课题把长度与多种格式特征同时纳入模型，避免逐特征单独分析；(3) 课程式正则权重（0.01→0.1→0.06）与课题敏感性分析中的稳健性梯度思路可类比；(4) 论断"消除捷径后长度更克制"可用于讨论去偏后的预期方向。
- **可直接引用的一手数字**：RewardBench 总分 PRISM 87.8 vs Bradley-Terry(Llama-3 8B) 83.6（四类中 Chat Hard 68.3、Safety 91.1、Reasoning 93.1）；RM-Bench 平均 71.0（对照 URM-LLaMa-3.1-8B 70.0、Skywork-Reward-Llama-3.1-8B 70.1）；训练集规模：UltraFeedback 340,025、UltraInteract 161,927、HH-RLHF-Helpful 115,396、SHP 93,301、HelpSteer 37,131、PKU-SafeRLHF 26,874、Distilabel-Capybara 14,811、Distilabel-Orca 6,926。
- **建议引用位置**：引言（"长度/风格等表层特征与偏好标签存在虚假相关"的出处）；方法（多特征联合正则化、把特征放入同一度量空间的思路对照）；讨论（关联≠因果、去偏方向与预期效应）；局限（奖励模型与人类选择属不同层次的证据）。
- **数据是否同源**：否。训练数据为 RLHFlow 混合的 8 个开源偏好数据集（HH-RLHF、SHP、HelpSteer、PKU-SafeRLHF、UltraFeedback、UltraInteract、Distilabel-Capybara、Distilabel-Orca），评测用 RewardBench / RM-Bench / AlpacaEval-2，与 LMArena 系数据无交集。可注意其 UltraFeedback 与 OffsetBias 论文的训练数据存在重叠谱系，但两文与课题数据均不同源。

## 七、可引用段落摘录

> 以下句子逐字取自 PDF 文本层（该文单栏排版，句子可直接核对）。

1. **Abstract（可用于"虚假特征"的定义式表述）**
   > They achieve high reward scores by exploiting shortcuts, that is, exploiting spurious features (e.g., response verbosity, agreeable tone, or sycophancy) that correlate with human preference labels in the training data rather than genuinely reflecting the intended objectives.
2. **§1 Introduction（可用于"长度偏置源于偏好数据中的强虚假相关"）**
   > The most well-studied and noticed manifestation of the problem is length correlations or verbosity [17, 18, 19, 20], where reward models favor longer responses regardless of their relevance to the given prompts due to the strong spurious correlation between the lengths of the responses and their desired traits in the preference data.
3. **§4.2 Main Results（可用于"去偏效果可被相关性指标量化"）**
   > In contrast, the PRISM model achieves near-zero PCCs across all three shortcut dimensions, demonstrating its effectiveness in mitigating shortcut learning.

## 八、局限与引用注意

- **作者自述**（Appendix C Limitations）：(1) 当前实现依赖对具体捷径的先验知识（长度、语气、谄媚），尚不能自动发现与缓解细微或新出现的捷径；(2) 面向更大或更复杂任务时需在计算效率/预算与算法性能之间权衡，LLM 评判式特征提取成本高；(3) 结论限于文本偏好任务，多模态与低资源语言留待未来工作。
- **引用风险 — 对象层次**：本文处理的是**奖励模型**（LLM 训练管线中的代理），不是人类 A/B 偏好数据；其"长度是捷径"的结论应表述为"在奖励模型语境下长度被证明是虚假特征"，不能直接等同于"人类选择中的长度关联是虚假的"；课题（观察性关联、人类真实投票）与本文（干预式去偏、模型代理）层次不同，务必写明。
- **引用风险 — 文本层与表格**：该 PDF 的 Table 1（RewardBench）与 Figure 3 在抽取文本中行标签与数值存在错位（如 RRM/RLHFlow/SSRM/GRM 各行），本笔记只引用可确定行（Bradley-Terry Llama-3 8B 83.6、PRISM 87.8）与正文陈述；引用其他模型分数前须回 PDF 核对。
- **引用风险 — 版本与 venue**：NeurIPS 2025 论文集版本与 arXiv:2510.19050v1 可能存在数字差异；引用时标明版本。论文标注为第 39 届 NeurIPS（2025）。
- **引用风险 — 数据不可比**：其偏好数据来自 OpenAI/Anthropic 等标注或 GPT-4 合成（HH-RLHF、UltraFeedback 等），与课题的 LMArena 真实用户投票在标注者、任务分布、语言分布上均不同，数字仅作机制对照。
- **未确认项**：Figure 3 中策略长度/WR/LC 的具体数值与模型对应关系未能从文本层可靠重建，本笔记未引用；如需引用请在 PDF 中核对原图。
