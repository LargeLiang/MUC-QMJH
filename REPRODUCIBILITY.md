# 权威重跑入口（2026-09-12）

当前结果由 CURRENT_RESULTS.json 选择，新旧逐项对应见 UNIFICATION.md。旧 C01–C23、Reports、Tables、Pictures 和 END 原有文件是历史研究记录，不再是当前推断依据。旧脚本直接运行默认停止；仅历史复核可设置 MUC_ALLOW_LEGACY=1，注意这会允许覆盖历史输出。新入口独立从全部七个原始分片构建分析数据，不读取旧缓存或旧胜率代理。

使用 Python 3.13.5，安装 `requirements-analysis.lock.txt` 后执行：

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:OPENBLAS_NUM_THREADS='2'
$env:MKL_NUM_THREADS='2'
python -m unittest discover -s tests -v
python Codes/reproduce.py --output Runs/my-new-run
```

输出目录必须不存在，防止覆盖结果。进入主计算异常处理后的失败会记录 run.json；创建目录或收集环境时失败、进程被强制终止，不保证有失败清单。status=complete 表示该脚本执行完成，不代表科研及论文验收。inputs.json 记录原始分片行数和 SHA-256，run.json 记录环境、代码及输出哈希。CSV 不人为舍入；极小 p 值可能浮点下溢为 0，不能解释为真实概率为零。只读校验使用 python Codes/verify_current.py --raw；新运行不自动成为当前结果。

## 研究范围与规则

- 分析单位为一次双模型评价，不将两侧镜像行当独立样本。
- 当前实现纳入首轮评价、交替且有文本字段的对话、相同用户消息轨迹、正 token 和完整布尔注释。在逐条清洗后，重复首轮会话全部排除并输出清单；排除原因按首次失败计数。审计发现内容 type、模型名与格式计数完整性验证仍不足；不得称为完整严格 schema 校验。
- 不重新计算 token 或 Markdown 计数：它们是发布方提供的测量，不等同于真实视觉排版或回答质量。具体 tokenizer 和计数算法尚未核实，不将模型 tokenizer 差异作为已经证实的事实。
- 胜负明确样本用于二元分析；平局保留并报告。结论仅适用于此选择后的总体。
- 长度、标题、列表、加粗：精确双侧符号检验；是否使用格式：精确 McNemar（不一致对上的二项检验）。秩二列相关使用正负秩和；Wilcoxon 仅为补充。
- 全量、英语、单轮以及 16 个互斥任务子集的全部主配对检验构成一个 Holm 家族。所有回归焦点系数构成另一个 Holm 家族。
- 联合二项 GLM 使用 log token 比、三种密度差、提示词属性、任务类型、输入长度、轮数、语言、Bradley–Terry 模型身份对比。连续焦点特征各分析样本内标准化。报告 HC0 SE、OR 区间、真实平均导数。检查设计满秩和收敛，失败不静默删控制项。
- 未观察到回答内容质量、同一用户跨会话身份；不能据此识别因果偏好。旧 SEM 不用另一组未经识别的路径分析替换。需要质量盲评或随机化同内容风格实验才能加强机制主张。

## 方法及数据来源

- [原始数据卡](https://huggingface.co/datasets/lmarena-ai/arena-human-preference-140k)：本地七分片的哈希为实际复现身份；不声称本地文件对应未经核实的远端 revision。发布许可和再分发要求以数据卡为准，不自动重新发布原始对话。
- [SciPy Wilcoxon](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wilcoxon.html)：单侧返回正秩和，零差及对称性条件。
- [statsmodels McNemar](https://www.statsmodels.org/dev/generated/statsmodels.stats.contingency_tables.mcnemar.html)：配对二元边际比较。

历史论文中的数值和因果叙事必须按新 REPORT.md 重写，旧 Word/PDF 未自动更新，不能直接提交为最新结果。
