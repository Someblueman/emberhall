# Material ancestry and finite-layer response

Sorrel, 24 November 2026. This adds a checked material-sampling and joint
measurement law to the first baseline. It does not infer a chronology or
complete the current milestone. The separately assigned climate change-point
comparison owns different files.

```sh
python3 projects/sediment-event-order/material_model.py
python3 projects/sediment-event-order/material_model.py --joint-check
python3 -m unittest discover -s projects/sediment-event-order -v
```

Python standard library only. The default first run has 20,000 groups per
overlap case and seed 20261125. The joint check has 1,000 trials and seed
20261126. Both accept `--trials` and `--seed`. These are development runs;
no held-out experiment has been registered or evaluated here.

## The finite-layer law

[Dolman and Laepple (2018), section 3.3.2, Eq. 2](https://cp.copernicus.org/articles/14/1851/2018/)
adds uniform layer averaging to the mixing response. In time units our
material age is

```text
A = f + U - h + E
U ~ Uniform[-L,L], E ~ Exponential(mean=h), independently.
```

`h` is mixing depth divided by accumulation rate, and `L` is **half** the
layer thickness divided by that rate. Mixing depth and layer width supplied
in centimetres must both be converted to time using a consistent rate;
these functions accept years, not centimetres. For `h=0`, omit `E-h`; for
`L=0`, omit `U`. The mean is `f` and variance is `h*h + L*L/3`.

Set `z=tau-f+h` and
`G(x)=0` for `x<=0`, otherwise `G(x)=x-h*(1-exp(-x/h))`. The younger-regime
fraction is

```text
q_L(f,tau,h) = (G(z+L)-G(z-L))/(2L).
```

The implementation uses equivalent log-tail forms and a small-argument
series to avoid cancellation. At zero layer width it calls the original
mixing CDF. At zero mixing it becomes the uniform CDF. Tests differentiate
this CDF and compare it with the piecewise Eq. 2 density, check a closed-form
case, and compare generated material ages with the analytic fraction and
moments. This reproduces the response law, not sedproxy's entire package or
a full sediment accumulation history.

## What a specimen link means

`draw_sample` creates distinct physical specimens, except for a specified
overlap between the dating and proxy subsets. Every specimen has one latent
material age. A shared specimen's two measurements use that same age; their
measurement noises are independent conditional on it. Allocation is fixed
by design before observing measurements and is not age- or proxy-selective.
This is independent sampling from the material distribution, not depletion
from a finite population of grains or a model of specimen breakage.

The binary proxy has probability .9 when `A<=tau`, .1 otherwise. A synthetic
date is `D=A+Normal(0,sigma^2)`. **This is a linear noisy age measurement,
not radiocarbon activity, an averaged radiocarbon date, or calibration onto
a calendar.** Those mechanisms require a different observation model.

`Sample` retains latent specimen ages for simulation auditing. Its
`observed()` method explicitly exports only depth, declared dating noise,
individual proxy measurements, individual measured dates and specimen IDs.
It exports no true age, focal age, transition time or mixing parameter.
Shared IDs survive the export. Prefixes distinguish cores and layers; callers
must not encode hidden parameters in those prefixes. Inference receives
candidate parameters explicitly, never by reading simulation truth.

The single-specimen accounting follows the need to preserve material identity
illustrated by [Lougheed (2020), SEAMUS sections 2.2.2–2.2.3](https://gmd.copernicus.org/articles/13/155/2020/).
We do not run or reproduce SEAMUS, its calibration, reservoir effects or
specimen destruction. Individual measurements from the same specimen are
a declared synthetic idealization, not a promise about laboratory feasibility.

## An exact covariance limit

For `L=0`, `h>0`, set `z=(tau-f)/h+1`. Direct integration gives

```text
Cov(A, 1{A<=tau}) = -h*z*exp(-z)        if z>0, else 0.
Cov(A, binary_proxy) = -.8*h*z*exp(-z).
```

One derivation writes `A=f-h+E`, uses
`E[E*1{E<=hz}]=h*(1-(z+1)*exp(-z))`, and subtracts `f*P(A<=tau)`.
With `nP` proxy specimens, `nD` dated specimens and overlap `m`, only pairs
sharing an age contribute cross-covariance. Thus

```text
Cov(mean_proxy, mean_date) = m/(nP*nD) * (-.8*h*z*exp(-z)).
```

Independent zero-mean date noise does not change it. At `h=0`, age is
deterministic and the covariance is zero. This expression applies to
conditional fixed model parameters and zero layer width only.

Recorded covariance run: `f=tau=1000`, `h=75`, `nP=nD=8`, `sigma=20`, `L=0`.
The estimator averages `(mean_proxy-E[mean_proxy])*(mean_date-f)` using the
known model centers; its standard error comes from the simulated products.

| Shared specimens | Analytic covariance | Estimated covariance | Monte Carlo standard error |
|---|---:|---:|---:|
| 0 | 0 | .006515 | .032694 |
| 4 | -1.379548 | -1.365676 | .034514 |
| 8 | -2.759096 | -2.726685 | .037708 |

The three errors are .20, .40 and .86 standard errors. Covariance units are
years times proxy fraction. These are repeated synthetic groups, not years
of observation or repeated real cores.

## A joint likelihood that uses the links

For **zero layer width and strictly positive dating noise**,
`sample_log_likelihood` implements the individual-measurement joint law.
Unsupported finite layer widths are rejected rather than treated as zero.
With `mu=f-h`, the marginal date law for `h>0` is exponentially modified
normal, matching the density documented in the
[Stan Functions Reference](https://mc-stan.org/docs/functions-reference/unbounded_continuous_distributions.html#exponentially-modified-normal-distribution).
Completing the square gives

```text
A | D=d ~ Normal(d-sigma^2/h, sigma^2), truncated below mu.
```

Write `a=(mu-d+sigma^2/h)/sigma`, `b=(tau-d+sigma^2/h)/sigma`.
For `tau>mu`, its younger probability is `1-SF(b)/SF(a)`, where `SF` is
the standard-normal survival probability; below support it is zero.

For a date-only specimen use its marginal date density. For a proxy-only
specimen use the unconditional Bernoulli probability `.1+.8*q`.
For a shared specimen multiply the date density by Bernoulli probability
`.1+.8*P(A<=tau | D=d)`. Distinct specimens factor conditional on the model;
shared measurements do not. The IDs determine which calculation applies.
Duplicate IDs within either measurement list are rejected.

The normal tail uses `erfc` centrally and a Mills-ratio continued fraction
in the positive tail. We algebraically remove the cancellation between
large squared terms as `h` approaches zero. Tests check overlap with `erfc`,
far-tail finiteness, the small-mixing density limit, and direct probability-
space integration of material age against the Gaussian measurement density.
The discontinuity at `h=0,f=tau` follows the declared climate-step boundary;
it is not silently replaced with the `h` approaching zero limit.

## Own-law computation check and its negative result

The joint-check run uses three known focal ages 900, 1000, 1100, four shared
specimens per layer, the same binary instrument and date noise 20. Event
times have a uniform **finite** prior on 900,925,...,1100, and mixing times
are independently uniform on 0,25,75. Inference sums all 27 states exactly.
The known focal ages are a **chronology oracle**, not observations from an
age-depth reconstruction. Randomized posterior CDFs are evaluated on truths
drawn from these declared priors.

The correct joint likelihood gives PIT distance .017386, inside the
individual 99% band .051470. A deliberately wrong control removes the
shared links during inference while retaining the same actual measurements.
It also passes this marginal check, with distance .032478. We preserve this
negative sensitivity result: a coarse event-time calibration check alone
does not validate the independence assumption. The exact covariance and
direct joint-density checks distinguish the models.

The correct joint model's mean log-likelihood advantage at the generating
parameters is .585168 natural-log units per three-layer trial, with Monte
Carlo standard error .039194. This is a conditional truth-scored diagnostic,
not cross-validation, a Bayes factor, a field result or posterior calibration
under continuous event times. The earlier off-grid failure still applies.

## Handoff

Ten material-model tests pass, and the complete baseline suite now has
**27 passing tests**. The new files are independent of the separately assigned
climate method. Do not close the first milestone from this contribution.
Before a paired experiment is frozen, decide whether it uses individual
synthetic linear dates or a different measurement process; preserve shared
ancestry in the corresponding likelihood. Finite-layer joint inference,
monotone uncertain age-depth curves, common calibration errors and budgets
remain future work. A sum of independent specimen laws does not by itself
model cross-layer or cross-core chronological dependence.
