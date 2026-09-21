# Mitigating Length Bias in RLHF through a Causal Lens

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 标题 | Mitigating Length Bias in RLHF through a Causal Lens |
| 作者 | Hyeonji Kim, Sujeong Oh, Sanghack Lee（通讯作者 Sanghack Lee） |
| 机构 | Graduate School of Data Science, Seoul National University（首尔大学数据科学研究生院） |
| 出处 | AAAI 2026（版权页标注 Copyright © 2026, Association for the Advancement of Artificial Intelligence）；arXiv:2511.12573v1 [cs.CL]，2025-11-16 |
| 语言 | 英文 |
| 与课题相关度 | ★★★☆☆（主题同为"长度偏置"，提供因果去偏路线与去偏代价的对照；但对象是奖励模型/RLHF 策略而非人类 A/B 选择，且不涉及格式特征） |
| 原文位置 | `Papers/English/Mitigating Length Bias in RLHF through a Causal Lens.pdf` |

## 一、三句话概括

1. 论文把 RLHF 奖励模型的长度偏置重述为因果问题：响应由潜变量语义内容 C 与可观测长度 L 共同生成，二者在自然偏好数据中纠缠，故纯观察性比较无法分离长度对奖励的因果效应。
2. 作者提出反事实数据增强框架，用大模型生成两类配对——"内容相同、长度不同"（content-fixed）与"长度相同、内容不同"（length-fixed）——并以"偏好翻转率 F>0.5"诊断长度偏置、用翻转后的配对重写监督标签。
3. 在 OpenLLaMA-3B 系奖励模型与 PPO 策略上，该方法在 49,861 对中诊断出 47.43% 存在长度偏置，训练后长度控制胜率由基线 PPO_HRO 的 18.97% 升至 37.18%，且输出更短、内容导向。

## 二、摘要

**原文（逐字）**

> Reinforcement learning from human feedback (RLHF) is widely used to align large language models (LLMs) with human preferences. However, RLHF-trained reward models often exhibit length bias--a systematic tendency to favor longer responses by conflating verbosity with quality. We propose a causal framework for analyzing and mitigating length bias in RLHF reward modeling. Central to our approach is a counterfactual data augmentation method that generates response pairs designed to isolate content quality from verbosity. These counterfactual examples are then used to train the reward model, enabling it to assess responses based on content quality independently of verbosity. Specifically, we construct (1) length-divergent pairs with similar content and (2) content-divergent pairs of similar length. Empirical evaluations show that our method reduces length bias in reward assignment and leads to more concise, content-focused outputs from the policy model. These findings demonstrate that the proposed approach effectively reduces length bias and improves the robustness and content sensitivity of reward modeling in RLHF pipelines.

**中文翻译**

> 基于人类反馈的强化学习（RLHF）被广泛用于使大语言模型（LLM）与人类偏好对齐。然而，经 RLHF 训练的奖励模型常常表现出长度偏置——一种把冗长等同于质量、从而系统性偏爱更长回答的倾向。我们提出一个因果框架来分析与缓解 RLHF 奖励建模中的长度偏置。方法的核心是一种反事实数据增强方法：它生成旨在把内容质量与冗长度分离开来的回答配对；这些反事实样本随后被用于训练奖励模型，使其能够在不受冗长度影响的情况下依据内容质量评估回答。具体而言，我们构造 (1) 内容相似而长度不同的配对，以及 (2) 长度相近而内容不同的配对。实证评估表明，我们的方法降低了奖励分配中的长度偏置，并使策略模型产生更简洁、以内容为中心的输出。这些发现表明，所提方法有效降低了长度偏置，并提升了 RLHF 流程中奖励建模的稳健性与内容敏感性。

（完整摘要另见 `Mitigating Length Bias in RLHF through a Causal Lens_摘要.md`）

## 三、章节结构与内容

| 位置 | 标题（原文） | 内容说明 |
| --- | --- | --- |
| 1 | Introduction | 指出 RLHF 继承并放大人类偏好数据中的冗长偏置，现有方法（ODIN、RRM 等）缺乏对长度的显式受控干预；以"巧克力消费与诺奖数量"的混淆例子说明仅凭观察性相关不可靠；给出三条贡献（现有方法局限、反事实数据增强框架、实证有效性） |
| 2 | Preliminaries | 两个无编号小节。*Length Bias in Reward Model*：RLHF/PPO/DPO 背景下 ODIN（双头奖励模型）与 RRM（长度扰动数据增强）的做法，并批评它们未对长度本身做受控干预、可能只是压制风格方差；*Pearl's Causal Hierarchy*：介绍因果阶梯三级（association / intervention / counterfactual）及对应问句形式 |
| 3 | Causal Interpretation of Length Bias | 因果刻画章。给出因果结构 X→T，而 T 由潜变量内容 C 与长度 L 生成（Fig. 1）；说明自然数据中 C 与 L 共变、观察性编辑会同时改变两者，故需反事实编辑（Fig. 2 的流形类比）；论证本文设定属"可实现的 L3 反事实"，可用干预近似。3.1 Operational Definitions of Length and Content：长度按 token 经验分布分 5 个分位桶，内容用"语义等价"的关系式定义（Fixed Content vs Varying Content） |
| 4 | Length Bias Mitigation Pipeline | 方法章，三阶段。4.1 Counterfactual Data Augmentation Implementations：length-fixed 增强（通过填充/冗语/复述/格式变化改长度、保语义）与 content-fixed 增强（细节删除/细化/信息替换/修辞改写），并用二分类器做保真过滤；4.2 Diagnosing Length Bias：Table 1 规则表（按获胜方的内容质量与相对长度判定 acceptable / implausible / length bias），提出偏好翻转（preference flip）与翻转率 F，F>0.5 判为长度偏置；4.3 Mitigating Length Bias：把内容固定的反事实 A′ 与原文回答 B 组成新训练对并改写监督标签（在长度被中性的条件下改为偏好 B），同时纳入 length-fixed 变体以直接监督语义质量，使奖励模型学到以内容而非冗长为准的排序 |
| 5 | Experiments | 5.1 Data Augmentation：基于 RLHFlow 的 699k prompt-response 对，筛出"偏好方更长且长度跨桶"的 225,358 例，抽样 50,000 例增强得到 474k content-fixed + 471k length-fixed（≈945k 比较，为原样本 19 倍），过滤后保留 472k/466k；5.2 Length Bias Identification and Mitigation Data Construction：用 OpenLLaMA-3B 参考奖励模型重新打分并做内容固定比较，49,861 对中 23,651 对（47.43%）存在长度偏置，得到 198,778 个翻转 content-fixed 对与 213,699 个等长 length-fixed 对，去重后 412,286 个唯一三元组。评测：奖励模型用 RewardBench-1/2 与 length-controlled accuracy（Table 3、Fig. 5），策略模型用 AlpacaEval 的 length-controlled winrate（Table 4、Fig. 6） |
| 6 | Conclusion | 总结因果框架与反事实增强效果，并指出方法假设内容与长度可干净分离，未来可扩展到 tone、coherence、factuality 等混淆因子 |
| 附录 | Appendix A–L | A RLHF 基础；B 结构因果模型中的反事实推理（含形式化）；C Response Manifold；D Counterfactual Realizability（可实现的 L3 分布的形式条件与 FCE 约束）；E Learning Length-Invariant Rewards via Counterfactuals（理论机制）；F 控制内容与长度的增强技术；G 长度分桶准则（Table 5：Very Short (1, 41) 至 Very Long (377, 5220)）；H 增强提示词与示例；I 微调细节（I.1 Cross-Encoder Fine-Tuning 等）；J 翻转率计算与阈值（Fig. 9 双峰分布）；K 评测结果（K.1 奖励模型、K.2 PPO 的逐次运行统计）；L 以 Meta-LLaMA-3-8B-Instruct / 3.1-8B-Instruct-Turbo 作评委的复核评测 |

## 四、核心创新点与贡献

1. **把长度偏置明确写成因果问题**：给出 X→T←(C, L) 的结构，指出 C 与 L 在自然数据中纠缠，是"观察性比较无法分离长度效应"的形式化理由；配置了"巧克力消费—诺奖"式的混淆例证。
2. **反事实数据增强的具体构造**：content-fixed（改内容、保长度）与 length-fixed（改长度、保语义）两类配对互补，用 GPT-4o-mini 生成 + all-mpnet-base-v2 二分类器做语义保真过滤，规模达 945k 比较（19 倍于原样本）。
3. **可自动化的偏置诊断量**：偏好翻转（preference flip）与翻转率 F = 翻转次数/反事实比较总数，阈值 F>0.5；给出 47.43%（23,651/49,861）的偏置比例这一可引用的量化结果。
4. **"改标签"式的奖励模型再训练**：不靠正则或双头结构，而是用翻转后的高质量监督信号（含等长对照）重塑排序，声称在降低长度偏置的同时不牺牲总体性能。
5. **去偏代价的对照结果**：ODIN 把输出平均长度压到 1026（最短）却使 winrate 掉到 11.34%，而本文 PPO_CDA_HRO 的 length-controlled winrate 达 37.18%——为"去偏是否牺牲区分度"提供了直接对照。

## 五、关键词

| 关键词 | 中文 | 在本论文中的重要性 |
| --- | --- | --- |
| Length bias / verbosity bias | 长度偏置 / 冗长偏置 | 全文主题：奖励模型把冗长误当质量 |
| Reward model (RM) | 奖励模型 | 被诊断与被去偏的对象 |
| RLHF / PPO / DPO | 人类反馈强化学习 / 近端策略优化 / 直接偏好优化 | 应用场景与下游评测链路 |
| Counterfactual data augmentation | 反事实数据增强 | 本文提出的核心方法 |
| Pearl's Causal Hierarchy (PCH) | 珀尔因果阶梯 | 论文的理论定位：association / intervention / counterfactual 三级 |
| Realizable counterfactual | 可实现的反事实 | 借用 Raghavan & Bareinboim (2025) 说明反事实数据可物理生成 |
| Preference flip / flip ratio | 偏好翻转 / 翻转率 | 偏置诊断的核心指标（阈值 0.5） |
| Content-fixed / length-fixed augmentation | 内容固定 / 长度固定增强 | 两类配对构造 |
| Length binning | 长度分桶 | 5 个 token 分位桶，(1,41) 至 (377,5220) |
| Length-controlled (LC) accuracy / winrate | 长度控制准确率 / 胜率 | 与 AlpacaEval-LC 同名的评测口径（Dubois et al. 2024） |

## 六、与本课题的相关要素

- **结论方向：仅适用于 LLM 评审/奖励模型，不能外推到人类 A/B 选择**。本论文的全部证据链（RewardBench、LC accuracy、AlpacaEval 胜率）都在模型侧；人类偏好仅以"人类也易受冗长影响"的引文方式出现（引 Saito et al. 2023、Shen et al. 2023），本文自身未做人类实验。课题引用时须写明证据层次差异。
- **支持"长度是偏好判断的强线索，且可被长度单独操控"**：正文报告 HRO 基线的奖励与长度强正相关（Fig. 5）；以 OpenLLaMA-3B 参考奖励模型重新打分后，在保持语义内容仅改变长度的反事实比较下，49,861 对中有 23,651 对（47.43%）发生偏好翻转——可作课题引言/讨论中"长度与偏好关联并非表层噪声"的外部证据（对象为奖励模型）。
- **为课题"关联≠因果"的表述提供现成论据**：论文用混淆偏相关（巧克力消费 vs 诺奖）说明 observational correlations 的不可靠，并明确说观察性比较"不足以分离长度对奖励的因果效应"；课题是观察性关联研究，可引用其措辞来界定自身结论层次（现象刻画 vs 因果识别）。
- **方法可借鉴处（分层/匹配与稳健性诊断）**：5 个 token 分位桶（Table 5：(1,41) / (41,98) / (98,204) / (204,377) / (377,5220)）把"同桶即近似等长"，与课题的长度分层匹配诊断同构，可作为"分层阈值如何设定"的方法学引用；翻转率 F（#翻转/总反事实比较，>0.5 判偏）可类比课题的稳健性/纯度效应指标设计。
- **去偏代价的数字对照**：Table 4——OpenLM 8.47（LC）/9.94（胜率）/1385（平均长度）；SFT 16.97/25.71/2061；PPO_HRO 18.97/28.45/2048；ODIN 12.19/11.34/1026；PPO_CDA_OpenLM 36.06/30.69/1072；PPO_CDA_HRO 37.18/32.55/1118。作者据此称 ODIN"以减少长度为代价换取胜率下降"，而本文方法在更短输出的同时提升胜率——可用于课题讨论"抹平长度效应会如何改变评价结果"及去偏的风险。
- **可直接引用的方法名/指标名**：counterfactual data augmentation、content-fixed / length-fixed pairs、preference flip、flip ratio（F>0.5）、length-controlled accuracy、RewardBench-1 / RewardBench-2、AlpacaEval length-controlled winrate（引自 Dubois et al. 2024）、Pearl's Causal Hierarchy、realizable counterfactual、Fundamental Constraint of Experimentation (FCE)。
- **数据不同源**：训练侧为 RLHFlow 偏好数据（699k prompt-response 对、7 个来源）与 GPT-4o-mini 生成的合成配对；评测侧为 RewardBench 与 AlpacaEval（LLaMA-2-7B-chat 评委）。与课题的 LMArena / Arena-Human-Preference-140k（135,634 输入、78,959 明确胜负对）无重叠，不可合并或直接互换结论。
- **建议引用位置**：引言（长度偏置在 RLHF/偏好数据中的普遍性与其因果化表述）；讨论（"观察相关不足以识别因果"、去偏可能牺牲区分度）；局限（课题无法做干预，反事实问句超出观察性数据的能力边界）。
- **格式特征的接口**：本文完全不涉及 Markdown/格式特征（内容与长度是其仅有的两个因子），课题的格式维度需另找文献；但其"逐因子隔离"的框架可类比说明课题为何只能对格式做调整关联而非因果归因。

## 七、可引用段落摘录

> 以下句子逐字取自 PDF 文本层（该文双栏排版，抽取文本存在大量插入空白，已按句子顺序逐句核对；原文破折号在文本层显示为 `--`，此处保持抽取原样）。

1. **§1 Introduction（混淆/因果，可用于讨论"关联≠因果"）**
   > This classic example highlights the risk of relying solely on observational correlations without causal reasoning.
2. **§3 Causal Interpretation of Length Bias（长度与内容纠缠，可用于方法或讨论）**
   > Since content and length often co-vary in natural data, conventional observational comparisons--such as randomly sampled response pairs from RLHF datasets--are insufficient to isolate the causal effect of length on reward.
3. **§5.2 Experiments（去偏的代价，可用于讨论"消除长度效应会付出什么"）**
   > Unlike ODIN, which reduces length at the cost of winrate, our method improves conciseness without degrading performance.

## 八、局限与引用注意

- **作者自述**（§6 Conclusion）：方法假设"内容与长度可干净分离"（原文 *While our method assumes a clean separation between content and length*），只处理长度这一混淆因子，tone / coherence / factuality 等留作未来工作；未设专门的 Limitations 章节。
- **数据生成带来的假设**：反事实配对由 GPT-4o-mini 生成、由 all-mpnet-base-v2 二分类器判定语义保真（"内容相同"），因此去偏效果依赖生成器与分类器的可靠性，存在生成式偏差与"保真"判定的假阴性/假阳性风险；引用时应写明这是合成监督信号。
- **结论层次**：全部为模型侧（奖励模型 + PPO 策略），无人类评审实验；不能作为"人类偏好中存在/不存在长度偏置"的证据，也不能与课题的人类 A/B 选择结论混同。
- **表格数字的抽取风险**：Table 3 / Table 15 / Table 16 的模型名与数值在 PDF 文本层被抽成相互分离的文本块（模型名列与数值列错位），本笔记所引 length-controlled accuracy（CDA_LoRA 0.249→0.248 一档）系按行序与正文自述"CDA_LoRA 的 LC accuracy 为 24.80%"交叉核对得出；**若要引用 Table 3 具体单元格，请回原 PDF 逐格核对**。Table 4 的抽取为逐行单列，无此问题。
- **PDF 加密**：英文 PDF 副本带密码保护，无法直接渲染核对页码；本笔记的章节与数字均来自纯文本抽取，页码一律未标注。
- **与课题的规模/口径差异**：本文 945k 合成比较、412,286 训练三元组、49,861 诊断对，量级与课题 135,634 输入 / 78,959 明确胜负对不同源也不同用；其"长度"按 token 分位桶离散化，课题按 token 连续计数，二者"等长"含义不同，不可直接比较数值。
- **venue**：正文版权页标注为 AAAI 2026，但正文未显式声明录用状态；正式引用请以官方出版信息为准。
