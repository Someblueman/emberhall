"""Two-dimensional compositions against the dense J C J^T oracle.

The randomised oracle property tests cover one-dimensional operator
chains.  This file runs the same independent-oracle check on grids:
shared monitor division, background subtraction, a scalar level,
``moving_window`` on one axis, ``rebin`` on the other, ``reorder_dims``
and reductions, with diagonal and densely correlated field covariance.
"""
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from covreduce import source  # noqa: E402
from covreduce.oracle import dense_jcjt_oracle  # noqa: E402

TOL = 1e-9


def _dense_covariance(rng, n):
    factors = [[rng.uniform(-0.4, 0.4) for _ in range(n)] for _ in range(n)]
    return [[sum(factors[i][k] * factors[j][k] for k in range(n))
             + (1.0 if i == j else 0.0) for j in range(n)]
            for i in range(n)]


def _build(seed, rows, cols, dense=False):
    rng = random.Random(seed)
    n = rows * cols
    cov = (_dense_covariance(rng, n) if dense
           else [rng.uniform(0.5, 3.0) for _ in range(n)])
    counts = source(
        [[rng.uniform(5.0, 50.0) for _ in range(cols)] for _ in range(rows)],
        cov, dims=("y", "x"))
    background = source(
        [[rng.uniform(0.0, 2.0) for _ in range(cols)] for _ in range(rows)],
        [rng.uniform(0.05, 0.3) for _ in range(n)], dims=("y", "x"))
    monitor = source(rng.uniform(80.0, 120.0), rng.uniform(2.0, 8.0))
    level = source(rng.uniform(0.5, 1.5), rng.uniform(0.01, 0.05))
    return counts, background, monitor, level


def _program(rows):
    edges = tuple(float(i) for i in range(rows + 1))

    def program(parts):
        counts, background, monitor, level = parts
        rates = counts / monitor - background / monitor + level
        smoothed = rates.moving_window("x", (0.25, 0.5, 0.25))
        rebinned = smoothed.rebin("y", old_edges=edges,
                                   new_edges=(edges[0], edges[-2],
                                              edges[-1]))
        reordered = rebinned.reorder_dims("x", "y")
        return reordered.sum("x") + reordered.mean("x")

    return program


class TestOracle2D(unittest.TestCase):
    def check(self, seed, rows, cols, dense=False):
        parts = _build(seed, rows, cols, dense)
        program = _program(rows)
        out = program(parts)
        values, cov = dense_jcjt_oracle(list(parts), program)
        self.assertEqual(out.shape, (2,))
        self.assertEqual(out.dims, ("y",))
        for got, want in zip(out.values, values):
            self.assertAlmostEqual(got, want, delta=TOL)
        got_cov = out.covariance()
        for i in range(2):
            for j in range(2):
                self.assertAlmostEqual(got_cov[i][j], cov[i][j], delta=TOL)
        # Shared monitor and level keep the two rebinned rows correlated.
        self.assertGreater(abs(got_cov[0][1]), 0.0)

    def test_diagonal_fields_several_seeds_and_shapes(self):
        for seed, rows, cols in [(1, 3, 4), (7, 4, 5), (23, 3, 6),
                                 (99, 5, 4)]:
            with self.subTest(seed=seed, rows=rows, cols=cols):
                self.check(seed, rows, cols)

    def test_densely_correlated_field(self):
        self.check(5, 3, 4, dense=True)


if __name__ == "__main__":
    unittest.main()
