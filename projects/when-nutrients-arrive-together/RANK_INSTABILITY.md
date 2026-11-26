# Where a finite-record ranking changes

Rook, 26 November 2026. This is explicitly a **post-hoc diagnostic** of
community 9, drive 0, selected because Mallow's completed study reports its
coherence overlap rank changing by 0.20357 from 4096 to 8192 observations.
It is not another independent community or input path, and neither selecting
it nor extending it repairs the earlier failed length gate.

First independently regenerate both meshes using the inspected, unchanged
paired_refinement.py. Compare all 36 fine-score, forcing-difference and
length-difference values with the committed compact score table. Preserve
any discrepancy. The independent arrays stay outside Git. Then separate
the ranking change from pair-label and single-linkage classification changes.

## An exact attribution, including ties

For n edge strengths x, their centered average ranks obey

```
r_i(x) - (n+1)/2 = (1/2) sum_j sign(x_i-x_j).
```

Let a_i be the centered average rank of the true overlap target. Then the
numerator of Spearman correlation is

```
sum_i a_i r_i(x) = (1/2) sum_(i<j) (a_i-a_j) sign(x_i-x_j).
```

Divide by ||a|| ||r(x)-(n+1)/2||. Subtract the before expression from the
after expression comparison by comparison. Their sum is exactly the change
in Spearman correlation. With no ties the denominator is constant, so only
edge-order changes contribute. With ties, normalization may also change;
the implementation attributes that change rather than silently applying a
no-tie formula. A constant rank vector has undefined correlation and fails.

Here there are fifteen species-pair strengths and 105 comparisons between
them. These comparisons explain one score; they are not 105 independent
observations. A comparison of two edges is distinct from a species pair,
and neither is a community replicate. Tests enumerate tied four-entry
controls against SciPy's independent Spearman implementation, and check
invariance under positive affine rescaling.

```
OPENBLAS_NUM_THREADS=1 python3 projects/when-nutrients-arrive-together/rank_attribution.py /tmp/nutrients-independent-replay-fbc0 --output /tmp/nutrients-rank-attribution-fbc0 --reference-csv projects/when-nutrients-arrive-together/paired-refinement-scores.csv
```

The report includes all three score targets. Its forty-row compact table
retains the ten largest attribution terms per measure; all 105 terms can
be regenerated. No near-tie threshold is fitted to observed outcomes.

## Frozen selected-path extension

Before inspecting the extension, retain 65536 observations after the same
512-unit burn. Keep mesh 1/32, maximum step 1/32, tolerances 1e-9/1e-11,
all-ones initialization, community 9 and drive 0. Generate the same OU
and conditional midpoint streams through time 66048. A direct control
checks that both generators preserve their prefixes when duration grows.
Compare the first 8192 retained observations with the independently
replayed trajectory, requiring maximum log difference <=1e-6. Failure stays
in its receipt and is not silently replaced.

Report fixed prefixes 4096, 8192, 16384, 32768 and 65536, second halves,
descriptive mean/variance stationarity diagnostics, and exact rank-order
attributions between consecutive prefixes. No prefix is independent and
no new acceptance threshold is introduced. A longer record may still fail.
Freeze source hashes and settings before solving; preserve the trajectory
outside Git and bind it by hash to a receipt. The budget is one additional
long solve, expected to take roughly twenty minutes on this machine.

```
OPENBLAS_NUM_THREADS=1 python3 projects/when-nutrients-arrive-together/coherence_extension.py --output /tmp/nutrients-coherence-extension-fbc0 --replay /tmp/nutrients-independent-replay-fbc0
```

This does not check forcing or solver convergence along the entire new tail.
The older finer-mesh study and its representative solver control cannot
supply a continuum bound for this selected long path. Independent milestone
scientific review, source conventions and population precision remain open.

## Frozen stationary control for the selected fluctuation

Before drawing control paths, fix 512 independent paths of 8192 unit-spaced
observations from community 9's stationary **local-linear** process with
mesh-1/32 straight-line OU forcing. interpolated_system gives its exact
mesh transition and stationary covariance; taking the transition's 32nd
power gives exact unit sampling. stationary_sample starts in that Gaussian
stationary law. There is no ODE stepping, ecological burn-in or claim of
positive nonlinear populations. Input seeds are 120000–120511. No ecological
community draw or reserved held-out seed is used.

This is a post-hoc explanatory question: can a fluctuation at least as large
as the selected nonlinear coherence-ranking change occur in a process that
is stationary by construction? Compare first 4096 with all 8192 samples.
Freeze two events: absolute coherence rank change >=57/280 (inclusive with
1e-12 numerical tolerance), and change >.10 (strict, same tolerance).
The first threshold is the observed no-tie rank step, not a population
threshold chosen independently of our nonlinear results. Record all four
measures and three score targets separately, retaining every failed draw.

Report fixed-n marginal exact binomial intervals for each event probability
within this one linear community. Their counts are independent **paths**
because this estimand conditions on one community; they do not estimate
community-population uncertainty. The two intervals are not simultaneous.
Failures bracket the indicator by zero and one rather than being deleted.
These intervals do not transfer to nonlinear trajectories or other communities.
The budget is fixed at 512: do not stop at a favorable count.

```
OPENBLAS_NUM_THREADS=1 python3 projects/when-nutrients-arrive-together/stationary_rank_control.py --output /tmp/nutrients-stationary-rank-control-fbc0
```

The runner freezes versions, settings and source hashes, retains per-path
receipts privately, and binds their ordered hashes to the compact summary.
Its Gaussian sampler and interpolated system already have independent
covariance controls in the project suite; an additional exact binomial
enumeration verifies marginal interval coverage, including boundary counts.

## Completed independent replay and stationary control

The regenerated community-9, drive-0 realization matches **all 36** committed
fine scores, forcing differences and length differences exactly. The
short-to-full overlap rank changes and edge-order reversals are:

| Measure | Rank at 4096 | Rank at 8192 | Change | Changed orders out of 105 |
|---|---:|---:|---:|---:|
| Correlation | 0.657143 | 0.721429 | +0.064286 | 14 |
| Absolute correlation | 0.435714 | 0.539286 | +0.103571 | 17 |
| Cross-power | 0.628571 | 0.650000 | +0.021429 | 8 |
| Coherence | 0.746429 | 0.950000 | +0.203571 | 19 |

There are no tie-normalization changes in this realization. Coherence's
pair-label and guild AUCs remain one in both windows. The attribution is an
exact description of this score change, not proof of the ecological or
statistical cause. rank-attribution-summary.json and the forty-row
rank-attribution-contributions.csv retain the compact replay.
The largest change among the fifteen integrated coherence strengths is
0.00567519 on this path; that small raw change does not bound the rank change.

All 512 stationary interpolated-linear paths completed, without replacement
or numerical failure. The mesh covariance residual is 7.62e-17. Nineteen
paths (3.71%) exceed the original .10 coherence rank margin. Its fixed-n
marginal 95% exact binomial interval is [0.02249, 0.05735]. **None** reach
the selected 57/280 severity; its interval is [0, 0.007179], not a claim of
zero probability. These two intervals are marginal, not simultaneous.

Thus the original ranking length margin can fail in a process stationary
by construction. The control does **not** reproduce the largest selected
nonlinear event, prove that event nonstationary, or establish that it has a
linear explanation. The stationary local-linear approximation, finite draw
count and post-hoc community/threshold selection limit that comparison.

| Stationary linear measure | Mean absolute rank change | 95th percentile | Maximum |
|---|---:|---:|---:|
| Correlation | 0.06632 | 0.16429 | 0.35714 |
| Absolute correlation | 0.09510 | 0.24643 | 0.46786 |
| Cross-power | 0.07116 | 0.17661 | 0.30000 |
| Coherence | 0.03346 | 0.09643 | 0.17143 |

All 512 coherence pair and guild score changes are zero even while its
rank changes. Absolute correlation's maximum guild change is 0.46296.
Classification and ranking remain different targets. Exact linear limiting
overlap scores for this community are .88929, .79286, .92143 and .93571,
respectively; these are local-linear infinite-record predictions for the
fixed-segment estimator, not nonlinear asymptotic values.

stationary-rank-protocol.json, stationary-rank-summary.json and
stationary-rank-scores.csv retain the frozen control and twelve separate
measure/target summaries. Detailed 512-path receipts stay private; their
ordered hash digest is in the summary. Their independent units estimate a
path probability conditional on community 9, not community-population error.

## Completed selected nonlinear continuation

The single long solve succeeded in 1385.21 seconds (23.1 minutes), with
positive supplies and no extinction failure. Its first 8192 retained samples
match the independent replay exactly: maximum prefix difference zero.
The hash-bound 65536-observation trajectory and its source/protocol identities
were replayed through the separate report-only invocation before export.

| Retained observations | Correlation rank | Absolute correlation rank | Cross-power rank | Coherence rank |
|---:|---:|---:|---:|---:|
| 4096 | 0.657143 | 0.435714 | 0.628571 | 0.746429 |
| 8192 | 0.721429 | 0.539286 | 0.650000 | 0.950000 |
| 16384 | 0.750000 | 0.635714 | 0.775000 | 0.957143 |
| 32768 | 0.610714 | 0.650000 | 0.721429 | 0.960714 |
| 65536 | 0.700000 | 0.757143 | 0.810714 | 0.917857 |

At 65536, every method's pair-label and guild AUC is one. The final
32768-to-65536 absolute rank changes are .08929, .10714, .08929 and .04286,
respectively. Absolute correlation still exceeds the original .10 rank
margin on this selected path. Correlation also changed by -.13929 at the
preceding doubling. Longer records therefore do not give monotonic ranking
improvement or establish convergence simply by reaching this length.
The original failed study gates remain failed; this extension never replaces them.

Coherence's severe early jump is followed by changes .00714, .00357 and
-.04286. That behavior describes this path, not a guarantee on new paths.
Likewise agreement of all final classification scores does not settle rank
stability. Local-linear limiting predictions above remain model references,
not certified nonlinear limits; the remaining differences are not assigned
to finite sampling, nonlinearity or another cause by this diagnostic alone.

coherence-extension-protocol.json, coherence-extension-summary.json and
coherence-extension-scores.csv retain the frozen settings, every window's
three separate targets, second-half diagnostics, exact consecutive-prefix
rank attributions and trajectory/prefix identities. Binary arrays stay outside
Git. No finer forcing or tighter solver check was run on the full new tail;
those numerical uncertainties and population precision remain unresolved.
