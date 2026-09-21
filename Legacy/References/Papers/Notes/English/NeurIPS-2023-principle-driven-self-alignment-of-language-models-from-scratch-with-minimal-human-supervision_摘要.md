# Principle-Driven Self-Alignment of Language Models from Scratch with Minimal Human Supervision — 摘要

> 来源：`Papers/English/NeurIPS-2023-principle-driven-self-alignment-of-language-models-from-scratch-with-minimal-human-supervision.pdf`
> 作者：Zhiqing Sun, Yikang Shen, Qinhong Zhou, Hongxin Zhang, Zhenfang Chen, David Cox, Yiming Yang, Chuang Gan
> 机构：Language Technologies Institute, CMU；MIT-IBM Watson AI Lab, IBM Research；UMass Amherst
> 出处：37th Conference on Neural Information Processing Systems (NeurIPS 2023)（arXiv 编号未在文本中出现，未确认）

## Abstract（原文逐字）

Recent AI-assistant agents, such as ChatGPT, predominantly rely on supervised fine-tuning (SFT) with human annotations and reinforcement learning from human feedback (RLHF) to align the output of large language models (LLMs) with human intentions, ensuring they are helpful, ethical, and reliable. However, this dependence can significantly constrain the true potential of AI-assistant agents due to the high cost of obtaining human supervision and the related issues on quality, reliability, diversity, self-consistency, and undesirable biases. To address these challenges, we propose a novel approach called SELF-ALIGN, which combines principle-driven reasoning and the generative power of LLMs for the self-alignment of the AI agents with minimal human supervision. Applying SELF-ALIGN to the LLaMA-65b base language model, we develop an AI assistant named Dromedary . With fewer than 300 lines of human annotations (including < 200 seed prompts, 16 generic principles, and 5 exemplars for in-context learning), Dromedary significantly surpasses the performance of several state-of-the-art AI systems, including Text-Davinci-003 and Alpaca, on benchmark datasets with various settings. We have open-sourced the code, LoRA weights of Dromedary, and our synthetic training data to encourage further research into aligning LLM-based AI agents with enhanced supervision efficiency, reduced biases, and improved controllability.

## 中文翻译

近来的 AI 助手智能体（如 ChatGPT）主要依赖带人工标注的监督微调（SFT）与基于人类反馈的强化学习（RLHF）来让大语言模型（LLM）的输出与人类意图对齐，确保其有帮助、合乎伦理且可靠。然而，这种依赖会显著限制 AI 助手智能体的真正潜力，原因在于获取人类监督成本高昂，以及由此带来的质量、可靠性、多样性、自洽性与不良偏置等问题。为应对这些挑战，我们提出一种新方法 SELF-ALIGN，它把原则驱动的推理与 LLM 的生成能力结合起来，以极少的人类监督实现 AI 智能体的自我对齐。将 SELF-ALIGN 应用于 LLaMA-65b 基座语言模型，我们开发出名为 Dromedary 的 AI 助手。仅用少于 300 行人工标注（包括 < 200 条种子提示、16 条通用原则，以及 5 个用于 in-context learning 的示例），Dromedary 在多种设定的基准数据集上显著超越若干最先进的 AI 系统，包括 Text-Davinci-003 与 Alpaca。我们已开源代码、Dromedary 的 LoRA 权重以及合成训练数据，以鼓励进一步研究如何在提升监督效率、减少偏置与改善可控性方面对齐基于 LLM 的 AI 智能体。

## 关键词

SELF-ALIGN、principle-driven self-alignment（原则驱动的自我对齐）、Dromedary、self-instruct / topic-guided red-teaming（自指示 / 主题引导红队）、principle engraving（原则刻录）、verbose cloning（冗长克隆）、context distillation（上下文蒸馏）、verbose tax（冗长税）、RLHF / SFT / Constitutional AI、LLaMA-65b

---

*说明：原文逐字取自 PDF 摘要（单栏排版，未改写）；"Dromedary ." 处的空格为 PDF 中脚注标记导致的抽取呈现，未作增删。中文翻译为便于阅读的机器翻译，引用请以英文为准。*
