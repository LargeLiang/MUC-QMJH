# Loose lips sink ships: Mitigating Length Bias in Reinforcement Learning from Human Feedback — 摘要

> 来源：`Papers/English/Loose lips sink ships Mitigating Length Bias in Reinforcement Learning from Human Feedback.pdf`
> 作者：Wei Shen, Rui Zheng, Wenyu Zhan, Jun Zhao, Shihan Dou, Tao Gui, Qi Zhang, Xuanjing Huang
> 机构：复旦大学计算机科学技术学院；International Human Phenome Institutes (Shanghai)；复旦大学现代语言学研究院
> 出处：arXiv:2310.05199v5 [cs.CL]，2023-11-29（venue 未确认）

## Abstract（原文逐字）

Reinforcement learning from human feedback serves as a crucial bridge, aligning large language models with human and societal values. This alignment requires a vast corpus of human feedback to learn a reward model, which is subsequently used to finetune language models. However, we have identified that the reward model often finds shortcuts to bypass its intended objectives, misleadingly assuming that humans prefer longer responses. The emergence of length bias often induces the model to favor longer outputs, yet it doesn't equate to an increase in helpful information within these outputs. In this paper, we propose an innovative solution, applying the Product-of-Experts (PoE) technique to separate reward modeling from the influence of sequence length. In our framework, the main expert concentrates on understanding human intents, while the biased expert targets the identification and capture of length bias. To further enhance the learning of bias, we introduce perturbations into the bias-focused expert, disrupting the flow of semantic information. Experimental results validate the effectiveness of our approach, indicating that language model performance is improved, irrespective of sequence length.

## 中文翻译

基于人类反馈的强化学习是一座关键桥梁，使大语言模型与人类及社会价值保持一致。这种对齐需要大量人类反馈语料来学习一个奖励模型，再用该奖励模型微调语言模型。然而我们发现，奖励模型常常找到捷径绕过其原本目标，错误地假定人类偏好更长的回答。长度偏置的出现往往使模型偏爱更长的输出，但这并不等于这些输出中有用信息的增加。本文提出一种新方案，用 Product-of-Experts（PoE）技术把奖励建模与序列长度的影响分离开来。在我们的框架中，主专家专注于理解人类意图，偏置专家则负责识别和捕捉长度偏置。为进一步加强偏置的学习，我们向聚焦偏置的专家引入扰动，破坏语义信息的流动。实验结果验证了本方法的有效性，表明语言模型性能得到提升，且与序列长度无关。

## 关键词

length bias（长度偏置）、RLHF（基于人类反馈的强化学习）、reward model（奖励模型）、reward hacking（奖励劫持）、confounding factor（混杂因子）、Product-of-Experts（专家乘积）、PPO、HH-RLHF、debiasing（去偏）、input perturbation（输入扰动）

---

*说明：原文逐字取自 PDF 摘要（该文双栏排版，正文与图注在文本层存在逐行交错，已按句子顺序重组，未改写）；中文翻译为便于阅读的机器翻译，引用请以英文原文为准。*
