# Does the nonlinear simulator approach its linear response?

Fern, 26 November 2026. This diagnostic was specified before its new solves.
It tests the local approximation used by the analytical reference; it does
not accept the clean nonlinear baseline or change its failed gates.

Use every development community 4–15, one new independent-input path per
community with seed 70000 + community, duration 2048 and the existing 1/16
forcing mesh. Start both models at the same deterministic equilibrium, with
zero perturbation in the linear model. Discard the first 512 time units and
observe at unit spacing. On this same path use supply perturbation fractions
1, 1/2, 1/4 and 1/8. The fraction-one perturbation has the original amplitude
0.1. The four outcomes are dependent, not four independent communities.
These choices do not use any reserved held-out community or correlated input.

The exact linear response to the *piecewise-linear* input is computed by one
matrix exponential of the augmented system z'=Jz+Bq, q'=v, v'=0. On each
forcing interval, reset q to its left endpoint and v to its slope, retaining
the continuous response z. This removes linear integration error up to
floating-point matrix arithmetic. It does not remove the input interpolation
choice. This finite-path response is distinct from the stationary continuous
OU covariance used in FINITE_COVARIANCE.md.

The nonlinear solve uses the original derivative in reference.py, maximum
step 1/32, relative tolerance 1e-10 and absolute tolerance 1e-12. No candidate
kernel is adopted. Compare its log-abundance perturbation divided by the
fraction with the unscaled linear response. Report trajectory relative RMS,
relative sample-covariance error, and every metric/target score difference.
A second-order Taylor remainder predicts O(fraction) scaled-response error
on a fixed finite path; this is a diagnostic expectation, not an acceptance
gate or a theorem uniform over all paths and durations. Scores need not
converge smoothly because ordering and linkage are discontinuous at ties.

For community 4 at fraction 1/8, also halve maximum step and tighten tolerance
to 1e-11 (absolute tolerance 1e-13), reporting trajectory disagreement in the
same units. This is a preselected representative numerical check, not a
bound on every trajectory. Retain all failures without silently replacing
paths. Resume reuses recorded successes and failures only with identical
configuration and source hashes. A missing final summary means an interrupted
batch, not a completed twelve-community experiment.

```
OPENBLAS_NUM_THREADS=1 python3 projects/when-nutrients-arrive-together/amplitude_limit.py \
  --output /tmp/nutrients-amplitude-limit
```

Three independent controls check the scalar ramp response against its closed
form, the linear Jacobian against central differences of the original
nonlinear derivative, and constant-supply equilibrium preservation. The
experiment writes settings and hashes before solving. Source conventions,
nonlinear stationarity, forcing and record-length convergence, community-level
precision, and independent milestone review remain separate requirements.

## Completed results

All twelve planned communities completed all four fractions: 48 successful
nonlinear solves, no failed communities. The preselected tighter solve also
completed. There was no selection or replacement of paths. Source and library
versions are in amplitude-limit-protocol.json; amplitude-limit-summary.json
retains all score targets, per-community trajectory errors and the solver check.

| Input fraction | Maximum scaled trajectory relative error | Maximum scaled covariance relative error |
|---|---:|---:|
| 1 | 0.00936985 | 0.00450005 |
| 1/2 | 0.00469153 | 0.00228092 |
| 1/4 | 0.00234753 | 0.00114857 |
| 1/8 | 0.00117424 | 0.00057637 |

Every community's trajectory error decreases under every halving. The 36
within-community consecutive error ratios range from 1.99551 to 2.00352,
consistent with the finite-path first-order scaled-response prediction.
The tighter solver changes the fraction-one-eighth response by 3.09e-7 in
the same normalized units, versus nonlinear-to-linear error 0.00113 in that
community. This representative check supports resolving the measured
trajectory discrepancy; it does not bound every score or realization.

Maximum absolute differences from the exact linear response's *finite-path*
scores are reported separately below. The AUC columns take maxima over all
four fractions and twelve communities; rank columns retain each fraction.

| Metric | Rank, 1 | Rank, 1/2 | Rank, 1/4 | Rank, 1/8 | Pair AUC, all | Guild AUC, all |
|---|---:|---:|---:|---:|---:|---:|
| Correlation | 0.007143 | 0.007143 | 0.007143 | 0 | 0 | 0 |
| Absolute correlation | 0.014337 | 0.014337 | 0.014337 | 0 | 0 | 0 |
| Cross-power | 0.007143 | 0 | 0 | 0 | 0 | 0 |
| Coherence | 0.016086 | 0.016086 | 0.016086 | 0.016086 | 0 | 0 |

The remaining coherence rank discrepancy is retained. These four amplitudes
do not establish its limiting behavior or diagnose its cause; a small
trajectory/covariance error alone cannot certify an ordering. No new smaller
fraction was selected after observing it. Agreement of both classification
targets likewise does not certify accurate overlap ranking.

All 49 project checks pass. These results support using the local-linear
model as a controlled approximation along these twelve finite paths, with
explicit measured errors. They do not transfer its Gaussian probability
bounds to nonlinear populations, demonstrate nonlinear stationarity, or
complete the clean convergence and community-precision requirements.

## Post-hoc diagnosis of the retained coherence gap

A targeted replay of community 4 at fraction 1/8, using the identical path
and settings, recovers exactly the retained 0.0160858 rank difference. There
is one pair-order inversion: species edges (1,3) and (1,5), indexed from zero.
Their linear affinity difference is -6.57024e-7; the nonlinear difference is
+2.98489e-6. The largest affinity change across all fifteen edges is 1.64704e-5.
Both classification scores remain one. Thus a small affinity change flips a
nearly tied ordering. This locates the score change arithmetically; it does
not distinguish every numerical and nonlinear contribution or establish
behavior below the tested amplitude. No original gate is changed.

The explicitly post-hoc protocol and full fifteen-edge values are retained in
coherence-gap-protocol.json and coherence-gap.json. Replay with
`OPENBLAS_NUM_THREADS=1 python3 projects/when-nutrients-arrive-together/diagnose_coherence.py --output /tmp/nutrients-coherence-gap`.
