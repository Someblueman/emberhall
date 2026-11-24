# Paired climate experiment: prospective freeze

Linnet, 24 November 2026. `paired-freeze-v1`. Development-only preflight;
independent milestone-two review remains required. No held-out result.

## Reproduce

Python 3.10+, standard library only, from the repository root:

```sh
python3 projects/sediment-event-order/paired_protocol_check.py > /tmp/paired-preflight.json
python3 -m unittest discover -s projects/sediment-event-order -p test_paired_protocol_check.py
```

The first command returns one machine-readable JSON report and exits zero only
when its frozen inputs, twelve independent analytic/failure checks, and one
50,000-particle development case in each scenario pass. It is ready for review,
not a milestone completion or scientific acceptance. `--manifest` checks and
prints the plan without fitting. The outer process stops its worker after 180
seconds. Timeout or errors exit nonzero; missing results never become passes.
The worker refuses every held-out random stream, including indirect generation.

## Frozen scientific inputs

The accepted paired source is Mica `5848d4d`, independently inspected by Fern
at journal 39255 ([source review](../../docs/PAIRED_SOURCE_REVIEW_FERN.md)).
The adopted first-milestone synthetic scope is [MODEL_CONTRACT](MODEL_CONTRACT.md),
not historical climate reconstruction. [PAIRED_EXPERIMENT](PAIRED_EXPERIMENT.md)
specifies the paired law. This freeze changes neither probability law nor seeds.
The script pins nine scientific source, test and contract files and the complete
exported protocol. Any drift refuses preflight and requires an explained new
freeze before evaluation. Runtime/Python fingerprints and all three preflight
artifact hashes accompany the report. These hashes identify inputs; they do not
authenticate fabricated reports or install rules.

The targets are latent ages tau_A and tau_B and delta=tau_B-tau_A, with positive
delta meaning B is older. Events independently follow Uniform(850,1150), so delta
has a triangular prior. Four depths per archive are 0,1,2,3 cm. Each archive has
surface age Normal(800,35 squared), independent positive Gamma increments of
shape 40 and scale 130/40 per cm, and linear interpolation. Mixing is independently
uniform on {25,45,65} for A and {45,65,85} for B.

Each finite specimen has age path(z)-h+Exp(mean=h), zero layer half-width, and
proxy Bernoulli(.9 when age<=tau, .1 otherwise). Each date is specimen age plus
one common Normal(0,50 squared) offset across both archives and independent
Normal(0,100 squared) noise. Shared proxy/date IDs use the same specimen age;
separate IDs do not. The fitter integrates that joint law and receives only
public observations; truth is used afterward for evaluation.

Balanced has (proxy,date,shared)=(4,4,2) per layer. Proxy-rich=(12,2,1),
date-rich=(2,12,1). The latter two have thirteen unique specimens per layer;
balanced has six and changes overlap too. Only the former comparison exchanges
measurement counts while preserving unique specimen count. No cost equivalence.
At a common namespace/index all scenarios share latent events, chronology,
mixing and calibration, while specimen allocations differ. Treat differences as
paired across 128 independent latent draws, never 384 independent replicates.

## Inference, budgets and prospective accounting

Guided importance sampling uses two independent batches totalling exactly
50,000 particles. Chronology/mixing increments retain their priors; the joint
surface/common-offset normal proposal and twelve-cell event proposal both have
exact prior/proposal corrections. Each event proposal retains 20 percent uniform
prior support. The analytic checks separately verify the shared-offset joint
Gaussian limit, positive-mixing shared-specimen integral, event quadrature and
collapsed-normal chronology correction; deliberately broken joint pairing fails.

Each batch needs ESS>=100; means must agree within three combined importance
standard errors, endpoint CDFs within .05, and order probabilities within .05.
These are numerical screens, not a convergence proof. A fit has a cooperative
20-second limit checked every 32 particles and after summarization. A benchmark
has 60 seconds, at most sixteen cases. Registered total charged wall budget is
5,400 seconds; use four-case chunks. Particle storage design budget is 32 MiB,
not an operating-system memory limit. No post-outcome budget or threshold tuning.

Held-out namespace `held-out`, indices 1000..1127 inclusive, stays untouched by
this command; indices below 1000 are retired. Later execution requires independent
milestone-two review and an explicit task. An outcome-driven revision requires a
new version and untouched range. A valid registered run retains every attempt
without retries. Existing reconciliation checks reject duplicate cases, changed
source/Python/protocol, controls, development reports and inconsistent counts;
failures and missing cases stay visible. Accounting fixtures in the preflight
are fabricated records, not held-out simulations.

Report central 90 percent interval coverage among passes with its selected
numerator/denominator, numerical failures, and missing cases out of 128 per
scenario. Report interval widths, order probabilities, declarations at >=.95 or
<=.05, wrong/declarations, and unresolved counts. Posterior PITs are approximate
weighted CDFs, with observed groups A_more_positive and A_not_more_positive
reported separately with group sizes. A prior-only control can look marginally
calibrated; marginal coverage is insufficient evidence of data use.

At nominal .90, binomial standard error with 128 independent cases is .02652;
a two-standard-error band is only a descriptive planning approximation. If all
128 cases declared and zero were wrong, the one-sided 95 percent binomial upper
bound would still be .02313. With fewer declarations it is larger. This is no
rare-error certification, fixed-parameter guarantee or scientific winner rule.
Paired scenario comparisons must retain common indices and failures; report
complete-pair counts and missingness before comparing widths or errors.

## Remaining scientific gates

Before milestone three, implement and independently check misspecification and
simultaneous-event robustness cases and a timing comparator targeting the same
latent climate event. The current Gaussian depth-boundary control cannot be
relabeled as climate time. Age-varying calibration curves, finite-width layers
and continuous mixing priors are still outside this model. Held-out evaluation,
precision audit and independent milestone-two review remain outstanding. This
freeze is an executable synthetic instrument, not an empirical climate result.

## Recorded bounded development output

Python 3.13.2. The bounded preflight returned `READY_FOR_INDEPENDENT_REVIEW`;
all twelve analytic checks passed and each scenario passed its single requested
development case, index zero, guided proposal, 50,000 particles. The three fits
took 8.172, 8.379 and 11.437 seconds (balanced, proxy-rich, date-rich).
All event orders remained unresolved at the frozen threshold. These are three
paired scenario runs on **one** latent draw, not three calibration trials or
an advantage estimate. No held-out stream ran. The separate 22 paired tests and
10 freeze/failure controls passed. No scientific source file was changed.

Exact recorded development rows (timing excluded; values are years where applicable):

```json
{"analytic_checks_passed":12,"development_records":{"balanced":[{"approximate_pit":0.5321295475127275,"covered":true,"endpoint_cdf_disagreement":0.001911170525460415,"index":0,"interval_width":217.48529636042667,"mean_disagreement":0.4693040529382557,"minimum_batch_ess":12581.626080564627,"observed_group":"A_not_more_positive","order":"unresolved","order_probability":0.8481377129558578,"order_probability_disagreement":0.004289483328159482,"predicted_order_error":null,"squared_error":40.92772174692931,"status":"PASS_DIAGNOSTICS","three_mcse":2.2749859962517798,"wrong_order":null}],"date-rich":[{"approximate_pit":0.3863622092064852,"covered":true,"endpoint_cdf_disagreement":0.0011225293846765377,"index":0,"interval_width":244.4198937221921,"mean_disagreement":0.7529207723085563,"minimum_batch_ess":5188.327081563925,"observed_group":"A_not_more_positive","order":"unresolved","order_probability":0.8830460709365493,"order_probability_disagreement":0.0020554754791395347,"predicted_order_error":null,"squared_error":302.3985021885652,"status":"PASS_DIAGNOSTICS","three_mcse":3.9117810245332136,"wrong_order":null}],"proxy-rich":[{"approximate_pit":0.47367717381791813,"covered":true,"endpoint_cdf_disagreement":0.004960668329827889,"index":0,"interval_width":182.1403033127907,"mean_disagreement":1.3446121125633397,"minimum_batch_ess":6923.258020571331,"observed_group":"A_not_more_positive","order":"unresolved","order_probability":0.9202548281932194,"order_probability_disagreement":0.002580376731895373,"predicted_order_error":null,"squared_error":14.675290449981116,"status":"PASS_DIAGNOSTICS","three_mcse":2.738199139069808,"wrong_order":null}]},"held_out_executed":false,"status":"READY_FOR_INDEPENDENT_REVIEW"}
```

The report includes a complete machine-readable manifest and scientific source
hashes. Its preflight-artifact hashes describe the files at that invocation;
this record was added afterward. Reproduction may change wall times and final
document hashes, but not the pinned scientific sources or random streams.
The next action is an independent milestone-two review, then a separately
scoped scientific-comparison slice addressing the gates above before evaluation.

