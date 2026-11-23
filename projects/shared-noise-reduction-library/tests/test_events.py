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

    def test_benchmark_shape(self):
        result = benchmark_100k_events(n_events=2000, n_bins=8)
        self.assertEqual(result["events"], 2000)
        self.assertGreater(result["peak_bytes"], 0)
        self.assertGreater(result["total_variance"], 0.0)


if __name__ == "__main__":
    unittest.main()
