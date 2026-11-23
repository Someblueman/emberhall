# Milestone 1 evidence — shared-noise reduction library

One page mapping the milestone's clauses to what delivers each and
what a fresh run measured (this machine, run `cd3570a8`; refreshed
from run `a4efaa8f`, whose four restored oracle verification modules
were rebased onto the current tree in run `641cb672` after the first
publish conflicted. Numbers not re-measured are marked as earlier
records).

| clause | delivered by | measured |
|---|---|---|
| Importable Python package | `pyproject.toml` (PEP 621, dynamic version), `covreduce/` | `tests/test_packaging.py` performs a real pip temp-target install and imports from a neutral directory; `python -m covreduce` and the `covreduce` console script both run from the install |
| First-order covariance operator contract | `CONTRACT.md`; enforcement in `covreduce/core.py` | `abs`, `//`, `%`, discontinuous ops and uncertain bin edges raise explicitly; covariance sums use a fixed source order, so results are bit-identical across processes (`tests/test_determinism.py`) |
| Dense J C J^T oracle check | `covreduce/oracle.py` (independent dual arrays, primitives only) | `python -m covreduce`: oracle parity max \|cov diff\| 8.470e-22; randomised 1-D compositions and `tests/test_oracle_2d.py` 2-D compositions to 1e-9; restored `tests/test_contract_oracle.py` (64 seeded random compositions + identity laws) and `tests/test_events_oracle.py` (seeded event streams vs hand-written dense oracle) — freshly passing in the rebased tree |
| Monte Carlo baseline | `covreduce/baselines.monte_carlo_covariance`; `tests/test_events_monte_carlo.py` | Canonical fit: covreduce σ 0.002207 vs Monte Carlo σ 0.002204 (6000 seeded draws); event pipeline agrees with direct nonlinear sampling within six-sigma Monte Carlo error |
| gvar-equivalent baseline | `covreduce/baselines.gvar_equivalent_variance` (dense graph, implemented locally — not the external gvar package) | Fit variance 4.873e-06, equal to covreduce's 0.002207² |
| ESSreduce upper bound | `covreduce/baselines.essreduce_upper_bound` (style only, bound only) | variance ≤ 1.249e-05, covering the exact 4.873e-06 |
| RME-style ellipse | `covreduce/baselines.rme_ellipse_attribution` (local, hand-checked; not `rmellipse`) | Ellipse area 3.400e-05 vs independent 3.430e-05, correlation 0.134 on the canonical pair |
| Fixed-bin monitor + shared background | `covreduce/cli.py` importing program; `covreduce/events.py` streaming reduction | Rates [0.115, 0.075, 0.04]; keeping shared sources gives σ 0.002207 where wrongly splitting them gives 0.002087; 100,000 events → 128 bins in 2.17 s, 651,584 B peak |
| Scale benefit | `covreduce/scale.py`, sparse `quadratic_form` | Earlier record (README, run `5ee0e5bf`, superseding `aa00d9dc`): on 2,000 elements sparse and dense agree to 5.2e-14 relative, 0.16 MB vs 128.38 MB peak; restored `tests/test_scale_verify.py` pins the same claim at 600 elements and `tests/test_benchmark_verify.py` pins the 100k-event streaming budget — both freshly passing in the rebased tree; the 2,000-element table itself was not re-measured |

Full suite freshly measured in the rebased tree (run `641cb672`):
80 tests, all passing in 12.3 s (61 on the current tree, plus 19 in
the four restored modules), the wheel builds offline, and both
importing programs pass via `run_all_demos.py`.

## What remains for the milestone judgment

The milestone's stop clause — one week without an importing program
giving a concrete composition or scale benefit — is a judgment for
the house, not a number above. The concrete benefit on record is
composition with shared-source cross terms kept (the wrongly-split
baseline understates σ by ~5% on the canonical fit) and the sparse
quadratic form's memory advantage. Whether that earns milestone 2,
and what external program should import this next, is the open
question this page deliberately does not answer. It is due before
the milestone deadline, 2026-11-29.
