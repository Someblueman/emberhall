# Held-out sediment comparison: first three independent indices

Sorrel, 24 November 2026. **Interim scientific results, not completed calibration.**
Indices1000,1001,1002 were each executed exactly once under the registration
`729ae32e453bb4a0dc9ff299428431b1e31a9250b114f21bd5955b4c5197b965`. All90 cells are retained in
[heldout_results.csv](heldout_results.csv), including failed and missing cells.
The model/extension/runner/test pins are unchanged from the pre-draw hash freeze
in [HELDOUT_PROTOCOL.md](HELDOUT_PROTOCOL.md). That document records the initial
Git sequencing correction; it must accompany these results.

## What was executed

The three-index slice requested90 cells, attempted90, passed88,
failed2, missing0. These are **three independent latent draws**,
not90 independent observations. The full registered study requests3,840 cells
across128 latent draws: 90 attempted, 88 passed,
2 failed, 3750 missing. Cases, designs and methods
within each index are paired. No fit was repeated, discarded, or given an
outcome-dependent budget. Each fit used50,000 particles, at most20 cooperative
seconds and the remaining portion of its fixed600-second index allowance.

| Index | Elapsed seconds | Passed | Failed | Missing |
|---|---:|---:|---:|---:|
| 1000 | 246.891 | 29 | 1 | 0 |
| 1001 | 242.563 | 30 | 0 | 0 |
| 1002 | 241.165 | 29 | 1 | 0 |

Runtime provenance (identical across these receipts unless shown separately):

`{"protocol_sha256":"ce44adc83c905e751ec43f703720c8c223410d4ef4358a2f5cb9b4b12d6268c1","python":"3.13.2","source_sha256":{"baseline.py":"b7e7039fca18aa0ea618210a865d00ad7904e05077efe0843af66ba65fa62b8a","change_point.py":"fb40bb3265a7117a0f2f9b1440e31754aad9b093bb5d10e81435fc5fcd502787","chronology_model.py":"30d70d5801a65f0e194bf95eabb68a0cfbcb1719c5ccaf7ad41a603f9c0d8eab","continuous.py":"89c9b7389c31666ecc08af13837e58b0e7659a57b0e462f9e2128ca5de0cb861","material_model.py":"c6bee7b0af91c69912d62315f7bd69d6b75b37c0e6c818cd293b9904a9520974","paired_experiment.py":"78bb5b647db08429155ec357186891202d7c51cfdf4f231e733c6b4446901d33"}}`

The CSV uses empty cells for absent scientific quantities, lowercase booleans,
and full round-trip Python numeric precision. Failure status, not a zero or an
imputed posterior, explains an empty scientific value. Its SHA-256 is
`c36b8e77f4aa5b2e23c91c1474d7f8744519a005e67f3f9f0d294b7b25b61195`.
The CSV was decoded back and compared field-for-field with all90 original
receipt cells. The frozen validator passed without changing the registration.

## Coverage and directional declarations

Each row requests three indices in this interim slice and128 in the complete
registration. Coverage and wrong-order fractions are **selected**: coverage
uses successful fits; wrong order uses directional declarations among successes.
Unresolved successful fits are not declarations. Wilson intervals below are
marginal95% intervals, with no multiplicity correction. E means exponential;
G means Gaussian material. F/M are failed/missing within the three-index slice.
At equality either directional declaration is wrong, and unresolved does not
mean equality was detected. The misspecified cases test explicit stress laws,
not calibration to the baseline prior or to real sediment records.

| Case | Design | Method | Pass | F/M | Covered/pass [95%] | Wrong/declared [95%] |
|---|---|---|---:|---:|---|---|
| baseline | balanced | E | 3 | 0/0 | 3/3 [0.4385,1] | 0/2 [0,0.6576] |
| baseline | balanced | G | 3 | 0/0 | 3/3 [0.4385,1] | 0/2 [0,0.6576] |
| baseline | proxy-rich | E | 3 | 0/0 | 3/3 [0.4385,1] | 0/1 [0,0.7935] |
| baseline | proxy-rich | G | 3 | 0/0 | 3/3 [0.4385,1] | 0/1 [0,0.7935] |
| baseline | date-rich | E | 3 | 0/0 | 3/3 [0.4385,1] | 0/1 [0,0.7935] |
| baseline | date-rich | G | 3 | 0/0 | 3/3 [0.4385,1] | 0/1 [0,0.7935] |
| simultaneous | balanced | E | 3 | 0/0 | 2/3 [0.2077,0.9385] | 1/1 [0.2065,1] |
| simultaneous | balanced | G | 3 | 0/0 | 2/3 [0.2077,0.9385] | 1/1 [0.2065,1] |
| simultaneous | proxy-rich | E | 3 | 0/0 | 2/3 [0.2077,0.9385] | 1/1 [0.2065,1] |
| simultaneous | proxy-rich | G | 3 | 0/0 | 2/3 [0.2077,0.9385] | 1/1 [0.2065,1] |
| simultaneous | date-rich | E | 3 | 0/0 | 2/3 [0.2077,0.9385] | 1/1 [0.2065,1] |
| simultaneous | date-rich | G | 3 | 0/0 | 2/3 [0.2077,0.9385] | 1/1 [0.2065,1] |
| mixing-x2 | balanced | E | 3 | 0/0 | 3/3 [0.4385,1] | 0/2 [0,0.6576] |
| mixing-x2 | balanced | G | 3 | 0/0 | 3/3 [0.4385,1] | 0/2 [0,0.6576] |
| mixing-x2 | proxy-rich | E | 3 | 0/0 | 2/3 [0.2077,0.9385] | 0/1 [0,0.7935] |
| mixing-x2 | proxy-rich | G | 3 | 0/0 | 2/3 [0.2077,0.9385] | 0/1 [0,0.7935] |
| mixing-x2 | date-rich | E | 2 | 1/0 | 1/2 [0.09453,0.9055] | 0/0 NA |
| mixing-x2 | date-rich | G | 3 | 0/0 | 2/3 [0.2077,0.9385] | 0/0 NA |
| finite-layer-40 | balanced | E | 3 | 0/0 | 3/3 [0.4385,1] | 0/2 [0,0.6576] |
| finite-layer-40 | balanced | G | 3 | 0/0 | 3/3 [0.4385,1] | 0/2 [0,0.6576] |
| finite-layer-40 | proxy-rich | E | 3 | 0/0 | 3/3 [0.4385,1] | 0/1 [0,0.7935] |
| finite-layer-40 | proxy-rich | G | 3 | 0/0 | 3/3 [0.4385,1] | 0/1 [0,0.7935] |
| finite-layer-40 | date-rich | E | 3 | 0/0 | 3/3 [0.4385,1] | 0/1 [0,0.7935] |
| finite-layer-40 | date-rich | G | 3 | 0/0 | 3/3 [0.4385,1] | 0/1 [0,0.7935] |
| differential-offset-75 | balanced | E | 3 | 0/0 | 3/3 [0.4385,1] | 0/0 NA |
| differential-offset-75 | balanced | G | 3 | 0/0 | 3/3 [0.4385,1] | 0/1 [0,0.7935] |
| differential-offset-75 | proxy-rich | E | 3 | 0/0 | 2/3 [0.2077,0.9385] | 0/1 [0,0.7935] |
| differential-offset-75 | proxy-rich | G | 3 | 0/0 | 2/3 [0.2077,0.9385] | 0/1 [0,0.7935] |
| differential-offset-75 | date-rich | E | 3 | 0/0 | 3/3 [0.4385,1] | 0/0 NA |
| differential-offset-75 | date-rich | G | 2 | 1/0 | 2/2 [0.3424,1] | 0/0 NA |

The unexecuted125 indices remain in every full-study requested denominator.
For example, even3/3 observed coverage leaves full-study coverage identification
bounds[3/128,1] when the other125 outcomes are unknown; it is not evidence of
100% coverage. Numerical failures leave further unknowns. The runner's
aggregate command returns all stratum bounds, failure-or-missing Wilson
intervals, selected error/width intervals and approximate PIT decile counts.
PIT is available only for accepted joint posterior rows; baseline uniformity
cannot be assessed with three draws. No cross-case pooled coverage is reported.

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
| baseline/E/P-D | 3/0 | -1022 [-3.6e+05,3.6e+05] | -43.32 [-600,600] | 0 [-1,1] | 0 [-1,1] |
| baseline/G/P-D | 3/0 | -565.7 [-3.6e+05,3.6e+05] | -54.85 [-600,600] | 0 [-1,1] | 0 [-1,1] |
| baseline/balanced/E-G | 3/0 | -178.7 [-3.6e+05,3.6e+05] | -2.367 [-600,600] | 0 [-1,1] | 0 [-1,1] |
| baseline/proxy-rich/E-G | 3/0 | -316.8 [-3.6e+05,3.6e+05] | 1.366 [-600,600] | 0 [-1,1] | 0 [-1,1] |
| baseline/date-rich/E-G | 3/0 | 139.1 [-3.6e+05,3.6e+05] | -10.17 [-600,600] | 0 [-1,1] | 0 [-1,1] |
| simultaneous/E/P-D | 3/0 | -2889 [-3.6e+05,3.6e+05] | -66.34 [-600,600] | 0 [-1,1] | 0 [-1,1] |
| simultaneous/G/P-D | 3/0 | -3410 [-3.6e+05,3.6e+05] | -63.97 [-600,600] | 0 [-1,1] | 0 [-1,1] |
| simultaneous/balanced/E-G | 3/0 | 358.7 [-3.6e+05,3.6e+05] | 5.142 [-600,600] | 0 [-1,1] | 0 [-1,1] |
| simultaneous/proxy-rich/E-G | 3/0 | 638.4 [-3.6e+05,3.6e+05] | 7.98 [-600,600] | 0 [-1,1] | 0 [-1,1] |
| simultaneous/date-rich/E-G | 3/0 | 117.4 [-3.6e+05,3.6e+05] | 10.35 [-600,600] | 0 [-1,1] | 0 [-1,1] |
| mixing-x2/E/P-D | 2/1 | -1.366e+04 [-3.6e+05,3.6e+05] | -87.13 [-600,600] | 0 [-1,1] | 0 [-1,1] |
| mixing-x2/G/P-D | 3/0 | -6838 [-3.6e+05,3.6e+05] | -87.94 [-600,600] | 0 [-1,1] | 0 [-1,1] |
| mixing-x2/balanced/E-G | 3/0 | -132.1 [-3.6e+05,3.6e+05] | 3.863 [-600,600] | 0 [-1,1] | 0 [-1,1] |
| mixing-x2/proxy-rich/E-G | 3/0 | -444.2 [-3.6e+05,3.6e+05] | -3.391 [-600,600] | 0 [-1,1] | 0 [-1,1] |
| mixing-x2/date-rich/E-G | 2/1 | 3051 [-3.6e+05,3.6e+05] | -4.152 [-600,600] | 0 [-1,1] | 0 [-1,1] |
| finite-layer-40/E/P-D | 3/0 | -6574 [-3.6e+05,3.6e+05] | -88.7 [-600,600] | 0 [-1,1] | 0 [-1,1] |
| finite-layer-40/G/P-D | 3/0 | -6400 [-3.6e+05,3.6e+05] | -98.87 [-600,600] | 0 [-1,1] | 0 [-1,1] |
| finite-layer-40/balanced/E-G | 3/0 | 72.87 [-3.6e+05,3.6e+05] | -8.22 [-600,600] | 0 [-1,1] | 0 [-1,1] |
| finite-layer-40/proxy-rich/E-G | 3/0 | -126.6 [-3.6e+05,3.6e+05] | 0.5825 [-600,600] | 0 [-1,1] | 0 [-1,1] |
| finite-layer-40/date-rich/E-G | 3/0 | 47.21 [-3.6e+05,3.6e+05] | -9.588 [-600,600] | 0 [-1,1] | 0 [-1,1] |
| differential-offset-75/E/P-D | 3/0 | -3627 [-3.6e+05,3.6e+05] | -92.07 [-600,600] | -0.3333 [-1,1] | 0 [-1,1] |
| differential-offset-75/G/P-D | 2/1 | 591.4 [-3.6e+05,3.6e+05] | -75.81 [-600,600] | -0.5 [-1,1] | 0 [-1,1] |
| differential-offset-75/balanced/E-G | 3/0 | -94.78 [-3.6e+05,3.6e+05] | -6.057 [-600,600] | 0 [-1,1] | 0 [-1,1] |
| differential-offset-75/proxy-rich/E-G | 3/0 | -301.8 [-3.6e+05,3.6e+05] | 0.6929 [-600,600] | 0 [-1,1] | 0 [-1,1] |
| differential-offset-75/date-rich/E-G | 2/1 | 2594 [-3.6e+05,3.6e+05] | -2.361 [-600,600] | 0 [-1,1] | 0 [-1,1] |

These broad intervals are a property of the small interim sample and conservative
bounded method. They establish neither a method winner nor calibrated interval
coverage or rare wrong-declaration rates. Complete the128-index registration
before its planned scientific report and independent milestone review. A
material Gaussian comparator targets the same latent event times, but its
normal-age approximation is not assumed to be better than exponential material.

## Reproduce and continue

Run the commands in HELDOUT_PROTOCOL.md with indices1000,1001,1002 into one
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
execute untouched indices1003..1127 exactly once under the existing registration.
Keep failed and missing cells, update the complete-pair and requested-denominator
summaries, and retain this interim history. A bounded next slice should state its
indices before execution. Never raise particle/time budgets to rescue failures.
An outcome-driven model revision needs a new version and untouched stream.
Milestone three remains open; no independent scientific milestone review is
claimed by this builder. The result so far is a runnable, falsifiable experiment
with honest denominators, not evidence that either design or model wins.
