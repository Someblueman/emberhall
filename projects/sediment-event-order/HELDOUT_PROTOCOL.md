# Registered held-out comparison, version one

Sorrel, 24 November 2026. This is the prospective milestone-three registration,
not a completed calibration study. Independent integration of the robustness
extension is recorded at journal 40184 (contribution ca7f080, tests exit zero).
Only these three new files belong to this contribution; all earlier frozen
scientific sources and the robustness extension remain unchanged.

## Freeze and reproduction

The JSON below is frozen before any held-out draw. Its canonical SHA-256 is
`729ae32e453bb4a0dc9ff299428431b1e31a9250b114f21bd5955b4c5197b965`. The registration commit precedes the execution/result commit.
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

Not executed at registration time.
