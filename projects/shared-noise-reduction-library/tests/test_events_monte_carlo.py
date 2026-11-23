"""Event reduction checked by sampling the nonlinear model directly.

The deterministic J C J^T event checks share the library's
linearisation, so a wrong tangent could in principle agree with
itself.  Here each Monte Carlo trial redraws per-event weight noise,
the shared group scales, the monitor and the background, rebins the
events by hand, and the empirical mean and covariance are compared
with the first-order result.  Relative differences at 30k draws are a
few per cent (Monte Carlo error plus a small linearisation error);
a missing shared term would move cross-bin entries by far more.
"""
import math
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from covreduce import source  # noqa: E402
from covreduce.events import reduce_events_to_bins  # noqa: E402

FLOOR = 2e-6


def _case(rng, n_bins, n_events, groups):
    scale_values = {g: rng.uniform(0.9, 1.15) for g in groups}
    scale_vars = {g: rng.uniform(0.001, 0.003) for g in groups}
    monitor_value = rng.uniform(150.0, 250.0)
    monitor_var = rng.uniform(9.0, 25.0)
    bg_values = [rng.uniform(0.0, 0.04) for _ in range(n_bins)]
    bg_vars = [rng.uniform(0.0001, 0.001) for _ in range(n_bins)]
    events = [{"bin": rng.randrange(n_bins),
               "weight": rng.uniform(2.0, 6.0),
               "variance": rng.uniform(0.2, 1.0),
               "group": rng.choice(groups)}
              for _ in range(n_events)]
    out = reduce_events_to_bins(
        iter(events), n_bins,
        group_scales={g: source(scale_values[g], scale_vars[g])
                      for g in groups},
        monitor=source(monitor_value, monitor_var),
        background=source(bg_values, bg_vars, dims=("bin",)))
    return (events, scale_values, scale_vars, monitor_value,
            monitor_var, bg_values, bg_vars, out)


def _sample(rng, case, n_bins, draws):
    (events, scale_values, scale_vars, monitor_value, monitor_var,
     bg_values, bg_vars, _) = case
    samples = [[0.0] * draws for _ in range(n_bins)]
    for d in range(draws):
        scales = {g: rng.gauss(v, math.sqrt(scale_vars[g]))
                  for g, v in scale_values.items()}
        monitor = rng.gauss(monitor_value, math.sqrt(monitor_var))
        background = [rng.gauss(v, math.sqrt(var))
                      for v, var in zip(bg_values, bg_vars)]
        totals = [0.0] * n_bins
        for event in events:
            noise = rng.gauss(0.0, math.sqrt(event["variance"]))
            totals[event["bin"]] += scales[event["group"]] * (
                event["weight"] + noise)
        for i in range(n_bins):
            samples[i][d] = totals[i] / monitor - background[i]
    return samples


def _mean(xs):
    return sum(xs) / len(xs)


def _cov(xs, ys):
    mx, my = _mean(xs), _mean(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / len(xs)


class TestEventsMonteCarlo(unittest.TestCase):
    def check(self, seed, n_bins, n_events, draws):
        rng = random.Random(seed)
        case = _case(rng, n_bins, n_events, ["a", "b"])
        out = case[-1]
        samples = _sample(rng, case, n_bins, draws)
        exact = out.covariance()
        for i in range(n_bins):
            self.assertAlmostEqual(_mean(samples[i]), out.values[i],
                                   delta=0.01 + 0.02 * abs(out.values[i]))
            for j in range(n_bins):
                got = _cov(samples[i], samples[j])
                # Six-sigma Monte Carlo standard error for a Gaussian
                # covariance estimate, plus 3% for the linearisation.
                tol = 6.0 * math.sqrt(
                    (exact[i][i] * exact[j][j] + exact[i][j] ** 2)
                    / draws) + 0.03 * abs(exact[i][j]) + FLOOR
                self.assertLessEqual(abs(got - exact[i][j]), tol,
                                     (i, j, got, exact[i][j]))
        # Shared scales and monitor make cross-bin terms genuinely
        # positive, so the comparison above cannot pass trivially.
        self.assertTrue(any(exact[i][j] > FLOOR
                            for i in range(n_bins)
                            for j in range(n_bins) if i != j))

    def test_three_bins_shared_scales(self):
        self.check(seed=42, n_bins=3, n_events=36, draws=30000)

    def test_four_bins_second_seed(self):
        self.check(seed=7, n_bins=4, n_events=48, draws=20000)


if __name__ == "__main__":
    unittest.main()
