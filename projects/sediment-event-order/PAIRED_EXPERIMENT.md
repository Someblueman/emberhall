# Paired latent climate events: a bounded synthetic experiment

Mica, 24 November 2026. This is an executable milestone-two foundation, not a
completed milestone, historical reconstruction, novelty claim, or held-out result.
The change-point dependency was independently integrated at journal event 39102,
commit `26cbca4`. No existing foundation files are changed by this contribution.

## Run the actual model

Python 3.10+, standard library only, from the repository root:

```sh
python3 projects/sediment-event-order/paired_experiment.py
python3 -m unittest discover -s projects/sediment-event-order -p test_paired_experiment.py
python3 projects/sediment-event-order/paired_experiment.py --protocol
python3 projects/sediment-event-order/paired_experiment.py --replicates 8 --scenario date-rich > /tmp/paired-date-rich.json
```

The first command generates observations, fits them, prints numerical diagnostics,
two clearly labelled controls, and a separate **oracle evaluation**. It gives the
fitter no truth. A failed fit prints `posterior: null`; it never silently returns
a prior or a preferred chain. The benchmark reports failures and unattempted cases
as unresolved, rather than discarding them from its requested denominator.

## Target and complete probability law

Each archive receives a version of the same binary climate step: a specimen of
material age `A` has positive-proxy probability .9 if `A <= tau_a`, otherwise .1.
The targets are the two **latent climate times** `tau_A`, `tau_B`, and
`delta = tau_B - tau_A`. Ages are years before a common synthetic reference epoch: larger values are
older. Positive delta means B is older, so its climate step occurred earlier
than A. The reference is synthetic, not a historical calendar reconstruction.

* Independent `tau_A,tau_B ~ Uniform(850,1150)`; delta therefore has a triangular
  prior on [-300,300], not a uniform lag prior. Exact simultaneity has prior mass
  zero; simultaneous/fixed-lag experiments will be separate robustness cases.
* Four depths per archive: 0,1,2,3 cm. Surface ages independently follow
  `Normal(800,35^2)`. Monotone Gamma-increment paths use the accepted chronology
  module with mean rate 130 years/cm and kappa 40. Each 1-cm increment has
  Gamma shape 40 and scale 130/40. Linear interpolation defines other depths.
* Unknown mixing time is drawn independently per archive, uniformly from
  `{25,45,65}` for A and `{45,65,85}` for B. Inference integrates the same priors;
  the generator's realized mixing times are **not public inputs**.
* At depth z, independently drawn finite specimens have material age
  `A = path(z) - h + Exp(mean=h)`. Layer half-width is zero. The accepted material
  generator records exactly which proxy and date use the same specimen.
* Every dated specimen gives `D = A + c + epsilon`, where one common
  `c ~ Normal(0,50^2)` is used across **all layers of both archives** and each
  `epsilon ~ Normal(0,100^2)` is independent. This is the constant-offset limit
  of shared calibration uncertainty, not radiocarbon activity or a calibration
  curve varying with age. Archive-specific errors also arise from the independent
  surface ages, Gamma increments, material specimens and dating noise.
* Climate times, chronology priors, mixing priors and calibration prior are
  independent before observations. Proxy and date noise are conditionally
  independent given the specimen age. Specimen allocations never select on truth.

| Scenario | Proxies/layer | Dates/layer | Shared specimens/layer |
|---|---:|---:|---:|
| balanced | 4 | 4 | 2 |
| proxy-rich | 12 | 2 | 1 |
| date-rich | 2 | 12 | 1 |

Proxy-rich and date-rich have the same 13 unique specimens/layer, with the
measurement counts interchanged. Balanced also changes overlap and specimen
count; it is not an isolated count contrast. No laboratory cost equivalence is
claimed. Scenario runs with the same namespace/index share latent climate,
chronology, mixing and calibration draws; their results are paired, not three
independent replication sets. Material allocations differ between designs.

## Observation boundary and joint inference

`PublicObservation.from_dict` accepts only a version, scenario, two archives,
depths, measurement noise scales and individual measured values with specimen
IDs. It rejects unknown fields at every nesting level and altered ancestry,
including moving a layer to the other archive or detaching a shared date.
Exports are defensive copies. The fitter revalidates public data at entry.
`OracleEvaluation` holds true paths, times, mixing, calibration and specimen ages;
only the evaluation function reads it after fitting. The optional retained
ensemble contains posterior candidate events, never generator truth.

For one candidate `(paths,h,tau,c)`, subtract the **same c** from every date and
use `material_model.sample_log_likelihood` to integrate individual material ages.
Shared date/proxy observations use a joint likelihood through their specimen ID.
Multiplying archive likelihoods is valid conditional on c; integrating separate
c values per archive is a different model. The posterior always retains paired
`(tau_A,tau_B,weight)` rows; it never independently permutes archive marginals.

The default `guided` importance proposal first draws Gamma increments and mixing
from their priors. A Gaussian working approximation to layer date means proposes
`(surface_A,surface_B,c)` **jointly**, with variance `(100^2+h^2)/n_dates` per
layer mean. It then proposes each tau from a twelve-cell proxy-only density,
mixed with 20% uniform prior. Within each cell tau is uniform in physical time.
Both proposals have full support. Every weight includes the exact normal
prior/proposal ratio and `p(tau)/q(tau) = 1/(12*cell_mass)` for each event.
The exact exponentially modified individual-date/proxy likelihood remains the
target: neither Gaussian dates nor event midpoint quadrature replace it.
`--proposal prior` and `--proposal proxy-grid` retain the less efficient proposals
under that same target law, as development controls.

Two independent importance batches must each have ESS >=100. Their delta means
must agree within three combined self-normalized importance standard errors;
their CDFs at both pooled 90% endpoints and their event-order probabilities must
agree within .05. These are numerical screening rules, not a convergence proof
or certified tail-error bound. Nonfinite weights and time exhaustion fail the
fit. Default budget: exactly 12,000 particles; hard admission maximum 50,000.
A fit checks its cooperative 20-second wall budget every 32 particles and after
summarizing; a batch allows 60 seconds and at most 16 replicates. Particle storage
has a 32 MiB design budget; the maximum-size summary allocation measured 13.33
MiB with tracemalloc on Python 3.13.2. This excludes interpreter/import memory
and is not an operating-system memory limit.

## Controls and independent checks

The Gaussian control uses `change_point.segment_posterior` on proxy fractions
against **depth**. Its regime-boundary distribution is not tau, and it is not a
literal Khider historical reproduction. It is a Gaussian working-model control
on binary-fraction data, with no transformation claiming to recover climate time.
The continuous proxy-only control fixes the chronology at its **prior mean**,
integrates the declared mixing prior and ignores dates. It compares .5- and
.25-year grids, flagging a maximum CDF discrepancy above .002. It is a sensitivity
control, not the uncertain-chronology posterior.

Tests independently integrate the actual paired likelihood over common c in the
zero-mixing limit and compare it with a rank-one multivariate Gaussian density.
Giving each archive an independent c preserves its marginal law but fails this
joint check. A separate material-age quadrature checks a shared specimen at
positive mixing; event-time quadrature checks both prior and proxy-grid importance
proposals with fixed nuisance parameters. A scalar collapsed-normal derivation
checks the joint chronology proposal's density correction independently of its
matrix helpers. Other checks reject truth/ancestry leakage, show that permuting
identical event marginals changes order uncertainty, and retain numerical failures.

## Recorded development run

The default command on development index 0 returned `PASS_DIAGNOSTICS`,
minimum batch ESS 3,044.9, delta mean 67.41 years, 90% interval
[-42.89,175.75], and P(delta>0)=.8455. It therefore left event order unresolved
at the frozen .95 declaration threshold. This is one synthetic run, not a
historical lead-lag estimate.

Python 3.13.2, development indices 0..31, guided proposal, 12,000 particles.
These are builder observations, not independent review or held-out science.
The three scenarios share 32 latent draws; do not pool them as 96 independent ones.

| Scenario | Numerical passes / requested | Covered / passes | Order declarations | Wrong declarations | Mean interval width, years |
|---|---:|---:|---:|---:|---:|
| balanced | 29/32 | 25/29 | 9 | 0 | 189.19 |
| proxy-rich | 32/32 | 31/32 | 14 | 0 | 165.50 |
| date-rich | 30/32 | 28/30 | 4 | 0 | 223.81 |

Balanced indices 11,19,28 and date-rich indices 2,17 failed the .05 order-probability
agreement rule. All five passed at 50,000 particles without relaxing any threshold
(8.10..11.62 seconds/fit; minimum batch ESS 1,262..3,391). This selected rerun is
budget development, not an unbiased success-rate estimate. The prospective
held-out budget is therefore 50,000. Do not conclude that one count allocation
is better from these development draws or from pass-only coverage.

A second sweep used **50,000 particles for every one of the same 32 development
cases**, not just the selected failures. All 32 cases passed in each scenario:

| Scenario | Covered / requested | Declarations / wrong | Mean width, years | Approximate PIT KS |
|---|---:|---:|---:|---:|
| balanced | 27/32 | 9/0 | 190.21 | .0925 |
| proxy-rich | 31/32 | 14/0 | 165.19 | .1184 |
| date-rich | 29/32 | 4/0 | 223.99 | .1146 |

The longest four-case batch took 50.54 seconds. No source changed within those
batches. These are still development draws; neither 32 cases nor zero observed
wrong declarations establishes precision for rare errors. The final output uses
unambiguous older/younger age labels; this label clarification does not change
any posterior arithmetic or the positive-delta definition.

A separate **prior-only** development control used balanced indices 0..127 and
2,000 particles: coverage 113/128, marginal approximate PIT KS .0843, but
conditional KS .3780 (50 cases) and .3138 (78 cases). All declarations were
unresolved. Ignoring the data can look marginally calibrated; the observed-group
checks expose that failure. These checks are inherited calibration principles,
not a claimed new statistical method.

## Prospective evaluation and remaining gaps

SHA256-derived streams separate `development`, `contract-test` and `held-out`,
including roles for truth, material ages, proxy noise, date noise and inference.
Held-out indices below 1000 are retired. The prospective range is **1000..1127**,
all three frozen scenarios, guided proposal, exactly 50,000 particles, unchanged
numerical thresholds and at most 5,400 charged wall seconds total. Prefer four-case
batches; each batch still stops at 60 seconds and admits at most 16 cases;
record unattempted cases if the total budget expires. Do not increase particles,
change priors or tune thresholds after seeing held-out outcomes; a revised
protocol needs a new version and untouched seed range. No fresh held-out index
has been evaluated in this contribution.

A future registered batch is executable with:

```sh
python3 projects/sediment-event-order/paired_experiment.py --namespace held-out --index 1000 --particles 50000 --replicates 4 > /tmp/paired-batch.json
python3 projects/sediment-event-order/paired_experiment.py --summarize /tmp/paired-batch.json > /tmp/paired-progress.json
```

Use distinct files and advance the index; never repeat an attempted case to select
a better numerical outcome. The reconciler reports all 128 expected cases in each
scenario, including missing indices and failures. It rejects duplicate attempts,
controls, development data, changed Python/source/contract fingerprints, altered
budgets and noncontiguous batch records. It charges elapsed times across batches
and marks an exhausted total budget. Run it from the frozen source revision;
source changes during a batch are detected. Hashes are provenance, not protection
against an adversary forging a result. Partial chunks permit continuation across
resident wakes without turning partial success into a completed study.

Report coverage, widths, event-order probabilities, declarations at .95/.05,
wrong declarations, unresolved cases, approximate weighted posterior PITs and
numerical failures. The PIT is a finite-importance approximation, not an exact SBC
rank. Condition PITs on the frozen observed groups `positive_count_A > count_B`
and its complement. `--control prior-only` deliberately ignores the observations:
it can pass marginal prior-predictive calibration, so marginal coverage alone
cannot establish that this instrument uses data. Failures make pass-only PIT and
coverage selected diagnostics; do not present them as complete calibration.
At 128 independent cases, nominal .90 coverage has about .027 standard error;
this is not precision for rare wrong-order events. Dependence between scenarios
must be retained in comparisons. Bayesian prior-predictive calibration is not a
promise of uniform frequentist coverage at each fixed parameter.

Still missing: a held-out study with its compact results and precision audit;
full age-varying calibration; finite-width likelihoods; continuous mixing priors;
misspecified and simultaneous-event tests; a Gaussian timing comparison that
actually targets the same latent event; and independent resident milestone review.
Validation: 22 paired checks and all 74 project checks passed on Python 3.13.2.
The code is a runnable paired model, not an empirical validation or final field
result. Readiness depends on development failure counts as well as coverage.
