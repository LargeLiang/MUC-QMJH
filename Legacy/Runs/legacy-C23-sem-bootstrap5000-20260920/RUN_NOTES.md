# 运行记录：C23 SEM legacy bootstrap=5000（2026-09-20）

本目录内容由脚本自动生成的 R21_sem_analysis_report.txt / T11–T15 / P13–P14 已完整覆盖分析结果，
本文件仅补充该次运行的执行上下文，供后续审计追溯。

## 执行方式

- 入口：`Codes/C23_sem_analysis.py` 的 `run_sem_analysis()`（未经 CLI，直接 import 调用）
- 环境变量：`MUC_ALLOW_LEGACY=1`（该脚本是历史入口，legacy_guard 要求显式 opt-in）
- 解释器：`C:/Code/Anaconda3/envs/muc-qmjh/python.exe`（Python 3.13.12，semopy 2.3.11）
- 工作目录：仓库根目录（`Path.cwd()` 决定 accessor.get_path 的数据根，必须在根目录下运行）
- 参数：`bootstrap_n=5000`，`max_n=None`（不抽样，全量 78,970 条建模样本），`seed=42`（默认）
- 输出目录：本目录（新建，未覆盖 `Reports/R20_sem_analysis_report.txt`、`Tables/T11–T15`、`Pictures/P13–P14` 等历史文件）

## 运行结果摘要

- 总耗时：约 2229.6 秒（37.2 分钟）
- Bootstrap 成功率：4818 / 5000（96.4%），其余样本因收敛失败被跳过（`fit_sem_model` 抛异常时静默跳过）
- 关键差异：此前用 3 次 bootstrap 做计时测试时，"长度直接效应""能力→长度→偏好""能力总间接效应""词冗性→长度→偏好""格式倾向直接效应" 均误判为 CI 排除 0；
  用真实 5000 次后，这些效应的 95% CI 均跨 0（详见本目录 `T15_sem_bootstrap_effects_ci.csv`）。
  仍稳健的效应：标题/粗体密度直接效应、能力直接效应/总效应、能力→标题/粗体密度→偏好、格式倾向→标题/粗体密度→偏好、格式倾向总间接效应。
- 原始运行日志（含逐次 bootstrap 进度与 semopy 警告）：`Runs/legacy-C23-sem-bootstrap5000-20260920.log`

## 状态声明

C23 属于历史 legacy 分析入口；按 `RESULTS_REBUILT.md` 声明，SEM 推断已被撤回，不构成当前有效结论。
本次运行仅为历史审查目的按用户要求执行，结果保留在独立目录中，不自动提升为当前结果，不得与
`Codes/reproduce.py` 产出的当前结果混用。
