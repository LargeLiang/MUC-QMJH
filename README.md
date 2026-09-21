# MUC-QMJH：大语言模型输出特征与人类选择偏好

当前工程研究回答长度、格式特征与配对胜负的**观察性关联**，不将其解释为因果效应或机制。

当前结果由 [CURRENT_RESULTS.json](CURRENT_RESULTS.json) 唯一指定。2026-09-20 已从全部 7 个原始分片完成整合试运行：135,634 条输入、108,154 条保留记录、78,959 对明确胜负。13 项可比产物与归档 final-v3 的 SHA-256 全部一致。

## 工程组织

| 位置 | 用途 |
| --- | --- |
| Codes/C00_run_all.py | 完整运行入口，统一调度 C01–C06 |
| Codes/C00_all_collection.ipynb | 无历史输出的交互入口，默认只校验 |
| Codes/C01_prepare_data.py | 从全部原始分片重建样本 |
| Codes/C02_paired_tests.py | 配对检验及 Holm 校正 |
| Codes/C03_adjusted_associations.py | 调整后的关联及敏感性分析 |
| Codes/C04_export_results.py | Markdown 报告和 Pxx 图 |
| Codes/C05_verify_results.py | 源码、输入与产物完整性校验 |
| Codes/C06_compare_legacy.py | 可选的归档基线等价性校验，由 C00 调用 |
| Data/lmarena-aiarena-human-preference-140k | 保留原位置的上游原始数据 |
| Data/analysis_data/运行编号 | 当前派生数据，不公开提交 |
| Reports/运行编号 | Rxx 输入记录、运行清单、报告和对照 |
| Tables/运行编号 | Txx 统计表 |
| Pictures/运行编号 | Pxx 图片 |
| Legacy | 所有旧工程、旧缓存、旧图表、旧运行及 END 结项材料 |
| 基于大语言模型输出文本的选择偏好研究 | 仍保留的论文工作稿；未自动替换旧结果 |

Cxx/Rxx/Txx/Pxx 命名传统保留；编号不表示与 Legacy 中同号文件的统计含义相同。每次运行独立分目录，禁止覆盖。

## 快速使用

建议 CPython 3.13.5，先安装锁定依赖：

```powershell
python -m pip install -r requirements-analysis.lock.txt
python -m unittest discover -s tests -v
python Codes/C05_verify_results.py --verify-raw
```

从原始分片重新运行（自动创建唯一运行编号，不默认改当前指针）：

```powershell
python Codes/C00_run_all.py
```

显式命名、对照归档并在验证成功后更新当前指针：

```powershell
python Codes/C00_run_all.py --run-id my-new-run --compare-legacy Legacy/Runs/final-v3 --promote
```

不要复用已有运行编号。对照基线属于可选迁移验收，不是新流程运行依赖。缺少本地原始/派生数据时，可使用 `python Codes/C05_verify_results.py --public-only` 仅校验公开产物；这不等于完整复现。

详见 [复现说明](REPRODUCIBILITY.md)、[新旧对应](UNIFICATION.md)、[当前结果摘要](RESULTS_REBUILT.md) 和 [迁移记录](MIGRATION.md)。

## 研究边界

重复提示词/用户的相关性、时间漂移、独立回答质量测量缺失、平局选择及细小子组不稳定仍需进一步研究。本次为工程整合和等价性验证，不是全部统计审计问题的修复，也不意味着论文已达到投稿验收标准。旧匹配、IPW、SEM 结果保留供审计，不作为当前推断证据。

代码及文档授权见 LICENSE、LICENSE-docs.md；原始数据、派生数据及第三方材料另遵循上游许可，迁入 Legacy 不改变权利边界。
