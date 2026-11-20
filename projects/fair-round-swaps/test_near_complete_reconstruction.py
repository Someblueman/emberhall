"""Independent predicates for Rook's near-complete theorem reconstruction."""
from fractions import Fraction
from random import Random
import unittest

from near_complete import path


def owners(witness, n, m):
    if len(witness) != m or sorted(g for _, g in witness) != list(range(m)):
        raise AssertionError("goods must occur exactly once")
    result = [-1] * m
    for agent, good in witness:
        if agent not in range(n):
            raise AssertionError("unknown owner")
        result[good] = agent
    return tuple(result)


def check_witness(u, missing, witness, greedy_final=False):
    n, m = len(u), len(u[0])
    result = owners(witness, n, m)
    q = m // n
    remaining = set(range(m))
    for start in range(0, m, n):
        block = witness[start:start + n]
        expected = set(range(n)) if start < q * n else set(range(n)) - {missing}
        if len(block) != len(expected) or {a for a, _ in block} != expected:
            raise AssertionError("wrong round recipients")
        for a, g in block:
            if (start < q * n or greedy_final) and any(u[a][h] > u[a][g] for h in remaining):
                raise AssertionError("non-greedy pick")
            remaining.remove(g)
    return result


def check_fair(u, allocation):
    bundles = [[g for g, a in enumerate(allocation) if a == i] for i in range(len(u))]
    for i, values in enumerate(u):
        own = sum(values[g] for g in bundles[i])
        for other in bundles:
            if other and not any(own >= sum(values[g] for g in other if g != removed)
                                 for removed in other):
                raise AssertionError("not EF1")


def check_step(a, b):
    changed = [g for g in range(len(a)) if a[g] != b[g]]
    if len(changed) != 2:
        raise AssertionError("not one exchange")
    x, y = changed
    if a[x] != b[y] or a[y] != b[x]:
        raise AssertionError("owners did not swap")


def endpoint(u, missing, rng):
    n, m = len(u), len(u[0])
    remaining, result = set(range(m)), []
    for r in range(m // n + 1):
        agents = list(range(n)) if r < m // n else [i for i in range(n) if i != missing]
        rng.shuffle(agents)
        for i in agents:
            best = max(u[i][g] for g in remaining)
            good = rng.choice(sorted(g for g in remaining if u[i][g] == best))
            result.append((i, good))
            remaining.remove(good)
    return tuple(result)


class ReconstructionTests(unittest.TestCase):
    def test_fresh_exact_profiles(self):
        rng = Random(2026112008)
        cases = outside_greedy = steps = 0
        for n in range(2, 6):
            for q in range(4):
                m = q * n + n - 1
                profiles = [tuple((0,) * m for _ in range(n)),
                            tuple(tuple(range(m)) for _ in range(n))]
                profiles += [tuple(tuple(Fraction(rng.randrange(5), rng.choice((1, 2, 7)))
                                         for _ in range(m)) for _ in range(n)) for _ in range(2)]
                for missing in range(n):
                    for u in profiles:
                        start, target = endpoint(u, missing, rng), endpoint(u, missing, rng)
                        for w in (start, target):
                            check_witness(u, missing, w, greedy_final=True)
                        rounds = (tuple(range(n)),) * q + (tuple(i for i in range(n) if i != missing),)
                        route = path(u, rounds, start, target)
                        actual = []
                        for w in route:
                            a = check_witness(u, missing, w)
                            check_fair(u, a)
                            actual.append(a)
                            try:
                                check_witness(u, missing, w, greedy_final=True)
                            except AssertionError:
                                outside_greedy += 1
                        self.assertEqual(actual[0], owners(start, n, m))
                        self.assertEqual(actual[-1], owners(target, n, m))
                        for a, b in zip(actual, actual[1:]):
                            check_step(a, b)
                            steps += 1
                        cases += 1
        self.assertGreater(outside_greedy, 0)
        print(f"independent reconstruction: {cases} paths, {steps} exchanges, "
              f"{outside_greedy} witnesses with non-greedy final picks")

    def test_independent_predicates_reject_corruption(self):
        u = ((9, 8, 3, 2, 1), (8, 9, 1, 3, 2), (9, 8, 2, 1, 3))
        with self.assertRaisesRegex(AssertionError, "non-greedy"):
            check_witness(u, 2, ((0, 2), (1, 1), (2, 0), (0, 3), (1, 4)))
        with self.assertRaisesRegex(AssertionError, "not EF1"):
            check_fair(u, (0, 0, 1, 1, 2))
        with self.assertRaisesRegex(AssertionError, "not one exchange"):
            check_step((0, 1, 2), (1, 2, 0))


if __name__ == "__main__":
    unittest.main()
