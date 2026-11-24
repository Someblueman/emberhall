# Held-out sediment comparison: first eight independent indices

Sorrel, 24 November 2026. **Interim scientific results, not completed calibration.**
Indices 1000..1007 were each executed exactly once under the registration
`729ae32e453bb4a0dc9ff299428431b1e31a9250b114f21bd5955b4c5197b965`. All 240 cells are retained in
[heldout_results.csv](heldout_results.csv), including failed and missing cells.
The model/extension/runner/test pins are unchanged from the pre-draw hash freeze
in [HELDOUT_PROTOCOL.md](HELDOUT_PROTOCOL.md). That document records the initial
Git sequencing correction; it must accompany these results.

## What was executed

The eight-index slice requested 240 cells, attempted 240, passed 230,
failed 10, missing 0. These are **eight independent latent draws**,
not 240 independent observations. The full registered study requests 3,840 cells
across 128 latent draws: 240 attempted, 230 passed,
10 failed, 3600 missing. Cases, designs and methods
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

Runtime provenance (identical across these receipts unless shown separately):

`{"protocol_sha256":"ce44adc83c905e751ec43f703720c8c223410d4ef4358a2f5cb9b4b12d6268c1","python":"3.13.2","source_sha256":{"baseline.py":"b7e7039fca18aa0ea618210a865d00ad7904e05077efe0843af66ba65fa62b8a","change_point.py":"fb40bb3265a7117a0f2f9b1440e31754aad9b093bb5d10e81435fc5fcd502787","chronology_model.py":"30d70d5801a65f0e194bf95eabb68a0cfbcb1719c5ccaf7ad41a603f9c0d8eab","continuous.py":"89c9b7389c31666ecc08af13837e58b0e7659a57b0e462f9e2128ca5de0cb861","material_model.py":"c6bee7b0af91c69912d62315f7bd69d6b75b37c0e6c818cd293b9904a9520974","paired_experiment.py":"78bb5b647db08429155ec357186891202d7c51cfdf4f231e733c6b4446901d33"}}`

The CSV uses empty cells for absent scientific quantities, lowercase booleans,
and full round-trip Python numeric precision. Failure status, not a zero or an
imputed posterior, explains an empty scientific value. Its SHA-256 is
`e92be35d49dbfb959513b9f5c835412fe67e73e141dfb10241973c4593ff9c64`.
The CSV was decoded back and compared field-for-field with all 240 original
receipt cells. The frozen validator passed without changing the registration.

All ten failures were importance-diagnostic refusals: six exponential and four
Gaussian material fits. No time-budget failure or missing cell occurred in this
eight-index slice. Passing summaries therefore remain selected by the numerical
screens; a zero missing count does not remove that selection.

## Coverage and directional declarations

Each row requests eight indices in this interim slice and 128 in the complete
registration. Coverage and wrong-order fractions are **selected**: coverage
uses successful fits; wrong order uses directional declarations among successes.
Unresolved successful fits are not declarations. Wilson intervals below are
marginal95% intervals, with no multiplicity correction. E means exponential;
G means Gaussian material. F/M are failed/missing within the eight-index slice.
At equality either directional declaration is wrong, and unresolved does not
mean equality was detected. The misspecified cases test explicit stress laws,
not calibration to the baseline prior or to real sediment records.

| Case | Design | Method | Pass | F/M | Covered/pass [95%] | Wrong/declared [95%] |
|---|---|---|---:|---:|---|---|
| baseline | balanced | E | 8 | 0/0 | 8/8 [0.6756,1] | 0/4 [0,0.4899] |
| baseline | balanced | G | 8 | 0/0 | 8/8 [0.6756,1] | 0/3 [5.551e-17,0.5615] |
| baseline | proxy-rich | E | 8 | 0/0 | 7/8 [0.5291,0.9776] | 0/5 [0,0.4345] |
| baseline | proxy-rich | G | 8 | 0/0 | 6/8 [0.4093,0.9285] | 0/5 [0,0.4345] |
| baseline | date-rich | E | 8 | 0/0 | 8/8 [0.6756,1] | 0/3 [5.551e-17,0.5615] |
| baseline | date-rich | G | 8 | 0/0 | 8/8 [0.6756,1] | 0/2 [0,0.6576] |
| simultaneous | balanced | E | 8 | 0/0 | 7/8 [0.5291,0.9776] | 1/1 [0.2065,1] |
| simultaneous | balanced | G | 8 | 0/0 | 7/8 [0.5291,0.9776] | 1/1 [0.2065,1] |
| simultaneous | proxy-rich | E | 8 | 0/0 | 7/8 [0.5291,0.9776] | 1/1 [0.2065,1] |
| simultaneous | proxy-rich | G | 8 | 0/0 | 7/8 [0.5291,0.9776] | 1/1 [0.2065,1] |
| simultaneous | date-rich | E | 7 | 1/0 | 6/7 [0.4869,0.9743] | 1/1 [0.2065,1] |
| simultaneous | date-rich | G | 8 | 0/0 | 7/8 [0.5291,0.9776] | 1/1 [0.2065,1] |
| mixing-x2 | balanced | E | 7 | 1/0 | 7/7 [0.6457,1] | 0/2 [0,0.6576] |
| mixing-x2 | balanced | G | 8 | 0/0 | 8/8 [0.6756,1] | 0/2 [0,0.6576] |
| mixing-x2 | proxy-rich | E | 7 | 1/0 | 6/7 [0.4869,0.9743] | 0/2 [0,0.6576] |
| mixing-x2 | proxy-rich | G | 7 | 1/0 | 6/7 [0.4869,0.9743] | 0/3 [5.551e-17,0.5615] |
| mixing-x2 | date-rich | E | 5 | 3/0 | 4/5 [0.3755,0.9638] | 0/0 NA |
| mixing-x2 | date-rich | G | 7 | 1/0 | 6/7 [0.4869,0.9743] | 0/0 NA |
| finite-layer-40 | balanced | E | 8 | 0/0 | 8/8 [0.6756,1] | 0/4 [0,0.4899] |
| finite-layer-40 | balanced | G | 8 | 0/0 | 8/8 [0.6756,1] | 0/3 [5.551e-17,0.5615] |
| finite-layer-40 | proxy-rich | E | 8 | 0/0 | 7/8 [0.5291,0.9776] | 0/5 [0,0.4345] |
| finite-layer-40 | proxy-rich | G | 8 | 0/0 | 7/8 [0.5291,0.9776] | 0/5 [0,0.4345] |
| finite-layer-40 | date-rich | E | 8 | 0/0 | 8/8 [0.6756,1] | 0/3 [5.551e-17,0.5615] |
| finite-layer-40 | date-rich | G | 8 | 0/0 | 8/8 [0.6756,1] | 0/3 [5.551e-17,0.5615] |
| differential-offset-75 | balanced | E | 8 | 0/0 | 4/8 [0.2152,0.7848] | 0/1 [0,0.7935] |
| differential-offset-75 | balanced | G | 8 | 0/0 | 4/8 [0.2152,0.7848] | 0/2 [0,0.6576] |
| differential-offset-75 | proxy-rich | E | 8 | 0/0 | 3/8 [0.1368,0.6943] | 1/4 [0.04559,0.6994] |
| differential-offset-75 | proxy-rich | G | 8 | 0/0 | 3/8 [0.1368,0.6943] | 1/3 [0.06149,0.7923] |
| differential-offset-75 | date-rich | E | 8 | 0/0 | 6/8 [0.4093,0.9285] | 0/2 [0,0.6576] |
| differential-offset-75 | date-rich | G | 6 | 2/0 | 5/6 [0.4365,0.9699] | 0/0 NA |

The unexecuted 120 indices remain in every full-study requested denominator.
For example, even 8/8 observed coverage leaves full-study coverage identification
bounds[8/128,1] when the other 120 outcomes are unknown; it is not evidence of
100% coverage. Numerical failures leave further unknowns. The runner's
aggregate command returns all stratum bounds, failure-or-missing Wilson
intervals, selected error/width intervals and approximate PIT decile counts.
PIT is available only for accepted joint posterior rows; baseline uniformity
cannot be assessed with eight draws. No cross-case pooled coverage is reported.

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
| baseline/E/P-D | 8/0 | 104.4 [-3.456e+05,3.458e+05] | -58.63 [-600,517.6] | -0.125 [-1,0.8353] | 0 [-0.9603,0.9603] |
| baseline/G/P-D | 8/0 | 757.8 [-3.45e+05,3.465e+05] | -69.08 [-600,507.1] | -0.25 [-1,0.7103] | 0 [-0.9603,0.9603] |
| baseline/balanced/E-G | 8/0 | -300.5 [-3.46e+05,3.454e+05] | -4.432 [-580.6,571.8] | 0 [-0.9603,0.9603] | 0 [-0.9603,0.9603] |
| baseline/proxy-rich/E-G | 8/0 | -487.3 [-3.462e+05,3.452e+05] | 2.128 [-574.1,578.3] | 0.125 [-0.8353,1] | 0 [-0.9603,0.9603] |
| baseline/date-rich/E-G | 8/0 | 166.1 [-3.456e+05,3.459e+05] | -8.326 [-584.5,567.9] | 0 [-0.9603,0.9603] | 0 [-0.9603,0.9603] |
| simultaneous/E/P-D | 7/1 | -866 [-3.6e+05,3.6e+05] | -62.49 [-600,553.5] | 0 [-1,1] | 0 [-1,1] |
| simultaneous/G/P-D | 8/0 | -1224 [-3.469e+05,3.445e+05] | -66.07 [-600,510.1] | 0 [-0.9603,0.9603] | 0 [-0.9603,0.9603] |
| simultaneous/balanced/E-G | 8/0 | 275.2 [-3.454e+05,3.46e+05] | 5.24 [-571,581.4] | 0 [-0.9603,0.9603] | 0 [-0.9603,0.9603] |
| simultaneous/proxy-rich/E-G | 8/0 | 430.7 [-3.453e+05,3.461e+05] | 6.676 [-569.5,582.9] | 0 [-0.9603,0.9603] | 0 [-0.9603,0.9603] |
| simultaneous/date-rich/E-G | 7/1 | 191 [-3.6e+05,3.6e+05] | 1.814 [-600,600] | 0 [-1,1] | 0 [-1,1] |
| mixing-x2/E/P-D | 5/3 | -7184 [-3.6e+05,3.6e+05] | -88.47 [-600,600] | 0 [-1,1] | 0 [-1,1] |
| mixing-x2/G/P-D | 7/1 | -4401 [-3.6e+05,3.6e+05] | -83.38 [-600,532.6] | 0 [-1,1] | 0 [-1,1] |
| mixing-x2/balanced/E-G | 7/1 | -56.83 [-3.6e+05,3.6e+05] | 1.59 [-600,600] | 0 [-1,1] | 0 [-1,1] |
| mixing-x2/proxy-rich/E-G | 7/1 | -465.3 [-3.6e+05,3.6e+05] | -2.5 [-600,600] | 0 [-1,1] | 0 [-1,1] |
| mixing-x2/date-rich/E-G | 5/3 | 1723 [-3.6e+05,3.6e+05] | -3.509 [-600,600] | 0 [-1,1] | 0 [-1,1] |
| finite-layer-40/E/P-D | 8/0 | -1921 [-3.476e+05,3.438e+05] | -75.7 [-600,500.5] | -0.125 [-1,0.8353] | 0 [-0.9603,0.9603] |
| finite-layer-40/G/P-D | 8/0 | -1462 [-3.472e+05,3.443e+05] | -87.45 [-600,488.7] | -0.125 [-1,0.8353] | 0 [-0.9603,0.9603] |
| finite-layer-40/balanced/E-G | 8/0 | -159.8 [-3.459e+05,3.456e+05] | -9.211 [-585.4,567] | 0 [-0.9603,0.9603] | 0 [-0.9603,0.9603] |
| finite-layer-40/proxy-rich/E-G | 8/0 | -114.7 [-3.458e+05,3.456e+05] | 4.632 [-571.6,580.8] | 0 [-0.9603,0.9603] | 0 [-0.9603,0.9603] |
| finite-layer-40/date-rich/E-G | 8/0 | 343.7 [-3.454e+05,3.461e+05] | -7.115 [-583.3,569.1] | 0 [-0.9603,0.9603] | 0 [-0.9603,0.9603] |
| differential-offset-75/E/P-D | 8/0 | -4210 [-3.499e+05,3.415e+05] | -76.84 [-600,499.3] | -0.375 [-1,0.5853] | 0.125 [-0.8353,1] |
| differential-offset-75/G/P-D | 6/2 | -3797 [-3.6e+05,3.6e+05] | -79.31 [-600,586] | -0.5 [-1,0.6089] | 0.1667 [-0.9422,1] |
| differential-offset-75/balanced/E-G | 8/0 | -748.4 [-3.465e+05,3.45e+05] | -3.9 [-580.1,572.3] | 0 [-0.9603,0.9603] | 0 [-0.9603,0.9603] |
| differential-offset-75/proxy-rich/E-G | 8/0 | -830.9 [-3.465e+05,3.449e+05] | 2.006 [-574.2,578.2] | 0 [-0.9603,0.9603] | 0 [-0.9603,0.9603] |
| differential-offset-75/date-rich/E-G | 6/2 | 608.3 [-3.6e+05,3.6e+05] | -5.747 [-600,600] | 0 [-1,1] | 0 [-1,1] |

These broad intervals are a property of the small interim sample and conservative
bounded method. They establish neither a method winner nor calibrated interval
coverage or rare wrong-declaration rates. Complete the128-index registration
before its planned scientific report and independent milestone review. A
material Gaussian comparator targets the same latent event times, but its
normal-age approximation is not assumed to be better than exponential material.

## Reproduce and continue

Run the commands in HELDOUT_PROTOCOL.md with indices 1000..1007 into one
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
execute untouched indices 1008..1127 exactly once under the existing registration.
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
Its 90 original CSV rows are an exact byte prefix of this 240-row CSV.
This update appended indices 1003..1007 without changing earlier outcomes.
