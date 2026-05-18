# note_14 — LLMs Are Biased Towards Output Formats! Systematically Evaluating and Mitigating Output Format Bias of LLMs

## 基本信息

| 字段 | 内容 |
|------|------|
| 编号 | [13] |
| 标题 | LLMs Are Biased Towards Output Formats! Systematically Evaluating and Mitigating Output Format Bias of LLMs |
| 作者 | Do Xuan Long, Hai Nguyen Ngoc, Tiviatis Sim, Hieu Dao, Shafiq Joty, Kenji Kawaguchi, Nancy F. Chen, Min-Yen Kan |
| 机构 | National University of Singapore (NUS); Institute for Infocomm Research (I2R), A*STAR; VinAI Research; Salesforce Research; NTU |
| 发表情况 | 预印本（arXiv 2024）|
| 关键词 | 格式偏见、输出格式评估、SysE / TrueE / EstTrueE、格式微调 |
| 相关性评级 | ★★★★★ |
| 论文位置 | D:\Files\MUC-QMJH\References\Papers\LLMs Are Biased Towards Output Formats! Systematically Evaluating and Mitigating Output Format Bias of LLMs.pdf |

---

## 摘要直接提取（Abstract）

> We present the first systematic evaluation examining format bias in performance of large language models (LLMs). Our approach distinguishes between two categories of an evaluation metric under format constraints to reliably and accurately assess performance: one measures performance when format constraints are adhered to, while the other evaluates performance regardless of constraint adherence. We then define a metric for measuring the format bias of LLMs and establish effective strategies to reduce it. Subsequently, we present our empirical format bias evaluation spanning four commonly used categories—multiple-choice question-answer, wrapping, list, and mapping—covering 15 widely-used formats. Our evaluation on eight generation tasks uncovers significant format bias across state-of-the-art LLMs. We further discover that improving the format-instruction following capabilities of LLMs across formats potentially reduces format bias. Based on our evaluation findings, we study prompting and fine-tuning with synthesized format data techniques to mitigate format bias. Our methods successfully reduce the variance in ChatGPT's performance among wrapping formats from 235.33 to 0.71 (‰²).

---

## 目录结构

1. Introduction（引言）
2. Related Works（相关工作）
3. Output Format Evaluation Framework（输出格式评估框架）
   - 3.1 理论分析：格式评估（SysE / TrueE / EstTrueE 定义）
   - 3.2 格式偏差指标
4. Evaluation Categories（评估类别）
   - MCQ格式、包装格式、列表格式、映射格式
5. Empirical Evaluation（实证评估）
   - 5.1–5.4 各格式类别详细评估结果
6. Mitigation Methods（缓解方法）
   - 提示法：少样本演示、重复格式指令
   - 微调法：合成格式数据微调
7. Conclusion（结论）

---

## 核心观点与方法

### 核心发现：LLM存在显著输出格式偏见

LLM不仅有**长度偏见**，还存在**格式偏见**（format bias）：不同输出格式约束下，同一模型的性能差异巨大。ChatGPT在"包装格式"（wrapping formats）之间的性能方差高达 **235.33**，经过格式微调后降至 **0.71**。

### 理论框架：两类评估指标

论文提出区分两类评估指标来准确测量格式偏见：

**1. SysE（Systematic Evaluation Score，系统评估分数）**
$$\text{SysE} = \frac{1}{n}\sum_{i=1}^{n}(E(y_i, \text{Ext}_C(\hat{y}_i)) \cdot F_C(\hat{y}_i))$$
- 仅对**满足格式约束的回答**评分，不满足格式的回答得0分
- 问题：当格式遵循率低时，SysE会被压低，不能反映模型真实能力

**2. TrueE（True Evaluation Score，真实评估分数）**
- 测量模型**不论是否满足格式约束**时的真实任务表现
- 问题：需要人工标注，成本高

**3. EstTrueE（估计真实分数）**
$$\text{EstTrueE} = \begin{cases} \frac{\text{SysE}}{\text{FI}_C} \cdot 100 & \text{if } \text{FI}_C \neq 0 \\ 0 & \text{otherwise} \end{cases}$$
- 通过将SysE除以格式遵循率（FI）来估计TrueE
- 无需人工标注，可大规模自动评估格式偏见

### 四大格式类别、15种格式

| 类别 | 代表格式 |
|------|---------|
| 多选问答（MCQ） | 选择题格式、链式思维格式 |
| 包装格式（Wrapping） | 加粗最终答案、斜体最终答案、填空句式等 |
| 列表格式（List） | 有序列表、无序列表等 |
| 映射格式（Mapping） | 键值对映射、JSON格式等 |

### 8项生成任务的评估结果

- 覆盖推理、问答等8类任务
- 发现所有主流LLM（包括ChatGPT、LLaMA等）均存在**显著格式偏见**
- 格式不同导致性能波动，并非因为模型能力本身，而是格式跟随能力的缺失

### 三种缓解方法

| 方法 | 效果 |
|------|------|
| 少样本演示提示 | 显著降低格式偏见 |
| 重复格式指令 | 降低格式偏见 |
| 合成格式数据微调 | ChatGPT包装格式方差从235.33→**0.71** |

---

## 对本论文写作的贡献

1. **格式偏见的量化框架**：SysE/TrueE/EstTrueE的三重指标体系，为论文第二章格式偏见概念界定提供严格的操作性定义。
2. **关键数字支撑**：235.33降至0.71的方差变化，是格式偏见规模最具说服力的量化证据之一。
3. **偏见范围的证明**：15种格式 × 8种任务的系统评估，证明格式偏见是**跨格式、跨任务**的普遍现象。
4. **与[8]（Zhang, Lists to Emojis）的互补**：[8]研究奖励模型中的格式偏见，本文研究直接任务性能中的格式偏见，两者共同构建格式偏见的完整图景。
5. **评估方法论贡献**：EstTrueE估计器的设计，对本论文在分析格式偏见时如何控制格式遵循率变量有参考意义。

---

## 可直接使用的表述

- "Do et al.（2024）首次系统性地评估了LLM输出格式偏见，发现ChatGPT在不同包装格式间的性能方差高达235.33，经过格式数据微调后降至0.71，证明格式偏见是可被量化和缓解的。"
- "该研究区分了SysE（系统评估分数）和TrueE（真实评估分数），并提出EstTrueE估计量，使格式偏见的大规模自动评估成为可能。"
- "覆盖15种格式、8类任务的评估表明，格式偏见在主流大语言模型中普遍存在，且不同格式下同一模型的性能差异具有统计显著性。"
