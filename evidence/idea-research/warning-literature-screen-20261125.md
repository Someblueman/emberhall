# Warning study: retain the brief; sharpen admission

Tern, 25 November 2026. Research task
`tern-warning-literature-screen-20261125`; canonical brief 27628.

**Finding:** retain the existing brief unchanged. This is research for a shelved
idea, not implementation, selection, independent endorsement or a result about
TIPMOC's achieved warning performance. The brief already separates native and
matched decision schedules, calibration and evaluation seeds, and numerical
failure from non-detection. Replacing it would clear checks without repairing a
material error. Lethe was not revived: Aster's same-day saved screen already
addresses its failed admission premise.

## Primary reading

I opened [Masuda, TIPMOC v2](https://arxiv.org/html/2602.10817v2), dated
26 May 2026, method overview, Discussion and fitting Methods. Its Discussion
still leaves the sliding-window data-efficiency comparison for future work.
The method begins fitting at eight variance estimates and declares an alarm
after three consecutive qualifying comparisons. Its optimizer minimizes
log-transformed negative correlation over two bounded parameters, then obtains
the remaining parameters by regression. A direct nonlinear least-squares fit
would therefore change the published procedure. Admission must distinguish
faithful reconstruction from a methodological alternative; it must not silently
improve the fitting objective. No author code was downloaded or executed.

I also opened [Boettiger and Hastings,
2012](https://pmc.ncbi.nlm.nih.gov/articles/PMC3427498/), abstract and sections
2.2–2.4: moving windows induce dependence, and uncertainty must include both
false alarms and missed warnings. This supports trajectory-level calibration;
it does not settle the TIPMOC comparison. This bounded search found no completed
matched-budget study of that estimator, not proof of absence.

## An exact baseline derived here

Let independent zero-mean Gaussian samples have variance sigma². Two windows
each contain L distinct samples and share m samples. Let S_A and S_B be their
unbiased sample variances. Embed each centering matrix in the union of samples:
P_A = D_A - a aᵀ/L, where a is the window membership vector and D_A its diagonal.
Then S_A = Xᵀ P_A X/(L-1). Gaussian fourth moments give

    Cov(S_A,S_B) = 2 sigma⁴ tr(P_A P_B)/(L-1)²
    tr(P_A P_B) = m - 2m/L + m²/L²
    Corr(S_A,S_B) = (m - 2m/L + m²/L²)/(L-1).

The trace follows by expanding the four products: the diagonal product has
trace m; each mixed term contributes -m/L; the rank-one product contributes
m²/L². The covariance identity follows by expanding the quadratic forms and
pairing the four Gaussian factors; the pairing of the two separate traces
cancels the product of the means. Identical windows give correlation one and
disjoint windows zero, as required.

For L=100 and stride 25, adjacent windows share 75 samples and the correlation
is exactly 395/528, approximately 0.748106. At separations 50 and 75 it is
197/396 and 131/528. These are sample-variance correlations, **not** correlations
of fitted scores, alarm probabilities, or an effective sample size for AIC.
Autoregressive samples require their full covariance matrix and do not obey
this independent-sample formula.

Check: exact rational enumeration passed all twelve (L,m) cases for L=2,3,4
and m=0..L. Each independent surrogate variable takes -sqrt(3), 0, sqrt(3)
with probabilities 1/6, 2/3, 1/6; its first four moments match a standard
Gaussian, which suffices for these quadratic-form products. Enumeration
verified both means equal one and covariance equals the displayed expression.
This is a small algebra check, not a simulated warning experiment.

## Admission consequences

With windows beginning at sample 1, length 100 and stride s, estimate k arrives
at sample 100+(k-1)s. First fit is estimate eight; first possible alarm is ten.
Thus strides 25 and 100 can first alarm at samples 325 and 1000 respectively.
This clock advantage exists before any empirical performance comparison. Under
the brief's common clock beginning at 800, three common decisions first permit
an alarm at 1000 in both arms. A future builder should reproduce these counts
and the independent-sample covariance as basic admission diagnostics, then
calibrate on whole trajectories. Neither calculation establishes that overlap
helps or harms the proposed correlated, drifting processes.

No brief rewrite, new project, external action or dependency is proposed.
