# Disentangling Length Bias in Preference Learning via Response-Conditioned Modeling

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 标题 | Disentangling Length Bias in Preference Learning via Response-Conditioned Modeling |
| 作者 | Jianfeng Cai, Jinhua Zhu\*, Ruopei Sun, Yue Wang, Li Li, Wengang Zhou, Houqiang Li（\*通讯作者） |
| 机构 | University of Science and Technology of China（中国科学技术大学）与 Independent Researcher（二者并列署于标题下方；**各作者的具体归属未能从文本层确认**） |
| 出处 | arXiv:2502.00814v2 [cs.LG]，2025-05-19（预印本；正式 venue 未确认） |
| 语言 | 英文 |
| 与课题相关度 | ★★★★☆（给出人类偏好数据中"被选回答更长"的直接比例 59.78% 与长度—奖励强线性相关的证据，与课题"长度与人类选择正相关"高度呼应；但研究对象是奖励模型/DPO 训练而非人类偏好本身） |
| 原文位置 | `Papers/English/Disentangling Length Bias In Preference Learning Via Response-Conditioned Modeling.pdf` |

## 一、三句话概括

1. 论文研究偏好学习中的**长度偏置**：奖励模型会大量依赖回答长度，以至于在"空提示词"或"随机提示词"的错配数据集上仍能维持约 60% 的准确率。
2. 作者发现两个并存的局限——LLM 对长度有内在敏感性，但微调后的模型却**无法遵循显式长度指令**（在长度评测集上准确率仅约 50%，与随机猜测无异）。
3. 为此提出 **Response-conditioned Bradley-Terry（Rc-BT）**，通过构造 (x, x_l¹, y_w) 与 (x_l², x, y_l) 两类响应条件偏好对，把"人类语义偏好"与"长度约束"显式分离，并推导出 Rc-RM 与 Rc-DPO 两个可直接落地的算法。

## 二、摘要

**原文（逐字）**

> Reinforcement Learning from Human Feedback (RLHF) has achieved considerable success in aligning large language models (LLMs) by modeling human preferences with a learnable reward model and employing a reinforcement learning algorithm to maximize the reward model's scores. However, these reward models are susceptible to exploitation through various superficial confounding factors, with length bias emerging as a particularly significant concern. Moreover, while the pronounced impact of length bias on preference modeling suggests that LLMs possess an inherent sensitivity to length perception, our preliminary investigations reveal that fine-tuned LLMs consistently struggle to adhere to explicit length instructions. To address these two limitations, we propose a novel framework wherein the reward model explicitly differentiates between human semantic preferences and response length requirements. Specifically, we introduce a Response-conditioned Bradley-Terry (Rc-BT) model that enhances the model's capability in length bias mitigating and length instruction following, through training on our augmented dataset. Furthermore, we propose the Rc-RM and Rc-DPO algorithm to leverage the Rc-BT model for reward modeling and direct policy optimization (DPO) of LLMs, simultaneously mitigating length bias and promoting adherence to length instructions. Extensive experiments across various foundational models and datasets demonstrate the effectiveness and generalizability of our approach.

**中文翻译**

> 人类反馈强化学习（RLHF）通过可学习的奖励模型对人类偏好建模，并用强化学习算法最大化奖励模型得分，在语言模型对齐上取得了显著成功。然而，这些奖励模型容易被各类表层混杂因素所利用，其中长度偏置尤为突出。此外，尽管长度偏置对偏好建模的显著影响说明 LLM 对长度具有内在感知敏感性，我们的前期考察却发现：微调后的 LLM 始终难以遵循显式的长度指令。针对这两个局限，我们提出一个新框架，使奖励模型能够显式区分"人类语义偏好"与"回答长度要求"。具体地，我们提出 Response-conditioned Bradley-Terry（Rc-BT）模型，通过在增广数据集上训练，提升模型缓解长度偏置与遵循长度指令的能力。进一步地，我们提出 Rc-RM 与 Rc-DPO 算法，利用 Rc-BT 完成奖励建模与 LLM 的直接偏好优化（DPO），在缓解长度偏置的同时提升对长度指令的遵循度。跨多种基座模型与数据集的大量实验证明了本方法的有效性与泛化性。

（完整摘要另见 `..._摘要.md`）

## 三、章节结构与内容

| 位置 | 标题（原文） | 内容说明 |
| --- | --- | --- |
| 1 | Introduction | 提出问题：奖励模型易被表层混杂因素（长度、项目符号、礼貌用语）利用；既有两类缓解路线（调整策略优化／解耦长度与质量）各有缺陷（超参敏感、双分支过参数化导致优化不稳、线性无关不保证真独立，且"强制长度与质量无关"在某些长度指令数据上并不合理）；引出"不如利用长度信息"的思路与三条贡献 |
| 2 | Related Work | 三小节：Reinforcement Learning From Human Feedback（RLHF 背景与 DPO）、Reward Hacking（长度偏置的既有缓解：ODIN 的长度正则、双模型不同学习率、DPO 目标加长度惩罚）、Length Instruction Following（LLM 能理解 "concise"/"verbose" 等定性描述但难遵循 "150 words or less" 这类数值约束；LIFT 提升服从度却损害语义质量）。定位：本文让模型区分语义意图与长度指令，二者兼顾 |
| 3 | Preliminary Explorations | 前期实证。数据为 OpenAssistant（Köpf et al., 2024），划分为 D_sft／D_rm／D_eval；模型为 Qwen2-1.5B、Qwen2.5-7B、Llama-3.1-8B。3.1 Length Bias Indeed Exists：构造空提示词集 D_eeval 与随机提示词集 D_reval，尽管回答与提示词语义错配，几乎所有模型准确率仍超 60%，接近原始 D_eval；且不同提示词下模型对回答的偏好一致率超过 85%——说明偏好并非由提示词驱动；奖励分数与回答长度呈强线性相关。3.2 Length Bias in Evaluation Dataset：59.78% 的 chosen 回答比对应 rejected 更长，仅靠"偏爱更长"即可拿到近 60% 准确率；作者用 GPT-4o 把每个三元组改写成两条长度约束相反的新三元组（\|y_l1\| > \|y_w1\| 且 \|y_l2\| < \|y_w2\|）得到 D_eqval，重构后 Baseline 准确率大幅下降、多数不超过 60%。3.3 Length Biased Reward Model Show Limited Adherence to Length Instructions：在 D_el^val 上（两条回答都语义满足 x、只有一条满足长度约束）所有 Baseline 模型准确率接近 50%，不比随机好——说明模型是"无意识地"习得长度偏置，并非把长度当作可测量属性。3.4 Length Instructions Are Easily Learned：把长度约束直接拼进提示词（{x_l, y_w, y_l} 格式，并把 LIFT 扩展为含"or more"的 LIFT-plus），模型能学会遵循长度，但在 D_eqval 上的语义准确率下降——即牺牲语义理解换取形式服从；训练过程中长度准确率快速上升而语义准确率先升后降 |
| 4 | Response-Conditioned Modeling | 方法章。4.1 Preliminary: Bradley-Terry Model：回顾 BT 与参数化奖励模型的最大似然目标（Eqn. 1、Eqn. 5）。4.2 Response-Conditioned BT Model：对原始 chosen 回答 y_w 构造违反长度约束的 x_l¹，形成偏好对 (x, x_l¹, y_w)（x 优于 x_l¹ 搭配 y_w）；对 rejected 回答 y_l 构造满足约束的 x_l²，形成偏好对 (x_l², x, y_l)；合并得 D_Rc = {(x, x_l¹, y_w)} ∪ {(x_l², x, y_l)}，据此写出 Rc-BT 目标（Eqn. 4），使模型显式比较 x 与其长度增广变体，把隐式长度偏置转为显式长度理解。4.3 Response-Conditioned Reward Model：架构不变、仅数据格式由 prompt-conditioned 改为 response-conditioned，给出 Rc-RM 损失（Eqn. 6，用系数 λ 平衡两类偏好对）。4.4 Response-Conditioned Direct Preference Optimization：由 DPO 目标（Eqn. 7）与最优策略—奖励映射推导出 Rc-DPO 目标（Eqn. 8），可直接用 DPO 训练策略 |
| 5 | Experiments | 5.1 Experimental Settings：D_sft 做 SFT，RM 与 DPO 均在 D_rm ∪ D_Rc 上训练；基座模型 Qwen2-1.5B、Qwen2.5-7B、Llama-3.1-8B（附录另有 Qwen2.5-1.5B）；Rc-RM 学习率 1×10⁻⁵、warmup 10 步、batch 64、训练 5 epoch，Rc-DPO 学习率 1×10⁻⁶，其余相同；基于 DeepSpeed 与 Transformers，8 张 NVIDIA A100 80GB。评测指标：Quality Eval Acc（D_eqval 上的准确率，衡量长度偏置缓解）与 Length Eval Acc（D_el^val 上的准确率，衡量长度指令服从）。5.2 The Results of Reward Models：Table 3 显示 Rc-RM 在全部 6 个设置上优于 Baseline 与 ODIN（Quality Eval Acc 69.55–73.07）；Qwen2-1.5B-Base 上比 Baseline 高 10.41%、比 ODIN 高 13.43%；Llama-3.1-8B-Instruct 上比 Baseline 高 16.85%、比 ODIN 高 11.54%；在长度分级的 D_mvl^al 上，Baseline 与 LIFT-plus 得分随长度上升，ODIN 因长度惩罚而波动，Rc-RM 最平稳。用 Rc-RM 做 PPO 训练 Qwen2-1.5B-Instruct 策略时，Quality Win Ratio 38.28→44.06（ODIN 41.57），平均回答长度 671.49→308.16（ODIN 342.85）；Qwen2.5-7B-Instruct 上 40.31→49.26（ODIN 45.03），长度 597.27→277.15（ODIN 336.15）。5.3 The Results of DPO Models：Table 2 显示 Rc-DPO 在四个模型设置中语义质量（Quality Win Ratio）均最优，且同时缩短回答长度；LIFT-plus 反而损害语义质量；R-DPO 提升语义但回答更长。5.4 Ablation Studies：把 D_Rc 拆为 D_Rc^c 与 D_Rc^r 分别训练，单独使用任一部分时 Quality Eval Acc 都显著掉回 Baseline 水平、Length Eval Acc 徘徊在 50% 左右，说明两部分互补、缺一不可 |
| 6 | Conclusion | 总结 Rc-BT 能分离人类语义意图与长度指令，在缓解长度偏置的同时保留长度敏感性，并给出到 RM 与 DPO 的数学扩展；实验证明其在降低长度偏置与提升长度指令服从两方面均有效 |
| Limitations | Limitations | 自述两点：(1) 数据增广带来额外计算开销——D_Rc 使偏好对数量约翻倍，且需同时训练奖励模型与策略模型，对算力受限的研究者构成一定约束；(2) 评测限于较小模型（Qwen2-1.5B、Qwen2.5-1.5B、Qwen2.5-7B、Llama-3.1-8B），13B/34B/70B 等更大模型未探索 |
| Appendix | A–E | A 相关工作的详细版；B Rc-DPO 的完整推导；C 训练与数据构造细节（C.2 D_eqval 生成、C.3 D_el^val 构造、C.4 长度指令格式与 LIFT-plus 及三个变体）；D 详细结果与分析（D.1 长度偏置分析、D.2 D_eqval 分析、D.3 LIFT-plus 结果）；E 扩展实验（E.1 评测细节、E.3 Qwen2.5-1.5B、E.6 消融、E.7 "short bias" 问题与 AlpacaEval-LI-plus-less／-plus-more 基准） |

## 四、核心创新点与贡献

1. **诊断性发现**：用"空提示词／随机提示词"替换原提示词后奖励模型准确率仍近 60%、偏好一致率 >85%，**干净地证明奖励模型的偏好主要由"回答更长"驱动而非语义质量**；D_eval 中 59.78% 的 chosen 更长，仅凭长度即可获得近 60% 准确率。
2. **第二个诊断**：长度偏置的模型**并不能遵循显式长度指令**（D_el^val 上约 50%，等同随机），说明长度偏置是隐式习得而非显式的长度感知——这一"敏感性高但可控性差"的分离是全文动机。
3. **Rc-BT 建模**：不改架构、只改数据格式（response-conditioned），把每条偏好样本增广为 (x, x_l¹, y_w) 与 (x_l², x, y_l) 两个偏好对，从而显式比较"原提示词 vs 长度增广提示词"，把隐式偏置转化为显式长度理解。
4. **两个可落地的算法扩展**：Rc-RM（Eqn. 6）与 Rc-DPO（Eqn. 8，含完整推导），并在 PPO 与 DPO 两条路线上都做了验证。
5. **方法学立场**：与既往"抑制/抹除长度信息"的做法（ODIN 的长度正则、R-DPO 的长度惩罚、LIFT 的数据改造）不同，主张**保留并显式建模长度信息**，从而在缓解偏置的同时不损害（甚至提升）语义质量。

## 五、关键词

| 关键词 | 中文 | 在本论文中的重要性 |
| --- | --- | --- |
| Length bias | 长度偏置 | 全文核心问题：奖励模型偏好更长回答 |
| Response-conditioned Bradley-Terry (Rc-BT) | 响应条件化 Bradley-Terry | 论文的核心建模创新 |
| Rc-RM / Rc-DPO | 响应条件化奖励模型／响应条件化 DPO | 由 Rc-BT 衍生的两个算法 |
| Reward hacking | 奖励劫持 | 长度偏置被定位为 reward hacking 的典型形式 |
| RLHF / DPO / PPO | — | 应用与评测所依托的对齐范式 |
| Length instruction following | 长度指令遵循 | 第二个待解决的局限（显式长度约束） |
| Quality Eval Acc / Length Eval Acc | 质量评测准确率／长度评测准确率 | 两个主指标，分别度量偏置缓解与指令服从 |
| D_eqval / D_el^val | — | 本文构造的去长度偏置语义评测集与长度评测集 |
| ODIN / LIFT / LIFT-plus / R-DPO | — | 主要对照方法 |
| Verbosity / response length | 冗长度／回答长度 | 与课题"长度（token 数）"直接对应的变量 |

## 六、与本课题的相关要素

- **结论方向高度一致（最重要的接口）**：§3.2 明确报告 "59.78% of the chosen responses in D_eval are longer than the corresponding rejected responses"，即**在人类偏好数据中被选回答更长的比例约六成**，且仅凭"偏爱更长"即可获得近 60% 准确率。这与课题在 Arena-Human-Preference 数据上"长度与人类选择正相关"的发现方向一致，可作为**引言或讨论中的外部独立佐证**（不同数据源、不同标注体系）。
- **可直接引用的数字**：59.78%（chosen 更长的比例）、"仅凭长度即可获得近 60% 准确率"、Baseline 在 D_eval/D_eeval/D_reval 上的准确率区间 56.25–65.22%（Table 1）、偏好一致率 85% 以上（Table 1 的一致率列 88.32–92.12%）、Rc-RM 的 Quality Eval Acc 69.55–73.07（Table 3）、Qwen2-1.5B-Base 上 Rc-RM 高于 Baseline 10.41%、高于 ODIN 13.43%，Llama-3.1-8B-Instruct 上高于 Baseline 16.85%、高于 ODIN 11.54%、PPO 后 Quality Win Ratio 38.28→44.06 且平均长度 671.49→308.16（Table 4）、Qwen2.5-7B-Instruct 40.31→49.26 与 597.27→277.15（Table 4）。
- **方法可借鉴处**：(a) **用"错配提示词"构造对照数据集**（空提示词/随机提示词）来隔离语义与表层特征——课题的"匹配诊断/纯度效应"敏感性分析在思想上与之同类，可引用为方法论先例；(b) **用"长度分级响应"考察奖励分数斜率**（D_mvl^al，斜率越小长度偏置越弱）——课题若需给出"长度效应随长度差的单调性"诊断，可借鉴这一斜率视角；(c) 其"把隐式偏置转为显式建模"的设计哲学，可用于课题讨论中说明"观察性关联不等于应当消除"。
- **可引用的方法名/指标名**：Response-conditioned Bradley-Terry (Rc-BT)、Rc-RM、Rc-DPO、D_eqval、D_el^val、D_eeval、D_reval、Quality Eval Acc、Length Eval Acc、Length Win Ratio、Quality Win Ratio、LIFT-plus、AlpacaEval-LI-plus-less / AlpacaEval-LI-plus-more、ODIN、R-DPO。
- **建议引用位置**：**引言**（长度偏置在偏好数据中的普遍性与"人类标注本身即含长度倾向"）、**讨论**（"偏好数据中的长度信号是真实偏好还是可利用的混杂因素"这一争议——该文主张保留而非抹除）、**局限**（说明课题为观察性关联，不做干预式建模）。
- **数据是否同源**：**不同源**。该文用 OpenAssistant 数据集（Köpf et al., 2024），课题用 LMArena/Arena-Human-Preference-140k；模型为 Qwen2-1.5B/Qwen2.5-7B/Llama-3.1-8B，与课题的数据来源、任务分布、语言构成均不同。
- **研究对象与人类偏好研究的层次差异**：该文研究的是**奖励模型/策略模型对长度的依赖**（模型内部机制与训练算法），人类偏好只作为**训练数据的来源**出现在 59.78% 这一描述统计里；课题研究的是**人类评审者在真实 A/B 场景中的选择行为**及其与文本特征的观察性关联。因此该文的 Rc-RM/Rc-DPO 结果不能当作"人类偏好"证据；引用 59.78% 时应明确它是"该文所用 OpenAssistant 子集上的描述统计"，与课题 135,634 条输入 / 78,959 对明确胜负的规模不可直接比较。

## 七、可引用段落摘录

> 以下句子逐字取自 PDF 文本层（该文双栏排版，行末断词已按原文拼合，未改写）。

1. **Abstract（可用于引言，说明长度偏置在偏好建模中的地位）**
   > However, these reward models are susceptible to exploitation through various superficial confounding factors, with length bias emerging as a particularly significant concern.
2. **§3.2 Length Bias in Evaluation Dataset（可用于引言或讨论，佐证人类偏好数据中"更长者被选"的比例）**
   > Specifically, our analysis reveals that 59.78% of the chosen responses in Deval are longer than the corresponding rejected responses.
3. **§3.3 Length Biased Reward Model Show Limited Adherence to Length Instructions（可用于讨论，区分"对长度的敏感性"与"对长度的可控性"）**
   > This finding suggests that reward models unconsciously acquire length bias during preference learning without explicit awareness of length as a measurable attribute.

## 八、局限与引用注意

- **作者自述局限**（Limitations）：(1) 数据增广使偏好对数量约翻倍、并需同时训练奖励模型与策略模型，带来额外算力开销；(2) 实验仅覆盖 Qwen2-1.5B、Qwen2.5-1.5B、Qwen2.5-7B、Llama-3.1-8B，13B/34B/70B 等更大模型未探索。
- **venue 未确认**：仅见 arXiv:2502.00814v2（2025-05-19），无正式发表信息，引用应按预印本处理。
- **作者归属未确认**：文本层丢失了作者与单位的上标标记，仅能确认署名同时包含 "University of Science and Technology of China" 与 "Independent Researcher"，**无法确定哪位作者属于哪个单位**；如需在参考文献中标注单位，应回查原 PDF 首页图。
- **数据集差异**：OpenAssistant 与 LMArena/Arena-Human-Preference-140k 在采集方式（众包 vs 真实匿名 A/B 平台）、任务分布、语言与提示词类型上差异较大；其 59.78% 不能直接与课题的胜率/关联强度横向比较，只能作方向性佐证。
- **"长度"口径不同**：该文以 token/word 计的回答长度并有"word_num"这类长度约束定义，课题以 token 数计；引用具体数值时应注明口径。
- **表格数字的抽取风险**：Table 2（DPO 结果）在双栏抽取中出现两栏交错，本文笔记只引用其中可从正文与列结构明确对应的值；若需精确引用，建议回查 PDF 原表。
- **结论层次**：论文的因果式措辞（"mitigates length bias"）来自其**干预式训练实验**（增广数据 + 重新训练），课题为观察性关联，不可移植其因果表述。
- **术语同名异指**：该文 length bias 指"奖励模型偏好更长回答"，与中文语境常说的"长度偏置"含义一致，但需与"位置偏置（position bias）"区分。
