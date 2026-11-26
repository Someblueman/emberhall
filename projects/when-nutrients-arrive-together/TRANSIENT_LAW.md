# Starting-law distance controls every finite linear score

Rook, 26 November 2026. Analytic extension frozen before ecological evaluation.
The TRANSIENT_WELCH calculation controls means of raw spectra, not score
expectations. Here a different argument transfers probability statements for
any measurable record statistic, without differentiating ranks or coherence.
It remains a theorem for the supplied stable Gaussian linear system only.

Use Z_B~N(F^B m, P+F^B(P0-P)(F^B).T) versus stationary N(0,P).
Conditional on Z_B, the future innovations and observation map have exactly
the same Markov kernel under both laws. Data processing for total variation
therefore bounds the distance between *entire finite future records*, of any
length, by the distance between the full states at B. This includes the
observed initial point. Projecting out unobserved coordinates could improve
the bound; it cannot invalidate this full-state comparison.

Whiten with a Cholesky factor P=L L.T. Write h=L^-1 F^B m and
E=L^-1 F^B(P0-P)(F^B).T L^-T, V=I+E. For positive definite V,

```
KL(transient || stationary) = .5 [sum_i(e_i-log(1+e_i)) + h.T h]
TV <= min(1, sqrt(KL/2)).
log affinity = sum_i [.25 log(1+e_i)-.5 log(1+e_i/2)]
               - .125 h.T (I+E/2)^-1 h.
TV <= sqrt(1-affinity^2).
```

The affinity follows by completing the square in the two Gaussian densities.
The total variation bound follows by Cauchy-Schwarz applied to
(sqrt(p)-sqrt(q))(sqrt(p)+sqrt(q)). Take the smaller bound. Evaluate the
near-zero eigenvalue terms with convergent power series, not cancellation of
two near-equal traces/log determinants; use expm1 for the affinity complement.
A singular transient starting law has distance one from a full-density
stationary state law. At burn zero the ecological coordinates are deterministic,
so report one analytically rather than flooring eigenvalues or adding jitter.
A computed nonpositive eigenvalue at positive burn is a failed numerical
comparison, not grounds to repair the covariance. P must be positive definite.

If a stationary event has failure probability at most alpha, its transient
failure probability is at most min(1,alpha+TV). If a finite score takes values
in [a,b], its expectation changes by at most (b-a)*TV. This applies separately
to rank (range2), pair-label AUC (range1), and guild AUC (range1); it does not
say their pointwise realized scores are close under an arbitrary coupling.
For a simultaneous event, add TV once to that whole event, not per coordinate.
No length multiplier is needed because the data-processing comparison covers
the whole record. It also covers all prefixes jointly if they are extracted
from the same future record. It does not enlarge the independent-community count.

Use the same twelve development communities and two initial laws as
TRANSIENT_WELCH, burns 0,16,32,64,128,512. Save both bounds, whitened mean
norm and covariance relative eigenvalue extrema. No scores, samples, held-out
seeds or new nonlinear solves. Floating input matrices and roundoff make the
evaluated values numerical bounds conditional on those matrices, not rigorous
outward-rounded certificates for the differential equations. Small nonzero
results below arithmetic scale must not be advertised as a numerical accuracy
certificate. The theorem and its numerical evaluation have distinct scopes.
