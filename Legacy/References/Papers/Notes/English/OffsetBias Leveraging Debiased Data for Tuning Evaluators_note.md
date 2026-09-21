# OffsetBias: Leveraging Debiased Data for Tuning Evaluators

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 标题 | OffsetBias: Leveraging Debiased Data for Tuning Evaluators |
| 作者 | Junsoo Park, Seungyeon Jwa, Meiying Ren, Daeyoung Kim, Sanghyuk Choi（前两位共同一作；Sanghyuk Choi 通讯） |
| 机构 | NC Research；NAVER Cloud |
| 出处 | arXiv:2407.06551v2 [cs.CL]，2024-10-07；正文未见会议/期刊标识，venue 未确认 |
| 语言 | 英文 |
| 与课题相关度 | ★★★★☆（系统列举判官模型的六类偏置，含长度偏置的量化阈值与"偏好数据中 chosen 更长"的统计证据，直接支撑长度混淆论述；但对象是 LLM 判官而非人类选择） |
| 原文位置 | `Papers/English/OffsetBias Leveraging Debiased Data for Tuning Evaluators.pdf` |

## 一、三句话概括

1. 论文以逐案错误分析的方式，定性识别出 LLM 判官模型常见的六类偏置：长度偏置、具体性偏置、空引用偏置、内容续写偏置、嵌套指令偏置、熟悉知识偏置，并构建含 80 个手工测试用例的元评测集 EVALBIASBENCH。
2. 作者提出用"离题回答法"与"错误回答法"构造去偏偏好数据集 OFFSETBIAS（8,504 条，坏回答含关键错误但具备判官偏爱的表层风格），通过难度过滤保留难例。
3. 实验显示把 OFFSETBIAS 加入训练可显著提升判官模型在 EVALBIASBENCH 与 LLMBar、HHH-Alignment、MT-Bench Human Judge 等基准上的稳健性，并可用于奖励模型微调，说明"用偏置感知数据抵消既有偏置"是有效路径。

## 二、摘要

**原文（逐字）**

> Employing Large Language Models (LLMs) to assess the quality of generated responses, such as prompting instruct-tuned models or fine-tuning judge models, has become a widely adopted evaluation method. It is also known that such evaluators are vulnerable to biases, such as favoring longer responses. While it is important to overcome this problem, the specifics of these biases remain under-explored. In this work, we qualitatively identify six types of biases inherent in various judge models. We propose EVALBIASBENCH as a meta-evaluation collection of hand-crafted test cases for each bias type. Additionally, we present debiasing dataset construction methods and the associated preference dataset OFFSETBIAS. Experimental results demonstrate that fine-tuning on our dataset significantly enhances the robustness of judge models against biases and improves performance across most evaluation scenarios. We release our datasets and the fine-tuned judge model to public.

**中文翻译**

> 使用大语言模型（LLM）评估生成回答的质量——例如提示经过指令微调的模型或微调判官模型——已成为广泛采用的评测方法。同时也已知这类评估器容易受偏置影响，例如偏爱更长的回答。尽管克服这一问题很重要，这些偏置的具体内容仍研究不足。本文定性识别出各类判官模型中固有的六种偏置，并提出 EVALBIASBENCH——一个针对每种偏置类型的手工测试用例元评测集合。此外，我们给出构建去偏数据集的方法及相应的偏好数据集 OFFSETBIAS。实验结果表明，在我们的数据上微调能显著增强判官模型对抗偏置的稳健性，并在大多数评测场景中提升表现。我们公开数据集与微调后的判官模型。

（完整摘要另见 `OffsetBias Leveraging Debiased Data for Tuning Evaluators_摘要.md`）

## 三、章节结构与内容

| 位置 | 标题（原文） | 内容说明 |
| --- | --- | --- |
| 1 | Introduction | 指出判官模型（专有 LLM 提示式与开源微调式）易受表层风格影响；提出先识别偏置类型（六类）、再构建元评测集（EVALBIASBENCH）与去偏数据（OFFSETBIAS）的路线；列出三条贡献 |
| 2 | Related Work | 2.1 LLM-based Evaluation（LLM-as-a-judge 与微调判官模型）；2.2 Meta-Evaluation Benchmarks and Judge Model Biases（人类偏好基准、已知的长度/位置偏置、对抗式元评测） |
| 3 | Bias of Judge Models | 给出偏置识别四步流程（多基准错误案例 → 提出偏置假设 → 构造同模式新样例 → 若多数模型性能下降则确认）并说明被否决的假设见附录 G。3.1 Identified Bias Types：定义六类偏置——(1) 长度偏置；(2) 具体性偏置（引用权威来源、数值、术语）；(3) 空引用偏置（指令信息不全时偏好幻觉式回答）；(4) 内容续写偏置（偏好续写输入文本而非执行指令）；(5) 嵌套指令偏置（偏好回答嵌入在输入中的问题）；(6) 熟悉知识偏置（偏好常见知识表述）；另单列位置偏置并说明未纳入基准。3.2 Construction of Bias Benchmark：EVALBIASBENCH 含 80 个用例、分 6 类；为使非长度类偏置的效应与长度隔离，先测得"坏/好回答长度比超过 2.0 时长度偏置开始起作用"，据此把成对回答长度控制在彼此两倍以内 |
| 4 | Training Data Construction | 4.1 Bad Response Generation：从 Alpaca、UltraChat、Evol-Instruct、Flan 采样指令，4.1.1 离题回答法（借鉴 GPTInst：用相似但不同的指令，弱模型生成"好"回答、强模型生成更具体但离题的"坏"回答），4.1.2 错误回答法（GPT-4 与 Claude-3-Opus 按五类错误生成坏回答并用 GPT-4 复核）；4.2 Difficulty filtering：用 Base-data 模型与 GPT-3.5-turbo-0125 过滤易例，约剔除 60% 生成实例，最终 8,504 条（离题 3,062 条；错误型 5,442 条，其中 Claude-3-Opus 1,044 条、GPT-4 4,398 条） |
| 5 | Experimental Setup | 5.1 Model Description：以 LLaMA-3-8B-Instruct 微调两个判官（仅 Base-data vs Base-data + OFFSETBIAS），Base-data 为 268k 人类偏好数据（UltraFeedback、HelpSteer、HH-RLHF-Helpful-Online、HH-RLHF-Harmless-Base、PKU-SafeRLHF 子集）；交换 A/B 位置以缓解位置偏置；另用 FsfairX-LLaMA3-RM-v0.1 通过 SLERP 权重合并训练奖励模型。5.2 Benchmarks：生成式判官用 LLMBar、HHH-Alignment、MT-Bench Human Judge；奖励模型用 RewardBench（Chat/Chat Hard/Safety/Reasoning）；并在 EVALBIASBENCH 上分类别评测。5.3 Baselines：GPT-4o-0513、GPT-3.5-turbo-0125、PandaLM、AutoJ、Prometheus-2、Phi-3-medium、Mixtral-8x7B、LLaMA2-Chat-70B、LLaMA3-70B-Instruct，以及 Eurus-RM-7B、Starling-RM-34B、RM-Mistral-7B、FsfairX-LLaMa3-RM |
| 6 | Experimental Results | 6.1 生成模型：OFFSETBIAS 模型在 LLMBar 各子集（Neighbor、GPTInst、Manual）与 HHH 的 Helpful/Honest 上明显提升，位置一致性最高；6.2 奖励模型：Chat Hard 与 Safety/Reasoning 提升、Chat 略降；6.3 EVALBIASBENCH：既有生成式判官几乎每类偏置都表现不佳，奖励模型相对更好，加入 OFFSETBIAS 后两类模型的总体准确率都提升；6.4 Ablation Study：分别去掉位置交换增强、离题法（ORM）、错误法（ERM）——去掉 ORM 使 LLMBar 大幅下降，去掉 ERM 使各基准降低 3–5 个百分点 |
| 7 | Discussion | 讨论 OFFSETBIAS 对偏置类型的覆盖不全（熟悉知识类偏置反而下降），以及"偏好 GPT-4 生成回答"的问题：GPT-4 倾向生成长回答，导致偏好数据中 chosen 普遍长于 rejected，在此数据上训练的判官在长度偏置用例上表现很差；OFFSETBIAS 有意让 rejected 更长，使模型学会不受表层质量影响 |
| 8 | Conclusion | 总结六类偏置、EVALBIASBENCH 与 OFFSETBIAS 的效果；点明只覆盖成对偏好评测 |
| — | Limitations | 自述局限（见第八节） |
| — | Ethical Considerations / Acknowledgments | 数据可能含不当内容但以已发表数据为种子；韩国 IITP 资助说明 |
| 附录 | A–H | A 数据构建提示词；B 训练提示词模板；C 训练细节（含 80k 训练集构成、批大小 128、学习率 1e-5、SLERP 合并比例 0.5、8×A100）；D EVALBIASBENCH 示例与各模型判定；F 长度分布（对比各基线判官训练数据与 OFFSETBIAS 的 chosen−rejected 长度差分布）；G 被否决的偏置假设（含格式/要点式排版偏置、重叠偏置、友善语气偏置）；H 与随机猜测对比的 EVALBIASBENCH 结果。E 部分标题未确认 |

## 四、核心创新点与贡献

1. **六类判官偏置的系统识别**：长度、具体性、空引用、内容续写、嵌套指令、熟悉知识，给出统一的"错误分析—假设—验证"识别流程与反例图例。
2. **EVALBIASBENCH 元评测集**：80 个手工用例（6 类偏置），并用"坏/好长度比 2.0"阈值控制长度混淆，使各偏置效应可分离。
3. **OFFSETBIAS 数据集与两条构造方法**：离题回答法 + 错误回答法，配合难度过滤（剔除约 60%），得 8,504 条"坏回答有错但表层更讨喜"的难例。
4. **去偏数据即插即用**：加入现有训练数据即可提升判官与奖励模型的稳健性；并揭示"GPT-4 生成长回答 → 偏好数据 chosen 更长 → 判官长度偏置"的传导链。
5. **公开资源**：数据集与微调后的判官模型开源（github.com/ncsoft/offsetbias）。

## 五、关键词

| 关键词 | 中文 | 在本论文中的重要性 |
| --- | --- | --- |
| Length bias | 长度偏置 | 六类偏置中最重要的第一类；给出 2.0 长度比阈值 |
| Concreteness bias | 具体性偏置 | 偏好含权威来源、数值、术语的回答 |
| Empty reference bias | 空引用偏置 | 指令信息不全时偏好幻觉式回答 |
| Content continuation bias | 内容续写偏置 | 偏好续写输入文本而非执行指令 |
| Nested instruction bias | 嵌套指令偏置 | 偏好回答输入中嵌入的子问题 |
| Familiar knowledge bias | 熟悉知识偏置 | 偏好常见知识表述 |
| EVALBIASBENCH | — | 80 用例的偏置元评测集 |
| OFFSETBIAS | — | 8,504 条去偏偏好数据集 |
| Judge model | 判官模型 | 被测试与被去偏的对象 |
| Position bias | 位置偏置 | A/B 顺序效应，通过交换位置增强训练数据缓解 |

## 六、与本课题的相关要素

- **结论方向：强支持"长度是评测中已确认的系统性偏置"，并给出可引用的量级与阈值**。"坏/好回答长度比超过 2.0 时长度偏置开始起作用"（§3.2）、以及附录 F "多数现有判官训练数据的 chosen 普遍长于 rejected"，与课题在 Arena 人类数据上观察到的长度-选择关联互为呼应；但本文对象是判官/奖励模型，属 LLM 评审侧证据。
- **传导链可引用于讨论**：§7 明确写出"GPT-4 tends to generate lengthy responses, thus resulted preference datasets tend to contain lengthy chosen responses compared to rejected responses"，说明偏好数据集的长度不对称可能来自数据生成模型而非人类真实偏好——这与课题区分"人类选择 vs 模型生成"的讨论直接相关。
- **格式接口（重要）**：附录 G 的 "Rejected Bias Hypotheses" 中，第一个被否决的假设即 "Format Bias"（Figure 9：模型似乎偏好要点式（bullet-point）排版的回答，但该假设未通过验证）。课题若讨论"Markdown 格式特征是否只是表象"，可直接引用这一"曾被发现但未被确证"的负面证据，说明格式效应需要更严格的混淆控制。
- **方法可借鉴处**：(1) 用长度比阈值（2.0）控制长度与其它变量的混淆，与课题的匹配/分层诊断同构；(2) 交换 A/B 位置以消除位置偏置，对应课题配对检验的对称性处理；(3) 难度过滤（只保留难例）对应课题纯度效应的敏感性分析思路；(4) "按偏置类型分解报告准确率"对应课题分特征、分场景的报告方式。
- **可直接引用的一手数字**：EVALBIASBENCH 80 个用例（换位增强后 n=160；长度类 n=34、具体性 n=28、空引用 n=26、内容续写 n=24、嵌套指令 n=24、熟悉知识 n=24）；OFFSETBIAS 8,504 条（离题 3,062 + 错误型 5,442，其中 Claude-3-Opus 生成 1,044、GPT-4 生成 4,398）；难度过滤剔除约 60% 生成实例；长度比阈值 2.0；Base-data 268k 人类偏好数据；奖励模型训练集 80k（71.5k 补充数据 + OFFSETBIAS）。
- **精度提醒**：Table 1（LLMBar/HHH/MT-Bench 各模型准确率）与 Table 4（EVALBIASBENCH 分模型准确率）在抽取文本中行标签与数值错位，本笔记未引用其中的具体准确率；如需引用（例：+OFFSETBIAS 行的 LLMBar 平均分、EVALBIASBENCH 总分）请回 PDF 原表核对。
- **建议引用位置**：引言（长度偏置是判官模型的公认问题，附量级）；方法（长度比阈值、位置交换、难度过滤的对照做法）；讨论（格式偏置假设被否决——提醒格式效应证据需谨慎）；局限（判官侧证据不能等同于人类 A/B 证据）。
- **数据是否同源**：否。偏好数据为 UltraFeedback、HelpSteer、HH-RLHF、PKU-SafeRLHF 等，评测集为 LLMBar、HHH-Alignment、MT-Bench、RewardBench，与 LMArena/Arena-Human-Preference-140k 无交集；但其"判官训练数据中 chosen 更长"的发现可作为课题讨论长度混淆来源的旁证。

## 七、可引用段落摘录

> 以下句子逐字取自 PDF 文本层（该文双栏排版，已按句子顺序重组；表格行列存在错位，句子本身可直接核对）。

1. **§3.1 Identified Bias Types, Type 1（可用于长度偏置的定义）**
   > A well-known yet significant bias is length bias (Zheng et al., 2024; Huang et al., 2024), which refers to the tendency of judge models to prefer longer responses, regardless of their quality or how well they adhere to the instruction.
2. **§7 Discussion（可用于"偏好数据中 chosen 更长源于生成模型而非人类"）**
   > For instance, GPT-4 tends to generate lengthy responses, thus resulted preference datasets tend to contain lengthy chosen responses compared to rejected responses.
3. **Appendix F Length Distribution（可用于"训练数据的长度不对称"）**
   > For most existing judge models, training datasets show a length difference distribution where more instances have chosen responses longer than rejected responses.

## 八、局限与引用注意

- **作者自述**（Limitations）：(1) 六类偏置依赖经验观察，不能视为穷尽的偏置清单；(2) 偏置本身依赖模型——先进的专有模型对某些偏置更稳健，未来更强的开源模型可能缓解该问题；(3) 讨论指出 OFFSETBIAS 的构造方法未覆盖全部偏置类型（熟悉知识偏置上奖励模型表现反而下降）；(4) 研究只覆盖成对偏好评测，单条打分场景不在范围内。
- **引用风险 — 结论层次**：本文是"判官模型/奖励模型"的偏置诊断与去偏，不是人类偏好的观察性研究；引用其长度偏置结论时须注明对象为 LLM 判官，不能直接支撑"人类偏好中的长度关联"。
- **引用风险 — 文本层表格**：抽取文本中 Table 1 与 Table 4 的行标签与数值明显错位（如 "LLaMA3-8B-Instruct / +Base-data / +OFFSETBIAS" 与各子集分数不在同一行），本笔记因此只引用可确证的流程性数字（用例数、样本数、阈值），未引用任何模型准确率；引用前务必回 PDF 原表核对。
- **引用风险 — 合成数据**：OFFSETBIAS 中"好回答"来自既有数据集、"坏回答"由 GPT-4/Claude-3-Opus 生成，存在合成数据偏差；其"去偏有效"的结论受数据生成模型能力限制。
- **引用风险 — 规模**：Base-data 268k、OFFSETBIAS 8,504，评测集 80 例（换位后 160），规模远小于课题数据；结论方向可引，量级不可迁移。
- **未确认项**：附录 E 的标题、会议/期刊 venue 均未确认（抽取文本仅见 arXiv:2407.06551v2 [cs.CL]，2024-10-07）。
