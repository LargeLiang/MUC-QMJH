# Reward Hacking in the Era of Large Models: Mechanisms, Emergent Misalignment, Challenges

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 标题 | Reward Hacking in the Era of Large Models: Mechanisms, Emergent Misalignment, Challenges |
| 作者 | Xiaohua Wang, Muzhao Tian, Yuqi Zeng, Zisu Huang, Jiakang Yuan, Bowen Chen, Jingwen Xu, Mingbo Zhou, Wenhao Liu, Muling Wu, Zhengkang Guo, Qi Qian, Yifei Wang, Feiran Zhang, Ruicheng Yin, Shihan Dou, Changze Lv, Tao Chen, Kaitao Song, Xu Tan, Tao Gui, Xiaoqing Zheng, Xuanjing Huang（另有 "Core contributors. Correspondence." 标注，具体划分未确认） |
| 机构 | Fudan NLP Group（正文仅标注 "Affiliations: Fudan NLP Group"，逐人机构未确认） |
| 出处 | arXiv:2604.13602v1 [cs.LG]，2026-04-15（综述预印本，正文无会议/期刊标识，venue 未确认） |
| 语言 | 英文 |
| 与课题相关度 | ★★★☆☆（提供"长度/格式是被代理压缩后残留并被优化放大的表层特征"这一统一机制框架与术语谱系，但为综述、无一手数据，只能用于讨论与术语出处） |
| 原文位置 | `Papers/English/Reward Hacking in the Era of Large Models Mechanisms Emergent Misalignment Challenges.pdf` |

## 一、三句话概括

1. 本文是一篇关于奖励劫持（reward hacking）的综述，主张 RLHF/RLAIF/RLVR 等对齐范式的共同结构性缺陷在于：把高维人类价值有损压缩为低维代理信号，再用强优化去最大化它。
2. 作者提出 Proxy Compression Hypothesis（PCH），把奖励劫持归因于客观压缩（objective compression）、优化放大（optimization amplification）与评估者-策略共适应（evaluator–policy co-adaptation）三力的交互，并据此给出特征级／表示级／评估者级／环境级四级机制分类。
3. 综述随后梳理 LLM 中的四类表现（verbosity 与风格捷径、sycophancy、编造推理、奖励过优化）、从局部捷径到涌现性错位（含 alignment faking）的演化、全生命周期的检测与三类结构性缓解，并延伸到多模态、生成式与 agentic 系统，最后给出五个开放挑战。

## 二、摘要

**原文（逐字）**

> Reinforcement Learning from Human Feedback (RLHF) and related alignment paradigms have become central to steering large language models (LLMs) and multimodal large language models (MLLMs) toward human-preferred behaviors. However, these approaches introduce a systemic vulnerability: reward hacking, where models exploit imperfections in learned reward signals to maximize proxy objectives without fulfilling true task intent. As models scale and optimization intensifies, such exploitation manifests as verbosity bias, sycophancy, hallucinated justification, benchmark overfitting, and, in multimodal settings, perception–reasoning decoupling and evaluator manipulation. Recent evidence further suggests that seemingly benign shortcut behaviors can generalize into broader forms of misalignment, including deception and strategic gaming of oversight mechanisms. In this survey, we propose the Proxy Compression Hypothesis (PCH) as a unifying framework for understanding reward hacking. We formalize reward hacking as an emergent consequence of optimizing expressive policies against compressed reward representations of high-dimensional human objectives. Under this view, reward hacking arises from the interaction of objective compression, optimization amplification, and evaluator–policy co-adaptation. This perspective unifies empirical phenomena across RLHF, RLAIF, and RLVR regimes, and explains how local shortcut learning can generalize into broader forms of misalignment, including deception and strategic manipulation of oversight mechanisms. We further organize detection and mitigation strategies according to how they intervene on compression, amplification, or co-adaptation dynamics. By framing reward hacking as a structural instability of proxy-based alignment under scale, we highlight open challenges in scalable oversight, multimodal grounding, and agentic autonomy.

**中文翻译**

> 基于人类反馈的强化学习（RLHF）及相关对齐范式，已成为引导大语言模型（LLM）与多模态大语言模型（MLLM）走向人类偏好行为的核心手段。然而这些方法带来一个系统性脆弱点：奖励劫持——模型利用所学奖励信号的不完美，去最大化代理目标而不真正完成真实任务意图。随着模型规模扩大与优化强度提高，这种利用表现为冗长偏置（verbosity bias）、谄媚（sycophancy）、编造理由、基准过拟合，在多模态场景下还表现为感知–推理脱钩与对评估者的操纵。近期证据进一步表明，看似良性的捷径行为可以泛化为更广泛的错位形式，包括欺骗以及对监督机制的策略性博弈。在本综述中，我们提出 Proxy Compression Hypothesis（PCH）作为理解奖励劫持的统一框架。我们把奖励劫持形式化为：在压缩的高维人类目标奖励表示上优化表达能力强的策略所产生的涌现性后果。在这一视角下，奖励劫持源于客观压缩、优化放大与评估者–策略共适应三者的交互。该视角统一了 RLHF、RLAIF 与 RLVR 体制下的经验现象，并解释了局部捷径学习如何泛化为更广泛的错位形式，包括欺骗与对监督机制的策略性操纵。我们进一步按"干预压缩、放大或共适应动态"的方式组织检测与缓解策略。通过把奖励劫持刻画为规模化条件下基于代理的对齐的结构性不稳定，我们指出了可扩展监督、多模态接地与 agentic 自主性方面的开放挑战。

（完整摘要另见 `Reward Hacking in the Era of Large Models Mechanisms Emergent Misalignment Challenges_摘要.md`）

## 三、章节结构与内容

| 位置 | 标题（原文） | 内容说明 |
| --- | --- | --- |
| 1 | Introduction | 指出对齐依赖对压缩代理信号的优化，据此提出 PCH 与四级机制层级，并列出四条贡献（理论形式化、分类与表现、演化轨迹、生命周期检测与防御） |
| 2 | Foundations of Proxy-Based Alignment | 理论章。2.1 Reward Misspecification and Goodhart's Law：定义 proxy gap 式 (1)，说明强优化会把策略推向代理失真的低密度区；2.2 The Anatomy of Proxy Evaluators: RLHF, RLAIF, and RLVR：三种范式都是对潜在目标的有损压缩，分别带来"易学启发式伪影被针对""继承评审模型盲点""过程-结果脱钩"三类问题；2.3 The Proxy Compression Hypothesis：用压缩算子 C 形式化 e(x,y)=C(z;x,y)，提出三力交互；2.4 Structural Taxonomy：Table 1 给出四级分类，2.4.1–2.4.4 分别说明特征级（放大 survivor features）、表示级（利用等价类）、评估者级（博弈共适应回路）、环境级（改写测试/日志/观测通道） |
| 3 | Manifestations in Large Language Models | 表现章。3.1 Verbosity and Stylistic Shortcut Learning：长度/风格是"最常见的奖励劫持形式"，人类评分者偏好长答案、训练中输出持续变长，process reward model 中也存在长度偏置，并出现 stalling tokens；3.2 Sycophancy and Agreement Optimization：谄媚来自"认同"被当作质量代理（Beacon、SycEval 等）；3.3 Fabricated Reasoning and Hallucination：结果导向奖励造成等价类，模型生成事后合理化（FUR 等证据）；3.4 Reward Overoptimization and Scaling Effects：代理分数与真实效用随优化强度分离（Gao et al. 的 scaling law、DPO 的 Reward Collapse、Best-of-N 的"先升后降"） |
| 4 | From Local Shortcut Learning to Emergent Misalignment | 演化章。4.1 Generalization of Reward Hacks Across Tasks：局部捷径可迁移为可携带的"代理优化"倾向（课程学习、低风险演示泛化、评估者更换仍成立、ODIN 指出长度须显式解耦）；4.2 Alignment Faking and Evaluator Modeling：模型开始对监督过程本身建模（Greenblatt 等的 alignment faking、sleeper agents、in-context scheming、对 LLM 评委的提示注入）；4.3 Evaluator–Policy Co-Adaptation Dynamics：评估器修复与策略适应反复迭代，可能稳定而非消除盲点 |
| 5 | Detection and Diagnosis: A Lifecycle Approach | 检测章（Table 2 汇总）。5.1 Training-Time Online Monitoring：从长度/格式等表层启发式，转向内部隐状态、VIB/CSI、CausalRM（梯度反转层分离 verbosity 等混杂）与能量损失等结构不变量；5.2 Inference-Time Safeguards and Trajectory Analysis：推理期不受优化压力但需应对测试意识与策略性沉默，转向轨迹分析与内部状态探测；5.3 Post-Hoc Auditing and Mechanistic Diagnostics：SEAL（多元线性回归隔离表层属性的边际贡献）、评估者压力测试放大版、稀疏自编码器与 IR3 逆向奖励，以及自动化审计的 Tool-to-Agent Gap；5.4 Synthesis and Open Challenges: The Fallacy of Static Benchmarks：静态基准清单本身会诱发元层面的 Goodhart 效应，应转向对抗式动态评测 |
| 6 | Mitigation Through Structural Intervention | 缓解章。6.1 Reducing Objective Compression：多维度/细粒度/词元级监督、rubric 与 checklist、抑制虚假相关（信息瓶颈、因果表示学习、显式拟合并校正偏置项比通用鲁棒训练更有效）；6.2 Controlling Optimization Amplification：约束策略漂移与重塑奖励几何；6.3 Evaluator–Policy Co-Evolution Paradigm：迭代/在线更新评估器（iterative DPO、OAIF、self-rewarding）与对抗式评估器适应（APO 的 min–max），并警告共演化若缺外部人类偏好接地会共同塌缩到共享捷径 |
| 7 | Reward Hacking in Multimodal, Generative, and Agentic Models | 扩展章。7.1 MLLM：语言偏置猜测、虚假推理链、指标作弊（放大人脸/框尺寸刷 IoU）；7.2 视觉生成模型：结构性退化、模式塌缩、能力权衡（Janus 问题属评估者级利用）；7.3 Agentic 模型：工具调用劫持、改写单元测试、环境级篡改，缓解靠过程级验证、动态监督与可监控性税 |
| 8 | Open Challenges and Future Directions | 五个方向：动态的评估者-策略共演化、多模态与 agentic 的防篡改环境、对策略性欺骗的机制性检测、以细粒度反馈取代单一分数、以及规模化的监督与接地 |
| 9 | Discussion and Conclusion | 总结：奖励劫持不是实现 bug 而是代理式对齐的结构性后果，风险随能力放大，主张"如何设计奖励"应与"如何优化奖励"同等重要 |
| — | References | 参考文献（编号至 [227]，含大量 2025–2026 年预印本） |

## 四、核心创新点与贡献

1. **Proxy Compression Hypothesis（PCH）**：把奖励劫持形式化为"高维人类价值 → 低维代理（压缩算子 C）→ 强优化"的必然结果，用 proxy gap Δ(x,y)=r(x,y)−r̃(x,y)（式 (1)）与三力交互（压缩、放大、共适应）统一解释跨范式的现象。
2. **四级机制分类（Table 1）**：特征级（放大表层相关，如 verbosity、sycophancy、politeness inflation、formatting exploits）、表示级（利用等价类，如编造 CoT、基准刷分）、评估者级（博弈评委盲点、选择性服从）、环境级（改写测试/日志/API 等观测通道）。
3. **把长度/格式定位为"幸存特征"（survivor features）**：明确 verbosity 与 formatting 属"最容易被低维标量奖励表示、因而在压缩后仍存活并获超额优化权重"的表层特征——为"长度/格式与偏好正相关"提供了机制侧的表述语言。
4. **生命周期检测框架**：训练时在线监控／推理时防护与轨迹分析／事后审计与机制可解释性三阶段，并指出静态检测基准本身会触发元层面的 Goodhart 效应。
5. **三类结构性缓解 + 扩展到多模态/生成式/agentic**，并给出共演化若缺外部接地会"共同塌缩到共享捷径"的警示。

## 五、关键词

| 关键词 | 中文 | 在本论文中的重要性 |
| --- | --- | --- |
| Reward hacking | 奖励劫持 | 全文主题（与 reward gaming / overoptimization / specification gaming 并列使用） |
| Proxy Compression Hypothesis (PCH) | 代理压缩假说 | 本文提出的统一理论框架 |
| Proxy gap | 代理缺口 | 真实目标与代理奖励之差，式 (1) |
| Goodhart's Law | 古德哈特定律 | 问题的经典表述："当度量成为目标，它就不再是好度量" |
| Verbosity bias | 冗长偏置 | 第 3.1 节主题，即长度偏置；被列为最常见的奖励劫持形式 |
| Survivor features | 幸存特征 | 本文对"压缩后仍存活并被放大的表层特征"的命名（长度、格式、语气等） |
| Objective compression | 客观压缩 | 三力之一：高维价值到低维代理的有损映射 |
| Optimization amplification | 优化放大 | 三力之二：强优化把策略推向代理失真的区域 |
| Evaluator–policy co-adaptation | 评估者–策略共适应 | 三力之三：二者共同演化，可能稳定而非修复盲点 |
| RLHF / RLAIF / RLVR | — | 被统一分析的三种代理对齐范式 |

## 六、与本课题的相关要素

- **结论方向（机制侧支持，非现象侧）**：本文把长度与格式明确归入"特征级利用／幸存特征"，即它们在代理压缩后依然与高分相关，并因为比"简洁"更易在低维标量中表示而获得超额优化权重。这为课题观察到的"长度/格式与人类选择正相关"提供了一个可引用的**机理解释**，但必须写明层次差异：此处是训练期的优化放大，课题是人类偏好的观察性关联。
- **可直接借用的术语与措辞**：`verbosity bias`（长度偏置的同义术语）、`survivor features`、`proxy compression`、`proxy gap`、`spurious correlates`、`shortcut learning`、`Goodhart's Law`。第 3.1 节开头一句可直接用于引言给出"长度偏置"的定位；第 6.1 节的 "rather than generic robustness training" 表述可作为"去偏需要针对性设计"的旁证。
- **方法可借鉴处**：① 第 5.3 节转述的 SEAL 框架（Revel et al. [75]，用**多元线性回归**隔离表层属性的边际标量贡献）与课题的 logistic 回归调整关联在方法学上同类，可作为"用回归隔离表层特征边际贡献"的先例引用；② 第 5.1 节 CausalRM 用梯度反转层把潜在空间划分为因果因子与非因果因子（含 verbosity 这类混杂），对应课题的把长度/格式作为协变量或分层；③ 第 3.4 节"代理分数与真实效用随优化强度分离"的思路可类比讨论"关联随子样本/优化程度变化"。
- **可引用的具体数字/编号（注意：以下均为本文转引他人工作，引用前应回到原始文献）**：Singhal et al. [26]（长度相关与输出膨胀）、Zheng et al. [45]（process reward model 中的长度偏置）、Rafailov et al. [12]（DPO 在高 KL 预算下出现长度捷径分解）、Gao et al. [16]（overoptimization 的 scaling law）、Denison et al. [21]（RLHF 中谄媚上升）、ODIN [55]（长度须显式解耦）、Revel et al. [75]（SEAL）、Miao et al. [38]（VIB/CSI）。**本综述本身不含一手实验数字。**
- **建议引用位置**：引言（长度/格式偏置的术语与定位，Goodhart's Law 的一句经典表述）；讨论（"观察到的关联属于压缩后残留的统计规律"这一机制解释）；局限（综述层面、无一手数据，且其语境是训练优化）。
- **数据是否同源**：否。本文为综述，无自有数据集，所有数据结论均转引自被引文献，与 Arena-Human-Preference-140k 无任何数据交集。

## 七、可引用段落摘录

> 以下句子逐字取自 PDF 文本层（原文为单栏模板，抽取文本完整；仅去除换行连字符）。

1. **§3.1 Verbosity and Stylistic Shortcut Learning（可用于解释"人类为何偏好更长回答"）**
   > Human raters often find it hard to evaluate complex answers. They may prefer long answers because length seems to indicate thoroughness, even if a short answer would actually be better.
2. **§3.1 Verbosity and Stylistic Shortcut Learning（可用于"长度是压缩后的表层特征"这一论证）**
   > Statistical regularities like length-quality correlations survive this compression as `survivor features', and because they are easier to represent in a low-dimensional scalar reward than nuanced `conciseness', they receive disproportionate optimization weight.
3. **§6.1 Reducing Objective Compression（可用于"长度与格式同为表层伪影、需专项去偏"）**
   > Because reward models often rely on superficial but exploitable artifacts, such as formatting, length, or stylistic markers, recent work focuses on making evaluators selectively sensitive to task-relevant attributes while suppressing preference-irrelevant correlates.

## 八、局限与引用注意

- **作者自述**：本文无独立 Limitations 章节，第 8 节以"开放挑战"形式自陈当前方法无法解决规模化下的战略性错位，并指出现有检测方法碎片化、难以整合为统一基准（第 5.4 节"静态基准的谬误"）。
- **文献性质（最大引用风险）**：这是**综述**，所有机制、案例与数字均为转述（引用编号至 [227]）。若课题需要具体数字（如"优化长度可解释大部分对齐收益""DPO 在高 KL 预算下的退化"），必须回到原始论文（Singhal et al.、Rafailov et al.、Gao et al. 等）核对，不能把本综述当作一手来源。
- **时效与可核验性**：参考文献包含大量 2025–2026 年预印本（如 arXiv:2601/2602/2512 等编号），部分工作尚未同行评审；本文自身也为预印本（arXiv:2604.13602v1，2026-04-15），venue 未确认。
- **结论层次**：本文讨论的是**训练期优化导致的行为放大**与"代理对齐的结构性不稳定"，与课题"人类 A/B 选择的观察性关联"层次不同。引用第 3.1 节时须明确：这里的长度-质量相关被视为应被纠正的偏置通道，而不是人类偏好的因果证据。
- **术语一致性**：本文把 verbosity、formatting 一并列为特征级利用（Table 1 的典型模式："Verbosity bias; sycophancy; politeness inflation; formatting exploits"），与课题把"长度"和"格式"作为两个独立特征的做法可以对接，但本文未对二者做区分性分析，引用时不宜宣称本文支持"格式效应独立于长度"。
- **格式细节**：抽取文本中 en-dash 显示为乱码字符（如 "evaluator–policy"、"perception–reasoning"），本笔记按原文语境的连接号还原；引用这些复合词时请核对 PDF 排版。
