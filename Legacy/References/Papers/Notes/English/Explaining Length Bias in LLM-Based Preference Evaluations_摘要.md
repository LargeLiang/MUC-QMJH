# Explaining Length Bias in LLM-Based Preference Evaluations — 摘要

> 来源：`Papers/English/Explaining Length Bias in LLM-Based Preference Evaluations.pdf`
> 作者：Zhengyu Hu, Linxin Song, Jieyu Zhang, Zheyuan Xiao, Tianfu Wang, Zhenyu Chen, Jianxun Lian, Nicholas Jing Yuan, Kaize Ding, Hui Xiong
> 机构：香港科技大学（广州）、香港科技大学、南加州大学、华盛顿大学、美团、微软、Resideo、西北大学
> 出处：arXiv:2407.01085v5 [cs.LG]，2025-09-04（预印本）

## Abstract（原文逐字）

The use of large language models (LLMs) as judges, particularly in preference comparisons has become widespread, but this reveals a notable bias towards longer responses, undermining the reliability of such evaluations. To better understand such bias, we propose to decompose the preference evaluation metric, specifically the win rate, into two key components: desirability and information mass, where the former is length-independent and related to trustworthiness such as correctness, toxicity, and consistency, and the latter is length-dependent and represents the amount of information in the response. We empirically demonstrated the decomposition through controlled experiments and found that response length impacts evaluations by influencing information mass. To derive a reliable evaluation metric that assesses content quality without being confounded by response length, we propose AdapAlpaca, a simple yet effective adjustment to win rate measurement. Specifically, AdapAlpaca ensures a fair comparison of response quality by aligning the lengths of reference and test model responses under equivalent length intervals.

## 中文翻译

大语言模型（LLM）作为评判者、尤其是在偏好比较中的使用已相当普遍，但这暴露出对较长回答的显著偏好，损害了此类评价的可靠性。为更好地理解该偏置，我们提出把偏好评价指标（具体为胜率）分解为两个关键成分：desirability 与 information mass，前者与长度无关，与正确性、毒性、一致性等可信赖性相关；后者与长度相关，表示回答中的信息量。我们通过受控实验实证验证了该分解，发现响应长度是通过影响信息量来影响评价的。为得到一个不被响应长度混淆、可评估内容质量的可靠指标，我们提出 AdapAlpaca——一种简单而有效的胜率测量调整：它在等长区间内对齐参照模型与被测模型响应的长度，从而保证对回答质量的公平比较。

## 关键词

length bias（长度偏置）、win rate（胜率）、desirability（合意度）、information mass（信息量）、conditional entropy（条件熵）、AdapAlpaca、LCWR（长度控制胜率）、AlpacaEval、DPO/RLHF、reward model（奖励模型）

---

*说明：原文逐字取自 PDF 摘要（双栏排版，已按句子顺序重组，未改写）；中文翻译为便于阅读的机器翻译，引用时请以英文原文为准。*
