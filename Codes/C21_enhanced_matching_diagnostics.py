# -*- coding: utf-8 -*-
"""
Enhanced length effect analysis with ability/difficulty proxies and matching diagnostics.
增加能力指标和匹配质量诊断。
输出：Reports/R15_enhanced_diagnostics_report.txt / R15_matching_diagnostics.csv / R15_ability_proxies.csv
"""

import os
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
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


def create_ability_proxies(df):
    """
    创建细化的能力和任务难度代理变量：
    - ability_quality: 质量维度（domain_knowledge, technical_accuracy, specificity）
    - ability_clarity: 清晰度维度（creativity, problem_solving）
    - task_difficulty: 难度维度（complexity, real_world）
    - answer_structure_score: 排版结构评分（header, list, bold）
    """
    df = df.copy()
    
    # 质量维度：知识深度 + 技术准确 + 具体性
    quality_cols = ['domain_knowledge', 'technical_accuracy', 'specificity']
    quality_available = [c for c in quality_cols if c in df.columns]
    if quality_available:
        df['ability_quality'] = df[quality_available].mean(axis=1)
    else:
        df['ability_quality'] = 0
    
    # 清晰度维度：创意性 + 问题解决
    clarity_cols = ['creativity', 'problem_solving']
    clarity_available = [c for c in clarity_cols if c in df.columns]
    if clarity_available:
        df['ability_clarity'] = df[clarity_available].mean(axis=1)
    else:
        df['ability_clarity'] = 0
    
    # 难度维度：复杂性 + 真实世界性
    difficulty_cols = ['complexity', 'real_world']
    difficulty_available = [c for c in difficulty_cols if c in df.columns]
    if difficulty_available:
        df['task_difficulty'] = df[difficulty_available].mean(axis=1)
    else:
        df['task_difficulty'] = 0
    
    # 排版结构评分（A和B答案差异）
    df['header_count_a'] = df.apply(lambda r: extract_count(r['a_header_counts'], 'header'), axis=1)
    df['header_count_b'] = df.apply(lambda r: extract_count(r['b_header_counts'], 'header'), axis=1)
    df['list_count_a'] = df.apply(lambda r: extract_count(r['a_list_counts'], 'list'), axis=1)
    df['list_count_b'] = df.apply(lambda r: extract_count(r['b_list_counts'], 'list'), axis=1)
    df['bold_count_a'] = df.apply(lambda r: extract_count(r['a_bold_counts'], 'bold'), axis=1)
    df['bold_count_b'] = df.apply(lambda r: extract_count(r['b_bold_counts'], 'bold'), axis=1)
    
    df['format_structure_a'] = df['header_count_a'] + df['list_count_a'] + df['bold_count_a']
    df['format_structure_b'] = df['header_count_b'] + df['list_count_b'] + df['bold_count_b']
    df['format_structure_diff'] = df['format_structure_a'] - df['format_structure_b']
    
    # 现有的长度和标签变量
    df['winner_a'] = (df['winner'] == 'model_a').astype(int)
    df['length_diff_ab'] = df['a_tokens'] - df['b_tokens']
    df['longer_a'] = (df['length_diff_ab'] > 0).astype(int)
    df['length_tie'] = (df['length_diff_ab'] == 0).astype(int)
    df['longer_wins'] = (((df['length_diff_ab'] > 0) & (df['winner'] == 'model_a')) |
                         ((df['length_diff_ab'] < 0) & (df['winner'] == 'model_b'))).astype(int)
    
    return df


def enhanced_confounders(df):
    """扩展混淆变量列表，包括新的代理变量"""
    base_confounders = [
        'user_tokens', 'turns', 'is_code',
        'creative_writing_bool', 'if_bool', 'math_bool',
        'complexity', 'creativity', 'domain_knowledge',
        'problem_solving', 'real_world', 'specificity', 'technical_accuracy'
    ]
    ability_proxies = ['ability_quality', 'ability_clarity', 'task_difficulty', 'format_structure_diff']
    all_vars = base_confounders + ability_proxies
    return [c for c in all_vars if c in df.columns]


def fit_logistic_model(X, y, robust=True):
    X = sm.add_constant(X, has_constant='add')
    model = sm.Logit(y, X)
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=ConvergenceWarning)
            res = model.fit(disp=0, maxiter=500)
        return res
    except Exception as e:
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


def propensity_score_matching_with_diagnostics(df, confounders, treatment='longer_a', caliper=0.05):
    """匹配，返回诊断信息"""
    df = df.copy()
    if treatment not in df.columns:
        return None, None
    if len(df[confounders].dropna()) != len(df):
        df = df.dropna(subset=confounders + [treatment, 'winner_a'])
    
    X = df[confounders].copy()
    X = X.astype(float)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    y = df[treatment].astype(int)
    
    model = LogisticRegression(max_iter=1000, solver='liblinear')
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=ConvergenceWarning)
        model.fit(X_scaled, y)
    ps = model.predict_proba(X_scaled)[:, 1]
    df['pscore'] = ps

    treated = df[df[treatment] == 1].reset_index(drop=True)
    control = df[df[treatment] == 0].reset_index(drop=True)
    if len(treated) == 0 or len(control) == 0:
        return None, None

    nbrs = NearestNeighbors(n_neighbors=1).fit(control[['pscore']].values)
    dist, idx = nbrs.kneighbors(treated[['pscore']].values)
    matched = []
    for i, d in enumerate(dist[:, 0]):
        if d <= caliper:
            matched.append((i, idx[i, 0], d))
    if not matched:
        return None, None

    treated_idx = [t for t, _, _ in matched]
    control_idx = [c for _, c, _ in matched]
    treated_matched = treated.iloc[treated_idx].reset_index(drop=True)
    control_matched = control.iloc[control_idx].reset_index(drop=True)
    
    effect = treated_matched['winner_a'].mean() - control_matched['winner_a'].mean()
    
    # 诊断信息
    diagnostics = {
        'n_treated_unmatched': len(treated),
        'n_control_unmatched': len(control),
        'n_treated_matched': len(treated_matched),
        'n_control_matched': len(control_matched),
        'match_rate_treated': len(treated_matched) / len(treated) if len(treated) > 0 else 0,
        'match_rate_control': len(control_matched) / len(control) if len(control) > 0 else 0,
        'treated_ps_mean_before': treated['pscore'].mean(),
        'control_ps_mean_before': control['pscore'].mean(),
        'treated_ps_mean_after': treated_matched['pscore'].mean(),
        'control_ps_mean_after': control_matched['pscore'].mean(),
        'treated_ps_std_before': treated['pscore'].std(),
        'control_ps_std_before': control['pscore'].std(),
        'treated_ps_std_after': treated_matched['pscore'].std(),
        'control_ps_std_after': control_matched['pscore'].std(),
        'mean_distance': np.mean([d for _, _, d in matched]),
        'max_distance': np.max([d for _, _, d in matched]),
        'min_distance': np.min([d for _, _, d in matched]),
    }
    
    result = {
        'n_treated': len(treated_matched),
        'n_control': len(control_matched),
        'treated_rate': float(treated_matched['winner_a'].mean()),
        'control_rate': float(control_matched['winner_a'].mean()),
        'average_treatment_effect': float(effect),
        'mean_distance': float(np.mean([d for _, _, d in matched]))
    }
    
    return result, diagnostics


def ipw_estimate(df, confounders, treatment='longer_a'):
    df = df.copy()
    df = df.dropna(subset=confounders + [treatment, 'winner_a'])
    X = df[confounders].astype(float)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    y = df[treatment].astype(int)
    model = LogisticRegression(max_iter=1000, solver='liblinear')
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=ConvergenceWarning)
        model.fit(X_scaled, y)
    ps = model.predict_proba(X_scaled)[:, 1]
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


def render_main_report():
    root = os.getcwd()
    df = load_optimized_data(root)
    df = create_ability_proxies(df)
    confounders = enhanced_confounders(df)

    report_lines = []
    report_lines.append('Enhanced Length Effect Analysis with Ability Proxies and Matching Diagnostics')
    report_lines.append('=' * 140)
    report_lines.append('Ability Proxies: ability_quality, ability_clarity, task_difficulty, format_structure_diff')
    report_lines.append('Matching Diagnostics include: propensity score balance before/after, match rates, distance statistics\n')

    for subset_name, selector in subset_names().items():
        subdf = selector(df)
        if len(subdf) < 30:
            report_lines.append(f'Subset: {subset_name} skipped due to small sample ({len(subdf)}).')
            report_lines.append('')
            continue
        
        included = [c for c in confounders if c in subdf.columns and subdf[c].nunique(dropna=True) > 1]
        if not included:
            report_lines.append(f'Subset: {subset_name} has no variable confounders.')
            report_lines.append('')
            continue
        
        report_lines.append('=' * 120)
        report_lines.append(f'Subset: {subset_name} (n={len(subdf)})')
        report_lines.append(f'Longer wins rate: {subdf["longer_wins"].mean():.4f}')
        report_lines.append(f'A longer rate: {subdf["longer_a"].mean():.4f}')
        report_lines.append('')

        # 基础模型
        model_a = fit_logistic_model(subdf[['longer_a']], subdf['winner_a'])
        summary_a = logistic_summary(model_a, 'longer_a')
        if summary_a is not None:
            report_lines.append('Model A (longer_a only):')
            report_lines.append(f'  coef={summary_a["coef"]:.4f}, OR={summary_a["or"]:.4f}, p={summary_a["p"]:.4f}, R2={summary_a["pseudo_r2"]:.4f}')
        report_lines.append('')

        # 加上所有混淆变量
        X = subdf[['longer_a'] + included].copy()
        X[included] = X[included].astype(float)
        model_b = fit_logistic_model(X, subdf['winner_a'])
        summary_b = logistic_summary(model_b, 'longer_a')
        if summary_b is not None:
            report_lines.append('Model B (longer_a + all confounders including ability proxies):')
            report_lines.append(f'  coef={summary_b["coef"]:.4f}, OR={summary_b["or"]:.4f}, p={summary_b["p"]:.4f}, R2={summary_b["pseudo_r2"]:.4f}')
        report_lines.append('')

        # 仅用基础混淆变量（不含代理变量）
        base_confounders = [c for c in included if not c.startswith('ability_') and c != 'format_structure_diff']
        if base_confounders:
            X_base = subdf[['longer_a'] + base_confounders].copy()
            X_base[base_confounders] = X_base[base_confounders].astype(float)
            model_base = fit_logistic_model(X_base, subdf['winner_a'])
            summary_base = logistic_summary(model_base, 'longer_a')
            if summary_base is not None:
                report_lines.append('Model C (longer_a + base confounders only):')
                report_lines.append(f'  coef={summary_base["coef"]:.4f}, OR={summary_base["or"]:.4f}, p={summary_base["p"]:.4f}, R2={summary_base["pseudo_r2"]:.4f}')
            report_lines.append('')

        # 匹配与诊断
        match_res, diag = propensity_score_matching_with_diagnostics(subdf, included, treatment='longer_a')
        if match_res is not None and diag is not None:
            report_lines.append('Propensity Score Matching Results:')
            report_lines.append(f'  Matched n (treated): {match_res["n_treated"]}, (control): {match_res["n_control"]}')
            report_lines.append(f'  Treated winner rate (matched): {match_res["treated_rate"]:.4f}')
            report_lines.append(f'  Control winner rate (matched): {match_res["control_rate"]:.4f}')
            report_lines.append(f'  Average Treatment Effect (ATE): {match_res["average_treatment_effect"]:.4f}')
            report_lines.append('')
            report_lines.append('Matching Diagnostics (Propensity Score Balance):')
            report_lines.append(f'  Before matching - Treated PS mean: {diag["treated_ps_mean_before"]:.4f} (std: {diag["treated_ps_std_before"]:.4f})')
            report_lines.append(f'  Before matching - Control PS mean: {diag["control_ps_mean_before"]:.4f} (std: {diag["control_ps_std_before"]:.4f})')
            report_lines.append(f'  After matching - Treated PS mean: {diag["treated_ps_mean_after"]:.4f} (std: {diag["treated_ps_std_after"]:.4f})')
            report_lines.append(f'  After matching - Control PS mean: {diag["control_ps_mean_after"]:.4f} (std: {diag["control_ps_std_after"]:.4f})')
            report_lines.append(f'  Match rate (treated matched/total): {diag["match_rate_treated"]:.4f}')
            report_lines.append(f'  Match rate (control matched/total): {diag["match_rate_control"]:.4f}')
            report_lines.append(f'  Matching distance stats - mean: {diag["mean_distance"]:.6f}, max: {diag["max_distance"]:.6f}, min: {diag["min_distance"]:.6f}')
        else:
            report_lines.append('Propensity Score Matching: Failed or no valid match.')
        report_lines.append('')

        # IPW
        ipw_res = ipw_estimate(subdf, included, treatment='longer_a')
        if ipw_res is not None:
            report_lines.append('Inverse Probability Weighting (IPW) Results:')
            report_lines.append(f'  Weighted treated rate: {ipw_res["weighted_treated_rate"]:.4f}')
            report_lines.append(f'  Weighted control rate: {ipw_res["weighted_control_rate"]:.4f}')
            report_lines.append(f'  IPW Treatment Effect: {ipw_res["ipw_effect"]:.4f}')
        report_lines.append('')

    return '\n'.join(report_lines)


def render_ability_proxy_summary():
    """生成能力代理变量描述和分布统计"""
    root = os.getcwd()
    df = load_optimized_data(root)
    df = create_ability_proxies(df)
    
    lines = []
    lines.append('Ability Proxy Variables - Descriptive Statistics')
    lines.append('=' * 100)
    lines.append('')
    
    proxy_vars = ['ability_quality', 'ability_clarity', 'task_difficulty', 'format_structure_diff']
    proxy_descriptions = {
        'ability_quality': 'Average of domain_knowledge, technical_accuracy, specificity',
        'ability_clarity': 'Average of creativity, problem_solving',
        'task_difficulty': 'Average of complexity, real_world',
        'format_structure_diff': 'Difference in formatting structure elements (headers, lists, bold)'
    }
    
    for var in proxy_vars:
        if var in df.columns:
            lines.append(f'{var}: {proxy_descriptions.get(var, "")}')
            lines.append(f'  Mean: {df[var].mean():.4f}')
            lines.append(f'  Std: {df[var].std():.4f}')
            lines.append(f'  Min: {df[var].min():.4f}')
            lines.append(f'  Max: {df[var].max():.4f}')
            lines.append(f'  Missing: {df[var].isna().sum()} ({df[var].isna().sum()/len(df)*100:.2f}%)')
            lines.append('')
    
    return '\n'.join(lines)


def main():
    root = os.getcwd()
    output_dir = Path(root) / 'Reports'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print('Rendering main enhanced analysis report...')
    main_report = render_main_report()
    with open(output_dir / 'R15_enhanced_diagnostics_report.txt', 'w', encoding='utf-8') as f:
        f.write(main_report)
    print(f'  Saved: Reports/R15_enhanced_diagnostics_report.txt')
    
    print('Rendering ability proxy summary...')
    proxy_summary = render_ability_proxy_summary()
    with open(output_dir / 'R15_ability_proxies.txt', 'w', encoding='utf-8') as f:
        f.write(proxy_summary)
    print(f'  Saved: Reports/R15_ability_proxies.txt')
    
    print('Done. All reports saved to Reports/ folder.')


if __name__ == '__main__':
    main()
