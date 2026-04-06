# -*- coding: utf-8 -*-
"""
Format feature preference test
输入: Data/optimized_data/optimized_data.parquet
输出: Reports/R11_format_preference_report.txt

分析思路：
1. 计算每个样本中`winner`相对于`loser`的格式特征差异：header/list/bold counts。
2. 执行 Wilcoxon 符号秩检验 (one-tailed, greater)，测试是否winner具有更高格式计数。
3. 补充：卡方检验（列联表）和 logistic 回归（说明格式差异是否预测胜率）。
"""
import os
import pandas as pd
import numpy as np
from scipy.stats import wilcoxon, chi2_contingency
from sklearn.linear_model import LogisticRegression


def get_count(value):
    if isinstance(value, dict):
        return sum(value.values())
    if pd.isna(value):
        return 0
    try:
        return float(value)
    except Exception:
        return 0


def format_diff(row, feature):
    a_val = get_count(row[f'a_{feature}_counts'])
    b_val = get_count(row[f'b_{feature}_counts'])
    if row['winner'] == 'model_a':
        return a_val - b_val
    else:
        return b_val - a_val


def compute_format_preference_lines(df, label):
    features = ['header', 'list', 'bold']
    lines = []
    lines.append('\n' + '=' * 80)
    lines.append(f'Subset: {label}')
    lines.append(f'  total samples: {len(df):,}')

    if len(df) == 0:
        lines.append('  empty subset, skip.')
        return lines

    # 计算差值
    for f in features:
        df[f'{f}_diff'] = df.apply(lambda row: format_diff(row, f), axis=1)

    # Wilcoxon
    lines.append('\nOne-sample Wilcoxon Signed-Rank Test (H1: diff > 0)')
    lines.append('-' * 80)
    for f in features:
        diff = df[f'{f}_diff']
        diff_nonzero = diff[diff != 0]
        if len(diff_nonzero) == 0:
            lines.append(f'{f}: no nonzero differences, skip')
            continue
        stat, p = wilcoxon(diff_nonzero, alternative='greater')
        pos_count = (diff_nonzero > 0).sum()
        neg_count = (diff_nonzero < 0).sum()
        lines.append(f"{f}: n_nonzero={len(diff_nonzero):,}, positive={pos_count:,}, negative={neg_count:,}, statistic={stat:.4f}, p={p:.6f}")

    # sign-like
    lines.append('\nSign-like preference (胜出者格式更高 vs 低)')
    lines.append('-' * 80)
    for f in features:
        diff = df[f'{f}_diff']
        pos = (diff > 0).sum()
        neg = (diff < 0).sum()
        tie = (diff == 0).sum()
        ratio = pos / (pos + neg) if (pos + neg) > 0 else np.nan
        lines.append(f"{f}: positive={pos:,}, negative={neg:,}, tie={tie:,}, pos_ratio={ratio:.3f}")

    lines.append('\nChi-square contingency: Format benefit (diff>0) vs winner')
    lines.append('-' * 80)
    for f in features:
        df[f'{f}_pos'] = (df[f'{f}_diff'] > 0).astype(int)
        crosstab = pd.crosstab(df[f'{f}_pos'], df['winner'])
        lines.append(f"{f} crosstab:\n{crosstab.to_string()}\n")

    # logistic regression
    lines.append('\nLogistic regression（format diff -> model_a胜率）')
    lines.append('-' * 80)
    df['winner_a'] = (df['winner'] == 'model_a').astype(int)
    X = df[[f'{f}_diff' for f in features]].fillna(0).values
    y = df['winner_a'].values
    lr = LogisticRegression(max_iter=1000)
    lr.fit(X, y)
    lines.append('Coef: ' + ', '.join([f'{features[i]}={lr.coef_[0, i]:.5f}' for i in range(len(features))]))
    lines.append(f'Intercept: {lr.intercept_[0]:.5f}')
    lines.append(f'Baseline accuracy: {np.mean(y):.4f}')
    lines.append(f'Model accuracy (train): {lr.score(X, y):.4f}')

    return lines


def run_format_preference_test():
    root = os.getcwd()
    data_path = os.path.join(root, 'Data', 'optimized_data', 'optimized_data.parquet')
    df = pd.read_parquet(data_path)

    df = df[df['winner'].isin(['model_a', 'model_b'])].copy()

    subsets = {
        'overall': df,
        'creative_writing': df[df['creative_writing_bool'] == True],
        'if': df[df['if_bool'] == True],
        'math': df[df['math_bool'] == True],
        'only_creative_writing': df[(df['creative_writing_bool'] == True) & (df['if_bool'] == False) & (df['math_bool'] == False)],
        'only_if': df[(df['creative_writing_bool'] == False) & (df['if_bool'] == True) & (df['math_bool'] == False)],
        'only_math': df[(df['creative_writing_bool'] == False) & (df['if_bool'] == False) & (df['math_bool'] == True)],
        'creative_writing_if': df[(df['creative_writing_bool'] == True) & (df['if_bool'] == True)],
        'creative_writing_math': df[(df['creative_writing_bool'] == True) & (df['math_bool'] == True)],
        'if_math': df[(df['if_bool'] == True) & (df['math_bool'] == True)],
        'all_categories': df[(df['creative_writing_bool'] == True) & (df['if_bool'] == True) & (df['math_bool'] == True)],
        'no_category': df[(df['creative_writing_bool'] == False) & (df['if_bool'] == False) & (df['math_bool'] == False)],
    }

    report_lines = []
    report_lines.append('Format Preference Test Report')
    report_lines.append('=' * 80)
    report_lines.append(f'Total samples (valid winner/b loser): {len(df):,}')

    for subset_name, subset_df in subsets.items():
        report_lines.extend(compute_format_preference_lines(subset_df.copy(), subset_name))

    out_path = os.path.join(root, 'Reports', 'R11_format_preference_report.txt')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))

    # print 1st page for quick check
    print('\n'.join(report_lines[:40]))
    print('\nReport saved to:', out_path)


if __name__ == '__main__':
    run_format_preference_test()
