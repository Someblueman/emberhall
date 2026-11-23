"""Section 24: Diophantine control of irrational-ratio windows.

s11 showed that at irrational rho = eps/Delta the normalized
residual R(m)/m^2 has limit function h(phi) taking both signs
(alpha != 0 always, s23), so no uniform relative margin exists;
it left open whether a fixed absolute tolerance admits an
effective finite window, calling it "a Diophantine question
about rho".  The mechanism: R(m) ~ C m^2 dist(psi_m, psi*) near
a zero psi* of h, where psi_m = frac((theta/2pi + m) rho).  So
min_m |R(m)|/m is governed by inhomogeneous Diophantine
approximation of psi* by the rotation m -> psi_m:

* badly approximable rho (bounded partial quotients; golden
  ratio conjugate, sqrt(2)-1): dist >= c/m, hence |R(m)|/m is
  bounded below and absolute residuals grow at least linearly
  along their minima -- for any tolerance tau only finitely many
  m need checking beyond an explicit-if-crude window;
* rho with a huge partial quotient (engineered here as the
  continued fraction [0; 9, 11, 1000, 7, 3]): the rotation has
  an almost-period, psi_m comes o(1/m)-close to psi*, and
  min |R(m)|/m collapses by orders of magnitude.

Exhibited on the frozen general example (EigenResidual of
completeness_rational.py): over m in [100, 200000],
min |R(m)|/m = 0.155 (golden), 0.202 (sqrt2-1), 0.0049
(engineered, at m = 169777).  Scope: one frozen truth and
float rho; the engineered rho is rational in float with the
stated continued fraction up to the huge quotient, which is
exactly the finite structure the exhibit uses.  A general
effective-window theorem (explicit c(rho) from partial
quotients, for all truths) is not claimed.
"""

from __future__ import annotations

import math
import sys
from fractions import Fraction

from completeness_rational import EigenResidual

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"[{'ok' if ok else 'FAIL'}] {name} {detail}")
    if not ok:
        FAILURES.append(name)


def cf_value(qs) -> Fraction:
    v = Fraction(qs[-1])
    for a in reversed(qs[:-1]):
        v = a + Fraction(1, v)
    return v


def min_scaled(rho: float, lo=100, hi=200_000):
    er = EigenResidual(0.9, rho * 0.9)
    best = (math.inf, None)
    for m in range(lo, hi + 1):
        v = abs(er.R(m)) / m
        if v < best[0]:
            best = (v, m)
    return er, best


def main() -> int:
    rho_eng = float(cf_value([0, 9, 11, 1000, 7, 3]))
    cases = [
        ("golden (sqrt5-1)/2, badly approximable", (math.sqrt(5) - 1) / 2, 0.10, True),
        ("sqrt2-1, badly approximable", math.sqrt(2) - 1, 0.10, True),
        ("engineered [0;9,11,1000,7,3]", rho_eng, 0.01, False),
    ]
    for name, rho, bound, is_badly in cases:
        er, (v, m) = min_scaled(rho)
        check(f"{name}: R(0)=0 control", abs(er.R(0)) < 1e-9,
              f"(|R(0)| {abs(er.R(0)):.1e})")
        if is_badly:
            check(f"{name}: min |R(m)|/m bounded below",
                  v > bound, f"(min {v:.4f} at m={m})")
        else:
            check(f"{name}: min |R(m)|/m collapses",
                  v < bound, f"(min {v:.4f} at m={m})")
    print("\nFAILED:", FAILURES if FAILURES else "none -- all checks passed")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
