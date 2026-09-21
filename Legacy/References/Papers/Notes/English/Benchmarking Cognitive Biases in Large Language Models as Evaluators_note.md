# Benchmarking Cognitive Biases in Large Language Models as Evaluators

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 标题 | Benchmarking Cognitive Biases in Large Language Models as Evaluators |
| 作者 | Ryan Koo, Minhwa Lee, Vipul Raheja, Jonginn Park, Zae Myung Kim, Dongyeop Kang |
| 机构 | University of Minnesota；Grammarly |
| 出处 | arXiv:2309.17012v3 [cs.CL]，2024-09-25（预印本；正文未见会议/期刊标识，venue 未确认） |
| 语言 | 英文 |
| 与课题相关度 | ★★★★☆（提供 SALIENCE BIAS 即长度偏置的量化基准、且给出"人类 vs 模型偏好一致性"的 RBO 度量（44%）与人类自身的偏置比例；但评审对象是模型评审而非真实人类 A/B 选择） |
| 原文位置 | `Papers/English/Benchmarking Cognitive Biases in Large Language Models as Evaluators.pdf` |

## 一、三句话概括

1. 论文构建 **COBBLER**（COgnitive Bias Benchmark for LLMs as EvaluatoRs）基准，让 16 个不同规模（3B 至 >175B）的 LLM 互为评审、对 50 条 QA 指令生成的回答做两两偏好排序，并测量六种认知偏置（隐式：ORDER、COMPASSION FADE、EGOCENTRIC、SALIENCE；诱导：BANDWAGON、ATTENTIONAL）。
2. 结果表明 LLM 是"有偏的文本质量评审者"：所有模型在每个偏置基准上都有约 ≥40% 的判定显示出强偏置迹象；模型规模变大并不能消除隐式偏置。
3. 论文同时做了人类对照：模型评审与人类偏好的平均 Rank-Biased Overlap（RBO）仅 **0.44**，而人类标注者之间为 0.54；人类自身也有偏置但总体弱于 LLM，因此作者认为 LLM 尚不适合作为与人类偏好对齐的自动标注者。

## 二、摘要

**原文（逐字）**

> Large Language Models (LLMs) have recently been shown to be effective as automatic evaluators with simple prompting and in-context learning. In this work, we assemble 16 LLMs encompassing four different size ranges and evaluate their output responses by preference ranking from the other LLMs as evaluators, such as System Star is better than System Square. We then evaluate the quality of ranking outputs introducing the COgnitive Bias Benchmark for LLMs as EvaluatoRs (COBBLER)1, a benchmark to measure six different cognitive biases in LLM evaluation outputs, such as the EGOCENTRIC bias where a model prefers to rank its own outputs highly in evaluation. We find that LLMs are biased text quality evaluators, exhibiting strong indications on our bias benchmark (≥ 40% of comparisons made by all models) within each of their evaluations that question their robustness as evaluators. Furthermore, we examine the correlation between human and machine preferences and calculate the average Rank-Biased Overlap (RBO) score to be 44%, indicating that machine preferences are misaligned with humans. According to our findings, LLMs may still be unable to be utilized for automatic annotation aligned with human preferences.

**中文翻译**

> 大语言模型（LLM）近来已被证明可借助简单提示与上下文学习充当有效的自动评估者。本文汇集了覆盖四个不同规模区间的 16 个 LLM，让它们互为评审、以偏好排序的方式评价彼此的输出回答，例如"System Star 优于 System Square"。随后我们引入 COBBLER（面向 LLM 评审的认知偏置基准），用以测量 LLM 评估输出中的六种认知偏置，例如 EGOCENTRIC（自我中心）偏置——模型倾向于在评估中把自己的输出排在前面。我们发现 LLM 是有偏的文本质量评审者：在所有模型各自的评估中，都有约 **≥40%** 的比较在我们的偏置基准上显示出强烈偏置迹象，这令其评审的稳健性受到质疑。此外，我们考察了人类偏好与机器偏好的相关性，算出平均 Rank-Biased Overlap（RBO）分数为 **44%**，表明机器偏好与人类并不一致。依据我们的发现，LLM 可能仍无法被用于与人类偏好对齐的自动标注。

（完整摘要另见 `..._摘要.md`）

## 三、章节结构与内容

| 位置 | 标题（原文） | 内容说明 |
| --- | --- | --- |
| 1 | Introduction | 提出 LLM-as-evaluator 的既有缺陷（偏好长输出、偏好与自身风格相近的输出），引出 COBBLER 与六种偏置，说明"有偏/无偏偏好"指的是类人偏置在模型中被放大，而非要求完全公正；列出三条贡献。 |
| 2 | Related Work | 三条线：LLMs as Evaluators（GPT-4/ChatGPT 与 reference-free 评价、GPTSCORE、LLM-as-a-judge）、LLM Evaluation Benchmarks（LM-Eval-Harness、MMLU、HELM、BIG-bench 只测能力不测评审）、Cognitive Biases in LLMs（示例顺序效应、GPT-3/Codex 的类人认知失败）。 |
| 3 | COBBLER: Cognitive Bias Benchmark for LLMs as Evaluators | 基准章。给出三条筛选准则：General Applicability、Impartiality、Memorylessness；并把偏置分为隐式与诱导两类，Table 1 给出六种偏置的定义与示例。 |
| 3.1 | Implicit Biases | 四种隐式偏置：**Order Bias**（按位置偏好，两序各测一次）、**Compassion Fade (Naming)**（真实模型名 vs 匿名别名的差异）、**Egocentric Bias (Self-Preference)**（偏好自己的回答）、**Salience Bias (Length)**（按 token 长度偏好，无偏评审应在长短之间均分）。 |
| 3.2 | Induced Biases | 两种诱导偏置：**Bandwagon Effect**（插入"85% 的人认为某系统更好"的假统计）、**Attentional Bias (Distraction)**（插入"System Star 喜欢吃橙子和苹果"之类的无关信息）；期望无偏评审被影响的比例约 25%（随机阈值）。 |
| 4 | Experiment Setup | 实验设置。 |
| 4.1 | Datasets and Models | 数据：ELI5 与 BIG-bench strategyQA 各取 25 条，共 50 条 QA 指令；模型：16 个（>100B：GPT-4、ChatGPT、InstructGPT；>40B：LLaMA2、LLaMA、Cohere、Falcon；>10B：Alpaca、Vicuna、OpenAssistant；<10B：Mistral-Instruct、OLMO、Baize、Koala、WizardLM、MPT）。 |
| 4.2 | Text Evaluation Setting | 流程：50 条指令生成 800 条回答 → 每对通过匿名化两两比较，共 105 个唯一对、每评审 5250 个样本；**每对用两种顺序各跑一次**以验证行为一致性；另做 4 模型列表排序（发现 <40B 模型多数无法产出有效排序）。以随机选择计算"偏置阈值"作 litmus test，附录 B.5 用两样本比例 Z 检验判断显著性。 |
| 4.3 | Human Preference Study | 人类对照：6 名 AMT 工作者做 N=13 的列表排序（共 300 条标注）；另对 ORDER、SALIENCE、BANDWAGON、ATTENTIONAL 四种偏置各招募 75 名工作者、每种偏置 750 对；用 RBO 作为标注者间一致性（IAA）与"人–机一致性"的统一度量。 |
| 5 | Results and Discussion | 结果与讨论。 |
| 5.1 | Bias Analysis | 隐式偏置：ORDER 上 11/15 模型倾向固定位置（>40B 组首序偏好超过 50%）；COMPASSION FADE 上所有模型受真实模型名显著影响；EGOCENTRIC 上最大模型与 Koala 偏好自身回答 >50%（InstructGPT 例外），换成真实模型名后 Koala 的自我偏好上升 100%；SALIENCE 上第一、二规模组的较大模型更偏好长回答，较小模型受影响较小。诱导偏置：11/15 模型受 BANDWAGON 严重影响，平均 >70% 的评估跟随假统计；ATTENTIONAL 上约半数模型受影响，>10B 组 >80%，而 ChatGPT、Cohere 等 API 模型较稳健。作者提醒 LLAMA2、LLaMA、Koala、OLMO 因有效回答率过低而结果异常，其结论只适用于能产出有效评估的模型。 |
| 5.1.1 | Identifying Egocentric and Salience Bias | 混淆解耦：先用 Table 3 看条件于生成质量后的长/短偏好（多数模型保持一致，个别翻转），再用 BERTScore 计算生成质量（各模型 F1 在 **0.81–0.86**），据此论证 EGOCENTRIC 与 SALIENCE 的识别"最可能不依赖生成质量"。 |
| 5.2 | Agreement Between Human Preferences and Model Evaluations | 人–机一致性：6 名标注者间平均 RBO **0.54**，人–机平均 RBO **0.44**；按规模看 >40B 为 0.49、>100B 为 0.48，而小于 10B 为 0.37、大于 10B 为 0.41；标注者两两 RBO 方差仅 0.004，均高于人–机一致性。配对人类实验的平均 RBO 为 0.39（ORDER）、0.50（BANDWAGON）、0.43（ATTENTIONAL）；Table 4 对比人类与 Vicuna 的偏置比例（人类 ORDER 0.20 / SALIENCE 0.52 / BANDWAGON 0.47 / ATTENTIONAL 0.35；Vicuna 对应 0.32 / 0.53 / 0.81 / 0.78），人类有偏但平均弱于 LLM。 |
| 6 | Conclusion | 16 个 LLM 在 QA 场景下作为自动质量标注者的适配性不足；将来可用 chain-of-thought 或对齐方法减偏。 |
| Limitations | Limitations（无编号） | 作者自述三条局限（见第八节）。 |
| 附录 | A–D | A：实验设置（超参 max new tokens 128、temperature 1.0、重复惩罚 1.2、beam 3；Microsoft Guidance / HuggingFace transformer 管线；GPU 规格；ELI5 与 strategyQA 数据集介绍）；B：补充结果（B.1 BANDWAGON 与统计数值的相关性、"0% 的人偏好…"反向实验；B.2 多维度提示词；B.3 引入 Tie 选项；B.4 解耦 EGOCENTRIC 与 SALIENCE 的"hierarchical rubric"与长短获胜统计；B.5 ORDER 上的两样本比例 Z 检验；B.6 LLM 之间的 RBO 与有效回答率；B.7 模型规模影响）；C：六类偏置的完整提示词模板（C.1 Order、C.2 Compassion Fade、C.3 Bandwagon Effect、C.4 Attentional Bias 与 Attentional Bank、C.5 Diverse Prompt、C.6 Tie Prompt）；D：人类偏好研究（D.1 标注者招募与流程、D.2 RBO 定义与参数 p≈0.8、D.3 配对实验细节、D.4 补充结果、D.5 界面设计）。 |

## 四、核心创新点与贡献

1. **提出 COBBLER 基准**：首个把"LLM 作为评审"的六种认知偏置（4 隐式 + 2 诱导）系统化、可复现地量化的基准，覆盖 16 个模型共约 630K 次比较。
2. **以随机选择为 litmus test 的判定方式**：为每种偏置给出明确的无偏期望（如 ORDER 0.24/0.25、EGOCENTRIC 0.5、BANDWAGON/ATTENTIONAL 0.25），使"有偏/无偏"有可检验的参照，并用两样本比例 Z 检验给出显著性。
3. **双序设计排除位置混淆**：每个两两比较在两种顺序下各跑一次，只有两次都选同一系统才计为 ORDER 偏置——这是"用配对设计识别系统性偏好"的干净范式。
4. **人–机偏好一致性的统一度量**：以 RBO（对 top-k 加权，本文按 Webber et al. 2010 把 86% 权重集中在 top 5）同时度量标注者间一致性与人–机一致性，得到人–机 RBO 0.44 vs 人–人 0.54 的直接对照。
5. **显式处理偏置之间的混淆**：B.4 用 hierarchical rubric（先判 ORDER，若命中则不再判 SALIENCE/EGOCENTRIC）+ BERTScore 质量对照 + Table 11 的长短获胜统计，论证 salience 与 egocentric 的可分性，并坦承 ChatGPT 等强模型的"自我偏好"可能是因为其回答确实更好。

## 五、关键词

| 关键词 | 中文 | 在本论文中的重要性 |
| --- | --- | --- |
| COBBLER | — | 论文提出的认知偏置基准本体 |
| Salience bias (length) | 显著度偏置（长度） | 六种偏置中与课题长度特征直接对应的一个 |
| Egocentric bias (self-preference) | 自我中心偏置（自我偏好） | 与课题"模型身份"控制项直接相关 |
| Order bias | 顺序偏置 | 两两比较的固有位置效应，双序设计的原因 |
| Compassion fade (naming) | 同情衰减（命名效应） | 匿名 vs 真实模型名对评审的影响 |
| Bandwagon effect | 从众效应 | 诱导偏置之一，假统计即可改变判定 |
| Attentional bias (distraction) | 注意偏置（分心） | 诱导偏置之一，无关信息即可改变判定 |
| Rank-Biased Overlap (RBO) | 排名偏置重叠度 | 人–人（0.54）与人–机（0.44）一致性的统一度量 |
| Random threshold | 随机阈值 | 判定"是否偏置"的基准线（如 ORDER 0.24/0.25） |
| Implicit / Induced bias | 隐式 / 诱导偏置 | 论文的两大偏置分类框架 |

## 六、与本课题的相关要素

- **结论方向（支持课题的核心立场：选择受与质量无关的表面特征影响）**：SALIENCE BIAS 被定义为"the tendency to prefer responses based on the length of the response"，无偏评审应在长短之间均分，随机阈值为 **0.25**；实测中多数模型对长回答的偏好显著高于随机（Table 2、Table 3），且"larger models in the first and second size groups are more strongly affected by longer responses"。这为课题"长度与选择正相关"提供独立的第三方证据。
- **可直接引用的关键辩护句（最贴近课题"关联≠因果"的表述）**：5.1 节明确承认 "For models such as ChatGPT, the EGOCENTRIC BIAS may be unfair because their generations are indeed better, or in SALIENCE, the longer generations indeed have higher quality."（见第七节），随后 5.1.1 用 BERTScore 对照（各模型生成质量 F1 **0.81–0.86**，彼此接近）来论证偏置识别"not dependent on generation quality"。这正是课题"匹配诊断"逻辑的同类做法，可作为方法论先例引用。
- **方法可借鉴处 1——双序 / 配对设计消除位置混淆**：每对在两种顺序下各测一次，只有两次同选一个系统才计为偏置。课题的 A/B 数据本身含 position 信息，可对照说明课题为何需要在回归中控制提示词属性（含位置相关属性）。
- **方法可借鉴处 2——人类–模型偏好一致性度量**：RBO（对 top-k 加权；本文把 86% 权重压在 top 5 位置、参数 p≈0.8）给出人–机 **0.44** vs 人–人 **0.54** 的量化反差。课题若需报告"模型偏好与人类偏好的对齐度"，RBO 是可直接引用的指标名与先例；同时 0.44 这一数字可作为"LLM 评审不能替代人类偏好"的引证。
- **方法可借鉴处 3——偏置叠加的分层判定**："hierarchical rubric"（若某评估已显示 ORDER 偏置，则不再用它判定 SALIENCE 或 EGOCENTRIC）是处理"多重表面特征互相混淆"的现成思路，与课题同时纳入长度与 Markdown 格式两类特征时的共线性问题直接相关。
- **人类自身也有偏置，且各项强度不同（课题讨论可用）**：Table 4 人类偏置比例为 ORDER **0.20**、SALIENCE **0.52**、BANDWAGON **0.47**、ATTENTIONAL **0.35**，均高于或接近随机阈值但**平均低于 LLM**（同表 Vicuna 为 0.32 / 0.53 / 0.81 / 0.78）。这说明"人类偏好中存在系统性成分"并非模型独有——支持课题把人类选择建模为"含可观测系统性成分的观察性结果"。
- **模型规模的边界条件**：>40B（0.49）与 >100B（0.48）的人–机 RBO 高于 <10B（0.37）与 >10B（0.41）；但"scaling model size does not reduce implicit biases in evaluators"。课题在按模型身份分层时，可引用该规模效应说明模型身份确会调节行为。
- **数据同源性**：**不同源**。本文数据为自建 50 条 QA 指令（ELI5 + BIG-bench strategyQA）× 16 模型生成的 800 条回答，评审为 16 个 LLM，人类侧为 AMT 众包（N=13 列表排序 6 人 / 配对实验每偏置 75 人），与课题的 LMArena / Arena-Human-Preference-140k（135,634 条输入、108,154 条保留、78,959 对明确胜负）在平台、规模、任务分布上均不同，不可合并数据。
- **建议引用位置**：引言（LLM 评审存在长度等技术性偏置、以及自动评审被用于替代人工标注的背景）；方法（双序配对设计、分层判定混淆、RBO 作为一致性指标的依据）；讨论（关联≠因果：长回答可能确实更好，故需质量对照；人类偏好同样含偏置成分；人–机偏好差异 0.44 vs 0.54）；局限（本文人类样本极小、且其"人类偏好"是 AMT 评测 LLM 输出而非真实使用场景的自由选择）。

## 七、可引用段落摘录

> 以下句子逐字取自 PDF 文本层（该文双栏排版且存在逐行交错，已按句子顺序重组并逐句核对）。

1. **§3.1 Implicit Biases（可用于方法：长度偏置的操作化定义与无偏参照）**
   > The evaluator tends to favor responses that are either shorter or longer in length. An unbiased evaluator would be split evenly between responses that are shorter or longer in length.
2. **§5.1 Bias Analysis（可用于讨论"关联≠因果"：长回答可能确实质量更高，故偏置判定需控制质量）**
   > For models such as ChatGPT, the EGOCENTRIC BIAS may be unfair because their generations are indeed better, or in SALIENCE, the longer generations indeed have higher quality. For further insight in decoupling these factors, we include supplementary experiments viewed in Appendix B.
3. **§5.1.1（可用于讨论：用质量度量对照后，偏置识别不依赖生成质量）**
   > From this, all models produce nearly the same quality of generations with respect to the reference answer (0.81 to 0.86 for F1), highlighting that identifying EGOCENTRIC or SALIENCE bias is most likely not dependent on generation quality.
4. **Abstract（可用于引言：人–机偏好不一致的直接数字）**
   > Furthermore, we examine the correlation between human and machine preferences and calculate the average Rank-Biased Overlap (RBO) score to be 44%, indicating that machine preferences are misaligned with humans.

## 八、局限与引用注意

- **作者自述局限（Limitations 节，无编号）**：三条——(1) 部分模型有效回答率极低，可能源于提示格式，若改用模型专属提示或可取得更清晰结果；(2) 人类判断研究中的 IAA 偏低（作者归因于让 AMT 标注者排序 15 个模型过于困难）；(3) 结论的长期稳定性存疑——模型能力随时间快速提升，旧模型（如已被下线 API 的 INSTRUCTGPT）的结果会迅速过时。
- **人类侧样本规模极小、场景受限**：N=13 列表排序仅 **6 名** AMT 工作者、共约 300 条标注；配对偏置实验每偏置 **75 名**工作者、每偏置 750 对（并注明"SLIENCE BIAS were computed using the annotations from ORDER BIAS experiments"）。人类偏好是在**评测 LLM 输出**的任务中收集的，与课题中真实用户对两个模型回答的自发选择场景不同，**其人类偏置比例（0.20/0.52/0.47/0.35）不可直接当作课题人类行为参数的参照值**。
- **有效回答率是重大干扰**：LLAMA2、LLaMA、Koala、OLMO 在多数组基准上结果异常，作者自述"we only apply our findings to ones that produced valid evaluations"。引用某些模型的具体偏置数值前，应先核对附录 B 的 Table 12（有效回答率）。
- **多组数字存在口径差异，引用需谨慎**：(1) 摘要写"≥40% of comparisons"，但 Table 2 各模型数值差异极大（如 GPT4 在 ORDER-Second 为 0.06、Koala 在 Attentional 为 0.52），**"40%"是跨偏置/跨模型的整体印象值而非统一门槛**；(2) 摘要的"16 LLMs"在正文中写作"all 15 choose 2 unique pairs"并脚注说明 LLAMAV2 是后加入的（它单独评了 16 choose 2 对），涉及模型数时应核对口径；(3) 摘要中"≥"符号在文本层被丢失（抽取为 "( 40%"），本文按上下文与 Fig. 2 的随机阈值判定为 ≥，如用于逐字引用请先核对 PDF。
- **显著性检验的边界**：附录 B.5 的作者自述 p-value "critically small (z-scores are blown up) due to our large sample size"，即显著性主要来自样本量；同时明确指出 InstructGPT 的 last-order 偏置**并不显著**，"one must consider the test for both positions"。
- **venue 未确认**：抽取文本中除 arXiv 标识外未见任何会议/期刊信息，引用时建议按 arXiv 预印本（arXiv:2309.17012v3）著录。
- **结论层次**：本文的对象是 **LLM 评审者（LLM-as-evaluator）**，其核心主张是"模型评审不可靠、与人类偏好不一致"；课题研究的是**人类**的 A/B 选择行为。引用其"人类偏置比例"时须写明这是 AMT 在特定评测任务下的表现，不能等同于课题的人类样本；引用其"长度偏置"时须写明对象是模型评审，可用于说明长度是公认的表面特征，但不能直接支撑课题人类侧的效应量。
