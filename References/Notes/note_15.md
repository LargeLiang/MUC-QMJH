# note_16 — RULER: A Model-Agnostic Method to Control Generated Length for Large Language Models

## 基本信息

| 字段 | 内容 |
|------|------|
| 编号 | [15] |
| 标题 | RULER: A Model-Agnostic Method to Control Generated Length for Large Language Models |
| 作者 | Jiaming Li, Lei Zhang, Yunshui Li, Ziqiang Liu, Yuelin Bai, Run Luo, Longze Chen, Min Yang |
| 机构 | Shenzhen Institute of Advanced Technology (SIAT), Chinese Academy of Sciences; University of Chinese Academy of Sciences |
| 发表情况 | arXiv 2024 |
| 关键词 | 长度控制、Meta Length Tokens（MLT）、目标长度生成任务（TLG）、精确匹配 / 灵活匹配 |
| 相关性评级 | ★★★★☆ |
| 论文位置 | D:\Files\MUC-QMJH\References\Papers\Ruler A Model-Agnostic Method to Control Generated Length for Large Language Models.pdf |

---

## 摘要直接提取（Abstract）

> The instruction-following ability of large language models enables humans to interact with AI agents in a natural way. However, when required to generate responses of a specific length, large language models often struggle to meet users' needs due to their inherent difficulty in accurately perceiving numerical constraints. To explore the ability of large language models to control the length of generated responses, we propose the Target Length Generation Task (TLG) and design two metrics, Precise Match (PM) and Flexible Match (FM) to evaluate the model's performance in adhering to specified response lengths. Furthermore, we introduce a novel, model-agnostic approach called RULER, which employs Meta Length Tokens (MLTs) to enhance the instruction-following ability of large language models under length-constrained instructions. Specifically, RULER equips LLMs with the ability to generate responses of a specified length based on length constraints within the instructions. Moreover, RULER can automatically generate appropriate MLT when length constraints are not explicitly provided, demonstrating excellent versatility and generalization. Comprehensive experiments show the effectiveness of RULER across different LLMs on Target Length Generation Task, e.g., at All Level 27.97 average gain on PM, 29.57 average gain on FM.

---

## 目录结构

1. Introduction（引言）
2. Related Works（相关工作）
   - 2.1 大语言模型
   - 2.2 指令跟随
   - 2.3 元令牌（Meta Token）
3. Can LLMs Accurately Generate with Target Length?（LLM能精确生成目标长度的文本吗？）
   - 3.1 目标长度生成任务（TLG）设计
   - 3.2 实验设置
   - 3.3 结果分析
4. RULER Method（RULER 方法）
   - MLT 设计与训练
5. Experiments（实验）
6. Conclusion（结论）

---

## 核心观点与方法

### 核心问题：LLM无法精确控制输出长度

LLM在被要求"用30个词说明如何做蛋糕"时，生成的响应往往远超目标长度。现有模型普遍缺乏对数值约束（如"30个词"）的精确感知能力，这一缺陷在实际部署中会造成严重的用户体验问题。

### 目标长度生成任务（Target Length Generation Task，TLG）

论文首次定义了TLG任务，将长度控制能力作为独立能力维度进行系统评估：

| 层级 | 目标长度 | PM范围 | FM范围 |
|------|---------|--------|--------|
| Level 0 | 10, 30, 50, 80词 | ±10词 | (0,20], (20,40]... |
| Level 1 | 150, 300, 500, 700词 | ±20词（150）/ ±50, ±70词 | (100,200]... |
| Level 2 | >800词 | (800,∞) | (800,∞) |

**两个评估指标**：
- **PM（Precise Match，精确匹配）**：响应长度严格落在目标长度的容差范围内
- **FM（Flexible Match，灵活匹配）**：响应长度落在更宽的容差区间

### 方法：RULER + Meta Length Tokens（MLT）

- **MLT**：特殊设计的令牌，用于编码目标长度信息
- **端到端训练**：LLM学习在给定目标长度时生成MLT，再生成符合长度的响应
- **无显式长度约束时**：RULER先自动生成适当的MLT，再生成响应
- **模型无关**：RULER可应用于任意LLM而无需修改基础架构

### 主要实验结果

**现有LLM长度控制表现**（TLG数据集，2000条样本）：

| 模型 | PM（All Level） | FM（All Level） |
|------|---------------|---------------|
| GPT-4-turbo | 61.35 | 77.35 |
| GPT-4o | 57.75 | 74.30 |
| Claude-3.5-sonnet | 61.65 | 79.55 |
| Llama3-8B | 29.35 | 44.25 |
| Llama3-70B | 46.55 | 63.75 |

→ 即使最先进的模型，PM也仅约60%，说明**长度控制是LLM普遍的短板**。

**RULER的提升**：

| 指标 | 平均提升 |
|------|---------|
| PM（All Level） | **+27.97** |
| FM（All Level） | **+29.57** |

---

## 对本论文写作的贡献

1. **反向证明长度偏见的合理性**：如果LLM本身难以精确控制输出长度，那么人类评估者在看到不同长度的响应时产生偏见，部分原因在于无法分离"长度"与"能力"两个维度。
2. **长度感知能力的可训练性**：RULER证明MLT可以教会模型精确匹配目标长度，为"通过训练数据控制输出长度"的偏见缓解思路提供了技术支撑。
3. **量化数据引用**：27.97/29.57的提升数据，以及现有LLM PM仅60%左右的基线，可用于论文第三章讨论"长度偏见的根源之一是LLM本身的长度感知局限"。
4. **与研究数据集的关联**：LMArena数据中的长度偏见，部分可归因于LLM在长度控制上的固有缺陷。

---

## 可直接使用的表述

- "Li et al.（2024）提出RULER方法，通过Meta Length Tokens（MLT）使LLM精确跟随长度约束，在目标长度生成任务上平均分别提升PM和FM指标27.97和29.57，揭示了现有LLM在长度感知上的固有局限。"
- "即使是最先进的GPT-4-turbo，在精确长度生成任务（TLG）上的精确匹配率也仅为61.35%，说明LLM普遍缺乏准确的数值长度感知能力，这为理解长度偏见的形成提供了模型侧的底层解释。"
- "RULER方法证明，通过引入专门的长度控制令牌（MLT）进行端到端训练，可以大幅提升LLM对长度约束的遵从能力，从而减少因长度不可控带来的评估偏差。"
