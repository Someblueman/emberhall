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

From a clone of the repository, reproduce the result with one command
(Python 3.10+, standard library only):

```sh
python3 projects/blurred-tracks-dissipation-bounds/blurred_tracks.py
```

Check it by routes that do not share the algebra (numerical quadrature of
the defining integrals, Monte Carlo simulation, complete branch accounting):

```sh
cd projects/blurred-tracks-dissipation-bounds
python3 verify_blurred.py
python3 -m pytest -q test_blurred_tracks.py
``` A seeded synthetic track of
the frozen example is in [synthetic_track.csv](synthetic_track.csv);
`make_synthetic.py` regenerates it. [RECORDED_RUN.md](RECORDED_RUN.md) holds
the actual outputs.

Status: milestones 1–2 of 3 (project `great-choice-20261124`). Milestone 2
([general_tracks.py](general_tracks.py), DERIVATION.md §7) extends the
covariance to general stable 2D drift/diffusion matrices and tests alias
branches of the matrix logarithm in a non-isotropic example. DERIVATION.md
§11 closes its remaining loopholes: all real logarithms of the propagator
are classified ([real_logs.py](real_logs.py) — unique or nonexistent
except a continuous family for scalar `Φ`, which the film itself
rejects on frozen examples); singular `Γ_1`/`UW` are proved impossible
in the declared class, replaced by an honest ill-conditioning regime
([singular_cases.py](singular_cases.py)); and all-branch completeness
extends to every rational `ε/Δ`, with irrational ratios shown to admit
no finite symmetry window ([completeness_rational.py](completeness_rational.py)).
Milestone 3 slices s12-s19 add set-valued reports, two-exposure and equal-frames comparisons, unknown-centre handling, and derived (Isserlis + delta-method) tolerance/slack calibration with a derived chi^2 two-exposure combination rule ([tolerance_calibration.py](tolerance_calibration.py), s16), plus a per-film parametric-bootstrap version of the same tolerances ([bootstrap_calibration.py](bootstrap_calibration.py), s17) and the same calibration for the general non-isotropic symmetry-residual test ([general_finite_record.py](general_finite_record.py), s18).
All claims here are population-level and conditional on the stated model;
see DERIVATION.md §5, §7 and §11 for what is deliberately not claimed.
