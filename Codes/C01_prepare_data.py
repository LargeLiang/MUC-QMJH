"""C01: rebuild the analysis sample from all seven original shards."""
from collections import Counter
import json
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from accessor import ROOT, CRITERIA, digest

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
