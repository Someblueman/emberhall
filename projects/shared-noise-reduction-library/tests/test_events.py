import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from covreduce import UnsupportedOperationError, source
from covreduce.events import benchmark_100k_events, reduce_events_to_bins


class TestEvents(unittest.TestCase):
    def test_plain_binning_values_and_variance(self):
        events = [{"bin": 0, "weight": 2.0, "variance": 0.5},
                  {"bin": 0, "weight": 1.0, "variance": 0.25},
                  {"bin": 1, "weight": 3.0, "variance": 1.0}]
        out = reduce_events_to_bins(iter(events), 2)
        self.assertEqual(out.values, (3.0, 3.0))
        self.assertEqual(out.variance, [0.75, 1.0])

    def test_shared_group_scale_correlates_bins(self):
        scale = source(2.0, 0.04)
        events = [{"bin": 0, "weight": 1.0, "group": "g"},
                  {"bin": 1, "weight": 1.0, "group": "g"}]
        out = reduce_events_to_bins(iter(events), 2,
                                    group_scales={"g": scale})
        self.assertEqual(out.values, (2.0, 2.0))
        self.assertAlmostEqual(out.covariance()[0][1], 0.04, places=12)
        # Same shared scale cancels in the difference.
        self.assertAlmostEqual((out[0] - out[1]).variance, 0.0, places=12)

    def test_monitor_and_background(self):
        monitor = source(10.0, 1.0)
        background = source([1.0, 1.0], [0.1, 0.1], dims=("bin",),
                            coords={"bin": (0.5, 1.5)})
        events = [{"bin": 0, "weight": 100.0}, {"bin": 1, "weight": 50.0}]
        out = reduce_events_to_bins(iter(events), 2, monitor=monitor,
                                    background=background)
        self.assertEqual(out.values, (9.0, 4.0))

    def test_uncertain_bin_edges_rejected(self):
        with self.assertRaises(UnsupportedOperationError):
            reduce_events_to_bins(iter([]), 2, bin_edges=(0.0, 1.0, 2.0))

    def test_event_bin_must_be_exact_integer(self):
        for bad in (0.9, False, "0"):
            with self.subTest(bin=bad):
                with self.assertRaises(TypeError):
                    reduce_events_to_bins(iter([{"bin": bad}]), 2)
        out = reduce_events_to_bins(iter([{"bin": 0}]), 2)
        self.assertEqual(out.values, (1.0, 0.0))

    def test_benchmark_shape(self):
        result = benchmark_100k_events(n_events=2000, n_bins=8)
        self.assertEqual(result["events"], 2000)
        self.assertGreater(result["peak_bytes"], 0)
        self.assertGreater(result["total_variance"], 0.0)

    def test_frozen_benchmark_under_one_gib_and_flat_in_events(self):
        # Milestone 3 frozen scale: 100,000 events, 128 bins, < 1 GiB,
        # and peak memory must not grow with event count (streaming,
        # no dense event matrix). Slack is generous to avoid flakes;
        # observed peaks are ~0.65 MB at both scales.
        small = benchmark_100k_events(n_events=10_000, n_bins=128)
        frozen = benchmark_100k_events()
        self.assertEqual(frozen["events"], 100_000)
        self.assertEqual(frozen["bins"], 128)
        self.assertLess(frozen["peak_bytes"], 1024 ** 3)
        self.assertLessEqual(
            frozen["peak_bytes"],
            max(2 * small["peak_bytes"], small["peak_bytes"] + 5_000_000))


if __name__ == "__main__":
    unittest.main()
