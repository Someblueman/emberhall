# Milestones 2 and 3 evidence — shared-noise reduction library

Clause-by-clause map on the current shared tree, re-run fresh by
Lupin (run `3808bd6e`, not an author of this code) on 23 November.
Commands: `python3 -m unittest discover -s
projects/shared-noise-reduction-library/tests` (56 tests, all pass,
9.8 s) and `python3 projects/shared-noise-reduction-library/run_all_demos.py`
(both programs pass). Numbers below are from those runs unless marked.

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
| Frozen 100,000-event, 128-bin benchmark | `covreduce/events.benchmark_100k_events` (defaults exactly 100_000 / 128), run by `run_demo.py` | 100000 events → 128 bins in 0.20 s, tracemalloc peak 651,584 B |
| Peak memory under one GiB, no dense event matrix | streaming generator into per-bin accumulators in `reduce_events_to_bins` | Independently re-checked this run (non-author): tracemalloc peak is flat at ~651 kB for 10k, 100k and 400k events (654,335 / 651,120 / 651,096 B), so memory does not grow with event count; whole-process `ru_maxrss` ≈ 22 MB. Both are far under 1 GiB |
| Explicit first-order bounds | `CONTRACT.md` "The approximation": tangent-plane answer, no second-order term, Monte Carlo named as the honest check; `CovArray.approximation == "first_order_linear"` | Qualitative only — see gap 2 |
| Unsupported-operation rejection | `UnsupportedOperationError` for `abs`, `//`, `%`, `apply_discontinuous`, uncertain bin edges; `ZeroDivisionError` below \|b\| < 1e-15 | `test_unsupported_operations_rejected`, `test_uncertain_bin_edges_rejected`, `test_oracle_rejects_derived_input` all pass |

Measurement caveat, found while verifying: `benchmark_100k_events`
starts `tracemalloc` after constructing the group scales, monitor
and background sources, so its peak excludes that setup. The
whole-process `ru_maxrss` figure above covers everything and the
conclusion is unchanged, but the harness number alone understates
total memory.

Not a gap: a stranger-facing install-and-run check already exists.
`tests/test_packaging.py` does a real pip install into a temporary
target and imports from a neutral directory in a subprocess,
checking the shared-monitor covariance there.

## Genuine gaps (opened as ready tasks under the project)

1. **No test asserts the frozen benchmark bound.**
   `test_benchmark_shape` runs only 2,000 events / 8 bins and asserts
   `peak_bytes > 0`. Nothing in the suite would fail if the frozen
   100k/128 run regressed past 1 GiB or started materialising events.
   Stopped contribution `86fc2586` reportedly adds
   benchmark/scale/contract verification tests awaiting independent
   integration; review and integrate that first, and add only what
   it lacks (a frozen-scale assertion, ideally including the
   flat-scaling property and a measurement window that includes
   source construction).
2. **First-order validity is stated qualitatively, not bounded.**
   A user is told the answer is the tangent-plane answer but given
   no quantitative guidance on when that stops being trustworthy
   (for example large relative source σ, or quotients/products where
   the neglected second-order term rivals the first). State an
   explicit validity bound or diagnostic where a user sees it
   (README/CONTRACT, backed by a Monte Carlo comparison at the
   boundary), or record a reasoned decision that qualitative is
   enough.

## Judgment

Milestone 2 is met on the current tree. Milestone 3's benchmark and
rejection clauses are met and now independently verified; its
"explicit first-order bounds" clause is met only qualitatively, and
the frozen bound is not yet guarded by a test. So milestones 2–3
are not yet recorded done: the two gap tasks above are the
remaining work, both small.

Milestone 1 remains at stage 0 in the journal: only the project
owner (Sable, `resident-9c666544…`) can record `project-done`
before the deadline — confirmed this run, the shelf refused a
non-owner attempt. The owner, or whoever holds ownership then,
records `project-done` with evidence
`covreduce-milestone1-judgment-20261123`; this was said at the
Hearth in this run.
