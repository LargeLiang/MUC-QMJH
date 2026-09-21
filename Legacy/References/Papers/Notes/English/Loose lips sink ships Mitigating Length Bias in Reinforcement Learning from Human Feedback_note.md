# Loose lips sink ships: Mitigating Length Bias in Reinforcement Learning from Human Feedback

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 标题 | Loose lips sink ships: Mitigating Length Bias in Reinforcement Learning from Human Feedback |
| 作者 | Wei Shen, Rui Zheng, Wenyu Zhan, Jun Zhao, Shihan Dou, Tao Gui, Qi Zhang, Xuanjing Huang |
| 机构 | 复旦大学计算机科学技术学院；International Human Phenome Institutes (Shanghai)；复旦大学现代语言学研究院（Institute of Modern Languages and Linguistics） |
| 出处 | arXiv:2310.05199v5 [cs.CL]，2023-11-29（正文无会议/期刊标识，venue 未确认） |
| 语言 | 英文 |
| 与课题相关度 | ★★★★☆（把长度明确写成偏好建模的混杂因子，并给出"去偏只能缓解、有代价"的实例，是课题混淆控制与局限讨论的直接对话对象） |
| 原文位置 | `Papers/English/Loose lips sink ships Mitigating Length Bias in Reinforcement Learning from Human Feedback.pdf` |

## 一、三句话概括

1. 论文指出 RLHF 的奖励模型会走捷径、把"人类偏好更长的回答"当作规律（length bias），使策略倾向生成更长输出，而更长并不等于更多有用信息。
2. 作者把长度视为偏好奖励建模中的混杂因子（confounder），提出 Product-of-Experts（PoE）双专家框架：主专家学人类意图、偏置专家专门捕捉长度，并对偏置专家的输入注入高斯噪声破坏语义信息。
3. 在 HH-RLHF 与 rm-static 两个数据集、LLaMA/BLOOMZ/Alpaca 三种设置上，该方法在提升奖励分数与胜率的同时抑制了输出长度增长，长度与奖励分数的相关系数普遍下降。

## 二、摘要

**原文（逐字）**

> Reinforcement learning from human feedback serves as a crucial bridge, aligning large language models with human and societal values. This alignment requires a vast corpus of human feedback to learn a reward model, which is subsequently used to finetune language models. However, we have identified that the reward model often finds shortcuts to bypass its intended objectives, misleadingly assuming that humans prefer longer responses. The emergence of length bias often induces the model to favor longer outputs, yet it doesn't equate to an increase in helpful information within these outputs. In this paper, we propose an innovative solution, applying the Product-of-Experts (PoE) technique to separate reward modeling from the influence of sequence length. In our framework, the main expert concentrates on understanding human intents, while the biased expert targets the identification and capture of length bias. To further enhance the learning of bias, we introduce perturbations into the bias-focused expert, disrupting the flow of semantic information. Experimental results validate the effectiveness of our approach, indicating that language model performance is improved, irrespective of sequence length.

**中文翻译**

> 基于人类反馈的强化学习是一座关键桥梁，使大语言模型与人类及社会价值保持一致。这种对齐需要大量人类反馈语料来学习一个奖励模型，再用该奖励模型微调语言模型。然而我们发现，奖励模型常常找到捷径绕过其原本目标，错误地假定人类偏好更长的回答。长度偏置的出现往往使模型偏爱更长的输出，但这并不等于这些输出中有用信息的增加。本文提出一种新方案，用 Product-of-Experts（PoE）技术把奖励建模与序列长度的影响分离开来。在我们的框架中，主专家专注于理解人类意图，偏置专家则负责识别和捕捉长度偏置。为进一步加强偏置的学习，我们向聚焦偏置的专家引入扰动，破坏语义信息的流动。实验结果验证了本方法的有效性，表明语言模型性能得到提升，且与序列长度无关。

（完整摘要另见 `Loose lips sink ships Mitigating Length Bias in Reinforcement Learning from Human Feedback_摘要.md`）

## 三、章节结构与内容

| 位置 | 标题（原文） | 内容说明 |
| --- | --- | --- |
| 1 | Introduction | 以 Figure 1 的对话实例说明奖励模型偏爱长回答、导致模型退化，并提出 PoE 双专家思路与三条贡献 |
| 2 | Related Work | 无编号小节：*Reinforcement Learning from Human Feedback*、*Reward Hacking*（Goodhart's law）、*Products-of-Experts*（Clark et al. 2019 去偏集成、Karimi Mahabadi et al. 2020 端到端）；此处明确把"人类偏好的长度"当作混杂因子 |
| 3 | Preliminary | 交代 RLHF 三阶段（SFT、Reward Modeling、RL Optimization）、Bradley-Terry 奖励损失式 (1) 与含 KL 惩罚的 PPO 目标 |
| 4 | Length Bias in Reward Model | 现象与归因章。4.1 Length Bias Phenomenon：4000 条 SFT 输出显示奖励分数与长度强相关，TL;DR 任务同样存在（Appendix A.4）；4.2 Confounding Factor：给出因果结构图（Figure 3），长度偏置为混杂因子 z，另有标注者噪声 η；4.3 Challenges：指出该虚假相关在传统 ERM 框架下难以处理，提出用集成去偏与表示解耦应对 |
| 5 | Proposed Method | 方法章。5.1 PoE Framework：r̂(x,y) 由两个专家的输出相乘/softmax 组合；5.2 Injecting Noise into Bias-only Expert：X̃ = X + N（token embedding 上的高斯噪声）；5.3 Training & Inference：两个专家按式 (2) 联合优化，PPO 阶段只用主专家，因此开销增加有限 |
| 6 | Experiments | 6.1 Settings：HH 与 rm-static 数据、LLaMA/BLOOMZ、SFT 与 PPO 超参、baseline 定义；6.2 True Reward Improvement：本方法奖励更高同时平均输出更短（Table 1）；6.3 Wining Rate（原文标题拼写）：人类、AlpacaFarm、GPT-4 三方评测胜率（Table 3）；6.4 Ablation Study：PoE 与输入扰动都提升奖励模型准确率（Table 2，数值受文本层列交错影响，见第八节） |
| 7 | Analysis and Discussion | 7.1 Leaning Curve（原文标题拼写）：训练曲线显示 vanilla RM 的输出长度持续增长、本方法保持稳定；7.2 Distribution of Reward Scores：本方法对 chosen/rejected 的区分度更好（Figure 5） |
| 8 | Conclusion | 总结长度偏置的挑战与 PoE 的缓解效果 |
| Limitations | Limitations（无编号） | 只能缓解不能完全消除；仅在两个 RLHF 数据集上验证，更大数据集是否成立不确定；人类评测只取有限样本 |
| — | Acknowledgements / References | 基金致谢与参考文献 |
| A | Appendix（A.1–A.6） | A.1 生成长度与奖励的 Spearman/Pearson 相关系数（Table 4）；A.2 bias-only 模型规模消融（Table 5）；A.3 PPO 训练稳定性；A.4 TL;DR 摘要任务中的长度偏置（Table 6）；A.5 不同奖励模型下的补充图示；A.6 案例分析（Table 7，含一个过度优化导致自我对话的失败例） |

## 四、核心创新点与贡献

1. **把 length bias 形式化为混杂因子**：以因果结构图（Figure 3）把长度写成 nuisance/confounding 变量 z，并说明其与 (x, y) 相关会导致奖励模型在分布漂移下失效——这是"长度-偏好关联 ≠ 因果"的可引用形式化。
2. **PoE 双专家解耦框架**：主专家（7B LLaMA，正常学习率）学人类意图，偏置专家（560M BLOOMZ，学习率约为主专家 3 倍）学长度，二者乘积式组合、联合训练（不采用两阶段）。小模型 + 大学习率被用来保证只能学到"粗粒度"信息。
3. **输入扰动强化偏置学习**：对偏置专家输入加高斯噪声（X̃ = X + N），破坏语义信息，迫使它只能依赖长度等表层特征。
4. **推断阶段零额外成本**：PPO 只用主专家提供奖励，偏置专家只在训练期存在。
5. **量化证据链**：输出长度下降的同时奖励与胜率上升（Table 1/3），长度-奖励相关系数下降（Table 4：BLOOMZ 0.3865/0.3932 → 0.2354/0.2990；LLaMA 0.2627/0.2765 → 0.2421/0.2213；Alpaca 0.1786/0.1765 → 0.1354/0.1490，S/P = Spearman/Pearson），并在 TL;DR 摘要任务上复现偏置。

## 五、关键词

| 关键词 | 中文 | 在本论文中的重要性 |
| --- | --- | --- |
| Length bias | 长度偏置 | 全文核心问题：奖励模型/策略对长回答的系统性倾斜 |
| RLHF | 基于人类反馈的强化学习 | 研究对象与训练范式 |
| Reward model (RM) | 奖励模型 | 偏置发生的位置，本文在奖励建模阶段去偏 |
| Confounding factor | 混杂因子 | 长度的形式化角色（因果图 z），是"关联非因果"论证的关键 |
| Product-of-Experts (PoE) | 专家乘积 | 本文方法骨架，用于解耦意图与偏置 |
| Reward hacking / reward gaming | 奖励劫持 | 论文给出的问题上位概念（Goodhart's law） |
| PPO | 近端策略优化 | RL 优化阶段；训练曲线中长度膨胀的展示场景 |
| HH-RLHF | Anthropic Helpful and Harmless 数据集 | 主实验数据（另有 rm-static、Alpaca/ChatAlpaca） |
| Debiasing / disentanglement | 去偏 / 解耦 | 方法目标：把长度从奖励表示中分离 |
| Gaussian noise perturbation | 高斯噪声扰动 | 5.2 节的关键技巧，使偏置专家只学到粗粒度特征 |

## 六、与本课题的相关要素

- **结论方向（支持现象 + 挑战因果解读）**：本文承认长度与奖励分数存在强关联（Figure 2：4000 条 SFT 输出），但把该关联定为 spurious correlation 与混杂效应。可直接支撑课题"长度与人类选择正相关，但不宜解读为因果/质量"的表述框架。
- **术语与形式化可借用**：§2 明确"把人类偏好的长度视为混杂因子（confounding factor）"；§4.2 的因果结构图把长度写作 z，并区分可观测特征 (x, y) 与不可观测的人类偏置与噪声 η。课题在"局限性/讨论"中可用这套语言说明 logistic 回归只是在给定协变量下调整关联。
- **方法可借鉴处**：用相关系数（Spearman/Pearson）作为"关联强度"的可量化指标，并以其下降作为去偏效果证据（Table 4）——课题可类比报告"长度-选择"与"格式-选择"关联强度在不同子集/匹配集下的变化；此外"偏置来源可被单独专家吸收"的思路可类比课题中把长度与格式作为独立特征分别入模。
- **可引用的具体数字（均来自原文）**：Table 4 相关系数（见第四节第 5 条）；Table 3 胜率——AnswerChosen 67.69 / 74.42 / 75.32，Ours vs SFT 54.23 / 59.42 / 56.42，Ours vs PPO 57.47 / 61.43 / 59.56（列分别为 Human / AlpacaFarm / GPT-4）；Figure 2 使用 4000 条 SFT 输出；主专家 7B、偏置专家 560M、学习率 5e-6 vs 8e-6。
- **建议引用位置**：引言（长度偏置是 RLHF 的公认问题，术语与出处）；方法/讨论（混淆因子框架、"关联非因果"的措辞）；局限（去偏方法的代价与不彻底性）。
- **数据是否同源**：否。使用 Anthropic HH-RLHF、Dahoas rm-static 以及 Alpaca/ChatAlpaca 的 SFT 数据，与课题的 LMArena / Arena-Human-Preference-140k 不同源、不同规模，只能作结论对照，不可合并。

## 七、可引用段落摘录

> 以下句子逐字取自 PDF 文本层（该文双栏排版，抽取文本存在列交错，已逐句核对；仅去除换行连字符）。

1. **§2 Related Work（可用于方法/讨论中的"长度是混杂因子"）**
   > In this study, we consider the length of human preferences as a confounding factor that hinders the reward model from accurately assessing the quality of model responses based on true human intent.
2. **§4.1 Length Bias Phenomenon（可用于描述"长度-偏好强相关"这一现象）**
   > It is evident that there is a strong correlation between the reward scores and lengths. This correlation contradicts human intent since the helpfulness and harmlessness of the output should not be solely determined by its length.
3. **§4.3 Challenges（可用于"关联 ≠ 因果/最优"的讨论）**
   > The spurious correlation between reward scalars and response lengths can be problematic, as it may result in biased or sub-optimal model behavior.

## 八、局限与引用注意

- **作者自述局限（Limitations 段）**：方法"只能在一定程度上缓解、不能完全消除"长度偏置；验证只在两个 RLHF 数据集上完成，规模更大的数据集上是否存在该现象"仍不确定"；人类评测只抽取了有限样本。
- **引用风险（数字一致性）**：Table 1、Table 2 在文本层存在明显的列交错（例如 Table 2 的 66.94 / 67.11 / 67.53 与 bias-only 列的 66.73 / 66.58 无法可靠对齐，且与正文"消融后准确率提升"的说法方向需回原文核对），Table 5 的规模-数值行对应关系同样不确定。**建议不要直接引用这些表格的精确数值，引用前必须回 PDF 核对。**
- **结论层次差异**：本文做的是训练阶段的干预（去偏），课题报告的是人类 A/B 选择的观察性关联；引用时须写明层次不同，不能把 PoE"有效去偏"当作课题因果结论的支持。
- **适用对象差异**：结论针对 LLM 奖励模型与 RLHF 数据，与课题的人类偏好数据场景不同源；"人类偏好长回答"在此处是作为待纠正的偏置出现，而非课题意义上的真实选择行为，引用时注意不要混淆。
- **其他**：venue 未在正文中出现（未确认）；作者单位、"Equal contribution / Corresponding author"仅在首页脚注给出。
