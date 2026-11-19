import unittest
from itertools import product

from cubic import cubic, enumerate_sectors, fourth_weights, matching_walk, sectors
from delayed_escape import extend, gaps, nest
from escape_chain import stop_weights
from weighted_open import exterior


class CubicTests(unittest.TestCase):
    def test_finite_fourth_stop_certificate(self):
        for a in range(5, 10):
            direct = stop_weights(a, 4)
            for d, expected in [(0, [8, 8]), (1, [9, 9])]:
                weights, touched = fourth_weights(a, d)
                self.assertEqual(weights, expected)
                self.assertEqual(weights, sorted(n for _, n in direct[a - d]))
                if a >= 8:
                    self.assertEqual(min(touched), a - 7)
                    start = nest(exterior(a - d - 1), d + 1, "M")
                    lifted = tuple(x for f in start
                                   for x in ((1, 0, 2) if f == 0 else (f + 2,)))
                    self.assertEqual(lifted, nest(exterior(a - d + 1), d + 1, "M"))

    def test_walk_recovers_all_and_only_matching_gaps(self):
        for symbols in product("MV", repeat=6):
            for order in extend((0,), "".join(symbols)):
                for symbol in "MV":
                    walked = list(matching_walk(order, symbol, set()))
                    self.assertEqual(sorted(walked), list(gaps(order, symbol)))

    def test_components_against_unpruned_stacks(self):
        for k in range(2, 10):
            self.assertEqual(enumerate_sectors(k), sectors(k))
        self.assertEqual(sectors(2), {2: 5, None: 5})
        self.assertEqual(cubic(8), 1618)

    def test_summation_and_domain(self):
        for k in (2, 3, 4, 5, 13, 78, 999):
            self.assertEqual(sum(sectors(k).values()), cubic(k))
        for k in (-1, 0, 1):
            for function in (sectors, cubic):
                with self.assertRaises(ValueError):
                    function(k)
