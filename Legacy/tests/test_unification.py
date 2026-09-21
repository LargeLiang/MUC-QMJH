import ast
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'Codes'))
from legacy_guard import require_legacy_opt_in
from verify_current import within


class UnificationTests(unittest.TestCase):
    def test_legacy_denied_by_default(self):
        with patch.dict(os.environ, {}, clear=True), self.assertRaises(SystemExit):
            require_legacy_opt_in('test')

    def test_explicit_legacy_warns(self):
        stream = io.StringIO()
        with patch.dict(os.environ, {'MUC_ALLOW_LEGACY': '1'}), contextlib.redirect_stderr(stream):
            require_legacy_opt_in('test')
        self.assertIn('WARNING', stream.getvalue())

    def test_all_legacy_entries_guarded_first(self):
        scripts = list((ROOT / 'Codes').glob('C[0-9][0-9]_*.py'))
        self.assertEqual(len(scripts), 23)
        for path in scripts:
            tree = ast.parse(path.read_text(encoding='utf-8-sig'))
            blocks = [n for n in tree.body if isinstance(n, ast.If) and '__main__' in ast.unparse(n.test)]
            self.assertEqual(len(blocks), 1, path.name)
            self.assertIn('require_legacy_opt_in', ast.unparse(blocks[0].body[1]), path.name)

    def test_result_pointer_complete(self):
        pointer = json.loads((ROOT / 'CURRENT_RESULTS.json').read_text())
        run = json.loads((ROOT / pointer['run'] / 'run.json').read_text())
        self.assertEqual(run['status'], 'complete')
        self.assertEqual(pointer['scope'], 'observational_associations')

    def test_path_escape_rejected(self):
        with self.assertRaises(ValueError):
            within(ROOT, '../outside')

    def test_current_notebook_no_stored_outputs(self):
        notebook = json.loads((ROOT / 'Codes/current_analysis.ipynb').read_text(encoding='utf-8'))
        for cell in notebook['cells']:
            if cell['cell_type'] == 'code':
                self.assertIsNone(cell['execution_count'])
                self.assertEqual(cell['outputs'], [])


if __name__ == '__main__':
    unittest.main()
