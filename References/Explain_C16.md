# C16_length_test 代码详解

> 来源文件：`Codes/C16_length_test.py`  
> 产出文件：`Reports/R13_wilcoxon_length_test_report.txt`、`Tables/T03_length_wilcoxon_summary.csv`、`Pictures/P06_length_wilcoxon_overview.png`

---

## 一、研究问题与分析目标

C14 和 C15 已完成长度与格式偏好的可视化描述，确认了"胜者更长"的初步趋势。C16 的任务是对这一趋势做严格的**统计假设检验**：在全量和各任务子集中，人类偏好是否存在系统性的长度偏差？偏差的量级和跨任务稳定性如何？

具体来说，C16 回答三个问题：
1. 在配对对决中，"获胜回答更长"是否显著优于偶然水平？
2. 效应量有多大？是可忽略的微弱偏差还是中等效应？
3. 这种偏差是否跨所有任务类型普遍存在？

---

## 二、方法选择

### 2.1 为什么选 Wilcoxon 符号秩检验

每一行数据是一次 model_a vs model_b 的配对对决，核心变量是：

$$\delta_i = \text{tokens}(\text{winner}_i) - \text{tokens}(\text{loser}_i)$$

这是一个配对差值，检验问题是"$\delta$ 的中位数是否显著大于 0"。相比 t 检验，选择 Wilcoxon 的理由：
- **分布不满足正态假设**：token 差值分布极度右偏、零值密集、存在大量离群值，违反 t 检验的正态假设。
- **配对结构**：每一对 (winner, loser) 是对应同一次对决的配对观测，Wilcoxon 符号秩正是为配对非参数场景设计的。
- **单侧检验**：研究假设明确（H₁：胜者倾向于更长），使用单侧检验既更有功效，也更符合理论预期。

### 2.2 多重比较与 Bonferroni 校正

C16 对 17 个子集（全量 + 16 个分区）依次做检验，每个子集是独立的假设。若不校正，多检验会膨胀家族误差率（FWER）。C16 采用 **Bonferroni 校正**，$k$ 取"实际成功执行的子集数"（非 17），这是因为样本量不足的子集会被 MIN_PAIRS=30 跳过，用实际 k 比用固定 17 更保守、也更合理。

本次实际执行了 **13 个子集**，$k=13$，校正显著性阈值 $\alpha/k = 0.05/13 \approx 0.0038$。

### 2.3 效应量：rank-biserial 相关系数

p 值只说"是否显著"，不说"有多大"。C16 用 **rank-biserial 相关系数** $r_{rb}$ 作为效应量：

$$r_{rb} = 1 - \frac{2W^-}{n(n+1)}$$

其中 $W^-$ 是负秩和，$n$ 是非零差值对数。$r_{rb}$ 的取值范围是 $[-1, 1]$，约定：
- $|r| < 0.1$：可忽略
- $0.1 \le |r| < 0.3$：小效应
- $0.3 \le |r| < 0.5$：中效应
- $|r| \ge 0.5$：大效应

同时输出 Cohen's d 和 Hedges' g 作为参数近似参考（标注"仅供参考"，因为正态假设并不成立）。

### 2.4 Bootstrap 中位数置信区间

中位数比均值对偏态分布更稳健，但中位数的解析置信区间很难计算。C16 使用 **Bootstrap 百分位法**（1000 次重采样，seed=42）估计中位长度差的 95% CI，提供一个对非正态分布安全的区间估计。

---

## 三、实现逻辑

### 3.1 整体流程

```
全量 + C13 子集 parquet（共 17 个）
        ↓ 只读 winner / metadata_a / metadata_b 三列（减少 IO）
with_flat_analysis_columns()  ← 从 metadata 嵌套列展平 a_tokens / b_tokens
        ↓
过滤 winner ∈ {model_a, model_b}（排除 tie / both_bad）
        ↓
for 每个子集：
    _build_diff()            ← 构造方向对齐的 δ 差值数组
    run_one_subset()         ← 计算胜率 / 中位数 / Bootstrap CI / Wilcoxon / r_rb / Cohen's d
        ↓
Bonferroni 校正（k = 实际执行子集数）
        ↓
build_summary_df() → plot_length_overview() → generate_report()
        ↓
输出 R13 / T03 / P06
```

### 3.2 关键函数

#### `_build_diff(df)`

```python
def _build_diff(df: pd.DataFrame) -> np.ndarray:
    # 根据 winner 决定差值方向
    # model_a 胜 → a_tokens - b_tokens
    # model_b 胜 → b_tokens - a_tokens
```

这是整个脚本的基础操作——把 A/B 两侧的 token 数"对齐到胜者方向"，使正值始终代表"胜者更长"。`oriented_winner_difference()` 在 `accessor.py` 中实现，用 `np.where` 向量化处理，避免逐行循环。

#### `run_one_subset(label, df)`

单个子集完整统计计算的入口：

1. 调用 `_build_diff()` 得到 $\delta$ 数组；
2. 统计非零差值数和胜者更长比例；
3. 用 `_bootstrap_ci()` 计算中位数 95% Bootstrap CI；
4. 用 `scipy.stats.wilcoxon` 做单侧 Wilcoxon 检验；
5. 计算 rank-biserial r 和 Cohen's d / Hedges' g；
6. 返回统计摘要字典（`p_bonferroni` 留空，主流程统一填充）。

注意：Wilcoxon 需要零差值处理策略，代码使用 `zero_method="zsplit"`（零差值各半分给正负秩）。

#### `_bootstrap_ci(arr, n_boot, seed)`

Bootstrap 百分位法实现：

```python
for _ in range(n_boot):
    sample = rng.choice(arr, size=len(arr), replace=True)
    medians.append(np.median(sample))
return np.quantile(medians, [0.025, 0.975])
```

使用 `np.random.default_rng(seed)` 保证可复现性。

#### `_effect_level(r)`

按 Cohen (1988) 分级标准将 $|r_{rb}|$ 转换为可读标签（可忽略 / 小 / 中 / 大）。

#### `run_length_test()`（主流程）

- 只读 `winner`、`metadata_a`、`metadata_b` 三列（约减少 30% IO 开销）；
- 调用 `get_analysis_subset_paths()` 统一获取"全量 + 16 个纯净子集"的路径字典；
- 循环逐子集执行，收集结果列表；
- 事后统一做 Bonferroni 校正（k = len(valid_results)）。

#### `build_summary_df()` 与 `plot_length_overview()`

`build_summary_df()` 将所有结果列表转为 DataFrame，并添加效应等级列。

`plot_length_overview()` 绘制**双面板气泡图**：
- 左面板：中位长度差及其 Bootstrap 95% CI（水平误差线）；
- 右面板：rank-biserial r 效应量；
- 点大小编码样本量（$s = \text{clip}(\sqrt{n_{pairs}} \times 1.6, 36, 180)$），全量子集用深色突出。

### 3.3 产出文件

| 文件 | 内容 |
|------|------|
| `Reports/R13_wilcoxon_length_test_report.txt` | 逐子集的完整检验摘要（样本量、胜率、中位差、CI、p 值、效应量） + 跨子集汇总表 |
| `Tables/T03_length_wilcoxon_summary.csv` | 结构化宽表，每子集一行，供后续分析读取 |
| `Pictures/P06_length_wilcoxon_overview.png` | 双面板气泡图 |

---

## 四、结论分析

### 4.1 全量结果：显著的中等效应

| 指标 | 数值 |
|------|------|
| 有效配对数 | 78,970 |
| 胜者更长比例 | **62.21%** |
| 中位长度差 | **+125 tokens** [Bootstrap 95% CI: +121, +130] |
| Wilcoxon p（Bonferroni 后）| 0.0000（< $10^{-300}$） |
| rank-biserial r | **0.336**（中效应） |

解读：在七万八千余次对决中，约有 62% 是"长回答赢了短回答"，中位数上赢家比输家多 125 个 token。这不是微弱偏差，rank-biserial r = 0.34 已进入中效应区间，意味着有约 67% 的概率随机从胜者一侧抽到更大的差值。

### 4.2 跨任务对比：12/13 子集显著

唯一不显著的子集是**创意+数学**（n=18，样本量过小导致检验力不足），其余 12 个子集全部在 Bonferroni 校正后显著。

| 子集 | 中位长度差 | $r_{rb}$ |
|------|-----------|---------|
| 指令+代码 | **+256 tokens** | 0.406 |
| 仅代码 | +203 tokens | 0.371 |
| 无类别 | +121 tokens | 0.316 |
| 全量 | +125 tokens | 0.336 |
| 仅创意写作 | +60 tokens | 0.345 |
| 仅数学 | **+56 tokens** | 0.384 |

技术类任务（代码、指令+代码）的中位长度差最大，可能因为完整的代码块、解释步骤天然需要更多篇幅；数学任务的中位差最小，但 $r_{rb}$ 反而最高（0.38），说明数学任务中"更长"的效应虽然在绝对量上较小，但在配对比较中方向一致性更强。

### 4.3 效应量的统一特征

所有 12 个显著子集的 $r_{rb}$ 均落在 **0.31～0.43** 之间，全部属于中效应。这一高度一致性说明长度偏好的强度跨任务是稳定的，不存在某个子集特别突出或特别弱化的情况。Cohen's d 普遍在 0.15～0.22 之间，参数效应量较小，与 $r_{rb}$ 反映的"配对方向一致性"的视角互补——长度偏好是稳定的配对方向性偏差，而不是两组分布均值差异极大的情况。

### 4.4 C16 在证据链中的位置

C16 提供"**现象存在**"层面的证据：长度偏好在统计上是真实的、跨任务的、中等量级的。但它无法回答"多少偏好来自混淆、多少是真实偏好"——这是后续 C18～C21 要解决的问题。

---

## 五、设计细节与注意事项

1. **MIN_PAIRS = 30**：少于 30 个有效配对时跳过，防止小样本 Wilcoxon 检验失效（n 太小时正态近似不准）。
2. **只读三列**：主流程只加载 `winner`、`metadata_a`、`metadata_b`，`with_flat_analysis_columns()` 负责在内存中临时解包 token 字段，不修改磁盘文件。
3. **Bonferroni k 动态计算**：取"实际执行成功的子集数"而非固定 17，避免因少数子集跳过导致不必要的过度校正。
4. **seed=42**：Bootstrap 使用固定随机种子确保结果可复现；`np.random.default_rng` 比 `np.random.seed` 更现代、线程安全。
5. **`zero_method="zsplit"`**：差值为零时各半计入正负秩，是 Wilcoxon 的标准保守做法，避免直接丢弃零差值引入偏差。
