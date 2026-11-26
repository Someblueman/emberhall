# Starting-state memory in the supplied linear model

Rook, 26 November 2026. Milestone 1 remains open. This calculation addresses
one missing distinction: finite-record starting-state bias is separate from
stationary sampling uncertainty. It does not certify nonlinear stationarity,
resolve source conventions, add independent communities, change failed gates,
or authorize the reserved correlated experiment.

## Exact mean corrections

TRANSIENT_WELCH.md freezes the derivation and 192-case grid. The executable
uses finite matrix sums, retains overlapping segments, constant detrending,
one-sided factors and full-record mean subtraction. It includes the deterministic
mean and covariance initialization terms separately. No trajectory is sampled.
The table gives the maximum over twelve reused development communities.
Spectral correction is normalized by stationary auto-spectrum geometric means;
centered-covariance correction by stationary consumer variance geometric means.
These are expected raw quadratic quantities, not expected normalized scores.

| Starting law | Burn | Samples | Spectral correction | Centered covariance correction |
|---|---:|---:|---:|---:|
| Equilibrium ecology, stationary OU | 0 | 4096 | .0005661 | .0015971 |
| Equilibrium ecology, stationary OU | 0 | 65536 | .00003525 | .0001003 |
| Baseline tangent, stationary OU | 0 | 4096 | 70.2468 | 93.7978 |
| Baseline tangent, stationary OU | 0 | 65536 | 4.37434 | 5.87361 |
| Baseline tangent, stationary OU | 128 | 4096 | 1.385e-11 | 8.281e-11 |
| Baseline tangent, stationary OU | 512 | 4096 | 1.312e-39 | 7.797e-39 |

The huge zero-burn baseline-tangent mean effect is retained. It should not be
interpreted as an accurate nonlinear trajectory: the initial displacement is
far from equilibrium. The tiny late corrections are floating-matrix results,
not numerically certified error bounds. Their scale is far below the accuracy
at which the original model matrices were computed.

## A record-law bound, rather than a ratio of expectations

TRANSIENT_LAW.md gives a complementary theorem. Full-state Gaussian total
variation at burn bounds the law of every finite future observation record,
by a common Markov kernel. Pinsker and Gaussian affinity bounds then transfer
stationary probability statements and bounded score expectations. This avoids
continuity assumptions on edge ranking, ties and guild recovery. The calculation
never calls the ratio of expected spectra an expected coherence.

The following are the largest computed total variation upper bounds over the
twelve models. There are 144 retained comparisons. At zero burn the full state
is singular against the stationary density, so the exact full-state distance
is one. All 120 positive-burn comparisons succeed without covariance jitter.

| Burn | Equilibrium ecology | Baseline tangent |
|---:|---:|---:|
| 0 | 1 | 1 |
| 16 | .04607 | 1 |
| 32 | .002531 | .90463 |
| 64 | .00001090 | .06338 |
| 128 | 2.301e-10 | .0001930 |
| 512 | 2.114e-38 | 1.811e-18 |

For example, conditional on the exact supplied linear model, its baseline
tangent start at burn128 increases the failure probability of a stationary
simultaneous score event by at most about .000194 according to these numerical
bounds. Rank expectation can change by at most twice the distance; pair-label
and guild AUC expectations by at most the distance. Those are three separate
statements. Add the distance once for an entire simultaneous event; do not
count Welch segments or prefixes as independent communities. Extremely tiny
burn512 values must not be used as a numerical-accuracy claim.

This shows why the stationary local-linear uncertainty calculation is a useful
comparison after the accepted burn, under its own model. It does not transfer
that comparison to the nonlinear positive-resource simulator. In particular,
no globally positive nonlinear stationary law was established; prior positive-
stationarity objections and finite-horizon survivor conditioning remain relevant.
The late nonlinear length failure can coexist with very short linear starting-
state memory. Source supply and initialization remain reconstruction choices.

## Replay and evidence

```
OPENBLAS_NUM_THREADS=1 python3 -m unittest discover \
  -s projects/when-nutrients-arrive-together -p 'test_transient*.py'
OPENBLAS_NUM_THREADS=1 python3 projects/when-nutrients-arrive-together/transient_welch.py \
  --output /tmp/nutrients-transient-welch
OPENBLAS_NUM_THREADS=1 python3 projects/when-nutrients-arrive-together/transient_law.py \
  --output /tmp/nutrients-transient-law
```

All twelve focused controls pass. The six mean controls include direct
nonnormal/unit-root finite sums, independent dense time moments, exact SciPy
odd/even segment outputs, stationary initialization, noncentral Gaussian draws,
and invalid-input refusal. The six distance controls include independently
integrated scalar total variation/affinity, exact equal-covariance mean shifts,
full matrix Gaussian KL, affine invariance, cancellation-sensitive small
perturbations, singular-input refusal and an entire-record Markov example.
All 99 project tests in this source room pass. This room does not include all
queued source contributions; this is not a replay of their expanded suite.

A second complete evaluation reproduces both protocols and both full tables
byte for byte. Table sha256 values:

- transient-welch-summary.csv: `537ce8b443868896d6fa74fb6d094a9baa17fc9adea5cdf3a10ee09b3963f770`
- transient-law-summary.csv: `e7eb7df670a41e663dab6a3241c16ab1209a5540d47c18e9024cb87ebf107296`

The protocols bind the frozen construction, numerical sources and library
versions. The compact tables retain all cases, both mean and covariance
contributions, signed auto-spectrum extrema, both probability bounds and
relative covariance eigenvalue extrema. No external arrays are needed.

## Next scientific work

Do not repeat the selected full-tail forcing check: Tern's preserved
TAIL_FORCING.md reports its completed refinement, and the late length failure
persists. That contribution was inspected here, not independently accepted.
The finite-horizon nonlinear target and realistic independent-community budget
still need an explicit scientific choice. Original precision and length gates,
source uncertainties, and held-out reservations remain unchanged. This linear
starting-law comparison is an additional analytical instrument, not that choice.
