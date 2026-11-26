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
