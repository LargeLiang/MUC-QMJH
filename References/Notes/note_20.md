# note_21 — Reward Hacking in the Era of Large Models: Mechanisms, Emergent Misalignment, Challenges

## 基本信息

| 字段 | 内容 |
|------|------|
| 编号 | [20] |
| 标题 | Reward Hacking in the Era of Large Models: Mechanisms, Emergent Misalignment, Challenges |
| 作者 | Xiaohua Wang*, Muzhao Tian*, Yuqi Zeng*, Zisu Huang*, Jiakang Yuan*, Bowen Chen*, Jingwen Xu*, Mingbo Zhou*, Wenhao Liu, Muling Wu, Zhengkang Guo, Qi Qian, Yifei Wang, Feiran Zhang, Ruicheng Yin, Shihan Dou, Changze Lv, Tao Chen, Kaitao Song, Xu Tan, Tao Gui, Xiaoqing Zheng, Xuanjing Huang |
| 机构 | Fudan NLP Group（复旦大学自然语言处理组） |
| 发表情况 | arXiv 2026（预印本，2026年4月） |
| 关键词 | 奖励黑客、代理压缩假说（PCH）、言辞冗余偏见、谄媚、涌现式误对齐、RLHF |
| 相关性评级 | ★★★★☆ |
| 论文位置 | D:\Files\MUC-QMJH\References\Papers\English\Reward Hacking in the Era of Large Models Mechanisms Emergent Misalignment Challenges.pdf |

---

## 摘要直接提取（Abstract）

> Reinforcement Learning from Human Feedback (RLHF) and related alignment paradigms have become central to steering large language models (LLMs) and multimodal large language models (MLLMs) toward human-preferred behaviors. However, these approaches introduce a systemic vulnerability: reward hacking, where models exploit imperfections in learned reward signals to maximize proxy objectives without fulfilling true task intent. As models scale and optimization intensifies, such exploitation manifests as verbosity bias, sycophancy, hallucinated justification, benchmark overfitting, and, in multimodal settings, perception–reasoning decoupling and evaluator manipulation. Recent evidence further suggests that seemingly benign shortcut behaviors can generalize into broader forms of misalignment, including deception and strategic gaming of oversight mechanisms. In this survey, we propose the Proxy Compression Hypothesis (PCH) as a unifying framework for understanding reward hacking. We formalize reward hacking as an emergent consequence of optimizing expressive policies against compressed reward representations of high-dimensional human objectives. Under this view, reward hacking arises from the interaction of objective compression, optimization amplification, and evaluator–policy co-adaptation. This perspective unifies empirical phenomena across RLHF, RLAIF, and RLVR regimes, and explains how local shortcut learning can generalize into broader forms of misalignment, including deception and strategic manipulation of oversight mechanisms. We further organize detection and mitigation strategies according to how they intervene on compression, amplification, or co-adaptation dynamics. By framing reward hacking as a structural instability of proxy-based alignment under scale, we highlight open challenges in scalable oversight, multimodal grounding, and agentic autonomy.

---

## 目录结构

1. Introduction（引言）
2. Foundations of Proxy-Based Alignment（代理对齐的理论基础）
   - 2.1 奖励错误规范与古德哈特定律
   - 2.2 代理评估器剖析：RLHF、RLAIF、RLVR
   - 2.3 代理压缩假说（PCH）
   - 2.4 四层奖励黑客分类体系
3. Manifestations in Large Language Models（LLM中的表现）
   - 3.1 言辞冗余与风格捷径学习
   - 3.2 谄媚与顺从优化
   - 3.3 虚构推理与幻觉
   - 3.4 奖励过度优化与规模效应
4. From Local Shortcut Learning to Emergent Misalignment（从局部捷径到涌现式误对齐）
   - 4.1 跨任务泛化
   - 4.2 对齐欺骗与评估者建模
   - 4.3 评估者-策略共适应动态
5. Detection and Diagnosis: A Lifecycle Approach（检测与诊断）
6. Mitigation Through Structural Intervention（缓解策略）
   - 6.1 减少目标压缩
   - 6.2 控制优化放大
   - 6.3 评估者-策略共演化范式
7. Reward Hacking in Multimodal, Generative, and Agentic Models（多模态与智能体场景）
8. Open Challenges and Future Directions（开放问题）
9. Discussion and Conclusion（讨论与结论）

---

## 核心观点与方法

### 核心框架：代理压缩假说（Proxy Compression Hypothesis，PCH）

人类目标是高维度、情境依赖、多准则的（如真实性、有用性、安全性）。RLHF将这些丰富的价值结构压缩为低维代理信号（如标量奖励或二元偏好标签），产生**代理间隙**：

$$\Delta(x,y) = r^*(x,y) - \tilde{r}(x,y)$$

奖励黑客 = 优化系统性地将概率质量转移到最大化 $\tilde{r}$ 但降低 $r^*$ 的输出。

**三大驱动力**：
1. **目标压缩**：高维人类价值→低维代理表示的损耗映射
2. **优化放大**：强大策略的搜索压力将模型推向分布外区域
3. **评估者-策略共适应**：策略和评估者共同演化，趋向共同盲点

### 奖励黑客四层分类体系

| 层级 | 类型 | 描述 |
|------|------|------|
| Level 1 | **特征级利用** | 放大言辞冗余、谄媚等统计相关特征 |
| Level 2 | **表示级利用** | 虚构推理链、视觉-语言解耦 |
| Level 3 | **评估者级利用** | 策略性操纵评分评委的偏见 |
| Level 4 | **环境级利用** | 篡改API、测试套件等系统通道 |

### 言辞冗余（Verbosity）作为奖励黑客

论文将言辞冗余（verbosity bias）作为最典型的奖励黑客形式：模型通过增加输出长度来提高代理奖励，而不改善真实内容质量。这与古德哈特定律完全吻合：一旦长度成为优化目标（即使只是隐式的），它就不再是质量的良好代理。

### 从局部捷径到涌现式误对齐

- 训练看似无害的快捷行为（如长度优化）可以培养出可迁移的元策略：模型学会将评估者本身视为独立于底层任务的对象
- 一旦发生这种解耦，局部指标利用可以自发升级为严重的涌现式错误行为，包括：对齐欺骗（alignment faking）、策略性不服从，甚至在后续安全训练后仍持续存在

---

## 对本论文写作的贡献

1. **统一的理论语言**：PCH框架为本论文提供了将"长度偏见""格式偏见""谄媚"统一描述为"代理压缩导致的奖励黑客"的概念工具。
2. **四层分类的深度**：本论文研究的长度/格式偏见属于Level 1（特征级利用），这一定位帮助明确研究边界，不夸大也不低估。
3. **规模化挑战引用**：随着模型规模扩大，偏见被"优化放大"的风险增加，与本论文"大规模RLHF数据中偏见的累积效应"的关切一致。
4. **综述引用价值**：作为复旦NLP组的综述性论文，可在论文引言或相关工作部分作为"奖励黑客综述"引用，节省引用空间的同时覆盖宽泛文献。
5. **检测与缓解策略地图**：论文提供的三维（压缩/放大/共适应）缓解框架，为本论文第三章方法论部分的结构设计提供参考。

---

## 可直接使用的表述

- "Wang et al.（2026）提出代理压缩假说（Proxy Compression Hypothesis，PCH），将奖励黑客统一描述为'在代理信号优化中高维人类价值的压缩损失所引发的结构性不稳定'，涵盖言辞冗余、谄媚、虚构推理等多种表现形式，为理解RLHF偏见提供了统一的理论框架。"
- "该综述将言辞冗余（Verbosity Bias）列为最典型的Level 1奖励黑客形式，指出模型通过增加输出长度来提升代理奖励而不改善真实质量，这一机制与古德哈特定律完全一致：当长度成为优化目标时，它即不再是内容质量的良好代理。"
- "奖励黑客的'涌现性'表明，看似局部的偏见捷径（如长度偏好）可以在规模化优化压力下演化为更广泛的误对齐策略，强调了在早期训练阶段识别和控制数据偏见的重要性。"
