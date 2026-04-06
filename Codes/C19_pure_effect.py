# -*- coding: utf-8 -*-
"""
Pseudo-correlation and confounder-control modeling, plus net effect quantification.

Task:
1. 核心混淆变量定义+操作化
2. 分层逻辑回归建模（token_diff/format_diff 控制混淆）
3. 混淆控制效果验证（coefficient changes, drop-in R2）
4. 净效应量化（adjusted effect / OR）

输出：Reports/R13_pure_effect_report.txt
"""

import os
import warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler
from statsmodels.tools.sm_exceptions import ConvergenceWarning


def norm_feature(x):
    return (x - np.nanmean(x)) / (np.nanstd(x, ddof=1) if np.nanstd(x, ddof=1) > 0 else 1)


def compute_diffs(df):
    df = df.copy()
    # winner-oriented differences (for Wilcoxon / effect size analysis)
    df['token_diff'] = df.apply(lambda r: r['a_tokens'] - r['b_tokens'] if r['winner']=='model_a' else r['b_tokens'] - r['a_tokens'], axis=1)

    # format diffs oriented by winner
    def ccount(v):
        if isinstance(v, dict):
            return sum(v.values())
        if pd.isna(v):
            return 0
        try:
            return float(v)
        except Exception:
            return 0

    for feat in ['header', 'list', 'bold']:
        df[f'{feat}_diff'] = df.apply(lambda r: (ccount(r[f'a_{feat}_counts']) - ccount(r[f'b_{feat}_counts'])) if r['winner']=='model_a' else (ccount(r[f'b_{feat}_counts']) - ccount(r[f'a_{feat}_counts'])), axis=1)

    df['winner_a'] = (df['winner'] == 'model_a').astype(int)
    return df


def extract_count(value, feature_type=None):
    if isinstance(value, dict):
        if feature_type == 'header':
            return sum(value.get(f'h{i}', 0) for i in range(1, 7))
        if feature_type == 'list':
            return value.get('ordered', 0) + value.get('unordered', 0)
        if feature_type == 'bold':
            return value.get('**', 0) + value.get('__', 0)
        return sum(value.values())
    if pd.isna(value):
        return 0
    try:
        return float(value)
    except Exception:
        return 0


def prepare_pure_effect_df(df):
    """Prepare pairwise difference features used for logistic regression."""
    df = df.copy()
    df['winner_a'] = (df['winner'] == 'model_a').astype(int)
    df['token_diff_ab'] = df['a_tokens'] - df['b_tokens']
    df['header_diff_ab'] = df.apply(lambda r: extract_count(r['a_header_counts'], 'header') - extract_count(r['b_header_counts'], 'header'), axis=1)
    df['list_diff_ab'] = df.apply(lambda r: extract_count(r['a_list_counts'], 'list') - extract_count(r['b_list_counts'], 'list'), axis=1)
    df['bold_diff_ab'] = df.apply(lambda r: extract_count(r['a_bold_counts'], 'bold') - extract_count(r['b_bold_counts'], 'bold'), axis=1)
    return df


def define_confounders(df):
    # 从可用列中抽取潜在混淆变量，根据立项书的可解释性和数据可用性
    confounders = [
        'user_tokens', 'turns', 'is_code',
        'creative_writing_bool', 'if_bool', 'math_bool',
        'complexity', 'creativity', 'domain_knowledge',
        'problem_solving', 'real_world', 'specificity', 'technical_accuracy'
    ]

    available = [c for c in confounders if c in df.columns]
    missing = [c for c in confounders if c not in df.columns]

    if missing:
        print('注意: 以下预设混淆变量不可用，已跳过:', missing)

    print('可用混淆变量:', available)
    return available


def fit_logistic_model(X, y):
    X2 = sm.add_constant(X, has_constant='add')
    model = sm.Logit(y, X2)
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=ConvergenceWarning)
            res = model.fit(disp=0, maxiter=200)
    except Exception as e:
        print('Logit fitting failed:', e)
        return None
    pseudo_r2 = 1 - res.llf / res.llnull if res.llnull != 0 else np.nan
    return {
        'result': res,
        'p2': pseudo_r2,
        'aic': res.aic,
        'bic': res.bic,
    }


def subset_pure_effect_analysis(df, subset_name, confounders, target='token_diff_ab'):
    s = df.copy()
    if 'winner_a' not in s.columns or target not in s.columns:
        s = prepare_pure_effect_df(s)

    required_columns = ['winner_a', target] + confounders
    missing = [c for c in required_columns if c not in s.columns]
    if missing:
        print(f'[{subset_name}] 缺少必要列，跳过：{missing}')
        return None

    s = s.dropna(subset=required_columns)
    if len(s) < 30:
        print(f'[{subset_name}] 样本量过少，跳过 ({len(s)} rows)')
        return None

    valid_confounders = [c for c in confounders if c in s.columns and s[c].nunique(dropna=True) > 1]
    dropped = [c for c in confounders if c not in valid_confounders]
    if dropped:
        print(f'[{subset_name}] 已排除常量或无效混淆变量: {dropped}')

    # 标准化混淆变量
    scaler = StandardScaler()
    conf_data = scaler.fit_transform(s[valid_confounders]) if valid_confounders else None
    conf_df = pd.DataFrame(conf_data, columns=valid_confounders, index=s.index) if valid_confounders else pd.DataFrame(index=s.index)

    X1 = s[[target]]
    X2 = pd.concat([X1, conf_df], axis=1)
    X3 = conf_df
    y = s['winner_a']

    m1 = fit_logistic_model(X1, y)
    m2 = fit_logistic_model(X2, y)
    m3 = fit_logistic_model(X3, y) if len(valid_confounders) > 0 else None

    if m1 is None or m2 is None or (len(valid_confounders) > 0 and m3 is None):
        print(f'[{subset_name}] 逻辑回归拟合失败，skip')
        return None

    coeff1 = m1['result'].params.get(target, np.nan)
    se1 = m1['result'].bse.get(target, np.nan)
    or1 = np.exp(coeff1) if not np.isnan(coeff1) else np.nan

    coeff2 = m2['result'].params.get(target, np.nan)
    se2 = m2['result'].bse.get(target, np.nan)
    or2 = np.exp(coeff2) if not np.isnan(coeff2) else np.nan

    control_effect = coeff2 - coeff1

    return {
        'subset': subset_name,
        'n': len(s),
        'n_pos': int(s['winner_a'].sum()),
        'n_neg': int((1 - s['winner_a']).sum()),
        'model1_coef': coeff1,
        'model1_se': se1,
        'model1_or': or1,
        'model1_p': m1['result'].pvalues.get(target, np.nan),
        'model1_r2': m1['p2'],
        'model2_coef': coeff2,
        'model2_se': se2,
        'model2_or': or2,
        'model2_p': m2['result'].pvalues.get(target, np.nan),
        'model2_r2': m2['p2'],
        'model3_r2': m3['p2'],
        'control_delta': control_effect,
        'confounders': valid_confounders,
        'dropped_confounders': dropped,
    }


def run_pure_effect():
    root = os.getcwd()
    df = pd.read_parquet(os.path.join(root, 'Data', 'optimized_data', 'optimized_data.parquet'))
    df = df[df['winner'].isin(['model_a', 'model_b'])].copy()

    df = compute_diffs(df)
    confounders = define_confounders(df)
    if not confounders:
        raise ValueError('No confounder available.')

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

    results = []
    for name, subdf in subsets.items():
        r = subset_pure_effect_analysis(subdf, name, confounders, target='token_diff')
        if r is not None:
            results.append(r)

    # 写报告
    report = []
    report.append('Pure Effect Analysis: token_diff as核心指标，confounders控制后拟合结果')
    report.append('='*120)
    report.append('')

    for r in results:
        report.append(f"Subset: {r['subset']} (n={r['n']})")
        report.append(f"  Model1 (token_diff only): coef={r['model1_coef']:.4f}, OR={r['model1_or']:.4f}, p={r['model1_p']:.4f}, R2={r['model1_r2']:.4f}")
        report.append(f"  Model2 (+confounders): coef={r['model2_coef']:.4f}, OR={r['model2_or']:.4f}, p={r['model2_p']:.4f}, R2={r['model2_r2']:.4f}")
        report.append(f"  Model3 (confounders only) R2={r['model3_r2']:.4f}")
        report.append(f"  Control delta (token_coef reduction): {r['control_delta']:.4f}")
        report.append('')

    out_path = os.path.join(root, 'Reports', 'R13_pure_effect_report.txt')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))

    print('\n'.join(report[:30]))
    print('\nReport saved to:', out_path)


if __name__ == '__main__':
    run_pure_effect()
