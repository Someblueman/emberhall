# Blurred tracks: covariance and dissipation of a rotating linear diffusion

Milestone 1 of *What a blurred particle track can prove*
(idea `blurred-tracks-dissipation-bounds`, project `great-choice-20261124`).
Everything below is implemented in [blurred_tracks.py](blurred_tracks.py) and
checked by independent routes in [verify_blurred.py](verify_blurred.py).
Notation is ours; the latent model and the dissipation definition follow the
Brownian-vortex solvable model of Di Terlizzi, Baiesi & Ritort, *Variance sum
rule: proofs and solvable models*, New J. Phys. (2024),
[doi:10.1088/1367-2630/ad4fb9](https://iopscience.iop.org/article/10.1088/1367-2630/ad4fb9),
and its use in Baiesi & Di Terlizzi, *CYNAR: a trajectory-based estimator of
entropy production*, [arXiv:2609.39654](https://arxiv.org/html/2609.39654v1).
Camera-integration statistics follow the observation model of Berglund,
*Statistics of camera-based single-particle tracking* (cited in the brief).
We re-derive every formula here rather than transcribing equation numbers;
where a published estimator (CYNAR, VSR) would have its own population target
under blur, that is milestone 3's question, not conflated with the physical
dissipation below.

## 1. Frozen assumptions

- Latent motion: stationary, isotropic, rotating linear (Ornstein–Uhlenbeck)
  diffusion in 2D, both coordinates observed.
- Camera: known frame period `Δ`, known rectangular shutter of width
  `0 < ε ≤ Δ` anchored at each frame start, independent Gaussian localization
  errors, variance `ℓ² ≥ 0` per coordinate, **unknown** to the compatibility
  test in §5 (the weaker, honest choice; known `ℓ²` only strengthens it).
- Compatibility statements in §5 are at the **population** level: the exact
  observed covariance sequence is given. Finite-record uncertainty is
  milestone 3 and can reopen near-aliases; the phase margin reported in §5
  is the quantity that will control that.
- Dissipation `σ` is the steady-state entropy production rate of the latent
  process, in units `k_B = 1` per unit time. It is not an estimator output.

## 2. Latent Brownian vortex: covariance (reproduction)

`dX = A X dt + sqrt(2D) dW`, with

```
A = -κ I + ω J,   J = [[0, -1], [1, 0]],   κ > 0, D > 0.
```

The symmetric part `-κI` is a harmonic trap; the antisymmetric part `ωJ` is a
non-conservative rotational drift (the vortex). The stationary covariance
`Σ` solves `A Σ + Σ Aᵀ + 2D I = 0`. The isotropic ansatz `Σ = s I` gives
`-2κs + 2D = 0`, so

```
s = D / κ        (stationary variance per coordinate).
```

Since `e^{Aτ} = e^{-κτ} R(ωτ)` with `R` the rotation matrix, the latent
covariance function is, for all lags `τ`,

```
C(τ) = E[X(t+τ) X(t)ᵀ] = s e^{-κ|τ|} R(ωτ).
```

This is the published Brownian-vortex covariance in our parametrization:
exponential relaxation at rate `κ`, rotation at rate `ω`, isotropic
stationary law. Its antisymmetric part `C(τ) - C(τ)ᵀ = 2s e^{-κτ} sin(ωτ) J`
(`τ > 0`) is the observable signature of the circulating current; it vanishes
iff `ω = 0`.

## 3. Dissipation

For an overdamped diffusion with drift `b(x) = Ax` and diffusion `D`, the
steady-state probability-current velocity is
`v(x) = b(x) - D ∇log p(x) = (A + D Σ⁻¹) x`. With `Σ⁻¹ = (κ/D) I`,

```
v(x) = ω J x,
σ = (1/D) E|v(X)|² = (ω²/D) E|X|² = (ω²/D)(2D/κ) = 2ω²/κ.
```

So the trap contributes nothing and the vortex everything:
equilibrium iff `ω = 0`, and `σ` grows quadratically in the rotation rate at
fixed relaxation rate. Note `σ` does not depend on `D` (equivalently on `s`)
for this family; the sampling ambiguity of §5 is therefore entirely about
which `ω` generated the film. [verify_blurred.py](verify_blurred.py)
recomputes `σ` from simulated currents (`E|ωJX|²/D`, with `E|X|²` estimated
from simulated frames) and agrees with `2ω²/κ` within Monte Carlo error.

## 4. Shutter-averaged covariance, all lags

Frames: `Y_n = (1/ε) ∫_{nΔ}^{nΔ+ε} X(t) dt + η_n`, `η_n` iid `N(0, ℓ² I)`.
Use the complex coordinate `z = x + iy`, in which `R(ωτ)` is multiplication
by `e^{iωτ}`. Write `λ = κ - iω`, `φ = e^{-λΔ}`, and
`γ_k = E[z_{n+k} conj(z_n)]` for observed frames. The real covariance
`Γ_k = Cov(Y_{n+k}, Y_n) = [[a, -b], [b, a]]` satisfies `γ_k = 2(a + ib)`.

**Lags `k ≥ 1`.** Here `kΔ + u - v ≥ Δ - ε ≥ 0` on the integration square,
so `|·|` in `C` never changes sign and the double integral factorizes:

```
γ_k = 2 s F φ^k,
F = 4 sinh²(λε/2) / (λε)²        (complex blur factor; F → 1 as ε → 0).
```

**Lag 0.** With `τ = u - v` the square integral becomes
`∫_{-ε}^{ε} (ε - |τ|) e^{-κ|τ|} e^{iωτ} dτ`, which is real, and

```
γ_0 = 2 s Z + 2ℓ²,
Z = (2/ε²) Re[ ε/λ - (1 - e^{-λε})/λ² ]  ∈ (0, 1]   (Z → 1 as ε → 0).
```

**Negative lags:** `γ_{-k} = conj(γ_k)`, i.e. `Γ_{-k} = Γ_kᵀ`.
Counter to a first guess, blur does not merely rescale magnitudes: `F` is
complex, so a finite shutter **rotates the phase** of every nonzero-lag
covariance relative to the propagator power `φ^k`. That phase is what §5
uses. [verify_blurred.py](verify_blurred.py) checks all of §4 against
numerical quadrature of the defining integrals in real matrix form
(max error `2.3e-07` at 1200 trapezoid steps) and against Monte Carlo.

## 5. Which latent motions fit the same film? Branches

Suppose the population covariances `γ_0, γ_1, γ_2, …` and the camera
constants `Δ, ε` are given. From §4, for every `k ≥ 1`,
`γ_{k+1}/γ_k = φ = e^{-κΔ} e^{iωΔ}`. Hence `κ = -ln|φ|/Δ` is unique, but
`ω` is only determined modulo the sampling frequency: the **branches**

```
ω_m = (arg φ + 2πm)/Δ,   m ∈ ℤ,   with dissipations σ_m = 2ω_m²/κ → ∞.
```

A branch is *compatible* iff some `s > 0` and `ℓ² ≥ 0` reproduce `γ_1, γ_0`
with that `ω_m`. Since `γ_1 = 2 s F_m φ` with `s` real, this splits into two
independent conditions:

- **Phase:** `arg F_m = arg(γ_1/φ)` exactly, where `F_m` is `F` at
  `λ_m = κ - iω_m`;
- **Zero lag:** `ℓ²_m := γ_0/2 - s_m Z_m ≥ 0`, where
  `s_m = |γ_1| / (2|F_m||φ|)`.

**Point sampling (`ε = 0`) never resolves branches:** `F ≡ 1`, `Z ≡ 1`, and
every branch gives the same observed law at all lags, so the compatible
dissipation set is `{σ_m : m ∈ ℤ}`, unbounded above. This restates classical
aliasing and would not by itself pass the brief's check.

**Finite exposure generically does resolve them**, through `arg F_m`, which
varies with `m`. For the frozen ratio `ε/Δ = 1/2` the accounting over *all*
integers `m` is complete, not a finite scan: `sinh(λ_m ε/2)` is periodic in
`m` with period 4, while `-2 arg λ_m` is strictly increasing in `m` with
range an open interval of length `2π`. So within each residue class
`m mod 4` the unwrapped phase of `F_m` is strictly monotone and can hit the
target phase (mod `2π`) for **at most one** `m`; four bisections enumerate
every candidate. [verify_blurred.py](verify_blurred.py) does exactly this,
starting from quadrature covariances rather than the closed form.

### Frozen result

`κ = 1, ω = 3.9, D = 1` (so `s = 1`, true `σ = 30.42`), `Δ = 1, ε = 0.5,
ℓ² = 0.04`. The rotation is under-resolved: `ωΔ = 3.9 > π`, so the principal
branch `m = 0` is a counter-rotating `ω = -2.383` with `σ = 11.36`. Over all
`m ∈ ℤ` the phase candidates reduce to `m ∈ [-8, 7]` (four per residue
class, including bracket neighbours); checking both conditions:

- `m = 1` (the truth): phase residual `2.3e-07` (quadrature error level),
  `ℓ² = 0.0400` recovered, `σ = 30.42`. **Compatible.**
- `m = 0`: passes zero lag (`ℓ² = +0.057`) but fails phase by `0.274` rad —
  the two conditions are both needed, and this is the nearest miss.
- Every other candidate fails phase by ≥ `0.38` rad and also gives
  `ℓ² < 0`; all sufficiently fast branches would claim `σ` in the hundreds
  to thousands and are excluded.

**Statement earned:** for this observation protocol and population
covariances, exactly one latent motion in the frozen family fits the film,
so the compatible dissipation set is the single value `σ = 30.42` — where
point sampling at the same `Δ` leaves `σ` completely unbounded. Finite
exposure, usually treated as a nuisance, is what breaks the alias.

### Honest limits of §5

- Population level only. With finite data, phase is estimated with error;
  the relevant robustness margin here is the `0.274` rad gap to the nearest
  rival branch. Milestone 3 must measure when that gap survives sampling
  noise; nothing here claims it always does.
- Completeness used `ε/Δ = 1/2`. For rational `ε/Δ = p/q` the same argument
  works with period `2q` classes. For irrational `ε/Δ` the `sinh` phases are
  dense in `m`, so phase residuals of far branches can be arbitrarily small
  (though generically nonzero): exact compatibility still fails, but no
  uniform margin exists, and we claim no finite candidate list there.
- Special parameter coincidences making two branches *exactly* compatible
  are not ruled out in general; they are codimension-one in
  `(κ, ω, ε/Δ)` and absent in the frozen example by the complete check.
- `ℓ²` was treated as unknown `≥ 0`. A calibrated known `ℓ²` turns zero lag
  into an equality and can only shrink the compatible set.
- All conclusions are conditional on the frozen family (isotropic rotating
  linear diffusion, rectangular shutter, iid Gaussian localization). They
  are not claims about real cells or non-Gaussian tracks.

## 6. Controls (all in verify_blurred.py)

- **Equilibrium** `ω = 0`: only branch `m = 0` compatible, `σ = 0`, observed
  covariances real — no spurious rotation is manufactured by blur.
- **Vanishing exposure:** `F, Z → 1`; at `ε = 1e-4` all branches `m ∈ [-3,3]`
  pass phase to `4.2e-08` rad, exhibiting the point-sampling degeneracy
  that finite `ε` removes.
- **Under-resolved rotation:** the frozen example itself (`ωΔ = 3.9`);
  the principal-branch fit has the wrong sign and a third of the true `σ`.

## 7. Milestone 2: general stable 2D drift and diffusion

Implemented in [general_tracks.py](general_tracks.py), checked by
[verify_general.py](verify_general.py). For `dX = AX dt + sqrt(2) B dW` with
any stable real `2×2` drift `A` and SPD diffusion matrix `Dm = BBᵀ`
(declared numerical class: `‖A‖Δ ≤ 50`), `Σ` solves
`AΣ + ΣAᵀ + 2Dm = 0`, `C(τ) = e^{Aτ}Σ`, and
`σ = tr(Dm⁻¹ M Σ Mᵀ)` with `M = A + Dm Σ⁻¹`. With
`U = ∫₀^ε e^{Au}du`, `W = ∫₀^ε e^{-Av}dv`, `U2 = ∫₀^ε (ε-τ)e^{Aτ}dτ`
(augmented matrix exponentials):

```
Γ_k = e^{AkΔ} U W Σ / ε²   (k ≥ 1),    Γ_0 = [U2Σ + (U2Σ)ᵀ]/ε² + ℓ²I.
```

Quadrature of the defining integrals agrees to `2.1e-07`; the milestone-1
isotropic formulas are recovered to machine precision.

**Branches, general case.** Since `Γ_k = e^{AkΔ} G` with `k`-independent
`G`, the propagator `Φ = e^{AΔ} = Γ_2Γ_1⁻¹` is identified (when `Γ_1` is
invertible). Candidate drifts are the real logarithms of `Φ`. For a complex
eigenvalue pair `re^{±iθ}` these are `A_m` with log-eigenvalues
`ln r ± i(θ + 2πm)`, all sharing `Φ`'s eigenvectors. Each `A_m` needs a
*unique* candidate `Σ_m = ε²(U_mW_m)⁻¹Φ⁻¹Γ_1`; compatibility then requires:
`Σ_m` symmetric, `Σ_m ≻ 0`, implied `Dm_m = -(A_mΣ_m + Σ_mA_mᵀ)/2 ≻ 0`, and
zero lag matching with a single `ℓ² ≥ 0`. In the frozen non-isotropic
example (`A = [[-1.2, -2.0], [0.8, -0.7]]`, `Dm = [[1, 0.3], [0.3, 0.6]]`,
`Δ = 0.9, ε = 0.45, ℓ² = 0.03`, true `σ = 4.770`), exactly the true branch
passes among `m ∈ [-60, 60]`; every other branch already fails `Σ_m`
symmetry by at least `0.576` in absolute entry units.

**Completeness for the frozen example (all `m`).**
[completeness_general.py](completeness_general.py) closes the window: all
branches share `Φ`'s eigenvectors, so in that eigenbasis
`Σ_m = ε² P diag(d_m, d̄_m) Ĝ P⁻¹` with `Ĝ` fixed and
`d_m = μ_m²/(e^{μ_m ε} + e^{-μ_m ε} - 2)`. At `ε/Δ = 1/2` the denominator
depends only on the parity of `m` while `μ_m²` is quadratic in `m`; the
symmetry residual `R(m) = (Σ_m)₀₁ - (Σ_m)₁₀`, a fixed real linear form in
`(d_m, d̄_m)`, is therefore an exact quadratic polynomial in `m` per parity.
Both parity quadratics have nonzero leading coefficients (verified against
direct evaluation at `|m| = 1000` in the eigenbasis), and their only integer
root is `m = 0`. Since symmetry of `Σ_m` is necessary for compatibility,
no other branch — at any `|m|` — fits this film, within the
complex-eigenvalue, `ε/Δ = 1/2` setting.

**Closed in §11:** all real logarithms of a real-spectrum `Φ` are now
classified (the feared non-primary families for distinct positive
eigenvalues do not exist; only scalar `Φ = λI` has extra real logarithms,
a continuous family, tested against the film); singular `Γ_1`/`U_mW_m`
are proved impossible in the declared class; and completeness over all
`m` extends to every rational `ε/Δ`, with the irrational case shown to
admit no finite window from symmetry alone. The primary-logarithm subcase
for distinct positive eigenvalues is implemented and tested in
[real_eigenvalue.py](real_eigenvalue.py) (§9).

## 8. Milestone-3 pilot: finite records

[finite_record.py](finite_record.py) simulates the frozen §5 example
(population phase margin `0.274` rad) at `N ∈ {1000, 4000, 16000}` frames,
24 seeded tracks each, estimates `γ_0..γ_2` by raw second moments
(mean known zero; simulation by exact substep transitions with trapezoid
frame averages), and runs the plug-in branch test over `m ∈ [-5, 5]`:

| N | true branch has smallest phase residual | median gap to best rival | median rel. σ error |
|---|---|---|---|
| 1000 | 21/24 | 0.199 rad | 0.109 |
| 4000 | 24/24 | 0.250 rad | 0.035 |
| 16000 | 24/24 | 0.268 rad | 0.026 |

Reading: in this design the population margin is mostly preserved already
at a few thousand frames, and dissipation from the winning branch is within
a few percent; at 1000 frames a rival branch occasionally wins the plug-in
comparison, so a finite-data procedure must report the *set* of branches
within noise of the best residual rather than a single winner. This pilot
is a simulation measurement of one frozen design — no coverage, optimality,
or robustness outside the stated model is claimed. Milestone 3 proper still
needs: set-valued reporting with calibrated tolerances, unknown-mean
handling, held-out two-exposure schedules, and the light/noise budget
accounting the brief asks for.

## 9. Real-eigenvalue propagators: primary logarithm

[real_eigenvalue.py](real_eigenvalue.py) handles the subcase where
`Φ = Γ_2Γ_1⁻¹` has distinct positive real eigenvalues: Sylvester's formula
gives the primary real `log Φ`, and in the frozen example
(`A = [[-1.5, 0.4], [0.4, -0.8]]` symmetric, `Dm = [[1, 0.5], [0.5, 1]]`,
`σ = 0.0710 > 0` despite no rotation in `A` — dissipation comes from
`A` and `Dm` not commuting) it recovers `A, Σ, Dm, ℓ², σ` exactly.
A negative-eigenvalue `Φ` is refused rather than silently assigned a
logarithm. §11 upgrades this section: the primary logarithm is in fact
the *only* real logarithm whenever the positive eigenvalues are distinct
(or defective), so exact recovery here is also uniqueness; genuine
non-primary real logarithms exist only for scalar `Φ = λI`.

## 10. Exposure ratio matters: margins at other `ε/Δ`

`all_branch_candidates` in [blurred_tracks.py](blurred_tracks.py) generalizes
§5's complete accounting to any rational `ε/Δ = p/q` (period
`P = 2q/gcd(p, 2q)` residue classes). [ratio_scan.py](ratio_scan.py) applies
it to the §5 vortex at several ratios; the true branch is the unique
compatible one over all `m` in each case, but the margin to the nearest
rival candidate varies by two orders of magnitude and is not monotone:

| `ε/Δ` | nearest rival \|phase residual\| |
|---|---|
| 1/4 | 0.031 |
| 1/3 | 0.0023 |
| 2/5 | 0.0045 |
| 1/2 | 0.274 |
| 3/4 | 0.064 |
| 1 | 0.306 |

So "finite exposure resolves the alias" is ratio-dependent in practice:
at `ε/Δ = 1/3` a far branch (`m = 11` in a window scan) nearly re-aliases,
and the finite-record study of §8 would need far more frames there. Choice
of exposure fraction is an experimental design variable, not just a
nuisance — and comparing two exposure schedules (milestone 3) is promising
precisely because near-aliases sit at different branches for different
ratios. Irrational `ε/Δ` remains outside the complete accounting (§5);
§11 shows this is intrinsic, not a gap in effort.

## 11. Closing the §7 loopholes

**All real logarithms of `Φ` ([real_logs.py](real_logs.py)).** Any
logarithm `L` of `Φ` commutes with `Φ = e^L`. Unless `Φ = λI` is scalar,
`Φ` is non-derogatory and its centralizer is `{aI + bΦ}`; so every
logarithm is a polynomial in `Φ`, fixed by scalar log branches on the
eigenvalues, and a *real* `L` needs a conjugation-closed spectrum. That
one argument settles every real-spectrum case:

- distinct positive `λ₁ ≠ λ₂`: pairing `ln λ₁ + 2πik` with its conjugate
  would force `λ₁ = λ₂`, so the only real logarithm is the primary one
  (§9's recovery is uniqueness, not just a subcase);
- any negative eigenvalue among distinct reals, or a single Jordan block
  on `λ < 0`: the branch imaginary parts are odd multiples of `π`, never
  real and never conjugate-pairable — **no real logarithm exists**, even
  with both eigenvalues negative. An observed such `Φ` has no latent
  motion in the class at all;
- defective `λ > 0`: unique real log `ln λ · I + (Φ − λI)/λ` (tested:
  recovers a Jordan drift exactly);
- scalar `Φ = λI`: the centralizer is everything, and there *are* extra
  compatible-with-`Φ` motions — a continuous family
  `L = ln|λ| I + N`, `N² = −β²I`, with `β = 2πk` (`λ > 0`) or
  `β = π(2k+1)` (`λ < 0`). These are genuine counterexamples to
  "`Φ` determines the drift", so the film must do the rejecting. In two
  frozen scalar examples (truth a rotation completing a half/full turn
  per frame, non-isotropic `Dm`), every member of a (stretch, rotation,
  `β`) grid is verified to exponentiate to the same `Φ`, yet only the
  true drift passes compatibility; the nearest rival already fails
  `Σ`-symmetry by `0.012` (resp. `0.042`). Dimension count says why this
  is generic: the family is 2-dimensional per `β`, while symmetry,
  zero-lag off-diagonal and equal-`ℓ²` impose 3 conditions. A proof for
  all parameters (rather than grids on frozen examples) is **not**
  claimed; neither is a compatible extra motion exhibited — constructing
  one would need those 3 conditions solved simultaneously, a
  codimension-one coincidence in the remaining parameters.

**Singular cases cannot occur ([singular_cases.py](singular_cases.py)).**
`U, W` are functions of `A`, so `UW = f(A)` with
`f(μ) = (e^{με} + e^{−με} − 2)/μ²` and the closed form
`|f(μ)| = (2 cosh(Re με) − 2 cos(Im με))/|μ|² ≥ (2 cosh(Re με) − 2)/|μ|²`,
strictly positive whenever `Re μ ≠ 0`. Stability gives `Re μ < 0` for the
true drift and for every branch `A_m` (`Re μ_m = ln r/Δ`), `Φ` is
invertible, and `Σ ≻ 0` because `Dm ≻ 0`; hence
`Γ_1 = Φ U W Σ/ε²` is nonsingular for every latent motion and every
branch in the declared class. An observed singular `Γ_1` certifies data
outside the class (or finite-sample noise) and is refused as such. The
real phenomenon near the boundary is *conditioning*: at
`κε = 0.0225, ωε = 2π`, `|f| = 2.6e-06` and `|det Γ_1| = 6.0e-08 > 0` —
weakly damped rotation completing whole turns inside one exposure makes
`Γ_1` nearly singular and branch recovery ill-conditioned, honestly a
regime to avoid or to report with errors, not a singularity to handle.

**Rational `ε/Δ` in the general case; the irrational obstruction
([completeness_rational.py](completeness_rational.py)).** For
`ρ = ε/Δ = p/q`, `e^{μ_m ε} = r^ρ e^{i(θ+2πm)ρ}` has period
`q/gcd(p,q)` in `m`, so §7's symmetry residual `R(m)` is an exact
quadratic polynomial on each of finitely many residue classes and all
integer roots are enumerable: completeness over all `m` at any rational
ratio (verified at `ρ = 1/3` on the frozen general example: only root
`m = 0`). For irrational `ρ` this fails intrinsically. The denominator
of `d_m`, as its phase traverses the circle, traces an ellipse centred
at `−2` with semi-axes `a + a⁻¹ > 2` and `a⁻¹ − a` (`a = r^ρ`), which
encloses the origin; hence the normalized limit function of `R(m)/m²`
takes both signs (its coefficient `α ≠ 0` in these examples; the
degenerate `α = 0` case, where symmetry is automatic, is not treated).
Dense phases then give: `R` changes sign at arbitrarily large `m`
(15,278 sign changes up to `m = 20000` at `ρ = (√5−1)/2`) and
`|R(m)|/m²` is arbitrarily small infinitely often (min `1.6e-05` over
`m > 10000`). So no finite window and no uniform *relative* margin
exist from symmetry alone at irrational ratio. Two honest qualifications:
absolute residuals at the golden ratio still grow (`min|R|` is `3.7`,
`113`, `5238` over `m < 100`, `< 1000`, `< 5000`), because it is badly
approximable — whether a fixed absolute tolerance admits an effective
finite window is a Diophantine question about `ρ`, not settled here; and
exact roots `R(m) = 0` at large `m` remain codimension-one coincidences,
generically absent but not excludable by any finite symmetry check.

**What remains open after §11, plainly:** a parameter-free proof (or a
compatible counterexample) for the scalar-`Φ` family; the `α = 0`
degenerate symmetry case; effective irrational-ratio windows via
Diophantine data; and everything finite-sample in milestone 3
(set-valued branches, two exposures, noise budgets).

## 12. Milestone 3a: set-valued branch reports, and a filter that bites

[branch_sets.py](branch_sets.py) reruns the §8 design (same seeds) but
reports, per replicate, the *set* of branches with phase residual within
`τ` of the best, for `τ ∈ {0.01, 0.03, 0.1}` rad and `τ = c/√N`,
`c ∈ {1, 3}`. Two findings, the second more useful than the first:

- **The sets are singletons.** Median (and maximum) set size is 1 at
  every `N` and `τ` tried: in this design the population gap (`0.274`
  rad) is so large relative to phase noise that no rival ever enters
  the tolerance band. Set-valued reporting on phase alone therefore
  adds nothing here — it would matter at the near-alias ratios of §10
  (margin `0.0023` rad at `ε/Δ = 1/3`), which is where a later slice
  should test it. Coverage failures at `N = 1000` (21–23/24 phase-only)
  are winner errors: the true residual occasionally sits further than
  `τ` from the best (largest gap `0.187` rad).
- **The population test's hard `ℓ² ≥ 0` filter discards the truth at
  finite `N`.** The true branch's *estimated* `ℓ²` is negative in 4/24
  replicates at both `N = 1000` and `N = 4000` (true `ℓ² = 0.04` is
  small against estimator noise). With the hard filter, coverage at
  `N = 4000` drops to 20/24 even though the true branch has the best
  phase residual in 24/24; a slack of `0.02` restores 24/24. Lesson for
  any finite-record version of the §5/§7 test: eligibility conditions
  that are exact at population level (`ℓ² ≥ 0`, and by analogy
  `Σ ≻ 0`, `Dm ≻ 0` in §7) must be softened by an `N`-dependent slack
  or turned into reported residuals — applied hard, they delete the
  correct motion before the phase evidence is even consulted.

Descriptive only, one frozen design, tolerances not calibrated from a
sampling theory; no coverage guarantee. Milestone 3 still needs:
tolerance calibration, set-valued tests at near-alias ratios,
unknown-mean handling, two-exposure schedules, noise/light budgets.

## 13. Milestone 3b: two exposures — population win, finite-N caution

[two_exposures.py](two_exposures.py) tests §10's suggestion on the
frozen vortex at `ε/Δ ∈ {1/3, 1/2}` (branches `m ∈ [−15, 15]`,
`ℓ²` slack `0.02` per §12). At population level the idea works exactly
as hoped, with one refinement: the `1/3` near-alias `m = 11`
(`|phase residual| = 0.0023` rad, would claim `σ = 8906`) is already
killed at that single ratio by zero lag (`ℓ² = −0.051`), and the
combined margin — min over rivals of the max residual across the two
exposures — is `0.274` rad, versus `0.0023` rad for `1/3` alone on
phase. Different ratios put their weak spots at different branches;
the max-residual combination inherits the better margin.

Finite records (24 seeded replicates per exposure, independent tracks)
are a caution against naive combination rules. Intersecting the two
plug-in tolerance sets is *worse* than the better single exposure at
`N ≤ 4000`: independent winner errors make the intersection empty in
14/24 replicates at `N = 1000, τ = 0.03` (coverage 6/24 vs 13/24 for
`1/2` alone). A joint rule — rank branches by the max residual across
exposures, keep those within `τ` of the best — does better than
intersection (12/24, empty 7/24, where emptiness now means the
slackened `ℓ²` eligibility shares no branch across exposures) but
still does not beat the good single exposure at small `N`. At
`N = 16000` every variant covers 24/24 with singleton sets. Two more
honest observations: at `1/3` the sets are genuinely non-singleton
(median size 2, max 10 at `τ = 0.1`) — set-valued reporting earns its
keep exactly where §12 predicted, at near-alias ratios; and widening
the search window from `m ∈ [−5, 5]` (§8/§12) to `[−15, 15]` visibly
costs coverage at small `N` (more rivals, more chances to win by
noise), so the §11 complete candidate accounting matters practically,
not just in principle. What milestone 3 still needs: tolerance/slack
calibration from estimator sampling theory (or a bootstrap), a
combination rule derived rather than guessed, unknown-mean handling,
and the light/noise budget accounting — whether two short films at two
exposures beat one long film at the better exposure, at equal total
frames, is the design question §13 leaves open: on this evidence, at
small `N`, they do not.

## 14. Milestone 3c: unknown trap centre costs nothing (in this design)

[unknown_mean.py](unknown_mean.py) removes §8's known-zero-mean
assumption. With the true centre at zero, demeaning by the sample mean
changes nothing measurable (true-branch wins 21/24, 24/24, 24/24 and
median relative `σ` errors 0.108/0.035/0.026 at `N = 1000/4000/16000`,
identical to the raw estimator to three decimals; median `κ` error
within `0.001` of raw) — the feared demeaning bias from correlated
frames is below the estimator noise everywhere in this design. With
an unknown centre offset `μ₀ = 0.7 + 0.4i` (stationary sd per
coordinate is 1), the raw-moment estimator fails outright: it refuses
all 24 replicates at every `N` because the offset inflates every lag
by `|μ₀|²` and drives `|φ̂|` out of `(0, 1)` — a loud failure, not a
silent wrong answer, but total. The demeaned estimator reproduces the
zero-centre numbers exactly (the offset cancels in floating point at
these seeds). So: always demean; in this design it is free insurance.
Caveats: one offset size, one design; a *drifting* centre (stage drift)
is a different, harder problem not touched here. Milestone 3's
remaining pieces are now tolerance/slack calibration and the
equal-frames light-budget comparison of §13.

## 15. Milestone 3d: equal frames — spend them at the good exposure

[equal_frames.py](equal_frames.py) answers §13's design question on
the frozen vortex: total budget `T = 2N` frames as (a) `2N` at
`ε/Δ = 1/2`, (b) `2N` at `1/3`, (c) `N + N` split across both, combined
by §13's joint max-residual ranking (all demeaned, slack `0.02`,
branches `[−15, 15]`, 24 seeded replicates):

| T | 2N @ 1/2 wins (σ err) | 2N @ 1/3 wins (σ err) | split wins (σ err) |
|---|---|---|---|
| 1000 | 17/24 (0.149) | 7/24 (2.262) | 16/24 (0.245) |
| 4000 | 24/24 (0.054) | 13/24 (0.079) | 22/24 (0.048) |
| 16000 | 24/24 (0.026) | 18/24 (0.036) | 24/24 (0.052) |

Splitting never beats concentrating at the good exposure on branch
identification; its only edge is a slightly smaller median `σ` error
at `T = 4000` (0.048 vs 0.054) bought with two lost replicates. And
`1/3` alone stays unreliable even at `T = 16000` (18/24): §10's margin
table is not a curiosity, it is the design variable that decides
whether finite films work at all. Verdict for this design: choose the
exposure fraction with a healthy margin (§10) and spend the whole
light budget there; a second exposure is insurance against an unknown
bad ratio, not an improvement over a known good one. What milestone 3
still owes: principled tolerance/slack calibration, and any claim at
all outside this frozen design family.

## 16. Milestone 3e: tolerances derived, not guessed

[tolerance_calibration.py](tolerance_calibration.py) removes the last
guessed numbers of milestone 3. The frame series is a proper complex
Gaussian stationary series with known population autocovariance
`γ_h`, so Isserlis' theorem gives the estimators' exact asymptotic
covariances, `N·Cov(γ̂_k, conj γ̂_l) → Σ_h γ_h γ_{k−l−h}` and
`N·Cov(γ̂_k, γ̂_l) → Σ_h γ_{k−h} γ_{l+h}` (geometric sums, evaluated at
the design). The true branch's phase residual `R` and implied `ℓ²`
are smooth in `(γ̂₀, γ̂₁, γ̂₂)`; the delta method gives
`sd(R)·√N = 3.935` rad and `sd(ℓ²)·√N = 2.209`, hence
`τ₉₅(N) = 1.96·sd(R) = 0.244 / 0.122 / 0.061` rad and `ℓ²` slack
`0.137 / 0.068 / 0.034` at `N = 1000 / 4000 / 16000`. Because the set
keeps branches within `τ` of the *best* residual, `|R_true| ≤ τ` is
sufficient for retention, so coverage is asymptotically ≥ 95% inside
the model. Monte Carlo on fresh seeds confirms the standard
deviations (0.126 vs 0.124 rad; 0.065 vs 0.070). Measured coverage on
the original §8 seeds is 24/24 at every `N` — against 21–23/24 for
the guessed tolerances of §12 — and the honest price shows at
`N = 1000`, where `τ₉₅ = 0.244` rad is close to the population
margin (0.274 rad): median set size 2, median relative `σ` spread
0.57. §12's guessed slack 0.02 was 2–7× too small; it appeared to
work only because the `ℓ²` dips at those seeds were shallow.

Two exposures get a derived combination rule: independent films give
independent, asymptotically Gaussian residuals, so rank branches by
the standardized quadratic form `Q_m = Σ_j R²_{j,m}/(v_j/N_j)`
(`χ²₂` at the true branch), not by §13's guessed max-residual. On
§13's exact seeds (whose joint-max numbers this slice reproduces:
12/24 and 18/24 at `N = 1000, 4000`), the relative cutoff
`Q_m ≤ Q_min + 5.99` covers 23/24, 23/24, 24/24 — better than or
equal to every rule tried in §13–§15 at every `N`. The absolute
cutoff `Q_m ≤ 5.99` covers only 21/24 at `N = 16000` with 3 empty
sets: it is detecting the trapezoid simulator's bias (mean estimated
`ℓ²` 0.019 vs population 0.04 at `N = 1000`; raw moment variances
inflated ~25% at substep 20, ~0% at substep 80), which does not
shrink with `N` while the noise does. So the absolute form is a
model check, the relative form the report — and §13's "emptiness"
pathologies were an artefact of combining unstandardized residuals
with a guessed tolerance, not of two exposures themselves; §15's
equal-frames verdict (spend frames at the good exposure) is
unchanged, since it compared winners, not calibrated sets.

**What remains unproved, plainly:** the calibration is first-order
asymptotic and in-model — 24 replicates cannot distinguish 95%
coverage from 88% (the two-exposure absolute rule's 21–22/24 is
consistent with both, plus simulator bias); nothing is claimed for
non-Gaussian films, drifting centres (§14), or designs other than
the frozen family; and the delta-method variance is evaluated at
population parameters a real user must first estimate (a parametric
bootstrap from the winning branch is the natural next slice).
Milestone 3's finite-record programme is otherwise complete on this
design: set-valued reports with derived tolerances, derived
two-exposure combination, unknown-centre handling, and the
equal-frames light-budget verdict.

## 17. Milestone 3f: the same tolerances from one film (bootstrap)

[bootstrap_calibration.py](bootstrap_calibration.py) closes §16's
plug-in gap. From a single film: take the winning branch's implied
`(κ, ω*, s*, ℓ²*)`, simulate `B = 24` bootstrap films of the same
length from that fitted motion, and set `τ_boot = 1.96·sd(R*)` over
the bootstrap worlds (where the fitted branch is true by
construction), with a one-sided bootstrap `ℓ²` slack. On the §8
seeds the bootstrap needs no population knowledge and loses almost
nothing: coverage 24/24 at every `N` (matching §16), median set
sizes identical (2 at `N = 1000`, else 1), and median
`τ_boot/τ_population = 0.94 / 0.93 / 0.96`. Even the 3 replicates at
`N = 1000` whose plug-in winner is the wrong branch still cover —
at that length `τ` is wide enough that the true branch sits inside
the wrongly-centred set — but this is luck of a wide tolerance, not
a guarantee: a bootstrap centred on a wrong winner calibrates for a
film that was not taken, and at a near-alias ratio (§10) with a
narrower margin it would fail silently. Cost is real: the recorded
run (24 films × 24 bootstraps × 3 lengths) takes about two minutes
in pure Python, against seconds for §16's closed form. Verdict:
§16's formula when a design's parameters are known or can be
estimated once and reused; the bootstrap as the per-film fallback
that asks the data only. What remains unproved is unchanged from
§16 (first-order, in-model, one frozen family) plus the bootstrap's
own plug-in bias, unmeasured beyond the τ ratios above.

## 18. Milestone 3g: finite records in the general case

[general_finite_record.py](general_finite_record.py) repeats §16's
construction for the general (non-isotropic) test of §7/§11, where
the scalar evidence per branch is the symmetry residual
`R(m) = (Σ_m)₀₁ − (Σ_m)₁₀`. On the frozen general example
(`A = [[−1.2, −2.0], [0.8, −0.7]]`, true branch `m = 0`, nearest
rival `|R| = 0.576` in `m ∈ [−5, 5]`), Isserlis' theorem for the
real Gaussian vector series gives the 11×11 asymptotic covariance
of `(Γ̂₀, Γ̂₁, Γ̂₂)`, and the delta method through the branch
construction gives `sd(R)·√N = 6.194`, i.e.
`τ₉₅ = 0.384 / 0.192 / 0.096` at `N = 1000 / 4000 / 16000`. Monte
Carlo agrees to 1% (0.198 vs 0.196 at `N = 1000`, 48 fresh seeds;
mean residual `+0.036`, a finite-sample/simulator bias of about
0.18 sd, reported not corrected). Calibrated sets cover 24/24 at
every `N`, with the true branch the outright winner in 22/24,
23/24, 24/24 — the set report earns its keep exactly in the
replicates where the winner is wrong. Scope: only the symmetry
residual is calibrated. The general test's remaining population
conditions (`Σ, Dm ≻ 0`, zero-lag off-diagonal, equal-`ℓ²`
diagonals) still need their finite-`N` slacks derived — each is
another smooth function of the same 11 coordinates, so the
machinery above applies unchanged, and §12's lesson says applying
them hard would delete the truth. That, a general-case bootstrap,
and any claim outside the two frozen designs are what milestone 3
still owes; the population-level remainders of §11 (scalar-`Φ`
proof, `α = 0`, irrational-ratio windows) are untouched by this
finite-record work.

## 19. Milestone 3h: general eligibility — hard filters bite, joint slacks matter

The second half of [general_finite_record.py](general_finite_record.py)
derives slacks for §18's remaining conditions by the same
11-coordinate delta method (all Monte-Carlo checked; the
`λ_min` standard deviations are first-order overestimates —
0.113 predicted vs 0.078 simulated for `Σ` — because `λ_min` is
concave, which errs on the safe side for a slack). Three
measurements on the §18 replicates:

- **Hard sign-filters are disastrous in the general case too.**
  Requiring `λ_min(Σ), λ_min(Dm) > 0`, `ℓ̂² ≥ 0` deletes the true
  branch in 9/24 films at `N = 1000` and 5/24 at `N = 4000`
  (coverage 15/24 and 19/24) — worse than §12's isotropic filter,
  because five noisy conditions each get a vote.
- **Per-condition 95% slacks undercover jointly** (21/20/21 of
  24): five conditions at 95% each retain the truth only about
  `0.95⁵ ≈ 77%` of the time if independent. Calibration must be
  joint, not per-condition — the union bound is not optional.
- **Bonferroni 99% slacks** (per-condition `z = 2.576`) recover
  22/24, 24/24, 23/24 against symmetry-only's 24/24 everywhere,
  and trim the median set at `N = 1000` from 2 to 1: eligibility
  buys smaller sets at a small coverage price. The residual gap
  at `N = 16000` tracks the simulator's off-diagonal bias
  (mean `−0.011` at `N = 1000`, not shrinking with `N`), the same
  effect §16's absolute cutoffs detected.

So the finite-record general test now has every tolerance derived:
symmetry `τ` (§18) and joint eligibility slacks (here), with the
honest recommendation to report symmetry sets with Bonferroni
eligibility as a trimming step, never as a gate. What milestone 3
still owes after §19: a general-case parametric bootstrap (§17
analogue), any claim outside the two frozen designs, and §11's
population remainders.

