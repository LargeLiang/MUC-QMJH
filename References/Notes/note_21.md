# note_22 — Mitigating Length Bias in RLHF through a Causal Lens

## 基本信息

| 字段 | 内容 |
|------|------|
| 编号 | [21] |
| 标题 | Mitigating Length Bias in RLHF through a Causal Lens |
| 作者 | Yanning Jiang, Tianyi Liang, Jianxin Chang, Bofang Li, Jia-Chen Gu |
| 机构 | Seoul National University（首尔国立大学） |
| 发表情况 | arXiv 2024（预印本） |
| 关键词 | 因果层次理论、反事实数据增强、长度偏见缓解、flip ratio诊断指标、奖励模型 |
| 相关性评级 | ★★★★★ |
| 论文位置 | D:\Files\MUC-QMJH\References\Papers\English\Mitigating Length Bias in RLHF through a Causal Lens.pdf |

---

## 摘要直接提取（Abstract）

> Reinforcement learning from human feedback (RLHF) has become an increasingly popular technique for aligning large language models (LLMs). The critical step in this approach is training a reward model from human preference data. However, human annotators can be biased by factors beyond quality, such as response length. Such annotation bias results in the training of length-biased reward models, where longer responses are disproportionately rewarded. To mitigate this issue, we propose a causal-based method that incorporates Pearl's causal hierarchy into reward modeling to disentangle the actual quality of an LLM's response from length-related features. Specifically, we augment the preference training data with two types of counterfactual examples: (1) length-divergent pairs (same content, varying length) and (2) content-divergent pairs (fixed length, varying content). This augmentation helps the reward model learn to separate content quality from length. We further introduce a flip ratio F metric to diagnose the severity of length bias in a given reward model. Experiments show that our method effectively reduces length bias while preserving content quality.

---

## 目录结构

1. Introduction（引言）
2. Background（背景）
   - 2.1 RLHF与奖励模型
   - 2.2 Pearl的因果层次理论
3. Method（方法）
   - 3.1 诊断指标：flip ratio F
   - 3.2 反事实数据增强：length-divergent pairs
   - 3.3 反事实数据增强：content-divergent pairs
   - 3.4 三阶段偏见缓解流程
4. Experiments（实验）
   - 4.1 奖励模型长度偏见评估
   - 4.2 RLHF下游任务评估
5. Analysis（分析）
6. Conclusion（结论）

---

## 核心观点与方法

### 核心问题：奖励模型中的长度偏见

人类标注者在评估LLM响应时受到响应长度的影响，导致训练出的奖励模型将长度本身（而非内容质量）作为偏好的预测因子。更长的响应被不成比例地奖励，产生"言辞冗余"（verbosity）激励。

### 理论基础：Pearl的因果层次理论（Causal Hierarchy）

采用Pearl因果层次（三级：关联/干预/反事实）作为方法论基础：

| 层次 | 操作 | 含义 |
|------|------|------|
| 关联（Association） | 观察 | P(reward \| length) |
| 干预（Intervention） | do(length=l) | 强制设定长度，观察奖励变化 |
| **反事实（Counterfactual）** | **T(z)** | **若长度为z'，奖励会如何？** |

目标：在**反事实**层次使奖励模型对长度保持不变性。

### 两类反事实数据增强

**1. 长度分歧对（Length-Divergent Pairs）**
- 同一内容，不同长度
- 目的：让模型学会"相同内容不因长度不同而获得不同奖励"

**2. 内容分歧对（Content-Divergent Pairs）**
- 不同内容，固定长度
- 目的：让模型学会"在控制长度的情况下，基于内容质量区分响应"

### 诊断指标：Flip Ratio（F）

Flip Ratio定义为在评估集上，奖励模型因响应长度变化而翻转偏好预测的比例：

$$F = \frac{\text{长度改变后偏好翻转的对数}}{\text{总评估对数}}$$

F值越高，说明奖励模型的长度偏见越严重。该指标为诊断任意奖励模型的长度偏见程度提供了简洁的工具。

### 三阶段偏见缓解流程

1. **阶段一**：计算Flip Ratio诊断现有奖励模型的偏见程度
2. **阶段二**：生成两类反事实数据并与原始训练数据混合
3. **阶段三**：在增强数据集上重新训练奖励模型，验证F值下降

---

## 对本论文写作的贡献

1. **Pearl因果层次作为理论工具**：将"干预"和"反事实"操作引入长度偏见分析，为本论文中控制虚假变量（如长度）的策略提供更深层次的因果理论支持。
2. **Flip Ratio作为偏见度量方法**：一种与传统相关性分析互补的、操控性的（interventional）偏见诊断指标，可在本论文方法论部分引用以拓宽偏见量化的视角。
3. **内容与长度的正交化**：通过"固定内容改变长度"和"固定长度改变内容"两种实验操作，实证验证了长度偏见的独立性（不依赖于内容质量），与本论文通过控制变量分析"纯长度效应"的方法高度互补。
4. **奖励模型视角**：从奖励模型训练角度切入长度偏见问题，与本论文从"人类偏好数据集"角度切入形成上下游的研究链条——数据集中的偏见进入奖励模型，再影响RLHF对齐结果。
5. **反事实增强思路**：为理解"为什么简单增加数据量无法消除长度偏见"提供了实验证据。

---

## 可直接使用的表述

- "Jiang et al.（2024）以Pearl因果层次为框架，通过构造长度分歧对与内容分歧对两类反事实样本增强训练数据，系统性地降低了奖励模型对响应长度的敏感性，并引入Flip Ratio（F）作为诊断奖励模型长度偏见程度的量化指标。"
- "该研究从因果干预视角证明，长度偏见是独立于内容质量存在的一种系统性偏差：在保持内容不变的情况下单独操纵长度，即可使现有奖励模型翻转偏好判断，验证了奖励模型对长度特征的直接利用。"
- "Flip Ratio作为干预性诊断指标，补充了传统相关性分析的不足，使得对奖励模型中长度偏见的量化从'观察是否相关'升级到'干预后偏好是否翻转'，更接近偏见的因果定义。"
