# 大修稿 v2

本稿另起于 2026-09-21；原 LaTeX、旧 PDF 和当前统计主流程均未覆盖。

## 文件

- `manuscript.tex`：七节完整正文，中英文摘要、数学模型、5 张表、2 张图和参考文献；已增加探索性路径分析。
- `../../output/pdf/数学的实践与认识_大修稿_v2.pdf`：可直接阅读的编译稿（以仓库根目录 output/pdf 为准）。
- `build_audit.py`：从冻结数据生成新增分层统计和图形。
- `assets/audit_strata.csv`：三类长度层的真实样本统计。
- `assets/audit_manifest.json`：新增分析输入、SHA-256、阈值和解释范围。

## 修订内容

1. 原 11 节重组为 7 节，聚焦“配对统计模型—关联证据—偏好数据审计”。删除教学式背景与重复研究假设。
2. 使用 integrated-20260920 的样本与统计结果，退出旧 IPW、PSM、SEM 及纯效应、机制识别叙事；按后续修订要求，用当前样本重估并保留观测变量 SEM 探索性路径分析。
3. 主模型与当前代码一致：长度对数比、每千 token 密度差、子集内标准化、模型身份对比项、HC0 和 Holm 校正。
4. 明确格式指标来自上游元数据，当前代码没有独立重做 Markdown 识别；提示词属性不是回答质量评分。
5. 新增无方向长度比 R 的三层审计示例：R≤1.25、1.25<R≤2、R>2，保留全部 108,154 条记录统计评价状态。
6. 用真实分层结果支撑抽样方案。300 条复核预算、争议比例估计公式为设计建议，没有进行人工复核或证明效率改善。
7. 缩减并核验直接相关文献来源，修正格式论文为 ACL 2025 正式版本。正文保留标准编号引用与可访问出处。

## 数值依据

| 正文内容 | 来源 |
| --- | --- |
| 样本筛选、标签分布 | Reports/integrated-20260920/R04_analysis_report.md、RESULTS_REBUILT.md |
| 表2配对结果 | Tables/integrated-20260920/T02_paired_tests.csv |
| 表3及图1回归结果 | Tables/integrated-20260920/T03_adjusted_associations.csv |
| 标准差及单位解释 | Tables/integrated-20260920/T03_01_scaling_full.csv |
| 表4、图2及粗体交叉描述 | draft_v2/assets/audit_strata.csv，由 build_audit.py 本次新增 |

## 复现

在仓库根目录，用已有分析依赖运行：

```powershell
python '基于大语言模型输出文本的选择偏好研究/draft_v2/build_audit.py'
```

进入本目录后：

```powershell
New-Item -ItemType Directory -Force build
xelatex -interaction=nonstopmode -halt-on-error -output-directory=build manuscript.tex
xelatex -interaction=nonstopmode -halt-on-error -output-directory=build manuscript.tex
```

PDF 使用 Windows 中文字体和 XeLaTeX；属于便于审阅的版式，不冒充期刊官方模板。

## 投稿前仍需完成

- 主要研究补强：独立内容质量复核；重复提示词/用户聚类、非线性及极端长度敏感性检查。现稿已如实写入限制，不将这些工作写为已完成。
- 第6节是数据审计应用示例，阈值为事后解释性分层，不是预注册或已验证最优阈值。
- 需要依据期刊正式要求进一步处理体例、篇幅和中英文作者信息。本次不代为投稿。
- 原稿作者列表为“梁斯祯”，通信信息中为“梁斯桢”；本稿沿用作者列表，未擅自判断哪一个字正确。基金信息沿用原稿，通信作者与邮箱应在作者确认后补回。
- 本稿不以常规统计模型为原创数学方法。若目标审稿要求更强的方法或应用贡献，应优先完善独立复核验证。

## 已核验的文献入口

- https://aclanthology.org/2024.acl-long.99/
- https://arxiv.org/abs/2404.04475
- https://aclanthology.org/2025.acl-long.1308/
- https://arxiv.org/abs/2403.04132
- https://huggingface.co/datasets/lmarena-ai/arena-human-preference-140k
- https://academic.oup.com/biomet/article-abstract/39/3-4/324/326091
- https://www.jstor.org/stable/4615733 （网页全文访问受限，列为标准文献入口）

## 原六节版交付检查（下列 PDF 检查仅对应增加路径分析之前）

- XeLaTeX 两遍编译完成，PDF 为 9 页，包含 6 节、4 表、2 图。
- 最终编译日志没有 Overfull、未定义引用、缺字或 LaTeX 错误；个别 Underfull 为行内疏排提示，已在页面中检查。
- 全部 9 页已渲染并检查，未见遮挡、越界、图表裁切或缺失公式。
- 新分层记录数合计为 108,154，明确胜负数合计为 78,959，与冻结数据一致；比例均从相应分母计算。
- 数学模型和主结果沿用当前已存在产物，未重拟合或覆盖当前结果指针；新增分析仅为可复现的描述分层。


## 2026-09-21 后续修订：保留 SEM 探索

- 新第5节为“探索性路径分析”，审计应用和结论顺延至第6、7节；摘要、关键词、引言与结论同步补充。
- 分析报告见 `../../Revision/exploratory_sem/README.md`，完整结果、协方差和追踪清单保存在同目录。
- 复现：仓库根目录运行 `python Revision/exploratory_paths.py`。
- 已实际完成全量、英语、单轮三组拟合，验证结果方程复现冻结主结果。路径乘积使用 50,000 次联合正态参数模拟区间，不称 Bootstrap 或因果中介效应。
- 本次已更新 LaTeX 源码；先前 `output/pdf/数学的实践与认识_大修稿_v2.pdf` 尚未重新编译，不含新增路径分析。此前九页 PDF 的视觉检查不适用于修订后源码。
