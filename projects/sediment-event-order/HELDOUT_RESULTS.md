# Held-out sediment comparison: first eighteen independent indices

Sorrel, 24 November 2026. **Interim scientific results, not completed calibration.**
Indices 1000..1017 were each executed exactly once under the registration
`729ae32e453bb4a0dc9ff299428431b1e31a9250b114f21bd5955b4c5197b965`. All 540 cells are retained in
[heldout_results.csv](heldout_results.csv), including failed and missing cells.
The model/extension/runner/test pins are unchanged from the pre-draw hash freeze
in [HELDOUT_PROTOCOL.md](HELDOUT_PROTOCOL.md). That document records the initial
Git sequencing correction; it must accompany these results.

## What was executed

The eighteen-index slice requested 540 cells, attempted 540, passed 522,
failed 18, missing 0. These are **eighteen independent latent draws**,
not 540 independent observations. The full registered study requests 3,840 cells
across 128 latent draws: 540 attempted, 522 passed,
18 failed, 3300 missing. Cases, designs and methods
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

Runtime provenance (identical across these receipts unless shown separately):

`{"protocol_sha256":"ce44adc83c905e751ec43f703720c8c223410d4ef4358a2f5cb9b4b12d6268c1","python":"3.13.2","source_sha256":{"baseline.py":"b7e7039fca18aa0ea618210a865d00ad7904e05077efe0843af66ba65fa62b8a","change_point.py":"fb40bb3265a7117a0f2f9b1440e31754aad9b093bb5d10e81435fc5fcd502787","chronology_model.py":"30d70d5801a65f0e194bf95eabb68a0cfbcb1719c5ccaf7ad41a603f9c0d8eab","continuous.py":"89c9b7389c31666ecc08af13837e58b0e7659a57b0e462f9e2128ca5de0cb861","material_model.py":"c6bee7b0af91c69912d62315f7bd69d6b75b37c0e6c818cd293b9904a9520974","paired_experiment.py":"78bb5b647db08429155ec357186891202d7c51cfdf4f231e733c6b4446901d33"}}`

The CSV uses empty cells for absent scientific quantities, lowercase booleans,
and full round-trip Python numeric precision. Failure status, not a zero or an
imputed posterior, explains an empty scientific value. Its SHA-256 is
`9fcf0fd0870cc078193a379fd5caf0c501dd97505bebf23987731ea0ea8f36f0`.
The 150 new CSV cells were decoded back and compared field-for-field with
the original receipts. The earlier 390 rows were preserved byte-for-byte.
The frozen validator passed without changing the registration.

All 18 failures were importance-diagnostic refusals: 11 exponential and 7
Gaussian material fits. No time-budget failure or missing cell occurred in this
eighteen-index slice. Passing summaries therefore remain selected by the numerical
screens; a zero missing count does not remove that selection.

## Coverage and directional declarations

Each row requests eighteen indices in this interim slice and 128 in the complete
registration. Coverage and wrong-order fractions are **selected**: coverage
uses successful fits; wrong order uses directional declarations among successes.
Unresolved successful fits are not declarations. Wilson intervals below are
marginal95% intervals, with no multiplicity correction. E means exponential;
G means Gaussian material. F/M are failed/missing within the eighteen-index slice.
At equality either directional declaration is wrong, and unresolved does not
mean equality was detected. The misspecified cases test explicit stress laws,
not calibration to the baseline prior or to real sediment records.

| Case | Design | Method | Pass | F/M | Covered/pass [95%] | Wrong/declared [95%] |
|---|---|---|---:|---:|---|---|
| baseline | balanced | E | 18 | 0/0 | 18/18 [0.8241,1] | 0/6 [2.776e-17,0.3903] |
| baseline | balanced | G | 18 | 0/0 | 18/18 [0.8241,1] | 0/5 [0,0.4345] |
| baseline | proxy-rich | E | 18 | 0/0 | 17/18 [0.7424,0.9901] | 0/7 [5.551e-17,0.3543] |
| baseline | proxy-rich | G | 18 | 0/0 | 16/18 [0.672,0.969] | 0/8 [0,0.3244] |
| baseline | date-rich | E | 18 | 0/0 | 17/18 [0.7424,0.9901] | 0/5 [0,0.4345] |
| baseline | date-rich | G | 18 | 0/0 | 17/18 [0.7424,0.9901] | 0/4 [0,0.4899] |
| simultaneous | balanced | E | 18 | 0/0 | 17/18 [0.7424,0.9901] | 1/1 [0.2065,1] |
| simultaneous | balanced | G | 18 | 0/0 | 17/18 [0.7424,0.9901] | 1/1 [0.2065,1] |
| simultaneous | proxy-rich | E | 18 | 0/0 | 17/18 [0.7424,0.9901] | 1/1 [0.2065,1] |
| simultaneous | proxy-rich | G | 17 | 1/0 | 16/17 [0.7302,0.9895] | 1/1 [0.2065,1] |
| simultaneous | date-rich | E | 17 | 1/0 | 15/17 [0.6566,0.9671] | 2/2 [0.3424,1] |
| simultaneous | date-rich | G | 18 | 0/0 | 16/18 [0.672,0.969] | 2/2 [0.3424,1] |
| mixing-x2 | balanced | E | 17 | 1/0 | 17/17 [0.8157,1] | 0/4 [0,0.4899] |
| mixing-x2 | balanced | G | 18 | 0/0 | 18/18 [0.8241,1] | 0/4 [0,0.4899] |
| mixing-x2 | proxy-rich | E | 17 | 1/0 | 16/17 [0.7302,0.9895] | 0/5 [0,0.4345] |
| mixing-x2 | proxy-rich | G | 17 | 1/0 | 16/17 [0.7302,0.9895] | 0/6 [2.776e-17,0.3903] |
| mixing-x2 | date-rich | E | 10 | 8/0 | 9/10 [0.5958,0.9821] | 0/1 [0,0.7935] |
| mixing-x2 | date-rich | G | 16 | 2/0 | 13/16 [0.5699,0.9341] | 0/1 [0,0.7935] |
| finite-layer-40 | balanced | E | 18 | 0/0 | 18/18 [0.8241,1] | 0/7 [5.551e-17,0.3543] |
| finite-layer-40 | balanced | G | 18 | 0/0 | 18/18 [0.8241,1] | 0/6 [2.776e-17,0.3903] |
| finite-layer-40 | proxy-rich | E | 18 | 0/0 | 17/18 [0.7424,0.9901] | 0/7 [5.551e-17,0.3543] |
| finite-layer-40 | proxy-rich | G | 17 | 1/0 | 16/17 [0.7302,0.9895] | 0/7 [5.551e-17,0.3543] |
| finite-layer-40 | date-rich | E | 18 | 0/0 | 18/18 [0.8241,1] | 0/4 [0,0.4899] |
| finite-layer-40 | date-rich | G | 18 | 0/0 | 18/18 [0.8241,1] | 0/4 [0,0.4899] |
| differential-offset-75 | balanced | E | 18 | 0/0 | 12/18 [0.4375,0.8372] | 0/6 [2.776e-17,0.3903] |
| differential-offset-75 | balanced | G | 18 | 0/0 | 13/18 [0.4913,0.875] | 0/6 [2.776e-17,0.3903] |
| differential-offset-75 | proxy-rich | E | 18 | 0/0 | 9/18 [0.2903,0.7097] | 1/8 [0.02242,0.4709] |
| differential-offset-75 | proxy-rich | G | 18 | 0/0 | 9/18 [0.2903,0.7097] | 1/8 [0.02242,0.4709] |
| differential-offset-75 | date-rich | E | 18 | 0/0 | 14/18 [0.5479,0.91] | 0/3 [5.551e-17,0.5615] |
| differential-offset-75 | date-rich | G | 16 | 2/0 | 13/16 [0.5699,0.9341] | 0/1 [0,0.7935] |

The unexecuted 110 indices remain in every full-study requested denominator.
For example, even 18/18 observed coverage leaves full-study coverage identification
bounds[18/128,1] when the other 110 outcomes are unknown; it is not evidence of
100% coverage. Numerical failures leave further unknowns. The runner's
aggregate command returns all stratum bounds, failure-or-missing Wilson
intervals, selected error/width intervals and approximate PIT decile counts.
PIT is available only for accepted joint posterior rows; baseline uniformity
cannot be assessed with eighteen draws. No cross-case pooled coverage is reported.

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
| baseline/E/P-D | 18/0 | -2522 [-2.33e+05,2.28e+05] | -70.37 [-454.5,313.8] | 0 [-0.6402,0.6402] | 0 [-0.6402,0.6402] |
| baseline/G/P-D | 18/0 | -2704 [-2.332e+05,2.278e+05] | -78.85 [-463,305.3] | -0.05556 [-0.6958,0.5847] | 0 [-0.6402,0.6402] |
| baseline/balanced/E-G | 18/0 | -198.1 [-2.307e+05,2.303e+05] | -2.102 [-386.2,382] | 0 [-0.6402,0.6402] | 0 [-0.6402,0.6402] |
| baseline/proxy-rich/E-G | 18/0 | -223.6 [-2.307e+05,2.303e+05] | 3.683 [-380.4,387.8] | 0.05556 [-0.5847,0.6958] | 0 [-0.6402,0.6402] |
| baseline/date-rich/E-G | 18/0 | -405.7 [-2.309e+05,2.301e+05] | -4.801 [-388.9,379.3] | 0 [-0.6402,0.6402] | 0 [-0.6402,0.6402] |
| simultaneous/E/P-D | 17/1 | -2411 [-2.396e+05,2.347e+05] | -78.93 [-474.2,316.3] | 0.05882 [-0.6,0.7176] | -0.05882 [-0.7176,0.6] |
| simultaneous/G/P-D | 17/1 | -1350 [-2.385e+05,2.358e+05] | -78.88 [-474.1,316.4] | 0 [-0.6588,0.6588] | 0 [-0.6588,0.6588] |
| simultaneous/balanced/E-G | 18/0 | 22.95 [-2.305e+05,2.305e+05] | 2.203 [-381.9,386.3] | 0 [-0.6402,0.6402] | 0 [-0.6402,0.6402] |
| simultaneous/proxy-rich/E-G | 17/1 | 152.9 [-2.37e+05,2.373e+05] | 4.773 [-390.5,400] | 0 [-0.6588,0.6588] | 0 [-0.6588,0.6588] |
| simultaneous/date-rich/E-G | 17/1 | -117.1 [-2.373e+05,2.37e+05] | 0.01309 [-395.3,395.3] | 0 [-0.6588,0.6588] | 0 [-0.6588,0.6588] |
| mixing-x2/E/P-D | 10/8 | -4949 [-3.142e+05,3.043e+05] | -88.41 [-600,427] | 0 [-0.8589,0.8589] | 0 [-0.8589,0.8589] |
| mixing-x2/G/P-D | 16/2 | -5639 [-2.501e+05,2.388e+05] | -87.16 [-494.6,320.3] | 0.125 [-0.5541,0.8041] | 0 [-0.6791,0.6791] |
| mixing-x2/balanced/E-G | 17/1 | -142 [-2.373e+05,2.37e+05] | -1.3 [-396.6,394] | 0 [-0.6588,0.6588] | 0 [-0.6588,0.6588] |
| mixing-x2/proxy-rich/E-G | 17/1 | -333.4 [-2.375e+05,2.368e+05] | 2.023 [-393.2,397.3] | 0 [-0.6588,0.6588] | 0 [-0.6588,0.6588] |
| mixing-x2/date-rich/E-G | 9/9 | 23.74 [-3.259e+05,3.26e+05] | -1.642 [-544.9,541.6] | 0.1111 [-0.7943,1] | 0 [-0.9054,0.9054] |
| finite-layer-40/E/P-D | 18/0 | -1860 [-2.323e+05,2.286e+05] | -71.79 [-455.9,312.3] | -0.05556 [-0.6958,0.5847] | 0 [-0.6402,0.6402] |
| finite-layer-40/G/P-D | 17/1 | -2395 [-2.396e+05,2.348e+05] | -84.37 [-479.6,310.9] | -0.05882 [-0.7176,0.6] | 0 [-0.6588,0.6588] |
| finite-layer-40/balanced/E-G | 18/0 | -217.6 [-2.307e+05,2.303e+05] | -7.209 [-391.3,376.9] | 0 [-0.6402,0.6402] | 0 [-0.6402,0.6402] |
| finite-layer-40/proxy-rich/E-G | 17/1 | -6.48 [-2.372e+05,2.372e+05] | 5.105 [-390.2,400.4] | 0 [-0.6588,0.6588] | 0 [-0.6588,0.6588] |
| finite-layer-40/date-rich/E-G | 18/0 | -401.9 [-2.309e+05,2.301e+05] | -7.817 [-391.9,376.3] | 0 [-0.6402,0.6402] | 0 [-0.6402,0.6402] |
| differential-offset-75/E/P-D | 18/0 | -5356 [-2.358e+05,2.251e+05] | -75.7 [-459.8,308.4] | -0.2778 [-0.918,0.3624] | 0.05556 [-0.5847,0.6958] |
| differential-offset-75/G/P-D | 16/2 | -5744 [-2.502e+05,2.387e+05] | -79.31 [-486.7,328.1] | -0.3125 [-0.9916,0.3666] | 0.0625 [-0.6166,0.7416] |
| differential-offset-75/balanced/E-G | 18/0 | -45.31 [-2.305e+05,2.304e+05] | -2.757 [-386.9,381.4] | -0.05556 [-0.6958,0.5847] | 0 [-0.6402,0.6402] |
| differential-offset-75/proxy-rich/E-G | 18/0 | -455.1 [-2.309e+05,2.3e+05] | 3.397 [-380.7,387.5] | 0 [-0.6402,0.6402] | 0 [-0.6402,0.6402] |
| differential-offset-75/date-rich/E-G | 16/2 | -269 [-2.447e+05,2.442e+05] | -2.168 [-409.6,405.3] | 0 [-0.6791,0.6791] | 0 [-0.6791,0.6791] |

These broad intervals are a property of the small interim sample and conservative
bounded method. They establish neither a method winner nor calibrated interval
coverage or rare wrong-declaration rates. Complete the128-index registration
before its planned scientific report and independent milestone review. A
material Gaussian comparator targets the same latent event times, but its
normal-age approximation is not assumed to be better than exponential material.

## Reproduce and continue

Run the commands in HELDOUT_PROTOCOL.md with indices 1000..1017 into one
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
execute untouched indices 1018..1127 exactly once under the existing registration.
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
private commit 9b7adb8 and task finish 40593.
This continuation appended indices 1013..1017 exactly once, preserving all
390 earlier rows byte-for-byte. No frozen source or budgets changed. Both
five-index receipt collections remain in this private run; the committed CSV
and table carry their outcomes and elapsed times.
