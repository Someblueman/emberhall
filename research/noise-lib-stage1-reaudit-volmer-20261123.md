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

## Stage 1 gate: met in this room, pending publication

Follow-up task `noise-lib-stage1-baselines-scale-recheck` (same run) redid
the two pieces lost with terminal f127, deriving values independently:

- Baselines: new `tests/test_baselines.py` (7 tests) with hand-written
  J C J^T expectations: shared-monitor covariance [[1.4e-3, 2e-4], [2e-4,
  6e-4]]; gvar-equivalent 0.92; ESSreduce bound exactly 8.0 covering true
  4.0; RME ellipse areas pi*sqrt(1.75) vs pi*sqrt(2); seeded Monte Carlo
  within tolerance of the hand values.
- Scale: `build_field`'s background was 2000 independent diagonal bins while
  the docstring claimed one shared background. It is now one scalar level
  (3.0, var 0.05) subtracted from every bin, Monte Carlo draws it once per
  draw, and a test pins the hand-computed 2x2 quadratic form 2.505236e-08
  (background variance enters whole, not divided by bin count). Full field:
  sparse 4.159356e-09 in 4.0s/0.16 MB vs dense equal to 2.1e-14 relative in
  21.3s/128 MB; Monte Carlo 3.81e-09 (300 draws).

Full suite: 38 tests OK; `run_demo.py` OK. Remaining before the gate is
recorded: a non-author publishes room commits e3950f0 + this follow-up, then
the Stage 1 gate can be called met on shared source.
