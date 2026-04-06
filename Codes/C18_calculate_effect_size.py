# -*- coding: utf-8 -*-
"""
Effect size analysis based on existing length/format preference tests.
目标：结合现有 C16/C17 数据结论，计算效应量并输出易读报告。

内容：
- 主要指标：Cohen's d / Hedges' g / Rank-biserial correlation / Wilcoxon r
- 适用变量：token_diff（长度偏好）+ header/list/bold diff（格式偏好）
- 子集：Overall + 11 分类子集

输出：Reports/R12_effect_size_report.txt
"""

import os
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon, norm


def get_token_diff(df):
    if df.empty:
        return pd.Series([], dtype=float)
    def diff(r):
        if r['winner'] == 'model_a':
            return r['a_tokens'] - r['b_tokens']
        return r['b_tokens'] - r['a_tokens']
    return df.apply(diff, axis=1)


def get_feature_diff(df, feature):
    def get_count(value):
        if isinstance(value, dict):
            return sum(value.values())
        if pd.isna(value):
            return 0
        try:
            return float(value)
        except Exception:
            return 0

    def diff(r):
        a = get_count(r[f'a_{feature}_counts'])
        b = get_count(r[f'b_{feature}_counts'])
        if r['winner'] == 'model_a':
            return a - b
        return b - a

    return df.apply(diff, axis=1)


def compute_effect_sizes(diff_series):
    if diff_series.empty:
        return {}

    diff_nonzero = diff_series[diff_series != 0.0]
    n = len(diff_nonzero)
    if n == 0:
        return {
            'n': 0,
            'mean_diff': 0.0,
            'sd_diff': 0.0,
            'cohen_d': np.nan,
            'hedges_g': np.nan,
            'rank_biserial': np.nan,
            'wilcoxon_T': np.nan,
            'wilcoxon_p': np.nan,
            'wilcoxon_r': np.nan,
            'interpretation': 'No nonzero differences',
        }

    mean_diff = diff_nonzero.mean()
    sd_diff = diff_nonzero.std(ddof=1)
    cohen_d = mean_diff / sd_diff if sd_diff > 0 else np.nan
    hedges_g = cohen_d * (1 - 3 / (4 * n - 9)) if n > 2 and not np.isnan(cohen_d) else np.nan
    positive = (diff_nonzero > 0).sum()
    negative = (diff_nonzero < 0).sum()
    rank_biserial = (positive - negative) / n

    try:
        T, p_value = wilcoxon(diff_nonzero, alternative='greater')
        z = norm.isf(p_value if p_value > 0 else 1e-16)
        r = z / np.sqrt(n)
    except Exception:
        T, p_value, r = np.nan, np.nan, np.nan

    if abs(cohen_d) < 0.2:
        interpretation = 'negligible'
    elif abs(cohen_d) < 0.5:
        interpretation = 'small'
    elif abs(cohen_d) < 0.8:
        interpretation = 'medium'
    else:
        interpretation = 'large'

    return {
        'n': n,
        'mean_diff': mean_diff,
        'sd_diff': sd_diff,
        'cohen_d': cohen_d,
        'hedges_g': hedges_g,
        'rank_biserial': rank_biserial,
        'wilcoxon_T': T,
        'wilcoxon_p': p_value,
        'wilcoxon_r': r,
        'interpretation': interpretation,
    }


def subset_effect_size_report(df):
    subsets = {
        'Overall': df,
        'Creative Writing': df[df['creative_writing_bool'] == True],
        'Instruction Following': df[df['if_bool'] == True],
        'Math': df[df['math_bool'] == True],
        'Only Creative Writing': df[(df['creative_writing_bool'] == True) & (df['if_bool'] == False) & (df['math_bool'] == False)],
        'Only IF': df[(df['creative_writing_bool'] == False) & (df['if_bool'] == True) & (df['math_bool'] == False)],
        'Only Math': df[(df['creative_writing_bool'] == False) & (df['if_bool'] == False) & (df['math_bool'] == True)],
        'CW & IF': df[(df['creative_writing_bool'] == True) & (df['if_bool'] == True)],
        'CW & Math': df[(df['creative_writing_bool'] == True) & (df['math_bool'] == True)],
        'IF & Math': df[(df['if_bool'] == True) & (df['math_bool'] == True)],
        'All Categories': df[(df['creative_writing_bool'] == True) & (df['if_bool'] == True) & (df['math_bool'] == True)],
        'No Category': df[(df['creative_writing_bool'] == False) & (df['if_bool'] == False) & (df['math_bool'] == False)],
    }

    report = []
    report.append('Effect Size Analysis Report')
    report.append('=' * 110)
    report.append('Overall direction: judge whether winning model tends to be longer / richer format')

    tokens = sorted(list(subsets.items()), key=lambda x: x[0])

    report.append('\nToken length effect size (winner - loser)')
    report.append('-' * 110)
    for subset_name, subset_df in tokens:
        diff = get_token_diff(subset_df)
        stats_ = compute_effect_sizes(diff)
        report.append(f"{subset_name}: n_nonzero={stats_['n']:,}, mean_diff={stats_['mean_diff']:.3f}, sd_diff={stats_['sd_diff']:.3f}, cohen_d={stats_['cohen_d']:.3f}, hedges_g={stats_['hedges_g']:.3f}, rank_biserial={stats_['rank_biserial']:.3f}, wilcoxon_r={stats_['wilcoxon_r']:.3f}, effect={stats_['interpretation']}")

    report.append('\nFormat features effect size (winner > loser)')
    report.append('-' * 110)
    for feature in ['header', 'list', 'bold']:
        report.append(f"\n== {feature} ==")
        for subset_name, subset_df in tokens:
            diff = get_feature_diff(subset_df, feature)
            stats_ = compute_effect_sizes(diff)
            report.append(f"{subset_name}: n_nonzero={stats_['n']:,}, mean_diff={stats_['mean_diff']:.3f}, sd_diff={stats_['sd_diff']:.3f}, cohen_d={stats_['cohen_d']:.3f}, rank_biserial={stats_['rank_biserial']:.3f}, effect={stats_['interpretation']}")

    return '\n'.join(report)


def main():
    root = os.getcwd()
    data_path = os.path.join(root, 'Data', 'optimized_data', 'optimized_data.parquet')

    df = pd.read_parquet(data_path)
    df = df[df['winner'].isin(['model_a', 'model_b'])].copy()

    report = subset_effect_size_report(df)

    out_path = os.path.join(root, 'Reports', 'R12_effect_size_report.txt')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(report[:1200])
    print('\nReport saved to:', out_path)


if __name__ == '__main__':
    main()
