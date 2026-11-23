# covreduce operator contract

What the library promises, and what it refuses. Every statement below
can be checked in `covreduce/core.py`, `covreduce/events.py`,
`covreduce/oracle.py` or the tests named beside it.

## The approximation

All propagation is `first_order_linear` (`CovArray.approximation`): a
derived array carries, for each primitive source, the sparse Jacobian
of its values with respect to that source's components, evaluated at
the sources' central values. Covariance is `J C J^T` summed over
primitive sources. Products and quotients use the first-order rules
(`d(ab) = b da + a db`; `d(a/b) = da/b - a db / b^2`). There is no
second-order term and no sampling inside the core; for strongly
nonlinear programs the answer is the tangent-plane answer, and the
Monte Carlo baseline in `covreduce/baselines.py` is the honest check.

## Source identity

Sharing is by object identity, not by value. Reusing one `source(...)`
result in several places keeps every cross term between those places
(one monitor normalising many bins correlates them; the same scale
cancels in a difference). Two separately created sources with equal
values and variances are independent and do not cancel. `source`
accepts a diagonal variance list or a full covariance matrix, which
must be symmetric and positive semidefinite or construction raises
`ValueError`. `constant` creates an exact (zero-variance) array.

## Supported operations

Arithmetic `+ - * /` and negation between arrays and scalars, with
label alignment on `dims`/`coords` (mismatches raise
`DimensionMismatchError`; size-1 and scalar operands broadcast).
Selection by index or index list, `sum`/`mean` over a dimension,
`reorder_dims`, `moving_window` with arbitrary (including negative)
weights in `valid`/`same` modes, extensive and intensive `rebin` with
explicit edges, `quadratic_form(w)` computing `w^T C w` without
materialising `C`, and dense `covariance()` when the caller wants it.

## Explicit rejections

Anything without a first-order derivative is refused rather than
approximated silently: `abs`, floor division and modulo raise
`UnsupportedOperationError`, as does `apply_discontinuous`; division
by a value with `|b| < 1e-15` raises `ZeroDivisionError`. In
`covreduce.events.reduce_events_to_bins`, uncertain bin edges are
rejected — an event's integer bin must be exact — and an out-of-range
bin raises `IndexError`.

## Events

`reduce_events_to_bins` streams any iterable of event mappings
(`bin`, optional `weight`, `variance`, `group`). Per-event variances
are independent and accumulate per bin scaled by the group's central
scale squared. Each group scale, the monitor and the background are
shared primitive sources attached after streaming, so shared-scale
and shared-monitor cross-bin covariance is exact to first order
without per-event Jacobian storage.

## Checking: the oracle

`covreduce.oracle.dense_jcjt_oracle` re-runs a caller's program on
independent dense dual arrays (one Jacobian row per primitive
component, repeated primitives sharing one block) and forms the dense
`J C J^T`. It accepts only primitive sources — derived arrays are
rejected rather than silently rescaled. The library is held to this
oracle by randomised 1-D and 2-D composition tests
(`tests/test_oracle_2d.py` and the importing programs `run_demo.py` /
`weighted_fit_demo.py`) and by hand-written event-stream checks.
Oracle programs use the method forms (`array.moving_window(...)`,
`array.rebin(..., old_edges=..., new_edges=...)`).

## Reproducibility

Covariance sums run over primitive sources in a fixed construction
order — in a binary operation, the left operand's sources first (in
their own order), then sources only the right operand has. One fixed
program therefore produces bit-identical values, variances,
covariances and quadratic forms in every process
(`tests/test_determinism.py`). Different association or operand order
is a different program and may differ in the last bit, as floating
point allows.
