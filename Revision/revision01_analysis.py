"""Revision 01: frozen-data sensitivity analyses and blinded format audit pack.

Run with the repository's locked analysis Python environment. Does not promote
or modify CURRENT_RESULTS.json. Local response text stays under Data/.
"""
import os
for k in ('OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'OMP_NUM_THREADS'):
    os.environ[k] = '2'
from pathlib import Path
import hashlib, json, sys, unicodedata, warnings
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import mistune
import scipy
from scipy import stats, special
import statsmodels.api as sm
from statsmodels.stats.sandwich_covariance import cov_cluster
from statsmodels.stats.multitest import multipletests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'Codes'))
from accessor import CRITERIA, digest
OUT = ROOT/'Revision/revision01_v3'
PRIVATE = ROOT/'Data/analysis_data/revision01-v3'
SOURCE = ROOT/'Data/analysis_data/integrated-20260920/analysis_data.parquet'
F = ['log_token_ratio', 'header_density_diff', 'list_density_diff', 'bold_density_diff']
GROUPS = ['prompt_first', 'prompt_sequence', 'model_pair']
MD = mistune.create_markdown(renderer='ast')


def dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')


def count_format(text):
    counts = dict(header=0, list=0, bold=0)
    def walk(nodes):
        for node in nodes:
            key = {'heading':'header', 'list_item':'list', 'strong':'bold'}.get(node['type'])
            if key: counts[key] += 1
            # Code/raw HTML contents are not interpreted as Markdown.
            if node['type'] not in ('block_code', 'codespan', 'block_html', 'inline_html'):
                walk(node.get('children', []))
    walk(MD(text))
    return counts


def texts(conv, role):
    return [''.join(p.get('text') or '' for p in m['content'] if p.get('type') == 'text')
            for m in conv if m['role'] == role]


def prompt_hash(seq):
    normalized = [unicodedata.normalize('NFC', s.replace('\r\n','\n').replace('\r','\n')) for s in seq]
    return hashlib.sha256(json.dumps(normalized, ensure_ascii=False).encode()).hexdigest()


def prepare():
    frozen = json.loads((ROOT/'Reports/integrated-20260920/R00_run_manifest.json').read_text())
    assert digest(SOURCE) == frozen['outputs'][SOURCE.relative_to(ROOT).as_posix()]
    df = pd.read_parquet(SOURCE)
    assert len(df) == 108154 and df.id.is_unique and df.evaluation_session_id.is_unique
    PRIVATE.mkdir(parents=True, exist_ok=True)
    cache = PRIVATE/'extended.parquet'
    if cache.exists():
        meta = json.loads((PRIVATE/'cache.json').read_text())
        assert meta['source_sha256'] == digest(SOURCE)
        assert meta['parser_version'] == mistune.__version__
        assert meta['extended_sha256'] == digest(cache)
        raw_expected=json.loads((ROOT/'Reports/integrated-20260920/R01_inputs.json').read_text())
        for item in raw_expected:
            assert meta['raw_sha256'][item['path'].replace('\\','/')] == item['sha256']
        return pd.read_parquet(cache)
    # Stratified response sample: upstream presence of heading/list/bold, 8 strata.
    frame = []
    for side in ('a','b'):
        for row in df[['id',f'header_{side}',f'list_{side}',f'bold_{side}']].itertuples(index=False, name=None):
            ident, h,l,b = row
            frame.append((ident, side, int(h>0)*4+int(l>0)*2+int(b>0), h,l,b))
    frame = pd.DataFrame(frame, columns=['id','side','stratum','header','list','bold'])
    selected = frame.groupby('stratum', group_keys=False).sample(n=50, random_state=20260921)
    selected = selected.sample(frac=1, random_state=20260922).reset_index(drop=True)
    selected['audit_id'] = [f'F{i+1:03d}' for i in range(len(selected))]
    selected['population_n'] = selected.stratum.map(frame.stratum.value_counts())
    selected['inclusion_probability'] = 50/selected.population_n
    selected.to_csv(PRIVATE/'format_audit_key.csv', index=False)
    sample_keys = {(r.id,r.side): r.audit_id for r in selected.itertuples()}
    wanted = set(df.id)
    extra, audit, raw_hashes = [], [], {}
    for path in sorted((ROOT/'Data/lmarena-aiarena-human-preference-140k/Data').glob('*.parquet')):
        print('Parsing', path.name, flush=True)
        raw_hashes[path.relative_to(ROOT).as_posix()] = digest(path)
        for batch in pq.ParquetFile(path).iter_batches(batch_size=128, columns=['id','timestamp','conversation_a','conversation_b']):
            for row in batch.to_pylist():
                if row['id'] not in wanted: continue
                user = texts(row['conversation_a'], 'user')
                d = dict(id=row['id'], month=str(pd.Timestamp(row['timestamp']).to_period('M')),
                         prompt_first=prompt_hash(user[:1]), prompt_sequence=prompt_hash(user))
                for side in ('a','b'):
                    answer = texts(row[f'conversation_{side}'], 'assistant')
                    counts = [count_format(s) for s in answer]
                    for f in ('header','list','bold'):
                        d[f'alt_{f}_{side}'] = sum(c[f] for c in counts)
                    aid = sample_keys.get((row['id'],side))
                    if aid:
                        audit.append(dict(audit_id=aid, assistant_messages=answer,
                                          reviewer_1=None, reviewer_2=None, adjudicated=None))
                extra.append(d)
    ex = pd.DataFrame(extra)
    df = df.merge(ex, on='id', validate='one_to_one')
    assert len(df) == 108154 and not df.month.isna().any()
    df['model_pair'] = [json.dumps(sorted([a,b])) for a,b in zip(df.model_a,df.model_b)]
    df.to_parquet(cache, index=False)
    with (PRIVATE/'format_audit_blinded.jsonl').open('w', encoding='utf-8') as file:
        for row in sorted(audit, key=lambda x: x['audit_id']):
            file.write(json.dumps(row, ensure_ascii=False)+'\n')
    assert len(audit) == 400
    dump(PRIVATE/'cache.json', dict(source_sha256=digest(SOURCE), parser_version=mistune.__version__,
                                  extended_sha256=digest(cache), raw_sha256=raw_hashes))
    return df


def features(df, alt=False, presence=False):
    x = pd.DataFrame(index=df.index)
    x[F[0]] = np.log(df.tokens_a/df.tokens_b)
    for f in ('header','list','bold'):
        p = 'alt_' if alt else ''
        a,b = df[f'{p}{f}_a'],df[f'{p}{f}_b']
        x[f'{f}_density_diff'] = (a.gt(0).astype(float)-b.gt(0).astype(float)) if presence else 1000*(a/df.tokens_a-b/df.tokens_b)
    return x


def design(df, scaling, alt=False, presence=False, month=False, symmetric=False, reference=None):
    x = features(df, alt, presence)
    if symmetric: x = x.abs()
    x = (x-scaling['mean'])/scaling['sd']
    x['log_user_tokens'] = np.log1p(df.user_tokens)
    x['turns'] = df.turns
    for f in ['cw','if','math','code']+CRITERIA: x[f] = df[f]
    lang = df.language.where(df.language.map(df.language.value_counts())>=100,'__rare__')
    x = pd.concat([x,pd.get_dummies(lang,prefix='language',drop_first=True,dtype=float)],axis=1)
    models = sorted(set(df.model_a)|set(df.model_b))
    reference = reference or models[0]
    for model in models:
        if model == reference: continue
        a,b = (df.model_a==model).astype(float),(df.model_b==model).astype(float)
        x['model:'+model] = a+b if symmetric else a-b
    if month:
        x = pd.concat([x,pd.get_dummies(df.month,prefix='month',drop_first=True,dtype=float)],axis=1)
    return sm.add_constant(x.loc[:,x.nunique()>1].astype(float))


def fit_glm(x,y):
    assert np.isfinite(x).all().all() and np.linalg.matrix_rank(x)==x.shape[1]
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        fit = sm.GLM(y,x,family=sm.families.Binomial()).fit(maxiter=150,cov_type='HC0')
    if not fit.converged or not np.isfinite(fit.params).all(): raise ValueError('Invalid GLM fit')
    if any('separation' in str(w.message).lower() for w in caught): raise ValueError('Separation warning')
    return fit


def inference(fit, x, df, label, diagnostics):
    rows=[]; covs={'HC0':np.asarray(fit.cov_params())}
    for group in GROUPS:
        codes,values=pd.factorize(df[group])
        covs[group]=cov_cluster(fit,codes,use_correction=True)
        counts=np.bincount(codes)
        diagnostics.append(dict(model=label,scheme=group,n=len(df),clusters=len(values),
                                singleton_clusters=int((counts==1).sum()),max_cluster=int(counts.max()),
                                median_cluster=float(np.median(counts)),df=len(values)-1))
    for scheme,cov in covs.items():
        dof=np.inf if scheme=='HC0' else df[scheme].nunique()-1
        dist=stats.norm if scheme=='HC0' else stats.t(dof)
        critical=dist.ppf(.975)
        for f in F:
            j=x.columns.get_loc(f); b=fit.params[f]; se=np.sqrt(cov[j,j]); z=b/se
            rows.append(dict(model=label,scheme=scheme,n=len(df),feature=f,beta=b,se=se,
                             odds_ratio=np.exp(b),ci_low=np.exp(b-critical*se),ci_high=np.exp(b+critical*se),
                             p_value=2*dist.sf(abs(z)),log_p_value=float(np.log(2)+dist.logsf(abs(z)))))
    return rows,covs


def rcs(values, knots):
    x=np.asarray(values); t=np.asarray(knots); scale=(t[-1]-t[0])**2
    return np.column_stack([(np.maximum(x-t[j],0)**3-
            np.maximum(x-t[-2],0)**3*(t[-1]-t[j])/(t[-1]-t[-2])+
            np.maximum(x-t[-1],0)**3*(t[-2]-t[j])/(t[-1]-t[-2]))/scale for j in range(len(t)-2)])


def sem(df,x,fit,label,rng):
    m=x.drop(columns=F[1:]); ma=m.to_numpy(); inv=np.linalg.inv(ma.T@ma)
    ai=m.columns.get_loc(F[0])
    fits=[sm.OLS(x[f],m).fit(cov_type='HC0') for f in F[1:]]
    xa=x.to_numpy(); p=fit.predict(x).to_numpy(); y=(df.winner=='model_a').astype(float).to_numpy()
    iy=np.linalg.inv(xa.T@((p*(1-p))[:,None]*xa))
    infl=[ma@inv[:,ai]*r.resid.to_numpy() for r in fits]
    order=F[1:]+F[:1]
    infl += [xa@iy[:,x.columns.get_loc(f)]*(y-p) for f in order]
    infl=np.column_stack(infl)
    theta=np.array([r.params[F[0]] for r in fits]+list(fit.params[order]))
    np.testing.assert_allclose(np.sqrt((infl**2).sum(axis=0)),[r.bse[F[0]] for r in fits]+list(fit.bse[order]),rtol=1e-6)
    paths=[]; products=[]
    for group in ['HC0']+GROUPS:
        if group=='HC0': covariance=infl.T@infl; dist=stats.norm
        else:
            codes,vals=pd.factorize(df[group]); g=len(vals); n=len(df)
            sums=np.zeros((g,7)); np.add.at(sums,codes,infl)
            correction=np.sqrt(g/(g-1)*(n-1)/(n-np.array([m.shape[1]]*3+[x.shape[1]]*4)))
            sums*=correction
            covariance=sums.T@sums; dist=stats.t(g-1)
        assert np.linalg.eigvalsh(covariance).min()>-1e-10
        draws=rng.multivariate_normal(theta,covariance,size=50000,check_valid='raise')
        for j,f in enumerate(F[1:]):
            lo,hi=np.quantile(draws[:,j]*draws[:,j+3],[.025,.975])
            products.append(dict(model=label,scheme=group,via=f,estimate=theta[j]*theta[j+3],ci_low=lo,ci_high=hi))
        for j in range(7):
            se=np.sqrt(covariance[j,j]); crit=dist.ppf(.975)
            paths.append(dict(model=label,scheme=group,path=(f'length_to_{F[j+1]}' if j<3 else f'{order[j-3]}_to_choice'),
                              estimate=theta[j],se=se,ci_low=theta[j]-crit*se,ci_high=theta[j]+crit*se,p_value=2*dist.sf(abs(theta[j]/se))))
        pd.DataFrame(covariance).to_csv(OUT/f'sem_cov_{label}_{group}.csv',index=False)
    return paths,products


def main():
    OUT.mkdir(exist_ok=True); dump(OUT/'manifest.json',dict(status='running'))
    df=prepare(); decisive=df[df.winner.isin(['model_a','model_b'])].copy()
    scale=pd.DataFrame({'mean':features(decisive).mean(),'sd':features(decisive).std(ddof=0)})
    scale.to_csv(OUT/'scaling.csv',index_label='feature')
    diagnostics=[]; rows=[]; path_rows=[]; prod_rows=[]; fits={}; designs={}; covariance={}
    rng=np.random.default_rng(20260921)
    for label,part in [('full',decisive),('english',decisive[decisive.language=='en']),('single_turn',decisive[decisive.turns==1])]:
        print('Fitting',label,flush=True)
        x=design(part,scale); fit=fit_glm(x,(part.winner=='model_a').astype(int))
        r,c=inference(fit,x,part,label,diagnostics); rows+=r
        fits[label]=fit; designs[label]=x; covariance[label]=c
        a,b=sem(part,x,fit,label,rng); path_rows+=a; prod_rows+=b
    # Reproduce frozen probabilities through the old scaling parameterization.
    frozen=pd.read_csv(ROOT/'Tables/integrated-20260920/T03_adjusted_associations.csv')
    np.testing.assert_allclose(fits['full'].params[F],frozen[frozen.subset=='full'].set_index('feature').loc[F].coefficient,rtol=1e-9)
    # Reference-model invariance check.
    ref=sorted(set(decisive.model_a)|set(decisive.model_b))[-1]
    xr=design(decisive,scale,reference=ref); fr=fit_glm(xr,(decisive.winner=='model_a').astype(int))
    np.testing.assert_allclose(fr.params[F],fits['full'].params[F],rtol=1e-7,atol=1e-9)
    np.testing.assert_allclose(fr.predict(xr),fits['full'].predict(designs['full']),atol=1e-8)
    # Prespecified one-at-a-time sensitivity variants.
    for label,part,kw in [('month',decisive,dict(month=True)),('alternative_format',decisive,dict(alt=True)),
                          ('format_presence',decisive,dict(presence=True)),
                          ('trim_1_99',decisive[features(decisive)[F[0]].between(*features(decisive)[F[0]].quantile([.01,.99]))],{})]:
        print('Fitting',label,flush=True)
        variant_scale=scale
        if label=='format_presence':
            fp=features(decisive,presence=True)
            variant_scale=pd.DataFrame({'mean':fp.mean(),'sd':fp.std(ddof=0)})
            variant_scale.to_csv(OUT/'presence_scaling.csv',index_label='feature')
        x=design(part,variant_scale,**kw); fit=fit_glm(x,(part.winner=='model_a').astype(int))
        r,c=inference(fit,x,part,label,diagnostics); rows+=r
        if label=='alternative_format':
            a,b=sem(part,x,fit,label,rng); path_rows+=a; prod_rows+=b
    # Spline replaces only the linearity restriction, with fixed 5/35/65/95% knots.
    x=designs['full'].copy(); knots=np.quantile(x[F[0]],[.05,.35,.65,.95]); basis=rcs(x[F[0]],knots)
    for j in range(2): x[f'length_rcs{j}']=basis[:,j]
    fit=fit_glm(x,(decisive.winner=='model_a').astype(int))
    r,c=inference(fit,x,decisive,'spline_format',diagnostics)
    rows += [entry for entry in r if entry['feature'] != F[0]]
    spline_tests=[]; spline_cov={}
    for scheme in ['HC0']+GROUPS:
        cov=np.asarray(fit.cov_params()) if scheme=='HC0' else cov_cluster(fit,pd.factorize(decisive[scheme])[0],use_correction=True)
        spline_cov[scheme]=cov
        idx=[x.columns.get_loc(f'length_rcs{j}') for j in range(2)]; b=fit.params.iloc[idx].to_numpy()
        w=float(b@np.linalg.solve(cov[np.ix_(idx,idx)],b))
        pv=stats.chi2.sf(w,2) if scheme=='HC0' else stats.f.sf(w/2,2,decisive[scheme].nunique()-1)
        spline_tests.append(dict(scheme=scheme,wald=w,df=2,p_value=pv))
    pd.DataFrame(spline_tests).to_csv(OUT/'spline_tests.csv',index=False)
    predictions=[]
    for ratio in np.geomspace(.25,4,61):
        value=(np.log(ratio)-scale.loc[F[0],'mean'])/scale.loc[F[0],'sd']
        for kind,mat,res,cov in [('linear',designs['full'],fits['full'],covariance['full']['prompt_first']),('spline',x,fit,spline_cov['prompt_first'])]:
            xx=mat.to_numpy().copy(); xx[:,mat.columns.get_loc(F[0])]=value
            if kind=='spline':
                bb=rcs([value],knots)[0]
                for j in range(2): xx[:,mat.columns.get_loc(f'length_rcs{j}')]=bb[j]
            p=special.expit(xx@res.params.to_numpy()); gradient=(xx*(p*(1-p))[:,None]).mean(axis=0)
            se=np.sqrt(gradient@cov@gradient); crit=stats.t.ppf(.975,decisive.prompt_first.nunique()-1)
            predictions.append(dict(model=kind,ratio=ratio,prediction=p.mean(),ci_low=max(0,p.mean()-crit*se),ci_high=min(1,p.mean()+crit*se)))
    pd.DataFrame(predictions).to_csv(OUT/'predictions.csv',index=False)
    dump(OUT/'spline.json',dict(knots_standardized=knots.tolist(),knots_log_ratio=(knots*scale.loc[F[0],'sd']+scale.loc[F[0],'mean']).tolist(),
                              observed_log_ratio_quantiles=features(decisive)[F[0]].quantile([.01,.05,.5,.95,.99]).to_dict(),
                              linear_aic=fits['full'].aic,spline_aic=fit.aic))
    # Symmetric decisiveness equation, all outcomes retained.
    dscale=pd.DataFrame({'mean':features(df).abs().mean(),'sd':features(df).abs().std(ddof=0)})
    dscale.to_csv(OUT/'decisive_scaling.csv',index_label='feature')
    xd=design(df,dscale,symmetric=True,month=True)
    yd=df.winner.isin(['model_a','model_b']).astype(int); fd=fit_glm(xd,yd)
    r,c=inference(fd,xd,df,'decisive_stage',diagnostics); rows+=r
    # Monthly outcomes and model coverage, descriptive only.
    pd.crosstab(df.month,df.winner).to_csv(OUT/'monthly_outcomes.csv')
    pd.concat([df[['month','model_a']].rename(columns={'model_a':'model'}),df[['month','model_b']].rename(columns={'model_b':'model'})]).groupby(['month','model']).size().rename('appearances').to_csv(OUT/'monthly_model_coverage.csv')
    # Measurement agreement, not accuracy against human truth.
    agreement=[]
    for f in ('header','list','bold'):
        upstream=np.concatenate([df[f'{f}_{s}'] for s in ('a','b')]); alt=np.concatenate([df[f'alt_{f}_{s}'] for s in ('a','b')])
        agreement.append(dict(feature=f,n=len(upstream),exact_count_agreement=float(np.mean(upstream==alt)),
                              presence_agreement=float(np.mean((upstream>0)==(alt>0))),mean_abs_count_difference=float(np.mean(abs(upstream-alt)))))
    pd.DataFrame(agreement).to_csv(OUT/'format_agreement.csv',index=False)
    pd.DataFrame(diagnostics).to_csv(OUT/'cluster_diagnostics.csv',index=False)
    table=pd.DataFrame(rows)
    # Primary family: 3 subsets x 4 focal features, separately per SE scheme.
    table['p_holm']=np.nan
    for scheme in table.scheme.unique():
        for family in [['full','english','single_turn'],['month','alternative_format','format_presence','trim_1_99'],['decisive_stage'],['spline_format']]:
            mask=(table.scheme==scheme)&table.model.isin(family)
            table.loc[mask,'p_holm']=multipletests(table.loc[mask,'p_value'],method='holm')[1]
    table.to_csv(OUT/'associations.csv',index=False)
    paths=pd.DataFrame(path_rows); paths['p_holm']=np.nan
    for scheme in paths.scheme.unique():
        for family in [['full','english','single_turn'],['alternative_format']]:
            mask=(paths.scheme==scheme)&paths.model.isin(family)
            paths.loc[mask,'p_holm']=multipletests(paths.loc[mask,'p_value'],method='holm')[1]
    paths.to_csv(OUT/'sem_paths.csv',index=False); pd.DataFrame(prod_rows).to_csv(OUT/'sem_products.csv',index=False)
    # Undirected comparison graph and unordered-pair diagnostics.
    nodes=set(decisive.model_a)|set(decisive.model_b); adj={m:set() for m in nodes}
    for a,b in zip(decisive.model_a,decisive.model_b): adj[a].add(b);adj[b].add(a)
    unseen=set(nodes); sizes=[]
    while unseen:
        stack=[unseen.pop()]; size=0
        while stack:
            v=stack.pop();size+=1
            for w in adj[v]&unseen: unseen.remove(w);stack.append(w)
        sizes.append(size)
    pair=decisive.copy(); pair['canonical_win']=np.where(pair.model_a<=pair.model_b,pair.winner=='model_a',pair.winner=='model_b')
    pp=pair.groupby('model_pair').canonical_win.agg(['size','sum']); pp.to_csv(OUT/'model_pair_counts.csv')
    dump(OUT/'identification.json',dict(models=len(nodes),connected_components=sizes,design_rank=designs['full'].shape[1],
         reference_invariance_passed=True,model_pairs=len(pp),pairs_under20=int((pp['size']<20).sum()),
         one_outcome_pairs=int(((pp['sum']==0)|(pp['sum']==pp['size'])).sum()),
         converged=True,separation_warning=False,formal_separation_lp_test=False,
         min_predicted=float(fits['full'].fittedvalues.min()),max_predicted=float(fits['full'].fittedvalues.max())))
    manifest=dict(status='complete',seed=20260921,input_sha256=digest(SOURCE),extended_sha256=digest(PRIVATE/'extended.parquet'),
                  script_sha256=digest(Path(__file__)),n_retained=len(df),n_decisive=len(decisive),
                  parser_version=mistune.__version__,numpy=np.__version__,pandas=pd.__version__,scipy=scipy.__version__,
                  artifacts={p.name:digest(p) for p in OUT.iterdir() if p.suffix in ('.csv','.json') and p.name!='manifest.json'},
                  independence='prompt or model-pair clusters, sensitivity schemes fitted separately',
                  human_validation='pending; 400 responses prepared, no human annotations completed')
    dump(OUT/'manifest.json',manifest)
    print('COMPLETE',flush=True)


if __name__=='__main__': main()
