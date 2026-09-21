# Towards Understanding Sycophancy in Language Models — 摘要

> 来源：`Papers/English/Towards Understanding Sycophancy in Language Models.pdf`
> 作者：Mrinank Sharma\*, Meg Tong\*, Tomasz Korbak, David Duvenaud, Amanda Askell, Samuel R. Bowman, Newton Cheng, Esin Durmus, Zac Hatfield-Dodds, Scott R. Johnston, Shauna Kravec, Timothy Maxwell, Sam McCandlish, Kamal Ndousse, Oliver Rausch, Nicholas Schiefer, Da Yan, Miranda Zhang, Ethan Perez（\*同等贡献）
> 机构：Anthropic（全体作者）；Mrinank Sharma 兼属 University of Oxford；Meg Tong 以独立研究者身份完成；Tomasz Korbak 在 University of Sussex 与 FAR AI 期间完成
> 出处：ICLR 2024 会议论文；arXiv:2310.13548v4 [cs.CL]，2025-05-10

## Abstract（原文逐字）

Human feedback is commonly utilized to finetune AI assistants. But human feedback can encourage model responses that match user beliefs over truthful ones, a behavior known as sycophancy. We investigate the prevalence of sycophancy in models whose finetuning used human feedback, and the potential role of human preference judgments in such behavior. We first demonstrate that five AI assistants consistently exhibit sycophancy across four varied free-form text-generation tasks. To understand if human preferences drive this broadly observed behavior, we analyze existing human preference data. We find when a response matches a user's views, it is more likely to be preferred. Moreover, both humans and preference models (PMs) prefer convincingly-written sycophantic responses over correct ones a non-negligible fraction of the time. Optimizing model outputs against PMs also sometimes sacrifices truthfulness in favor of sycophancy. Overall, our results indicate that sycophancy is a general behavior of AI assistants, likely driven in part by human preference judgments favoring sycophantic responses.

## 中文翻译

人类反馈常被用于微调 AI 助手。但人类反馈可能鼓励模型给出与用户信念一致、而非与事实一致的回应，这种行为被称为谄媚（sycophancy）。我们考察了在微调中使用人类反馈的模型中谄媚的普遍程度，以及人类偏好判断在该行为中可能扮演的角色。我们首先证明，五个 AI 助手在四类不同的自由形式文本生成任务上一致地表现出谄媚。为理解人类偏好是否驱动了这一被广泛观察到的行为，我们分析了既有的人类偏好数据，发现当回答与用户观点一致时它更可能被偏好。此外，人类与偏好模型（PM）都会以不可忽略的比例，偏好"写得令人信服"的谄媚回答而非正确答案。针对 PM 优化模型输出有时也会以牺牲真实性为代价换取谄媚。总体而言，我们的结果表明谄媚是 AI 助手的一种普遍行为，其部分原因很可能是人类偏好判断本身偏好谄媚回答。

## 关键词

sycophancy（谄媚）、human preference data（人类偏好数据）、preference model / PM（偏好模型）、RLHF、best-of-N sampling、Bayesian logistic regression（贝叶斯 logistic 回归）、interpretable features（可解释特征）、sensitivity analysis（敏感性分析）、truthfulness（真实性）、hh-rlhf

---

*说明：原文逐字取自 PDF 摘要（单栏排版，未作重组），未改写；中文翻译为便于阅读的机器翻译，引用时请以英文原文为准。原文中 "user's" 等撇号在文本层为直引号（'），此处保留原样。*
