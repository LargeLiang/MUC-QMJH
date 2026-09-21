"""Observed-variable generalized path analysis; no causal mediation claims.

OLS formatting equations + Bernoulli/logit choice equation. Cross-equation
HC0 sandwich includes dependence of estimating scores within each pair.
Joint-normal simulation intervals are NOT bootstrap intervals.
"""
import os
for key in ('OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'OMP_NUM_THREADS'):
    os.environ[key] = '2'
from pathlib import Path
import hashlib
import json
import platform
import sys
import numpy as np
import pandas as pd
import scipy
import statsmodels
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'Codes'))
from accessor import CRITERIA
OUT = ROOT / 'Revision' / 'exploratory_sem'
SOURCE = ROOT / 'Data/analysis_data/integrated-20260920/analysis_data.parquet'
FEATURES = ['log_token_ratio', 'header_density_diff', 'list_density_diff', 'bold_density_diff']
NAMES = dict(zip(FEATURES, ['长度', '标题', '列表', '粗体']))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def analyze(part, label, rng):
    part = part[part.winner.isin(['model_a', 'model_b'])].copy()
    x = pd.DataFrame(index=part.index)
    x[FEATURES[0]] = np.log(part.tokens_a / part.tokens_b)
    for f in ['header', 'list', 'bold']:
        x[f'{f}_density_diff'] = 1000 * (part[f'{f}_a']/part.tokens_a - part[f'{f}_b']/part.tokens_b)
    scaling = pd.DataFrame({'mean': x.mean(), 'sd': x.std(ddof=0)})
    x = (x - scaling['mean']) / scaling['sd']
    z = x.copy()
    x['log_user_tokens'] = np.log1p(part.user_tokens)
    x['turns'] = part.turns
    for col in ['cw', 'if', 'math', 'code'] + CRITERIA:
        x[col] = part[col]
    lang = part.language.where(part.language.map(part.language.value_counts()) >= 100, '__rare__')
    x = pd.concat([x, pd.get_dummies(lang, prefix='language', drop_first=True, dtype=float)], axis=1)
    models = sorted(set(part.model_a) | set(part.model_b))
    for model in models[1:]:
        x['model:' + model] = (part.model_a == model).astype(float) - (part.model_b == model).astype(float)
    x = sm.add_constant(x.loc[:, x.nunique() > 1].astype(float))
    if not np.isfinite(x).all().all() or np.linalg.matrix_rank(x) != x.shape[1]:
        raise ValueError('Nonfinite or rank-deficient design')
    m = x.drop(columns=FEATURES[1:])
    ma = m.to_numpy()
    inv_m = np.linalg.inv(ma.T @ ma)
    a_index = m.columns.get_loc(FEATURES[0])
    a_fits = [sm.OLS(z[f], m).fit(cov_type='HC0') for f in FEATURES[1:]]
    y = (part.winner == 'model_a').astype(int)
    fit = sm.GLM(y, x, family=sm.families.Binomial()).fit(maxiter=150, cov_type='HC0')
    if not fit.converged or not np.isfinite(fit.params).all():
        raise ValueError('Failed outcome fit')
    # Check that the outcome equation reproduces the frozen primary analysis.
    frozen = pd.read_csv(ROOT / 'Tables/integrated-20260920/T03_adjusted_associations.csv')
    expected = frozen[frozen.subset == label].set_index('feature').loc[FEATURES]
    np.testing.assert_allclose(fit.params[FEATURES], expected.coefficient, rtol=1e-9, atol=1e-10)
    p = fit.predict(x).to_numpy()
    xa = x.to_numpy()
    inv_y = np.linalg.inv(xa.T @ ((p*(1-p))[:, None] * xa))
    # Each row is an unscaled observation contribution; sums of outer products
    # give the HC0 covariance, including cross-equation blocks.
    influence = [ma @ inv_m[:, a_index] * f.resid.to_numpy() for f in a_fits]
    outcome_features = FEATURES[1:] + FEATURES[:1]
    influence += [xa @ inv_y[:, x.columns.get_loc(f)] * (y.to_numpy()-p) for f in outcome_features]
    influence = np.column_stack(influence)
    covariance = influence.T @ influence
    theta = np.array([f.params[FEATURES[0]] for f in a_fits] + list(fit.params[outcome_features]))
    se = np.sqrt(np.diag(covariance))
    np.testing.assert_allclose(se, [f.bse[FEATURES[0]] for f in a_fits] + list(fit.bse[outcome_features]), rtol=1e-6)
    if np.linalg.eigvalsh(covariance).min() < -1e-10:
        raise ValueError('Invalid joint covariance')
    draws = rng.multivariate_normal(theta, covariance, size=50000, check_valid='raise')
    rows = []
    paths = [f'长度→{NAMES[f]}' for f in FEATURES[1:]] + [f'{NAMES[f]}→选择' for f in outcome_features]
    pvals = [f.pvalues[FEATURES[0]] for f in a_fits] + list(fit.pvalues[outcome_features])
    for i, name in enumerate(paths):
        rows.append(dict(subset=label, n=len(part), path=name, estimate=theta[i], se=se[i],
                         ci_low=theta[i]-1.96*se[i], ci_high=theta[i]+1.96*se[i], p_value=pvals[i],
                         log_p_value=float(np.log(2) + scipy.stats.norm.logsf(abs(theta[i]/se[i])))))
    products = []
    for j, f in enumerate(FEATURES[1:]):
        low, high = np.quantile(draws[:, j]*draws[:, j+3], [.025, .975])
        products.append(dict(subset=label, n=len(part), path=f'长度→{NAMES[f]}→选择',
                             estimate=theta[j]*theta[j+3], ci_low=low, ci_high=high))
    low, high = np.quantile((draws[:, :3]*draws[:, 3:6]).sum(axis=1), [.025, .975])
    products.append(dict(subset=label, n=len(part), path='三条乘积之和',
                         estimate=float(theta[:3] @ theta[3:6]), ci_low=low, ci_high=high))
    scaling.to_csv(OUT / f'scaling_{label}.csv', index_label='feature')
    pd.DataFrame(covariance, index=paths, columns=paths).to_csv(OUT / f'joint_covariance_{label}.csv')
    all_terms = []
    for equation, result in list(zip(FEATURES[1:], a_fits)) + [('winner_a', fit)]:
        for term in result.params.index:
            all_terms.append(dict(equation=equation, term=term, estimate=result.params[term], se=result.bse[term]))
    pd.DataFrame(all_terms).to_csv(OUT / f'all_terms_{label}.csv', index=False)
    pd.DataFrame({f: a_fits[i].resid for i, f in enumerate(FEATURES[1:])}).corr().to_csv(OUT / f'format_residual_correlations_{label}.csv')
    return rows, products, dict(subset=label, n=len(part), design_rank=x.shape[1],
                               reference_model=models[0], converged=bool(fit.converged),
                               outcome_matches_frozen=True)


def main():
    OUT.mkdir(exist_ok=True)
    source_manifest = json.loads((ROOT / 'Reports/integrated-20260920/R00_run_manifest.json').read_text(encoding='utf-8'))
    # Locate the frozen input digest without relying on a current pointer change.
    source_hash = sha(SOURCE)
    if source_manifest['status'] != 'complete' or source_hash != source_manifest['outputs'][SOURCE.relative_to(ROOT).as_posix()]:
        raise ValueError('Input is not the frozen analysis artifact')
    df = pd.read_parquet(SOURCE)
    assert len(df) == 108154 and df.evaluation_session_id.is_unique
    rng = np.random.default_rng(20260921)
    paths, products, diagnostics = [], [], []
    for label, part in [('full', df), ('english', df[df.language == 'en']), ('single_turn', df[df.turns == 1])]:
        print(f'Fitting {label}', flush=True)
        r, q, d = analyze(part, label, rng)
        paths.extend(r); products.extend(q); diagnostics.append(d)
    paths = pd.DataFrame(paths)
    paths['p_holm'] = multipletests(paths.p_value, method='holm')[1]
    paths.to_csv(OUT / 'paths.csv', index=False)
    products = pd.DataFrame(products)
    products.to_csv(OUT / 'path_products.csv', index=False)
    manifest = dict(status='complete', source=str(SOURCE.relative_to(ROOT)), source_sha256=source_hash,
                    script_sha256=sha(Path(__file__)), seed=20260921, normal_simulation_draws=50000,
                    method='OLS + logit; cross-equation HC0; joint-normal Monte Carlo product intervals, not bootstrap',
                    versions=dict(python=platform.python_version(), numpy=np.__version__, pandas=pd.__version__,
                                  scipy=scipy.__version__, statsmodels=statsmodels.__version__),
                    diagnostics=diagnostics, independence='pairs; no user/prompt clustering',
                    scaling='fixed sample means and population SDs; intervals conditional on this scaling',
                    artifacts={p.name: sha(p) for p in sorted(OUT.glob('*.csv'))})
    (OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(paths.to_string(index=False))
    print(products.to_string(index=False))


if __name__ == '__main__':
    main()
