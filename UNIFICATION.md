# 新旧成果对应与当前权威

唯一当前结果由 CURRENT_RESULTS.json 指定。2026-09-20 整合后，当前入口为 Codes/C00_run_all.py，不再是 reproduce.py；所有旧入口已移入 Legacy。

| 类别 | 归档位置 | 当前位置/处理 |
| --- | --- | --- |
| 旧 C01–C23、旧 Notebook、旧 reproduce.py | Legacy/Codes | Codes/C00–C06 与新 C00 Notebook |
| 旧格式、长度、整合、清洗、子集缓存 | Legacy/Data | 重新从活动原始分片构建 Data/analysis_data/运行编号 |
| 旧图、报告和统计表 | Legacy/Pictures、Reports、Tables | 新结果只写 Pictures、Reports、Tables/运行编号 |
| final-v3 等旧运行及 5,000 次 Bootstrap 运行 | Legacy/Runs | 当前结果由根目录指针选取；旧 SEM 仅历史 |
| END 校内创新项目结项文件 | Legacy/END | 原件归档，不当成论文主版本 |
| 方法材料、旧归档、临时脚本和旧测试 | Legacy/References、Archive、tmp、tests 等 | 当前文档在根目录，当前测试在 tests |
| 上游原始分片 | 未搬动 | Data/lmarena-aiarena-human-preference-140k |
| “基于……”论文工作稿 | 未搬动、未修改正文 | 留在根目录原子目录，尚需依据新结果修订 |

迁移保留了用户最近对旧 Notebook、SEM 代码、结构图和 Bootstrap 产物的修改。旧文件原文里的相对路径和“当前”措辞保留历史语境，不再视为活动指令。Legacy 不是无需配置即可直接运行的独立快照：原始数据仍在活动工程，旧环境及路径也可能需要单独配置。

当前统计规格与 final-v3 完全相同；本次 13 项可比数据/统计文件字节一致。原先撤回的匹配/IPW/SEM 因果解释没有因迁移而恢复有效。新版编号是职责编号，不能用同号机械替代历史表格。

论文工作稿未覆盖，旧研究结果与新分析口径仍需逐项转换。END 已明确归为结项材料，论文目录才是继续写作的工作位置。
