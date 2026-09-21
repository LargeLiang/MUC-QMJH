# LLMs Are Biased Towards Output Formats! Systematically Evaluating and Mitigating Output Format Bias of LLMs

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 标题 | LLMs Are Biased Towards Output Formats! Systematically Evaluating and Mitigating Output Format Bias of LLMs |
| 作者 | Do Xuan Long, Hai Nguyen Ngoc, Tiviatis Sim, Hieu Dao, Shafiq Joty, Kenji Kawaguchi, Nancy F. Chen, Min-Yen Kan |
| 机构 | 新加坡国立大学（NUS）；新加坡科技研究局（A*STAR）信息通信研究院 I2R；VinAI Research；A*STAR 高性能计算研究院 IHPC；Salesforce Research；南洋理工大学（NTU） |
| 出处 | arXiv:2408.08656v2 [cs.CL]，2025-02-23；正文未见会议/期刊标识，venue 未确认 |
| 语言 | 英文 |
| 与课题相关度 | ★★★★☆（"格式改变模型可测表现"的最直接证据链，但格式定义是输出约束式格式，评价对象是模型答题准确率而非人类 A/B 偏好） |
| 原文位置 | `Papers/English/LLMs Are Biased Towards Output Formats! Systematically Evaluating and Mitigating Output Format Bias of LLMs.pdf` |

## 一、三句话概括

1. 论文对 LLM 在格式约束下的表现做了首次系统性评估，提出把评测指标区分为"只计合规答案"的 SysE 与"不分合规与否"的 TrueE，并给出可全自动计算的真实表现估计量 EstTrueE。
2. 作者以 EstTrueE 的跨格式方差定义格式偏置指标 BiasFo，在 MCQ、wrapping、list、mapping 四大类共 15 种格式、8 个任务、4 个模型上测得显著偏置，并把成因归为"format token bias"。
3. 论文进一步用示例演示、重复格式指令、按系统评分反比合成格式数据微调三种手段缓解偏置，把 ChatGPT 在 wrapping 格式上的性能方差从 235.33（%²）降到 0.71（%²）。

## 二、摘要

**原文（逐字）**

> We present the first systematic evaluation examining format bias in performance of large language models (LLMs). Our approach distinguishes between two categories of an evaluation metric under format constraints to reliably and accurately assess performance: one measures performance when format constraints are adhered to, while the other evaluates performance regardless of constraint adherence. We then define a metric for measuring the format bias of LLMs and establish effective strategies to reduce it. Subsequently, we present our empirical format bias evaluation spanning four commonly used categories--multiple-choice question-answer, wrapping, list, and mapping--covering 15 widely-used formats. Our evaluation on eight generation tasks uncovers significant format bias across state-of-the-art LLMs. We further discover that improving the format-instruction following capabilities of LLMs across formats potentially reduces format bias. Based on our evaluation findings, we study prompting and fine-tuning with synthesized format data techniques to mitigate format bias. Our methods successfully reduce the variance in ChatGPT's performance among wrapping formats from 235.33 to 0.71 (%2).

**中文翻译**

> 我们给出首个考察大语言模型（LLM）表现中格式偏置的系统性评估。我们的方法把格式约束下的评测指标区分为两类，以可靠且准确地衡量表现：一类只衡量遵守了格式约束时的表现，另一类则无论是否遵守约束都衡量表现。随后我们定义了一个度量 LLM 格式偏置的指标，并确立了降低该偏置的有效策略。接着，我们给出覆盖四类常用格式——多项选择问答、包裹（wrapping）、列表、映射——共 15 种广泛使用格式的实证格式偏置评估。我们在八个生成任务上的评估揭示了当前最先进 LLM 中显著的格式偏置。我们进一步发现，提升 LLM 跨格式的格式指令跟随能力可能降低格式偏置。基于评估发现，我们研究用合成格式数据进行提示与微调来缓解格式偏置。我们的方法成功把 ChatGPT 在各类包裹格式间的表现方差从 235.33 降到 0.71（%2）。

（完整摘要另见 `LLMs Are Biased Towards Output Formats! Systematically Evaluating and Mitigating Output Format Bias of LLMs_摘要.md`）

## 三、章节结构与内容

| 位置 | 标题（原文） | 内容说明 |
| --- | --- | --- |
| 1 | Introduction | 提出研究问题"如何系统、准确地评估 LLM 表现的格式偏置、偏置有多大"；给出 FI Score / SysE / TrueE / EstTrueE / BiasFo 的思路与三条贡献（首个系统性框架、15 格式×8 任务×4 模型的评估、三种缓解方法） |
| 2 | Related Works | 综述 LLM 输出格式与格式跟随基准（Zhou et al. 2023；Xia et al. 2024 等），指出既有工作只评"能否遵守格式"、不评"格式如何影响表现"；点名同期工作 Tam et al. (2024) 未区分评测指标且只覆盖 3 种结构化格式 |
| 3 | Output Format Evaluation Framework | 框架章，含 3.1 Theoretical Analysis: Format Evaluation（定义格式跟随二元函数 FC、FI Score、SysE 与 TrueE，提出估计量 EstTrueE 及一致性/可靠性定理 Thm. 3.1：只有 FI 足够高时估计才可靠）；3.2 Theoretical Analysis: Format Bias（以 k 种格式下 EstTrueE 的方差定义 BiasFo，给出两条去偏判据：降低 BiasFo、同时提高所有格式的 FI）；3.3 Formats for Evaluation（确立 MCQ、wrapping、list、mapping 四大类共 15 种格式） |
| 4 | General Experimental Setups | 基准：MMLU、BBH（MCQ），GSM8K、FairytaleQA、HotpotQA（wrapping），SciDocsRR、SemEval 2017（list），SciREX（mapping，分 easy/medium/hard），非 MCQ 各抽 200 条；模型：Gemma-7B-it、Mistral-7B-it-v0.2、Llama-3.1-8B-it、ChatGPT（gpt-3.5-turbo-0125）；指标 EstTrueAcc / EstTrueF1 / EstTrueMAP（α=β=5%）；提示基线为 zero-shot 与 zero-shot CoT，主文取二者平均 |
| 5 | Format Evaluation Experiments | 总览：所有模型与数据上均存在显著格式偏置，78.30% 的 EstTrue 结果可靠（MCQ 70%、wrapping 82.5%、list 67.19%、mapping 77.08%）。5.1 Experiments on MCQ Format：字符标识符 vs 选项文本，Mistral 平均 58.69% vs 4.22%、ChatGPT 差 19.03%，模型整体偏向字符标识符；5.2 Experiments on Wrapping Format：7 种包裹方式，Llama 的 BiasFo 最高（74.86%²），"Placeholder"（37.15%）表现最好，"Quoting"（24.58%）与"Parenthesis"（28.57%）最差；5.3 Experiments on List Format：4 种列表，Mistral BiasFo 353.80%²、ChatGPT 7.08%²、Gemma 1.32%²，Python 与换行列表最好、bullet-point 最差；5.4 Experiments on Mapping Format：JSON vs YAML，Gemma 差 16.51%、Mistral 16.07%，JSON 平均优于 YAML；各小节均把成因归于 format token bias |
| 6 | Mitigating Performance Format Bias: Actionable Recommendations | 三条缓解策略（对象为 ChatGPT / MMLU / wrapping）：(1) 加演示，1 例与 5 例使 FI 由 72.99% 升至 79.19% / 85.31%、BiasFo 降至 172.69%² / 111.78%²；(2) 重复格式指令三次，BiasFo 降至 146.84%²（但 Placeholder 反而变差）；(3) 按各格式 SysE 分数的反比合成 6,500 条格式数据微调，FI 达 99.58%、BiasFo 从 235.33%² 降至 0.71%²，近乎消除偏置（Gemma-2B-it 亦验证，见 C.5） |
| 7 | Conclusions | 总结格式偏置的系统性发现与缓解方法，呼吁更公平、更稳健的 LLM 研发 |
| — | Limitations | 三条自述局限（见第八节） |
| — | Ethical Considerations | 讨论格式偏置在公平性、社会影响与不同人群沟通偏好上的风险 |
| 附录 | A–E | A 规则式格式跟随打分算法（Alg. 1）；B EstTrueE 的可靠性分析与 Thm. 3.1 证明（B.1）；C 各类格式的详细讨论（C.1 MCQ、C.2 Wrapping、C.3 List、C.4 Mapping）与缓解结果（C.5，含 Gemma-2B-it 与全部数值表）；D 数据集说明（D.1）与解码/微调超参（D.2）；E 四类任务的提示词模板（E.1–E.4） |

## 四、核心创新点与贡献

1. **首个系统性的格式偏置评估框架**：把格式约束下的评测区分为"合规答案表现"（SysE）与"真实表现"（TrueE），并用 FI Score 归一化得到可自动计算的 EstTrueE，附一致性定理 Thm. 3.1（FI 越低估计越不可靠）。
2. **新的偏置度量 BiasFo**：以 EstTrueE 在 k 种格式上的方差定义偏置，并给出可操作的去偏判据（降低 BiasFo 且提高各格式 FI 使估计可靠）。
3. **大规模实证**：15 种格式 × 8 个任务 × 4 个模型（开源与闭源），揭示 78.30% 的估计结果可靠、Mistral/ChatGPT/Gemma/Llama 各有不同格式短板。
4. **"format token bias" 归因假设**：认为偏置源于预训练中格式 token 的分布不均，使模型对格式指令的理解不均衡；并用微调使其"均衡熟悉格式 token"作为验证。
5. **三种可迁移的缓解手段**：演示示例、重复格式指令、按系统评分反比合成格式数据微调，后者把 wrapping 方差 235.33%² 降到 0.71%²。

## 五、关键词

| 关键词 | 中文 | 在本论文中的重要性 |
| --- | --- | --- |
| Format bias | 格式偏置 | 全文主题：模型表现在不同输出格式下的系统性差异 |
| BiasFo | 格式偏置度量 | 作者定义的指标，= EstTrueE 在多种格式上的方差 |
| EstTrueE / TrueE / SysE | 估计真实评分 / 真实评分 / 系统评分 | 三层评测指标体系，是全自动评估格式偏置的核心工具 |
| Format Instruction-following Score (FI) | 格式指令跟随分数 | 决定 EstTrueE 可靠性的前提（Thm. 3.1） |
| Format token bias | 格式 token 偏置 | 作者对偏置成因的核心假设 |
| MCQ / wrapping / list / mapping | 多项选择问答 / 包裹 / 列表 / 映射 | 四类评估格式；wrapping 涉及加粗、斜体等记号 |
| Placeholder / Bolding / Italicizing | 占位符 / 加粗 / 斜体 | 7 种 wrapping 策略中的代表；加粗与斜体即 Markdown 常见语法 |
| Zero-shot CoT prompting | 零样本思维链提示 | 两条提示基线之一 |
| Synthesized format data | 合成格式数据 | 缓解偏置的微调数据构建方法 |
| MMLU / BBH / GSM8K | — | 主要评测数据（MMLU 与 BBH 为 MCQ） |

## 六、与本课题的相关要素

- **结论方向：支持"格式会系统性改变评测结果"，但仅在 LLM 表现层面**。论文测得模型在 15 种格式上的表现差异巨大（如 Mistral 在 MCQ 上字符标识符 58.69% vs 选项文本 4.22%；wrapping 中 "Quoting" 与 "Parenthesis" 最低），说明"格式"本身是一个未受控时足以颠覆结论的变量——可为课题在引言论证"格式特征必须纳入混淆控制"提供旁证。
- **与课题的差异（引用时必须写明）**：本文的"格式"是任务指令要求的结构性输出约束（包裹记号、列表语法、JSON/YAML 键值结构），与课题的 Markdown 标题/列表/加粗等**自发写作特征**不同；其结局变量是模型答题准确率，不是人类 A/B 选择；因此只能支撑"格式重要"，不能直接支撑"格式特征与人类选择相关"。
- **方法可借鉴处**：(1) 区分"合规表现"与"真实表现"的双指标思路，类比课题中"特征存在与否"的纯度/处理效应拆分；(2) 用 FI 分数为估计量设可靠性门槛（Thm. 3.1），可类比课题匹配诊断/IPW 的假设检验式诊断；(3) 按评分反比构造对照数据（第 6 节）与课题敏感性分析中的匹配/加权去偏思路同构。
- **可直接引用的一手数字**：wrapping 方差 235.33%² → 0.71%²（微调）；FI 72.99% → 99.58%；Mistral MCQ 58.69% vs 4.22%；ChatGPT 两格式差 19.03%；78.30% 的 EstTrue 结果可靠（MCQ 70%、wrapping 82.5%、list 67.19%、mapping 77.08%）；演示示例与重复指令的 BiasFo 172.69%² / 111.78%² / 146.84%²。本文不涉及响应长度维度，故无长度相关数字可引。
- **建议引用位置**：引言（"格式是评测中未受控的混淆变量"、格式跟随基准的出处）；方法（前缀性对照/去偏判据类比）；讨论（模型侧对格式敏感，与人类侧格式偏好形成对照）；局限（本文格式定义与课题不同，只能作旁证）。
- **数据是否同源**：否。本文数据为 MMLU/BBH/GSM8K/FairytaleQA/HotpotQA/SciDocsRR/SemEval2017/SciREX 等能力评测集，与 LMArena / Arena-Human-Preference-140k 无交集，仅可在讨论中作机制对照。

## 七、可引用段落摘录

> 以下句子逐字取自 PDF 文本层（该文双栏排版，抽取文本存在逐行交错，已按句子顺序核对）。

1. **§5.1（可用于"格式混淆影响结论可靠性"）**
   > This emphasizes the necessity of more research in fine-tuning LLMs to reduce format bias and raises concerns about the reliability and reproducibility of recent studies using varied formats.
2. **§5.1（可用于"格式差异可归因于 token 层面偏置"的机制解释）**
   > We hypothesize the root cause of the significant performance bias across different formats is the format token bias of LLMs.
3. **Abstract（可用于概括"格式是普遍现象"）**
   > Our evaluation on eight generation tasks uncovers significant format bias across state-of-the-art LLMs.

## 八、局限与引用注意

- **作者自述**（Limitations）：(1) EstTrueE 与 BiasFo 只是估计量而非精确度量，精确度量需昂贵的人工核查与微调；(2) 受算力与预算限制，格式、数据集与模型范围有限，外推性受限；(3) 只把偏置归因于训练数据的 token 偏置，未探索模型结构与训练过程等更根本的因素。另有 Ethical Considerations 讨论公平性与社会影响。
- **引用风险 — 概念层次**：本文讨论的是 LLM 在格式约束下的**任务准确率**，与课题的**人类偏好选择**属不同结局变量；引用时须明示"格式在模型侧已被证明会改变可测表现"，不可暗示其结论直接适用于人类偏好。
- **引用风险 — 格式定义不同**：本文格式 = 输出结构约束（wrap/list/mapping/JSON/YAML/加粗/斜体），课题格式 = Markdown 标题/列表/加粗的计数特征；"加粗/斜体"虽同时出现在 wrapping 策略中，但语境是"按要求包裹答案"，与"自发使用加粗"不等价。
- **引用风险 — 文本层质量**：该 PDF 为双栏，抽取文本逐行交错，正文数字（如 "Placeholder (37.15%)"、"Quoting (24.58%)"）含义依赖上下文；本笔记中的数字均取自可确证段落，引用前建议回到 PDF 原页核对表格（Appx.-Tab. 6/7/10/14/18）。
- **venue 未确认**：抽取文本仅见 arXiv:2408.08656v2 标识，正文无会议/期刊名；引用时按预印本处理。
- **数字口径**：仓库类指标写作 "(%2)"，实为方差除以 100 的百分平方记号（如 235.33%² → 0.71%²）；引用时建议保留原文记法并说明。
