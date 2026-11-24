# Held-out sediment comparison: first fifty-eight independent indices

Sorrel, Gorse, Mica and Fern, 24 November 2026. **Interim scientific results, not completed calibration.**
Indices 1000..1057 were each executed exactly once under the registration
`729ae32e453bb4a0dc9ff299428431b1e31a9250b114f21bd5955b4c5197b965`. All 1,740 cells are retained in
[heldout_results.csv](heldout_results.csv), including failed and missing cells.
The model/extension/runner/test pins are unchanged from the pre-draw hash freeze
in [HELDOUT_PROTOCOL.md](HELDOUT_PROTOCOL.md). That document records the initial
Git sequencing correction; it must accompany these results.

## What was executed

The fifty-eight-index slice requested 1,740 cells, attempted 1,740, passed 1,603,
failed 137, missing 0. These are **fifty-eight independent latent draws**,
not 1,740 independent observations. The full registered study requests 3,840 cells
across 128 latent draws: 1,740 attempted, 1,603 passed,
137 failed, 2,100 missing. Cases, designs and methods
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
| 1038 | 240.683 | 30 | 0 | 0 |
| 1039 | 242.865 | 29 | 1 | 0 |
| 1040 | 241.607 | 30 | 0 | 0 |
| 1041 | 254.795 | 29 | 1 | 0 |
| 1042 | 242.391 | 30 | 0 | 0 |
| 1043 | 242.916 | 30 | 0 | 0 |
| 1044 | 244.519 | 29 | 1 | 0 |
| 1045 | 243.235 | 30 | 0 | 0 |
| 1046 | 239.248 | 29 | 1 | 0 |
| 1047 | 239.877 | 30 | 0 | 0 |

| 1048 | 264.050 | 30 | 0 | 0 |
| 1049 | 314.646 | 28 | 2 | 0 |
| 1050 | 381.410 | 29 | 1 | 0 |
| 1051 | 363.776 | 30 | 0 | 0 |
| 1052 | 347.095 | 30 | 0 | 0 |
| 1053 | 335.789 | 29 | 1 | 0 |
| 1054 | 301.958 | 29 | 1 | 0 |
| 1055 | 245.853 | 30 | 0 | 0 |
| 1056 | 246.415 | 30 | 0 | 0 |
| 1057 | 248.755 | 30 | 0 | 0 |

Runtime provenance (all 58 receipts share identical protocol and source hashes; indices 1000..1017 and 1028..1057 recorded `"python":"3.13.2"` and indices 1018..1027 recorded `"python":"3.15.2"`):

- 1000..1017 and 1028..1057: `{"protocol_sha256":"ce44adc83c905e751ec43f703720c8c223410d4ef4358a2f5cb9b4b12d6268c1","python":"3.13.2","source_sha256":{"baseline.py":"b7e7039fca18aa0ea618210a865d00ad7904e05077efe0843af66ba65fa62b8a","change_point.py":"fb40bb3265a7117a0f2f9b1440e31754aad9b093bb5d10e81435fc5fcd502787","chronology_model.py":"30d70d5801a65f0e194bf95eabb68a0cfbcb1719c5ccaf7ad41a603f9c0d8eab","continuous.py":"89c9b7389c31666ecc08af13837e58b0e7659a57b0e462f9e2128ca5de0cb861","material_model.py":"c6bee7b0af91c69912d62315f7bd69d6b75b37c0e6c818cd293b9904a9520974","paired_experiment.py":"78bb5b647db08429155ec357186891202d7c51cfdf4f231e733c6b4446901d33"}}`
- 1018..1027: `{"protocol_sha256":"ce44adc83c905e751ec43f703720c8c223410d4ef4358a2f5cb9b4b12d6268c1","python":"3.15.2","source_sha256":{"baseline.py":"b7e7039fca18aa0ea618210a865d00ad7904e05077efe0843af66ba65fa62b8a","change_point.py":"fb40bb3265a7117a0f2f9b1440e31754aad9b093bb5d10e81435fc5fcd502787","chronology_model.py":"30d70d5801a65f0e194bf95eabb68a0cfbcb1719c5ccaf7ad41a603f9c0d8eab","continuous.py":"89c9b7389c31666ecc08af13837e58b0e7659a57b0e462f9e2128ca5de0cb861","material_model.py":"c6bee7b0af91c69912d62315f7bd69d6b75b37c0e6c818cd293b9904a9520974","paired_experiment.py":"78bb5b647db08429155ec357186891202d7c51cfdf4f231e733c6b4446901d33"}}`

The CSV uses empty cells for absent scientific quantities, lowercase booleans,
and full round-trip Python numeric precision. Failure status, not a zero or an
imputed posterior, explains an empty scientific value. Its SHA-256 is
`85c6e05f461a7d7d0e58c4ab2c8e372db9c48346b0bb0f50aa313d128a4b747b`.
The 300 new CSV cells were decoded back and compared field-for-field with
the original receipts. The earlier 1,440 rows were preserved byte-for-byte.
The frozen validator passed without changing the registration.

Across the fifty-eight-index slice, all statuses are retained: `FAILED_IMPORTANCE_DIAGNOSTICS`: 50, `FAILED_TIME_BUDGET`: 87, `PASS_DIAGNOSTICS`: 1603.
No fit was retried or given an outcome-dependent budget. Cooperative deadlines
and host speed can alter failure status; passing summaries remain selected by
the numerical and time-budget screens. The absence of missing cells establishes
completed accounting; it does not establish successful inference.

## Coverage and directional declarations

Each row requests fifty-eight indices in this interim slice and 128 in the complete
registration. Coverage and wrong-order fractions are **selected**: coverage
uses successful fits; wrong order uses directional declarations among successes.
Unresolved successful fits are not declarations. Wilson intervals below are
marginal 95% intervals, with no multiplicity correction. E means exponential;
G means Gaussian material. F/M are failed/missing within the fifty-eight-index slice.
At equality either directional declaration is wrong, and unresolved does not
mean equality was detected. The misspecified cases test explicit stress laws,
not calibration to the baseline prior or to real sediment records.

| Case | Design | Method | Pass | F/M | Covered/pass [95%] | Wrong/declared [95%] |
|---|---|---|---:|---:|---|---|
| baseline | balanced | E | 57 | 1/0 | 55/57 [0.8808,0.9903] | 0/17 [0,0.1843] |
| baseline | balanced | G | 57 | 1/0 | 55/57 [0.8808,0.9903] | 0/15 [0,0.2039] |
| baseline | proxy-rich | E | 56 | 2/0 | 54/56 [0.8788,0.9902] | 0/19 [0,0.1682] |
| baseline | proxy-rich | G | 57 | 1/0 | 54/57 [0.8563,0.9819] | 0/22 [0,0.1487] |
| baseline | date-rich | E | 52 | 6/0 | 48/52 [0.8183,0.9697] | 0/11 [0,0.2588] |
| baseline | date-rich | G | 55 | 3/0 | 52/55 [0.8515,0.9813] | 0/10 [0,0.2775] |
| simultaneous | balanced | E | 54 | 4/0 | 49/54 [0.8009,0.9598] | 5/5 [0.5655,1] |
| simultaneous | balanced | G | 57 | 1/0 | 54/57 [0.8563,0.9819] | 3/3 [0.4385,1] |
| simultaneous | proxy-rich | E | 53 | 5/0 | 50/53 [0.8463,0.9806] | 3/3 [0.4385,1] |
| simultaneous | proxy-rich | G | 53 | 5/0 | 48/53 [0.7975,0.959] | 5/5 [0.5655,1] |
| simultaneous | date-rich | E | 48 | 10/0 | 43/48 [0.7783,0.9547] | 5/5 [0.5655,1] |
| simultaneous | date-rich | G | 57 | 1/0 | 53/57 [0.833,0.9724] | 4/4 [0.5101,1] |
| mixing-x2 | balanced | E | 50 | 8/0 | 46/50 [0.8116,0.9685] | 0/14 [1.388e-17,0.2153] |
| mixing-x2 | balanced | G | 54 | 4/0 | 49/54 [0.8009,0.9598] | 0/16 [0,0.1936] |
| mixing-x2 | proxy-rich | E | 50 | 8/0 | 46/50 [0.8116,0.9685] | 0/18 [0,0.1759] |
| mixing-x2 | proxy-rich | G | 55 | 3/0 | 51/55 [0.8274,0.9714] | 0/21 [0,0.1546] |
| mixing-x2 | date-rich | E | 30 | 28/0 | 26/30 [0.7032,0.9469] | 0/5 [0,0.4345] |
| mixing-x2 | date-rich | G | 51 | 7/0 | 45/51 [0.7662,0.9449] | 0/10 [0,0.2775] |
| finite-layer-40 | balanced | E | 55 | 3/0 | 49/55 [0.7817,0.949] | 0/21 [0,0.1546] |
| finite-layer-40 | balanced | G | 57 | 1/0 | 52/57 [0.8106,0.9619] | 0/22 [0,0.1487] |
| finite-layer-40 | proxy-rich | E | 54 | 4/0 | 49/54 [0.8009,0.9598] | 0/20 [0,0.1611] |
| finite-layer-40 | proxy-rich | G | 54 | 4/0 | 50/54 [0.8245,0.9708] | 0/21 [0,0.1546] |
| finite-layer-40 | date-rich | E | 50 | 8/0 | 47/50 [0.8378,0.9794] | 0/12 [2.776e-17,0.2425] |
| finite-layer-40 | date-rich | G | 56 | 2/0 | 51/56 [0.8074,0.9613] | 0/11 [0,0.2588] |
| differential-offset-75 | balanced | E | 55 | 3/0 | 40/55 [0.5977,0.8272] | 1/22 [0.008069,0.218] |
| differential-offset-75 | balanced | G | 56 | 2/0 | 40/56 [0.5852,0.8158] | 0/20 [0,0.1611] |
| differential-offset-75 | proxy-rich | E | 55 | 3/0 | 35/55 [0.5042,0.7507] | 3/31 [0.03346,0.249] |
| differential-offset-75 | proxy-rich | G | 57 | 1/0 | 37/57 [0.5194,0.76] | 3/32 [0.0324,0.2422] |
| differential-offset-75 | date-rich | E | 54 | 4/0 | 42/54 [0.6506,0.868] | 0/14 [1.388e-17,0.2153] |
| differential-offset-75 | date-rich | G | 54 | 4/0 | 44/54 [0.6916,0.8962] | 0/11 [0,0.2588] |

The unexecuted 70 indices remain in every full-study requested denominator.
For each stratum, the 70 unexecuted outcomes remain unknown in its full-study
coverage identification bounds; even perfect selected coverage cannot establish
full-study coverage. Numerical failures leave further unknowns. The runner's
aggregate command returns all stratum bounds, failure-or-missing Wilson
intervals, selected error/width intervals and approximate PIT decile counts.
PIT is available only for accepted joint posterior rows; baseline uniformity
cannot be assessed with fifty-eight draws. No cross-case pooled coverage is reported.

## Paired contrasts and their uncertainty

P-D compares proxy-rich minus date-rich at matched unique specimen count.
E-G compares exponential minus Gaussian material within each design. The
balanced design changes overlap too; it is not a clean count-budget contrast.
Only complete passing pairs enter each mean, with all incomplete pairs counted.
The displayed intervals are conservative marginal 95% Hoeffding intervals for
bounded differences, not standard errors treating methods/designs as independent.
The wrong-declaration contrast uses one for a false declaration and zero for
correct or unresolved successful fits; it differs from wrong/declared above.
Time/diagnostic selection can bias these complete-pair summaries. Squared error
is in years squared, width in years, and the last two columns are indicators.

| Case / contrast | Complete/incomplete | Squared error difference [95%] | Width difference [95%] | Coverage difference [95%] | False declaration difference [95%] |
|---|---:|---|---|---|---|
| baseline/E/P-D | 52/6 | -3490 [-1.391e+05,1.321e+05] | -81.14 [-307.1,144.9] | 0.03846 [-0.3382,0.4151] | 0 [-0.3767,0.3767] |
| baseline/G/P-D | 55/3 | -3679 [-1.355e+05,1.282e+05] | -89.52 [-309.3,130.2] | 0 [-0.3663,0.3663] | 0 [-0.3663,0.3663] |
| baseline/balanced/E-G | 57/1 | -172.7 [-1.297e+05,1.293e+05] | -0.8451 [-216.7,215] | 0 [-0.3598,0.3598] | 0 [-0.3598,0.3598] |
| baseline/proxy-rich/E-G | 56/2 | -2.193 [-1.307e+05,1.307e+05] | 3.247 [-214.5,221] | 0.01786 [-0.3451,0.3808] | 0 [-0.363,0.363] |
| baseline/date-rich/E-G | 52/6 | -80.23 [-1.357e+05,1.355e+05] | -4.035 [-230,222] | -0.01923 [-0.3959,0.3574] | 0 [-0.3767,0.3767] |
| simultaneous/E/P-D | 48/10 | -3203 [-1.443e+05,1.379e+05] | -83.91 [-319.1,151.3] | 0.04167 [-0.3504,0.4337] | -0.04167 [-0.4337,0.3504] |
| simultaneous/G/P-D | 53/5 | -2404 [-1.367e+05,1.319e+05] | -88.56 [-312.4,135.3] | -0.03774 [-0.4108,0.3354] | 0.03774 [-0.3354,0.4108] |
| simultaneous/balanced/E-G | 54/4 | 60.18 [-1.33e+05,1.331e+05] | 0.5329 [-221.2,222.3] | -0.03704 [-0.4067,0.3326] | 0.03704 [-0.3326,0.4067] |
| simultaneous/proxy-rich/E-G | 52/6 | 71.36 [-1.355e+05,1.357e+05] | 3.096 [-222.9,229.1] | 0.03846 [-0.3382,0.4151] | -0.03846 [-0.4151,0.3382] |
| simultaneous/date-rich/E-G | 48/10 | 214 [-1.409e+05,1.414e+05] | -3.714 [-238.9,231.5] | -0.02083 [-0.4129,0.3712] | 0.02083 [-0.3712,0.4129] |
| mixing-x2/E/P-D | 30/28 | -5726 [-1.843e+05,1.728e+05] | -86.55 [-384.1,211] | 0.06667 [-0.4292,0.5626] | 0 [-0.4959,0.4959] |
| mixing-x2/G/P-D | 49/9 | -4038 [-1.437e+05,1.357e+05] | -89.32 [-322.1,143.5] | 0.06122 [-0.3268,0.4493] | 0 [-0.388,0.388] |
| mixing-x2/balanced/E-G | 49/9 | 269.5 [-1.394e+05,1.4e+05] | -2.18 [-235,230.6] | 0 [-0.388,0.388] | 0 [-0.388,0.388] |
| mixing-x2/proxy-rich/E-G | 49/9 | 139 [-1.396e+05,1.398e+05] | 0.4711 [-232.3,233.3] | 0 [-0.388,0.388] | 0 [-0.388,0.388] |
| mixing-x2/date-rich/E-G | 28/30 | 230.2 [-1.846e+05,1.85e+05] | -4.39 [-312.4,303.6] | 0.03571 [-0.4776,0.549] | 0 [-0.5133,0.5133] |
| finite-layer-40/E/P-D | 48/10 | -3701 [-1.448e+05,1.374e+05] | -73.54 [-308.8,161.7] | -0.0625 [-0.4546,0.3296] | 0 [-0.3921,0.3921] |
| finite-layer-40/G/P-D | 52/6 | -4288 [-1.399e+05,1.313e+05] | -88.14 [-314.1,137.9] | -0.01923 [-0.3959,0.3574] | 0 [-0.3767,0.3767] |
| finite-layer-40/balanced/E-G | 55/3 | -14.82 [-1.319e+05,1.318e+05] | -3.738 [-223.5,216] | -0.01818 [-0.3844,0.3481] | 0 [-0.3663,0.3663] |
| finite-layer-40/proxy-rich/E-G | 53/5 | 165.8 [-1.341e+05,1.345e+05] | 3.833 [-220,227.7] | -0.01887 [-0.392,0.3542] | 0 [-0.3731,0.3731] |
| finite-layer-40/date-rich/E-G | 49/9 | -62.31 [-1.398e+05,1.396e+05] | -6.826 [-239.6,226] | 0.02041 [-0.3676,0.4084] | 0 [-0.388,0.388] |
| differential-offset-75/E/P-D | 54/4 | -5734 [-1.388e+05,1.273e+05] | -83.07 [-304.8,138.7] | -0.1481 [-0.5178,0.2215] | 0.05556 [-0.3141,0.4252] |
| differential-offset-75/G/P-D | 54/4 | -5649 [-1.387e+05,1.274e+05] | -88.69 [-310.5,133.1] | -0.1667 [-0.5363,0.203] | 0.05556 [-0.3141,0.4252] |
| differential-offset-75/balanced/E-G | 55/3 | 25.12 [-1.318e+05,1.319e+05] | -0.8618 [-220.6,218.9] | 0 [-0.3663,0.3663] | 0.01818 [-0.3481,0.3844] |
| differential-offset-75/proxy-rich/E-G | 55/3 | -172.7 [-1.32e+05,1.317e+05] | 3.211 [-216.5,223] | 0 [-0.3663,0.3663] | 0 [-0.3663,0.3663] |
| differential-offset-75/date-rich/E-G | 51/7 | 156.4 [-1.368e+05,1.371e+05] | -2.929 [-231.1,225.3] | -0.03922 [-0.4196,0.3411] | 0 [-0.3803,0.3803] |

These broad intervals are a property of the small interim sample and conservative
bounded method. They establish neither a method winner nor calibrated interval
coverage or rare wrong-declaration rates. Complete the 128-index registration
before its planned scientific report and independent milestone review. A
material Gaussian comparator targets the same latent event times, but its
normal-age approximation is not assumed to be better than exponential material.

## Reproduce and continue

Run the commands in HELDOUT_PROTOCOL.md with indices 1000..1057 into one
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
execute untouched indices 1058..1127 exactly once under the existing registration.
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

The thirty-eight-index snapshot (SHA-256
`ffe1d398c1c4fd187d04cc99613d0c81f9cee12a1c6bd5702285574b7efbf5d1`)
was independently integrated and the next slice readied at journal 41523.
Mica appended indices 1038..1047 exactly once, preserving all 1,140 earlier
rows byte-for-byte. CSV-only recalculation independently checked all 30
Wilson rows and 25 complete-pair Hoeffding rows, including every displayed
table cell. The ten original receipts remain in this private run under
`.house-mailbox/sediment-s48`; no source pins or budgets changed.

The forty-eight-index snapshot (SHA-256
`4b0ce356b21a9018e88960c5b08b4af33bbd728dff3c8ac00cfddab3ec9d7db3`)
was independently integrated at journal 41729. Fern appended indices 1048..1057
exactly once, preserving all 1,440 earlier rows byte-for-byte. All 30 coverage
rows and 25 paired-contrast rows were regenerated from the complete CSV. The ten
original receipts remain in this private run under `.house-mailbox/sediment-58`;
no source pins or budgets changed. Seventy registered draws remain unexecuted.
