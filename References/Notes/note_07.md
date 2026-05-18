# note_08 — Zhang Junda et al.（2024）

## 基本信息

| 项目 | 内容 |
|------|------|
| 标题 | From Lists to Emojis: How Format Biases Affect LLM-Based Preference Judgments |
| 作者 | Zhang Junda, et al. |
| 来源 | arXiv, 2024 |
| 文献编号 | [7] |
| 相关性评级 | ★★★★★ 核心文献（格式偏差实证） |

## 摘要（直接提取）

> Large language models (LLMs) are increasingly used as judges in preference evaluations. However, LLM-based evaluations can be biased by **format features** such as bullet lists, bold text, and emojis. We systematically study how such format biases affect preference judgments, finding that **less than 1% of biased training samples can cause significant reward model bias**, and that different format types can interact or cancel each other out. We demonstrate that these biases transfer from training data to reward models used in RLHF, compounding the alignment risk.

## 目录结构

1. Introduction — 格式偏差问题背景
2. Format Features and Bias Types — 格式特征分类（列表、粗体、emoji等）
3. Empirical Analysis — 实证分析（多格式、多任务）
   - 3.1 Reward Model Format Bias
   - 3.2 Interaction Effects Between Formats
4. Impact on RLHF — 对训练数据与奖励模型的影响
5. Mitigation Approaches — 缓解方案
6. Related Work
7. Conclusion

## 核心观点与方法

### 主要论点
1. 格式特征（列表、粗体、emoji等）会系统性影响LLM裁判的偏好判断
2. **极少量有偏样本即可导致显著奖励模型偏差**：训练数据中仅 <1% 的格式有偏样本，即可在奖励模型中造成显著偏差
3. 不同格式特征之间存在**交互效应**（某些组合会放大偏差，某些会相消）
4. 格式偏差从人类偏好数据传导至奖励模型，并最终影响RLHF训练的模型行为

### 方法
- **格式分类体系**：定义覆盖列表（ordered/unordered）、粗体、emoji、代码块、标题等多类格式特征
- **控制实验**：固定内容，通过添加/删除格式特征来测量纯格式效应
- **污染实验**：在训练数据中注入不同比例的格式有偏样本，观察奖励模型偏差变化
- **交互分析**：两两格式组合的偏差交互矩阵

### 关键数据
- **<1% 有偏样本足以导致奖励模型显著偏差**（这是最核心的发现）
- 不同格式特征之间的交互效应既有放大也有相消
- Emoji 和 Bold 的效果在不同模型间有较大差异，而 Lists 的效果更为稳定

## 对论文写作的贡献

1. **格式偏差的核心引用**：为本文"格式特征影响偏好判断"提供最直接的实证支撑
2. **引用位置**：
   - Section 1.2.2（"Zhang 等人进一步发现，训练数据中仅不足 1% 的格式有偏样本便可导致奖励模型出现显著偏差[8]"）
   - Section 2.1（格式偏差综述段落）
3. **与本研究的对话**：本文对列表（list_counts）、粗体（bold_counts）、标题（header_counts）三类格式特征的独立效应分析，是对该文"格式偏差分类"工作的大样本实证延伸
4. **<1% 门槛**：这一发现揭示格式偏差的"高杠杆效应"，支撑本文关注格式偏差的研究必要性

## 可直接使用的表述

- "Zhang 等人专门研究了格式特征（列表、粗体、表情符号等）对基于 LLM 的偏好判断的影响，发现训练数据中仅不足 1% 的格式有偏样本便可导致奖励模型出现显著偏差，且不同格式之间存在交互效应[8]"
