"""Section 22: can a scalar-Phi rival drift ever fake the film?

DERIVATION s11 ([real_logs.py](real_logs.py)) shows that when the
one-frame propagator Phi = exp(A Delta) is scalar, Phi alone admits a
continuous 2-parameter family of extra real logarithms per winding
branch beta (stretch t, orientation phi).  On two frozen examples a
coarse grid found only the true drift compatible with the observed
covariances, and a dimension count (2 parameters, 3 equality
conditions: Sigma-symmetry, zero-lag off-diagonal, equal ell^2
diagonals) says a compatible rival would be a codimension-one
coincidence in the remaining truth parameters.  This script searches
for that coincidence instead of assuming it away:

* truths sweep beta_true in {pi, 2pi, 3pi}, alpha, stretch/orientation
  of the true drift, four diffusion shapes (including isotropic), and
  shutter fractions;
* for every rival branch beta != beta_true's motion, the joint
  residual J(t, phi) = sym^2 + offdiag^2 + ell_split^2 (from
  real_logs.compatibility, scaled by the observed covariance scale)
  is minimized continuously: coarse grid, then pattern-search
  refinement to step < 1e-7;
* a rival counts only if J ~ 0 AND the positivity conditions
  (Sigma, Dm positive definite, ell^2 >= 0) hold there; the true
  drift itself is recovered as a control (J ~ 1e-20).

Result (recorded in RECORDED_RUN.md): the smallest rival minimum over
the sweep stays orders of magnitude above the control, so on this
truth family the film separates every rival motion; no compatible
counterexample is exhibited.  This is a search over a stated family,
not a proof for all parameters.
"""

from __future__ import annotations

import math
import sys

from general_tracks import GeneralVortex, expm, inverse2, matmul, scale
from real_logs import compatibility, family_drift, real_log_candidates

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"[{'ok' if ok else 'FAIL'}] {name} {detail}")
    if not ok:
        FAILURES.append(name)


def joint_residual(r: dict, s: float) -> float:
    return (r["sym"] / s) ** 2 + (r["offdiag"] / s) ** 2 + (r["ell_split"] / s) ** 2


def minimize_branch(beta, alpha, G0, G1, Phi, Delta, eps, s, truth=None):
    """Minimize J(t, phi) for one rival branch; optionally exclude a
    small ball around the true drift (same-branch rivals)."""

    def J(t: float, phi: float):
        Ac = family_drift(alpha, beta, t, phi, Delta)
        if truth is not None:
            d = max(abs(Ac[i][j] - truth[i][j]) for i in range(2) for j in range(2))
            if d < 0.25:
                return None, None
        return joint_residual(compatibility(Ac, G0, G1, Phi, Delta, eps), s), Ac

    best = (math.inf, 0.0, 0.0)
    for i in range(-6, 7):
        for j in range(24):
            v, _ = J(0.25 * i, math.pi * j / 24)
            if v is not None and v < best[0]:
                best = (v, 0.25 * i, math.pi * j / 24)
    # pattern search refinement
    step_t, step_p = 0.25, math.pi / 24
    v, t, phi = best
    while step_t > 1e-7:
        improved = False
        for dt, dp in ((step_t, 0), (-step_t, 0), (0, step_p), (0, -step_p),
                       (step_t, step_p), (step_t, -step_p),
                       (-step_t, step_p), (-step_t, -step_p)):
            nv, _ = J(t + dt, phi + dp)
            if nv is not None and nv < v:
                v, t, phi, improved = nv, t + dt, phi + dp, True
        if not improved:
            step_t *= 0.5
            step_p *= 0.5
    Ac = family_drift(alpha, beta, t, phi, Delta)
    r = compatibility(Ac, G0, G1, Phi, Delta, eps)
    return v, t, phi, r, Ac


def run_truth(name, alpha, beta_true, t_true, phi_true, Dm, Delta, eps_frac):
    eps, ell2 = eps_frac * Delta, 0.03
    A = family_drift(alpha, beta_true, t_true, phi_true, Delta)
    g = GeneralVortex(A, Dm)
    G0 = g.observed_cov_matrix(Delta, eps, ell2, 0)
    G1 = g.observed_cov_matrix(Delta, eps, ell2, 1)
    G2 = g.observed_cov_matrix(Delta, eps, ell2, 2)
    Phi = matmul(G2, inverse2(G1))
    # the observed Phi must be the scalar exp(A Delta)
    E = expm(scale(A, Delta))
    perr = max(abs(Phi[i][j] - E[i][j]) for i in range(2) for j in range(2))
    s = max(1.0, max(abs(G0[i][j]) for i in range(2) for j in range(2)))
    kind, payload = real_log_candidates(Phi, Delta)
    if kind != "family" or perr > 1e-8:
        check(f"{name}: scalar Phi setup", False, f"(kind={kind}, err {perr:.1e})")
        return math.inf
    a_rec, betas = payload
    r_true = compatibility(A, G0, G1, Phi, Delta, eps)
    j_true = joint_residual(r_true, s)
    # Different-branch rivals are the genuine extra motions.  A
    # same-branch minimum outside a ball around the truth only
    # measures continuity (it sits on the ball boundary), so it is
    # printed for scale but excluded from the separation verdict.
    worst = math.inf
    worst_beta = None
    for beta in betas:
        same_motion = abs(abs(beta) - abs(beta_true)) < 1e-12
        v, t, phi, r, Ac = minimize_branch(
            beta, a_rec, G0, G1, Phi, Delta, eps, s,
            truth=A if same_motion else None)
        pos = r["detS"] > 0 and r["s00"] > 0 and r["detDm"] > 0 and r["dm00"] > 0 \
            and r["ell2"] >= -1e-9
        tag = " (same branch, >0.25 from truth)" if same_motion else ""
        if not same_motion and v < worst:
            worst, worst_beta = v, beta
        print(f"    beta={beta:+.3f} min J={v:.3e} at t={t:+.3f} phi={phi:.3f} "
              f"positivity={'holds' if pos else 'fails'}{tag}")
    check(f"{name}: truth control J~0, other branches separated",
          j_true < 1e-16 and worst > 1e-4,
          f"(J_true={j_true:.1e}, min other-branch J={worst:.3e} "
          f"at beta={worst_beta:+.3f})")
    return worst


def main() -> int:
    Dms = {
        "mixed": [[1.0, 0.3], [0.3, 0.6]],
        "isotropic": [[1.0, 0.0], [0.0, 1.0]],
        "aniso-diag": [[1.5, 0.0], [0.0, 0.5]],
        "rotated": [[0.9, -0.4], [-0.4, 1.2]],
    }
    cases = [
        # name, alpha, beta_true, t_true, phi_true, Dm key, Delta, eps_frac
        ("pi/mixed", -1.0, math.pi, 0.0, 0.0, "mixed", 1.0, 0.5),
        ("2pi/mixed", -1.0, 2 * math.pi, 0.0, 0.0, "mixed", 1.0, 0.5),
        ("pi/isotropic", -1.0, math.pi, 0.0, 0.0, "isotropic", 1.0, 0.5),
        ("2pi/isotropic", -0.7, 2 * math.pi, 0.0, 0.0, "isotropic", 0.9, 0.4),
        ("pi/aniso stretched truth", -1.2, math.pi, 0.4, 0.7, "aniso-diag", 1.0, 0.5),
        ("3pi/rotated", -0.9, 3 * math.pi, -0.3, 1.1, "rotated", 0.8, 0.6),
        ("2pi/short shutter", -1.5, 2 * math.pi, 0.2, 0.3, "mixed", 1.0, 0.15),
        ("pi/full shutter", -0.6, math.pi, 0.0, 0.0, "aniso-diag", 1.0, 0.95),
    ]
    minima = []
    for name, alpha, bt, tt, pt, dm, Delta, ef in cases:
        print(f"  truth {name}:")
        minima.append(run_truth(name, alpha, bt, tt, pt, Dms[dm], Delta, ef))
    check("no compatible other-branch rival in sweep (all minima > 1e-4)",
          min(minima) > 1e-4, f"(smallest other-branch minimum {min(minima):.3e})")
    print("\nFAILED:", FAILURES if FAILURES else "none -- all checks passed")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
