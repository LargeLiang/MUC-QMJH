"""
C19_pure_format_effect

控制混淆变量后估计格式偏好的净效应，并量化效应衰减。

功能：
- 加载全量数据计算全局模型统计量（复用 C18 共享基础设施）
- 拟合四层嵌套逻辑回归（F0→F3），追踪标题/列表/粗体密度差的净效应
- 输出净效应汇总表、OR 热图和方法报告

数据流向：
    optimized_data.parquet 与 C13 子集 parquet → 配对特征构造与嵌套格式模型拟合
    → Tables/T06_pure_format_net_effect_summary.csv
    + Reports/R17_pure_format_effect_report.txt
    + Pictures/P09_format_net_effect_heatmaps.png
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import TwoSlopeNorm

from accessor import (
    SUBSET_LABELS_EN,
    get_analysis_subset_paths,
    get_path,
)
from C18_pure_length_effect import (
    CRITERIA_COLS,
    FORMAT_DENSITY_LABELS,
    FORMAT_DENSITY_VARS,
    TASK_TYPE_COLS,
    _active,
    _configure_plot_style,
    _extract_coef,
    _fit_logit,
    _standardize,
    _wald_partial_r,
    build_model_stats,
    load_data_global,
    load_subset,
    validate_model_confounding,
)
from table_export_utils import export_table_bundle

FORMAT_EFFECT_TABLE_FILE   = "T06_pure_format_net_effect_summary.csv"
FORMAT_EFFECT_PICTURE_FILE = "P09_format_net_effect_heatmaps.png"

# 格式标签英译（仅用于图表列名显示）
_FORMAT_AXIS_LABELS: dict[str, str] = {
    "标题密度差": "Header density",
    "列表密度差": "List density",
    "粗体密度差": "Bold density",
}


# 格式嵌套模型（F0 → F3）


def run_nested_models_format(
    df: pd.DataFrame,
    subset_name: str,
    report_lines: list[str],
) -> dict | None:
    """
    四层嵌套逻辑回归（格式系列）：追踪三个格式密度差值变量的净效应。

    z_token_diff_ab 在所有层次中作为固定协变量（控制长度-格式共线性）；
    三个格式密度变量同时入模型（各系数代表控制其他格式类型后的净边际效应）。

    层次：
      F0：z_token_diff_ab + [z_header/list/bold_density_diff]   [粗格式效应，控制长度]
      F1：F0 + 任务类型 + z_user_tokens + z_turns               [+问题特征]
      F2：F1 + criteria（7维）                                   [+问题复杂度]
      F3：F2 + z_ability_diff + z_verbosity_diff + z_format_tendency_diff  [+模型层]

    格式模型最低样本量门槛为 100（多变量场景下奇异矩阵风险更高）。

    返回值：
      包含三个密度变量在各层 β/OR/混淆比例的摘要字典，或 None（样本量不足）
    """
    MIN_N = 100

    avail_criteria = [c for c in CRITERIA_COLS if c in df.columns]
    s = _standardize(
        df.dropna(subset=["token_diff_ab", "winner_a"] + FORMAT_DENSITY_VARS).copy()
    )

    if len(s) < MIN_N:
        report_lines.append(
            f"  【{subset_name}】格式模型样本量不足（n={len(s)} < {MIN_N}），跳过。"
        )
        return None

    y      = s["winner_a"]
    y_mean = float(y.mean())
    n      = len(s)

    z_tok      = "_z_token_diff_ab"
    z_fmts_all = [f"_z_{v}" for v in FORMAT_DENSITY_VARS]
    z_fmts     = _active(s, z_fmts_all)

    task_bool = _active(s, TASK_TYPE_COLS)
    prompt_z  = _active(s, ["_z_user_tokens", "_z_turns"])
    crit_cols = _active(s, avail_criteria)
    model_z   = _active(s, ["_z_ability_diff", "_z_verbosity_diff", "_z_format_tendency_diff"])

    # z_token_diff_ab 在所有层次中作为固定协变量
    base = [z_tok] + z_fmts
    F0   = s[base]
    F1   = s[base + task_bool + prompt_z]
    F2   = pd.concat([F1, s[crit_cols]], axis=1) if crit_cols else F1
    F3   = pd.concat([F2, s[model_z]],   axis=1) if model_z   else F2

    fits = {lbl: _fit_logit(X.dropna(axis=1), y)
            for lbl, X in [("F0", F0), ("F1", F1), ("F2", F2), ("F3", F3)]}

    # 写报告块（每层输出三个密度变量的系数行）
    w = 80
    report_lines += [
        "",
        f"【{subset_name}】  n = {n:,}  ( y_mean = {y_mean:.4f} )",
        "-" * w,
    ]

    LAYER_LABELS = {
        "F0": "F0（粗格式效应，控长度）",
        "F1": "F1（+问题特征）",
        "F2": "F2（+criteria）",
        "F3": "F3（+模型能力+风格）",
    }

    or_f0: dict[str, float] = {}
    or_f3: dict[str, float] = {}

    for lbl, desc in LAYER_LABELS.items():
        f   = fits[lbl]
        r2  = f["pseudo_r2"] if f else np.nan
        report_lines.append(f"  {desc:<32}  ( R² = {r2:.4f} )")
        for var in FORMAT_DENSITY_VARS:
            z_var          = f"_z_{var}"
            coef, se, pval = _extract_coef(f, z_var)
            or_v           = float(np.exp(coef)) if not np.isnan(coef) else np.nan
            wald_r         = _wald_partial_r(coef, se, n)
            sig            = "*" if pval < 0.05 else " "
            label          = FORMAT_DENSITY_LABELS[var]
            report_lines.append(
                f"    {label:<10}  β={coef:>8.4f}  SE={se:>6.4f}"
                f"  p={pval:>10.4e}{sig}  OR={or_v:>6.4f}  Wald_r={wald_r:>7.4f}"
            )
            if lbl == "F0":
                or_f0[var] = or_v
            if lbl == "F3":
                or_f3[var] = or_v

    # 各变量净效应小结
    report_lines.append("")
    confound_pcts: dict[str, float] = {}
    for var in FORMAT_DENSITY_VARS:
        o0    = or_f0.get(var, np.nan)
        o3    = or_f3.get(var, np.nan)
        label = FORMAT_DENSITY_LABELS[var]
        if not np.isnan(o0) and not np.isnan(o3) and abs(o0 - 1) > 1e-6:
            cp      = (o0 - o3) / (o0 - 1)
            verdict = (
                "真实偏好" if cp < 0.3
                else "部分混淆" if cp < 0.7
                else "主要混淆"
            )
            confound_pcts[var] = cp
            report_lines.append(
                f"  ▶ {label}净 OR = {o3:.4f}，"
                f"混淆比例 = {cp:.2%}  → {verdict}"
            )
        else:
            confound_pcts[var] = np.nan
            report_lines.append(
                f"  ▶ {label}净 OR = {o3:.4f}，混淆比例无法计算"
            )

    return {
        "subset": subset_name, "n": n,
        "or_f0": or_f0, "or_f3": or_f3,
        "confound_pcts": confound_pcts,
        "r2_f0": fits["F0"]["pseudo_r2"] if fits["F0"] else np.nan,
        "r2_f3": fits["F3"]["pseudo_r2"] if fits["F3"] else np.nan,
    }


def _render_format_summary(results: list[dict | None], report_lines: list[str]) -> None:
    """格式净效应跨子集汇总表，按标题密度净 OR 降序排列。"""
    valid = [r for r in results if r is not None]
    if not valid:
        report_lines.append("  无有效结果。")
        return

    valid.sort(
        key=lambda x: x["or_f3"].get("header_density_diff", 0)
        if not np.isnan(x["or_f3"].get("header_density_diff", np.nan)) else 0,
        reverse=True,
    )

    report_lines += [
        "",
        "【格式净效应汇总（按标题密度净 OR 降序）】",
        "=" * 80,
        f"  {'子集':<18}{'n':>8}  "
        f"{'标题OR_粗':>9}{'标题OR_净':>9}{'混淆%':>7}  "
        f"{'列表OR_粗':>9}{'列表OR_净':>9}{'混淆%':>7}  "
        f"{'粗体OR_粗':>9}{'粗体OR_净':>9}{'混淆%':>7}",
        "-" * 80,
    ]
    for r in valid:
        row = f"  {r['subset']:<18}{r['n']:>8,}  "
        for var in FORMAT_DENSITY_VARS:
            o0   = r["or_f0"].get(var, np.nan)
            o3   = r["or_f3"].get(var, np.nan)
            cp   = r["confound_pcts"].get(var, np.nan)
            cp_s = f"{cp:.0%}" if not np.isnan(cp) else " N/A"
            row += f"  {o0:>9.4f}{o3:>9.4f}{cp_s:>7}"
        report_lines.append(row)


def build_format_summary_df(results: list[dict | None]) -> pd.DataFrame:
    """将格式嵌套模型结果展开为长表结构。"""
    rows: list[dict[str, float | str]] = []
    for result in results:
        if result is None:
            continue
        for feature in FORMAT_DENSITY_VARS:
            rows.append({
                "subset": result["subset"],
                "n": result["n"],
                "feature": feature,
                "feature_label": FORMAT_DENSITY_LABELS[feature],
                "or_f0": result["or_f0"].get(feature, np.nan),
                "or_f3": result["or_f3"].get(feature, np.nan),
                "confound_pct": result["confound_pcts"].get(feature, np.nan),
                "r2_f0": result["r2_f0"],
                "r2_f3": result["r2_f3"],
            })
    if not rows:
        return pd.DataFrame()

    summary_df = pd.DataFrame(rows)
    header_df  = summary_df[summary_df["feature"] == "header_density_diff"].copy()
    subset_order = header_df.sort_values("or_f3", ascending=False, na_position="last")["subset"].tolist()
    summary_df["subset"] = pd.Categorical(summary_df["subset"], categories=subset_order, ordered=True)
    return summary_df.sort_values(["subset", "feature"]).reset_index(drop=True)


def plot_format_heatmaps(format_df: pd.DataFrame, picture_path: Path) -> None:
    """绘制格式净效应 OR 与混淆比例热图。"""
    if format_df.empty:
        return

    _configure_plot_style()
    order          = list(dict.fromkeys(format_df["subset"].astype(str).tolist()))
    or_matrix      = format_df.pivot(index="subset", columns="feature_label", values="or_f3").reindex(order)
    confound_matrix = format_df.pivot(index="subset", columns="feature_label", values="confound_pct").reindex(order)
    or_matrix.index      = [SUBSET_LABELS_EN.get(idx, idx) for idx in or_matrix.index]
    confound_matrix.index = [SUBSET_LABELS_EN.get(idx, idx) for idx in confound_matrix.index]
    or_matrix.columns      = [_FORMAT_AXIS_LABELS.get(col, col) for col in or_matrix.columns]
    confound_matrix.columns = [_FORMAT_AXIS_LABELS.get(col, col) for col in confound_matrix.columns]

    fig, axes = plt.subplots(
        1, 2, figsize=(15, max(7, len(or_matrix) * 0.42)), constrained_layout=True
    )

    finite_or = or_matrix.to_numpy(dtype=float)
    finite_or = finite_or[np.isfinite(finite_or)]
    if finite_or.size == 0:
        plt.close(fig)
        return
    norm  = TwoSlopeNorm(vmin=float(finite_or.min()), vcenter=1.0, vmax=float(finite_or.max()))
    im_or = axes[0].imshow(or_matrix.to_numpy(dtype=float), aspect="auto", cmap="RdYlBu_r", norm=norm)
    axes[0].set_title("Net odds ratio (F3)")

    confound_values = confound_matrix.to_numpy(dtype=float)
    finite_confound = confound_values[np.isfinite(confound_values)]
    confound_vmax   = float(np.nanmax(finite_confound)) if finite_confound.size else 1.0
    confound_vmax   = max(confound_vmax, 0.5)
    im_conf = axes[1].imshow(
        confound_values, aspect="auto", cmap="YlOrRd", vmin=0.0, vmax=confound_vmax,
    )
    axes[1].set_title("Confounding share")

    for ax in axes:
        ax.set_xticks(np.arange(len(or_matrix.columns)))
        ax.set_xticklabels(or_matrix.columns)
        ax.set_yticks(np.arange(len(or_matrix.index)))
        ax.set_yticklabels(or_matrix.index)
        ax.tick_params(axis="x", rotation=0)

    for i in range(or_matrix.shape[0]):
        for j in range(or_matrix.shape[1]):
            value = or_matrix.iat[i, j]
            if not np.isnan(value):
                axes[0].text(j, i, f"{value:.2f}", ha="center", va="center", fontsize=9, color="#111827")
            confound = confound_matrix.iat[i, j]
            if not np.isnan(confound):
                axes[1].text(j, i, f"{confound:.0%}", ha="center", va="center", fontsize=9, color="#111827")

    fig.colorbar(im_or,   ax=axes[0], fraction=0.046, pad=0.04)
    fig.colorbar(im_conf, ax=axes[1], fraction=0.046, pad=0.04)
    fig.suptitle("C19 Format Net Effect Overview")
    picture_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(picture_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


# 主流程


def run_pure_format_effect(
    file_path: Path | str | None = None,
    report_dir: Path | str | None = None,
    table_dir: Path | str | None = None,
    picture_dir: Path | str | None = None,
) -> dict[str, Path]:
    """
    主分析函数：加载全量数据 → 计算全局模型统计量 → 逐子集运行格式嵌套逻辑回归 → 写报告。

    参数说明：
    - file_path  : optimized_data.parquet 路径（默认按 CWD 自动定位）
    - report_dir : 报告输出目录（默认 CWD/Reports）
    - table_dir  : 汇总表输出目录（默认 CWD/Tables）
    - picture_dir: 图片输出目录（默认 CWD/Pictures）
    """
    root        = Path.cwd()
    report_path = (
        Path(report_dir) / "R17_pure_format_effect_report.txt"
        if report_dir else get_path("report", "R17_pure_format_effect_report.txt", root)
    )
    table_path = (
        Path(table_dir) / FORMAT_EFFECT_TABLE_FILE
        if table_dir else get_path("table", FORMAT_EFFECT_TABLE_FILE, root)
    )
    picture_path = (
        Path(picture_dir) / FORMAT_EFFECT_PICTURE_FILE
        if picture_dir else get_path("picture", FORMAT_EFFECT_PICTURE_FILE, root)
    )
    subset_paths = get_analysis_subset_paths(root)

    report_lines: list[str] = []

    # 报告头
    report_lines += [
        "=" * 80,
        "格式偏好净效应分析报告（嵌套逻辑回归）",
        "=" * 80,
        "",
        "【分析框架】",
        "  格式系列（F0→F3）：同层次结构；z_token_diff_ab 在所有层次作为固定协变量；",
        "                    格式变量：标题/列表/粗体密度差（均 z 标准化），三变量同入模型。",
        "  混淆比例 = (OR_F0 − OR_F3) / (OR_F0 − 1)",
        "  数据来源：C13 生成的纯净分区子集文件；模型统计量从全量数据统一计算。",
        "",
    ]

    # 步骤 1：加载全量数据（仅用于全局模型统计量计算）
    print("=" * 60)
    print("步骤 1/4：加载全量 optimized_data（仅用于全局模型统计量计算）")
    opt_path  = get_path("optimized", root=root) if file_path is None else Path(file_path)
    df_global = load_data_global(opt_path)
    print(f"  全量有效配对行数：{len(df_global):,}")

    # 步骤 2：计算全局模型统计量
    print("步骤 2/4：计算全局模型统计量（胜率 / 词冗性 / 格式风格）")
    model_stats = build_model_stats(df_global)
    print(f"  模型总数：{len(model_stats)}")
    del df_global  # 释放内存

    report_lines.append("【模型统计量一览（按胜率排序，Top-10）】")
    for name, row in model_stats.sort_values("win_rate", ascending=False).head(10).iterrows():
        report_lines.append(
            f"  {name:<50}  胜率={row['win_rate']:.4f}  "
            f"均长={row['mean_tokens']:>7.1f}  均格式={row['mean_format']:>5.1f}"
        )

    # 步骤 3：前置验证（能力−格式共线性）
    print("步骤 3/4：验证模型能力−长度/格式共线性")
    validate_model_confounding(model_stats, report_lines)

    # 步骤 4：逐子集运行格式嵌套模型
    print("步骤 4/4：逐子集加载 C13 数据并运行格式嵌套模型（F0→F3）")
    fmt_results: list[dict | None] = []
    report_lines += [
        "",
        "=" * 80,
        "【格式净效应 — 各子集嵌套模型分析结果（F0 → F3）】",
        "=" * 80,
    ]
    n_subsets = len(subset_paths)
    for i, (name, path) in enumerate(subset_paths.items(), 1):
        print(f"  {i}/{n_subsets}: {name}（格式）")
        sub_df = load_subset(path, model_stats)
        fmt_results.append(run_nested_models_format(sub_df, name, report_lines))

    # 汇总渲染
    report_lines += ["", "=" * 80]
    _render_format_summary(fmt_results, report_lines)

    # 保存表格与图片
    format_df = build_format_summary_df(fmt_results)
    if not format_df.empty:
        table_path.parent.mkdir(parents=True, exist_ok=True)
        export_table_bundle(format_df, table_path)
        plot_format_heatmaps(format_df, picture_path)

    # 写报告
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"\n报告已写入：{report_path}")
    print("\n任务完成！")
    print("=" * 60)
    return {"report": report_path, "table": table_path, "picture": picture_path}


if __name__ == "__main__":
    run_pure_format_effect()
