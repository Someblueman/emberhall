# Independent-input reference: reconstruction and pilot contract

Source opened 26 November 2026: Chen, Crocker, Kuehn, Walczak and Mora,
[*Inferring Resource Competition in Microbial Communities from Time Series*,
PRX Life 3, 023019 (2025)](https://journals.aps.org/prxlife/pdf/10.1103/8gkj-rdzy),
CC BY 4.0. No source code was downloaded or executed.

## Source reconstruction

Equations (1–2) give consumer growth and resource depletion:
`d log(x)/dt = G R - dx`, `dR/dt = K - (dR + r.T x) R`, with
`G = r * yield`. Equations (6–8) specify additive, resource-independent OU
supply deviations, `dQ = -omega Q dt + A sqrt(omega) dW`.
Thus stationary variance is `A²/2`, not `A²`. Equations (14–15) integrate
absolute cross-power and magnitude-squared coherence. Section IV.A uses
uptake 0.1, positive normal yields (mean 1, deviation 1/6), consumer death
0.3 and resource decay 0.5. The small community has six species, thirty
resources, two guilds and private resources. The paper compares overlap
ranking separately from clustering-based guild detection; its full long-record
experiments are not reproduced here.

## Our frozen pilot choices

These choices are ours, not claimed as the authors' exact settings. There are
24 shared and six private resources. Three consumers per diet group choose
shared resources independently with probabilities 0.9 within and 0.1 outside
the preferred block. Private uptake is a diagonal matrix. Yields are sampled
independently using a positive normal redraw. Supply means are one for shared
resources and three for private ones; OU amplitude is 0.1 and rate is one.
Initial consumer and resource amounts are one. These supply and initial
conditions need comparison with the supplement before a numerical replication
claim. Private resources reduce extinction risk but do not prove coexistence.

Seeds 0–3 independently draw both community and input path; input seeds are
10000–10003. No seed is selected by score. Simulation spans 1536 time units,
discards the first 512, and samples log absolute abundance every unit. This is
a pilot, not the paper's 20000-unit experiment. No relative-abundance claims,
real-community claims, or correlated-input results follow from it.

OU transitions are exact on a stationary 0.125 mesh. Linear interpolation
between mesh points is an explicit approximation to continuous OU forcing.
The main run subsamples the same path onto a 0.25 mesh. Two adaptive RK45
solves use maximum steps 0.25 and 0.125 and relative tolerances 1e-6 and 1e-8.
A third uses the finer forcing mesh at the tighter solver setting. Reported
trajectory RMS and score changes distinguish solver from forcing resolution.
There is no clipping, reflection or resampling of negative supplies. Any
nonpositive supply, resource failure, or abundance below 1e-8 fails the entire
seed and appears in the report. Failures invalidate a clean-baseline claim;
success-only summaries are conditional if any seed fails.

## Scoring and uncertainty

Each species' log abundance is standardized over the retained window. Metrics
are signed equal-time correlation, absolute correlation, integrated absolute
cross-power, and integrated coherence. Our Welch implementation uses SciPy,
a Hann window, constant segment detrending, half overlap, one-sided density,
and a rectangular frequency sum including DC and Nyquist. Thirty samples per
segment give frequency spacing 1/30; segments of 16 and 60 are retained as
sensitivity checks. This does not assert MATLAB-toolbox equivalence.

Overlap ranking is Spearman correlation against the fifteen off-diagonal
entries of `G G.T`. Diet scoring includes pairwise same-diet AUC with tie credit and a distinct
single-linkage guild AUC. For the latter, maximin path weights give the
threshold at which two vertices become connected. An independent
threshold-by-threshold graph search checks this implementation, including
negative weights, ties and isolated vertices. These are threshold-swept
classification scores, not a chosen partition or a claim of perfect recovery. Labels enter scoring only, never spectral estimates.
AUC is checked against perfect, inverted and tied controls. A delayed common
signal provides a spectral positive control alongside independent signals.

Replicate means and Student-t intervals use independent *communities*, not
the fifteen dependent pairs as replicates. Four replicates give very uncertain
pilot intervals, not a precise population estimate. No bootstrap over pairs,
performance threshold selection, or held-out correlated-input testing occurs.
Keep all seeds and inspect convergence before interpreting the means.

## What remains before milestone acceptance

Audit supply parameters, private-resource convention, estimator normalization
and initial conditions against the supplement or authors' archived materials.
Replicate the longer clean experiment with adequate independently seeded
communities, stationarity diagnostics, and an explicit convergence tolerance.
Validate the clustering estimates over more communities. Freeze these decisions and
the held-out protocol before running correlated inputs. Obtain one independent
scientific replay at the milestone; the current pilot is not that review.

## Local linear transfer check

At a positive deterministic equilibrium we differentiate the original equations
in log-consumer and resource coordinates. The resulting blocks are
`J = [[0, G], [-diag(R) r.T diag(x), -diag(0.5 + r.T x)]]`.
A centered finite-difference check of the nonlinear right-hand side verifies
all Jacobian columns. Resource supply enters through `B = [0; I]`.

With independent OU supply, the angular-frequency consumer spectrum is
`H(w) H(w)* A² omega/(omega²+w²)`, where
`H(w)` is the consumer block of `(iwI-J)^(-1) B`.
We integrate its real part from zero to infinity divided by pi. Independently,
we augment the linear system with the OU states and solve the continuous
Lyapunov covariance equation. Agreement checks normalization, forcing power
and transfer algebra. Eigenvalues must have negative real parts; root residual
must be below 1e-10. This calculation is local and does not prove the nonlinear
simulation is stationary or that a finite-window estimator is unbiased.
