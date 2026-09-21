"""C06: validate an optional archived baseline and compare numerical results."""
import json
import pandas as pd
from accessor import ARTIFACTS, digest, write_json


def compare(out, baseline):
    baseline = baseline.resolve()
    old = json.loads((baseline / 'run.json').read_text(encoding='utf-8'))
    if old.get('status') != 'complete':
        raise ValueError('Baseline did not complete')
    checks = []
    for key in ARTIFACTS:
        source = baseline / key
        if key in ('run.json', 'REPORT.md', 'equivalence.json') or not source.is_file():
            continue
        if old['outputs'].get(key) != digest(source):
            raise ValueError(f'Archived baseline checksum mismatch: {key}')
        target = out / key
        exact = digest(source) == digest(target)
        if key.endswith('.csv'):
            pd.testing.assert_frame_equal(pd.read_csv(source), pd.read_csv(target),
                                          check_exact=False, rtol=1e-12, atol=1e-12)
        elif key.endswith('.parquet'):
            pd.testing.assert_frame_equal(pd.read_parquet(source), pd.read_parquet(target),
                                          check_exact=True)
        elif key == 'inputs.json':
            if json.loads(source.read_text()) != json.loads(target.read_text()):
                raise ValueError('Input provenance differs from baseline')
        checks.append({'artifact': key, 'byte_identical': exact, 'numeric_match': True})
    if len(checks) != 13:
        raise ValueError(f'Expected 13 comparable artifacts, found {len(checks)}')
    report = {'baseline': str(baseline), 'status': 'passed',
              'csv_tolerance': {'rtol': 1e-12, 'atol': 1e-12},
              'checks': checks}
    write_json(out / 'equivalence.json', report)
    return report
