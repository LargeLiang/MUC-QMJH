# Length-Controlled AlpacaEval: A Simple Way to Debias Automatic Evaluators — 摘要

> 来源：`Papers/English/Length-Controlled AlpacaEval A Simple Way to Debias Automatic Evaluators.pdf`
> 作者：Yann Dubois, Balázs Galambosi, Percy Liang, Tatsunori B. Hashimoto
> 机构：Stanford University；Independent Researcher
> 出处：arXiv:2404.04475v2 [cs.LG]，2025-03-10（据引用该文的 Kim et al. 2025 参考文献条目，另发表于 First Conference on Language Modeling / COLM 2024；原文正文未标注）

## Abstract（原文逐字）

LLM-based auto-annotators have become a key component of the LLM development process due to their cost-effectiveness and scalability compared to human-based evaluation. However, these auto-annotators can introduce biases that are hard to remove. Even simple, known confounders such as preference for longer outputs remain in existing automated evaluation metrics. We propose a simple regression analysis approach for controlling biases in auto-evaluations. As a real case study, we focus on reducing the length bias of AlpacaEval, a fast and affordable benchmark for instruction-tuned LLMs that uses LLMs to estimate response quality. Despite being highly correlated with human preferences, AlpacaEval is known to favor models that generate longer outputs. We introduce a length-controlled AlpacaEval that aims to answer the counterfactual question: "What would the preference be if the model's and baseline's output had the same length?" To achieve this, we first fit a generalized linear model to predict the biased auto-annotator's preferences based on the mediators we want to control for (length difference) and other relevant features. We then obtain length-controlled preferences by predicting preferences while conditioning the GLM with a zero difference in lengths. Length-controlling not only improves the robustness of the metric to manipulations in model verbosity, we also find that it increases the Spearman correlation with LMSYS Chatbot Arena from 0.94 to 0.98. We release the code and resulting leaderboard.

## 中文翻译

基于 LLM 的自动标注者（auto-annotator）因成本低、可扩展性优于人工评估，已成为 LLM 研发流程的关键环节。然而这些自动标注者会引入难以去除的偏置，即便是"偏好更长输出"这类简单且已知的混淆因素，在现有自动评价指标中依然存在。我们提出一种简单的回归分析方法来控制自动评价中的偏置。作为一个真实案例，我们聚焦降低 AlpacaEval 的长度偏置——AlpacaEval 是一个面向指令微调 LLM 的快速且低成本的基准，使用 LLM 来估计回答质量。尽管与人类偏好高度相关，AlpacaEval 已知会偏爱生成较长输出的模型。我们提出长度控制的 AlpacaEval，旨在回答如下反事实问题："若被测模型与基线的输出长度相同，偏好会是什么？"为此，我们先拟合一个广义线性模型，依据我们希望控制的中介变量（长度差）及其它相关特征来预测带偏的自动标注者偏好；随后在把长度差置零的条件下做预测，得到长度控制的偏好。长度控制不仅提升了指标对"操纵模型冗长程度"的稳健性，我们还发现它把与 LMSYS Chatbot Arena 的 Spearman 相关系数从 0.94 提高到 0.98。我们公开了代码与所得排行榜。

## 关键词

length bias（长度偏置）、LLM-based auto-annotator / LLM-as-a-judge（大模型自动标注者 / 大模型评审）、AlpacaEval、length-controlled win rate（长度控制胜率）、mediator / confounder（中介 / 混淆变量）、Controlled Direct Effect（控制直接效应）、generalized linear model / logistic regression（广义线性模型 / logistic 回归）、length gameability（长度可博弈性）、Chatbot Arena / Spearman correlation、spurious correlation（虚假相关，含 presence of lists）

---

*说明：原文逐字取自 PDF 摘要（双栏排版，已按句子顺序重组，未改写）；中文翻译为便于阅读的机器翻译，引用时请以英文原文为准。*
