# From Lists to Emojis: How Format Bias Affects Model Alignment — 摘要

> 来源：`Papers/English/From Lists to Emojis How Format Bias Affects Model Alignment.pdf`
> 作者：Xuanchang Zhang\*, Wei Xiong\*, Lichang Chen, Tianyi Zhou, Heng Huang, Tong Zhang（\*同等贡献）
> 机构：University of Illinois Urbana-Champaign；University of Maryland College Park
> 出处：arXiv:2409.11704v2 [cs.CL]，2025-05-23（预印本）

## Abstract（原文逐字）

In this paper, we study format biases in reinforcement learning from human feedback (RLHF). We observe that many widely-used preference models--including human evaluators, GPT-4, and top-ranking models on the RewardBench benchmark--exhibit strong biases towards specific format patterns, such as lists, links, bold text, and emojis. Furthermore, large language models (LLMs) can exploit these biases to achieve higher rankings on popular benchmarks like AlpacaEval and LMSYS Chatbot Arena.

One notable example is verbosity bias, where current preference models favor longer responses that appear more comprehensive, even when their quality is equal to or lower than shorter responses. However, format biases beyond verbosity remain largely underexplored. In this work, we extend the study of biases in preference learning beyond the commonly recognized length bias, offering a comprehensive analysis of a wider range of format biases. Additionally, we show that with a small amount of biased data (less than 1%), we can inject significant bias into the reward model. Moreover, these format biases can also be easily exploited by downstream alignment algorithms, such as best-of-n sampling and online iterative DPO, as it is usually easier to manipulate the format than to improve the quality of responses. Our findings emphasize the need to disentangle format and content both for designing alignment algorithms and evaluating models.

*(原文中 `--` 为 em dash 的抽取呈现；两段之间的空行为原文段落分隔。)*

## 中文翻译

本文研究人类反馈强化学习（RLHF）中的格式偏置。我们观察到，许多广泛使用的偏好模型——包括人类评估者、GPT-4 以及 RewardBench 榜单上名列前茅的模型——对特定格式模式表现出强烈偏好，例如列表、链接、加粗文本与 emoji。此外，大语言模型（LLM）可以利用这些偏置在 AlpacaEval、LMSYS Chatbot Arena 等流行榜单上取得更高排名。

一个典型例子是冗长偏置：当前偏好模型偏爱看起来更全面、更长的回答，即使其质量与较短回答相当甚至更低。然而，冗长之外的格式偏置仍研究不足。本文把偏好学习中的偏置研究从常见的长度偏置扩展到更广范围，对多种格式偏置做了系统分析。我们还表明，只需少量（不到 1%）带偏数据即可向奖励模型注入显著偏置；而且这些格式偏置很容易被 best-of-n 采样、在线迭代 DPO 等下游对齐算法利用——因为操纵格式通常比提高回答质量更容易。我们的发现强调：设计对齐算法与评估模型时都必须把格式与内容解耦。

## 关键词

format bias（格式偏置）、reward hacking（奖励劫持）、RLHF、preference model（偏好模型）、length bias / verbosity（长度偏置）、pattern bias（模式偏置）、LLM-as-a-judge、best-of-n、iterative DPO、LMSYS Chatbot Arena

---

*说明：原文逐字取自 PDF 摘要（双栏排版，已按句子顺序重组，未改写）；中文翻译为便于阅读的机器翻译，引用时请以英文原文为准。*
