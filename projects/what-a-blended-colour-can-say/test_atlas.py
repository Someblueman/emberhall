"""The public renderer and actual regenerated artifact bundle."""
from copy import deepcopy
from fractions import Fraction as F
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import blended_colour as bc
import display_colour as dc
import quantized_bounds as qb
import render_legend as rl
from verify_atlas import verify_atlas

ROOT = Path(__file__).resolve().parent


class AtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rendered = rl.render_atlas(bc.builtin_palettes(), rl.default_cases())
        cls.data = json.loads(cls.rendered['witnesses'])

    def test_six_accepted_cases_and_new_held_out_endpoints(self):
        expected = [('3/4','3/4'), ('3/5','3/5'), ('1/2','3/5'),
                    ('0','2/5'), ('0','2/3'), ('0','1'), ('2/7','4/7')]
        for s, pair in zip(self.data['swatches'], expected):
            self.assertEqual((s['certificate']['p_min'], s['certificate']['p_max']), pair)
        s7 = self.data['swatches'][6]
        self.assertEqual(s7['certificate']['witness_min'], ['0','0','5/7','3/14','1/14'])
        self.assertEqual(s7['certificate']['witness_max'], ['1/7','2/7','0','3/7','1/7'])
        self.assertTrue(s7['held_out'])

    def test_verifier_uses_no_optimizer_and_rejects_corrupted_envelopes(self):
        mutations = [lambda d: d.update(rounding='ties-even'),
                     lambda d: d['swatches'][0].update(hex='#ffffff'),
                     lambda d: d['swatches'][0]['weights'].__setitem__(0, '0'),
                     lambda d: d['swatches'][0]['observations'][0].update(mode='gamma22'),
                     lambda d: d['swatches'][0]['observations'][0]['rgb8'].__setitem__(0, 0),
                     lambda d: d['swatches'][0]['observations'][0]['lower'].__setitem__(0, '0'),
                     lambda d: d['swatches'][0]['observations'][0]['certificate'].update(p_max='0')]
        with patch.object(bc, '_simplex_minimize', side_effect=AssertionError('called optimizer')):
            self.assertEqual(verify_atlas(self.data), (10, 20))
            for mutation in mutations:
                bad = deepcopy(self.data)
                mutation(bad)
                with self.assertRaises(ValueError):
                    verify_atlas(bad)

    def test_arbitrary_palette_and_case_are_imported_into_svg(self):
        palette = bc.Palette('caller<&', ('B', 'W'), (F(0), F(1)), ((F(0),)*3, (F(1),)*3))
        case = rl.Case('mine', 'Caller <& title', palette.name, (F(1,2),)*2, (1,), 'P(W)')
        rendered = rl.render_atlas({palette.name: palette}, (case,), modes=('linear8',), title='Custom & title')
        svg = ET.fromstring(rendered['svg'])
        self.assertIn('Caller <& title', ''.join(svg.itertext()))
        data = json.loads(rendered['witnesses'])
        self.assertEqual(verify_atlas(data), (1, 1))
        s = data['swatches'][0]
        self.assertEqual(s['hex'], '#bcbcbc')
        self.assertEqual(s['observations'][0]['hex'], '#808080')
        self.assertEqual(s['observations'][0]['certificate']['p_max'], '257/510')
        self.assertEqual(set(data['palettes']), {palette.name})

    def test_html_embeds_the_real_vector_at_native_width_with_case_controls(self):
        html = self.rendered['html']
        self.assertIn(self.rendered['svg'], html)
        self.assertIn('width:1040px;max-width:none', html)
        self.assertIn('tabindex="0" role="region"', html)
        self.assertIn('id="vector-left"', html)
        self.assertIn('id="vector-right"', html)
        for i, case in enumerate(rl.default_cases()):
            self.assertIn(f'<option value="{i}">{case.id} / ', html)
            self.assertIn(f'<article data-case="{i}">', html)

    def test_supported_observation_bounds_include_exact_intervals(self):
        for s in self.data['swatches']:
            exact = s['certificate']
            for observation in s['observations']:
                bound = observation['certificate']
                self.assertLessEqual(F(bound['p_min']), F(exact['p_min']))
                self.assertGreaterEqual(F(bound['p_max']), F(exact['p_max']))

    def test_all_artifacts_are_deterministic_and_committed_generation_matches(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            rl.generate_all(target)
            first = {p.name:p.read_bytes() for p in target.iterdir()}
            self.assertEqual(len(first), 6)
            rl.generate_all(target)
            self.assertEqual(first, {p.name:p.read_bytes() for p in target.iterdir()})
            for name, content in first.items():
                self.assertEqual(content, (ROOT / 'legends' / name).read_bytes(), name)
            for name in ('first_legend.svg', 'example.svg'):
                ET.fromstring(first[name])
            self.assertEqual(verify_atlas(json.loads(first['example-certificates.json'])), (1, 2))
            output = json.loads(first['example-output.txt'])
            self.assertEqual((output['p_min'], output['p_max']), ('1/2','3/5'))
            self.assertEqual(output['hex'], '#59c82c')

    def test_actual_verify_cli_success_and_failure(self):
        command = [sys.executable, str(ROOT/'verify_atlas.py')]
        result = subprocess.run(command + [str(ROOT/'legends/witnesses.json')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('10 exact cases', result.stdout)
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp)/'bad.json'
            bad.write_text('{"schema":"wrong"}')
            result = subprocess.run(command + [str(bad)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn('INVALID', result.stderr)

    def test_real_importing_program_reproduces_recorded_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run([sys.executable, str(ROOT/'example_import.py'), '--out', tmp],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, (ROOT/'legends/example-output.txt').read_text())
            self.assertEqual((Path(tmp)/'example.svg').read_bytes(), (ROOT/'legends/example.svg').read_bytes())

    def test_empty_duplicate_and_unsupported_renderer_inputs(self):
        palettes = bc.builtin_palettes()
        case = rl.default_cases()[0]
        for cases, modes in (((), dc.MODES), ((case,case), dc.MODES), ((case,), ()),
                             ((case,), ('srgb8','srgb8')), ((case,), ('display-p3',))):
            with self.assertRaises(ValueError):
                rl.render_atlas(palettes, cases, modes=modes)

    def test_mode_led_cards_and_vector_use_matching_scope_certificates(self):
        rendered = rl.render_atlas(bc.builtin_palettes(), rl.default_cases(), mode_led=True)
        for swatch in self.data['swatches']:
            for mode in ('exact', *dc.MODES):
                cert, scope, status = rl._mode_result(swatch, mode)
                self.assertIn(scope, rendered['html'])
                self.assertIn(rl._range(cert, mode == 'exact'), rendered['html'])
                self.assertIn(status, rendered['svg'])
        self.assertIn('id="mode-choice"', rendered['html'])
        self.assertIn('aria-live="polite"', rendered['html'])
        self.assertNotIn('data-mode="linear8"', rendered['svg'])
        self.assertIn('id="vector-models"', rendered['html'])
        self.assertIn('data-mode="srgb8"', rendered['svg'])
        self.assertEqual(rendered['witnesses'], self.rendered['witnesses'])

    def test_query_defaults_and_missing_observation_mode(self):
        case = rl.default_cases()[0]
        rendered = rl.render_atlas(bc.builtin_palettes(), (case,), mode_led=True,
                                  modes=('linear8',), query_modes={case.id:'exact'})
        self.assertIn('data-mode="exact" data-query="exact">', rendered['html'])
        self.assertIn('data-mode="linear8" data-query="exact" hidden', rendered['html'])
        with self.assertRaises(ValueError):
            rl.render_atlas(bc.builtin_palettes(), (case,), mode_led=True,
                            modes=('linear8',), query_modes={case.id:'srgb8'})


if __name__ == '__main__':
    unittest.main()
