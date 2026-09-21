# Principle-Driven Self-Alignment of Language Models from Scratch with Minimal Human Supervision

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 标题 | Principle-Driven Self-Alignment of Language Models from Scratch with Minimal Human Supervision |
| 作者 | Zhiqing Sun, Yikang Shen, Qinhong Zhou, Hongxin Zhang, Zhenfang Chen, David Cox, Yiming Yang, Chuang Gan（正文标注 Correspondence: zhiqings@cs.cmu.edu） |
| 机构 | Language Technologies Institute, CMU；MIT-IBM Watson AI Lab, IBM Research；UMass Amherst |
| 出处 | 37th Conference on Neural Information Processing Systems (NeurIPS 2023)（正文页脚标注）；arXiv 编号未在文本中出现，未确认 |
| 语言 | 英文 |
| 与课题相关度 | ★★☆☆☆（提供 "verbose tax"（冗长反而损害部分基准）与"人类标注本身有质量/偏置问题"两条可引用旁证，但主题是对齐方法本身，不涉及长度-偏好关联） |
| 原文位置 | `Papers/English/NeurIPS-2023-principle-driven-self-alignment-of-language-models-from-scratch-with-minimal-human-supervision.pdf` |

## 一、三句话概括

1. 论文提出 SELF-ALIGN，用极少量人工监督（少于 300 行标注：195 条种子提示、16 条通用原则、5 个 in-context 示例）让语言模型自我对齐，并在 LLaMA-65b 上训练出 AI 助手 Dromedary。
2. 方法含四个阶段：(Topic-Guided Red-Teaming) Self-Instruct 生成合成指令、Principle-Driven Self-Alignment 由原则驱动生成回答、Principle Engraving 在剪除原则与示例后微调原模型、Verbose Cloning 用 context distillation 让回答更详尽。
3. 评测显示 Dromedary 在 TruthfulQA MC1（69）与 BIG-bench HHH Eval 上超过 LLaMA-65B、Alpaca-65B 等开源模型，但作者发现 Verbose Cloning 在提升生成质量的同时损害了多个多选题基准的表现，并称之为 verbose tax。

## 二、摘要

**原文（逐字）**

> Recent AI-assistant agents, such as ChatGPT, predominantly rely on supervised fine-tuning (SFT) with human annotations and reinforcement learning from human feedback (RLHF) to align the output of large language models (LLMs) with human intentions, ensuring they are helpful, ethical, and reliable. However, this dependence can significantly constrain the true potential of AI-assistant agents due to the high cost of obtaining human supervision and the related issues on quality, reliability, diversity, self-consistency, and undesirable biases. To address these challenges, we propose a novel approach called SELF-ALIGN, which combines principle-driven reasoning and the generative power of LLMs for the self-alignment of the AI agents with minimal human supervision. Applying SELF-ALIGN to the LLaMA-65b base language model, we develop an AI assistant named Dromedary . With fewer than 300 lines of human annotations (including < 200 seed prompts, 16 generic principles, and 5 exemplars for in-context learning), Dromedary significantly surpasses the performance of several state-of-the-art AI systems, including Text-Davinci-003 and Alpaca, on benchmark datasets with various settings. We have open-sourced the code, LoRA weights of Dromedary, and our synthetic training data to encourage further research into aligning LLM-based AI agents with enhanced supervision efficiency, reduced biases, and improved controllability.

**中文翻译**

> 近来的 AI 助手智能体（如 ChatGPT）主要依赖带人工标注的监督微调（SFT）与基于人类反馈的强化学习（RLHF）来让大语言模型（LLM）的输出与人类意图对齐，确保其有帮助、合乎伦理且可靠。然而，这种依赖会显著限制 AI 助手智能体的真正潜力，原因在于获取人类监督成本高昂，以及由此带来的质量、可靠性、多样性、自洽性与不良偏置等问题。为应对这些挑战，我们提出一种新方法 SELF-ALIGN，它把原则驱动的推理与 LLM 的生成能力结合起来，以极少的人类监督实现 AI 智能体的自我对齐。将 SELF-ALIGN 应用于 LLaMA-65b 基座语言模型，我们开发出名为 Dromedary 的 AI 助手。仅用少于 300 行人工标注（包括 < 200 条种子提示、16 条通用原则，以及 5 个用于 in-context learning 的示例），Dromedary 在多种设定的基准数据集上显著超越若干最先进的 AI 系统，包括 Text-Davinci-003 与 Alpaca。我们已开源代码、Dromedary 的 LoRA 权重以及合成训练数据，以鼓励进一步研究如何在提升监督效率、减少偏置与改善可控性方面对齐基于 LLM 的 AI 智能体。

（完整摘要另见 `NeurIPS-2023-principle-driven-self-alignment-of-language-models-from-scratch-with-minimal-human-supervision_摘要.md`）

## 三、章节结构与内容

| 位置 | 标题（原文） | 内容说明 |
| --- | --- | --- |
| 1 | Introduction | 指出主流对齐依赖 SFT + RLHF 的昂贵人工监督，且标注存在质量、可靠性、多样性、自洽性与不良偏置等问题；提出 SELF-ALIGN 与四阶段流程，并以 Table 1 对比 77K（InstructGPT）等监督量与本文的 "< 300 lines" |
| 2 | Related Works | 综述章。无编号小节 AI Alignment（RLHF、Constitutional AI 与 SELF-ALIGN 的三点区别：由模型自行选择规则、无需 RLHF 预热、但受上下文 token 上限约束）与 State-of-the-art AI Assistants（InstructGPT、ChatGPT、Alpaca、Vicuna、Koala、Dolly-V2、OpenAssistant） |
| 3 | Our Method: SELF-ALIGN | 方法章。3.1 Topic-Guided Red-Teaming Self-Instruct：175 条手写指令 + 20 类对抗式指令类型与主题引导生成合成指令；3.2 Principle-Driven Self-Alignment：16 条原则（ethical/informative/helpful/…/operational）+ 5 个 ICL 示例，以 "internal thoughts" 先选规则再作答；3.3 Principle Engraving：剪除原则与示例后在自对齐输出上微调基座模型，同时节省 1.7k token 上下文；3.4 Verbose Cloning：用 verbose 提示 + context distillation 解决回答过短与"背诵维基段落"两个问题 |
| 4 | Evaluation | 评测章。4.1 Dromedary 与基线模型说明（Dromedary final 与 Dromedary non-verbose 两个变体）；4.2.1 TruthfulQA：MC1 达 69，生成任务上 Truthful 0.72 / Truthful*Informative 0.61（Vicuna-13B 为 0.84 / 0.84）；4.2.2 BIG-bench HHH Eval：overall 0.83，优于 LLaMA-65B 0.77 与 Alpaca-65B 0.79，低于 ChatGPT 0.87；4.2.3 Vicuna Benchmark Questions (Evaluated by GPT-4)：胜过 Text-Davinci-003 与 Alpaca，不及 ChatGPT 与 Vicuna；4.2.4 Discussions：提出"先对齐后遵循"的新范式，并定义 verbose tax；4.3 Qualitative Demonstrations：定性示例 |
| 5 | Conclusion & Future Work | 总结 SELF-ALIGN 与 Dromedary，并列出原则消融、引入 CAI 式自评与强化学习、开展人类评测等五个方向 |
| — | Acknowledgements | 致谢（IBM research、Microsoft AFMR award、Google PhD Fellowship） |
| ~ | References | 参考文献 |
| 附录 | A–O | A Limitations & Social Impacts（A.1 局限：内在知识不完整、原则难定义、泛化性有限、原则遵循不一致；A.2 社会影响：滥用风险与偏置公平性）；B More Details about Dromedary（含数据统计与训练配置）；C Dromedary-2（基于 LLaMA-2 的后续模型）；D Additional Experimental Details（D.1 模型与基线、D.2 超参、D.3 基准数据集）；E–F Vicuna 基准额外分析与失败案例（Failure Mode I 间接回答、Failure Mode II 原则遵循不一致；F 小节标题未在文本层出现）；G 16 条原则；H ICL 示例；I 原则刻录提示；J Verbose Cloning 提示；K 推理提示（K.1 冗长输出、K.2 多语言输出）；L/M Topic-Guided Red-Teaming Self-Instruct 的 20 条种子提示与指令提示；N MC 基准评测提示；O Vicuna 基准少样本提示 |

## 四、核心创新点与贡献

1. **SELF-ALIGN 框架**：把"原则驱动的推理"与 LLM 生成能力结合，用少于 300 行人工标注（195 条种子提示 + 16 条原则 + 5 个示例）完成对齐，不依赖 ChatGPT/GPT-4 等已对齐模型的蒸馏，即所谓 "from scratch"。
2. **Topic-Guided Red-Teaming Self-Instruct**：在 Self-Instruct 之上加入 20 类对抗式指令类型与主题引导，提高合成指令的多样性与覆盖面（论文统计了自建数据集的动词-宾语分布与原则使用频次）。
3. **Principle Engraving**：把原则与 ICL 示例"刻"进参数后将其从上下文中剪除，既提升对齐表现又节省约 1.8k token 的固定上下文开销。
4. **Verbose Cloning 与 "verbose tax"**：用 context distillation 让回答更详尽，同时诚实报告该步骤在多个多选题基准上造成性能下降，并借用"alignment tax"提出 verbose tax 概念。
5. **完整开源与对照实验**：公开代码、LoRA 权重与合成数据，并在 Table 1 中系统对比 InstructGPT（77K）、Alpaca（52K）、Vicuna（70K）、Koala（472K）等系统的监督量与对齐技术。

## 五、关键词

| 关键词 | 中文 | 在本论文中的重要性 |
| --- | --- | --- |
| SELF-ALIGN | — | 论文提出的对齐框架名称 |
| Principle-driven self-alignment | 原则驱动的自我对齐 | 第二阶段核心：由模型自选规则再作答 |
| Dromedary | — | 用 SELF-ALIGN 在 LLaMA-65b 上训练出的 AI 助手 |
| Self-Instruct / Topic-Guided Red-Teaming | 自指示 / 主题引导红队 | 合成指令生成机制，构成训练数据来源 |
| Principle Engraving | 原则刻录 | 把原则写入参数的微调阶段 |
| Verbose Cloning | 冗长克隆 | context distillation 阶段，提升回答详尽度 |
| Context distillation | 上下文蒸馏 | Verbose Cloning 的实现技术 |
| Verbose tax | 冗长税 | 论文自创术语：提升冗长度对部分基准造成的性能损失 |
| RLHF / SFT / Constitutional AI | — | 被对比的对齐范式 |
| Internal thoughts | 内部思考 | ICL 示例中"先选规则后作答"的显式推理形式 |

## 六、与本课题的相关要素

- **"冗长税"：更长 ≠ 更好，且方向随评价范式反转（对讨论"长度与质量"最有价值的一条）**：§4.2.4 明确 Verbose Cloning 提升了 Vicuna 基准（GPT-4 评审）与 TruthfulQA 生成任务的表现，却损害了多个多选题基准，"particularly in ranking more trustworthy responses"。这为课题讨论"人类偏好-长度正相关"的边界条件提供了异质证据：同一模型在生成式评价上获益、在判别式评价上受损。
- **人类标注本身有质量与偏置问题**：§1 指出依赖人工监督 "has potential issues with the quality, reliability, diversity, creativity, self-consistence, undesirable biases, etc., in human-provided annotations"。课题在讨论"人类 A/B 选择作为标签的可靠性边界"时可以引用（注意本文语境是 SFT/RLHF 标注，而非大规模 A/B 偏好选择）。
- **用户偏好更长回答的动机性说明**：§3.4 记录 principle-engraved 模型 "tended to generate unduly brief responses, while users typically expect more comprehensive and elaborate answers"，可作为"长度偏好部分来自用户对详尽度的预期"的引用来源，与课题观察到的长度效应方向相呼应。
- **对齐数据全部由模型自生成**：360k 合成指令、260k（过滤后）自对齐回答、358,777 条 verbose 回答；可用于讨论"偏好/对齐数据的生产方式会塑造其分布特征"，但本文未统计长度或 Markdown 格式特征，不能作为格式证据。
- **GPT-4 评审的早期用例**：§4.2.3 使用 Vicuna 基准 + GPT-4 打分（4.2.1 另用 GPT-4 完成 TruthfulQA 生成任务的评分），属 LLM-as-judge 路线，与课题的人类选择层不同；可作为"LLM 评审 vs 人类评审"对照的背景引用。
- **建议引用位置**：讨论（verbose tax 作为"长度/详略与评价指标方向不一致"的证据；人类标注含偏；用户对详尽度的预期）；局限（其对齐目标是 HHH 与对话质量，不涉及长度或格式的统计关联）。
- **数据是否同源**：否。本文使用 Self-Instruct/TGRT 合成数据、Vicuna 基准问题、TruthfulQA、BIG-bench HHH Eval 与自建的 self-instruct 数据集，与 LMArena/Arena-Human-Preference-140k 无交集。
- **可核对数字**：人工标注少于 300 行（195 条种子提示 / 16 条原则 / 5 个示例）；TruthfulQA MC1 = 69；TruthfulQA 生成任务 Truthful 0.72 与 Truthful*Informative 0.61（Vicuna-13B 0.84 / 0.84；Davinci-003 0.60 / 0.59）；HHH Eval overall：LLaMA-65B 0.77、Alpaca-65B 0.79、ChatGPT 0.87、Dromedary non-verbose 0.85、Dromedary final 0.83；合成指令 360k / 过滤后 260k / verbose 回答 358,777 条；固定原则与示例约占 1800 token。

## 七、可引用段落摘录

> 以下句子逐字取自 PDF 文本层（单栏抽取，语句完整，已逐句核对）。

1. **§4.2.4 Discussions（可用于讨论"更长/更详尽不必然更好"与去偏代价）**
   > However, the benchmark results reveal a noteworthy observation: while Verbose Cloning significantly improves generation quality (as evidenced by the Vicuna Benchmark Questions and our TruthfulQA generation task), it harms the model's performance in several multiple-choice benchmarks, particularly in ranking more trustworthy responses.
2. **§1 Introduction（可用于讨论人类标注数据的可靠性边界）**
   > The success of these techniques heavily relies on the availability of extensive human supervision, which is not only expensive to obtain but also has potential issues with the quality, reliability, diversity, creativity, self-consistence, undesirable biases, etc., in human-provided annotations [48, 20, 47].
3. **§3.4 Verbose Cloning（可用于说明"用户期待更长回答"这一偏好来源）**
   > In our preliminary testing of the principle-engraved model, we identified two primary challenges: 1) the model tended to generate unduly brief responses, while users typically expect more comprehensive and elaborate answers from an AI assistant, and 2) the model occasionally recited relevant Wikipedia passages without directly addressing the user's query.

## 八、局限与引用注意

- **作者自述局限**（Appendix A.1）：基座模型的内在知识可能不完整或过时；原则的定义非平凡、原则之间可能冲突并导致意外行为；模型泛化性有限，某些场景需要额外微调；初步测试中发现 Dromedary 偶尔产生违反既定原则的幻觉，不应假定该对齐流程提供"能阻止所有不良输出的确定性护栏"。
- **作者自述社会影响**（Appendix A.2）：存在被滥用于生成恶意内容或自动化虚假信息的风险；模型可能延续或放大基座模型预训练数据中的偏置，导致不公平或歧视性结果。
- **种子提示数量存在表述分歧**：摘要写 "< 200 seed prompts"，§1 写 175 条种子提示 + 20 条主题专用提示，Figure 1 标注 "195 seed prompts"。引用具体数字时建议以 §1/Figure 1 的 195 为准，或直接沿用摘要的 "< 200" 表述并注明分歧。
- **评测规模与层次**：TruthfulQA、BIG-bench HHH Eval（约 200 组比较）、Vicuna 基准均为数百题量级；Vicuna 基准由 GPT-4 评审（LLM-as-judge），且 Dromedary 在 TruthfulQA 生成任务上仍明显落后于蒸馏自 ChatGPT 的 Vicuna-13B，结论不具全面优势。
- **引用位置错位**：§4.2.1 正文写 "As shown in Table 4 (right)"，但 Truthful 与 Truthful*Informative 的数值实际位于 Figure 4 右侧表格；引用数字前须回 PDF 核对图表编号。
- **层次差异**：本文不测量偏好数据中的长度或格式偏置，其 verbose tax 是"同一模型在不同基准上的表现差异"，既不是人类 A/B 偏好的关联证据，也不是因果证据；引用时应明确其为对齐过程中的指标间取舍现象。
- **数据不可比**：合成数据全部由 LLaMA-65b 自生成，评测问题集与课题的 LMArena 真实人类偏好数据无交集；本文的"人类标注问题"论断是动机性陈述，未提供作者自己的标注质量统计。
