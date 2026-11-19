"""Exact certificates for the one-dimensional Dirichlet diffusion spectrum."""

from __future__ import annotations

import argparse
from fractions import Fraction
from functools import cache
from itertools import combinations
from math import gcd


def divide_monic(
    poly: tuple[int, ...], divisor: tuple[int, ...]
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Polynomial long division, constant coefficient first. Divisor is monic."""
    work = list(poly)
    degree = len(divisor) - 1
    quotient = [0] * max(0, len(work) - degree)
    for offset in reversed(range(len(quotient))):
        coefficient = quotient[offset] = work[offset + degree]
        if coefficient:
            for i, value in enumerate(divisor):
                work[offset + i] -= coefficient * value
    return tuple(quotient), tuple(work[:degree])


@cache
def cyclotomic(order: int) -> tuple[int, ...]:
    """Factor X**order - 1 using the cyclotomics of its proper divisors."""
    poly = (-1,) + (0,) * (order - 1) + (1,)
    for divisor in range(1, order):
        if order % divisor == 0:
            poly, remainder = divide_monic(poly, cyclotomic(divisor))
            if any(remainder):
                raise ArithmeticError("inexact cyclotomic factorization")
    return poly


def rate_sum(p: int, shift: Fraction, counts: dict[int, int]) -> tuple[Fraction, ...]:
    """Canonical coefficients of a normalized level sum in Q[X]/Phi_(2p)."""
    terms = sum(counts.values())
    poly = [0] * (2 * p)
    poly[0] = 2 * terms
    for j, copies in counts.items():
        if not 1 <= j < p or copies < 0:
            raise ValueError("invalid mode or multiplicity")
        poly[j] -= copies
        poly[2 * p - j] -= copies
    _, remainder = divide_monic(tuple(poly), cyclotomic(2 * p))
    result = [Fraction(c, 4) for c in remainder]
    result[0] -= terms * shift
    return tuple(result)


def rational_value(coefficients: tuple[Fraction, ...]) -> Fraction:
    if any(coefficients[1:]):
        raise ArithmeticError("expected a rational sum")
    return coefficients[0]


def check_equal(actual, expected, description: str) -> None:
    if actual != expected:
        raise ArithmeticError(f"{description}: got {actual}, expected {expected}")


def stable(p: int, r: Fraction) -> bool:
    """Sylvester test for the Dirichlet tridiagonal minus 4r times identity."""
    diagonal = 2 - 4 * r
    previous, current = 0, 1
    for _ in range(p - 1):
        previous, current = current, diagonal * current - previous
        if current <= 0:
            return False
    return True


def base_witness(p: int, r: Fraction) -> tuple[int, int, int] | None:
    """Return target mode, repeated mode, copies, using the theorem."""
    if r == 0 and p % 3 == 0:
        return 2 * p // 3, p // 3, 3
    if p == 3:
        ratio = (Fraction(3, 4) - r) / (Fraction(1, 4) - r)
        if ratio.denominator == 1:
            return 2, 1, ratio.numerator
    return None


def orbit_witness(p: int, r: Fraction) -> tuple[dict[int, int], dict[int, int]] | None:
    """Use the least odd prime divisor. Compute both sums from the spectrum."""
    q = next((d for d in range(3, p + 1, 2) if p % d == 0), None)
    if q is None:
        return None
    odd = {t * (p // q): 1 for t in range(1, q, 2)}
    even = {t * (p // q): 1 for t in range(2, q, 2)}
    a = rational_value(rate_sum(p, r, odd))
    b = rational_value(rate_sum(p, r, even))
    check_equal(b - a, Fraction(1, 2), "prime orbit gap")
    ratio = b / a
    return dict.fromkeys(odd, ratio.numerator), dict.fromkeys(even, ratio.denominator)


def conjugate_mean(p: int, j: int) -> Fraction:
    """Direct Galois average, independent of the totient/Möbius formula."""
    counts: dict[int, int] = {}
    for unit in range(1, 2 * p):
        if gcd(unit, 2 * p) == 1:
            power = unit * j % (2 * p)
            mode = min(power, 2 * p - power)
            counts[mode] = counts.get(mode, 0) + 1
    return rational_value(rate_sum(p, Fraction(0), counts)) / sum(counts.values())


def certificates() -> None:
    p, r = 3, Fraction(1, 12)
    levels = [
        {rational_value(rate_sum(p, r, {1: m - t, 2: t})) for t in range(m + 1)}
        for m in range(1, 5)
    ]
    check_equal(levels[0], {Fraction(1, 6), Fraction(2, 3)}, "two-point spectrum")
    for first, second in combinations(levels[:3], 2):
        check_equal(first & second, set(), "overlap before depth four")
    check_equal(levels[0] & levels[3], {Fraction(2, 3)}, "level-four intersection")
    check_equal(rate_sum(p, r, {1: 4}), rate_sum(p, r, {2: 1}), "four-copy witness")
    print("p=3, r=1/12: levels 1, 2, 3 disjoint; first overlap at 4: 4 b1 = b2 = 2/3")

    p, r = 5, Fraction(1, 50)
    check_equal(stable(p, r), True, "four-point strict stability")
    means = [conjugate_mean(p, j) - r for j in range(1, p)]
    least, greatest = min(means), max(means)
    check_equal(least > 0 and 2 * least > greatest, True, "four-point base exclusion")
    odd, even = orbit_witness(p, r)
    check_equal((odd, even), ({1: 121, 3: 121}, {2: 71, 4: 71}), "orbit counts")
    value = rational_value(rate_sum(p, r, odd))
    check_equal(rate_sum(p, r, even), rate_sum(p, r, odd), "different-level equality")
    check_equal(value, Fraction(8591, 100), "normalized eigenvalue")
    print(f"p=5, r=1/50: base nonresonant; levels 142 and 242 share {value}")
    print(f"  smallest two-term trace {2 * least} exceeds largest base trace {greatest}")
    print("  71 copies each of modes 2 and 4 = 121 copies each of modes 1 and 3")

    # sqrt(5) = 1 + 2*(X^2 + X^-2) at X = exp(pi*i/5).
    # Thus 12r = 2 - 3*(X^2 + X^-2). Reduce this independently of the rates.
    _, numerator = divide_monic((2, 0, -3, 0, 0, 0, 0, 0, -3), cyclotomic(10))
    irrational = tuple(Fraction(c, 12) for c in numerator)
    check_equal(any(irrational[1:]), True, "nonrational control")
    for j, expected in ((1, Fraction(1, 12)), (2, Fraction(1, 3))):
        s = rate_sum(p, Fraction(0), {j: 1})
        shifted = tuple(c - d for c, d in zip(s, irrational))
        check_equal(rational_value(shifted), expected, "irrational control rate")
    check_equal(stable(5, Fraction(1, 12)), True, "s1 > 1/12 makes control positive")
    print("p=5, r=(7-3 sqrt(5))/24: 4 b1 = b2 = 1/3, with b1 = 1/12")

    # At p=4, X + X^-1 = sqrt(2). Independently reduce 6r = 3 - 2 sqrt(2).
    _, shift_numerator = divide_monic((3, -2, 0, 0, 0, 0, 0, -2), cyclotomic(8))
    _, root_two = divide_monic((0, 1, 0, 0, 0, 0, 0, 1), cyclotomic(8))
    for j, denominator in ((1, 12), (2, 3)):
        s = rate_sum(4, Fraction(0), {j: 1})
        shifted = tuple(c - Fraction(d, 6) for c, d in zip(s, shift_numerator))
        check_equal(shifted, tuple(Fraction(d, denominator) for d in root_two),
                    "irrational control on a power-of-two grid")
    print("p=4, r=(3-2 sqrt(2))/6: levels 1 and 4 share sqrt(2)/3")

    check_equal(stable(2, Fraction(1, 2)), False, "zero decay rate at endpoint")
    zero = rate_sum(2, Fraction(1, 2), {1: 1})
    check_equal(rational_value(zero), 0, "endpoint eigenvalue")
    check_equal(rate_sum(2, Fraction(1, 2), {1: 2}), zero, "endpoint overlap")
    print("p=2, r=1/2: strict stability fails; levels 1 and 2 share 0")

    count = 0
    for p in range(2, 33):
        for j in range(1, p):
            mean = conjugate_mean(p, j)
            low, high = (Fraction(1, 4), Fraction(3, 4))
            if p % 3:
                low, high = Fraction(3, 8), Fraction(5, 8)
            if (p & (p - 1)) == 0:
                low = high = Fraction(1, 2)
            check_equal(low <= mean <= high, True, f"trace bound for p={p}, j={j}")
            count += 1
    print(f"Direct conjugate averages: {count} modes on p=2..32 satisfy the proof bounds")


def classify(p: int, r: Fraction) -> None:
    if p < 2 or r < 0 or not stable(p, r):
        raise ValueError("requires p >= 2 and a rational shift 0 <= r < sin²(pi/(2p))")
    base = base_witness(p, r)
    if base:
        target, repeated, copies = base
        check_equal(rate_sum(p, r, {target: 1}), rate_sum(p, r, {repeated: copies}),
                    "base witness")
        print(f"Base resonance: b{target} = {copies} b{repeated}")
    else:
        print("Base nonresonant at every depth (trace theorem).")
    orbit = orbit_witness(p, r)
    if orbit is None:
        print("All distinct levels are disjoint (power-of-two trace theorem).")
    else:
        left, right = orbit
        lhs = rate_sum(p, r, left)
        check_equal(lhs, rate_sum(p, r, right), "level certificate")
        print(f"Levels {sum(left.values())} and {sum(right.values())} share {rational_value(lhs)}")
        print(f"Mode counts: {left} = {right}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("p", nargs="?", type=int, help="grid denominator (interior points + 1)")
    parser.add_argument("r", nargs="?", help="normalized rational shift, e.g. 1/50")
    args = parser.parse_args()
    if args.p is None:
        certificates()
    elif args.r is None:
        parser.error("supply both p and r, or neither for the recorded certificates")
    else:
        try:
            classify(args.p, Fraction(args.r))
        except (ValueError, ZeroDivisionError) as exc:
            parser.error(str(exc))


if __name__ == "__main__":
    main()
