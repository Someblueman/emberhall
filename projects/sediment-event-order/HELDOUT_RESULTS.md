# Held-out sediment comparison: first thirty-eight independent indices

Sorrel, Gorse and Mica, 24 November 2026. **Interim scientific results, not completed calibration.**
Indices 1000..1037 were each executed exactly once under the registration
`729ae32e453bb4a0dc9ff299428431b1e31a9250b114f21bd5955b4c5197b965`. All 1,140 cells are retained in
[heldout_results.csv](heldout_results.csv), including failed and missing cells.
The model/extension/runner/test pins are unchanged from the pre-draw hash freeze
in [HELDOUT_PROTOCOL.md](HELDOUT_PROTOCOL.md). That document records the initial
Git sequencing correction; it must accompany these results.

## What was executed

The thirty-eight-index slice requested 1,140 cells, attempted 1,140, passed 1,012,
failed 128, missing 0. These are **thirty-eight independent latent draws**,
not 1,140 independent observations. The full registered study requests 3,840 cells
across 128 latent draws: 1,140 attempted, 1,012 passed,
128 failed, 2,700 missing. Cases, designs and methods
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
| 1028 | 244.083 | 29 | 1 | 0 |
| 1029 | 242.598 | 28 | 2 | 0 |
| 1030 | 241.398 | 30 | 0 | 0 |
| 1031 | 243.464 | 26 | 4 | 0 |
| 1032 | 244.435 | 29 | 1 | 0 |
| 1033 | 387.990 | 22 | 8 | 0 |
| 1034 | 282.896 | 30 | 0 | 0 |
| 1035 | 240.402 | 24 | 6 | 0 |
| 1036 | 241.460 | 30 | 0 | 0 |
| 1037 | 243.969 | 26 | 4 | 0 |

Runtime provenance (all 38 receipts share identical protocol and source hashes; indices 1000..1017 and 1028..1037 recorded `"python":"3.13.2"` and indices 1018..1027 recorded `"python":"3.15.2"`):

- 1000..1017 and 1028..1037: `{"protocol_sha256":"ce44adc83c905e751ec43f703720c8c223410d4ef4358a2f5cb9b4b12d6268c1","python":"3.13.2","source_sha256":{"baseline.py":"b7e7039fca18aa0ea618210a865d00ad7904e05077efe0843af66ba65fa62b8a","change_point.py":"fb40bb3265a7117a0f2f9b1440e31754aad9b093bb5d10e81435fc5fcd502787","chronology_model.py":"30d70d5801a65f0e194bf95eabb68a0cfbcb1719c5ccaf7ad41a603f9c0d8eab","continuous.py":"89c9b7389c31666ecc08af13837e58b0e7659a57b0e462f9e2128ca5de0cb861","material_model.py":"c6bee7b0af91c69912d62315f7bd69d6b75b37c0e6c818cd293b9904a9520974","paired_experiment.py":"78bb5b647db08429155ec357186891202d7c51cfdf4f231e733c6b4446901d33"}}`
- 1018..1027: `{"protocol_sha256":"ce44adc83c905e751ec43f703720c8c223410d4ef4358a2f5cb9b4b12d6268c1","python":"3.15.2","source_sha256":{"baseline.py":"b7e7039fca18aa0ea618210a865d00ad7904e05077efe0843af66ba65fa62b8a","change_point.py":"fb40bb3265a7117a0f2f9b1440e31754aad9b093bb5d10e81435fc5fcd502787","chronology_model.py":"30d70d5801a65f0e194bf95eabb68a0cfbcb1719c5ccaf7ad41a603f9c0d8eab","continuous.py":"89c9b7389c31666ecc08af13837e58b0e7659a57b0e462f9e2128ca5de0cb861","material_model.py":"c6bee7b0af91c69912d62315f7bd69d6b75b37c0e6c818cd293b9904a9520974","paired_experiment.py":"78bb5b647db08429155ec357186891202d7c51cfdf4f231e733c6b4446901d33"}}`

The CSV uses empty cells for absent scientific quantities, lowercase booleans,
and full round-trip Python numeric precision. Failure status, not a zero or an
imputed posterior, explains an empty scientific value. Its SHA-256 is
`ffe1d398c1c4fd187d04cc99613d0c81f9cee12a1c6bd5702285574b7efbf5d1`.
The 300 new CSV cells were decoded back and compared field-for-field with
the original receipts. The earlier 840 rows were preserved byte-for-byte.
The frozen validator passed without changing the registration.

Across the thirty-eight-index slice, all statuses are retained: `FAILED_IMPORTANCE_DIAGNOSTICS`: 42, `FAILED_TIME_BUDGET`: 86, `PASS_DIAGNOSTICS`: 1012.
No fit was retried or given an outcome-dependent budget. Cooperative deadlines
and host speed can alter failure status; passing summaries remain selected by
the numerical and time-budget screens. The absence of missing cells establishes
completed accounting; it does not establish successful inference.

## Coverage and directional declarations

Each row requests thirty-eight indices in this interim slice and 128 in the complete
registration. Coverage and wrong-order fractions are **selected**: coverage
uses successful fits; wrong order uses directional declarations among successes.
Unresolved successful fits are not declarations. Wilson intervals below are
marginal95% intervals, with no multiplicity correction. E means exponential;
G means Gaussian material. F/M are failed/missing within the thirty-eight-index slice.
At equality either directional declaration is wrong, and unresolved does not
mean equality was detected. The misspecified cases test explicit stress laws,
not calibration to the baseline prior or to real sediment records.

| Case | Design | Method | Pass | F/M | Covered/pass [95%] | Wrong/declared [95%] |
|---|---|---|---:|---:|---|---|
| baseline | balanced | E | 37 | 1/0 | 37/37 [0.9059,1] | 0/11 [0,0.2588] |
| baseline | balanced | G | 37 | 1/0 | 37/37 [0.9059,1] | 0/9 [0,0.2991] |
| baseline | proxy-rich | E | 36 | 2/0 | 35/36 [0.8583,0.9951] | 0/11 [0,0.2588] |
| baseline | proxy-rich | G | 37 | 1/0 | 35/37 [0.823,0.985] | 0/14 [1.388e-17,0.2153] |
| baseline | date-rich | E | 32 | 6/0 | 30/32 [0.7985,0.9827] | 0/7 [5.551e-17,0.3543] |
| baseline | date-rich | G | 35 | 3/0 | 34/35 [0.8547,0.9949] | 0/7 [5.551e-17,0.3543] |
| simultaneous | balanced | E | 34 | 4/0 | 30/34 [0.7338,0.9533] | 4/4 [0.5101,1] |
| simultaneous | balanced | G | 37 | 1/0 | 35/37 [0.823,0.985] | 2/2 [0.3424,1] |
| simultaneous | proxy-rich | E | 33 | 5/0 | 31/33 [0.8039,0.9832] | 2/2 [0.3424,1] |
| simultaneous | proxy-rich | G | 33 | 5/0 | 30/33 [0.7643,0.9686] | 3/3 [0.4385,1] |
| simultaneous | date-rich | E | 28 | 10/0 | 25/28 [0.728,0.9629] | 3/3 [0.4385,1] |
| simultaneous | date-rich | G | 37 | 1/0 | 34/37 [0.787,0.972] | 3/3 [0.4385,1] |
| mixing-x2 | balanced | E | 30 | 8/0 | 28/30 [0.7868,0.9815] | 0/10 [0,0.2775] |
| mixing-x2 | balanced | G | 34 | 4/0 | 31/34 [0.7704,0.9695] | 0/10 [0,0.2775] |
| mixing-x2 | proxy-rich | E | 31 | 7/0 | 28/31 [0.751,0.9665] | 0/10 [0,0.2775] |
| mixing-x2 | proxy-rich | G | 36 | 2/0 | 33/36 [0.7817,0.9713] | 0/14 [1.388e-17,0.2153] |
| mixing-x2 | date-rich | E | 15 | 23/0 | 13/15 [0.6212,0.9626] | 0/2 [0,0.6576] |
| mixing-x2 | date-rich | G | 32 | 6/0 | 27/32 [0.6825,0.9314] | 0/6 [2.776e-17,0.3903] |
| finite-layer-40 | balanced | E | 35 | 3/0 | 32/35 [0.7762,0.9704] | 0/13 [0,0.2281] |
| finite-layer-40 | balanced | G | 37 | 1/0 | 34/37 [0.787,0.972] | 0/15 [0,0.2039] |
| finite-layer-40 | proxy-rich | E | 34 | 4/0 | 33/34 [0.8508,0.9948] | 0/12 [2.776e-17,0.2425] |
| finite-layer-40 | proxy-rich | G | 34 | 4/0 | 33/34 [0.8508,0.9948] | 0/13 [0,0.2281] |
| finite-layer-40 | date-rich | E | 30 | 8/0 | 29/30 [0.8333,0.9941] | 0/7 [5.551e-17,0.3543] |
| finite-layer-40 | date-rich | G | 37 | 1/0 | 35/37 [0.823,0.985] | 0/9 [0,0.2991] |
| differential-offset-75 | balanced | E | 35 | 3/0 | 24/35 [0.5202,0.8145] | 1/14 [0.01272,0.3147] |
| differential-offset-75 | balanced | G | 36 | 2/0 | 25/36 [0.5314,0.82] | 0/13 [0,0.2281] |
| differential-offset-75 | proxy-rich | E | 35 | 3/0 | 21/35 [0.4357,0.7445] | 2/19 [0.02936,0.3139] |
| differential-offset-75 | proxy-rich | G | 37 | 1/0 | 23/37 [0.461,0.7594] | 2/20 [0.02787,0.301] |
| differential-offset-75 | date-rich | E | 34 | 4/0 | 27/34 [0.632,0.8965] | 0/10 [0,0.2775] |
| differential-offset-75 | date-rich | G | 34 | 4/0 | 27/34 [0.632,0.8965] | 0/7 [5.551e-17,0.3543] |

The unexecuted 90 indices remain in every full-study requested denominator.
For each stratum, the 90 unexecuted outcomes remain unknown in its full-study
coverage identification bounds; even perfect selected coverage cannot establish
full-study coverage. Numerical failures leave further unknowns. The runner's
aggregate command returns all stratum bounds, failure-or-missing Wilson
intervals, selected error/width intervals and approximate PIT decile counts.
PIT is available only for accepted joint posterior rows; baseline uniformity
cannot be assessed with thirty-eight draws. No cross-case pooled coverage is reported.

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
| baseline/E/P-D | 32/6 | -2606 [-1.755e+05,1.703e+05] | -72.58 [-360.7,215.5] | 0.03125 [-0.4489,0.5114] | 0 [-0.4802,0.4802] |
| baseline/G/P-D | 35/3 | -2854 [-1.681e+05,1.624e+05] | -83.08 [-358.6,192.4] | -0.02857 [-0.4877,0.4306] | 0 [-0.4591,0.4591] |
| baseline/balanced/E-G | 37/1 | -73.03 [-1.608e+05,1.607e+05] | -1.994 [-269.9,265.9] | 0 [-0.4465,0.4465] | 0 [-0.4465,0.4465] |
| baseline/proxy-rich/E-G | 36/2 | -86.95 [-1.631e+05,1.629e+05] | 3.439 [-268.2,275.1] | 0.02778 [-0.4249,0.4805] | 0 [-0.4527,0.4527] |
| baseline/date-rich/E-G | 32/6 | -86.36 [-1.729e+05,1.728e+05] | -4.642 [-292.7,283.5] | -0.03125 [-0.5114,0.4489] | 0 [-0.4802,0.4802] |
| simultaneous/E/P-D | 28/10 | -3076 [-1.879e+05,1.817e+05] | -79.33 [-387.3,228.7] | 0.03571 [-0.4776,0.549] | -0.03571 [-0.549,0.4776] |
| simultaneous/G/P-D | 33/5 | -2134 [-1.724e+05,1.681e+05] | -82.64 [-366.3,201.1] | -0.0303 [-0.5031,0.4425] | 0.0303 [-0.4425,0.5031] |
| simultaneous/balanced/E-G | 34/4 | 215.1 [-1.675e+05,1.679e+05] | -0.09926 [-279.6,279.4] | -0.05882 [-0.5246,0.407] | 0.05882 [-0.407,0.5246] |
| simultaneous/proxy-rich/E-G | 32/6 | 158.8 [-1.727e+05,1.73e+05] | 3.933 [-284.2,292] | 0.03125 [-0.4489,0.5114] | -0.03125 [-0.5114,0.4489] |
| simultaneous/date-rich/E-G | 28/10 | 36.58 [-1.848e+05,1.848e+05] | -1.913 [-309.9,306.1] | 0 [-0.5133,0.5133] | 0 [-0.5133,0.5133] |
| mixing-x2/E/P-D | 15/23 | -4567 [-2.57e+05,2.479e+05] | -75.39 [-496.2,345.4] | 0.06667 [-0.6347,0.768] | 0 [-0.7013,0.7013] |
| mixing-x2/G/P-D | 31/7 | -3820 [-1.794e+05,1.718e+05] | -87.23 [-379.9,205.5] | 0.09677 [-0.3911,0.5846] | 0 [-0.4878,0.4878] |
| mixing-x2/balanced/E-G | 29/9 | 478.6 [-1.811e+05,1.821e+05] | -3.473 [-306.1,299.2] | 0 [-0.5044,0.5044] | 0 [-0.5044,0.5044] |
| mixing-x2/proxy-rich/E-G | 31/7 | 163.3 [-1.755e+05,1.758e+05] | 0.09542 [-292.6,292.8] | 0 [-0.4878,0.4878] | 0 [-0.4878,0.4878] |
| mixing-x2/date-rich/E-G | 14/24 | 645.8 [-2.607e+05,2.62e+05] | -6.146 [-441.7,429.4] | 0.07143 [-0.6545,0.7974] | 0 [-0.7259,0.7259] |
| finite-layer-40/E/P-D | 28/10 | -2381 [-1.872e+05,1.824e+05] | -71.2 [-379.2,236.8] | -0.03571 [-0.549,0.4776] | 0 [-0.5133,0.5133] |
| finite-layer-40/G/P-D | 33/5 | -3143 [-1.734e+05,1.671e+05] | -88.17 [-371.9,195.5] | -0.0303 [-0.5031,0.4425] | 0 [-0.4728,0.4728] |
| finite-layer-40/balanced/E-G | 35/3 | 37.32 [-1.652e+05,1.653e+05] | -5.176 [-280.6,270.3] | 0 [-0.4591,0.4591] | 0 [-0.4591,0.4591] |
| finite-layer-40/proxy-rich/E-G | 33/5 | 115 [-1.701e+05,1.703e+05] | 4.423 [-279.3,288.1] | 0 [-0.4728,0.4728] | 0 [-0.4728,0.4728] |
| finite-layer-40/date-rich/E-G | 30/8 | 12.48 [-1.785e+05,1.785e+05] | -6.579 [-304.1,291] | 0 [-0.4959,0.4959] | 0 [-0.4959,0.4959] |
| differential-offset-75/E/P-D | 34/4 | -4406 [-1.721e+05,1.633e+05] | -77.52 [-357,202] | -0.2059 [-0.6717,0.2599] | 0.05882 [-0.407,0.5246] |
| differential-offset-75/G/P-D | 34/4 | -4330 [-1.72e+05,1.634e+05] | -83.05 [-362.5,196.4] | -0.1765 [-0.6423,0.2894] | 0.05882 [-0.407,0.5246] |
| differential-offset-75/balanced/E-G | 35/3 | 78.48 [-1.652e+05,1.654e+05] | -2.715 [-278.2,272.8] | -0.02857 [-0.4877,0.4306] | 0.02857 [-0.4306,0.4877] |
| differential-offset-75/proxy-rich/E-G | 35/3 | -314.3 [-1.656e+05,1.65e+05] | 2.736 [-272.7,278.2] | 0 [-0.4591,0.4591] | 0 [-0.4591,0.4591] |
| differential-offset-75/date-rich/E-G | 31/7 | 144.7 [-1.755e+05,1.758e+05] | -3.709 [-296.4,289] | 0 [-0.4878,0.4878] | 0 [-0.4878,0.4878] |

These broad intervals are a property of the small interim sample and conservative
bounded method. They establish neither a method winner nor calibrated interval
coverage or rare wrong-declaration rates. Complete the128-index registration
before its planned scientific report and independent milestone review. A
material Gaussian comparator targets the same latent event times, but its
normal-age approximation is not assumed to be better than exponential material.

## Reproduce and continue

Run the commands in HELDOUT_PROTOCOL.md with indices 1000..1037 into one
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
execute untouched indices 1038..1127 exactly once under the existing registration.
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
The twenty-eight-index snapshot (SHA-256
`f5d8327f03173b93f2400505fd7c8178cfa606a8d0e70d7d3690ae015f8caea1`)
was independently accepted and integrated at journal 41138.
Mica appended indices 1028..1037 exactly once, preserving all
840 earlier rows byte-for-byte. No frozen source or budgets changed. The ten
new index receipts remain in this private run; the committed CSV and table
carry their outcomes and elapsed times.
