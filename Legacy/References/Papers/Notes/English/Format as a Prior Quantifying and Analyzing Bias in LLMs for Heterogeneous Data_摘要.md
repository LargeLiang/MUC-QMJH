# Format as a Prior: Quantifying and Analyzing Bias in LLMs for Heterogeneous Data — 摘要

> 来源：`Papers/English/Format as a Prior Quantifying and Analyzing Bias in LLMs for Heterogeneous Data.pdf`
> 作者：Jiacheng Liu\*, Mayi Xu\*, Qiankun Pi, Wenli li, Ming Zhong, Yuanyuan Zhu, Mengchi Liu, Tieyun Qian（\*共同第一作者；通讯作者 Tieyun Qian）
> 机构：School of Computer Science, Wuhan University, China
> 出处：arXiv:2508.15793v1 [cs.CL]，2025-08-13（预印本；正式 venue 未确认）

## Abstract（原文逐字）

Large Language Models (LLMs) are increasingly employed in applications that require processing information from heterogeneous formats, including texts, tables, infoboxes, and knowledge graphs. However, systematic biases toward particular formats may undermine LLMs' ability to integrate heterogeneous data impartially, potentially resulting in reasoning errors and increased risks in downstream tasks. Despite these concerns, it remains uncertain whether such format biases are systematic, which data-level factors contribute to them, and what internal mechanisms in LLMs underlie their emergence.

In this paper, we make the first attempt to investigate and analyze the format bias in LLMs. To systematically investigate the aforementioned questions, we conduct a three-stage empirical study by constructing an heterogeneous data conflict scenario for the exploration of bias. The first stage explores the presence and direction of bias across a diverse range of LLMs. The second stage aims to examine how key data-level factors, including information richness, structure quality, and format type, influence these biases.

The third stage analyzes how format bias emerges within LLMs' attention patterns and evaluates a lightweight intervention to test its effectiveness. Based on these investigations, we identify three future research directions to reduce format bias: enhancing data pre-processing through format repair and normalization, introducing inference-time interventions such as attention re-weighting, and developing format-balanced training corpora. These directions will support the design of more robust and fair heterogeneous data processing systems.

*(原文双栏排版，抽取文本存在行末断词与两栏交错；以上已按句子顺序重组并拼合断词，未改动任何措辞。三个自然段的分段取自原排版。)*

## 中文翻译

大语言模型（LLM）越来越多地被用于处理来自异构格式（包括文本、表格、信息框与知识图谱）的信息。然而，对特定格式的系统性偏好可能损害 LLM 公平整合异构数据的能力，进而导致推理错误并放大下游任务的风险。尽管存在这些担忧，但此类格式偏置是否具有系统性、哪些数据层因素导致它们、以及 LLM 内部何种机制使其产生，仍不清楚。

本文首次尝试对 LLM 中的格式偏置进行考察与分析。为系统研究上述问题，我们构造了一个异构数据冲突场景，开展三阶段实证研究。第一阶段探究偏置在多种 LLM 上的存在性与方向；第二阶段考察关键数据层因素（信息丰富度、结构质量、格式类型）如何影响这些偏置。

第三阶段分析格式偏置如何体现在 LLM 的注意力模式中，并评估一种轻量级干预是否有效。基于这些考察，我们提出三个减少格式偏置的未来研究方向：通过格式修复与归一化强化数据预处理、引入注意力重加权等推理期干预、以及构建格式均衡的训练语料。这些方向将支撑更稳健、更公平的异构数据处理系统的设计。

## 关键词

format bias（格式偏置）、heterogeneous data / heterogeneous reasoning（异构数据／异构推理）、format as a prior（格式即先验）、Dual Coverage Rate / DCR（双重覆盖率）、Format Preference Ratio / FPR（格式偏好比）、attention re-weighting（注意力重加权）、knowledge conflict（知识冲突）、ConflictBank、LLM-as-a-judge

*（说明：原文未设关键词栏，以上关键词为据摘要与正文抽取的主题词。）*

---

*说明：原文逐字取自 PDF 摘要（双栏排版，已按句子顺序重组并拼合行末断词，未改写）；中文翻译为便于阅读的机器翻译，引用时请以英文原文为准。*
