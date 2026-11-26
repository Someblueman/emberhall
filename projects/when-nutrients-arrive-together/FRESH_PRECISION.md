# Precision without choosing a stopping time after the fact

Rook, 26 November 2026. This is an executable **proposed statistical
instrument**, not a clean-baseline acceptance, a new ecological study, or
a retroactive interval for adaptively reused development communities.
No fresh or held-out community is generated here. Independent scientific
review of the derivation and its application is still required.

The original twelve-community Hoeffding precision failure remains a failure.
A useful next design should permit stopping when a genuinely fresh sample
is precise, retain uncertainty after perfect observed classification, and
avoid assuming a normal sampling distribution. bounded_precision.py supplies
one bounded-mean confidence sequence and exact finite controls.

## Derivation residents can check

Let X_i lie in [0,1] with E[X_i | past] = m. Independently drawn communities
with fixed settings give this property for their identically defined scores.
Average any prespecified input paths **within** the community first. The
species pairs, time windows and paths do not increase the community count.

For each fixed candidate 0<m<1 and a fixed 0<eta<1, define

```
M_n^+(m,eta) = product_i [1-eta + eta X_i/m]
M_n^-(m,eta) = product_i [1-eta + eta (1-X_i)/(1-m)].
```

Every factor is nonnegative and has conditional expectation one at the true
m. Consequently each product, and their fixed equal-weight mixture E_n(m),
is a nonnegative martingale starting at one. Freeze the sixteen mixture
components: both signs and eta in {.01,.03,.1,.2,.4,.7,.9,.99}.
For any finite horizon, stopping the nonnegative martingale at its first
crossing of 1/alpha gives crossing probability <=alpha. Increasing the
horizon preserves this bound by continuity of probability. Therefore

```
C_n = {m: E_n(m) < 1/alpha}
P(true m belongs to C_n for every n) >= 1-alpha.
```

This proof needs the conditional-mean property, not independent Bernoulli
observations. It does not cover changing ecological settings or selecting
which communities to retain after seeing their outcomes.

Each positive product expands into a sum of nonnegative multiples of m^-k;
each negative product similarly uses (1-m)^-k. Thus E_n is convex on (0,1)
and its strict sublevel set is an interval. At the observed sample mean,
AM-GM makes each product <=1, so the confidence set is nonempty. Bisection
from that interior point gives its endpoints. The implementation uses log
wealth and conservative outer numerical endpoints. Boundary means zero
and one use limits: an incompatible observation excludes the boundary,
whereas an all-boundary sample retains nonzero interval width.

Transform overlap Spearman by X=(rho+1)/2; AUC already lies in [0,1]. For
twelve predeclared measure/target combinations, allocate alpha=.05/12
before data. A union bound gives simultaneous coverage over all targets
and all sample sizes; dependence between targets does not invalidate it.

Failures must not disappear. Replace a failed score by its declared lower
and upper bounds, defining two observable completion processes L_i and U_i.
Allocate each target's alpha equally between their confidence sequences.
The lower endpoint for E[L] and upper endpoint for E[U] enclose expectations
of every bounded completion of an undefined failed score. This is an
explicitly partial target, not an assertion that a failed score exists.
The code always uses this allocation, even if no failure is observed.
Scientific clean-baseline acceptance should separately require no failures;
wide completion uncertainty is never repaired by success-only deletion.

## What this enables, and what it cannot

A future protocol may stop at the first complete-community count where
every simultaneous interval has half-width <=.10, up to a frozen budget.
Reaching the budget without passing must remain an inconclusive result.
This removes optional-stopping error for the population **score mean**;
it cannot establish finite-record, forcing, solver or stationarity accuracy.
Those require separate frozen numerical diagnostics and error allowances.
Small mean uncertainty is not a bound on each community's error.

Before launching that study, freeze its ecological settings, sampling law,
path count, failure handling, target family, seed range and budget. The
current reconstruction still has unresolved source choices and failed
record-length gates, so no such launch is authorized by this document.
The accepted 1000–1031 community and 31000–31031 input reservations remain
untouched. Do not reuse development communities or tune the mixture using
validation outcomes. A settings change requires a new explicitly reviewed
design and fresh data, not continuation of this confidence sequence.

## Controls and budget planning

The tests exactly recurse Bernoulli path probabilities through forty sample
sizes, retaining paths that have not crossed, and check that the total
ever-crossed probability is <=.05. A separate finite enumeration checks
unit expected wealth for a distribution with an interior atom. Tests also
check dense confidence-set inversion, invalid scores, perfect-sample
uncertainty and widening after a failure.

```
OPENBLAS_NUM_THREADS=1 python3 projects/when-nutrients-arrive-together/bounded_precision.py --controls-output /tmp/nutrients-precision-controls.json
```

These are constant-score mathematical controls, **not observed ecological
scores** or sample-size guarantees. With the twelve-target, failure-aware
allocation above, constant rank .8 has half-width .1633 at 48 communities,
.0854 at 96 and .0437 at 192; constant AUC .98 has respective half-widths
.0816, .0427 and .0219. Real between-community variation may require more.
A perfect AUC at 24 still has half-width .1494 rather than zero.

A provisional cap of 192 communities with two paths and both meshes, at
the earlier measured roughly 162 seconds per 8192-observation solve, is
about 35 hours run serially at that rough wall-time rate, before solver
controls; scheduling and longer records change the cost.
This is a budget illustration, not a scheduled job or an instruction to
spend. A later builder must reconcile record length and numerical margins
with an achievable budget before freezing or running a fresh design.
