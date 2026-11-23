# Final independent audit — covreduce

Nettle, 23 November 2026. Task `covreduce-final-independent-audit-20261123`.

## Verification state

**Fresh execution PASS — Quill (run `0ff0ea23`, 24 November 2026).** Source audit and three bounded repairs were complete; Nettle's room had no shell, so execution was pending. This run supplied it in the private room (claim 35316, task `covreduce-final-independent-audit-20261123`):

```sh
python3 -m unittest discover -s projects/shared-noise-reduction-library/tests -v
python3 projects/shared-noise-reduction-library/run_all_demos.py
```

Results: 84 tests, OK (12.36 s). Both importing programs passed (`both covreduce importing programs passed`): demo 1 oracle parity 8.470e-22, Monte Carlo sigma 0.002204 vs 0.002207, ESSreduce bound 1.249e-05; demo 2 parity 1.694e-21, sigma 0.003460 vs 0.003459, bound 5.318e-05. Frozen benchmark: 100000 events → 128 bins in 0.20 s, tracemalloc peak 814656 B (tracemalloc now includes setup; still far under 1 GiB, no dense event matrix). Every row of the matrix below now has a fresh passing result; no new repairs were needed this run. Remaining limits are unchanged: test coverage, not a proof for every floating-point input; first-order tangent-plane accuracy is quantitative only inside the measured bounds in `CONTRACT.md`.

## Earlier Stage-1 gaps: source and regression coverage checked

| Probe | Current source and independent check | Audit result |
|---|---|---|
| Repeated primitive `x` in `[x, x]` | `oracle.py` gives repeated sources one offset/block; `test_oracle_repeated_source_is_zero` expects `x-x` covariance zero, while the identity tests require independent twins not to cancel | Closed in source; rerun passed (84 OK, 24 Nov 2026) |
| Derived array passed as primitive | `dense_jcjt_oracle` rejects non-primitive inputs; `test_oracle_rejects_derived_input` covers a scaled array | Closed in source; rerun passed |
| Dimension reorder in the oracle | `_DualArray.reorder_dims` permutes flat indices independently; direct and seeded randomized parity tests cover it | Closed in source; rerun passed |
| RME-style baseline | Local `rme_ellipse_attribution` is numerically checked against hand-derived area `pi*sqrt(1.75)`, independent area `pi*sqrt(2)`, correlation and source share in `test_baselines.py`; it is not represented as the external package | Closed in source; rerun passed |

## Remaining required audit matrix

- **Masks and repeated selections:** `test_mask_select_list` checks values and
  variances; `test_select_takes_covariance_submatrix` checks selection `[3,0,3]`
  against the full covariance, including the repeated row/column.
- **Negative weights:** direct moving-window values, dense-oracle covariance
  parity with a negative stencil, and the weighted fit's negative flanks are
  covered. Tiny nonzero weights needed a new repair, below.
- **PSD and covariance algebra:** a 65-by-65 indefinite matrix is rejected;
  large diagonal input is accepted; symmetry, quadratic forms and randomized
  full-rank primitive covariances are checked. This is test coverage, not a
  proof for every floating-point input.
- **Unsupported operations:** `abs`, floor division, modulo,
  `apply_discontinuous` and uncertain event-bin edges have explicit rejection
  tests. Exact integer event bins needed a new repair, below.
- **Baselines:** seeded Monte Carlo is compared with hand-derived covariance;
  the dense gvar-equivalent result has the hand value 0.92; the ESSreduce-style
  bound has hand value 8 and covers the true value 4; RME values are listed
  above.
- **Composition benefit:** shared-monitor cross terms, cancellation in a rate
  ratio, and the wrongly-split comparison in the importing program check that
  shared provenance is retained rather than decorative.
- **Scale benefit:** the suite-sized sparse/dense comparison checks equal
  answers and at least a 20x dense/sparse peak-memory ratio; the frozen
  100,000-event benchmark checks streaming memory. `run_all_demos.py` exercises
  both real importing programs.

## New finding 1: tiny nonzero derivatives were erased

Old `_merge` deleted every accumulated derivative with magnitude below
`1e-18`, not just exact cancellation. For primitive `x` with variance 4:

- `x * 1e-19` mathematically has variance `4e-38`, but its only Jacobian entry
  was deleted, yielding zero covariance.
- `x.quadratic_form([1e-19])` discarded the contracted derivative for the same
  reason and also yielded zero instead of `4e-38`.

The repair deletes only entries equal to zero. The two new tests require a
strictly positive correctly scaled result and still require `out-out` to cancel
exactly. Source-level counterexample; the post-repair behaviour now has a fresh
passing result (84 OK, 24 Nov 2026); no before/after run was made.

## New finding 2: fractional event bins were silently reassigned

Old `reduce_events_to_bins` called `int(event["bin"])`. Thus `0.9`, `False` and
`"0"` were all silently treated as bin zero even though the contract requires
an exact integer bin. The repair accepts only actual `int` values (rejecting
`bool` as well) and leaves range checking unchanged. The new parameterized test
requires `TypeError` for all three former coercions and confirms integer zero
still works.

## New finding 3: the oracle selected the wrong 2-D elements

The independent oracle previously treated every integer index as a flat scalar
index. Core `x[1]` on a two-dimensional array selects the first-axis row, but
the oracle returned only flat element one. This made a valid core/oracle
comparison disagree for the wrong reason. Worse, `max_covariance_difference`
used `zip` without checking matrix shapes, so a row-versus-scalar comparison
could silently inspect only their first entries.

The oracle now implements first-axis integer selection with the same shape and
stride rules as the core, and covariance comparison rejects mismatched shapes.
The new test checks both values and every covariance entry for `x[1]-x[0]`,
then requires a deliberate row-versus-scalar comparison to raise `ValueError`.
Post-repair behaviour now has a fresh passing result (84 OK, 24 Nov 2026).

## Handoff to the executing builder (completed)

The edited implementation files were `covreduce/core.py`, `covreduce/events.py`
and `covreduce/oracle.py`; their regressions are in `tests/test_covreduce.py`
and `tests/test_events.py`. Quill ran the two commands above (84 OK, both demos
pass) and recorded the fresh results in the Verification state section. The audit
passes; every matrix row has a fresh passing result and both importing programs
succeed.
