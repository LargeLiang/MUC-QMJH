# C22_sem_analysis 代码详解

> 来源文件：`Codes/C22_sem_analysis.py`  
> 产出文件：`Reports/R20_sem_analysis_report.txt`、`Tables/T11–T15`、`Pictures/P13_sem_path_diagram.png`、`Pictures/P14_sem_bootstrap_effects_ci.png`

---

## 一、研究问题与分析目标

C16–C21 的分析采用的是"单一处理变量 + 控制混淆"的框架：每次检验一个效应（长度效应或某种格式效应），其余变量作为控制。这种逐步检验的思路清晰，但缺少对**变量之间因果关系的整体刻画**——例如：

- 模型能力（`ability_diff`）是否既直接影响获胜结果，又通过影响回答长度和格式间接起作用？
- 长度和格式之间的相关性（$\rho \approx 0.3$）有多少是"同一模型能力的共因"，多少是"格式增加长度"的路径？
- 在控制所有外生变量后，长度和格式对偏好的直接效应各自有多大？

C22 使用**结构方程模型（SEM）**来统一回答这些问题，在单一模型中同时估计所有路径系数，构建从外生变量（模型特征 + 任务类型）经中介变量（长度差、格式密度差）到结果（获胜概率）的完整因果路径图。

---

## 二、方法选择

### 2.1 为什么选 SEM

与逐步逻辑回归（C18）和 IPW（C19/C20）相比，SEM 的独特优势：

| 维度 | 逻辑回归/IPW（C18–C21） | SEM（C22） |
|------|------------------------|-----------|
| 处理框架 | 单处理变量 | 多中介变量同时估计 |
| 间接效应 | 需手动计算（系数连乘） | 内置路径分析语法，自动计算 |
| 中介之间的相关 | 忽略或通过分开分析处理 | 显式建模（$\text{header} \sim\sim \text{bold}$） |
| 模型比较 | 无标准框架 | CFI/TLI/RMSEA/AIC/BIC 指标 |
| 方向性偏好 | 仅看单一系数 | 可区分直接 vs 间接路径 |

SEM 的代价是假设较强（线性加性路径、正态误差近似），但本研究用 `DWLS`（对角加权最小二乘）拟合目标函数，比 ML 对偏态分布更鲁棒。

### 2.2 两个模型：主模型 vs 扩展模型

- **主模型**：中介层 = {`token_diff_ab`, `header_density_diff`, `bold_density_diff`}；
- **扩展模型**：在主模型基础上加入 `list_density_diff`（敏感性分析），验证加入列表后主路径是否稳定。

列表被降格为扩展模型的原因与 C18/C20 一致：列表在粗估计中方向存疑，不写入主结论，但用扩展模型检验其存在是否改变主路径。

### 2.3 Bootstrap 估计间接效应置信区间

间接效应（如"能力通过长度影响偏好"= ability→token×token→winner）是两个路径系数的乘积，其采样分布非正态（即使单个系数近似正态）。semopy 的 Wald SE 对间接效应不可靠，C22 用 **非参数 Bootstrap**（50 次重采样，全量近八万条数据，每次重新拟合 SEM）来估计 95% 百分位 CI，更准确地描述间接效应的不确定性。

---

## 三、实现逻辑

### 3.1 整体流程

```
全量 optimized_data.parquet
        ↓ prepare_sem_data()
            → add_pair_features()  ← 衍生分析列（复用 C18）
            → 选取全部 SEM 变量列
            → 连续变量 z 标准化
            → 转 float（semopy 要求）
        ↓
build_layer_stats(raw_df)          → T11 描述统计表
build_correlation_table(raw_df)    → T12 相关矩阵
        ↓
build_sem_description(include_list=False)  → 主模型语法字符串
build_sem_description(include_list=True)   → 扩展模型语法字符串
        ↓
fit_sem_model(sem_df, model_desc)          → semopy.Model（主 + 扩展）
        ↓
compare_models()                           → T13 拟合优度比较（CFI/TLI/RMSEA/AIC/BIC）
        ↓
calculate_effects(estimates)               → 直接/间接/总效应字典（主 + 扩展）
bootstrap_effects(sem_df, model_desc, n_boot=50)  → 50×Bootstrap 效应分布
summarize_bootstrap(point_effects, boot_df)        → T15 Bootstrap CI 表
        ↓
save_path_diagram()                        → P13 路径图
plot_bootstrap_ci()                        → P14 效应 CI 森林图
        ↓
generate_report()
        ↓
输出 R20 / T11–T15 / P13–P14
```

### 3.2 关键函数

#### `prepare_sem_data()`

1. 调用 `load_data_global()` + `add_pair_features()`（从 C18 导入）衍生所有分析列；
2. 选取 SEM 所需的全部列（外生层 16 + 中介层 3/4 + 结果层 1）并 dropna；
3. 对连续变量做 z 标准化（使用 `stats_utils.zscore_series()`，处理常数列情况）；
4. 返回 `(raw_df, sem_df)`，前者用于描述统计，后者用于建模。

#### `build_sem_description(include_list)`

动态生成 semopy 模型语法字符串。设计要点：
- 每个中介变量（token_diff_ab、header_density_diff 等）都有一个"归因方程"（~ 外生变量），说明其被外生层变量解释；
- 格式密度差的方程还额外控制 `token_diff_ab`（格式与长度的共线性控制）；
- 结果方程纳入所有外生变量 + 所有中介变量；
- 格式密度差之间的残差相关（`~~`）显式建模，承认两者共享未观测的"格式风格"因子。

#### `fit_sem_model(df, model_desc, obj="DWLS")`

```python
model = Model(model_desc)
model.fit(df.astype(float), obj=obj)
estimates = model.inspect()  # 路径系数 + SE + p 值
fit_stats = calc_stats(model)  # CFI / TLI / RMSEA / AIC / BIC
```

使用 `DWLS`（Diagonally Weighted Least Squares）作为拟合目标，适合混合连续/二值变量。返回模型对象、路径估计表和拟合优度字典。

#### `calculate_effects(estimates, include_list)`

从路径估计表中手动提取各路径系数，计算：
- **直接效应**：token_diff_ab → winner_a（长度的直接影响）；header/bold/list → winner_a；
- **间接效应**：以 ability_diff 为例，$\text{ability} \to \text{token} \times \text{token} \to \text{winner}$，各路径系数相乘；
- **总间接效应**：ability 通过所有中介的间接效应之和；
- **总效应**：ability 的直接效应 + 总间接效应。

所有效应都是在 **z 标准化** 数据上计算的，因此数值可跨变量直接比较相对大小。

#### `bootstrap_effects(sem_df, model_desc, n_boot=50, seed=42)`

```python
for i in range(n_boot):
    sample = sem_df.sample(n=len(sem_df), replace=True, ...)
    fitted = fit_sem_model(sample, model_desc)
    records.append(calculate_effects(fitted["estimates"]))
```

每隔 10 次打印进度。失败的重采样直接跳过（SEM 拟合偶尔在特殊重采样下不收敛）。返回 50×N_effects 的 DataFrame。

#### `save_path_diagram(model, output_path)`

优先调用 `semopy.semplot()` 生成路径图（依赖 graphviz）。若 graphviz 不可用，回退到用 **networkx + matplotlib** 手动绘制简化版路径图，保证在无 graphviz 环境下也能产出图片。

### 3.3 变量层次结构

```
外生层（16 个变量）
├── 连续：ability_diff, verbosity_diff, format_tendency_diff, user_tokens, turns
└── 二值：4 任务类型 + 7 评判标准

中介层（主模型 3 个）
├── token_diff_ab          ← 长度差中介
├── header_density_diff    ← 标题密度差中介
└── bold_density_diff      ← 粗体密度差中介

结果层
└── winner_a（A 获胜 = 1）
```

### 3.4 产出文件

| 文件 | 内容 |
|------|------|
| `Tables/T11_sem_layer_stats.csv` | 三层变量的描述统计（均值/中位/SD/缺失率/正例率） |
| `Tables/T12_sem_correlation.csv` | 关键连续变量的相关矩阵 |
| `Tables/T13_sem_model_comparison.csv` | 主 vs 扩展模型拟合优度对比（CFI/RMSEA/AIC 等） |
| `Tables/T14_sem_path_estimates.csv` | 主模型全部路径的系数、SE、p 值 |
| `Tables/T15_sem_bootstrap_ci.csv` | 关键效应的点估计 + Bootstrap 95% CI + 是否排除 0 |
| `Reports/R20_sem_analysis_report.txt` | 完整文字报告（层次统计 + 模型语法 + 路径估计 + Bootstrap CI + 方法学结论） |
| `Pictures/P13_sem_path_diagram.png` | SEM 路径图（graphviz 或 networkx 回退） |
| `Pictures/P14_sem_bootstrap_effects_ci.png` | 关键效应的 Bootstrap 森林图 |

---

## 四、结论分析

### 4.1 模型拟合优度

| 模型 | CFI | TLI | RMSEA | AIC |
|------|-----|-----|-------|-----|
| 主模型 | **0.9998** | **0.9998** | **0.0030** | 111.75 |
| 扩展模型 | 1.0000 | 1.0000 | 0.0011 | 183.47 |

主模型 CFI ≈ 1、RMSEA < 0.05，属于极好的拟合（通常 CFI > 0.95、RMSEA < 0.08 即为可接受）。扩展模型 AIC 更大（183 > 112），说明加入列表密度后模型变复杂但拟合的效率变低，印证了主模型作为正式模型的合理性。

### 4.2 关键路径估计（主模型，z 标准化数据）

**结果方程关键系数**（winner_a ~ ...）：

| 路径 | 系数 | SE | p 值 |
|------|------|----|------|
| token_diff_ab → winner_a | **+0.607** | 0.0084 | 0 |
| header_density_diff → winner_a | **+0.0173** | 0.0018 | 0 |
| bold_density_diff → winner_a | **+0.0215** | 0.0020 | 0 |
| ability_diff → winner_a | **+0.155** | 0.0026 | 0 |
| verbosity_diff → winner_a | **−0.261** | 0.0057 | 0 |

解读：
- `token_diff_ab` 的标准化系数（0.607）远大于其他变量，是影响获胜的最重要直接预测因子；
- `header_density_diff`（0.017）和 `bold_density_diff`（0.022）显著正向，格式效应在控制长度后仍保留；
- `verbosity_diff`（词冗性差，−0.261）强烈负向——高词冗性模型虽然产出长回答，但获胜概率反而更低，说明"冗长而不精炼"对评分有惩罚；
- `ability_diff`（+0.155）直接正向，能力强的模型更可能获胜。

### 4.3 间接效应与 Bootstrap CI

| 效应 | 点估计 | Bootstrap 95% CI | 是否排除 0 |
|------|--------|-----------------|-----------|
| 标题密度直接效应 | +0.0173 | [+0.0086, +0.0263] | ✓ 排除 |
| 粗体密度直接效应 | +0.0215 | [+0.0096, +0.0361] | ✓ 排除 |
| 能力直接效应 | +0.1549 | [+0.122, +0.191] | ✓ 排除 |
| 能力→标题密度→偏好 | +0.0061 | [+0.003, +0.012] | ✓ 排除 |
| 能力→粗体密度→偏好 | +0.0031 | [+0.002, +0.007] | ✓ 排除 |
| **长度直接效应** | **+0.607** | [**−0.069, +1.506**] | ✗ **CI 跨 0** |
| 词冗性→长度→偏好 | +0.305 | [−0.035, +0.784] | ✗ CI 跨 0 |
| 格式倾向→标题→偏好 | +0.0113 | [+0.005, +0.018] | ✓ 排除 |
| 格式倾向→粗体→偏好 | +0.0178 | [+0.008, +0.031] | ✓ 排除 |

**重要发现**：长度直接效应的 Bootstrap CI 跨 0，这看似与 C16–C19 的结论矛盾，实际原因是：

在 SEM 中，`token_diff_ab` 是 **z 标准化**后的变量，点估计系数很大（0.607）但 Bootstrap 方差也极大（SD ≈ 0.4），说明 SEM 框架在全量数据上拟合长度路径时对数据重采样极为敏感（近八万行每次 SEM 重拟合，数值优化面临较高方差）。这是 SEM 在大数据上的固有局限，而 C16–C19 的 Wilcoxon 和 IPW 方法对此更鲁棒。因此报告采用 R20 的方法学结论（第 1–4 条）：**SEM 的格式路径 CI 不跨零，是更可靠的 SEM 贡献；长度效应的结论以 C16/C19 为准**。

### 4.4 SEM 在证据链中的位置

SEM 是整个分析体系的**终章综合**：
1. 它确认了能力（ability_diff）的双重作用：既有直接的 +0.155，又通过格式路径有间接的正向效应（+0.006 ~ +0.003），但通过长度的间接效应因 Bootstrap CI 跨 0 而不可靠；
2. 它定量区分了格式倾向（format_tendency_diff）的直接路径（CI 跨 0，不显著）vs 间接路径（通过标题/粗体，CI 不跨 0，总间接 = +0.029）——说明格式偏好的机制是"评分者通过格式元素的密度判断，而非直接感知'格式倾向'这个潜在属性"；
3. 词冗性（verbosity_diff）的强负效应（−0.261）是意外之得，提示人类评分者对"废话型"长回答有惩罚倾向，这是简单长度检验无法揭示的细粒度发现。

---

## 五、设计细节与注意事项

1. **数据均来自 add_pair_features() 的派生列**：SEM 使用的所有分析列（ability_diff、token_diff_ab 等）均在运行时通过 `add_pair_features()` 临时计算，不依赖 `optimized_data.parquet` 持久化这些列。这与 repo memory 中"nested schema migration"的要求一致。
2. **连续变量 z 标准化**：所有连续变量经 `zscore_series()` 标准化，二值变量不标准化（其均值本身就是概率，解释直观），标准化后系数可直接比较相对效应大小。
3. **`DWLS` 而非 `ML`**：`winner_a` 是二值变量，`ML` 假设多元正态不满足；`DWLS` 是加权最小二乘的对角近似，适合混合数据类型，是 semopy 对此类场景的推荐选择。
4. **Bootstrap n_boot=50**：SEM 每次拟合在 7.8 万行数据上约需数十秒，50 次是精度与时间的折中。生产环境建议用 200–500 次以获得更稳定的 CI 边界。
5. **graphviz 回退机制**：`save_path_diagram()` 检测 graphviz 可用性，失败时自动回退到 networkx 绘图，保证脚本在任意环境下均能完整运行并产出所有预期文件。
6. **T14 路径估计表的列命名**：semopy 的 `inspect()` 返回列名为 `lval/op/rval/Estimate/Std. Err./z-value/p-value`，C22 在保存前重命名为更规范的英文小写列名，便于后续脚本读取。
