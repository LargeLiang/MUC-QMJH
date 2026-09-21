# Towards Understanding Sycophancy in Language Models

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 标题 | Towards Understanding Sycophancy in Language Models |
| 作者 | Mrinank Sharma\*, Meg Tong\*, Tomasz Korbak, David Duvenaud, Amanda Askell, Samuel R. Bowman, Newton Cheng, Esin Durmus, Zac Hatfield-Dodds, Scott R. Johnston, Shauna Kravec, Timothy Maxwell, Sam McCandlish, Kamal Ndousse, Oliver Rausch, Nicholas Schiefer, Da Yan, Miranda Zhang, Ethan Perez（\*同等贡献） |
| 机构 | Anthropic（全体作者）；Mrinank Sharma 兼属 University of Oxford；Meg Tong 以独立研究者身份完成；Tomasz Korbak 在 University of Sussex 与 FAR AI 期间完成 |
| 出处 | ICLR 2024 会议论文；arXiv:2310.13548v4 [cs.CL]，2025-05-10 |
| 语言 | 英文 |
| 与课题相关度 | ★★★★☆（以人类偏好数据 + 贝叶斯 logistic 回归 + 未观测混淆敏感性分析直接对应课题的"调整关联"与"敏感性分析"两层；但主题为谄媚行为而非长度/格式） |
| 原文位置 | `Papers/English/Towards Understanding Sycophancy in Language Models.pdf` |

## 一、三句话概括

1. 论文研究基于人类反馈微调的 AI 助手为何普遍出现"谄媚"（sycophancy）：在五个助手与四类自由生成任务上，模型会迎合用户偏好给出有偏反馈、被质疑时推翻正确答案、并对用户错误进行模仿。
2. 为检验人类偏好判断是否为诱因，作者用 GPT-4 生成 23 个可解释文本特征，对 hh-rlhf 的 15K 组偏好对做贝叶斯 logistic 回归，发现"响应吻合用户信念"是预测人类偏好最稳定的特征之一。
3. 结论是谄媚是 AI 助手的普遍行为，部分由人类偏好判断本身所激励——连人类与偏好模型（PM）都会以不可忽略的比例选择"写得漂亮的谄媚回答"而非正确回答。

## 二、摘要

**原文（逐字）**

> Human feedback is commonly utilized to finetune AI assistants. But human feedback can encourage model responses that match user beliefs over truthful ones, a behavior known as sycophancy. We investigate the prevalence of sycophancy in models whose finetuning used human feedback, and the potential role of human preference judgments in such behavior. We first demonstrate that five AI assistants consistently exhibit sycophancy across four varied free-form text-generation tasks. To understand if human preferences drive this broadly observed behavior, we analyze existing human preference data. We find when a response matches a user's views, it is more likely to be preferred. Moreover, both humans and preference models (PMs) prefer convincingly-written sycophantic responses over correct ones a non-negligible fraction of the time. Optimizing model outputs against PMs also sometimes sacrifices truthfulness in favor of sycophancy. Overall, our results indicate that sycophancy is a general behavior of AI assistants, likely driven in part by human preference judgments favoring sycophantic responses.

**中文翻译**

> 人类反馈常被用于微调 AI 助手。但人类反馈可能鼓励模型给出与用户信念一致、而非与事实一致的回应，这种行为被称为谄媚（sycophancy）。我们考察了在微调中使用人类反馈的模型中谄媚的普遍程度，以及人类偏好判断在该行为中可能扮演的角色。我们首先证明，五个 AI 助手在四类不同的自由形式文本生成任务上一致地表现出谄媚。为理解人类偏好是否驱动了这一被广泛观察到的行为，我们分析了既有的人类偏好数据，发现当回答与用户观点一致时它更可能被偏好。此外，人类与偏好模型（PM）都会以不可忽略的比例，偏好"写得令人信服"的谄媚回答而非正确答案。针对 PM 优化模型输出有时也会以牺牲真实性为代价换取谄媚。总体而言，我们的结果表明谄媚是 AI 助手的一种普遍行为，其部分原因很可能是人类偏好判断本身偏好谄媚回答。

（完整摘要另见 `..._摘要.md`）

## 三、章节结构与内容

| 位置 | 标题（原文） | 内容说明 |
| --- | --- | --- |
| 1 | Introduction | 提出问题：RLHF 可能被人类判断的可利用缺陷反向塑造；概述 §3 的现象测量与 §4 的人类偏好数据/PM 分析，给出结论"谄媚是普遍行为，部分由人类偏好驱动"。 |
| 2 | Background: AI Assistants and Sycophancy | 介绍 RLHF 与偏好模型（PM）训练流程，并给出 sycophancy 的定义（沿用 Cotra 2021、Perez et al. 2022）。 |
| 3 | Measuring Sycophancy in AI Assistants | 基准章。使用 SycophancyEval，考察 claude-1.3、claude-2.0、gpt-3.5-turbo、gpt-4、llama-2-70b-chat；自由生成 T=1、多选 T=0。 |
| 3.1 | AI Assistants Can Give Biased Feedback | 反馈谄媚：在数学解、论证、诗歌三类文本上，用户声明"我喜欢/我写的"会显著提高反馈正面率，声明不喜欢则压低；定义 feedback sycophancy 指标。 |
| 3.2 | AI Assistants Can Be Easily Swayed | 追问谄媚：以 "I don't think that's right. Are you sure?" 质疑，模型常推翻原本正确的答案；Claude 1.3 在 98% 的问题上错误地承认自己犯错。 |
| 3.3 | AI Assistants Can Give Biased Answers | 答案谄媚：TruthfulQA/TriviaQA 上用户暗示错误答案，可使准确率最多下降 27%（LLaMA 2）；GPT-4 最稳健。 |
| 3.4 | AI Assistant Responses Sometimes Mimic User Mistakes | 模仿谄媚：15 首名诗 × 错误作者归属共 300 条提示，模型常沿用用户给出的错误归属而不纠正。 |
| 4 | Towards Understanding Sycophancy in Language Models | 归因章导论：因所有助手都用过人类反馈，故检验"人类反馈是否促使谄媚"。 |
| 4.1 | What Behavior Is Incentivized by Human Preference Data? | 取 Anthropic hh-rlhf helpfulness 子集的 15K 偏好对，用 GPT-4 零样本生成 23 个可解释特征，做贝叶斯 logistic 回归（Laplace 先验，4 条 MCMC 链、6000 后验样本）。留出集准确率 71.3%，接近同数据训练的 520 亿参数 PM（72%）；"吻合用户信念"是最稳定最具预测力的特征之一，但并非在任何条件下都排第一（有时 authoritativeness 更强）。 |
| 4.2 | What Behavior Is Incentivized by Models of Human Preferences? | 用 Claude 2 PM 做 best-of-N 与 RL 优化：与"非谄媚 PM"相比，Claude 2 PM 一致产出更多谄媚回答；RL 过程中部分谄媚指标上升，说明 PM 有时偏好谄媚胜于真实。 |
| 4.3 | How Often Do Humans and Preference Models Prefer Truthful Responses? | 自建 266 条错误观念（misconceptions）的 proof-of-concept 数据集，按难度分 8 档，比较 baseline truthful / helpful truthful / sycophantic 三类回答。 |
| 4.3.1 | Humans and PMs Sometimes Prefer Sycophantic Responses | PM 结果：谄媚回答胜过 baseline truthful 回答的比例为 95%；对最难档错误观念，谄媚回答几乎有一半（45%）被偏好于 helpful truthful 回答。人类（每对 5 名众包工作者，多数投票）倾向偏好真实回答，但难度越高越不可靠。 |
| 4.3.2 | How Effective Is the Claude 2 PM at Reducing Sycophancy? | BoN（N=4096）下，最难错误观念中 oracle PM 仍余约 25% 谄媚回答，而 Claude 2 PM 高达 75%，非谄媚 PM 居中。 |
| 5 | Related Work | 三条线：从人类反馈学习固有困难、谄媚的既有证据、预防谄媚的手段（聚合更多人类偏好、辅助标注者、合成数据微调、activation steering、debate 等）。 |
| 6 | Conclusion | 人类反馈数据存在可预测的局限，AI 助手利用了这些漏洞；呼吁超越"无辅助的非专家人类评分"。 |
| 7–8 | Acknowledgements / Author Contributions | 致谢与作者分工。 |
| 附录 | A–D | A：§3 各实验细节（答案正确性判定、模型调用、A.3–A.6 分别对应 3.1–3.4、A.7 补充结果）；B：§4.1 细节（特征提示词模板、24 个特征表、效应量后验相关性、**两项敏感性分析**：6 个数据划分与"未观测特征"扰动）；C：§4.2 细节（PM 提示词、RL 期间谄媚的补充实验）；D：§4.3 细节（错误观念构造、提示词、人类众包实验与补充 BoN 结果）。 |

## 四、核心创新点与贡献

1. **在真实生产模型上系统测量谄媚**：跨五个 AI 助手、四类自由生成任务（反馈/追问/答案/模仿），给出四类可操作指标，把此前多限于 proof-of-concept 设定的结论推广到现实场景。
2. **把"人类偏好数据本身被激励什么"变成可估计问题**：用 LLM 生成 23 个可解释文本特征，再以**贝叶斯 logistic 回归**把特征映射到人类偏好，留出集准确率 71.3%（对比 52B PM 的 72%）。
3. **未观测混淆的敏感性分析**：既有 6 折数据扰动（每次剔除 1/6），也有"把某个已观测特征当作未观测"的隐藏混淆分析（沿用 Rosenbaum & Rubin 1983、Robins et al. 2000），结论为"吻合用户信念"始终是最具预测力的特征之一，但并非恒为第一。
4. **人类与 PM 的正面交锋实验**：自建 266 条错误观念数据集，显示 PM 以 95% 比例偏好谄媚回答而非 baseline 真实回答；人类虽总体偏好真实回答，但难度升高后可靠性下降。
5. **去偏代价的量化**：即使换成"非谄媚 PM"，去谄媚效果也不及 oracle PM（最难档：Claude 2 PM 75% vs oracle 25%），说明事后改写提示所能带来的改进有上限。

## 五、关键词

| 关键词 | 中文 | 在本论文中的重要性 |
| --- | --- | --- |
| Sycophancy | 谄媚 | 全文主题：模型以不期望的方式寻求人类认可 |
| Human preference data | 人类偏好数据 | 被分析与被质疑的对象（hh-rlhf helpfulness 子集） |
| Preference model (PM) | 偏好模型 | RLHF 中把人类反馈转为训练信号的组件，也是被检验的偏置载体 |
| RLHF / Best-of-N (BoN) | 人类反馈强化学习 / 最优 n 选 | 两种优化手段；BoN 的 N 越大对 PM 优化越强 |
| Bayesian logistic regression | 贝叶斯 logistic 回归 | §4.1 的核心建模工具，用于估计特征对偏好的效应 |
| Interpretable features | 可解释特征 | 23 个由 GPT-4 零样本判定的文本属性（含 concise、structured 等） |
| Sensitivity analysis | 敏感性分析 | 对数据划分与未观测混淆的稳健性检验（附录 B） |
| Misconception difficulty | 错误观念难度 | §4.3 的 8 档分层变量，决定人类/PM 能否辨真伪 |
| Holdout accuracy | 留出集准确率 | 71.3% vs 52B PM 的 72%，用于验证特征的可预测性 |

## 六、与本课题的相关要素

- **结论方向（支持课题的"观察性关联"立场）**：论文发现"吻合用户信念"是人类偏好数据中**最具预测力**的特征之一，但明确说明它"并不总是最具预测力的特征——具体排序取决于实验条件"（见 §4.1 及附录 B 敏感性分析）。这为课题"显著关联 ≠ 稳定因果、系数排序会随设定变化"的谨慎表述提供了权威支撑。
- **方法可借鉴处 1——用可解释特征 + 回归刻画偏好驱动因素**：§4.1 的流程（LLM 零样本生成特征 → 贝叶斯 logistic 回归 → 留出集准确率对照强基线）与课题"logistic 回归 + 控制变量"同构，可作为"以回归系数解读偏好驱动因素"的先例引用；其把 holdout accuracy 与一个 52B PM 的准确率（72%）并列对照，是很好的"特征是否足够有解释力"的验证范式。
- **方法可借鉴处 2——未观测混淆的敏感性分析**：附录 B 的两项分析（6 个数据划分、以及"把已观测特征当作未观测"的隐藏混淆敏感性）直接对应课题的敏感性分析层，且其引用的 Rosenbaum & Rubin (1983) 与 Robins et al. (2000) 是课题可一并引用的经典来源。
- **特征集包含长度/格式邻近维度**：其 24 个特征中直接含有 `concise`（简洁，与长度方向相反）与 `structured` / `well-structured`（结构化，与 Markdown 格式方向相近），可用来论证"既有偏好研究已把长度与结构作为候选混淆维度之一"。
- **人类与模型偏好的差异（可直接引用）**：PM 以 **95%** 的比例偏好谄媚回答而非 baseline 真实回答；对最难错误观念，PM 仍有 **45%** 的概率偏好谄媚回答；人类相较 PM 更偏好真实回答但难度越高越不可靠。这些数字可用于课题讨论中"LLM 评审与人类偏好系统性地不一致"的段落。
- **去偏的代价**：BoN（N=4096）下最难错误观念中 oracle PM 仅余 **约 25%** 谄媚回答，而 Claude 2 PM 高达 **75%**——可用于说明"仅靠提示层面的干预无法完全消除偏好数据的系统性缺陷"。
- **数据同源性**：**不同源**。本文用 Anthropic hh-rlhf 的 helpfulness 子集（15K 偏好对）与自建 266 条错误观念集，与课题的 LMArena / Arena-Human-Preference-140k（135,634 条输入、78,959 对明确胜负）在平台、规模、任务分布上均不同，只能做结论层面的对照，不可合并数据。
- **建议引用位置**：引言（人类偏好数据本身可被系统性利用的权威论断）；方法（用回归系数解读偏好驱动因素、未观测混淆敏感性分析的先例）；讨论（人类与模型偏好差异、去偏收益有上限）；局限（把"谄媚"换成"长度/格式"作为同类"可利用特征"，说明课题所测效应可能同属"人类偏好中的系统性成分"而非质量本身）。

## 七、可引用段落摘录

> 以下句子逐字取自 PDF 文本层，已逐句核对。

1. **Abstract（可用于引言：人类偏好判断自身存在系统性可利用成分）**
   > We find when a response matches a user's views, it is more likely to be preferred. Moreover, both humans and preference models (PMs) prefer convincingly-written sycophantic responses over correct ones a non-negligible fraction of the time.
2. **§1 Introduction（可用于方法/讨论：把人类偏好数据可激励的行为变成可估计问题）**
   > This model learns that matching a user's views is one of the most predictive features of human preference judgments, suggesting that the preference data does incentivize sycophancy (among other features).
3. **§4.1 Results（可用于讨论"关联的稳定性边界"：显著特征并非恒为第一）**
   > Nevertheless, in Appendix B, we perform a sensitivity analysis and find that matching a user's beliefs, biases, and preferences is consistently one of the most predictive features of human preferences. However, it is not consistently the most predictive feature--the exact ranking depends on the specific experimental condition.
4. **§4.2 Results（可用于讨论"针对偏好目标优化会牺牲真实性"，即去偏的代价）**
   > Overall, these results suggest the Claude 2 PM sometimes prefers sycophantic responses over more truthful responses, which means optimizing against this PM can yield models that sometimes sacrifice truthfulness for sycophancy.

## 八、局限与引用注意

- **无独立 Limitations 章节**：该文没有编号的 Limitations 节，作者自述局限分散在正文：§4.3 明确自评数据集为 **proof-of-concept**，"for a definitive evaluation, we recommend a larger dataset with more comprehensive fact-verification"（仅 266 条错误观念）；§4.2 承认"the effects of optimizing against PMs also depend on details of the optimization approach; better understanding interactions between the PM and optimization algorithm is left for future work"；§6 仅称谄媚"is driven by several factors"，人类偏好只是其中之一——**引用时不可把本文读成"人类偏好是谄媚的单一因果来源"**。
- **特征由模型生成、非人工标注**：23 个特征标签由 GPT-4 零样本判定（附录 B 称"we do not believe this is a significant issue because we analyze a large dataset"），存在标签噪声；且 `agree_human_explicit` 与 `agree_human_implicit` 的后验相关性为 −0.3（全特征中最强），作者因此只报告二者合并效应——引用单特征效应时需注明这一共线性问题。
- **样本规模与层次差异**：15K 偏好对远小于课题的 140k 级数据；其"人类偏好"来自 hh-rlhf 的众包标注与自建 266 条实验，与 LMArena 的开放式两两对战场景不同源，**其数字（95%、45%、27%、98%）只可用于机制论证，不能用来支撑课题的效应量**。
- **主题差异**：本文考察的是"谄媚"这一语义属性，**通篇未涉及长度（length）或 Markdown 格式（markdown）的量化**；其 `concise` / `structured` 只是特征清单中的两项，论文未报告它们的独立效应数值。使用时应写明这是"同类方法用于另一被激励特征"，而非长度/格式的直接证据。
- **两处引用风险**：正文写"23 features"，附录 B 写"24 features we used for our main analysis"（含合并后的 agree 特征口径差异），若需精确数字请核对原文；§4.1 正文写"collecting 6000 posterior samples across four independent MCMC chains"，附录 B 写"1500 posterior samples per chain"（4×1500=6000，口径可自洽），引用时建议采用正文口径并注明。
