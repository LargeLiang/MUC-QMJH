# note_03 — Liu et al.（2025）

## 基本信息

| 项目 | 内容 |
|------|------|
| 标题 | Format as a Prior: Quantifying and Analyzing Bias in LLMs for Heterogeneous Data |
| 作者 | Liu Jiacheng, et al. |
| 来源 | arXiv, 2025 |
| 文献编号 | [3] |
| 相关性评级 | ★★★★★ 核心文献（格式偏差） |

## 摘要（直接提取）

> We study a specific form of format bias in large language models (LLMs): how formatting of data (structured tables, code, markdown) shapes model outputs and evaluations on heterogeneous tasks. We propose the term "format as a prior" to describe how LLMs encode strong priors over expected output formats, which systematically distort evaluation results on heterogeneous data. We quantify these biases across multiple task types and demonstrate that format preferences can be as influential as content quality in determining evaluation outcomes.

## 目录结构

1. Introduction — 格式作为先验的问题定义
2. Format as a Prior — 理论框架（格式偏差来源与机制）
3. Quantifying Format Bias — 量化格式偏差实验
4. Format Bias in Heterogeneous Data — 异质数据场景下的偏差分析
5. Mitigation Strategies — 缓解策略
6. Related Work
7. Conclusion

## 核心观点与方法

### 主要论点
- LLM 对输出格式存在强先验，这种先验会在异质数据评估中产生系统性偏差
- "格式即先验"（Format as a Prior）：模型倾向于生成并偏好与其训练数据格式分布一致的输出
- 格式偏差在评估中的影响程度可与内容质量相当

### 方法
- **跨任务量化**：在结构化表格、代码生成、Markdown 格式等多类型任务上系统量化格式偏差
- **对比分析**：比较不同格式呈现下的评估结果差异
- **控制实验**：固定内容改变格式，测量纯格式效应大小

### 关键数据与发现
- 格式差异单独引起的评估偏差幅度可达内容质量差异的同量级
- 不同格式类型（表格/代码/Markdown）产生的偏差方向和大小各异

## 对论文写作的贡献

1. **格式偏差的理论化**："Format as a Prior"框架为本文"格式呈现方式影响偏好判断"的论点提供理论基础
2. **引用位置**：Section 1.2.1 末尾，与[5]并列引用，支撑"偏好数据中的形式偏差会被奖励模型误学"
3. **Section 2.1**：可用于说明格式偏差已从多个维度被证实（与[1][5][6]构成证据集合）
4. **与本研究的接口**：本研究对标题、列表、粗体格式特征的独立效应分析，与该文的格式量化思路直接对接

## 可直接使用的表述

- "Liu 等人进一步指出，LLM 对输出格式编码了强先验，使得格式偏差在异质任务评估中达到与内容质量偏差同量级的影响[3]"
