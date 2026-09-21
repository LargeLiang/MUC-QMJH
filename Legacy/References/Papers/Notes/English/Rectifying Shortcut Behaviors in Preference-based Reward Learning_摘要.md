# Rectifying Shortcut Behaviors in Preference-based Reward Learning — 摘要

> 来源：`Papers/English/Rectifying Shortcut Behaviors in Preference-based Reward Learning.pdf`
> 作者：Wenqian Ye, Guangtao Zheng, Aidong Zhang
> 机构：University of Virginia；Accenture（论文注明工作完成于 University of Virginia）
> 出处：第 39 届 Conference on Neural Information Processing Systems（NeurIPS 2025）；arXiv:2510.19050v1 [cs.AI]，2025-10-21

## Abstract（原文逐字）

In reinforcement learning from human feedback, preference-based reward models play a central role in aligning large language models to human-aligned behavior. However, recent studies show that these models are prone to reward hacking and often fail to generalize well due to over-optimization. They achieve high reward scores by exploiting shortcuts, that is, exploiting spurious features (e.g., response verbosity, agreeable tone, or sycophancy) that correlate with human preference labels in the training data rather than genuinely reflecting the intended objectives. In this paper, instead of probing these issues one at a time, we take a broader view of the reward hacking problem as shortcut behaviors and introduce a principled yet flexible approach to mitigate shortcut behaviors in preference-based reward learning. Inspired by the invariant theory in the kernel perspective, we propose Preference-based Reward Invariance for Shortcut Mitigation (PRISM), which learns group-invariant kernels with feature maps in a closed-form learning objective. Experimental results in several benchmarks show that our method consistently improves the accuracy of the reward model on diverse out-of-distribution tasks and reduces the dependency on shortcuts in downstream policy models, establishing a robust framework for preference-based alignment.

## 中文翻译

在基于人类反馈的强化学习（RLHF）中，基于偏好的奖励模型在让大语言模型对齐人类期望行为方面起核心作用。然而近期研究表明，这类模型容易发生奖励劫持（reward hacking），并常因过度优化而泛化不佳。它们通过利用捷径来获得高奖励分数，即利用与训练数据中人类偏好标签相关、但并未真正反映预期目标的虚假特征（如响应冗长、讨好的语气或谄媚）。本文不去逐个探查这些问题，而是把奖励劫持问题更宏观地视为捷径行为，并提出一种有原则且灵活的方法来缓解基于偏好的奖励学习中的捷径行为。受核视角下不变量理论的启发，我们提出 PRISM（Preference-based Reward Invariance for Shortcut Mitigation），它通过闭式学习目标用特征映射学习群不变核。多项基准上的实验结果表明，我们的方法持续提升奖励模型在多样分布外任务上的准确率，并降低下游策略模型对捷径的依赖，为基于偏好的对齐建立了一个稳健框架。

## 关键词

shortcut learning（捷径学习）、reward hacking（奖励劫持）、preference-based reward model（基于偏好的奖励模型）、spurious features（虚假特征）、PRISM、group-invariant kernel（群不变核）、random feature map（随机特征映射）、Pearson correlation（皮尔逊相关）、RewardBench、RM-Bench、RLHF / DPO

---

*说明：原文逐字取自 PDF 摘要（该文为单栏排版，未改写）；中文翻译为便于阅读的机器翻译，引用时请以英文原文为准。*
