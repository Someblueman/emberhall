#!/usr/bin/env python3
"""Exact algebra accompanying proof.md; Python 3.10+, standard library only.

Sparse Laurent polynomials over Q allow the scaling factors b^-1 and c^-1.
All exponents in the Dulac certificate itself are nonnegative. This checks
identities, not the topological or differential-equation arguments in the proof.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import sys


NAMES = ("u", "v", "alpha", "m", "a", "b", "c")
ZERO_POWER = (0,) * len(NAMES)


class Poly:
    """A small exact expression type, with no parser or external CAS."""

    def __init__(self, terms: dict[tuple[int, ...], Fraction]):
        self.terms = {p: Fraction(c) for p, c in terms.items() if c}

    @staticmethod
    def constant(value: int | Fraction) -> Poly:
        if not isinstance(value, (int, Fraction)):
            raise TypeError("coefficients must be integers or Fractions")
        return Poly({ZERO_POWER: Fraction(value)})

    @staticmethod
    def variable(name: str, exponent: int = 1) -> Poly:
        powers = list(ZERO_POWER)
        powers[NAMES.index(name)] = exponent
        return Poly({tuple(powers): Fraction(1)})

    def __add__(self, other: Poly | int | Fraction) -> Poly:
        if not isinstance(other, Poly):
            other = Poly.constant(other)
        terms = self.terms.copy()
        for powers, coefficient in other.terms.items():
            terms[powers] = terms.get(powers, Fraction(0)) + coefficient
        return Poly(terms)

    __radd__ = __add__

    def __neg__(self) -> Poly:
        return Poly({p: -c for p, c in self.terms.items()})

    def __sub__(self, other: Poly | int | Fraction) -> Poly:
        return self + (-other)

    def __rsub__(self, other: int | Fraction) -> Poly:
        return -self + other

    def __mul__(self, other: Poly | int | Fraction) -> Poly:
        if not isinstance(other, Poly):
            other = Poly.constant(other)
        terms: dict[tuple[int, ...], Fraction] = {}
        for p, c in self.terms.items():
            for q, d in other.terms.items():
                powers = tuple(i + j for i, j in zip(p, q))
                terms[powers] = terms.get(powers, Fraction(0)) + c * d
        return Poly(terms)

    __rmul__ = __mul__

    def __pow__(self, exponent: int) -> Poly:
        if not isinstance(exponent, int) or exponent < 0:
            raise ValueError("expression powers must be nonnegative integers")
        result = Poly.constant(1)
        for _ in range(exponent):
            result = result * self
        return result

    def diff(self, name: str) -> Poly:
        index = NAMES.index(name)
        terms = {}
        for powers, coefficient in self.terms.items():
            if powers[index]:
                derived = list(powers)
                derived[index] -= 1
                terms[tuple(derived)] = coefficient * powers[index]
        return Poly(terms)

    def substitute(self, name: str, value: Poly | int | Fraction) -> Poly:
        """Substitute in a variable with nonnegative powers (u, v, alpha, m)."""
        if not isinstance(value, Poly):
            value = Poly.constant(value)
        index = NAMES.index(name)
        result = Poly.constant(0)
        for powers, coefficient in self.terms.items():
            remaining = list(powers)
            remaining[index] = 0
            result += Poly({tuple(remaining): coefficient}) * value ** powers[index]
        return result

    def evaluate(self, **values: int | Fraction) -> Fraction:
        result = Fraction(0)
        for powers, coefficient in self.terms.items():
            term = coefficient
            for name, exponent in zip(NAMES, powers):
                if exponent:
                    term *= Fraction(values[name]) ** exponent
            result += term
        return result


u, v, alpha, m, a, b, c = (Poly.variable(name) for name in NAMES)


def field(y_loss: int | Fraction = 1) -> tuple[Poly, Poly, Poly, Poly]:
    """The published m=2 field, or the explicitly stated m extension."""
    f = alpha * u**2 - (u - 1) * v
    g = m * alpha * u**2 - y_loss * u * v
    h = (u - 1) * (v + 2) - alpha * u**2
    p = u * (alpha * (u - 2)**2 + (m - 2) * alpha * u * (u - 1)
             + 2 * (u - 1))
    return f, g, h, p


def residual(f: Poly, g: Poly, h: Poly, p: Poly) -> Poly:
    return h * (f.diff("u") + g.diff("v")) - h.diff("u") * f - h.diff("v") * g + p


def require_zero(expression: Poly, label: str) -> None:
    if expression.terms:
        raise ValueError(f"{label}: nonzero residual ({len(expression.terms)} terms)")


def run_checks(altered_coefficient: bool = False) -> list[str]:
    passed = []

    def check(expression: Poly, label: str) -> None:
        require_zero(expression, label)
        passed.append(label)

    f, g, h, p = field()
    f2, g2, h2, p2 = (term.substitute("m", 2) for term in (f, g, h, p))

    # Reconstruct the original field from reaction vectors (1,2), (-1,-1), (1,0).
    # dx/dt = (c^2/b) du/ds for x=(c/b)u and s=ct, likewise for y.
    b_inv, c_inv = Poly.variable("b", -1), Poly.variable("c", -1)
    x, y = c * b_inv * u, c * b_inv * v
    original_x = a * x**2 - b * x * y + c * y
    original_y = 2 * a * x**2 - b * x * y
    factor = b * c_inv**2
    check(factor * original_x - f2.substitute("alpha", a * b_inv), "x scaling")
    check(factor * original_y - g2.substitute("alpha", a * b_inv), "y scaling")
    check(h2 - (2 * (u - 1) - f2), "H = 2(u-1) - f")
    check(f2.substitute("u", 1) - alpha, "u=1 points right")
    check(h2.substitute("u", 1) + alpha, "H at u=1")

    if altered_coefficient:
        _, bad_g, _, _ = field(y_loss=2)
        check(residual(f2, bad_g.substitute("m", 2), h2, p2), "altered m=2 Dulac identity")
    check(residual(f2, g2, h2, p2), "m=2 Dulac identity")
    check(p2 - (alpha * u * (u - 2)**2 + 2 * u * (u - 1)), "m=2 positive decomposition")
    check(f2.substitute("u", 2).substitute("v", 4 * alpha), "equilibrium f")
    check(g2.substitute("u", 2).substitute("v", 4 * alpha), "equilibrium g")
    check(h2.substitute("u", 2).substitute("v", 4 * alpha) - 2, "equilibrium H")

    # Check the extension only after the original system passes.
    check(residual(f, g, h, p), "symbolic m Dulac identity")
    check(p - p2 - (m - 2) * alpha * u**2 * (u - 1), "m>=2 positive extension")

    _, bad_g, _, _ = field(y_loss=2)
    try:
        require_zero(residual(f2, bad_g.substitute("m", 2), h2, p2), "negative control")
    except ValueError:
        passed.append("negative control rejected (y loss coefficient 1 -> 2)")
    else:
        raise ValueError("negative control unexpectedly passed")
    return passed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--altered-coefficient", action="store_true",
                        help="damage the y loss term; must exit 1")
    args = parser.parse_args()
    try:
        for label in run_checks(args.altered_coefficient):
            print(f"PASS {label}")
    except ValueError as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 1
    print("Exact algebra passed. Domain and orbit arguments are in proof.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
