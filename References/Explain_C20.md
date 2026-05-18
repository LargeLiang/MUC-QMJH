# C20_format_effect_robust 代码详解

> 来源文件：`Codes/C20_format_effect_robust.py`  
> 产出文件：`Reports/R18_format_effect_robust_report.txt`、`Tables/T08_format_robust_summary.csv`、`Pictures/P11_format_robust_forest.png`

---

## 一、研究问题与分析目标

C19 对长度效应做了稳健性验证，C20 是其格式效应的对应分析。核心问题是：

> "在控制长度差和其他格式特征后，各格式元素（标题/粗体/列表）对人类偏好是否存在独立的稳健处理效应？"

与 C19 平行，C20 同样使用"二值化处理变量 + 调整逻辑回归 + IPW"的三步框架，但有几个针对格式分析的特殊设计：
- **标题和粗体**为主分析（有正向先验）；
- **列表**仅作敏感性分析（C17 发现其方向存疑，C18 发现存在抑制效应）；
- 每次只分析一种格式特征时，**token_diff_ab 始终固定作为控制**（消除"格式更多的回答同时也更长"这一主要混淆），另外两种格式密度差同样纳入控制。

---

## 二、方法选择

### 2.1 与 C19 的异同

| 维度 | C19（长度稳健性） | C20（格式稳健性） |
|------|-----------------|-----------------|
| 处理变量 | `longer_a = (token_diff_ab > 0)` | `treatment_a = (feature_col > 0)` |
| 剔除条件 | `token_diff_ab == 0`（长度平局） | `feature_col == 0`（两侧格式密度相同） |
| 强制控制 | 无 | `token_diff_ab` 始终在 confounders 中 |
| 其他格式控制 | 三类格式密度差均纳入 | 另外两类格式密度差纳入（排除目标特征） |
| 特征轮次 | 单次（长度是唯一处理） | 三轮循环（header / bold / list） |

### 2.2 强制控制 token_diff_ab 的必要性

C16/C17 已证明胜者更长（r_rb ≈ 0.34）且更有格式（header r_rb ≈ 0.19），两者正相关。若在格式处理效应分析中不控制长度，则"高格式密度"的处理效应会部分反映长度优势的混淆贡献，无法剥离出纯格式效应。因此 `token_diff_ab` 是**强制纳入**的优先混淆变量，即使 `active_confounders()` 未从数据中识别它，代码也会手动保证其在控制列表中。

### 2.3 列表的特殊地位

`FORMAT_FEATURES` 配置中将列表标记为 `role: "敏感性分析"`：
```python
FORMAT_FEATURES = [
    {"column": "header_density_diff", "label": "标题密度", "role": "主分析"},
    {"column": "bold_density_diff",   "label": "粗体密度", "role": "主分析"},
    {"column": "list_density_diff",   "label": "列表密度", "role": "敏感性分析"},
]
```

列表被降格的原因：C17 中全量列表 Wilcoxon $r_{rb} < 0$，提示潜在的辛普森悖论；C18 净效应分析显示控制混淆后列表方向发生反转。因此 C20 对列表的稳健性结果不写入主结论，仅作敏感性参考。

---

## 三、实现逻辑

### 3.1 整体流程

```
全量 parquet → build_model_stats() → 模型级特征
        ↓
for 每个子集（全量 + 16 纯净子集）：
    add_pair_features()           ← 衍生控制变量（复用 C18）
    for feature_cfg ∈ FORMAT_FEATURES：  ← 3 轮格式特征循环
        prepare_subset_for_feature(df, feature_col)
            ↓
            treatment_a = (feature_col > 0)  ← 二值化
            winner_a = (winner == model_a)
            剔除 feature_col == 0 的行（密度平局）
            ↓
        active_confounders()           ← 动态过滤常数列（含强制 token_diff_ab）
        fit_logit_effect("treatment_a", [...])  ← 粗模型 / 调整模型
        compute_ipw_ate("treatment_a", confounders)
        bootstrap_ipw_ci(n_boot=30)
            ↓
汇总 → plot_format_robust_forest() → generate_report()
        ↓
输出 R18 / T08 / P11
```

### 3.2 关键函数

#### `prepare_subset_for_feature(df, feature_col)`

类似 C19 的 `prepare_subset_for_robustness()`，但处理变量改为目标格式列：
1. 调用 `add_pair_features()` 衍生模型级混淆；
2. 构造 `treatment_a = (feature_col > 0)`（A 侧格式密度差更高）；
3. 构造 `treatment_wins = 1 if (treatment_a == winner_a) else 0`（处理方向是否与获胜方一致）；
4. 剔除 `feature_col == 0`（密度差为零）的行。

#### `active_confounders(df, feature_col)`

```python
BASE_CONTINUOUS_CONFOUNDERS = [
    "token_diff_ab",  # 强制首位（长度控制）
    "header_density_diff", "list_density_diff", "bold_density_diff",
    "user_tokens", "turns", "ability_diff", "verbosity_diff", "format_tendency_diff",
]
# 从 continuous 列表中排除当前目标格式特征，避免自我控制
continuous = [col for col in BASE_CONTINUOUS_CONFOUNDERS if col != feature_col]
candidates = continuous + TASK_TYPE_COLS + CRITERIA_COLS
return active_nonconstant_columns(df, candidates)
```

确保 `token_diff_ab` 始终在候选列中，同时排除目标格式列自身（避免"用 header 控制 header"的逻辑错误），以及动态过滤常数列。

#### `fit_logit_effect(df, treatment_col, predictors)`

签名与 C19 略不同（多了 `treatment_col` 参数），因为 C20 的处理变量名称是动态的（"treatment_a"），而 C19 固定为 "longer_a"。其余逻辑相同。

#### `analyze_feature_subset(feature_cfg, subset_name, df, bootstrap_n, seed)`

每个 (特征, 子集) 组合的完整分析函数，输出报告文本块和汇总字典行。

#### `plot_format_robust_forest(summary_df, picture_path)`

双面板森林图，但 Y 轴按 **(子集, 特征)** 的组合排列（每个子集有 3 行）。颜色按特征区分（header/bold/list 各一种颜色），辅助读者区分三条分析线。

### 3.3 产出文件

| 文件 | 内容 |
|------|------|
| `Reports/R18_format_effect_robust_report.txt` | 逐子集 × 逐格式特征的粗/调整/IPW 结果 |
| `Tables/T08_format_robust_summary.csv` | 结构化宽表（含 feature 列区分格式类型） |
| `Pictures/P11_format_robust_forest.png` | 按特征分色的双面板森林图 |

---

## 四、结论分析

### 4.1 标题密度：全量稳健，但跨子集衰减

| 子集 | 粗 OR | 调整 OR | IPW ATE | 显著性 |
|------|-------|---------|---------|--------|
| 全量 | 1.531 | **1.132** [1.083, 1.182] | **+0.028** [0.022, 0.036] | ✓ |
| 无类别 | 1.869 | 1.162 [1.087, 1.243] | +0.035 [0.024, 0.054] | ✓ |
| 仅创意写作 | 1.572 | 1.090 | +0.018 [−0.041, 0.084] | ✗ 不显著 |
| 仅数学 | 1.285 | **0.951** | −0.017 [−0.070, 0.026] | ✗ OR < 1 |
| 仅代码 | 1.407 | 1.078 | +0.010 [−0.011, 0.025] | ✗ IPW CI 跨 0 |
| 指令+代码 | 2.672 | 2.235 | +0.208 | ✓ 最强子集 |

关键发现：
- **全量调整 OR = 1.13**，效应小但在近五万样本上显著；
- 数学任务中调整 OR < 1（方向逆转），标题在数学回答中可能是"罗列步骤"的信号而非"结构清晰"；
- 跨子集的标题效应相比长度效应更不稳定，部分任务类型的净效应不显著。

### 4.2 粗体密度：与标题类似但更稳定

粗体的调整 OR 在全量为约 1.10–1.15，跨子集的显著率高于标题（IPW CI 更多不跨 0）。数学任务同样存在方向性衰减。

### 4.3 列表密度（敏感性）：全量 OR > 1，与 C17 形成对比

C20 对列表密度的稳健性分析给出了一个有意思的转变：
- C17（粗 Wilcoxon）：列表 $r_{rb} < 0$（负向，胜者列表密度反而更低）；
- C18 M3 净效应 OR > 1（控制后方向反转）；
- **C20 全量调整 OR ≈ 1.07，IPW ATE 轻微正向但 CI 可能跨 0**（取决于子集）。

这一系列变化揭示了列表密度效应方向依赖于混淆控制程度——粗估计为负，深度控制后为弱正，印证了辛普森悖论的解释（强模型既能赢又少用列表，引入了负向混淆）。

### 4.4 格式稳健性 vs 长度稳健性的对比

相比 C19（长度，调整 OR 全量 1.91），C20 的格式效应（调整 OR ≈ 1.13）要小得多。这说明：
- **长度偏差**是人类评分中的主要格式偏好；
- **格式偏差**（标题/粗体）是次要但独立的偏好信号，在全量数据和部分子集中显著；
- 两类偏差加总后都是非功能性的表面信号（不直接代表答案质量），有助于理解 RLHF 数据的系统性偏差来源。

---

## 五、设计细节与注意事项

1. **三轮循环 vs 三次独立调用**：C20 将三种格式特征的分析封装在同一个 `analyze_feature_subset()` 函数中，通过 `feature_cfg` 字典参数化，减少代码重复，同时保证三种特征使用完全相同的分析流程。
2. **格式特征"自我回避"**：`active_confounders()` 从候选混淆列表中排除当前目标格式列，防止 `header_density_diff` 同时作为处理变量和控制变量（会导致系数估计崩溃）。
3. **另外两种格式密度的对称控制**：例如分析标题时，同时控制列表和粗体密度差，排除"这个 A 的标题更多只因为整体格式更丰富"的可能。
4. **IPW 倾向得分用 sklearn**（非 statsmodels）：sklearn 的 `LogisticRegression` 带 L2 正则化，比 statsmodels Logit 更稳定，不容易因小样本或共线性导致不收敛。代价是 OR 等解释不如 statsmodels 直接，但倾向得分估计本身更可靠。
5. **子集标签映射 SUBSET_LABELS_EN**：图表 Y 轴的子集名从中文映射到英文缩写（如"仅代码" → "Code-Only"），便于论文的英文图表使用。
