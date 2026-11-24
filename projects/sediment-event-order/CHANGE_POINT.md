# A regime boundary is not automatically the climate event

Tern, 24 November 2026. **Task result: a proved target mismatch, an explicit
Gaussian working model, and a matched comparison. Milestone one remains open.**
This is research code and
development evidence, not a historical fit, paired-archive result or novelty claim.

The selected brief (journal 31118) explicitly forbids replacing uncertainty about
the latent climate event with uncertainty about a smoothed proxy midpoint. This
report supplies a counterexample to that replacement, including the Gaussian
profile-likelihood version on the foundation's binary specimen observations.

## Reproduce

Python 3.10+, standard library only, from the repository root:

```sh
python3 projects/sediment-event-order/change_point.py
python3 -m unittest discover -s projects/sediment-event-order -v
python3 projects/sediment-event-order/change_point.py --foundation --calibration 2000 --event-trials 2000
python3 projects/sediment-event-order/change_point.py --gaussian-event-trials 2000
```

The last two commands additionally require the foundation modules from Sorrel's
commit `b6f3e85`. This private room predates that commit. For the recorded run,
all eight foundation artifacts were read from Sorrel's preserved room, verified
against the SHA256 values in immutable finish **38710**, and copied to a temporary
reference directory. The command used `PYTHONPATH=/tmp/tern-sediment-foundation`.
Only this task's three new files are submitted here; this is not source acceptance
of that foundation. After independent integration, no extra path is needed.

## What the sources actually supply

[Khider et al. (2017), section 2.3](https://www.lorraine-lisiecki.com/Khider2017.pdf)
fits linear regimes to chronological SST realizations: at most ten changes,
minimum spacing ten thousand years, and selected termination windows. Its
boundary probabilities are not a sediment-mixing inverse model.

The author-hosted [Ruggieri (2013)](https://mathcs.holycross.edu/~eruggier/joc3447.pdf)
timed out on direct fetch. Search-indexed author text exposed its discussion and
appendix, including the independent-error restriction. The accessible primary
[Qiang and Ruggieri (2023), sections 2 and 3.1](https://www.mdpi.com/2227-7390/11/5/1082)
supplies the Gaussian conjugate priors, segmentation recursion and simulation
law used here. Segment coefficients have zero-mean normal priors conditional on
variance; variance has a scaled inverse-chi-square prior. Count and admissible
partition priors are uniform. The reproduced control uses 200 observations of
`1 + N(0,1)`, precision `.01`, variance degrees `1`, sample-variance scale,
minimum length `5`, and maximum changes `20`. This is one new Python draw of a
documented simulation law, **not reproduction of a historical climate example,
the paper's aggregate tables, pre-whitening or its model-averaging extension**.

## Probability law and independent checks

Our implementation integrates segment parameters analytically, then sums
partitions with forward/backward recursions. It reports `P(K|Y)`, boundary
inclusion probabilities, and the location distribution conditional on `K=1`.
Inclusion probabilities sum to `E[K|Y]`; they are not a normalized event-time
distribution. Conditioning on one break must never hide the probability of none.

For segment design matrix `X`, response `y`, prior precision `D=diag(k0)`,
`a=v0/2`, `b=v0*s0²/2`, set `A=D+X'X`, `c=X'y`. The integrated log density is

```text
-n/2 log(2π) + (log det D - log det A)/2
+ a log b - (a+n/2) log[b+(y'y-c'A⁻¹c)/2]
+ log Γ(a+n/2) - log Γ(a).
```

All coefficients use the supplied global coordinates; recentering them without
transforming their prior changes the model. Each segment has independent
coefficients and variance; adjacent fitted lines need not meet.

Our endpoint convention is explicit: `n` observations have `n-1` interior gaps;
all segments, including the ends, have at least `d` observations. There are
`choose(n-(k+1)d+k,k)` admissible `k`-break partitions. This removes ambiguous
endpoint/count notation in the source, rather than silently using `choose(n,k)`.
The count prior is normalized on `0..kmax`. No claimed bit-for-bit equivalence
to the authors' software follows from these declared conventions.

Seventeen checks include a separate observation-space multivariate Student-t
density, exhaustive partitions, an uninformative-likelihood trap for the count
prior, stars-and-bars generator enumeration, Simpson integration of the response,
and independent Decimal checks of rational exponential/log enclosures.
An exact three-interval likelihood also checks the unmixed continuous-time
comparator independently of the foundation's quadrature implementation.
An unequal-gap example verifies a uniform physical-time prior in the
single-event model, rather than accidentally assigning equal mass to each gap.

## Counterexample and exact certificate

Use the foundation's [Dolman–Laepple response](https://cp.copernicus.org/articles/14/1851/2018/)
and dimensionless focal age `u=(f-tau)/h`, with `h>0`. The younger fraction is
`q(u)=1-exp(u-1)` below `u=1`, and zero above it. The latent event is `u=0`.
It is a smooth point of this response with nonzero curvature. The half-height
is `1-log(2)` and the support kink is `1`; neither equals the latent event.
Knowing just one apparent boundary cannot recover both `tau` and unknown `h`.

For a segment `[l,r]`, compute `I0=∫q`, `I1=∫u q`, `I2=∫q²`. Below `u=1`
their primitives are `u-e^(u-1)`, `u²/2-(u-1)e^(u-1)`, and
`u-2e^(u-1)+e^(2u-2)/2`; truncate at one. Its best linear residual integral is

```text
R(l,r) = I2 - I0²/(r-l) - [I1-(l+r)I0/2]² / [(r-l)³/12].
```

On `[-4,3]`, the total residual at split `0` exceeds that at split `1/2` by
**0.0131701613850**. `certified_mismatch()` proves strict positivity with exact
rational enclosures: a positive-term Taylor series bounds each exponential,
with a geometric remainder; interval operations preserve the bounds. Decimal
renderings are display values only. No global optimum needs to be found.

This also holds for the Gaussian fit to the actual binary observation law,
with uniform focal-age density on the stated window in this population example.
For proportion `Y/16`, `p=.1+.8q` and `Var(Y/16)=p(1-p)/16`. The best segment
Gaussian mean is its linear projection; the best Gaussian variance is

```text
V(l,r) = [.09(r-l)/16 + .64(I0-I2)/16 + .64 R(l,r)] / (r-l).
```

The expected profiled Gaussian objective is `Σ(r-l)log V(l,r)` up to constants.
Its value at split zero exceeds that at one-half by **0.371675416520**.
An exact rational log enclosure proves the sign using the atanh series and
its absolute tail bound. Outward dyadic rounding bounds fraction growth without
weakening the certificate. Thus even a two-line Gaussian population fit with
separate unknown variances need not target `tau`. This is a counterexample to
interchangeable targets, not a theorem describing every finite posterior.
It does not prohibit using a segmented boundary as a deliberately misspecified
estimator of `tau`. That requires an explicit working observation model and
event-selection rule; the population approximation then explains possible bias.

An exhaustive 4,000-cell candidate scan further shows window dependence:

| Window in units of `h` from `tau` | Best constant split | Best linear split |
|---|---:|---:|
| [-4,3] | .361 | .4975 |
| [-1,3] | .564 | .844 |
| [-4,.75] | -.2700625 | -.6548125 |

These grid scans use exact integrated responses, permit 1% minimum segment
length, and are numerical illustrations, not certified continuous optima.

## Recorded development run

Python 3.13.2. The white-noise control, seed `20261124`, has sample variance
`1.1510908125`, `P(K=0|Y)=.98368213234`, and expected count `.01650811276`.
The SHA256 of compact JSON `[x,y]` is
`dd37ce2621618b2eab9bd0c84d501e72a969d5c3c815ca91c0418a32835deb5d`.
This empirical-variance prior is not an own-fixed-prior calibration experiment.

A separate 2,000-trial fixed-prior experiment, seed `914073`, uses 24 samples,
constant segments, `k0=.1`, `v0=4`, `s0²=1`, minimum length four and `K=0..2`.
Truth parameters are generated separately from the integrated likelihood.
Posterior count PIT distance is `.0171233` (individual 99% band `.0363948`),
coverage `.9915` versus mean actual discrete interval mass `.9918342`, and
mean count information `.622037` nats. The prior-only control passes marginal
PIT (`.0230432`) but fails in observed-range groups: `.149172` and `.260538`
against `.046695` and `.058092`. The posterior gives `.019353` and `.021803`.
These are computational diagnostics, not simultaneous guarantees or field results.
The separate location check conditional on exactly one change gives PIT
distance `.0399532` on 669 generated one-change cases, with band `.0629276`.

On the foundation's exact same 17 layer counts (seed `20261124`, true `tau=0`,
`h=75`, chronology known), observation-aware latent inference gives a 90%
interval `[-4.421162,36.239902]`; assuming no mixing gives
`[25.956792,48.734613]`. Both estimate the same declared latent event.
The Gaussian line model instead gives `P(K=0,1,2)=(.757820,.238831,.003350)`;
**conditional on one break**, its gap-midpoint labels span `[12.5,37.5]` at 90%.
Those labels are not a latent-event posterior. Its prior choices are explicit
development choices, not Khider's settings or a fair model-selection benchmark.

The common-event comparison used 2,000 paired development trials, seed
`20261124`, and maximum cell width `.0625` years. Both models saw exactly the
same simulated observations. Event times were uniform on `[-100,100]`, with
independent uniform `h∈{0,25,75}`. The observation-aware prior matches that law.

| Model for the same latent `tau` | PIT distance | 90% coverage | Mean width, years |
|---|---:|---:|---:|
| Observation-aware | .0172440 | .9040 | 24.474401 |
| Assume no mixing | .2486474 | .6655 | 26.282410 |
| Explicit one-event Gaussian working model | .2593754 | .6660 | 57.173242 |

The individual 99% uniform-PIT band is `.0363948`. At true mixing times
`0,25,75`, observation-aware coverage is `.914826,.891207,.906475`; the
unmixed comparator gives `.921136,.722802,.376978`. These strata are robustness
diagnostics: conditioning on a true nuisance parameter does not preserve the
marginal prior-predictive uniform-PIT or 90% coverage identity. In particular,
the observation-aware PIT distance `.065856` in the `h=75` stratum is retained,
not declared a failed numerical fit against an inappropriate uniform target.
The `.0625` integration resolution inherits the foundation's numerical audits;
it is not a certified global error bound. The unmixed likelihood is exactly
constant between focal ages; its independent three-interval check passes.
Across all 2,000 cases its interval endpoints agree with an independent exact
rational posterior to at most `1.95e-12` years. The paired coverage difference
is `.2385`, with Monte Carlo standard error `.0107874`.

For unmixed specimens the likelihood is constant between adjacent focal ages.
Conditional on a gap, a uniform time prior therefore remains uniform even with
arbitrarily many specimens. With the present 25-year gaps, posterior density
cannot exceed `1/25`, so any 90% interval must be at least 22.5 years wide.
Swapping two latent events within the same sampled gap leaves the entire joint
observation law unchanged. This is an exact sampling obstruction, not a paired
simulation result or a claim about real archives. Midpoint atoms would hide it.

## An explicit Gaussian working model for the same event

`GaussianOneEventInference` supplies the previously missing target contract.
There is exactly one latent boundary `tau`, uniform in physical time on
`[-100,100]`. Before mixing, separate Gaussian linear regimes switch at that
boundary without a continuity constraint. The working model assumes **no
mixing** and Gaussian noise on observed specimen proportions. Its coefficients
and variances use the displayed conjugate priors: precisions `(.01,.01)`,
degrees `1`, variance scale `.01`; both segments require four samples.
No true event or mixing time is passed to inference.

For each candidate gap, multiply the two integrated segment likelihoods by
its intersection length with the time-prior window. Within that intersection
the posterior is uniform. This fixes both the time interpretation and the
missing within-gap uncertainty. End restrictions that would truncate the prior
are rejected. The fixed one-event assumption matches this synthetic generator;
it would need justification and transition selection for real climate records.
This model deliberately misspecifies mixing, observation noise and known proxy
levels. It is a restricted, documented Gaussian baseline, **not a literal
reproduction of Khider's multiple-transition analysis**. Its calibration is a
robustness question, not an own-law 90% promise for binary specimens.

For the recorded observation it gives `[.759870,48.719720]` at 90%, which
differs from simply assigning midpoint labels to gap probabilities. On binary
development trials, coverage at true `h=0,25,75` is
`.922713,.643815,.453237`. Broad intervals in the heavily mixed group do not
guarantee coverage; mean width there is `99.521319` years. No prior was tuned
against these results.

Its separate **own-law** check draws Gaussian observations from its actual
coefficient/variance prior, with 12 irregular focal ages and `tau∼Uniform[-1,1]`.
It uses precisions `(.2,.2)`, degrees `4`, variance scale `1`, and minimum
length `3`, including partial end gaps. In 2,000 development trials, seed
`672419`, PIT distance is `.0208920` against `.0363948`, 90% coverage is
`.8905`, and mean width is `1.136073`. Continuous truth goes only to evaluation;
`fit_values` receives only responses. This verifies the explicit Gaussian model's
computation rather than pretending the binary archive generator follows it.

## Precise alternative first-milestone design

Preserve the current latent step and binary specimens. Use the continuous
uniform event prior on `[-100,100]` with `h∈{0,25,75}` as the observation-aware
model. Use the identical likelihood, priors and observations with `h=0` as the
conventional abrupt-boundary comparator. Both parameters are explicitly `tau`;
the latter is misspecified when mixing is present. `--event-trials` executes
this proposal, keeping known chronology labelled as an oracle in both fits.
Gaussian segmentation remains a separately verified diagnostic for proxy
regimes; the explicitly mapped single-event Gaussian countermodel is now an
additional competing estimator of `tau`, with its misspecifications visible.

Before freezing: the project owner must record which target/model contract is
adopted; an independent milestone reviewer must check the certificate and the
source baseline. If a literal Khider-style climate baseline remains mandatory,
add a separate continuous-proxy forward model and reproduce an archived climate
example with its actual inputs, priors and termination-window rule. Do not
silently relabel this binary prototype as that reproduction. Then add monotone
chronology, material ancestry and paired shared errors, freeze evaluation seeds
and numerical limits, and conduct held-out order trials. No such trial is
claimed here, and none of these development seeds is reserved as held-out.
