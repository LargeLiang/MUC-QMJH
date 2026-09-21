"""Shared paths and hashes; analytical stages have no implicit working-directory dependency."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
CRITERIA = ['complexity', 'creativity', 'domain_knowledge', 'problem_solving',
            'real_world', 'specificity', 'technical_accuracy']
ARTIFACTS = {
    'analysis_data.parquet': ('Data/analysis_data', 'analysis_data.parquet'),
    'ambiguous_sessions.csv': ('Data/analysis_data', 'ambiguous_sessions.csv'),
    'inputs.json': ('Reports', 'R01_inputs.json'),
    'run.json': ('Reports', 'R00_run_manifest.json'),
    'REPORT.md': ('Reports', 'R04_analysis_report.md'),
    'equivalence.json': ('Reports', 'R05_legacy_equivalence.json'),
    'attrition.csv': ('Tables', 'T01_01_attrition.csv'),
    'language_outcomes.csv': ('Tables', 'T01_02_language_outcomes.csv'),
    'paired_tests.csv': ('Tables', 'T02_paired_tests.csv'),
    'adjusted_associations.csv': ('Tables', 'T03_adjusted_associations.csv'),
    'sample_flow.png': ('Pictures', 'P01_sample_flow.png'),
    'associations.png': ('Pictures', 'P02_adjusted_associations.png'),
}
for i, label in enumerate(['full', 'english', 'single_turn'], 1):
    ARTIFACTS[f'scaling_{label}.csv'] = ('Tables', f'T03_{i:02d}_scaling_{label}.csv')
    ARTIFACTS[f'model_{label}_all_terms.csv'] = ('Tables', f'T03_{i:02d}_model_{label}_all_terms.csv')


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n',
                          encoding='utf-8')


class RunPaths:
    """Route logical artifact names to traditional numbered output directories."""
    def __init__(self, run_id, root=ROOT):
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}', run_id):
            raise ValueError('run-id must be 1-80 ASCII letters, digits, underscores or hyphens')
        self.run_id = run_id
        self.root = Path(root).resolve()

    def __truediv__(self, key):
        folder, name = ARTIFACTS[key]
        return self.root / folder / self.run_id / name

    def relative(self, path):
        return Path(path).relative_to(self.root).as_posix()

    def create(self):
        directories = sorted({self.root / folder / self.run_id for folder, _ in ARTIFACTS.values()})
        existing = [str(p) for p in directories if p.exists()]
        if existing:
            raise FileExistsError('Refusing to overwrite a run: ' + ', '.join(existing))
        for folder in directories:
            folder.mkdir(parents=True, exist_ok=False)
