import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'Codes'))
from accessor import ROOT, ARTIFACTS, RunPaths, digest, write_json
from C05_verify_results import safe_path, verify


class IntegrationTests(unittest.TestCase):
    def test_numbered_unique_paths(self):
        out = RunPaths('test-run')
        self.assertEqual((out / 'REPORT.md').name, 'R04_analysis_report.md')
        self.assertEqual((out / 'paired_tests.csv').parent, ROOT / 'Tables/test-run')
        self.assertEqual(len({out / k for k in ARTIFACTS}), len(ARTIFACTS))

    def test_invalid_identifiers(self):
        for name in ('../escape', '', 'a/b', 'a\\b', 'a.b', 'a'*81):
            with self.subTest(name=name), self.assertRaises(ValueError):
                RunPaths(name)

    def test_refuse_existing_run(self):
        with tempfile.TemporaryDirectory() as folder:
            out = RunPaths('run', Path(folder))
            out.create()
            (out / 'REPORT.md').write_text('untouched')
            with self.assertRaises(FileExistsError):
                out.create()
            self.assertEqual((out / 'REPORT.md').read_text(), 'untouched')

    def test_fail_before_creating_other_directories(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'Tables/run').mkdir(parents=True)
            with self.assertRaises(FileExistsError):
                RunPaths('run', root).create()
            self.assertFalse((root / 'Reports/run').exists())

    def test_path_escape_rejected(self):
        with self.assertRaises(ValueError):
            safe_path('../outside')

    def test_current_public_outputs(self):
        pointer = json.loads((ROOT / 'CURRENT_RESULTS.json').read_text())
        manifest = ROOT / pointer['manifest']
        self.assertEqual(digest(manifest), pointer['manifest_sha256'])
        self.assertGreater(verify(manifest, public_only=True)['verified_files'], 0)

    def test_notebook_is_current_and_clear(self):
        nb = json.loads((ROOT / 'Codes/C00_all_collection.ipynb').read_text(encoding='utf-8'))
        for cell in nb['cells']:
            if cell['cell_type'] == 'code':
                self.assertEqual(cell['outputs'], [])
                self.assertIsNone(cell['execution_count'])
                self.assertNotIn('MUC_ALLOW_LEGACY', ''.join(cell['source']))

    def test_entry_from_other_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            result = subprocess.run([sys.executable, str(ROOT / 'Codes/C00_run_all.py'), '--help'],
                                    cwd=folder, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('--run-id', result.stdout)

    def test_tampered_and_incomplete_outputs_fail(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            out = RunPaths('test', root)
            out.create()
            (root / 'Codes').mkdir()
            (root / 'Codes/example.py').write_text('# fixture')
            (root / 'requirements-analysis.lock.txt').write_text('# fixture')
            for key in ARTIFACTS:
                if key != 'run.json':
                    (out / key).write_text('{}')
            meta = {'schema_version': 2, 'run_id': 'test', 'status': 'complete',
                    'source_sha256': {name: digest(root / name) for name in
                                      ['Codes/example.py', 'requirements-analysis.lock.txt']},
                    'outputs': {out.relative(out / k): digest(out / k) for k in ARTIFACTS if k != 'run.json'}}
            write_json(out / 'run.json', meta)
            verify(out / 'run.json', root=root)
            (out / 'paired_tests.csv').write_text('tampered')
            with self.assertRaisesRegex(ValueError, 'Checksum'):
                verify(out / 'run.json', root=root)
            meta['outputs'].pop(out.relative(out / 'paired_tests.csv'))
            write_json(out / 'run.json', meta)
            with self.assertRaisesRegex(ValueError, 'omits'):
                verify(out / 'run.json', root=root)
            meta['status'] = 'failed'
            write_json(out / 'run.json', meta)
            with self.assertRaisesRegex(ValueError, 'completed'):
                verify(out / 'run.json', root=root)


if __name__ == '__main__':
    unittest.main()
