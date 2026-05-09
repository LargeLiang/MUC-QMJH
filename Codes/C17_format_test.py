"""
C17_format_test

对优化数据集及各任务类别子集执行格式偏好检验。

功能：
- 对标题、列表、粗体三类格式特征执行 Wilcoxon 检验
- 辅助计算格式密度检验和存在性卡方检验
- 生成汇总表、热力图和文本报告

数据流向：
    optimized_data.parquet 与 C13 子集 parquet → 格式计数与密度检验 → Tables/T19_format_test_summary.csv
    + Reports/R14_format_test_report.txt + Pictures/P13_format_effect_heatmaps.png
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import wilcoxon, chi2_contingency
from typing import Dict, List, Optional, Tuple

from accessor import (
    get_analysis_subset_paths,
    get_data_path,
    get_output_path,
    oriented_winner_density_difference,
    oriented_winner_difference,
    safe_int_count,
    with_flat_analysis_columns,
)

SUBSET_LABELS_EN = {
    "全量": "Full",
    "无类别": "No category",
    "仅创意写作": "CW only",
    "仅指令遵循": "IF only",
    "仅数学": "Math only",
    "仅代码": "Code only",
    "创意+指令": "CW + IF",
    "创意+数学": "CW + Math",
    "创意+代码": "CW + Code",
    "指令+数学": "IF + Math",
    "指令+代码": "IF + Code",
    "数学+代码": "Math + Code",
    "创意+指令+数学": "CW + IF + Math",
    "创意+指令+代码": "CW + IF + Code",
    "创意+数学+代码": "CW + Math + Code",
    "指令+数学+代码": "IF + Math + Code",
    "四类全含": "All four",
}

FEATURES = ["header", "list", "bold"]
MIN_PAIRS = 30
N_BOOTSTRAP = 1000
BONFERRONI_K = len(FEATURES)


def _build_paired(df: pd.DataFrame, feature: str
                  ) -> Tuple[np.ndarray, np.ndarray]:
    """构造格式计数差值和格式密度差值数组。"""
    a_col = f"a_{feature}_count"
    b_col = f"b_{feature}_count"

    a_cnt = df[a_col].apply(safe_int_count).values.astype(np.float64)
    b_cnt = df[b_col].apply(safe_int_count).values.astype(np.float64)
    a_tok = df["a_tokens"].values.astype(np.float64)
    b_tok = df["b_tokens"].values.astype(np.float64)

    count_diff = oriented_winner_difference(a_cnt, b_cnt, df["winner"].values)
    density_diff = oriented_winner_density_difference(
        a_cnt,
        b_cnt,
        a_tok,
        b_tok,
        df["winner"].values,
    )

    return count_diff, density_diff


def _bootstrap_ci(arr: np.ndarray, n_boot: int = N_BOOTSTRAP,
                  rng: Optional[np.random.Generator] = None
                  ) -> Tuple[float, float]:
    """计算中位数的 Bootstrap 百分位 95% CI。"""
    if rng is None:
        rng = np.random.default_rng(42)
    medians = np.array([
        np.median(rng.choice(arr, size=len(arr), replace=True))
        for _ in range(n_boot)
    ])
    return float(np.percentile(medians, 2.5)), float(np.percentile(medians, 97.5))


def _effect_level(r: float) -> str:
    abs_r = abs(r)
    if abs_r < 0.1:
        return "可忽略"
    elif abs_r < 0.3:
        return "小"
    elif abs_r < 0.5:
        return "中"
    return "大"


def _wilcoxon_one(arr: np.ndarray) -> Tuple[float, float, float]:
    """
    执行 Wilcoxon 检验，返回 (W, p_raw, r_rb)。

    scipy wilcoxon(alternative='greater') 返回负秩和 W⁻，
    故 r_rb = 1 - 2W⁻/(n*(n+1))。
    """
    nonzero = arr[arr != 0]
    if len(nonzero) == 0:
        return np.nan, np.nan, np.nan
    stat, p = wilcoxon(nonzero, alternative="greater", zero_method="wilcox")
    n = len(nonzero)
    r_rb = float(1 - 2 * stat / (n * (n + 1)))
    return float(stat), float(p), r_rb


def _cohens_d(arr: np.ndarray) -> Tuple[float, float]:
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


def _chisquare_presence(df: pd.DataFrame, feature: str) -> Optional[float]:
    """对"胜者有格式 vs 败者有格式"构造列联表并执行卡方检验，返回 p 值。"""
    a_col = f"a_{feature}_count"
    b_col = f"b_{feature}_count"
    a_cnt = df[a_col].apply(safe_int_count)
    b_cnt = df[b_col].apply(safe_int_count)
    winner_is_a = (df["winner"] == "model_a").values
    win_has = np.where(winner_is_a, a_cnt > 0, b_cnt > 0).astype(int)
    los_has = np.where(winner_is_a, b_cnt > 0, a_cnt > 0).astype(int)
    ct = pd.crosstab(pd.Series(los_has, name="loser_has"),
                     pd.Series(win_has, name="winner_has"))
    if ct.shape != (2, 2):
        return None
    try:
        _, p, _, _ = chi2_contingency(ct)
        return float(p)
    except Exception:
        return None


def run_one_subset(label: str, df: pd.DataFrame) -> Optional[Dict]:
    """
    对单个子集执行全部格式偏好检验。

    参数说明：
    - label：子集标签
    - df：已过滤（只含 model_a/model_b winner）的子集

    返回值：
    - 结果字典；样本不足时返回 None
    """
    df = with_flat_analysis_columns(df)

    n_total = len(df)
    if n_total < MIN_PAIRS:
        print(f"  [{label}] 有效对数 {n_total} < {MIN_PAIRS}，跳过")
        return None

    rng = np.random.default_rng(42)
    feature_results: List[Dict] = []

    for feat in FEATURES:
        count_diff, density_diff = _build_paired(df, feat)

        stat, p_raw, r_rb = _wilcoxon_one(count_diff)
        if np.isnan(p_raw):
            continue

        p_adj = min(p_raw * BONFERRONI_K, 1.0)
        median_diff = float(np.median(count_diff))
        ci_low, ci_high = _bootstrap_ci(count_diff, rng=rng)
        n_more = int(np.sum(count_diff > 0))
        pct_more = n_more / n_total * 100

        _, p_den, _ = _wilcoxon_one(density_diff)
        median_den = float(np.median(density_diff))

        p_chi = _chisquare_presence(df, feat)
        cohen_d, hedges_g = _cohens_d(count_diff)

        feature_results.append({
            "feature":             feat,
            "n_pairs":             n_total,
            "n_winner_more":       n_more,
            "pct_winner_more":     round(pct_more, 2),
            "median_diff":         round(median_diff, 3),
            "ci_low":              round(ci_low, 3),
            "ci_high":             round(ci_high, 3),
            "wilcoxon_stat":       stat,
            "p_value":             p_raw,
            "p_bonferroni":        round(p_adj, 6),
            "rank_biserial_r":     round(r_rb, 4),
            "effect_level":        _effect_level(r_rb),
            "cohen_d":             cohen_d,
            "hedges_g":            hedges_g,
            "significant":         p_adj < 0.05,
            "density_median_diff": round(median_den, 6),
            "density_p_value":     float(p_den) if not np.isnan(p_den) else None,
            "chisq_presence_p":    round(p_chi, 6) if p_chi is not None else None,
        })

    if not feature_results:
        return None

    return {"label": label, "n_pairs": n_total, "features": feature_results}


def _configure_plot_style() -> None:
    """配置论文图表的全局样式。"""
    plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.style.use("seaborn-v0_8-darkgrid")


def build_summary_df(all_results: List[Dict]) -> pd.DataFrame:
    """将全部子集的格式检验结果展开为长表。"""
    rows: List[Dict] = []
    for res in all_results:
        for feature_result in res["features"]:
            rows.append({
                "subset": res["label"],
                "n_pairs": res["n_pairs"],
                **feature_result,
            })
    if not rows:
        return pd.DataFrame()
    summary_df = pd.DataFrame(rows)
    subset_order = (
        summary_df.groupby("subset")["rank_biserial_r"].apply(lambda s: s.abs().mean())
        .sort_values(ascending=False)
        .index
        .tolist()
    )
    summary_df["subset"] = pd.Categorical(summary_df["subset"], categories=subset_order, ordered=True)
    return summary_df.sort_values(["subset", "feature"]).reset_index(drop=True)


def plot_format_heatmaps(summary_df: pd.DataFrame, picture_path: Path) -> None:
    """绘制格式偏好效应热图与密度检验热图。"""
    if summary_df.empty:
        return

    _configure_plot_style()
    feature_labels = {"header": "Header", "list": "List", "bold": "Bold"}
    order = list(dict.fromkeys(summary_df["subset"].astype(str).tolist()))
    r_matrix = (
        summary_df.assign(feature_label=summary_df["feature"].map(feature_labels))
        .pivot(index="subset", columns="feature_label", values="rank_biserial_r")
        .reindex(order)
    )
    density_matrix = (
        summary_df.assign(feature_label=summary_df["feature"].map(feature_labels))
        .pivot(index="subset", columns="feature_label", values="density_p_value")
        .reindex(order)
    )

    fig, axes = plt.subplots(1, 2, figsize=(15, max(7, len(r_matrix) * 0.42)), constrained_layout=True)
    im_r = axes[0].imshow(r_matrix.to_numpy(dtype=float), aspect="auto", cmap="RdBu_r", vmin=-1, vmax=1)
    axes[0].set_title("Rank-biserial r")

    density_values = density_matrix.to_numpy(dtype=float)
    density_strength = -np.log10(np.clip(density_values, 1e-12, 1.0))
    im_density = axes[1].imshow(density_strength, aspect="auto", cmap="YlGnBu")
    axes[1].set_title("Density evidence (-log10 p)")

    for ax in axes:
        ax.set_xticks(np.arange(len(r_matrix.columns)))
        ax.set_xticklabels(r_matrix.columns)
        ax.set_yticks(np.arange(len(r_matrix.index)))
        ax.set_yticklabels([SUBSET_LABELS_EN.get(idx, idx) for idx in r_matrix.index])

    for i in range(r_matrix.shape[0]):
        for j in range(r_matrix.shape[1]):
            r_value = r_matrix.iat[i, j]
            if not np.isnan(r_value):
                cell_row = summary_df[
                    (summary_df["subset"].astype(str) == r_matrix.index[i])
                    & (summary_df["feature"].map(feature_labels) == r_matrix.columns[j])
                ]
                sig_mark = "*" if (not cell_row.empty and bool(cell_row.iloc[0]["significant"])) else ""
                axes[0].text(j, i, f"{r_value:.2f}{sig_mark}", ha="center", va="center", fontsize=9, color="#111827")
            density_p = density_matrix.iat[i, j]
            if not np.isnan(density_p):
                axes[1].text(j, i, f"{density_p:.3f}", ha="center", va="center", fontsize=8.5, color="#111827")

    fig.colorbar(im_r, ax=axes[0], fraction=0.046, pad=0.04)
    fig.colorbar(im_density, ax=axes[1], fraction=0.046, pad=0.04)
    fig.suptitle("C17 Format Preference Overview")
    picture_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(picture_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def run_format_test(data_dir: Path | str | None = None,
                    report_dir: Path | str | None = None,
                    table_dir: Path | str | None = None,
                    picture_dir: Path | str | None = None) -> dict[str, Path] | None:
    """
    对所有预定义子集执行格式偏好检验并生成报告。

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
    optimized_file_path = get_data_path("optimized", root=root)

    if data_dir is None:
        subset_paths = default_subset_paths
    else:
        subset_root = Path(data_dir)
        subset_paths = {
            label: optimized_file_path if label == "全量" else subset_root / path.name
            for label, path in default_subset_paths.items()
        }

    if report_dir is None:
        report_dir = get_output_path("report", "R14_format_test_report.txt", root).parent
    else:
        report_dir = Path(report_dir)

    if table_dir is None:
        table_path = get_output_path("table", "T19_format_test_summary.csv", root)
    else:
        table_path = Path(table_dir) / "T19_format_test_summary.csv"

    if picture_dir is None:
        picture_path = get_output_path("picture", "P13_format_effect_heatmaps.png", root)
    else:
        picture_path = Path(picture_dir) / "P13_format_effect_heatmaps.png"

    report_dir.mkdir(parents=True, exist_ok=True)
    table_path.parent.mkdir(parents=True, exist_ok=True)
    picture_path.parent.mkdir(parents=True, exist_ok=True)

    all_results: List[Dict] = []

    print("=" * 80)
    print("C17 格式偏好 Wilcoxon 符号秩检验（含密度辅助 + 卡方存在性）")
    print("=" * 80)

    for label, fpath in subset_paths.items():
        if not fpath.exists():
            print(f"  [{label}] 文件不存在，跳过：{fpath}")
            continue

        need_cols = ["winner", "metadata_a", "metadata_b"]
        df_raw = pd.read_parquet(fpath, columns=need_cols)
        df = df_raw[df_raw["winner"].isin(["model_a", "model_b"])].copy()
        print(f"\n[{label}]  总行数={len(df_raw):,}  有效对数={len(df):,}")

        res = run_one_subset(label, df)
        if res is not None:
            all_results.append(res)

    if not all_results:
        print("ERROR: 无有效检验结果，退出。")
        return

    generate_report(all_results, report_dir)
    summary_df = build_summary_df(all_results)
    summary_df.to_csv(table_path, index=False, encoding="utf-8-sig")
    plot_format_heatmaps(summary_df, picture_path)
    return {
        "report": report_dir / "R14_format_test_report.txt",
        "table": table_path,
        "picture": picture_path,
    }


def generate_report(all_results: List[Dict], report_dir: Path) -> None:
    """生成 R14 格式检验报告。"""

    report_path = report_dir / "R14_format_test_report.txt"

    with open(report_path, "w", encoding="utf-8") as f:

        f.write("=" * 80 + "\n")
        f.write("格式偏好 Wilcoxon 符号秩检验报告\n")
        f.write("=" * 80 + "\n\n")

        f.write("【检验方法】\n")
        f.write("  假设：H₀: median(Δ)=0  vs  H₁: median(Δ)>0（单侧）\n")
        f.write("  Δᵢ = count_f(获胜模型) - count_f(落败模型)\n")
        f.write("  排除 winner∈{tie, both_bad}\n")
        f.write(f"  多重比较：子集内 Bonferroni（k={BONFERRONI_K} 个格式特征）\n")
        f.write("  辅助：格式密度差值 Wilcoxon（Δ_density，不纳入校正）\n")
        f.write("  效应量：rank-biserial r = 1 - 2W⁻/(n*(n+1))\n")
        f.write(f"  Bootstrap CI：{N_BOOTSTRAP} 次重采样（百分位法，seed=42）\n\n")

        f.write("【格式密度定义】\n")
        f.write("  density = count_f / (tokens + 1)\n\n")

        f.write("-" * 80 + "\n\n")

        for res in all_results:
            f.write(f"【{res['label']}】  有效配对数 = {res['n_pairs']:,}\n")
            f.write("-" * 60 + "\n")

            for fr in res["features"]:
                feat_name = {"header": "标题", "list": "列表", "bold": "粗体"}[fr["feature"]]
                sig_tag = "✓ 显著" if fr["significant"] else "✗ 不显著"
                f.write(f"\n  [{feat_name}（{fr['feature']}）]  {sig_tag}\n")
                f.write(f"    胜者格式更多比例    : {fr['pct_winner_more']}%"
                        f"  ({fr['n_winner_more']:,} / {fr['n_pairs']:,})\n")
                f.write(f"    中位计数差          : {fr['median_diff']:+.3f}"
                        f"  [Bootstrap 95% CI: {fr['ci_low']:+.3f}, {fr['ci_high']:+.3f}]\n")
                f.write(f"    Wilcoxon W          : {fr['wilcoxon_stat']:.1f}\n")
                f.write(f"    p 值（原始）        : {fr['p_value']:.4e}\n")
                f.write(f"    p 值（Bonferroni）  : {fr['p_bonferroni']:.4e}\n")
                f.write(f"    rank-biserial r     : {fr['rank_biserial_r']:.4f}"
                        f"  [{fr['effect_level']}效应]\n")
                cd_str = f"{fr['cohen_d']:.4f}" if not np.isnan(fr['cohen_d']) else "N/A"
                hg_str = f"{fr['hedges_g']:.4f}" if not np.isnan(fr['hedges_g']) else "N/A"
                f.write(f"    Cohen's d / Hedges' g: {cd_str} / {hg_str}  （参数近似，仅供参考）\n")
                f.write(f"    密度差中位数        : {fr['density_median_diff']:+.6f}\n")
                den_str = (f"{fr['density_p_value']:.4e}"
                           if fr["density_p_value"] is not None else "N/A")
                f.write(f"    密度检验 p（辅助）  : {den_str}\n")
                if fr["chisq_presence_p"] is not None:
                    f.write(f"    卡方存在性 p        : {fr['chisq_presence_p']:.4e}\n")

            f.write("\n")

        # 汇总表
        f.write("=" * 80 + "\n")
        f.write("汇总（全部子集 × 全部特征，按 |r_rb| 倒序）\n")
        f.write("=" * 80 + "\n")

        rows = []
        for res in all_results:
            for fr in res["features"]:
                rows.append({
                    "子集":   res["label"],
                    "特征":   fr["feature"],
                    "n":      res["n_pairs"],
                    "胜者%":  fr["pct_winner_more"],
                    "中位差": fr["median_diff"],
                    "p(adj)": fr["p_bonferroni"],
                    "r_rb":   fr["rank_biserial_r"],
                    "d":      fr["cohen_d"],
                    "效应":   fr["effect_level"],
                    "显著":   "✓" if fr["significant"] else "✗",
                    "密度p":  fr["density_p_value"] if fr["density_p_value"] is not None else float("nan"),
                })

        rows_sorted = sorted(rows, key=lambda x: abs(x["r_rb"]), reverse=True)

        hdr = (f"{'子集':<14} {'特征':<8} {'n':>8} {'胜者%':>8} "
               f"{'中位差':>8} {'p(adj)':>12} {'r_rb':>8} {'d':>8} {'效应':>6} {'显著':>4} {'密度p':>12}")
        f.write(hdr + "\n")
        f.write("-" * len(hdr) + "\n")
        for r in rows_sorted:
            den_str = f"{r['密度p']:.4e}" if not np.isnan(r["密度p"]) else "N/A"
            cd_str  = f"{r['d']:.4f}" if not np.isnan(r["d"]) else "N/A"
            f.write(
                f"{r['子集']:<14} {r['特征']:<8} {r['n']:>8,} "
                f"{r['胜者%']:>7.1f}% {r['中位差']:>+8.3f} "
                f"{r['p(adj)']:>12.4e} {r['r_rb']:>8.4f} "
                f"{cd_str:>8} {r['效应']:>6} {r['显著']:>4} {den_str:>12}\n"
            )

        n_sig = sum(1 for r in rows if r["显著"] == "✓")
        f.write(f"\n显著结果数：{n_sig} / {len(rows)}（Bonferroni 校正 k=3，α=0.05）\n\n")

        f.write("=" * 80 + "\n")
        f.write("报告生成时间: " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        f.write("=" * 80 + "\n")

    print(f"\n报告已保存至: {report_path}")


if __name__ == "__main__":
    print("=" * 80)
    print("C17  格式偏好统计检验（Wilcoxon + 密度辅助 + 卡方存在性）")
    print("=" * 80 + "\n")

    run_format_test()

    print("\n" + "=" * 80)
    print("任务完成！")
    print("=" * 80)
