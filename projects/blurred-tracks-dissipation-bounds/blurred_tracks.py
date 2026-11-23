#!/usr/bin/env python3
"""Shutter-averaged covariance and dissipation for a rotating linear diffusion.

Latent motion (Brownian vortex / rotating Ornstein-Uhlenbeck process):

    dX = A X dt + sqrt(2 D) dW,   A = -kappa I + omega J,
    J = [[0, -1], [1, 0]],  kappa > 0, D > 0.

Stationary covariance is s I with s = D / kappa, and the latent covariance
function is C(tau) = s exp(-kappa |tau|) R(omega tau), R a rotation.
The steady-state entropy production rate (k_B = 1) is sigma = 2 omega^2 / kappa.

Observation: frames every Delta, rectangular shutter of width eps in (0, Delta]
anchored at the frame start, both coordinates observed, plus independent
Gaussian localization error of variance ell^2 per coordinate:

    Y_n = (1/eps) int_{n Delta}^{n Delta + eps} X(t) dt + eta_n.

All covariances are derived in DERIVATION.md.  In complex form, with
lam = kappa - i omega, phi = exp(-lam Delta), z = x + i y and
gamma_k = E[z_{n+k} conj(z_n)] for the observed frames:

    gamma_k = 2 s F phi^k            (k >= 1)
    gamma_0 = 2 s Z + 2 ell^2
    gamma_{-k} = conj(gamma_k)
    F = 4 sinh^2(lam eps / 2) / (lam eps)^2
    Z = (2 / eps^2) Re[ eps/lam - (1 - exp(-lam eps)) / lam^2 ]   (real, in (0, 1])

Standard library only.  Run as a script for the frozen milestone-1 result.
"""
from __future__ import annotations

import cmath
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Vortex:
    kappa: float   # trap relaxation rate, > 0
    omega: float   # rotation rate (signed)
    D: float       # diffusion coefficient, > 0

    @property
    def s(self) -> float:
        """Stationary variance per coordinate."""
        return self.D / self.kappa

    @property
    def lam(self) -> complex:
        return complex(self.kappa, -self.omega)

    def dissipation(self) -> float:
        """Steady-state entropy production rate, k_B = 1 units."""
        return 2.0 * self.omega ** 2 / self.kappa

    def latent_cov_complex(self, tau: float) -> complex:
        """E[z(t+tau) conj(z(t))] for the latent process."""
        return 2.0 * self.s * math.exp(-self.kappa * abs(tau)) * cmath.exp(1j * self.omega * tau)

    def latent_cov_matrix(self, tau: float) -> tuple[tuple[float, float], tuple[float, float]]:
        """C(tau) = s exp(-kappa|tau|) R(omega tau)."""
        a = self.s * math.exp(-self.kappa * abs(tau))
        c, sn = math.cos(self.omega * tau), math.sin(self.omega * tau)
        return ((a * c, -a * sn), (a * sn, a * c))


@dataclass(frozen=True)
class Camera:
    Delta: float   # frame period, > 0
    eps: float     # exposure (shutter width), 0 < eps <= Delta
    ell2: float    # localization variance per coordinate, >= 0

    def __post_init__(self) -> None:
        if not (0.0 < self.eps <= self.Delta):
            raise ValueError("require 0 < eps <= Delta")
        if self.ell2 < 0.0:
            raise ValueError("require ell2 >= 0")


def blur_factor_F(lam: complex, eps: float) -> complex:
    """F = 4 sinh^2(lam eps/2) / (lam eps)^2; F -> 1 as eps -> 0."""
    z = lam * eps
    return 4.0 * cmath.sinh(z / 2.0) ** 2 / z ** 2


def blur_factor_Z(lam: complex, eps: float) -> float:
    """Zero-lag shutter factor Z in (0, 1]; Z -> 1 as eps -> 0."""
    val = eps / lam - (1.0 - cmath.exp(-lam * eps)) / lam ** 2
    return 2.0 * val.real / eps ** 2


def observed_cov_complex(v: Vortex, cam: Camera, k: int) -> complex:
    """gamma_k = E[z_{n+k} conj(z_n)] for shutter-averaged frames."""
    if k < 0:
        return observed_cov_complex(v, cam, -k).conjugate()
    if k == 0:
        return complex(2.0 * v.s * blur_factor_Z(v.lam, cam.eps) + 2.0 * cam.ell2, 0.0)
    phi = cmath.exp(-v.lam * cam.Delta)
    return 2.0 * v.s * blur_factor_F(v.lam, cam.eps) * phi ** k


def observed_cov_matrix(v: Vortex, cam: Camera, k: int) -> tuple[tuple[float, float], tuple[float, float]]:
    """Gamma_k = Cov(Y_{n+k}, Y_n) = [[a, -b], [b, a]] with gamma_k = 2(a + i b)."""
    g = observed_cov_complex(v, cam, k)
    a, b = g.real / 2.0, g.imag / 2.0
    return ((a, -b), (b, a))


def wrap_angle(a: float) -> float:
    """Wrap to (-pi, pi]."""
    return (a + math.pi) % (2.0 * math.pi) - math.pi if a != math.pi else math.pi


@dataclass(frozen=True)
class Branch:
    m: int                 # branch index; omega = (theta + 2 pi m) / Delta
    omega: float
    phase_residual: float  # wrap(arg F_m - arg(gamma_1 / phi)); 0 iff phase identity holds
    s: float               # stationary variance per coordinate implied by |gamma_1|
    ell2: float            # localization variance implied by gamma_0; must be >= 0
    sigma: float           # dissipation 2 omega^2 / kappa on this branch

    def compatible(self, tol: float = 1e-9) -> bool:
        return abs(self.phase_residual) <= tol and self.ell2 >= -tol


def branches_from_covariances(g0: float, g1: complex, g2: complex,
                              Delta: float, eps: float,
                              m_values) -> tuple[float, complex, list[Branch]]:
    """Enumerate sampling branches compatible with population covariances.

    kappa and phi = gamma_2 / gamma_1 are branch-independent.  Each integer
    branch m gives omega_m; it is compatible iff the phase identity
    arg F_m = arg(gamma_1 / phi) holds and the implied ell^2 >= 0.
    Returns (kappa, phi, branches).
    """
    phi = g2 / g1
    if not (0.0 < abs(phi) < 1.0):
        raise ValueError("require 0 < |phi| < 1 (stable, nondegenerate)")
    kappa = -math.log(abs(phi)) / Delta
    theta = cmath.phase(phi)
    target_phase = cmath.phase(g1 / phi)
    out: list[Branch] = []
    for m in m_values:
        omega = (theta + 2.0 * math.pi * m) / Delta
        lam = complex(kappa, -omega)
        F = blur_factor_F(lam, eps)
        s = abs(g1) / (2.0 * abs(F) * abs(phi))
        ell2 = g0 / 2.0 - s * blur_factor_Z(lam, eps)
        out.append(Branch(m=m, omega=omega,
                          phase_residual=wrap_angle(cmath.phase(F) - target_phase),
                          s=s, ell2=ell2, sigma=2.0 * omega ** 2 / kappa))
    return kappa, phi, out


# Frozen milestone-1 example (see DERIVATION.md, section 5).
FROZEN = {
    "vortex": Vortex(kappa=1.0, omega=3.9, D=1.0),
    "camera": Camera(Delta=1.0, eps=0.5, ell2=0.04),
    "branch_range": range(-200, 201),
}


def main() -> None:
    v: Vortex = FROZEN["vortex"]
    cam: Camera = FROZEN["camera"]
    print("Frozen example: kappa=1, omega=3.9, D=1 (s=1), Delta=1, eps=0.5, ell^2=0.04")
    print(f"True dissipation sigma = 2 omega^2/kappa = {v.dissipation():.6f}")
    gs = [observed_cov_complex(v, cam, k) for k in range(5)]
    for k, g in enumerate(gs):
        print(f"  gamma_{k} = {g.real:+.10f} {g.imag:+.10f}i")
    kappa, phi, branches = branches_from_covariances(
        gs[0].real, gs[1], gs[2], cam.Delta, cam.eps, FROZEN["branch_range"])
    print(f"Recovered phi = {phi.real:+.10f} {phi.imag:+.10f}i, kappa = {kappa:.10f}")
    ok = [b for b in branches if b.compatible(tol=1e-9)]
    print(f"Branches m in [-200, 200]: compatible = {[b.m for b in ok]}")
    for b in ok:
        print(f"  m={b.m}: omega={b.omega:.10f}  s={b.s:.10f}  ell^2={b.ell2:.10f}  sigma={b.sigma:.6f}")
    others = [b for b in branches if not b.compatible(tol=1e-9)]
    nearest = min(others, key=lambda b: abs(b.phase_residual))
    print(f"Nearest excluded branch by phase: m={nearest.m}, "
          f"|phase residual|={abs(nearest.phase_residual):.6f} rad, sigma would be {nearest.sigma:.3f}")
    neg = [b for b in branches if b.ell2 < 0]
    print(f"Branches excluded by ell^2 < 0 alone: {len(neg)} of {len(branches)}")


if __name__ == "__main__":
    main()
