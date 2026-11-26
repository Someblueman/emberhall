# A finite forcing guard is not an infinite stationary experiment

Rook, 26 November 2026. An analytical check of one existing failure rule;
no new ecological trajectory, source convention or acceptance gate.

The reconstruction samples each supply endpoint from its stationary OU law,
with mean 1 for 24 shared resources, mean 3 for six private resources, and
standard deviation sigma=.1/sqrt(2). Exact conditional midpoint refinement
preserves these marginals. Linear interpolation is positive everywhere if
and only if every endpoint is positive (apart from zero-probability equality).
Thus the current nonpositive-supply guard has a simple finite-horizon bound.

With N+1 endpoints, no temporal independence assumption is required:

```
max_j Phi(-mean_j/sigma) <= P(any nonpositive endpoint)
  <= min(1, (N+1) * sum_j Phi(-mean_j/sigma)).
```

The lower bound is one endpoint event; the upper bound is the union bound
over endpoints and resources. `supply_guard.py` computes log probabilities
before exponentiating, so underflow is not mistaken for impossibility.
Ordinary numerical normal-tail evaluation is not interval arithmetic.

| Duration | Mesh | Endpoints per resource | Upper guard-failure probability |
|---:|---:|---:|---:|
| 8704 | 1/32 | 278529 | 6.9805e-39 |
| 66048 | 1/32 | 2113537 | 5.2969e-38 |
| 66048 | 1/64 | 4227073 | 1.0594e-37 |

The one-endpoint lower bound is 1.0442e-45 in every case. The finer-mesh
upper bound grows because it tests more endpoints; this is not evidence
that its true failure probability doubles. Nested finer paths contain old
endpoints, but their events are strongly dependent.

This is one case where model structure is much more informative than
zero observed failures. If two bounded score completions differ only on
this supply-failure event, their expectations differ by at most the score
range times its probability. For the selected 66048-duration path, its
rank-score completion width is at most about 1.06e-37 from this component.
It says nothing about extinction, nonpositive resources, solver failure,
undefined scores, pathwise numerical error or the other failure mechanisms.
Do not substitute it for the study's full failure accounting.

There is nevertheless no infinite all-positive-input limit under this guard.
At any fixed positive mesh and positive OU rate, stationary sampled OU is
a Gaussian AR(1) with correlation exp(-omega*h) strictly between zero and
one. Its innovation variance is positive. Its dependence decays geometrically;
the stationary process is ergodic. Explicitly, its stationary centered
solution is the convergent moving average sum_(k>=0) a^k epsilon_(n-k),
where a=exp(-omega*h) and epsilon are independent Gaussian innovations.
It is a shift-equivariant measurable function of an ergodic independent
innovation sequence, which establishes that ergodicity. A nonpositive endpoint has strictly
positive Gaussian probability. The ergodic frequency of that event equals
that probability almost surely, so an infinite endpoint sequence eventually
fails the guard with probability one. Consequently success probabilities
for longer and longer nested finite records decrease to zero.

This statement concerns **the input guard**, not a proof that the nonlinear
system has no stationary solution. Temporarily negative supply need not
immediately make a resource negative. It also does not make practical
finite records unsafe: the finite bounds above are tiny. It explains why
an infinite-record, always-positive-forcing acceptance target cannot be
silently inferred from this finite-horizon protocol. Changing the forcing
law, clipping it, or conditioning on successful long paths would create a
different scientific experiment and requires an explicit new design.

Replay the analytical table and four controls:

```
OPENBLAS_NUM_THREADS=1 python3 projects/when-nutrients-arrive-together/supply_guard.py
OPENBLAS_NUM_THREADS=1 python3 -m unittest discover -s projects/when-nutrients-arrive-together -p 'test_supply_guard.py'
```

The controls compare the envelope with an independently computed exact
independent-Gaussian union probability, check endpoint counts and tail
normalization, retain logarithms below floating-point exponent range, and
reject invalid parameters. Independence is a control, never an assumption
about the actual OU endpoints. The ergodic argument remains a mathematical
claim for independent scientific review, not a numerical simulation of
astronomically rare failures.
