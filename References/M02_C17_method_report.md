# M02：C17 格式偏好统计检验方法说明

**所属脚本**：`Codes/C17_format_test.py`  
**输出报告**：`Reports/R14_format_test_report.txt`  
**撰写时间**：2026-04-08  
**参照**：M01_C16_method_report.md（保持分析单元与检验框架一致）

---

## 一、研究假设

**核心命题**：在 LMArena 人类偏好评价中，获胜模型的回复在格式使用（标题、列表、粗体）上系统性地多于落败模型。

### 1.1 主假设（配对差值方向性检验）

对每种格式特征 $f \in \{\text{header, list, bold}\}$：

$$H_0^{(f)}: \text{median}(\Delta_i^{(f)}) = 0$$

$$H_1^{(f)}: \text{median}(\Delta_i^{(f)}) > 0$$

其中

$$\Delta_i^{(f)} = \text{count}_f(\text{winner}_i) - \text{count}_f(\text{loser}_i)$$

### 1.2 密度假设（控制长度混淆，辅助）

长度是格式的最大混淆变量——更长的回复理所当然含有更多格式元素。定义**格式密度**：

$$\rho_i^{(f)} = \frac{\text{count}_f(\text{winner}_i)}{\text{tokens}(\text{winner}_i) + 1} - \frac{\text{count}_f(\text{loser}_i)}{\text{tokens}(\text{loser}_i) + 1}$$

同样执行 Wilcoxon 单侧检验（$H_1: \text{median}(\rho) > 0$）。若主检验显著而密度检验不显著，说明格式效应可能是长度效应的代理。

### 1.3 排除标准

`winner ∈ {tie, both_bad}` 的行排除（与 C16 一致），仅保留方向明确的配对。

---

## 二、格式列数据说明

`optimized_data.parquet` 中格式列（`a_header_count`、`a_list_count`、`a_bold_count` 及 `b_*`）以 **Python dict** 形式存储：

```
a_header_count: {'h1': 0, 'h2': 0, 'h3': 8, 'h4': 0, 'h5': 0, 'h6': 0}
a_bold_count:   {'**': 5, '__': 0}
```

提取总数量时，对 dict 的所有 value 求和；若值为 `NaN` 或非 dict 则视为 0。

---

## 三、检验方法

### 3.1 主检验：Wilcoxon 符号秩检验（配对）

与 C16 完全对齐：
- **单侧，$H_1 > 0$**
- 效应量 rank-biserial：$r_{rb} = 1 - 2W^- / (n(n+1))$（$W^-$为 scipy 返回的负秩和，$n$ 为非零差值对数）
- Bootstrap 95% CI（中位差值，1000 次，seed=42）

### 3.2 格式存在性检验：卡方检验

定义二元变量：
$$\text{winner\_has\_format}_i = \mathbb{1}[\text{count}_f(\text{winner}_i) > 0]$$
$$\text{loser\_has\_format}_i = \mathbb{1}[\text{count}_f(\text{loser}_i) > 0]$$

构造 2×2 列联表，执行 Pearson 卡方独立性检验：

|  | 胜者有格式 | 胜者无格式 |
|--|-----------|-----------|
| **败者有格式** | A | B |
| **败者无格式** | C | D |

关注 C 格（"胜者有，败者没有"）与 B 格（"胜者没有，败者有"）的比值——C > B 即初步支持格式偏好。

### 3.3 多重比较校正

策略：**每个子集内** 对 3 个特征的主检验做 Bonferroni 校正（$k=3$）：

$$p_{\text{adj}} = \min(p \times 3,\ 1.0)$$

另额外报告密度检验的原始 $p$ 值（作为参考，不纳入主校正体系）。

> 与 C16 不同，C16 的 $k$ 跨子集计算；C17 改为跨特征计算，因为三种格式特征对同一个命题（"格式偏好"）的检验属于同一族假设。

---

## 四、子集设计

与 C16 完全一致的 10 个子集（全量 + 4 含类 + 4 纯净 + 无类别），保证两个分析模块的可比性。样本量下限 $n_{\min} = 30$（有效对数）。

---

## 五、输出指标清单（R14 每个子集每个特征）

| 字段 | 含义 |
|------|------|
| `feature` | 格式特征（header/list/bold）|
| `n_pairs` | 有效配对数 |
| `n_winner_more` | 胜者格式更多的对数 |
| `pct_winner_more` | 胜者格式更多比例（%）|
| `median_diff` | 中位格式计数差 |
| `ci_low` / `ci_high` | Bootstrap 95% CI |
| `wilcoxon_stat` | Wilcoxon W 统计量 |
| `p_value` | 原始单侧 p 值 |
| `p_bonferroni` | Bonferroni 校正 p 值（×3）|
| `rank_biserial_r` | 效应量 |
| `effect_level` | 效应分级 |
| `density_median_diff` | 密度差中位数 |
| `density_p_value` | 密度检验 p 值（辅助参考）|

---

## 六、方法局限性

1. **长度-格式混淆**：密度检验只能部分控制，彻底分离需要 C19 逻辑回归同时纳入 `tokens_diff`。
2. **格式语义差异**：不同任务中格式的"合适性"不同（数学题加粗可能适得其反）；C17 在任务类别子集中分别检验以初步观察异质性，但不做交互项检验（留 C19）。
3. **dict 格式的测量噪声**：`h3` 与 `h1` 权重相同，实际视觉感知差异被忽略。本模块仍以总数为准，语义加权留未来研究。

---

## 七、与其他模块的关系

```
C16  长度偏好存在性（配对 Wilcoxon）
C17（本模块）  格式偏好存在性（配对 Wilcoxon + 密度控制）
      ↓
C18  效应量综合汇总（Cohen's d, Hedges' g，跨语言/类别）
      ↓
C19  净效应（逻辑回归，格式 + 长度 + 模型能力联合控制）
```
