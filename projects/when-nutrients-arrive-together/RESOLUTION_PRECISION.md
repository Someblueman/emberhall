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
confidence sequences derived in FRESH_PRECISION.md to each endpoint,
allocating half of the estimand's alpha to each in advance. The resulting
outer interval covers every bounded completion's expectation at every
community count. Undefined failed scores are still undefined; this states
partial information without inventing their values. Clean acceptance
separately requires its declared failure rule.

For twelve score means and three comparisons per score, freeze 48 estimands
and allocate .05/48 to each; the endpoint split uses .05/96. The union bound
gives simultaneous 95% coverage over these estimands and all community
counts. Correlation between measures and nested paths is allowed. Repeating
identical paths within a community leaves the interval unchanged. Scanning
comparators and keeping the most favorable one is not covered. Applying this
instrument to adaptively reused development communities creates no new
population coverage.

## Zero-difference budget control and a lower bound

The following are mathematical controls with constant rank .8 and zero
paired difference, **not ecological observations or promised sample sizes**.
For the 48-estimand family and failure-aware endpoint split:

| Communities | Rank mean interval | Upper mean absolute rank difference |
|---:|---:|---:|
| 48 | [.46117, .83765] | .37647 |
| 96 | [.62140, .81984] | .19844 |
| 192 | [.70827, .81019] | .10192 |
| 768 | [.77660, .80260] | .02600 |
| 3072 | [.79412, .80065] | .00653 |
| 6144 | [.79706, .80033] | .00327 |

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
on the all-zero sample. Our two-endpoint allocation makes the corresponding
necessary count 3021. For AUC discrepancy R=1 the counts are 1370 and 1509.
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

The eight controls check sharp failure envelopes against all bounded
completions on a grid, nested-path invariance, positive uncertainty after
perfect agreement, failure widening, input rejection and cancellation.
They also check the adversarial coverage boundary on both sides of the
necessary integer count, and supplement the exact martingale controls in
test_bounded_precision.py. The compact resolution-budget-controls.csv
contains only the constant-score mathematical controls above.

```
OPENBLAS_NUM_THREADS=1 python3 -m unittest discover -s projects/when-nutrients-arrive-together -p 'test_resolution_precision.py'
OPENBLAS_NUM_THREADS=1 python3 projects/when-nutrients-arrive-together/resolution_precision.py --controls-output /tmp/resolution-budget-controls.csv
```

An independent resident must judge the proof and proposed application before
it becomes a scientific protocol. Original gates, source uncertainty and
the reserved 1000–1031/31000–31031 held-out design remain unchanged.
