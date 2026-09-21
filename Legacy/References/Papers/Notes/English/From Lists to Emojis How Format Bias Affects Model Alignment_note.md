# From Lists to Emojis: How Format Bias Affects Model Alignment

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 标题 | From Lists to Emojis: How Format Bias Affects Model Alignment |
| 作者 | Xuanchang Zhang\*, Wei Xiong\*, Lichang Chen, Tianyi Zhou, Heng Huang, Tong Zhang（\*同等贡献；通讯作者 Wei Xiong） |
| 机构 | University of Illinois Urbana-Champaign；University of Maryland College Park |
| 出处 | arXiv:2409.11704v2 [cs.CL]，2025-05-23（预印本；venue 未确认） |
| 语言 | 英文 |
| 与课题相关度 | ★★★★★（格式偏置的系统清单 + 与课题同源的 LMSYS-Arena 人类数据描述统计） |
| 原文位置 | `Papers/English/From Lists to Emojis How Format Bias Affects Model Alignment.pdf` |

## 一、三句话概括

1. 论文系统研究 RLHF 中"长度偏置"之外更广泛的**格式模式偏置**，覆盖列表、链接、加粗、emoji、感叹号、肯定语气等，并报告其在人类标注者、GPT-4 与主流开源偏好/奖励模型中普遍存在。
2. 通过可控数据注入实验证明：不到 1% 的带偏数据即可让奖励模型产生显著格式偏置，并被 best-of-n 采样、离线/在线迭代 DPO、PPO 等下游对齐算法放大，进而推高 AlpacaEval 与 LMSYS Chatbot Arena 排名。
3. 作者提出双头奖励模型加相关性约束的去偏初探，并指出被动数据过滤不可行——必须在设计对齐算法与评测模型时显式解耦格式与内容。

## 二、摘要

**原文（逐字）**

> In this paper, we study format biases in reinforcement learning from human feedback (RLHF). We observe that many widely-used preference models--including human evaluators, GPT-4, and top-ranking models on the RewardBench benchmark--exhibit strong biases towards specific format patterns, such as lists, links, bold text, and emojis. Furthermore, large language models (LLMs) can exploit these biases to achieve higher rankings on popular benchmarks like AlpacaEval and LMSYS Chatbot Arena.
>
> One notable example is verbosity bias, where current preference models favor longer responses that appear more comprehensive, even when their quality is equal to or lower than shorter responses. However, format biases beyond verbosity remain largely underexplored. In this work, we extend the study of biases in preference learning beyond the commonly recognized length bias, offering a comprehensive analysis of a wider range of format biases. Additionally, we show that with a small amount of biased data (less than 1%), we can inject significant bias into the reward model. Moreover, these format biases can also be easily exploited by downstream alignment algorithms, such as best-of-n sampling and online iterative DPO, as it is usually easier to manipulate the format than to improve the quality of responses. Our findings emphasize the need to disentangle format and content both for designing alignment algorithms and evaluating models.

**中文翻译**

> 本文研究人类反馈强化学习（RLHF）中的格式偏置。我们观察到，许多广泛使用的偏好模型——包括人类评估者、GPT-4 以及 RewardBench 榜单上名列前茅的模型——对特定格式模式表现出强烈偏好，例如列表、链接、加粗文本与 emoji。此外，大语言模型（LLM）可以利用这些偏置在 AlpacaEval、LMSYS Chatbot Arena 等流行榜单上取得更高排名。
>
> 一个典型例子是冗长偏置：当前偏好模型偏爱看起来更全面、更长的回答，即使其质量与较短回答相当甚至更低。然而，冗长之外的格式偏置仍研究不足。本文把偏好学习中的偏置研究从常见的长度偏置扩展到更广范围，对多种格式偏置做了系统分析。我们还表明，只需少量（不到 1%）带偏数据即可向奖励模型注入显著偏置；而且这些格式偏置很容易被 best-of-n 采样、在线迭代 DPO 等下游对齐算法利用——因为操纵格式通常比提高回答质量更容易。我们的发现强调：设计对齐算法与评估模型时都必须把格式与内容解耦。

（完整摘要另见 `..._摘要.md`）

## 三、章节结构与内容

| 位置 | 标题（原文） | 内容说明 |
| --- | --- | --- |
| 1 | Introduction | 提出核心问题"IF 榜单分数是否真反映模型能力"；指出 reward hacking 与长度偏置之外的格式偏置被忽视；给出四条贡献（偏置普遍存在／榜单模型利用偏置／<1% 数据即可注入／被动过滤无效） |
| 2 | The Pattern Bias in Preference Learning | 总览偏置现象。2.1 Pattern Statistics in Preference Datasets and Benchmarks：在 RLHFlow-Preference-700K（Mixture）、LMSYS-Arena-55K（Human，49865 条）、AlpacaEval（GPT-4，169927）、UltraFeedback-binarized（GPT-4，61135）上统计 7 种 pattern——length、emoji、bold、exclamation、list、link、affirmative 在 preferred 与 unpreferred 中的占比；结论：人类与 GPT-4 都偏好更长/加粗/列表/感叹号/肯定语气（GPT-4 更强），而 emoji 与超链接只被 GPT-4 偏好、人类并不共享，UltraFeedback 偏置最弱。2.2 Bias Evaluation of Preference Model：对 LMSYS-Arena prompt 生成回答后"删掉 pattern"构造仅格式不同的配对（每种 200 对），测量 7 个偏好模型（GPT-4 Turbo、ArmoRM、Pairwise-model-Llama-3-8B、FsfairX、Skywork-Critic、Zephyr-Beta、OffsetBias-RM）的含 pattern 方胜率（无偏应为 50%）；GPT-4 各 pattern 普遍有偏（bold 89.5%、list 75.75%、emoji 86.75%），连去偏奖励模型 OffsetBias 仍偏向 bold/list。2.3 Pattern Bias and Preference Flipping：加粗等样式可使 GPT-4 偏好内容更差但"更好看"的回答 |
| 3 | Pattern Bias Transfer in Downstream Reward Modeling and Alignment | 可控因果式实验（聚焦 bold 与 list）。3.1 A Small Amount of Data Can Lead to Significant Reward Model Bias：以 UltraFeedback 过滤出的 71.6K 偏好对为基座，构造"含 pattern 者为 preferred"的攻击集训练 Llama-3-8B-it 奖励模型；list 胜率 51.0% → 74.0/77.5%（注入 0.70%/1.40%），bold 57.5% → 88.0%。3.2 Downstream Alignment Task: DPO and PPO Training：被攻击的 RM 用于离线 DPO、在线迭代 DPO 与 PPO 后，bold/list 生成比例持续上升 |
| 4 | Mitigate the Format Bias | 方法章。4.1 Method：训练双头 RM（authentic reward 与 disentangled reward），在 Bradley-Terry 结构下加相关性约束损失 L_C（Pearson 相关 + 启发式 #bold/#list 计数），并用 reordering 处理 pattern 稀疏。4.2 Main Results：在 RewardBench（23 子集、四类）上评估，显式约束可将 bold 胜率 89.0% 降至约 49–56%，但存在 RM 容量—偏置权衡；被动删除全部含 pattern 配对会删掉 57% 数据并损害 RM 质量，reordering 可兼顾；用去偏 RM 重排 AlpacaEval 榜单（ELO，K=32）后 Llama 系排名下降（Llama3-70B-it −3、Llama3-8B-it −2）、闭源模型上升 |
| 5 | Conclusion | 总结：<1% 偏置数据即可影响 RM，在线算法易利用偏置，需解耦格式与内容 |
| 6 | Limitations | 自述算力不足，在线 DPO/PPO 未跑更大模型（如 LLaMA-70B） |
| 附录 | A–E | A Preliminaries（偏好数据、Bradley-Terry、KL 正则 RLHF 目标、DPO 推导）；B Related Work（RLHF 算法设计 / Reward hacking / Length hacking，含 LCWR 与 position bias、self-enhancement bias）；C 偏置示例；D preference flipping 示例；E 实验细节（E.1 best-of-n：bold 42.8%→51.9%、list 57.1%→64.4%；E.2 迭代 DPO 的长度控制胜率 10.2%→20.72%→28.34%→33.06%，PPO 28.76%） |

## 四、核心创新点与贡献

1. 把偏好偏置研究从"长度/verbosity"扩展到 **7 种格式 pattern 的系统清单与统一度量**（Table 1 占比 + Table 2 受控胜率）。
2. 用**"同内容、仅改格式"的配对**构造评测集（每 pattern 200 对），干净地隔离格式效应，区别于纯观察性统计。
3. 首次量化**数据投毒的剂量效应**：低至 0.7%–1.4% 的偏置数据即可把 RM 胜率从 51% 推到 74%–77.5%，bold 由 57.5% 推到 88%。
4. 打通偏置传导链：best-of-n / 离线 DPO / 在线迭代 DPO / PPO 均会放大格式偏置。
5. 提出**双头 RM + 相关性约束 + reordering** 的去偏初探，并证明被动过滤（删掉 57% 配对）不可行，稀疏 pattern 是核心难点。

## 五、关键词

| 关键词 | 中文 | 在本论文中的重要性 |
| --- | --- | --- |
| Format bias | 格式偏置 | 全文主题：格式特征引起的评审系统性倾斜 |
| Reward hacking | 奖励劫持 | 论文把格式偏置定位为 reward hacking 的新形式 |
| RLHF / preference model | 人类反馈强化学习 / 偏好模型 | 应用场景与被测对象 |
| Length bias (verbosity) | 长度偏置 | 被超越的既有研究基线 |
| Pattern bias | 模式偏置 | 论文自造标签，涵盖 list/bold/emoji/exclamation/link/affirmative |
| LLM-as-a-judge | 大模型评审 | GPT-4 Turbo 是主要被测对象，也是偏置来源 |
| Two-head RM / correlation loss / reordering | 双头奖励模型 / 相关约束 / 重排序 | 第 4 节的去偏手段 |
| Best-of-n / iterative DPO / PPO | — | 放大偏置的下游对齐算法 |
| LMSYS Chatbot Arena / AlpacaEval | — | 榜单场景（与课题数据同源） |

## 六、与本课题的相关要素

- **数据同源、方向一致**：其 LMSYS-Arena-55K（49865 对，Labeller=Human）与课题的 Arena-Human-Preference-140k 同属 LMArena 系人类偏好数据。Table 1 对人类侧 preferred vs unpreferred 的格式占比统计为：Bold 7.61 vs 4.54、List 38.84 vs 31.67、Emoji 0.73 vs 0.62、Exclamation 18.52 vs 15.77、Link 1.20 vs 1.08、Affirmative 7.30 vs 6.45、Length 191.64 vs 159.77（词数）——方向与课题"格式特征与人类选择正相关"一致，可作为引言或结果部分的外部佐证。
- **可用于区分"人类偏好"与"LLM 评审偏好"**：论文明确报告 GPT-4 对 emoji 与超链接的偏好人类并不共享——这是课题讨论中区分两类偏好时的现成论据（人类侧证据更保守）。
- **证据分层**：人类侧证据（2.1）与课题一致；2.2 / 3.x / 4.x 的受控实验与去偏结论均建立在 LLM 评审与奖励模型上，引用时不可与人类偏好混同。
- **可引用的方法名/指标名**：adjusted win rate（平局折半）、length-controlled win rate（Li et al., 2023，logistic 回归控制长度差）、Bradley-Terry、RewardBench（23 子集/4 类）、ELO(K=32)、启发式计数 #bold/#list、Pearson 相关约束 L_C、two-head RM、reordering、best-of-n 中的 pattern 比例曲线。
- **可引用的数字**：<1% 偏置数据使 list 胜率 51.0% → 74.0/77.5%（Table 3；正文称 0.7% 对应 77.5%，表格标注 1.40%，引用时建议以表格为准或注明）；bold 57.5% → 88.0%；best-of-n 中 bold 42.8% → 51.9%、list 57.1% → 64.4%；被动过滤删除 57% 配对；去偏后 bold 胜率由 89.0% 降至约 49–56%。
- **可写入讨论/局限**：作者认为部分格式偏置"可能是人类偏好本身固有的"（intrinsic to human preference），但仍主张在算法与评测中显式处理——可用于课题"观察性关联不等于必须消除的偏置"的立场表述；其"受控配对 + two-head RM"可作为课题敏感性分析/纯度效应设计的方法学对话对象（课题为观察性，无法复制干预设计）。
- **未覆盖**：其 pattern 清单不含 Markdown 标题（heading），课题的标题特征需另找文献；其 bold/list 定义为启发式计数，与课题 Markdown 计数口径不同，需在方法中说明差异。

## 七、可引用段落摘录

> 以下句子逐字取自 PDF 文本层（该文双栏排版，抽取文本存在区隔，已逐句核对）。

1. **Abstract（主题句，可用于引言综述格式偏置）**
   > In this paper, we study format biases in reinforcement learning from human feedback (RLHF).
2. **§1 Introduction（可用于讨论"人类偏好中的格式倾向"与"需处理的对齐问题"之间的区别）**
   > Even though one believes that some format biases are intrinsic to human preference, they can still cause problems in downstream alignment tasks if not explicitly addressed through regularization.
3. **Abstract（结论句，可用于讨论或局限）**
   > Our findings emphasize the need to disentangle format and content both for designing alignment algorithms and evaluating models.

## 八、局限与引用注意

- **作者自述**（§6）：算力不足，在线 DPO/PPO 未使用更大模型（如 LLaMA-70B），结论以小模型外推。
- **人类证据弱于模型证据**：人类侧仅有 LMSYS-Arena 的描述性占比（未做显著性检验、未控制长度与任务），全部受控实验与去偏实验均为 LLM judge / RM，不能当作人类偏好证据引用。
- **格式—长度混淆**：bold/list 与长度天然相关，论文在 Table 1/2 层面未控制长度；课题在自身回归中应明确控制长度并说明该文未做。
- **措辞层级**：论文把格式偏好框定为"偏置/可被劫持"（干预式配对 + 投毒实验），课题为观察性关联；引用时应写成"格式可能带来评审系统性倾斜"，避免移植其因果式措辞。
- **数字一致性**：3.1 正文称 0.7% 注入使 list 胜率达 77.5%，而 Table 3 中 77.5% 对应 +1.40%（0.70% 行为 74.0%），引用时以表格为准或注明。
- **数据规模差异**：其 base 为 UltraFeedback 过滤版（71.6K 对）、RM 为 Llama-3-8B-it，与课题 135,634 输入 / 78,959 明确胜负对在预处理与任务分布上不同。
- **venue 未确认**（仅 arXiv v2，2025-05-23），若投稿中文期刊需按预印本格式引用。
