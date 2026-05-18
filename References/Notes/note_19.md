# note_20 — Beyond Reward Hacking: Causal Rewards for Large Language Model Alignment

## 基本信息

| 字段 | 内容 |
|------|------|
| 编号 | [19] |
| 标题 | Beyond Reward Hacking: Causal Rewards for Large Language Model Alignment |
| 作者 | Chaoqi Wang*, Zhuokai Zhao*, Yibo Jiang*, Zhaorun Chen*, Chen Zhu, Yuxin Chen, Jiayi Liu, Lizhu Zhang, Xiangjun Fan, Hao Ma, Sinong Wang |
| 机构 | Meta; University of Chicago |
| 发表情况 | arXiv 2025（预印本，2025年6月） |
| 关键词 | 因果奖励模型（CRM）、反事实不变性、奖励黑客、虚假相关、长度偏见缓解 |
| 相关性评级 | ★★★★★ |
| 论文位置 | D:\Files\MUC-QMJH\References\Papers\English\Beyond Reward Hacking Causal Rewards for Large Language Model Alignment.pdf |

---

## 摘要直接提取（Abstract）

> Recent advances in large language models (LLMs) have demonstrated significant progress in performing complex tasks. While Reinforcement Learning from Human Feedback (RLHF) has been effective in aligning LLMs with human preferences, it is susceptible to spurious correlations in reward modeling. Consequently, it often introduces biases—such as length bias, sycophancy, conceptual bias, and discrimination—that hinder the model's ability to capture true causal relationships. To address this, we propose a novel causal reward modeling approach that integrates causality to mitigate these spurious correlations. Our method enforces counterfactual invariance, ensuring reward predictions remain consistent when irrelevant variables are altered. Through experiments on both synthetic and real-world datasets, we show that our approach mitigates various types of spurious correlations effectively, resulting in more reliable and fair alignment of LLMs with human preferences. As a drop-in enhancement to the existing RLHF workflow, our causal reward modeling provides a practical way to improve the trustworthiness and fairness of LLM finetuning.

---

## 目录结构

1. Introduction（引言）
2. Related Works（相关工作）
   - 2.1 奖励黑客与虚假相关
   - 2.2 缓解虚假相关（现有方法综述）
3. Preliminaries（基础知识）
   - 3.1 RLHF三阶段流程
   - 3.2 反事实不变性
   - 3.3 因果分解（T → TZ⊥, TZ∧L, TL⊥）
4. Method（方法）
   - 因果奖励模型（CRM）设计
   - 因果正则化
5. Experiments（实验）
   - 合成数据集 + 真实世界数据集
   - 长度偏见、谄媚偏见、概念偏见、歧视偏见的缓解效果
6. Conclusion（结论）

---

## 核心观点与方法

### 核心问题：奖励模型中的不可减少误差

奖励模型的总误差 = 可减少误差（数据不足、模型容量限制）+ **不可减少误差**（训练数据中的虚假相关）。

**关键认识**：增加数据量无法消除虚假相关带来的偏见，甚至可能加剧奖励黑客行为。因此必须从**因果机制**层面解决问题。

### 理论框架：反事实不变性（Counterfactual Invariance）

**核心假设**：理想的去偏奖励模型应对虚假因子 Z 的变化保持不变。

**形式化定义**：奖励模型 r 对 Z 具有反事实不变性，当且仅当 r(T(z)) = r(T(z')) 对所有 z, z' 成立。

### 因果分解（Causal Decomposition）

提示-响应对 T 可分解为三个潜在成分：

| 成分 | 含义 |
|------|------|
| **T_{Z,⊥}**（独立于Z的成分） | 与虚假因子无关的真实内容质量 |
| **T_{Z∧L}**（Z和L共同影响的成分） | 被虚假因子Z和偏好标签L共同影响的部分 |
| **T_{L,⊥}**（不直接影响L的成分） | 不直接影响人类偏好的部分 |

**目标**：构建仅依赖 T_{Z,⊥} 的奖励模型，消除虚假路径 Z→L 的直接影响。

### 方法：因果奖励模型（CRM）

- 将因果正则化直接嵌入奖励建模训练过程
- 通过可观测的因果图签名（causal graph signatures）推导正则化约束，无需反事实样本
- 作为RLHF工作流的"即插即用"增强方案

### 实验覆盖的四类偏见

| 偏见类型 | 描述 |
|---------|------|
| **长度偏见** | 奖励模型偏好更长响应而非更高质量响应 |
| **谄媚偏见** | 奖励模型偏好迎合用户观点的响应而非真实响应 |
| **概念偏见** | 模型将特定文本概念（如"食物"）与奖励关联 |
| **歧视偏见** | 模型对特定人口群体的内容产生系统性偏好 |

CRM在合成和真实世界数据集上均有效缓解以上四类偏见。

---

## 对本论文写作的贡献

1. **统一的偏见缓解框架**：将长度偏见、谄媚偏见等置于因果框架下统一处理，与本论文将"长度偏见"和"格式偏见"视为同一类"虚假相关"问题的视角高度一致。
2. **因果图分解工具**：T→T_{Z⊥}、T_{Z∧L}、T_{L⊥}的分解框架，为本论文在方法论章节引入"控制虚假变量"思路提供了严格的数学语言。
3. **反事实不变性作为去偏准则**：为本论文讨论"什么是真正去偏的奖励模型"提供了规范化的理论标准。
4. **即插即用特性**：CRM作为RLHF的drop-in增强，说明偏见缓解不需要从头重设计对齐流程，与本论文强调"现有数据利用"的研究边界一致。
5. **四类偏见的整合视角**：将长度、谄媚、概念、歧视偏见统一纳入"虚假相关"框架，支持本论文中"多种偏见具有共同因果根源"的论点。

---

## 可直接使用的表述

- "Wang et al.（2025）提出因果奖励建模方法（CRM），通过强制反事实不变性——即奖励预测在无关变量（如响应长度）发生变化时保持不变——系统性地缓解了包括长度偏见、谄媚偏见、概念偏见和歧视偏见在内的多类虚假相关问题。"
- "该研究指出，奖励模型中由虚假相关引起的'不可减少误差'无法通过增加数据量解决，只能通过嵌入因果约束的训练机制加以克服，这为研究人类偏好数据中系统性偏见的传播机制提供了重要理论依据。"
- "CRM对提示-响应对T进行因果分解（T→T_{Z⊥}、T_{Z∧L}、T_{L⊥}），目标是训练仅依赖独立于虚假因子Z的成分T_{Z⊥}的奖励模型，从根本上切断了虚假特征（如响应长度）对奖励分配的直接影响路径。"
