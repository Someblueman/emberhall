# covreduce — shared-noise covariance reduction

An importable, standard-library-only Python package (3.10+) for first-order
covariance propagation (`J C J^T`) over labelled arrays where primitive
sources can be *shared*: one monitor normalising many bins, one background
subtracted from every bin, one detector scale applied to a group of events.
Reusing a source keeps its cross terms; two equal-valued but independent
sources do not cancel. That distinction is the whole point.

## Run it

```sh
python3 projects/shared-noise-reduction-library/run_all_demos.py
python3 -m unittest discover -s projects/shared-noise-reduction-library/tests -v
```

`run_all_demos.py` runs both importing programs with one command and
fails if either check fails.

`run_demo.py` is a real importing program: fixed bins normalised by a shared
monitor, a shared background subtracted, a weighted downstream fit, compared
against an independent dense `J C J^T` oracle, seeded Monte Carlo, an
independent-variance baseline, an ESSreduce-style upper bound, a dense
gvar-equivalent check, and an RME-style error-ellipse attribution, plus a
100,000-event streaming benchmark. `weighted_fit_demo.py` is a second one:
a sharpened spectrum (overlapping moving-window stencil with negative
side lobes, mode `same`) and a peak fit with negative flanks, checked
against the same oracle, bound and Monte Carlo, plus rebin conservation.

## Use it

```python
from covreduce import source

monitor = source(1000.0, 25.0)
counts = source([120.0, 80.0], [12.0, 9.0], dims=("bin",))
rates = counts / monitor
rates.covariance()          # shared-monitor cross terms included
rates.quadratic_form(w)     # w^T C w without materialising C
```

Operators: arithmetic with first-order product/quotient rules, `select`
(including mask-style index lists), `sum`/`mean`, `reorder_dims`,
`moving_window` (custom and negative weights), extensive/intensive `rebin`,
and streaming event-to-bin reduction in `covreduce.events`. Discontinuous
operations (`//`, `%`, uncertain bin edges) are rejected explicitly.
Propagation is first-order: `CONTRACT.md` ("When first order stops
being trustworthy") gives measured error bounds — within ~0.5% for
products when every factor's relative σ is at most 0.1, with
quotients needing a Monte Carlo check much sooner.

## Scale evidence

```sh
PYTHONPATH=projects/shared-noise-reduction-library python3 -m covreduce.scale
```

On a 2,000-element (40x50) field sharing one monitor and one background,
one downstream quadratic form `w^T C w` measures (this machine, run
`aa00d9dc`):

| route | value | time | peak memory |
|---|---|---|---|
| covreduce sparse Jacobians | 2.160356e-09 | 9.2 s | 0.16 MB |
| dense 2000x2000 covariance | 2.160356e-09 | 27.4 s | 128.38 MB |
| Monte Carlo (300 draws) | 2.016731e-09 | 1.5 s | 0.23 MB |

Sparse and dense agree to 2.1e-13 relative; the sparse route never forms
the covariance matrix, using roughly 800x less memory. Monte Carlo is
fastest but only estimates the value.

## Provenance (Stage-1 recovery)

`covreduce/core.py` is Pippin's preserved implementation, copied verbatim
from preserved commit `c6db336` in stopped run `41a3f269` (the only surviving
file of the original package; run `be4a8769`'s room no longer exists, and
trusted inspection of it fails). One minimal repair was made during
recovery: a size-1 labelled array combined with a scalar constant raised
"array shapes do not match"; `_aligned_pair` now broadcasts shape-`()`
operands first. All other modules (`oracle`, `baselines`, `events`, `cli`,
tests, this README) were reconstructed by Isolde in run `aa00d9dc` to the
recorded task contracts, with the independent-audit findings built in from
the start: the oracle combines repeated primitives, rejects derived inputs,
and implements `reorder_dims`; the RME-style ellipse baseline is implemented
locally and hand-checked, and is not claimed to be the external `rmellipse`
package.
