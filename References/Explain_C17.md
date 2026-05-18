# C17_format_test 代码详解

> 来源文件：`Codes/C17_format_test.py`  
> 产出文件：`Reports/R14_format_test_report.txt`、`Tables/T04_format_test_summary.csv`、`Pictures/P07_format_effect_heatmaps.png`

---

## 一、研究问题与分析目标

C17 对格式偏好进行系统性的统计检验。C15 已通过可视化描述了标题、列表、粗体三种格式特征的分布趋势，C17 的任务是：

1. 是否存在"格式化更丰富的回答更受偏好"的统计显著信号？
2. 对于三种格式特征（header / list / bold），偏好效应是否一致？方向是否相同？
3. 格式偏好在不同任务类型子集中是否稳定？

---

## 二、方法选择

### 2.1 为什么同样选 Wilcoxon

格式特征的偏好分析与 C16 的长度分析面对同样的数据结构：每行仍然是配对对决，差值仍然非正态（计数数据往往高度离散，列表数 = 0 的行占多数），因此 **Wilcoxon 符号秩检验** 是最自然的选择。

### 2.2 三套并行检验机制

C17 为每个格式特征（feature ∈ {header, list, bold}）设计了三套相互补充的检验：

| 检验 | 核心变量 | 检验内容 |
|------|----------|----------|
| **Wilcoxon（计数差）** | $\Delta_{\text{count}} = f_{\text{winner}} - f_{\text{loser}}$ | 胜者的格式出现次数是否系统性更多 |
| **Wilcoxon（密度差）** | $\Delta_{\text{density}} = \frac{f}{\text{tokens}+1}$ 的差值 | 控制回答长度后，格式密度是否仍偏向胜者 |
| **卡方检验（出现/不出现）** | 2×2 列联表：{胜者含 feature} × {输者含 feature} | 胜者比输者更"倾向于包含"格式元素的概率是否显著 |

密度检验是对计数检验的重要补充：如果"胜者更长"（C16 已证明），那么光靠计数增加来赢得格式偏好是不充分的，必须验证在每单位 token 上的格式密度也更高。

### 2.3 Bonferroni 校正

每个子集内对 3 个特征做检验，BONFERRONI_K = 3（仅子集内校正），各子集之间的多重性在 C16 中已处理。校正阈值 $\alpha / 3 \approx 0.017$，使三个特征的联合 FWER ≤ 5%。

---

## 三、实现逻辑

### 3.1 整体流程

```
全量 + C13 子集 parquet
        ↓ with_flat_analysis_columns()  ← 展平 a/b 的 header/list/bold 计数与 token 数
        ↓
for 每个子集：
    for feature ∈ {header, list, bold}：
        _build_paired(df, feature)
            → count_diff 数组（胜者方向对齐的计数差）
            → density_diff 数组（胜者方向对齐的密度差）
        _wilcoxon_one(count_diff)      → W, p, r_rb
        _wilcoxon_one(density_diff)    → W, p, r_rb  ← 关键辅助检验
        _chisquare_presence(df, feat)  → p（2×2 卡方）
        Bonferroni 校正（k=3）
        ↓
汇总 → plot_format_heatmaps() → generate_report()
        ↓
输出 R14 / T04 / P07
```

### 3.2 关键函数

#### `_build_paired(df, feature)`

```python
# 计算方向对齐后的格式计数差与密度差
count_diff = winner_count - loser_count  # 使用 oriented_winner_difference 向量化
density_diff = (winner_count / (winner_tokens + 1)) - (loser_count / (loser_tokens + 1))
```

`+1` 平滑分母，避免 token 数为 0 时的除以零错误（极少数情况）。密度 = 每 token 的格式出现次数，量纲统一，可跨长度不同的回答进行比较。

#### `_wilcoxon_one(arr)`

复用 C16 的逻辑，但输入是格式差值而非 token 差值。返回 $(W, p, r_{rb})$ 三元组。注意格式差值有大量零值（很多回答双方都没有标题/粗体），零值处理同样使用 `zero_method="zsplit"`。

#### `_chisquare_presence(df, feature)`

构建 2×2 列联表：
- 行：胜者是否含格式 feature（count > 0）
- 列：输者是否含格式 feature

用 `scipy.stats.chi2_contingency` 检验四格表的独立性。这是一个无方向的关联性检验，补充了 Wilcoxon 单侧检验的视角。

#### `run_one_subset(label, df)`

对单个子集运行全部三个特征的三套检验，收集每个特征的完整统计摘要，返回带 `subset` 字段的行列表（用于拼接 summary DataFrame）。

#### `plot_format_heatmaps(summary_df, path)`

绘制**双热力图**：
- **左图**：$r_{rb}$（密度检验的效应量），正值表示"格式化更多的胜"，颜色由蓝（负）到红（正）；
- **右图**：$-\log_{10}(p_{\text{density}})$，越深表示密度检验越显著。
- 横轴：feature（header / list / bold），纵轴：子集。

这种布局可以同时看到"效应方向"和"显著性强度"，便于快速识别跨子集的一致性模式。

### 3.3 产出文件

| 文件 | 内容 |
|------|------|
| `Reports/R14_format_test_report.txt` | 逐子集 × 逐特征的三套检验结果（计数 Wilcoxon、密度 Wilcoxon、卡方）+ 汇总 |
| `Tables/T04_format_test_summary.csv` | 宽格式汇总表，每子集一行，每特征的三套检验各一列组 |
| `Pictures/P07_format_effect_heatmaps.png` | 双热力图（r_rb 与显著性） |

---

## 四、结论分析

### 4.1 总体显著率：31/39

在 13 个有效子集 × 3 个特征 = 39 次密度 Wilcoxon 检验中，**31 次在 Bonferroni 校正后显著**（$p_{\text{adj}} < 0.017$）。三种格式特征的通过情况：

| 特征 | 全量 $r_{rb}$ | 全量密度 p | 跨子集显著次数 |
|------|--------------|------------|----------------|
| **标题密度** | 0.189 | < 0.001 | 10/13 |
| **粗体密度** | 0.195 | < 0.001 | 10/13 |
| **列表密度** | **-0.032** | < 0.001 | 11/13 |

### 4.2 列表密度的"反向"现象

列表密度在全量数据的密度 Wilcoxon 中达到了显著性（p 很低），但 **$r_{rb} < 0$**，即"胜者的列表密度反而更低"。这是一个初看令人困惑的结果。

可能的解释：
- **辛普森悖论**：在未控制任务类型的全量数据中，代码类任务占比很大（约 27%）。代码回答少用列表但更专业，代码任务对应的强模型往往格式更整洁，而非堆砌列表；混入全量后，"擅长代码的模型少用列表且胜率高"产生了负向的边际相关。
- C18 的净效应嵌套逻辑回归印证了这一点：控制模型能力与任务类型后，列表密度的方向会发生反转。

这说明 C17 的"粗检验"结果在没有控制混淆时可能具有误导性，C18 解决了这个问题。

### 4.3 标题与粗体：稳定的正向效应

标题和粗体密度的 $r_{rb}$ 均为正、约 0.19，跨 10/13 子集显著，效应等级属于"小效应"。在全量中：
- 标题密度计数 Wilcoxon：$r_{rb} = 0.189$，卡方 p < 0.001
- 粗体密度计数 Wilcoxon：$r_{rb} = 0.195$，卡方 p < 0.001

不显著的子集集中在样本量较小（< 500）的多类别交叉组，这属于检验力不足，而非效应消失。

### 4.4 密度检验 vs 计数检验

所有三个特征的密度 Wilcoxon 结果与计数 Wilcoxon 结果高度一致，说明格式偏好不是仅由"长回答出现更多格式"驱动——即便标准化到 token 数量，胜者仍然在每单位长度上使用更多标题和粗体。

### 4.5 C17 在证据链中的位置

C17 提供"**格式偏好现象存在**"的初步证据，但全量数据的列表密度反向结果提示：未控制混淆的粗检验存在遮蔽效应。C18 的嵌套逻辑回归才能给出净效应。

---

## 五、设计细节与注意事项

1. **BONFERRONI_K = 3**：仅在子集内对三个特征做校正，子集间不做额外校正（与 C16 统一框架，避免双重校正混乱）。
2. **density = count / (tokens + 1)**：+1 平滑确保计算安全；密度变量量纲一致，可直接在 Wilcoxon 中与不同长度的回答进行比较。
3. **卡方检验与 Wilcoxon 并用**：两种检验考察不同层次的效应——卡方只看"有无"（二值化），Wilcoxon 看"多少"（连续计数差）。两者一致时结论更有说服力。
4. **with_flat_analysis_columns()**：格式计数字段（`a_header_counts` 等）存在于 `optimized_data.parquet` 的顶层，accessor 函数负责选择正确列并做基础类型转换，脚本自身不做反序列化逻辑。
5. **热力图颜色中心**：`vmin / vmax` 对称设计，零点对应白色，使方向性（正/负）可以通过颜色直觉判断。
