# note_19 — Benchmarking Cognitive Biases in Large Language Models as Evaluators (CoBBLEr)

## 基本信息

| 字段 | 内容 |
|------|------|
| 编号 | [18] |
| 标题 | Benchmarking Cognitive Biases in Large Language Models as Evaluators |
| 作者 | Ryan Koo, Minhwa Lee, Vipul Raheja, Jong Inn Park, Zae Myung Kim, Dongyeop Kang |
| 机构 | University of Minnesota; Grammarly |
| 发表会议 | ACL 2024 Findings |
| 关键词 | 认知偏见基准、CoBBLEr、LLM-as-evaluator、RBO偏好相关性、6类认知偏见 |
| 相关性评级 | ★★★★★ |
| 论文位置 | D:\Files\MUC-QMJH\References\Papers\English\Benchmarking Cognitive Biases in Large Language Models as Evaluators.pdf |

---

## 摘要直接提取（Abstract）

> Large Language Models (LLMs) have recently been shown to be effective as automatic evaluators with simple prompting and in-context learning. In this work, we assemble 16 LLMs encompassing four different size ranges and evaluate their output responses by preference ranking from the other LLMs as evaluators, such as System Star is better than System Square. We then evaluate the quality of ranking outputs introducing the COgnitive Bias Benchmark for LLMs as EvaluatoRs (COBBLER), a benchmark to measure six different cognitive biases in LLM evaluation outputs, such as the EGOCENTRIC bias where a model prefers to rank its own outputs highly in evaluation. We find that LLMs are biased text quality evaluators, exhibiting strong indication on our bias benchmark (≈40% of comparisons made by all models) within each of their evaluations that question their robustness as evaluators. Furthermore, we examine the correlation between human and machine preferences and calculate the average Rank-Biased Overlap (RBO) score to be 44%, indicating that machine preferences are misaligned with humans. According to our findings, LLMs may still be unable to be utilized for automatic annotation aligned with human preferences.

---

## 目录结构

1. Introduction（引言）
2. Related Work（相关工作）
   - LLMs作为评估者
   - LLM评估基准
   - 认知偏见
3. COBBLER: Cognitive Bias Benchmark for LLMs as Evaluators（基准框架）
   - 3.1 隐式偏见（Implicit Biases）
   - 3.2 诱导偏见（Induced Biases）
4. Experimental Setup（实验设置）
5. Results and Analysis（结果与分析）
6. Conclusion（结论）

---

## 核心观点与方法

### 核心问题：LLM-as-evaluator的认知偏见

当LLM被用作自动评估者时，它们表现出类似于人类认知偏见的系统性误判。这些偏见严重影响了LLM-as-judge方法的可靠性，进而影响RLHF中偏好数据的质量。

### 六大认知偏见类型（COBBLER）

| 偏见类型 | 类别 | 定义 |
|---------|------|------|
| **Order Bias（顺序偏见）** | 隐式 | 倾向于偏好某一特定顺序（第一个或最后一个）的响应 |
| **Compassion Fade（同情消退）** | 隐式 | 因出现可识别的名字（vs匿名别名）而产生不同评估 |
| **Egocentric Bias（自我中心偏见）** | 隐式 | 倾向于偏好自己生成的响应 |
| **Salience Bias / Length Bias（显著性偏见/长度偏见）** | 隐式 | 倾向于偏好更长或更短的响应 |
| **Bandwagon Effect（从众效应）** | 诱导 | 受"85%的人认为..."等虚假统计影响评判 |
| **Attentional Bias（注意力偏见）** | 诱导 | 被无关信息分散注意力（如"系统X喜欢吃橘子"）|

### 实验设计

- **16个LLM**：涵盖4个规模范围（从3B到>175B参数）的开源/闭源模型
- **50条QA指令**：来自BIGBENCH和ELI5两个成熟基准
- **轮询比较**：每个模型评估所有其他模型生成的响应
- **总计**：42K样本 × 6种偏见 × 各模型 = 630K比较

### 主要发现

| 发现 | 关键数据 |
|------|---------|
| 认知偏见普遍性 | **≈40%**的比较中出现偏见信号 |
| 人机偏好对齐 | 平均RBO（Rank-Biased Overlap）得分 = **44%** |
| 含义 | LLM偏好与人类偏好严重不一致 |

**重要注意**：论文原文明确指出平均RBO = **44%**，而非49.6%。如论文中引用的是49.6%，需要修正。

### 两类偏见的区别

- **隐式偏见**：无需额外信息就能通过标准评估提示观察到（顺序/同情消退/自我中心/长度）
- **诱导偏见**：通过在提示中加入虚假或无关信息引发（从众效应/注意力偏见）

---

## 对本论文写作的贡献

1. **长度偏见的LLM评估者视角**：Salience Bias（长度偏见）作为六大认知偏见之一，证明长度偏见不仅存在于人类评估者，也广泛存在于LLM-as-judge系统中，形成双重偏见结构。
2. **≈40%的偏见发生率**：为本论文量化偏见"规模"提供了直接可引用的数据。
3. **RBO=44%的人机不对齐**：证明LLM的偏好分布与人类真实偏好存在系统性偏差，为本论文使用**真实人类偏好数据**（而非LLM-as-judge）的设计选择提供了方法论依据。
4. **认知偏见框架**：将偏好数据中的偏见与认知科学文献连接，为本论文引入"偏见"概念时的理论框架选择提供参考。
5. **数字修正**：本论文中若引用了"49.6%"的RBO，需更正为论文原文中的 **44%**。

---

## 注意事项（数据修正）

**现有论文草稿中的错误**：
- 论文草稿写到"RBO均值仅为49.6%"
- CoBBLEr原文明确说："calculate the average Rank-Biased Overlap (RBO) score to be 44%"
- **需要将49.6%修正为44%**

---

## 可直接使用的表述

- "Koo et al.（2024）提出COBBLER基准，系统评估16个主流LLM作为自动评估者时表现出的六类认知偏见，包括顺序偏见、自我中心偏见和长度偏见（Salience Bias）等，发现约40%的比较中存在明显偏见信号，且机器偏好与人类偏好的Rank-Biased Overlap（RBO）仅为44%，揭示了LLM-as-judge方法与人类判断之间的系统性偏差。"
- "该研究中，长度偏见被作为显著性偏见（Salience Bias）纳入认知偏见框架，表明LLM评估者与人类评估者均倾向于偏好特定长度的响应，无论其内容质量如何。"
- "COBBLER的实验结果表明，即使是最先进的LLM也无法胜任可靠的自动标注工作，机器偏好与人类偏好的平均RBO仅44%，这从评估者层面为研究人类偏好数据中系统性偏见提供了方法论依据。"
