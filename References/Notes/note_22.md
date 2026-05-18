# note_23 — Disentangling Length Bias In Preference Learning Via Response-Conditioned Modeling

## 基本信息

| 字段 | 内容 |
|------|------|
| 编号 | [22] |
| 标题 | Disentangling Length Bias In Preference Learning Via Response-Conditioned Modeling |
| 作者 | Haotian Cai, Zongwei Liang, Tianyu Zhang, Qixin Tan, Xiaohong Liu, Xun Guo |
| 机构 | University of Science and Technology of China（中国科学技术大学，USTC） |
| 发表情况 | arXiv 2025（预印本） |
| 关键词 | 响应条件Bradley-Terry模型（Rc-BT）、长度偏见解耦、奖励模型、DPO去偏 |
| 相关性评级 | ★★★★★ |
| 论文位置 | D:\Files\MUC-QMJH\References\Papers\English\Disentangling Length Bias In Preference Learning Via Response-Conditioned Modeling.pdf |

---

## 摘要直接提取（Abstract）

> Preference learning—a key component of RLHF for aligning large language models (LLMs)—is significantly affected by length bias, where longer responses are incorrectly favored regardless of quality. We provide both theoretical and empirical evidence that this bias stems from misaligned length heuristics in training data: 59.78% of chosen responses in OpenAssistant are longer than rejected ones, indicating training data-level bias. Furthermore, even when semantic alignment is intentionally disrupted by matching prompts with semantically mismatched responses, reward models trained on length-biased datasets still achieve ≈60% accuracy, confirming that reward models capture length signals rather than true quality. To address these issues, we propose a Response-Conditioned Bradley-Terry (Rc-BT) model that disentangles quality-driven preferences from length-driven ones by conditioning reward computation on the response pair length distribution. This yields a bias-mitigated reward model (Rc-RM) and a new alignment algorithm (Rc-DPO) that outperform their respective baselines without adding inference overhead.

---

## 目录结构

1. Introduction（引言）
2. Related Work（相关工作）
3. Length Bias in Preference Learning: Theoretical and Empirical Evidence（长度偏见的理论与实证证据）
   - 3.1 数据集统计：OpenAssistant偏好分布
   - 3.2 语义失配实验：奖励模型精度测试
4. Response-Conditioned Bradley-Terry Model（Rc-BT模型）
   - 4.1 BT模型的长度偏见形式化
   - 4.2 响应条件化的理论推导
5. Rc-RM and Rc-DPO（算法设计）
6. Experiments（实验）
   - 评估数据集：Deval, Deval_e, Deval_r
7. Analysis（分析）
8. Conclusion（结论）

---

## 核心观点与方法

### 核心问题：偏好学习中的长度启发式

长度偏见不仅是标注噪声，而是**系统性地嵌入**在偏好数据集中。研究提供两类证据：

**数据集层面（OpenAssistant）**：
- 59.78%的"被选择"响应比"被拒绝"响应更长
- 说明长度在原始人类偏好标注中已经产生了系统性偏斜

**奖励模型层面（语义失配实验）**：
- 人为打乱prompt-response匹配关系（语义失配），奖励模型仍然达到**≈60%**精度
- 说明奖励模型学习的是长度信号而非真实语义质量

### 理论框架：Bradley-Terry模型的长度偏见形式化

标准BT模型中，响应 $y_w$ 被偏好于 $y_l$ 的概率为：

$$P(y_w \succ y_l | x) = \frac{\exp(r(x, y_w))}{\exp(r(x, y_w)) + \exp(r(x, y_l))}$$

若训练数据中 len($y_w$) > len($y_l$) 的频率过高，则奖励函数 $r$ 会隐式地将长度特征纳入优化目标。

### 方法：响应条件Bradley-Terry模型（Rc-BT）

**核心思想**：在奖励计算中条件化于响应对的长度分布，将质量驱动的偏好与长度驱动的偏好解耦。

**两个算法产出**：

| 算法 | 描述 |
|------|------|
| **Rc-RM** | 响应条件奖励模型，消除长度对奖励分配的直接影响 |
| **Rc-DPO** | 响应条件DPO对齐算法，在无需奖励模型的情况下直接去偏 |

**关键优势**：不增加推断开销（no inference overhead），即插即用。

### 评估数据集设计

| 数据集 | 含义 |
|--------|------|
| **Deval** | 标准评估集，标注与长度相关 |
| **Deval_e** | 长度平衡评估集（chosen与rejected长度差异被控制） |
| **Deval_r** | 反转评估集（有意反转长度关系），测试反事实鲁棒性 |

三套数据集的设计允许在不同长度条件下分解偏见来源。

---

## 对本论文写作的贡献

1. **数据集层面的直接证据**：59.78%的比率为本论文量化"LMArena数据集中较长响应被选择的频率"时提供了对比基准——本论文数据集中的类似统计可直接与该数字对照。
2. **语义失配实验设计思路**：利用"人为破坏语义关联后奖励模型仍达60%精度"的方法，为本论文中"验证偏见独立于内容质量"的实证检验提供了可借鉴的实验设计。
3. **BT模型长度偏见形式化**：提供了在Bradley-Terry框架内正式描述长度偏见的数学工具，与本论文使用Bradley-Terry框架分析偏好数据的方法一致。
4. **Deval/Deval_e/Deval_r设计**：分层评估数据集的设计，为本论文"分组检验不同长度条件下偏见效应"的方法论提供参考。
5. **即插即用特性**：强调去偏算法无需推断开销的实用性，与本论文强调"面向实践的偏见控制"研究定位一致。

---

## 可直接使用的表述

- "Cai et al.（2025）从理论和实证两个层面系统论证了偏好学习中的长度偏见：在OpenAssistant数据集中，59.78%的被选择响应比被拒绝响应更长；当语义匹配被人为破坏后，基于长度偏斜数据训练的奖励模型仍能达到≈60%精度，证明奖励模型捕获了长度信号而非真实质量。"
- "针对这一问题，该研究提出响应条件Bradley-Terry模型（Rc-BT），通过在奖励计算中条件化于响应对的长度分布，将质量驱动的偏好与长度驱动的偏好解耦，衍生出Rc-RM和Rc-DPO两种实用算法，在无额外推断开销的前提下有效缓解长度偏见。"
- "该工作揭示了长度偏见在偏好数据集层面的系统性存在：超过59%的被选择响应更长这一数据集统计特征，表明长度已作为隐式特征被人类标注者所利用，且这种偏见可以从数据集无缝传递到奖励模型和最终对齐结果。"
