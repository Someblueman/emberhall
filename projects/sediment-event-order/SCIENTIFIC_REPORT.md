# Which ancient change came first? The complete registered comparison

Fern, 26 November 2026. Scientific synthesis of the frozen 128-draw study;
independent scientific milestone review remains required.

## Finding and scope

This benchmark estimates the order of two **latent climate changes**, before
sediment mixing. It supplies a runnable synthetic experiment, retained failures
and a compact result dataset. It does not reconstruct a historical event.
The strongest warning is the fixed opposite dating bias: neither fitted method
accounts for it, and selected coverage falls to roughly 63–73% rather than the
nominal 90%. More proxy measurements give narrower intervals in the observed
complete pairs, but the registered uncertainty does not establish a design or
method winner. Numerical failures, especially with doubled mixing and many
dates, prevent interpreting passing fits as the full requested population.

## What was fixed before evaluation

The [registration](HELDOUT_PROTOCOL.md) freezes source hashes, the five generating
laws, 50,000 particles per fit, two importance batches and numerical screens,
20 cooperative seconds per fit, and 600 seconds per index. Its canonical hash
is `729ae32e453bb4a0dc9ff299428431b1e31a9250b114f21bd5955b4c5197b965`.
The initial Git sequencing correction is retained there: hash freeze preceded
execution, but the registration commit followed the first draw. This is not a
claim that the commit itself was prospective.

Indices 1000–1127 are **128 independent latent units**. The five laws, three
designs and two methods within an index are paired, giving 3,840 requested fits,
not 3,840 independent replications. All were attempted: 3,612 passed diagnostics,
108 failed importance diagnostics and 120 exhausted time; none is missing.
Execution history and full tables are in [HELDOUT_RESULTS.md](HELDOUT_RESULTS.md).
The final dataset hash is
`3afc747e8b97af776e6d3f06b5e7c458c35fcb9328bfd72294376647cb91e6c1`.
The independent data integration is journal 49078, delivery 49081; this report
recalculates the data, rather than witnessing original executions again.

Both methods estimate delta = tau_B − tau_A in years before a synthetic epoch;
positive delta means B happened earlier. Independent event priors are uniform
on [850,1150], giving a triangular lag prior on [−300,300]. Each archive has four
depths, a monotone Gamma-increment chronology, uncertain surface age and mixing.
A specimen's binary proxy probability is .9 on the younger side of the climate
step and .1 on the older side. Dates have independent 100-year noise and one
shared Normal(0,50²) calibration offset across both archives. Shared proxy/date
specimens retain their common material age in the likelihood. This constant
offset is not an age-varying radiocarbon calibration curve.

The exponential fit uses A = focal − h + Exp(mean=h); Gaussian material replaces
that with Normal(focal,h²), preserving mean and variance but changing skew and
support. It estimates the same latent times with the same other priors and
ancestry. It is an explicit approximation, not a published segmentation method.
See [PAIRED_EXPERIMENT.md](PAIRED_EXPERIMENT.md) and [ROBUSTNESS.md](ROBUSTNESS.md)
for the complete law and proposal corrections. The exponential fit matches the
baseline generator; the Gaussian fit is already misspecified in that baseline.

Proxy-rich allocates 12 proxies, 2 dates and 1 shared specimen per layer;
date-rich reverses the measurement counts with the same 13 unique specimens.
This matches specimen count, not laboratory cost. Balanced uses 4 proxies,
4 dates and 2 shared specimens, and is descriptive rather than an isolated
count contrast.

The five generating laws are baseline; simultaneous events (tau_B = tau_A);
doubled realized mixing; an independent Uniform(−40,40)-year addition to each
material age; and fixed extra date offsets −75 years in A and +75 in B.
Both fits retain their original assumptions in every law. Simultaneity imposes
a truth constraint absent from their independent continuous event priors;
non-declaration cannot detect exact equality. The finite-layer law is a time
half-width, not a measured physical thickness. These stresses do not represent
all possible model errors or validate real archives.

## Baseline estimates and their denominators

Intervals are central 90% posterior intervals. Declare B older at P(delta>0)
≥.95 and A older at ≤.05; otherwise leave the ordering unresolved. Coverage is
among passing fits. Wrong/declarations conditions again on declaring, while
requested-denominator wrong-event bounds below treat unresolved passes as zero.
These are different estimands.

E = exponential material; G = Gaussian material. MSE has units years² and mean
interval width has units years. Every row requests 128 units.

| Design, fit | Passed | Covered/passed | Coverage, marginal 95% Wilson | Wrong/declarations | Mean MSE | Mean width |
|---|---:|---:|---|---:|---:|---:|
| balanced, E | 126 | 117/126 | 0.870–0.962 | 1/39 | 3094.6 | 202.8 |
| balanced, G | 126 | 115/126 | 0.850–0.951 | 1/39 | 3367.2 | 204.0 |
| proxy-rich, E | 124 | 112/124 | 0.838–0.944 | 1/52 | 2941.4 | 170.2 |
| proxy-rich, G | 126 | 112/126 | 0.822–0.933 | 1/54 | 2944.3 | 166.9 |
| date-rich, E | 119 | 108/119 | 0.842–0.948 | 0/26 | 6216.4 | 248.3 |
| date-rich, G | 123 | 112/123 | 0.847–0.949 | 0/25 | 6301.9 | 251.0 |

These Wilson intervals are marginal and selected, with no multiplicity
correction. Containing .90 does not certify calibration or equivalence.
Even 128 independent units have about .0265 binomial standard error at .90
before selection. Zero wrong declarations in a small declaring subset does
not certify rare-error control; full Wilson intervals are in the result table.

## What the stress cases expose

With opposite date offsets, every selected coverage Wilson upper limit is
below .90. This is a substantial failure under this particular fixed bias, not
a quantified prevalence of real-world calibration errors. The table gives
worst-case **finite-study identification bounds**, not confidence intervals:
for c covered, w wrong and p passed out of 128, coverage is bounded by
[c/128,(c+128−p)/128] and wrong-declaration frequency by
[w/128,(w+128−p)/128]. Failed fits have unknown scientific outcomes.

| Opposite offsets: design, fit | Covered/passed | Coverage Wilson 95% | Coverage identification bounds | Wrong/declarations | Wrong-event identification bounds |
|---|---:|---|---|---:|---|
| balanced, E | 85/124 | 0.599–0.761 | 0.664–0.695 | 5/56 | 0.039–0.070 |
| balanced, G | 89/126 | 0.622–0.779 | 0.695–0.711 | 4/54 | 0.031–0.047 |
| proxy-rich, E | 79/125 | 0.545–0.711 | 0.617–0.641 | 6/66 | 0.047–0.070 |
| proxy-rich, G | 79/126 | 0.540–0.706 | 0.617–0.633 | 5/66 | 0.039–0.055 |
| date-rich, E | 79/115 | 0.597–0.765 | 0.617–0.719 | 1/38 | 0.008–0.109 |
| date-rich, G | 89/122 | 0.645–0.800 | 0.695–0.742 | 2/34 | 0.016–0.062 |

In doubled mixing, date-rich E passes only 73/128 fits: 67/73 cover, but the
requested coverage bounds are .523–.953 and wrong-event bounds 0–.430.
Its apparently high selected coverage cannot resolve that missing scientific
information. Date-rich G passes 116/128 with 105 covering and coverage bounds
.820–.914. Fewer failures are an observed numerical advantage under this
budget and stress, not proof of better scientific inference.

At simultaneity, proxy-rich E declares 11 times in 122 passes and G 14 times in
122 passes; all declarations are false. Their requested wrong-event bounds are
.086–.133 and .109–.156. An unresolved result is consistent with uncertainty,
not a posterior probability of equality. Under the finite-layer perturbation,
proxy-rich E and G cover 106/122 and 107/123; both coverage identification upper
bounds are .875, while the selected Wilson intervals still include .90.
Finite-study bounds and sampling uncertainty answer different questions.

## Paired budget and method comparisons

The primary contrast is proxy-rich minus date-rich **within a latent index**.
Complete pairs require both fits to pass. MSE and width differences below are
means on those complete pairs, with registered marginal 95% Hoeffding intervals
for width. Counts and intervals change with selection; independent stratum
means must not be subtracted to obtain the paired contrast.

| Law, fit | Complete/128 | Mean MSE difference (years²) | Mean width difference (years), Hoeffding 95% |
|---|---:|---:|---|
| baseline, E | 117/128 | -3358.5 | -78.5 [-229.1, 72.2] |
| baseline, G | 122/128 | -3479.3 | -84.4 [-231.9, 63.2] |
| simultaneous, E | 112/128 | -1698.1 | -79.1 [-233.0, 74.9] |
| simultaneous, G | 120/128 | -1415.3 | -81.8 [-230.6, 67.0] |
| mixing-x2, E | 73/128 | -4160.8 | -87.8 [-278.5, 102.9] |
| mixing-x2, G | 112/128 | -2979.6 | -91.6 [-245.6, 62.4] |
| finite-layer-40, E | 110/128 | -3760.7 | -78.7 [-234.1, 76.7] |
| finite-layer-40, G | 119/128 | -3944.2 | -87.6 [-237.0, 61.7] |
| differential-offset-75, E | 115/128 | -6061.4 | -75.4 [-227.3, 76.6] |
| differential-offset-75, G | 122/128 | -5786.9 | -83.1 [-230.7, 64.4] |

All 100 registered marginal intervals (25 contrasts × four metrics: coverage,
unconditional wrong-declaration indicator, squared error and width) include
zero. This reflects conservative known-range bounds and limited independent
units; it establishes neither equality nor a winner. In baseline proxy-rich,
E minus G on 124 complete pairs has mean MSE difference −39.3 years² with
interval [−87851.3,87772.7], and width difference 3.0 years with interval
[−143.3,149.4]. Under doubled mixing, date-rich method comparison has only
71 complete pairs. Full method contrasts and all four uncertainty intervals
are retained in the result table and CSV summary command below.

## Posterior CDF diagnostics

Approximate PIT is the fitted posterior CDF at true delta. Uniformity is
relevant to the matched baseline prior-predictive law, not a requirement under
simultaneity or other misspecification. The baseline balanced E decile counts
are [12,14,9,12,19,16,12,12,13,7] from 126 passing fits; G gives
[10,13,14,13,14,14,15,14,10,9]. These are descriptive selected diagnostics, not
a uniformity acceptance test or certified posterior accuracy. Under opposite
date offsets, balanced E has 64/124 and G 66/126 in the
lowest decile, consistent with the coverage failure and shifted event ordering.
Every stratum's deciles and marginal Wilson intervals are reproducible below.

## Runtime and reproducibility limits

Summed per-index elapsed times are 37,589.577 seconds (10.44 hours), ranging
238.607–534.306 seconds. This is accumulated execution time, not a continuous
life observation or a portable speed promise. Cooperative deadlines depend on
host speed and Python version and can slightly overrun; identical random
streams do not guarantee identical failure screens on another host.

Historical receipts for indices 1018–1027 say Python 3.15.2; the other 118 say
3.13.2. We preserve that metadata without independently attesting interpreter
availability. Those ten indices contribute 78 time failures and 6 importance
failures out of 300 attempts; the other indices contribute 42 and 102 out of
3,540. Index content, host and version are confounded, so this does not estimate
a version effect. No unfavorable receipt was replaced. The CSV cannot recover
complete runtime provenance or independently prove once-only execution; the
original retained receipts and recorded independent integration supply that
history. Numerical screens (batch ESS, mean, endpoint CDF and order-probability
agreement) are necessary admission rules, not a convergence theorem.

## Recompute the recorded study without running new draws

Python 3.10+, standard library only, repository root. The CSV path is an explicit
argument, so an independently retrieved exact dataset can also be checked.
The command was run against the accepted final CSV and its hash; the frozen
source validator passed. It writes all strata, PIT diagnostics and paired
contrasts to standard output. This recalculation does not execute any fit.

```sh
python3 - projects/sediment-event-order/heldout_results.csv <<'PYCSV'
import csv,hashlib,json,sys
sys.path.insert(0,'projects/sediment-event-order')
import heldout_protocol as h
h.validate_registration('729ae32e453bb4a0dc9ff299428431b1e31a9250b114f21bd5955b4c5197b965')
p=sys.argv[1]
assert hashlib.sha256(open(p,'rb').read()).hexdigest() == '3afc747e8b97af776e6d3f06b5e7c458c35fcb9328bfd72294376647cb91e6c1'
numeric={'squared_error','predicted_order_error','approximate_pit',
         'interval_width','order_probability','minimum_batch_ess'}
with open(p,newline='') as f:
    rows=[{k:(None if v=='' else int(v) if k=='index' else float(v) if k in numeric
              else v=='true' if k in ('covered','wrong_order') else v)
           for k,v in r.items()} for r in csv.DictReader(f)]
print(json.dumps(h.summarize(rows,tuple(range(1000,1128))),sort_keys=True))
PYCSV
```

Key real outputs: requested 3840, attempted 3840, passed 3612, failed 228,
missing 0; baseline/proxy-rich/paired-exponential covered 112/124, declared 52,
wrong 1; mixing-x2/date-rich/paired-exponential passed 73 and covered 67.
Independent arithmetic in this synthesis checked all 30 coverage/declaration
rows and all 25 four-metric complete-pair contrasts against separate Wilson,
bounds and Hoeffding formulas. Data recalculation does not authenticate receipts
or independently validate a scientific model. Original study reproduction with
new fits is separately documented in HELDOUT_PROTOCOL.md and must remain a
labelled replication, never a replacement for this dataset.

## What this result permits

A researcher can now inspect an explicit event-order model, rerun its frozen
comparison and quantify where numerical selection or a stated model error
prevents a claim. The fixed opposite-bias experiment demonstrates a concrete
limit of using one common dating offset. The narrow observed proxy-rich
intervals are a hypothesis for later design studies, with no claim of general
superiority. Extending physical realism, improving numerical reliability or
choosing a winner requires a new registered study and untouched stream.
Independent scientific review must assess this milestone and its worth from
the executable experiment and retained data; this report does not close it.
