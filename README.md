# MUC-QMJH 人类偏好关联研究

当前分析研究回答长度、标题、列表和加粗特征与人类比较结果的观察性关联。模型调整不等同于控制回答真实质量，也不支持纯因果效应或机制已证实的表述。

## 当前状态

- 唯一结果指针：[CURRENT_RESULTS.json](CURRENT_RESULTS.json)，当前指向 Runs/final-v3。
- 计算与哈希已验证；数据校验、时间与提示依赖敏感性等研究限制仍待处理。
- 正式 Word、旧论文图表尚未同步，不能将历史材料直接作为新版提交。
- 新旧文件逐项对应及待确认事项见 [统一清单](UNIFICATION.md)。

## 使用入口

使用 Python 3.13.5，在项目根目录执行：

```powershell
python -m pip install -r requirements-analysis.lock.txt
python -m unittest discover -s tests -v
python Codes/verify_current.py --raw
python Codes/reproduce.py --output Runs/my-new-run
```

最后一条命令执行全量重跑；输出目录必须不存在。新运行不会自动成为正式当前结果，应经审阅后更新结果指针。科学复现需要本地七个原始分片，位置及方法边界见 [复现说明](REPRODUCIBILITY.md)。Notebook 用户使用 [current_analysis.ipynb](Codes/current_analysis.ipynb)。

## 阅读成果

1. [当前结果摘要](RESULTS_REBUILT.md)：样本、调整关联与研究限制。
2. [运行报告](Runs/final-v3/REPORT.md)：原始运行报告，只读保留。
3. [配对检验](Runs/final-v3/paired_tests.csv)和[调整后关联](Runs/final-v3/adjusted_associations.csv)：完整精度结果。
4. [统一清单](UNIFICATION.md)：历史成果与新版对应关系。

不在首页手工复制统计数值，以减少多份结果漂移。历史 C01–C23 默认禁止直接执行；仅供有意识的历史审查。Reports、Tables、Pictures、END 中原有文件不属于当前提交成果。旧首页等原件保存在 Archive/pre-unification-20260912。

## 数据与许可

原始数据不随代码自动再分发。参见 [许可边界](LICENSE_POLICY.md)、[代码许可](LICENSE)、[文档许可](LICENSE-docs.md)。作者和正式引用信息见 [CITATION.cff](CITATION.cff)，其中版本仍为已发布历史版本，不将工作区改动虚构成已发布版本。

协作要求见 [CONTRIBUTING.md](CONTRIBUTING.md)。本工程尚未完成论文统一与研究验收。
