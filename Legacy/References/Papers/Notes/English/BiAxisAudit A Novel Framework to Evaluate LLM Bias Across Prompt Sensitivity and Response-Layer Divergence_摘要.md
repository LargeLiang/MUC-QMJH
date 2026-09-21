# BiAxisAudit: A Novel Framework to Evaluate LLM Bias Across Prompt Sensitivity and Response-Layer Divergence — 摘要

> 来源：`Papers/English/BiAxisAudit A Novel Framework to Evaluate LLM Bias Across Prompt Sensitivity and Response-Layer Divergence.pdf`
> 作者：Jialing Gan*, Junhao Dong, Songze Li*（* 为通讯作者标注；逐人机构对应关系未在文本层标明，未确认）
> 机构：Southeast University, China；Nanyang Technological University, Singapore
> 出处：arXiv:2605.09041v1 [cs.CL]，2026-05-09（预印本；venue 未确认）

## Abstract（原文逐字）

Bias auditing of large language models is increasingly shaped by voluntary governance frameworks such as the NIST AI RMF and binding regulatory regimes such as the EU AI Act. Consequently, benchmark reliability has become a security property in its own right. Yet existing benchmarks often reduce bias to a single scalar derived from a fixed prompt format and a single surface-level label, leaving two blind spots that a vendor can exploit without modifying any model weights. These blind spots are structurally independent (correcting one leaves the other unconstrained) and compound in practice rather than cancel. Across prompts, meaning-preserving format changes shift bias endorsement by more than 0.7 on a fixed statement pool. Within a single response, the discrete Selection and the free-text Elaboration can express opposing stances, so a clean aggregate can mask widespread internal inconsistency (a "cancellation trap"). Consequently, selection-only and elaboration-only rankings are nearly uncorrelated across eight LLMs (Spearman ρ = 0.238, p = 0.570): LLaMA3-70B ranks mid-pack under selection-only yet highest under elaboration-only on the same responses. We introduce BIAXISAUDIT, a protocol that pairs every bias score with a reliability estimate along two orthogonal axes. The across-prompt axis presents each statement under a factorial grid of task format, perspective, role, and sentiment, reporting bias as a distribution rather than a point estimate. The within-response axis applies Split Coding to recover Selection and Elaboration as independent signals, quantified by the Inconsistency Rate and Divergence Net Imbalance. Across eight LLMs with 80,200 coded responses each, task format alone explains as much variance in bias scores as the choice of model; 63.6% of bias signals in the pooled audit (up to 85.2% per model) appear in only one coding layer and prompt-dimension interactions exceed main effects, which together rule out any single-axis report as a reliable audit. The same instrument also distinguishes genuine bias reductions from apparent ones caused by cross-layer redistribution: some prompt configurations reduce both BER and IR simultaneously, while others suppress only the selection-layer score, leaving the elaboration-layer bias intact, a pattern that single-scalar audits cannot detect.

## 中文翻译

大语言模型的偏见审计正日益受到自愿性治理框架（如 NIST AI RMF）与具有约束力的监管制度（如 EU AI Act）的塑造。因此，基准的可靠性本身已成为一种安全属性。然而现有基准往往把偏见压缩成由固定提示格式与单一表层标签导出的一个标量，留下两个厂商无需修改任何模型权重即可利用的盲点。这两个盲点在结构上相互独立（修正其一并不约束其二），在实践中会叠加而非相互抵消。就提示而言，在固定陈述池上，保持语义不变的格式变化可使偏见认同率变动超过 0.7。在单条回答内部，离散的 Selection 与自由文本的 Elaboration 可以表达相反的立场，因此一个干净的汇总值可能掩盖广泛的内部不一致（"抵消陷阱"）。于是，仅按 Selection 与仅按 Elaboration 得到的模型排名在八个 LLM 上几乎不相关（Spearman ρ = 0.238，p = 0.570）：在同一批回答上，LLaMA3-70B 在 selection-only 下处于中游，却在 elaboration-only 下排在最前。我们提出 BIAXISAUDIT：该协议为每一个偏见分数配一个沿两条正交轴的可靠性估计。跨提示轴把每条陈述置于 task format、perspective、role 与 sentiment 的因子网格下，把偏见报告为分布而非点估计。回答内轴用 Split Coding 把 Selection 与 Elaboration 还原为独立信号，并以 Inconsistency Rate 与 Divergence Net Imbalance 加以量化。在八个 LLM、每个模型 80,200 条编码回答上，仅任务格式一项对偏见分数方差的解释力就与模型选择相当；汇总审计中有 63.6% 的偏见信号（单模型最高 85.2%）只出现在一个编码层，且提示维度之间的交互项超过主效应——这些共同排除了以任何单轴报告作为可靠审计的可能。同一工具还能区分真实的偏见下降与由跨层重分配造成的表面下降：某些提示配置同时降低 BER 与 IR，另一些则只压低 selection 层的分数、让 elaboration 层的偏见原封不动，而这种模式是单标量审计无法察觉的。

## 关键词

bias auditing（偏见审计）、prompt sensitivity（提示敏感性）、split coding（分层编码）、BER / Bias Endorsement Rate（偏见认同率）、Inconsistency Rate / IR（不一致率）、Divergence Net Imbalance / DNI（分歧净不平衡）、cancellation trap（抵消陷阱）、prompt-shopping（挑提示词）、factorial design（因子设计）、LLM-as-a-judge（以 LLM 为评委）

---

*说明：原文逐字取自 PDF 摘要（该文双栏排版，图注与正文在文本层存在逐行交错，已按句子顺序重组，未改写）；原文本层的希腊字母 ρ 缺失，此处按上下文恢复为 Spearman ρ，引用前请核对 PDF。中文翻译为便于阅读的机器翻译，引用请以英文原文为准。*
