# 新旧成果统一清单

唯一当前结果指针为 `CURRENT_RESULTS.json`。当前使用 `Runs/final-v3`，这是已完成计算校验、但尚有研究限制的观察性分析，不代表论文已经完成验收。

|成果类别|历史位置|当前对应|处理决定|
|---|---|---|---|
|分析入口|Codes/C01–C23|Codes/reproduce.py|旧入口默认停用；显式允许才可历史复核|
|交互入口|Codes/C00_all_collection.ipynb|Codes/current_analysis.ipynb|旧 notebook 保留并标记；新 notebook 调用唯一入口|
|整合及清洗数据|Data/integrated_data、optimized_data、subsets|Runs/final-v3/analysis_data.parquet|不搬动旧缓存；新链不读取它们|
|样本清洗报告|Reports/R01–R10|Runs/final-v3/attrition.csv、inputs.json|新旧保留；不互换样本口径|
|长度与格式检验|Tables/T01–T04、Reports/R11–R14|Runs/final-v3/paired_tests.csv|以新检验为准；旧分箱和图没有声称已重建|
|调整后关联|Tables/T05–T06|Runs/final-v3/adjusted_associations.csv|模型与尺度不同，不将新 OR 当旧 OR 的直接替换|
|IPW 与匹配|Tables/T07–T10|无有效替代推断|撤回旧推断，非重新验证通过|
|SEM|Tables/T11–T15|无有效替代推断|撤回旧机制解释|
|论文图表|Pictures、Tables/paper_ready|待生成新版|全部旧图表仍为历史，不用于新提交|
|结题正文与答辩|END|等待确认正式主版本及另存方案|原件保留，未擅自改写正式材料|
|方法教学材料|References|历史学习资料|不作为当前研究已经执行的步骤证明|
|运行结果|Runs/rebuild-v1、rebuild-v2|Runs/final-v3|前者失败或已被替代，不作为默认结果|

## 本轮不改变的内容

本轮是工程及成果身份统一，不改动 `Codes/reproduce.py`、原始数据、final-v3 产物或统计规格。时间分层、提示聚类、异常计数校验等审计建议仍未实施，不能写作已修复。旧报告本身保留原文，历史标记不表示其结论有效。

## 已知口径差异

- 旧明确胜负样本 78,970，新样本 78,959；旧清洗总量 108,171，新总量 108,154。
- 新 62.37% 的分母是长度不相等的 78,772 对；旧 62.21% 使用含等长配对的分母，不能直接解读为偏好增强。
- 新长度变量为标准化 log token 比，旧模型采用不同特征与控制；OR 的差异并不等于研究效应随修复变大。
- 新秩二列相关修正为 0.3278；标题在英语和单轮敏感性分析中不稳定，不能统一成“格式稳定有效”。

## 验收与后续

运行 `python Codes/verify_current.py --raw` 验证当前输入、源代码和产物；公开仓库缺少派生记录时使用 `--public-only`，此模式不是完整数据验收。运行 `python -m unittest discover -s tests -v` 检查基础统计与统一入口约束。

本轮尚待用户确认：以 END/结题报告.docx 为正式材料主版本，另存新稿，统一为观察性关联叙述。没有用户确认前不覆盖、删除或发布正式论文。
