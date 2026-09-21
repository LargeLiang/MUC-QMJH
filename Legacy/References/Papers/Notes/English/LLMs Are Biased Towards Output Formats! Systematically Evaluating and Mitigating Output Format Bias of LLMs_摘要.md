# LLMs Are Biased Towards Output Formats! Systematically Evaluating and Mitigating Output Format Bias of LLMs — 摘要

> 来源：`Papers/English/LLMs Are Biased Towards Output Formats! Systematically Evaluating and Mitigating Output Format Bias of LLMs.pdf`
> 作者：Do Xuan Long, Hai Nguyen Ngoc, Tiviatis Sim, Hieu Dao, Shafiq Joty, Kenji Kawaguchi, Nancy F. Chen, Min-Yen Kan
> 机构：National University of Singapore；Institute for Infocomm Research (I2R), A*STAR；VinAI Research；Institute of High Performance Computing (IHPC), A*STAR；Salesforce Research；Nanyang Technological University
> 出处：arXiv:2408.08656v2 [cs.CL]，2025-02-23（预印本，会议/期刊未确认）

## Abstract（原文逐字）

We present the first systematic evaluation examining format bias in performance of large language models (LLMs). Our approach distinguishes between two categories of an evaluation metric under format constraints to reliably and accurately assess performance: one measures performance when format constraints are adhered to, while the other evaluates performance regardless of constraint adherence. We then define a metric for measuring the format bias of LLMs and establish effective strategies to reduce it. Subsequently, we present our empirical format bias evaluation spanning four commonly used categories--multiple-choice question-answer, wrapping, list, and mapping--covering 15 widely-used formats. Our evaluation on eight generation tasks uncovers significant format bias across state-of-the-art LLMs. We further discover that improving the format-instruction following capabilities of LLMs across formats potentially reduces format bias. Based on our evaluation findings, we study prompting and fine-tuning with synthesized format data techniques to mitigate format bias. Our methods successfully reduce the variance in ChatGPT's performance among wrapping formats from 235.33 to 0.71 (%2).

## 中文翻译

我们给出首个考察大语言模型（LLM）表现中格式偏置的系统性评估。我们的方法把格式约束下的评测指标区分为两类，以可靠且准确地衡量表现：一类只衡量遵守了格式约束时的表现，另一类则无论是否遵守约束都衡量表现。随后我们定义了一个度量 LLM 格式偏置的指标，并确立了降低该偏置的有效策略。接着，我们给出覆盖四类常用格式——多项选择问答、包裹（wrapping）、列表、映射——共 15 种广泛使用格式的实证格式偏置评估。我们在八个生成任务上的评估揭示了当前最先进 LLM 中显著的格式偏置。我们进一步发现，提升 LLM 跨格式的格式指令跟随能力可能降低格式偏置。基于评估发现，我们研究用合成格式数据进行提示与微调来缓解格式偏置。我们的方法成功把 ChatGPT 在各类包裹格式间的表现方差从 235.33 降到 0.71（%2）。

## 关键词

format bias（格式偏置）、BiasFo（格式偏置度量）、EstTrueE / TrueE / SysE（估计真实评分 / 真实评分 / 系统评分）、format-instruction following（格式指令跟随）、format token bias（格式 token 偏置）、wrapping（包裹格式）、multiple-choice question-answer（多项选择问答）、prompting（提示）、fine-tuning with synthesized format data（合成格式数据微调）

---

*说明：原文逐字取自 PDF 摘要（该文双栏排版，已按句子顺序重组，未改写；摘要中 `--` 为 em dash 的抽取呈现）；中文翻译为便于阅读的机器翻译，引用时请以英文原文为准。*
