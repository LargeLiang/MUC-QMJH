"""
C20_format_effect_robust

评估格式密度处理变量在控制混淆因素后的稳健效应。

功能：
- 构造标题、粗体和列表三类格式处理变量
- 结合调整逻辑回归与稳定化 IPW 估计格式效应
- 输出稳健性汇总表、森林图和文本报告

数据流向：
    optimized_data.parquet 与 C13 子集 parquet → 格式稳健性估计 → Tables/T15_format_robust_summary.csv
    + Reports/R18_format_effect_robust_report.txt + Pictures/P17_format_robust_forest.png
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

from accessor import get_analysis_subset_paths, get_output_path
from C18_pure_effect import (
    CRITERIA_COLS,
    FORMAT_DENSITY_VARS,
    TASK_TYPE_COLS,
    build_model_stats,
    load_data_global,
    load_subset,
)
from stats_utils import active_nonconstant_columns, zscore_series


FORMAT_FEATURES: list[dict[str, str | bool]] = [
    {
        "column": "header_density_diff",
        "label": "标题密度",
        "short": "header",
        "role": "主分析",
    },
    {
        "column": "bold_density_diff",
        "label": "粗体密度",
        "short": "bold",
        "role": "主分析",
    },
    {
        "column": "list_density_diff",
        "label": "列表密度",
        "short": "list",
        "role": "敏感性分析",
    },
]

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

BASE_CONTINUOUS_CONFOUNDERS: list[str] = [
    "user_tokens",
    "turns",
    "ability_diff",
    "verbosity_diff",
    "format_tendency_diff",
    "token_diff_ab",
    "header_density_diff",
    "list_density_diff",
    "bold_density_diff",
]

def prepare_subset_for_feature(df: pd.DataFrame, feature_col: str) -> pd.DataFrame:
    """
    构造单个格式特征的稳健性分析数据表。

    参数说明：
    - df：包含配对差值特征的子集数据框
    - feature_col：当前分析的格式密度差列名

    返回值：
    - 剔除该格式差值为 0 的配对
    - 新增 treatment_a 和 treatment_wins
    - 所有连续混淆变量完成 z 标准化
    """
    s = df.copy()
    s = s[s[feature_col] != 0].copy()
    s["treatment_a"] = (s[feature_col] > 0).astype(int)
    s["treatment_wins"] = (s["treatment_a"] == s["winner_a"]).astype(int)

    continuous_cols = [col for col in BASE_CONTINUOUS_CONFOUNDERS if col in s.columns]
    for col in continuous_cols:
        s[col] = zscore_series(s[col])

    for col in TASK_TYPE_COLS + CRITERIA_COLS + ["winner_a", "treatment_a", "treatment_wins"]:
        if col in s.columns:
            s[col] = s[col].astype(float)

    return s


def active_confounders(df: pd.DataFrame, feature_col: str) -> list[str]:
    """返回当前格式特征可用且非常数的混淆变量。"""
    continuous = [col for col in BASE_CONTINUOUS_CONFOUNDERS if col != feature_col]
    candidates = continuous + TASK_TYPE_COLS + CRITERIA_COLS
    return active_nonconstant_columns(df, candidates)


def fit_logit_effect(df: pd.DataFrame, treatment_col: str, predictors: list[str]) -> dict[str, float] | None:
    """
    拟合 winner_a 的逻辑回归并提取处理变量效应量。

    参数说明：
    - df：稳健性分析数据表
    - treatment_col：处理变量列名
    - predictors：回归自变量列表

    返回值：
    - 包含 coef、se、p、OR、OR 95% CI 和 pseudo_r2 的字典；失败时返回 None
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

    coef = float(result.params.get(treatment_col, np.nan))
    se = float(result.bse.get(treatment_col, np.nan))
    pval = float(result.pvalues.get(treatment_col, np.nan))
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


def fit_propensity_scores(df: pd.DataFrame, treatment_col: str, confounders: list[str]) -> np.ndarray | None:
    """拟合 treatment_a 的倾向得分模型。"""
    if not confounders:
        return None

    X = df[confounders].astype(float)
    t = df[treatment_col].astype(int)
    if t.nunique() < 2:
        return None

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = LogisticRegression(max_iter=1000, solver="lbfgs")
    model.fit(X_scaled, t)
    pscore = model.predict_proba(X_scaled)[:, 1]
    return np.clip(pscore, 0.01, 0.99)


def compute_ipw_ate(df: pd.DataFrame, treatment_col: str, confounders: list[str]) -> dict[str, float] | None:
    """计算稳定化 IPW ATE。"""
    pscore = fit_propensity_scores(df, treatment_col, confounders)
    if pscore is None:
        return None

    t = df[treatment_col].to_numpy(dtype=float)
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
    treatment_col: str,
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
        res = compute_ipw_ate(sample, treatment_col, confounders)
        if res is not None and not np.isnan(res["ate"]):
            values.append(float(res["ate"]))

    if not values:
        return np.nan, np.nan, 0
    series = pd.Series(values)
    return float(series.quantile(0.025)), float(series.quantile(0.975)), int(series.shape[0])


def analyze_feature_subset(
    feature_cfg: dict[str, str | bool],
    subset_name: str,
    df: pd.DataFrame,
    bootstrap_n: int,
    seed: int,
) -> tuple[list[str], dict[str, float | str] | None]:
    """分析单个格式特征在单个子集中的稳健性表现。"""
    feature_col = str(feature_cfg["column"])
    feature_label = str(feature_cfg["label"])
    role = str(feature_cfg["role"])

    lines: list[str] = []
    s = prepare_subset_for_feature(df, feature_col)
    n = len(s)
    if n < 100:
        lines.append(f"【{subset_name} - {feature_label}】样本量不足（n={n} < 100），跳过。")
        return lines, None

    confounders = active_confounders(s, feature_col)
    crude = fit_logit_effect(s, "treatment_a", ["treatment_a"])
    adjusted = fit_logit_effect(s, "treatment_a", ["treatment_a"] + confounders)
    ipw = compute_ipw_ate(s, "treatment_a", confounders)
    ci_low, ci_high, boot_ok = bootstrap_ipw_ci(s, "treatment_a", confounders, n_boot=bootstrap_n, seed=seed)

    lines.append("")
    lines.append("-" * 80)
    lines.append(f"【{subset_name} - {feature_label}（{role}）】n = {n:,}")
    lines.append(f"  处理定义：A 的{feature_label}更高（{feature_col} > 0）")
    lines.append(f"  格式优势一侧获胜比例：{s['treatment_wins'].mean():.4f}")
    lines.append(f"  A 侧格式优势比例：{s['treatment_a'].mean():.4f}")
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

    summary_row: dict[str, float | str] = {
        "feature": feature_label,
        "feature_column": feature_col,
        "role": role,
        "subset": subset_name,
        "n": n,
        "format_win_rate": float(s["treatment_wins"].mean()),
        "a_treatment_rate": float(s["treatment_a"].mean()),
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


def plot_format_robust_forest(summary_df: pd.DataFrame, picture_path: Path) -> None:
    """按格式特征绘制调整 OR 森林图，并用颜色编码 IPW ATE。"""
    if summary_df.empty:
        return

    plot_df = summary_df.dropna(subset=["adjusted_or", "adjusted_or_ci_low", "adjusted_or_ci_high", "ipw_ate"]).copy()
    if plot_df.empty:
        return

    _configure_plot_style()
    feature_order = ["标题密度", "粗体密度", "列表密度"]
    feature_titles = {
        "标题密度": "Header density (primary)",
        "粗体密度": "Bold density (primary)",
        "列表密度": "List density (sensitivity)",
    }
    ate_abs_max = float(plot_df["ipw_ate"].abs().max()) if not plot_df.empty else 0.1
    ate_abs_max = max(ate_abs_max, 0.05)

    fig, axes = plt.subplots(1, 3, figsize=(18, 9), sharex=True)
    for ax, feature_label in zip(axes, feature_order):
        feature_df = plot_df[plot_df["feature"] == feature_label].copy()
        feature_df = feature_df.sort_values("adjusted_or", ascending=True).reset_index(drop=True)
        if feature_df.empty:
            ax.set_visible(False)
            continue

        y_pos = np.arange(len(feature_df))
        xerr = np.vstack([
            feature_df["adjusted_or"] - feature_df["adjusted_or_ci_low"],
            feature_df["adjusted_or_ci_high"] - feature_df["adjusted_or"],
        ])
        ax.errorbar(
            feature_df["adjusted_or"],
            y_pos,
            xerr=xerr,
            fmt="none",
            ecolor="#94a3b8",
            elinewidth=2,
            capsize=3,
            zorder=1,
        )
        scatter = ax.scatter(
            feature_df["adjusted_or"],
            y_pos,
            c=feature_df["ipw_ate"],
            cmap="RdBu_r",
            vmin=-ate_abs_max,
            vmax=ate_abs_max,
            s=72,
            edgecolors="#0f172a",
            linewidths=0.5,
            zorder=3,
        )
        ax.axvline(1.0, color="#6b7280", linestyle="--", linewidth=1.2)
        ax.set_title(feature_titles[feature_label])
        ax.set_yticks(y_pos)
        ax.set_yticklabels(feature_df["subset"].replace(SUBSET_LABELS_EN))
        ax.set_xlabel("Adjusted odds ratio")

    fig.colorbar(scatter, ax=axes, fraction=0.022, pad=0.02, label="IPW ATE")
    fig.suptitle("C20 Format Robustness")
    fig.tight_layout()
    picture_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(picture_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def run_format_effect_robust(
    file_path: Path | str | None = None,
    report_dir: Path | str | None = None,
    table_dir: Path | str | None = None,
    picture_dir: Path | str | None = None,
    bootstrap_n: int = 30,
    seed: int = 42,
) -> dict[str, Path]:
    """执行完整的 R18 格式稳健性分析。"""
    root = Path.cwd()
    if report_dir is None:
        report_path = get_output_path("report", "R18_format_effect_robust_report.txt", root)
    else:
        report_path = Path(report_dir) / "R18_format_effect_robust_report.txt"

    if table_dir is None:
        table_path = get_output_path("table", "T15_format_robust_summary.csv", root)
    else:
        table_path = Path(table_dir) / "T15_format_robust_summary.csv"

    if picture_dir is None:
        picture_path = get_output_path("picture", "P17_format_robust_forest.png", root)
    else:
        picture_path = Path(picture_dir) / "P17_format_robust_forest.png"

    report_path.parent.mkdir(parents=True, exist_ok=True)
    table_path.parent.mkdir(parents=True, exist_ok=True)
    picture_path.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("1/3 读取全量数据并构造模型级统计量")
    print("=" * 80)
    global_path = file_path if file_path is not None else None
    df_global = load_data_global(global_path)
    model_stats = build_model_stats(df_global)
    subset_paths = get_analysis_subset_paths(root)

    report_lines: list[str] = []
    report_lines.append("=" * 80)
    report_lines.append("格式效应稳健性分析报告（R18）")
    report_lines.append("=" * 80)
    report_lines.append("")
    report_lines.append("【方法】")
    report_lines.append("  - 处理变量：A 是否具有更高的目标格式密度")
    report_lines.append("  - 结果变量：winner_a（A 是否获胜）")
    report_lines.append("  - 稳健性方法：调整逻辑回归 + 稳定化 IPW")
    report_lines.append("  - 长度控制：token_diff_ab 始终作为混淆控制纳入")
    report_lines.append("  - 其余格式控制：对目标格式外的另外两类格式密度差同步控制")
    report_lines.append("  - 列表密度仅作敏感性分析，不写入主结论")
    report_lines.append("")

    summary_rows: list[dict[str, float | str]] = []

    print("=" * 80)
    print("2/3 按格式特征与子集执行稳健性分析")
    print("=" * 80)
    for feature_cfg in FORMAT_FEATURES:
        feature_label = str(feature_cfg["label"])
        print(f"分析格式特征：{feature_label}")
        for subset_name, path in subset_paths.items():
            subset_df = load_subset(path, model_stats)
            block_lines, summary_row = analyze_feature_subset(
                feature_cfg=feature_cfg,
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
        summary_df = summary_df.sort_values(["feature", "subset"])
        summary_df.to_csv(table_path, index=False, encoding="utf-8-sig")
        plot_format_robust_forest(summary_df, picture_path)

    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("3/3 汇总结论")
    report_lines.append("=" * 80)
    if not summary_df.empty:
        full_df = summary_df[summary_df["subset"] == "全量"].copy()
        for feature_cfg in FORMAT_FEATURES:
            feature_label = str(feature_cfg["label"])
            role = str(feature_cfg["role"])
            row_df = full_df[full_df["feature"] == feature_label]
            if row_df.empty:
                continue
            row = row_df.iloc[0]
            report_lines.append(
                f"全量样本 - {feature_label}（{role}）：调整 OR={row['adjusted_or']:.4f}，"
                f"IPW ATE={row['ipw_ate']:.4f}，95% CI [{row['ipw_ci_low']:.4f}, {row['ipw_ci_high']:.4f}]"
            )
        report_lines.append("解释：若标题/粗体的调整 OR 仍 > 1 且 IPW CI 不跨 0，则说明格式偏好在处理效应视角下仍保持稳健。")
        report_lines.append("解释：若列表密度结果不稳定或区间跨 0，应将其保留为敏感性变量，而不作为主结论。")
    else:
        report_lines.append("无可用子集结果。")

    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("任务完成！")
    report_lines.append("=" * 80)
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    print(report_path.read_text(encoding="utf-8")[:1600])
    return {"report": report_path, "table": table_path, "picture": picture_path}


def main() -> None:
    """命令行入口。"""
    parser = argparse.ArgumentParser(description="运行格式效应稳健性分析（R18）。")
    parser.add_argument("--bootstrap", type=int, default=30, help="IPW bootstrap 次数，默认 30")
    parser.add_argument("--seed", type=int, default=42, help="随机种子")
    args = parser.parse_args()

    run_format_effect_robust(
        bootstrap_n=args.bootstrap,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()