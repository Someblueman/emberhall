# What a finer input mesh actually controls

A stationary OU input has covariance C(s,t) = sigma² exp(-omega |t-s|),
with sigma² = A²/2. At fraction theta of an interval of length h, approximate
Q(theta h) by L = (1-theta) Q(0) + theta Q(h). Expanding Var(Q-L) gives

```
Var(Q-L)/sigma² = 1 + (1-theta)² + theta²
  + 2 theta (1-theta) exp(-omega h)
  - 2 (1-theta) exp(-omega h theta)
  - 2 theta exp(-omega h (1-theta)).
```

Averaging over theta in [0,1], with a = omega h, gives

```
E_theta Var(Q-L)/sigma² = 5/3 + exp(-a)/3 - 4(a-1+exp(-a))/a².
```

The leading fine-mesh term is a/3. Thus mean-square unresolved forcing decreases
linearly with mesh size; RMS decreases only as its square root. This is not a
strong-order statement about an arbitrary solver or an error bound on a ranking.
`forcing_error.py` evaluates the covariance expression with stable `expm1` terms
and quadrature, avoiding cancellation in the closed form at small a. Independent
checks expand a three-point covariance matrix, simulate midpoint interpolation
errors, and verify the small-mesh asymptote.

For A=0.1 and omega=1:

| Mesh | Time-averaged input RMS error | Fraction of input stationary deviation |
|---|---:|---:|
| 1/4 | 0.020374 | 0.28813 |
| 1/8 | 0.014427 | 0.20402 |
| 1/16 | 0.010205 | 0.14432 |
| 1/32 | 0.007217 | 0.10206 |

These are exact second-moment calculations for replacing an underlying
continuous stationary OU path by its endpoint linear interpolation, averaged
within an interval. They include the unresolved OU bridge, not merely a solver
residual. They do not bound the nonlinear abundance trajectory or its estimated
scores. The consumer dynamics filter high frequencies; the continuously forced
local-linear transfer check validates the independent algebra, but does not
establish global nonlinear stability or stationary sampling.

Nested mesh differences in convergence.py are therefore **empirical
sensitivities**, never a certified continuum-error bound. Even shrinking
trajectory errors can reorder near-tied scores. A statement about converged
overlap, pair classification or guild classification must name the observed
mesh, sample, estimators and changes separately.
