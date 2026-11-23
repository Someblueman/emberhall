"""Scale evidence: sparse Jacobians vs dense covariance vs Monte Carlo.

A 40x50 (2000-element) field of counts shares one monitor and one
background level: a single scalar source subtracted from every bin, so
its uncertainty is fully correlated across the field.  The quantity of
interest is one downstream quadratic form
``w^T C w``.  covreduce contracts the sparse per-source Jacobians without
ever forming the 2000x2000 covariance; the dense route materialises it;
Monte Carlo estimates it from seeded draws.  Run directly:

    PYTHONPATH=projects/shared-noise-reduction-library \
        python3 -m covreduce.scale
"""
from __future__ import annotations

import random
import time
import tracemalloc

from .core import source

ROWS, COLS = 40, 50


def build_field(rows=ROWS, cols=COLS):
    n = rows * cols
    monitor = source(5000.0, 100.0)
    counts = source([[100.0 + (r * cols + c) % 37 for c in range(cols)]
                     for r in range(rows)],
                    [2.0 + (i % 5) * 0.1 for i in range(n)],
                    dims=("row", "col"))
    background = source(3.0, 0.05)  # one shared level for the whole field
    rates = counts / monitor - background / monitor
    weights = tuple(1.0 / n for _ in range(n))
    return monitor, counts, background, rates, weights


def _timed(fn):
    tracemalloc.start()
    start = time.perf_counter()
    value = fn()
    elapsed = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return value, elapsed, peak


def run_comparison(rows=ROWS, cols=COLS, draws=300, seed=7):
    monitor, counts, background, rates, weights = build_field(rows, cols)
    n = rows * cols
    sparse, sparse_s, sparse_b = _timed(lambda: rates.quadratic_form(weights))

    def dense():
        cov = rates.covariance()
        return sum(weights[i] * cov[i][j] * weights[j]
                   for i in range(n) for j in range(n))

    dense_v, dense_s, dense_b = _timed(dense)

    def monte_carlo():
        rng = random.Random(seed)
        mon_v, mon_sd = monitor.value, monitor.variance ** 0.5
        cnt_v = list(counts.values)
        cnt_sd = [v ** 0.5 for v in counts.variance]
        bkg_v, bkg_sd = background.value, background.variance ** 0.5
        vals = []
        for _ in range(draws):
            m = rng.gauss(mon_v, mon_sd)
            b = rng.gauss(bkg_v, bkg_sd)  # one shared draw for every bin
            vals.append(sum(w * ((c + rng.gauss(0, s)) / m - b / m)
                            for w, c, s in
                            zip(weights, cnt_v, cnt_sd)))
        mean = sum(vals) / draws
        return sum((v - mean) ** 2 for v in vals) / (draws - 1)

    mc_v, mc_s, mc_b = _timed(monte_carlo)
    return {
        "elements": n,
        "sparse": (sparse, sparse_s, sparse_b),
        "dense": (dense_v, dense_s, dense_b),
        "monte_carlo": (mc_v, mc_s, mc_b),
    }


def main(argv=None):
    result = run_comparison()
    print(f"scale comparison: {result['elements']} elements, one shared "
          f"monitor + background, quadratic form w^T C w")
    for name in ("sparse", "dense", "monte_carlo"):
        value, seconds, peak = result[name]
        print(f"  {name:12s} value {value:.6e}  {seconds:7.3f}s  "
              f"peak {peak / 1e6:8.2f} MB")
    sparse, dense = result["sparse"][0], result["dense"][0]
    print(f"  sparse vs dense relative difference: "
          f"{abs(sparse - dense) / dense:.3e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
