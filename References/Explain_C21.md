# C21_enhanced_matching_diagnostics 代码详解

> 来源文件：`Codes/C21_enhanced_matching_diagnostics.py`  
> 产出文件：`Reports/R19_enhanced_diagnostics_report.txt`、`Tables/T09_matching_summary.csv`、`Tables/T10_matching_balance.csv`、`Pictures/P12_matching_diagnostics_overview.png`

---

## 一、研究问题与分析目标

C19 用 IPW 估计了长度效应，但 IPW 依赖"无未观测混淆"假设，且极端权重可能使估计不稳定。C21 用另一条完全独立的因果推断路径——**倾向得分匹配（PSM）**——来验证 C19 的结论，并专注于回答一个 C19 无法直接回答的诊断性问题：

> "匹配之后，处理组和控制组在混淆变量上是否真正实现了均衡？"

C21 的贡献不仅是"再算一遍处理效应"，更是对整个倾向得分框架的**方法论质量检验**（即"匹配质量诊断"）。如果匹配后混淆变量不均衡，则所有基于倾向得分的因果推断（包括 C19 的 IPW）的可信度都值得怀疑。

---

## 二、方法选择

### 2.1 为什么用 PSM 而不只用 IPW

| 方法 | IPW（C19） | PSM（C21） |
|------|-----------|-----------|
| 如何消除混淆 | 用倾向得分倒数加权，重新平衡两组 | 为每个处理样本找到最相似的控制样本 |
| 处理效应估计 | 加权均值差 ATE | 匹配后均值差 ATT（处理组的平均处理效应） |
| 可视化诊断 | 较难直接可视化均衡性 | SMD 前后对比（Love plot）直观展示均衡效果 |
| 样本损失 | 无（全量加权） | 有（未匹配样本丢弃） |
| 假设依赖 | 倾向得分模型设定正确 | 倾向得分模型设定正确 + 共同支持假设 |

PSM 的特有优势是**可诊断性**：通过计算匹配前后的 SMD（标准化均值差），可以客观评估混淆变量是否均衡，而 IPW 只给出最终的 ATE 估计，不直接提供均衡质量的数值证据。

### 2.2 标准化均值差（SMD）作为均衡性指标

SMD（Standardized Mean Difference）是比较两组在某变量上分布差异的标准化指标：

$$\text{SMD} = \frac{\bar{X}_{\text{treated}} - \bar{X}_{\text{control}}}{\sqrt{\frac{s_{\text{treated}}^2 + s_{\text{control}}^2}{2}}}$$

优点：不依赖样本量（不像 t 检验会随 n 变大而变显著），是观测性研究中评估共变量均衡的黄金标准。

经验阈值：$|\text{SMD}| < 0.1$ 被广泛用作"基本均衡"的判定标准。

### 2.3 1:1 最近邻匹配与 caliper

C21 使用 **1:1 最近邻匹配**（有放回），在 logit 变换后的倾向得分（logit ps）空间中寻找最近的控制组样本。使用 logit 变换而非原始 ps 的原因：原始 ps 分布在 (0, 1)，极端值附近（接近 0 或 1）的配对距离被压缩；logit 变换将 ps 映射到 $(-\infty, +\infty)$，使距离更均匀。

**caliper = 0.2 × SD(logit ps)**：限制匹配距离的上界，防止"硬匹配"（强制为每个处理样本找一个控制样本，即使最近邻也很远）。0.2 × SD 是 Austin (2011) 推荐的经验准则。超出 caliper 的处理样本放弃匹配（match rate < 1.0 时记录）。

---

## 三、实现逻辑

### 3.1 整体流程

```
全量 parquet → build_model_stats()
        ↓
for 每个子集（全量 + 16 纯净子集）：
    prepare_subset_for_robustness()  ← 完全复用 C19
    fit_propensity_scores()          ← 完全复用 C19
        ↓
    match_with_caliper(s, pscore)
        → 计算 logit_ps、caliper
        → NearestNeighbors(n_neighbors=1).kneighbors 对 logit_ps 做 1:1 匹配
        → 筛选距离 ≤ caliper 的匹配对
        → 计算公共支持区间和覆盖率
        ↓
    build_balance_rows(treated_before, control_before, treated_after, control_after)
        → 对每个 confounder 计算 before/after 的 SMD
        ↓
    paired_wilcoxon_test(treated_matched, control_matched)
        → 对匹配后的 winner_a 做配对 Wilcoxon（one-sided, zsplit）
        ↓
汇总 → plot_matching_diagnostics() → generate_report()
        ↓
输出 R19 / T09 / T10 / P12
```

### 3.2 关键函数

#### `standardized_mean_difference(treated, control)`

```python
pooled_std = np.sqrt((treated.std(ddof=1)**2 + control.std(ddof=1)**2) / 2)
if pooled_std < 1e-10:
    return 0.0  # 两组完全相同
return (treated.mean() - control.mean()) / pooled_std
```

对零方差情况做安全处理（返回 0 而非 NaN 或错误）。

#### `build_balance_rows(...)`

对每个混淆变量分别计算：
- 匹配前（before）：全量处理组 vs 全量控制组的 SMD
- 匹配后（after）：匹配样本处理组 vs 匹配样本控制组的 SMD

返回长格式 DataFrame（每个变量 × 每个阶段一行），供 T10 和 Love Plot 使用。

#### `match_with_caliper(s, pscore)`

1. 计算 logit_ps：`logit_ps = log(ps / (1 - ps))`
2. 设置 caliper = 0.2 × SD(logit_ps)
3. 将数据分为 treated（`longer_a == 1`）和 control（`longer_a == 0`）
4. 用 `sklearn.neighbors.NearestNeighbors` 在 logit_ps 空间中 1D 最近邻搜索
5. 只保留距离 ≤ caliper 的匹配对
6. 计算公共支持区间（treated 和 control 的 ps 范围交集）及其覆盖率
7. 返回 `(treated_matched, control_matched, diag)`，其中 `diag` 包含匹配诊断指标

注意：`NearestNeighbors` 用于 1D 最近邻（只有 logit_ps 一维），比直接排序更易扩展到多维。

#### `paired_wilcoxon_test(treated_matched, control_matched)`

```python
stat, pval = wilcoxon(
    treated_matched["winner_a"].to_numpy(dtype=float),
    control_matched["winner_a"].to_numpy(dtype=float),
    alternative="greater",  # 单侧：处理组获胜率更高
    zero_method="zsplit",
)
```

匹配后的配对样本天然构成配对数据，Wilcoxon 配对检验比独立样本 t 检验更适合（依然非正态）。

#### `plot_matching_diagnostics(summary_df, balance_df, picture_path)`

双面板图：
- **左面板**（overview）：每个子集一行，左侧橙点 = 匹配前 mean|SMD|，右侧绿点 = 匹配后 mean|SMD|，竖线连接，直观展示每个子集的改善幅度；虚线标出 0.1 阈值。
- **右面板**（Love plot）：以全量子集为例，每个混淆变量一行，展示该变量匹配前/后的 |SMD|，直接判断哪些变量均衡充分、哪些仍有残余不均衡。

### 3.3 产出文件

| 文件 | 内容 |
|------|------|
| `Reports/R19_enhanced_diagnostics_report.txt` | 逐子集的匹配对数、caliper、公共支持、SMD 改善、ATE、Wilcoxon p |
| `Tables/T09_matching_summary.csv` | 每子集汇总行（匹配质量指标 + ATE） |
| `Tables/T10_matching_balance.csv` | 长格式均衡表（每变量 × 每阶段，全部子集） |
| `Pictures/P12_matching_diagnostics_overview.png` | Overview 面板 + 全量 Love plot |

---

## 四、结论分析

### 4.1 全量匹配结果

| 指标 | 数值 |
|------|------|
| 样本量 | 78,783 |
| 匹配对数 | **39,237**（match rate = 100.0%） |
| caliper(logit_ps) | 0.371 |
| 公共支持覆盖率 | 100.0% |
| max\|SMD\| | 1.473 → **0.177**（大幅改善） |
| mean\|SMD\| | 0.250 → **0.060**（≈ 一阶数量级改善） |
| 匹配后 ATE | **+0.160** |
| 配对 Wilcoxon p | **< 1×10⁻³⁰⁰**（极显著） |

匹配前的 max|SMD| = 1.47 说明处理组和控制组在某些混淆变量（如 `verbosity_diff`）上分布极不均衡；匹配后降至 0.18，mean|SMD| 降至 0.06（低于 0.1 阈值），说明 PSM 显著改善了均衡性，尽管 max|SMD| = 0.18 仍略高于理想阈值（0.1），说明有少数变量仍有残余不均衡。

匹配后 ATE = 0.160 与 C19 的 IPW ATE = 0.149 非常接近，两种方法结论高度一致。

### 4.2 跨子集均衡改善情况

| 子集 | mean|SMD|改善 | max|SMD|匹配后 | Wilcoxon p | 结论 |
|------|-------------|------------|-----------|------|
| 无类别 | 0.345 → 0.092 | 0.291 | < 1×10⁻²⁵⁴ | ✓ 显著 |
| 仅代码 | 0.331 → 0.076 | 0.183 | < 1×10⁻¹¹² | ✓ 显著 |
| 指令+代码 | 0.271 → 0.031 | 0.083 | 1.1×10⁻²⁴ | ✓ 均衡最好 |
| 仅数学 | 0.308 → 0.073 | 0.179 | 2.2×10⁻⁵ | ✓ 显著（弱） |
| 数学+代码 | 0.306 → 0.114 | 0.251 | 0.031 | ✓ 边缘 |
| 创意+代码 | 0.304 → 0.097 | 0.306 | 0.551 | ✗ 不显著 |
| 创意+指令+代码 | 0.319 → 0.224 | 0.483 | 0.294 | ✗ 小样本，均衡差 |

- **所有子集**的 mean|SMD| 均在匹配后显著降低，证明 PSM 过程有效；
- **大多数主要子集**（n > 1000）均衡到 mean|SMD| < 0.1 阈值；
- 小样本交叉子集（n < 300）匹配质量差，残余均衡不足，ATE 估计不可靠——这与 C19 中同类子集的 IPW CI 宽且跨 0 的发现一致。

### 4.3 对 C19 IPW 结论的验证

| 全量指标 | C19 IPW | C21 PSM |
|---------|---------|---------|
| ATE 估计 | +0.149 | +0.160 |
| 显著性 | ✓ CI [0.135, 0.161] | ✓ Wilcoxon p ≈ 0 |
| 方向 | 长度优势 → 获胜优势 | 长度优势 → 获胜优势 |

两种方法的 ATE 差距仅 0.011（约 7%），在不同假设下给出高度一致的结论，极大增强了"长度偏好在控制混淆后仍显著存在"的证据强度。

---

## 五、设计细节与注意事项

1. **完全复用 C19 的数据准备与倾向得分函数**：`from C19_length_effect_robust import fit_propensity_scores, prepare_subset_for_robustness`，确保口径一致。任何对 C19 这两个函数的修改都会同步影响 C21 的结果。
2. **有放回匹配**：允许控制组同一样本被多次匹配（有放回），减少样本损耗，代价是估计的是 ATT（处理组平均效应）而非 ATE（全样本平均效应）。对于本研究问题（"被呈现给更长回答时效应有多大"），ATT 更有针对性。
3. **Love plot 选全量子集**：图的右面板固定展示"全量"子集的变量级 SMD（若"全量"不在数据中，则取第一个子集），保证最大可读性（全量变量最全，图最完整）。
4. **两张输出表**：T09 是"宽表"（每子集一行，汇总指标），T10 是"长表"（每变量 × 阶段 × 子集一行），两者服务于不同的下游使用场景（T09 写入报告摘要，T10 可供后续精细可视化或 meta 分析）。
5. **`zero_method="zsplit"` 与 C16/C17 一致**：所有 Wilcoxon 检验统一使用相同的零值处理策略，保证跨脚本结论的可比性。
