"""Focused tests for the long-period hunt.

Run: python3 -m pytest projects/five-marks/test_longperiod.py -q
  or: python3 -m unittest discover -s projects/five-marks -p "test_longperiod.py"
Finite computation is supporting evidence, never an infinite-family proof.
"""
import unittest

from counterexample import differences, shape
from longperiod import lower_construction_legal, periodic_maximum_at

try:
    from counterexample import differences as _d, shape as _s  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover - exercised only under packaging
    pass


def expanded_translates_legal(residues, period, forbidden) -> bool:
    """Independent oracle: expand residues to integer starts and check pairs."""
    from itertools import combinations

    lifts = sorted({r + k * period for r in residues for k in (-2, -1, 0, 1, 2)})
    for x, y in combinations(lifts, 2):
        if y - x in forbidden:
            return False
    return True


class SelfCollisionPeriodTests(unittest.TestCase):
    def test_period_dividing_a_forbidden_distance_is_empty(self) -> None:
        self.assertEqual(periodic_maximum_at(1, differences(shape(1))), (0, ()))
        self.assertEqual(periodic_maximum_at(3, differences(shape(3))), (0, ()))

    def test_reported_witnesses_check_across_repeats(self) -> None:
        cases = [(1, 1), (3, 3), (5, 5), (1, 9), (3, 19), (5, 10), (11, 59)]
        cases += [(b, k * (5 * b + 4)) for b in (1, 3, 5) for k in (3, 4)]
        for parameter, period in cases:
            forbidden = differences(shape(parameter))
            size, residues = periodic_maximum_at(period, forbidden)
            self.assertEqual(len(residues), size)
            self.assertTrue(
                expanded_translates_legal(residues, period, forbidden),
                (parameter, period, residues),
            )
            if any(d % period == 0 for d in forbidden):
                self.assertEqual(residues, ())

    def test_noncolliding_period_gives_nonempty_witness(self) -> None:
        size, residues = periodic_maximum_at(9, differences(shape(1)))
        self.assertGreater(size, 0)
        self.assertTrue(expanded_translates_legal(residues, 9, differences(shape(1))))

    def test_lower_construction_rejects_off_domain_period(self) -> None:
        with self.assertRaises(ValueError):
            lower_construction_legal(1, 10)
        with self.assertRaises(ValueError):
            lower_construction_legal(3, 20)


class LongPeriodTests(unittest.TestCase):
    def test_no_density_beats_the_bound(self) -> None:
        for parameter in (1, 3, 5, 7, 9, 11):
            n = 5 * parameter + 4
            m = differences(shape(parameter))
            for multiple in (3, 4):
                period = multiple * n
                size, _ = periodic_maximum_at(period, m)
                self.assertEqual(size * n, parameter * period)

    def test_lower_construction_stays_legal(self) -> None:
        for parameter in (1, 3, 5, 7, 9, 11):
            n = 5 * parameter + 4
            for period in (n, 2 * n, 3 * n, 4 * n):
                self.assertTrue(lower_construction_legal(parameter, period))


if __name__ == '__main__':
    unittest.main()
