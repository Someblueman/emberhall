"""Seeded property checks of the first-order operator contract.

Random primitive sources and random compositions of supported operators
are built once as a step list and applied to both the library arrays and
the independent dense ``J C J^T`` oracle duals; the covariances must agree
for every generated case.  Shared-source identity laws are pinned
separately: reusing one primitive cancels exactly, two equal-valued
independent primitives do not.
"""
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from covreduce import rebin, reorder_dims, select, source
from covreduce.oracle import dense_jcjt_oracle, max_covariance_difference

TOL = 1e-8


def random_psd(rng, n):
    a = [[rng.uniform(-1.0, 1.0) for _ in range(n)] for _ in range(n)]
    return [[sum(a[i][k] * a[j][k] for k in range(n)) + (0.5 if i == j else 0.0)
             for j in range(n)] for i in range(n)]


def make_parts(rng, n):
    monitor = source(rng.uniform(50.0, 150.0), rng.uniform(1.0, 9.0))
    counts = source([rng.uniform(20.0, 120.0) for _ in range(n)],
                    random_psd(rng, n), dims=("bin",),
                    coords={"bin": tuple(i + 0.5 for i in range(n))})
    background = source([rng.uniform(0.0, 10.0) for _ in range(n)],
                        [rng.uniform(0.1, 1.0) for _ in range(n)],
                        dims=("bin",),
                        coords={"bin": tuple(i + 0.5 for i in range(n))})
    other = source([rng.uniform(20.0, 120.0) for _ in range(n)],
                   [rng.uniform(1.0, 9.0) for _ in range(n)], dims=("bin",),
                   coords={"bin": tuple(i + 0.5 for i in range(n))})
    return [monitor, counts, background, other]


def generate_steps(rng, n):
    """A random valid step list; returns (steps, final_length)."""
    steps = []
    length = n
    divided = False
    for _ in range(rng.randint(2, 5)):
        choices = ["scale", "neg_scale", "window_same"]
        if length == n:
            choices += ["add_background", "sub_other", "add_counts_scaled"]
        if not divided:
            choices.append("divide_monitor")
        if length >= 3:
            choices.append("window_valid")
        step = rng.choice(choices)
        if step == "divide_monitor":
            divided = True
        if step == "window_valid":
            w = rng.randint(2, 3)
            steps.append((step, tuple(rng.uniform(-1.0, 1.0)
                                       for _ in range(w))))
            length -= w - 1
        elif step == "window_same":
            w = rng.randint(2, 3)
            steps.append((step, tuple(rng.uniform(-1.0, 1.0)
                                       for _ in range(w))))
        elif step in ("scale", "neg_scale", "add_counts_scaled"):
            steps.append((step, rng.uniform(0.5, 2.0)
                          * (1.0 if step == "scale" else -1.0)))
        else:
            steps.append((step, None))
    if rng.random() < 0.5:
        steps.append((rng.choice(["sum", "mean"]), None))
    return steps


def apply_steps(parts, steps):
    monitor, counts, background, other = parts
    x = counts
    for step, arg in steps:
        if step in ("scale", "neg_scale"):
            x = x * arg
        elif step == "add_counts_scaled":
            x = x + counts * arg
        elif step == "add_background":
            x = x + background
        elif step == "sub_other":
            x = x - other
        elif step == "divide_monitor":
            x = x / monitor
        elif step == "window_same":
            x = x.moving_window("bin", arg, mode="same")
        elif step == "window_valid":
            x = x.moving_window("bin", arg, mode="valid")
        elif step == "sum":
            x = x.sum()
        elif step == "mean":
            x = x.mean()
    return x


class TestRandomCompositions(unittest.TestCase):
    def test_random_1d_compositions_match_oracle(self):
        cases = 0
        for seed in range(40):
            rng = random.Random(10_000 + seed)
            n = rng.randint(3, 6)
            parts = make_parts(rng, n)
            steps = generate_steps(rng, n)
            out = apply_steps(parts, steps)
            with self.subTest(seed=seed, steps=[s for s, _ in steps]):
                values, _ = dense_jcjt_oracle(
                    parts, lambda p: apply_steps(p, steps))
                for got, want in zip(out.values, values):
                    self.assertAlmostEqual(got, want, places=9)
                diff = max_covariance_difference(
                    out, parts, lambda p: apply_steps(p, steps))
                self.assertLess(diff, TOL)
            cases += 1
        self.assertEqual(cases, 40)

    def test_random_rebin_partitions_match_oracle(self):
        for seed in range(12):
            rng = random.Random(20_000 + seed)
            n = 6
            parts = make_parts(rng, n)
            cuts = sorted(rng.sample([1, 2, 3, 4, 5], rng.randint(1, 2)))
            edges = tuple(float(e) for e in [0, *cuts, n])
            intensive = rng.random() < 0.5
            old_edges = tuple(float(i) for i in range(n + 1))
            out = rebin(parts[1], "bin", edges, intensive=intensive)
            diff = max_covariance_difference(
                out, parts,
                lambda p: p[1].rebin("bin", old_edges=old_edges,
                                     new_edges=edges,
                                     intensive=intensive))
            with self.subTest(seed=seed, edges=edges, intensive=intensive):
                self.assertLess(diff, TOL)
                if not intensive:
                    self.assertAlmostEqual(sum(out.values),
                                           sum(parts[1].values), places=9)

    def test_random_2d_reorder_reduce_matches_oracle(self):
        for seed in range(12):
            rng = random.Random(30_000 + seed)
            r, c = rng.randint(2, 3), rng.randint(2, 3)
            x = source(
                [[rng.uniform(1.0, 50.0) for _ in range(c)]
                 for _ in range(r)],
                random_psd(rng, r * c), dims=("row", "col"))
            scale_factor = rng.uniform(-2.0, 2.0)
            out = reorder_dims(x, "col", "row") * scale_factor
            out = out.sum("row")
            diff = max_covariance_difference(
                out, [x],
                lambda a: (a[0].reorder_dims("col", "row")
                           * scale_factor).sum("row"))
            with self.subTest(seed=seed, shape=(r, c)):
                self.assertLess(diff, TOL)


class TestIdentityLaws(unittest.TestCase):
    def test_shared_source_cancels_exactly(self):
        rng = random.Random(99)
        x = source([rng.uniform(1.0, 9.0) for _ in range(4)],
                   random_psd(rng, 4), dims=("bin",))
        self.assertEqual((x - x).values, (0.0,) * 4)
        for v in (x - x).variance:
            self.assertEqual(v, 0.0)

    def test_independent_twins_do_not_cancel(self):
        a = source([10.0, 5.0], [2.0, 1.0], dims=("bin",))
        b = source([10.0, 5.0], [2.0, 1.0], dims=("bin",))
        self.assertEqual((a - b).values, (0.0, 0.0))
        self.assertAlmostEqual((a - b).variance[0], 4.0, places=12)
        self.assertGreater((a - b).variance[1], 0.0)

    def test_shared_monitor_cancels_in_ratio_of_rates(self):
        monitor = source(1000.0, 25.0)
        counts = source([120.0, 80.0], [12.0, 9.0], dims=("bin",))
        rates = counts / monitor
        with_monitor = rates[0] / rates[1]
        counts_only = counts[0] / counts[1]
        self.assertAlmostEqual(with_monitor.value, counts_only.value,
                               places=12)
        self.assertAlmostEqual(with_monitor.variance, counts_only.variance,
                               places=12)

    def test_select_takes_covariance_submatrix(self):
        rng = random.Random(7)
        x = source([rng.uniform(1.0, 9.0) for _ in range(5)],
                   random_psd(rng, 5), dims=("bin",))
        out = select(x, "bin", [3, 0, 3])
        full = x.covariance()
        for i, si in enumerate([3, 0, 3]):
            for j, sj in enumerate([3, 0, 3]):
                self.assertAlmostEqual(out.covariance()[i][j], full[si][sj],
                                       places=12)


if __name__ == "__main__":
    unittest.main()

