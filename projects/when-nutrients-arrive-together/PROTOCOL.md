# Clean reference and held-out contract, version 1

Sorrel, 26 November 2026. Frozen before inspecting this study's scores.
The executable writes its exact configuration, numerical-library versions and
code hashes before its first solve. This contract extends the reconstructed
model in MODEL.md; it does not turn unresolved source conventions into facts.

## Work sequence and acceptance

1. Audit the readable source, retaining access failures and unresolved choices.
2. Run twelve new independent communities (4–15), with independent supply seeds
   20004–20015; no selection by score. Retain 4096 unit-spaced observations after
   512 units of burn-in. Each finest stationary OU path is generated once on a
   1/16 mesh; nested subsamples provide 1/8 and 1/4 meshes. This coupling isolates
   interpolation resolution. Rerunning `reference.py` with another mesh changes
   its random path and is not a paired refinement of an earlier run.
3. Solve every mesh with relative tolerance 1e-8 and maximum step equal to the
   mesh. Repeat the finest supply at tolerance 1e-10 and maximum step 1/32.
   Use the same initial conditions, supply endpoints and observation times.
4. Report overlap rank, pair-label AUC and single-linkage guild AUC separately
   for all four measures. Welch segment 30 is primary; 16 and 60 are sensitivity
   analyses, never selected by the observed outcome. Compare the first retained
   2048 observations with all 4096, plus report second-half scores. This is a
   nested record-length diagnostic, not an independent replicate.
5. Retain every failure. Across successful *communities*, report Student-t
   intervals and distribution-free marginal Hoeffding intervals using known
   score ranges. Neither pairs nor temporal halves increase the replicate count.
   A failed community makes success-only summaries conditional. A perfect sample
   never warrants population certainty; Student-t intervals alone can collapse.
6. Prespecified empirical gates: every finest solver score change <=0.005;
   every 1/8-to-1/16 forcing change <=0.05 in overlap rank and <=0.03 in either
   AUC; every half-to-full record change <=0.10 in overlap and <=0.05 in AUC.
   For precision require both reported marginal intervals' half-widths <=0.10
   for every primary measure and target. These are scientific working tolerances,
   not source-paper tolerances, rigorous continuum error estimates, or a
   guarantee on unseen communities. Twelve communities may fail precision.

Half-window mean shifts (in whole-window standard deviations) and variance
ratios are descriptive stationarity warnings. No single cutoff certifies
stationarity. Compare relaxation times from the independently checked local
linear model and extend burn/record lengths when warranted; nonlinear
stationarity still requires independent scientific review. The one-run input
per community estimates joint community/path variation, not their separate
variance components. More paths within communities must remain nested for
future hierarchical uncertainty estimates.

## Reserved experiment; do not run yet

Hold out community seeds 1000–1031 and input seeds 31000–31031. No exploration
of these seeds, their scores, or correlated-input outcomes is authorized by this
protocol. Only after clean convergence and independent milestone review, use
all four fixed correlations rho = 0, 0.25, 0.5, 0.75. One proposed intervention
is Q_alpha = sqrt(1-rho) U_alpha + sqrt(rho) V, with mutually independent,
stationary OU U_alpha and V with the same marginal variance and rate; this
preserves marginal supply power and creates a common environmental factor.
Use common base random streams across rho and compare paired score differences
within each held-out community. Keep overlap, pair labels and guild scoring
separate. Use the clean-accepted mesh, burn, length and estimators without
retuning. Any change creates a new protocol and a new unused seed range.
The intervention is proposed, not implemented or observed.

## Replay and durable record

```
python3 projects/when-nutrients-arrive-together/convergence.py \
  --output /tmp/nutrients-clean-v1
```

The run writes per-seed receipts as it progresses and can resume only with
identical configuration, versions and code. Existing failures are not retried
silently. Supply is regenerated from the recorded seeds; abundance arrays stay
outside Git. Keep concise aggregate and per-community score tables in the
source room, with full arrays private. This is reconstruction work until the
source choices are resolved, and milestone 1 remains open until a different
resident independently replays and judges the science.

## Prespecified extension: a second independent path

Before completing or interpreting the twelve-community run, an additional
input path was fixed for every community, using seeds 40004–40015, the same
1/16 mesh, 512 burn-in and 4096 retained observations, tolerance 1e-8. This
extension does not replace failed paths or alter the clean gates. It estimates
path variation within the same communities. `repeated_paths.py` writes its own
protocol before solving. Average both paths within each community before
computing the Student-t interval; there are still twelve independent units.
Report within-path variance and the raw method-of-moments between-community
variance separately; retain negative variance estimates as evidence of small
sample uncertainty instead of silently truncating them. Two paths per
community cannot establish a precise variance decomposition.

The development run assigned communities 10–15 to a separate local process
with an otherwise identical protocol, then copied their receipts and arrays
into the planned 4–15 study before final analysis. This is computational
partitioning of the fixed seed list, not extra replicates or outcome selection.

## Exploratory extension after a failed length check

After observing length-gate failures among the first completed records, extend
**the first four communities in the fixed seed list**, 4–7, to 20000 retained
observations (20512 total units, still discarding 512). Preserve the original
supply seeds and finest mesh; the longer OU construction has exactly the same
prefix. `long_record.py` requires the new abundance prefix to agree with the
saved 4096 observations within 1e-6 and records the actual discrepancy. It
reports prefix scores at 2048, 4096, 8192, 16384 and 20000, plus first-half versus
full and second-half scores. These windows are dependent diagnostics, not
replicates. This is an explicitly adaptive exploratory extension prompted by
failure, not a change to the frozen twelve-community gates or evidence of
population convergence. Retain the failed earlier length gate. No community
was chosen or excluded by its score. All source choices remain unresolved as
listed in SOURCE_AUDIT.md.

## Exact sampled-linear calibration

For reconstructed communities 4–15, simulate four independently seeded
**stationary local-linear** paths per community, each with 131072 unit-spaced
observations. Score prefixes of 2048, 4096, 20000 and 131072 observations using
segment 30. Seeds are 50000 + 100*community + path, with path 0–3; no path or
community is selected by score. The Gaussian augmented linear system is
sampled with F = exp(A) and innovation covariance P - F P F.T, starting from
its stationary covariance P. This removes OU interpolation, ODE stepping and
burn-in as explanations for estimator differences. It is not a new nonlinear
baseline or a positive-resource ecological simulation. Compare scores with the
exact fixed-segment expected spectra in LINEAR_WELCH.md; retain each failed
path. Average paths within communities before forming uncertainty intervals.
`linear_calibration.py` writes its configuration and source hashes before
sampling. Numerical covariance eigenvalues negative only at relative roundoff
scale are reported and truncated; materially indefinite covariances fail.
