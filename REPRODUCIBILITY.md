# 完整复现说明

## 环境及输入

使用 CPython 3.13.5；`requirements-analysis.lock.txt` 固定分析与绘图依赖。C00 记录实际 Python、平台、依赖版本及 BLAS 线程数，并拒绝包版本与锁不一致的完整运行。Python/系统差异仍可能影响浮点或图像字节；跨平台复现不承诺所有文件字节一致。

原始输入固定为 `Data/lmarena-aiarena-human-preference-140k/Data/train-00000-of-00007.parquet` 至 `train-00006-of-00007.parquet`。必须具备全部七片。上游许可由使用者确认，本仓库不复制或重新授权原始数据。每片 SHA-256 和行数记入 R01_inputs.json。

## 执行

在工程根目录：

```powershell
python -m pip install -r requirements-analysis.lock.txt
python -m unittest discover -s tests -v
python Codes/C00_run_all.py --run-id independent-reproduction
python Codes/C05_verify_results.py --manifest Reports/independent-reproduction/R00_run_manifest.json --verify-raw
```

也可从其他工作目录使用 C00/C05 的绝对路径；源码中的 ROOT 由文件位置解析，不依赖当前工作目录。CLI 的 `--manifest` 和 `--compare-legacy` 相对参数则相对于调用者当前目录。

程序依次重建样本、运行配对检验、拟合三个模型、导出报告/图、校验源码/产物及七片原始输入。所有结果直接生成于 Data、Reports、Tables、Pictures 各自的运行编号目录，不建立新的 Runs。

运行编号仅允许 1–80 个英文字母、数字、下划线和短横线，首字符必须为字母或数字；任一产出目录已存在则拒绝运行，不覆盖。已开始阶段计算后的异常写入失败清单，失败目录保留用于排查，应换编号重试。`--promote` 仅在全链成功且完整性校验通过后更新当前指针。硬终止或环境缺失可能留下 running 清单或部分目录，不能当完成结果使用。

## 校验层级

- `python Codes/C05_verify_results.py --verify-raw`：当前指针的清单哈希、全套分析源码/Notebook/依赖锁、全部产物及原始七片。
- `python Codes/C05_verify_results.py`：当前指针、源码及全部派生产物，不重新哈希原始分片。
- `python Codes/C05_verify_results.py --public-only`：跳过私有派生数据；用于不含本地数据的 CI。
- `--compare-legacy Legacy/Runs/final-v3`：C00 可选校验旧清单内的基线文件哈希，再比较 13 项数据和统计产物；CSV 容差 1e-12，Parquet 数据逐值完全一致，同时记录是否字节相同。

修改 Codes 中任意 .py/.ipynb 或依赖锁都会使现有结果的源码校验失败，需要新运行，不能只改清单哈希。.gitattributes 固定当前源码为 LF，并禁止 Git 对结果及归档做换行转换，以免跨平台检出改变哈希。该校验用于完整性追踪，不是数字签名或防恶意篡改机制，也不证明研究假设成立。

## 本轮验收

运行 `integrated-20260920` 由全部七片从头完成；13 项对照产物全部字节一致，原始数据/源代码/产物完整校验通过。R04 报告和 P01/P02 图为新版生成，不要求与旧文字或图字节一致。详见 Reports/integrated-20260920/R00_run_manifest.json 与 R05_legacy_equivalence.json。

统计规格沿袭归档 final-v3。未在本次迁移中加入时间分层、提示词聚类、扩展缺失/异常 schema 检查或新因果模型；这些仍列为后续方法工作。
