"""Hand-derived dense ``J C J^T`` for random event streams.

For each seeded stream the test accumulates, in plain Python, the
per-bin totals at the group scales' central values, the independent
per-bin variances, and each group's weight form.  The reduced output is

    out_i = (T_i + sum_g F_gi * (s_g - s_g0)) / m - b_i

with primitive components (T, s, m, b) independent between blocks, so

    d out_i/dT_j    = delta_ij / m0
    d out_i/ds_g    = F_gi / m0
    d out_i/dm      = -T_i / m0^2       (delta term vanishes centrally)
    d out_i/db_j    = -delta_ij

Expected covariance is the dense product of that Jacobian with the
block-diagonal primitive covariance, computed with explicit loops here —
no library or oracle code is used for the expectation.
"""
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from covreduce import source
from covreduce.events import reduce_events_to_bins


def hand_expectation(events, n_bins, groups, scale_val, scale_var,
                     monitor_val, monitor_var, bg_val, bg_var):
    totals = [0.0] * n_bins
    variances = [0.0] * n_bins
    forms = {g: [0.0] * n_bins for g in groups}
    for e in events:
        idx, w, v = e["bin"], e.get("weight", 1.0), e.get("variance", 0.0)
        g = e.get("group")
        s = scale_val[g] if g is not None else 1.0
        if g is not None:
            forms[g][idx] += w
        totals[idx] += s * w
        variances[idx] += s * s * v
    values = [totals[i] / monitor_val - bg_val[i] for i in range(n_bins)]
    # Primitive order: T (n), scales (G), monitor (1), background (n).
    prim_var = (variances + [scale_var[g] for g in groups]
                + [monitor_var] + list(bg_var))
    jac = []
    for i in range(n_bins):
        row = [0.0] * len(prim_var)
        row[i] = 1.0 / monitor_val
        for gi, g in enumerate(groups):
            row[n_bins + gi] = forms[g][i] / monitor_val
        row[n_bins + len(groups)] = -totals[i] / monitor_val ** 2
        row[n_bins + len(groups) + 1 + i] = -1.0
        jac.append(row)
    cov = [[sum(jac[i][k] * prim_var[k] * jac[j][k]
                for k in range(len(prim_var)))
            for j in range(n_bins)] for i in range(n_bins)]
    return values, cov


class TestEventsManualJCJT(unittest.TestCase):
    def run_case(self, seed, n_events, n_bins, n_groups, grouped=True):
        rng = random.Random(seed)
        groups = list(range(n_groups))
        events = []
        for _ in range(n_events):
            e = {"bin": rng.randrange(n_bins),
                 "weight": rng.uniform(0.5, 2.0),
                 "variance": rng.uniform(0.0, 0.5)}
            if grouped:
                e["group"] = rng.randrange(n_groups)
            events.append(e)
        scale_val = {g: rng.uniform(0.8, 1.4) for g in groups}
        scale_var = {g: rng.uniform(0.0001, 0.01) for g in groups}
        monitor_val, monitor_var = rng.uniform(80.0, 120.0), rng.uniform(1, 9)
        bg_val = [rng.uniform(0.0, 1.0) for _ in range(n_bins)]
        bg_var = [rng.uniform(0.001, 0.05) for _ in range(n_bins)]
        out = reduce_events_to_bins(
            iter(events), n_bins,
            group_scales={g: source(scale_val[g], scale_var[g])
                          for g in groups} if grouped else None,
            monitor=source(monitor_val, monitor_var),
            background=source(bg_val, bg_var, dims=("bin",)))
        want_val, want_cov = hand_expectation(
            events, n_bins, groups if grouped else [],
            scale_val, scale_var, monitor_val, monitor_var, bg_val, bg_var)
        for i in range(n_bins):
            self.assertAlmostEqual(out.values[i], want_val[i], places=9)
            for j in range(n_bins):
                self.assertAlmostEqual(out.covariance()[i][j], want_cov[i][j],
                                       places=9)

    def test_seeded_streams_match_hand_jcjt(self):
        for seed, n_events, n_bins, n_groups in [
                (11, 60, 3, 2), (22, 120, 4, 3), (33, 200, 5, 2),
                (44, 80, 4, 4), (55, 150, 6, 3)]:
            with self.subTest(seed=seed):
                self.run_case(seed, n_events, n_bins, n_groups)

    def test_ungrouped_stream_matches_hand_jcjt(self):
        self.run_case(66, 100, 4, 1, grouped=False)

    def test_shared_scale_and_monitor_make_cross_terms(self):
        rng = random.Random(77)
        events = [{"bin": rng.randrange(3), "weight": 1.0,
                   "variance": 0.1, "group": 0} for _ in range(90)]
        out = reduce_events_to_bins(
            iter(events), 3,
            group_scales={0: source(1.2, 0.04)},
            monitor=source(100.0, 4.0),
            background=source([0.5] * 3, [0.01] * 3, dims=("bin",)))
        cov = out.covariance()
        for i in range(3):
            for j in range(3):
                if i != j:
                    self.assertGreater(cov[i][j], 0.0)


if __name__ == "__main__":
    unittest.main()

