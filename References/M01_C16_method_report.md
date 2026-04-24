# M01：C16 长度偏好统计检验方法说明

**所属脚本**：`Codes/C16_length_test.py`  
**输出报告**：`Reports/R13_wilcoxon_length_test_report.txt`  
**撰写时间**：2026-04-08  

---

## 一、研究假设

**核心命题**：在 LMArena 人类偏好评价中，获胜模型的回复长度（tokens）系统性地高于落败模型。

### 1.1 正式假设

$$H_0: \text{median}(\delta_i) = 0$$

$$H_1: \text{median}(\delta_i) > 0$$

其中 $\delta_i = \text{tokens}_{\text{winner},i} - \text{tokens}_{\text{loser},i}$，代表第 $i$ 对评价中"胜者"与"败者"回复的 token 数之差。

### 1.2 排除标准

- `winner == 'tie'`：平局无明确胜者，跳过
- `winner == 'both_bad'`：双方均差，无法定义胜者，跳过

仅保留 `winner ∈ {'model_a', 'model_b'}` 的行用于检验，以确保 $\delta_i$ 方向明确。

---

## 二、检验方法选择

### 2.1 为何选择 Wilcoxon 符号秩检验

| 候选方法 | 适用条件 | 本数据情况 | 适用性 |
|---------|---------|----------|--------|
| 配对 t 检验 | 差值服从正态分布 | token 差值高度右偏（长尾），正态假设不成立 | ✗ |
| Wilcoxon 符号秩检验 | 差值分布关于中位数对称（连续分布） | token 差值连续，偏态无妨（秩变换缓解） | ✓ |
| 符号检验 | 仅依赖符号方向 | 效能低于 Wilcoxon，浪费量级信息 | 次优 |

Wilcoxon 符号秩检验不要求差值正态性，仅假设差值分布关于中位数对称（或等价地：差值为连续随机变量），适合本场景。

### 2.2 单侧还是双侧

采用**单侧**检验（右尾）：理论依据（Length Bias 文献）及描述性数据（胜率随长度单调增）均支持方向性假设 $H_1 > 0$，单侧检验统计功效更高。

---

## 三、效应量

仅 p 值不足以描述"实践意义"（n≈8万时极微小效应也可 p<0.001）。

### 3.1 Rank-Biserial 相关系数 $r_{rb}$

scipy 的 `wilcoxon(alternative='greater')` 返回的统计量为**负秩和** $W^-$（差值绝对值较小一侧的秩和），非"正秩和"。因此效应量公式为：

$$r_{rb} = 1 - \frac{2W^-}{n(n+1)}$$

其中 $n$ 为非零差值对数。当多数 $\delta_i > 0$ 时 $W^-$ 较小，$r_{rb}$ 为正，方向符合 $H_1$。

解释：
- $r_{rb} \in [-1, 1]$
- $|r_{rb}| < 0.1$：可忽略效应
- $0.1 \leq |r_{rb}| < 0.3$：小效应
- $0.3 \leq |r_{rb}| < 0.5$：中等效应
- $|r_{rb}| \geq 0.5$：大效应

### 3.2 中位差值 $\tilde{\delta}$ 及 Bootstrap 95% CI

$\tilde{\delta} = \text{median}(\delta_i)$ 直接量化"典型情况下胜者多说了多少 tokens"，具有直观可解释性。

Bootstrap 置信区间（1,000 次重采样，百分位法）：

$$\text{CI}_{95\%} = [\hat{\delta}_{2.5\%},\ \hat{\delta}_{97.5\%}]$$

---

## 四、多重比较校正

C16 对多个子集（全量 + 4 单类 + 多个纯净分区）分别执行独立检验，存在多重比较问题。

**校正方法**：Bonferroni 校正

$$p_{\text{adj}} = \min(p \times k,\ 1.0)$$

其中 $k$ 为实际执行检验的子集数量（动态计算，排除 n < 30 的子集）。

**理由**：研究目的是**发现性**（确认偏好是否系统存在），Bonferroni 因保守性强（控制 FWER）而被优先采用；若结论为"多数子集在 Bonferroni 校正后仍显著"，推论强度最高。

---

## 五、子集选择策略

### 5.1 主检验子集

| 子集 | 来源文件 | 说明 |
|------|---------|------|
| all_data | optimized_data.parquet | 全量（基准） |
| creative_writing_true | creative_writing_true_data.parquet | 含 CW（允许重叠） |
| if_true | if_true_data.parquet | 含 IF（允许重叠）|
| math_true | math_true_data.parquet | 含 MATH（允许重叠）|
| code_true | code_true_data.parquet | 含 CODE（允许重叠）|
| only_cw | only_cw_data.parquet | 仅 CW |
| only_if | only_if_data.parquet | 仅 IF |
| only_math | only_math_data.parquet | 仅 MATH |
| only_code | only_code_data.parquet | 仅 CODE |
| no_category | no_category_data.parquet | 无任何类别标签 |

共 **10 个子集**，与旧版 C16 保持数量一致，但子集定义更新为适配 4 类体系。

### 5.2 样本量下限

$n_{\min} = 30$（有效对数，排除 tie/both_bad 后）。对于 $n < 30$ 的子集（如 `cw_math_code`  n=2，`all_categories` n=4），跳过检验并在报告中注明。Bonferroni 的 $k$ 仅计入实际执行检验的子集数。

---

## 六、输出指标清单（R13 报告每个子集包含）

| 字段 | 含义 |
|------|------|
| `n_pairs` | 有效对数（winner ∈ {model_a, model_b}） |
| `n_winner_longer` | 胜者更长的对数 |
| `pct_winner_longer` | 胜者更长比例（%） |
| `median_diff` | $\tilde{\delta}$（tokens，胜者 − 败者）|
| `ci_low` / `ci_high` | Bootstrap 95% CI 下/上界 |
| `wilcoxon_stat` | Wilcoxon W 统计量 |
| `p_value` | 原始单侧 p 值 |
| `p_bonferroni` | Bonferroni 校正后 p 值（×k，截断至 1.0）|
| `rank_biserial_r` | 效应量 $r_{rb}$ |
| `effect_level` | 效应分级（可忽略/小/中/大）|
| `significant` | 是否在 α=0.05 下显著（基于校正后 p 值）|

---

## 七、方法局限性

1. **配对独立性**：同一会话的多个 order 行已由 C12 过滤（仅保留 order=1），但同一用户的不同会话仍视为独立配对，忽略了用户内相关。

2. **Wilcoxon 对称假设**：若 $\delta_i$ 的分布高度非对称（如存在大量极端正值），检验功效可能虚高；Bootstrap CI 不依赖此假设，将作为独立验证。

3. **Bonferroni 保守性**：子集间并非独立（含重叠行），Bonferroni 对 FWER 的控制可能过于严格，实际 FDR 更低。此处作为保守基准。

4. **因果解释**：本检验仅建立相关，不确立因果关系（"更长导致获胜"vs"评分标准更易给奖 → 同时产生更长回复"）。因果分析留待 C19–C22。

---

## 八、与其他模块的关系

```
C16（本模块）  → 证明长度偏好存在（单变量配对检验）
      ↓
C17            → 证明格式偏好存在（单变量配对检验，格式差值 Wilcoxon）
      ↓
C18            → 净效应嵌套逻辑回归（长度 M0→M3；格式 F0→F3）
      ↓
C19–C22        → 稳健性、匹配诊断与 SEM 机制解释
```
