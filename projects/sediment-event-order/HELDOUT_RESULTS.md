# Held-out sediment comparison: first thirteen independent indices

Sorrel, 24 November 2026. **Interim scientific results, not completed calibration.**
Indices 1000..1012 were each executed exactly once under the registration
`729ae32e453bb4a0dc9ff299428431b1e31a9250b114f21bd5955b4c5197b965`. All 390 cells are retained in
[heldout_results.csv](heldout_results.csv), including failed and missing cells.
The model/extension/runner/test pins are unchanged from the pre-draw hash freeze
in [HELDOUT_PROTOCOL.md](HELDOUT_PROTOCOL.md). That document records the initial
Git sequencing correction; it must accompany these results.

## What was executed

The thirteen-index slice requested 390 cells, attempted 390, passed 377,
failed 13, missing 0. These are **thirteen independent latent draws**,
not 390 independent observations. The full registered study requests 3,840 cells
across 128 latent draws: 390 attempted, 377 passed,
13 failed, 3450 missing. Cases, designs and methods
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

Runtime provenance (identical across these receipts unless shown separately):

`{"protocol_sha256":"ce44adc83c905e751ec43f703720c8c223410d4ef4358a2f5cb9b4b12d6268c1","python":"3.13.2","source_sha256":{"baseline.py":"b7e7039fca18aa0ea618210a865d00ad7904e05077efe0843af66ba65fa62b8a","change_point.py":"fb40bb3265a7117a0f2f9b1440e31754aad9b093bb5d10e81435fc5fcd502787","chronology_model.py":"30d70d5801a65f0e194bf95eabb68a0cfbcb1719c5ccaf7ad41a603f9c0d8eab","continuous.py":"89c9b7389c31666ecc08af13837e58b0e7659a57b0e462f9e2128ca5de0cb861","material_model.py":"c6bee7b0af91c69912d62315f7bd69d6b75b37c0e6c818cd293b9904a9520974","paired_experiment.py":"78bb5b647db08429155ec357186891202d7c51cfdf4f231e733c6b4446901d33"}}`

The CSV uses empty cells for absent scientific quantities, lowercase booleans,
and full round-trip Python numeric precision. Failure status, not a zero or an
imputed posterior, explains an empty scientific value. Its SHA-256 is
`e511cbf7c9e850d733718e3831b85c090e3be80e4ea739c01fbcbca341c5adca`.
The 150 new CSV cells were decoded back and compared field-for-field with
the original receipts. The earlier 240 rows were preserved byte-for-byte.
The frozen validator passed without changing the registration.

All 13 failures were importance-diagnostic refusals: 8 exponential and 5
Gaussian material fits. No time-budget failure or missing cell occurred in this
thirteen-index slice. Passing summaries therefore remain selected by the numerical
screens; a zero missing count does not remove that selection.

## Coverage and directional declarations

Each row requests thirteen indices in this interim slice and 128 in the complete
registration. Coverage and wrong-order fractions are **selected**: coverage
uses successful fits; wrong order uses directional declarations among successes.
Unresolved successful fits are not declarations. Wilson intervals below are
marginal95% intervals, with no multiplicity correction. E means exponential;
G means Gaussian material. F/M are failed/missing within the thirteen-index slice.
At equality either directional declaration is wrong, and unresolved does not
mean equality was detected. The misspecified cases test explicit stress laws,
not calibration to the baseline prior or to real sediment records.

| Case | Design | Method | Pass | F/M | Covered/pass [95%] | Wrong/declared [95%] |
|---|---|---|---:|---:|---|---|
| baseline | balanced | E | 13 | 0/0 | 13/13 [0.7719,1] | 0/4 [0,0.4899] |
| baseline | balanced | G | 13 | 0/0 | 13/13 [0.7719,1] | 0/3 [5.551e-17,0.5615] |
| baseline | proxy-rich | E | 13 | 0/0 | 12/13 [0.6669,0.9863] | 0/5 [0,0.4345] |
| baseline | proxy-rich | G | 13 | 0/0 | 11/13 [0.5777,0.9567] | 0/5 [0,0.4345] |
| baseline | date-rich | E | 13 | 0/0 | 13/13 [0.7719,1] | 0/3 [5.551e-17,0.5615] |
| baseline | date-rich | G | 13 | 0/0 | 13/13 [0.7719,1] | 0/2 [0,0.6576] |
| simultaneous | balanced | E | 13 | 0/0 | 12/13 [0.6669,0.9863] | 1/1 [0.2065,1] |
| simultaneous | balanced | G | 13 | 0/0 | 12/13 [0.6669,0.9863] | 1/1 [0.2065,1] |
| simultaneous | proxy-rich | E | 13 | 0/0 | 12/13 [0.6669,0.9863] | 1/1 [0.2065,1] |
| simultaneous | proxy-rich | G | 13 | 0/0 | 12/13 [0.6669,0.9863] | 1/1 [0.2065,1] |
| simultaneous | date-rich | E | 12 | 1/0 | 11/12 [0.6461,0.9851] | 1/1 [0.2065,1] |
| simultaneous | date-rich | G | 13 | 0/0 | 12/13 [0.6669,0.9863] | 1/1 [0.2065,1] |
| mixing-x2 | balanced | E | 12 | 1/0 | 12/12 [0.7575,1] | 0/3 [5.551e-17,0.5615] |
| mixing-x2 | balanced | G | 13 | 0/0 | 13/13 [0.7719,1] | 0/3 [5.551e-17,0.5615] |
| mixing-x2 | proxy-rich | E | 12 | 1/0 | 11/12 [0.6461,0.9851] | 0/3 [5.551e-17,0.5615] |
| mixing-x2 | proxy-rich | G | 12 | 1/0 | 11/12 [0.6461,0.9851] | 0/4 [0,0.4899] |
| mixing-x2 | date-rich | E | 8 | 5/0 | 7/8 [0.5291,0.9776] | 0/0 NA |
| mixing-x2 | date-rich | G | 12 | 1/0 | 10/12 [0.552,0.953] | 0/0 NA |
| finite-layer-40 | balanced | E | 13 | 0/0 | 13/13 [0.7719,1] | 0/5 [0,0.4345] |
| finite-layer-40 | balanced | G | 13 | 0/0 | 13/13 [0.7719,1] | 0/4 [0,0.4899] |
| finite-layer-40 | proxy-rich | E | 13 | 0/0 | 12/13 [0.6669,0.9863] | 0/5 [0,0.4345] |
| finite-layer-40 | proxy-rich | G | 12 | 1/0 | 11/12 [0.6461,0.9851] | 0/5 [0,0.4345] |
| finite-layer-40 | date-rich | E | 13 | 0/0 | 13/13 [0.7719,1] | 0/3 [5.551e-17,0.5615] |
| finite-layer-40 | date-rich | G | 13 | 0/0 | 13/13 [0.7719,1] | 0/3 [5.551e-17,0.5615] |
| differential-offset-75 | balanced | E | 13 | 0/0 | 9/13 [0.4237,0.8732] | 0/4 [0,0.4899] |
| differential-offset-75 | balanced | G | 13 | 0/0 | 9/13 [0.4237,0.8732] | 0/4 [0,0.4899] |
| differential-offset-75 | proxy-rich | E | 13 | 0/0 | 8/13 [0.3552,0.8229] | 1/6 [0.03005,0.5635] |
| differential-offset-75 | proxy-rich | G | 13 | 0/0 | 8/13 [0.3552,0.8229] | 1/6 [0.03005,0.5635] |
| differential-offset-75 | date-rich | E | 13 | 0/0 | 11/13 [0.5777,0.9567] | 0/2 [0,0.6576] |
| differential-offset-75 | date-rich | G | 11 | 2/0 | 10/11 [0.6226,0.9838] | 0/0 NA |

The unexecuted 115 indices remain in every full-study requested denominator.
For example, even 13/13 observed coverage leaves full-study coverage identification
bounds[13/128,1] when the other 115 outcomes are unknown; it is not evidence of
100% coverage. Numerical failures leave further unknowns. The runner's
aggregate command returns all stratum bounds, failure-or-missing Wilson
intervals, selected error/width intervals and approximate PIT decile counts.
PIT is available only for accepted joint posterior rows; baseline uniformity
cannot be assessed with thirteen draws. No cross-case pooled coverage is reported.

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
| baseline/E/P-D | 13/0 | -331.5 [-2.715e+05,2.709e+05] | -67.67 [-519.7,384.3] | -0.07692 [-0.8303,0.6764] | 0 [-0.7533,0.7533] |
| baseline/G/P-D | 13/0 | -42.78 [-2.712e+05,2.712e+05] | -74.34 [-526.3,377.7] | -0.1538 [-0.9072,0.5995] | 0 [-0.7533,0.7533] |
| baseline/balanced/E-G | 13/0 | -203.3 [-2.714e+05,2.71e+05] | -2.793 [-454.8,449.2] | 0 [-0.7533,0.7533] | 0 [-0.7533,0.7533] |
| baseline/proxy-rich/E-G | 13/0 | -232 [-2.714e+05,2.71e+05] | 3.5 [-448.5,455.5] | 0.07692 [-0.6764,0.8303] | 0 [-0.7533,0.7533] |
| baseline/date-rich/E-G | 13/0 | 56.75 [-2.711e+05,2.713e+05] | -3.17 [-455.2,448.8] | 0 [-0.7533,0.7533] | 0 [-0.7533,0.7533] |
| simultaneous/E/P-D | 12/1 | -704.9 [-2.83e+05,2.816e+05] | -71.04 [-541.5,399.4] | 0 [-0.7841,0.7841] | 0 [-0.7841,0.7841] |
| simultaneous/G/P-D | 13/0 | -1181 [-2.724e+05,2.7e+05] | -72.71 [-524.7,379.3] | 0 [-0.7533,0.7533] | 0 [-0.7533,0.7533] |
| simultaneous/balanced/E-G | 13/0 | 57.53 [-2.711e+05,2.713e+05] | 4.871 [-447.1,456.9] | 0 [-0.7533,0.7533] | 0 [-0.7533,0.7533] |
| simultaneous/proxy-rich/E-G | 13/0 | 300.8 [-2.709e+05,2.715e+05] | 5.073 [-446.9,457.1] | 0 [-0.7533,0.7533] | 0 [-0.7533,0.7533] |
| simultaneous/date-rich/E-G | 12/1 | -113.2 [-2.824e+05,2.822e+05] | 1.968 [-468.5,472.4] | 0 [-0.7841,0.7841] | 0 [-0.7841,0.7841] |
| mixing-x2/E/P-D | 8/5 | -6294 [-3.52e+05,3.394e+05] | -83.67 [-600,492.5] | 0 [-0.9603,0.9603] | 0 [-0.9603,0.9603] |
| mixing-x2/G/P-D | 12/1 | -4009 [-2.863e+05,2.783e+05] | -84.27 [-554.7,386.2] | 0.08333 [-0.7008,0.8674] | 0 [-0.7841,0.7841] |
| mixing-x2/balanced/E-G | 12/1 | -170.3 [-2.824e+05,2.821e+05] | -2.226 [-472.7,468.2] | 0 [-0.7841,0.7841] | 0 [-0.7841,0.7841] |
| mixing-x2/proxy-rich/E-G | 12/1 | -427.8 [-2.827e+05,2.818e+05] | 0.9872 [-469.5,471.4] | 0 [-0.7841,0.7841] | 0 [-0.7841,0.7841] |
| mixing-x2/date-rich/E-G | 8/5 | 112.9 [-3.456e+05,3.458e+05] | -1.799 [-578,574.4] | 0.125 [-0.8353,1] | 0 [-0.9603,0.9603] |
| finite-layer-40/E/P-D | 13/0 | -1200 [-2.724e+05,2.7e+05] | -67.45 [-519.5,384.6] | -0.07692 [-0.8303,0.6764] | 0 [-0.7533,0.7533] |
| finite-layer-40/G/P-D | 12/1 | -1170 [-2.834e+05,2.811e+05] | -80.6 [-551.1,389.9] | -0.08333 [-0.8674,0.7008] | 0 [-0.7841,0.7841] |
| finite-layer-40/balanced/E-G | 13/0 | -14.77 [-2.712e+05,2.712e+05] | -10.42 [-462.4,441.6] | 0 [-0.7533,0.7533] | 0 [-0.7533,0.7533] |
| finite-layer-40/proxy-rich/E-G | 12/1 | -12.33 [-2.823e+05,2.823e+05] | 5.943 [-464.5,476.4] | 0 [-0.7841,0.7841] | 0 [-0.7841,0.7841] |
| finite-layer-40/date-rich/E-G | 13/0 | 116.8 [-2.711e+05,2.713e+05] | -8.038 [-460,444] | 0 [-0.7533,0.7533] | 0 [-0.7533,0.7533] |
| differential-offset-75/E/P-D | 13/0 | -2519 [-2.737e+05,2.687e+05] | -79.84 [-531.8,372.2] | -0.2308 [-0.9841,0.5226] | 0.07692 [-0.6764,0.8303] |
| differential-offset-75/G/P-D | 11/2 | -2006 [-2.968e+05,2.928e+05] | -80.37 [-571.7,411] | -0.2727 [-1,0.5462] | 0.09091 [-0.7281,0.9099] |
| differential-offset-75/balanced/E-G | 13/0 | 77.36 [-2.711e+05,2.713e+05] | -3.748 [-455.8,448.3] | 0 [-0.7533,0.7533] | 0 [-0.7533,0.7533] |
| differential-offset-75/proxy-rich/E-G | 13/0 | -564.3 [-2.718e+05,2.706e+05] | 3.445 [-448.6,455.4] | 0 [-0.7533,0.7533] | 0 [-0.7533,0.7533] |
| differential-offset-75/date-rich/E-G | 11/2 | 249.3 [-2.946e+05,2.951e+05] | 0.8433 [-490.5,492.2] | 0 [-0.819,0.819] | 0 [-0.819,0.819] |

These broad intervals are a property of the small interim sample and conservative
bounded method. They establish neither a method winner nor calibrated interval
coverage or rare wrong-declaration rates. Complete the128-index registration
before its planned scientific report and independent milestone review. A
material Gaussian comparator targets the same latent event times, but its
normal-age approximation is not assumed to be better than exponential material.

## Reproduce and continue

Run the commands in HELDOUT_PROTOCOL.md with indices 1000..1012 into one
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
execute untouched indices 1013..1127 exactly once under the existing registration.
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
was independently integrated at journal 40461. This update appended indices
1008..1012 exactly once, preserving its 240 rows byte-for-byte. No frozen source
or budgets changed. The five original receipts were retained in the private
run directory; this table and CSV carry their outcomes and elapsed times.
