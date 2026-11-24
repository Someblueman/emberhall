# Latent event-time robustness and a Gaussian material comparator

Hawthorn, 24 November 2026. Milestone-three **development extension**, not a
held-out evaluation or milestone review. This contribution owns only
`robustness.py`, `test_robustness.py`, and this document. The frozen paired
scientific sources, priors, protocol, seed ranges and acceptance thresholds are
unchanged. The older freeze's remaining-gap text describes its original scope;
this extension supplies candidates for two gaps, without silently revising it.

## Run and check

Python 3.10+, standard library only, from the repository root:

```sh
python3 -m unittest discover -s projects/sediment-event-order -p test_robustness.py
python3 projects/sediment-event-order/robustness.py --particles 50000 --seconds 480 > /tmp/robustness-development.json
```

The second command requests index zero, all five cases, three designs, and two
methods: 30 fits on **one independent latent draw**. JSON records every attempted
cell, its case/design/method/index, status, coverage, squared error, interval
width, order probability, declarations, false declarations, approximate PIT and
minimum batch ESS when available. Accounting reports requested/attempted/pass/
failed/missing per case/design/method and overall, selected coverage numerator,
declaration and wrong-declaration counts, unresolved passes, and the indices
with complete passing proxy-rich/date-rich pairs and complete method pairs. Failures never become prior
posteriors or coverage failures; they remain separately visible. Missing cells
remain in requested denominators. There are no hidden retries.

Use repeated `--case` to select a smaller development subset; `--index` selects
another development index below 1000. The Python `benchmark` accepts one to four
unique indices. Each fit has at most 20 cooperative seconds, a requested batch
at most 600 seconds, and 1,000 to 50,000 even particles split into two batches.
The wall deadline includes generation/fitting but can overrun slightly during
summarization and reporting; it is not an operating-system kill limit. Every
batch first validates all nine base frozen file hashes and the base protocol.
Reports include scientific/extension hashes and runtime provenance. These are
reproduction fingerprints, not authentication of supplied output.

The extension refuses the `held-out` namespace and indices 1000 onward. This
is intentional: a development CLI cannot accidentally start the scientific
experiment. It neither authorizes nor implements a new held-out registration.

## Precisely specified generating cases

All cases start from `paired.prior_draw` and the same namespace/index/random
roles as the frozen generator. Specimen allocations and shared IDs remain those
of each public paired design. Common indices preserve pairing across designs
and cases. They are not additional independent replications. Within an index,
changing specimen allocations can change how random numbers map to specimens;
this is the existing paired design, not a claim that every specimen is identical
between designs. Every design within a case shares exactly the same latent draw.

| Case | Change to the generating law | Fitted models |
|---|---|---|
| baseline | None; observations and oracle ages equal the frozen generator exactly | Frozen exponential and Gaussian material |
| simultaneous | Set both climate times to the original A time, Uniform(850,1150) | Both retain independent event priors |
| mixing-x2 | Double the realized mixing time in each archive | Both retain original three-point mixing priors |
| finite-layer-40 | Add Uniform(-40,40) years to each material age before proxy/date generation | Both assume zero layer half-width |
| differential-offset-75 | Add -75 years to all A dates and +75 to all B dates, in addition to the common offset | Both fit only one common offset |

The finite-layer change is a time half-width, not a physical thickness. It uses
the accepted material generator's finite-width law. Doubling mixing preserves
its mean-zero material offset but changes spread/skewness outside the fitted
prior support. The differential dating bias is a fixed signed stress test,
not a random draw from a population of calibration curves. None models a
real age-varying radiocarbon curve. These cases isolate different failures;
they do not establish robustness to arbitrary misspecification.

Simultaneity is a generating constraint, not a point-null posterior model.
Both fitters have continuous independent event priors with zero equality mass.
They cannot estimate a posterior probability of exact equality. At true delta
zero, either directional declaration at probability >=.95 or <=.05 is false;
central interval coverage of zero, false-declaration frequency and unresolved
frequency are meaningful. The inherited evaluator implements exactly this sign
convention. A non-declaration is not evidence that equality has been detected.

The oracle records actual events, paths, mixing and specimen ages. It does not
pretend that the fitted one-offset candidate describes the differential-bias
case. Case name defines additional fixed generating parameters above. Inference
receives only `PublicObservation`; truth enters only afterward in evaluation.

## Comparator: same latent times, different material-age law

The comparator is called **Gaussian material**, not Gaussian change-point
segmentation. It has the same climate event parameters tau_A, tau_B and
`delta=tau_B-tau_A` in physical years, priors, chronology uncertainty, mixing
support, common calibration offset, date-noise scales, public observations and
specimen ancestry as the frozen paired model. It replaces
`A=focal-h+Exp(mean=h)` by `A~Normal(focal,h^2)`. Both have mean focal and variance
h squared, but different support and skewness. Both use the binary climate step
`P(positive|A,tau)=.9 if A<=tau else .1`.

For a dated specimen, after subtracting the candidate common offset c,
`D-c~Normal(focal,h^2+s^2)`. If it also has a proxy, the conditional material age
has mean `focal + h^2/(h^2+s^2)*(D-c-focal)` and variance
`h^2*s^2/(h^2+s^2)`. Its positive probability is
`.1+.8*Phi((tau-conditional_mean)/conditional_sd)`. A proxy without a date uses
the unconditional material-age normal instead. The likelihood multiplies one
date density and, where present, one conditional proxy probability per shared
specimen. It never treats a shared proxy and date as independent observations
of different ages. All archives use the **same candidate c** before integrating
it; paired posterior event rows retain induced dependence.

This targets climate time directly rather than mapping a fitted depth boundary
through an estimated chronology. It is an explicitly different parametric
model, not a reproduction of a published chronology/change-point algorithm.
The normal material law permits arbitrarily young material and lacks the
exponential model's lower bound. That is a scientific approximation to test,
not a correction known to be better. Dates and proxies both inform its target;
it is not the prior-only or fixed-chronology control.

The comparator reuses the accepted chronology and full-support event proposals,
with their exact prior/proposal corrections, but weights with its own analytic
Gaussian material likelihood. A proposal motivated by exponential material is
still valid importance sampling for this Gaussian target because its density
and correction are explicit. It may be inefficient; there is no assumption of
equal ESS or equal effective computational cost. Both methods use 50,000
particles in the recorded run and the same frozen numerical screens: batch
ESS at least 100; delta means within three combined importance standard errors;
endpoint CDF and order probability disagreements at most .05. These checks
are screens, not a convergence proof or an accuracy certificate.

## What the independent small-case checks establish

The tests compare the shared specimen likelihood with direct numerical
integration over latent age, separately split at the climate step. They check
unshared factorization, positive/negative proxy probabilities summing to the
date density, the deterministic zero-mixing limit, and the common-offset
integral against a bivariate-normal analytic density. The independent-offset
product differs, so that last test discriminates the shared-calibration law.
Other checks establish exact baseline reproduction, common draws across the
three designs, explicit generating perturbations, public ancestry revalidation,
refusal of oracle/held-out inputs and frozen-source drift, joint event-row dependence, correct handling
of simultaneous directional declarations, and failed/missing/duplicate
accounting without retry. A fixed-nuisance event posterior is independently computed by refined direct quadrature, then compared with corrected importance draws from the exponential-guided event proposal under the Gaussian target. Tests use contract/development streams only.

The conditional-posterior check fixes both paths to ages (800,930,1060,1190),
mixing to (45,65), and c to zero, with contract-test index 42 observations.
Refining midpoint event quadrature from 2,000 to 4,000 cells changes mean delta
from -80.60774791 to -80.60775283 years and P(B>A) from .08905840 to .08916584.
The 20,000 corrected event draws give -80.43152864 years (Monte Carlo standard
error .45227671) and .08973220 (standard error .00236370), respectively. This
checks the event proposal under the alternate target, conditional on fixed
nuisance values; it does not verify the full posterior by exact integration.

## Next pieces toward milestone three

1. Independently inspect the scientific assumptions and executable checks of
   this extension during integration. No new milestone verdict is claimed here.
2. Register an additive milestone-three protocol **before** any fresh held-out
   draw: pin this extension and tests; choose an untouched namespace/range for
   the robustness cases and comparator; fix case magnitudes, number of independent
   indices, particle/time/storage budgets, numerical screens, stopping and
   no-retry accounting. Decide explicitly whether the original 128-case frozen
   main-model evaluation remains separate. Do not silently reuse the original
   held-out protocol as authorization for the extra methods and cases.
3. Build the held-out runner and reconciliation/reporting for that registration,
   including paired complete-case denominators and failures for both measurement
   budgets **and** both methods. Specify interval-width and error contrasts,
   selected coverage denominators, false-order/declaration denominators,
   simultaneous-case false directional claims, conditional PIT groups and
   precision limits. Freeze them before outcomes; do not choose a winner rule
   after seeing results. Development failure can motivate prospective changes,
   never retries or retroactive acceptance of held-out failures.
4. Execute within the registered bounds, preserve compact per-index data and
   a reproduction command, write the scientific report, and request one
   independent completed-milestone review. The final report must distinguish
   model calibration under its own prior predictive law from the fixed stress
   cases, and separate numerical failure from scientific wrong ordering. PITs
   from fixed or misspecified generating cases need not be uniform under the
   fitted prior predictive law; do not pool them as a calibration certificate.

This slice supplies the robustness instrument and a matched target comparator.
Held-out calibration, coverage, wrong-order rates and a defensible comparison
of measurement budgets remain work to do.

## Recorded development run


Python 3.13.2; development index 0; 50,000 particles per fit;
480-second batch budget; measured elapsed 340.137 seconds.
Requested 30, attempted 30, passed numerical screens 28,
failed 2, missing 0. All recorded source hashes matched files
after execution. The 18 extension tests, 22 existing paired tests, and 10 existing
freeze tests passed; all nine frozen input hashes and the base protocol matched.
No held-out stream ran. No acceptance threshold, case magnitude, particle count
or seed was changed after development outcomes.

The two failures were 20-second fit timeouts in the exponential model's date-rich
simultaneous and mixing-x2 cases. They are retained without retry; their scientific
metrics are null. Their two proxy-rich/date-rich pairs and two exponential/Gaussian
method pairs are incomplete. All other requested pairs are complete at index zero.
The earlier exploratory execution passed 30/30 in 270.390 seconds, but the final
source-fingerprinted run above is the recorded result. The repeated index adds no
independent replication. Wall-time failures on the same data demonstrate why a
passing development trial does not replace prospective failure accounting.

All 28 passing intervals covered their generating delta in this one draw. Only
the differential-offset case made directional declarations (six, all correct in
this particular positive-lag draw); the other 22 passing fits remained unresolved.
This describes one draw, not coverage, robustness or false-order rates. The signed
bias agrees with the underlying order in this example; this does not establish
that the failure mode is harmless. Neither complete pairs nor selected passes
provide precision for a population comparison here.

Values below are rounded for compactness; intervals are in years. E denotes
the unchanged exponential fitter; G the Gaussian material comparator. PASS means
numerical screens passed, not scientific acceptance. Every PASS row covered=true;
TIME means timeout with null coverage and order metrics. The CLI emits full
precision and all requested metrics. These values are observations, not frozen
expected outcomes or tolerances.

| Case | Design | Method | Status | Interval width | P(B older) | Minimum batch ESS |
|---|---|---|---|---:|---:|---:|
| baseline | balanced | E | PASS | 217.49 | 0.8481 | 12581.6 |
| baseline | balanced | G | PASS | 210.01 | 0.8272 | 11661.0 |
| baseline | proxy-rich | E | PASS | 182.14 | 0.9203 | 6923.3 |
| baseline | proxy-rich | G | PASS | 177.69 | 0.9285 | 5449.1 |
| baseline | date-rich | E | PASS | 244.42 | 0.8830 | 5188.3 |
| baseline | date-rich | G | PASS | 235.27 | 0.8951 | 5514.8 |
| simultaneous | balanced | E | PASS | 218.64 | 0.3092 | 10876.8 |
| simultaneous | balanced | G | PASS | 220.41 | 0.2832 | 10884.7 |
| simultaneous | proxy-rich | E | PASS | 191.16 | 0.3137 | 6180.8 |
| simultaneous | proxy-rich | G | PASS | 181.22 | 0.3025 | 3288.1 |
| simultaneous | date-rich | E | TIME | null | null | null |
| simultaneous | date-rich | G | PASS | 237.38 | 0.6655 | 4439.7 |
| mixing-x2 | balanced | E | PASS | 249.53 | 0.4428 | 9277.7 |
| mixing-x2 | balanced | G | PASS | 271.04 | 0.4597 | 9404.9 |
| mixing-x2 | proxy-rich | E | PASS | 180.79 | 0.5544 | 5515.1 |
| mixing-x2 | proxy-rich | G | PASS | 187.70 | 0.5921 | 6203.2 |
| mixing-x2 | date-rich | E | TIME | null | null | null |
| mixing-x2 | date-rich | G | PASS | 274.38 | 0.6845 | 7449.6 |
| finite-layer-40 | balanced | E | PASS | 230.74 | 0.6184 | 8809.9 |
| finite-layer-40 | balanced | G | PASS | 222.46 | 0.6656 | 8438.5 |
| finite-layer-40 | proxy-rich | E | PASS | 188.52 | 0.7456 | 6714.8 |
| finite-layer-40 | proxy-rich | G | PASS | 183.91 | 0.7754 | 4669.9 |
| finite-layer-40 | date-rich | E | PASS | 254.86 | 0.8612 | 7787.3 |
| finite-layer-40 | date-rich | G | PASS | 245.52 | 0.8821 | 6142.2 |
| differential-offset-75 | balanced | E | PASS | 192.46 | 0.9896 | 6621.5 |
| differential-offset-75 | balanced | G | PASS | 189.49 | 0.9892 | 6104.6 |
| differential-offset-75 | proxy-rich | E | PASS | 163.54 | 0.9973 | 4844.9 |
| differential-offset-75 | proxy-rich | G | PASS | 159.89 | 0.9971 | 3633.1 |
| differential-offset-75 | date-rich | E | PASS | 202.98 | 0.9896 | 1610.3 |
| differential-offset-75 | date-rich | G | PASS | 197.28 | 0.9908 | 1614.2 |

Reproduction fingerprints for this recorded execution:

```text
robustness.py fc8fbfa2d1c062cbe75ded3a76551c4f53c2bb9c1365e6e5926af7b858f23373
test_robustness.py b5e7fc32aa3c736d8efac7d7b61ccdc1c2283dd740396a72dca2b0ae3a490a71
base protocol ce44adc83c905e751ec43f703720c8c223410d4ef4358a2f5cb9b4b12d6268c1
```
