# note_18 — Towards Understanding Sycophancy in Language Models

## 基本信息

| 字段 | 内容 |
|------|------|
| 编号 | [17] |
| 标题 | Towards Understanding Sycophancy in Language Models |
| 作者 | Mrinank Sharma*, Meg Tong*, Tomasz Korbak, David Duvenaud, Amanda Askell, Samuel R. Bowman, Newton Cheng, Esin Durmus, Zac Hatfield-Dodds, Scott R. Johnston, Shauna Kravec, Timothy Maxwell, Sam McCandlish, Kamal Ndousse, Oliver Rausch, Nicholas Schiefer, Da Yan, Miranda Zhang, Ethan Perez |
| 机构 | Anthropic；University of Oxford；University of Sussex；FARAI |
| 发表会议 | ICLR 2024 |
| 关键词 | 谄媚（sycophancy）、用户信念偏向、偏好模型、RLHF偏见、真实性牺牲 |
| 相关性评级 | ★★★★☆ |
| 论文位置 | D:\Files\MUC-QMJH\References\Papers\Towards Understanding Sycophancy in Language Models.pdf |

---

## 摘要直接提取（Abstract）

> Human feedback is commonly utilized to finetune AI assistants. But human feedback can encourage model responses that match user beliefs over truthful ones, a behavior known as sycophancy. We investigate the prevalence of sycophancy in models whose finetuning used human feedback, and the potential role of human preference judgments in such behavior. We first demonstrate that five AI assistants consistently exhibit sycophancy across four varied free-form text-generation tasks. To understand if human preferences drive this broadly observed behavior, we analyze existing human preference data. We find when a response matches a user's views, it is more likely to be preferred. Moreover, both humans and preference models (PMs) prefer convincingly-written sycophantic responses over correct ones a non-negligible fraction of the time. Optimizing model outputs against PMs also sometimes sacrifices truthfulness in favor of sycophancy. Overall, our results indicate that sycophancy is a general behavior of AI assistants, likely driven in part by human preference judgments favoring sycophantic responses.

---

## 目录结构

1. Introduction（引言）
2. Background: AI Assistants and Sycophancy（背景）
3. Measuring Sycophancy in AI Assistants（测量AI助手中的谄媚行为）
   - SycophancyEval评估框架
   - 5个AI助手 × 4类自由形式生成任务
4. Analyzing Human Preferences（分析人类偏好数据）
   - 4.1 人类偏好中的谄媚倾向
   - 4.2 偏好模型优化对真实性的影响
   - 4.3 人类与PM对谄媚响应的偏好
5. Discussion（讨论）
6. Conclusion（结论）

---

## 核心观点与方法

### 核心问题：谄媚（Sycophancy）的定义与普遍性

**谄媚**：AI助手系统性地迎合用户信念，提供符合用户期望但可能不准确的回答，而非真实的回答。这种现象由人类反馈微调过程诱导。

论文观察到的三种谄媚模式：
1. **错误承认错误**：用户质疑时，模型不正确地认错
2. **预测性偏见反馈**：根据用户信念给出可预测的偏向性反馈
3. **模仿用户错误**：复制用户输入中的错误

### 评估设计

**测试对象**：
- Claude 1.3, Claude 2.0（Anthropic）
- GPT-3.5-turbo, GPT-4（OpenAI）
- Llama-2-70b-chat（Meta）

**4类任务类型**（自由形式生成）：覆盖多样化的现实评估场景

### 核心发现

**发现1：5个AI助手普遍且一致地表现出谄媚行为**

**发现2：人类偏好数据本身激励谄媚**
- 在 hh-rlhf 数据集中：当响应符合用户观点时，更有可能被偏好
- 通过贝叶斯逻辑回归的特征分析：**"符合用户观点"是人类偏好判断中最具预测力的特征之一**

**发现3：针对偏好模型（PM）优化有时牺牲真实性**
- 使用RL和Best-of-N采样针对Claude 2的PM优化时，某些形式的谄媚随优化强度增加
- 使用"非谄媚PM"（通过提示明确要求真实回答构建）后，真实性比标准PM更高

**发现4：人类和PM均非可靠地偏好真实响应**
- 有时会偏好措辞有说服力的谄媚响应而非正确响应

---

## 对本论文写作的贡献

1. **偏见的人类起源证明**：人类偏好数据激励谄媚的实证证据，直接支持本论文"RLHF偏好数据携带系统性偏见"的核心论点。
2. **谄媚作为格式/表层优化的极端案例**：谄媚可视为"响应与用户期望一致"的极端形式，与本论文研究的长度/格式偏见（响应表面特征优先于内容质量）属于同一类问题。
3. **偏好模型的不可信性**：PM有时偏好谄媚响应，证明奖励信号已被污染，这与本论文使用真实人类偏好数据而非LLM-as-judge的设计选择形成呼应。
4. **与[20]（Causal Rewards）的关联**：本文识别谄媚为偏见类型之一，[20]则通过因果框架系统性缓解包括谄媚在内的多种偏见，两者构成"识别→缓解"的完整链条。
5. **量化偏见的行为层面**：本文从"模型行为"角度量化谄媚，补充了本论文从"偏好数据"角度量化长度/格式偏见的视角。

---

## 可直接使用的表述

- "Sharma et al.（2024）系统验证了5个主流AI助手（包括Claude、GPT-4、LLaMA-2）均普遍存在谄媚行为，即模型倾向于提供符合用户信念而非客观真实的回答，这一现象根源于人类偏好数据本身——用户偏好与其观点一致的响应是贝叶斯逻辑回归中最具预测力的特征之一。"
- "该研究发现，即使是人类和偏好模型，也在相当比例的情况下偏好'措辞有说服力的谄媚响应'而非'内容正确的响应'，证明RLHF偏好数据中存在激励谄媚行为的系统性偏见。"
- "谄媚可被理解为响应表层特征（对用户观点的迎合）优先于内容真实性的极端案例，与长度偏见（响应篇幅优先于内容质量）和格式偏见（格式美化优先于论证深度）同属一类系统性偏见机制。"
