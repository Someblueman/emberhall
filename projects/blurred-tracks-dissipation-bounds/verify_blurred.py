#!/usr/bin/env python3
"""Independent verification of blurred_tracks.py.

Three routes that do not share the closed-form algebra:
  1. Numerical quadrature of the defining double integrals in real 2x2
     matrix form, using only the latent covariance C(tau).
  2. Monte Carlo simulation of the latent diffusion with exact Gaussian
     transitions on a fine sub-grid, trapezoid frame averages, and added
     localization noise.
  3. Branch completeness: for eps/Delta = 1/2 the unwrapped phase of the
     blur factor is strictly monotone within each residue class m mod 4
     (DERIVATION.md, section 5), so each class holds at most one candidate
     branch; the verifier finds every candidate from quadrature covariances
     and tests it, instead of scanning a finite window and hoping.

Exits nonzero on any failure.  Standard library only.
"""
from __future__ import annotations

import cmath
import math
import random
import sys

from blurred_tracks import (Camera, FROZEN, Vortex, blur_factor_F,
                            blur_factor_Z, branches_from_covariances,
                            observed_cov_complex, observed_cov_matrix,
                            wrap_angle)

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"[{'ok' if ok else 'FAIL'}] {name} {detail}")
    if not ok:
        FAILURES.append(name)


# --- route 1: quadrature of the defining integrals -------------------------

def quadrature_cov_matrix(v: Vortex, cam: Camera, k: int, n: int = 1200):
    """(1/eps^2) int int C(k Delta + u - v) du dv by trapezoid rule."""
    h = cam.eps / n
    acc = [[0.0, 0.0], [0.0, 0.0]]
    for i in range(n + 1):
        wi = 0.5 if i in (0, n) else 1.0
        for j in range(n + 1):
            wj = 0.5 if j in (0, n) else 1.0
            C = v.latent_cov_matrix(k * cam.Delta + (i - j) * h)
            w = wi * wj
            for a in (0, 1):
                for b in (0, 1):
                    acc[a][b] += w * C[a][b]
    scale = h * h / cam.eps ** 2
    out = [[acc[a][b] * scale for b in (0, 1)] for a in (0, 1)]
    if k == 0:
        out[0][0] += cam.ell2
        out[1][1] += cam.ell2
    return out


def complex_from_matrix(G) -> complex:
    return complex(G[0][0] + G[1][1], G[1][0] - G[0][1])


# --- route 2: Monte Carlo ---------------------------------------------------

def simulate_frames(v: Vortex, cam: Camera, n_frames: int, seed: int,
                    sub: int = 40) -> list[complex]:
    rng = random.Random(seed)
    lam = v.lam
    h = cam.eps / sub
    step = cmath.exp(-lam * h)
    sd = math.sqrt(v.s * (1.0 - math.exp(-2.0 * v.kappa * h)))
    gap = cam.Delta - cam.eps
    gap_step = cmath.exp(-lam * gap)
    gap_sd = math.sqrt(v.s * (1.0 - math.exp(-2.0 * v.kappa * gap)))
    noise_sd = math.sqrt(cam.ell2)
    z = complex(rng.gauss(0.0, math.sqrt(v.s)), rng.gauss(0.0, math.sqrt(v.s)))
    frames: list[complex] = []
    for _ in range(n_frames):
        acc = 0.5 * z
        for _i in range(sub):
            z = step * z + complex(rng.gauss(0.0, sd), rng.gauss(0.0, sd))
            acc += z
        acc -= 0.5 * z  # trapezoid: last point half weight
        y = acc / sub + complex(rng.gauss(0.0, noise_sd), rng.gauss(0.0, noise_sd))
        frames.append(y)
        z = gap_step * z + complex(rng.gauss(0.0, gap_sd), rng.gauss(0.0, gap_sd))
    return frames


def empirical_gamma(frames: list[complex], k: int) -> complex:
    n = len(frames) - k
    return sum(frames[i + k] * frames[i].conjugate() for i in range(n)) / n


# --- route 3: complete branch accounting for eps/Delta = 1/2 ---------------

def class_candidates(g0: float, g1: complex, g2: complex,
                       Delta: float, eps: float) -> list[int]:
    """All m that could satisfy the phase identity, over ALL integers m.

    arg F_m (unwrapped) = 2 arg sinh(c_r) - 2 arg(lam_m) within class
    r = m mod 4, strictly increasing in m, range an open interval of
    length 2 pi.  At most one target + 2 pi j lies in it; bisect for it.
    """
    phi = g2 / g1
    kappa = -math.log(abs(phi)) / Delta
    theta = cmath.phase(phi)
    target = cmath.phase(g1 / phi)
    found: list[int] = []

    def omega_of(m: int) -> float:
        return (theta + 2.0 * math.pi * m) / Delta

    for r in range(4):
        m0 = r - 4 if r >= 2 else r  # a representative with small |m|
        lam0 = complex(kappa, -omega_of(m0))
        A = cmath.phase(cmath.sinh(lam0 * eps / 2.0))

        def P(m: int) -> float:
            return 2.0 * A - 2.0 * math.atan2(-omega_of(m), kappa)

        lo_lim, hi_lim = 2.0 * A - math.pi, 2.0 * A + math.pi
        js = [j for j in range(-3, 4) if lo_lim < target + 2.0 * math.pi * j < hi_lim]
        if not js:
            continue
        want = target + 2.0 * math.pi * js[0]
        # bracket then bisect on the arithmetic progression m = m0 + 4 t
        t_lo, t_hi = -1, 1
        while P(m0 + 4 * t_lo) > want:
            t_lo *= 2
        while P(m0 + 4 * t_hi) < want:
            t_hi *= 2
        while t_hi - t_lo > 1:
            t_mid = (t_lo + t_hi) // 2
            if P(m0 + 4 * t_mid) <= want:
                t_lo = t_mid
            else:
                t_hi = t_mid
        for t in (t_lo - 1, t_lo, t_hi, t_hi + 1):
            found.append(m0 + 4 * t)
    return sorted(set(found))


def main() -> int:
    v: Vortex = FROZEN["vortex"]
    cam: Camera = FROZEN["camera"]

    # route 1
    quad_g: list[complex] = []
    max_err = 0.0
    for k in range(4):
        Q = quadrature_cov_matrix(v, cam, k)
        quad_g.append(complex_from_matrix(Q))
        G = observed_cov_matrix(v, cam, k)
        for a in (0, 1):
            for b in (0, 1):
                max_err = max(max_err, abs(Q[a][b] - G[a][b]))
    check("quadrature vs closed form, k=0..3", max_err < 5e-5,
          f"(max abs err {max_err:.2e})")

    # route 3 on quadrature covariances (not the closed form)
    cands = class_candidates(quad_g[0].real, quad_g[1], quad_g[2],
                             cam.Delta, cam.eps)
    _, _, cand_branches = branches_from_covariances(
        quad_g[0].real, quad_g[1], quad_g[2], cam.Delta, cam.eps, cands)
    ok = [b for b in cand_branches if abs(b.phase_residual) < 1e-6 and b.ell2 >= -1e-9]
    print(f"  all-integer phase candidates: {cands}")
    for b in cand_branches:
        print(f"    m={b.m}: phase residual {b.phase_residual:+.2e}, ell^2 {b.ell2:+.6f}, "
              f"sigma {b.sigma:.3f}")
    check("exactly one compatible branch (true m=1)",
          len(ok) == 1 and ok[0].m == 1 and abs(ok[0].omega - v.omega) < 1e-6
          and abs(ok[0].sigma - v.dissipation()) < 1e-4,
          f"(compatible: {[b.m for b in ok]})")

    # route 2
    frames = simulate_frames(v, cam, n_frames=30000, seed=20261123)
    mc_errs = []
    for k in range(3):
        emp = empirical_gamma(frames, k)
        exact = observed_cov_complex(v, cam, k)
        mc_errs.append(abs(emp - exact))
    check("Monte Carlo vs closed form, k=0..2", max(mc_errs) < 0.04,
          f"(abs errs {[f'{e:.4f}' for e in mc_errs]}, N=30000 frames)")

    # dissipation by the current-velocity route on simulated latent states:
    # sigma = E|omega J X|^2 / D, estimated from E|X|^2 = gamma_0(latent).
    latent_cam = Camera(Delta=cam.Delta, eps=cam.eps, ell2=0.0)
    lat = simulate_frames(v, latent_cam, n_frames=20000, seed=7)
    # frame averages underestimate E|X|^2 by the zero-lag factor Z; undo it.
    ex2 = empirical_gamma(lat, 0).real / blur_factor_Z(v.lam, cam.eps)
    sigma_mc = v.omega ** 2 * ex2 / v.D
    check("dissipation via simulated current velocity",
          abs(sigma_mc - v.dissipation()) < 0.05 * v.dissipation(),
          f"(MC {sigma_mc:.2f} vs exact {v.dissipation():.2f})")

    # controls
    v_eq = Vortex(kappa=1.0, omega=0.0, D=1.0)
    g_eq = [observed_cov_complex(v_eq, cam, k) for k in range(3)]
    _, _, b_eq = branches_from_covariances(g_eq[0].real, g_eq[1], g_eq[2],
                                           cam.Delta, cam.eps, range(-50, 51))
    ok_eq = [b for b in b_eq if b.compatible()]
    check("equilibrium control: only m=0, sigma=0",
          len(ok_eq) == 1 and ok_eq[0].m == 0 and ok_eq[0].sigma == 0.0)

    small = Camera(Delta=1.0, eps=1e-4, ell2=0.04)
    F = blur_factor_F(v.lam, small.eps)
    Z = blur_factor_Z(v.lam, small.eps)
    check("vanishing exposure: F, Z -> 1", abs(F - 1) < 1e-6 and abs(Z - 1) < 1e-3,
          f"(|F-1|={abs(F-1):.2e}, |Z-1|={abs(Z-1):.2e} at eps=1e-4)")
    g_ps = [observed_cov_complex(v, small, k) for k in range(3)]
    _, _, b_ps = branches_from_covariances(g_ps[0].real, g_ps[1], g_ps[2],
                                           1.0, small.eps, range(-3, 4))
    max_res = max(abs(b.phase_residual) for b in b_ps)
    check("point-sampling near-degeneracy at eps=1e-4 (all branches nearly pass phase)",
          max_res < 0.01, f"(max |residual| {max_res:.2e} for m in -3..3)")

    print("FAILED:", FAILURES if FAILURES else "none — all checks passed")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
