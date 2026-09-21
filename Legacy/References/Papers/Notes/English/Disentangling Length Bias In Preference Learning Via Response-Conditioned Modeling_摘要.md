# Disentangling Length Bias in Preference Learning via Response-Conditioned Modeling — 摘要

> 来源：`Papers/English/Disentangling Length Bias In Preference Learning Via Response-Conditioned Modeling.pdf`
> 作者：Jianfeng Cai, Jinhua Zhu\*, Ruopei Sun, Yue Wang, Li Li, Wengang Zhou, Houqiang Li（\*通讯作者）
> 机构：University of Science and Technology of China；Independent Researcher（二者并列署于标题下方；各作者的具体归属未确认）
> 出处：arXiv:2502.00814v2 [cs.LG]，2025-05-19（预印本；正式 venue 未确认）

## Abstract（原文逐字）

Reinforcement Learning from Human Feedback (RLHF) has achieved considerable success in aligning large language models (LLMs) by modeling human preferences with a learnable reward model and employing a reinforcement learning algorithm to maximize the reward model's scores. However, these reward models are susceptible to exploitation through various superficial confounding factors, with length bias emerging as a particularly significant concern. Moreover, while the pronounced impact of length bias on preference modeling suggests that LLMs possess an inherent sensitivity to length perception, our preliminary investigations reveal that fine-tuned LLMs consistently struggle to adhere to explicit length instructions. To address these two limitations, we propose a novel framework wherein the reward model explicitly differentiates between human semantic preferences and response length requirements. Specifically, we introduce a Response-conditioned Bradley-Terry (Rc-BT) model that enhances the model's capability in length bias mitigating and length instruction following, through training on our augmented dataset. Furthermore, we propose the Rc-RM and Rc-DPO algorithm to leverage the Rc-BT model for reward modeling and direct policy optimization (DPO) of LLMs, simultaneously mitigating length bias and promoting adherence to length instructions. Extensive experiments across various foundational models and datasets demonstrate the effectiveness and generalizability of our approach.

*(原文双栏排版，抽取文本存在行末断词与两栏交错；以上已按句子顺序重组并拼合断词，未改动任何措辞。摘要为原文单一自然段。)*

## 中文翻译

人类反馈强化学习（RLHF）通过可学习的奖励模型对人类偏好建模，并用强化学习算法最大化奖励模型得分，在语言模型对齐上取得了显著成功。然而，这些奖励模型容易被各类表层混杂因素所利用，其中长度偏置尤为突出。此外，尽管长度偏置对偏好建模的显著影响说明 LLM 对长度具有内在感知敏感性，我们的前期考察却发现：微调后的 LLM 始终难以遵循显式的长度指令。针对这两个局限，我们提出一个新框架，使奖励模型能够显式区分"人类语义偏好"与"回答长度要求"。具体地，我们提出 Response-conditioned Bradley-Terry（Rc-BT）模型，通过在增广数据集上训练，提升模型缓解长度偏置与遵循长度指令的能力。进一步地，我们提出 Rc-RM 与 Rc-DPO 算法，利用 Rc-BT 完成奖励建模与 LLM 的直接偏好优化（DPO），在缓解长度偏置的同时提升对长度指令的遵循度。跨多种基座模型与数据集的大量实验证明了本方法的有效性与泛化性。

## 关键词

length bias（长度偏置）、reward hacking（奖励劫持）、Response-conditioned Bradley-Terry / Rc-BT（响应条件化 Bradley-Terry）、Rc-RM、Rc-DPO、RLHF、DPO、PPO、length instruction following（长度指令遵循）、Quality Eval Acc、Length Eval Acc

*（说明：原文未设关键词栏，以上关键词为据摘要与正文抽取的主题词。）*

---

*说明：原文逐字取自 PDF 摘要（双栏排版，已按句子顺序重组并拼合行末断词，未改写）；中文翻译为便于阅读的机器翻译，引用时请以英文原文为准。*
