# RULER: A Model-Agnostic Method to Control Generated Length for Large Language Models — 摘要

> 来源：`Papers/English/Ruler A Model-Agnostic Method to Control Generated Length for Large Language Models.pdf`
> 作者：Jiaming Li, Lei Zhang, Yunshui Li, Ziqiang Liu, Yuelin Bai, Run Luo, Longze Chen, Min Yang（Min Yang 为通讯作者）
> 机构：Shenzhen Institute of Advanced Technology, Chinese Academy of Sciences；University of Chinese Academy of Sciences
> 出处：arXiv:2409.18943v2 [cs.CL]，2024-10-01（venue 未确认）

## Abstract（原文逐字）

The instruction-following ability of large language models enables humans to interact with AI agents in a natural way. However, when required to generate responses of a specific length, large language models often struggle to meet users' needs due to their inherent difficulty in accurately perceiving numerical constraints. To explore the ability of large language models to control the length of generated responses, we propose the Target Length Generation Task (TLG) and design two metrics, Precise Match (PM) and Flexible Match (FM) to evaluate the model's performance in adhering to specified response lengths. Furthermore, we introduce a novel, model-agnostic approach called RULER, which employs Meta Length Tokens (MLTs) to enhance the instruction-following ability of large language models under length-constrained instructions. Specifically, RULER equips LLMs with the ability to generate responses of a specified length based on length constraints within the instructions. Moreover, RULER can automatically generate appropriate MLT when length constraints are not explicitly provided, demonstrating excellent versatility and generalization. Comprehensive experiments show the effectiveness of RULER across different LLMs on Target Length Generation Task, e.g., at All Level 27.97 average gain on PM, 29.57 average gain on FM. In addition, we conduct extensive ablation experiments to further substantiate the efficacy and generalization of RULER. Our code and data is available at https://github.com/Geaming2002/Ruler.

## 中文翻译

大语言模型（LLM）的指令遵循能力使人类能够以自然方式与 AI 智能体交互。然而，当被要求生成特定长度的回答时，大语言模型常常难以满足用户需求，因为它们在准确感知数值约束方面存在固有困难。为探究大语言模型控制生成回答长度的能力，我们提出目标长度生成任务（Target Length Generation Task, TLG），并设计两个指标——精确匹配（Precise Match, PM）与灵活匹配（Flexible Match, FM），用以评估模型遵守指定回答长度的表现。此外，我们提出一种新颖且模型无关的方法 RULER，它使用元长度标记（Meta Length Tokens, MLT）来增强大语言模型在带长度约束的指令下的指令遵循能力。具体而言，RULER 让 LLM 具备依据指令中的长度约束生成指定长度回答的能力。而且，当未显式给出长度约束时，RULER 能自动生成合适的 MLT，展现出优异的通用性与泛化性。大量实验表明 RULER 在不同 LLM 的目标长度生成任务上均有效，例如在 All Level 上 PM 平均提升 27.97、FM 平均提升 29.57。我们还开展了充分的消融实验，进一步证实 RULER 的有效性与泛化性。代码与数据见 https://github.com/Geaming2002/Ruler。

## 关键词

Target Length Generation Task (TLG)（目标长度生成任务）、Precise Match (PM)（精确匹配）、Flexible Match (FM)（灵活匹配）、Meta Length Token (MLT)（元长度标记）、RULER、instruction following（指令遵循）、length control（长度控制）、model-agnostic（模型无关）、DMLT、Arena-Hard-Auto

---

*说明：原文逐字取自 PDF 摘要（双栏排版，已按句子顺序重组，未改写）；标题中 RULER 的 R 在 PDF 中为 drop cap，文本层呈现为 "ULER"，此处按原文复原。中文翻译为便于阅读的机器翻译，引用请以英文为准。*
