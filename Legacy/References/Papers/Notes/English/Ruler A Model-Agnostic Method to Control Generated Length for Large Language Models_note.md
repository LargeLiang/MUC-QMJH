# RULER: A Model-Agnostic Method to Control Generated Length for Large Language Models

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 标题 | RULER: A Model-Agnostic Method to Control Generated Length for Large Language Models（PDF 首页标题首字母 R 为 drop cap，文本层抽取为 "ULER"，此处按原文复原） |
| 作者 | Jiaming Li, Lei Zhang, Yunshui Li, Ziqiang Liu, Yuelin Bai, Run Luo, Longze Chen, Min Yang（Min Yang 为通讯作者） |
| 机构 | Shenzhen Institute of Advanced Technology, Chinese Academy of Sciences（中国科学院深圳先进技术研究院）；University of Chinese Academy of Sciences（中国科学院大学） |
| 出处 | arXiv:2409.18943v2 [cs.CL]，2024-10-01；正文无会议/期刊标识，venue 未确认 |
| 语言 | 英文 |
| 与课题相关度 | ★★☆☆☆（提供"长度是可独立操控的生成属性"与长度感知噪声的证据，但属生成端控制，不涉及偏好评价） |
| 原文位置 | `Papers/English/Ruler A Model-Agnostic Method to Control Generated Length for Large Language Models.pdf` |

## 一、三句话概括

1. 论文提出 Target Length Generation Task（TLG），考察 LLM 能否按指令生成指定长度的回答，并设计 Precise Match（PM）与 Flexible Match（FM）两个指标来衡量长度遵从度。
2. 对 15 个开源模型与 5 个闭源模型的评测显示现有 LLM 普遍达不到长度约束（最好的 claude-3.5-Sonnet 在 All Level 上 PM 仅 61.65），作者把原因归于 subword tokenization 与训练目标未显式约束输出长度。
3. 论文提出模型无关的 RULER 方法，用 Meta Length Tokens（MLT）做端到端训练，使 6 个基座模型在 All Level 上平均提升 PM 27.97、FM 29.57，并在六个通用基准上基本保持原有性能。

## 二、摘要

**原文（逐字）**

> The instruction-following ability of large language models enables humans to interact with AI agents in a natural way. However, when required to generate responses of a specific length, large language models often struggle to meet users' needs due to their inherent difficulty in accurately perceiving numerical constraints. To explore the ability of large language models to control the length of generated responses, we propose the Target Length Generation Task (TLG) and design two metrics, Precise Match (PM) and Flexible Match (FM) to evaluate the model's performance in adhering to specified response lengths. Furthermore, we introduce a novel, model-agnostic approach called RULER, which employs Meta Length Tokens (MLTs) to enhance the instruction-following ability of large language models under length-constrained instructions. Specifically, RULER equips LLMs with the ability to generate responses of a specified length based on length constraints within the instructions. Moreover, RULER can automatically generate appropriate MLT when length constraints are not explicitly provided, demonstrating excellent versatility and generalization. Comprehensive experiments show the effectiveness of RULER across different LLMs on Target Length Generation Task, e.g., at All Level 27.97 average gain on PM, 29.57 average gain on FM. In addition, we conduct extensive ablation experiments to further substantiate the efficacy and generalization of RULER. Our code and data is available at https://github.com/Geaming2002/Ruler.

**中文翻译**

> 大语言模型（LLM）的指令遵循能力使人类能够以自然方式与 AI 智能体交互。然而，当被要求生成特定长度的回答时，大语言模型常常难以满足用户需求，因为它们在准确感知数值约束方面存在固有困难。为探究大语言模型控制生成回答长度的能力，我们提出目标长度生成任务（Target Length Generation Task, TLG），并设计两个指标——精确匹配（Precise Match, PM）与灵活匹配（Flexible Match, FM），用以评估模型遵守指定回答长度的表现。此外，我们提出一种新颖且模型无关的方法 RULER，它使用元长度标记（Meta Length Tokens, MLT）来增强大语言模型在带长度约束的指令下的指令遵循能力。具体而言，RULER 让 LLM 具备依据指令中的长度约束生成指定长度回答的能力。而且，当未显式给出长度约束时，RULER 能自动生成合适的 MLT，展现出优异的通用性与泛化性。大量实验表明 RULER 在不同 LLM 的目标长度生成任务上均有效，例如在 All Level 上 PM 平均提升 27.97、FM 平均提升 29.57。我们还开展了充分的消融实验，进一步证实 RULER 的有效性与泛化性。代码与数据见 https://github.com/Geaming2002/Ruler。

（完整摘要另见 `Ruler A Model-Agnostic Method to Control Generated Length for Large Language Models_摘要.md`）

## 三、章节结构与内容

| 位置 | 标题（原文） | 内容说明 |
| --- | --- | --- |
| 1 | Introduction | 指出用户常在指令中指定长度（如 "Tell me how to make a cake in 30 words"），而 LLM 普遍做不到；引出 TLG 任务、PM/FM 指标与 RULER 方法，并列出三条贡献 |
| 2 | Related Work | 综述章。2.1 Large Language Model：LLM、in-context learning、CoT；2.2 Instruction Following：指令遵循的定义与指令微调数据构建；2.3 Meta Token：Function Vector、gist tokens、HD-Gist tokens 等自定义 token 的用法 |
| 3 | Can LLMs Accurately Generate with Target Length? | 问题检验章。3.1 Target Length Generation Task：定义 TLG 与九档目标长度（10/30/50/80/150/300/500/700/>800）分三个 Level，给出 PM 的严格容差与 FM 的宽区间定义（式 1、式 2）；3.2 Experimental Setup：TLG 数据从 OpenHermes2.5 随机抽 2,000 条并只保留问题、随机指派目标长度，推理用 vllm、temperature=0；3.3 Results and Analysis：几乎所有模型 Level:2 最差、Level:1 最好，最好成绩为 claude-3.5-Sonnet 的 All Level PM 61.65 / FM 79.55，归因于 tokenization 与模型训练目标 |
| 4 | RULER: Meta Length Token Controlled Generation | 方法章。4.1 Method：定义 MLT（[MLT:10]…[MLT:>800] 及其变化区间），构造 DMLT 并把 MLT 直接拼在回答 y 之前、以标准 next-token 目标训练（式 3）；4.2 RULER Inference：TLG 场景下把目标长度转成 MLT，非 TLG 场景下模型先生成 MLT 再生成回答 |
| 5 | Experiments | 实验章。5.1 Experimental Setup：DMLT 由 OpenHermes2.5（剔除 TLG 用过的数据）、LongForm、ELI5 构成，共 121,229 条、每个 MLT 上限 20,000，选 6 个 7B 级模型；5.2 Main Results：全 Level 全面提升，平均增益 PM 27.97 / FM 29.57，最好与最差模型增益区间为 PM 21.35–34.40、FM 22.15–37.10；5.3 Do MLTs actually influence the length of the generated content?：multi MLT 实验（Arena-Hard-Auto 抽 200 条 × 9 档长度 = 1,800 条）与 self-generated MLT 实验（FM 73.40–88.40，平均词数 187–347）；5.4 Evaluation on Overall Performance：六个基准（ARC、HellaSwag、TruthfulQA、MMLU、Winogrande、GSM8K）上总体性能基本持平 |
| 6 | Conclusion | 总结 TLG、RULER 与三项实验结论 |
| — | Limitations | 作者自述局限，见第八节 |
| — | Ethical Statements | 声明未评估生成有毒内容的风险、无人类被试、只用开源/合规许可资源 |
| — | Acknowledgements | 致谢与基金编号 |
| ~ | References | 参考文献 |
| 附录 | A–C | A Target Length Generation Task Deatils（A.1 TLG 数据集 2,000 条示例、A.2 模型与提示模板、A.3 各目标长度下 PM/FM 明细表）；B DMLT Data Creation（Algorithm 1 与各数据集 MLT 分布）；C Experiments Details（C.1 数据集中的 MLT 分布、C.2 训练细节与 loss 曲线、C.3 multi MLT 实验、C.4 其他任务的评测设置） |

## 四、核心创新点与贡献

1. **新任务 TLG**：把"按指定长度生成"从指令遵循中单独析出，构成一个可量化、带人工指定长度约束的评测任务（数据集 2,000 条，九档目标长度）。
2. **两个长度匹配指标**：PM（严格容差 ±10/±20/±50/±70）与 FM（更宽的分档区间，如 (0,20]、(20,40]…(800,∞)），为"是否命中目标长度"提供了可比口径。
3. **模型无关的 RULER 方法**：用 Meta Length Tokens 把长度要求显式写入词表并端到端训练，6 个基座模型全部提升，All Level 平均 +27.97 PM / +29.57 FM。
4. **非 TLG 场景的自动 MLT 生成**：未给出长度约束时模型自发生成 MLT 再作答，self-generated MLT 实验 FM 达 73.40–88.40，说明该机制不是对提示词的简单过拟合。
5. **能力保持的验证**：在 ARC、HellaSwag、TruthfulQA、MMLU、Winogrande、GSM8K 上总体性能与原始 SFT 模型基本一致，个别任务有小幅升降。

## 五、关键词

| 关键词 | 中文 | 在本论文中的重要性 |
| --- | --- | --- |
| Target Length Generation Task (TLG) | 目标长度生成任务 | 论文提出的核心评测任务，全文实验围绕它展开 |
| Precise Match (PM) | 精确匹配 | 严格容差下的长度命中率指标（主指标之一） |
| Flexible Match (FM) | 灵活匹配 | 宽区间下的长度命中率指标（主指标之一） |
| Meta Length Token (MLT) | 元长度标记 | 方法核心：把长度区间编码为可生成的特殊 token |
| RULER | — | 论文提出的模型无关长度控制方法 |
| DMLT | 带 MLT 的微调数据集 | 121,229 条 (x, mlt, y) 训练数据，各 MLT 上限 20,000 |
| Instruction following | 指令遵循 | 论文所定位的能力范畴（长度约束被视为指令遵循的一部分） |
| Tokenization / word count | 分词 / 词数 | 作者归因的长度失配来源：token 数与人类理解的词数不一致 |
| Arena-Hard-Auto | — | multi MLT 与 self-generated MLT 实验的问题来源（各抽 200 条） |
| Level:0 / Level:1 / Level:2 | 长度档位 | 九档目标长度按短中长分层的评测口径 |

## 六、与本课题的相关要素

- **长度是可被独立操控的生成属性（对课题"混淆/可操纵特征"论述有用）**：RULER 通过对齐长度区间构造 DMLT 并训练模型，证明长度可以在几乎不改变回答内容的条件下被系统性地拉长或压短；这为课题把 token 长度视为"可被模型侧策略影响的输出特征"提供生成端依据。
- **长度感知本身有噪声（对"测量误差"论述有用）**：Table 2 中多数开源模型的 All Level PM 只有 10–30 量级，最好的 claude-3.5-Sonnet 也仅 PM 61.65 / FM 79.55；§3.3 把失配归因于 "a discrepancy between the token counts generated by LLMs and the lengths as understood by humans"。可支撑课题在局限中说明"以 token 数作为长度的代理指标"存在模型侧偏差，且该偏差随长度档位变化（Level:2 最差、Level:1 最好）。
- **长度与任务类别相关（对"混淆控制"论述有用）**：§5.3 发现模型自发生成的 MLT 集中于 150 与 300，作者解释为 "the complex nature of the queries in the Arena-Hard-Auto, which require longer responses for problem resolution" —— 与课题在 logistic 回归中控制任务类别（以及 7 种提示词属性）的理由一致：长度需求由问题类型决定。
- **长度分档口径可借鉴**：Table 1 的九档目标长度 + 三档 Level，以及 PM/FM 双层容差，是"长度分层"的现成做法，可与课题的匹配诊断（长度分箱）并列引用，说明分档粒度会改变长度效应估计。
- **"提升长度控制几乎不损失通用能力"的对照**：§5.4 中 RULER 在六个基准上与原模型基本持平，可作为"改变长度特征不必然改变内容质量"的一个（弱）旁证，用于讨论"长度与质量可分离"。
- **数据线索（部分同生态、不同源）**：TLG 数据取自 OpenHermes2.5；multi MLT 与 self-generated MLT 实验的问题取自 Arena-Hard-Auto（Li et al., 2024a）。Arena-Hard-Auto 与课题使用的 LMArena 偏好数据同属 Arena 生态，但本文用的是其问题集、且课题用的是 Arena-Human-Preference-140k 的 135,634 条输入与 78,959 对胜负，二者不同源，不可合并或互证。
- **建议引用位置**：引言（长度是 LLM 输出中可测量且可干预的显式属性）；方法（长度分档与容差设计的先例）；讨论（长度需求由任务类型决定、长度感知噪声）；局限（生成端证据不能直接支持评价端的长度-偏好关联）。
- **可直接引用的数字**：All Level 平均增益 PM 27.97 / FM 29.57；增益区间 PM 21.35–34.40、FM 22.15–37.10（6 个模型）；DMLT 121,229 条；TLG 2,000 条；multi MLT 实验 200 条 × 9 档 = 1,800 条；self-generated MLT 实验 FM 73.40–88.40、平均词数 187–347。

## 七、可引用段落摘录

> 以下句子逐字取自 PDF 文本层（该文双栏排版，摘要与表头存在区隔，已逐句核对）。

1. **§3.3 Results and Analysis（可用于讨论长度特征的测量误差与"长度感知"问题）**
   > The poor performance in TLG can be attributed to a discrepancy between the token counts generated by LLMs and the lengths as understood by humans.
2. **§5.3 Do MLTs actually influence the length of the generated content?（可用于讨论长度需求与任务类别混淆）**
   > Models show a preference for producing responses with target lengths of 150 and 300. This inclination is likely attributable to the complex nature of the queries in the Arena-Hard-Auto, which require longer responses for problem resolution.
3. **§5.4 Evaluation on Overall Performance（可用于讨论"改变长度特征是否损害内容质量"）**
   > Overall performance of models using Ruler generally remains consistent with the original models.

## 八、局限与引用注意

- **作者自述局限**（§Limitations）：论文只从"控制生成长度"这一角度分析 LLM 能力；作者主张 meta token 比 prompt 提供更稳健的控制，并把"如何借助 token 更有效地开发与使用模型"列为待研究问题。局限章节未列出具体实验性局限。
- **作者自述伦理边界**（§Ethical Statements）：只关注生成长度，未评估生成有毒内容的风险；无人类被试。
- **数据不平衡导致的性能下降（作者自述）**：Level:2 的效果因模型而异，deepseek-llm-7b-chatR 在 Level:2 出现小幅下降，作者归因于 DMLT 中 Level:2 数据不足（700 词档在三个数据源中仅数百条）。
- **venue 未确认**：文本层无会议/期刊标识，只有 arXiv:2409.18943v2 [cs.CL] 与日期 2024-10-01；引用时建议以 arXiv 编号标注。
- **文本层质量问题**：Table 4（RULER 与基线对比）在抽取文本中数字粘连（如 "70.1849.89"），Table 1 的行序与 Level 标签存在错位（据附录 A.3.1–A.3.3，实际分组为 Level:0 = {10,30,50,80}、Level:1 = {150,300,500}、Level:2 = {700,>800}），引用逐模型数字前须回 PDF 核对。
- **层次差异**：本文是生成端干预实验，不测量人类 A/B 偏好，也不涉及长度与胜率的关联；引用其"27.97 / 29.57"等数字只能支撑"长度可被控制"，不能支撑"长度影响人类选择"。
- **指标名冲突**：本文 PM/FM 是长度命中率，与偏好研究中常见的 win rate / 胜率无关，切不可混用缩写。
- **同名文献风险**："RULER" 这一名称在长上下文评测等方向另有同名工作，检索与引用时需以 arXiv:2409.18943 及作者列表区分。
