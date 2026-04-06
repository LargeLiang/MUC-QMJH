# 代码阅读报告

## 一、项目背景与当前进展

项目主题为“基于大语言模型输出文本的选择偏好研究——以LMArena对话数据为例”。

- 数据来源：`Data/lmarena-aiarena-human-preference-140k`。
- 目标：分析长度偏好、格式偏好、伪相关性、混淆变量控制与偏好机制。
- 当前进展：已经完成原始数据合并、会话/order结构检查、字段完整性分析、数据优化、长度与格式可视化分析、子集划分、Wilcoxon检验、效应量计算、纯净效应建模、稳健性分析和匹配诊断。

> 本报告仅对代码进行阅读总结，不修改任何源代码。


## 二、Python 运行环境说明

- 建议 Python 解释器位置：`C:\Code\Python_3.13\python.exe`
- 运行时请从项目根目录 `d:\Files\25_10_22_青苗计划` 启动。
- 代码多数依赖：`pandas`, `numpy`, `scipy`, `statsmodels`, `sklearn`, `matplotlib`, `seaborn`, `tqdm`。


## 三、`Codes` 文件夹脚本功能总结

### 1. C01_verify_session_integrity.py

- 函数：`verify_session_integrity()`
- 作用：读取 7 个原始 parquet 文件，统计每个文件中 `evaluation_session_id` 的唯一值并比较它们的总和与整体唯一值数。
- 目的：验证原始数据是否存在跨文件会话拆分，判断会话是否被分割。

### 2. C02_integrate_data.py

- 函数：`integrate_original_data()`
- 作用：读取7个原始 parquet，使用 `pd.concat` 合并为一个整体 DataFrame，并保存为 `Data/integrated_data/integrated_data.parquet`。
- 目的：恢复数据完整性，方便后续统一分析。

### 3. C03_verify_order_consistency.py

- 函数：`verify_order_consistency()`
- 作用：分析 `Data/integrated_data/integrated_data.parquet` 中每个 `evaluation_session_id` 的出现次数，并取 `evaluation_order` 的最大值。
- 目的：判断同一会话内是否存在 Order 缺失。

### 4. C04_touch_session.py

- 函数：`touch_evaluation_session_id()`，`generate_session_report(...)`
- 作用：统计 `evaluation_session_id` 的出现次数，提取重复会话信息，并将分析结果写入 `Reports/R01_session_report.txt`。
- 目的：生成可复现的会话层级分析报告。

### 5. C05_touch_order.py

- 函数：`touch_order()`，`generate_Order_report(...)`
- 作用：统计 `evaluation_order` 不同取值及其计数，并输出 `Reports/R02_order_report.txt`。
- 目的：检查数据中 Order 的分布和数量。

### 6. C06_touch_turn.py

- 函数：`touch_turn()`，`generate_session_report(...)`
- 作用：基于 `conv_metadata['turns']` 检查 `conversation_a` 与 `conversation_b` 的长度一致性，并将结果写入 `Reports/R03_turn_report.txt`。
- 目的：验证对话轮次与对话内容结构之间的关系。

### 7. C07_touch_model.py

- 函数：`touch_model()`，`generate_model_report(...)`
- 作用：统计所有模型的出场次数与胜率，输出 `Reports/R04_model_report.txt`。
- 目的：分析模型分布与胜率差异，是后续模型能力或混淆变量分析的基础。

### 8. C08_touch_role.py

- 函数：`touch_role()`
- 作用：统计 `conversation_a` 和 `conversation_b` 的角色值分布，检查是否只包含 `user` / `assistant` 等角色。
- 目的：验证对话角色规范性。

### 9. C09_touch_cont.py

- 函数：`touch_cont()`
- 作用：检查每个对话单元中 `content` 的结构，统计 `type`、`text`、`image`、`mimeType` 等子属性，并输出发现。
- 目的：判断是否存在空内容或嵌套结构异常。

### 10. C10_verify_token_correction.py

- 函数：`verify_token_correction()`
- 作用：验证 `conv_metadata` 中 `sum_user_tokens` 与 `sum_assistant_b_tokens` 是否与各 `conversation_b` 内实际 `num_tokens` 累计一致。
- 目的：审计 token 汇总字段是否正确，可用作后续长度特征信赖基础。

### 11. C11_touch_category_tag.py

- 函数：`touch_category_tag()`
- 作用：统计 `category_tag` 中多个子字段的分布：creative_writing、if、math、language、is_code 等，并打印不同值的计数。
- 目的：理解分类标签与任务属性的分布情况，为后续子集分析提供基础。

### 12. C12_optimize_data.py

- 函数：`check_qualification(row)`、`optimize_conversation(conv_a, conv_b)`、`optimize_conv_metadata(metadata)`、`optimize_category_tag(category_tag)`、`optimize_criteria(category_tag)`、`optimize_data()`、`divide_data()`
- 作用：
  - `check_qualification`: 剔除 `evaluation_order>1`、空 `content`、无效标签、异常语言的样本。
  - `optimize_conversation`: 按 turn 重构 `user_conv`、`a_conv`、`b_conv`。
  - `optimize_conv_metadata`: 提取关键 token/格式计数字段。
  - `optimize_category_tag`: 压缩 `category_tag` 为布尔值与分数字段。
  - `optimize_criteria`: 提取核心 criteria 字段。
  - `optimize_data`: 生成 `Data/optimized_data/optimized_data.parquet`。
  - `divide_data`: 进一步按 `creative_writing`、`if`、`math` 划分子文件。
- 目的：生成结构化、去噪、分析友好的优化数据集。
- 备注：`divide_data()` 中对三个 bool 字段的筛选方式使用了 `~...isin([True])`，这与 `C15_divide_subset.py` 中的 True 过滤逻辑不一致。建议确认是否为笔误。

### 13. C13_visualize_length_preference.py

- 函数：`prepare_length_data(df)`、`create_length_ratio_bins(...)`、`create_length_diff_bins(...)`、`find_optimal_interval_ratio(...)`、`find_optimal_interval_diff(...)`、`plot_length_ratio_preference_chart(...)`、`plot_length_diff_preference_chart(...)`、`create_statistical_table(...)`、`generate_analysis_report(...)`
- 作用：
  - 过滤无效 winner 样本，构造 `length_ratio` 和 `length_diff`。
  - 使用分箱分析长度比率与长度差值对赢率的影响。
  - 生成可视化图、统计表和文本报告。
- 输出文件：`
  * Pictures/P04_length_ratio_line_chart.png
  * Pictures/P05_length_diff_line_chart.png
  * Reports/R05_length_analysis_report.txt
  * Tables/T01_length_ratio_analysis_stats.csv
  * Tables/T02_length_diff_analysis_stats.csv
`
- 目的：量化并可视化“长度偏好”的分布与最优区间。

### 14. C14_visualize_format_preference.py

- 函数：`extract_header_count(...)`、`extract_list_count(...)`、`extract_bold_count(...)`、`prepare_format_data(df)`、`analyze_format_presence(...)`、`analyze_header_count(...)`、`analyze_list_count(...)`、`analyze_bold_count(...)`、`analyze_format_combinations(...)`、`plot_presence_bar_chart(...)`、`plot_header_count_line_chart(...)`、`plot_list_count_line_chart(...)`、`plot_bold_count_line_chart(...)`、`plot_combination_bar_chart(...)`、`create_summary_tables(...)`、`generate_report(...)`
- 作用：
  - 从优化数据中提取格式特征：标题、列表、粗体数量与组合。
  - 统计比较带格式和不带格式的赢率差异。
  - 绘制格式偏好图表，并输出报告与表格。
- 输出文件：`
  * Pictures/P06_format_presence_bar_chart.png
  * Pictures/P07_header_count_line_chart.png
  * Pictures/P08_list_count_line_chart.png
  * Pictures/P09_bold_count_line_chart.png
  * Pictures/P10_format_combination_bar_chart.png
  * Reports/R06_format_analysis_report.txt
  * Tables/T03_basic_statistics.csv
  * Tables/T04_format_presence_analysis.csv
  * Tables/T05_header_count_analysis.csv
  * Tables/T06_list_count_analysis.csv
  * Tables/T07_bold_count_analysis.csv
  * Tables/T08_format_combination_analysis.csv
`
- 目的：量化“格式偏好”的存在性与强度。

### 15. C15_divide_subset.py

- 函数：`divide_subset_by_category()`
- 作用：按 `creative_writing_bool`、`if_bool`、`math_bool` 划分子集，生成单一标签、纯子集、交叉子集、全标签与无标签数据文件。
- 输出文件：多个 `Data/optimized_data/*.parquet` 子集文件，并写 `Reports/R07_subset_division_report.txt`。
- 目的：为类别分层分析与稳健性验证准备子集。

### 16. C16_length_test.py

- 类：`PreferenceAnalyzer`
- 方法：`calculate_token_diff(...)`、`perform_wilcoxon_test(...)`、`load_and_test_dataset(...)`、`run_all_tests()`、`generate_report()`、`save_report(...)`
- 作用：进行Wilcoxon符号秩检验，比较赢者与输者之间 token 差异，并对多个子集输出检验结果。
- 输出文件：`Reports/R08_wilcoxon_test_report.txt`。
- 目的：验证长度偏好的统计显著性。

### 17. C17_format_test.py

- 函数：`get_count(value)`、`format_diff(row, feature)`、`compute_format_preference_lines(df, label)`、`run_format_preference_test()`
- 作用：
  - 计算 winner 相对于 loser 的格式特征差异。
  - 进行 Wilcoxon 检验、卡方列联表分析和逻辑回归。
  - 输出格式偏好检验报告 `Reports/R11_format_preference_report.txt`。
- 目的：补充格式偏好统计检验和预测分析。

### 18. C18_calculate_effect_size.py

- 函数：`get_token_diff(df)`、`get_feature_diff(df, feature)`、`compute_effect_sizes(diff_series)`、`subset_effect_size_report(df)`
- 作用：根据已有长度与格式差异计算效应量，包括 Cohen's d、Hedges' g、rank-biserial 和 Wilcoxon r。
- 输出文件：`Reports/R12_effect_size_report.txt`。
- 目的：将偏好结果转换为可解释效应量。

### 19. C19_pure_effect.py

- 函数：`norm_feature(x)`、`compute_diffs(df)`、`extract_count(value, feature_type)`、`prepare_pure_effect_df(df)`、`define_confounders(df)`、`fit_logistic_model(X, y)`、`subset_pure_effect_analysis(...)`、`run_pure_effect()`
- 作用：
  - 构建 winner_oriented 差异特征 `token_diff`、`header_diff`、`list_diff`、`bold_diff`。
  - 定义潜在混淆变量并拟合逻辑回归：仅目标变量、目标+混淆变量、混淆变量单独模型。
  - 输出纯效应报告 `Reports/R13_pure_effect_report.txt`。
- 目的：评估混淆变量控制后偏好效应是否仍然稳健。

### 20. C20_length_effect_robust.py

- 函数：`extract_count(...)`、`load_optimized_data(...)`、`prepare_robust_data(...)`、`available_confounders(...)`、`fit_logistic_model(...)`、`logistic_summary(...)`、`propensity_score_matching(...)`、`ipw_estimate(...)`、`subset_names()`、`render_report()`
- 作用：
  - 引入 `longer_a`、`longer_wins`、`length_tie` 等直接长度处理标签。
  - 用 Logistic 回归、PSM、IPW 进行稳健性分析。
  - 输出 `Reports/R14_length_effect_robust_report.txt`。
- 目的：构建更稳健的长度偏好证据链并衡量混淆控制效果。

### 21. C21_enhanced_matching_diagnostics.py

- 函数：`extract_count(...)`、`load_optimized_data(...)`、`create_ability_proxies(...)`、`enhanced_confounders(...)`、`fit_logistic_model(...)`、`logistic_summary(...)`、`propensity_score_matching_with_diagnostics(...)`、`ipw_estimate(...)`、`subset_names()`、`render_main_report()`、`render_ability_proxy_summary()`
- 作用：
  - 在原有稳健分析基础上增加能力/难度代理变量：`ability_quality`, `ability_clarity`, `task_difficulty`, `format_structure_diff`。
  - 生成匹配质量诊断报告与能力代理统计。
  - 输出 `Reports/R15_enhanced_diagnostics_report.txt` 和 `Reports/R15_ability_proxies.txt`。
- 目的：从更多角度评估长度偏好与样本能力/难度之间的关系。

### 22. data_audit.py

- 脚本：顶层执行，无函数
- 作用：遍历项目中 `Data` 子目录下多个 parquet 文件夹，检查 parquet 文件是否存在并记录行数与列名。
- 输出文件：`Reports/R14_data_audit_report.txt`。
- 目的：快速审计数据文件状态。


## 四、核心代码特性与架构点评

### 4.1 代码结构

- `C01`~`C11` 主要完成数据探索与字段审计。
- `C12` 为核心优化与数据清洗模块，输出统一分析数据集。
- `C13`~`C14` 负责可视化与描述性偏好分析。
- `C15`~`C21` 负责子集划分、统计检验、效应量和稳健性建模。
- `data_audit.py` 是独立的数据完整性检查脚本。

### 4.2 设计优点

- 流程清晰：从原数据到优化数据，再到偏好分析、检验与稳健模型。
- 报告输出明确：各阶段分析均写入 `Reports` 文件，便于复现和审阅。
- 脚本模块化较好：每个脚本专注一个分析阶段。

### 4.3 发现的代码问题或风险点

- `C12_optimize_data.py` 中的 `divide_data()` 逻辑使用 `~df['creative_writing_bool'].isin([True])` 等表达式。这实际上会选择 False, NaN 样本，而不是 True 样本，可能与 `C15_divide_subset.py` 的目的不一致。
- 多个脚本依赖 `os.getcwd()` 获取项目路径，要求运行时必须位于工作区根目录，否则文件路径会错。
- 部分统计脚本直接调用 `df.apply(...)` 或循环 `for idx in range(len(df))`，在大数据帧上性能较低。
- 代码普遍缺少异常处理和日志输出，运行失败时难以定位具体文件或样本。
- `C17_format_test.py` 的 logistic regression 结果只打印训练准确率，未进行 train/test 拆分或稳健性检查。
- `C20`/`C21` 中 `fit_logistic_model(...)` 的 sklearn 回退模式构造 `params` 变量时，名称长度可能与系数长度不一致，需进一步检查兼容性。


## 五、构建代码的建议

### 5.1 运行与依赖管理

- 建议使用 `venv` 或 conda 环境，并将依赖写入 `requirements.txt`。
- 依赖建议清单：
  - pandas
  - numpy
  - scipy
  - statsmodels
  - scikit-learn
  - matplotlib
  - seaborn
  - tqdm

- 运行命令示例：
  ```powershell
  C:\Code\Python_3.13\python.exe d:\Files\25_10_22_青苗计划\Codes\C02_integrate_data.py
  ```
- 统一项目根目录启动，以保证 `os.getcwd()` 与相对路径一致。

### 5.2 数据处理与性能优化

- 将 `for idx in range(len(df))` 改为矢量化 `pandas` 操作，提升性能。
- 优化 `check_qualification()` 和数据筛选逻辑为批量条件过滤，而非逐行判断。
- 建议在 `C12` 中保留 `evaluation_order>1` 过滤逻辑说明，并确认是否应在划分时使用 True 子集。
- 增加数据审计脚本对缺失值和异常值的自动统计，而不仅仅是文件结构。

### 5.3 代码结构与复用性

- 建议将公共路径与读取函数抽成一个共享模块，例如 `Codes/utils.py`，减少 `os.getcwd()`、路径硬编码和重复转换。
- 将重复的 `subset` 选择逻辑提取为统一函数，避免 `C16`~`C21` 中多次重复。
- 将可视化、报告生成、统计分析与数据准备分层组织：
  - `data_preparation.py`
  - `exploratory_analysis.py`
  - `preference_visualization.py`
  - `statistical_tests.py`
  - `robust_analysis.py`

### 5.4 测试与可复现性

- 添加单元测试或小型脚本验证：
  - 路径读取是否可用
  - 原始 parquet 是否加载成功
  - 优化数据字段是否齐全
  - 主要输出文件是否生成
- 在 `Reports` 目录之外，考虑输出 `Logs` 或 `debug` 文件以记录运行过程。

### 5.5 文档与说明

- 建议补充 `README.md`：说明项目目录结构、运行顺序、所需数据路径、核心脚本用途。
- 将每个关键脚本入口的执行流程写入 `README` 或 `project_plan.md` 的技术实现部分。
- 对统计方法增加说明：为什么选 Wilcoxon、为什么使用 PSM / IPW、混淆变量如何定义。


## 六、建议执行顺序

1. `C02_integrate_data.py`：合并原始 parquet 数据。
2. `C04_touch_session.py` / `C05_touch_order.py` / `C06_touch_turn.py` / `C07_touch_model.py` / `C08_touch_role.py` / `C09_touch_cont.py` / `C10_verify_token_correction.py` / `C11_touch_category_tag.py`：探索与审计。
3. `C12_optimize_data.py`：生成 `Data/optimized_data/optimized_data.parquet`。
4. `C15_divide_subset.py`：按类别划分子集。
5. `C13_visualize_length_preference.py` 和 `C14_visualize_format_preference.py`：描述性偏好分析与图表。
6. `C16_length_test.py` / `C17_format_test.py`：统计检验。
7. `C18_calculate_effect_size.py`：效应量计算。
8. `C19_pure_effect.py` / `C20_length_effect_robust.py` / `C21_enhanced_matching_diagnostics.py`：混淆控制与稳健性检验。
9. `data_audit.py`：数据审计结果检查。


## 七、结论

该代码库已经包含完整的数据审计、特征构造、偏好可视化、统计检验和稳健性分析链路。当前关键改进点在于路径统一、数据筛选逻辑一致性、性能优化以及参数和报告说明的规范化。

建议以 `C12_optimize_data.py` 作为核心数据处理入口，后续分析脚本统一读取 `Data/optimized_data/optimized_data.parquet`，并在 `README.md` 中给出明确运行顺序。
