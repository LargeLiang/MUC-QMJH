"""C03: observational associations with model-identity contrasts (not causal effects)."""
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
from accessor import CRITERIA

def regressions(df, out):
    rows = []
    for label, part in [('full', df), ('english', df[df.language == 'en']),
                        ('single_turn', df[df.turns == 1])]:
        part = part[part.winner.isin(['model_a', 'model_b'])].copy()
        x = pd.DataFrame(index=part.index)
        x['log_token_ratio'] = np.log(part.tokens_a / part.tokens_b)
        for feature in ['header', 'list', 'bold']:
            x[f'{feature}_density_diff'] = 1000 * (part[f'{feature}_a'] / part.tokens_a - part[f'{feature}_b'] / part.tokens_b)
        focal = list(x.columns)
        scaling = []
        for col in focal:
            scaling.append(dict(feature=col, mean=x[col].mean(), sd=x[col].std(ddof=0)))
            x[col] = (x[col] - x[col].mean()) / x[col].std(ddof=0)
        pd.DataFrame(scaling).to_csv(out / f'scaling_{label}.csv', index=False)
        x['log_user_tokens'] = np.log1p(part.user_tokens)
        x['turns'] = part.turns
        for col in ['cw', 'if', 'math', 'code'] + CRITERIA:
            x[col] = part[col]
        language = part.language.where(part.language.map(part.language.value_counts()) >= 100, '__rare__')
        x = pd.concat([x, pd.get_dummies(language, prefix='language', drop_first=True, dtype=float)], axis=1)
        # Bradley-Terry model identity contrasts; no outcome-derived ability proxy.
        models = sorted(set(part.model_a) | set(part.model_b))
        for model in models[1:]:
            x['model:' + model] = (part.model_a == model).astype(float) - (part.model_b == model).astype(float)
        x = x.loc[:, x.nunique() > 1].astype(float)
        x = sm.add_constant(x)
        # Detect nonidentifiability rather than silently dropping model/control columns.
        if np.linalg.matrix_rank(x.to_numpy()) != x.shape[1]:
            raise ValueError(f'Rank deficient design: {label}')
        print(f'Fitting {label}: {len(part)} pairs, {x.shape[1]} coefficients', flush=True)
        result = sm.GLM((part.winner == 'model_a').astype(int), x,
                        family=sm.families.Binomial()).fit(maxiter=150, cov_type='HC0')
        if not result.converged or not np.isfinite(result.params).all():
            raise RuntimeError(f'Unconverged regression: {label}')
        prob = result.predict(x)
        for feature in focal:
            beta, se = result.params[feature], result.bse[feature]
            rows.append(dict(subset=label, feature=feature, n=len(part), coefficient=beta,
                             robust_se=se, odds_ratio=np.exp(beta), ci_low=np.exp(beta-1.96*se),
                             ci_high=np.exp(beta+1.96*se), p_value=result.pvalues[feature],
                             log_p_value=float(np.log(2) + stats.norm.logsf(abs(beta/se))),
                             average_derivative_per_sd=float(np.mean(prob*(1-prob))*beta),
                             converged=result.converged, design_rank=x.shape[1]))
        pd.DataFrame({'term': result.params.index, 'coefficient': result.params,
                      'robust_se': result.bse, 'p_value': result.pvalues}).to_csv(out / f'model_{label}_all_terms.csv', index=False)
    table = pd.DataFrame(rows)
    table['p_holm'] = multipletests(table.p_value, method='holm')[1]
    table.to_csv(out / 'adjusted_associations.csv', index=False)
    return table
