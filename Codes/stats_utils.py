"""
stats_utils

提供分析阶段复用的统计预处理 helper。

本模块只负责数值预处理与列筛选，不负责路径管理、schema 访问或模型拟合。
"""

from collections.abc import Iterable

import numpy as np
import pandas as pd


def zscore_series(series: pd.Series) -> pd.Series:
    """对连续变量做 z-score 标准化，常数列返回 0。"""

    mu = float(series.mean())
    sigma = float(series.std(ddof=1))
    if sigma <= 0 or np.isnan(sigma):
        return pd.Series(np.zeros(len(series)), index=series.index, dtype=float)
    return ((series - mu) / sigma).astype(float)


def active_nonconstant_columns(df: pd.DataFrame,
                               candidate_columns: Iterable[str]) -> list[str]:
    """返回当前数据中存在且非常数的候选列。"""

    return [
        column for column in candidate_columns
        if column in df.columns and df[column].nunique(dropna=True) > 1
    ]
