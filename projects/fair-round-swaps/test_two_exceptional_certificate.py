"""Independent graph, deletion, inference and corrupted-proof checks."""
from copy import deepcopy
from fractions import Fraction
from itertools import combinations, permutations, product
import json
from pathlib import Path
from random import Random
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from two_exceptional_certificate import (BooleanDiagrams, Formulas, Propagation, certificates,
    favorite_attachment, graph, verified_proof, verify_certificate, _fair)


def deletion_fair(u, state):
    bundles = [[g for g, a in enumerate(state) if a == i] for i in range(5)]
    return all(any(sum(row[g] for g in bundles[i]) >=
                   sum(row[g] for g in bundle if g != removed) for removed in bundle)
               for i, row in enumerate(u) for bundle in bundles if bundle)


class CertificateTests(unittest.TestCase):
    def test_complete_graph_and_verified_proof(self):
        states, edges = graph()
        independent = {(3,) + p for p in permutations((0, 0, 1, 1, 2, 2, 4))}
        self.assertEqual(set(states), independent)
        expected = {(i, j) for i, a in enumerate(states) for j, b in enumerate(states)
                    if i < j and sum(x != y for x, y in zip(a, b)) == 2}
        self.assertEqual(set(edges), expected)
        self.assertEqual((len(states), len(edges)), (630, 5670))
        reports = verified_proof()
        self.assertEqual([r['case'] for r in reports], ['exceptional', 'automatic'])
        self.assertEqual([r['RUP_steps'] for r in reports], [5841, 1726])

    def test_paths_and_every_fairness_binding(self):
        rng = Random(2026112094)
        states, _ = graph()
        tested = 0
        for case in range(20):
            u = [tuple(Fraction(rng.randrange(6), rng.choice((1, 2, 7)))
                       for _ in range(8)) for _ in range(5)]
            u[2] = (1,) * 8
            for i in (3, 4):
                u[i] = (max(u[i]),) + u[i][1:]
            if case == 0:
                u = [(0,) * 8] * 5
            live = []
            for a in states:
                fair = deletion_fair(u, a)
                self.assertEqual(_fair(u, a), fair)
                if fair:
                    live.append(a)
            for start in rng.sample(live, min(5, len(live))):
                route = favorite_attachment(u, start)
                best = max(range(1, 8), key=lambda g: (u[4][g], -g))
                self.assertEqual(route[0], start)
                self.assertEqual(route[-1].index(4), best)
                self.assertLessEqual(len(route), 630)
                for a in route:
                    self.assertEqual(a[0], 3)
                    self.assertEqual([a.count(i) for i in range(5)], [2, 2, 2, 1, 1])
                    self.assertTrue(deletion_fair(u, a))
                for a, b in zip(route, route[1:]):
                    changed = [g for g in range(8) if a[g] != b[g]]
                    self.assertEqual(len(changed), 2)
                    x, y = changed
                    self.assertEqual((a[x], a[y]), (b[y], b[x]))
                tested += 1
        self.assertEqual(tested, 100)

    def test_corrupted_proofs_are_rejected(self):
        original = certificates()[0]
        bad = deepcopy(original)
        bad['variables'][1] = ['linear', 2, [0, 1, 0, 0, 0, 0, 0, 0]]
        with self.assertRaisesRegex(ValueError, 'utility row'):
            verify_certificate(bad)
        bad = deepcopy(original)
        bad['theory'][0][1][0][1] += 1
        with self.assertRaisesRegex(ValueError, 'sum to zero'):
            verify_certificate(bad)
        bad = deepcopy(original)
        atom = next(i for i, spec in enumerate(bad['variables'], 1) if spec[0] == 'linear')
        bad['tautologies'] = [[atom]]
        with self.assertRaisesRegex(ValueError, 'tautology'):
            verify_certificate(bad)
        bad = deepcopy(original)
        bad['proof'] = [[]]
        with self.assertRaisesRegex(ValueError, 'RUP step'):
            verify_certificate(bad)
        bad = deepcopy(original)
        bad['proof'].pop()
        with self.assertRaisesRegex(ValueError, 'empty clause'):
            verify_certificate(bad)

    def test_symbolic_fairness_definitions_match_deletions(self):
        states, edges = graph()
        data = certificates()[0]
        formulas = Formulas(data['variables'], states, edges, data['case'])
        rng = Random(2094)
        for _ in range(4):
            u = [[rng.randrange(5) for _ in range(8)] for _ in range(5)]
            u[2] = [1] * 8
            for i in (3, 4):
                u[i][0] = max(u[i])
            values = {1: True}
            for k, spec in enumerate(data['variables'][1:], 2):
                kind = spec[0]
                if kind == 'linear':
                    values[k] = sum(a*b for a, b in zip(u[spec[1]], spec[2])) >= 0
                elif kind == 'fair':
                    values[k] = deletion_fair(u, states[spec[1]])
                elif kind == 'reach':
                    values[k] = True
                else:
                    args = [values[abs(v)] == (v > 0) for v in spec[1]]
                    values[k] = all(args) if kind == 'and' else any(args) if kind == 'or' else args[0] == args[1]
            fair_ids = {k for (kind, _), k in formulas.names.items() if kind == 'fair'}
            asserted = {clause[0] for clause in formulas.clauses if len(clause) == 1}
            bindings = [k for k, (op, args) in formulas.defs.items()
                        if op == 'iff' and k in asserted and any(v in fair_ids for v in args)]
            self.assertEqual(len(bindings), 630)
            self.assertTrue(all(values[k] for k in bindings))

    def test_boolean_and_propagation_oracles(self):
        definitions = {4: ('and', (2, 3)), 5: ('or', (-2, -3)), 6: ('iff', (4, -5))}
        diagrams = BooleanDiagrams(definitions)
        for clause in combinations((2, -2, 3, -3, 4, -4, 5, -5, 6, -6), 3):
            def evaluate(a, b):
                values = {1: True, 2: a, 3: b, 4: a and b, 5: not a or not b, 6: True}
                return any(values[abs(v)] == (v > 0) for v in clause)
            self.assertEqual(diagrams.tautology(clause),
                             all(evaluate(a, b) for a, b in product((False, True), repeat=2)))
        rng = Random(94)
        for _ in range(100):
            clauses = [tuple(rng.choice((-1, 1))*rng.randrange(1, 5) for _ in range(3))
                       for _ in range(10)]
            p = Propagation()
            for clause in clauses:
                p.add(clause)
            assumed = (rng.choice((-1, 1))*rng.randrange(1, 5),)
            # A positive RUP answer must make the negated clause unsatisfiable.
            if p.contradiction(assumed):
                self.assertFalse(any(all(any(values[abs(v)-1] == (v > 0) for v in c)
                                             for c in clauses + [tuple(-v for v in assumed)])
                                     for values in product((False, True), repeat=4)))

    def test_invalid_inputs_and_real_command(self):
        u = ((1,) * 8,) * 5
        start = (3, 4, 0, 0, 1, 1, 2, 2)
        with self.assertRaisesRegex(ValueError, 'sizes'):
            favorite_attachment(u, (0,) * 8)
        with self.assertRaisesRegex(ValueError, 'exact nonnegative'):
            favorite_attachment(((1.0,) * 8,) * 5, start)
        bad = list(u)
        bad[2] = (0, 0, 0, 0, 1, 1, 1, 1)
        with self.assertRaisesRegex(ValueError, 'automatically fair'):
            favorite_attachment(bad, start)
        result = subprocess.run([sys.executable, '-S', str(Path(__file__).with_name(
            'two_exceptional_certificate.py'))], text=True, capture_output=True, check=True)
        self.assertIn('"status": "verified"', result.stdout)
        self.assertIn('"RUP_steps": 5841', result.stdout)

    def test_cli_accepts_both_case_orders(self):
        command = Path(__file__).with_name('two_exceptional_certificate.py')
        with TemporaryDirectory() as directory:
            source, exported = Path(directory) / 'input.json', Path(directory) / 'export.json'
            for data in (certificates(), list(reversed(certificates()))):
                with self.subTest(cases=[item['case'] for item in data]):
                    source.write_text(json.dumps(data))
                    result = subprocess.run([sys.executable, '-I', '-S', str(command),
                        '--certificate', str(source), '--export', str(exported)],
                        text=True, capture_output=True, check=True)
                    report = json.loads(result.stdout)
                    self.assertEqual(report['status'], 'verified')
                    self.assertEqual([item['case'] for item in report['proofs']],
                                     [item['case'] for item in data])
                    self.assertEqual(json.loads(exported.read_text()), data)

    def test_cli_rejects_incomplete_and_malformed_pairs(self):
        command = Path(__file__).with_name('two_exceptional_certificate.py')
        exceptional, automatic = certificates()
        corrupted = deepcopy(automatic)
        corrupted['proof'].pop()
        cases = {
            'empty': [], 'only exceptional': [exceptional], 'only automatic': [automatic],
            'duplicate exceptional': [exceptional, exceptional],
            'duplicate automatic': [automatic, automatic],
            'extra': [exceptional, automatic, exceptional],
            'object': {}, 'null': None, 'scalar': 1,
            'nonobject entry': [exceptional, None],
            'missing case': [exceptional, {}],
            'unknown case': [exceptional, {'case': 'other'}],
            'malformed case': [exceptional, {'case': ['automatic']}],
            'corrupt second proof': [exceptional, corrupted],
        }
        with TemporaryDirectory() as directory:
            source, exported = Path(directory) / 'input.json', Path(directory) / 'export.json'
            for name, data in cases.items():
                with self.subTest(name=name):
                    source.write_text(json.dumps(data))
                    exported.write_text('unchanged')
                    result = subprocess.run([sys.executable, '-I', '-S', str(command),
                        '--certificate', str(source), '--export', str(exported)],
                        text=True, capture_output=True)
                    self.assertEqual(result.returncode, 2, result.stderr)
                    self.assertEqual(result.stdout, '')
                    self.assertIn('certificate error:', result.stderr)
                    self.assertEqual(exported.read_text(), 'unchanged')


if __name__ == '__main__':
    unittest.main()
