# Format as a Prior: Quantifying and Analyzing Bias in LLMs for Heterogeneous Data

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 标题 | Format as a Prior: Quantifying and Analyzing Bias in LLMs for Heterogeneous Data |
| 作者 | Jiacheng Liu\*, Mayi Xu\*, Qiankun Pi, Wenli li, Ming Zhong, Yuanyuan Zhu, Mengchi Liu, Tieyun Qian（\*共同第一作者；通讯作者 Tieyun Qian） |
| 机构 | School of Computer Science, Wuhan University, China |
| 出处 | arXiv:2508.15793v1 [cs.CL]，2025-08-13（预印本；正式 venue 未确认） |
| 语言 | 英文 |
| 与课题相关度 | ★★☆☆☆（提供"格式即先验"的机制侧证据与注意力干预方法，但研究对象是 LLM 对**输入数据格式**的偏置，不涉及人类偏好数据） |
| 原文位置 | `Papers/English/Format as a Prior Quantifying and Analyzing Bias in LLMs for Heterogeneous Data.pdf` |

## 一、三句话概括

1. 论文首次系统研究 LLM 的**格式偏置（format bias）**：当同一事实以 text、table、infobox、KG 四种等价格式呈现且内容冲突时，模型会系统性地偏向某类格式而非公平整合证据。
2. 作者以 ConflictBank 为底料构造异构冲突场景，做三阶段实证：先确认偏置的存在与方向（十个 LLM、60 种格式对条件），再分解出信息丰富度、结构质量、格式类型三个数据层因素，最后从注意力分配角度解释机制并测试推理期干预。
3. 结论是偏置的"存在"可被注意力重加权缓解（DCR 显著上升），但偏置的"方向"更顽固、可能源自预训练，因此作者主张从数据预处理、推理期干预与格式均衡语料三个层面处理。

## 二、摘要

**原文（逐字）**

> Large Language Models (LLMs) are increasingly employed in applications that require processing information from heterogeneous formats, including texts, tables, infoboxes, and knowledge graphs. However, systematic biases toward particular formats may undermine LLMs' ability to integrate heterogeneous data impartially, potentially resulting in reasoning errors and increased risks in downstream tasks. Despite these concerns, it remains uncertain whether such format biases are systematic, which data-level factors contribute to them, and what internal mechanisms in LLMs underlie their emergence.
>
> In this paper, we make the first attempt to investigate and analyze the format bias in LLMs. To systematically investigate the aforementioned questions, we conduct a three-stage empirical study by constructing an heterogeneous data conflict scenario for the exploration of bias. The first stage explores the presence and direction of bias across a diverse range of LLMs. The second stage aims to examine how key data-level factors, including information richness, structure quality, and format type, influence these biases.
>
> The third stage analyzes how format bias emerges within LLMs' attention patterns and evaluates a lightweight intervention to test its effectiveness. Based on these investigations, we identify three future research directions to reduce format bias: enhancing data pre-processing through format repair and normalization, introducing inference-time interventions such as attention re-weighting, and developing format-balanced training corpora. These directions will support the design of more robust and fair heterogeneous data processing systems.

**中文翻译**

> 大语言模型（LLM）越来越多地被用于处理来自异构格式（包括文本、表格、信息框与知识图谱）的信息。然而，对特定格式的系统性偏好可能损害 LLM 公平整合异构数据的能力，进而导致推理错误并放大下游任务的风险。尽管存在这些担忧，但此类格式偏置是否具有系统性、哪些数据层因素导致它们、以及 LLM 内部何种机制使其产生，仍不清楚。
>
> 本文首次尝试对 LLM 中的格式偏置进行考察与分析。为系统研究上述问题，我们构造了一个异构数据冲突场景，开展三阶段实证研究。第一阶段探究偏置在多种 LLM 上的存在性与方向；第二阶段考察关键数据层因素（信息丰富度、结构质量、格式类型）如何影响这些偏置。
>
> 第三阶段分析格式偏置如何体现在 LLM 的注意力模式中，并评估一种轻量级干预是否有效。基于这些考察，我们提出三个减少格式偏置的未来研究方向：通过格式修复与归一化强化数据预处理、引入注意力重加权等推理期干预、以及构建格式均衡的训练语料。这些方向将支撑更稳健、更公平的异构数据处理系统的设计。

（完整摘要另见 `..._摘要.md`）

## 三、章节结构与内容

| 位置 | 标题（原文） | 内容说明 |
| --- | --- | --- |
| 1 | Introduction | 提出核心问题：LLM 是否公平对待不同格式的外部知识；以临床决策案例（Qwen3-8b 在 table 呈现时误判、KG 呈现时正确）说明后果；列出三条贡献（首次系统研究格式偏置／三阶段实证／三条缓解方向） |
| 2 | Related Work | 综述两条脉络。2.1 Heterogeneous reasoning：跨格式推理基准（COMPMIX、CompMix-IR）与两类既有方案（统一检索框架、LLM 中心流水线），指出既有工作默认"检索到即公平评估"；2.2 LLM Behavior under Conflicting Evidence：参数知识 vs 上下文证据的冲突、实体流行度/事件时新性/证据频率等偏置来源、ConflictBank/WikiContradict/WhoQA 等基准与冲突感知解码等缓解手段。结论：本文补充了此前被忽视的"格式"这一偏置来源 |
| 3 | Investigation Framework | 框架章（含数据集构造、混杂因素排除、自动评估）。3.1 Dataset and Format Construction：以 ConflictBank 随机抽样 4,000 条，每条含 1 个事实主张与 3 个反主张及各自证据，构成 12,000 个矛盾对；用 GPT-4o-mini 做转换引擎生成 KG（S–P–O 三元组）、Infobox（键值对）、Table（表格）三种 Wikipedia 风格格式；人工抽检 5%（600 例）验证转换完整性，事实准确性 98.7%、语法有效性 99.3%。3.2 Confounding Factor Control：排除两类混杂——(a) 内部知识过滤，每条事实主张先零样本查询 16 次，只保留"模型全部失败复现"的样本；(b) 随机化证据呈现顺序以消除位置偏置。3.3 Evaluated LLMs：评估十个模型、六大系列（GPT-4o-mini、LLaMA-3.1-8B、Mistral-7B、Qwen3 8B/14B/30B-A3B/32B、Gemma-2 9B/27B、GLM-4-9B），temperature=0。3.4 Evaluation Protocol and Metrics：以 GPT-4o-mini 为评审，每条回答独立判三次取多数票；定义三类互斥输出（Pref-A／Pref-B／Both）与两个指标 DCR（Dual Coverage Rate，同时承认双方的比例）与 FPR（Format Preference Ratio，单边回答中偏向 A 的比例）；人工标注 5%（600 例）与自动判定比对，599 例一致（99.8%） |
| 4 | Experimental Results and Analysis | 4.1 Establishing the Existence of Format Bias：十模型 × 六种格式对 = 60 个条件。DCR 普遍偏低（3.01%–24.02%），同构（同为纯文本）条件下 DCR 明显上升；方向上有稳定的偏好层级——语义丰富格式（texts、KGs）持续优于视觉结构格式（infoboxes、tables），且按主题域分组后依然成立；规模不带来改善（Qwen3 系列更大模型未见提升）。FPR 热力图显示格式对之间显著不对称（双侧二项检验，原假设 FPR=0.5）。4.2 Identifying the Factors Behind Format Bias：分解出三个数据层因素并在同构/异构两种设定下检验。(1) 信息丰富度：4 vs 8、8 vs 12、4 vs 12 条目，模型一致偏向条目更多的一方，异构设定下偏向随条目数单调增强；(2) 结构质量：以 0.45/0.9 的概率破坏结构符号（括号、冒号、分隔符），同构设定下模型偏向结构完好者且偏好在中等破坏后饱和，异构设定下对结构化输入的偏好随破坏程度急剧下降；(3) 格式类型：Table 1 平均 FPR 为 Table 0.398 > KGs 0.336 > Infobox 0.235（以 texts 为对照），说明布局本身而非信息内容在调节偏置；跨因素结论：格式同构使 DCR 显著提升 28%–53%。4.3 Mechanism Behind Format Bias：以 Qwen3-8B、Mistral-7B-Instruct-v0.3、Llama-3.1-8B-Instruct 为例，计算两段证据的注意力质量差与 DCR 的关系，Spearman 秩相关系数为 −0.31、−0.37、−0.54（弱到中度负相关）；82.35% 的单边回答中模型反而偏向**注意力更少**的一侧；随后提出注意力均衡重加权干预（把两段证据的总注意力质量拉平、段内分布不变），干预后 DCR 在所有格式对与三个模型上显著上升（p ≤ 0.016，Wilcoxon signed-rank test），但 FPR 基本不变、统计不显著——即"存在性"可干预、"方向性"更顽固 |
| 5 | Discussion | 提出三层缓解路径：数据预处理（自动修复被破坏的表格/KG 结构、统一输入格式）、推理期干预（注意力再平衡，可改善中间处理但未必改变最终输出偏置）、模型开发与微调（格式均衡语料、对比目标惩罚格式驱动决策、格式感知模块），并推测输出层的格式偏好可能源自预训练暴露 |
| 6 | Conclusion | 总结：格式偏置是系统性效应，由信息丰富度、结构质量、格式类型驱动；表现为"可缓解的存在性偏置"与"可能根植于预训练的方向性偏置"两类；应把数据格式当作 LLM 设计与评估的核心因素 |
| Appendix | A Prompt Templates / B Model Query and Evaluation Protocols / C Full Results | A.1 提示模板、A.2 格式转换示例、A.3 数据验证统计（600 例抽样中 592 例通过事实一致性、596 例通过语法有效性）；B.1 十个被评模型及其 HuggingFace 标识、B.2 解码温度 0 与"GPT-4o-mini 三次多数票"、B.3 回答提示模板、B.4 评审提示；C.1–C.4 报告各格式对、各因素下的原始回答计数，C.7 为主题域层面结果 |

## 四、核心创新点与贡献

1. **首次把"格式"确立为 LLM 偏置的独立来源**：与既往关注内容层因素（时新性、频率、实体流行度）的工作相对，论文证明仅格式表征差异即可系统性改变模型行为。
2. **三阶段实证框架与可复用指标**：提出 DCR（存在性）与 FPR（方向性）两个互补指标，配合"内部知识过滤 + 证据顺序随机化"的混杂控制，把格式效应从内容效应中分离出来。
3. **把"格式"这一抽象概念操作化为三个可实验操纵的维度**：信息丰富度（条目数）、结构质量（结构符号破坏概率 0.45/0.9）、格式类型（text/table/infobox/KG）。
4. **给出注意力层面的机制证据**：注意力分配不均衡与 DCR 负相关（Spearman −0.31/−0.37/−0.54），且单边回答中 82.35% 偏向注意力更少的一侧——说明注意力解释"是否看到"但不解释"最终选谁"。
5. **提出并验证推理期注意力均衡干预**：在不改模型权重的前提下显著提升 DCR（p ≤ 0.016），同时诚实地报告该干预对 FPR 无效，划出"可干预/难干预"的边界。

## 五、关键词

| 关键词 | 中文 | 在本论文中的重要性 |
| --- | --- | --- |
| Format bias | 格式偏置 | 全文核心概念：格式本身引起的判断倾斜 |
| Heterogeneous data / heterogeneous reasoning | 异构数据／异构推理 | 应用场景：文本、表格、信息框、知识图谱并存 |
| Format as a prior | 格式即先验 | 论文的框定方式——格式是模型决策的一种先验 |
| Dual Coverage Rate (DCR) | 双重覆盖率 | 度量偏置"存在性"的主指标 |
| Format Preference Ratio (FPR) | 格式偏好比 | 度量偏置"方向性"的主指标 |
| Knowledge conflict | 知识冲突 | 实验场景：同一主谓关系的冲突主张与各自证据 |
| ConflictBank | — | 数据来源基准（随机抽样 4,000 条） |
| Information richness / structure quality / format type | 信息丰富度／结构质量／格式类型 | 论文分解出的三个数据层致偏因素 |
| Attention re-weighting | 注意力重加权 | 推理期干预手段，用于均衡两段证据的注意力质量 |
| Spearman's rank correlation / Wilcoxon signed-rank test | 斯皮尔曼秩相关／Wilcoxon 符号秩检验 | 机制分析与干预显著性检验所用统计工具 |

## 六、与本课题的相关要素

- **结论方向**：论文证明"格式偏好是系统性的、且方向稳定"，并给出"格式同构使 DCR 提升 28%–53%"的量化结果。课题讨论"格式特征与人类选择正相关"时，可引其作为"格式效应并非噪声"的旁证。
- **可借鉴的框定方式**：标题与摘要中的 "Format as a Prior" 是课题引言里可直接借用的表述框架——把格式（Markdown 标题/列表/加粗）理解为评审者（此处为人类）的一种先验，而非纯粹的信息载体。
- **方法可借鉴处**：(a) 用**二项检验检验方向性**（论文对 FPR=0.5 做双侧二项检验）；(b) 用 **Spearman 秩相关**量化"注意力不均衡—整合失败"的关联，课题中可用于"长度/格式差异幅度—选择结果"的单调性诊断；(c) **Wilcoxon signed-rank test** 的用法与课题的配对检验（Wilcoxon/符号检验 + Holm 校正）同族，可作为方法先例引用；(d) 论文的"混杂排除"两步（内部知识过滤与顺序随机化）与课题控制提示词属性、模型身份的调整策略在思想上一致。
- **可引用的指标名/方法名**：Dual Coverage Rate (DCR)、Format Preference Ratio (FPR)、three-stage empirical study、attention re-weighting、Spearman's rank correlation、Wilcoxon signed-rank test、two-sided binomial test。
- **可引用的数字（均取自原文）**：12,000 个矛盾对（4,000 条 × 3 反主张）、10 个 LLM、60 个实验条件（10 模型 × 6 格式对）、DCR 区间 3.01%–24.02%、事实准确性 98.7%、语法有效性 99.3%、评审与人工一致率 99.8%、Spearman −0.31/−0.37/−0.54、单边回答中 82.35% 偏向注意力更少的一侧、干预后 p ≤ 0.016、Table 1 的 FPR（Infobox 0.235／Table 0.398／KGs 0.336）、格式同构使 DCR 提升 28%–53%。
- **建议引用位置**：**引言**（说明"格式"已被证明是 LLM 判断的独立影响因素，为课题关注格式特征提供依据）、**讨论**（引入"存在性可缓解、方向性根植于预训练"这一二分，用于解释为何观察到的格式关联可能难以通过简单控制消除）、**局限**（说明课题只做观察性关联而无法像该文那样做注意力干预）。
- **数据是否同源**：**不同源**。该文底料为 ConflictBank（知识冲突基准），与课题的 LMArena/Arena-Human-Preference-140k 无交集，也不含任何人类偏好标注。
- **研究对象与人类偏好研究的层次差异**：该文研究的是 **LLM 对输入数据格式的偏置**（模型内部行为，输出为 Pref-A/Pref-B/Both 三分类），课题研究的是**人类对模型输出文本特征的偏好**（人类行为，输出为 A/B 二选一）。二者共享"格式影响判断"的主题，但一个是"模型当评审者、格式在输入端"，一个是"人类当评审者、格式在输出端"。引用时须显式说明这一层次差异，不可把该文的 DCR/FPR 数字与人类胜率并列。

## 七、可引用段落摘录

> 以下句子逐字取自 PDF 文本层（该文双栏排版，行末断词已按原文拼合，未改写）。

1. **Abstract（首句，可用于引言论证"格式偏置"这一研究缺口）**
   > In this paper, we make the first attempt to investigate and analyze the format bias in LLMs.
2. **§4.1 Establishing the Existence of Format Bias（用于讨论"格式差异本身即可改变判断"）**
   > This contrast highlights a broader pattern: format heterogeneity alone can independently and substantially impair a model's ability to jointly consider multiple inputs, even when the content is semantically equivalent.
3. **§6 Conclusion（用于讨论或局限，说明格式应被视作设计与评估的核心变量）**
   > These findings underscore the importance of treating data format as a core factor in LLM design and evaluation.

## 八、局限与引用注意

- **作者自述局限**：论文没有独立的 Limitations 章节；在 §4.3 与 §5 中作者承认注意力重加权"可能无法完全改变模型的最终输出偏置"，只改善中间处理，并把更深层的格式偏好归因于预训练，留作未来工作。
- **venue 未确认**：仅有 arXiv:2508.15793v1（2025-08-13），版式为 AAAI 风格但**未见正式会议/期刊信息**，引用时应按预印本标注。
- **"格式"语义不同**：该文的 format 指证据的**数据呈现格式**（文本/表格/信息框/知识图谱），课题的 format 指模型输出文本的 **Markdown 标记**（标题/列表/加粗）。术语同名而异指，引用时务必加限定语，避免读者混淆。
- **无人类偏好数据**：全部标签来自 GPT-4o-mini 评审（三次多数票），人类只用于抽检评估一致性（599/600）。因此其结论属于"LLM-as-a-judge 的行为证据"，不能直接移植为人类偏好证据。
- **模型与提示敏感性**：被评模型以 FP8 量化版本为主，temperature=0，且评审模型与被转换数据共用 GPT-4o-mini（转换引擎与评审同源），存在潜在同源偏差；引用数字时应说明这是该设定下的结果。
- **数据与任务差异**：ConflictBank 属于知识冲突事实性问答，与课题的开放式对话偏好对在任务分布、文本长度尺度上差异很大。
- **统计表述**：干预显著的表述为 p ≤ 0.016（Wilcoxon signed-rank），未见效应量与置信区间，引用时宜同时给出 DCR 变化方向而非只引 p 值。
