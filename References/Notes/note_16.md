# note_17 — BiAxisAudit: A Novel Framework to Evaluate LLM Bias Across Prompt Sensitivity and Response-Layer Divergence

## 基本信息

| 字段 | 内容 |
|------|------|
| 编号 | [16] |
| 标题 | BiAxisAudit: A Novel Framework to Evaluate LLM Bias Across Prompt Sensitivity and Response-Layer Divergence |
| 作者 | Jialing Gan, Junhao Dong, Songze Li |
| 机构 | Southeast University（中国）; Nanyang Technological University（新加坡） |
| 发表情况 | arXiv 2025 |
| 关键词 | 偏见审计、提示敏感性、分层编码（Split Coding）、偏见背书率（BER）、双轴框架 |
| 相关性评级 | ★★★★★ |
| 论文位置 | D:\Files\MUC-QMJH\References\Papers\BiAxisAudit A Novel Framework to Evaluate LLM Bias Across Prompt Sensitivity and Response-Layer Divergence.pdf |

---

## 摘要直接提取（Abstract）

> Bias auditing of large language models is increasingly shaped by voluntary governance frameworks such as the NIST AI RMF and binding regulatory regimes such as the EU AI Act. Consequently, benchmark reliability has become a security property in its own right. Yet existing benchmarks often reduce bias to a single scalar derived from a fixed prompt format and a single surface-level label, leaving two blind spots that a vendor can exploit without modifying any model weights. These blind spots are structurally independent (correcting one cannot cancel. Across prompts, meaning-preserving format changes shift bias endorsement by more than 0.7 on a fixed statement pool. Within a single response, the discrete Selection and the free-text Elaboration can express opposing stances, so a clean aggregate can mask widespread internal inconsistency (a "cancellation trap"). Consequently, selection-only and elaboration-only rankings are nearly uncorrelated across LLMs (Spearman ρ=0.238, p=0.570). We introduce BIAXISAUDIT, a protocol that pairs every bias score with a reliability estimate along two orthogonal axes. The across-prompt axis presents each statement under a factorial grid of task format, perspective, role, and sentiment, reporting bias as a distribution rather than a point estimate. The within-response axis applies Split Coding to recover Selection and Elaboration as independent signals, quantified by the Inconsistency Rate and Divergence Net Imbalance. Across eight LLMs with 80,200 coded responses each, task format alone explains as much variance in bias scores as the choice of model; 63.6% of bias signals in the pooled audit (up to 85.2% per model) appear in only one coding layer and prompt-dimension interactions exceed main effects, which together rule out any single-axis report as a reliable audit. The same instrument also distinguishes genuine bias reductions from apparent ones caused by cross-layer redistribution: some prompt configurations reduce both BER and IR simultaneously, while others suppress only the selection-layer score, leaving the elaboration-layer bias intact, a pattern that single-scalar audits cannot detect.

---

## 目录结构

1. Introduction（引言）
   - 现有偏见基准的三大缺陷
2. Framework: BIAXISAUDIT（双轴审计框架）
   - 轴一：跨提示轴（Across-Prompt Axis）——4维提示网格
   - 轴二：响应内轴（Within-Response Axis）——分层编码
3. Research Questions（RQ1–RQ4）
4. Findings（四大发现）
   - Finding 1: 任务格式解释的方差与模型选择相当（η²=0.395）
   - Finding 2: 单层审计遗漏大量偏见信号
   - Finding 3: 维度交互效应超越主效应
   - Finding 4: 双轴框架区分真实vs表观偏见缩减
5. Discussion（讨论）
6. Conclusion（结论）

---

## 核心观点与方法

### 核心问题：现有偏见评估基准的系统性盲点

现有偏见基准（如CrowS-Pairs、StereoSet、BBQ）将偏见压缩为固定提示格式下的单一标量，存在三个结构性缺陷：

1. **格式扭曲判决**：仅改变任务格式，同一模型的偏见背书率（BER）可从0.06变化到0.78，格式本身解释了模型间总方差的 **η²=0.395**。
2. **标签出卖立场**：模型的选择（Selection）和阐述（Elaboration）可以表达对立的立场，传统仅记录离散选项的方法会系统性高估或低估偏见（3/8个模型偏差>10个百分点）。
3. **错误静默抵消**（cancellation trap）：跨条目的高估与低估可相互抵消，产生虚假的"校准良好"分数。

### BIAXISAUDIT双轴框架

**轴一：跨提示轴（Across-Prompt Axis）**
- 在4个维度的析因设计上呈现每条声明：
  - 任务格式（Task Format）：BJ、CTO等不同评估格式
  - 视角（Perspective）：不同叙事视角
  - 角色（Role）：不同角色设定
  - 情感（Sentiment）：正向/负向/中立等
- 以**分布**而非单点估计报告偏见

**轴二：响应内轴（Within-Response Axis）——Split Coding**
- 将每个响应的**离散选择（Selection）**与**自由文本阐述（Elaboration）**作为独立信号分别编码
- 两个统计量：
  - **不一致率（Inconsistency Rate，IR）**：衡量选择与阐述不一致的幅度
  - **散度净不平衡（Divergence Net Imbalance，DNI）**：衡量不一致的方向

### 四大核心发现

| 发现 | 关键数据 |
|------|---------|
| Finding 1 | 任务格式解释方差 η²=0.395，与模型选择相当；单一模型BER波动可达0.78 |
| Finding 2 | 63.6%（最高85.2%）的偏见信号仅出现在单一编码层 |
| Finding 3 | 维度交互效应（η²=0.043）超越情感单独主效应 |
| Finding 4 | 双轴框架区分"共同降低"（BER+IR同降）vs"层重路由"（仅选择层分数下降）|

- **Selection vs Elaboration相关性**：Spearman ρ=0.238，p=0.570，**近乎不相关**——单层分析无法代表另一层

---

## 对本论文写作的贡献

1. **提示格式作为主要混淆变量**：η²=0.395的发现直接支持本论文对"格式偏见"的关注——格式解释的方差与模型本身相当，说明格式不是噪声而是核心驱动因素。
2. **格式变化的量化影响**：0.7以上的BER偏移（仅因格式变化）为本论文格式效应的显著性提供了强有力的旁证。
3. **偏见测量方法论批判**：BiAxisAudit对传统单轴评估的批判，与本论文对"偏好数据不能直接等同于内容质量"的核心论点一致。
4. **分层分析视角**：Split Coding的思路可启发本论文在分析偏好数据时，区分"表层格式信号"与"内容质量信号"。
5. **研究规模参考**：80,200条编码响应 × 8个LLM的评估规模，为本论文136k条数据的分析规模提供比较参照。

---

## 可直接使用的表述

- "Gan et al.（2025）提出双轴偏见审计框架BiAxisAudit，发现任务格式格式所解释的偏见方差（η²=0.395）与模型选择相当，仅改变任务格式就可使同一模型的偏见背书率（BER）波动0.7以上，有力证明了提示格式本身是LLM偏见测量中不可忽视的核心驱动因素。"
- "BiAxisAudit的Split Coding机制揭示，63.6%的偏见信号仅在选择层或阐述层之一出现，两层之间的Spearman相关系数仅为0.238（p=0.570），说明传统仅记录离散选项的评估方式会系统性地遗漏大量真实偏见信号。"
- "该研究的核心警示是：当前LLM偏见审计中普遍使用的单标量方法，既无法捕捉提示格式变化带来的偏见波动，也无法区分'真实偏见缩减'与'层间重路由'带来的表象改善。"
