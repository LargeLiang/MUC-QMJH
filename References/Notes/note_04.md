# note_05 — Li Junlong et al.（2024）

## 基本信息

| 项目 | 内容 |
|------|------|
| 标题 | Dissecting Human and LLM Preferences |
| 作者 | Li Junlong, Fan Zhou, Shichao Sun, Yikai Zhang, Hai Zhao, Pengfei Liu |
| 来源 | arXiv:2402.11296, 2024（上海交通大学 & 上海人工智能实验室） |
| 文献编号 | [4] |
| 相关性评级 | ★★★★★ 核心文献（人类偏好结构分析） |

## 摘要（直接提取）

> As a relative quality comparison of model responses, human and Large Language Model (LLM) preferences serve as common alignment goals in model fine-tuning and criteria in evaluation. Yet, these preferences merely reflect broad tendencies, resulting in less explainable and controllable models with potential safety risks. In this work, we dissect the preferences of human and 32 different LLMs to understand their quantitative composition, using annotations from real-world user-model conversations for a fine-grained, scenario-wise analysis. We find that **humans are less sensitive to errors, favor responses that support their stances, and show clear dislike when models admit their limits**. On the contrary, advanced LLMs like GPT-4-Turbo emphasize correctness, clarity, and harmlessness more. Additionally, LLMs of similar sizes tend to exhibit similar preferences, regardless of their training methods, and fine-tuning for alignment does not significantly alter the preferences of pretrained-only LLMs. Finally, we show that preference-based evaluation can be intentionally manipulated.

## 目录结构

1. Introduction — 人类与LLM偏好研究的动机与问题
2. Related Work — 对齐方法、偏好研究现状
3. Preference Dissection（偏好解剖框架）
   - 3.1 High-level Methodology
   - 3.2 Properties Definition（属性定义）
   - 3.3 Annotation Pipeline
4. Dissecting Human Preferences — 人类偏好特征分析
5. Dissecting LLM Preferences — LLM偏好特征分析
6. Manipulating Preference-based Evaluation — 偏好评估可操控性
7. Conclusion

## 核心观点与方法

### 主要论点
1. **人类偏好的系统性结构**：人类偏好"lengthy（篇幅长）"的权重在比较评估中居首位，超过正确性等实质内容指标
2. **人机偏好差异**：GPT-4-Turbo 偏好正确性、清晰度、无害性；人类偏好支持其观点的回答，不喜欢模型承认局限
3. **偏好的可操控性**：通过训练可以调高/调低任意属性的评分，在 AlpacaEval 上得分变化最高 31.94 分
4. **长度是最强的人类偏好驱动因素之一**

### 方法
- **数据来源**：ChatBot Arena 真实对话（Chatbot Arena Conversations）
- **标注体系**：31个预定义属性，GPT-4-Turbo自动标注（Likert量表）
- **分析模型**：Bayesian logistic regression（贝叶斯逻辑回归），拟合各属性对最终偏好的权重
- **32个LLM**：覆盖参数量 1B 到 >175B 的主流开源/闭源模型

### 关键数据
- 人类最高偏好属性：**lengthy** > no severe error > supportive of stance
- GPT-4-Turbo 最高偏好：no severe error > clarity > harmless
- 通过 MT-Bench 操控实验：分数变化区间 ±0.59（1-10分制）

## 对论文写作的贡献

1. **核心证据**：为本文"lengthy 是人类偏好最高权重属性"提供实证基础，是最直接的支撑文献
2. **引用位置**：Section 1.2.2（"Li 等人的细粒度拆解分析表明，'lengthy' 是真实对话场景中人类偏好最具分量的属性之一[5]"）；Section 1.2.1 末尾；Section 2.1
3. **数据集关联**：该研究使用的 ChatBot Arena 数据集与本文使用的 LMArena 数据集同源，增强可比性
4. **可操控性论证**：其 Section 4.3 的操控实验，支撑了本文关于"形式偏差会被对齐算法放大"的论点

## 可直接使用的表述

- "Li 等人通过对人类与 32 种 LLM 偏好的细粒度量化拆解，发现在真实对话场景中，'lengthy（篇幅更长）'是人类偏好评估中权重最高的属性之一[5]"
