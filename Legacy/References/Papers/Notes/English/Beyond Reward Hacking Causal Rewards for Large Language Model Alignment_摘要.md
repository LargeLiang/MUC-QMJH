# Beyond Reward Hacking: Causal Rewards for Large Language Model Alignment — 摘要

> 来源：`Papers/English/Beyond Reward Hacking Causal Rewards for Large Language Model Alignment.pdf`
> 作者：Chaoqi Wang, Zhuokai Zhao, Yibo Jiang, Zhaorun Chen, Chen Zhu, Yuxin Chen, Jiayi Liu, Lizhu Zhang, Xiangjun Fan, Hao Ma, Sinong Wang
> 机构：Meta；University of Chicago
> 出处：arXiv:2501.09620v2 [cs.LG]，2025-05-29（venue 未确认）

## Abstract（原文逐字）

Recent advances in large language models (LLMs) have demonstrated significant progress in performing complex tasks. While Reinforcement Learning from Human Feedback (RLHF) has been effective in aligning LLMs with human preferences, it is susceptible to spurious correlations in reward modeling. Consequently, it often introduces biases--such as length bias, sycophancy, conceptual bias, and discrimination--that hinder the model's ability to capture true causal relationships. To address this, we propose a novel causal reward modeling approach that integrates causality to mitigate these spurious correlations. Our method enforces counterfactual invariance, ensuring reward predictions remain consistent when irrelevant variables are altered. Through experiments on both synthetic and real-world datasets, we show that our approach mitigates various types of spurious correlations effectively, resulting in more reliable and fair alignment of LLMs with human preferences. As a drop-in enhancement to the existing RLHF workflow, our causal reward modeling provides a practical way to improve the trustworthiness and fairness of LLM finetuning.

## 中文翻译

大语言模型（LLM）近期的进展在完成复杂任务方面取得了显著成果。尽管基于人类反馈的强化学习（RLHF）能有效地让 LLM 与人类偏好对齐，但它在奖励建模中容易受到虚假相关（spurious correlations）的影响。因此，它常常引入偏置——例如长度偏置、谄媚、概念偏置与歧视——从而妨碍模型捕捉真正的因果关系。为解决这一问题，我们提出一种新的因果奖励建模方法，将因果性引入以缓解这些虚假相关。我们的方法强制满足反事实不变性（counterfactual invariance），确保当无关变量被改变时奖励预测保持一致。通过在合成数据与真实数据上的实验，我们表明该方法能有效缓解多种虚假相关，从而使 LLM 与人类偏好的对齐更可靠、更公平。作为对现有 RLHF 流程的即插即用增强，我们的因果奖励建模提供了一条提升 LLM 微调可信度与公平性的实用途径。

## 关键词

reward hacking（奖励劫持）、spurious correlation（虚假相关）、counterfactual invariance（反事实不变性）、causal reward model / CRM（因果奖励模型）、MMD（最大均值差异）、length bias（长度偏置）、sycophancy（谄媚）、concept bias（概念偏置）、discrimination bias（歧视偏置）、RLHF / PPO / DPO

---

*说明：原文逐字取自 PDF 摘要（单栏排版，未改写；原文中的 `--` 为 em dash 的抽取呈现）；中文翻译为便于阅读的机器翻译，引用请以英文为准。*
