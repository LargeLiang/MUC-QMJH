# Reward Hacking in the Era of Large Models: Mechanisms, Emergent Misalignment, Challenges — 摘要

> 来源：`Papers/English/Reward Hacking in the Era of Large Models Mechanisms Emergent Misalignment Challenges.pdf`
> 作者：Xiaohua Wang, Muzhao Tian, Yuqi Zeng, Zisu Huang, Jiakang Yuan, Bowen Chen, Jingwen Xu, Mingbo Zhou, Wenhao Liu, Muling Wu, Zhengkang Guo, Qi Qian, Yifei Wang, Feiran Zhang, Ruicheng Yin, Shihan Dou, Changze Lv, Tao Chen, Kaitao Song, Xu Tan, Tao Gui, Xiaoqing Zheng, Xuanjing Huang
> 机构：Fudan NLP Group（正文仅标注此集体署名，逐人机构未确认）
> 出处：arXiv:2604.13602v1 [cs.LG]，2026-04-15（综述预印本；venue 未确认）

## Abstract（原文逐字）

Reinforcement Learning from Human Feedback (RLHF) and related alignment paradigms have become central to steering large language models (LLMs) and multimodal large language models (MLLMs) toward human-preferred behaviors. However, these approaches introduce a systemic vulnerability: reward hacking, where models exploit imperfections in learned reward signals to maximize proxy objectives without fulfilling true task intent. As models scale and optimization intensifies, such exploitation manifests as verbosity bias, sycophancy, hallucinated justification, benchmark overfitting, and, in multimodal settings, perception–reasoning decoupling and evaluator manipulation. Recent evidence further suggests that seemingly benign shortcut behaviors can generalize into broader forms of misalignment, including deception and strategic gaming of oversight mechanisms. In this survey, we propose the Proxy Compression Hypothesis (PCH) as a unifying framework for understanding reward hacking. We formalize reward hacking as an emergent consequence of optimizing expressive policies against compressed reward representations of high-dimensional human objectives. Under this view, reward hacking arises from the interaction of objective compression, optimization amplification, and evaluator–policy co-adaptation. This perspective unifies empirical phenomena across RLHF, RLAIF, and RLVR regimes, and explains how local shortcut learning can generalize into broader forms of misalignment, including deception and strategic manipulation of oversight mechanisms. We further organize detection and mitigation strategies according to how they intervene on compression, amplification, or co-adaptation dynamics. By framing reward hacking as a structural instability of proxy-based alignment under scale, we highlight open challenges in scalable oversight, multimodal grounding, and agentic autonomy.

## 中文翻译

基于人类反馈的强化学习（RLHF）及相关对齐范式，已成为引导大语言模型（LLM）与多模态大语言模型（MLLM）走向人类偏好行为的核心手段。然而这些方法带来一个系统性脆弱点：奖励劫持——模型利用所学奖励信号的不完美，去最大化代理目标而不真正完成真实任务意图。随着模型规模扩大与优化强度提高，这种利用表现为冗长偏置（verbosity bias）、谄媚（sycophancy）、编造理由、基准过拟合，在多模态场景下还表现为感知–推理脱钩与对评估者的操纵。近期证据进一步表明，看似良性的捷径行为可以泛化为更广泛的错位形式，包括欺骗以及对监督机制的策略性博弈。在本综述中，我们提出 Proxy Compression Hypothesis（PCH）作为理解奖励劫持的统一框架。我们把奖励劫持形式化为：在压缩的高维人类目标奖励表示上优化表达能力强的策略所产生的涌现性后果。在这一视角下，奖励劫持源于客观压缩、优化放大与评估者–策略共适应三者的交互。该视角统一了 RLHF、RLAIF 与 RLVR 体制下的经验现象，并解释了局部捷径学习如何泛化为更广泛的错位形式，包括欺骗与对监督机制的策略性操纵。我们进一步按"干预压缩、放大或共适应动态"的方式组织检测与缓解策略。通过把奖励劫持刻画为规模化条件下基于代理的对齐的结构性不稳定，我们指出了可扩展监督、多模态接地与 agentic 自主性方面的开放挑战。

## 关键词

reward hacking（奖励劫持）、proxy compression（代理压缩）、Proxy Compression Hypothesis / PCH（代理压缩假说）、Goodhart's Law（古德哈特定律）、verbosity bias（冗长偏置／长度偏置）、survivor features（幸存特征）、objective compression（客观压缩）、optimization amplification（优化放大）、evaluator–policy co-adaptation（评估者–策略共适应）、alignment faking（对齐伪装）、RLHF / RLAIF / RLVR、scalable oversight（可扩展监督）

---

*说明：原文逐字取自 PDF 摘要（该文为单栏模板，文本层完整，未改写）；原文中 "evaluator–policy"、"perception–reasoning" 的连接号在文本层显示为乱码字符，此处按上下文还原为 en-dash，引用前请核对 PDF。中文翻译为便于阅读的机器翻译，引用请以英文原文为准。*
