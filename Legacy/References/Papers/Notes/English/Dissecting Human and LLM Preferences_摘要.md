# Dissecting Human and LLM Preferences — 摘要

> 来源：`Papers/English/Dissecting Human and LLM Preferences.pdf`
> 作者：Junlong Li, Fan Zhou, Shichao Sun, Yikai Zhang, Hai Zhao, Pengfei Liu
> 机构：Shanghai Jiao Tong University；Shanghai Artificial Intelligence Laboratory；Hong Kong Polytechnic University；Generative AI Research Lab (GAIR)
> 出处：arXiv:2402.11296v1 [cs.CL]，2024-02-17（预印本，会议/期刊未确认）

## Abstract（原文逐字）

As a relative quality comparison of model responses, human and Large Language Model (LLM) preferences serve as common alignment goals in model fine-tuning and criteria in evaluation. Yet, these preferences merely reflect broad tendencies, resulting in less explainable and controllable models with potential safety risks. In this work, we dissect the preferences of human and 32 different LLMs to understand their quantitative composition, using annotations from real-world user-model conversations for a fine-grained, scenario-wise analysis. We find that humans are less sensitive to errors, favor responses that support their stances, and show clear dislike when models admit their limits. On the contrary, advanced LLMs like GPT-4-Turbo emphasize correctness, clarity, and harmlessness more. Additionally, LLMs of similar sizes tend to exhibit similar preferences, regardless of their training methods, and fine-tuning for alignment does not significantly alter the preferences of pretrained-only LLMs. Finally, we show that preference-based evaluation can be intentionally manipulated. In both training-free and training-based settings, aligning a model with the preferences of judges boosts scores, while injecting the least preferred properties lowers them. This results in notable score shifts: up to 0.59 on MT-Bench (1-10 scale) and 31.94 on AlpacaEval 2.0 (0-100 scale), highlighting the significant impact of this strategic adaptation.

## 中文翻译

作为模型回答之间的相对质量比较，人类与大语言模型（LLM）的偏好既是模型微调中常见的对齐目标，也是评测中的常见准则。然而这些偏好只反映了宽泛的倾向，导致模型可解释性与可控性不足，并带来潜在安全风险。本文分解了人类与 32 个不同 LLM 的偏好以理解其量化构成，使用真实用户—模型对话的标注做细粒度、分场景的分析。我们发现人类对错误较不敏感，偏好支持自身立场的回答，并在模型承认能力有限时表现出明显反感。相反，GPT-4-Turbo 等先进 LLM 更强调正确性、清晰度与无害性。此外，规模相近的 LLM 往往表现出相似偏好，与训练方法无关；对齐微调也不会显著改变仅预训练模型的偏好。最后，我们证明基于偏好的评测可被有意操纵：在免训练与基于训练的两种设置下，使模型贴近评委偏好会抬升分数，而注入最不受偏好的属性会压低分数。这带来显著的分数变动：MT-Bench（1–10 分制）最高 0.59，AlpacaEval 2.0（0–100 分制）最高 31.94，凸显了这种策略性适配的巨大影响。

## 关键词

preference dissection（偏好分解）、Bayesian logistic regression（贝叶斯 logistic 回归）、Chatbot Arena Conversations、degree of preference（偏好度）、well formatted（格式良好）、lengthy（冗长）、sycophancy（谄媚）、LLM-as-a-judge、AlpacaEval 2.0、MT-Bench

---

*说明：原文逐字取自 PDF 摘要（该文为单栏排版，未改写）；中文翻译为便于阅读的机器翻译，引用时请以英文原文为准。*
