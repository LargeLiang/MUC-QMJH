# note_24 — Rectifying Shortcut Behaviors in Preference-based Reward Learning (PRISM)

## 基本信息

| 字段 | 内容 |
|------|------|
| 编号 | [23] |
| 标题 | Rectifying Shortcut Behaviors in Preference-based Reward Learning |
| 作者 | Wenqian Ye, Guangtao Zheng, Aidong Zhang |
| 机构 | University of Virginia（弗吉尼亚大学）; Accenture |
| 发表情况 | NeurIPS 2025 |
| 关键词 | 核不变性理论、群不变核、随机特征图、快捷行为抑制、PRISM、OOD鲁棒性 |
| 相关性评级 | ★★★★★ |
| 论文位置 | D:\Files\MUC-QMJH\References\Papers\English\Rectifying Shortcut Behaviors in Preference-based Reward Learning.pdf |

---

## 摘要直接提取（Abstract）

> Reinforcement learning from human feedback (RLHF) is pivotal for aligning large language models (LLMs) with human values, yet it faces significant challenges in reward modeling due to shortcuts—models exploit spurious correlations like verbosity, sycophancy, and agreeable tone rather than true response quality. Inspired by kernel invariance theory, we propose PRISM (Preference Reward Invariant Shortcut Mitigation), a novel approach that leverages group-invariant kernels to enforce invariance to nuisance attributes. By approximating these kernels with random feature maps, PRISM introduces computationally tractable regularizers that can be seamlessly integrated into the reward learning objective, requiring only a small set of contrastive examples to specify shortcut behaviors. Our approach is theoretically grounded in learning theory and empirically validated on existing reward model benchmarks. Experiments show that PRISM improves out-of-distribution (OOD) reward model accuracy and reduces the prevalence of shortcut behaviors, demonstrating its effectiveness in improving the robustness and generalizability of reward models.

---

## 目录结构

1. Introduction（引言）
2. Related Work（相关工作）
   - 奖励建模的快捷行为
   - 核方法与不变性
3. Problem Formulation（问题定义）
   - 快捷行为的形式化定义
   - 目标：对"干扰属性"的群不变性
4. Method: PRISM（方法）
   - 4.1 核不变性理论（Kernel Invariance Theory）
   - 4.2 群不变核（Group-Invariant Kernels）
   - 4.3 随机特征图近似（Random Feature Maps）
   - 4.4 PRISM学习目标 = Bradley-Terry损失 + 核正则化项
5. Experiments（实验）
   - OOD奖励模型精度评估
   - 快捷行为（言辞冗余/谄媚/顺从语气）缓解效果
6. Analysis（分析）
7. Conclusion（结论）

---

## 核心观点与方法

### 核心问题：奖励学习中的快捷行为

RLHF中的奖励模型在训练时会利用**快捷行为**（shortcut behaviors）——即与响应质量相关但并不构成真实质量证据的表面特征：

| 快捷行为 | 描述 |
|---------|------|
| **言辞冗余（Verbosity）** | 偏好更长的响应 |
| **谄媚（Sycophancy）** | 偏好迎合用户期望的响应 |
| **顺从语气（Agreeable Tone）** | 偏好使用礼貌/顺从语言风格的响应 |

这些特征在训练数据中与高质量响应存在虚假相关，导致奖励模型在OOD场景下泛化性差。

### 理论基础：核不变性理论（Kernel Invariance Theory）

**核心思路**：若奖励函数对"干扰属性"（如响应长度）具有不变性，则它必须属于对这些属性保持不变的函数族——即**群不变核**（group-invariant kernels）诱导的再生核希尔伯特空间（RKHS）。

形式化：设 $G$ 为干扰属性变换群（如所有长度变换），奖励函数 $r$ 满足：

$$r(x,y) = r(x, g \cdot y), \quad \forall g \in G$$

**群不变核**：核函数 $k$ 满足 $k(y, y') = k(g \cdot y, g \cdot y')$ 对所有 $g \in G$ 成立。

### 方法：PRISM学习目标

由于精确计算群不变核在高维文本空间中计算代价极高，PRISM使用**随机特征图**（Random Feature Maps）对群不变核进行近似，将不变性约束转化为**可计算的正则化项**。

$$\mathcal{L}_{PRISM} = \mathcal{L}_{BT}(r_\phi) + \lambda \cdot \mathcal{R}_{kernel}(r_\phi)$$

其中：
- $\mathcal{L}_{BT}$：标准Bradley-Terry偏好学习损失
- $\mathcal{R}_{kernel}$：基于群不变核的正则化项，约束奖励模型对快捷特征的不变性
- 仅需少量**对比样本**（contrastive examples）来规范快捷行为的定义

**实用特性**：
- 正则化项可以无缝集成到任何标准奖励学习框架
- 只需少量额外对比样本即可指定要抑制的快捷行为类型
- 无需大规模反事实数据集

### 实验结果

- PRISM显著提高奖励模型的**OOD精度**（在分布外数据上的正确率）
- 在言辞冗余、谄媚、顺从语气三类快捷行为上均有效降低
- 理论保证来自学习理论（泛化界分析）

---

## 对本论文写作的贡献

1. **核不变性作为理论对齐目标**：为本论文"真正去偏的奖励模型应对无关特征保持不变"的直觉提供了严格的函数空间（RKHS）理论支撑——与其他论文的反事实不变性形成互补视角。
2. **快捷行为的三类分类**：言辞冗余/谄媚/顺从语气的分类与本论文"长度偏见+格式偏见"的研究框架直接对应，其中言辞冗余完全覆盖了本论文的长度偏见概念。
3. **对比样本而非大数据集的去偏方法**：说明偏见缓解不需要大规模反事实数据，少量精心设计的对比样本即可达到效果，为小规模实验设计提供理论可行性。
4. **NeurIPS 2025顶会背书**：作为NeurIPS 2025录用论文，为本论文引用最新研究进展提供了高质量学术依据。
5. **OOD评估框架**：PRISM对OOD场景下奖励模型性能的关注，与本论文讨论"跨任务类型（creative_writing/math/code等子集）的偏见稳健性"的视角相契合。

---

## 可直接使用的表述

- "Ye et al.（2025）提出PRISM（Preference Reward Invariant Shortcut Mitigation），以核不变性理论为基础，通过群不变核逼近和随机特征图将不变性约束转化为可计算的正则化项，有效抑制奖励模型对言辞冗余、谄媚和顺从语气等快捷行为的利用，显著提升了奖励模型在OOD场景下的泛化精度。"
- "该研究将快捷行为（shortcut behaviors）定义为奖励模型学习到的与质量存在虚假相关的表面特征，涵盖言辞冗余（verbosity）、谄媚（sycophancy）和顺从语气（agreeable tone）三类，与本文所研究的长度偏见和格式偏见在机制上高度吻合。"
- "PRISM的正则化目标函数 $\mathcal{L}_{PRISM} = \mathcal{L}_{BT} + \lambda\mathcal{R}_{kernel}$ 兼容任何标准奖励学习框架，且仅需少量对比样本即可规范需抑制的快捷行为，展现了去偏技术在大规模偏好学习实践中的可行性。"
