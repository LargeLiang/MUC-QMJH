# C19_length_effect_robust 代码详解

> 来源文件：`Codes/C19_length_effect_robust.py`  
> 产出文件：`Reports/R17_length_effect_robust_report.txt`、`Tables/T07_length_robust_summary.csv`、`Pictures/P10_length_robust_forest.png`

---

## 一、研究问题与分析目标

C18 通过嵌套逻辑回归（M0→M3）量化了混淆程度，并给出了净效应的 OR 估计。C19 的任务是用**不同的因果推断方法**重复 C18 的核心结论，回答：

> "若用'处理-控制'框架代替连续变量框架，长度优势的处理效应是否依然稳健？"

具体地，C19 将连续变量 `token_diff_ab` 二值化为**处理变量** `longer_a`（A 是否更长），然后同时使用两条独立的分析路径估计"A 更长"对"A 获胜"的因果效应：

1. **调整逻辑回归**：在粗模型（只有 `longer_a`）基础上纳入所有可用混淆变量，得到调整 OR；
2. **稳定化 IPW（逆概率加权）**：估计每个观测被分配到"A更长"组的倾向得分，用倒数权重消除混淆，计算 ATE（平均处理效应）并用 Bootstrap 构建 95% CI。

两条路径对混淆的控制方式截然不同，若结论一致，则提供更强的稳健性证据。

---

## 二、方法选择

### 2.1 二值化处理变量的优点

C18 直接用 `token_diff_ab`（连续变量）作为自变量，其正交性依赖于模型线性假设。C19 将"A 是否更长"二值化后：
- **概念更直观**：处理 = 呈现一个更长的回答给评分者；
- **因果框架更清晰**：可以套用 Rubin 潜在结果框架（$Y(1) - Y(0)$）；
- **倾向得分方法天然适用**：IPW 要求离散处理变量；
- **排除长度平局**：`token_diff_ab == 0` 的行被剔除，避免将无法判断长度方向的样本混入处理组。

### 2.2 稳定化 IPW 的优势

标准 IPW 权重 $1/P(T|X)$ 在倾向得分极端时方差爆炸。C19 使用**稳定化 IPW**：

$$w_i = \begin{cases} \frac{P(T=1)}{P(T=1|X_i)} & \text{if } T_i = 1 \\ \frac{P(T=0)}{P(T=0|X_i)} & \text{if } T_i = 0 \end{cases}$$

分子用边际处理率 $P(T=1)$ 归一化，有效减小极端权重。倾向得分裁剪至 $[0.01, 0.99]$ 进一步保护稳定性。等效样本量（ESS）报告权重集中度：ESS 越接近样本量，说明权重分布越均匀，估计越可靠。

### 2.3 两种方法互补的逻辑

| 方法 | 优势 | 局限 |
|------|------|------|
| 调整逻辑回归 | 推断直接、OR 解释直觉清晰 | 依赖线性加性假设、交互项未建模 |
| 稳定化 IPW | 不对结果建模、对函数形式假设更少 | 依赖倾向得分模型设定正确 |

两种方法对混淆做不同假设，若结论方向相同，则对"长度优势是真实处理效应"的论断更有底气。

---

## 三、实现逻辑

### 3.1 整体流程

```
全量 parquet → build_model_stats() → 计算模型级 ability/verbosity/format_tendency
        ↓
for 每个子集（全量 + 16 纯净子集）：
    add_pair_features()  ← 复用 C18 的特征衍生逻辑
    prepare_subset_for_robustness()
        ↓
        longer_a = (token_diff_ab > 0)  ← 二值化处理变量
        winner_a = (winner == model_a)   ← 二值化结果变量
        剔除 token_diff_ab == 0 的行
        ↓
    active_confounders()              ← 剔除常数列，返回可用混淆变量列表
    fit_logit_effect(["longer_a"])    ← 粗模型：只加 longer_a
    fit_logit_effect(["longer_a"] + confounders)  ← 调整模型
    compute_ipw_ate()                 ← 稳定化 IPW ATE
    bootstrap_ipw_ci(n_boot=30)      ← 30 次 Bootstrap 95% CI
        ↓
汇总 → plot_length_robust_forest() → generate_report()
        ↓
输出 R17 / T07 / P10
```

### 3.2 关键函数

#### `prepare_subset_for_robustness(df)`

这是 C19/C21 共享的数据预处理入口：

1. 调用 `add_pair_features()` 衍生全部模型级控制变量；
2. 构造 `longer_a`（A 是否更长）、`winner_a`（A 是否获胜）；
3. 过滤掉 `token_diff_ab == 0`（长度平局行）；
4. 转换数值类型；
5. 返回干净的子集 DataFrame。

此函数是 C21 的直接依赖（`from C19 import prepare_subset_for_robustness`），代码复用保证了两脚本的处理口径完全一致。

#### `active_confounders(df)`

```python
CONTINUOUS_CONFOUNDERS = [
    "user_tokens", "turns", "ability_diff", "verbosity_diff",
    "format_tendency_diff", "header_density_diff", "list_density_diff", "bold_density_diff",
]
```

调用 `stats_utils.active_nonconstant_columns()` 过滤常数列（某子集中可能所有值相同的控制变量）。这一动态过滤避免了逻辑回归因常数列报错而崩溃。

#### `fit_logit_effect(df, predictors)`

封装 `statsmodels.Logit` 拟合，提取 `longer_a` 对应的系数、SE、p 值，转换为 OR 及 95% CI（Wald 近似）和 McFadden 伪 $R^2$。使用 `try/except` + `warnings.filterwarnings` 抑制收敛警告，失败时返回 `None`。

#### `fit_propensity_scores(df, confounders)`

用 `sklearn.LogisticRegression`（LBFGS solver，max_iter=1000）对 `longer_a` 拟合倾向得分，使用 `StandardScaler` 标准化特征，裁剪到 $[0.01, 0.99]$。返回倾向得分数组和标准化后的特征矩阵（后者供 C21 的匹配使用）。

#### `compute_ipw_ate(df, confounders)`

用稳定化权重计算加权均值差 ATE，同时返回倾向得分范围和 ESS。

#### `bootstrap_ipw_ci(df, confounders, n_boot=30, seed=42)`

非参数 Bootstrap（有放回重采样），每次重新拟合倾向得分并重新计算 ATE，取 2.5/97.5 百分位构成 95% CI。n_boot=30 是计算效率与估计精度的平衡（完整分析用更多次数会更准确，但考虑到子集数量多、每次倾向得分拟合的计算代价，30 是合理的默认值）。

#### `plot_length_robust_forest(summary_df, picture_path)`

双面板森林图（竖向水平误差线图）：
- **左面板**：调整 OR（以 1.0 为参考线）+ 95% Wald CI；
- **右面板**：IPW ATE（以 0 为参考线）+ Bootstrap 95% CI；
- 全量子集用深色标注，Y 轴按调整 OR 从小到大排列，直观比较两种方法的一致性。

### 3.3 产出文件

| 文件 | 内容 |
|------|------|
| `Reports/R17_length_effect_robust_report.txt` | 逐子集粗模型/调整模型/IPW ATE 的完整数值 |
| `Tables/T07_length_robust_summary.csv` | 结构化宽表，供横向比较与 C21 引用 |
| `Pictures/P10_length_robust_forest.png` | 双面板森林图（调整 OR + IPW ATE） |

---

## 四、结论分析

### 4.1 全量结果：两种方法高度一致

| 指标 | 数值 |
|------|------|
| 有效样本量 | 78,783（剔除长度平局后） |
| 胜者更长比例 | **62.36%** |
| 粗模型 OR | 2.745 [2.667, 2.825] |
| **调整 OR** | **1.910** [1.842, 1.982] |
| **IPW ATE** | **+0.149** [0.135, 0.161] |

- 调整 OR > 1 且 CI 不跨 1：在逻辑回归框架下，控制 19 个混淆变量后，A 更长时 A 获胜的概率仍是 A 更短时的 **1.91 倍**。
- IPW ATE = 0.149：在倾向得分均衡后，"A 更长"这一处理使 A 的获胜概率提升约 **14.9 个百分点**，Bootstrap CI 不跨 0。
- C18 M3 层 OR（~1.93）与本脚本调整 OR（1.91）数值极为接近，说明二值化处理框架与连续变量框架给出了一致的结论。

### 4.2 跨子集一致性

| 子集 | 调整 OR | IPW ATE | 结论一致性 |
|------|---------|---------|-----------|
| 无类别 | 2.085 | +0.166 | ✓ 均显著 |
| 仅创意写作 | 1.994 | +0.176 | ✓ 均显著 |
| 仅代码 | 1.776 | +0.156 | ✓ 均显著 |
| 仅指令遵循 | 1.615 | +0.094 | ✓ 均显著 |
| **仅数学** | **1.340** | **+0.072** | ✓ 均显著（效应最小） |
| 指令+代码 | 2.235 | +0.208 | ✓ 均显著（效应最大） |
| 数学+代码 | 1.122 | +0.015 | ✗ 调整 OR 不显著（p=0.51），IPW CI 跨 0 |
| 指令+数学 | 1.066 | +0.097 | ✗ 调整 OR 不显著（p=0.73） |
| 创意+代码 | 1.347 | +0.073 | ✗ CI 跨 0（小样本 n=248） |

- **11/14 个有效子集**中调整 OR 显著且 IPW ATE CI 不跨 0。
- **数学相关交叉子集**（数学+代码、指令+数学）效应减弱，与 C16 中数学任务效应量偏小的结论一致。
- 两种方法的方向一致性极高，仅在显著性临界子集（小样本/数学组合）有分歧。

### 4.3 对 C18 的稳健性补充

C18 使用连续变量 + 嵌套 M0→M3 结构，C19 使用二值化处理 + IPW，两者的主要数值差异在于处理变量定义的粒度，但核心结论完全一致：

- 约 30-35% 的粗效应来自混淆（模型能力、任务类型等），约 65-70% 是真实的长度偏好；
- 这种偏好跨大多数任务类型稳健存在；
- 数学任务中偏好最弱，可能因为数学的"正确性"比"篇幅"更能影响人类判断。

---

## 五、设计细节与注意事项

1. **与 C18 共享特征衍生逻辑**：`build_model_stats` 和 `add_pair_features` 直接从 C18 导入（`from C18_pure_effect import ...`），确保两脚本的混淆变量定义完全一致。
2. **IPW 倾向得分裁剪**：裁剪到 `[0.01, 0.99]` 而非更小区间，保留极端倾向得分行（若裁剪到 0.05 会排除更多样本）。权衡：裁剪越宽，遗漏值估计偏差越小，但方差可能略大。
3. **Bootstrap n_boot=30**：轻量化设计，降低运行时间。对于大样本（n > 5000）子集，30 次足以稳定 2.5/97.5 百分位；对于小样本子集，置信区间本身也不可靠（体现在 CI 很宽）。
4. **`active_confounders()` 动态选列**：某些小样本子集的 7 个 criteria 布尔列可能全为 0 或全为 1，动态过滤防止 Logit 奇异矩阵报错。
5. **C21 的依赖**：`fit_propensity_scores` 和 `prepare_subset_for_robustness` 是 C21 的外部依赖，若修改这两个函数的签名，须同步更新 C21。
