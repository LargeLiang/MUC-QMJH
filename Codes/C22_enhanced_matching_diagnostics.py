"""
C22_enhanced_matching_diagnostics

评估长度处理变量的匹配质量，并输出匹配后诊断结果。

功能：
- 复用 C20 的处理定义和倾向得分估计逻辑
- 计算匹配前后平衡性指标与匹配后 Wilcoxon 结果
- 输出诊断表、总览图和文本报告

数据流向：
    optimized_data.parquet 与 C13 子集 parquet → 倾向得分匹配与平衡性诊断 → Tables/T09_matching_summary.csv 与 Tables/T10_matching_balance.csv
    + Reports/R20_enhanced_diagnostics_report.txt + Pictures/P12_matching_diagnostics_overview.png
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon
from sklearn.neighbors import NearestNeighbors

from accessor import get_analysis_subset_paths, get_path, SUBSET_LABELS_EN
from C18_pure_length_effect import build_model_stats, load_data_global, load_subset
from C20_length_effect_robust import active_confounders, fit_propensity_scores, prepare_subset_for_robustness
from table_export_utils import export_table_bundle


MATCHING_TABLE_FILES = {
    "summary": "T09_matching_summary.csv",
    "balance": "T10_matching_balance.csv",
}

MATCHING_PICTURE_FILE = "P12_matching_diagnostics_overview.png"

def standardized_mean_difference(
    treated: pd.Series,
    control: pd.Series,
) -> float:
    """计算 treated 与 control 的标准化均值差（SMD）。"""
    treated = treated.astype(float)
    control = control.astype(float)
    mean_diff = float(treated.mean() - control.mean())
    var_t = float(treated.var(ddof=1)) if treated.shape[0] > 1 else 0.0
    var_c = float(control.var(ddof=1)) if control.shape[0] > 1 else 0.0
    pooled_sd = np.sqrt((var_t + var_c) / 2)
    if pooled_sd <= 0 or np.isnan(pooled_sd):
        return 0.0
    return mean_diff / pooled_sd


def build_balance_rows(
    subset_name: str,
    treated_before: pd.DataFrame,
    control_before: pd.DataFrame,
    treated_after: pd.DataFrame,
    control_after: pd.DataFrame,
    confounders: list[str],
) -> list[dict[str, float | str]]:
    """生成匹配前后平衡性表。"""
    rows: list[dict[str, float | str]] = []
    for stage, treated_df, control_df in [
        ("before", treated_before, control_before),
        ("after", treated_after, control_after),
    ]:
        for col in confounders:
            rows.append({
                "subset": subset_name,
                "stage": stage,
                "variable": col,
                "treated_mean": float(treated_df[col].mean()),
                "control_mean": float(control_df[col].mean()),
                "smd": float(standardized_mean_difference(treated_df[col], control_df[col])),
            })
    return rows


def match_with_caliper(df: pd.DataFrame, pscore: np.ndarray) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, float]] | None:
    """
    基于 logit(PS) 做 1:1 最近邻匹配（有放回）。

    caliper 使用 0.2 * SD(logit_ps) 的常见经验规则。
    """
    s = df.copy().reset_index(drop=True)
    s["pscore"] = pscore
    s["logit_ps"] = np.log(s["pscore"] / (1 - s["pscore"]))

    treated = s[s["longer_a"] == 1].reset_index(drop=True)
    control = s[s["longer_a"] == 0].reset_index(drop=True)
    if treated.empty or control.empty:
        return None

    logit_sd = float(s["logit_ps"].std(ddof=1)) if len(s) > 1 else 0.0
    caliper = 0.2 * logit_sd if logit_sd > 0 else 0.2

    nbrs = NearestNeighbors(n_neighbors=1)
    nbrs.fit(control[["logit_ps"]].to_numpy())
    dist, idx = nbrs.kneighbors(treated[["logit_ps"]].to_numpy())

    matched_pairs: list[tuple[int, int, float]] = []
    for i, d in enumerate(dist[:, 0]):
        if d <= caliper:
            matched_pairs.append((i, int(idx[i, 0]), float(d)))

    if not matched_pairs:
        return None

    treated_idx = [i for i, _, _ in matched_pairs]
    control_idx = [j for _, j, _ in matched_pairs]
    treated_matched = treated.iloc[treated_idx].reset_index(drop=True)
    control_matched = control.iloc[control_idx].reset_index(drop=True)

    overlap_low = max(float(treated["pscore"].min()), float(control["pscore"].min()))
    overlap_high = min(float(treated["pscore"].max()), float(control["pscore"].max()))
    common_support_share = float(((s["pscore"] >= overlap_low) & (s["pscore"] <= overlap_high)).mean())

    diag = {
        "caliper": caliper,
        "treated_n": int(treated.shape[0]),
        "control_n": int(control.shape[0]),
        "matched_pairs": int(len(matched_pairs)),
        "match_rate": float(len(matched_pairs) / treated.shape[0]),
        "mean_distance": float(np.mean([d for _, _, d in matched_pairs])),
        "max_distance": float(np.max([d for _, _, d in matched_pairs])),
        "overlap_low": overlap_low,
        "overlap_high": overlap_high,
        "common_support_share": common_support_share,
    }
    return treated_matched, control_matched, diag


def paired_wilcoxon_test(
    treated_matched: pd.DataFrame,
    control_matched: pd.DataFrame,
) -> tuple[float, float]:
    """对匹配后 treated/control 的 winner_a 做配对 Wilcoxon 检验。"""
    try:
        stat, pval = wilcoxon(
            treated_matched["winner_a"].to_numpy(dtype=float),
            control_matched["winner_a"].to_numpy(dtype=float),
            alternative="greater",
            zero_method="zsplit",
        )
        return float(stat), float(pval)
    except Exception:
        return np.nan, np.nan


def diagnose_subset(
    subset_name: str,
    subset_df: pd.DataFrame,
) -> tuple[list[str], dict[str, float] | None, list[dict[str, float | str]]]:
    """诊断单个子集的匹配质量并返回报告块、汇总行和平衡性表。"""
    lines: list[str] = []
    balance_rows: list[dict[str, float | str]] = []

    s = prepare_subset_for_robustness(subset_df)
    if len(s) < 100:
        lines.append(f"【{subset_name}】样本量不足（n={len(s)} < 100），跳过。")
        return lines, None, balance_rows

    confounders = active_confounders(s)
    fitted = fit_propensity_scores(s, confounders)
    if fitted is None:
        lines.append(f"【{subset_name}】倾向得分模型失败，跳过。")
        return lines, None, balance_rows

    pscore, _ = fitted
    matched = match_with_caliper(s, pscore)
    if matched is None:
        lines.append(f"【{subset_name}】无有效匹配样本，跳过。")
        return lines, None, balance_rows

    treated_matched, control_matched, diag = matched
    treated_before = s[s["longer_a"] == 1].reset_index(drop=True)
    control_before = s[s["longer_a"] == 0].reset_index(drop=True)
    balance_rows = build_balance_rows(
        subset_name=subset_name,
        treated_before=treated_before,
        control_before=control_before,
        treated_after=treated_matched,
        control_after=control_matched,
        confounders=confounders,
    )
    balance_df = pd.DataFrame(balance_rows)

    before_abs = balance_df[balance_df["stage"] == "before"]["smd"].abs()
    after_abs = balance_df[balance_df["stage"] == "after"]["smd"].abs()
    matched_ate = float(treated_matched["winner_a"].mean() - control_matched["winner_a"].mean())
    w_stat, w_p = paired_wilcoxon_test(treated_matched, control_matched)

    lines.append("")
    lines.append("-" * 80)
    lines.append(f"【{subset_name}】n = {len(s):,}")
    lines.append(f"  匹配对数：{diag['matched_pairs']}（treated match rate={diag['match_rate']:.2%}）")
    lines.append(f"  caliper(logit_ps)：{diag['caliper']:.6f}")
    lines.append(
        f"  公共支持区间：[{diag['overlap_low']:.4f}, {diag['overlap_high']:.4f}]，"
        f"覆盖率={diag['common_support_share']:.2%}"
    )
    lines.append(
        f"  平衡性改善：max|SMD| {before_abs.max():.4f} → {after_abs.max():.4f}，"
        f"mean|SMD| {before_abs.mean():.4f} → {after_abs.mean():.4f}"
    )
    lines.append(
        f"  匹配后 ATE：{matched_ate:.4f}；配对 Wilcoxon p={w_p:.4g}"
    )

    summary_row = {
        "subset": subset_name,
        "n": int(len(s)),
        "treated_n": diag["treated_n"],
        "control_n": diag["control_n"],
        "matched_pairs": diag["matched_pairs"],
        "match_rate": diag["match_rate"],
        "caliper": diag["caliper"],
        "mean_distance": diag["mean_distance"],
        "max_distance": diag["max_distance"],
        "overlap_low": diag["overlap_low"],
        "overlap_high": diag["overlap_high"],
        "common_support_share": diag["common_support_share"],
        "max_abs_smd_before": float(before_abs.max()),
        "max_abs_smd_after": float(after_abs.max()),
        "mean_abs_smd_before": float(before_abs.mean()),
        "mean_abs_smd_after": float(after_abs.mean()),
        "matched_ate": matched_ate,
        "wilcoxon_stat": w_stat,
        "wilcoxon_p": w_p,
    }
    return lines, summary_row, balance_rows


def _configure_plot_style() -> None:
    """配置论文图表的全局样式。"""
    plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.style.use("seaborn-v0_8-darkgrid")


def plot_matching_diagnostics(
    summary_df: pd.DataFrame,
    balance_df: pd.DataFrame,
    picture_path: Path,
) -> None:
    """绘制匹配平衡性改善图与全量样本 love plot。"""
    if summary_df.empty or balance_df.empty:
        return

    _configure_plot_style()
    fig, axes = plt.subplots(1, 2, figsize=(16, 9), gridspec_kw={"width_ratios": [1.0, 1.1]})

    overview_df = summary_df.sort_values("mean_abs_smd_after", ascending=True).reset_index(drop=True)
    y_pos = np.arange(len(overview_df))
    overview_labels = overview_df["subset"].replace(SUBSET_LABELS_EN)
    axes[0].hlines(y_pos, overview_df["mean_abs_smd_after"], overview_df["mean_abs_smd_before"], color="#94a3b8", linewidth=2)
    axes[0].scatter(overview_df["mean_abs_smd_before"], y_pos, color="#d97706", s=55, label="Before")
    axes[0].scatter(overview_df["mean_abs_smd_after"], y_pos, color="#0f766e", s=55, label="After")
    axes[0].axvline(0.1, color="#6b7280", linestyle="--", linewidth=1.2)
    axes[0].set_yticks(y_pos)
    axes[0].set_yticklabels(overview_labels)
    axes[0].set_xlabel("Mean |SMD|")
    axes[0].set_title("Balance improvement by subset")
    axes[0].legend(loc="lower right")

    full_df = balance_df[balance_df["subset"] == "全量"].copy()
    if full_df.empty:
        full_df = balance_df.copy()
        full_df = full_df[full_df["subset"] == full_df["subset"].iloc[0]]
    before_df = full_df[full_df["stage"] == "before"].copy()
    after_df = full_df[full_df["stage"] == "after"].copy()
    merge_df = before_df.merge(after_df, on=["subset", "variable"], suffixes=("_before", "_after"))
    merge_df["abs_smd_before"] = merge_df["smd_before"].abs()
    merge_df["abs_smd_after"] = merge_df["smd_after"].abs()
    merge_df = merge_df.sort_values("abs_smd_before", ascending=True).reset_index(drop=True)
    love_y = np.arange(len(merge_df))
    axes[1].scatter(merge_df["abs_smd_before"], love_y, color="#d97706", s=52, label="Before")
    axes[1].scatter(merge_df["abs_smd_after"], love_y, color="#0f766e", s=52, label="After")
    axes[1].hlines(love_y, merge_df["abs_smd_after"], merge_df["abs_smd_before"], color="#cbd5e1", linewidth=1.8)
    axes[1].axvline(0.1, color="#6b7280", linestyle="--", linewidth=1.2)
    axes[1].set_yticks(love_y)
    axes[1].set_yticklabels(merge_df["variable"])
    axes[1].set_xlabel("|SMD|")
    axes[1].set_title("Full-sample Love plot")
    axes[1].legend(loc="lower right")

    fig.suptitle("C21 Matching Diagnostics Overview")
    fig.tight_layout()
    picture_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(picture_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def run_matching_diagnostics(
    file_path: Path | str | None = None,
    report_dir: Path | str | None = None,
    table_dir: Path | str | None = None,
    picture_dir: Path | str | None = None,
) -> dict[str, Path]:
    """执行完整的 R19 匹配诊断流程。"""
    root = Path.cwd()
    if report_dir is None:
        report_path = get_path("report", "R20_enhanced_diagnostics_report.txt", root)
    else:
        report_path = Path(report_dir) / "R20_enhanced_diagnostics_report.txt"

    if table_dir is None:
        table_paths = {
            name: get_path("table", file_name, root)
            for name, file_name in MATCHING_TABLE_FILES.items()
        }
    else:
        table_root = Path(table_dir)
        table_paths = {
            "summary": table_root / MATCHING_TABLE_FILES["summary"],
            "balance": table_root / MATCHING_TABLE_FILES["balance"],
        }

    if picture_dir is None:
        picture_path = get_path("picture", MATCHING_PICTURE_FILE, root)
    else:
        picture_path = Path(picture_dir) / MATCHING_PICTURE_FILE

    report_path.parent.mkdir(parents=True, exist_ok=True)
    for path in table_paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    picture_path.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("1/3 读取全量数据并准备子集")
    print("=" * 80)
    global_path = file_path if file_path is not None else None
    df_global = load_data_global(global_path)
    model_stats = build_model_stats(df_global)
    subset_paths = get_analysis_subset_paths(root)

    report_lines: list[str] = []
    report_lines.append("=" * 80)
    report_lines.append("匹配诊断报告（R19）")
    report_lines.append("=" * 80)
    report_lines.append("")
    report_lines.append("【诊断标准】")
    report_lines.append("  - 处理变量与混淆变量口径完全复用 C19")
    report_lines.append("  - 平衡性指标：标准化均值差 SMD，经验阈值 |SMD| < 0.1")
    report_lines.append("  - 匹配：1:1 最近邻，有放回，caliper = 0.2 * SD(logit_ps)")
    report_lines.append("  - 显著性：匹配后 winner_a 的配对 Wilcoxon 检验")
    report_lines.append("")

    summary_rows: list[dict[str, float]] = []
    all_balance_rows: list[dict[str, float | str]] = []

    print("=" * 80)
    print("2/3 执行匹配诊断")
    print("=" * 80)
    for subset_name, path in subset_paths.items():
        print(f"诊断子集：{subset_name}")
        subset_df = load_subset(path, model_stats)
        block_lines, summary_row, balance_rows = diagnose_subset(subset_name, subset_df)
        report_lines.extend(block_lines)
        if summary_row is not None:
            summary_rows.append(summary_row)
        all_balance_rows.extend(balance_rows)

    summary_df = pd.DataFrame(summary_rows)
    balance_df = pd.DataFrame(all_balance_rows)
    if not summary_df.empty:
        summary_df = summary_df.sort_values("mean_abs_smd_after")
        export_table_bundle(summary_df, table_paths["summary"])
    if not balance_df.empty:
        export_table_bundle(balance_df, table_paths["balance"])
    if not summary_df.empty and not balance_df.empty:
        plot_matching_diagnostics(summary_df, balance_df, picture_path)

    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("3/3 汇总结论")
    report_lines.append("=" * 80)
    if not summary_df.empty:
        full_row = summary_df[summary_df["subset"] == "全量"]
        if not full_row.empty:
            row = full_row.iloc[0]
            report_lines.append(
                f"全量样本：匹配后 max|SMD|={row['max_abs_smd_after']:.4f}，"
                f"mean|SMD|={row['mean_abs_smd_after']:.4f}，ATE={row['matched_ate']:.4f}，"
                f"Wilcoxon p={row['wilcoxon_p']:.4g}"
            )
        report_lines.append("解释：若匹配后 |SMD| 明显下降且 Wilcoxon 仍显著，则说明处理效应结论不依赖原始样本失衡。")
    else:
        report_lines.append("无可用子集结果。")

    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("任务完成！")
    report_lines.append("=" * 80)
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    print(report_path.read_text(encoding="utf-8")[:1200])
    return {
        "report": report_path,
        "summary_table": table_paths["summary"],
        "balance_table": table_paths["balance"],
        "picture": picture_path,
    }


def main() -> None:
    """命令行入口。"""
    parser = argparse.ArgumentParser(description="运行匹配诊断分析（R19）。")
    parser.parse_args()
    run_matching_diagnostics()


if __name__ == "__main__":
    main()

