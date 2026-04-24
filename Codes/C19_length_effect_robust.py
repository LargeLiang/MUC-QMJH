# -*- coding: utf-8 -*-
"""
长度效应稳健性分析（调整逻辑回归 + IPW）。

研究问题：
  在控制任务类型、问题属性、模型能力与格式风格后，
  “A 是否更长”这一处理变量是否仍然显著提高 A 获胜的概率？

方法说明：
  1. 处理变量：longer_a = 1（a_tokens > b_tokens），0（a_tokens < b_tokens）
  2. 长度平局（a_tokens == b_tokens）直接剔除，避免把 tie 混入对照组
  3. 结果变量：winner_a = 1（model_a 获胜）
  4. 混淆变量：
     - prompt 负荷：user_tokens, turns
     - 任务类型：creative_writing_bool, if_bool, math_bool, code_bool
     - 问题级控制：7 个 criteria
     - 模型级代理：ability_diff, verbosity_diff, format_tendency_diff
     - 格式控制：header/list/bold_density_diff
  5. 稳健性估计：
     - 调整逻辑回归（OR 与 95% CI）
     - IPW ATE（bootstrap 95% CI）

输出：
  - Reports/R17_length_effect_robust_report.txt
  - Tables/T14_length_robust_summary.csv
    - Pictures/P16_length_robust_forest.png
"""

from __future__ import annotations

import argparse
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from statsmodels.tools.sm_exceptions import ConvergenceWarning

from C18_pure_effect import (
    CRITERIA_COLS,
    SUBSET_LABELS_EN,
    TASK_TYPE_COLS,
    build_model_stats,
    get_subset_paths,
    load_data_global,
    load_subset,
)


CONTINUOUS_CONFOUNDERS: list[str] = [
    "user_tokens",
    "turns",
    "ability_diff",
    "verbosity_diff",
    "format_tendency_diff",
    "header_density_diff",
    "list_density_diff",
    "bold_density_diff",
]


def get_report_path(root: Path | str | None = None) -> Path:
    """返回 R17 报告路径。"""
    if root is None:
        root = Path.cwd()
    return Path(root) / "Reports" / "R17_length_effect_robust_report.txt"


def get_table_path(root: Path | str | None = None) -> Path:
    """返回 R17 汇总表路径。"""
    if root is None:
        root = Path.cwd()
    return Path(root) / "Tables" / "T14_length_robust_summary.csv"


def get_picture_path(root: Path | str | None = None) -> Path:
    """返回 R17 森林图路径。"""
    if root is None:
        root = Path.cwd()
    return Path(root) / "Pictures" / "P16_length_robust_forest.png"


def _zscore(series: pd.Series) -> pd.Series:
    """对连续变量做 z 标准化，常数列返回 0。"""
    mu = float(series.mean())
    sigma = float(series.std(ddof=1))
    if sigma <= 0 or np.isnan(sigma):
        return pd.Series(np.zeros(len(series)), index=series.index, dtype=float)
    return ((series - mu) / sigma).astype(float)


def prepare_subset_for_robustness(df: pd.DataFrame) -> pd.DataFrame:
    """
    构造稳健性分析数据表。

    返回值：
    - 剔除长度平局后的子集
    - 新增 longer_a, longer_wins
    - 所有连续混淆变量完成 z 标准化
    """
    s = df.copy()
    s = s[s["token_diff_ab"] != 0].copy()
    s["longer_a"] = (s["token_diff_ab"] > 0).astype(int)
    s["longer_wins"] = (s["longer_a"] == s["winner_a"]).astype(int)

    for col in CONTINUOUS_CONFOUNDERS:
        if col in s.columns:
            s[col] = _zscore(s[col])

    for col in TASK_TYPE_COLS + CRITERIA_COLS + ["winner_a", "longer_a", "longer_wins"]:
        if col in s.columns:
            s[col] = s[col].astype(float)

    return s


def active_confounders(df: pd.DataFrame) -> list[str]:
    """返回当前子集可用且非常数的混淆变量。"""
    candidates = CONTINUOUS_CONFOUNDERS + TASK_TYPE_COLS + CRITERIA_COLS
    return [col for col in candidates if col in df.columns and df[col].nunique(dropna=True) > 1]


def fit_logit_effect(df: pd.DataFrame, predictors: list[str]) -> dict[str, float] | None:
    """
    拟合 winner_a 的逻辑回归并提取 longer_a 的效应量。

    返回值：coef, se, p, OR, OR 95% CI, pseudo_r2。
    """
    if not predictors:
        return None

    X = df[predictors].astype(float)
    y = df["winner_a"].astype(float)
    X = sm.add_constant(X, has_constant="add")
    model = sm.Logit(y, X)
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=ConvergenceWarning)
            warnings.filterwarnings("ignore", category=RuntimeWarning)
            result = model.fit(disp=0, maxiter=300)
    except Exception:
        return None

    coef = float(result.params.get("longer_a", np.nan))
    se = float(result.bse.get("longer_a", np.nan))
    pval = float(result.pvalues.get("longer_a", np.nan))
    ci_low = coef - 1.96 * se
    ci_high = coef + 1.96 * se
    pseudo_r2 = 1 - result.llf / result.llnull if result.llnull != 0 else np.nan
    return {
        "coef": coef,
        "se": se,
        "p": pval,
        "or": float(np.exp(coef)),
        "or_ci_low": float(np.exp(ci_low)),
        "or_ci_high": float(np.exp(ci_high)),
        "pseudo_r2": float(pseudo_r2),
    }


def fit_propensity_scores(
    df: pd.DataFrame,
    confounders: list[str],
) -> tuple[np.ndarray, np.ndarray] | None:
    """拟合 longer_a 的倾向得分模型并返回标准化后的倾向得分。"""
    if not confounders:
        return None

    X = df[confounders].astype(float)
    t = df["longer_a"].astype(int)
    if t.nunique() < 2:
        return None

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = LogisticRegression(max_iter=1000, solver="lbfgs")
    model.fit(X_scaled, t)
    pscore = model.predict_proba(X_scaled)[:, 1]
    pscore = np.clip(pscore, 0.01, 0.99)
    return pscore, X_scaled


def compute_ipw_ate(
    df: pd.DataFrame,
    confounders: list[str],
) -> dict[str, float] | None:
    """计算稳定化 IPW ATE。"""
    fitted = fit_propensity_scores(df, confounders)
    if fitted is None:
        return None

    pscore, _ = fitted
    t = df["longer_a"].to_numpy(dtype=float)
    y = df["winner_a"].to_numpy(dtype=float)
    treat_rate = float(t.mean())

    weight = np.where(t == 1, treat_rate / pscore, (1 - treat_rate) / (1 - pscore))
    treated_mask = t == 1
    control_mask = t == 0
    if treated_mask.sum() == 0 or control_mask.sum() == 0:
        return None

    treated_mean = float(np.average(y[treated_mask], weights=weight[treated_mask]))
    control_mean = float(np.average(y[control_mask], weights=weight[control_mask]))
    ess = float((weight.sum() ** 2) / np.square(weight).sum())
    return {
        "treated_mean": treated_mean,
        "control_mean": control_mean,
        "ate": treated_mean - control_mean,
        "ess": ess,
        "ps_min": float(pscore.min()),
        "ps_max": float(pscore.max()),
    }


def bootstrap_ipw_ci(
    df: pd.DataFrame,
    confounders: list[str],
    n_boot: int = 30,
    seed: int = 42,
) -> tuple[float, float, int]:
    """为 IPW ATE 提供 bootstrap 95% CI。"""
    rng = np.random.default_rng(seed)
    values: list[float] = []
    for _ in range(n_boot):
        sample = df.sample(
            n=len(df),
            replace=True,
            random_state=int(rng.integers(0, 2**32 - 1)),
        )
        res = compute_ipw_ate(sample, confounders)
        if res is not None and not np.isnan(res["ate"]):
            values.append(float(res["ate"]))

    if not values:
        return np.nan, np.nan, 0
    series = pd.Series(values)
    return float(series.quantile(0.025)), float(series.quantile(0.975)), int(series.shape[0])


def analyze_subset(
    subset_name: str,
    df: pd.DataFrame,
    bootstrap_n: int,
    seed: int,
) -> tuple[list[str], dict[str, float] | None]:
    """分析单个子集并返回报告文本块与汇总行。"""
    lines: list[str] = []
    s = prepare_subset_for_robustness(df)
    n = len(s)
    if n < 100:
        lines.append(f"【{subset_name}】样本量不足（n={n} < 100），跳过。")
        return lines, None

    confounders = active_confounders(s)
    crude = fit_logit_effect(s, ["longer_a"])
    adjusted = fit_logit_effect(s, ["longer_a"] + confounders)
    ipw = compute_ipw_ate(s, confounders)
    ci_low, ci_high, boot_ok = bootstrap_ipw_ci(s, confounders, n_boot=bootstrap_n, seed=seed)

    lines.append("")
    lines.append("-" * 80)
    lines.append(f"【{subset_name}】n = {n:,}")
    lines.append(f"  更长一侧获胜比例：{s['longer_wins'].mean():.4f}")
    lines.append(f"  A 更长比例：{s['longer_a'].mean():.4f}")
    lines.append(f"  可用混淆变量数：{len(confounders)}")

    if crude is not None:
        lines.append(
            "  粗模型："
            f"OR={crude['or']:.4f} "
            f"95% CI [{crude['or_ci_low']:.4f}, {crude['or_ci_high']:.4f}] "
            f"p={crude['p']:.4g} R²={crude['pseudo_r2']:.4f}"
        )
    else:
        lines.append("  粗模型：拟合失败。")

    if adjusted is not None:
        lines.append(
            "  调整模型："
            f"OR={adjusted['or']:.4f} "
            f"95% CI [{adjusted['or_ci_low']:.4f}, {adjusted['or_ci_high']:.4f}] "
            f"p={adjusted['p']:.4g} R²={adjusted['pseudo_r2']:.4f}"
        )
    else:
        lines.append("  调整模型：拟合失败。")

    if ipw is not None:
        lines.append(
            "  IPW ATE："
            f"{ipw['ate']:.4f} "
            f"95% CI [{ci_low:.4f}, {ci_high:.4f}] "
            f"ESS={ipw['ess']:.1f} bootstrap_success={boot_ok}/{bootstrap_n}"
        )
        lines.append(
            f"  倾向得分范围：[{ipw['ps_min']:.4f}, {ipw['ps_max']:.4f}]"
        )
    else:
        lines.append("  IPW：估计失败。")

    summary_row = {
        "subset": subset_name,
        "n": n,
        "longer_win_rate": float(s["longer_wins"].mean()),
        "a_longer_rate": float(s["longer_a"].mean()),
        "crude_or": crude["or"] if crude else np.nan,
        "crude_or_ci_low": crude["or_ci_low"] if crude else np.nan,
        "crude_or_ci_high": crude["or_ci_high"] if crude else np.nan,
        "crude_p": crude["p"] if crude else np.nan,
        "adjusted_or": adjusted["or"] if adjusted else np.nan,
        "adjusted_or_ci_low": adjusted["or_ci_low"] if adjusted else np.nan,
        "adjusted_or_ci_high": adjusted["or_ci_high"] if adjusted else np.nan,
        "adjusted_p": adjusted["p"] if adjusted else np.nan,
        "ipw_ate": ipw["ate"] if ipw else np.nan,
        "ipw_ci_low": ci_low,
        "ipw_ci_high": ci_high,
        "ipw_ess": ipw["ess"] if ipw else np.nan,
        "bootstrap_success": boot_ok,
    }
    return lines, summary_row


def _configure_plot_style() -> None:
    """配置论文图表的全局样式。"""
    plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.style.use("seaborn-v0_8-darkgrid")


def plot_length_robust_forest(summary_df: pd.DataFrame, picture_path: Path) -> None:
    """绘制调整 OR 与 IPW ATE 的双面板森林图。"""
    if summary_df.empty:
        return

    plot_df = summary_df.dropna(subset=["adjusted_or", "ipw_ate"]).copy()
    if plot_df.empty:
        return

    _configure_plot_style()
    plot_df = plot_df.sort_values("adjusted_or", ascending=True).reset_index(drop=True)
    y_pos = np.arange(len(plot_df))
    colors = ["#0f766e" if subset == "全量" else "#2563eb" for subset in plot_df["subset"]]
    y_labels = plot_df["subset"].replace(SUBSET_LABELS_EN)

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(15, max(7, len(plot_df) * 0.42)),
        sharey=True,
        gridspec_kw={"width_ratios": [1.15, 1.0]},
    )

    or_xerr = np.vstack([
        plot_df["adjusted_or"] - plot_df["adjusted_or_ci_low"],
        plot_df["adjusted_or_ci_high"] - plot_df["adjusted_or"],
    ])
    axes[0].errorbar(
        plot_df["adjusted_or"],
        y_pos,
        xerr=or_xerr,
        fmt="none",
        ecolor="#94a3b8",
        elinewidth=2,
        capsize=3,
        zorder=1,
    )
    axes[0].scatter(plot_df["adjusted_or"], y_pos, s=65, c=colors, zorder=3)
    axes[0].axvline(1.0, color="#6b7280", linestyle="--", linewidth=1.2)
    axes[0].set_xlabel("Adjusted odds ratio")
    axes[0].set_title("Adjusted logistic model")

    ate_xerr = np.vstack([
        plot_df["ipw_ate"] - plot_df["ipw_ci_low"],
        plot_df["ipw_ci_high"] - plot_df["ipw_ate"],
    ])
    axes[1].errorbar(
        plot_df["ipw_ate"],
        y_pos,
        xerr=ate_xerr,
        fmt="none",
        ecolor="#cbd5e1",
        elinewidth=2,
        capsize=3,
        zorder=1,
    )
    axes[1].scatter(plot_df["ipw_ate"], y_pos, s=65, c=colors, zorder=3)
    axes[1].axvline(0.0, color="#6b7280", linestyle="--", linewidth=1.2)
    axes[1].set_xlabel("IPW ATE")
    axes[1].set_title("Stabilized IPW")

    axes[0].set_yticks(y_pos)
    axes[0].set_yticklabels(y_labels)
    axes[1].set_yticks(y_pos)
    axes[1].tick_params(axis="y", labelleft=False)

    fig.suptitle("C19 Length Robustness")
    fig.tight_layout()
    picture_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(picture_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def run_length_effect_robust(
    file_path: Path | str | None = None,
    report_dir: Path | str | None = None,
    table_dir: Path | str | None = None,
    picture_dir: Path | str | None = None,
    bootstrap_n: int = 30,
    seed: int = 42,
) -> dict[str, Path]:
    """执行完整的 R17 稳健性分析。"""
    root = Path.cwd()
    if report_dir is None:
        report_path = get_report_path(root)
    else:
        report_path = Path(report_dir) / "R17_length_effect_robust_report.txt"

    if table_dir is None:
        table_path = get_table_path(root)
    else:
        table_path = Path(table_dir) / "T14_length_robust_summary.csv"

    if picture_dir is None:
        picture_path = get_picture_path(root)
    else:
        picture_path = Path(picture_dir) / "P16_length_robust_forest.png"

    report_path.parent.mkdir(parents=True, exist_ok=True)
    table_path.parent.mkdir(parents=True, exist_ok=True)
    picture_path.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("1/3 读取全量数据并构造模型级统计量")
    print("=" * 80)
    global_path = file_path if file_path is not None else None
    df_global = load_data_global(global_path)
    model_stats = build_model_stats(df_global)
    subset_paths = get_subset_paths(root)

    report_lines: list[str] = []
    report_lines.append("=" * 80)
    report_lines.append("长度效应稳健性分析报告（R17）")
    report_lines.append("=" * 80)
    report_lines.append("")
    report_lines.append("【方法】")
    report_lines.append("  - 处理变量：longer_a（A 是否更长）")
    report_lines.append("  - 结果变量：winner_a（A 是否获胜）")
    report_lines.append("  - 稳健性方法：调整逻辑回归 + 稳定化 IPW")
    report_lines.append("  - 长度平局行已剔除")
    report_lines.append("")

    summary_rows: list[dict[str, float]] = []

    print("=" * 80)
    print("2/3 按子集执行稳健性分析")
    print("=" * 80)
    for subset_name, path in subset_paths.items():
        print(f"分析子集：{subset_name}")
        subset_df = load_subset(path, model_stats)
        block_lines, summary_row = analyze_subset(
            subset_name=subset_name,
            df=subset_df,
            bootstrap_n=bootstrap_n,
            seed=seed,
        )
        report_lines.extend(block_lines)
        if summary_row is not None:
            summary_rows.append(summary_row)

    summary_df = pd.DataFrame(summary_rows)
    if not summary_df.empty:
        summary_df = summary_df.sort_values("adjusted_or", ascending=False)
        summary_df.to_csv(table_path, index=False, encoding="utf-8-sig")
        plot_length_robust_forest(summary_df, picture_path)

    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("3/3 汇总结论")
    report_lines.append("=" * 80)
    if not summary_df.empty:
        full_row = summary_df[summary_df["subset"] == "全量"]
        if not full_row.empty:
            row = full_row.iloc[0]
            report_lines.append(
                f"全量样本：调整 OR={row['adjusted_or']:.4f}，"
                f"IPW ATE={row['ipw_ate']:.4f}，"
                f"95% CI [{row['ipw_ci_low']:.4f}, {row['ipw_ci_high']:.4f}]"
            )
        report_lines.append("解释：若调整 OR 仍 > 1 且 IPW CI 不跨 0，则说明长度优势在处理效应视角下依旧稳健。")
    else:
        report_lines.append("无可用子集结果。")

    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("任务完成！")
    report_lines.append("=" * 80)
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    print(report_path.read_text(encoding="utf-8")[:1200])
    return {"report": report_path, "table": table_path, "picture": picture_path}


def main() -> None:
    """命令行入口。"""
    parser = argparse.ArgumentParser(description="运行长度效应稳健性分析（R17）。")
    parser.add_argument("--bootstrap", type=int, default=30, help="IPW bootstrap 次数，默认 30")
    parser.add_argument("--seed", type=int, default=42, help="随机种子")
    args = parser.parse_args()

    run_length_effect_robust(
        bootstrap_n=args.bootstrap,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()