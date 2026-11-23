# covreduce — shared-noise covariance reduction

An importable, standard-library-only Python package (3.10+) for first-order
covariance propagation (`J C J^T`) over labelled arrays where primitive
sources can be *shared*: one monitor normalising many bins, one background
subtracted from every bin, one detector scale applied to a group of events.
Reusing a source keeps its cross terms; two equal-valued but independent
sources do not cancel. That distinction is the whole point.

## Run it

```sh
python3 projects/shared-noise-reduction-library/run_demo.py
python3 -m unittest discover -s projects/shared-noise-reduction-library/tests -v
```

`run_demo.py` is a real importing program: fixed bins normalised by a shared
monitor, a shared background subtracted, a weighted downstream fit, compared
against an independent dense `J C J^T` oracle, seeded Monte Carlo, an
independent-variance baseline, an ESSreduce-style upper bound, a dense
gvar-equivalent check, and an RME-style error-ellipse attribution, plus a
100,000-event streaming benchmark.

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
