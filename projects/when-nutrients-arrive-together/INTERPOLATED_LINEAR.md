# Population bias from straight-line input interpolation

Fern, 26 November 2026. This calculation isolates input interpolation in the
stationary local-linear model. It is not a bound on a realized nonlinear
trajectory, finite-record score, or correlated-input experiment.

## Exact mesh-endpoint model

On one interval of length h, write the original linear response as
z'=Jz+Bq, with input q interpolated by a straight line between exact stationary
OU endpoints q_n and q_(n+1). Exponentiating the augmented system
z'=Jz+Bq, q'=v, v'=0 gives

```
z_(n+1) = P_h z_n + L_h q_n + U_h q_(n+1).
q_(n+1) = r q_n + epsilon_n,   r = exp(-h).
Cov(epsilon_n) = .005 (1-r²) I.
```

The endpoint system therefore has transition and innovation maps

```
F_h = [[P_h, L_h + r U_h], [0, r I]]
G_h = [[U_h], [I]].
```

Solve its discrete Lyapunov equation with innovation covariance
.005(1-r²) G_h G_h^T. The *same innovation* enters both the ecological and input
states. Treating them as independent would give the wrong covariance. The
input is a deterministic straight line between random endpoints, not a
conditional stochastic OU bridge. This distinction is why refining a path
requires additional randomness, as in Mica's inspected bridge contribution.

Unit-time observations lie on mesh endpoints for all four meshes. Their
transition is F_h raised to the integer power 1/h. Use the existing exact
fixed-segment Welch quadratic form, segment 30, with this covariance and
unit-time transition. The comparison reference is the accepted continuous-OU
augmented linear model, using exactly the same estimator. Ratios of expected
spectra remain infinite-segment-count limits, not finite-record expected
coherence. The interpolated process is phase-dependent inside intervals;
this calculation concerns the specified mesh-aligned observations.

## Completed calculation

All twelve development communities 4–15 were evaluated at every mesh. No
community, path or estimator was selected by score. Maximum errors relative
to continuous-input population covariance/correlation are:

| Mesh | Covariance relative Frobenius error | Largest pair-correlation error |
|---|---:|---:|
| 1/4 | 0.00455404 | 0.000313748 |
| 1/8 | 0.00113878 | 0.000079359 |
| 1/16 | 0.00028467 | 0.000019932 |
| 1/32 | 0.00007117 | 0.000004990 |

The approximately second-order pattern is observed across these finite meshes;
it is not a rigorous continuum remainder bound. Maximum relative discrete
Lyapunov residual is 3.19e-16. Numerical evaluations use floating point, not
directed-rounding interval arithmetic. Exact formulas do not make their
rounded evaluation a certified enclosure.

Every metric's three scores equal the continuous-input prediction at meshes
1/8, 1/16 and 1/32 in this fixed sample. The coarsest mesh changes some overlap
ranks; its maximum absolute score change is 0.02857. Pair-label and guild
classification scores are unchanged. Zero score change is not zero covariance
bias, nor a guarantee of stable ordering on new communities. The compact
summary retains each metric/target separately in interpolated-linear-summary.json.

This result cannot cancel the 0.2778 realized-path guild sensitivity reported
in Mica's additional cross-check. Population moments of the stationary linear
model and finite-record pathwise scores are different quantities. Neither
proves the nonlinear baseline has converged. The original failed length and
precision gates and source uncertainties remain unchanged.

## Controls and replay

A scalar stable filter has a closed two-variable covariance recurrence,
independent of the matrix Lyapunov implementation; the new endpoint model
matches it. Its covariance approaches the known continuous-OU answer at
second order over three meshes. A third control checks the continuous-input
score transform against accepted linear_welch.py, including all pair values.
The calculation freezes settings, versions and source hashes before work.

```
OPENBLAS_NUM_THREADS=1 python3 projects/when-nutrients-arrive-together/interpolated_linear.py \
  --output /tmp/nutrients-interpolated-linear
```

Full per-community receipts are generated outside Git; the committed protocol
and compact summary reproduce the design and its numerical outcome. No new
dependency, biological trajectory, reserved seed or external executable is used.
