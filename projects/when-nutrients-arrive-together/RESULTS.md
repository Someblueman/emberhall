# Clean reference: a measured failure to establish convergence

Sorrel, 26 November 2026. **Milestone 1 is not complete.** Source conventions
remain partly unresolved, the frozen convergence/precision gates below are
not all satisfied, and independent scientific review has not occurred.
No correlated-input or reserved held-out experiment was run.

## Scope and replay

Communities 4–15; 4096 retained unit-spaced observations after 512 burn-in.
Nested 1/4, 1/8 and 1/16 meshes on one OU path per community; separate finest
solver refinement. Twelve additional independent paths use the same communities.
An exploratory first-four-community extension retains 20000 observations.
All decisions, including the adaptive extension, are in [PROTOCOL.md](PROTOCOL.md).
The committed protocol files preserve seeds, settings, versions and code hashes.
The score tables round to eight significant digits; binary trajectories and
full receipts stay private and can be regenerated using the recorded commands.
`analyze.py STUDY --output DESTINATION` reconstructs the detailed primary summary.
No new dependency was installed. The project suite now passes 26 checks, including the later linear calibration.

## Frozen primary gates

| Gate | Result |
|---|---|
| no_failures | True |
| forcing | True |
| length | False |
| solver | True |
| precision | False |

All 12 planned primary communities were attempted; failures: 0.
Second-path complete communities: 12; failed pairs: 0.
Long-record attempts: 4; failures: 0.

Passing a finite mesh comparison is an empirical sensitivity result, not a
rigorous continuum bound. A failed length gate remains failed after an
exploratory extension. Precision requires both approximate Student-t and
bounded-score Hoeffding marginal intervals to have half-width at most 0.10.
Twelve communities are insufficient for that conservative guarantee. Intervals
are marginal, not simultaneous across all measures and targets.

## Primary uncertainty across communities

Rank = overlap Spearman; pair = same-diet pair AUC; guild = single-linkage AUC.
The fifteen dependent species pairs never count as independent replicates.

| Measure | Target | Mean | Student-t 95% interval | Hoeffding 95% interval |
|---|---|---:|---|---|
| correlation | rank | 0.7483 | 0.6964, 0.8003 | -0.0358, 1.0000 |
| correlation | pair | 0.9645 | 0.9430, 0.9861 | 0.5725, 1.0000 |
| correlation | guild | 0.9074 | 0.8205, 0.9943 | 0.5154, 1.0000 |
| absolute_correlation | rank | 0.7064 | 0.6525, 0.7603 | -0.0777, 1.0000 |
| absolute_correlation | pair | 0.9568 | 0.9331, 0.9805 | 0.5647, 1.0000 |
| absolute_correlation | guild | 0.9074 | 0.8205, 0.9943 | 0.5154, 1.0000 |
| cpsd | rank | 0.8399 | 0.8048, 0.8750 | 0.0558, 1.0000 |
| cpsd | pair | 0.9985 | 0.9951, 1.0019 | 0.6064, 1.0000 |
| cpsd | guild | 1.0000 | 1.0000, 1.0000 | 0.6079, 1.0000 |
| coherence | rank | 0.9297 | 0.9091, 0.9503 | 0.1456, 1.0000 |
| coherence | pair | 1.0000 | 1.0000, 1.0000 | 0.6079, 1.0000 |
| coherence | guild | 1.0000 | 1.0000, 1.0000 | 0.6079, 1.0000 |

The paired coherence-minus-correlation overlap advantage is 0.1814
with approximate marginal Student-t 95% interval 0.1364–0.2263.
This is an effect in this reconstructed development sample, not a universal
comparison or an exact published-figure replication.

## Maximum observed score changes

Entries are maxima of absolute changes across all twelve communities; they
do not extrapolate to unseen communities. Solver and forcing columns refer
only to the fixed primary segment length.

| Measure | Target | Finest solver | 1/8 to 1/16 | 2048 to 4096 | Segment 16/60 versus 30 |
|---|---|---:|---:|---:|---:|
| correlation | rank | 0.00000 | 0.03929 | 0.27857 | 0.00000 |
| correlation | pair | 0.00000 | 0.01852 | 0.14815 | 0.00000 |
| correlation | guild | 0.00000 | 0.00000 | 0.27778 | 0.00000 |
| absolute_correlation | rank | 0.00000 | 0.03929 | 0.35357 | 0.00000 |
| absolute_correlation | pair | 0.00000 | 0.01852 | 0.25926 | 0.00000 |
| absolute_correlation | guild | 0.00000 | 0.00000 | 0.27778 | 0.00000 |
| cpsd | rank | 0.00000 | 0.03214 | 0.14643 | 0.15714 |
| cpsd | pair | 0.00000 | 0.00000 | 0.03704 | 0.01852 |
| cpsd | guild | 0.00000 | 0.00000 | 0.00000 | 0.00000 |
| coherence | rank | 0.00000 | 0.02502 | 0.06810 | 0.03932 |
| coherence | pair | 0.00000 | 0.00000 | 0.00000 | 0.00000 |
| coherence | guild | 0.00000 | 0.00000 | 0.00000 | 0.00000 |

## Independent input paths within communities

Both paths are averaged within each community before the interval is formed.
Within-path variance and raw between-community variance are method-of-moments
diagnostics with only two paths per community. Negative estimates are retained.
Perfect observed scores still do not establish perfect population recovery.

| Measure | Target | Two-path mean | Student-t 95% interval | Within-path variance | Between-community variance, raw |
|---|---|---:|---|---:|---:|
| correlation | rank | 0.7430 | 0.7061, 0.7800 | 0.00794 | -0.0005844 |
| correlation | pair | 0.9568 | 0.9323, 0.9813 | 0.002172 | 0.0004001 |
| correlation | guild | 0.9120 | 0.8465, 0.9776 | 0.01183 | 0.004723 |
| absolute_correlation | rank | 0.7203 | 0.6786, 0.7621 | 0.007282 | 0.0006727 |
| absolute_correlation | pair | 0.9460 | 0.9236, 0.9684 | 0.002743 | -0.0001273 |
| absolute_correlation | guild | 0.9144 | 0.8494, 0.9793 | 0.01067 | 0.005109 |
| cpsd | rank | 0.8318 | 0.8004, 0.8633 | 0.004392 | 0.0002585 |
| cpsd | pair | 0.9985 | 0.9962, 1.0007 | 2.858e-05 | -1.299e-06 |
| cpsd | guild | 1.0000 | 1.0000, 1.0000 | 0 | 0 |
| coherence | rank | 0.9308 | 0.9108, 0.9509 | 0.0008082 | 0.0005945 |
| coherence | pair | 1.0000 | 1.0000, 1.0000 | 0 | 0 |
| coherence | guild | 1.0000 | 1.0000, 1.0000 | 0 | 0 |

## Stationarity, long records and limiting reference

Primary half-window mean shifts reach 0.388 whole-window deviations;
half-window variance ratios span 0.737–1.235. These are
descriptive diagnostics, not tests proving stationarity or nonstationarity.
Local-linear relaxation times span 8.98–11.90 units; the largest
independent covariance-integral discrepancy is 6.39e-13.

| Extended community | Same-prefix max error | Largest 10000-to-20000 score change |
|---|---:|---:|
| 4 | 0 | 0.12154 |
| 5 | 0 | 0.11260 |
| 6 | 0 | 0.15000 |
| 7 | 0 | 0.08929 |

See [long-record-scores.csv](long-record-scores.csv) for every fixed window.
Four dependent-path duration extensions do not establish community-level
convergence. [LINEAR_WELCH.md](LINEAR_WELCH.md) supplies the exact fixed-segment
stationary linear reference: it predicts strong equal-time correlation as well
as coherence under our reconstructed parameters. This contradicts any claim
that the reconstruction has demonstrated universal failure of correlation.
[FORCING.md](FORCING.md) quantifies unresolved continuous OU input; it is not
a nonlinear score-error bound. [SOURCE_AUDIT.md](SOURCE_AUDIT.md) preserves
access failures and all unresolved source choices.

## Next scientific work

Resolve source supply and initial-state conventions without claiming exact
replication in their absence. Choose and freeze a larger, longer clean study
using these failed gates as development evidence; use a fresh unused seed range
and retain this study unchanged. Assess score stability and uncertainty for
overlap, pair labels and guild closure independently. Obtain independent
scientific replay before accepting the baseline or touching reserved correlated
inputs. The original clean-reference task remains unfinished.
