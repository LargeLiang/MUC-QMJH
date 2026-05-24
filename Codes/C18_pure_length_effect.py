"""
C18_pure_length_effect

控制混淆变量后估计长度偏好的净效应，并量化效应衰减。

功能：
- 加载全量数据计算全局模型统计量（胜率、词冗性、格式风格）
- 构造配对层面的长度差与模型差异特征
- 拟合四层嵌套逻辑回归（M0→M3），追踪 β_token_diff 的衰减路径
- 输出净效应汇总表、OR 衰减图和方法报告

数据流向：
    optimized_data.parquet 与 C13 子集 parquet → 配对特征构造与嵌套长度模型拟合
    → Tables/T05_pure_length_net_effect_summary.csv
    + Reports/R16_pure_length_effect_report.txt
    + Pictures/P08_length_confounding_attenuation.png
"""

import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tools.sm_exceptions import ConvergenceWarning

from accessor import (
    SUBSET_LABELS_EN,
    get_analysis_subset_paths,
    get_path,
    safe_int_count,
    with_flat_analysis_columns,
)
from stats_utils import zscore_series
from table_export_utils import export_table_bundle

LENGTH_EFFECT_TABLE_FILE = "T05_pure_length_net_effect_summary.csv"
LENGTH_EFFECT_PICTURE_FILE = "P08_length_confounding_attenuation.png"

# C19 会使用这些格式变量常量（导入自此模块）
FORMAT_DENSITY_VARS: list[str] = [
    "header_density_diff",
    "list_density_diff",
    "bold_density_diff",
]

FORMAT_DENSITY_LABELS: dict[str, str] = {
    "header_density_diff": "标题密度差",
    "list_density_diff":   "列表密度差",
    "bold_density_diff":   "粗体密度差",
}

CRITERIA_COLS: list[str] = [
    "complexity", "creativity", "domain_knowledge",
    "problem_solving", "real_world", "specificity", "technical_accuracy",
]

TASK_TYPE_COLS: list[str] = [
    "creative_writing_bool", "if_bool", "math_bool", "code_bool",
]

# 所有需要 z-score 标准化的连续型变量
_CONT_VARS: list[str] = [
    "user_tokens", "turns",
    "token_diff_ab",
    "header_density_diff", "list_density_diff", "bold_density_diff",
    "ability_diff", "verbosity_diff", "format_tendency_diff",
]


# 数据加载与特征构建


def load_data_global(file_path: Path | str | None = None) -> pd.DataFrame:
    """
    加载全量 optimized_data.parquet，仅保留结果明确的配对行。

    仅用于 build_model_stats() 的全局统计计算；
    子集分析从 C13 生成的分区文件读取（见 load_subset）。
    """
    path = get_path("optimized") if file_path is None else Path(file_path)
    df = pd.read_parquet(path)
    df = df[df["winner"].isin(["model_a", "model_b"])].copy()
    return with_flat_analysis_columns(df)


def build_model_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    从全量数据计算每个模型的历史统计量，作为模型能力与风格的代理变量。

    统计口径：在全数据集中，每个模型作为 model_a 或 model_b 出现时的记录。
    必须从全量数据计算，不得在子集内重估（避免小样本偏差）。

    返回值：
      DataFrame，index = 模型名称，列包含：
        win_rate        全局胜率
        mean_tokens     平均回复长度（tokens）
        mean_format     平均总格式元素数（header+list+bold）
    """
    records_a = df[["model_a", "winner", "a_tokens",
                    "a_header_count", "a_list_count", "a_bold_count"]].copy()
    records_a.columns = ["model", "winner", "tokens", "header_count", "list_count", "bold_count"]
    records_a["is_winner"] = (records_a["winner"] == "model_a").astype(int)

    records_b = df[["model_b", "winner", "b_tokens",
                    "b_header_count", "b_list_count", "b_bold_count"]].copy()
    records_b.columns = ["model", "winner", "tokens", "header_count", "list_count", "bold_count"]
    records_b["is_winner"] = (records_b["winner"] == "model_b").astype(int)

    records = pd.concat([records_a, records_b], ignore_index=True)

    # 部分行格式计数列可能仍为 dict，统一转换为 int
    for col in ("header_count", "list_count", "bold_count"):
        records[col] = records[col].map(safe_int_count)

    records["format_total"] = (records["header_count"] + records["list_count"]
                               + records["bold_count"])

    stats = records.groupby("model").agg(
        appearances=("is_winner", "count"),
        wins=("is_winner", "sum"),
        mean_tokens=("tokens", "mean"),
        mean_format=("format_total", "mean"),
    )
    stats["win_rate"] = stats["wins"] / stats["appearances"]
    return stats


def add_pair_features(df: pd.DataFrame, model_stats: pd.DataFrame) -> pd.DataFrame:
    """
    新增配对差异特征列（含格式密度变量）。

    长度差值：
    - token_diff_ab           : a_tokens − b_tokens

    格式计数差值：
    - header_diff_ab / list_diff_ab / bold_diff_ab

    格式密度差值（核心格式分析变量，已归一化长度，分母取 max(tokens,1) 防止除零）：
    - header_density_diff     : (a_header_count/a_tokens) − (b_header_count/b_tokens)
    - list_density_diff       : 同理
    - bold_density_diff       : 同理

    结果变量：
    - winner_a                : 1=model_a 获胜，0=model_b 获胜

    模型层差异代理变量（从全局 model_stats 映射，不在子集内重估）：
    - ability_diff            : wr_a − wr_b（全局胜率差）
    - verbosity_diff          : mean_tokens_a − mean_tokens_b
    - format_tendency_diff    : mean_format_a − mean_format_b
    """
    df = df.copy()

    # 格式计数列统一转 int（防止 dict 类型导致算术错误）
    for col in ("a_header_count", "a_list_count", "a_bold_count",
                "b_header_count", "b_list_count", "b_bold_count"):
        df[col] = df[col].map(safe_int_count)

    # 长度差值
    df["token_diff_ab"] = df["a_tokens"] - df["b_tokens"]

    # 格式计数差值
    df["header_diff_ab"] = df["a_header_count"] - df["b_header_count"]
    df["list_diff_ab"]   = df["a_list_count"]   - df["b_list_count"]
    df["bold_diff_ab"]   = df["a_bold_count"]   - df["b_bold_count"]

    # 格式密度差值（归一化，clip(lower=1) 防止除零）
    df["header_density_diff"] = (
        df["a_header_count"] / df["a_tokens"].clip(lower=1)
        - df["b_header_count"] / df["b_tokens"].clip(lower=1)
    )
    df["list_density_diff"] = (
        df["a_list_count"] / df["a_tokens"].clip(lower=1)
        - df["b_list_count"] / df["b_tokens"].clip(lower=1)
    )
    df["bold_density_diff"] = (
        df["a_bold_count"] / df["a_tokens"].clip(lower=1)
        - df["b_bold_count"] / df["b_tokens"].clip(lower=1)
    )

    # 结果变量
    df["winner_a"] = (df["winner"] == "model_a").astype(int)

    # 模型能力与风格代理（映射自全局 model_stats）
    for side in ("a", "b"):
        col = f"model_{side}"
        df[f"wr_{side}"]              = df[col].map(model_stats["win_rate"])
        df[f"verbosity_{side}"]       = df[col].map(model_stats["mean_tokens"])
        df[f"format_tendency_{side}"] = df[col].map(model_stats["mean_format"])

    df["ability_diff"]         = df["wr_a"]              - df["wr_b"]
    df["verbosity_diff"]       = df["verbosity_a"]       - df["verbosity_b"]
    df["format_tendency_diff"] = df["format_tendency_a"] - df["format_tendency_b"]

    return df


def load_subset(path: Path, model_stats: pd.DataFrame) -> pd.DataFrame:
    """
    读取 C13 生成的子集 parquet 文件，过滤 winner，映射模型统计量并新增特征列。

    参数说明：
    - path        : C13 子集 parquet 文件路径
    - model_stats : 从全量数据计算的模型统计量（不在子集内重估，避免小样本偏差）

    返回值：
      添加了所有 add_pair_features 衍生列的 DataFrame（仅明确获胜行）
    """
    df = pd.read_parquet(path)
    df = df[df["winner"].isin(["model_a", "model_b"])].copy()
    df = with_flat_analysis_columns(df)
    return add_pair_features(df, model_stats)


# 模型拟合工具


def _fit_logit(X: pd.DataFrame, y: pd.Series) -> dict | None:
    """
    拟合 statsmodels Logit 模型，返回关键统计量字典。

    返回值字典包含：
      result   : statsmodels Result 对象
      pseudo_r2: McFadden R²
      aic / bic: 信息准则
    """
    # 强制所有列转为 float64，避免 bool / object 列导致 statsmodels 报错
    try:
        X_float = X.astype(float)
    except Exception as cast_exc:
        print(f"    [警告] X 类型转换失败: {cast_exc}")
        return None
    X2 = sm.add_constant(X_float, has_constant="add")
    model = sm.Logit(y.astype(float), X2)
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=ConvergenceWarning)
            res = model.fit(disp=0, maxiter=300)
    except Exception as exc:
        print(f"    [警告] Logit 拟合失败: {exc}")
        return None
    pseudo_r2 = (1 - res.llf / res.llnull) if res.llnull and res.llnull != 0 else np.nan
    return {"result": res, "pseudo_r2": pseudo_r2, "aic": res.aic, "bic": res.bic}


def _extract_coef(fit_dict: dict | None, var: str) -> tuple[float, float, float]:
    """从拟合字典中提取 (coef, se, p_value)。若拟合失败则返回 nan 三元组。"""
    if fit_dict is None:
        return np.nan, np.nan, np.nan
    res = fit_dict["result"]
    coef = float(res.params.get(var, np.nan))
    se   = float(res.bse.get(var, np.nan))
    pval = float(res.pvalues.get(var, np.nan))
    return coef, se, pval


def _ame_at_mean(coef: float, y_mean: float) -> float:
    """在样本均值处估算平均边际效应 AME ≈ β × p̄(1 − p̄)。"""
    return coef * y_mean * (1 - y_mean)


def _wald_partial_r(coef: float, se: float, n: int) -> float:
    """Wald 部分相关 r = z_wald / sqrt(N)，z = coef / se。"""
    if se == 0 or np.isnan(se):
        return np.nan
    return (coef / se) / np.sqrt(n)


def _standardize(s: pd.DataFrame) -> pd.DataFrame:
    """
    对连续型变量进行 z-score 标准化，以 _z_ 前缀新增列，原列保留不变。

    标准差为零（常数列）时设为 0.0，不报错。
    """
    s = s.copy()
    for col in _CONT_VARS:
        if col in s.columns:
            s[f"_z_{col}"] = zscore_series(s[col])
    return s


def _active(s: pd.DataFrame, cols: list[str]) -> list[str]:
    """返回 cols 中满足'列存在且 nunique > 1'条件的列名列表。"""
    return [c for c in cols if c in s.columns and s[c].nunique() > 1]


# 验证：胜率与词冗性、格式风格相关性


def validate_model_confounding(
    model_stats: pd.DataFrame, report_lines: list[str]
) -> None:
    """
    验证模型能力（胜率）与词冗性/格式风格的 Spearman 相关性。

    若 |Spearman r| > 0.3，证明能力−长度/格式共线性成立，控制 ability_diff 为必要操作。
    """
    from scipy.stats import spearmanr

    valid        = model_stats.dropna(subset=["win_rate", "mean_tokens", "mean_format"])
    r_len, p_len = spearmanr(valid["win_rate"], valid["mean_tokens"])
    r_fmt, p_fmt = spearmanr(valid["win_rate"], valid["mean_format"])

    report_lines += [
        "",
        "【前置验证：模型能力 vs 词冗性 / 格式风格相关性】",
        f"  Spearman r（胜率 ~ 平均 token 数）= {r_len:.4f}  p = {p_len:.4e}",
        (f"  → |r| = {abs(r_len):.4f} > 0.3，能力−长度共线性成立，控制 ability_diff 为必要操作。"
         if abs(r_len) > 0.3 else
         f"  → |r| = {abs(r_len):.4f} ≤ 0.3，能力−长度共线性较弱。"),
        f"  Spearman r（胜率 ~ 平均格式数）= {r_fmt:.4f}  p = {p_fmt:.4e}",
        (f"  → |r| = {abs(r_fmt):.4f} > 0.3，能力−格式共线性成立，格式净效应分析需控制 format_tendency_diff。"
         if abs(r_fmt) > 0.3 else
         f"  → |r| = {abs(r_fmt):.4f} ≤ 0.3，能力−格式共线性较弱。"),
    ]


# 长度嵌套模型（M0 → M3）


def run_nested_models_length(
    df: pd.DataFrame,
    subset_name: str,
    report_lines: list[str],
) -> dict | None:
    """
    四层嵌套逻辑回归（长度系列）：追踪 β_token_diff 从粗效应到净效应的衰减路径。

    层次：
      M0：粗效应（仅 z_token_diff_ab）
      M1：+ 任务类型布尔 + z_user_tokens + z_turns
      M2：+ criteria（7维问题复杂度布尔值）
      M3：+ z_ability_diff + z_verbosity_diff + z_format_tendency_diff（模型层）

    混淆比例 = (OR_M0 − OR_M3) / (OR_M0 − 1)

    返回值：
      包含各层关键指标的摘要字典，或 None（样本量不足时返回 None）
    """
    TARGET = "token_diff_ab"
    MIN_N  = 30

    avail_criteria = [c for c in CRITERIA_COLS if c in df.columns]
    s = _standardize(df.dropna(subset=[TARGET, "winner_a"]).copy())

    if len(s) < MIN_N:
        report_lines.append(f"  【{subset_name}】样本量不足（n={len(s)}），跳过。")
        return None

    y      = s["winner_a"]
    y_mean = float(y.mean())
    n      = len(s)
    z_tgt  = "_z_token_diff_ab"

    task_bool = _active(s, TASK_TYPE_COLS)
    prompt_z  = _active(s, ["_z_user_tokens", "_z_turns"])
    crit_cols = _active(s, avail_criteria)
    model_z   = _active(s, ["_z_ability_diff", "_z_verbosity_diff", "_z_format_tendency_diff"])

    X0 = s[[z_tgt]]
    X1 = s[[z_tgt] + task_bool + prompt_z]
    X2 = pd.concat([X1, s[crit_cols]], axis=1) if crit_cols else X1
    X3 = pd.concat([X2, s[model_z]],   axis=1) if model_z   else X2

    fits = {lbl: _fit_logit(X.dropna(axis=1), y)
            for lbl, X in [("M0", X0), ("M1", X1), ("M2", X2), ("M3", X3)]}

    def _st(lbl: str) -> dict:
        coef, se, pval = _extract_coef(fits[lbl], z_tgt)
        or_v = float(np.exp(coef)) if not np.isnan(coef) else np.nan
        return {
            "coef": coef, "se": se, "pval": pval, "OR": or_v,
            "AME":    _ame_at_mean(coef, y_mean),
            "wald_r": _wald_partial_r(coef, se, n),
            "r2":     fits[lbl]["pseudo_r2"] if fits[lbl] else np.nan,
        }

    m    = {lbl: _st(lbl) for lbl in ("M0", "M1", "M2", "M3")}
    or0  = m["M0"]["OR"]
    or3  = m["M3"]["OR"]
    confound_pct = (
        (or0 - or3) / (or0 - 1)
        if not np.isnan(or0) and not np.isnan(or3) and abs(or0 - 1) > 1e-6
        else np.nan
    )

    # 写报告块
    w = 80
    report_lines += [
        "",
        f"【{subset_name}】  n = {n:,}  ( y_mean = {y_mean:.4f} )",
        "-" * w,
        f"  {'模型':<28}{'β_token':>10}{'SE':>8}{'p':>12}{'OR':>8}"
        f"{'AME':>10}{'Wald r':>9}{'R²':>8}",
    ]
    LAYER_LABELS = {
        "M0": "M0（粗效应）",
        "M1": "M1（+问题特征）",
        "M2": "M2（+criteria）",
        "M3": "M3（+模型能力+风格）",
    }
    for lbl, desc in LAYER_LABELS.items():
        st  = m[lbl]
        sig = "*" if st["pval"] < 0.05 else " "
        report_lines.append(
            f"  {desc:<28}  {st['coef']:>8.4f}  {st['se']:>6.4f}"
            f"  {st['pval']:>10.4e}{sig}  {st['OR']:>6.4f}"
            f"  {st['AME']:>8.4f}  {st['wald_r']:>7.4f}  {st['r2']:>6.4f}"
        )

    report_lines.append("")
    report_lines.append(f"  ▶ 净效应（M3）：OR = {or3:.4f}，Wald r = {m['M3']['wald_r']:.4f}")
    if not np.isnan(confound_pct):
        verdict = (
            "效应主要为真实偏好" if confound_pct < 0.3
            else "部分受混淆放大" if confound_pct < 0.7
            else "效应主要由混淆驱动"
        )
        report_lines.append(
            f"  ▶ 混淆比例：(OR_M0 − OR_M3)/(OR_M0 − 1) = {confound_pct:.2%}  → {verdict}"
        )
    else:
        report_lines.append("  ▶ 混淆比例：无法计算（OR_M0 未收敛或 ≤ 1）")

    return {
        "subset": subset_name, "n": n,
        "or0": or0, "or3": or3,
        "wald_r_adj": m["M3"]["wald_r"],
        "ame_adj":    m["M3"]["AME"],
        "r2_m0":      m["M0"]["r2"],
        "r2_m3":      m["M3"]["r2"],
        "confound_pct": confound_pct,
    }


def _render_length_summary(results: list[dict | None], report_lines: list[str]) -> None:
    """长度净效应跨子集汇总表，按调整后 OR 降序排列。"""
    valid = [r for r in results if r is not None]
    if not valid:
        report_lines.append("  无有效结果。")
        return

    valid.sort(key=lambda x: x["or3"] if not np.isnan(x["or3"]) else 0, reverse=True)

    report_lines += [
        "",
        "【长度净效应汇总（按调整后 OR 降序）】",
        "=" * 80,
        f"  {'子集':<18}{'n':>8}{'OR_粗':>8}{'OR_净':>8}"
        f"{'Wald_r':>9}{'AME':>8}{'混淆%':>9}{'结论':>16}",
        "-" * 80,
    ]
    for r in valid:
        cp      = r["confound_pct"]
        cp_str  = f"{cp:.1%}" if not np.isnan(cp) else "N/A"
        verdict = (
            ("真实偏好" if cp < 0.3 else "部分混淆" if cp < 0.7 else "主要混淆")
            if not np.isnan(cp) else "无法判断"
        )
        report_lines.append(
            f"  {r['subset']:<18}{r['n']:>8,}{r['or0']:>8.4f}{r['or3']:>8.4f}"
            f"{r['wald_r_adj']:>9.4f}{r['ame_adj']:>8.4f}{cp_str:>9}{verdict:>16}"
        )


def build_length_summary_df(results: list[dict | None]) -> pd.DataFrame:
    """将长度嵌套模型结果整理为结构化表格。"""
    rows = [r for r in results if r is not None]
    if not rows:
        return pd.DataFrame()
    summary_df = pd.DataFrame(rows)
    return summary_df.sort_values("or3", ascending=False, na_position="last").reset_index(drop=True)


def _configure_plot_style() -> None:
    """配置论文图表的全局样式。"""
    plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.style.use("seaborn-v0_8-darkgrid")


def plot_length_attenuation(length_df: pd.DataFrame, picture_path: Path) -> None:
    """绘制长度粗效应到净效应的 OR 衰减图。"""
    plot_df = length_df.dropna(subset=["or0", "or3"]).copy()
    if plot_df.empty:
        return

    _configure_plot_style()
    plot_df  = plot_df.sort_values("or3", ascending=True).reset_index(drop=True)
    y_pos    = np.arange(len(plot_df))
    y_labels = plot_df["subset"].replace(SUBSET_LABELS_EN)

    fig, ax = plt.subplots(figsize=(12, max(7, len(plot_df) * 0.45)))
    for idx, row in plot_df.iterrows():
        line_color = "#b3b3b3" if row["subset"] != "全量" else "#1f2937"
        ax.hlines(y=idx, xmin=row["or3"], xmax=row["or0"], color=line_color, linewidth=2.0, alpha=0.85)

    crude_color = "#d97706"
    net_color   = "#0f766e"
    marker_size = np.clip(np.sqrt(plot_df["n"]) * 1.6, 36, 180)
    ax.scatter(plot_df["or0"], y_pos, s=marker_size, color=crude_color, label="Crude OR (M0)", zorder=3)
    ax.scatter(plot_df["or3"], y_pos, s=marker_size, color=net_color,   label="Net OR (M3)",   zorder=4)

    or_values  = plot_df[["or0", "or3"]].to_numpy(dtype=float)
    confound_x = float(np.nanmax(or_values) + 0.08)
    for idx, row in plot_df.iterrows():
        confound_pct = row["confound_pct"]
        label = f"{confound_pct:.0%}" if not np.isnan(confound_pct) else "N/A"
        ax.text(confound_x, idx, label, va="center", ha="left", fontsize=9, color="#374151")

    ax.axvline(1.0, color="#6b7280", linestyle="--", linewidth=1.2)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(y_labels)
    ax.set_xlabel("Odds ratio")
    ax.set_title("C18 Length Net Effect Attenuation")
    ax.text(confound_x, len(plot_df) - 0.35, "Confounding share",
            ha="left", va="bottom", fontsize=10, color="#111827")
    ax.legend(loc="lower right")
    ax.set_xlim(left=min(0.9, float(np.nanmin(or_values)) - 0.05),
                right=confound_x + 0.18)
    fig.tight_layout()
    picture_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(picture_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


# 主流程


def run_pure_length_effect(
    file_path: Path | str | None = None,
    report_dir: Path | str | None = None,
    table_dir: Path | str | None = None,
    picture_dir: Path | str | None = None,
) -> dict[str, Path]:
    """
    主分析函数：加载全量数据 → 计算全局模型统计量 → 逐子集运行长度嵌套逻辑回归 → 写报告。

    参数说明：
    - file_path  : optimized_data.parquet 路径（默认按 CWD 自动定位）
    - report_dir : 报告输出目录（默认 CWD/Reports）
    - table_dir  : 汇总表输出目录（默认 CWD/Tables）
    - picture_dir: 图片输出目录（默认 CWD/Pictures）
    """
    root        = Path.cwd()
    report_path = (
        Path(report_dir) / "R16_pure_length_effect_report.txt"
        if report_dir else get_path("report", "R16_pure_length_effect_report.txt", root)
    )
    table_path = (
        Path(table_dir) / LENGTH_EFFECT_TABLE_FILE
        if table_dir else get_path("table", LENGTH_EFFECT_TABLE_FILE, root)
    )
    picture_path = (
        Path(picture_dir) / LENGTH_EFFECT_PICTURE_FILE
        if picture_dir else get_path("picture", LENGTH_EFFECT_PICTURE_FILE, root)
    )
    subset_paths = get_analysis_subset_paths(root)

    report_lines: list[str] = []

    # 报告头
    report_lines += [
        "=" * 80,
        "长度偏好净效应分析报告（嵌套逻辑回归）",
        "=" * 80,
        "",
        "【分析框架】",
        "  长度系列（M0→M3）：逐步加入问题特征 → criteria → 模型能力与风格，",
        "                    追踪 z_token_diff_ab 的 β 系数衰减路径。",
        "  混淆比例 = (OR_M0 − OR_M3) / (OR_M0 − 1)",
        "  数据来源：C13 生成的纯净分区子集文件；模型统计量从全量数据统一计算。",
        "",
    ]

    # 步骤 1：加载全量数据（仅用于全局模型统计量计算）
    print("=" * 60)
    print("步骤 1/4：加载全量 optimized_data（仅用于全局模型统计量计算）")
    opt_path   = get_path("optimized", root=root) if file_path is None else Path(file_path)
    df_global  = load_data_global(opt_path)
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

    # 步骤 3：前置验证（能力−长度/格式共线性）
    print("步骤 3/4：验证模型能力−长度/格式共线性")
    validate_model_confounding(model_stats, report_lines)

    # 步骤 4：逐子集运行长度嵌套模型
    print("步骤 4/4：逐子集加载 C13 数据并运行长度嵌套模型（M0→M3）")
    len_results: list[dict | None] = []
    report_lines += [
        "",
        "=" * 80,
        "【长度净效应 — 各子集嵌套模型分析结果（M0 → M3）】",
        "=" * 80,
    ]
    n_subsets = len(subset_paths)
    for i, (name, path) in enumerate(subset_paths.items(), 1):
        print(f"  {i}/{n_subsets}: {name}")
        sub_df = load_subset(path, model_stats)
        len_results.append(run_nested_models_length(sub_df, name, report_lines))

    # 汇总渲染
    report_lines += ["", "=" * 80]
    _render_length_summary(len_results, report_lines)

    # 保存表格与图片
    length_df = build_length_summary_df(len_results)
    if not length_df.empty:
        table_path.parent.mkdir(parents=True, exist_ok=True)
        export_table_bundle(length_df, table_path)
        plot_length_attenuation(length_df, picture_path)

    # 写报告
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"\n报告已写入：{report_path}")
    print("\n任务完成！")
    print("=" * 60)
    return {"report": report_path, "table": table_path, "picture": picture_path}


if __name__ == "__main__":
    run_pure_length_effect()
