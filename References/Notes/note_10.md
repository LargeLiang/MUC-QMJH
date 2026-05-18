# note_11 — Ouyang et al.（2022）

## 基本信息

| 项目 | 内容 |
|------|------|
| 标题 | Training Language Models to Follow Instructions with Human Feedback |
| 作者 | Ouyang Long, Wu Jeffrey, Jiang Xu, Almeida Diogo, Wainwright Carroll, Mishkin Pamela, Zhang Chong, Agarwal Sandhini, Slama Katarina, Ray Alex, et al. |
| 来源 | NeurIPS 2022（arXiv:2203.02155，OpenAI） |
| 文献编号 | [10] |
| 相关性评级 | ★★★★★ 奠基性文献（InstructGPT / RLHF） |

## 摘要（直接提取）

> Making language models bigger does not inherently make them better at following a user's intent. Large language models can generate outputs that are untruthful, toxic, or simply not helpful to the user. In this paper, we show an avenue for aligning language models with user intent on a wide range of tasks by fine-tuning with human feedback. Starting from GPT-3, we collect a dataset of labeler demonstrations of the desired model behavior, and use this to fine-tune GPT-3 using supervised learning. We then collect a dataset of rankings of model outputs, train a reward model on this data, and use this reward model to further fine-tune our supervised learning fine-tuned model using PPO. We call the resulting models **InstructGPT**. We find that a 1.3B parameter InstructGPT model is preferred over a 175B GPT-3 model by human labelers, despite having 100x fewer parameters.

## 目录结构

1. Introduction — 对齐问题与研究动机
2. Related Work — 相关工作
3. Methods — RLHF 三阶段训练方法
   - 3.1 Supervised Fine-Tuning (SFT)
   - 3.2 Reward Modeling (RM)
   - 3.3 Reinforcement Learning (PPO)
4. Results — 实验结果
   - 4.1 Human Preference Evaluation
   - 4.2 Safety Evaluations
5. Discussion — 局限性与未来方向
6. Conclusion

## 核心观点与方法

### 主要论点
1. 大模型的"更大"不等于"更符合用户意图"——需要显式对齐
2. **RLHF 三阶段范式**（SFT → RM → PPO）是将人类偏好纳入模型训练的实践路径
3. 1.3B 参数的 InstructGPT 优于 175B 参数的 GPT-3，证明对齐质量比参数规模更重要

### 方法（RLHF Pipeline）
- **Stage 1 — SFT**：收集人类演示数据，监督微调 GPT-3
- **Stage 2 — Reward Modeling**：收集模型输出的人类排名，训练奖励模型（RM）
- **Stage 3 — PPO-ptx**：用奖励模型作为强化学习环境，用 PPO 算法优化策略模型
- 标注者评估维度：帮助性（helpful）、无害性（harmless）、诚实性（honest）

### 关键数据
- 1.3B InstructGPT vs. 175B GPT-3：人类评估者 **85% 偏好 InstructGPT**
- SFT 数据量：13,000 条人类演示
- RM 排名数据：33,000 次比较

## 对论文写作的贡献

1. **奠基性引用**：RLHF 范式的开创性论文，是整个研究领域的共同基础
2. **引用位置**：
   - Section 1.1（"Ouyang 等人通过 RLHF 提出 InstructGPT，奠定了人类反馈对齐的基础范式[11]"）
   - Section 2.1（RLHF 背景介绍）
3. **偏差根源**：RLHF 三阶段中，RM 阶段是偏差（长度/格式）进入对齐系统的关键节点，本文的研究正是在这一节点上展开

## 可直接使用的表述

- "Ouyang 等人提出的 InstructGPT 奠定了 RLHF 的基础范式：通过'监督微调→奖励建模→强化学习优化'三阶段流程，将人类偏好融入大语言模型训练[11]"
