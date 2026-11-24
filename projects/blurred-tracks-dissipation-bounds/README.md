# What a blurred particle track can prove

How much energy dissipation can a filmed particle track actually establish,
once the camera's finite shutter is accounted for? This project derives the
exact covariance of a shutter-averaged rotating Brownian particle, then asks
which continuous-time motions could have produced the same film — keeping
every compatible motion instead of silently fitting one.

**Milestone 1 result.** For a stationary isotropic rotating linear diffusion
(Brownian vortex) filmed with frame period `Δ = 1`, exposure `ε = 0.5` and
unknown localization noise, point sampling would leave the dissipation `σ`
completely unbounded (infinitely many rotation rates alias to the same
frames). The finite shutter breaks the alias: it twists the phase of each
lagged covariance by an amount that depends on the true rotation rate. In
the frozen example (true `σ = 30.42`, rotation under-resolved so a naive fit
even gets the sign wrong), exactly one latent motion in the family is
compatible with the exact observed covariances — over *all* alias branches,
not a finite scan. Full derivation, frozen assumptions and honest limits:
[DERIVATION.md](DERIVATION.md).

From a clone, run the current population and finite-track boundary checks
(Python 3.10+, standard library only):

```sh
python3 projects/blurred-tracks-dissipation-bounds/dissipation_bounds.py
```

The original covariance example remains runnable with
`python3 projects/blurred-tracks-dissipation-bounds/blurred_tracks.py`.
For the supplied seeded synthetic track:

```sh
cd projects/blurred-tracks-dissipation-bounds
python3 dissipation_bounds.py --csv synthetic_track.csv --json
```

This exits **1**, deliberately: `status` is `uncertainty_unavailable`,
`search_complete` is false and `sigma_bounds` is null. Its searched plug-in
span is approximately `[12.4537, 45.9583]`; this is **not a confidence interval**.
The CSV must contain `frame,y1,y2`, with consecutive nonnegative integer
frame labels (any starting label), finite coordinates and at least three rows.
`--Delta` is the time between consecutive frames; gaps, duplicates and reordered
frames are refused. Missing observations outside the supplied interval cannot
be detected. `--detrend 0` removes the sample mean; degrees 1–3 remove fitted
polynomials and do not establish robustness to arbitrary drift.

The API `certify_covariances` separates three questions:

| Input/search | What the returned result supports |
|---|---|
| Population moments, complete numerical branch enumeration | Model-conditional `sigma_bounds`, subject to numerical tolerances |
| Population moments, truncated enumeration | `status="incomplete"`, diagnostic `plugin_span`, no bounds |
| Finite or bootstrap moments | Branch diagnostics, `status="uncertainty_unavailable"`, no bounds |

Complex-pair all-integer elimination requires the caller to declare ideal exact
timing with `exposure_ratio=Fraction(p, q)` from Python's `fractions` module.
A float ratio alone never supplies that assumption. Excessive denominators
(currently above 2000), degenerate or excessive residue searches remain
incomplete. Scalar propagators use a finite winding-sheet search and are
incomplete even when only one candidate survives. Population bounds use floating
point, not interval-arithmetic proof enclosures.

`certify_two_exposures` filters motions against both sets of population moments,
with the same motion and localization-noise variance. A complete enumeration
from either exposure can suffice; two incomplete searches cannot establish global
uniqueness. Finite/bootstrap two-exposure uncertainty is currently refused.
A tested scalar example loses a rival with a second exposure, but remains globally
incomplete. See [DERIVATION.md §28](DERIVATION.md#28-current-algorithm-and-milestone-synthesis).

A minimal import example, from the project directory, uses population moments
constructed from a known motion. The rational timing declaration is an assumption
about this synthetic design, not something inferred from the moments:

```sh
python3 - <<'PYTHON'
from fractions import Fraction
from dissipation_bounds import certify_covariances, certify_two_exposures
from general_tracks import GeneralVortex

g = GeneralVortex([[-1., -3.9], [3.9, -1.]], [[1., 0.], [0., 1.]])
def exposure(eps):
    return (*[g.observed_cov_matrix(1., eps, .04, k) for k in range(3)], 1., eps)
half = exposure(.5)
r = certify_covariances(*half, exposure_ratio=Fraction(1, 2))
print(r['status'], r['search_complete'], round(r['sigma_bounds'][0], 6))
r = certify_covariances(*half)
print(r['status'], r['sigma_bounds'])
r = certify_two_exposures(exposure(1e-4), half,
                         exposure_ratios=(None, Fraction(1, 2)), tol=1e-5)
print(r['status'], r['resolved_by_two_exposures'], round(r['sigma_bounds'][0], 6))
PYTHON
```

This prints `unique True 30.42`, `incomplete None`, and `unique True 30.42`.

Reproduce the independent checks and the camera-noise experiment:

```sh
python3 verify_blurred.py
python3 verify_general.py
python3 -m pytest -q
python3 noise_misspecification.py
```

The implementation uses only the standard library; the test command needs pytest.
The noise experiment studies marginal coverage of branch residuals and zero-lag
gates, with known mean, not coverage of dissipation bounds. Independent white
localization noise of arbitrary covariance preserves positive-lag drift information;
unequal covariance can invalidate the extra isotropic-noise gates. Heavy tails
can change those gates' first-order variance. Block bootstrap is an empirical
comparison, not a universal repair; unavailable fits count as misses. Commands,
outputs and limitations are in [RECORDED_RUN.md](RECORDED_RUN.md).

Status: milestones 1–2 accepted; milestone 3 synthesis is ready for independent
review, with finite-data dissipation uncertainty still unsupported. This is a
runnable covariance/branch-analysis library and computation, not a universal
finite-film dissipation estimator.

Research history (project `great-choice-20261124`). Milestone 2
([general_tracks.py](general_tracks.py), DERIVATION.md §7) extends the
covariance to general stable 2D drift/diffusion matrices and tests alias
branches of the matrix logarithm in a non-isotropic example. DERIVATION.md
§11 addresses logarithm classification and singular cases: all real logarithms of the propagator
are classified ([real_logs.py](real_logs.py) — unique or nonexistent
except a continuous family for scalar `Φ`, which the film itself
rejects on frozen examples); singular `Γ_1`/`UW` are proved impossible
in the declared class, replaced by an honest ill-conditioning regime
([singular_cases.py](singular_cases.py)); and all-branch completeness
extends to every rational `ε/Δ`, with irrational ratios shown to admit
no finite symmetry window ([completeness_rational.py](completeness_rational.py)).
Milestone 3 slices s12-s21 add set-valued reports, two-exposure and equal-frames comparisons, unknown-centre handling, and derived (Isserlis + delta-method) tolerance/slack calibration with a derived chi^2 two-exposure combination rule ([tolerance_calibration.py](tolerance_calibration.py), s16), plus per-film parametric-bootstrap versions of the same tolerances for both the isotropic vortex ([bootstrap_calibration.py](bootstrap_calibration.py), s17) and the general non-isotropic symmetry-residual test ([general_finite_record.py](general_finite_record.py), s18-s19; [general_bootstrap.py](general_bootstrap.py), s20), and a bound showing the general test's leaning means were noise ([general_trapezoid_bias.py](general_trapezoid_bias.py), s21).
Slices s22-s24 close two of §11's population remainders: a continuous
search finds no scalar-`Φ` rival motion compatible with the film across
an 8-truth sweep ([scalar_phi_search.py](scalar_phi_search.py), s22);
the `α = 0` case where symmetry would be automatic is proved empty —
`α = it/d_0` with bracket `z†adj(Σ)z > 0`
([alpha_zero.py](alpha_zero.py), s23); and the irrational-ratio window
question is exhibited as Diophantine: `min |R(m)|/m` stays above `0.15`
at golden-ratio `ε/Δ` but collapses to `0.005` at a ratio with one huge
partial quotient ([diophantine_windows.py](diophantine_windows.py), s24).
Slice s25 ([window_constant.py](window_constant.py), DERIVATION.md §25)
settles the form of that window constant: an exact decomposition gives
`liminf |R(m)|/m` as an explicit truth-dependent factor times an
inhomogeneous-Diophantine distance `dist(ξ*, Ξ)`, proves no constant
depending on `ε/Δ` alone works for all truths, and checks an effective
finite-range bound against brute force to branch 200000 at three ratios.
Slice s26 ([ostrowski_liminf.py](ostrowski_liminf.py), DERIVATION.md §26)
attacks that distance on the frozen truth at the golden ratio and
`√2−1` via the Ostrowski expansion of `γ`: an exact digit
parametrization of `Ξ`, plus certified values along the prefix
subsequence, show s25's flat scan minima were finite-range effects —
the liminf is at most `0.079` (golden) resp. `0.0052` (`√2−1`), not
`0.155`/`0.202` — and that no finite-window argument can prove the
distance positive; exact positivity is a digit-density property of
`γ`, named as the open core.
Slice s27 ([scalar_phi_proof.py](scalar_phi_proof.py), DERIVATION.md §27)
takes the first proof step past s22's search: the scalar-`Φ` rival
equations reduce to a `3×3` determinant in the stretch variable whose
only candidate root on rival branches is inadmissible, giving a
complete verified exclusion (70-digit arithmetic) for s22's closest
truth over the whole rival family.
Each script runs standalone (`python3 <script>.py`) and all results are
recorded in RECORDED_RUN.md; `python3 -m pytest -q` runs the test suite
(historical count; current full run: 114 tests). Still open, plainly: the parameter-free scalar-`Φ` theorem
(s27 settles one truth and names the remaining quantity `w*`), whether
`dist(ξ*, Ξ)` is exactly zero (s26), the per-truth liminf at
non-quadratic `ρ`, and claims outside the frozen designs.
The all-branch algebra concerns population covariances under the declared model.
Finite-record experiments measure performance on frozen designs; branch inclusion
is not dissipation confidence coverage. See DERIVATION.md §28 for the current
contract and remaining limitations.
