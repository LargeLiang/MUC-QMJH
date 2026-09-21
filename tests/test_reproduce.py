import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'Codes'))
from C02_paired_tests import paired
from C01_prepare_data import extract
from accessor import CRITERIA


class PairedTests(unittest.TestCase):
    def test_direction(self):
        self.assertEqual(paired([1, 2, 3])['rank_biserial'], 1)
        self.assertEqual(paired([-1, -2, -3])['rank_biserial'], -1)

    def test_zero(self):
        self.assertEqual(paired([0, 0])['p_sign'], 1)
        self.assertEqual(paired([0, 0])['rank_biserial'], 0)

    def test_ties_and_sign_reversal(self):
        a = paired([0, 1, 1, -2, 3])
        b = paired([0, -1, -1, 2, -3])
        self.assertAlmostEqual(a['rank_biserial'], -b['rank_biserial'])
        self.assertEqual(a['p_sign'], b['p_sign'])
        self.assertEqual(a['nonzero'], 4)

    def test_mcnemar(self):
        self.assertAlmostEqual(paired([1]*5 + [0]*10)['p_sign'], .0625)

    def test_missing_rejected(self):
        with self.assertRaises(ValueError):
            paired([np.nan])

    def test_invalid_order_rejected(self):
        self.assertEqual(extract({'evaluation_order': None})[1], 'not_first_evaluation')

    def test_clean_fixture_and_missing_tokens(self):
        conv = [{'role': r, 'content': [{'text': 'text'}]} for r in ['user', 'assistant']]
        row = dict(evaluation_order=1, id='x', evaluation_session_id='s', model_a='a',
                   model_b='b', winner='model_a', language='en', is_code=False,
                   conversation_a=conv, conversation_b=conv,
                   category_tag={'creative_writing_v0.1': {'creative_writing': False},
                                 'if_v0.1': {'if': False}, 'math_v0.1': {'math': False},
                                 'criteria_v0.1': dict.fromkeys(CRITERIA, False)},
                   conv_metadata={'sum_user_tokens': 1})
        for side in ['a', 'b']:
            row['conv_metadata'][f'sum_assistant_{side}_tokens'] = 3
            for feature in ['header', 'list', 'bold']:
                row['conv_metadata'][f'{feature}_count_{side}'] = {'x': 0}
        self.assertEqual(extract(row)[1], 'retained')
        row['conv_metadata']['sum_assistant_a_tokens'] = None
        self.assertEqual(extract(row)[1], 'invalid_tokens')


if __name__ == '__main__':
    unittest.main()
