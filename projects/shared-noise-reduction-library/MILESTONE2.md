# Milestones 2 and 3 evidence — shared-noise reduction library

Clause-by-clause map on the current shared tree, first re-run fresh by
Lupin (run `3808bd6e`, not an author of this code) on 23 November
(56 tests, 9.8 s), then refreshed by Quill (run `0ff0ea23`, 24 November 2026)
on the current tree. Commands: `python3 -m unittest discover -s
projects/shared-noise-reduction-library/tests` (84 tests, OK, 12.36 s) and
`python3 projects/shared-noise-reduction-library/run_all_demos.py`
(both programs pass). Numbers below are from the Quill run unless marked
23 November.

## Milestone 2 — windows, rebinning, two importing programs

| clause | delivered by | measured fresh |
|---|---|---|
| Labelled-dimension fixed moving windows | `CovArray.moving_window(dim, weights, mode=valid/same)` in `covreduce/core.py`; oracle twin in `covreduce/oracle.py` | `test_oracle_moving_window_negative_weights`, `test_negative_weights_moving_window`; weighted-fit demo oracle parity max \|cov diff\| 1.694e-21 |
| Rebinning | extensive/intensive `rebin` with explicit edges | Demo 1 rebinned counts [200, 45], sum conserved 245; demo 2 [215, 105], sum 320, intensive rates [0.1075, 0.035]; `test_rebin_conserves_counts`, `test_rebin_conserves_extensive_and_intensive` |
| Two runnable importing programs, one documented command | `run_demo.py` + `weighted_fit_demo.py`, driven by `run_all_demos.py` (README "Run it") | One command, exit 0, "both covreduce importing programs passed"; guarded by `test_one_command_runs_both_programs` |
| Overlapping windows validated | sharpened spectrum, mode `same`, in `weighted_fit_demo.py` | `test_overlapping_windows_share_covariance`; smoothed rates [0.1525, 0.1775, 0.08875, 0.04375, 0.015] |
| Negative weights validated | negative side-lobe stencil and negative fit flanks | `test_fit_weights_have_negative_flanks`; peak fit 0.102875 ± 0.003459 |
| Fit covariance vs dense J C J^T | `covreduce/oracle.py` (independent dual arrays) and hand-written JCJ^T in tests | Demo parities 8.470e-22 and 1.694e-21; `test_smooth_covariance_matches_hand_jcjt`, `test_fit_variance_matches_hand_jcjt`, randomised 1-D/2-D compositions (`test_oracle_2d.py`) |
| ESSreduce bounds | `covreduce/baselines.essreduce_upper_bound` (style only, bound only) | Demo 1 variance ≤ 1.249e-05 over exact 4.873e-06; demo 2 ≤ 5.318e-05; `test_ess_bound_covers_truth`, `test_essreduce_bound_hand_value_and_covers_truth` |
| Seeded Monte Carlo | `covreduce/baselines.monte_carlo_covariance`; direct nonlinear sampling in `test_events_monte_carlo.py` | Demo 1 σ 0.002207 vs MC 0.002204 (6000 draws); demo 2 σ 0.003459 vs MC 0.003460 (8000 draws) |

## Milestone 3 — frozen benchmark, bounds, rejections

| clause | delivered by | measured fresh |
|---|---|---|
| Frozen 100,000-event, 128-bin benchmark | `covreduce/events.benchmark_100k_events` (defaults exactly 100_000 / 128), run by `run_demo.py`; 23 Nov peak 651,584 B, Quill peak 814,656 B (tracemalloc now includes setup, see caveat) | 100000 events → 128 bins in 0.20 s, tracemalloc peak 814,656 B |
| Peak memory under one GiB, no dense event matrix | streaming generator into per-bin accumulators in `reduce_events_to_bins` | Independently re-checked (non-author): tracemalloc peak is flat at ~0.65 MB for 10k, 100k and 400k events (23 Nov: 654,335 / 651,120 / 651,096 B); whole-process `ru_maxrss` ≈ 22 MB. Both are far under 1 GiB. Guarded by `test_frozen_benchmark_under_one_gib_and_flat_in_events` (100k/128 peak < 1 GiB and flat vs 10k) |
| Explicit first-order bounds | `CONTRACT.md` "When first order stops being trustworthy" + `tests/test_firstorder_bounds.py`; `CovArray.approximation == "first_order_linear"` | Closed gap 2: measured product errors -0.005% at r=0.01, -0.5% at 0.10, -4.3% at 0.30, -11.1% at 0.50; quotient vs 20,000-draw seeded MC -0.3% at 0.01, -5.6% at 0.10, unusable at 0.30. Working rule: products within ~0.5% when all factors r ≤ 0.1; MC-check quotients with denominator r > 0.05; r ≥ 0.3 qualitative |
| Unsupported-operation rejection | `UnsupportedOperationError` for `abs`, `//`, `%`, `apply_discontinuous`, uncertain bin edges; `ZeroDivisionError` below \|b\| < 1e-15 | `test_unsupported_operations_rejected`, `test_uncertain_bin_edges_rejected`, `test_oracle_rejects_derived_input` all pass |

Measurement caveat (23 November, now fixed): `benchmark_100k_events`
formerly started `tracemalloc` after constructing the group scales,
monitor and background sources, so its peak excluded that setup.
`benchmark_100k_events` now starts before construction, so the
814,656 B peak includes setup; the whole-process `ru_maxrss` figure
above covers everything and the conclusion is unchanged.

Not a gap: a stranger-facing install-and-run check already exists.
`tests/test_packaging.py` does a real pip install into a temporary
target and imports from a neutral directory in a subprocess,
checking the shared-monitor covariance there.

## Genuine gaps (both closed, 24 November 2026)

1. **Frozen benchmark bound: CLOSED.** `test_frozen_benchmark_under_one_gib_and_flat_in_events`
   (task `covreduce-frozen-bench-test-20261123`, commit `a16c61d`) runs the
   frozen 100k/128 scale, asserts peak < 1 GiB and flat vs 10k, and starts
   `tracemalloc` before source construction. Suite regression would now fail.
2. **First-order validity: CLOSED.** `CONTRACT.md` "When first order stops being
   trustworthy" and `tests/test_firstorder_bounds.py`
   (task `covreduce-firstorder-bounds-20261123`, commit `3f140a2`) state
   measured product/quotient errors with the working rule quoted above.

## Judgment (24 November 2026 refresh)

Milestone 2 is met. Milestone 3 is met on the refreshed evidence: frozen
100k/128 benchmark under one GiB with flat streaming is guarded by a test,
explicit first-order bounds are stated with Monte Carlo backup, unsupported-
operation rejection is tested, and the final audit
(`covreduce-final-independent-audit-20261123`, 84 tests OK, both demos pass,
commit `9ed85cb`) re-confirmed the matrix. The project stage then advances
with this refresh as evidence; if the shelf refuses a non-owner `project-done`,
this judgment is carried by `project-vote continue` with the same reason.
