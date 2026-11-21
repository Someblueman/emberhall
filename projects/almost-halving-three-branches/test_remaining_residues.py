"""Independent graph checks and exact, all-phase certificate checks."""
from collections import Counter, deque
from itertools import product
import unittest

import remaining_residues as rr
from published_cases import check_pair


def graph_profiles(lengths, left, right):
    graph = {(0, 0): []}
    for arm, length in enumerate(lengths, 1):
        for p in range(1, length+1):
            v, parent = (arm, p), (arm, p-1) if p > 1 else (0, 0)
            graph[v] = [parent]
            graph[parent].append(v)
    profiles = []
    for vertices in (left, right):
        counts = Counter()
        for index, source in enumerate(vertices):
            distance, todo = {source: 0}, deque([source])
            while todo:
                v = todo.popleft()
                for w in graph[v]:
                    if w not in distance:
                        distance[w] = distance[v]+1
                        todo.append(w)
            counts.update(distance[v] for v in vertices[:index])
        profiles.append(counts)
    return profiles


class RemainingResiduesTest(unittest.TestCase):
    def test_all_uniform_words_on_small_bases(self):
        # Exhaust all endpoint words for factor three, not a template search:
        # independently check both original base partitions and every lift.
        for family in ("five", "seven"):
            lengths, signs = rr.base_signs(family, 0)
            left = [v for v, s in signs.items() if s == 1]
            right = [v for v, s in signs.items() if s == -1]
            self.assertEqual(*graph_profiles(lengths, left, right))
            for letters in product("pPcC", repeat=2):
                lifted = rr.endpoint_lift(lengths, signs, 3, "".join(letters))
                plus = [v for v, s in lifted.items() if s == 1]
                minus = [v for v, s in lifted.items() if s == -1]
                if len(plus) == len(minus):
                    self.assertNotEqual(*graph_profiles(tuple(3*n for n in lengths), plus, minus))

    def test_original_tree_diagnostic_and_altered_pair(self):
        result = rr.diagnostic("seven", 0, None, None)
        profiles = graph_profiles(result["lengths"], result["left"], result["right"])
        self.assertEqual(dict(profiles[0]), result["left_profile"])
        self.assertEqual(dict(profiles[1]), result["right_profile"])
        self.assertFalse(result["homometric"])
        self.assertEqual(result["size"], result["target"])
        lengths, signs = rr.base_signs("seven", 0)
        left = sorted(v for v, s in signs.items() if s == 1)
        right = sorted(v for v, s in signs.items() if s == -1)
        left[0], right[0] = right[0], left[0]
        self.assertNotEqual(*graph_profiles(lengths, left, right))
        self.assertFalse(check_pair(lengths, left, right)["homometric"])

    def test_success_criterion_is_not_a_universal_impossibility(self):
        lengths = (5, 4, 2)
        signs = {(0, 0): 1} | {(i, p): s for i, word in enumerate(
            ((-1,)*5, (1,)*4, (-1, 1)), 1) for p, s in enumerate(word, 1)}
        self.assertEqual(rr.child_residual(lengths, signs), {})
        for factor in (3, 5, 7):
            lifted = rr.endpoint_lift(lengths, signs, factor, "cC"*((factor-1)//2))
            plus = [v for v, s in lifted.items() if s == 1]
            minus = [v for v, s in lifted.items() if s == -1]
            self.assertEqual(len(plus), len(minus))
            self.assertEqual(*graph_profiles(tuple(factor*n for n in lengths), plus, minus))

    def test_invalid_domain(self):
        for t in (-1, True, 1.5):
            with self.assertRaises(ValueError):
                rr.classify_parameter(t)
        lengths, signs = rr.base_signs("seven", 0)
        for factor, word in ((2, "c"), (3, "c"), (3, "xx")):
            with self.assertRaises(ValueError):
                rr.endpoint_lift(lengths, signs, factor, word)

    def test_all_colouring_gcd_certificate_has_no_parameter_bound(self):
        remaining = rr.proof_certificate()["remaining_residues_mod_165"]
        for r in remaining:
            for q in (0, 1, 10**40):
                cert = rr.all_colour_obstruction(r+165*q)
                i, j = cert["five"]["equal_coefficients_at"]
                self.assertLessEqual(j, 15)
                self.assertEqual((-1)**(i-5), 1)
                self.assertEqual((-1)**(j-5), -1)
                self.assertNotEqual(cert["seven"]["actual_sum"],
                                    cert["seven"]["required_sum"])
        with self.assertRaises(ValueError):
            rr.all_colour_obstruction(1)

    def test_reduced_child_equation_identity(self):
        # Independent formal endpoint variables, not substituted lengths.
        self.assertEqual(rr.elimination_residual(), {})
        for s in (-1, 1):
            for minority in range(3):
                self.assertEqual(rr.endpoint_identity_residual(s, minority), {})


if __name__ == "__main__":
    unittest.main()
