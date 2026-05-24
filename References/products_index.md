# 产物清单 Products Index

本文件列出所有 Codes/ 脚本产生的分析产物（表格、图片、报告），按脚本运行顺序编排。

---

## 概览

| 类型 | 编号范围 | 说明 |
|------|----------|------|
| 报告 (R) | R01–R21 | 文字分析报告，存于 `Reports/` |
| 表格 (T) | T01–T15 | 统计数据表，存于 `Tables/` |
| 图片 (P) | P01–P14 | 可视化图表，存于 `Pictures/` |

> P01–P03 为手工制作的数据结构思维导图（XMind 格式），不由代码产生。

---

## 详细清单

### Layer 1 — 数据摄入（C01–C02）

| 脚本 | 类型 | 文件名 | 说明 |
|------|------|--------|------|
| C01 | — | — | 校验原始分片，无文件产物 |
| C02 | — | — | 合并 7 个 parquet 分片为 `Data/integrated_data/integrated_data.parquet` |

---

### Layer 2 — 探索分析（C03–C11）

| 脚本 | 类型 | 文件名 | 说明 |
|------|------|--------|------|
| C03 | — | — | 验证 order 一致性，无独立报告文件 |
| C04 | R01 | `R01_session_report.txt` | Session 分布分析报告 |
| C05 | R02 | `R02_order_report.txt` | Order 层次分析报告 |
| C06 | R03 | `R03_turn_report.txt` | Turn 层次分析报告 |
| C07 | R04 | `R04_model_report.txt` | 模型统计分析报告 |
| C08 | R05 | `R05_role_report.txt` | 角色字段分析报告 |
| C09 | R06 | `R06_cont_report.txt` | 内容字段分析报告 |
| C10 | R07 | `R07_token_report.txt` | Token 分布分析报告 |
| C11 | R08 | `R08_category_tag_report.txt` | category_tag 字段分析报告 |

---

### Layer 3 — 数据清洗（C12–C13）

| 脚本 | 类型 | 文件名 | 说明 |
|------|------|--------|------|
| C12 | R09 | `R09_optimization_report.txt` | 数据优化过滤报告 |
| C13 | R10 | `R10_division_report.txt` | 20 个任务类型子集划分报告 |

---

### Layer 4 — 分析（C14–C23）

#### 可视化偏好（C14–C15，长度↔格式对应）

| 脚本 | 类型 | 文件名模板 | 说明 |
|------|------|-----------|------|
| C14 | T01 | `T01_{idx:02d}_{slug}_length_diff_analysis_stats.csv` | 各子集长度差分析表（每子集一文件） |
| C14 | P04 | `P04_{idx:02d}_{slug}_length_diff_line_chart.png` | 各子集长度差折线图（每子集一文件） |
| C14 | R11 | `R11_length_preference_report.txt` | 长度偏好可视化汇总报告 |
| C15 | T02 | `T02_01_basic_statistics.csv` | 格式基础统计 |
| C15 | T02 | `T02_02_format_presence_analysis.csv` | 格式出现率分析 |
| C15 | T02 | `T02_03_header_count_analysis.csv` | 标题数量分析 |
| C15 | T02 | `T02_04_list_count_analysis.csv` | 列表数量分析 |
| C15 | T02 | `T02_05_bold_count_analysis.csv` | 粗体数量分析 |
| C15 | T02 | `T02_06_format_combination_analysis.csv` | 格式组合分析 |
| C15 | P05 | `P05_01_format_presence_bar_chart.png` | 格式出现率柱状图 |
| C15 | P05 | `P05_02_header_count_line_chart.png` | 标题数量折线图 |
| C15 | P05 | `P05_03_list_count_line_chart.png` | 列表数量折线图 |
| C15 | P05 | `P05_04_bold_count_line_chart.png` | 粗体数量折线图 |
| C15 | P05 | `P05_05_format_combination_bar_chart.png` | 格式组合柱状图 |
| C15 | R12 | `R12_format_preference_report.txt` | 格式偏好可视化汇总报告 |

#### 统计检验（C16–C17，长度↔格式对应）

| 脚本 | 类型 | 文件名 | 说明 |
|------|------|--------|------|
| C16 | T03 | `T03_length_wilcoxon_summary.csv` | 长度 Wilcoxon 检验汇总表 |
| C16 | P06 | `P06_length_wilcoxon_overview.png` | 长度效应总览图 |
| C16 | R13 | `R13_wilcoxon_length_test_report.txt` | 长度 Wilcoxon 检验报告 |
| C17 | T04 | `T04_format_test_summary.csv` | 格式检验汇总表 |
| C17 | P07 | `P07_format_effect_heatmaps.png` | 格式效应热图 |
| C17 | R14 | `R14_format_test_report.txt` | 格式检验报告 |

#### 净效应估计（C18–C19，长度↔格式对应）

| 脚本 | 类型 | 文件名 | 说明 |
|------|------|--------|------|
| C18 | T05 | `T05_pure_length_net_effect_summary.csv` | 长度净效应嵌套模型汇总表 |
| C18 | P08 | `P08_length_confounding_attenuation.png` | 长度 OR 衰减图（M0→M3） |
| C18 | R16 | `R16_pure_length_effect_report.txt` | 长度净效应嵌套回归报告 |
| C19 | T06 | `T06_pure_format_net_effect_summary.csv` | 格式净效应嵌套模型汇总表 |
| C19 | P09 | `P09_format_net_effect_heatmaps.png` | 格式净 OR 与混淆比例热图（F0→F3） |
| C19 | R17 | `R17_pure_format_effect_report.txt` | 格式净效应嵌套回归报告 |

#### 稳健性检验（C20–C21，长度↔格式对应）

| 脚本 | 类型 | 文件名 | 说明 |
|------|------|--------|------|
| C20 | T07 | `T07_length_robust_summary.csv` | 长度 IPW 稳健性汇总表 |
| C20 | P10 | `P10_length_robust_forest.png` | 长度稳健性森林图 |
| C20 | R18 | `R18_length_effect_robust_report.txt` | 长度稳健性报告 |
| C21 | T08 | `T08_format_robust_summary.csv` | 格式 IPW 稳健性汇总表 |
| C21 | P11 | `P11_format_robust_forest.png` | 格式稳健性森林图 |
| C21 | R19 | `R19_format_effect_robust_report.txt` | 格式稳健性报告 |

#### 匹配诊断与 SEM（C22–C23）

| 脚本 | 类型 | 文件名 | 说明 |
|------|------|--------|------|
| C22 | T09 | `T09_matching_summary.csv` | 倾向得分匹配结果汇总 |
| C22 | T10 | `T10_matching_balance.csv` | 匹配前后协变量平衡性表 |
| C22 | P12 | `P12_matching_diagnostics_overview.png` | 匹配诊断总览图 |
| C22 | R20 | `R20_enhanced_diagnostics_report.txt` | 匹配诊断报告 |
| C23 | T11 | `T11_sem_layer_stats.csv` | SEM 各层变量描述统计 |
| C23 | T12 | `T12_sem_correlations.csv` | SEM 变量相关矩阵 |
| C23 | T13 | `T13_sem_model_comparison.csv` | SEM 主模型与扩展模型比较 |
| C23 | T14 | `T14_sem_path_estimates.csv` | SEM 路径系数与置信区间 |
| C23 | T15 | `T15_sem_bootstrap_effects_ci.csv` | SEM Bootstrap 直接/间接效应 CI |
| C23 | P13 | `P13_sem_path_diagram.png` | SEM 路径图 |
| C23 | P14 | `P14_sem_bootstrap_effects_ci.png` | Bootstrap 效应置信区间图 |
| C23 | R21 | `R21_sem_analysis_report.txt` | SEM 分析报告 |

---

## 产物编号规则

- **R（报告）**：按脚本运行顺序 R01–R21，R15 空缺（历史遗留）
- **T（表格）**：按脚本运行顺序 T01–T15；T01/T02 为模板化多文件
- **P（图片）**：P01–P03 为手工思维导图；P04–P14 由脚本产生；P04/P05 为模板化多文件
- 长度↔格式对应关系：C14/C15、C16/C17、C18/C19、C20/C21 各自对应同类分析的长度版与格式版
