# Mitigating Length Bias in RLHF through a Causal Lens — 摘要

> 来源：`Papers/English/Mitigating Length Bias in RLHF through a Causal Lens.pdf`
> 作者：Hyeonji Kim, Sujeong Oh, Sanghack Lee（通讯作者 Sanghack Lee）
> 机构：Graduate School of Data Science, Seoul National University
> 出处：AAAI 2026（版权页标注）；arXiv:2511.12573v1 [cs.CL]，2025-11-16

## Abstract（原文逐字）

Reinforcement learning from human feedback (RLHF) is widely used to align large language models (LLMs) with human preferences. However, RLHF-trained reward models often exhibit length bias--a systematic tendency to favor longer responses by conflating verbosity with quality. We propose a causal framework for analyzing and mitigating length bias in RLHF reward modeling. Central to our approach is a counterfactual data augmentation method that generates response pairs designed to isolate content quality from verbosity. These counterfactual examples are then used to train the reward model, enabling it to assess responses based on content quality independently of verbosity. Specifically, we construct (1) length-divergent pairs with similar content and (2) content-divergent pairs of similar length. Empirical evaluations show that our method reduces length bias in reward assignment and leads to more concise, content-focused outputs from the policy model. These findings demonstrate that the proposed approach effectively reduces length bias and improves the robustness and content sensitivity of reward modeling in RLHF pipelines.

## 中文翻译

基于人类反馈的强化学习（RLHF）被广泛用于使大语言模型（LLM）与人类偏好对齐。然而，经 RLHF 训练的奖励模型常常表现出长度偏置——一种把冗长等同于质量、从而系统性偏爱更长回答的倾向。我们提出一个因果框架来分析与缓解 RLHF 奖励建模中的长度偏置。方法的核心是一种反事实数据增强方法：它生成旨在把内容质量与冗长度分离开来的回答配对；这些反事实样本随后被用于训练奖励模型，使其能够在不受冗长度影响的情况下依据内容质量评估回答。具体而言，我们构造 (1) 内容相似而长度不同的配对，以及 (2) 长度相近而内容不同的配对。实证评估表明，我们的方法降低了奖励分配中的长度偏置，并使策略模型产生更简洁、以内容为中心的输出。这些发现表明，所提方法有效降低了长度偏置，并提升了 RLHF 流程中奖励建模的稳健性与内容敏感性。

## 关键词

length bias / verbosity bias（长度偏置 / 冗长偏置）、RLHF（人类反馈强化学习）、reward model（奖励模型）、counterfactual data augmentation（反事实数据增强）、Pearl's Causal Hierarchy（珀尔因果阶梯）、preference flip / flip ratio（偏好翻转 / 翻转率）、content-fixed & length-fixed augmentation（内容固定 / 长度固定增强）、length-controlled accuracy / winrate（长度控制准确率 / 胜率）、RewardBench、PPO/DPO

---

*说明：原文逐字取自 PDF 摘要（双栏排版，已按句子顺序重组，未改写；原文破折号在 PDF 文本层抽取为双连字符 `--`，此处保持抽取原样）；中文翻译为便于阅读的机器翻译，引用时请以英文原文为准。*
