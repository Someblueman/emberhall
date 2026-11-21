"""Independent instrument boundaries: freeze, distinct cases, scope and stop rules."""
import json
import re
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import blended_colour as bc
import comparison as first
import comparison_v2 as second


class SecondInstrumentTests(unittest.TestCase):
    def test_new_cases_and_palettes_are_held_out_and_cover_regimes(self):
        old = first.heldout_specs()
        specs = second.specs()
        self.assertEqual(len(specs), 10)
        self.assertFalse({s.case.id for s in specs} & {s.case.id for s in old})
        old_colours = {p.colours for p in first.heldout_palettes().values()}
        self.assertFalse(old_colours & {p.colours for p in second.palettes().values()})
        for group in ('A','B'):
            cases = [s for s in specs if s.set_name == group]
            data = [first._evaluate_spec(s, second.palettes()) for s in cases]
            self.assertEqual([x['queried_status'] for x in data],
                             ['EXACT','BOUNDED','UNIDENTIFIABLE','BOUNDED','BOUNDED'])
            self.assertEqual([s.query_mode for s in cases], ['exact']*3+['srgb8','linear8'])

    def test_second_pack_regenerates_and_frozen_keys_verify_without_solver(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            second.generate(target)
            committed = {str(p.relative_to(second.OUT)):p.read_bytes()
                         for p in second.OUT.rglob('*') if p.is_file()}
            generated = {str(p.relative_to(target)):p.read_bytes() for p in target.rglob('*') if p.is_file()}
            self.assertEqual(generated, committed)
            with patch.object(bc, '_simplex_minimize', side_effect=AssertionError('optimizer called')):
                self.assertEqual(second.verify(target), (10,20))
            key = target/'keys/answers.json'
            key.write_text(key.read_text()+' ')
            with self.assertRaisesRegex(ValueError, 'Frozen instrument differs'):
                second.verify(target)

    def test_baseline_has_same_scope_endpoints_but_no_answer_summaries(self):
        palette_map = second.palettes()
        specs = [s for s in second.specs() if s.set_name == 'A']
        items = [first._evaluate_spec(s, palette_map) for s in specs]
        html = second.baseline(items, palette_map, 'Test')
        self.assertEqual(html.count('<article '), 15)
        self.assertEqual(len(re.findall(r'<article [^>]* hidden>', html)), 10)
        for mode in ('exact','srgb8','linear8'):
            self.assertEqual(html.count(f'data-mode="{mode}"'), 5)
        self.assertNotIn('class="result"', html)
        self.assertNotIn('witnesses.json', html)
        self.assertIn('id="mode-choice"', html)
        self.assertIn("card.dataset.mode !== wanted", html)
        for item in items:
            for weight in item['queried_witness_min']:
                if weight and item['spec'].query_mode != 'exact':
                    self.assertIn(first._round_pct_2(weight), html)

    def responses(self):
        keys = json.loads((second.OUT/'keys/answers.json').read_text())['cases']
        response = dict(order=second.ORDER, phone_desktop_ok=True, dist_view={}, atlas_view={})
        for cid, key in keys.items():
            response['dist_view' if key['set']=='A' else 'atlas_view'][cid] = dict(
                q1_p_min=key['p_min'], q2_p_max=key['p_max'], q3_status=key['status'],
                q4_probe=key['q4_answer'], q5_clarity=4)
        return response

    def test_no_lowered_threshold_and_fail_inconclusive_stop_outcomes(self):
        response = self.responses()
        self.assertEqual(second.score(response)['outcome'], 'INCONCLUSIVE')
        for answer in response['dist_view'].values():
            answer['q5_clarity'] = 3
        self.assertEqual(second.score(response)['outcome'], 'PASS')
        response['phone_desktop_ok'] = False
        self.assertEqual(second.score(response)['outcome'], 'FAIL')
        response['phone_desktop_ok'] = True
        response['atlas_view']['V2-3B']['q3_status'] = 'BOUNDED'
        self.assertEqual(second.score(response)['outcome'], 'FAIL')
        response['order'] = 'atlas_a_then_dist_b'
        with self.assertRaises(ValueError):
            second.score(response)

    def test_cli_refuses_overwriting_the_frozen_pack(self):
        before = (second.OUT/'freeze.json').read_bytes()
        result = subprocess.run([sys.executable, str(second.ROOT/'comparison_v2.py'),
                                 'generate', '--out', str(second.OUT)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('Frozen pack already exists', result.stderr)
        self.assertEqual(before, (second.OUT/'freeze.json').read_bytes())

    def test_scores_reject_truthy_strings_and_coerced_clarity(self):
        for field, value in (('phone_desktop_ok','true'), ('clarity',4.8), ('clarity',True)):
            response = self.responses()
            if field == 'clarity':
                response['atlas_view']['V2-1B']['q5_clarity'] = value
            else:
                response[field] = value
            with self.assertRaises(ValueError):
                second.score(response)


if __name__ == '__main__':
    unittest.main()
