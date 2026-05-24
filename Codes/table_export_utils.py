"""
论文表格导出辅助工具。

保留原始 CSV 的同时，为核心结果表生成适合嵌入论文的中文 CSV 与 Markdown 版本。
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import pandas as pd


FEATURE_LABELS: dict[str, str] = {
    "header": "标题",
    "list": "列表",
    "bold": "粗体",
    "header_density_diff": "标题密度差",
    "list_density_diff": "列表密度差",
    "bold_density_diff": "粗体密度差",
}

VARIABLE_LABELS: dict[str, str] = {
    "ability_diff": "能力差",
    "verbosity_diff": "冗长度差",
    "format_tendency_diff": "格式倾向差",
    "user_tokens": "用户输入长度",
    "turns": "对话轮数",
    "token_diff_ab": "回答长度差",
    "header_density_diff": "标题密度差",
    "bold_density_diff": "粗体密度差",
    "list_density_diff": "列表密度差",
    "winner_a": "A 模型获胜",
    "creative_writing_bool": "创意写作任务",
    "if_bool": "指令遵循任务",
    "math_bool": "数学任务",
    "code_bool": "代码任务",
}

STAGE_LABELS: dict[str, str] = {
    "before": "匹配前",
    "after": "匹配后",
}

RELATION_LABELS: dict[str, str] = {
    "~": "回归",
    "~~": "协方差",
    "~1": "截距",
}

PAPER_READY_DIRNAME = "paper_ready"
BRIEF_READY_DIRNAME = "brief"
RAW_FLOAT_DECIMALS = 4
RAW_P_VALUE_SIGNIFICANT_DIGITS = 6
MAX_BRIEF_COLUMNS = 8
TOP_CORRELATION_ROWS = 12


def export_table_bundle(
    df: pd.DataFrame,
    table_path: Path | str,
    *,
    index: bool = False,
) -> dict[str, Path]:
    """
    导出原始表格及论文版伴随文件。

    参数说明：
    - df：待保存的数据表
    - table_path：原始 CSV 保存路径
    - index：是否保留索引（默认 False）

    返回值：
    - 实际写入的文件路径字典
    """

    table_path = Path(table_path)
    export_df = build_raw_export_table(df)
    table_path.parent.mkdir(parents=True, exist_ok=True)
    export_df.to_csv(table_path, index=index, encoding="utf-8-sig")

    outputs = {"raw_csv": table_path}
    outputs.update(export_paper_companions(df, table_path))
    return outputs


def export_paper_companions(
    df: pd.DataFrame,
    table_path: Path | str,
) -> dict[str, Path]:
    """
    为既有数据表生成论文版与简表版 CSV / Markdown 伴随文件。

    参数说明：
    - df：原始表格数据
    - table_path：原始 CSV 路径

    返回值：
    - 导出文件路径字典；若当前表格未配置论文版模板，则返回空字典
    """

    table_path = Path(table_path)
    paper_df = build_paper_ready_table(df, table_path)
    if paper_df is None or paper_df.empty:
        return {}

    brief_df = build_brief_ready_table(df, table_path)

    paper_dir = table_path.parent / PAPER_READY_DIRNAME
    paper_dir.mkdir(parents=True, exist_ok=True)
    brief_dir = paper_dir / BRIEF_READY_DIRNAME
    brief_dir.mkdir(parents=True, exist_ok=True)

    paper_csv_path = paper_dir / f"{table_path.stem}_paper.csv"
    paper_md_path = paper_dir / f"{table_path.stem}_paper.md"
    brief_csv_path = brief_dir / f"{table_path.stem}_brief.csv"
    brief_md_path = brief_dir / f"{table_path.stem}_brief.md"

    paper_df.to_csv(paper_csv_path, index=False, encoding="utf-8-sig")
    paper_md_path.write_text(dataframe_to_markdown(paper_df), encoding="utf-8")
    if brief_df is not None and not brief_df.empty:
        brief_df.to_csv(brief_csv_path, index=False, encoding="utf-8-sig")
        brief_md_path.write_text(dataframe_to_markdown(brief_df), encoding="utf-8")

    return {
        "paper_csv": paper_csv_path,
        "paper_md": paper_md_path,
        "brief_csv": brief_csv_path,
        "brief_md": brief_md_path,
    }


def export_existing_paper_tables(
    table_dir: Path | str | None = None,
    *,
    refresh_raw: bool = False,
) -> dict[str, dict[str, Path]]:
    """
    为现有核心结果表批量补生成论文版伴随文件。

    参数说明：
    - table_dir：表格目录（默认 Tables）
    - refresh_raw：是否同步重写原始 CSV（默认 False）

    返回值：
    - 以表格 stem 为键的输出路径字典
    """

    if table_dir is None:
        table_dir = Path.cwd() / "Tables"
    else:
        table_dir = Path(table_dir)

    outputs: dict[str, dict[str, Path]] = {}
    for stem in PAPER_BUILDERS:
        csv_path = table_dir / f"{stem}.csv"
        if not csv_path.exists():
            continue
        df = pd.read_csv(csv_path)
        if refresh_raw:
            bundle_outputs = export_table_bundle(df, csv_path)
        else:
            bundle_outputs = export_paper_companions(df, csv_path)
        if bundle_outputs:
            outputs[stem] = bundle_outputs
    return outputs


def build_raw_export_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    对原始结果表执行统一的导出位数控制。

    参数说明：
    - df：待导出的原始结果表

    返回值：
    - 已按列类型控位数的数据表副本
    """

    export_df = df.copy()
    for column in export_df.columns:
        series = export_df[column]
        if not pd.api.types.is_float_dtype(series):
            continue

        if _is_p_value_column(column):
            export_df[column] = series.map(
                lambda value: _round_significant(value, RAW_P_VALUE_SIGNIFICANT_DIGITS)
            )
        else:
            export_df[column] = series.round(RAW_FLOAT_DECIMALS)

    return export_df


def build_paper_ready_table(
    df: pd.DataFrame,
    table_path: Path | str,
) -> pd.DataFrame | None:
    """按表格编号分派论文版整形逻辑。"""

    stem = Path(table_path).stem
    builder = PAPER_BUILDERS.get(stem)
    if builder is None:
        return None
    return builder(df.copy())


def build_brief_ready_table(
    df: pd.DataFrame,
    table_path: Path | str,
) -> pd.DataFrame | None:
    """按表格编号分派简表整形逻辑，并限制列数不超过 8 列。"""

    stem = Path(table_path).stem
    builder = BRIEF_BUILDERS.get(stem)
    if builder is None:
        return None

    brief_df = builder(df.copy())
    if brief_df.shape[1] > MAX_BRIEF_COLUMNS:
        raise ValueError(f"{stem} 简表列数超过 {MAX_BRIEF_COLUMNS} 列")
    return brief_df


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    """将 DataFrame 渲染为 Markdown 表格。"""

    text_df = df.astype(object).where(pd.notna(df), "").astype(str)
    headers = "| " + " | ".join(_escape_markdown(col) for col in text_df.columns) + " |"
    separator = "| " + " | ".join("---" for _ in text_df.columns) + " |"

    rows = []
    for _, row in text_df.iterrows():
        rows.append("| " + " | ".join(_escape_markdown(value) for value in row.tolist()) + " |")

    return "\n".join([headers, separator, *rows]) + "\n"


def _escape_markdown(value: object) -> str:
    text = str(value)
    return text.replace("|", "\\|").replace("\n", "<br>")


def _format_count(value: object) -> str:
    if pd.isna(value):
        return ""
    return f"{int(round(float(value))):,}"


def _format_decimal(
    value: object,
    digits: int = 3,
    *,
    signed: bool = False,
) -> str:
    if pd.isna(value):
        return ""
    number = float(value)
    sign = "+" if signed else ""
    return f"{number:{sign}.{digits}f}"


def _format_percent_fraction(value: object, digits: int = 2) -> str:
    if pd.isna(value):
        return ""
    return f"{float(value) * 100:.{digits}f}"


def _is_p_value_column(column_name: str) -> bool:
    text = column_name.lower()
    return (
        text == "p_value"
        or "p_value" in text
        or text.startswith("p_")
        or text.endswith("_p")
        or "_p_" in text
        or text.endswith(" p")
        or "p-value" in text
    )


def _round_significant(value: object, digits: int) -> float | object:
    if pd.isna(value):
        return value
    return float(f"{float(value):.{digits}g}")


def _format_percent(value: object, digits: int = 1) -> str:
    if pd.isna(value):
        return ""
    return f"{float(value):.{digits}f}"


def _format_p_value(value: object) -> str:
    if pd.isna(value):
        return ""
    number = float(value)
    if number < 0.001:
        return "<0.001"
    return f"{number:.3f}"


def _format_interval(
    low: object,
    high: object,
    digits: int = 3,
    *,
    signed: bool = False,
) -> str:
    if pd.isna(low) or pd.isna(high):
        return ""
    low_text = _format_decimal(low, digits=digits, signed=signed)
    high_text = _format_decimal(high, digits=digits, signed=signed)
    return f"[{low_text}, {high_text}]"


def _format_or_ci(estimate: object, low: object, high: object, digits: int = 3) -> str:
    if pd.isna(estimate) or pd.isna(low) or pd.isna(high):
        return ""
    estimate_text = _format_decimal(estimate, digits=digits)
    ci_text = _format_interval(low, high, digits=digits)
    return f"{estimate_text} {ci_text}"


def _format_bool(value: object) -> str:
    if pd.isna(value):
        return ""
    return "是" if bool(value) else "否"


def _map_feature(value: object) -> str:
    text = str(value)
    return FEATURE_LABELS.get(text, text)


def _map_variable(value: object) -> str:
    text = str(value)
    return VARIABLE_LABELS.get(text, text)


def _extract_top_correlations(df: pd.DataFrame, top_n: int = TOP_CORRELATION_ROWS) -> pd.DataFrame:
    """从相关矩阵中提取绝对值最高的唯一变量对。"""

    row_col = df.columns[0]
    rows: list[dict[str, object]] = []
    seen_pairs: set[tuple[str, str]] = set()

    for _, row in df.iterrows():
        row_name = str(row[row_col])
        for column in df.columns[1:]:
            col_name = str(column)
            if row_name == col_name:
                continue

            pair_key = tuple(sorted((row_name, col_name)))
            if pair_key in seen_pairs:
                continue

            value = row[column]
            if pd.isna(value):
                continue

            corr = float(value)
            rows.append(
                {
                    "变量 1": _map_variable(row_name),
                    "变量 2": _map_variable(col_name),
                    "相关系数 r": _format_decimal(corr),
                    "|r|": _format_decimal(abs(corr)),
                }
            )
            seen_pairs.add(pair_key)

    corr_df = pd.DataFrame(rows)
    if corr_df.empty:
        return corr_df

    return corr_df.sort_values("|r|", ascending=False).head(top_n).reset_index(drop=True)


def _paper_t03(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "子集": df["label"],
            "有效配对数": df["n_pairs"].map(_format_count),
            "胜者更长比例（%）": df["pct_winner_longer"].map(_format_percent),
            "中位长度差（tokens）": df["median_diff"].map(lambda x: _format_decimal(x, digits=1, signed=True)),
            "95% 置信区间": [
                _format_interval(low, high, digits=1, signed=True)
                for low, high in zip(df["ci_low"], df["ci_high"])
            ],
            "校正后 p 值": df["p_bonferroni"].map(_format_p_value),
            "rank-biserial r": df["rank_biserial_r"].map(_format_decimal),
            "Cohen's d": df["cohen_d"].map(_format_decimal),
            "Hedges' g": df["hedges_g"].map(_format_decimal),
            "效应分级": df["effect_level"],
            "显著性": df["significant"].map(_format_bool),
        }
    )


def _paper_t04(df: pd.DataFrame) -> pd.DataFrame:
    paper_df = pd.DataFrame(
        {
            "子集": df["subset"],
            "格式特征": df["feature"].map(_map_feature),
            "有效配对数": df["n_pairs"].map(_format_count),
            "胜者格式更多比例（%）": df["pct_winner_more"].map(_format_percent),
            "中位计数差": df["median_diff"].map(lambda x: _format_decimal(x, digits=1, signed=True)),
            "95% 置信区间": [
                _format_interval(low, high, digits=1, signed=True)
                for low, high in zip(df["ci_low"], df["ci_high"])
            ],
            "校正后 p 值": df["p_bonferroni"].map(_format_p_value),
            "rank-biserial r": df["rank_biserial_r"].map(_format_decimal),
            "中位密度差": df["density_median_diff"].map(lambda x: _format_decimal(x, digits=4, signed=True)),
            "密度检验 p 值": df["density_p_value"].map(_format_p_value),
            "效应分级": df["effect_level"],
            "显著性": df["significant"].map(_format_bool),
        }
    )
    if "chisq_presence_p" in df.columns and df["chisq_presence_p"].notna().any():
        paper_df["存在性卡方 p 值"] = df["chisq_presence_p"].map(_format_p_value)
    return paper_df


def _paper_t05(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "子集": df["subset"],
            "样本量": df["n"].map(_format_count),
            "粗模型 OR（M0）": df["or0"].map(_format_decimal),
            "完整模型 OR（M3）": df["or3"].map(_format_decimal),
            "调整后 Wald r": df["wald_r_adj"].map(_format_decimal),
            "调整后 AME": df["ame_adj"].map(_format_decimal),
            "M0 pseudo-R²": df["r2_m0"].map(_format_decimal),
            "M3 pseudo-R²": df["r2_m3"].map(_format_decimal),
            "混淆解释比例（%）": df["confound_pct"].map(lambda x: _format_percent_fraction(x, digits=1)),
        }
    )


def _paper_t06(df: pd.DataFrame) -> pd.DataFrame:
    feature_series = df["feature_label"] if "feature_label" in df.columns else df["feature"].map(_map_feature)
    return pd.DataFrame(
        {
            "子集": df["subset"],
            "格式特征": feature_series,
            "样本量": df["n"].map(_format_count),
            "粗模型 OR（F0）": df["or_f0"].map(_format_decimal),
            "完整模型 OR（F3）": df["or_f3"].map(_format_decimal),
            "F0 pseudo-R²": df["r2_f0"].map(_format_decimal),
            "F3 pseudo-R²": df["r2_f3"].map(_format_decimal),
            "混淆解释比例（%）": df["confound_pct"].map(lambda x: _format_percent_fraction(x, digits=1)),
        }
    )


def _paper_t07(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "子集": df["subset"],
            "样本量": df["n"].map(_format_count),
            "更长侧获胜率（%）": df["longer_win_rate"].map(_format_percent_fraction),
            "粗 OR [95% CI]": [
                _format_or_ci(estimate, low, high)
                for estimate, low, high in zip(df["crude_or"], df["crude_or_ci_low"], df["crude_or_ci_high"])
            ],
            "粗 p 值": df["crude_p"].map(_format_p_value),
            "调整 OR [95% CI]": [
                _format_or_ci(estimate, low, high)
                for estimate, low, high in zip(df["adjusted_or"], df["adjusted_or_ci_low"], df["adjusted_or_ci_high"])
            ],
            "调整 p 值": df["adjusted_p"].map(_format_p_value),
            "IPW ATE [95% CI]": [
                f"{_format_decimal(estimate)} {_format_interval(low, high)}"
                for estimate, low, high in zip(df["ipw_ate"], df["ipw_ci_low"], df["ipw_ci_high"])
            ],
            "有效样本量 ESS": df["ipw_ess"].map(lambda x: _format_decimal(x, digits=1)),
            "Bootstrap 成功次数": df["bootstrap_success"].map(_format_count),
        }
    )


def _paper_t08(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "子集": df["subset"],
            "格式特征": df["feature"].map(_map_feature),
            "分析角色": df["role"],
            "样本量": df["n"].map(_format_count),
            "处理组获胜率（%）": df["format_win_rate"].map(_format_percent_fraction),
            "粗 OR [95% CI]": [
                _format_or_ci(estimate, low, high)
                for estimate, low, high in zip(df["crude_or"], df["crude_or_ci_low"], df["crude_or_ci_high"])
            ],
            "粗 p 值": df["crude_p"].map(_format_p_value),
            "调整 OR [95% CI]": [
                _format_or_ci(estimate, low, high)
                for estimate, low, high in zip(df["adjusted_or"], df["adjusted_or_ci_low"], df["adjusted_or_ci_high"])
            ],
            "调整 p 值": df["adjusted_p"].map(_format_p_value),
            "IPW ATE [95% CI]": [
                f"{_format_decimal(estimate)} {_format_interval(low, high)}"
                for estimate, low, high in zip(df["ipw_ate"], df["ipw_ci_low"], df["ipw_ci_high"])
            ],
            "有效样本量 ESS": df["ipw_ess"].map(lambda x: _format_decimal(x, digits=1)),
            "Bootstrap 成功次数": df["bootstrap_success"].map(_format_count),
        }
    )


def _paper_t09(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "子集": df["subset"],
            "原始样本量": df["n"].map(_format_count),
            "处理组样本量": df["treated_n"].map(_format_count),
            "对照组样本量": df["control_n"].map(_format_count),
            "匹配对数": df["matched_pairs"].map(_format_count),
            "匹配率（%）": df["match_rate"].map(_format_percent_fraction),
            "卡钳宽度": df["caliper"].map(_format_decimal),
            "平均匹配距离": df["mean_distance"].map(_format_decimal),
            "最大匹配距离": df["max_distance"].map(_format_decimal),
            "公共支持区间": [
                _format_interval(low, high)
                for low, high in zip(df["overlap_low"], df["overlap_high"])
            ],
            "公共支持覆盖率（%）": df["common_support_share"].map(_format_percent_fraction),
            "匹配前 max|SMD|": df["max_abs_smd_before"].map(_format_decimal),
            "匹配后 max|SMD|": df["max_abs_smd_after"].map(_format_decimal),
            "匹配前 mean|SMD|": df["mean_abs_smd_before"].map(_format_decimal),
            "匹配后 mean|SMD|": df["mean_abs_smd_after"].map(_format_decimal),
            "匹配后 ATE": df["matched_ate"].map(_format_decimal),
            "Wilcoxon p 值": df["wilcoxon_p"].map(_format_p_value),
        }
    )


def _paper_t10(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "子集": df["subset"],
            "阶段": df["stage"].map(lambda x: STAGE_LABELS.get(str(x), str(x))),
            "协变量": df["variable"].map(_map_variable),
            "处理组均值": df["treated_mean"].map(_format_decimal),
            "对照组均值": df["control_mean"].map(_format_decimal),
            "标准化均值差 SMD": df["smd"].map(_format_decimal),
        }
    )


def _paper_t11(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "变量": df["variable"].map(_map_variable),
            "层级": df["layer"],
            "类型": df["type"],
            "样本量": df["n"].map(_format_count),
            "缺失值个数": df["missing"].map(_format_count),
            "缺失率（%）": df["missing_pct"].map(_format_percent_fraction),
            "均值": df["mean"].map(_format_decimal),
            "标准差": df["std"].map(_format_decimal),
            "最小值": df["min"].map(_format_decimal),
            "P25": df["p25"].map(_format_decimal),
            "中位数": df["median"].map(_format_decimal),
            "P75": df["p75"].map(_format_decimal),
            "最大值": df["max"].map(_format_decimal),
            "正值比例（%）": df["positive_rate"].map(_format_percent_fraction),
        }
    )


def _paper_t12(df: pd.DataFrame) -> pd.DataFrame:
    renamed = df.rename(columns={column: _map_variable(column) for column in df.columns})
    first_col = renamed.columns[0]
    renamed[first_col] = renamed[first_col].map(_map_variable)

    for column in renamed.columns[1:]:
        renamed[column] = renamed[column].map(_format_decimal)

    renamed = renamed.rename(columns={first_col: "变量"})
    return renamed


def _paper_t13(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "模型": df["model_name"],
            "自由度": df["DoF"].map(_format_count),
            "卡方统计量": df["chi2"].map(_format_decimal),
            "卡方检验 p 值": df["chi2 p-value"].map(_format_p_value),
            "CFI": df["CFI"].map(_format_decimal),
            "TLI": df["TLI"].map(_format_decimal),
            "GFI": df["GFI"].map(_format_decimal),
            "AGFI": df["AGFI"].map(_format_decimal),
            "NFI": df["NFI"].map(_format_decimal),
            "RMSEA": df["RMSEA"].map(_format_decimal),
            "AIC": df["AIC"].map(_format_decimal),
            "BIC": df["BIC"].map(_format_decimal),
        }
    )


def _paper_t14(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "模型": df["model_name"],
            "因变量": df["lval"].map(_map_variable),
            "关系": df["op"].map(lambda x: RELATION_LABELS.get(str(x), str(x))),
            "自变量": df["rval"].map(_map_variable),
            "估计值": df["Estimate"].map(_format_decimal),
            "标准误": df["Std. Err"].map(_format_decimal),
            "z 值": df["z-value"].map(_format_decimal),
            "p 值": df["p-value"].map(_format_p_value),
        }
    )


def _paper_t15(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "效应": df["effect"],
            "点估计": df["estimate"].map(_format_decimal),
            "Bootstrap 均值": df["boot_mean"].map(_format_decimal),
            "Bootstrap 标准差": df["boot_std"].map(_format_decimal),
            "95% 置信区间": [
                _format_interval(low, high)
                for low, high in zip(df["ci_low"], df["ci_high"])
            ],
            "成功重采样数": df["successful_bootstrap_n"].map(_format_count),
            "95% CI 排除 0": df["exclude_zero"].map(_format_bool),
        }
    )


def _brief_t03(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "子集": df["label"],
            "有效配对数": df["n_pairs"].map(_format_count),
            "胜者更长比例（%）": df["pct_winner_longer"].map(_format_percent),
            "中位长度差": df["median_diff"].map(lambda x: _format_decimal(x, digits=1, signed=True)),
            "校正后 p 值": df["p_bonferroni"].map(_format_p_value),
            "rank-biserial r": df["rank_biserial_r"].map(_format_decimal),
            "效应分级": df["effect_level"],
            "显著性": df["significant"].map(_format_bool),
        }
    )


def _brief_t04(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "子集": df["subset"],
            "格式特征": df["feature"].map(_map_feature),
            "有效配对数": df["n_pairs"].map(_format_count),
            "胜者格式更多比例（%）": df["pct_winner_more"].map(_format_percent),
            "中位计数差": df["median_diff"].map(lambda x: _format_decimal(x, digits=1, signed=True)),
            "校正后 p 值": df["p_bonferroni"].map(_format_p_value),
            "rank-biserial r": df["rank_biserial_r"].map(_format_decimal),
            "显著性": df["significant"].map(_format_bool),
        }
    )


def _brief_t05(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "子集": df["subset"],
            "样本量": df["n"].map(_format_count),
            "粗模型 OR": df["or0"].map(_format_decimal),
            "完整模型 OR": df["or3"].map(_format_decimal),
            "调整后 AME": df["ame_adj"].map(_format_decimal),
            "调整后 Wald r": df["wald_r_adj"].map(_format_decimal),
            "混淆解释比例（%）": df["confound_pct"].map(lambda x: _format_percent_fraction(x, digits=1)),
        }
    )


def _brief_t06(df: pd.DataFrame) -> pd.DataFrame:
    feature_series = df["feature_label"] if "feature_label" in df.columns else df["feature"].map(_map_feature)
    return pd.DataFrame(
        {
            "子集": df["subset"],
            "格式特征": feature_series,
            "样本量": df["n"].map(_format_count),
            "粗模型 OR": df["or_f0"].map(_format_decimal),
            "完整模型 OR": df["or_f3"].map(_format_decimal),
            "F3 pseudo-R²": df["r2_f3"].map(_format_decimal),
            "混淆解释比例（%）": df["confound_pct"].map(lambda x: _format_percent_fraction(x, digits=1)),
        }
    )


def _brief_t07(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "子集": df["subset"],
            "样本量": df["n"].map(_format_count),
            "更长侧获胜率（%）": df["longer_win_rate"].map(_format_percent_fraction),
            "粗 OR": df["crude_or"].map(_format_decimal),
            "调整 OR": df["adjusted_or"].map(_format_decimal),
            "IPW ATE": df["ipw_ate"].map(_format_decimal),
            "调整 p 值": df["adjusted_p"].map(_format_p_value),
            "有效样本量 ESS": df["ipw_ess"].map(lambda x: _format_decimal(x, digits=1)),
        }
    )


def _brief_t08(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "子集": df["subset"],
            "格式特征": df["feature"].map(_map_feature),
            "分析角色": df["role"],
            "样本量": df["n"].map(_format_count),
            "处理组获胜率（%）": df["format_win_rate"].map(_format_percent_fraction),
            "调整 OR": df["adjusted_or"].map(_format_decimal),
            "IPW ATE": df["ipw_ate"].map(_format_decimal),
            "调整 p 值": df["adjusted_p"].map(_format_p_value),
        }
    )


def _brief_t09(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "子集": df["subset"],
            "原始样本量": df["n"].map(_format_count),
            "匹配对数": df["matched_pairs"].map(_format_count),
            "匹配率（%）": df["match_rate"].map(_format_percent_fraction),
            "匹配后 max|SMD|": df["max_abs_smd_after"].map(_format_decimal),
            "匹配后 mean|SMD|": df["mean_abs_smd_after"].map(_format_decimal),
            "匹配后 ATE": df["matched_ate"].map(_format_decimal),
            "Wilcoxon p 值": df["wilcoxon_p"].map(_format_p_value),
        }
    )


def _brief_t10(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "子集": df["subset"],
            "阶段": df["stage"].map(lambda x: STAGE_LABELS.get(str(x), str(x))),
            "协变量": df["variable"].map(_map_variable),
            "标准化均值差 SMD": df["smd"].map(_format_decimal),
        }
    )


def _brief_t11(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "变量": df["variable"].map(_map_variable),
            "层级": df["layer"],
            "类型": df["type"],
            "样本量": df["n"].map(_format_count),
            "缺失率（%）": df["missing_pct"].map(_format_percent_fraction),
            "均值": df["mean"].map(_format_decimal),
            "标准差": df["std"].map(_format_decimal),
            "中位数": df["median"].map(_format_decimal),
        }
    )


def _brief_t12(df: pd.DataFrame) -> pd.DataFrame:
    return _extract_top_correlations(df)


def _brief_t13(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "模型": df["model_name"],
            "卡方统计量": df["chi2"].map(_format_decimal),
            "卡方检验 p 值": df["chi2 p-value"].map(_format_p_value),
            "CFI": df["CFI"].map(_format_decimal),
            "TLI": df["TLI"].map(_format_decimal),
            "RMSEA": df["RMSEA"].map(_format_decimal),
            "AIC": df["AIC"].map(_format_decimal),
            "BIC": df["BIC"].map(_format_decimal),
        }
    )


def _brief_t14(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "模型": df["model_name"],
            "因变量": df["lval"].map(_map_variable),
            "关系": df["op"].map(lambda x: RELATION_LABELS.get(str(x), str(x))),
            "自变量": df["rval"].map(_map_variable),
            "估计值": df["Estimate"].map(_format_decimal),
            "标准误": df["Std. Err"].map(_format_decimal),
            "p 值": df["p-value"].map(_format_p_value),
        }
    )


def _brief_t15(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "效应": df["effect"],
            "点估计": df["estimate"].map(_format_decimal),
            "Bootstrap 均值": df["boot_mean"].map(_format_decimal),
            "95% 置信区间": [
                _format_interval(low, high)
                for low, high in zip(df["ci_low"], df["ci_high"])
            ],
            "成功重采样数": df["successful_bootstrap_n"].map(_format_count),
            "95% CI 排除 0": df["exclude_zero"].map(_format_bool),
        }
    )


PAPER_BUILDERS: dict[str, Callable[[pd.DataFrame], pd.DataFrame]] = {
    "T03_length_wilcoxon_summary": _paper_t03,
    "T04_format_test_summary": _paper_t04,
    "T05_pure_length_net_effect_summary": _paper_t05,
    "T06_pure_format_net_effect_summary": _paper_t06,
    "T07_length_robust_summary": _paper_t07,
    "T08_format_robust_summary": _paper_t08,
    "T09_matching_summary": _paper_t09,
    "T10_matching_balance": _paper_t10,
    "T11_sem_layer_stats": _paper_t11,
    "T12_sem_correlations": _paper_t12,
    "T13_sem_model_comparison": _paper_t13,
    "T14_sem_path_estimates": _paper_t14,
    "T15_sem_bootstrap_effects_ci": _paper_t15,
}


BRIEF_BUILDERS: dict[str, Callable[[pd.DataFrame], pd.DataFrame]] = {
    "T03_length_wilcoxon_summary": _brief_t03,
    "T04_format_test_summary": _brief_t04,
    "T05_pure_length_net_effect_summary": _brief_t05,
    "T06_pure_format_net_effect_summary": _brief_t06,
    "T07_length_robust_summary": _brief_t07,
    "T08_format_robust_summary": _brief_t08,
    "T09_matching_summary": _brief_t09,
    "T10_matching_balance": _brief_t10,
    "T11_sem_layer_stats": _brief_t11,
    "T12_sem_correlations": _brief_t12,
    "T13_sem_model_comparison": _brief_t13,
    "T14_sem_path_estimates": _brief_t14,
    "T15_sem_bootstrap_effects_ci": _brief_t15,
}