"""只读验证当前结果指针、源代码和产物哈希；不需要科学计算依赖。"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def within(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f'Path escapes root: {relative}')
    return path


def verify(root: Path = ROOT, raw: bool = False, public_only: bool = False) -> dict:
    pointer = json.loads((root / 'CURRENT_RESULTS.json').read_text(encoding='utf-8'))
    run = within(root, pointer['run'])
    manifest = json.loads((run / 'run.json').read_text(encoding='utf-8'))
    if manifest['status'] != 'complete':
        raise ValueError('Current run is not complete')
    if sha256(within(root, pointer['analysis_entry'])) != manifest['code_sha256']:
        raise ValueError('Analysis source differs from current run')
    checked, skipped = [], []
    for name, expected in manifest['outputs'].items():
        if public_only and (name.endswith('.parquet') or name == 'ambiguous_sessions.csv'):
            skipped.append(name)
            continue
        path = within(run, name)
        if sha256(path) != expected:
            raise ValueError(f'Output checksum mismatch: {name}')
        checked.append(name)
    if raw:
        for item in json.loads((run / 'inputs.json').read_text(encoding='utf-8')):
            if sha256(within(root, item['path'])) != item['sha256']:
                raise ValueError(f'Input checksum mismatch: {item["path"]}')
    return {'run': pointer['run'], 'checked_outputs': len(checked),
            'skipped_private_outputs': skipped, 'raw_checked': raw,
            'note': 'Integrity validation only; not scientific or document acceptance.'}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', action='store_true', help='Also hash all raw shards')
    parser.add_argument('--public-only', action='store_true', help='Skip private derived records explicitly')
    args = parser.parse_args()
    print(json.dumps(verify(raw=args.raw, public_only=args.public_only), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
