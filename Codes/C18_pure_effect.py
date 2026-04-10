# -*- coding: utf-8 -*-
"""
长度与格式偏好净效应分析（配对逻辑回归嵌套模型 + 混淆比例量化）。

研究问题：
  控制问题特征及模型能力差异后，长度差值与格式密度差值对人类偏好的净效应有多大？
  原始效应（r_rb=0.336, R13）中有多少百分比可归因于混淆变量？

分析框架（长度系列）：
  配对偏好逻辑回归，结果变量 winner_a ∈ {0,1}；
  核心预测变量 token_diff_ab = a_tokens − b_tokens（z 标准化）。

  四层嵌套模型（M0 → M3）：
    M0: winner_a ~ z_token_diff_ab                                         [粗效应]
    M1: + 任务类型(CW/IF/MATH/CODE) + z_user_tokens + z_turns              [+问题特征]
    M2: + criteria(7维)                                                     [+问题复杂度]
    M3: + z_ability_diff + z_verbosity_diff + z_format_tendency_diff       [+模型能力与风格]

分析框架（格式系列）：
  三个格式密度差值变量：header/list/bold_density_diff（均 z 标准化）；
  z_token_diff_ab 始终作为固定协变量（控制长度-格式共线性）；
  三变量同时入模型，各系数代表控制其他格式类型后的净边际效应。

  四层嵌套模型（F0 → F3）：
    F0: winner_a ~ z_token_diff_ab + [z_header/list/bold_density_diff]     [粗格式效应，控制长度]
    F1: + 任务类型 + z_user_tokens + z_turns                                [+问题特征]
    F2: + criteria(7维)                                                     [+问题复杂度]
    F3: + z_ability_diff + z_verbosity_diff + z_format_tendency_diff       [+模型能力与风格]

净效应量指标：
  - 调整后 Odds Ratio: exp(β @ 末层)
  - 平均边际效应 AME: β × p̄(1 − p̄)
  - Wald 部分相关 r: z_wald / sqrt(N)
  - 混淆比例: (OR_层0 − OR_层末) / (OR_层0 − 1)

数据来源：
  C13 生成的纯净分区子集文件（Data/optimized_data/*_data.parquet）；
  模型统计量从全量 optimized_data.parquet 统一计算后映射，不在子集内重估。

输出：
  Reports/R16_pure_effect_report.txt

参考：
  References/M03_confounding_analysis.md
"""

import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tools.sm_exceptions import ConvergenceWarning


# ── 路径工厂 ────────────────────────────────────────────────────────────────

def get_optimized_parquet_path(root: Path | str | None = None) -> Path:
    if root is None:
        root = Path.cwd()
    return Path(root) / "Data" / "optimized_data" / "optimized_data.parquet"


def get_report_path(root: Path | str | None = None) -> Path:
    if root is None:
        root = Path.cwd()
    return Path(root) / "Reports" / "R16_pure_effect_report.txt"


def get_subset_paths(root: Path | str | None = None) -> dict[str, Path]:
    """
    返回 C13 生成的各纯净分区子集文件路径映射。

    键为报告中使用的中文子集名，值为对应 parquet 文件的绝对路径。
    全量子集直接指向 optimized_data.parquet（C13 不另存全量文件）。
    """
    if root is None:
        root = Path.cwd()
    d = Path(root) / "Data" / "optimized_data"
    return {
        "全量":           d / "optimized_data.parquet",
        "无类别":         d / "no_category_data.parquet",
        "仅创意写作":     d / "only_cw_data.parquet",
        "仅指令遵循":     d / "only_if_data.parquet",
        "仅数学":         d / "only_math_data.parquet",
        "仅代码":         d / "only_code_data.parquet",
        "创意+指令":      d / "cw_if_data.parquet",
        "创意+代码":      d / "cw_code_data.parquet",
        "指令+数学":      d / "if_math_data.parquet",
        "指令+代码":      d / "if_code_data.parquet",
        "数学+代码":      d / "math_code_data.parquet",
        "指令+数学+代码": d / "if_math_code_data.parquet",
    }


# ── 数据加载与特征构建 ────────────────────────────────────────────────────────

def _safe_count(val) -> int:
    """
    将格式计数列中可能存在的 dict / float / int / None 值统一转换为整数。

    optimized_data 中部分行的 a_header_count 等列仍以 dict 形式存储
    （如 {'h1': 2, 'h2': 1}），需要在分析前统一数值化。
    """
    if isinstance(val, dict):
        return int(sum(val.values()))
    if val is None:
        return 0
    try:
        v = float(val)
        return 0 if np.isnan(v) else int(v)
    except (ValueError, TypeError):
        return 0


def load_data_global(file_path: Path | str | None = None) -> pd.DataFrame:
    """
    加载全量 optimized_data.parquet，仅保留结果明确的配对行。

    仅用于 build_model_stats() 的全局统计计算；
    子集分析从 C13 生成的分区文件读取（见 load_subset）。
    """
    path = get_optimized_parquet_path() if file_path is None else Path(file_path)
    df = pd.read_parquet(path)
    return df[df["winner"].isin(["model_a", "model_b"])].copy()


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
        records[col] = records[col].map(_safe_count)

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
        df[col] = df[col].map(_safe_count)

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
    return add_pair_features(df, model_stats)


# ── 模型拟合工具 ─────────────────────────────────────────────────────────────

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


# ── 标准化辅助 ────────────────────────────────────────────────────────────────

# 所有需要 z-score 标准化的连续型变量
_CONT_VARS: list[str] = [
    "user_tokens", "turns",
    "token_diff_ab",
    "header_density_diff", "list_density_diff", "bold_density_diff",
    "ability_diff", "verbosity_diff", "format_tendency_diff",
]


def _standardize(s: pd.DataFrame) -> pd.DataFrame:
    """
    对连续型变量进行 z-score 标准化，以 _z_ 前缀新增列，原列保留不变。

    标准差为零（常数列）时设为 0.0，不报错。
    """
    s = s.copy()
    for col in _CONT_VARS:
        if col in s.columns:
            mu, sigma = s[col].mean(), s[col].std(ddof=1)
            s[f"_z_{col}"] = (s[col] - mu) / sigma if sigma > 0 else 0.0
    return s


def _active(s: pd.DataFrame, cols: list[str]) -> list[str]:
    """返回 cols 中满足'列存在且 nunique > 1'条件的列名列表。"""
    return [c for c in cols if c in s.columns and s[c].nunique() > 1]


# ── 常量 ──────────────────────────────────────────────────────────────────────

CRITERIA_COLS: list[str] = [
    "complexity", "creativity", "domain_knowledge",
    "problem_solving", "real_world", "specificity", "technical_accuracy",
]

TASK_TYPE_COLS: list[str] = [
    "creative_writing_bool", "if_bool", "math_bool", "code_bool",
]

FORMAT_DENSITY_VARS: list[str] = [
    "header_density_diff", "list_density_diff", "bold_density_diff",
]

FORMAT_DENSITY_LABELS: dict[str, str] = {
    "header_density_diff": "标题密度差",
    "list_density_diff":   "列表密度差",
    "bold_density_diff":   "粗体密度差",
}


# ── 长度嵌套模型（M0 → M3） ───────────────────────────────────────────────────

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

    # ── 写报告块 ──
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


# ── 格式嵌套模型（F0 → F3） ───────────────────────────────────────────────────

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
    z_fmts     = _active(s, z_fmts_all)   # 过滤常数列

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

    # ── 写报告块（每层输出三个密度变量的系数行） ──
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

    # ── 各变量净效应小结 ──
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


# ── 验证：胜率 vs 词冗性 / 格式风格相关性 ────────────────────────────────────

def validate_model_confounding(
    model_stats: pd.DataFrame, report_lines: list[str]
) -> None:
    """
    验证模型能力（胜率）与词冗性/格式风格的 Spearman 相关性。

    若 |Spearman r| > 0.3，证明能力−长度/格式共线性成立，控制 ability_diff 为必要操作。
    """
    from scipy.stats import spearmanr

    valid           = model_stats.dropna(subset=["win_rate", "mean_tokens", "mean_format"])
    r_len, p_len    = spearmanr(valid["win_rate"], valid["mean_tokens"])
    r_fmt, p_fmt    = spearmanr(valid["win_rate"], valid["mean_format"])

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


# ── 汇总渲染 ──────────────────────────────────────────────────────────────────

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


# ── 主流程 ────────────────────────────────────────────────────────────────────

def run_pure_effect(
    file_path: Path | str | None = None,
    report_dir: Path | str | None = None,
) -> None:
    """
    主分析函数：加载全量数据计算模型统计量 → 逐子集读取 C13 文件 →
    运行长度与格式双系列嵌套逻辑回归 → 写报告。

    参数说明：
    - file_path  : optimized_data.parquet 路径（默认按 CWD 自动定位）
    - report_dir : 报告输出目录（默认按 CWD/Reports 定位）
    """
    root        = Path.cwd()
    report_path = (
        Path(report_dir) / "R16_pure_effect_report.txt"
        if report_dir else get_report_path(root)
    )
    subset_paths = get_subset_paths(root)

    report_lines: list[str] = []

    # ── 报告头 ──
    report_lines += [
        "=" * 80,
        "长度与格式偏好净效应分析报告（嵌套逻辑回归）",
        "=" * 80,
        "",
        "【分析框架】",
        "  长度系列（M0→M3）：逐步加入问题特征 → criteria → 模型能力与风格，",
        "                    追踪 z_token_diff_ab 的 β 系数衰减路径。",
        "  格式系列（F0→F3）：同层次结构；z_token_diff_ab 在所有层次作为固定协变量；",
        "                    格式变量：标题/列表/粗体密度差（均 z 标准化），三变量同入模型。",
        "  混淆比例 = (OR_层0 − OR_层末) / (OR_层0 − 1)",
        "  数据来源：C13 生成的纯净分区子集文件；模型统计量从全量数据统一计算。",
        "",
    ]

    # ─ 步骤 1：全量数据 → 全局模型统计量（不使用子集重估，避免小样本偏差）
    print("=" * 60)
    print("步骤 1/5：加载全量 optimized_data（仅用于全局模型统计量计算）")
    opt_path = get_optimized_parquet_path(root) if file_path is None else Path(file_path)
    df_global = pd.read_parquet(opt_path)
    df_global = df_global[df_global["winner"].isin(["model_a", "model_b"])].copy()
    print(f"  全量有效配对行数：{len(df_global):,}")

    print("步骤 2/5：计算全局模型统计量（胜率 / 词冗性 / 格式风格）")
    model_stats = build_model_stats(df_global)
    print(f"  模型总数：{len(model_stats)}")
    del df_global  # 释放内存

    report_lines.append("【模型统计量一览（按胜率排序，Top-10）】")
    for name, row in model_stats.sort_values("win_rate", ascending=False).head(10).iterrows():
        report_lines.append(
            f"  {name:<50}  胜率={row['win_rate']:.4f}  "
            f"均长={row['mean_tokens']:>7.1f}  均格式={row['mean_format']:>5.1f}"
        )

    # ─ 步骤 3：前置验证
    print("步骤 3/5：验证模型能力−长度/格式共线性")
    validate_model_confounding(model_stats, report_lines)

    # ─ 步骤 4：长度嵌套模型
    print("步骤 4/5：逐子集加载 C13 数据并运行长度嵌套模型（M0→M3）")
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

    # ─ 步骤 5：格式嵌套模型
    print("步骤 5/5：逐子集运行格式嵌套模型（F0→F3）")
    fmt_results: list[dict | None] = []
    report_lines += [
        "",
        "=" * 80,
        "【格式净效应 — 各子集嵌套模型分析结果（F0 → F3）】",
        "=" * 80,
    ]
    for i, (name, path) in enumerate(subset_paths.items(), 1):
        print(f"  {i}/{n_subsets}: {name}（格式）")
        sub_df = load_subset(path, model_stats)
        fmt_results.append(run_nested_models_format(sub_df, name, report_lines))

    # ─ 汇总
    report_lines += ["", "=" * 80]
    _render_length_summary(len_results, report_lines)
    _render_format_summary(fmt_results, report_lines)

    # ─ 写文件
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"\n报告已写入：{report_path}")
    print("\n任务完成！")
    print("=" * 60)


if __name__ == "__main__":
    run_pure_effect()
