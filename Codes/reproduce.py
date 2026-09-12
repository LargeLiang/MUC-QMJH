"""Authoritative, fail-closed paired observational analysis. Run from any cwd."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import sys

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

ROOT = Path(__file__).resolve().parents[1]
CRITERIA = ['complexity', 'creativity', 'domain_knowledge', 'problem_solving',
            'real_world', 'specificity', 'technical_accuracy']


def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


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


def extract(row):
    if row['evaluation_order'] != 1:
        return None, 'not_first_evaluation'
    conversations = [row['conversation_a'], row['conversation_b']]
    users = []
    for conv in conversations:
        if not conv or len(conv) % 2:
            return None, 'invalid_conversation'
        texts = []
        for i, message in enumerate(conv):
            if message['role'] != ('user' if i % 2 == 0 else 'assistant'):
                return None, 'invalid_role_sequence'
            content = message['content']
            if not content or any(not isinstance(c.get('text'), str) or not c['text'].strip()
                                  for c in content):
                return None, 'empty_or_nontext_content'
            if i % 2 == 0:
                texts.append('\n'.join(c['text'] for c in content))
        users.append(texts)
    if users[0] != users[1]:
        return None, 'different_user_trajectories'
    if row['language'] in (None, '<err>'):
        return None, 'invalid_language'
    tag = row['category_tag']
    modules = [('cw', 'creative_writing_v0.1', 'creative_writing'),
               ('if', 'if_v0.1', 'if'), ('math', 'math_v0.1', 'math')]
    result = {k: row[k] for k in ['id', 'evaluation_session_id', 'evaluation_order',
                                'model_a', 'model_b', 'winner', 'language']}
    if result['winner'] not in ['model_a', 'model_b', 'tie', 'both_bad']:
        raise ValueError(f'Unknown winner label: {result["winner"]}')
    result['turns'] = len(conversations[0]) // 2
    for short, module, field in modules:
        value = (tag.get(module) or {}).get(field)
        if not isinstance(value, bool):
            return None, 'missing_task_annotation'
        result[short] = int(value)
    if not isinstance(row['is_code'], bool):
        return None, 'missing_code_annotation'
    result['code'] = int(row['is_code'])
    for field in CRITERIA:
        value = (tag.get('criteria_v0.1') or {}).get(field)
        if not isinstance(value, bool):
            return None, 'missing_criteria_annotation'
        result[field] = int(value)
    metadata = row['conv_metadata']
    for side in ['a', 'b']:
        value = metadata.get(f'sum_assistant_{side}_tokens')
        if value is None or not np.isfinite(value) or value <= 0:
            return None, 'invalid_tokens'
        result[f'tokens_{side}'] = float(value)
        for feature in ['header', 'list', 'bold']:
            counts = metadata.get(f'{feature}_count_{side}')
            if not isinstance(counts, dict) or any(v is None or v < 0 for v in counts.values()):
                return None, 'invalid_format_counts'
            result[f'{feature}_{side}'] = sum(counts.values())
    value = metadata.get('sum_user_tokens')
    if value is None or not np.isfinite(value) or value < 0:
        return None, 'invalid_user_tokens'
    result['user_tokens'] = value
    return result, 'retained'


def rebuild(out):
    folder = ROOT / 'Data/lmarena-aiarena-human-preference-140k/Data'
    paths = [folder / f'train-{i:05d}-of-00007.parquet' for i in range(7)]
    if not all(p.is_file() for p in paths):
        raise FileNotFoundError('All seven raw shards are mandatory')
    manifest, records, exclusions, ids = [], [], Counter(), set()
    columns = ['id', 'evaluation_session_id', 'evaluation_order', 'model_a', 'model_b',
               'winner', 'language', 'conversation_a', 'conversation_b', 'category_tag',
               'conv_metadata', 'is_code']
    for path in paths:
        print(f'Reading {path.name}', flush=True)
        source = pq.ParquetFile(path)
        manifest.append(dict(path=str(path.relative_to(ROOT)), sha256=digest(path),
                             rows=source.metadata.num_rows))
        for batch in source.iter_batches(batch_size=512, columns=columns):
            for row in batch.to_pylist():
                if row['id'] in ids:
                    raise ValueError(f'Duplicate raw ID: {row["id"]}')
                ids.add(row['id'])
                record, reason = extract(row)
                exclusions[reason] += 1
                if record is not None:
                    records.append(record)
    frame = pd.DataFrame(records)
    ambiguous = frame.evaluation_session_id.duplicated(keep=False)
    frame.loc[ambiguous, ['id', 'evaluation_session_id']].to_csv(out / 'ambiguous_sessions.csv', index=False)
    exclusions['ambiguous_session_records'] = int(ambiguous.sum())
    exclusions['retained'] -= int(ambiguous.sum())
    frame = frame.loc[~ambiguous].copy()
    if frame.empty or frame.evaluation_session_id.isna().any() or frame.evaluation_session_id.duplicated().any():
        raise ValueError('Expected one retained first evaluation per nonmissing session')
    frame.to_parquet(out / 'analysis_data.parquet', index=False)
    pd.DataFrame(exclusions.items(), columns=['reason_first_failure', 'n']).to_csv(out / 'attrition.csv', index=False)
    (out / 'inputs.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    return frame


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True, help='New, non-existing output directory')
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    metadata = dict(started=datetime.now(timezone.utc).isoformat(), python=sys.version,
                    platform=platform.platform(), code_sha256=digest(Path(__file__)),
                    packages={p: importlib.metadata.version(p) for p in
                              ['numpy', 'pandas', 'pyarrow', 'scipy', 'statsmodels', 'patsy',
                               'packaging', 'python-dateutil', 'pytz', 'tzdata', 'six']}, status='running')
    try:
        df = rebuild(out)
        df.groupby(['language', 'winner']).size().rename('n').to_csv(out / 'language_outcomes.csv')
        tests = descriptive(df, out)
        models = regressions(df, out)
        report = '# 重跑结果：配对观察性关联\n\n'
        report += f'严格清洗后 {len(df):,} 个独立会话首轮评价；明确胜负 {df.winner.isin(["model_a", "model_b"]).sum():,}。平局保留在数据和描述表中，不进入二元胜负分析。\n\n'
        report += '## 全量配对检验\n\n' + tests[tests.subset == 'full'].to_string(index=False) + '\n\n'
        report += '## 调整后的关联\n\n' + models.to_string(index=False) + '\n\n'
        report += ('长度采用 log(A tokens/B tokens)，格式采用每千 token 密度差，四者同时入模并标准化。控制任务标签、提示词属性、输入长度、轮数、语言和模型身份对比。OR 为每一标准差变化的条件优势比；平均导数由每行预测概率计算，不是均值处边际效应。HC0 标准误假定不同会话独立，无法消除同一匿名用户跨会话的相关性。\n\n'
                   '所有检验双侧；配对表全部 sign/McNemar 检验构成一个 Holm 家族，回归全部焦点系数组成另一个家族。Wilcoxon 为补充统计，其对称性假设未被保证。极小样本结果不宜作实质解释。\n\n'
                   '不将关联称为偏见、纯效应或因果机制：缺少独立回答质量测量，风格与内容同时产生；排除平局和严格文本配对会改变目标总体。英语、单轮为敏感性分析，不是独立复制。模型身份控制不能等同题目级质量控制。旧 IPW、匹配与 SEM 推断被撤回，不作为新结论依据；没有通过无依据的重新计算来保留旧因果叙事。\n')
        (out / 'REPORT.md').write_text(report, encoding='utf-8')
        metadata['status'] = 'complete'
        metadata['outputs'] = {p.name: digest(p) for p in out.iterdir() if p.is_file()}
    except Exception as exc:
        metadata['status'] = 'failed'
        metadata['error'] = repr(exc)
        raise
    finally:
        metadata['finished'] = datetime.now(timezone.utc).isoformat()
        (out / 'run.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
