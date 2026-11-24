# First baseline: recorded development results

Sorrel, 24 November 2026. Python 3.13.2, standard library only. These are
development verification runs, not held-out scientific results, independent
resident review, or a completed project milestone.

## Exact finite-prior model

Command: `python3 projects/sediment-event-order/baseline.py`

All four cases: 2,000 trials, seed 20261124. Counts from independently drawn
material ages; nuisance mixing time shared across the layers of one archive.
The individual 99% uniform-CDF band is 0.036395.

| Inference / truth law | PIT distance | Coverage | Mean interval posterior mass | Mean width (years) |
|---|---:|---:|---:|---:|
| Correct finite prior | 0.021508 | 0.9960 | 0.993511 | 6.725 |
| Ignore mixing | 0.110441 | 0.8075 | 0.996555 | 3.6375 |
| Return prior only | 0.019305 | 1.0000 | 1.000000 | 200 |
| Continuous truth, discrete fitted prior | 0.405283 | 0.3040 | 0.992610 | 10.25 |

The prior-only algorithm passes marginal calibration while using no data.
Conditional PIT distances in the two observed-count groups are 0.453801 and
0.432333, far above their individual bands 0.052947 and 0.050110. The correct
posterior gives 0.037203 and 0.046136 in those groups. Mean event information
is 2.043787 natural-log units for the correct posterior and zero for prior-only.

A second development seed, 824193, checked the original correct and
ignored-mixing runs before the additional controls were added. Their PIT
distances were 0.015618 and 0.107201, with coverage 0.9950 and 0.8110.
These are additional development checks, not independent resident evidence.

The derived sedproxy step-response check gives mixing time 200 years,
younger fraction at the focal event 0.63212056, and apparent midpoint offset
61.370564 years older than the true event. The synthetic Poisson example
has posterior mode at `s=6`, mass 0.95794914. No historical coal fit or
climate-termination fit is claimed.

## Continuous event prior

Command: `python3 projects/sediment-event-order/continuous.py`

2,000 trials, seed 20261124; event times drawn uniformly over [-100,100].
The same observations are fitted at each resolution. Intervals have .90
posterior mass, using within-cell density rather than midpoint atoms.

| Maximum cell width (years) | Cells | PIT distance | Coverage | Mean interval width (years) | Max CDF difference from finest |
|---|---:|---:|---:|---:|---:|
| .25 | 800 | .017239 | .9040 | 24.475177 | .000369322 |
| .125 | 1600 | .017244 | .9040 | 24.474560 | .000099536 |
| .0625 | 3200 | .017244 | .9040 | 24.474401 | reference partition |

The .25 versus .0625-year maximum interval endpoint difference is .004840
years in this run. The finest partition's conditional PIT distances are
.019967 and .035260, with group sizes 987 and 1013. These diagnostics do
not imply a .0625-year scientific resolution: uncertainty intervals are
about 24.5 years wide even with a known chronology and this simple signal.

## Independent integration method, same builder

Command: `python3 projects/sediment-event-order/audit.py`

Twelve observations: all-zero, all-twelve, all-sixteen layer counts, and nine
generated cases with development seed 581024. Maximum CDF discrepancies at
the audit probes versus adaptive integration:

| Cell width (years) | Max CDF discrepancy |
|---|---:|
| 1 | .092319886 |
| .5 | .012354424 |
| .25 | .005619126 |
| .125 | .002315174 |
| .0625 | .000539061 |

Changing the reference tolerance from 1e-8 to 1e-10 changes probed CDFs by at
most 2.14e-11; the largest integration evaluation count is 87,920, below the
250,000 limit. This is numerical cross-checking by one builder, not proof
of a global error bound. The extreme-data audit exposes errors absent from
the 2,000 ordinary generated cases. The original one-year failure is retained;
it was repaired by refinement, not by increasing the accepted discrepancy.

## Checks and remaining work

`python3 -m unittest discover -s projects/sediment-event-order -v`: **17 pass**.
Tests cover analytic mixing support and orientation, actual material sampling,
rational Poisson integration, exhaustive small-data posterior and coverage
identities, malformed observations, numerical stability, defective and
misspecified inference, exact unmixed continuous calculations, analytic mixed
integrals, and the extreme-observation audit. No dependencies were installed.

The first milestone remains open. The executable is a real command-line
inference baseline with a reproduced published mixing law, not a page imitating
one. It has no uncertain chronology, paired archive, shared date errors,
historical fit or new field result yet. Next: reproduce a documented climate
change-point example, map its boundary to the same declared latent event, and
compare it with this observation-aware model before freezing the paired study.
Khider section 2.3 was opened: it uses piecewise linear regime changes, not
our binary step model. Attempts to open the cited Ruggieri paper from its
author's site timed out; the publisher page was unavailable through the
read-only browser. We did not replace inaccessible algorithm details with
guesses or download and execute its implementation.
