"""Independent projection and original-tree controls for parity coordinates."""
from itertools import combinations, product
import json
import hashlib
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

import word_frontier as frontier
import word_transfer_compression as compressed
from test_word_frontier import graph_census, certificate


class CompressionTests(unittest.TestCase):
    def test_affine_projection_against_exhaustive_bits(self):
        rng = random.Random(91644)
        for _ in range(100):
            size = rng.randrange(1, 8)
            rows = [(rng.randrange(1 << size), rng.randrange(2))
                    for _ in range(rng.randrange(1, 10))]
            expected = {b for b in range(1 << size)
                        if all((b & m).bit_count() % 2 == r for m, r in rows)}
            parity = compressed.Parity()
            try:
                for m, r in rows:
                    parity.add(m, r)
            except compressed.InconsistentParity:
                self.assertFalse(expected)
                continue
            active = list(range(size))
            rng.shuffle(active)
            while active:
                free = parity.free(active)
                actual = {parity.decode(code, free) for code in range(1 << len(free))}
                self.assertEqual(actual, expected)
                removed = active.pop()
                parity.forget(removed)
                expected = {b & ~(1 << removed) for b in expected}
            self.assertEqual(parity.rows, {})

    def test_counts_against_original_tree_positive_and_negative(self):
        for lengths in ((3, 2, 1), (4, 2, 1), (4, 3, 1), (5, 3, 2),
                        (6, 4, 3), (7, 4, 2), (5, 4, 2), (9, 4, 2),
                        (7, 5, 2), (6, 5, 4)):
            with self.subTest(lengths=lengths):
                expected, _ = graph_census(lengths)
                result = compressed.solve(frontier.build_system(lengths))
                self.assertTrue(result['existence_decided'])
                self.assertEqual(result['colourings_up_to_reversal'], expected)
                self.assertEqual(result['exists'], bool(expected))

    def test_decoding_every_live_state_matches_integer_transfer(self):
        # More cases than the independent graph census can cheaply enumerate.
        for c, b, a in combinations(range(1, 9), 3):
            system = frontier.build_system((a, b, c))
            expected = frontier.solve(system, max_width=25)
            actual = compressed.solve(system, max_width=25)
            self.assertEqual(actual['colourings_up_to_reversal'],
                             expected['colourings_up_to_reversal'], (a, b, c))

    def test_target_compression_certificate_and_resource_refusal(self):
        system = frontier.build_system((7787, 7627, 7571))
        saved = compressed.describe(system)
        self.assertEqual(saved['original_assignment_width'], 1141)
        self.assertEqual(saved['compressed_assignment_width'], 965)
        self.assertEqual(saved['maximum_stored_bits'], 964)
        self.assertFalse(saved['existence_decided'])
        self.assertTrue(compressed.verify(saved)['valid'])
        altered = dict(saved, compressed_assignment_width=964)
        with self.assertRaisesRegex(ValueError, 'differs'):
            compressed.verify(altered)
        answer = compressed.solve(system)
        self.assertEqual(answer['status'], 'resource_limit')
        self.assertFalse(answer['existence_decided'])
        self.assertNotIn('exists', answer)

    def test_full_integer_middle_cycle(self):
        saved = compressed.cycle_certificate()
        self.assertEqual(saved['loop_period'], 16)
        self.assertEqual(saved['extra_cycles_per_branch_step'], 945)
        self.assertEqual(saved['maximum_assignment_bits'], 965)
        self.assertEqual(saved['loop_state_bits'], 963)
        self.assertGreater(saved['original_width_witness'], saved['ordered_width'])
        self.assertFalse(saved['existence_decided'])
        self.assertTrue(compressed.verify(saved)['valid'])
        altered = dict(saved, extra_cycles_per_branch_step=946)
        with self.assertRaisesRegex(ValueError, 'differs'):
            compressed.verify(altered)

    def test_branch_insertion_preserves_every_integer_transition(self):
        # A separate full-stencil comparison, including forgetting and tail
        # windings, tests the symbolic insertion argument on t=1 and t=5.
        def trace(t):
            lengths = tuple(n + 7560 * t for n in (227, 67, 11))
            system, _ = compressed.order_system(frontier.build_system(lengths))
            c, frames = lengths[2], {}
            def label(i, layer):
                arm, depth = system.vertices[i]
                if not arm:
                    return (0, 0, 0, -1 - layer)
                q = 2 * depth - (lengths[arm - 1] - c)
                winding, residue = divmod(q, 2 * c)
                return (arm, winding, int(residue > c),
                        min(residue, 2 * c - residue) // 2 - layer)
            for i, before, after in frontier.schedule(system):
                arm, depth = system.vertices[i]
                q = 2 * depth - (lengths[arm - 1] - c) if arm else -2
                residue = q % (2 * c)
                layer = min(residue, 2 * c - residue) // 2 if arm else -1
                rows = tuple(sorted(tuple(sorted((label(j, layer), v)
                    for j, v in row.items())) for row in system.ending[i]))
                after_set = set(after)
                forgotten = tuple(label(j, layer) for j in before if j not in after_set)
                event = (label(i, layer), rows, forgotten, i in after_set)
                frames.setdefault(layer, hashlib.sha256()).update(repr(event).encode())
            return [frames[layer].hexdigest() for layer in sorted(frames)]
        base, longer = trace(1), trace(5)
        cut = 1041  # includes the centre at layer -1 and layers 0..1039
        inserted = 15120
        self.assertEqual(longer[:cut], base[:cut])
        self.assertEqual(set(longer[cut:cut + inserted]), {base[1025]})
        self.assertEqual(longer[cut + inserted:], base[cut:])

    def test_literal_witness_and_alteration(self):
        lengths = (4, 2, 1)
        _, signs = graph_census(lengths)
        saved = certificate(lengths, signs)
        self.assertTrue(frontier.verify(saved, audit_graph=True)['valid'])
        saved['arm1'] = ('+' if saved['arm1'][0] == '-' else '-') + saved['arm1'][1:]
        with self.assertRaises(ValueError):
            frontier.verify(saved)

    def test_cli_and_limits(self):
        script = str(Path(compressed.__file__))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'compression.json'
            run = subprocess.run([sys.executable, script, '--lengths', '4', '2', '1',
                                  '--write', str(path)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stdout)
            run = subprocess.run([sys.executable, script, '--verify', str(path)],
                                 capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stdout)
            bad = json.loads(path.read_text())
            bad['maximum_stored_bits'] += 1
            path.write_text(json.dumps(bad))
            run = subprocess.run([sys.executable, script, '--verify', str(path)],
                                 capture_output=True, text=True)
            self.assertEqual(run.returncode, 1)
        system = frontier.build_system((4, 2, 1))
        for kwargs in ({'max_width': 0}, {'max_states': 1}):
            result = compressed.solve(system, **kwargs)
            self.assertEqual(result['status'], 'resource_limit')
            self.assertFalse(result['existence_decided'])
            self.assertNotIn('exists', result)
        for kwargs in ({'max_width': -1}, {'max_states': 0}, {'max_width': True}):
            with self.assertRaises(ValueError):
                compressed.solve(system, **kwargs)


if __name__ == '__main__':
    unittest.main()
