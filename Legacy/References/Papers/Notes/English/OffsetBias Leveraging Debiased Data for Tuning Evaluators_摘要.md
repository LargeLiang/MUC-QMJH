# OffsetBias: Leveraging Debiased Data for Tuning Evaluators — 摘要

> 来源：`Papers/English/OffsetBias Leveraging Debiased Data for Tuning Evaluators.pdf`
> 作者：Junsoo Park\*, Seungyeon Jwa\*, Meiying Ren, Daeyoung Kim, Sanghyuk Choi（\*共同一作；通讯作者 Sanghyuk Choi）
> 机构：NC Research；NAVER Cloud
> 出处：arXiv:2407.06551v2 [cs.CL]，2024-10-07（预印本，会议/期刊未确认）

## Abstract（原文逐字）

Employing Large Language Models (LLMs) to assess the quality of generated responses, such as prompting instruct-tuned models or fine-tuning judge models, has become a widely adopted evaluation method. It is also known that such evaluators are vulnerable to biases, such as favoring longer responses. While it is important to overcome this problem, the specifics of these biases remain under-explored. In this work, we qualitatively identify six types of biases inherent in various judge models. We propose EVALBIASBENCH as a meta-evaluation collection of hand-crafted test cases for each bias type. Additionally, we present debiasing dataset construction methods and the associated preference dataset OFFSETBIAS. Experimental results demonstrate that fine-tuning on our dataset significantly enhances the robustness of judge models against biases and improves performance across most evaluation scenarios. We release our datasets and the fine-tuned judge model to public.

## 中文翻译

使用大语言模型（LLM）评估生成回答的质量——例如提示经过指令微调的模型或微调判官模型——已成为广泛采用的评测方法。同时也已知这类评估器容易受偏置影响，例如偏爱更长的回答。尽管克服这一问题很重要，这些偏置的具体内容仍研究不足。本文定性识别出各类判官模型中固有的六种偏置，并提出 EVALBIASBENCH——一个针对每种偏置类型的手工测试用例元评测集合。此外，我们给出构建去偏数据集的方法及相应的偏好数据集 OFFSETBIAS。实验结果表明，在我们的数据上微调能显著增强判官模型对抗偏置的稳健性，并在大多数评测场景中提升表现。我们公开数据集与微调后的判官模型。

## 关键词

length bias（长度偏置）、concreteness bias（具体性偏置）、empty reference bias（空引用偏置）、content continuation bias（内容续写偏置）、nested instruction bias（嵌套指令偏置）、familiar knowledge bias（熟悉知识偏置）、EVALBIASBENCH、OFFSETBIAS、judge model（判官模型）、reward model（奖励模型）、LLM-as-a-judge

---

*说明：原文逐字取自 PDF 摘要（该文双栏排版，已按句子顺序重组；相邻图注文字已剔除，未改写原文）；中文翻译为便于阅读的机器翻译，引用时请以英文原文为准。*
