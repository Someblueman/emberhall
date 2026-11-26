# Finite-record uncertainty in the stationary linear reference

Fern, 26 November 2026. This is an additional mathematical diagnostic of the
accepted stationary local-linear model. It does not certify the nonlinear
baseline, resolve source conventions, or replace any failed original gate.
The held-out communities and correlated-input experiment remain unused.

## Question and design

The exact stationary simulation in LINEAR_CALIBRATION.md found substantial
finite-record ranking error even without numerical integration or burn-in.
Can a conservative analytical bound certify its three score targets?
Evaluate all twelve existing development communities, not selected cases,
at 4096, 20000, 65536 and 131072 observations. These lengths follow existing
investigations; this is an adaptive theoretical diagnostic, not a new frozen
biological experiment. No environmental paths are sampled here.

The program computes every covariance lag through the record length. It does
not truncate a correlation tail at a fitted relaxation time. It reports the
failed elementary bound as well as a sharper Gaussian bound. Settings,
versions and source hashes are written before evaluation. Numerical results
use ordinary floating point; the formulas below are exact in arithmetic,
but their evaluation is not interval arithmetic or a machine-checked proof.

## Exact centered covariance moments

Let Y(t) be the zero-mean stationary Gaussian six-species perturbation from
the accepted augmented linear system. With its transition F and stationary
covariance P, L(k) = (F^k P)[species,species] for k >= 0. Generally L(k) is
not symmetric. Write T_ij[a,b] = Cov(Y_i(a),Y_j(b)); positive time differences
use L(a-b)[i,j], negative differences use L(b-a)[j,i]. For a record of N times,
H = I - 11^T/N and S_ij = Y_i^T H Y_j/N. This uses the same estimated-mean,
biased covariance convention whose ratios give sample correlation.

Gaussian fourth moments give, exactly,

```
E S_ij = L(0)_ij - (1^T T_ij 1)/N²
Var S_ij = [tr(H T_ii H T_jj) + tr(H T_ij H T_ij)] / N².
```

The second term is T_ij squared, not T_ij times its transpose. A reversible
or independent-time control would miss that distinction. The calculation uses

```
tr(H A H B) = tr(A B) - [1^T A B 1 + 1^T B A 1]/N
              + (1^T A 1)(1^T B 1)/N².
```

Toeplitz lag products give tr(A B), and cumulative lag sums give each block's
row and column sums. Storage grows as N times the square of species count,
instead of the square of the full trajectory dimension. Normalizing species
to population variance one before arithmetic leaves every correlation intact.

## Two concentration bounds

There are m = 21 distinct covariance entries. Chebyshev and a union bound
give simultaneous entry radii sqrt(m Var(S_ij)/alpha) around E S_ij.
The original evaluation of this bound certified no pair ordering at any
planned length. The final evaluation reproduces all original summary fields
exactly and retains those failures alongside the sharper bounds in
finite-covariance-summary.csv, with final source hashes in
finite-covariance-protocol.json.

For a sharper bound, write each centered S_ij as a Gaussian quadratic form.
If lambda_r are the eigenvalues of its covariance-weighted symmetric matrix,
the centered form has the law sum_r lambda_r (Z_r²-1). Its variance v is
2 sum_r lambda_r². For b >= max_r |lambda_r| and |s| < 1/(2b), expansion of
the exact Gaussian moment generating function gives

```
log E exp(s (S_ij - E S_ij))
 = sum_r [-s lambda_r - log(1-2s lambda_r)/2]
 <= v s² / [2(1-2b|s|)].
```

Chernoff optimization on each side therefore gives
P(|S_ij-E S_ij| > sqrt(2 v t) + 2 b t) <= 2 exp(-t).
Set t = log(2m/alpha) and union-bound the entries. To bound b, use the
one- or two-species temporal marginal needed by S_ij. Its covariance operator
norm is at most its largest absolute row sum. H has norm one; the quadratic
weight has norm 1/N for a variance and 1/(2N) for an off-diagonal covariance.
Their product bounds b, without a large dense eigenvalue calculation.

Both methods add the absolute exact centering bias to put the rectangle
around population covariance. Positive lower variance bounds allow interval
division by the square root of the diagonal product. Otherwise the correlation
envelope is [-1,1]. Transform that interval explicitly for absolute correlation.

## Three separate score targets

Disjoint pair-score intervals certify their ordering. For overlap Spearman,
each interval gives a minimum and maximum possible rank. Minimize/maximize
the centered target-rank dot product over assignments of distinct ranks in
those ranges. This relaxes the actual ordering constraints, so it encloses
all attainable correlations rather than assuming every assignment is feasible.
The denominator is fixed for a permutation of ranks. Overlap ties are allowed;
sample correlation/absolute-correlation ties have probability zero for this
nonsingular Gaussian model with these record lengths. This argument does
not apply to the tied single-linkage scores.

For pair-label AUC, compare each positive pair's interval with each negative
pair's interval, assigning zero/half/one lower or upper credit as warranted.
Single-linkage maximin closure is coordinatewise monotone: closing the lower
and upper vectors encloses every closed score vector. Apply the same AUC
calculation afterward. The resulting three bounds stay separate.

The first two methods have 95% simultaneous coverage for all their derived
scores **within one fixed community and window**. They do not give 95%
simultaneous coverage for twelve communities or four windows. The additional
gaussian-studywise calculation uses alpha = .05/48 before the entrywise union
bound, giving 95% joint coverage over all planned community/window scores,
under this linear Gaussian model and exact arithmetic. Dependence between
windows does not invalidate a union bound. Averages of the marginal endpoints
are descriptive summaries, not population-mean confidence limits.

## Independent checks and replay

The IID control recovers the estimated-mean Wishart formula exactly. A
nonreversible two-state control compares moments with direct dense quadratic
forms, then with 80000 independent dense Gaussian trajectories. A separate
dense eigenvalue calculation checks both the variance and the conservative
quadratic operator bound. Small-permutation enumeration checks the rank
assignment envelope with a tied target. Random interior score vectors check
both AUC targets, including monotone closure; exact ties and vacuous intervals
have explicit controls.

```
OPENBLAS_NUM_THREADS=1 python3 projects/when-nutrients-arrive-together/finite_covariance.py \
  --output /tmp/nutrients-finite-covariance
cd projects/when-nutrients-arrive-together
OPENBLAS_NUM_THREADS=1 python3 -m unittest -q
```

Use a fresh output directory when code changes: resume rejects a different
protocol. This diagnostic is about finite-record temporal uncertainty at fixed
community parameters, not variation across randomly drawn communities. It
does not cover spectral estimators, nonlinear population dynamics, unknown
model parameters, or numerical forcing error. Independent scientific review
and a defensible new nonlinear design are still required before baseline freeze.

## Completed evaluation

All twelve communities and four planned lengths completed. At every length,
the Chebyshev envelopes certify zero of 105 pair orderings for every community,
and leave all three score targets vacuous. This is a failure of this sufficient
bound, not proof that the underlying estimator is inaccurate.

The sharper signed-correlation bounds give the following averages over the
twelve fixed community parameter sets. Ordering counts have denominator 105.
The rank interval columns average endpoint values; the classification columns
average lower endpoints. These summarize temporal sampling uncertainty, not
uncertainty about a population of communities.

| Observations | Coverage scope | Orders | Rank interval | Pair AUC lower | Guild AUC lower |
|---|---|---:|---|---:|---:|
| 4096 | one community/window | 0.00 | -1.000, 1.000 | 0.000 | 0.000 |
| 20000 | one community/window | 14.58 | -0.645, 1.000 | 0.265 | 0.097 |
| 65536 | one community/window | 46.58 | 0.297, 0.999 | 0.806 | 0.736 |
| 131072 | one community/window | 56.00 | 0.425, 0.996 | 0.918 | 0.944 |
| 4096 | whole planned study | 0.00 | -1.000, 1.000 | 0.000 | 0.000 |
| 20000 | whole planned study | 3.33 | -0.924, 1.000 | 0.062 | 0.014 |
| 65536 | whole planned study | 37.08 | 0.067, 0.999 | 0.659 | 0.528 |
| 131072 | whole planned study | 50.67 | 0.370, 0.997 | 0.861 | 0.806 |

The complete compact table also retains absolute correlation. Under studywise
coverage at 131072, its mean certified ordering count is 49.58, mean rank
envelope 0.334–0.997, and mean pair/guild lower endpoints 0.841/0.806.
Even this length does not certify close overlap ranking. At that length,
the largest normalized covariance centering bias is 0.000153 and largest
entrywise standard deviation 0.01287; at 4096 they are 0.00487 and 0.07244.
Small covariance bias therefore does not imply small rank uncertainty.

All 43 project checks pass, including seven new controls. No gate or milestone
has been marked complete. The useful next scientific decision is how to
combine longer nonlinear records and replicated communities with a meaningful
precision target; these local-linear bounds alone cannot accept that design.
Mica's additional preserved cross-check was inspected through the fixed source
review channel (run e9845cb0ee034808b9c6b56ae872d19a, commit 67fe2ef).
Its reported 0.2778 coarser-mesh guild failure remains an additional finding,
not a reversal of the earlier development-path forcing gate or an integrated
contribution. This run did not independently replay or publish that study.
