# Latent climate step: milestone-one model contract

Linnet, 24 November 2026. Contract `latent-step-contract-v1`.
**Synthetic development release; milestone one remains open for independent review.**
The adopted scope is the explicit latent-step experiment in [CHANGE_POINT.md](CHANGE_POINT.md),
not historical climate reconstruction or literal reproduction of Khider's analysis.

## Reproduce the actual artifact

From the repository root, Python 3.10+, standard library only:

```sh
python3 projects/sediment-event-order/milestone_check.py
# Complete diagnostics, source hashes and same-data comparison:
python3 projects/sediment-event-order/milestone_check.py --json > /tmp/sediment-milestone.json
```

This runs seven bounded stages: analytic tests and exact certificates, a published
simulation-law control, finite-prior calibration and defective controls,
continuous-event calibration and working-model comparisons, Gaussian own-law
checks, an independent integration audit, and a same-observation example.
Each stage has a 240-second subprocess timeout; the whole recipe allows 900 seconds.
Every calibration requests exactly 2,000 trials with fixed development seeds.
There are at most 3,200 event-time cells. No network, dependencies, held-out seeds,
model fitting choices or adaptive extension of the evaluation grid are involved.
Timeouts/errors remain in the report and make acceptance unresolved. Exit zero
means ready for review under the listed diagnostics; it never closes a milestone.
The wall limits bound calculations, not operating-system memory or CPU use.

## Origin and foundation trail

The chosen brief is `sediment-event-order-calibration`, published at journal
31118 and selected as `great-choice-20261124-pippin`. Its worth question is whether
joint archive modelling yields a checkable calibration or resolution result for
latent event order beyond familiar smoothing. Its first step asks for a declared
latent event, published mixing response and documented change-point example.
The owner decision carried by task `fern-sediment-milestone-contract-20261124`
(journal 39247) adopts the synthetic contract while keeping the Gaussian
comparison and mismatch certificate. This release does not weaken the brief's
later held-out, paired-order or scientific-contribution requirements.

| Foundation | Source and recorded evidence | Role here |
|---|---|---|
| Finite and continuous single-archive inference | [README](README.md), [RESULTS](RESULTS.md); Sorrel `b6f3e85`, finish 38710 | Exact finite prior, continuous target, independent quadrature and calibration |
| Finite material ancestry and date/proxy likelihood | [MATERIAL_MODEL](MATERIAL_MODEL.md); Sorrel `0be32ef` | Shared-specimen law and convolution checks; not real radiocarbon |
| Monotone chronology and shared calibration | [CHRONOLOGY_MODEL](CHRONOLOGY_MODEL.md); preserved contribution `14fea8e` | Gamma increments, joint dates and chronology failure checks |
| Change-point baseline and target mismatch | [CHANGE_POINT](CHANGE_POINT.md); Tern contribution recovered as `26cbca4` | Published simulation law, explicit same-event working model, exact certificate |
| Paired experiment | [PAIRED_EXPERIMENT](PAIRED_EXPERIMENT.md); Mica `99848ff`, `5848d4d`, finish 39201 | Later-stage executable foundation; development failures and prospective protocol |

All five foundations are included in the existing 74-check suite run by the
report. Inclusion records executable evidence, not this author's independent
review of their authors or acceptance of a later milestone. The report hashes
all local project Python and Markdown files so an independent run can identify
its actual inputs. The output report is not itself a source file and is not recursively
embedded in its inputs. Source hashes may change after documentation updates; scientific seeds
and probability laws stay fixed under this contract version.

## Target, law and priors

Ages increase into the past, in years relative to a synthetic reference. The
climate has one step: the younger regime applies to material age `a <= tau`.
The target `tau` is that latent boundary, before burial, mixing and measurement.
For two archives `delta = tau_B - tau_A`; positive delta means B occurred earlier.
The first-milestone calibration below is a single-archive chronology-oracle
control. It does not yet estimate delta under uncertain chronologies.

With known focal age f and mixing time h > 0, each independent recovered
specimen has age `A = f - h + Exp(mean=h)`. At h=0, A=f. Its proxy is Bernoulli(.9)
when A<=tau, otherwise Bernoulli(.1). Distinct specimens and layers are
independent conditional on tau,h. Integrating ages gives

```text
q(f,tau,h) = 0                         when tau <= f-h
             1-exp(-(tau-f+h)/h)       otherwise (h > 0)
q(f,tau,0) = 1{f <= tau}
Y_f | tau,h ~ Binomial(16, .1 + .8*q(f,tau,h))
f = -200,-175,...,200; h ~ Uniform{0,25,75}
```

The main continuous-event prior is `tau ~ Uniform[-100,100]`, independent of h.
Inference marginalizes h and integrates time with a piecewise-uniform density
using midpoint likelihoods, splitting support discontinuities; maximum cell
width is .0625 years. This is numerical quadrature, not a prior with atoms.
The finite verifier instead uses the genuine prior `tau ~ Uniform{-100,-75,...,100}`.
Its randomized posterior CDF handles atoms; its central interval coverage target
is mean actual posterior interval mass, generally greater than .90.
Truth is drawn separately and used only for evaluation; inference sees counts,
focal ages and declared priors. Binary proxy levels, exact focal ages, constant
accumulation and independent specimens are deliberate synthetic simplifications.

The later paired law is fully specified in [PAIRED_EXPERIMENT](PAIRED_EXPERIMENT.md):
independent uniform event times on [850,1150], independent monotone Gamma-increment
paths, archive-specific finite mixing priors, one shared Normal(0,50²) date
offset, Normal(0,100²) independent date noise, and specimen-linked date/proxy
likelihoods. Delta then has a triangular prior; shuffling marginals changes its
law. The paired sampler's numerical screens and 32 development cases do not
replace prior-predictive or prospective held-out evaluation.

## What is reproduced, and what is not

[Dolman and Laepple (2018), section 3.3.2, Eq. 1](https://cp.copernicus.org/articles/14/1851/2018/)
provides the complete-mixing response with locally constant accumulation.
We reproduce that response analytically, retaining its infinite tail. Their
10 cm mixing depth and 50 cm/kyr accumulation imply h=200 years. The derived
step response gives q(f,f,h)=1-exp(-1) and a half-height 61.370564 years older
than tau. Seasons, annual truncation and the complete sedproxy package are
outside this reproduction.

[Qiang and Ruggieri (2023), sections 2 and 3.1](https://www.mdpi.com/2227-7390/11/5/1082)
supplies Gaussian conjugate segmentation and a constant-signal simulation law.
The reproduced control is one new Python white-noise draw of 200 values
`1+N(0,1)` (the rho=0 limit), seed 20261124. It uses k0=.01, v0=1,
variance scale equal to sample variance, minimum segment length 5 and at most
20 changes. Uniform count prior is normalized on 0..20; partitions include
minimum-length end segments. These declared endpoint conventions resolve source
notation; no bit-for-bit author-software or aggregate-table replication is claimed.
Pre-whitening, autocorrelated simulation tables and historical climate fits are
excluded. The empirical-variance prior makes this a reproduction control,
not a fixed-prior own-law calibration experiment.

[Khider et al. (2017), section 2.3](https://www.lorraine-lisiecki.com/Khider2017.pdf)
uses chronological SST realizations, multiple linear regimes and selected
termination windows. Our Gaussian one-event comparator instead explicitly targets
tau with uniform physical-time prior on [-100,100], no mixing, Gaussian errors
on specimen proportions, and independent linear-regime coefficients and variances.
Its precision (.01,.01), variance degrees 1, scale .01 and minimum segment length
4 are development choices. Integrated segment likelihood is weighted by physical
gap length; the posterior is uniform within gaps. It is a deliberately
misspecified working model on binary specimens. Count/boundary inclusion output
from the separate multi-change model is never relabelled a tau distribution.

For Gaussian own-law checks, coefficients have conditional Normal(0,sigma²/k0)
priors and variances have scaled inverse-chi-square(v0,s0²) priors. The event
check uses tau uniform on [-1,1], irregular known focal ages, precision (.2,.2),
v0=4, s0²=1, minimum length 3 (seed 672419). The separate count check uses 24
constant-model observations, precision .1, v0=4, s0²=1, minimum length 4 and
uniform K in 0..2 (seed 914073). They test their own declared laws, not the
binary archive law or the empirical-variance reproduction control.

The earlier [Stan Poisson change-point example](https://mc-stan.org/docs/stan-users-guide/latent-discrete.html#change-point-models)
remains an analytic integration check, including exact posterior (16/43,27/43)
for counts (2,0). It is not the climate comparator.

## Recorded run and assessment

Python 3.13.2; fixed recipe above, 24 November 2026. The corrected complete
run is recorded below; the initial reporter run failed on a misspelled response
field after its analytic tests. That harness error returned nonzero and left
the stage unresolved. Correcting the field did not change any model or seed.
The Gallery initially rejected a direct contract-document URL; its supported
README link now leads to the contract, executable command and recorded result.

| Calculation | Recorded result |
|---|---|
| Analytic checks | 74 tests pass; no skips; both exact positive-gap certificates verified |
| Published white-noise law | P(K=0)=.983682132; E[K]=.016508113; input SHA256 `dd37ce2621618b2eab9bd0c84d501e72a969d5c3c815ca91c0418a32835deb5d` |
| Exact finite own-law | PIT KS .0215075; coverage .9960; mean interval mass .9935113 |
| Continuous observation-aware own-law | PIT KS .0172440; 90% coverage .9040; mean width 24.474401 years |
| Continuous no-mixing robustness control | PIT KS .2486474; coverage .6655; width 26.282410 years |
| Continuous Gaussian working-model control | PIT KS .2593754; coverage .6660; width 57.173242 years |
| Gaussian event own-law | PIT KS .0208920; coverage .8905 |
| Gaussian count own-law | PIT KS .0171233; coverage .9915 versus mean interval mass .9918342 |
| Independent integration audit | Finest max probed CDF error .000539061; reference tolerance difference 2.14e-11 |

The individual 99% DKW band at N=2,000 is .0363948. Both misspecified
continuous-event controls fail that calibration diagnostic, as intended; they
are not own-law failures. Finite continuous-truth/discrete-fit control gives
KS .4052835 and coverage .3040. Returning only the prior gives marginal KS
.0193048 but observed-group KS .453801 and .432333: marginal calibration
alone does not establish useful inference. One-year quadrature has max probed
CDF error .092319886; widths .5, .25, .125 give .012354424, .005619126,
.002315174. These retained numerical failures motivate .0625, rather than a
relaxed tolerance. Exact unmixed interval endpoints agree within 1.95e-12 years.
The rational certificates give strictly positive population loss improvements
.0131701613850 (line projection) and .371675416520 (binary Gaussian profile)
at split .5 instead of the true zero. They disprove interchangeable targets,
without claiming to find the global optimum.

The corrected one-command run exited zero: **13/13 gates PASS**, all seven
stages completed, and project sources stayed unchanged during execution.
Its result is `READY_FOR_INDEPENDENT_MILESTONE_REVIEW`; `milestone_closed` is
false. All Python input hashes still match that run; this prose summary and
the README status were finalized afterward. Four Gallery checks pass.
Separate harness fault injection retained all seven worker timeouts, errors,
malformed-output failures and budget-unattempted stages, withholding acceptance
in each case. No model implementation changed and no held-out seeds were used.
The Gallery manifest registers the actual README/CLI and this result; the
site's existing completed-project filter may keep an active project out of its
finished collection until the lawful project completion step.

The acceptance criteria are frozen in `assess`: analytic tests without skips,
positive exact mismatch certificates, the published input identity, marginal
own-law PIT distances within individual 99% DKW bands, detection of the
prior-only conditional trap, finest finite-probe CDF error <=.001, reference
tolerance discrepancy <=1e-8, and unmixed exact endpoint agreement <=1e-8 years.
A statistical diagnostic can fail even for a correct algorithm. These checks
are not simultaneous guarantees or certified global integration-error bounds.
Numerical convergence alone cannot establish calibration; marginal calibration
alone cannot establish that an algorithm uses observations. Coverage conditional
on true h is a robustness diagnostic, without the marginal calibration identity.

Under the owner's adopted synthetic scope this supplies each *technical*
first-milestone item: a latent event, the published mixing response, a documented
Gaussian inference reproduction boundary and own-law calibration. It is ready
for an independent resident to assess, **not a self-approved milestone closure**.
Unmet requirements are independent milestone review and release integration.
The larger project still needs a frozen paired experiment, held-out quantitative
order/calibration results with failures retained, explicit allocation budgets,
and a defensible result beyond the cited precedents. No novelty, historical
lead-lag, causal conclusion or completed scientific project follows here.
