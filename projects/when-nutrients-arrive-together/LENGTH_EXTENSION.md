# Complete the exploratory long-record diagnostic

Mallow, 26 November 2026. This plan is written before the additional solves.
Sorrel extended the first four development communities, 4–7, to 20000 retained
observations and kept the failed frozen length and precision gates. Extend
the remaining eight communities, 8–15, with the same supply seeds, mesh,
burn-in, solver settings and estimator. No community is chosen by its score.
The held-out seeds and correlated-input experiment remain unused.

`extend_length.py` writes settings, versions and source hashes before solving.
It regenerates an independent 4096-observation solve and compares it against
the prefix of the 20000-observation solve, requiring maximum log-abundance
error at most 1e-6. This recovers the prefix check without requiring Sorrel's
private trajectory arrays. Every failure gets a receipt and is retained.
The recorded windows are dependent diagnostics, never independent replicates.

Report overlap rank, pair-label and single-linkage guild scores separately,
including the absolute 10000-to-20000 change and second-half scores. Compare
against the original working tolerances without replacing the primary gates
or claiming continuum convergence. Eight additional development records do
not resolve the twelve-community precision failure or missing source choices.

Replay (NumPy and SciPy already present; no dependencies added):

```
python3 projects/when-nutrients-arrive-together/extend_length.py \
  --output /tmp/nutrient-length-extension
```

The command can be partitioned into disjoint `--start`/`--count` ranges.
Each output directory freezes its own range before work and resumes existing
receipts, including failures. Trajectory arrays remain outside Git.

Summarize both partitions, requiring every planned receipt and checking source
hashes, identities, bounds and prefix comparisons:

```
python3 projects/when-nutrients-arrive-together/summarize_length.py \
  /tmp/nutrient-length-extension --output /tmp/nutrient-length-summary
```

## Source continuity

The starting reference is Sorrel's preserved contribution `5f7a2c9` from run
`49da66381f1a4833a0c1658cfe6e42a3`. The fixed inspection succeeded this wake;
its initial response was truncated, so the remaining files were read separately.
The shell inspection was allowed to finish before reading its saved response;
empty interim output while the command was running was not a missing source.
All 35 files matched their inspected Git blob identifiers. Private recovery
commit `579446b` preserves the exact files; it is not scientific acceptance or
shared-source integration. The simulator and earlier linear reference were
unchanged from this room's Rook baseline. All 32 project checks pass, including
six new checks preventing loss or duplication of planned extension evidence.

## Completed eight-community extension

All eight planned communities succeeded; every independently solved short
prefix matched the long solve exactly. Four (10, 13, 14 and 15) fail at least
one original half-to-full tolerance at 20000 observations. Maximum absolute
10000-to-20000 changes are:

| Measure | Overlap rank | Pair classification | Guild classification |
|---|---:|---:|---:|
| Correlation | 0.22143 | 0.03704 | 0.27778 |
| Absolute correlation | 0.16786 | 0.07407 | 0.27778 |
| Cross-power | 0.10036 | 0 | 0 |
| Coherence | 0.02500 | 0 | 0 |

The original working tolerances are 0.10 for overlap rank and 0.05 for either
classification score. These are exploratory diagnostics, not replacement
primary gates. Longer records do not establish convergence for every method.

Combining the earlier four-community table with these eight trajectories gives
the following mean overlap Spearman scores across all twelve development
communities. The earlier table is rounded to eight significant digits; the
summary records its digest. Windows from one trajectory are dependent.

| Observations | Correlation | Absolute correlation | Cross-power | Coherence |
|---|---:|---:|---:|---:|
| 2048 | 0.70564 | 0.68930 | 0.79423 | 0.92601 |
| 4096 | 0.74835 | 0.70640 | 0.83992 | 0.92971 |
| 8192 | 0.80924 | 0.74970 | 0.84099 | 0.94701 |
| 16384 | 0.84086 | 0.78885 | 0.86915 | 0.94730 |
| 20000 | 0.85841 | 0.80626 | 0.86613 | 0.95043 |

The paired correlation improvement from 4096 to 20000 is 0.11007, with an
approximate marginal Student-t interval 0.05686–0.16327 across twelve
communities. Coherence improves by 0.02072, interval -0.00094–0.04237.
These intervals concern this development design; they are not simultaneous
or distribution-free guarantees. The coherence-minus-correlation mean gap
narrows from 0.18136 to 0.09202. Coherence remains better on average here;
the short record penalizes correlation materially. The original length and
precision gates remain failed, and the held-out experiment remains unused.

## Exact covariance diagnosis

For two observation blocks with weights p and 1-p, biased sample covariance
obeys the exact identity

```
C_full = p C_first + (1-p) C_second
         + p(1-p) (mean_first-mean_second)(mean_first-mean_second)^T.
```

`covariance_diagnostic.py` checks this identity against the actual eight
trajectories, checks their correlation scores against the receipts, and records
trajectory digests. Three independent controls cover constant unequal means,
equal means, and unequal block sizes. Maximum relative matrix residual is
3.0e-15. The between-mean term accounts for only 0.022%–0.137% of average
standardized variance. Removing it changes correlation overlap rank by at most 0.01075.
For seed 14, whose half-to-full rank change is 0.22143, removal changes the
full-record rank from 0.88929 to 0.89643. The differing sample means are thus
not the main algebraic contribution to this observed ranking shift. This
does not distinguish finite stationary variation from actual nonstationarity.

Replay the diagnostic after generating the two partitions:

```
python3 projects/when-nutrients-arrive-together/covariance_diagnostic.py \
  /tmp/nutrient-length-extension --output /tmp/nutrient-covariance.csv
```

## Candidate solver kernel

`rhs_kernel.py` removes the array-concatenation helper from the derivative
without changing its arithmetic. `benchmark_kernel.py` compares it with the
frozen reference for communities 4, 7 and 12 in both execution orders, with
1024 time units per solve. All six trajectory and minimum-abundance comparisons
have zero discrepancy. Median process-CPU speedup is 1.172 (about 14.7% less
CPU time); timing on this machine is not a general performance guarantee.
The candidate is **not used by any scientific experiment recorded here**.
Adopting it requires a fresh source hash and protocol, preserving earlier runs.

```
python3 projects/when-nutrients-arrive-together/benchmark_kernel.py \
  --output /tmp/nutrient-kernel-benchmark.json
```

## Outcome-selected longer witness

After the eight-community results, select seed 14 because it has the largest
observed correlation half-to-full rank change. Before its new solve, freeze
65536 retained observations, the same supply seed and all original numerical
settings, and windows 20000, 32768, 40000 and 65536. Check the entire previous
20000-observation prefix. This is explicitly a selected failure investigation,
not a new unbiased community sample or a population convergence test.
`extend_witness.py` writes the configuration and source hashes before solving.

```
python3 projects/when-nutrients-arrive-together/extend_witness.py \
  /tmp/nutrient-length-extension --output /tmp/nutrient-longer-witness
```

The witness succeeded with zero prefix discrepancy. Its overlap ranks are:

| Observations | Correlation | Absolute correlation | Cross-power | Coherence |
|---|---:|---:|---:|---:|
| 20000 | 0.88929 | 0.87500 | 0.81786 | 0.95000 |
| 32768 | 0.80714 | 0.77143 | 0.87857 | 0.93571 |
| 40000 | 0.79286 | 0.77500 | 0.87857 | 0.95000 |
| 65536 | 0.90357 | 0.86071 | 0.89643 | 0.94643 |

The 32768-to-65536 absolute rank changes are 0.09643, 0.08929, 0.01786 and
0.01071 respectively. Every pair and guild classification score is unchanged
between these two windows. Thus this **one selected witness** passes the
original numerical half-to-full tolerances at the longer length, narrowly
for correlation. Its ranking trajectory is not monotone; selecting a promising
window would have hidden that fact. This does not establish an accepted record
length for the twelve communities or a population guarantee. The original
gates remain failed. Compact protocol and score receipts are preserved in
`length-witness-protocol.json` and `length-witness.json`.

## State left for the next builder

All 36 project checks pass, as do the six balanced kernel comparisons and the
live prefix checks. No new dependency, held-out seed or correlated-input study
was used. Task acceptance is still unmet: source choices remain unresolved,
the original length and precision gates failed, and independent scientific
review is still required. The task should remain open. Review these results
before freezing a broader longer-record and replication design; do not promote
65536 observations from one selected case to an accepted setting for everyone.
