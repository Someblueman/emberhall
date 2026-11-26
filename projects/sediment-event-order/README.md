# Which Ancient Change Came First?

Complete registered synthetic study, 26 November 2026. Read the
[scientific report](SCIENTIFIC_REPORT.md) for the question, results, numerical
failures and limits, and its tested CSV-only reproduction command. The
[full tables and execution history](HELDOUT_RESULTS.md) accompany the
[compact dataset](heldout_results.csv) and [frozen registration](HELDOUT_PROTOCOL.md).

All 128 planned latent draws are accounted for: 3,840 attempted fits, 3,612
passing diagnostics, 228 failures and none missing. Opposite dating offsets
produce substantial coverage loss in both models; the registered comparisons
do not establish a design or method winner. This is a synthetic benchmark,
not a historical climate reconstruction. Independent scientific milestone
review remains open; the first two milestones were accepted at journal 39668
and 40043.

Python 3.10+, standard library only, from the repository root:

```sh
python3 projects/sediment-event-order/heldout_protocol.py --validate --registration-sha 729ae32e453bb4a0dc9ff299428431b1e31a9250b114f21bd5955b4c5197b965
```

Then run the CSV-only command in the scientific report to reproduce all
coverage, declaration, PIT and paired-contrast summaries without new fits.
For the earlier analytic/development checks, run
`python3 projects/sediment-event-order/milestone_check.py`; its recorded scope
is in the [model contract](MODEL_CONTRACT.md). The
[paired executable](PAIRED_EXPERIMENT.md) specifies the complete probability law.

## Single-archive foundation

First executable foundation, 24 November 2026. This is a single-archive,
finite-prior verification baseline for the selected sediment event-order
project. It is **not yet the paired-archive scientific experiment**.

From the repository root, Python 3.10 or later, no dependencies:

```sh
python3 projects/sediment-event-order/baseline.py
python3 projects/sediment-event-order/continuous.py
python3 projects/sediment-event-order/audit.py
python3 -m unittest discover -s projects/sediment-event-order -v
```

The first two commands write reproducible JSON to standard output, defaulting
to 2,000 trials and seed 20261124; `--trials` and `--seed` allow fresh checks.
The audit compares selected observations to an independent numerical integrator.
The recorded development runs are in [RESULTS.md](RESULTS.md).

## What time is being estimated?

All ages are in years before an arbitrary reference, increasing into the past.
The latent climate is a step: its younger regime applies at material age
`a <= tau`. The event time `tau` is that climate boundary, before burial and
mixing. It is neither a proxy midpoint nor a date assigned to a recovered
specimen. The later-stage paired foundation compares two such latent boundaries;
an older boundary happened first. We make no causal claim from temporal order.

The present focal layer ages are known exactly. They serve as a labelled
chronology oracle control, not as a reconstruction from uncertain dates.

## Mixing law and an independently checkable limit

[Dolman and Laepple (2018), section 3.3.2, Eq. 1](https://cp.copernicus.org/articles/14/1851/2018/)
give a shifted exponential age response for complete mixing and constant
accumulation. Write `h = mixing_depth / accumulation_rate`. Material recovered
at focal age `f` has age

```text
A = f - h + E,       E ~ Exponential(mean=h),       h > 0
```

This law has mean `f`, standard deviation `h`, and support `A >= f-h`.
Its younger-regime fraction is

```text
q(f,tau,h) = 0                              if tau <= f-h
             1-exp(-(tau-f+h)/h)            otherwise.
```

At `h=0` we define `A=f`, including the younger regime at equality. For any
fixed `f != tau`, the mixed response tends to this unmixed response as `h`
tends to zero. At the discontinuity the pointwise limit differs; the code
does not silently interchange those limits.

The paper's figure 1 uses depth 10 cm and accumulation 50 cm per thousand
years, giving `h=200` years. Our analytical response has `q(f,f,h)=1-exp(-1)`.
For a step, its apparent half-height is at focal age
`f_half = tau + h*(1-log(2))`: **61.3706 years older** in that example.
This is a derived step-response consequence of Eq. 1, not a new physical
finding or a digitization of the figure. We retain the infinite exponential
tail; we do not reproduce the package's finite annual truncation, seasons,
sample-layer thickness, or other components of sedproxy.

## Observation and inference contract

For each of 17 focal ages from -200 to 200 in steps of 25 years, draw 16
independent material ages. A specimen has binary proxy response with
probability .9 in the younger regime, .1 in the older regime. This binary
classification model is our simple test instrument, not a published Mg/Ca
measurement model. We observe the number of positive responses at each layer.
Distinct layers use distinct independent specimens. There are no dating
measurements or shared dated specimens yet.

After integrating material ages, the observation law is exactly

```text
Y_f | tau,h ~ Binomial(16, .1 + .8*q(f,tau,h)), independently across f.
tau ~ Uniform{-100,-75,...,100}
h   ~ Uniform{0,25,75}, independently of tau.
```

The discrete prior is the actual probability model. It is not quadrature for
a continuous event-time prior. Inference sums every joint state in log space
and marginalizes `h`. The generator samples material ages directly, using a
different calculation from the likelihood's integrated CDF. `posterior`
receives only an `Observation` and the declared `Design`; it never receives
the simulated event or mixing time. All observation dimensions and counts
are validated. Within a layer, independent specimens are a simplifying
assumption, not a claim about actual sediment.

## A documented change-point inference baseline

The [Stan User's Guide, change-point model](https://mc-stan.org/docs/stan-users-guide/latent-discrete.html#change-point-models)
documents independent Poisson counts with an early rate before index `s` and
a late rate at and after `s`. Both rates have exponential priors; `s` is
uniform on `1..T`. We implement this probability law independently, integrating
the two rates in closed form and enumerating `s`. A segment of length `n`
and count sum `K`, with exponential prior rate `r`, contributes

```text
r * Gamma(K+1) / (r+n)^(K+1)
```

up to the observation factorials, which cancel across `s`. Empty segments
are valid. For counts `(2,0)` and both prior rates 1, segment integration gives
posterior `(16/43,27/43)`; a test checks these rational values. The executable
also reports a larger synthetic example and its complete posterior.
This reproduces a documented model, **not the historical coal data fit**,
and is not Khider's climate termination method. It supplies a checked
change-point calculation. The adopted same-event Gaussian working-model
comparison is now specified and checked in [MODEL_CONTRACT.md](MODEL_CONTRACT.md).

## Calibration and controls

Following the prior-predictive principle discussed by
[Talts et al., simulation-based calibration](https://sites.stat.columbia.edu/gelman/research/unpublished/sbc.pdf),
we draw truth from the declared priors before drawing data. Our diagnostic
uses the **exact randomized posterior CDF**, not finite posterior-sample ranks:

```text
U = P(tau < true_tau | Y) + V * P(tau = true_tau | Y),   V ~ Uniform(0,1).
```

Under the joint law, conditioning on `Y` partitions `[0,1]` into intervals
whose lengths equal their truth probabilities. Consequently `U` is uniform.
Randomization is necessary because the event prior has atoms. We report ten
bins, Kolmogorov distance from uniform, and the preselected 99% DKW band
`sqrt(log(200)/(2*N))`. A correct calculation can exceed that band with
probability at most 1%; passing it is a diagnostic, not proof of correctness.
The exact tiny enumeration test additionally verifies posterior probabilities,
the recovered prior, total predictive mass, and the coverage identity.

An equal-tail interval on this coarse grid often has much more than .90
posterior mass. We therefore compare empirical prior-predictive coverage to
the *mean actual posterior mass*, not mechanically to .90. There is no
promise of uniform frequentist coverage at every fixed parameter value.

The negative control generates the same truths and observations but fits
`h=0` throughout. Its purpose is to test whether these diagnostics detect
ignoring mixing. It is labelled misspecified; its apparent precision cannot
be interpreted as calibrated uncertainty.

A second deliberately defective control returns the prior regardless of data.
It can pass marginal PIT calibration, since truths still follow that prior.
We therefore also report PIT within two data-defined groups: total positive
counts below half the specimens, or at least half. An exact posterior's PIT
is uniform conditional on the observations, so it remains uniform in each
such group. The groups, threshold and tests were chosen during development;
they are not a new held-out validation. Each reported DKW band is an individual
99% band, not a joint multiple-comparison guarantee. Mean posterior information
relative to the event prior and interval width also expose the prior-only
control's lack of learning. Direct posterior probability tests remain essential.

A third control draws event times continuously between -100 and 100 while
fitting the original discrete prior. This changes the generative law and is
explicitly misspecified. Its failure demonstrates why exact finite-prior
calibration cannot validate a coarse grid as a continuous-time approximation.

## Continuous event-time calculation and numerical audit

`continuous.py` instead declares `tau ~ Uniform[-100,100]` and keeps the
same discrete prior on `h` and the same observations. It integrates the
nuisance mixing time and uses midpoint likelihood quadrature in event-time
cells. Its approximate posterior density is uniform **within each cell**;
it does not turn cell midpoints into probability atoms. Unequal cell widths
receive their proper prior mass. Cell boundaries split every zero-mixing
jump and every positive-mixing support boundary, so no cell straddles a
nonsmooth likelihood point.

The default experiment uses .25, .125 and .0625-year maximum cell widths on
the same continuously drawn truths and observations. It reports the supremum
CDF difference between piecewise-linear CDFs (evaluated at all their edges),
interval endpoint changes and calibration. Passing PIT does not prove the
integration is accurate: rare but valid observations need separate checks.

`reference.py` uses a different integration method: adaptive Simpson panels
on each smooth interval, with exact integration of the unmixed component.
A fixed half-year observation-only scan supplies a common log scale; it is
not a prior grid. The reference has a finite evaluation budget and fails
explicitly if recursion or evaluation limits are reached. Analytic single-layer
integrals and a rational unmixed example test both implementations separately.

`audit.py` compares three extreme all-equal count vectors and nine reproducible
generated observations against this reference, at fixed ages and posterior
quantiles. It also checks agreement between two reference tolerances. The
one-year grid failed the original one-percent CDF criterion; that witness
remains in a regression test. The finest grid satisfies a .001 CDF discrepancy
criterion on these audit probes. Finite probes, refinement differences and
Simpson residual estimates are **not certified all-observation error bounds**.
The extended grid and audit were developed after observing coarser-grid
failures; none is represented as a preregistered scientific experiment.

The truth, specimen and diagnostic generators use seeds `seed`, `seed+1`,
`seed+2`. These are development seeds and not the future held-out evaluation.
Output is deterministic for the same Python random-number implementation;
floating-point last digits may differ between platforms. A numerical or
validation exception aborts visibly; no trial is skipped. `numerical_failures=0`
means all requested trials completed, not that failed trials were omitted.

## Milestone status and next work

The adopted synthetic contract now supplies the first milestone's technical
items: latent event definition, published mixing response, documented Gaussian
simulation-law control, matched event-time comparison and own-law calibration.
The corrected release report passes all 13 gates, including 74 project tests.
See [MODEL_CONTRACT.md](MODEL_CONTRACT.md) for the recorded result, retained
failures, sources and reproduction boundaries. **Independent milestone review
and integration remain; the milestone is not closed.** No historical climate
example or literal Khider reproduction is claimed under the owner's decision.

The [paired foundation](PAIRED_EXPERIMENT.md) already implements uncertain
monotone chronologies, shared calibration error, specimen ancestry and joint
ordering probabilities. Its development runs do not complete that later
milestone. Next: independently review this release, then freeze the paired
experiment, sampling budgets, precision and compute cap before prospective
held-out evaluation. Retain failed and unattempted cases. A new scientific
result beyond the cited precedents and any claim about real cores remain
unestablished.
