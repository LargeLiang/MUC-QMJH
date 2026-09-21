"""Build descriptive audit strata and paper figures from the frozen current run.

No relabeling, causal estimation, or validation of audit efficiency is performed.
Run from any directory: python path/to/build_audit.py
"""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import binomtest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUN = 'integrated-20260920'
SOURCE = ROOT / 'Data/analysis_data' / RUN / 'analysis_data.parquet'
OUT = HERE / 'assets'
OUT.mkdir(exist_ok=True)
df = pd.read_parquet(SOURCE)
assert len(df) == 108154 and df.evaluation_session_id.is_unique
ratio = np.maximum(df.tokens_a, df.tokens_b) / np.minimum(df.tokens_a, df.tokens_b)
df['audit_stratum'] = pd.cut(ratio, [0, 1.25, 2, np.inf], labels=['R<=1.25', '1.25<R<=2', 'R>2'])
decisive = df.winner.isin(['model_a', 'model_b'])
assert int(decisive.sum()) == 78959
rows = []
for label, group in df.groupby('audit_stratum', observed=True):
    d = group[group.winner.isin(['model_a', 'model_b'])]
    unequal = d[d.tokens_a != d.tokens_b]
    longer_wins = ((unequal.tokens_a > unequal.tokens_b) == (unequal.winner == 'model_a')).sum()
    ci = binomtest(int(longer_wins), len(unequal)).proportion_ci()
    bold_diff = d.bold_a / d.tokens_a - d.bold_b / d.tokens_b
    nonzero_bold = bold_diff != 0
    bold_wins = ((bold_diff[nonzero_bold] > 0) == (d.loc[nonzero_bold, 'winner'] == 'model_a')).sum()
    rows.append(dict(stratum=str(label), retained_n=len(group), decisive_n=len(d),
                     tie_n=int((group.winner == 'tie').sum()), both_bad_n=int((group.winner == 'both_bad').sum()),
                     non_decisive_fraction=1-len(d)/len(group), unequal_n=len(unequal),
                     longer_wins=int(longer_wins), longer_win_fraction=longer_wins/len(unequal),
                     ci_low=ci.low, ci_high=ci.high, bold_unequal_n=int(nonzero_bold.sum()),
                     bold_density_wins=int(bold_wins), bold_density_win_fraction=bold_wins/nonzero_bold.sum()))
audit = pd.DataFrame(rows)
assert audit.retained_n.sum() == len(df)
assert audit.decisive_n.sum() == decisive.sum()
audit.to_csv(OUT / 'audit_strata.csv', index=False, encoding='utf-8-sig')

plt.rcParams.update({'font.sans-serif': ['Microsoft YaHei', 'SimHei'], 'axes.unicode_minus': False,
                     'font.size': 10, 'savefig.dpi': 220, 'axes.spines.top': False, 'axes.spines.right': False})
reg = pd.read_csv(ROOT / 'Tables' / RUN / 'T03_adjusted_associations.csv')
features = ['log_token_ratio', 'header_density_diff', 'bold_density_diff', 'list_density_diff']
labels = ['长度对数比', '标题密度差', '粗体密度差', '列表密度差']
fig, axes = plt.subplots(1, 2, figsize=(9, 3.6), gridspec_kw={'width_ratios': [1, 1.8]})
for ax, fs, ls in [(axes[0], features[:1], labels[:1]), (axes[1], features[1:], labels[1:])]:
    for k, (subset, title, color) in enumerate([('full','全量','#245a81'),('english','英语','#b16c35'),('single_turn','单轮','#438979')]):
        part = reg[reg.subset == subset].set_index('feature').loc[fs]
        y = np.arange(len(fs)) + (k-1)*.18
        ax.errorbar(part.odds_ratio, y, xerr=np.array([part.odds_ratio-part.ci_low,part.ci_high-part.odds_ratio]),
                    fmt='o', ms=4, capsize=3, color=color, label=title)
    ax.set_yticks(range(len(fs)), ls)
    ax.invert_yaxis()
    ax.axvline(1,color='#888888',lw=.8,ls='--')
    ax.set_xlabel('每标准差的 OR 及 95% 逐项区间')
    ax.grid(axis='x',alpha=.18)
axes[0].set_xlim(1.48,1.71)
axes[1].set_xlim(.94,1.13)
axes[1].legend(loc='upper right', frameon=False)
fig.tight_layout()
fig.savefig(OUT / 'adjusted_associations.pdf', bbox_inches='tight')
fig.savefig(OUT / 'adjusted_associations.png', bbox_inches='tight')
plt.close(fig)

fig, ax = plt.subplots(figsize=(7, 3.3))
for j, row in audit.iterrows():
    ax.errorbar(row.longer_win_fraction*100, j,
                xerr=np.array([[row.longer_win_fraction-row.ci_low],[row.ci_high-row.longer_win_fraction]])*100,
                fmt='o',color='#245a81',capsize=4)
    ax.text(83,j,f'n={row.unequal_n:,}',va='center',fontsize=9)
ax.set_yticks(range(3), ['长度接近：R≤1.25','中等差异：1.25<R≤2','较大差异：R>2'])
ax.invert_yaxis()
ax.axvline(50,color='#999999',ls='--',lw=.8)
ax.set_xlim(47,98)
ax.set_xlabel('不等长且明确胜负配对中，较长回答获胜比例（%）')
ax.grid(axis='x', alpha=.18)
fig.tight_layout()
fig.savefig(OUT / 'audit_strata.pdf',bbox_inches='tight')
fig.savefig(OUT / 'audit_strata.png',bbox_inches='tight')
plt.close(fig)

metadata = {'run':RUN, 'source':str(SOURCE.relative_to(ROOT)),
            'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            'thresholds':[1.25,2], 'scope':'Post-hoc descriptive audit illustration; not an efficiency validation.',
            'counts':{'retained':len(df),'decisive':int(decisive.sum())}}
(OUT / 'audit_manifest.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(audit.to_string(index=False))
