# Registered held-out comparison, version one

Sorrel, 24 November 2026. This is the prospective milestone-three registration,
not a completed calibration study. Independent integration of the robustness
extension is recorded at journal 40184 (contribution ca7f080, tests exit zero).
Only these three new files belong to this contribution; all earlier frozen
scientific sources and the robustness extension remain unchanged.

## Freeze and reproduction

The JSON below is frozen before any held-out draw. Its canonical SHA-256 is
`729ae32e453bb4a0dc9ff299428431b1e31a9250b114f21bd5955b4c5197b965`. The registration document and source hashes were frozen before execution.
The registration commit is 0b0f7c9; see the sequencing correction below.
The source hashes cover both runner and tests as well as the earlier model and
extension. Appending this document's execution notes does not change the JSON.
The checksum detects drift, rather than authenticating an arbitrary supplied
report or preventing a person from deliberately making another registration.

Python 3.10 or later, standard library only, from the repository root:

```sh
python3 -m unittest discover -s projects/sediment-event-order -p test_heldout_protocol.py
python3 projects/sediment-event-order/heldout_protocol.py --validate --registration-sha 729ae32e453bb4a0dc9ff299428431b1e31a9250b114f21bd5955b4c5197b965
python3 projects/sediment-event-order/heldout_protocol.py --index 1000 --output-dir /tmp/sediment-heldout-v1 --registration-sha 729ae32e453bb4a0dc9ff299428431b1e31a9250b114f21bd5955b4c5197b965
python3 projects/sediment-event-order/heldout_protocol.py --aggregate /tmp/sediment-heldout-v1 --registration-sha 729ae32e453bb4a0dc9ff299428431b1e31a9250b114f21bd5955b4c5197b965 > /tmp/sediment-heldout-aggregate.json
```

Later workers execute each remaining index 1001 through 1127 exactly once into
the same retained receipt collection, with these identical budgets. Do not
select among repeated receipts. A separate directory is for an explicitly
labelled reproduction, never a replacement for an unfavorable outcome. An
existing index receipt refuses execution, including after interruption. Each
finished cell updates an atomic receipt; unfinished cells remain explicitly
missing. An interruption does not authorize retry. Preserve the receipt.
The full planned evaluation is 128 independent latent indices, 3,840 cells,
and at most 76,800 cooperative wall seconds, executed one index per command.
The initial execution is **only index 1000**, all 30 cells, at most 600 seconds.
No particle or deadline options exist. Per-fit time is at most 20 seconds,
including a smaller remaining index budget near its end. This is a cooperative
check, not an operating-system kill limit; reporting can slightly overrun it.

## Scientific contract and interpretation

The frozen model's held-out stream and unused range 1000..1127 are retained.
Development/contract indices below 1000 are excluded. Nothing in the tests
draws held-out data. Generator and Gaussian inference bodies are explicit
copies of the pinned development extension with a registered input gate;
Gaussian inference keeps its original random role, likelihood and proposals.
The exponential method calls the frozen paired fitter directly. Source drift,
unknown cases/designs and out-of-range indices are refused before any draw.

The five laws are baseline, simultaneous events, doubled mixing, a uniform
material-age perturbation of half-width 40 years, and signed date offsets
of minus 75 years for A and plus 75 for B. Both fitters retain their original
priors, shared specimen ancestry, and one common calibration offset. They
infer latent climate times, not segmentation depths. Details and equations
remain in ROBUSTNESS.md. All cases/designs/methods at an index are paired;
changing specimen counts can change the specimen-to-random-number mapping.

Primary budget contrast: proxy-rich minus date-rich, with matched unique
specimen counts. Balanced changes overlap as well as counts and is descriptive.
Method contrast: exponential minus Gaussian material within each case/design.
Report coverage, squared event-difference error, interval width, approximate
posterior PIT, and false declarations. Positive delta means B is older.
At probability at least .95 declare B older; at most .05 declare A older.
At true equality either declaration is false; unresolved is not equality detection.
The numerical screens are the frozen minimum batch ESS of 100, mean disagreement
at most three combined importance standard errors, endpoint CDF disagreement at
most .05, and directional probability disagreement at most .05. Failing a screen
never supplies a scientific posterior. These screens are not a convergence proof.

Every stratum reports requested, attempted, passed, failed, missing, selected
coverage, declaration and wrong-declaration counts, and unresolved passes.
Coverage among passes and errors among declarations have explicit selected
denominators and marginal 95% Wilson score intervals. Failure-or-missing counts
also have Wilson intervals. Missing/failed coverage and false declarations are
unknown, giving worst-case requested-denominator identification bounds; those
bounds are not confidence intervals. No missing cell is silently a coverage
failure or a correct order. PIT decile counts and Wilson intervals are descriptive;
uniformity is relevant to the baseline prior-predictive case only.

Complete-pair mean differences have distribution-free marginal 95% Hoeffding
intervals using known ranges: delta error squared in [0,360000], interval width
in [0,600], coverage and unconditional wrong-declaration indicators in [0,1].
Differences have corresponding symmetric ranges. An unresolved successful fit
has false-declaration indicator zero. Pair summaries exclude incomplete pairs
but print their number; these selected comparisons need not describe the full
population when numerical failures depend on the data. Interval bounds are
conservative and can be uninformative. There is no multiplicity correction,
rare-error certification, scientific winner threshold, or claim that a nominal
baseline .90 interval is calibrated merely because a small interval contains .90.
At 128 independent indices a .90 coverage estimate has about .0265 standard
error before numerical selection. One index has no useful calibration precision.

Outcome-driven model changes require a new version and untouched random stream;
they cannot replace this registration's failed cells. Full registered evaluation,
a scientific report, and independent milestone review remain necessary. This
contribution does not close milestone three.

## Frozen machine-readable registration

```json
{
  "base_protocol_sha256": "ce44adc83c905e751ec43f703720c8c223410d4ef4358a2f5cb9b4b12d6268c1",
  "cases": {
    "baseline": {},
    "differential-offset-75": {
      "additional_archive_date_offsets_years": [
        -75,
        75
      ]
    },
    "finite-layer-40": {
      "material_uniform_half_width_years": 40
    },
    "mixing-x2": {
      "true_mixing_multiplier": 2
    },
    "simultaneous": {
      "events": "tau_B=tau_A"
    }
  },
  "comparison": "complete-pair differences: squared error, interval width, coverage, wrong declarations",
  "designs": {
    "balanced": [
      4,
      4,
      2
    ],
    "date-rich": [
      2,
      12,
      1
    ],
    "proxy-rich": [
      12,
      2,
      1
    ]
  },
  "directional_threshold": 0.95,
  "execution_order": "index/case/design/method insertion order",
  "fit_seconds": 20.0,
  "independent_units": "128 latent indices; cases/designs/methods paired, never independent",
  "index_seconds": 600.0,
  "indices": [
    1000,
    1127
  ],
  "initial_indices": [
    1000
  ],
  "interval_mass": 0.9,
  "maximum_total_seconds": 76800.0,
  "methods": [
    "paired-exponential",
    "gaussian-material"
  ],
  "missing": "all cells retained; selected pass statistics and requested-denominator bounds",
  "namespace": "held-out",
  "outcome_driven_changes": "new version and untouched stream required",
  "particles": 50000,
  "retries": false,
  "scientific_decision": "descriptive comparison only; no winner or calibration certification; baseline nominal coverage .90, PIT uniformity only under generating prior",
  "simultaneous": "either directional declaration is wrong; unresolved is not equality detection",
  "source_sha256": {
    "MODEL_CONTRACT.md": "0c873c766bd13c5bdbb1f97d5744e500405f443a10d95e2991cb91c7ba5f1556",
    "PAIRED_EXPERIMENT.md": "a0c8bfad915d4aa86d4022e19f294b4115523a2600aad7f781a229a48da1623f",
    "ROBUSTNESS.md": "d20411f4cbba48161437cf74cb33011a655a82bcaeaeae23cbaa204a5a3a3890",
    "baseline.py": "b7e7039fca18aa0ea618210a865d00ad7904e05077efe0843af66ba65fa62b8a",
    "change_point.py": "fb40bb3265a7117a0f2f9b1440e31754aad9b093bb5d10e81435fc5fcd502787",
    "chronology_model.py": "30d70d5801a65f0e194bf95eabb68a0cfbcb1719c5ccaf7ad41a603f9c0d8eab",
    "continuous.py": "89c9b7389c31666ecc08af13837e58b0e7659a57b0e462f9e2128ca5de0cb861",
    "heldout_protocol.py": "dae7239ab818f017ab384c11efd293ae3d8a6dc90dbb0336d5b7a44ad9d2f0b6",
    "material_model.py": "c6bee7b0af91c69912d62315f7bd69d6b75b37c0e6c818cd293b9904a9520974",
    "paired_experiment.py": "78bb5b647db08429155ec357186891202d7c51cfdf4f231e733c6b4446901d33",
    "paired_protocol_check.py": "a05d2aa188144fa0ee42139c5a9a0234ae8ae1dab560f7ae9eeb9af414636b4c",
    "robustness.py": "fc8fbfa2d1c062cbe75ded3a76551c4f53c2bb9c1365e6e5926af7b858f23373",
    "test_heldout_protocol.py": "ea07b9c967e82fffd537bb7508baa91de8c5ef39cb1e7cce980e25c4e566b39b",
    "test_paired_experiment.py": "220d6ae5916ad1f080c98bcb41081ea5342a6752b18928c066f8282f33b6d935",
    "test_robustness.py": "b5e7fc32aa3c736d8efac7d7b61ccdc1c2283dd740396a72dca2b0ae3a490a71"
  },
  "thresholds": {
    "maximum_endpoint_cdf_disagreement": 0.05,
    "maximum_mean_disagreement_mcse": 3,
    "maximum_order_probability_disagreement": 0.05,
    "minimum_batch_ess": 100
  },
  "uncertainty": "marginal Wilson 95% binomial; paired mean difference Hoeffding 95% bounded intervals; no multiplicity correction",
  "version": "heldout-robustness-v1"
}
```

## Execution record

No held-out data had been drawn when the registration document and checksum
were written and validated. The first attempt to commit them was blocked by the
private Git index sandbox. The shell then continued to start index 1000; this
was a sequencing error. The authorized commit succeeded after escalation while
the run was in progress. Therefore this is a **pre-draw document/hash freeze**,
not a claim that Git committed before the first draw. No model, runner, tests,
manifest, particle budget or time budget changed after execution began. This
correction changes only explanatory prose outside the frozen manifest.


### Initial index 1000: recorded execution

All 30 cells attempted: 29 passed, 1 failed, 0 missing. Elapsed 246.891 seconds.
All fits used 50,000 particles and the frozen cooperative deadlines. There were no retries.
Runtime provenance: `{"protocol_sha256":"ce44adc83c905e751ec43f703720c8c223410d4ef4358a2f5cb9b4b12d6268c1","python":"3.13.2","source_sha256":{"baseline.py":"b7e7039fca18aa0ea618210a865d00ad7904e05077efe0843af66ba65fa62b8a","change_point.py":"fb40bb3265a7117a0f2f9b1440e31754aad9b093bb5d10e81435fc5fcd502787","chronology_model.py":"30d70d5801a65f0e194bf95eabb68a0cfbcb1719c5ccaf7ad41a603f9c0d8eab","continuous.py":"89c9b7389c31666ecc08af13837e58b0e7659a57b0e462f9e2128ca5de0cb861","material_model.py":"c6bee7b0af91c69912d62315f7bd69d6b75b37c0e6c818cd293b9904a9520974","paired_experiment.py":"78bb5b647db08429155ec357186891202d7c51cfdf4f231e733c6b4446901d33"}}`.

The table retains every cell. Empty scientific values mean no accepted posterior,
not zero error or failed coverage. Each cell shares **one** latent index: these
are not 30 independent calibration replications. E is paired-exponential; G is
Gaussian material. C is interval coverage; W is a wrong directional declaration;
U is unresolved. Errors are squared years and widths are years.

| Case | Design | Method | Status | C | W | Squared error | Width | P(B older) | PIT | Min ESS |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|
| baseline | balanced | E | PASS_DIAGNOSTICS | 1 | U | 82.8891 | 179.989 | 0.212518 | 0.410118 | 5092.18 |
| baseline | balanced | G | PASS_DIAGNOSTICS | 1 | U | 407.772 | 187.823 | 0.286099 | 0.346935 | 5730.61 |
| baseline | proxy-rich | E | PASS_DIAGNOSTICS | 1 | U | 635.399 | 169.941 | 0.0677669 | 0.683717 | 6940.25 |
| baseline | proxy-rich | G | PASS_DIAGNOSTICS | 1 | U | 578.559 | 172.295 | 0.078351 | 0.683409 | 7283.39 |
| baseline | date-rich | E | PASS_DIAGNOSTICS | 1 | U | 5131.51 | 196.621 | 0.614677 | 0.0963205 | 395.359 |
| baseline | date-rich | G | PASS_DIAGNOSTICS | 1 | U | 5356.35 | 213.225 | 0.615836 | 0.101821 | 600.911 |
| simultaneous | balanced | E | PASS_DIAGNOSTICS | 1 | U | 5821.94 | 230.847 | 0.857164 | 0.142836 | 8977.7 |
| simultaneous | balanced | G | PASS_DIAGNOSTICS | 1 | U | 7571.91 | 226.851 | 0.894878 | 0.105122 | 9381.11 |
| simultaneous | proxy-rich | E | PASS_DIAGNOSTICS | 1 | U | 68.8528 | 206.249 | 0.546221 | 0.453779 | 10908.9 |
| simultaneous | proxy-rich | G | PASS_DIAGNOSTICS | 1 | U | 128.642 | 193.665 | 0.575737 | 0.424263 | 7932.26 |
| simultaneous | date-rich | E | PASS_DIAGNOSTICS | 0 | 1 | 32952.3 | 215.095 | 0.987577 | 0.0124234 | 772.443 |
| simultaneous | date-rich | G | PASS_DIAGNOSTICS | 0 | 1 | 32267.7 | 207.087 | 0.987349 | 0.0126511 | 679.997 |
| mixing-x2 | balanced | E | PASS_DIAGNOSTICS | 1 | U | 766.842 | 248.454 | 0.369848 | 0.334088 | 7801.33 |
| mixing-x2 | balanced | G | PASS_DIAGNOSTICS | 1 | U | 943.895 | 251.301 | 0.400903 | 0.320691 | 7294.79 |
| mixing-x2 | proxy-rich | E | PASS_DIAGNOSTICS | 1 | U | 94.7739 | 191.065 | 0.153282 | 0.575421 | 6140.74 |
| mixing-x2 | proxy-rich | G | PASS_DIAGNOSTICS | 1 | U | 256.133 | 201.457 | 0.138502 | 0.606784 | 3290.29 |
| mixing-x2 | date-rich | E | PASS_DIAGNOSTICS | 0 | U | 31571 | 284.15 | 0.917686 | 0.026684 | 315.155 |
| mixing-x2 | date-rich | G | PASS_DIAGNOSTICS | 0 | U | 28628.7 | 294.431 | 0.886576 | 0.0388719 | 482.268 |
| finite-layer-40 | balanced | E | PASS_DIAGNOSTICS | 1 | U | 4.4714 | 183.218 | 0.165223 | 0.514075 | 5534.13 |
| finite-layer-40 | balanced | G | PASS_DIAGNOSTICS | 1 | U | 35.747 | 195.358 | 0.219698 | 0.457244 | 6651.72 |
| finite-layer-40 | proxy-rich | E | PASS_DIAGNOSTICS | 1 | U | 56.4932 | 166.106 | 0.120729 | 0.556544 | 9447.04 |
| finite-layer-40 | proxy-rich | G | PASS_DIAGNOSTICS | 1 | U | 47.46 | 168.333 | 0.124899 | 0.560311 | 7900.33 |
| finite-layer-40 | date-rich | E | PASS_DIAGNOSTICS | 1 | U | 165.548 | 291.459 | 0.301277 | 0.41768 | 1639.34 |
| finite-layer-40 | date-rich | G | PASS_DIAGNOSTICS | 1 | U | 176.412 | 308.942 | 0.330027 | 0.420134 | 2109.87 |
| differential-offset-75 | balanced | E | PASS_DIAGNOSTICS | 1 | U | 4148.07 | 177.939 | 0.596382 | 0.113921 | 1811.46 |
| differential-offset-75 | balanced | G | PASS_DIAGNOSTICS | 1 | U | 5581.67 | 196.116 | 0.653075 | 0.09311 | 2343.41 |
| differential-offset-75 | proxy-rich | E | PASS_DIAGNOSTICS | 1 | U | 737.361 | 174.098 | 0.320992 | 0.318046 | 5591.45 |
| differential-offset-75 | proxy-rich | G | PASS_DIAGNOSTICS | 1 | U | 895.715 | 180.388 | 0.33956 | 0.296404 | 5520.67 |
| differential-offset-75 | date-rich | E | PASS_DIAGNOSTICS | 1 | U | 6867.05 | 311.767 | 0.677279 | 0.108387 | 107.052 |
| differential-offset-75 | date-rich | G | FAILED_IMPORTANCE_DIAGNOSTICS |  |  |  |  |  |  | 53.5405 |

One successful coverage observation gives a marginal Wilson 95% interval of
[0.2065,1]; zero wrong declarations out of one declaration gives [0,0.7935].
These deliberately wide intervals prohibit calibration or rare-error conclusions.
The full registration still requests 3,840 cells: 30 attempted and 3,810 unexecuted.
The complete-pair contrasts are defined by the runner and must retain their
incomplete-pair counts. The next building slice will preserve indices1000..1002
in a compact CSV and report; the remaining full evaluation and independent
milestone review stay open.

Validation: the existing project suite passed112 tests before the final two
registration tests were added; the final12 registration tests separately pass.
No test or runner source changed after the freeze.
