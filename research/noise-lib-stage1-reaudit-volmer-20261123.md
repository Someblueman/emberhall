# Stage 1 covreduce re-audit after repair (Volmer, 2026-11-23)

Task `noise-lib-stage1-publish-reaudit`. Contribution f127922a (9d0ac9de) was
reviewed acceptable but its publish conflicted (seq 33607/33615): aa00d9dc was
already merged (8123eb5) with the old `if n <= 64` PSD guard, so f127's fixes
never reached shared source. This run re-applied the two fixes onto 5f000b7.

## Fixes re-applied (`covreduce/core.py` only)

1. Dense PSD at every size: replaced `if n <= 64 and not _cholesky_psd(...)`
   with a Cholesky check whenever any off-diagonal entry is nonzero.
   Diagonal-only matrices keep the existing diagonal check, so large diagonal
   sources avoid O(n^3).
2. Booleans are not numbers: new `_real()` helper rejects `bool` with
   `TypeError`; used for values, covariance entries (scalar, rows, flat),
   scalar constants, weights, centres and bin edges.

Regression tests added to `tests/test_covreduce.py`:
`test_large_dense_non_psd_rejected` (65x65, off-diag 2.0),
`test_large_diagonal_covariance_accepted` (n=200),
`test_booleans_are_not_numbers` (values, scalar covariance, entries).

## Evidence (this room, repaired source)

- Probe before fix: 65x65 non-PSD accepted; bool accepted in all three spots.
  After fix: all rejected (`ValueError` PSD, `TypeError` bool); sanity
  variance `[1.0, 2.0]` and n=200 diagonal unchanged.
- `python3 -m unittest discover -s tests`: 30 tests OK (6.6s).
- `python3 run_demo.py`: passes; gvar-equiv 4.873e-06, rebin sum conserved.
- Independent re-audit probe (not the package oracle): hand dense
  Var(x0+x1)=5.4 exact; Var(x-x)=0; Monte Carlo (40,000 seeded draws) of
  counts/monitor matches package covariance to <0.5% on all 4 entries
  (e.g. cov[0][1] 2.000e-4 vs MC 1.964e-4). REAUDIT PASS.

## Stage 1 gate: not yet fully re-certified

Two pieces finished only inside the now-terminal f127 contribution and are
absent from merged source; they were not reconstructed from truncated
summaries: (a) Vesper's baselines hand-check tests (`tests/test_baselines.py`,
finish 33568); (b) the scale contract discrepancy fix in `covreduce/scale.py`
(finish 33565). Current merged `build_field` uses one background source with
diagonal covariance; whether that matches the README's "shared background"
claim in Vesper's sense needs a fresh bounded check. Recommend one short
follow-up task for (a)+(b) before recording the Stage 1 gate as met.
