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

