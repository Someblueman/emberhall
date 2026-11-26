# Independent-input pilot: recorded run

Rook, 26 November 2026. This is bounded progress on the first milestone,
not a replication of the paper’s figures or a completed scientific result.

Command (repository root):

```
python3 projects/when-nutrients-arrive-together/reference.py --output /tmp/nutrient-reference
```

NumPy 2.4.6, SciPy 1.18.0. Four communities (seeds 0–3); none failed.
Retained duration 1024, sampling interval 1, after burn-in 512.

| Metric | Overlap rank correlation, mean | Pair diet AUC, mean | Cluster guild AUC, mean |
|---|---:|---:|---:|
| correlation | 0.5731 | 0.9213 | 0.8750 |
| absolute_correlation | 0.5273 | 0.8426 | 0.8611 |
| cpsd | 0.6786 | 0.9722 | 1.0000 |
| coherence | 0.9184 | 1.0000 | 1.0000 |

Full community-level Student-t intervals are regenerated in `report.json`.
Four communities cannot establish a population recovery rate. In particular,
an interval of zero width after four perfect scores does not establish
certainty; the unbounded linear intervals are not clipped to the score range.

Maximum solver trajectory RMS in log abundance: 1.96e-06.
Solver refinement changed none of the rank or classification scores.
Maximum forcing-grid trajectory RMS: 0.000755.
Maximum forcing-grid score change: 0.2778.
This is a witnessed forcing-resolution sensitivity, not a passed convergence gate.

Largest half-window mean shift divided by whole-window deviation: 0.568.
Half-window variance ratios span 0.670–1.508.
These diagnostics do not establish stationarity.

The local-linear check independently integrates the transfer spectrum and
solves the augmented continuous Lyapunov equation. The worst relative
covariance discrepancy across the four equilibria is 2.65e-13.
This tests the pilot algebra, not the nonlinear simulation’s long-run law.

Nine checks pass: exact resource solution, equilibrium balance, independent
OU stationary law, AUC controls, delayed-signal spectral control, private
resource isolation, nonlinear Jacobian, covariance integration, and independent
threshold-by-threshold verification of single-linkage connections.

The source paper was opened and read. The supplement endpoint failed in the
built-in reader; the linked [author archive](https://osf.io/hvnjt/) returned 403,
and its public metadata endpoint was inaccessible. No shell networking,
new account, credential, or downloaded code was used. Exact source supply
and initialization choices remain unresolved; [MODEL.md](MODEL.md) lists
our choices explicitly.

Next: audit source parameters when those pages are readable, tighten forcing
resolution and record length, quantify uncertainty across more communities,
and freeze the clean protocol before correlated-input testing. Preserve the
distinction between overlap, pair labels and clustering throughout.
