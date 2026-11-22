"""Independent original-tree controls for exact, non-affine row joins."""
from copy import deepcopy
from itertools import product
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import integer_language_decision as decision
import word_frontier as frontier
from test_word_frontier import graph_census, graph_data, profile


class IntegerJoinsTests(unittest.TestCase):
    def test_integer_relation_is_not_replaced_by_its_affine_hull(self):
        domain = decision.integer_patterns((1,) * 6)
        self.assertEqual(domain.bit_count(), 20)
        # Twenty patterns cannot be an affine binary subspace (power of two).
        for pattern in range(64):
            self.assertEqual(bool(domain >> pattern & 1), pattern.bit_count() == 3)

    def test_overlap_selectors_partition_patterns(self):
        for width in range(1, 7):
            positions = tuple(range(0, width, 2))
            masks = decision.selectors(width, positions)
            self.assertEqual(sum(masks), (1 << (1 << width)) - 1)
            for pattern in range(1 << width):
                expected = sum(((pattern >> i) & 1) << j
                               for j, i in enumerate(positions))
                self.assertEqual(decision.projection(1 << pattern, masks), 1 << expected)

    def test_join_can_reject_compatible_single_row_affine_hulls(self):
        # The second row forces b=c=d=e=f=-a. Its two assignments satisfy
        # the first row's parity hull (odd negative count), but not its sum.
        rows = {0: dict.fromkeys(range(6), 1),
                1: {0: 5, **dict.fromkeys(range(1, 6), 1)}}
        system = frontier.System((4, 2, 1),
                                 [(0, 0)] + [(1, i) for i in range(1, 6)],
                                 [], rows, [], [])
        engine = decision.RowJoins(system)
        self.assertEqual(engine.domains[0].bit_count(), 20)
        self.assertEqual(engine.domains[1].bit_count(), 2)
        self.assertTrue(all(p.bit_count() % 2 == 1 for p in range(64)
                            if engine.domains[1] >> p & 1))
        self.assertFalse(engine.propagate(range(len(engine.keys))))

    def test_original_graph_existence_and_witness(self):
        cases = ((3, 2, 1), (4, 2, 1), (4, 3, 1), (5, 3, 1),
                 (5, 3, 2), (6, 4, 3), (7, 4, 2), (5, 4, 2),
                 (9, 4, 2), (7, 5, 2), (6, 5, 4), (7, 5, 3))
        for lengths in cases:
            with self.subTest(lengths=lengths):
                count, _ = graph_census(lengths)
                result = decision.solve(lengths)
                self.assertEqual(result['status'], 'exact')
                self.assertEqual(result['exists'], bool(count))
                if not count:
                    continue
                word = result['word']
                vertices, pairs = graph_data(lengths)
                signs = {(0, 0): word['centre']}
                for arm in range(1, 4):
                    signs.update({(arm, d): 1 if ch == '+' else -1
                                  for d, ch in enumerate(word[f'arm{arm}'],
                                                         2 if arm < 3 else 1)})
                values = [signs[v] for v in vertices]
                self.assertEqual(sum(values), 0)
                self.assertFalse(any(profile(values, pairs).values()))
                self.assertEqual(len(values) // 2, (1 + sum(lengths)) // 2 - 1)

    def test_join_propagation_never_removes_a_real_solution(self):
        system = frontier.build_system((5, 3, 1))
        engine = decision.RowJoins(system)
        solutions = []
        for bits in product((0, 1), repeat=len(system.vertices)):
            if bits[system.vertices.index((0, 0))]:
                continue
            if all(sum(a * (1 - 2 * bits[v]) for v, a in row.items()) == 0
                   for row in system.rows.values()):
                solutions.append(bits)
        self.assertTrue(engine.propagate(range(len(engine.keys))))
        before = engine.domains.copy()
        row, left, _ = engine.branch()
        mark = len(engine.trail)
        engine.restrict(row, left)
        engine.propagate((row,))
        for bits in solutions:
            chosen = sum(bits[v] << i for i, v in enumerate(engine.keys[row]))
            if not left >> chosen & 1:
                continue
            for key, domain in zip(engine.keys, engine.domains):
                pattern = sum(bits[v] << i for i, v in enumerate(key))
                self.assertTrue(domain >> pattern & 1)
        engine.restore(mark)
        self.assertEqual(engine.domains, before)

    def test_limits_and_consistency_are_not_negative_answers(self):
        for options in ({'max_variables': 1}, {'max_nodes': 1}):
            result = decision.solve((4, 2, 1), **options)
            self.assertEqual(result['status'], 'resource_limit')
            self.assertFalse(result['existence_decided'])
            self.assertNotIn('exists', result)
        result = decision.solve((4, 2, 1), closure_only=True)
        self.assertEqual(result['status'], 'consistent_relaxation')
        self.assertFalse(result['existence_decided'])
        for options in ({'max_nodes': True}, {'max_nodes': 0},
                        {'max_variables': -1}, {'closure_only': 1}):
            with self.assertRaises(ValueError):
                decision.solve((4, 2, 1), **options)

    def test_receipt_and_damaged_word_rejection(self):
        result = decision.solve((4, 2, 1))
        self.assertTrue(decision.verify(json.loads(json.dumps(result)))['valid'])
        bad = deepcopy(result)
        word = bad['word']['arm1']
        bad['word']['arm1'] = ('+' if word[0] == '-' else '-') + word[1:]
        with self.assertRaises(ValueError):
            frontier.verify(bad['word'], audit_graph=True)
        with self.assertRaises(ValueError):
            decision.verify(bad)
        bad = deepcopy(result)
        bad['nodes'] += 1
        with self.assertRaises(ValueError):
            decision.verify(bad)
        self.assertTrue(decision.verify(decision.solve((7, 4, 2)))['valid'])

    def test_cli_records_and_replays(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / 'receipt.json')
            script = decision.__file__
            run = subprocess.run([sys.executable, script, '--lengths', '4', '2', '1',
                                  '--write', path], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertTrue(json.loads(run.stdout)['word_saved'])
            run = subprocess.run([sys.executable, script, '--verify', path],
                                 capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertTrue(json.loads(run.stdout)['valid'])


if __name__ == '__main__':
    unittest.main()
