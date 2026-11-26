# Replicated nonlinear mesh and record-length diagnostic

Mallow, 26 November 2026. Written before the new solves. The prior clean
reference's failed length and precision gates remain failed. This adaptive
development study addresses NEXT.md's broader nonlinear design; it does not
freeze a clean baseline, replace the accepted protocol, or use held-out seeds.

Use all twelve development communities 4–15 and two new independent input
paths each. Input seed is 80000 + 100*community + drive (drive 0 or 1).
Generate stationary independent OU supply on mesh 1/16, then conditionally
refine each interval at its midpoint with bridge seed 90000 + 100*community
+ drive. The bridge preserves every coarse endpoint exactly and has the
joint OU law checked in test_ou_bridge.py. The two meshes are paired
approximations to one path, never independent replicates. They do not
certify a continuum bound. No correlated inputs are generated.

Start every consumer and resource amount at one, as in the accepted
reconstruction. Supply means, private resources and amplitude remain the
explicit reconstruction choices in MODEL.md and SOURCE_AUDIT.md. No new
published-figure replication claim follows. Simulate 8704 units, discard
512, and retain 8192 unit-spaced samples. Both meshes use maximum step
1/32 and relative tolerance 1e-9 (absolute tolerance 1e-11), isolating
forcing interpolation while keeping solver settings equal. On preselected
community 4, drive 0, repeat both meshes at maximum step 1/64, relative
tolerance 1e-11 and absolute tolerance 1e-13. This is a representative
solver control, not an error bound on the other paths.

For each metric, report overlap Spearman, pair-label AUC and single-linkage
guild AUC separately. Segment 30 is primary; segments 16 and 60 are
diagnostics. Compare coarse with fine over the entire retained window;
compare first 4096 with all 8192 samples on the fine mesh and report the
second half separately. Report half-mean shifts and variance ratios as
descriptive stationarity diagnostics, not a stationarity proof. Preserve
nonpositive supply, resource or extinction failures without replacement.

Average the two drives within each community before marginal Student-t
intervals. Also report untruncated distribution-free marginal Hoeffding
radii (score ranges two for rank, one for AUC; difference ranges twice
these). Twelve independent communities cannot provide distribution-free
precision of .10: the marginal radii for means are about .784 and .392.
No nominal population-precision success is possible by pretending 24
paths are 24 communities. Missing or failed drives exclude the entire
community from conditional means, with failures retained. The signed mean
of paired changes can hide cancellation, so retain the worst individual
absolute change and community counts exceeding the original forcing
margins (.05 rank, .03 AUC) and length margins (.10 rank, .05 AUC).
Those are descriptive comparisons, not new acceptance gates. No multiple
comparison or simultaneous-coverage claim is made.

Coverage qualification identified while the frozen solves were running:
the design was chosen adaptively after earlier results on these same
development communities. Its Student-t intervals and Hoeffding radii are
nominal **fixed-design references**, not a certification of post-selection
population coverage. New independent paths do not make the reused community
sample fresh. This limitation does not change any seed, solve or numerical
summary; independent validation remains reserved by the accepted protocol.

The exporter adds a separate analytical diagnostic for the **fixed cohort**.
Condition on the twelve communities and all design history before the new
input paths. The 24 new paths are independent conditional on that history,
although they are not 24 community draws. For any one of the 36 predeclared
metric/target/field combinations (scores, forcing changes, length changes),
let its bounded outcome have range width W. On failure replace its undefined
value by the range's lower and upper endpoints, obtaining L and U. Every
bounded completion has expectation between the averages of E L and E U.
Two one-sided Hoeffding inequalities give an envelope

```
[mean(L) - W sqrt(log(2/alpha)/(2*24)),
 mean(U) + W sqrt(log(2/alpha)/(2*24))].
```

This needs independence, not identical path distributions. Use alpha=.05
for a marginal envelope, and .05/36 for simultaneous coverage of all 36.
It does not condition away observed failures. With no failures, marginal
radii for mean scores are about .554 for rank and .277 for AUC; difference
ranges double those radii. Thus these conditional bounds also do not give
.10 precision. They concern expected behavior over new inputs to this fixed
cohort, including explicitly bounded failure completions, not a population
of newly drawn communities. This analytical scope clarification is added
after interim results; no solve, seed, estimator or scoring target changes.
An exact binomial control checks coverage and the nonzero radius after a
perfect sample; failure receipts widen the empirical completion interval.

The computational budget is 48 primary solves and two representative
solver checks. Run two disjoint six-community partitions in local worker
processes, using only already installed NumPy/SciPy. A wall-time stop
leaves an explicitly incomplete batch with each completed receipt retained;
it cannot establish a population result. Exact settings, versions and
source hashes are frozen before solving, and all successful trajectories
are hash-bound outside Git. Only the small protocol, summary and a compact
per-realization score table belong in the repository.

```
OPENBLAS_NUM_THREADS=1 python3 projects/when-nutrients-arrive-together/paired_refinement.py --output /tmp/nutrients-paired-refinement --start 4 --stop 10
OPENBLAS_NUM_THREADS=1 python3 projects/when-nutrients-arrive-together/paired_refinement.py --output /tmp/nutrients-paired-refinement --start 10 --stop 16
OPENBLAS_NUM_THREADS=1 python3 projects/when-nutrients-arrive-together/paired_refinement.py --output /tmp/nutrients-paired-refinement --report-only
```

Initialize the shared protocol with `--report-only` before starting both
partitions. Each owns disjoint receipts and arrays. Resume retains success
and failure receipts only under matching protocol and seed identities.
An incomplete summary is a progress report, never completed evidence.
Independent milestone scientific review remains outstanding.

After the first paired solve took about 324 seconds, two additional local
workers took communities 8–9 and 14–15, far ahead of the original ascending
workers. Two further workers took communities 7 and 13 before the original
workers reached them. The latter reuse completed receipts when they reach
those communities. This changes computational scheduling only, not the
frozen seed list, mesh, duration or analysis. No realization is an extra replicate.

After every planned receipt exists, independently re-score each hash-bound
trajectory and export the compact results:

```
OPENBLAS_NUM_THREADS=1 python3 projects/when-nutrients-arrive-together/refinement_report.py /tmp/nutrients-paired-refinement --output /tmp/nutrients-refinement-report
```

This audit rejects missing receipts, changed source/protocol identities,
changed trajectory files, or score/diagnostic values that do not replay.
The report retains receipt digests and its own exporter digest. Timing fields
need not reproduce byte-for-byte on another machine; the scores and settings
are the scientific replay targets. Binary arrays and detailed receipts stay
outside Git; the compact score table and protocol preserve the reported run.

## Completed results

All 24 planned realizations completed successfully: twelve communities,
two new drives each, 48 primary solves and two preselected tighter checks.
No path was replaced. The complete audit replayed every primary score,
segment comparison, stationarity diagnostic and mesh trajectory discrepancy
from the hash-bound arrays. The frozen protocol and compact exports are
[paired-refinement-protocol.json](paired-refinement-protocol.json),
[paired-refinement-summary.json](paired-refinement-summary.json) and
[paired-refinement-scores.csv](paired-refinement-scores.csv).

Mean fine-mesh scores average the drives within each community first:

| Measure | Overlap rank | Pair AUC | Guild AUC |
|---|---:|---:|---:|
| Correlation | 0.80214 | 0.97608 | 0.97685 |
| Absolute correlation | 0.73209 | 0.95833 | 0.97917 |
| Cross-power | 0.84442 | 1.00000 | 1.00000 |
| Coherence | 0.95437 | 1.00000 | 1.00000 |

Maximum absolute changes across all 24 realizations:

| Measure | Mesh rank | Mesh pair | Mesh guild | Length rank | Length pair | Length guild |
|---|---:|---:|---:|---:|---:|---:|
| Correlation | 0.03214 | 0.01852 | 0 | 0.23056 | 0.25926 | 0.42593 |
| Absolute correlation | 0.03214 | 0.01852 | 0 | 0.26095 | 0.22222 | 0.42593 |
| Cross-power | 0.01430 | 0 | 0 | 0.14643 | 0.01852 | 0 |
| Coherence | 0.01072 | 0 | 0 | 0.20357 | 0 | 0 |

Every path is inside the original forcing margins for this finer comparison.
Eighteen paths in eleven communities exceed at least one original length
margin. Coherence rank changes by 0.20357 on community 9, drive 0, although
its two classification scores remain one. Classification agreement therefore
does not establish overlap-ranking stability. These findings preserve the
older failed length gate and the distinct coarser-mesh failure in CROSSCHECK_RESULTS.md.

Maximum mesh log-abundance RMS is 0.00018957. On the preselected solver
control, tighter solves differ by 4.36e-9 and 6.60e-9 RMS on the two meshes;
all score changes are zero. Maximum half-mean shift is 0.29625 whole-window
standard deviations, and half-variance ratios span 0.74137–1.25609. These
descriptive diagnostics do not establish nonlinear stationarity.
The tighter-solver receipts are retained, but their arrays were not archived;
those controls require rerunning the tighter solves for independent replay.

All nominal community intervals and conditional fixed-cohort envelopes are
retained in the summary with their different scopes. The latter remain too
wide for .10 precision. No continuum error bound, fresh-community validation,
source-parameter resolution, clean-baseline freeze or milestone acceptance
is obtained. The held-out communities and correlated inputs remain unused.

Verification: 57 project checks passed after the runner was added, followed
by three export/audit controls, including the binomial coverage control.
The source model and derivative are unchanged from the preserved pilot.
