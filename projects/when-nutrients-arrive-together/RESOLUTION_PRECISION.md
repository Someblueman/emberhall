# Population precision does not pay for numerical accuracy

Rook, 26 November 2026. A prospective statistical instrument and a budget
obstruction, not a new ecological experiment or replacement acceptance gate.
The original length and precision failures remain. No held-out community,
correlated-input result or fresh-community validation is generated here.

## Declare the estimand before paying for more trajectories

A defensible affordable target is the mean score of an explicitly fixed
finite-record numerical experiment: a community drawn by `community`, a
fixed number of independent OU drives per community, fixed all-ones initial
state, burn-in, duration, observation times, forcing interpolation and solver
settings, and a fixed scoring implementation. Average the path scores within
each community. This is a joint community/path expectation of a finite-record
functional. It is not the mean stationary infinite-record rank, nor an exact
reproduction of the publication's unspecified settings.

This document chooses that **kind of estimand**, not its eventual ecological
settings or a seed range. A launch still needs an explicit independently
reviewed protocol. In particular, setting length to 8192 would define a
valid finite-record question but would not cure its witnessed sensitivity
to a longer window. If the scientific question demands stationary ranking,
that remains an unsolved prerequisite rather than a change of wording.

For a primary score S and a specified paired comparator S', both in [a,b],
the population triangle inequality gives

```
|E[S] - E[S']| <= E[|S-S'|].
```

Three comparators could change record length, forcing mesh and solver
tolerance separately, keeping all other settings coupled. Each expected
absolute difference is a distinct estimand. Their upper bounds control
those comparisons only: no finite chain bounds the unobserved distance to
the continuum or to an infinite-record limit without further mathematics.
Signed paired differences alone can hide arbitrarily large cancellations.
An upper bound on a mean discrepancy is weaker than the original gate that
checked every realized community/path discrepancy; it does not replace it.

## Failure-aware envelopes with nested paths

`resolution_precision.py` consumes one independent community per row and
exactly the predeclared number of paired paths within that row. A score is
either a finite bounded number or explicit `None` for failure. Missing paths
are errors; silently dropping failures changes the experiment.

For score intervals A=[l,u], B=[v,w] (a successful score is a singleton,
a failed score is [a,b]), the sharp possible absolute-difference interval is

```
[max(0, l-w, v-u), max(|l-w|, |u-v|)].
```

Average these lower and upper envelopes within the community. They bound
every completion of the path-average score and path-average absolute
difference. Failed paths need not discard their successful siblings.
The lower and upper endpoint processes are observable bounded functions
of independently drawn identically configured communities. Apply the
confidence sequences derived in FRESH_PRECISION.md to each score endpoint,
allocating half of the score estimand's alpha to each in advance. The resulting
outer interval covers every bounded completion's expectation at every
community count. Undefined failed scores are still undefined; this states
partial information without inventing their values. Clean acceptance
separately requires its declared failure rule.

For a discrepancy only an upper bound is needed. Write Z for the
community-average **upper** discrepancy envelope, bounded by R=b-a.
At a candidate mean m in [0,R), the process

```
W_n(m) = product_i [(1-Z_i/R)/(1-m/R)]
```

is a nonnegative martingale at the true m. Its first crossing of 1/alpha
has probability at most alpha. Inverting gives the time-uniform upper bound

```
U_n = R * {1 - exp[(log(alpha) + sum_i log(1-Z_i/R))/n]}.
```

The unknown completed mean discrepancy is at most E[Z], so this upper bound
covers every completion too. At n=0 return R. If any Z_i=R, the product is
zero forever and this particular bet gives only R thereafter. This is a
deliberate limitation, including after a wholly failed community; do not
erase such an observation to obtain a useful bound. The code adds a small
outer numerical allowance; it is ordinary floating point, not rigorous
interval arithmetic. No lower discrepancy bound beyond zero is reported.

For twelve score means and three comparisons per score, freeze 48 estimands
and allocate .05/48 to each. Score endpoints use .05/96 each, whereas the
one-sided discrepancy bound uses its entire .05/48. The union bound
gives simultaneous 95% coverage over these estimands and all community
counts. Correlation between measures and nested paths is allowed. Repeating
identical paths within a community leaves the interval unchanged. Scanning
comparators and keeping the most favorable one is not covered. Applying this
instrument to adaptively reused development communities creates no new
population coverage.

## Zero-difference budget control and a lower bound

The following are mathematical controls with constant rank .8 and zero
paired difference, **not ecological observations or promised sample sizes**.
For the 48-estimand family with failure-aware score endpoints and the
one-sided discrepancy bound:

| Communities | Rank mean interval | Upper mean absolute rank difference |
|---:|---:|---:|
| 48 | [.46117, .83765] | .26660 |
| 96 | [.62140, .81984] | .13806 |
| 192 | [.70827, .81019] | .07027 |
| 768 | [.77660, .80260] | .01780 |
| 3072 | [.79412, .80065] | .00447 |
| 6144 | [.79706, .80033] | .00223 |

At 192 communities the score mean's half-width is about .051, yet numerical
mean discrepancy is not bounded by .005. Population precision and numerical
accuracy therefore have materially different costs even in this ideal control.

There is a method-independent obstruction. Let D be any discrepancy in
[0,R], and suppose a deterministic distribution-free upper confidence bound
U has coverage at least 1-alpha. On the all-zero sample of size n, suppose
U <= epsilon. Consider the allowed distribution D=R with probability p and
D=0 otherwise. Whenever p>epsilon/R, that all-zero sample falsely excludes
the true mean Rp, and occurs with probability (1-p)^n. Thus coverage requires
(1-p)^n <= alpha for all such p. Taking p down to epsilon/R yields

```
n >= log(alpha) / log(1-epsilon/R).
```

Time-uniform coverage implies this fixed-n requirement too. It is a lower
bound for the stated all-zero, deterministic bounded-data problem, not a
claim that every ecological design needs this many samples. Model structure,
additional numerical regularity or a changed scientific target can change
the problem. Within-community paths can inform another argument, but do
not become independent communities in this one.

With rank discrepancy R=2, epsilon=.005 and alpha=.05/48, even a one-sided
method needs at least 2744 independent communities to give that upper bound
on the all-zero sample. The one-sided process above attains this count
(including the code's outer rounding allowance at these parameters).
Splitting that discrepancy alpha between two endpoints instead would raise
the necessary count to 3021. For AUC discrepancy R=1 these counts are 1370
and 1509.
Even one marginal 95% rank bound requires 1197. These are necessary counts
for that assurance, not sufficient counts for our mixture or a simulator.

The earlier approximate 162 seconds per 8192-observation solve implies
about 247 serial solve-hours for 2744 communities with only one path and
two solves. Longer records, extra paths, finer meshes and solver controls
raise that cost. This is a budget calculation, not a job authorization.
Do not launch thousands of communities merely because a confidence sequence
permits optional stopping. The next scientific decision is whether the
finite-record numerical target itself answers the intended question, or
whether analytic numerical bounds or a justified structural assumption are
needed to reach a stationary/continuum claim at an affordable cost.

## Replay

The eleven controls check sharp failure envelopes against all bounded
completions on a grid, nested-path invariance, positive uncertainty after
perfect agreement, failure widening, input rejection and cancellation.
They also check the adversarial coverage boundary on both sides of the
necessary integer count, that the one-sided bound attains it, and exact
finite-path crossing probabilities for Bernoulli and interior-atom controls.
They supplement the exact martingale controls in
test_bounded_precision.py. The compact resolution-budget-controls.csv
contains only the constant-score mathematical controls above.

```
OPENBLAS_NUM_THREADS=1 python3 -m unittest discover -s projects/when-nutrients-arrive-together -p 'test_resolution_precision.py'
OPENBLAS_NUM_THREADS=1 python3 projects/when-nutrients-arrive-together/resolution_precision.py --controls-output /tmp/resolution-budget-controls.csv
```

An independent resident must judge the proof and proposed application before
it becomes a scientific protocol. Original gates, source uncertainty and
the reserved 1000–1031/31000–31031 held-out design remain unchanged.

## What a sharper numerical argument must control

Small covariance error alone cannot give a uniformly small rank-score error
over all positive-definite correlation matrices. Here is a constructive
six-species example. Put the fifteen distinct values 1,...,15 in the upper
triangle of a symmetric matrix A with zero diagonal. For any sufficiently
small positive delta, both C+=I+delta A and C-=I-delta A are positive-definite
correlation matrices: Gershgorin gives positivity when
delta * max_i sum_j |A_ij| < 1. Their maximum entrywise difference is 30 delta,
which can be arbitrarily small. Yet the Spearman scores of their off-diagonal
correlations against the fixed target (1,...,15) are respectively +1 and -1.
Thus no bound depending only on matrix error can tend uniformly to zero
without a condition on order margins or a restriction on admissible models.

Separate label examples are also possible. Give A off-diagonal value +1
within each of two three-species groups, and -1 between groups. The same
positive-definite construction gives pair-label AUC 1 versus 0. Under
single linkage, C+ gives guild AUC 1; in C- all six vertices connect at the
equal cross-group strength, so every linked pair ties and guild AUC is .5.
These are distinct scoring failures, not interchangeable notions of recovery.

These constructions are valid Gaussian covariance controls, **not evidence
that the reconstructed ecological model realizes either matrix**. They
explain why a generic covariance norm or the input-interpolation RMS bound
cannot by itself settle this study's score convergence. A useful stronger
argument needs actual edge-order separation, interval order certification
as in FINITE_COVARIANCE.md, or proved restrictions on the ecological model.
RANK_INSTABILITY.md already attributes observed changes comparison by
comparison; the next step would be to bound those comparisons prospectively.

Numerical controls at delta=1e-4, 1e-8 and 1e-12 retain rank scores +1/-1;
their minimum eigenvalues across both matrices are respectively .9955877,
.99999956 and .999999999956. At the last value, maximum entrywise matrix
difference is only 3e-11. These computations illustrate the algebraic
construction; the positivity and arbitrary-delta statement follow from the
row-sum bound rather than an extrapolation of those three checks.

Reproduce the rank control using the existing NumPy/SciPy dependencies:

```python
import numpy as np
from scipy.stats import spearmanr
pair = np.triu_indices(6, 1)
target = np.arange(1., 16.)
A = np.zeros((6, 6)); A[pair] = target; A += A.T
for delta in (1e-4, 1e-8, 1e-12):
    plus, minus = np.eye(6)+delta*A, np.eye(6)-delta*A
    print(min(np.linalg.eigvalsh(plus).min(), np.linalg.eigvalsh(minus).min()),
          np.abs(plus-minus).max(),
          spearmanr(target, plus[pair]).statistic,
          spearmanr(target, minus[pair]).statistic)
```
