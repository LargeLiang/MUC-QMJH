# note_09 — Park et al.（2024）

## 基本信息

| 项目 | 内容 |
|------|------|
| 标题 | OffsetBias: Leveraging Debiased Data for Tuning Evaluators |
| 作者 | Park Junsoo, et al. |
| 来源 | EMNLP Findings 2024 |
| 文献编号 | [8] |
| 相关性评级 | ★★★★★ 核心文献（系统性偏差分类） |

## 摘要（直接提取）

> Recent large language models (LLMs) used as evaluators demonstrate strong performance in assessing response quality, but they suffer from systematic biases. We introduce **EvalBiasBench**, a benchmark that encompasses **six types of systematic biases**: positional bias, verbosity bias, bandwagon bias, beauty bias, authority bias, and knowledge bias. We develop OffsetBias, an evaluator model tuned on debiased data using our benchmark, and demonstrate significant improvements over state-of-the-art evaluators on both biased and unbiased evaluations.

## 目录结构

1. Introduction — LLM评估器偏差问题
2. EvalBiasBench — 六类系统性偏差基准
   - 2.1 Positional Bias（位置偏差）
   - 2.2 Verbosity Bias（冗长偏差）
   - 2.3 Bandwagon Bias（从众偏差）
   - 2.4 Beauty Bias（美观偏差）
   - 2.5 Authority Bias（权威偏差）
   - 2.6 Knowledge Bias（知识偏差）
3. OffsetBias Model — 去偏评估器训练
4. Experiments — 评估与比较
5. Analysis — 深入分析
6. Conclusion

## 核心观点与方法

### 主要论点
1. **六类系统性偏差的完整分类**：建立了评估器偏差的标准分类体系
2. Verbosity Bias（冗长偏差）：评估器偏好更长的回答，与本课题直接相关
3. 通过构建去偏数据集（debiased data）来训练鲁棒评估器

### 方法
- **EvalBiasBench**：构建覆盖六类偏差的评估基准，每类偏差设计专门测试用例
- **去偏训练**：在识别偏差后，构建明确标注偏差类型的训练数据，训练 OffsetBias 模型
- **评估**：在有偏和无偏数据集上分别评估，证明去偏的有效性

### 关键数据
- OffsetBias 在有偏评估场景下的性能显著优于 GPT-4 和其他 SOTA 评估器
- Verbosity Bias 是六类偏差中效果量最大的之一

## 对论文写作的贡献

1. **偏差分类学**：EvalBiasBench 的六类偏差分类是领域内的标准框架，本文可引用此分类来定位"长度偏差=verbosity bias"和"格式偏差=beauty bias/format preference"的类别归属
2. **引用位置**：
   - Section 1.2.2（"Park 等人构建的 EvalBiasBench 将评估器偏差系统分类为六种类型，其中冗长偏差（verbosity bias）与美观偏差（beauty bias）与本研究核心聚焦直接呼应[9]"）
   - Section 2.1（偏差类型综述）
3. **EMNLP 权威性**：EMNLP Findings 2024，可增加引文的会议级别权威性

## 可直接使用的表述

- "Park 等人在 EMNLP Findings 2024 中构建了 EvalBiasBench，将 LLM 评估器的系统性偏差划分为六类，其中冗长偏差（verbosity bias）与本研究中的长度偏差直接对应[9]"
