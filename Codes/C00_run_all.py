"""C00: run the complete chain from raw shards; never overwrite a prior run."""
import os
# Set before importing numerical libraries for reproducible resource use.
for key in ('OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'OMP_NUM_THREADS'):
    os.environ[key] = '2'
import argparse
from datetime import datetime, timezone
import importlib.metadata
import platform
from pathlib import Path
import sys
from accessor import ROOT, ARTIFACTS, RunPaths, digest, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id', default=datetime.now(timezone.utc).strftime('run-%Y%m%dT%H%M%S%fZ'))
    parser.add_argument('--compare-legacy', type=Path,
                        help='Optional completed old flat-output run directory')
    parser.add_argument('--promote', action='store_true',
                        help='Update CURRENT_RESULTS.json only after successful verification')
    args = parser.parse_args()
    paths = RunPaths(args.run_id)
    paths.create()
    sources = sorted(p for p in (ROOT / 'Codes').glob('*') if p.suffix in ('.py', '.ipynb'))
    sources.append(ROOT / 'requirements-analysis.lock.txt')
    packages = {}
    for line in (ROOT / 'requirements-analysis.lock.txt').read_text().splitlines():
        if '==' in line and not line.lstrip().startswith('#'):
            package, version = line.strip().split('==')
            packages[package] = {'expected': version, 'installed': importlib.metadata.version(package)}
    meta = {'schema_version': 2, 'run_id': args.run_id, 'status': 'running',
            'started': datetime.now(timezone.utc).isoformat(), 'python': sys.version,
            'platform': platform.platform(), 'packages': packages,
            'threads': {key: os.environ[key] for key in ('OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'OMP_NUM_THREADS')},
            'source_sha256': {paths.relative(p): digest(p) for p in sources}}
    write_json(paths / 'run.json', meta)
    try:
        mismatch = [p for p, values in packages.items() if values['expected'] != values['installed']]
        if mismatch:
            raise RuntimeError('Locked package version mismatch: ' + ', '.join(mismatch))
        from C01_prepare_data import rebuild
        from C02_paired_tests import descriptive
        from C03_adjusted_associations import regressions
        from C04_export_results import export
        from C05_verify_results import verify
        from C06_compare_legacy import compare
        df = rebuild(paths)
        df.groupby(['language', 'winner']).size().rename('n').to_csv(paths / 'language_outcomes.csv')
        tests = descriptive(df, paths)
        models = regressions(df, paths)
        export(df, tests, models, paths)
        if args.compare_legacy:
            compare(paths, args.compare_legacy)
        meta['counts'] = {'retained': len(df),
                          'decisive': int(df.winner.isin(['model_a', 'model_b']).sum()),
                          'winners': {str(k): int(v) for k, v in df.winner.value_counts().items()}}
        meta['outputs'] = {paths.relative(paths / key): digest(paths / key)
                           for key in ARTIFACTS if key != 'run.json' and (paths / key).is_file()}
        meta['status'] = 'complete'
        meta['finished'] = datetime.now(timezone.utc).isoformat()
        write_json(paths / 'run.json', meta)
        check = verify(paths / 'run.json', verify_raw=True)
        if args.promote:
            pointer = {'schema_version': 2, 'run_id': args.run_id,
                       'manifest': paths.relative(paths / 'run.json'),
                       'manifest_sha256': digest(paths / 'run.json'),
                       'report': paths.relative(paths / 'REPORT.md'),
                       'scope': 'observational associations; archival comparisons are not causal validation'}
            temporary = ROOT / ('CURRENT_RESULTS.' + args.run_id + '.tmp')
            write_json(temporary, pointer)
            temporary.replace(ROOT / 'CURRENT_RESULTS.json')
        print(f'COMPLETE: {paths / "run.json"}', flush=True)
        print(check, flush=True)
    except BaseException as exc:
        meta['status'] = 'failed'
        meta['error'] = repr(exc)
        meta['finished'] = datetime.now(timezone.utc).isoformat()
        write_json(paths / 'run.json', meta)
        raise


if __name__ == '__main__':
    main()
