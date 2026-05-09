"""
C22_sem_analysis

基于配对差异特征拟合结构方程模型，并输出路径估计与 bootstrap 结果。

功能：
- 构造 SEM 所需的外生层、中介层和结果层变量
- 比较主模型与扩展模型并估计直接效应与间接效应
- 输出表格、路径图、bootstrap 效应图和文本报告

数据流向：
    optimized_data.parquet 与 C18 配对特征 → SEM 建模与 bootstrap 估计 → Tables/T11_sem_layer_stats.csv 至 Tables/T15_sem_bootstrap_effects_ci.csv
    + Reports/R20_sem_analysis_report.txt + Pictures/P13_sem_path_diagram.png + Pictures/P14_sem_bootstrap_effects_ci.png
"""

from __future__ import annotations

import argparse
import time
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from semopy import Model, calc_stats, semplot

from accessor import (
    build_output_paths,
    get_data_path,
    get_output_path,
)
from C18_pure_effect import add_pair_features, build_model_stats, load_data_global
from stats_utils import zscore_series


# 这些列名对应 C18 / accessor 在分析阶段派生的临时列，
# 不代表 optimized_data.parquet 的持久顶层 schema。
ANALYSIS_CONTINUOUS_EXOG_COLS: list[str] = [
    "ability_diff",
    "verbosity_diff",
    "format_tendency_diff",
    "user_tokens",
    "turns",
]

ANALYSIS_BINARY_EXOG_COLS: list[str] = [
    "creative_writing_bool",
    "if_bool",
    "math_bool",
    "code_bool",
    "complexity",
    "creativity",
    "domain_knowledge",
    "problem_solving",
    "real_world",
    "specificity",
    "technical_accuracy",
]

PRIMARY_MEDIATOR_COLS: list[str] = [
    "token_diff_ab",
    "header_density_diff",
    "bold_density_diff",
]

SUPPLEMENTARY_MEDIATOR_COLS: list[str] = ["list_density_diff"]

OUTCOME_ANALYSIS_COL = "winner_a"

EFFECT_LABELS_EN: dict[str, str] = {
    "长度直接效应": "Length direct",
    "标题密度直接效应": "Header direct",
    "粗体密度直接效应": "Bold direct",
    "列表密度直接效应": "List direct",
    "能力直接效应": "Ability direct",
    "能力→长度→偏好": "Ability -> length -> preference",
    "能力→标题密度→偏好": "Ability -> header -> preference",
    "能力→粗体密度→偏好": "Ability -> bold -> preference",
    "能力→列表密度→偏好": "Ability -> list -> preference",
    "能力总间接效应": "Ability total indirect",
    "能力总效应": "Ability total",
    "词冗性→长度→偏好": "Verbosity -> length -> preference",
    "格式倾向直接效应": "Format tendency direct",
    "格式倾向→标题密度→偏好": "Format tendency -> header -> preference",
    "格式倾向→粗体密度→偏好": "Format tendency -> bold -> preference",
    "格式倾向→列表密度→偏好": "Format tendency -> list -> preference",
    "格式倾向总间接效应": "Format tendency total indirect",
}

KEY_FIT_METRICS: list[str] = [
    "DoF",
    "chi2",
    "chi2 p-value",
    "CFI",
    "TLI",
    "GFI",
    "AGFI",
    "NFI",
    "RMSEA",
    "AIC",
    "BIC",
]

SEM_TABLE_FILES = {
    "layer": "T11_sem_layer_stats.csv",
    "corr": "T12_sem_correlations.csv",
    "model": "T13_sem_model_comparison.csv",
    "paths": "T14_sem_path_estimates.csv",
    "boot": "T15_sem_bootstrap_effects_ci.csv",
}

SEM_PATH_PICTURE_FILE = "P13_sem_path_diagram.png"
SEM_BOOTSTRAP_PICTURE_FILE = "P14_sem_bootstrap_effects_ci.png"

def _fit_stats_to_dict(stats_df: pd.DataFrame) -> dict[str, float]:
    """将 semopy calc_stats 输出整理为扁平字典。"""
    if stats_df.empty:
        return {metric: np.nan for metric in KEY_FIT_METRICS}
    row = stats_df.iloc[0]
    return {metric: float(row.get(metric, np.nan)) for metric in KEY_FIT_METRICS}


def prepare_sem_data(
    file_path: Path | str | None = None,
    max_n: int | None = None,
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    读取全量数据并构造 SEM 所需数据表。

    参数说明：
    - file_path：输入 parquet 路径（默认使用 Data/optimized_data/optimized_data.parquet）
    - max_n：调试时可选抽样上限（默认不抽样）
    - seed：抽样随机种子

    返回值：
    - raw_df：原始量纲变量表（用于描述统计）
    - sem_df：连续变量已 z 标准化、全列已转 float 的建模表
    """
    if file_path is None:
        file_path = get_data_path("optimized")

    df_global = load_data_global(file_path)
    model_stats = build_model_stats(df_global)
    df = add_pair_features(df_global, model_stats)

    analysis_cols = (
        [OUTCOME_ANALYSIS_COL]
        + ANALYSIS_CONTINUOUS_EXOG_COLS
        + ANALYSIS_BINARY_EXOG_COLS
        + PRIMARY_MEDIATOR_COLS
        + SUPPLEMENTARY_MEDIATOR_COLS
    )

    raw_df = df[analysis_cols].dropna().copy()
    if max_n is not None and len(raw_df) > max_n:
        raw_df = raw_df.sample(n=max_n, random_state=seed).copy()

    sem_df = raw_df.copy()
    for col in ANALYSIS_CONTINUOUS_EXOG_COLS + PRIMARY_MEDIATOR_COLS + SUPPLEMENTARY_MEDIATOR_COLS:
        sem_df[col] = zscore_series(sem_df[col])

    for col in sem_df.columns:
        sem_df[col] = sem_df[col].astype(float)

    return raw_df, sem_df


def build_layer_stats(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    汇总外生层、中介层、结果层变量的描述统计。

    返回字段包括：均值、标准差、四分位数、缺失率、二值变量占比。
    """
    layer_map: dict[str, tuple[str, str]] = {}
    for col in ANALYSIS_CONTINUOUS_EXOG_COLS:
        layer_map[col] = ("外生层", "连续")
    for col in ANALYSIS_BINARY_EXOG_COLS:
        layer_map[col] = ("外生层", "二值")
    for col in PRIMARY_MEDIATOR_COLS:
        layer_map[col] = ("中介层（主模型）", "连续")
    for col in SUPPLEMENTARY_MEDIATOR_COLS:
        layer_map[col] = ("中介层（扩展模型）", "连续")
    layer_map[OUTCOME_ANALYSIS_COL] = ("结果层", "二值")

    rows: list[dict[str, float | str]] = []
    for col in raw_df.columns:
        series = raw_df[col]
        series_float = series.astype(float)
        layer, var_type = layer_map.get(col, ("其他", "未知"))
        row: dict[str, float | str] = {
            "variable": col,
            "layer": layer,
            "type": var_type,
            "n": int(series.notna().sum()),
            "missing": int(series.isna().sum()),
            "missing_pct": float(series.isna().mean()),
            "mean": float(series_float.mean()),
            "std": float(series_float.std(ddof=1)) if series.notna().sum() > 1 else np.nan,
            "min": float(series_float.min()),
            "p25": float(series_float.quantile(0.25)),
            "median": float(series_float.quantile(0.50)),
            "p75": float(series_float.quantile(0.75)),
            "max": float(series_float.max()),
            "positive_rate": float(series_float.mean()) if var_type == "二值" else np.nan,
        }
        rows.append(row)

    out = pd.DataFrame(rows)
    return out.sort_values(["layer", "variable"]).reset_index(drop=True)


def build_correlation_table(raw_df: pd.DataFrame) -> pd.DataFrame:
    """构建关键连续变量与结果变量的相关矩阵。"""
    analysis_corr_cols = (
        ANALYSIS_CONTINUOUS_EXOG_COLS
        + PRIMARY_MEDIATOR_COLS
        + SUPPLEMENTARY_MEDIATOR_COLS
        + [OUTCOME_ANALYSIS_COL]
    )
    corr_df = raw_df[analysis_corr_cols].astype(float).corr(method="pearson")
    corr_df.index.name = "variable"
    return corr_df.reset_index()


def build_sem_description(include_list: bool = False) -> str:
    """
    生成 SEM 模型语法。

    主模型不纳入 list_density_diff；扩展模型将其作为敏感性分析路径。

    这里使用的列名都是 C18 / accessor 派生的分析列名，
    不要求 optimized_data.parquet 在顶层持久化这些字段。
    """
    token_rhs_cols = ANALYSIS_CONTINUOUS_EXOG_COLS + ANALYSIS_BINARY_EXOG_COLS
    format_rhs_cols = ANALYSIS_CONTINUOUS_EXOG_COLS + ANALYSIS_BINARY_EXOG_COLS + ["token_diff_ab"]
    outcome_rhs_cols = ANALYSIS_CONTINUOUS_EXOG_COLS + ANALYSIS_BINARY_EXOG_COLS + PRIMARY_MEDIATOR_COLS.copy()
    if include_list:
        outcome_rhs_cols += SUPPLEMENTARY_MEDIATOR_COLS

    lines = [
        f"token_diff_ab ~ {' + '.join(token_rhs_cols)}",
        f"header_density_diff ~ {' + '.join(format_rhs_cols)}",
        f"bold_density_diff ~ {' + '.join(format_rhs_cols)}",
    ]

    if include_list:
        lines.append(f"list_density_diff ~ {' + '.join(format_rhs_cols)}")

    lines.append(f"{OUTCOME_ANALYSIS_COL} ~ {' + '.join(outcome_rhs_cols)}")
    lines.append("header_density_diff ~~ bold_density_diff")
    if include_list:
        lines.append("header_density_diff ~~ list_density_diff")
        lines.append("bold_density_diff ~~ list_density_diff")

    return "\n".join(lines)


def fit_sem_model(df: pd.DataFrame, model_desc: str, obj: str = "DWLS") -> dict[str, object]:
    """
    拟合单个 SEM 模型并返回模型对象、路径表与拟合优度。

    参数说明：
    - df：已数值化的数据表
    - model_desc：semopy 模型语法
    - obj：拟合目标函数（默认 DWLS）
    """
    model = Model(model_desc)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        model.fit(df.astype(float), obj=obj)

    estimates = model.inspect().copy()
    estimates["model_name"] = ""
    fit_stats = _fit_stats_to_dict(calc_stats(model))
    return {
        "model": model,
        "estimates": estimates,
        "fit_stats": fit_stats,
    }


def _extract_path(estimates: pd.DataFrame, lhs: str, rhs: str) -> float:
    """提取路径 lhs ~ rhs 的点估计，不存在则返回 nan。"""
    mask = (
        (estimates["lval"] == lhs)
        & (estimates["op"] == "~")
        & (estimates["rval"] == rhs)
    )
    if not mask.any():
        return np.nan
    return float(estimates.loc[mask, "Estimate"].iloc[0])


def calculate_effects(estimates: pd.DataFrame, include_list: bool = False) -> dict[str, float]:
    """
    计算关键直接效应、间接效应和总效应。

    重点关注：
    - 长度与格式的直接效应
    - ability_diff 通过长度/格式的间接效应
    - verbosity_diff 与 format_tendency_diff 的代表性间接效应
    """
    token_to_win = _extract_path(estimates, OUTCOME_ANALYSIS_COL, "token_diff_ab")
    header_to_win = _extract_path(estimates, OUTCOME_ANALYSIS_COL, "header_density_diff")
    bold_to_win = _extract_path(estimates, OUTCOME_ANALYSIS_COL, "bold_density_diff")
    ability_to_win = _extract_path(estimates, OUTCOME_ANALYSIS_COL, "ability_diff")
    list_to_win = _extract_path(estimates, OUTCOME_ANALYSIS_COL, "list_density_diff")

    ability_to_token = _extract_path(estimates, "token_diff_ab", "ability_diff")
    ability_to_header = _extract_path(estimates, "header_density_diff", "ability_diff")
    ability_to_bold = _extract_path(estimates, "bold_density_diff", "ability_diff")
    ability_to_list = _extract_path(estimates, "list_density_diff", "ability_diff")

    verbosity_to_token = _extract_path(estimates, "token_diff_ab", "verbosity_diff")

    fmt_to_header = _extract_path(estimates, "header_density_diff", "format_tendency_diff")
    fmt_to_bold = _extract_path(estimates, "bold_density_diff", "format_tendency_diff")
    fmt_to_list = _extract_path(estimates, "list_density_diff", "format_tendency_diff")
    fmt_to_win = _extract_path(estimates, OUTCOME_ANALYSIS_COL, "format_tendency_diff")

    effects: dict[str, float] = {
        "长度直接效应": token_to_win,
        "标题密度直接效应": header_to_win,
        "粗体密度直接效应": bold_to_win,
        "能力直接效应": ability_to_win,
        "能力→长度→偏好": ability_to_token * token_to_win,
        "能力→标题密度→偏好": ability_to_header * header_to_win,
        "能力→粗体密度→偏好": ability_to_bold * bold_to_win,
        "能力总间接效应": (
            ability_to_token * token_to_win
            + ability_to_header * header_to_win
            + ability_to_bold * bold_to_win
        ),
        "能力总效应": np.nan,
        "词冗性→长度→偏好": verbosity_to_token * token_to_win,
        "格式倾向直接效应": fmt_to_win,
        "格式倾向→标题密度→偏好": fmt_to_header * header_to_win,
        "格式倾向→粗体密度→偏好": fmt_to_bold * bold_to_win,
        "格式倾向总间接效应": (
            fmt_to_header * header_to_win + fmt_to_bold * bold_to_win
        ),
    }

    if include_list:
        effects["列表密度直接效应"] = list_to_win
        effects["能力→列表密度→偏好"] = ability_to_list * list_to_win
        effects["格式倾向→列表密度→偏好"] = fmt_to_list * list_to_win
        effects["能力总间接效应"] += ability_to_list * list_to_win
        effects["格式倾向总间接效应"] += fmt_to_list * list_to_win

    effects["能力总效应"] = effects["能力直接效应"] + effects["能力总间接效应"]
    return effects


def bootstrap_effects(
    sem_df: pd.DataFrame,
    model_desc: str,
    include_list: bool,
    n_boot: int = 50,
    seed: int = 42,
) -> pd.DataFrame:
    """
    通过非参数 bootstrap 估计关键效应的采样分布。

    参数说明：
    - sem_df：已标准化并转 float 的建模数据
    - model_desc：SEM 模型语法
    - include_list：是否为扩展模型
    - n_boot：bootstrap 次数
    - seed：随机种子
    """
    rng = np.random.default_rng(seed)
    records: list[dict[str, float]] = []
    start = time.time()

    for i in range(n_boot):
        sample = sem_df.sample(
            n=len(sem_df),
            replace=True,
            random_state=int(rng.integers(0, 2**32 - 1)),
        )
        try:
            fitted = fit_sem_model(sample, model_desc)
            records.append(calculate_effects(fitted["estimates"], include_list=include_list))
        except Exception:
            continue

        if (i + 1) % 10 == 0 or i + 1 == n_boot:
            elapsed = time.time() - start
            print(f"Bootstrap 进度：{i + 1}/{n_boot}，累计耗时 {elapsed:.1f}s")

    return pd.DataFrame(records)


def summarize_bootstrap(
    point_effects: dict[str, float],
    boot_df: pd.DataFrame,
) -> pd.DataFrame:
    """整理 bootstrap 均值、标准差和 95% 百分位置信区间。"""
    rows: list[dict[str, float | str | bool]] = []
    for effect_name, point_value in point_effects.items():
        series = boot_df.get(effect_name, pd.Series(dtype=float)).dropna()
        if series.empty:
            rows.append({
                "effect": effect_name,
                "estimate": float(point_value),
                "boot_mean": np.nan,
                "boot_std": np.nan,
                "ci_low": np.nan,
                "ci_high": np.nan,
                "successful_bootstrap_n": 0,
                "exclude_zero": False,
            })
            continue

        ci_low = float(series.quantile(0.025))
        ci_high = float(series.quantile(0.975))
        rows.append({
            "effect": effect_name,
            "estimate": float(point_value),
            "boot_mean": float(series.mean()),
            "boot_std": float(series.std(ddof=1)),
            "ci_low": ci_low,
            "ci_high": ci_high,
            "successful_bootstrap_n": int(series.shape[0]),
            "exclude_zero": bool((ci_low > 0) or (ci_high < 0)),
        })

    return pd.DataFrame(rows)


def save_path_diagram(model: Model, output_path: Path) -> bool:
    """尝试保存路径图；若 graphviz 不可用则返回 False。"""
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        semplot(model, str(output_path), plot_covs=False, plot_exos=True, show=False)
        return True
    except Exception as exc:
        print(f"semplot 路径图生成失败，改用内置回退图：{exc}")

    try:
        graph = nx.DiGraph()
        graph.add_nodes_from([
            "Ability Diff",
            "Verbosity Diff",
            "Format Tendency",
            "Prompt Controls",
            "Token Diff",
            "Header Density",
            "Bold Density",
            "Preference",
        ])
        graph.add_edges_from([
            ("Ability Diff", "Token Diff"),
            ("Ability Diff", "Header Density"),
            ("Ability Diff", "Bold Density"),
            ("Ability Diff", "Preference"),
            ("Verbosity Diff", "Token Diff"),
            ("Verbosity Diff", "Preference"),
            ("Format Tendency", "Header Density"),
            ("Format Tendency", "Bold Density"),
            ("Format Tendency", "Preference"),
            ("Prompt Controls", "Token Diff"),
            ("Prompt Controls", "Header Density"),
            ("Prompt Controls", "Bold Density"),
            ("Prompt Controls", "Preference"),
            ("Token Diff", "Header Density"),
            ("Token Diff", "Bold Density"),
            ("Token Diff", "Preference"),
            ("Header Density", "Preference"),
            ("Bold Density", "Preference"),
        ])

        positions = {
            "Ability Diff": (0.0, 0.90),
            "Verbosity Diff": (0.0, 0.60),
            "Format Tendency": (0.0, 0.30),
            "Prompt Controls": (0.0, 0.00),
            "Token Diff": (0.52, 0.70),
            "Header Density": (0.52, 0.42),
            "Bold Density": (0.52, 0.14),
            "Preference": (1.0, 0.42),
        }

        plt.figure(figsize=(12, 7))
        nx.draw_networkx_nodes(
            graph,
            positions,
            node_color=["#dceefb", "#dceefb", "#dceefb", "#f7f0c6", "#f8d7da", "#f8d7da", "#f8d7da", "#d4edda"],
            node_size=3600,
            edgecolors="#34495e",
            linewidths=1.2,
        )
        nx.draw_networkx_labels(graph, positions, font_size=11)
        nx.draw_networkx_edges(
            graph,
            positions,
            arrows=True,
            arrowstyle="-|>",
            arrowsize=18,
            width=1.4,
            edge_color="#546e7a",
        )
        plt.title("SEM Main Model (Fallback Diagram)")
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(output_path, dpi=200, bbox_inches="tight")
        plt.close()
        return True
    except Exception as fallback_exc:
        print(f"回退路径图仍失败：{fallback_exc}")
        return False


def _configure_plot_style() -> None:
    """配置论文图表的全局样式。"""
    plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.style.use("seaborn-v0_8-darkgrid")


def plot_bootstrap_effects_ci(bootstrap_summary: pd.DataFrame, output_path: Path) -> None:
    """绘制 SEM 关键效应的 bootstrap 置信区间森林图。"""
    if bootstrap_summary.empty:
        return

    plot_df = bootstrap_summary.dropna(subset=["estimate", "ci_low", "ci_high"]).copy()
    if plot_df.empty:
        return

    _configure_plot_style()
    category_map = {
        "直接": [],
        "间接": [],
        "总效应": [],
        "其他": [],
    }
    for effect in plot_df["effect"]:
        if "总效应" in effect:
            category_map["总效应"].append(effect)
        elif "间接" in effect or "→" in effect:
            category_map["间接"].append(effect)
        elif "直接效应" in effect:
            category_map["直接"].append(effect)
        else:
            category_map["其他"].append(effect)

    order: list[str] = []
    for key in ["直接", "间接", "总效应", "其他"]:
        order.extend(category_map[key])
    plot_df["effect"] = pd.Categorical(plot_df["effect"], categories=order, ordered=True)
    plot_df = plot_df.sort_values("effect", ascending=True).reset_index(drop=True)
    effect_labels = [EFFECT_LABELS_EN.get(effect, effect) for effect in plot_df["effect"].astype(str)]

    y_pos = np.arange(len(plot_df))
    colors = ["#0f766e" if flag else "#9ca3af" for flag in plot_df["exclude_zero"]]
    center = plot_df["boot_mean"].fillna(plot_df["estimate"]).astype(float)
    center = center.clip(lower=plot_df["ci_low"], upper=plot_df["ci_high"])
    xerr = np.vstack([
        (center - plot_df["ci_low"]).clip(lower=0),
        (plot_df["ci_high"] - center).clip(lower=0),
    ])

    fig, ax = plt.subplots(figsize=(12, max(7, len(plot_df) * 0.45)))
    ax.errorbar(
        center,
        y_pos,
        xerr=xerr,
        fmt="none",
        ecolor="#94a3b8",
        elinewidth=2,
        capsize=3,
        zorder=1,
    )
    ax.scatter(center, y_pos, c=colors, s=72, edgecolors="#0f172a", linewidths=0.5, zorder=3)
    ax.axvline(0.0, color="#6b7280", linestyle="--", linewidth=1.2)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(effect_labels)
    ax.set_xlabel("Standardized effect")
    ax.set_title("C22 SEM Bootstrap Effects 95% CI")

    success_min = int(plot_df["successful_bootstrap_n"].min()) if not plot_df.empty else 0
    success_max = int(plot_df["successful_bootstrap_n"].max()) if not plot_df.empty else 0
    ax.text(
        0.99,
        0.02,
        f"Successful bootstraps: {success_min}-{success_max}",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=9,
        color="#374151",
    )

    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def generate_report(
    raw_df: pd.DataFrame,
    layer_stats: pd.DataFrame,
    model_comparison: pd.DataFrame,
    primary_paths: pd.DataFrame,
    bootstrap_summary: pd.DataFrame,
    primary_desc: str,
    extended_desc: str,
    bootstrap_n: int,
    plot_saved: bool,
) -> str:
    """生成主报告文本。"""
    lines: list[str] = []
    lines.append("=" * 80)
    lines.append("结构方程模型（SEM）分析报告")
    lines.append("=" * 80)
    lines.append("")
    lines.append("【数据与建模口径】")
    lines.append(f"  样本量：{len(raw_df):,}")
    lines.append("  数据来源：optimized_data.parquet（nested schema） + C18 loader / add_pair_features 派生的分析列")
    lines.append("  结果变量：winner_a（A 获胜=1，分析阶段派生列）")
    lines.append("  主模型中介：token_diff_ab, header_density_diff, bold_density_diff（均为分析阶段派生列）")
    lines.append("  扩展模型：在主模型基础上加入 list_density_diff（敏感性分析；同为派生列）")
    lines.append(f"  Bootstrap 次数：{bootstrap_n}")
    lines.append("")

    lines.append("【层次变量摘要】")
    for layer_name, g in layer_stats.groupby("layer"):
        lines.append(f"  {layer_name}：{len(g)} 个变量")
        for row in g.itertuples():
            if row.type == "二值":
                lines.append(
                    f"    - {row.variable}: 均值/占比={row.mean:.4f}, 缺失率={row.missing_pct:.2%}"
                )
            else:
                lines.append(
                    f"    - {row.variable}: mean={row.mean:.4f}, std={row.std:.4f}, "
                    f"median={row.median:.4f}"
                )
    lines.append("")

    lines.append("【模型语法】")
    lines.append("  主模型：")
    lines.extend([f"    {line}" for line in primary_desc.splitlines()])
    lines.append("  扩展模型：")
    lines.extend([f"    {line}" for line in extended_desc.splitlines()])
    lines.append("")

    lines.append("【模型比较】")
    for row in model_comparison.itertuples():
        lines.append(
            f"  {row.model_name}: CFI={row.CFI:.4f}, TLI={row.TLI:.4f}, "
            f"RMSEA={row.RMSEA:.4f}, AIC={row.AIC:.2f}, BIC={row.BIC:.2f}"
        )
    lines.append("  解释：主模型用于正式结论；扩展模型用于检验 list_density_diff 是否改变主路径。")
    lines.append("")

    lines.append("【主模型关键路径估计】")
    show_paths = primary_paths[
        (primary_paths["op"] == "~")
        & (
            primary_paths["lval"].isin([OUTCOME_ANALYSIS_COL] + PRIMARY_MEDIATOR_COLS)
        )
    ].copy()
    for _, row in show_paths.iterrows():
        lines.append(
            f"  {row['lval']} ~ {row['rval']}: Estimate={row['Estimate']:.4f}, "
            f"SE={row['Std. Err']:.4f}, p={row['p-value']:.4g}"
        )
    lines.append("")

    lines.append("【Bootstrap 95% 置信区间】")
    for row in bootstrap_summary.itertuples():
        sig = "CI 排除 0" if row.exclude_zero else "CI 跨 0"
        lines.append(
            f"  {row.effect}: 点估计={row.estimate:.4f}, 95% CI "
            f"[{row.ci_low:.4f}, {row.ci_high:.4f}]，{sig}"
        )
    lines.append("")

    lines.append("【方法学结论】")
    lines.append("  1. 主模型将长度差与标题/粗体密度差作为并列中介，能够同时刻画内容冗长度与格式化程度对偏好的直接影响。")
    lines.append("  2. 扩展模型保留 list_density_diff 仅作敏感性分析，以避免将 C18 已识别的抑制效应直接写入主结论。")
    lines.append("  3. Bootstrap 置信区间用于补充 semopy 的正态近似标准误，尤其适合间接效应这类乘积项。")
    lines.append("  4. prompt-level 变量（任务类型与 criteria）在本模型中仅作为外生控制，不作为中介解释链条；它们同样来自 nested schema 的临时分析列。")
    lines.append(
        "  5. 路径图{}。".format("已保存到 Pictures/P13_sem_path_diagram.png" if plot_saved else "未生成（graphviz 依赖不可用）")
    )
    lines.append("")
    lines.append("=" * 80)
    lines.append("任务完成！")
    lines.append("=" * 80)
    return "\n".join(lines)


def run_sem_analysis(
    file_path: Path | str | None = None,
    report_dir: Path | str | None = None,
    table_dir: Path | str | None = None,
    picture_dir: Path | str | None = None,
    bootstrap_n: int = 50,
    max_n: int | None = None,
    seed: int = 42,
) -> dict[str, Path]:
    """
    执行完整 SEM 分析流程。

    参数说明：
    - file_path：输入 parquet 文件路径
    - report_dir：报告目录（默认 Reports）
    - table_dir：表格目录（默认 Tables）
    - picture_dir：图片目录（默认 Pictures）
    - bootstrap_n：bootstrap 次数
    - max_n：调试抽样上限
    - seed：随机种子

    返回值：输出文件路径字典。
    """
    if report_dir is None:
        report_path = get_output_path("report", "R20_sem_analysis_report.txt")
    else:
        report_path = Path(report_dir) / "R20_sem_analysis_report.txt"

    if table_dir is None:
        table_paths = build_output_paths(
            "table",
            SEM_TABLE_FILES,
        )
    else:
        table_root = Path(table_dir)
        table_paths = {
            "layer": table_root / SEM_TABLE_FILES["layer"],
            "corr": table_root / SEM_TABLE_FILES["corr"],
            "model": table_root / SEM_TABLE_FILES["model"],
            "paths": table_root / SEM_TABLE_FILES["paths"],
            "boot": table_root / SEM_TABLE_FILES["boot"],
        }

    if picture_dir is None:
        picture_path = get_output_path("picture", SEM_PATH_PICTURE_FILE)
        bootstrap_picture_path = get_output_path("picture", SEM_BOOTSTRAP_PICTURE_FILE)
    else:
        picture_path = Path(picture_dir) / SEM_PATH_PICTURE_FILE
        bootstrap_picture_path = Path(picture_dir) / SEM_BOOTSTRAP_PICTURE_FILE

    report_path.parent.mkdir(parents=True, exist_ok=True)
    for path in table_paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    picture_path.parent.mkdir(parents=True, exist_ok=True)
    bootstrap_picture_path.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("1/6 加载并准备 SEM 数据")
    print("=" * 80)
    raw_df, sem_df = prepare_sem_data(file_path=file_path, max_n=max_n, seed=seed)
    print(f"建模样本量：{len(sem_df):,}")

    print("=" * 80)
    print("2/6 生成层次变量统计")
    print("=" * 80)
    layer_stats = build_layer_stats(raw_df)
    corr_df = build_correlation_table(raw_df)
    layer_stats.to_csv(table_paths["layer"], index=False, encoding="utf-8-sig")
    corr_df.to_csv(table_paths["corr"], index=False, encoding="utf-8-sig")

    print("=" * 80)
    print("3/6 拟合主模型与扩展模型")
    print("=" * 80)
    primary_desc = build_sem_description(include_list=False)
    extended_desc = build_sem_description(include_list=True)

    primary_fit = fit_sem_model(sem_df, primary_desc)
    extended_fit = fit_sem_model(sem_df, extended_desc)

    primary_fit["estimates"]["model_name"] = "主模型"
    extended_fit["estimates"]["model_name"] = "扩展模型"

    model_comparison = pd.DataFrame([
        {"model_name": "主模型", **primary_fit["fit_stats"]},
        {"model_name": "扩展模型", **extended_fit["fit_stats"]},
    ])
    model_comparison.to_csv(table_paths["model"], index=False, encoding="utf-8-sig")

    all_paths = pd.concat([primary_fit["estimates"], extended_fit["estimates"]], ignore_index=True)
    all_paths.to_csv(table_paths["paths"], index=False, encoding="utf-8-sig")

    print("=" * 80)
    print("4/6 计算主模型关键效应与 bootstrap 置信区间")
    print("=" * 80)
    point_effects = calculate_effects(primary_fit["estimates"], include_list=False)
    boot_df = bootstrap_effects(
        sem_df=sem_df,
        model_desc=primary_desc,
        include_list=False,
        n_boot=bootstrap_n,
        seed=seed,
    )
    bootstrap_summary = summarize_bootstrap(point_effects, boot_df)
    bootstrap_summary.to_csv(table_paths["boot"], index=False, encoding="utf-8-sig")
    plot_bootstrap_effects_ci(bootstrap_summary, bootstrap_picture_path)

    print("=" * 80)
    print("5/6 尝试生成路径图")
    print("=" * 80)
    plot_saved = save_path_diagram(primary_fit["model"], picture_path)

    print("=" * 80)
    print("6/6 写出报告")
    print("=" * 80)
    report_text = generate_report(
        raw_df=raw_df,
        layer_stats=layer_stats,
        model_comparison=model_comparison,
        primary_paths=primary_fit["estimates"],
        bootstrap_summary=bootstrap_summary,
        primary_desc=primary_desc,
        extended_desc=extended_desc,
        bootstrap_n=bootstrap_n,
        plot_saved=plot_saved,
    )
    report_path.write_text(report_text, encoding="utf-8")

    print(report_text)
    return {
        "report": report_path,
        "layer_table": table_paths["layer"],
        "corr_table": table_paths["corr"],
        "model_table": table_paths["model"],
        "paths_table": table_paths["paths"],
        "boot_table": table_paths["boot"],
        "picture": picture_path,
        "bootstrap_picture": bootstrap_picture_path,
    }


def main() -> None:
    """命令行入口。"""
    parser = argparse.ArgumentParser(description="运行结构方程模型（SEM）分析。")
    parser.add_argument("--bootstrap", type=int, default=50, help="bootstrap 次数，默认 50")
    parser.add_argument("--max-n", type=int, default=None, help="调试时的抽样上限")
    parser.add_argument("--seed", type=int, default=42, help="随机种子")
    args = parser.parse_args()

    run_sem_analysis(
        bootstrap_n=args.bootstrap,
        max_n=args.max_n,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()