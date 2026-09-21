# Benchmarking Cognitive Biases in Large Language Models as Evaluators — 摘要

> 来源：`Papers/English/Benchmarking Cognitive Biases in Large Language Models as Evaluators.pdf`
> 作者：Ryan Koo, Minhwa Lee, Vipul Raheja, Jonginn Park, Zae Myung Kim, Dongyeop Kang
> 机构：University of Minnesota；Grammarly
> 出处：arXiv:2309.17012v3 [cs.CL]，2024-09-25（预印本；venue 未确认）

## Abstract（原文逐字）

Large Language Models (LLMs) have recently been shown to be effective as automatic evaluators with simple prompting and in-context learning. In this work, we assemble 16 LLMs encompassing four different size ranges and evaluate their output responses by preference ranking from the other LLMs as evaluators, such as System Star is better than System Square. We then evaluate the quality of ranking outputs introducing the COgnitive Bias Benchmark for LLMs as EvaluatoRs (COBBLER)1, a benchmark to measure six different cognitive biases in LLM evaluation outputs, such as the EGOCENTRIC bias where a model prefers to rank its own outputs highly in evaluation. We find that LLMs are biased text quality evaluators, exhibiting strong indications on our bias benchmark (≥ 40% of comparisons made by all models) within each of their evaluations that question their robustness as evaluators. Furthermore, we examine the correlation between human and machine preferences and calculate the average Rank-Biased Overlap (RBO) score to be 44%, indicating that machine preferences are misaligned with humans. According to our findings, LLMs may still be unable to be utilized for automatic annotation aligned with human preferences.

## 中文翻译

大语言模型（LLM）近来已被证明可借助简单提示与上下文学习充当有效的自动评估者。本文汇集了覆盖四个不同规模区间的 16 个 LLM，让它们互为评审、以偏好排序的方式评价彼此的输出回答，例如"System Star 优于 System Square"。随后我们引入 COBBLER（面向 LLM 评审的认知偏置基准），用以测量 LLM 评估输出中的六种认知偏置，例如 EGOCENTRIC（自我中心）偏置——模型倾向于在评估中把自己的输出排在前面。我们发现 LLM 是有偏的文本质量评审者：在所有模型各自的评估中，都有约 ≥40% 的比较在我们的偏置基准上显示出强烈偏置迹象，这令其评审的稳健性受到质疑。此外，我们考察了人类偏好与机器偏好的相关性，算出平均 Rank-Biased Overlap（RBO）分数为 44%，表明机器偏好与人类并不一致。依据我们的发现，LLM 可能仍无法被用于与人类偏好对齐的自动标注。

## 关键词

COBBLER（认知偏置基准）、cognitive bias（认知偏置）、LLM-as-evaluator（LLM 作为评审）、salience bias / length bias（显著度偏置/长度偏置）、egocentric bias / self-preference（自我中心偏置/自我偏好）、order bias（顺序偏置）、bandwagon effect（从众效应）、Rank-Biased Overlap / RBO（排名偏置重叠度）、human–machine preference alignment（人–机偏好一致性）、pairwise preference（两两偏好）

---

*说明：原文逐字取自 PDF 摘要（双栏排版，已按句子顺序重组，未改写）；中文翻译为便于阅读的机器翻译，引用时请以英文原文为准。两点抽取痕迹已标注：(1) 摘要中"≥ 40%"处原符号在文本层丢失（抽取为 "( 40%"），此处按上下文与正文无偏随机阈值判定还原；(2) "(COBBLER)1" 中的 "1" 为原文脚注标记（指向项目主页），非摘要文字内容。*
