# Held-out sediment comparison: first forty-eight independent indices

Sorrel, Gorse and Mica, 24 November 2026. **Interim scientific results, not completed calibration.**
Indices 1000..1047 were each executed exactly once under the registration
`729ae32e453bb4a0dc9ff299428431b1e31a9250b114f21bd5955b4c5197b965`. All 1,440 cells are retained in
[heldout_results.csv](heldout_results.csv), including failed and missing cells.
The model/extension/runner/test pins are unchanged from the pre-draw hash freeze
in [HELDOUT_PROTOCOL.md](HELDOUT_PROTOCOL.md). That document records the initial
Git sequencing correction; it must accompany these results.

## What was executed

The forty-eight-index slice requested 1,440 cells, attempted 1,440, passed 1,308,
failed 132, missing 0. These are **forty-eight independent latent draws**,
not 1,440 independent observations. The full registered study requests 3,840 cells
across 128 latent draws: 1,440 attempted, 1,308 passed,
132 failed, 2,400 missing. Cases, designs and methods
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

Runtime provenance (all 48 receipts share identical protocol and source hashes; indices 1000..1017 and 1028..1047 recorded `"python":"3.13.2"` and indices 1018..1027 recorded `"python":"3.15.2"`):

- 1000..1017 and 1028..1047: `{"protocol_sha256":"ce44adc83c905e751ec43f703720c8c223410d4ef4358a2f5cb9b4b12d6268c1","python":"3.13.2","source_sha256":{"baseline.py":"b7e7039fca18aa0ea618210a865d00ad7904e05077efe0843af66ba65fa62b8a","change_point.py":"fb40bb3265a7117a0f2f9b1440e31754aad9b093bb5d10e81435fc5fcd502787","chronology_model.py":"30d70d5801a65f0e194bf95eabb68a0cfbcb1719c5ccaf7ad41a603f9c0d8eab","continuous.py":"89c9b7389c31666ecc08af13837e58b0e7659a57b0e462f9e2128ca5de0cb861","material_model.py":"c6bee7b0af91c69912d62315f7bd69d6b75b37c0e6c818cd293b9904a9520974","paired_experiment.py":"78bb5b647db08429155ec357186891202d7c51cfdf4f231e733c6b4446901d33"}}`
- 1018..1027: `{"protocol_sha256":"ce44adc83c905e751ec43f703720c8c223410d4ef4358a2f5cb9b4b12d6268c1","python":"3.15.2","source_sha256":{"baseline.py":"b7e7039fca18aa0ea618210a865d00ad7904e05077efe0843af66ba65fa62b8a","change_point.py":"fb40bb3265a7117a0f2f9b1440e31754aad9b093bb5d10e81435fc5fcd502787","chronology_model.py":"30d70d5801a65f0e194bf95eabb68a0cfbcb1719c5ccaf7ad41a603f9c0d8eab","continuous.py":"89c9b7389c31666ecc08af13837e58b0e7659a57b0e462f9e2128ca5de0cb861","material_model.py":"c6bee7b0af91c69912d62315f7bd69d6b75b37c0e6c818cd293b9904a9520974","paired_experiment.py":"78bb5b647db08429155ec357186891202d7c51cfdf4f231e733c6b4446901d33"}}`

The CSV uses empty cells for absent scientific quantities, lowercase booleans,
and full round-trip Python numeric precision. Failure status, not a zero or an
imputed posterior, explains an empty scientific value. Its SHA-256 is
`4b0ce356b21a9018e88960c5b08b4af33bbd728dff3c8ac00cfddab3ec9d7db3`.
The 300 new CSV cells were decoded back and compared field-for-field with
the original receipts. The earlier 1,140 rows were preserved byte-for-byte.
The frozen validator passed without changing the registration.

Across the forty-eight-index slice, all statuses are retained: `FAILED_IMPORTANCE_DIAGNOSTICS`: 46, `FAILED_TIME_BUDGET`: 86, `PASS_DIAGNOSTICS`: 1308.
No fit was retried or given an outcome-dependent budget. Cooperative deadlines
and host speed can alter failure status; passing summaries remain selected by
the numerical and time-budget screens. The absence of missing cells establishes
completed accounting; it does not establish successful inference.

## Coverage and directional declarations

Each row requests forty-eight indices in this interim slice and 128 in the complete
registration. Coverage and wrong-order fractions are **selected**: coverage
uses successful fits; wrong order uses directional declarations among successes.
Unresolved successful fits are not declarations. Wilson intervals below are
marginal 95% intervals, with no multiplicity correction. E means exponential;
G means Gaussian material. F/M are failed/missing within the forty-eight-index slice.
At equality either directional declaration is wrong, and unresolved does not
mean equality was detected. The misspecified cases test explicit stress laws,
not calibration to the baseline prior or to real sediment records.

| Case | Design | Method | Pass | F/M | Covered/pass [95%] | Wrong/declared [95%] |
|---|---|---|---:|---:|---|---|
| baseline | balanced | E | 47 | 1/0 | 45/47 [0.8575,0.9883] | 0/16 [0,0.1936] |
| baseline | balanced | G | 47 | 1/0 | 45/47 [0.8575,0.9883] | 0/14 [0,0.2153] |
| baseline | proxy-rich | E | 46 | 2/0 | 44/46 [0.8547,0.988] | 0/17 [0,0.1843] |
| baseline | proxy-rich | G | 47 | 1/0 | 44/47 [0.8284,0.9781] | 0/20 [0,0.1611] |
| baseline | date-rich | E | 42 | 6/0 | 38/42 [0.7793,0.9623] | 0/9 [0,0.2991] |
| baseline | date-rich | G | 45 | 3/0 | 42/45 [0.8214,0.9771] | 0/9 [0,0.2991] |
| simultaneous | balanced | E | 44 | 4/0 | 39/44 [0.7602,0.9505] | 5/5 [0.5655,1] |
| simultaneous | balanced | G | 47 | 1/0 | 44/47 [0.8284,0.9781] | 3/3 [0.4385,1] |
| simultaneous | proxy-rich | E | 43 | 5/0 | 40/43 [0.8139,0.976] | 3/3 [0.4385,1] |
| simultaneous | proxy-rich | G | 43 | 5/0 | 39/43 [0.784,0.9632] | 4/4 [0.5101,1] |
| simultaneous | date-rich | E | 38 | 10/0 | 34/38 [0.7587,0.9583] | 4/4 [0.5101,1] |
| simultaneous | date-rich | G | 47 | 1/0 | 43/47 [0.8007,0.9664] | 4/4 [0.5101,1] |
| mixing-x2 | balanced | E | 40 | 8/0 | 36/40 [0.7695,0.9604] | 0/14 [0,0.2153] |
| mixing-x2 | balanced | G | 44 | 4/0 | 39/44 [0.7602,0.9505] | 0/15 [0,0.2039] |
| mixing-x2 | proxy-rich | E | 41 | 7/0 | 37/41 [0.7745,0.9614] | 0/16 [0,0.1936] |
| mixing-x2 | proxy-rich | G | 45 | 3/0 | 41/45 [0.7927,0.9649] | 0/19 [0,0.1682] |
| mixing-x2 | date-rich | E | 23 | 25/0 | 19/23 [0.6286,0.9302] | 0/4 [0,0.4899] |
| mixing-x2 | date-rich | G | 41 | 7/0 | 35/41 [0.7156,0.9312] | 0/9 [0,0.2991] |
| finite-layer-40 | balanced | E | 45 | 3/0 | 39/45 [0.7382,0.9374] | 0/18 [0,0.1759] |
| finite-layer-40 | balanced | G | 47 | 1/0 | 42/47 [0.7741,0.9537] | 0/19 [0,0.1682] |
| finite-layer-40 | proxy-rich | E | 44 | 4/0 | 40/44 [0.7884,0.9641] | 0/19 [0,0.1682] |
| finite-layer-40 | proxy-rich | G | 44 | 4/0 | 41/44 [0.8177,0.9765] | 0/19 [0,0.1682] |
| finite-layer-40 | date-rich | E | 40 | 8/0 | 38/40 [0.835,0.9862] | 0/10 [0,0.2775] |
| finite-layer-40 | date-rich | G | 47 | 1/0 | 43/47 [0.8007,0.9664] | 0/11 [0,0.2588] |
| differential-offset-75 | balanced | E | 45 | 3/0 | 32/45 [0.5663,0.8227] | 1/18 [0.009875,0.2576] |
| differential-offset-75 | balanced | G | 46 | 2/0 | 32/46 [0.5519,0.8092] | 0/16 [0,0.1936] |
| differential-offset-75 | proxy-rich | E | 45 | 3/0 | 28/45 [0.4763,0.7489] | 2/25 [0.02222,0.2497] |
| differential-offset-75 | proxy-rich | G | 47 | 1/0 | 30/47 [0.4954,0.7603] | 2/26 [0.02136,0.2414] |
| differential-offset-75 | date-rich | E | 44 | 4/0 | 35/44 [0.655,0.8885] | 0/12 [0,0.2425] |
| differential-offset-75 | date-rich | G | 44 | 4/0 | 35/44 [0.655,0.8885] | 0/9 [0,0.2991] |

The unexecuted 80 indices remain in every full-study requested denominator.
For each stratum, the 80 unexecuted outcomes remain unknown in its full-study
coverage identification bounds; even perfect selected coverage cannot establish
full-study coverage. Numerical failures leave further unknowns. The runner's
aggregate command returns all stratum bounds, failure-or-missing Wilson
intervals, selected error/width intervals and approximate PIT decile counts.
PIT is available only for accepted joint posterior rows; baseline uniformity
cannot be assessed with forty-eight draws. No cross-case pooled coverage is reported.

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
| baseline/E/P-D | 42/6 | -3334 [-1.542e+05,1.475e+05] | -80.38 [-331.8,171.1] | 0.04762 [-0.3715,0.4667] | 0 [-0.4191,0.4191] |
| baseline/G/P-D | 45/3 | -3606 [-1.494e+05,1.422e+05] | -88.87 [-331.8,154.1] | 0 [-0.4049,0.4049] | 0 [-0.4049,0.4049] |
| baseline/balanced/E-G | 47/1 | -127.8 [-1.428e+05,1.425e+05] | -1.719 [-239.4,236] | 0 [-0.3962,0.3962] | 0 [-0.3962,0.3962] |
| baseline/proxy-rich/E-G | 46/2 | -57.79 [-1.442e+05,1.441e+05] | 3.146 [-237.1,243.4] | 0.02174 [-0.3787,0.4222] | 0 [-0.4005,0.4005] |
| baseline/date-rich/E-G | 42/6 | -191 [-1.511e+05,1.507e+05] | -3.946 [-255.4,247.5] | -0.02381 [-0.4429,0.3953] | 0 [-0.4191,0.4191] |
| simultaneous/E/P-D | 38/10 | -3229 [-1.619e+05,1.554e+05] | -81.34 [-345.7,183] | 0.02632 [-0.4143,0.4669] | -0.02632 [-0.4669,0.4143] |
| simultaneous/G/P-D | 43/5 | -2450 [-1.516e+05,1.467e+05] | -85.08 [-333.6,163.4] | -0.02326 [-0.4375,0.391] | 0.02326 [-0.391,0.4375] |
| simultaneous/balanced/E-G | 44/4 | 101.1 [-1.473e+05,1.475e+05] | -0.2723 [-246,245.4] | -0.04545 [-0.4549,0.364] | 0.04545 [-0.364,0.4549] |
| simultaneous/proxy-rich/E-G | 42/6 | 84.03 [-1.508e+05,1.51e+05] | 2.785 [-248.7,254.3] | 0.02381 [-0.3953,0.4429] | -0.02381 [-0.4429,0.3953] |
| simultaneous/date-rich/E-G | 38/10 | 29.81 [-1.586e+05,1.587e+05] | -3.267 [-267.6,261.1] | 0 [-0.4406,0.4406] | 0 [-0.4406,0.4406] |
| mixing-x2/E/P-D | 23/25 | -5585 [-2.095e+05,1.983e+05] | -78.88 [-418.7,260.9] | 0.08696 [-0.4794,0.6533] | 0 [-0.5664,0.5664] |
| mixing-x2/G/P-D | 39/9 | -4023 [-1.606e+05,1.526e+05] | -88.36 [-349.3,172.6] | 0.07692 [-0.358,0.5119] | 0 [-0.4349,0.4349] |
| mixing-x2/balanced/E-G | 39/9 | 440.4 [-1.561e+05,1.57e+05] | -4.241 [-265.2,256.7] | 0 [-0.4349,0.4349] | 0 [-0.4349,0.4349] |
| mixing-x2/proxy-rich/E-G | 40/8 | 209.4 [-1.544e+05,1.548e+05] | 0.5939 [-257.1,258.3] | 0 [-0.4295,0.4295] | 0 [-0.4295,0.4295] |
| mixing-x2/date-rich/E-G | 21/27 | 185.6 [-2.132e+05,2.136e+05] | -7.495 [-363.1,348.1] | 0.04762 [-0.5451,0.6403] | 0 [-0.5927,0.5927] |
| finite-layer-40/E/P-D | 38/10 | -3199 [-1.618e+05,1.554e+05] | -74.81 [-339.2,189.6] | -0.07895 [-0.5196,0.3617] | 0 [-0.4406,0.4406] |
| finite-layer-40/G/P-D | 43/5 | -3932 [-1.53e+05,1.452e+05] | -90.19 [-338.7,158.3] | -0.02326 [-0.4375,0.391] | 0 [-0.4142,0.4142] |
| finite-layer-40/balanced/E-G | 45/3 | 12.75 [-1.458e+05,1.458e+05] | -4.949 [-247.9,238] | -0.02222 [-0.4271,0.3827] | 0 [-0.4049,0.4049] |
| finite-layer-40/proxy-rich/E-G | 43/5 | 161.5 [-1.49e+05,1.493e+05] | 3.564 [-245,252.1] | -0.02326 [-0.4375,0.391] | 0 [-0.4142,0.4142] |
| finite-layer-40/date-rich/E-G | 40/8 | -173.6 [-1.548e+05,1.544e+05] | -7.745 [-265.4,249.9] | 0.025 [-0.4045,0.4545] | 0 [-0.4295,0.4295] |
| differential-offset-75/E/P-D | 44/4 | -6300 [-1.537e+05,1.411e+05] | -85.51 [-331.2,160.2] | -0.1818 [-0.5913,0.2277] | 0.04545 [-0.364,0.4549] |
| differential-offset-75/G/P-D | 44/4 | -6301 [-1.537e+05,1.411e+05] | -89.68 [-335.4,156] | -0.1591 [-0.5686,0.2504] | 0.04545 [-0.364,0.4549] |
| differential-offset-75/balanced/E-G | 45/3 | 87.64 [-1.457e+05,1.459e+05] | -2.091 [-245,240.9] | 0 [-0.4049,0.4049] | 0.02222 [-0.3827,0.4271] |
| differential-offset-75/proxy-rich/E-G | 45/3 | -194.4 [-1.46e+05,1.456e+05] | 2.898 [-240,245.8] | 0 [-0.4049,0.4049] | 0 [-0.4049,0.4049] |
| differential-offset-75/date-rich/E-G | 41/7 | 100.1 [-1.526e+05,1.528e+05] | -1.848 [-256.4,252.7] | 0 [-0.4242,0.4242] | 0 [-0.4242,0.4242] |

These broad intervals are a property of the small interim sample and conservative
bounded method. They establish neither a method winner nor calibrated interval
coverage or rare wrong-declaration rates. Complete the 128-index registration
before its planned scientific report and independent milestone review. A
material Gaussian comparator targets the same latent event times, but its
normal-age approximation is not assumed to be better than exponential material.

## Reproduce and continue

Run the commands in HELDOUT_PROTOCOL.md with indices 1000..1047 into one
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
execute untouched indices 1048..1127 exactly once under the existing registration.
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
