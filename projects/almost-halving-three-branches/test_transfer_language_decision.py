"""Exhaustive projection controls and original-tree checks for the refinement."""
from itertools import combinations
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import transfer_language_decision as decision
import word_frontier as frontier
import word_transfer_compression as compression
from test_word_frontier import certificate, graph_census


class TwoEndedTests(unittest.TestCase):
    def test_projection_is_full_affine_image(self):
        # Enumerate the complete parity relaxation independently of elimination.
        for lengths in ((4, 2, 1), (5, 3, 1), (5, 3, 2), (6, 4, 2)):
            system, _ = compression.order_system(frontier.build_system(lengths))
            rows = [compression.parity_row(row) for row in system.rows.values()]
            centre = system.vertices.index((0, 0))
            assignments = [bits for bits in range(1 << len(system.vertices))
                           if not bits >> centre & 1
                           and all((mask & bits).bit_count() % 2 == rhs
                                   for mask, rhs in rows)]
            try:
                spaces = decision.projections(system, range(len(system.vertices) + 1))
            except compression.InconsistentParity:
                self.assertEqual(assignments, [])
                continue
            for active, _, _, space in spaces.values():
                active_mask = sum(1 << i for i in active)
                expected = {bits & active_mask for bits in assignments}
                free = space.free(active)
                actual = {space.decode(code, free) for code in range(1 << len(free))}
                self.assertEqual(actual, expected, lengths)

    def test_exact_counts_and_original_distances(self):
        for lengths in ((3, 2, 1), (4, 2, 1), (4, 3, 1), (5, 3, 2),
                        (6, 4, 3), (7, 4, 2), (5, 4, 2), (9, 4, 2),
                        (7, 5, 2), (6, 5, 4)):
            expected, signs = graph_census(lengths)
            result = decision.solve(lengths)
            self.assertTrue(result['existence_decided'])
            self.assertEqual(result['colourings_up_to_reversal'], expected)
            if signs is not None:
                saved = certificate(lengths, signs)
                self.assertTrue(frontier.verify(saved, audit_graph=True)['valid'])
                saved['arm1'] = ('+' if saved['arm1'][0] == '-' else '-') + saved['arm1'][1:]
                with self.assertRaises(ValueError):
                    frontier.verify(saved, audit_graph=True)

    def test_counts_preserve_every_integer_row(self):
        for c, b, a in combinations(range(1, 9), 3):
            old = frontier.solve(frontier.build_system((a, b, c)), max_width=25)
            new = decision.solve((a, b, c), max_width=25)
            self.assertEqual(new['colourings_up_to_reversal'],
                             old['colourings_up_to_reversal'], (a, b, c))

    def test_branch_return_and_corruption(self):
        saved = decision.branch_certificate()
        self.assertEqual(saved['two_ended_interface_bits'], 879)
        self.assertEqual(saved['future_period_layers'], 160)
        self.assertTrue(saved['parity_feasible_for_every_u'])
        self.assertFalse(saved['existence_decided'])
        # Verify the actual replay; do not accept even a plausible edited rank.
        saved['two_ended_interface_bits'] -= 1
        with self.assertRaisesRegex(ValueError, 'differs'):
            decision.verify(saved)

    def test_limits_never_claim_an_obstruction(self):
        for kwargs in ({'max_variables': 1}, {'max_width': 0}, {'max_states': 1}):
            result = decision.solve((4, 2, 1), **kwargs)
            self.assertEqual(result['status'], 'resource_limit')
            self.assertFalse(result['existence_decided'])
            self.assertNotIn('exists', result)
        for kwargs in ({'max_variables': True}, {'max_width': -1}, {'max_states': 0}):
            with self.assertRaises(ValueError):
                decision.solve((4, 2, 1), **kwargs)

    def test_integer_row_hull_detects_stronger_information(self):
        space = compression.Parity()
        row = {0: 2, 1: 1, 2: 1}
        space.add(*compression.parity_row(row))
        # Parity only forces b1=b2; integers additionally force b0!=b1.
        self.assertEqual(decision.row_hull(space, row), (2, 1, 4, 2))
        space.add(1, 0)
        self.assertEqual(decision.row_hull(space, row), (1, 0, 2, 1))
        space.add(2, 0)
        self.assertEqual(decision.row_hull(space, row), (0, -1, 1, 0))

    def test_complete_local_hull_replay(self):
        small = decision.local_hull_report((4, 2, 1), batch_size=2)
        self.assertTrue(small['complete'])
        self.assertEqual(small['rows_examined'],
                         len(frontier.build_system((4, 2, 1)).rows))
        self.assertEqual(small['empty_row_domains'], 0)
        self.assertFalse(small['existence_decided'])
        self.assertTrue(decision.verify(json.loads(json.dumps(small)))['valid'])

    def test_cli(self):
        script = str(Path(decision.__file__))
        run = subprocess.run([sys.executable, script, '--lengths', '4', '2', '1'],
                             capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stdout)
        self.assertEqual(json.loads(run.stdout)['colourings_up_to_reversal'], 2)
        run = subprocess.run([sys.executable, script, '--lengths', '4', '2', '1',
                              '--max-variables', '1'], capture_output=True, text=True)
        self.assertEqual(run.returncode, 2, run.stdout)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'bad.json'
            path.write_text('{"format": "wrong"}')
            run = subprocess.run([sys.executable, script, '--verify', str(path)],
                                 capture_output=True, text=True)
            self.assertEqual(run.returncode, 1)


if __name__ == '__main__':
    unittest.main()
