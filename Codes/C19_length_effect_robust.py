# -*- coding: utf-8 -*-
"""
Robust length effect analysis using direct longer-wins labels, logistic regression, and propensity score matching.
输出：Reports/R17_length_effect_robust_report.txt
"""

import os
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import pairwise_distances_argmin_min
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler


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


def load_optimized_data(root=None):
    if root is None:
        root = os.getcwd()
    path = Path(root) / 'Data' / 'optimized_data' / 'optimized_data.parquet'
    df = pd.read_parquet(path)
    return df[df['winner'].isin(['model_a', 'model_b'])].copy()


def prepare_robust_data(df):
    df = df.copy()
    df['winner_a'] = (df['winner'] == 'model_a').astype(int)
    df['length_diff_ab'] = df['a_tokens'] - df['b_tokens']
    df['longer_a'] = (df['length_diff_ab'] > 0).astype(int)
    df['length_tie'] = (df['length_diff_ab'] == 0).astype(int)
    df['longer_wins'] = (((df['length_diff_ab'] > 0) & (df['winner'] == 'model_a')) |
                         ((df['length_diff_ab'] < 0) & (df['winner'] == 'model_b'))).astype(int)
    df['header_diff_ab'] = df.apply(lambda r: extract_count(r['a_header_counts'], 'header') - extract_count(r['b_header_counts'], 'header'), axis=1)
    df['list_diff_ab'] = df.apply(lambda r: extract_count(r['a_list_counts'], 'list') - extract_count(r['b_list_counts'], 'list'), axis=1)
    df['bold_diff_ab'] = df.apply(lambda r: extract_count(r['a_bold_counts'], 'bold') - extract_count(r['b_bold_counts'], 'bold'), axis=1)
    return df


def available_confounders(df):
    confounders = [
        'user_tokens', 'turns', 'is_code',
        'creative_writing_bool', 'if_bool', 'math_bool',
        'complexity', 'creativity', 'domain_knowledge',
        'problem_solving', 'real_world', 'specificity', 'technical_accuracy'
    ]
    return [c for c in confounders if c in df.columns]


def fit_logistic_model(X, y, robust=True):
    X = sm.add_constant(X, has_constant='add')
    model = sm.Logit(y, X)
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=ConvergenceWarning)
            res = model.fit(disp=0, maxiter=500)
        return res
    except Exception as e:
        print('Statsmodels Logit failed, fallback to sklearn:', e)
        try:
            X_np = X.astype(float).values
            y_np = y.astype(int).values
            sklearn_model = LogisticRegression(max_iter=1000, solver='liblinear')
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', category=ConvergenceWarning)
                sklearn_model.fit(X_np, y_np)
            probs = sklearn_model.predict_proba(X_np)[:, 1]
            ll = np.sum(y_np * np.log(probs + 1e-15) + (1 - y_np) * np.log(1 - probs + 1e-15))
            p0 = y_np.mean()
            ll_null = np.sum(y_np * np.log(p0 + 1e-15) + (1 - y_np) * np.log(1 - p0 + 1e-15))
            pseudo_r2 = 1 - ll / ll_null if ll_null != 0 else np.nan
            W = np.diag(probs * (1 - probs))
            cov = np.linalg.pinv(X_np.T @ W @ X_np)
            se = np.sqrt(np.diag(cov))
            params = np.concatenate(([sklearn_model.intercept_[0]], sklearn_model.coef_.ravel()))
            names = list(X.columns)
            if len(params) != len(names):
                names = ['const'] + [f'x{i}' for i in range(X_np.shape[1])]
            se = np.sqrt(np.abs(np.diag(cov)))
            return {
                'type': 'sklearn',
                'params': pd.Series(params, index=names),
                'bse': pd.Series(se, index=names),
                'pvalues': pd.Series(np.nan, index=names),
                'llf': ll,
                'llnull': ll_null,
            }
        except Exception as ee:
            print('Sklearn fallback failed:', ee)
            return None


def logistic_summary(res, variable):
    if res is None:
        return None
    if isinstance(res, dict):
        coef = res['params'].get(variable, np.nan)
        se = res['bse'].get(variable, np.nan)
        p = res['pvalues'].get(variable, np.nan)
        llf = res.get('llf', np.nan)
        llnull = res.get('llnull', np.nan)
    else:
        coef = res.params.get(variable, np.nan)
        se = res.bse.get(variable, np.nan)
        p = res.pvalues.get(variable, np.nan)
        llf = res.llf
        llnull = res.llnull
    odds_ratio = np.exp(coef) if not pd.isna(coef) else np.nan
    pseudo_r2 = 1 - llf / llnull if llnull != 0 else np.nan
    return {
        'coef': float(coef),
        'se': float(se),
        'p': float(p) if not pd.isna(p) else np.nan,
        'or': float(odds_ratio),
        'pseudo_r2': float(pseudo_r2) if not pd.isna(pseudo_r2) else np.nan
    }


def propensity_score_matching(df, confounders, treatment='longer_a', caliper=0.05):
    df = df.copy()
    if treatment not in df.columns:
        return None
    if len(df[confounders].dropna()) != len(df):
        df = df.dropna(subset=confounders + [treatment, 'winner_a'])
    X = df[confounders].copy()
    X = X.astype(float)
    scaler = StandardScaler()
    X = scaler.fit_transform(X)
    y = df[treatment].astype(int)
    model = LogisticRegression(max_iter=1000, solver='liblinear')
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=ConvergenceWarning)
        model.fit(X, y)
    ps = model.predict_proba(X)[:, 1]
    df['pscore'] = ps

    treated = df[df[treatment] == 1].reset_index(drop=True)
    control = df[df[treatment] == 0].reset_index(drop=True)
    if len(treated) == 0 or len(control) == 0:
        return None

    nbrs = NearestNeighbors(n_neighbors=1).fit(control[['pscore']].values)
    dist, idx = nbrs.kneighbors(treated[['pscore']].values)
    matched = []
    for i, d in enumerate(dist[:, 0]):
        if d <= caliper:
            matched.append((i, idx[i, 0], d))
    if not matched:
        return None

    treated_idx = [t for t, _, _ in matched]
    control_idx = [c for _, c, _ in matched]
    treated_matched = treated.iloc[treated_idx].reset_index(drop=True)
    control_matched = control.iloc[control_idx].reset_index(drop=True)
    effect = treated_matched['winner_a'].mean() - control_matched['winner_a'].mean()
    return {
        'n_treated': len(treated_matched),
        'n_control': len(control_matched),
        'treated_rate': float(treated_matched['winner_a'].mean()),
        'control_rate': float(control_matched['winner_a'].mean()),
        'average_treatment_effect': float(effect),
        'mean_distance': float(np.mean([d for _, _, d in matched]))
    }


def ipw_estimate(df, confounders, treatment='longer_a'):
    df = df.copy()
    df = df.dropna(subset=confounders + [treatment, 'winner_a'])
    X = df[confounders].astype(float)
    scaler = StandardScaler()
    X = scaler.fit_transform(X)
    y = df[treatment].astype(int)
    model = LogisticRegression(max_iter=1000, solver='liblinear')
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=ConvergenceWarning)
        model.fit(X, y)
    ps = model.predict_proba(X)[:, 1]
    ps = np.clip(ps, 0.01, 0.99)
    df['weight'] = df[treatment] / ps + (1 - df[treatment]) / (1 - ps)
    weighted_treated = np.average(df.loc[df[treatment] == 1, 'winner_a'], weights=df.loc[df[treatment] == 1, 'weight'])
    weighted_control = np.average(df.loc[df[treatment] == 0, 'winner_a'], weights=df.loc[df[treatment] == 0, 'weight'])
    return {
        'weighted_treated_rate': float(weighted_treated),
        'weighted_control_rate': float(weighted_control),
        'ipw_effect': float(weighted_treated - weighted_control)
    }


def subset_names():
    return {
        'Overall': lambda df: df,
        'Creative Writing': lambda df: df[df['creative_writing_bool'] == True],
        'Instruction Following': lambda df: df[df['if_bool'] == True],
        'Math': lambda df: df[df['math_bool'] == True],
        'Only Creative Writing': lambda df: df[(df['creative_writing_bool'] == True) & (df['if_bool'] == False) & (df['math_bool'] == False)],
        'Only IF': lambda df: df[(df['creative_writing_bool'] == False) & (df['if_bool'] == True) & (df['math_bool'] == False)],
        'Only Math': lambda df: df[(df['creative_writing_bool'] == False) & (df['if_bool'] == False) & (df['math_bool'] == True)],
        'CW & IF': lambda df: df[(df['creative_writing_bool'] == True) & (df['if_bool'] == True)],
        'CW & Math': lambda df: df[(df['creative_writing_bool'] == True) & (df['math_bool'] == True)],
        'IF & Math': lambda df: df[(df['if_bool'] == True) & (df['math_bool'] == True)],
        'All Categories': lambda df: df[(df['creative_writing_bool'] == True) & (df['if_bool'] == True) & (df['math_bool'] == True)],
        'No Category': lambda df: df[(df['creative_writing_bool'] == False) & (df['if_bool'] == False) & (df['math_bool'] == False)],
    }


def render_report():
    root = os.getcwd()
    df = load_optimized_data(root)
    df = prepare_robust_data(df)
    confounders = available_confounders(df)

    report_lines = []
    report_lines.append('Robust Length Effect Report')
    report_lines.append('=' * 120)
    report_lines.append('This analysis uses a direct longer-wins label, logistic regression, matching, and IPW.\n')

    def summary_block(name, subdf):
        lines = []
        n = len(subdf)
        if n == 0:
            lines.append(f'Subset: {name} has 0 samples, skipped.')
            return lines
        longer_wins = subdf['longer_wins'].mean()
        tie_rate = subdf['length_tie'].mean()
        longer_a_rate = subdf['longer_a'].mean()
        lines.append(f'Subset: {name} (n={n})')
        lines.append(f'  Longer wins frequency: {longer_wins:.4f}')
        lines.append(f'  Length ties frequency: {tie_rate:.4f}')
        lines.append(f'  A longer frequency: {longer_a_rate:.4f}')
        return lines

    report_lines.extend(summary_block('Overall', df))
    report_lines.append('')

    report_lines.append('Available confounders: ' + ', '.join(confounders))
    report_lines.append('')

    for subset_name, selector in subset_names().items():
        subdf = selector(df)
        if len(subdf) < 30:
            report_lines.append(f'Subset: {subset_name} skipped due to small sample ({len(subdf)}).')
            continue
        report_lines.append('=' * 80)
        report_lines.append(f'Subset: {subset_name}')
        report_lines.append(f'Total rows: {len(subdf)}')
        report_lines.append(f'Longer wins rate: {subdf["longer_wins"].mean():.4f}')
        report_lines.append(f'A longer rate: {subdf["longer_a"].mean():.4f}')

        included = [c for c in confounders if c in subdf.columns and subdf[c].nunique(dropna=True) > 1]
        if not included:
            report_lines.append('  No variable-confounders available for this subset.')
            continue

        model_a = fit_logistic_model(subdf[['longer_a']], subdf['winner_a'])
        summary_a = logistic_summary(model_a, 'longer_a')
        if summary_a is not None:
            report_lines.append('  Model A (longer_a only):')
            report_lines.append(f'    coef={summary_a["coef"]:.4f}, OR={summary_a["or"]:.4f}, p={summary_a["p"]:.4f}, R2={summary_a["pseudo_r2"]:.4f}')

        X = subdf[['longer_a'] + included].copy()
        X[included] = X[included].astype(float)
        model_b = fit_logistic_model(X, subdf['winner_a'])
        summary_b = logistic_summary(model_b, 'longer_a')
        if summary_b is not None:
            report_lines.append('  Model B (longer_a + confounders):')
            report_lines.append(f'    coef={summary_b["coef"]:.4f}, OR={summary_b["or"]:.4f}, p={summary_b["p"]:.4f}, R2={summary_b["pseudo_r2"]:.4f}')

        match_res = propensity_score_matching(subdf, included, treatment='longer_a')
        if match_res is not None:
            report_lines.append('  Matching result (longer_a treated vs control):')
            report_lines.append(f'    matched treated count: {match_res["n_treated"]}')
            report_lines.append(f'    treated winner_a rate: {match_res["treated_rate"]:.4f}')
            report_lines.append(f'    control winner_a rate: {match_res["control_rate"]:.4f}')
            report_lines.append(f'    ATE: {match_res["average_treatment_effect"]:.4f}')
            report_lines.append(f'    mean propensity distance: {match_res["mean_distance"]:.4f}')
        else:
            report_lines.append('  Matching failed or no valid matched sample.')

        ipw_res = ipw_estimate(subdf, included, treatment='longer_a')
        if ipw_res is not None:
            report_lines.append('  IPW result:')
            report_lines.append(f'    weighted treated rate: {ipw_res["weighted_treated_rate"]:.4f}')
            report_lines.append(f'    weighted control rate: {ipw_res["weighted_control_rate"]:.4f}')
            report_lines.append(f'    IPW effect: {ipw_res["ipw_effect"]:.4f}')
        report_lines.append('')

    out_path = Path(root) / 'Reports' / 'R17_length_effect_robust_report.txt'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))

    print('Report saved to:', out_path)
    return out_path


if __name__ == '__main__':
    render_report()
