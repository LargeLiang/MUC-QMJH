"""
C16_length_test

对优化数据集及各任务类别子集执行长度偏好 Wilcoxon 符号秩检验。

功能：
- 对全量与 16 个纯净分区子集执行长度差值检验
- 输出 Wilcoxon 统计量、Bootstrap 区间和效应量摘要
- 生成汇总表、总览图和文本报告

数据流向：
    optimized_data.parquet 与 C13 子集 parquet → 长度差值检验 → Tables/T03_length_wilcoxon_summary.csv
    + Reports/R13_wilcoxon_length_test_report.txt + Pictures/P06_length_wilcoxon_overview.png
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import wilcoxon
from typing import Dict, List, Optional

from accessor import (
    get_analysis_subset_paths,
    get_path,
    with_length_tokens,
    SUBSET_LABELS_EN)
from table_export_utils import export_table_bundle

# 每个子集有效对数的最小阈值（低于此数则跳过）
MIN_PAIRS = 30

# Bootstrap 置信区间重采样次数
N_BOOTSTRAP = 1000

# 效应量分级阈值（Cohen's 惯例）
EFFECT_THRESHOLDS = [(0.1, "可忽略"), (0.3, "小"), (0.5, "中"), (float("inf"), "大")]

LENGTH_TEST_TABLE_FILE = "T03_length_wilcoxon_summary.csv"
LENGTH_TEST_PICTURE_FILE = "P06_length_wilcoxon_overview.png"

# 核心计算


def _oriented_winner_difference(a_values: np.ndarray,
                                b_values: np.ndarray,
                                winner_values: np.ndarray) -> np.ndarray:
    """按 winner 方向构造获胜方减落败方的差值数组。"""

    return np.where(winner_values == "model_a", a_values - b_values, b_values - a_values)

def _build_diff(df: pd.DataFrame) -> np.ndarray:
    """
    构造 δᵢ = tokens(获胜模型) − tokens(落败模型)。

    排除 winner ∈ {tie, both_bad}，仅保留方向明确的配对。
    """
    if "a_tokens" not in df.columns or "b_tokens" not in df.columns:
        df = with_length_tokens(df)

    mask = df["winner"].isin(["model_a", "model_b"])
    sub = df[mask].copy()
    delta = _oriented_winner_difference(
        sub["a_tokens"].values.astype(np.float64),
        sub["b_tokens"].values.astype(np.float64),
        sub["winner"].values,
    )
    return delta.astype(np.float64)


def _bootstrap_ci(arr: np.ndarray, n_boot: int = N_BOOTSTRAP,
                  rng: Optional[np.random.Generator] = None) -> tuple[float, float]:
    """
    计算中位数的 Bootstrap 百分位置信区间（95%）。

    参数说明：
    - arr：差值数组
    - n_boot：重采样次数
    - rng：随机数生成器（可传入固定 seed，默认新建）

    返回值：
    - (ci_low, ci_high)
    """
    if rng is None:
        rng = np.random.default_rng(42)
    medians = np.array([
        np.median(rng.choice(arr, size=len(arr), replace=True))
        for _ in range(n_boot)
    ])
    return float(np.percentile(medians, 2.5)), float(np.percentile(medians, 97.5))


def _effect_level(r: float) -> str:
    """根据 rank-biserial r 的绝对值返回效应分级标签。"""
    abs_r = abs(r)
    if abs_r < 0.1:
        return "可忽略"
    elif abs_r < 0.3:
        return "小"
    elif abs_r < 0.5:
        return "中"
    else:
        return "大"


def _cohens_d(arr: np.ndarray) -> tuple[float, float]:
    """
    计算 Cohen's d 和 Hedges' g（参数效应量，非正态分布下仅供参考）。

    参数说明：
    - arr：差值数组（含零值）

    返回值：
    - (cohen_d, hedges_g)；非零样本 < 3 时返回 (nan, nan)
    """
    nonzero = arr[arr != 0]
    n = len(nonzero)
    if n < 3:
        return np.nan, np.nan
    d = float(nonzero.mean() / nonzero.std(ddof=1))
    g = d * (1 - 3 / (4 * n - 9))
    return round(d, 4), round(g, 4)


def run_one_subset(label: str, df: pd.DataFrame) -> Optional[Dict]:
    """
    对单个子集执行完整检验流程。

    参数说明：
    - label：子集标签（用于报告显示）
    - df：子集 DataFrame（包含 winner 和 nested metadata，或已解包的 a_tokens、b_tokens 列）

    返回值：
    - 结果字典；若有效对数 < MIN_PAIRS 则返回 None
    """
    delta = _build_diff(df)
    n_pairs = len(delta)

    if n_pairs < MIN_PAIRS:
        print(f"  [{label}] 有效对数 {n_pairs} < {MIN_PAIRS}，跳过")
        return None

    # 排除差值为 0 的对（Wilcoxon 默认行为）
    nonzero = delta[delta != 0]
    n_nonzero = len(nonzero)

    # Wilcoxon 符号秩检验（单侧，H₁: median > 0）
    stat, p_raw = wilcoxon(delta, alternative="greater", zero_method="wilcox")

    # Rank-biserial 相关系数
    # scipy wilcoxon(alternative='greater') 返回负秩和 W⁻
    # 公式：r_rb = 1 - 2W⁻ / (n*(n+1))，此时 r_rb > 0 表示正向效应
    if n_nonzero > 0:
        r_rb = float(1 - 2 * stat / (n_nonzero * (n_nonzero + 1)))
    else:
        r_rb = 0.0

    # 中位差值与 Bootstrap CI
    median_diff = float(np.median(delta))
    ci_low, ci_high = _bootstrap_ci(delta)

    # 胜者更长的统计
    n_longer = int(np.sum(delta > 0))
    pct_longer = n_longer / n_pairs * 100

    cohen_d, hedges_g = _cohens_d(delta)

    result = {
        "label":            label,
        "n_pairs":          n_pairs,
        "n_winner_longer":  n_longer,
        "pct_winner_longer": round(pct_longer, 2),
        "median_diff":      round(median_diff, 1),
        "ci_low":           round(ci_low, 1),
        "ci_high":          round(ci_high, 1),
        "wilcoxon_stat":    float(stat),
        "p_value":          float(p_raw),
        # p_bonferroni 在主函数中填充（需知道 k）
        "p_bonferroni":     None,
        "rank_biserial_r":  round(r_rb, 4),
        "effect_level":     _effect_level(r_rb),
        "cohen_d":          cohen_d,
        "hedges_g":         hedges_g,
        "significant":      None,   # 在主函数中填充
    }
    return result


def _configure_plot_style() -> None:
    """配置论文图表的全局样式。"""
    plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.style.use("seaborn-v0_8-darkgrid")


def build_summary_df(results: List[Dict]) -> pd.DataFrame:
    """将检验结果整理为结构化汇总表。"""
    if not results:
        return pd.DataFrame()
    summary_df = pd.DataFrame(results)
    return summary_df.sort_values("rank_biserial_r", ascending=False, na_position="last").reset_index(drop=True)


def plot_length_overview(summary_df: pd.DataFrame, picture_path: Path) -> None:
    """绘制中位长度差 CI 与 rank-biserial r 的双面板总览图。"""
    if summary_df.empty:
        return

    _configure_plot_style()
    plot_df = summary_df.sort_values("rank_biserial_r", ascending=True).reset_index(drop=True)
    y_pos = np.arange(len(plot_df))
    colors = ["#0f766e" if sig else "#9ca3af" for sig in plot_df["significant"]]
    marker_size = np.clip(np.sqrt(plot_df["n_pairs"]) * 1.6, 36, 180)
    y_labels = plot_df["label"].replace(SUBSET_LABELS_EN)

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(15, max(7, len(plot_df) * 0.42)),
        sharey=True,
        gridspec_kw={"width_ratios": [1.35, 1.0]},
    )

    median_xerr = np.vstack([
        plot_df["median_diff"] - plot_df["ci_low"],
        plot_df["ci_high"] - plot_df["median_diff"],
    ])
    axes[0].errorbar(
        plot_df["median_diff"],
        y_pos,
        xerr=median_xerr,
        fmt="none",
        ecolor="#94a3b8",
        elinewidth=2,
        capsize=3,
        zorder=1,
    )
    axes[0].scatter(plot_df["median_diff"], y_pos, s=marker_size, c=colors, zorder=3)
    axes[0].axvline(0, color="#6b7280", linestyle="--", linewidth=1.2)
    axes[0].set_xlabel("Median length difference (tokens)")
    axes[0].set_title("Bootstrap 95% CI")

    axes[1].barh(y_pos, plot_df["rank_biserial_r"], color=colors, alpha=0.9)
    axes[1].axvline(0, color="#6b7280", linestyle="--", linewidth=1.2)
    axes[1].axvline(0.1, color="#cbd5e1", linestyle=":", linewidth=1.0)
    axes[1].axvline(0.3, color="#cbd5e1", linestyle=":", linewidth=1.0)
    axes[1].axvline(0.5, color="#cbd5e1", linestyle=":", linewidth=1.0)
    axes[1].set_xlabel("rank-biserial r")
    axes[1].set_title("Effect size")

    axes[0].set_yticks(y_pos)
    axes[0].set_yticklabels(y_labels)
    axes[1].set_yticks(y_pos)
    axes[1].tick_params(axis="y", labelleft=False)

    for idx, row in plot_df.iterrows():
        sig_mark = "*" if row["significant"] else ""
        axes[1].text(
            row["rank_biserial_r"] + 0.012,
            idx,
            f"{row['rank_biserial_r']:.2f}{sig_mark}",
            va="center",
            ha="left",
            fontsize=9,
            color="#111827",
        )

    fig.suptitle("C16 Length Preference Overview")
    fig.tight_layout()
    picture_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(picture_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

# 主函数

def run_length_test(data_dir: Path | str | None = None,
                    report_dir: Path | str | None = None,
                    table_dir: Path | str | None = None,
                    picture_dir: Path | str | None = None) -> dict[str, Path] | None:
    """
    对所有预定义子集执行长度偏好 Wilcoxon 符号秩检验并生成报告。

    参数说明：
    - data_dir：子集 parquet 文件目录（默认为 Data/subsets）
    - report_dir：报告保存目录（默认为 Reports）
    - table_dir：汇总表保存目录（默认为 Tables）
    - picture_dir：图片保存目录（默认为 Pictures）

    返回值：
    - 输出文件路径字典；若无有效结果则返回 None
    """

    root = Path.cwd()
    default_subset_paths = get_analysis_subset_paths(root)
    optimized_file_path = get_path("optimized", root=root)

    if data_dir is None:
        subset_paths = default_subset_paths
    else:
        subset_root = Path(data_dir)
        subset_paths = {
            label: optimized_file_path if label == "全量" else subset_root / path.name
            for label, path in default_subset_paths.items()
        }

    if report_dir is None:
        report_dir = get_path("report", "R13_wilcoxon_length_test_report.txt", root).parent
    else:
        report_dir = Path(report_dir)

    if table_dir is None:
        table_path = get_path("table", LENGTH_TEST_TABLE_FILE, root)
    else:
        table_path = Path(table_dir) / LENGTH_TEST_TABLE_FILE

    if picture_dir is None:
        picture_path = get_path("picture", LENGTH_TEST_PICTURE_FILE, root)
    else:
        picture_path = Path(picture_dir) / LENGTH_TEST_PICTURE_FILE

    report_dir.mkdir(parents=True, exist_ok=True)
    table_path.parent.mkdir(parents=True, exist_ok=True)
    picture_path.parent.mkdir(parents=True, exist_ok=True)

    results: List[Dict] = []

    print("=" * 80)
    print("C16 长度偏好 Wilcoxon 符号秩检验")
    print("=" * 80)

    for label, fpath in subset_paths.items():
        if not fpath.exists():
            print(f"  [{label}] 文件不存在，跳过：{fpath}")
            continue

        df = pd.read_parquet(fpath, columns=["winner", "metadata_a", "metadata_b"])
        print(f"\n[{label}]  总行数={len(df):,}  读取完成")

        res = run_one_subset(label, df)
        if res is not None:
            results.append(res)

    if not results:
        print("ERROR: 无有效检验结果，退出。")
        return

    # Bonferroni 校正（k = 实际执行检验的子集数）
    k = len(results)
    for res in results:
        adj_p = min(res["p_value"] * k, 1.0)
        res["p_bonferroni"] = adj_p
        res["significant"] = adj_p < 0.05

    generate_report(results, k, report_dir)
    summary_df = build_summary_df(results)
    export_table_bundle(summary_df, table_path)
    plot_length_overview(summary_df, picture_path)
    return {
        "report": report_dir / "R13_wilcoxon_length_test_report.txt",
        "table": table_path,
        "picture": picture_path,
    }

# 报告生成

def generate_report(results: List[Dict], k: int, report_dir: Path) -> None:
    """生成 R13 Wilcoxon 长度检验报告。"""

    report_path = report_dir / "R13_wilcoxon_length_test_report.txt"

    with open(report_path, "w", encoding="utf-8") as f:

        f.write("=" * 80 + "\n")
        f.write("长度偏好 Wilcoxon 符号秩检验报告\n")
        f.write("=" * 80 + "\n\n")

        # 方法说明
        f.write("【检验方法】\n")
        f.write("  假设：H₀: median(δ)=0  vs  H₁: median(δ)>0（单侧）\n")
        f.write("  δᵢ = tokens(获胜模型) - tokens(落败模型)\n")
        f.write("  排除 winner∈{tie, both_bad}，仅使用方向明确的配对\n")
        f.write(f"  多重比较校正：Bonferroni（k={k} 个子集）\n")
        f.write(f"  效应量：rank-biserial r（W 统计量推导）\n")
        f.write(f"  中位差 CI：Bootstrap 百分位法（{N_BOOTSTRAP} 次重采样，seed=42）\n\n")

        # 效应量分级说明
        f.write("【效应量分级】\n")
        f.write("  |r| < 0.1  可忽略  |  0.1 ≤ |r| < 0.3  小\n")
        f.write("  0.3 ≤ |r| < 0.5  中  |  |r| ≥ 0.5  大\n\n")

        f.write("-" * 80 + "\n\n")

        for res in results:
            sig_tag = "✓ 显著" if res["significant"] else "✗ 不显著"
            f.write(f"【{res['label']}】{sig_tag}\n")
            f.write(f"  有效配对数          : {res['n_pairs']:,}\n")
            f.write(f"  胜者更长的对数       : {res['n_winner_longer']:,}  ({res['pct_winner_longer']}%)\n")
            f.write(f"  中位长度差 (tokens)  : {res['median_diff']:+.1f}  "
                    f"[Bootstrap 95% CI: {res['ci_low']:+.1f}, {res['ci_high']:+.1f}]\n")
            f.write(f"  Wilcoxon W           : {res['wilcoxon_stat']:.1f}\n")
            f.write(f"  p 值（原始）         : {res['p_value']:.4e}\n")
            f.write(f"  p 值（Bonferroni）   : {res['p_bonferroni']:.4e}\n")
            f.write(f"  rank-biserial r      : {res['rank_biserial_r']:.4f}  [{res['effect_level']}效应]\n")
            cd_str = f"{res['cohen_d']:.4f}" if not np.isnan(res['cohen_d']) else "N/A"
            hg_str = f"{res['hedges_g']:.4f}" if not np.isnan(res['hedges_g']) else "N/A"
            f.write(f"  Cohen's d / Hedges' g: {cd_str} / {hg_str}  （参数近似，仅供参考）\n")
            f.write("\n")

        # 汇总表格
        f.write("=" * 80 + "\n")
        f.write("汇总（按 rank-biserial r 排序）\n")
        f.write("=" * 80 + "\n")
        col_w = 16
        header = (f"{'子集':<{col_w}} {'n':>8} {'胜者偏长%':>10} "
                  f"{'中位差':>8} {'p(adj)':>12} {'r_rb':>8} {'d':>8} {'效应':>8} {'显著':>6}")
        f.write(header + "\n")
        f.write("-" * len(header) + "\n")

        for res in sorted(results, key=lambda x: abs(x["rank_biserial_r"]), reverse=True):
            sig_mark = "✓" if res["significant"] else "✗"
            cd_str = f"{res['cohen_d']:.4f}" if not np.isnan(res['cohen_d']) else "N/A"
            row = (f"{res['label']:<{col_w}} {res['n_pairs']:>8,} "
                   f"{res['pct_winner_longer']:>9.1f}% "
                   f"{res['median_diff']:>+8.1f} "
                   f"{res['p_bonferroni']:>12.4e} "
                   f"{res['rank_biserial_r']:>8.4f} "
                   f"{cd_str:>8} "
                   f"{res['effect_level']:>8} "
                   f"{sig_mark:>6}")
            f.write(row + "\n")

        n_sig = sum(1 for r in results if r["significant"])
        f.write(f"\n显著子集数：{n_sig} / {k}（Bonferroni 校正 α=0.05）\n\n")

        f.write("=" * 80 + "\n")
        f.write("报告生成时间: " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        f.write("=" * 80 + "\n")

    print(f"\n报告已保存至: {report_path}")

# 入口

if __name__ == "__main__":
    print("=" * 80)
    print("C16  长度偏好统计检验（Wilcoxon 符号秩 + Bonferroni + rank-biserial r）")
    print("=" * 80 + "\n")

    run_length_test()

    print("\n" + "=" * 80)
    print("任务完成！")
    print("=" * 80)

