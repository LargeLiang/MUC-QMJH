# Dissecting Human and LLM Preferences

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 标题 | Dissecting Human and LLM Preferences |
| 作者 | Junlong Li, Fan Zhou, Shichao Sun, Yikai Zhang, Hai Zhao, Pengfei Liu（通讯作者：Pengfei Liu） |
| 机构 | 上海交通大学；上海人工智能实验室；香港理工大学；Generative AI Research Lab (GAIR) |
| 出处 | arXiv:2402.11296v1 [cs.CL]，2024-02-17；正文未见会议/期刊标识，venue 未确认 |
| 语言 | 英文 |
| 与课题相关度 | ★★★★★（直接分解人类与 LLM 的偏好构成，数据与课题同源自 Chatbot Arena，且含 "lengthy" 与 "well formatted" 两个与课题高度对应的属性） |
| 原文位置 | `Papers/English/Dissecting Human and LLM Preferences.pdf` |

## 一、三句话概括

1. 论文提出一个把"整体偏好"分解为若干明确属性的量化框架：用 GPT-4-Turbo 对真实用户对话中的一对回答按 29 个属性打分，再以贝叶斯 logistic 回归拟合属性差异对偏好的贡献强度。
2. 基于 Chatbot Arena Conversations 的场景平衡采样，论文发现人类对错误较不敏感、偏好支持自身立场的回答、厌恶模型"承认能力有限"，而 GPT-4-Turbo 等先进模型更重视正确性、清晰度与无害性；同规模模型偏好相似且对齐微调几乎不改变偏好倾向。
3. 论文进一步证明偏好驱动的评测可被操纵：无论免训练的系统提示还是基于 DPO 的微调，让回答贴近评委偏好可抬分、注入最不受偏好的属性则压低分数，MT-Bench 变动最高 0.59、AlpacaEval 2.0 最高 31.94。

## 二、摘要

**原文（逐字）**

> As a relative quality comparison of model responses, human and Large Language Model (LLM) preferences serve as common alignment goals in model fine-tuning and criteria in evaluation. Yet, these preferences merely reflect broad tendencies, resulting in less explainable and controllable models with potential safety risks. In this work, we dissect the preferences of human and 32 different LLMs to understand their quantitative composition, using annotations from real-world user-model conversations for a fine-grained, scenario-wise analysis. We find that humans are less sensitive to errors, favor responses that support their stances, and show clear dislike when models admit their limits. On the contrary, advanced LLMs like GPT-4-Turbo emphasize correctness, clarity, and harmlessness more. Additionally, LLMs of similar sizes tend to exhibit similar preferences, regardless of their training methods, and fine-tuning for alignment does not significantly alter the preferences of pretrained-only LLMs. Finally, we show that preference-based evaluation can be intentionally manipulated. In both training-free and training-based settings, aligning a model with the preferences of judges boosts scores, while injecting the least preferred properties lowers them. This results in notable score shifts: up to 0.59 on MT-Bench (1-10 scale) and 31.94 on AlpacaEval 2.0 (0-100 scale), highlighting the significant impact of this strategic adaptation.

**中文翻译**

> 作为模型回答之间的相对质量比较，人类与大语言模型（LLM）的偏好既是模型微调中常见的对齐目标，也是评测中的常见准则。然而这些偏好只反映了宽泛的倾向，导致模型可解释性与可控性不足，并带来潜在安全风险。本文分解了人类与 32 个不同 LLM 的偏好以理解其量化构成，使用真实用户—模型对话的标注做细粒度、分场景的分析。我们发现人类对错误较不敏感，偏好支持自身立场的回答，并在模型承认能力有限时表现出明显反感。相反，GPT-4-Turbo 等先进 LLM 更强调正确性、清晰度与无害性。此外，规模相近的 LLM 往往表现出相似偏好，与训练方法无关；对齐微调也不会显著改变仅预训练模型的偏好。最后，我们证明基于偏好的评测可被有意操纵：在免训练与基于训练的两种设置下，使模型贴近评委偏好会抬升分数，而注入最不受偏好的属性会压低分数。这带来显著的分数变动：MT-Bench（1–10 分制）最高 0.59，AlpacaEval 2.0（0–100 分制）最高 31.94，凸显了这种策略性适配的巨大影响。

（完整摘要另见 `Dissecting Human and LLM Preferences_摘要.md`）

## 三、章节结构与内容

| 位置 | 标题（原文） | 内容说明 |
| --- | --- | --- |
| 1 | Introduction | 提出偏好本身缺乏研究、只有二元标签；以 RLHF/DPO 与 LLM-as-a-judge 为背景，列出三条主要发现（人类与先进 LLM 的偏好差异、规模与对齐的影响、评测可被操纵） |
| 2 | Related Work | 三段：偏好数据在训练与评测中的应用；偏好受长度、谄媚、写作风格等特征影响的挑战（含 Sharma et al. 2023、Hosking et al. 2023 的回归式分析对照）；既有偏好理解与演示工作 |
| 3 | Preference Dissection | 方法章。3.1 High-level Methodology：标注属性满足度（0–3 Likert）→ 比较两回答得 +1/0/−1 特征 → 贝叶斯 logistic 回归权重即"效应强度"；3.2 Dataset：取 Chatbot Arena Conversations，过滤 Tie/Both Bad 与多轮，做场景平衡采样（unsafe 400 条，Knowledge-Aware 与 Others 各 820 条，其余 8 个场景各 400 条）；3.3 Collecting Preferences：人类偏好直接取自原数据，另用 2 个闭源 + 30 个开源 LLM 采集 32 份 LLM 偏好，用 "A/B" 首 token log-prob 并按交换位置平均以消除位置偏置；3.4 Pre-defined Properties and Annoatation：定义 29 个属性（21 个 basic、5 个 query-specific、3 个 error detection 严重度），"well formatted" 明确界定为使用要点、编号列表、表格、标题等排版元素；标注一致性 93.1%（basic）、85.1%（错误检测）等；3.5 Calculating Effect Strengths of Properties：Laplace 先验 scale 0.1、NUTS 采样 4 链 × 6,000 后验样本、10 折聚合 |
| 4 | Analysis and Application | 结果章。4.1 Which Properties are Most or Least Preferred by Human and GPT-4-Turbo?：4.1.1 定义偏好度 P(p) 为"仅在该属性上更优时被选中的概率"，>50% 偏好、<50% 反感；4.1.2 人类与 GPT-4-Turbo 在部分场景 top-3 相同（Creative Writing、Daily Tasks 等），但人类对严重错误更不敏感（Table 4：人类 62.86 vs GPT-4-Turbo 76.19）、厌恶 "admit limits"、偏好支持自身立场；GPT-4-Turbo 更重视 correctness、clarity、harmlessness。4.2 How similar are the preferences of different LLMs?：以各场景回归权重的平均 Pearson 系数定义相似度，同规模模型组内相似度（<14B 0.83、>30B 0.88）高于组间（0.74）；对齐微调前后偏好相似度高（多数 0.88–0.96），但 A/B 首 token log-prob 差大幅上升。4.3 Can Preference-based Evaluation be Intentionally Manipulated?：4.3.1 基准为 AlpacaEval 2.0（805 查询）与 MT-Bench（80 段两轮对话，只报第一轮）；4.3.2 免训练（system message 注入 top/last-3 属性，含 80 查询的人类评委子集）与基于训练（用回归模型标 DPO 数据，GPT-3.5-Turbo 4,022 条、GPT-4-Turbo 3,991 条）；4.3.3 结果：贴近评委偏好抬分、反向压低分数，针对 GPT-3.5-Turbo 效果更强，人类评委下仍有效（如 GPT-4-Turbo 模型 AlpacaEval 胜率 50.00 → 81.94、反向 22.08） |
| 5 | Conclusion | 人类"直接解决问题"优先且对错误不敏感，先进 LLM 更重正确/清晰/无害；模型规模是偏好的区分因素；对齐不改变偏好倾向；LLM-as-a-judge 基准脆弱；公开全部资源 |
| 6 | Limitation and Future Work | 自述局限（见第八节） |
| 附录 | A–K | A 各属性标注提示词；B 场景定义；C 所选开源模型清单（含基座与对齐方式）；D 标注样例；E 数据集统计（各属性均值、属性相关性）；F query-specific 属性评分换算；G 人工标注质量核查统计；H 比较特征构建规则；I 回归拟合细节；J 各评委拟合模型准确率（人类 78.12、GPT-4-Turbo 86.79 等）；K 附加分析结果（完整 top/last-3 表与偏好相似度图） |

## 四、核心创新点与贡献

1. **偏好分解框架**：把二元偏好标签分解为 29 个属性的定量组合（贝叶斯 logistic 回归权重 = 效应强度），并用"P(p) = 仅该属性更优时被选中的概率"给出可解释、可排序的偏好度。
2. **人类 vs LLM 偏好的直接对照**：同一批真实对话上比较人类与 32 个 LLM，发现人类对错误不敏感、偏好立场支持与"不认输"，先进 LLM 更重正确性/清晰度/无害性。
3. **模型规模与对齐的效应**：同规模模型偏好相似（组内 0.83/0.88 > 组间 0.74），对齐微调几乎不改变偏好倾向，只增强表达强度。
4. **评测可被操纵的实证**：免训练与 DPO 两条路径都能按评委偏好"定制"分数，MT-Bench 最高 ±0.59、AlpacaEval 2.0 最高 31.94，揭示 LLM-as-a-judge 基准的脆弱性。
5. **资源公开**：数据（GAIR/preference-dissection）、代码与可视化 demo 全部开源。

## 五、关键词

| 关键词 | 中文 | 在本论文中的重要性 |
| --- | --- | --- |
| Preference dissection | 偏好分解 | 全文核心：把整体偏好拆成属性贡献 |
| Bayesian logistic regression | 贝叶斯 logistic 回归 | 拟合属性差异→偏好标签，权重即效应强度 |
| Chatbot Arena Conversations | — | 原始数据来源（真实用户双模型对话与选择） |
| Degree of preference | 偏好度 | 属性层面的可解释指标（50% 为中性线） |
| Well formatted | 格式良好 | 属性之一，定义为使用要点/编号列表/表格/标题等排版元素，与课题 Markdown 特征直接对应 |
| Lengthy | 冗长 | 属性之一（以 NLTK 词数直接度量）；Figure 1 中人类在 Communication 场景最偏好的属性 |
| Scenario-wise analysis | 分场景分析 | 避免不同场景偏好混合，10 个场景 + unsafe + query-specific 子集 |
| Admit limits | 承认能力有限 | 人类明显反感的属性 |
| LLM-as-a-judge | 以 LLM 为评委 | 被证明可被操纵的评测范式 |
| Position bias | 位置偏置 | 采集 LLM 偏好时通过交换 A/B 位置取平均来消除 |

## 六、与本课题的相关要素

- **结论方向：支持并细化"人类偏好由可量化文本属性驱动"**。论文以人类与 32 个 LLM 为对象，给出属性层面的偏好度（>50% 偏好、<50% 反感），其中 "lengthy" 在 Communication 场景被 Figure 1 标注为人类最偏好的属性——可直接支撑课题"长度与人类选择正相关"的观察，并提示该关联具有场景异质性（论文强调偏好构成随场景/查询类型差异很大）。
- **格式接口**：属性 "well formatted" 的原文定义涵盖 "bullet points, numbered lists, tables, and headings" 与结构化数据格式，与课题的 Markdown 标题/列表/加粗特征几乎一一对应；Table 9 给出该属性在数据中的均值（1.26，0–3 量表）。课题可引用其属性定义作为"格式特征"操作化的旁证，并指出课题进一步把它做成计数特征并纳入回归控制。
- **方法可借鉴处**：(1) 以"配对比较特征 + 回归权重"量化属性贡献，与课题 logistic 回归中特征系数的解释框架同构；(2) 通过交换 A/B 位置取平均消除位置偏置，对应课题配对检验中的对称性处理；(3) 过滤 Tie/Both Bad 只保留明确胜负，与课题保留 78,959 对明确胜负的口径一致；(4) 分场景（strata）分别拟合，对应课题控制任务类别的分层/固定效应思路。
- **人类 vs 模型偏好差异可直接引用**：人类对错误更不敏感（Table 4 no severe errors：人类 62.86、GPT-4-Turbo 76.19、其余最高 65.27）、人类偏好立场支持与直接答疑、反感 "admit limits"；GPT-4-Turbo 更重正确/清晰/无害。可用于课题讨论"人类偏好不等于质量"。
- **可引用的一手数字**：MT-Bench 最高 0.59、AlpacaEval 2.0 最高 31.94（操纵幅度）；GPT-4-Turbo 模型在 AlpacaEval 2.0 上 50.00 → 81.94 / 22.08；同规模组内相似度 0.83、0.88 vs 组间 0.74；拟合模型准确率人类 78.12、GPT-4-Turbo 86.79；标注一致性 93.1% / 85.1% / 94.8% / 85.5%。
- **数据同源**：是（同一 Arena 家族）。本文原始数据为 Chatbot Arena Conversations（Zheng et al., 2023），与课题的 LMArena/Arena-Human-Preference-140k 同源同机制（真实用户与两个模型对话后投票）；但本文为场景平衡采样的小样本（未给出合计数字，按正文各场景条数推算约 5.2k），且只保留单轮、过滤 Tie/Both Bad，不能与课题数据合并，只能作为同源不同子集的方法与结论对照。
- **建议引用位置**：引言（人类偏好可由文本属性分解、"格式良好"属性的定义出处）；方法（配对比较特征、交换位置去偏、过滤 tie 的口径）；讨论（人类与模型偏好差异、评测可被操纵、关联≠因果的旁证）；局限（其样本量与场景平衡采样与课题全量数据不同）。

## 七、可引用段落摘录

> 以下句子逐字取自 PDF 文本层（该文单栏排版，正文表格存在字体编码偏移，句子本身可直接核对）。

1. **§3.2 Dataset（可用于说明数据同源于 Chatbot Arena）**
   > It is collected from a public platform where users can freely converse with two models simultaneously and select a preferred one.
2. **§4.1.2 Results（可用于"人类偏好不等于质量/人类与 LLM 偏好差异"）**
   > Humans also prefer responses that support their subjective stances (known as sycophancy), and pay little attention to how well a response corrects the mistakes or biases in queries.
3. **§4.3.3 Results（可用于"偏好型评测脆弱、分数可被策略性操纵"）**
   > Generally, we find that in both training-free and training-based settings, adapting model responses to align with or diverge from judge preferences results in corresponding improvements or reductions in scores.

## 八、局限与引用注意

- **作者自述**（§6）：(1) 需要首 token log-prob 的采集方式不适用于不返回 log-prob 的闭源模型（如 Gemini、Claude）；(2) 贝叶斯 logistic 回归假设各属性独立影响偏好，可能遗漏属性间交互；(3) 预设属性与标注提示词的设计耗时费力，未来可自动发现属性；(4) 只研究单轮对话。
- **引用风险 — 偏好采集方式**：LLM 偏好取自首 token "A/B" 的 log-prob（而非生成式评判），与课题所研究的"人类 A/B 点击"机制不同；引用其 LLM 侧数字时应写明口径。
- **引用风险 — 标注由 LLM 完成**：29 个属性的 Likert 评分由 GPT-4-Turbo 自动标注（人工抽查一致率 93.1% 等），"属性满足度"本身带模型偏差；不宜把其属性均值当作金标准数据。
- **引用风险 — 文本层缺陷**：Table 3/13（top/last-3 属性表）在抽取文本中出现字体编码偏移（字符整体位移，如 "OHQJW\" = "lengthy"、"ZHOOIRUPDWWHG" = "well formatted"），表内排序不可直接引用；本笔记只引用 Figure 1 图注与正文明确表述。引用具体排序前须回 PDF 原图核对。
- **引用风险 — 样本规模与代表性**：正文只给出各场景采样条数（400/820/400），未见合计数字；相对课题的 135,634 条输入规模小两个数量级，且为场景平衡采样（非自然分布），比例类结论不可直接迁移。
- **venue 未确认**：抽取文本仅见 arXiv:2402.11296v1 标识，正文无会议/期刊名；引用时按预印本处理。
- **代际差异**：论文的"先进 LLM"以 GPT-4-Turbo 为代表（2024 年初），与课题所涉模型代际不同，讨论时宜标注时间。
