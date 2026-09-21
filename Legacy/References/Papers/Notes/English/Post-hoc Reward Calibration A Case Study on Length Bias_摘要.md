# Post-hoc Reward Calibration: A Case Study on Length Bias — 摘要

> 来源：`Papers/English/Post-hoc Reward Calibration A Case Study on Length Bias.pdf`
> 作者：Zeyu Huang, Zihan Qiu, Zili Wang, Edoardo M. Ponti, Ivan Titov
> 机构：University of Edinburgh；Alibaba Group；INF Technology；University of Amsterdam
> 出处：ICLR 2025 会议论文；arXiv:2409.17407v2 [cs.AI]，2025-09-21

## Abstract（原文逐字）

Reinforcement Learning from Human Feedback aligns the outputs of Large Language Models with human values and preferences. Central to this process is the reward model (RM), which translates human feedback into training signals for optimising LLM behaviour. However, RMs can develop biases by exploiting spurious correlations in their training data, such as favouring outputs based on length or style rather than true quality. These biases can lead to incorrect output rankings, sub-optimal model evaluations, and the amplification of undesirable behaviours in LLMs' alignment. This paper addresses the challenge of correcting such biases without additional data and training, introducing the concept of Post-hoc Reward Calibration. We first propose to use the local average reward to estimate the bias term and, thus, remove it to approximate the underlying true reward. We then extend the approach to a more general and robust form with the Locally Weighted Regression. Focusing on the prevalent length bias, we validate our proposed approaches across three experimental settings, demonstrating consistent improvements: (1) a 3.11 average performance gain across 33 reward models on the RewardBench dataset; (2) improved agreement of RM produced rankings with GPT-4 evaluations and human preferences based on the AlpacaEval benchmark; and (3) improved Length-Controlled win rate (Dubois et al., 2024) of the RLHF process in multiple LLM–RM combinations. According to our experiments, our method is computationally efficient and generalisable to other types of bias and RMs, offering a scalable and robust solution for mitigating biases in LLM alignment and evaluation.

## 中文翻译

人类反馈强化学习（RLHF）使大语言模型的输出与人类价值观和偏好对齐。该过程的核心是奖励模型（RM），它把人类反馈转化为优化 LLM 行为的训练信号。然而，RM 可能通过利用训练数据中的虚假相关而形成偏置，例如依据长度或风格而非真实质量来偏好输出。这些偏置会导致错误的输出排序、次优的模型评估，并在 LLM 对齐中放大不良行为。本文解决在**不增加额外数据与训练**的前提下纠正此类偏置的难题，提出 Post-hoc Reward Calibration 这一概念。我们首先提出用**局部平均奖励**估计偏置项并将其扣除，以逼近底层真实奖励；随后用**局部加权回归**把该做法推广为更一般、更稳健的形式。聚焦于普遍存在的长度偏置，我们在三种实验设定下验证所提方法并得到一致的改进：（1）在 RewardBench 数据集上对 33 个奖励模型平均提升 3.11；（2）基于 AlpacaEval，RM 产出的排序与 GPT-4 评估、人类偏好的一致性提升；（3）在多个 LLM–RM 组合中，RLHF 过程的长度控制胜率（Length-Controlled win rate，Dubois et al., 2024）提升。实验表明我们的方法计算高效，且可推广到其他类型的偏置与 RM，为缓解 LLM 对齐与评估中的偏置提供了可扩展且稳健的方案。

## 关键词

post-hoc reward calibration（事后奖励校准）、length bias（长度偏置）、reward model / RM（奖励模型）、Locally Weighted Regression / LOWESS（局部加权回归）、Length-Controlled win rate（长度控制胜率）、Gameability（可博弈性）、RewardBench、AlpacaEval、Chatbot Arena、RLHF / DPO

---

*说明：原文逐字取自 PDF 文本摘要，未改写；中文翻译为便于阅读的机器翻译，引用时请以英文原文为准。文本层有两处字符在抽取中损坏（原文为 "multiple LLM?RM combinations" 一处连接符），此处按上下文还原为连接号 "–"（en dash），正文 §4.3 同一词组在文本层呈现为 "LLM-RM"（普通连字符）；如用于逐字引用请先核对 PDF 原文。*
