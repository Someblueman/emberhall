"""Finite falsification checks for the candidate general near-complete theorem."""

from itertools import combinations
from random import Random
import unittest

from near_complete import path, validate_relaxed
from swaps import allocation, ef1, favorites, picking_outcomes, rounds_for


def random_witness(u, rounds, rng):
    picks = []
    goods = list(range(len(u[0])))
    for agents in rounds:
        order = list(agents)
        rng.shuffle(order)
        for i in order:
            g = rng.choice(favorites(u, i, tuple(goods)))
            picks.append((i, g))
            goods.remove(g)
    return tuple(picks)


class NearCompleteTest(unittest.TestCase):
    def test_all_small_outcomes_and_ties(self):
        rng = Random(2026112002)
        pairs = cases = non_greedy = 0
        for n, m in ((2, 3), (3, 2), (3, 5), (3, 8), (4, 3), (4, 7)):
            for missing in range(n):
                rounds = rounds_for(n, m, tuple(i for i in range(n) if i != missing))
                for trial in range(8):
                    u = tuple(tuple(0 if trial == 0 else rng.randrange(4) for _ in range(m))
                              for _ in range(n))
                    outcomes = picking_outcomes(u, rounds)
                    values = list(outcomes.values())
                    choices = list(combinations(range(len(values)), 2))
                    if len(choices) > 30:
                        choices = rng.sample(choices, 30)
                    for a, b in choices:
                        result = path(u, rounds, values[a], values[b])
                        self.assertEqual(allocation(result[0], m), allocation(values[a], m))
                        self.assertEqual(allocation(result[-1], m), allocation(values[b], m))
                        non_greedy += sum(allocation(w, m) not in outcomes for w in result)
                        pairs += 1
                    cases += 1
        self.assertGreater(non_greedy, 0)  # The relaxed final round is actually exercised.
        print(f"near-complete small cases: {cases}, paths: {pairs}, "
              f"vertices outside greedy outcomes: {non_greedy}")

    def test_longer_sampled_endpoints(self):
        rng = Random(2026112003)
        pairs = longest = 0
        for n, m in ((3, 11), (4, 11), (5, 9), (5, 14)):
            for missing in range(n):
                rounds = rounds_for(n, m, tuple(i for i in range(n) if i != missing))
                for trial in range(12):
                    u = tuple(tuple(rng.choice((0, 0, 1, 2, 7)) for _ in range(m)) for _ in range(n))
                    a = random_witness(u, rounds, rng)
                    b = random_witness(u, rounds, rng)
                    result = path(u, rounds, a, b)
                    self.assertEqual(allocation(result[0], m), allocation(a, m))
                    self.assertEqual(allocation(result[-1], m), allocation(b, m))
                    longest = max(longest, len(result) - 1)
                    pairs += 1
        print(f"near-complete larger cases: {pairs}, longest path: {longest} swaps")

    def test_free_final_round_and_invalid_prefix(self):
        u = ((9, 8, 3, 2, 1), (8, 9, 1, 3, 2), (9, 8, 2, 1, 3))
        rounds = rounds_for(3, 5, (0, 1))
        # A nonmaximizing final choice is legal and EF1; an earlier one is not.
        witness = ((0, 0), (1, 1), (2, 4), (0, 3), (1, 2))
        validate_relaxed(u, rounds, witness)
        self.assertTrue(ef1(u, allocation(witness, 5)))
        with self.assertRaises(ValueError):
            validate_relaxed(u, rounds, ((0, 2), (1, 1), (2, 0), (0, 3), (1, 4)))
        with self.assertRaises(ValueError):
            path(u, rounds_for(3, 4, (0,)), (), ())


if __name__ == "__main__":
    unittest.main()
