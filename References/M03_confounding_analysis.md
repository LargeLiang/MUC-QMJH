# 混淆变量分析报告
**项目**：基于大语言模型输出文本的选择偏好研究（MUC 青苗计划）  
**报告时间**：2026-04-10  
**依据**：R13（长度检验）、R14（格式检验）及数据架构审查

---

## 一、研究问题与因果模型

### 核心因果主张

本研究试图论证：**回复长度和格式本身会导致人类评注者更倾向于选择该回复**，与回复质量无关。

$$\text{Length/Format} \xrightarrow{?} \text{Human Preference}$$

若不控制混淆，观测到的关联（R13: r_rb = 0.336）同样可以由下面的替代路径解释：

$$\text{Model Quality} \rightarrow \text{Longer + Better Response} \rightarrow \text{Preference}$$
$$\text{Task Type} \rightarrow \text{Longer Expected Response} \rightarrow \text{Preference}$$

---

## 二、混淆变量完整分类

### 2.1 类型 I：问题级混淆（Prompt-level Confounders）

这些变量影响"这道题理应回答多长、多格式化"，与具体模型无关。

| 混淆变量 | 混淆路径 | 操作化列 | C19 当前状态 |
|---------|---------|---------|-------------|
| **任务类型** | 代码/数学题本身要求更长的结构化输出 | `creative_writing_bool`, `if_bool`, `math_bool`, `code_bool` | ✅ 已纳入 |
| **Prompt 复杂度** | 复杂问题引发更长、结构化程度更高的回复 | 7 个 `criteria` 布尔（`complexity` 等）| ✅ 已纳入 |
| **Prompt 长度** | 长问题通常要求长回复 | `user_tokens` | ✅ 已纳入 |
| **对话轮数** | 多轮对话语境更丰富，单次回复可能更短 | `turns` | ✅ 已纳入 |
| **语言** ⚠️ | 语言文化圈对格式的规范不同（日语/中文 markdown 使用率更低）| `language`（可生成 `lang_en_bool`）| ❌ **遗漏** |

> **语言混淆的规模**：optimized_data 保留 126 种语言，英语仅占 ~52.5%。不同语言用户对 markdown 格式的偏好存在系统性差异，这是一个尚未控制的偏差来源。

---

### 2.2 类型 II：模型级混淆（Model-level Confounders）——最大遗漏

**这是当前研究最严重的漏洞。** `model_a` 和 `model_b` 列在 optimized_data 中完整保留，但 C19/C20/C21 均未利用。

强模型可能**系统性地**同时产出更长、更格式化且更高质量的回复，导致以下虚假关联：

$$\text{Better Model} \rightarrow \text{Longer Reply} \rightarrow \text{Win}$$
$$\text{Better Model} \rightarrow \text{More Formatted} \rightarrow \text{Win}$$

#### 2.2.1 需要计算的模型级统计量

| 代理变量 | 计算方法 | 代理含义 |
|---------|---------|---------|
| `wr_a` | 模型 A 在全数据集的胜率 | 模型综合能力 |
| `wr_b` | 模型 B 在全数据集的胜率 | 模型综合能力 |
| `ability_diff` = `wr_a − wr_b` | 两模型胜率之差 | 本次对决的能力不对称程度 |
| `verbosity_a` | 模型 A 在全数据集的平均 token 数 | 模型固有词冗性 |
| `verbosity_diff` = `verbosity_a − verbosity_b` | 词冗性差异 | 与质量无关的长度风格差异 |
| `format_tendency_a` | 模型 A 的平均总格式元素数 | 模型固有格式风格 |
| `format_tendency_diff` = `format_tendency_a − format_tendency_b` | 格式风格差异 | 与质量无关的格式偏好 |

> **验证实验（前置步骤）**：检验各模型胜率 vs 平均回复长度的 Spearman 相关性。若 |r| > 0.3，则证明模型能力—长度共线性成立，纳入控制为必要操作。

#### 2.2.2 实证预期

基于 R04 数据，53 个模型胜率从 0% 到 54.82%（gemini-2.5-pro），差异极大。若强模型确实更冗长，则在不控制 `ability_diff` 的情况下，`r_rb = 0.336` 中有一部分实为模型能力效应的代理。

---

### 2.3 类型 III：数据生成机制混淆（Arena Mechanism Confounders）

| 混淆变量 | 机制描述 | 可处理性 |
|---------|---------|---------|
| **位置偏差**（左/A 偏）| lmarena 中 model_a 在左侧，可能存在阅读习惯偏向 | 检验 P(winner=A) 是否接近 0.5；由截距项（intercept）部分吸收 |
| **评注者异质性** | 不同用户对长度偏好不同，无用户 ID 可控制 | ❌ 不可观测，构成残差方差 |
| **时序效应** | 较新的模型可能更长也更好 | 无时间戳；由 `ability_diff`（胜率代理）间接控制 |

---

### 2.4 类型 IV：当前 C21 的结构性错误

C21 的 `ability_quality/clarity/task_difficulty` **看似是模型能力代理，实则不是**。

它们由 `criteria` 字段（complexity、creativity 等 7 维布尔值）聚合而来。但这 7 个维度是**问题级标签**，同一行的 model_a 和 model_b 取值**完全相同**。

因此这些变量：
- ✅ 可以描述**问题难度**（任务需要多复杂的回复）
- ❌ **无法** 区分两个模型在同一问题上的回复质量差异
- ❌ **不能** 用于控制模型能力混淆

---

### 2.5 关于 criteria 字段的正确定位

| 用途 | 结论 | 理由 |
|------|------|------|
| 作为**混淆变量**控制（回归协变量）| ✅ **正确** | 问题复杂度影响"该题型的典型回复有多长"，是 prompt→长度→偏好路径上的混淆 |
| 作为 **SEM 中介变量**（length→criteria→preference）| ❌ **错误** | 同一行 a、b 的 criteria 值相同，无法解释"为何这条回复比另一条更受偏好" |

---

## 三、净效应量计算方案

### 3.1 分析框架

**配对偏好逻辑回归**：结果变量 `winner_a ∈ {0,1}`；核心预测变量 `token_diff_ab = a_tokens − b_tokens`。

通过**嵌套模型序列**观察 β_token_diff 的衰减，量化各层混淆的贡献。

### 3.2 五层嵌套模型

$$\text{Model 0}：\text{winner\_a} \sim \beta_0 \cdot \text{token\_diff}$$

$$\text{Model 1}：\text{winner\_a} \sim \beta_1 \cdot \text{token\_diff} + \text{任务类型} + \text{用户 tokens} + \text{对话轮数}$$

$$\text{Model 2}：+ \text{criteria（7 个维度）}$$

$$\text{Model 3}：+ \text{lang\_en\_bool（语言控制）}$$

$$\text{Model 4}：+ \text{ability\_diff（模型能力差异）}$$

$$\text{Model 5}：+ \text{verbosity\_diff} + \text{format\_tendency\_diff（模型风格差异）}$$

> Model 5 的 β_token_diff 为**净效应估计**。

### 3.3 净效应量指标

| 指标 | 计算方法 | 解释 |
|------|---------|------|
| **调整后 Odds Ratio** | $\exp(\hat{\beta}_{\text{token\_diff}}^{M5})$ | 每增加 1 token 差值，偏好 A 的比数倍数 |
| **标准化 AME** | 平均边际效应 × SD(token_diff) | P(win) 随长度变化 1 SD 对应的平均变化量 |
| **Wald 部分相关 r** | $r = z_\text{wald}/\sqrt{N}$ | 控制所有混淆后的效应大小，可与 r_rb = 0.336 直接比较 |
| **混淆比例** | $(OR_0 - OR_5) / (OR_0 - 1)$ | 原始效应中由混淆解释的百分比 |

### 3.4 稳健性检验方案

| 方案 | 方法 | 优势 | 对应脚本 |
|------|------|------|---------|
| **IPW** | 以 `longer_a` 为处理变量，估计倾向得分，IPW 加权后计算 ATE | 非参数，不依赖函数形式假定 | C19（新） |
| **Within-pair Wilcoxon** | 固定模型对（model_a × model_b 组合）内部分别做 Wilcoxon，再 meta-analysis 加权合并 | 完全控制模型身份混淆 | C20 |
| **模型固定效应** | 逻辑回归加入 53 个 model_a + 53 个 model_b 虚拟变量 | 吸收所有模型级固定特征 | C18 Model 6（可选）|

---

## 四、实施优先级

| 优先级 | 任务 | 脚本 | 说明 |
|--------|------|------|------|
| 🔴 P0 | 计算模型级统计量（胜率、平均长度、平均格式）| C18 前置 | 必须先计算 `ability_diff` 等字段 |
| 🔴 P0 | 嵌套逻辑回归 Model 0→5，报告 β 衰减路径 | C18 | 核心净效应分析 |
| 🔴 P0 | 报告混淆比例 $(OR_0 - OR_5)/(OR_0 - 1)$ | C18 | 判断效应有多少是真实的 |
| 🟡 P1 | IPW 稳健性检验 | C19 | 非参数验证 |
| 🟡 P1 | Within-pair Wilcoxon（按固定模型对）| C20 | 最纯粹的模型混淆控制 |
| 🟢 P2 | 语言子集（英语/非英语）分层重复上述分析 | C18 扩展 | 稳健性补充 |

---

## 五、预期结论场景

| 场景 | β_token_diff 在 M5 的变化 | 解释 |
|------|--------------------------|------|
| **A. 效应稳健** | 衰减 < 30%，OR 仍显著 | 长度偏好是真实的人类审美偏好，与模型质量相对独立 |
| **B. 部分混淆** | 衰减 30%–70% | 长度偏好真实存在但被模型质量放大；论文需注明混淆比例 |
| **C. 主要混淆** | 衰减 > 70%，OR 不显著 | 观测到的长度偏好主要是"强模型更冗长"的副产品；主张须大幅修正 |

基于现有数据（53 模型胜率 0%–54.82%，极度分化），**预期场景 B** 概率最高，即长度效应真实但被部分模型质量混淆放大。
