"""Independent verification of the frozen 100,000-event benchmark.

The frozen benchmark (``benchmark_100k_events``, 100,000 events into 128
bins) must stay under a one-gibibyte peak-memory budget and must do so by
streaming: it may not build a dense event-by-bin matrix (which alone would
take 100,000 x 128 x 8 bytes = 102.4 MB as float64).  Here the same scale
is reproduced with two independently seeded event streams through the
public ``reduce_events_to_bins`` path, and the explicit first-order-linear
rejects on that path are pinned.  Results are first-order (linearised)
propagations; discontinuous operations are not approximated, they are
rejected.
"""
import random
import sys
import time
import tracemalloc
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from covreduce import UnsupportedOperationError, source
from covreduce.events import benchmark_100k_events, reduce_events_to_bins

N_EVENTS = 100_000
N_BINS = 128
BUDGET_BYTES = 2 ** 30  # one gibibyte; do not loosen
DENSE_EVENT_MATRIX_BYTES = N_EVENTS * N_BINS * 8  # float64 event x bin
# Streaming state is O(bins x groups); anything near the dense-matrix size
# means the event stream was materialised.  16 MiB is >10x the observed
# peak and still >6x smaller than the dense matrix.
STREAMING_CEILING_BYTES = 16 * 2 ** 20
SEEDS = (1, 20261122)


def run_seeded_benchmark(seed, n_events=N_EVENTS, n_bins=N_BINS):
    """Reproduce the frozen benchmark scale with a seeded event stream."""
    rng = random.Random(seed)

    def stream():
        for _ in range(n_events):
            yield {"bin": rng.randrange(n_bins),
                   "weight": 1.0 + rng.random() * 0.07,
                   "variance": 0.25, "group": rng.randrange(4)}

    scales = {g: source(1.0 + 0.01 * g, 0.0004) for g in range(4)}
    monitor = source(1000.0, 25.0)
    background = source([0.5] * n_bins, [0.01] * n_bins, dims=("bin",))
    started = not tracemalloc.is_tracing()
    if started:
        tracemalloc.start()
    else:
        tracemalloc.reset_peak()
    try:
        start = time.perf_counter()
        result = reduce_events_to_bins(stream(), n_bins, group_scales=scales,
                                        monitor=monitor, background=background)
        elapsed = time.perf_counter() - start
        _, peak = tracemalloc.get_traced_memory()
    finally:
        if started:
            tracemalloc.stop()
    return {"seed": seed, "events": n_events, "bins": n_bins,
            "seconds": elapsed, "peak_bytes": peak,
            "values": result.values, "total_variance": sum(result.variance)}


class TestFrozenBenchmarkBudget(unittest.TestCase):
    def test_frozen_benchmark_under_budget(self):
        result = benchmark_100k_events()
        self.assertEqual(result["events"], N_EVENTS)
        self.assertEqual(result["bins"], N_BINS)
        self.assertLess(result["peak_bytes"], BUDGET_BYTES)
        self.assertLess(result["peak_bytes"], STREAMING_CEILING_BYTES)
        self.assertLess(STREAMING_CEILING_BYTES * 6,
                        DENSE_EVENT_MATRIX_BYTES)
        self.assertGreater(result["total_variance"], 0.0)

    def test_two_seeds_under_budget_and_reproducible(self):
        runs = {}
        for seed in SEEDS:
            with self.subTest(seed=seed):
                run = run_seeded_benchmark(seed)
                runs[seed] = run
                self.assertLess(run["peak_bytes"], BUDGET_BYTES)
                self.assertLess(run["peak_bytes"], STREAMING_CEILING_BYTES)
                self.assertEqual(len(run["values"]), N_BINS)
                self.assertGreater(run["total_variance"], 0.0)
        # Different seeds give different event assignments ...
        self.assertNotEqual(runs[SEEDS[0]]["values"], runs[SEEDS[1]]["values"])
        # ... but the same seed reproduces exactly in values, and in
        # total variance to 1e-12 (core Jacobian summation order over a
        # source set can move the last bit between processes).
        again = run_seeded_benchmark(SEEDS[0])
        self.assertEqual(again["values"], runs[SEEDS[0]]["values"])
        self.assertAlmostEqual(again["total_variance"],
                               runs[SEEDS[0]]["total_variance"], places=12)

    def test_small_seeded_stream_matches_manual_accumulation(self):
        rng = random.Random(7)
        events = [{"bin": rng.randrange(4),
                   "weight": 1.0 + rng.random(), "variance": 0.25}
                  for _ in range(200)]
        out = reduce_events_to_bins(iter(events), 4)
        for b in range(4):
            sel = [e for e in events if e["bin"] == b]
            self.assertAlmostEqual(out.values[b],
                                   sum(e["weight"] for e in sel), places=12)
            self.assertAlmostEqual(out.variance[b], 0.25 * len(sel),
                                   places=12)


class TestEventPathRejects(unittest.TestCase):
    def test_uncertain_bin_edges_rejected_explicitly(self):
        with self.assertRaises(UnsupportedOperationError) as caught:
            reduce_events_to_bins(iter([]), N_BINS,
                                  bin_edges=tuple(float(i) for i in range(129)))
        self.assertIn("first_order_linear", str(caught.exception))

    def test_discontinuous_operations_rejected_on_reduced_result(self):
        out = reduce_events_to_bins(iter([{"bin": 0, "weight": 2.0}]), 2)
        for attempt in (lambda: abs(out), lambda: out // 2,
                        lambda: out % 2, lambda: out.apply_discontinuous()):
            with self.assertRaises(UnsupportedOperationError):
                attempt()

    def test_out_of_range_bin_rejected(self):
        with self.assertRaises(IndexError):
            reduce_events_to_bins(iter([{"bin": N_BINS}]), N_BINS)


if __name__ == "__main__":
    unittest.main()

