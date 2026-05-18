# note_13 — Post-hoc Reward Calibration: A Case Study on Length Bias

## 基本信息

| 字段 | 内容 |
|------|------|
| 编号 | [12] |
| 标题 | Post-hoc Reward Calibration: A Case Study on Length Bias |
| 作者 | Zeyu Huang, Zihan Qiu, Zili Wang, Edoardo M. Ponti, Ivan Titov |
| 机构 | University of Edinburgh; Alibaba Group; INF Technology; University of Amsterdam |
| 发表会议 | ICLR 2025 |
| 关键词 | 后验奖励校准、长度偏见、局部加权回归、奖励模型去偏 |
| 相关性评级 | ★★★★★ |
| 论文位置 | D:\Files\MUC-QMJH\References\Papers\Post-hoc Reward Calibration A Case Study on Length Bias.pdf |

---

## 摘要直接提取（Abstract）

> Reinforcement Learning from Human Feedback aligns the outputs of Large Language Models with human values and preferences. Central to this process is the reward model (RM), which translates human feedback into training signals for optimising LLM behaviour. However, RMs can develop biases by exploiting spurious correlations in their training data, such as favouring outputs based on length or style rather than true quality. These biases can lead to incorrect output rankings, sub-optimal model evaluations, and the amplification of undesirable behaviours in LLMs' alignment. This paper addresses the challenge of correcting such biases without additional data and training, introducing the concept of Post-hoc Reward Calibration. We first propose to use the local average reward to estimate the bias term and, thus, remove it to approximate the underlying true reward. We then extend the approach to a more general and robust form with the Locally Weighted Regression. Focusing on the prevalent length bias, we validate our proposed approaches across three experimental settings, demonstrating consistent improvements: (1) a 3.11 average performance gain across 33 reward models on the RewardBench dataset; (2) improved agreement of RM produced rankings with GPT-4 evaluations and human preferences based on the AlpacaEval benchmark; and (3) improved Length-Controlled win rate (Dubois et al., 2024) of the RLHF process in multiple LLM–RM combinations. According to our experiments, our method is computationally efficient and generalisable to other types of bias and RMs, offering a scalable and robust solution for mitigating biases in LLM alignment and evaluation.

---

## 目录结构

1. Introduction（引言）
2. Related Works（相关工作）
   - 奖励模型
   - RLHF偏见缓解
3. Method（方法）
   - 3.1 问题陈述：奖励校准
   - 3.2 偏差估计（均匀平均法 / 局部加权回归法）
   - 3.3 应用与实践
4. Experiments（实验）
   - 4.1 RewardBench 基准测试
   - 4.2 AlpacaEval 排名相关性
   - 4.3 RLHF 对齐效果
5. Analysis（分析）
6. Conclusion（结论）

---

## 核心观点与方法

### 核心问题

奖励模型（RM）会通过学习训练数据中的虚假相关性（spurious correlations）产生偏见，最典型的是**长度偏见**：RM倾向于给更长的输出分配更高的奖励，而非真正质量更高的输出。这一偏见无需额外数据或重新训练即可被纠正。

### 理论框架：后验奖励校准

论文的核心假设是：**有偏奖励 = 真实奖励 + 偏差项（仅依赖于特定可测量特征c）**

$$r_\theta(x) = r^*(x) + b_\theta^c(c(x))$$

**奖励校准目标**：给定已评分的提示-响应对，找到接近真实奖励边际的校准后奖励边际：

$$\Delta_{r_\theta}(x_1, x_2) = \Delta_{r_\theta}(x_1, x_2) - (E[r_\theta(x)|c(x_1)] - E[r_\theta(x)|c(x_2)])$$

### 方法1：均匀平均法（Uniform Averaging）

对特征值相近的样本取平均奖励，估计该特征值对应的偏差项。

### 方法2：局部加权回归（Locally Weighted Regression，LWR）

使用带宽参数 f 定义用于回归的数据比例，对邻近数据点赋予更高权重，拟合加权线性回归来近似局部奖励期望。相比均匀平均法更通用、更鲁棒，能适应不均匀数据密度。

### 三大假设

1. **独立性**：真实奖励与偏差特征 c 相互独立
2. **充分密度**：特征函数 c 在其值域上分布足够密集
3. **Lipschitz连续性**：偏差项随特征值变化缓慢

### 实验关键结果

| 实验设置 | 结果 |
|---------|------|
| RewardBench（33个RM） | 平均性能提升 **+3.11分** |
| AlpacaEval排名 | 与GPT-4评估和人类偏好的一致性提升 |
| RLHF对齐（4个LLM-RM组合） | Length-Controlled胜率一致提升 |
| 计算效率 | 30万样本校准仅需约30秒（单CPU） |

### 方法创新点

- **无需额外数据**：在已打分样本上后处理，无需重新收集偏好数据
- **无需重新训练**：不干预偏好数据收集、RM训练或强化学习阶段
- **可推广到其他偏差**：包括Markdown格式特征、GPT-4评判模型等
- **偏差越强，校准效果越显著**

---

## 对本论文写作的贡献

1. **方法论对应**：为论文第三章（去偏方法）提供了"无需重训练"的后验去偏方案，与论文强调的"现有数据利用"思路一致。
2. **实验数据引用**：3.11分的RewardBench平均提升是具体可引用的量化证据。
3. **偏差分解框架**：奖励 = 真实质量 + 偏差项的分解公式，可用于论文方法论章节的数学表达。
4. **与[7]（LC-AlpacaEval）的关联**：本文在AlpacaEval验证中使用了[7]的LC胜率指标，两文互为支撑。
5. **计算可行性论证**：30秒处理30万样本说明去偏方法在实际中是可扩展的。

---

## 可直接使用的表述

- "Huang et al.（2025）提出后验奖励校准（Post-hoc Reward Calibration）框架，在不增加额外数据和训练的前提下，通过局部加权回归估计并剔除奖励模型中的长度偏差项，在33个奖励模型上平均取得3.11分的RewardBench性能提升。"
- "该研究将有偏奖励分解为真实奖励与仅依赖于可测量特征（如响应长度）的偏差项之和，为奖励模型去偏提供了形式化的数学基础。"
- "后验校准方法揭示了一个关键规律：RM偏差越强烈，校准效果越显著，这说明偏差本身是系统性且可被量化的。"
