"""C02: paired descriptive tests; preserve the final-v3 specification."""
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

def paired(d):
    d = np.asarray(d, dtype=float)
    if not np.isfinite(d).all():
        raise ValueError('Nonfinite paired differences')
    nz = d[d != 0]
    wins = int((nz > 0).sum())
    test = stats.binomtest(wins, len(nz), .5) if len(nz) else None
    ci = test.proportion_ci() if test else (np.nan, np.nan)
    ranks = stats.rankdata(abs(nz))
    r = float(np.dot(np.sign(nz), ranks) / ranks.sum()) if len(nz) else 0.
    return dict(n=len(d), nonzero=len(nz), positive=wins, equal=int((d == 0).sum()),
                positive_fraction=wins / len(nz) if len(nz) else np.nan,
                ci_low=ci[0], ci_high=ci[1], median=float(np.median(d)),
                p_sign=test.pvalue if test else 1., rank_biserial=r,
                p_wilcoxon=float(stats.wilcoxon(nz, alternative='two-sided',
                                               method='asymptotic').pvalue) if len(nz) else 1.)


def descriptive(df, out):
    rows = []
    groups = [('full', df), ('english', df[df.language == 'en']), ('single_turn', df[df.turns == 1])]
    groups += [(f'task_mask_{mask:04b}', df[(df[['cw', 'if', 'math', 'code']].to_numpy() @ np.array([1,2,4,8])) == mask]) for mask in range(16)]
    for label, subset in groups:
        subset = subset[subset.winner.isin(['model_a', 'model_b'])]
        if len(subset) == 0:
            continue
        sign = np.where(subset.winner == 'model_a', 1, -1)
        for feature in ['tokens', 'header', 'list', 'bold']:
            delta = subset[f'{feature}_a'] - subset[f'{feature}_b']
            rows.append(dict(subset=label, feature=feature, measure='count', **paired(delta * sign)))
            if feature != 'tokens':
                delta = 1000 * (subset[f'{feature}_a'] / subset.tokens_a - subset[f'{feature}_b'] / subset.tokens_b)
                rows.append(dict(subset=label, feature=feature, measure='per_1000_tokens', **paired(delta * sign)))
                delta = (subset[f'{feature}_a'] > 0).astype(int) - (subset[f'{feature}_b'] > 0).astype(int)
                rows.append(dict(subset=label, feature=feature, measure='presence_mcnemar_exact', **paired(delta * sign)))
    table = pd.DataFrame(rows)
    # Explicit family: every reported descriptive sign/McNemar test, including sensitivities.
    table['p_holm'] = multipletests(table.p_sign, method='holm')[1]
    table.to_csv(out / 'paired_tests.csv', index=False)
    return table
