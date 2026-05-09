# GitHub 公开前合规审查

审查日期：2026-04-15

审查目标：在不改变研究主线的前提下，判断当前仓库中哪些内容适合直接公开，哪些内容应移出公开仓库，哪些内容应改为“说明下载 / 说明重生成”。

本次审查同时考虑两类要求：

- 合法性：是否涉及第三方数据、第三方文献、原始文本内容、上游许可边界不清的材料。
- 规范性：是否适合作为 GitHub 公开仓库长期保留，是否属于临时文件、本地配置、可再生成产物或过大二进制资产。

## 一、结论摘要

### 1. 立即阻断公开项

以下内容不建议直接随 GitHub 公开仓库发布：

- Data/ 全目录
- References/Papers/ 全目录中的第三方 PDF 文献
- [Reports/R06_cont_report.txt](../Reports/R06_cont_report.txt)，因为它包含原始文本片段
- [Temp](../Temp) 全目录
- [.vscode](../.vscode) 全目录
- [~$QMJH.doc](../~$QMJH.doc)

### 2. 应保留为公开仓库主体的内容

以下内容适合保留：

- 代码脚本主体 [Codes](../Codes)
- 自研文档 [README.md](../README.md)、[References](.) 下的大部分 Markdown 文件
- 治理与许可文件：[LICENSE](../LICENSE)、[LICENSE_POLICY.md](../LICENSE_POLICY.md)、[CITATION.cff](../CITATION.cff)、[CONTRIBUTING.md](../CONTRIBUTING.md)、[SECURITY.md](../SECURITY.md)
- 聚合性结果文件 [Tables](../Tables) 与大部分 [Pictures](../Pictures)

### 3. 建议改为“说明下载 / 说明重生成”的内容

- Data/ 中的原始数据、整合数据、派生数据和子集 parquet
- References/Papers/ 中的第三方 PDF 文献包
- 含原始文本示例的报告文件

## 二、关键证据

### 1. 数据体量

顶层目录体量显示 [Data](../Data) 约 3089.55 MB，是仓库绝对主体，不适合继续作为 GitHub 普通仓库存储。

其中最大文件包括：

- [Data/integrated_data/integrated_data.parquet](../Data/integrated_data/integrated_data.parquet)，约 1530.67 MB
- [Data/lmarena-aiarena-human-preference-140k/Data/train-00000-of-00007.parquet](../Data/lmarena-aiarena-human-preference-140k/Data/train-00000-of-00007.parquet) 等 7 个原始分片，每个约 216 到 222 MB

### 2. 上游数据许可信息

[Data/lmarena-aiarena-human-preference-140k/README.md](../Data/lmarena-aiarena-human-preference-140k/README.md) 中写明上游数据集许可为 `cc-by-4.0`。这意味着法律上“可能允许分享”，但并不等于“适合把全部数据直接塞进 GitHub 仓库”。从规范性、体量控制和边界清晰度看，仍建议改为下载说明而不是仓库内打包再分发。

### 3. 第三方文献包

[References](.) 约 60.31 MB，其中主要体量来自 [References/Papers](../References/Papers) 下的第三方 PDF 文献。这类文件即便用于研究阅读，也不适合作为公开 GitHub 仓库直接分发。

### 4. 报告中的原始文本泄露风险

[Reports/R06_cont_report.txt](../Reports/R06_cont_report.txt) 明确含有原始文本值列表，例如 “Hello! How can I help you today?”、“What is the capital of Taiwan?” 等。这意味着 [Reports](../Reports) 不能按整目录直接公开，至少应逐文件检查。

## 三、逐目录审查结论

### 顶层目录与关键文件

| 路径 | 建议动作 | 结论 | 说明 |
| --- | --- | --- | --- |
| [.github](../.github) | 保留 | 适合公开 | Issue/PR 模板和仓库治理设置是公开仓库的标准组成部分。 |
| [.vscode](../.vscode) | 移出 | 不适合公开 | 含本地编辑器设置，且 [settings.json](../.vscode/settings.json) 带有本机 R/Python 路径。 |
| [Codes](../Codes) | 保留为主 | 适合公开 | 主研究代码应保留；但需剔除局部临时文件。 |
| [Data](../Data) | 改为说明下载 | 不建议直接公开 | 含原始数据、整合数据、派生 parquet 和子集 parquet。建议只保留目录说明与获取方法。 |
| [Pictures](../Pictures) | 条件保留 | 大部分可公开 | PNG 图一般可保留；但可编辑源文件应单独判断。 |
| [References](.) | 条件保留 | Markdown 文档可公开，PDF 需分流 | 自研说明文档建议保留，第三方 PDF 不建议随仓库分发。 |
| [Reports](../Reports) | 条件保留 | 需逐文件筛查 | 大部分统计报告可保留，但含原始文本或样例行的文件需移出或重生成。 |
| [Tables](../Tables) | 保留 | 适合公开 | 当前为聚合统计表，体量小，复现价值高。 |
| [Temp](../Temp) | 移出 | 不适合公开 | 明确属于临时调试和 smoke test 产物。 |
| [README.md](../README.md) | 保留 | 适合公开 | 已具备 GitHub 首页功能。 |
| [LICENSE](../LICENSE) 等治理文件 | 保留 | 适合公开 | 属于公开仓库必要文件。 |
| [.Rprofile](../.Rprofile) | 建议移出 | 偏本地开发配置 | 仅在将来正式支持 R 工作流时再保留。 |
| [check_nb.py](../check_nb.py) | 建议移出 | 临时检查脚本 | 作用是本地检查 Notebook 结构，不是正式研究产物。 |
| [~$QMJH.doc](../~$QMJH.doc) | 立即移出 | 临时 Office 锁文件 | 明确不应进入公开仓库。 |

## 四、分目录细化建议

### 1. Codes/

#### 建议保留

- [Codes/C00_all_collection.ipynb](../Codes/C00_all_collection.ipynb)
- [Codes/C01_verify_session_integrity.py](../Codes/C01_verify_session_integrity.py) 到 [Codes/C22_sem_analysis.py](../Codes/C22_sem_analysis.py)
- [Codes/data_audit.py](../Codes/data_audit.py)

这些文件构成了研究主链，属于仓库最核心的公开内容。

#### 建议移出

- [Codes/__pycache__](../Codes/__pycache__)
- [Codes/test.R](../Codes/test.R)

原因：

- `__pycache__` 属于纯缓存。
- `test.R` 当前只是一个简单试验脚本，不属于正式研究流程。

#### 额外说明

若未来确实需要保留 R 工作流，建议新增明确的 R 分析脚本和 R 依赖说明，再重新引入 `.Rprofile` 与 R 相关支持文件。

### 2. Data/

#### 当前判断

整个 [Data](../Data) 不建议直接公开，建议改为“说明下载 / 说明重生成”。

#### 子目录建议

| 子目录 | 建议动作 | 说明 |
| --- | --- | --- |
| [Data/lmarena-aiarena-human-preference-140k](../Data/lmarena-aiarena-human-preference-140k) | 移出并改说明下载 | 上游原始数据快照，不宜作为公开仓库直接再分发主体。 |
| [Data/integrated_data](../Data/integrated_data) | 移出并改说明重生成 | 属于中间产物，可由 [Codes/C02_integrate_data.py](../Codes/C02_integrate_data.py) 重建。 |
| [Data/optimized_data](../Data/optimized_data) | 移出并改说明重生成 | 属于分析主表目录，可由 [Codes/C12_optimize_data.py](../Codes/C12_optimize_data.py) 生成。 |
| [Data/subsets](../Data/subsets) | 移出并改说明重生成 | 属于子集 parquet 目录，可由 [Codes/C13_divide_subset.py](../Codes/C13_divide_subset.py) 基于 [Data/optimized_data](../Data/optimized_data) 下主表生成。 |
| [Data/length_data](../Data/length_data) | 移出并改说明重生成 | 属于分析中间表，可由 [Codes/C14_visualize_length_preference.py](../Codes/C14_visualize_length_preference.py) 生成。 |
| [Data/format_data](../Data/format_data) | 移出并改说明重生成 | 属于分析中间表，可由 [Codes/C15_visualize_format_preference.py](../Codes/C15_visualize_format_preference.py) 生成。 |

#### 建议替代方案

公开仓库中将 [Data](../Data) 替换为：

- `Data/README.md`：说明上游数据来源、许可、下载入口、目录结构要求
- 可选的 `scripts/download_data.*`：如果上游允许自动下载，可提供脚本
- 小型合成样例数据：仅在确有测试需要时保留，不应包含真实原始文本

### 3. References/

#### 建议保留

以下自研 Markdown 文档建议保留：

- [References/current_report.md](./current_report.md)
- [References/progress.md](./progress.md)
- [References/project_plan.md](./project_plan.md)
- [References/paper_framework.md](./paper_framework.md)
- [References/method_list.md](./method_list.md)
- [References/methods](./methods)
- 其余自研 `.md` 说明文档

#### 建议移出

- [References/Papers](../References/Papers) 全目录

原因：该目录包含第三方 PDF 文献包，不适合直接随 GitHub 仓库公开分发。

#### 条件保留

- [References/71-基于大语言模型输出文本的选择偏好研究.pdf](./71-%E5%9F%BA%E4%BA%8E%E5%A4%A7%E8%AF%AD%E8%A8%80%E6%A8%A1%E5%9E%8B%E8%BE%93%E5%87%BA%E6%96%87%E6%9C%AC%E7%9A%84%E9%80%89%E6%8B%A9%E5%81%8F%E5%A5%BD%E7%A0%94%E7%A9%B6.pdf)

只有在以下条件同时满足时才建议保留：

- 文件为本项目自有成果或已获明确公开授权
- 不受投稿期刊、学位提交或校内流程限制

若无法快速确认，建议先移出公开仓库。

#### 建议替代方案

将 `References/Papers/` 改为：

- `References/Papers/README.md`：列出论文题目、作者、来源链接、DOI 或会议期刊信息

### 4. Reports/

#### 可以保留的报告

从抽检看，以下文件偏向汇总统计和研究解释，适合在再次人工复核后保留：

- [Reports/R01_session_report.txt](../Reports/R01_session_report.txt)
- [Reports/R02_order_report.txt](../Reports/R02_order_report.txt)
- [Reports/R03_turn_report.txt](../Reports/R03_turn_report.txt)
- [Reports/R04_model_report.txt](../Reports/R04_model_report.txt)
- [Reports/R05_role_report.txt](../Reports/R05_role_report.txt)
- [Reports/R08_category_tag_report.txt](../Reports/R08_category_tag_report.txt)
- [Reports/R09_optimization_report.txt](../Reports/R09_optimization_report.txt)
- [Reports/R10_division_report.txt](../Reports/R10_division_report.txt)
- [Reports/R11_length_preference_report.txt](../Reports/R11_length_preference_report.txt)
- [Reports/R12_format_preference_report.txt](../Reports/R12_format_preference_report.txt)
- [Reports/R13_wilcoxon_length_test_report.txt](../Reports/R13_wilcoxon_length_test_report.txt)
- [Reports/R14_format_test_report.txt](../Reports/R14_format_test_report.txt)
- [Reports/R16_pure_effect_report.txt](../Reports/R16_pure_effect_report.txt)
- [Reports/R17_length_effect_robust_report.txt](../Reports/R17_length_effect_robust_report.txt)
- [Reports/R18_format_effect_robust_report.txt](../Reports/R18_format_effect_robust_report.txt)
- [Reports/R19_enhanced_diagnostics_report.txt](../Reports/R19_enhanced_diagnostics_report.txt)
- [Reports/R20_sem_analysis_report.txt](../Reports/R20_sem_analysis_report.txt)

#### 不建议直接保留的报告

- [Reports/R06_cont_report.txt](../Reports/R06_cont_report.txt)

原因：包含原始 `text` 字段值列表，已构成对原始文本内容的再暴露。

#### 条件保留

- [Reports/R07_token_report.txt](../Reports/R07_token_report.txt)

该文件虽然不含原始文本，但含有 “部分不一致示例” 区块与行级 ID。若追求更稳妥的公开边界，建议重生成一个不含示例行、只保留聚合统计版本。

#### 另建议移出

- [Reports/阶段报告.docx](../Reports/%E9%98%B6%E6%AE%B5%E6%8A%A5%E5%91%8A.docx)

原因：

- Office 二进制文件不利于版本管理
- 公开仓库优先保留 Markdown、TXT、PDF 等更可审阅格式

### 5. Tables/

当前 [Tables](../Tables) 下均为聚合统计 CSV，体量小、复现价值高、未见原始文本片段，建议保留。

### 6. Pictures/

#### 建议保留

以下 PNG 图像建议保留：

- [Pictures/P01_original_structure.png](../Pictures/P01_original_structure.png)
- [Pictures/P02_chat_structure.png](../Pictures/P02_chat_structure.png)
- [Pictures/P03_optimized_structure.png](../Pictures/P03_optimized_structure.png)
- [Pictures/P04_01_full_length_diff_line_chart.png](../Pictures/P04_01_full_length_diff_line_chart.png) 及其子集图
- [Pictures/P05_01_format_presence_bar_chart.png](../Pictures/P05_01_format_presence_bar_chart.png)
- [Pictures/P05_02_header_count_line_chart.png](../Pictures/P05_02_header_count_line_chart.png)
- [Pictures/P05_03_list_count_line_chart.png](../Pictures/P05_03_list_count_line_chart.png)
- [Pictures/P05_04_bold_count_line_chart.png](../Pictures/P05_04_bold_count_line_chart.png)
- [Pictures/P05_05_format_combination_bar_chart.png](../Pictures/P05_05_format_combination_bar_chart.png)
- [Pictures/P13_sem_path_diagram.png](../Pictures/P13_sem_path_diagram.png)

#### 建议移出

- [Pictures/P01 ——features.xmind](../Pictures/P01%20%E2%80%94%E2%80%94features.xmind)

原因：

- 属于编辑源文件，不是最终公开展示材料
- XMind 为专有编辑格式，不是公开仓库的理想长期归档格式

### 7. Temp/

整个 [Temp](../Temp) 目录建议移出。当前包含 [Temp/sem_smoke](../Temp/sem_smoke) 这样的临时 smoke test 产物，只适合本地调试，不适合公开仓库。

### 8. .vscode/

整个 [.vscode](../.vscode) 目录建议移出。当前 [settings.json](../.vscode/settings.json) 中含有本机解释器和 R 路径，不适合公开暴露，也容易误导其他贡献者环境。

## 五、建议的公开版目录状态

### 建议保留

- `Codes/` 正式脚本与 Notebook
- `.github/` 模板与仓库配置
- `README.md`、`LICENSE*`、`CITATION.cff`、`CONTRIBUTING.md`、`SECURITY.md`
- `References/` 下的自研 Markdown 文档与方法介绍
- `Tables/`
- `Pictures/` 下的 PNG 图像
- 经过复核和必要脱敏后的 `Reports/`

### 建议移出

- `.vscode/`
- `Temp/`
- `Data/` 中全部实际数据文件
- `References/Papers/`
- `Codes/__pycache__/`
- `Codes/test.R`
- `check_nb.py`
- `.Rprofile`
- `Reports/阶段报告.docx`
- `Pictures/P01 ——features.xmind`
- `~$QMJH.doc`

### 建议改为说明下载 / 说明重生成

- `Data/`
- `References/Papers/`
- 含原始文本或行级样例的报告文件

## 六、建议的后续动作顺序

1. 先把 `Data/`、`References/Papers/`、`.vscode/`、`Temp/`、`__pycache__/` 和临时文件移出 Git 仓库。
2. 新增 `Data/README.md`，说明上游数据来源、许可、下载方式和目录结构。
3. 新增 `References/Papers/README.md`，用论文列表替代 PDF 打包。
4. 修改 [Codes/C09_touch_cont.py](../Codes/C09_touch_cont.py)，让它不再把原始 `text` 值写入报告，然后重生成 [Reports/R06_cont_report.txt](../Reports/R06_cont_report.txt)。
5. 复核 [Reports/R07_token_report.txt](../Reports/R07_token_report.txt) 等含“示例”段落的报告，尽量改成纯聚合统计输出。
6. 最后再做一次 `git status` 与人工抽检，确认没有原始文本、原始数据、第三方 PDF 和本地路径残留。

## 七、审查结论

当前仓库已经具备公开仓库的代码、治理和许可骨架，但仍未达到“可直接公开推送”的状态。最大的三个阻断因素是：

- 数据目录仍完整留在仓库中
- 第三方 PDF 文献包仍打包在 References/Papers 中
- 至少一个报告文件已暴露原始文本片段

在完成上述清理与替换后，这个仓库就会更接近一个合规、规范、可复现的研究型 GitHub Repo。