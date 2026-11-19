import copy
import json
from fractions import Fraction as F
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import markov as m


class MarkovTests(unittest.TestCase):
    def test_complete_and_cycle_against_count_chains(self):
        for n in (3, 4, 5):
            for r in (F(1, 3), F(1), F(2), F(7, 2)):
                with self.subTest(n=n, fitness=r):
                    complete = m.solve(m.complete(n), r)
                    cycle = m.solve(m.cycle(tuple(range(n))), r)
                    self.assertEqual(m.uniform_fixation(complete, n), m.complete_probability(n, r))
                    self.assertEqual(m.uniform_fixation(cycle, n), m.cycle_probability(n, r))

    def test_four_vertex_research_seed(self):
        triples = [(F(1, 3),) * 3, (F(1, 2), F(1, 2), F(0)),
                   (F(1, 6), F(1, 3), F(1, 2)), (F(1, 20), F(3, 20), F(4, 5)),
                   (F(0), F(1, 5), F(4, 5))]
        for a, b, c in triples:
            w = [[0, a, b, c], [a, 0, c, b], [b, c, 0, a], [c, b, a, 0]]
            for r in (F(1, 2), F(1), F(3, 2), F(2)):
                s = sum(t / (2*r + (r-1)**2*t) for t in (a, b, c))
                expected = r*r*s / (1 + (r*r+1)*s)
                values = m.solve(w, r)
                self.assertEqual(m.uniform_fixation(values, 4), expected)

    def test_asymmetric_neutral_states_and_elementary_verifier(self):
        extremes = m.five_vertex_extremes()
        w = m.mixture([extremes[1], extremes[15], extremes[20]], [F(1, 7), F(2, 7), F(4, 7)])
        self.assertEqual(m.solve(w, F(1)), [F(s.bit_count(), 5) for s in range(32)])
        self.assertEqual(m.verify(m.certificate(w, F(3, 2))),
                         m.uniform_fixation(m.solve(w, F(3, 2)), 5))

    def test_transition_mass_and_no_dead_parent(self):
        w, r = m.validate(m.complete(5), F(3))
        for state in range(32):
            row = m.transition_row(w, r, state)
            self.assertEqual(sum(row.values()), 1)
            self.assertTrue(all(p >= 0 for p in row.values()))
        self.assertEqual(m.transition_row(w, r, 1)[0], F(1, 5))

    def test_neutral_derivatives_against_closed_forms(self):
        for n in (2, 3, 4, 5):
            first, second = m.neutral_derivatives(m.complete(n))
            self.assertEqual(m.uniform_fixation(first, n), F(n - 2, 2*n))
            self.assertEqual(m.uniform_fixation(second, n), F((n - 2)*(n - 6), 6*n))
        for a, b, c in [(F(1, 3),)*3, (F(1, 2), F(1, 2), F(0)),
                        (F(0), F(1, 5), F(4, 5))]:
            w = [[0, a, b, c], [a, 0, c, b], [b, c, 0, a], [c, b, a, 0]]
            first, second = m.neutral_derivatives(w)
            self.assertEqual(m.uniform_fixation(first, 4), F(1, 4))
            self.assertEqual(m.uniform_fixation(second, 4), -(1 + a*a + b*b + c*c) / 8)

    def test_extreme_counts_and_disconnected_faces(self):
        extremes = m.five_vertex_extremes()
        self.assertEqual(len(extremes), 22)
        self.assertEqual(len({tuple(map(tuple, w)) for w in extremes}), 22)
        for w in extremes[:12]:
            m.validate(w, F(1))
        for w in extremes[12:]:
            with self.assertRaisesRegex(ValueError, "connected"):
                m.solve(w, F(1))

    def test_bad_graph_and_fitness_refused(self):
        bad = [([[0, 1], [0, 0]], 1), ([[0, 0], [0, 0]], 1),
               ([[0, 1, 0], [0, 0, 1], [1, 0, 0]], 1),
               ([[F(1, 2), F(1, 2)], [F(1, 2), F(1, 2)]], 1),
               ([[0, 1.0], [1.0, 0]], 1), ([[0, 1], [1, 0]], 0),
               ([[0, 1], [1, 0]], True), ([[0, 1], [1, 0]], F(-1)),
               ([[0, 1, 0], [1, 0]], 1)]
        for w, r in bad:
            with self.subTest(w=w, r=r), self.assertRaises(ValueError):
                m.solve(w, r)

    def test_corrupt_certificates_refused(self):
        original = m.certificate(m.complete(4), F(2))
        edits = [("probabilities", 1, "1/2"), ("probabilities", 0, "1/10"),
                 ("probabilities", 1, "2"), ("probabilities", 1, 0.5)]
        for key, index, value in edits:
            data = copy.deepcopy(original)
            data[key][index] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                m.verify(data)
        for key, value in [("fitness", "3"), ("model", "Birth-death"), ("version", True)]:
            data = copy.deepcopy(original)
            data[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                m.verify(data)

    def test_real_cli_round_trip_and_corruption(self):
        script = str(Path(m.__file__).resolve())
        with tempfile.TemporaryDirectory() as directory:
            source, cert = Path(directory) / "input.json", Path(directory) / "cert.json"
            source.write_text(json.dumps({"weights": [[str(x) for x in row]
                                                       for row in m.complete(3)], "fitness": "2"}))
            made = subprocess.run([sys.executable, script, "--solve", str(source)],
                                  text=True, capture_output=True, check=True)
            cert.write_text(made.stdout)
            checked = subprocess.run([sys.executable, script, "--verify", str(cert)],
                                     text=True, capture_output=True)
            self.assertEqual(checked.returncode, 0, checked.stderr)
            self.assertIn("4/9", checked.stdout)
            data = json.loads(made.stdout)
            data["probabilities"][1] = "1/2"
            cert.write_text(json.dumps(data))
            rejected = subprocess.run([sys.executable, script, "--verify", str(cert)],
                                      text=True, capture_output=True)
            self.assertEqual(rejected.returncode, 1)
            self.assertIn("harmonic residual", rejected.stderr)


if __name__ == "__main__":
    unittest.main()
