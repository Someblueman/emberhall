#!/usr/bin/env python3
"""Public-contract regressions for population and finite-track searches."""
from contextlib import redirect_stdout, redirect_stderr
from fractions import Fraction
import io
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import dissipation_bounds as db
from general_finite_record import empirical_Gamma, simulate_general_frames
from general_tracks import FROZEN_GENERAL, GeneralVortex
from real_logs import family_drift

TRACK = str(Path(__file__).with_name('synthetic_track.csv'))


def moments(g, D, e, ell=0.03):
    return [g.observed_cov_matrix(D, e, ell, k) for k in range(3)]


class TestDissipationBounds(unittest.TestCase):
    def setUp(self):
        self.f = FROZEN_GENERAL
        self.g = GeneralVortex(self.f['A'], self.f['Dm'])
        self.iso = GeneralVortex([[-1., -3.9], [3.9, -1.]], [[1., 0.], [0., 1.]])

    def test_exact_population_examples_preserved(self):
        for g, D, e, ell, ratio in [(self.iso, 1., .5, .04, Fraction(1, 2)),
                                     (self.g, .9, .3, .03, Fraction(1, 3))]:
            with self.subTest(ratio=ratio):
                r = db.certify_covariances(*moments(g, D, e, ell), D, e,
                                           exposure_ratio=ratio)
                self.assertEqual(r['status'], 'unique')
                self.assertTrue(r['search_complete'])
                self.assertIn('all-m rational completeness', r['completeness'])
                self.assertAlmostEqual(r['sigma_bounds'][0], g.dissipation(), places=6)

    def test_float_and_near_rational_timing_cannot_certify_all_m(self):
        for e in (.3, .3 + 1e-12, .9*(math.sqrt(5)-1)/2):
            with self.subTest(e=e):
                r = db.certify_covariances(*moments(self.g, .9, e), .9, e)
                self.assertEqual(r['status'], 'incomplete')
                self.assertFalse(r['search_complete'])
                self.assertIsNone(r['sigma_bounds'])
        with self.assertRaisesRegex(ValueError, 'disagrees'):
            db.certify_covariances(*moments(self.g, .9, .3+1e-12), .9, .3+1e-12,
                                   exposure_ratio=Fraction(1, 3))
        with self.assertRaisesRegex(ValueError, 'Fraction'):
            db.certify_covariances(*moments(self.g, .9, .3), .9, .3, exposure_ratio=1/3)

    def test_empty_truncated_window_is_not_global_refusal(self):
        r = db.certify_covariances(*moments(self.iso, 1., .5), 1., .5, m_window=0)
        self.assertEqual(r['status'], 'incomplete')
        self.assertEqual(r['candidate_status'], 'none')
        self.assertIsNone(r['sigma_bounds'])

    def test_residue_search_finds_branch_outside_window(self):
        g = GeneralVortex([[-1., -18.], [18., -1.]], [[1., 0.], [0., 1.]])
        r = db.certify_covariances(*moments(g, 1., 1/7), 1., 1/7, m_window=0,
                                   exposure_ratio=Fraction(1, 7))
        self.assertEqual(r['status'], 'unique')
        self.assertNotEqual(r['compatible'][0]['m'], 0)
        self.assertAlmostEqual(r['sigma_bounds'][0], g.dissipation(), places=5)

    def test_rational_elimination_agrees_with_independent_wide_windows(self):
        clockwise = GeneralVortex([[-1., 18.], [-18., -1.]], [[1., 0.], [0., 1.]])
        for g in (self.g, self.iso, clockwise):
            for denominator in (2, 3, 5, 7):
                with self.subTest(A=g.A, denominator=denominator):
                    ratio = Fraction(1, denominator)
                    Gs = moments(g, 1., float(ratio))
                    exact = db.certify_covariances(*Gs, 1., float(ratio),
                                                   exposure_ratio=ratio, m_window=0)
                    scan = db.certify_covariances(*Gs, 1., float(ratio), m_window=12)
                    self.assertTrue(exact['search_complete'])
                    self.assertTrue({c['m'] for c in scan['compatible']} <=
                                    {c['m'] for c in exact['compatible']})
                    self.assertAlmostEqual(exact['sigma_bounds'][0], g.dissipation(), places=5)

    def test_excessive_exact_denominator_is_incomplete(self):
        ratio = Fraction(1, 2001)
        r = db.certify_covariances(*moments(self.g, 1., float(ratio)), 1., float(ratio),
                                   exposure_ratio=ratio, m_window=0)
        self.assertFalse(r['search_complete'])
        self.assertEqual(r['status'], 'incomplete')
        self.assertIsNone(r['sigma_bounds'])

    def test_degenerate_residue_search_fails_closed(self):
        with patch('general_finite_record.symmetry_residual', return_value=0.):
            roots, complete = db._rational_complex_roots(None, None, None, 1., .5, 2, 1e-7, 0)
        self.assertFalse(complete)
        self.assertEqual(roots, {0})

    def test_finite_singleton_has_no_certified_bound(self):
        f = self.f
        frames = simulate_general_frames(self.g, f['Delta'], f['eps'], f['ell2'],
                                         1000, seed=12345, sub=20)
        Gs = [empirical_Gamma(frames, k) for k in range(3)]
        for mode in ('finite', 'bootstrap'):
            with self.subTest(mode=mode):
                r = db.certify_covariances(*Gs, f['Delta'], f['eps'], mode=mode,
                                           n_frames=1000, bootstrap_reps=4,
                                           exposure_ratio=Fraction(1, 2))
                self.assertEqual(r['status'], 'uncertainty_unavailable')
                self.assertEqual(r['uncertainty'], 'unavailable')
                self.assertFalse(r['search_complete'])
                self.assertIsNone(r['sigma_bounds'])
                self.assertEqual(r['candidate_status'], 'single')
                self.assertAlmostEqual(r['plugin_span'][0], 11.4818297137227)
                self.assertGreater(r['plugin_span'][0], self.g.dissipation()+6)
                self.assertTrue(any('not a confidence interval' in c for c in r['caveats']))

    def test_finite_missing_sample_size_and_unknown_mode_rejected(self):
        Gs = moments(self.g, .9, .45)
        for kw in ({'mode': 'finite'}, {'mode': 'bootstrap', 'n_frames': 1},
                   {'mode': 'bootstrap', 'n_frames': 1000, 'bootstrap_reps': 1},
                   {'mode': 'typo'}, {'tol': -1}, {'slack': float('nan')}):
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                db.certify_covariances(*Gs, .9, .45, **kw)

    def test_scalar_counterexample_and_truncated_sheets_are_incomplete(self):
        A = family_drift(-1.051604554356144, 2*math.pi, .916683, 3.077661, 1.)
        g = GeneralVortex(A, [[.195454, .216758], [.216758, .780373]])
        a = (*moments(g, 1., .691196, .2), 1., .691196)
        b = (*moments(g, 1., .5, .2), 1., .5)
        r = db.certify_covariances(*a, tol=1e-6)
        self.assertEqual(r['status'], 'incomplete')
        self.assertEqual(len(r['compatible']), 2)
        self.assertGreater(r['plugin_span'][1]-r['plugin_span'][0], 1500)
        joint = db.certify_two_exposures(a, b, tol=1e-6)
        self.assertEqual(len(joint['compatible']), 1)
        self.assertEqual(joint['status'], 'incomplete')
        self.assertFalse(joint['resolved_by_two_exposures'])
        self.assertIsNone(joint['sigma_bounds'])
        empty = db.certify_covariances(*a, max_scalar_sheets=0)
        self.assertEqual(empty['candidate_status'], 'none')
        self.assertEqual(empty['status'], 'incomplete')
        self.assertIsNone(empty['sigma_bounds'])

    def test_two_exposures_can_use_complete_second_source(self):
        a = (*moments(self.iso, 1., 1e-4, .04), 1., 1e-4)
        b = (*moments(self.iso, 1., .5, .04), 1., .5)
        r = db.certify_two_exposures(a, b, exposure_ratios=(None, Fraction(1, 2)), tol=1e-5)
        self.assertEqual(r['status'], 'unique')
        self.assertTrue(r['search_complete'])
        self.assertTrue(r['resolved_by_two_exposures'])
        self.assertAlmostEqual(r['sigma_bounds'][0], 30.42, places=6)
        rev = db.certify_two_exposures(b, a, exposure_ratios=(Fraction(1, 2), None), tol=1e-5)
        self.assertEqual(rev['sigma_bounds'], r['sigma_bounds'])

    def test_two_exposures_cannot_upgrade_incomplete_or_finite_results(self):
        a = (*moments(self.iso, 1., .5), 1., .5)
        r = db.certify_two_exposures(a, a)
        self.assertEqual(r['status'], 'incomplete')
        self.assertIsNone(r['sigma_bounds'])
        for mode in ('finite', 'bootstrap'):
            r = db.certify_two_exposures(a, a, mode=mode, n_frames=1000)
            self.assertEqual(r['status'], 'refused')
            self.assertIn('unsupported', r['reason'])
            self.assertIsNone(r['sigma_bounds'])

    def test_real_population_and_unsupported_finite_class(self):
        g = GeneralVortex([[-1., 1.], [0., -1.]], [[1., .3], [.3, .6]])
        Gs = moments(g, .9, .45)
        r = db.certify_covariances(*Gs, .9, .45)
        self.assertEqual(r['status'], 'unique')
        self.assertEqual(r['kind'], 'defective')
        r = db.certify_covariances(*Gs, .9, .45, mode='finite', n_frames=1000)
        self.assertEqual(r['status'], 'refused')
        self.assertIsNone(r['sigma_bounds'])
        r = db.certify_covariances(Gs[0], [[0., 0.], [0., 0.]], Gs[2], .9, .45)
        self.assertEqual(r['status'], 'refused')
        self.assertIsNone(r['sigma_bounds'])

    def test_detrending_and_csv_diagnostics(self):
        poly = [[1.+.02*t+.001*t*t-1e-4*t**3, -.5+.01*t*t] for t in range(50)]
        clean = db.detrend_frames(poly, 3)
        self.assertLess(max(abs(v) for row in clean for v in row), 1e-10)
        r = db.certify_track_csv(TRACK, 1., .5)
        self.assertEqual(r['status'], 'uncertainty_unavailable')
        self.assertIsNone(r['sigma_bounds'])
        self.assertTrue(any(c['m'] == -1 for c in r['compatible']))

    def test_csv_and_cli_cannot_claim_population_uncertainty(self):
        with self.assertRaisesRegex(ValueError, 'sampled CSV'):
            db.certify_track_csv(TRACK, 1., .5, mode='population')
        out = io.StringIO()
        with redirect_stdout(out):
            code = db.main(['--csv', TRACK, '--json'])
        r = json.loads(out.getvalue())
        self.assertEqual(code, 1)
        self.assertEqual(r['uncertainty'], 'unavailable')
        self.assertEqual(r['status'], 'uncertainty_unavailable')
        self.assertIsNone(r['sigma_bounds'])
        self.assertIsNotNone(r['plugin_span'])
        out = io.StringIO()
        with redirect_stdout(out):
            db.main(['--csv', TRACK])
        self.assertNotIn('Certified dissipation bounds', out.getvalue())
        self.assertIn('not a confidence interval', out.getvalue())

    def test_bootstrap_cannot_use_failed_replicates_as_zero_error(self):
        Gs = moments(self.g, .9, .45)
        with patch.object(db, 'branch_quantities_general', return_value=None):
            r = db.certify_covariances(*Gs, .9, .45, mode='bootstrap', n_frames=1000,
                                       bootstrap_reps=2)
        self.assertEqual(r['status'], 'uncertainty_unavailable')
        self.assertIsNone(r['sigma_bounds'])
        self.assertTrue(any('bootstrap' in c for c in r['caveats']))


class TestTrackCadence(unittest.TestCase):
    def read_text(self, text):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'track.csv'
            path.write_text(text, encoding='utf-8')
            return db.load_csv_track(str(path))

    def test_regular_frames_preserve_coordinates_and_allow_arbitrary_origin(self):
        for start in (0, 17, 2**60):
            with self.subTest(start=start):
                text = 'frame,y1,y2,quality\n' + ''.join(
                    f'{start+i},{i+.25},{-i-.5},ok\n' for i in range(4))
                self.assertEqual(self.read_text(text), [[i+.25, -i-.5] for i in range(4)])

    def test_missing_duplicate_reordered_and_nonconsecutive_frames_refused(self):
        for labels in ((0, 2, 3), (0, 1, 1), (2, 1, 0), (0, 1, 3), (0, 2, 4)):
            with self.subTest(labels=labels):
                text = 'frame,y1,y2\n' + ''.join(f'{i},1,2\n' for i in labels)
                with self.assertRaisesRegex(ValueError, 'consecutively'):
                    self.read_text(text)

    def test_missing_or_malformed_frame_cells_and_headers_refused(self):
        for token in ('', '1.5', '1.0', 'nan', 'inf', '-1', '1e3', '1_000'):
            with self.subTest(token=token):
                with self.assertRaisesRegex(ValueError, 'frame must be'):
                    self.read_text(f'frame,y1,y2\n{token},1,2\n1,2,3\n2,3,4\n')
        for header in ('y1,y2', 'frame,y1', 'frame,y2', ''):
            with self.subTest(header=header):
                with self.assertRaisesRegex(ValueError, 'requires frame,y1,y2'):
                    self.read_text(header+'\n0,1,2\n1,2,3\n2,3,4\n')
        with self.assertRaisesRegex(ValueError, 'duplicate column'):
            self.read_text('frame,y1,y2,frame\n0,1,2,0\n1,2,3,1\n2,3,4,2\n')

    def test_bad_coordinates_and_short_tracks_refused(self):
        for value in ('', 'nan', 'inf', '-inf', 'oops'):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, 'finite numbers'):
                    self.read_text(f'frame,y1,y2\n0,{value},1\n1,2,3\n2,3,4\n')
        with self.assertRaisesRegex(ValueError, 'too many fields'):
            self.read_text('frame,y1,y2\n0,1,2,3\n1,2,3\n2,3,4\n')
        for body in ('', '0,1,2\n', '0,1,2\n1,2,3\n'):
            with self.assertRaisesRegex(ValueError, 'at least three'):
                self.read_text('frame,y1,y2\n'+body)

    def test_invalid_cadence_never_reaches_moment_estimation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'gap.csv'
            path.write_text('frame,y1,y2\n0,1,2\n2,2,3\n3,3,4\n')
            with patch.object(db, 'empirical_Gamma', side_effect=AssertionError('must not estimate')):
                with self.assertRaisesRegex(ValueError, 'consecutively'):
                    db.certify_track_csv(str(path), 1., .5)

    def test_cli_refuses_gaps_with_a_clear_error_and_no_result(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'gap.csv'
            path.write_text('frame,y1,y2\n0,1,2\n2,2,3\n3,3,4\n')
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                with self.assertRaises(SystemExit) as failure:
                    db.main(['--csv', str(path), '--json'])
            self.assertEqual(failure.exception.code, 2)
            self.assertEqual(out.getvalue(), '')
            self.assertIn('CSV line 3', err.getvalue())
            self.assertIn('consecutively', err.getvalue())
            self.assertNotIn('Traceback', err.getvalue())


if __name__ == '__main__':
    unittest.main()
