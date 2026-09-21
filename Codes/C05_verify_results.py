"""C05: fail-closed verification of code, public outputs and optional local data."""
import argparse
import json
from pathlib import Path
from accessor import ROOT, ARTIFACTS, RunPaths, digest


def safe_path(relative, root=ROOT):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f'Path escapes project: {relative}')
    return path


def verify(manifest_path, public_only=False, verify_raw=False, root=ROOT):
    root = Path(root).resolve()
    meta = json.loads(Path(manifest_path).read_text(encoding='utf-8'))
    if meta.get('schema_version') != 2 or meta.get('status') != 'complete':
        raise ValueError('Manifest is not a completed schema-v2 run')
    paths = RunPaths(meta['run_id'], root)
    required = {paths.relative(paths / key) for key in ARTIFACTS
                if key not in ('run.json', 'equivalence.json')}
    if not required.issubset(meta.get('outputs', {})):
        raise ValueError('Manifest omits required outputs')
    if set(meta.get('source_sha256', {})) != {
            p.relative_to(root).as_posix() for p in (root / 'Codes').glob('*')
            if p.suffix in ('.py', '.ipynb')} | {'requirements-analysis.lock.txt'}:
        raise ValueError('Source inventory differs from manifest')
    checked = skipped = 0
    for section in ('source_sha256', 'outputs'):
        for relative, expected in meta[section].items():
            if section == 'outputs' and public_only and relative.startswith('Data/'):
                skipped += 1
                continue
            path = safe_path(relative, root)
            if not path.is_file() or digest(path) != expected:
                raise ValueError(f'Checksum mismatch or missing: {relative}')
            checked += 1
    if verify_raw:
        inputs = json.loads((paths / 'inputs.json').read_text(encoding='utf-8'))
        for item in inputs:
            path = safe_path(item['path'], root)
            if not path.is_file() or digest(path) != item['sha256']:
                raise ValueError(f'Raw input mismatch: {item["path"]}')
            checked += 1
    return {'verified_files': checked, 'skipped_private_outputs': skipped,
            'raw_inputs_checked': verify_raw}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path)
    parser.add_argument('--public-only', action='store_true',
                        help='Skip private derived files; not a full reproduction check')
    parser.add_argument('--verify-raw', action='store_true')
    args = parser.parse_args()
    if args.public_only and args.verify_raw:
        parser.error('--public-only and --verify-raw are mutually exclusive')
    if args.manifest:
        manifest = args.manifest.resolve()
    else:
        pointer = json.loads((ROOT / 'CURRENT_RESULTS.json').read_text(encoding='utf-8'))
        manifest = safe_path(pointer['manifest'])
        if digest(manifest) != pointer['manifest_sha256']:
            raise ValueError('Current manifest differs from approved pointer')
    print(json.dumps(verify(manifest, args.public_only, args.verify_raw), indent=2))


if __name__ == '__main__':
    main()
