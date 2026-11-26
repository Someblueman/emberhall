# Uniform starting-range comparison in the supplied linear model

Rook, 26 November 2026. Derivation and grid frozen before evaluation.
This extends TRANSIENT_LAW.md from fixed starting states to a declared family.
It is a finite-horizon Gaussian linear-model comparison, not a nonlinear
burn-in certificate or a new source convention. Original gates remain failed.

Every ecological initial amount may lie independently in [.5,2], with OU
supply initialized independently and stationarily. Consumer coordinates are
log amounts relative to equilibrium; resource coordinates are amount differences.
Thus initial consumer means have center -log(x_equilibrium) and radius log2,
resource means have center1.25-R_equilibrium and radius.75, and OU means are0.
There are36 uncertain deterministic coordinates. Their common covariance P0
has only the OU block .005 I. The accepted all-ones start belongs to this
family; the family itself is a new diagnostic choice, not a changed baseline.

For burn B let T=F^B, D=T(P0-P)T.T and P=L L.T. Whiten mean center c=L^-1 T m0
and box map A=L^-1 T[:, :36] diag(r), so h=c+A z, |z_j|<=1. The following
four quantities each upper-bound max_z ||h||; take their minimum:

```
||c|| + sum_j ||A_j||
||c|| + sqrt(q) ||A||_2
|| abs(c)+abs(A) 1 ||
sqrt( ||c||^2 + 2 sum_j |(A.T c)_j| + sum_jk |(A.T A)_jk| ).
```

The first is the triangle inequality; the second also uses ||z||<=sqrt(q).
The third bounds each coordinate separately. The fourth expands the quadratic
norm and bounds each bounded monomial, retaining inner-product cancellation.
Zero-radius columns are dropped when counting q. No corner sampling or
independence assumption is used to prove these upper envelopes. No inverse
of I-F, diagonalization of F or asymptotic burn approximation is used.

Let E=L^-1 D L^-T, V=I+E positive definite, with eigenpairs (e,U).
The covariance-only Gaussian KL and negative log affinity are those in
TRANSIENT_LAW.md. Add half the squared mean envelope to KL. For affinity,
apply the SAME box calculation to diag(1+e/2)^(-1/2) U.T c and its transformed
map, and add one eighth of that squared envelope. Then Pinsker and the
Gaussian-affinity inequality give a uniform total variation upper bound.
This preserves the full covariance/mean interaction in the affinity metric,
instead of replacing that metric by its least eigenvalue alone.

By the common future kernel, every predetermined initial state in this range
has finite-record score failure probability at most alpha+U when the stationary
failure probability is at most alpha. Bounded score expectation changes are
at most range times U, separately for rank, pair labels and guild scores.
A mixture over starts chosen independently of future innovations obeys the
same bound by convexity of total variation. This is uniform POINTWISE coverage,
not a simultaneous pathwise claim about all starts driven by common noise.
It does not justify choosing a start after looking at its future trajectory.
Nor does it enlarge the independent-community count or certify the nonlinear law.

For geometry diagnostics, freeze a feasible-corner lower bound as well. Start
coordinate ascent at all-plus, all-minus and sign(A.T c), retaining the current
sign on ties, for at most20 sequential sweeps. Every returned corner is feasible,
so its norm is a lower bound on the maximum mean norm; it is not a certified
optimizer or a lower bound on total variation. Report it beside the upper
bound to expose geometric looseness. All methods are fixed before results.

Evaluate reused development communities4–15, burns0,16,32,64,128,512. At burn0
each deterministic ecological start has a singular state law versus the full
stationary Gaussian density, so its exact state distance is1. At positive burns,
retain any failed positive-definiteness check; never add covariance jitter.
Bind source/library identities and numeric input matrices. No new stochastic
path, nonlinear solve, held-out community or correlated input is used.

Validate every mean envelope against all corners of independent small boxes,
including nonnormal maps and zero radii; validate both divergence envelopes
against the exact pointwise Gaussian formulas, retain the zero-burn case, and
replay all72 cases byte-identically. Numerical evaluations use floating matrices
and ordinary BLAS/SVD, not outward rounding. Tiny computed bounds are not
accuracy certificates for the underlying differential equations.

## Results

The construction above is frozen separately from this outcome report; the
protocol hashes that construction prefix and all numerical sources. The
manifest binder separates the report from the construction without changing
the evaluated grid, equations or any numerical table value.

All72 comparisons are retained:12 analytically singular zero-burn laws and60
successful positive-burn matrix comparisons, with no covariance repair. Largest
computed uniform total variation upper bound across the twelve reused models:

| Burn | Largest upper bound |
|---:|---:|
| 0 | 1 |
| 16 | 1 |
| 32 | 1 |
| 64 | .394148 |
| 128 | .00179542 |
| 512 | 1.71002e-17 |

On the positive-burn cases the geometric mean-norm upper bound is at most
1.13512 times a retained feasible-corner lower bound. At burn128 the largest
ratio is1.04272. This describes geometric looseness, not a certified maximizer
or an estimate of actual total variation. At burn512 one reported floating
upper/lower ratio is0.9999999999999998; it is retained as roundoff evidence,
not rounded into a rigorous certificate. This method does not use outward
arithmetic, and tiny late values cannot certify numerical accuracy of the
underlying equations. Bounds equal to1 are vacuous, not successful convergence.

### Transferring a family of stationary guarantees

For community i, let E_i be failure of a stationary score envelope jointly over
all its prefixes/measures/targets, with stationary probability at most alpha_i.
The longest future record determines all those prefix scores. The same starting-
law bound delta_i therefore gives P_transient(E_i)<=alpha_i+delta_i ONCE for
that whole event. A union bound over communities gives

```
P_transient(any E_i) <= min(1, sum_i alpha_i + sum_i delta_i).
```

This corollary does not need independence across the community events, provided
each marginal starting-law/kernel assumption holds. It does not add delta once
per spectral bin, measure, target or prefix. It also does not establish joint
coverage of every initial state under one noise realization. The tuple of
starting states must be predetermined, or independently randomized as specified
above. An outcome-selected start remains outside this theorem.

For the twelve fixed models, the sums of the computed delta values are12 at
burn16,11.999898 at32,2.433699 at64,.00595624 at128 and1.81337e-17 at512.
Thus a hypothetical stationary family allocation sum alpha_i=.05 yields a
vacuous transferred family bound through burn64, and a computed .0559563
failure upper bound at128. At512 the additional computed term is negligible
at ordinary matrix accuracy; no exact ecological confidence claim follows.
These are illustrative transfers of a stationary theorem under its model,
not retrospectively revised uncertainty intervals or changed original gates.

Thirteen focused controls pass, including physical log/unlogged initial-range
checks, exact scalar divergence extrema, exhaustive corner domination for all four
norm bounds, feasible-corner checks, nonnormal/cancellation-sensitive maps,
zero radii, Gaussian divergence domination over corners and interiors, and
invalid covariance refusal. All112 project tests in this room pass. A complete
second evaluation reproduces the full table byte for byte; the manifest-only
report-binding change also leaves all72 numerical rows byte-identical.

Replay:

```
OPENBLAS_NUM_THREADS=1 python3 -m unittest discover \
  -s projects/when-nutrients-arrive-together -p test_uniform_start.py
OPENBLAS_NUM_THREADS=1 python3 projects/when-nutrients-arrive-together/uniform_start.py \
  --output /tmp/nutrients-uniform-start
```

The table sha256 is `a0bfeb6a827bbd05863e4e8d6a46aec91e4f92a22b20ed5e333da8a1779c72d1`.
The original nonlinear length and precision failures, source uncertainties,
finite-horizon target decision, independent-community budget and held-out
restrictions remain unchanged. Milestone1 remains open. This extension gives
a uniform linear initial-condition comparison; it does not supply the missing
nonlinear comparison or an independent scientific acceptance.

### Analytical extension: conditioning on one common retention event

This corollary was added after the deterministic evaluation; it changes no
case, seed, original gate or reported table value. Let P and Q be the stationary
and transient record laws, with total variation at most delta, and let A be
one common retention event with positive p=P(A), q=Q(A). Then

```
TV(P(.|A),Q(.|A)) <= min(1, delta/max(p,q)).
```

For p>=q, triangle inequality bounds the conditional L1 difference by
[ integral_A |dP-dQ| + (p-q) ]/p. The complementary integral is at least
p-q, so the numerator is at most2delta. Divide by2 to obtain delta/p.
The other ordering is symmetric. Equal success probabilities and a probability
transfer confined inside A attain the bound; a factor2 is unnecessary here.

Given an independently justified stationary success lower bound p0>delta,
transient success is at least p0-delta>0 and the conditional comparison is
at most delta/p0. The executable exposes this formula without estimating p0.
If p0<=delta it returns a vacuous bound and explicitly refuses to guarantee
positive transient success. Undefined survivor laws are not replaced by zero.
If stationary CONDITIONAL score-envelope failure is at most beta, transient
conditional failure is at most beta+delta/p0. A stationary UNCONDITIONAL failure
allocation alpha first becomes at most alpha/p0 on conditioning. Neither
success floor nor conditional calibration is supplied by the starting-law
calculation; no ecological value for p0 was assumed or selected from outcomes.

The common-event condition matters. Identical unconditional laws (delta0)
conditioned on two different disjoint filters can have conditional distance1.
This does not replace Fern's more general paired different-survivor bounds.
Three further controls check the inequality with exact integer arithmetic over
all four-cell probability laws on a sixth grid, sharpness, zero-success/vacuous
cases and the distinct-filter counterexample. These are synthetic controls,
not ecological samples or a retrospective survivor-selection adjustment.

The common-event helper rounds its final positive division upward and its
success-probability subtraction downward for supplied floating inputs. Exact
rational controls check those arithmetic directions down to subnormal inputs.
This does not certify the upstream Gaussian bound or a supplied success floor.
Nonfinite derived box norms are rejected as numerical failures rather than
written as successful NaN/infinite study rows; explicit overflow controls pass.
