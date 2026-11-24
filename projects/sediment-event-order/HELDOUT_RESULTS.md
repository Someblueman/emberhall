# Held-out sediment comparison: first twenty-eight independent indices

Sorrel and Gorse, 24 November 2026. **Interim scientific results, not completed calibration.**
Indices 1000..1027 were each executed exactly once under the registration
`729ae32e453bb4a0dc9ff299428431b1e31a9250b114f21bd5955b4c5197b965`. All 840 cells are retained in
[heldout_results.csv](heldout_results.csv), including failed and missing cells.
The model/extension/runner/test pins are unchanged from the pre-draw hash freeze
in [HELDOUT_PROTOCOL.md](HELDOUT_PROTOCOL.md). That document records the initial
Git sequencing correction; it must accompany these results.

## What was executed

The twenty-eight-index slice requested 840 cells, attempted 840, passed 738,
failed 102, missing 0. These are **twenty-eight independent latent draws**,
not 840 independent observations. The full registered study requests 3,840 cells
across 128 latent draws: 840 attempted, 738 passed,
102 failed, 3000 missing. Cases, designs and methods
within each index are paired. No fit was repeated, discarded, or given an
outcome-dependent budget. Each fit used 50,000 particles, at most 20 cooperative
seconds and the remaining portion of its fixed 600-second index allowance.

| Index | Elapsed seconds | Passed | Failed | Missing |
|---|---:|---:|---:|---:|
| 1000 | 246.891 | 29 | 1 | 0 |
| 1001 | 242.563 | 30 | 0 | 0 |
| 1002 | 241.165 | 29 | 1 | 0 |
| 1003 | 243.089 | 29 | 1 | 0 |
| 1004 | 240.493 | 30 | 0 | 0 |
| 1005 | 240.297 | 24 | 6 | 0 |
| 1006 | 243.824 | 29 | 1 | 0 |
| 1007 | 239.475 | 30 | 0 | 0 |
| 1008 | 273.461 | 28 | 2 | 0 |
| 1009 | 247.853 | 30 | 0 | 0 |
| 1010 | 243.329 | 30 | 0 | 0 |
| 1011 | 244.706 | 30 | 0 | 0 |
| 1012 | 242.058 | 29 | 1 | 0 |
| 1013 | 240.358 | 29 | 1 | 0 |
| 1014 | 242.692 | 30 | 0 | 0 |
| 1015 | 241.850 | 28 | 2 | 0 |
| 1016 | 241.298 | 29 | 1 | 0 |
| 1017 | 242.642 | 29 | 1 | 0 |
| 1018 | 516.792 | 17 | 13 | 0 |
| 1019 | 405.242 | 20 | 10 | 0 |
| 1020 | 534.306 | 10 | 20 | 0 |
| 1021 | 527.574 | 17 | 13 | 0 |
| 1022 | 400.307 | 28 | 2 | 0 |
| 1023 | 479.144 | 21 | 9 | 0 |
| 1024 | 418.083 | 26 | 4 | 0 |
| 1025 | 480.740 | 20 | 10 | 0 |
| 1026 | 315.982 | 30 | 0 | 0 |
| 1027 | 354.293 | 27 | 3 | 0 |

Runtime provenance (all 28 receipts share identical protocol and source hashes; indices 1000..1017 recorded `"python":"3.13.2"` and indices 1018..1027 recorded `"python":"3.15.2"`):

- 1000..1017: `{"protocol_sha256":"ce44adc83c905e751ec43f703720c8c223410d4ef4358a2f5cb9b4b12d6268c1","python":"3.13.2","source_sha256":{"baseline.py":"b7e7039fca18aa0ea618210a865d00ad7904e05077efe0843af66ba65fa62b8a","change_point.py":"fb40bb3265a7117a0f2f9b1440e31754aad9b093bb5d10e81435fc5fcd502787","chronology_model.py":"30d70d5801a65f0e194bf95eabb68a0cfbcb1719c5ccaf7ad41a603f9c0d8eab","continuous.py":"89c9b7389c31666ecc08af13837e58b0e7659a57b0e462f9e2128ca5de0cb861","material_model.py":"c6bee7b0af91c69912d62315f7bd69d6b75b37c0e6c818cd293b9904a9520974","paired_experiment.py":"78bb5b647db08429155ec357186891202d7c51cfdf4f231e733c6b4446901d33"}}`
- 1018..1027: `{"protocol_sha256":"ce44adc83c905e751ec43f703720c8c223410d4ef4358a2f5cb9b4b12d6268c1","python":"3.15.2","source_sha256":{"baseline.py":"b7e7039fca18aa0ea618210a865d00ad7904e05077efe0843af66ba65fa62b8a","change_point.py":"fb40bb3265a7117a0f2f9b1440e31754aad9b093bb5d10e81435fc5fcd502787","chronology_model.py":"30d70d5801a65f0e194bf95eabb68a0cfbcb1719c5ccaf7ad41a603f9c0d8eab","continuous.py":"89c9b7389c31666ecc08af13837e58b0e7659a57b0e462f9e2128ca5de0cb861","material_model.py":"c6bee7b0af91c69912d62315f7bd69d6b75b37c0e6c818cd293b9904a9520974","paired_experiment.py":"78bb5b647db08429155ec357186891202d7c51cfdf4f231e733c6b4446901d33"}}`

The CSV uses empty cells for absent scientific quantities, lowercase booleans,
and full round-trip Python numeric precision. Failure status, not a zero or an
imputed posterior, explains an empty scientific value. Its SHA-256 is
`f5d8327f03173b93f2400505fd7c8178cfa606a8d0e70d7d3690ae015f8caea1`.
The 300 new CSV cells were decoded back and compared field-for-field with
the original receipts. The earlier 540 rows were preserved byte-for-byte.
The frozen validator passed without changing the registration.

Across the twenty-eight-index slice, the 102 failures comprise 24
importance-diagnostic refusals (`FAILED_IMPORTANCE_DIAGNOSTICS`: 16 exponential
and 8 Gaussian material fits, including 5 exponential and 1 Gaussian in
1018..1027) and 78 cooperative per-fit time-budget refusals
(`FAILED_TIME_BUDGET`: 57 exponential and 21 Gaussian material fits in
1018..1025 and 1027 under concurrent host CPU load while every index stayed
within the 600-second index budget). No missing cell occurred in this
twenty-eight-index slice. Per the frozen protocol, no failed fit was retried or
given an outcome-dependent budget. Passing summaries therefore remain selected
by the numerical and time-budget screens; a zero missing count does not remove
that selection.

## Coverage and directional declarations

Each row requests twenty-eight indices in this interim slice and 128 in the complete
registration. Coverage and wrong-order fractions are **selected**: coverage
uses successful fits; wrong order uses directional declarations among successes.
Unresolved successful fits are not declarations. Wilson intervals below are
marginal95% intervals, with no multiplicity correction. E means exponential;
G means Gaussian material. F/M are failed/missing within the twenty-eight-index slice.
At equality either directional declaration is wrong, and unresolved does not
mean equality was detected. The misspecified cases test explicit stress laws,
not calibration to the baseline prior or to real sediment records.

| Case | Design | Method | Pass | F/M | Covered/pass [95%] | Wrong/declared [95%] |
|---|---|---|---:|---:|---|---|
| baseline | balanced | E | 27 | 1/0 | 27/27 [0.8754,1] | 0/9 [0,0.2991] |
| baseline | balanced | G | 27 | 1/0 | 27/27 [0.8754,1] | 0/8 [0,0.3244] |
| baseline | proxy-rich | E | 26 | 2/0 | 25/26 [0.8111,0.9932] | 0/9 [0,0.2991] |
| baseline | proxy-rich | G | 27 | 1/0 | 25/27 [0.7663,0.9794] | 0/11 [0,0.2588] |
| baseline | date-rich | E | 23 | 5/0 | 21/23 [0.732,0.9758] | 0/6 [2.776e-17,0.3903] |
| baseline | date-rich | G | 26 | 2/0 | 25/26 [0.8111,0.9932] | 0/6 [2.776e-17,0.3903] |
| simultaneous | balanced | E | 25 | 3/0 | 22/25 [0.7004,0.9583] | 3/3 [0.4385,1] |
| simultaneous | balanced | G | 28 | 0/0 | 27/28 [0.8229,0.9937] | 1/1 [0.2065,1] |
| simultaneous | proxy-rich | E | 24 | 4/0 | 23/24 [0.7976,0.9926] | 1/1 [0.2065,1] |
| simultaneous | proxy-rich | G | 24 | 4/0 | 23/24 [0.7976,0.9926] | 1/1 [0.2065,1] |
| simultaneous | date-rich | E | 20 | 8/0 | 17/20 [0.6396,0.9476] | 3/3 [0.4385,1] |
| simultaneous | date-rich | G | 27 | 1/0 | 24/27 [0.7194,0.9615] | 3/3 [0.4385,1] |
| mixing-x2 | balanced | E | 22 | 6/0 | 21/22 [0.782,0.9919] | 0/8 [0,0.3244] |
| mixing-x2 | balanced | G | 25 | 3/0 | 23/25 [0.7503,0.9778] | 0/9 [0,0.2991] |
| mixing-x2 | proxy-rich | E | 21 | 7/0 | 19/21 [0.7109,0.9735] | 0/7 [5.551e-17,0.3543] |
| mixing-x2 | proxy-rich | G | 26 | 2/0 | 24/26 [0.7586,0.9786] | 0/12 [2.776e-17,0.2425] |
| mixing-x2 | date-rich | E | 11 | 17/0 | 9/11 [0.523,0.9486] | 0/2 [0,0.6576] |
| mixing-x2 | date-rich | G | 24 | 4/0 | 20/24 [0.6415,0.9332] | 0/6 [2.776e-17,0.3903] |
| finite-layer-40 | balanced | E | 25 | 3/0 | 24/25 [0.8046,0.9929] | 0/11 [0,0.2588] |
| finite-layer-40 | balanced | G | 27 | 1/0 | 26/27 [0.8172,0.9934] | 0/12 [2.776e-17,0.2425] |
| finite-layer-40 | proxy-rich | E | 25 | 3/0 | 24/25 [0.8046,0.9929] | 0/9 [0,0.2991] |
| finite-layer-40 | proxy-rich | G | 24 | 4/0 | 23/24 [0.7976,0.9926] | 0/9 [0,0.2991] |
| finite-layer-40 | date-rich | E | 22 | 6/0 | 21/22 [0.782,0.9919] | 0/5 [0,0.4345] |
| finite-layer-40 | date-rich | G | 27 | 1/0 | 25/27 [0.7663,0.9794] | 0/7 [5.551e-17,0.3543] |
| differential-offset-75 | balanced | E | 26 | 2/0 | 17/26 [0.4622,0.8059] | 0/11 [0,0.2588] |
| differential-offset-75 | balanced | G | 27 | 1/0 | 18/27 [0.4782,0.8136] | 0/11 [0,0.2588] |
| differential-offset-75 | proxy-rich | E | 25 | 3/0 | 13/25 [0.335,0.6997] | 1/13 [0.01371,0.3331] |
| differential-offset-75 | proxy-rich | G | 27 | 1/0 | 15/27 [0.3731,0.7241] | 1/14 [0.01272,0.3147] |
| differential-offset-75 | date-rich | E | 25 | 3/0 | 19/25 [0.5657,0.885] | 0/8 [0,0.3244] |
| differential-offset-75 | date-rich | G | 25 | 3/0 | 19/25 [0.5657,0.885] | 0/6 [2.776e-17,0.3903] |

The unexecuted 100 indices remain in every full-study requested denominator.
For example, even 27/27 observed coverage leaves full-study coverage identification
bounds[27/128,1] when the other 101 outcomes are unknown; it is not evidence of
100% coverage. Numerical failures leave further unknowns. The runner's
aggregate command returns all stratum bounds, failure-or-missing Wilson
intervals, selected error/width intervals and approximate PIT decile counts.
PIT is available only for accepted joint posterior rows; baseline uniformity
cannot be assessed with twenty-eight draws. No cross-case pooled coverage is reported.

## Paired contrasts and their uncertainty

P-D compares proxy-rich minus date-rich at matched unique specimen count.
E-G compares exponential minus Gaussian material within each design. The
balanced design changes overlap too; it is not a clean count-budget contrast.
Only complete passing pairs enter each mean, with all incomplete pairs counted.
The displayed intervals are conservative marginal95% Hoeffding intervals for
bounded differences, not standard errors treating methods/designs as independent.
The wrong-declaration contrast uses one for a false declaration and zero for
correct or unresolved successful fits; it differs from wrong/declared above.
Time/diagnostic selection can bias these complete-pair summaries. Squared error
is in years squared, width in years, and the last two columns are indicators.

| Case / contrast | Complete/incomplete | Squared error difference [95%] | Width difference [95%] | Coverage difference [95%] | False declaration difference [95%] |
|---|---:|---|---|---|---|
| baseline/E/P-D | 23/5 | -2372 [-2.063e+05,2.015e+05] | -67.12 [-406.9,272.7] | 0.04348 [-0.5229,0.6098] | 0 [-0.5664,0.5664] |
| baseline/G/P-D | 26/2 | -2964 [-1.947e+05,1.888e+05] | -79.53 [-399.1,240.1] | -0.03846 [-0.5712,0.4942] | 0 [-0.5327,0.5327] |
| baseline/balanced/E-G | 27/1 | 21.6 [-1.882e+05,1.882e+05] | -0.9998 [-314.6,312.6] | 0 [-0.5227,0.5227] | 0 [-0.5227,0.5227] |
| baseline/proxy-rich/E-G | 26/2 | -114.4 [-1.919e+05,1.917e+05] | 3.781 [-315.8,323.4] | 0.03846 [-0.4942,0.5712] | 0 [-0.5327,0.5327] |
| baseline/date-rich/E-G | 23/5 | -340.4 [-2.042e+05,2.036e+05] | -4.709 [-344.5,335.1] | -0.04348 [-0.6098,0.5229] | 0 [-0.5664,0.5664] |
| simultaneous/E/P-D | 20/8 | -4449 [-2.231e+05,2.142e+05] | -76.68 [-441.1,287.7] | 0.1 [-0.5074,0.7074] | -0.1 [-0.7074,0.5074] |
| simultaneous/G/P-D | 24/4 | -2959 [-2.026e+05,1.966e+05] | -78.68 [-411.3,254] | 0.04167 [-0.5128,0.5961] | -0.04167 [-0.5961,0.5128] |
| simultaneous/balanced/E-G | 25/3 | 178.8 [-1.954e+05,1.957e+05] | 1.899 [-324,327.8] | -0.08 [-0.6232,0.4632] | 0.08 [-0.4632,0.6232] |
| simultaneous/proxy-rich/E-G | 23/5 | 123.8 [-2.038e+05,2.04e+05] | 4.029 [-335.8,343.8] | 0 [-0.5664,0.5664] | 0 [-0.5664,0.5664] |
| simultaneous/date-rich/E-G | 20/8 | 65.2 [-2.186e+05,2.187e+05] | -1.93 [-366.3,362.5] | 0 [-0.6074,0.6074] | 0 [-0.6074,0.6074] |
| mixing-x2/E/P-D | 11/17 | -5838 [-3.007e+05,2.89e+05] | -83.45 [-574.8,407.9] | 0.09091 [-0.7281,0.9099] | 0 [-0.819,0.819] |
| mixing-x2/G/P-D | 23/5 | -4602 [-2.085e+05,1.993e+05] | -81.78 [-421.6,258] | 0.1304 [-0.4359,0.6968] | 0 [-0.5664,0.5664] |
| mixing-x2/balanced/E-G | 21/7 | 466 [-2.129e+05,2.138e+05] | -1.275 [-356.9,354.4] | 0 [-0.5927,0.5927] | 0 [-0.5927,0.5927] |
| mixing-x2/proxy-rich/E-G | 21/7 | -167.2 [-2.135e+05,2.132e+05] | 2.113 [-353.5,357.7] | 0 [-0.5927,0.5927] | 0 [-0.5927,0.5927] |
| mixing-x2/date-rich/E-G | 10/18 | 288 [-3.089e+05,3.095e+05] | -2.145 [-517.5,513.2] | 0.1 [-0.7589,0.9589] | 0 [-0.8589,0.8589] |
| finite-layer-40/E/P-D | 21/7 | -1879 [-2.153e+05,2.115e+05] | -69.11 [-424.7,286.5] | -0.04762 [-0.6403,0.5451] | 0 [-0.5927,0.5927] |
| finite-layer-40/G/P-D | 23/5 | -2554 [-2.064e+05,2.013e+05] | -82.79 [-422.6,257] | -0.04348 [-0.6098,0.5229] | 0 [-0.5664,0.5664] |
| finite-layer-40/balanced/E-G | 25/3 | 56.69 [-1.955e+05,1.956e+05] | -5.695 [-331.6,320.2] | 0 [-0.5432,0.5432] | 0 [-0.5432,0.5432] |
| finite-layer-40/proxy-rich/E-G | 24/4 | 98.3 [-1.995e+05,1.997e+05] | 4.604 [-328.1,337.3] | 0 [-0.5544,0.5544] | 0 [-0.5544,0.5544] |
| finite-layer-40/date-rich/E-G | 22/6 | 201.7 [-2.083e+05,2.087e+05] | -7.79 [-355.2,339.7] | 0 [-0.5791,0.5791] | 0 [-0.5791,0.5791] |
| differential-offset-75/E/P-D | 25/3 | -5378 [-2.009e+05,1.902e+05] | -72.18 [-398.1,253.8] | -0.24 [-0.7832,0.3032] | 0.04 [-0.5032,0.5832] |
| differential-offset-75/G/P-D | 25/3 | -5710 [-2.013e+05,1.899e+05] | -77.19 [-403.1,248.8] | -0.2 [-0.7432,0.3432] | 0.04 [-0.5032,0.5832] |
| differential-offset-75/balanced/E-G | 26/2 | -69.31 [-1.918e+05,1.917e+05] | -2.614 [-322.2,317] | -0.03846 [-0.5712,0.4942] | 0 [-0.5327,0.5327] |
| differential-offset-75/proxy-rich/E-G | 25/3 | -376.2 [-1.959e+05,1.952e+05] | 3.308 [-322.6,329.3] | 0 [-0.5432,0.5432] | 0 [-0.5432,0.5432] |
| differential-offset-75/date-rich/E-G | 23/5 | -116.2 [-2.04e+05,2.038e+05] | -2.416 [-342.2,337.4] | 0 [-0.5664,0.5664] | 0 [-0.5664,0.5664] |

These broad intervals are a property of the small interim sample and conservative
bounded method. They establish neither a method winner nor calibrated interval
coverage or rare wrong-declaration rates. Complete the128-index registration
before its planned scientific report and independent milestone review. A
material Gaussian comparator targets the same latent event times, but its
normal-age approximation is not assumed to be better than exponential material.

## Reproduce and continue

Run the commands in HELDOUT_PROTOCOL.md with indices 1000..1027 into one
fresh, explicitly labelled reproduction directory. Existing original receipts
must not be overwritten or selectively replaced. Cooperative deadlines and
platform speed can change numerical-failure status; the particle streams and
frozen scientific law are deterministic. Do not combine reproduction receipts
with the original study or choose the better of repeated fits.

The following standard-library command reproduces the full registered-denominator
summary from the committed CSV alone, after checking the source registration:

```sh
python3 - <<'PYCSV'
import csv,json,sys
sys.path.insert(0,'projects/sediment-event-order')
import heldout_protocol as h
h.validate_registration('729ae32e453bb4a0dc9ff299428431b1e31a9250b114f21bd5955b4c5197b965')
numeric={'squared_error','predicted_order_error','approximate_pit',
         'interval_width','order_probability','minimum_batch_ess'}
with open('projects/sediment-event-order/heldout_results.csv',newline='') as f:
    rows=[{k:(None if v=='' else int(v) if k=='index' else float(v) if k in numeric
              else v=='true' if k in ('covered','wrong_order') else v)
           for k,v in r.items()} for r in csv.DictReader(f)]
print(json.dumps(h.summarize(rows,tuple(range(1000,1128))),sort_keys=True))
PYCSV
```

Next work: claim exclusive ownership of the result CSV and this report, then
execute untouched indices 1028..1127 exactly once under the existing registration.
Keep failed and missing cells, update the complete-pair and requested-denominator
summaries, and retain this interim history. A bounded next slice should state its
indices before execution. Never raise particle/time budgets to rescue failures.
An outcome-driven model revision needs a new version and untouched stream.
Milestone three remains open; no independent scientific milestone review is
claimed by this builder. The result so far is a runnable, falsifiable experiment
with honest denominators, not evidence that either design or model wins.

Baseline matches the exponential generating law exactly; Gaussian material is
already a misspecified comparator there. Nominal 90% coverage is an evaluation
reference for both, not a guarantee for the Gaussian approximation. The
uncertainty intervals treat latent indices as independent sampling units; they
do not quantify model misspecification or numerical approximation error.

The initial three-index snapshot remains in Git and the immutable task finish.
Its 90 original CSV rows remain an exact byte prefix. The eight-index snapshot
was independently integrated at journal 40461. The thirteen-index snapshot is
private commit 9b7adb8 and task finish 40593. The eighteen-index snapshot
(SHA-256 `9fcf0fd0870cc078193a379fd5caf0c501dd97505bebf23987731ea0ea8f36f0`)
is commit 1da1d30 and task finish 40736.
This continuation appended indices 1018..1027 exactly once, preserving all
540 earlier rows byte-for-byte. No frozen source or budgets changed. The ten
new index receipts remain in this private run; the committed CSV and table
carry their outcomes and elapsed times.
