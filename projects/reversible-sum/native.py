"""Separate binary64 execution using elementary error-free transforms."""

import sys
from fractions import Fraction


def require_binary64() -> None:
    if (sys.float_info.radix, sys.float_info.mant_dig, sys.float_info.min_exp,
            sys.float_info.max_exp) != (2, 53, -1021, 1024):
        raise RuntimeError("native comparison requires IEEE binary64")


def two_sum(a: float, b: float) -> tuple[float, float]:
    s = a + b
    v = s - a
    return s, (a - (s - v)) + (b - v)


def two_product(a: float, b: float) -> tuple[float, float]:
    # Dekker splitting; this experiment uses moderate finite exponents only.
    product = a * b
    ca, cb = 134217729.0 * a, 134217729.0 * b
    ah, bh = ca - (ca - a), cb - (cb - b)
    al, bl = a - ah, b - bh
    error = ((ah * bh - product) + ah * bl + al * bh) + al * bl
    return product, error


def add(left: tuple[float, float], right: tuple[float, float]) -> tuple[float, float]:
    h1, l1 = left
    h2, l2 = right
    s, e1 = two_sum(h1, h2)
    t, e2 = two_sum(l1, l2)
    _, e3 = two_sum(e1, t)
    return s, (l1 + l2) + ((e1 + e2) + e3)


def multiply(left: tuple[float, float], right: tuple[float, float]) -> tuple[float, float]:
    h1, l1 = left
    h2, l2 = right
    p, e1 = two_product(h1, h2)
    c1, e2 = two_product(h1, l2)
    c2, e3 = two_product(l1, h2)
    s, e4 = two_sum(c1, c2)
    t, e5 = two_sum(e1, e2)
    _, e6 = two_sum(e3, e4)
    v, e7 = two_sum(t, s)
    hp, e8 = two_sum(p, v)
    return hp, (((l1 * l2 + e5) + e6) + e7) + e8


def exact(pair: tuple[float, float]) -> tuple[Fraction, Fraction]:
    return tuple(Fraction.from_float(word) for word in pair)


def floating(pair: tuple[Fraction, Fraction]) -> tuple[float, float]:
    result = tuple(float(word) for word in pair)
    if exact(result) != pair:
        raise ValueError("native operand conversion lost information")
    return result


def matrix_trace(a: list[list[tuple[float, float]]],
                 b: list[list[tuple[float, float]]]) -> list[dict]:
    """Execute both sweeps independently, without oracle intermediate states."""
    zero = (0.0, 0.0)
    c = [[zero, zero], [zero, zero]]
    trace = []
    for i in range(2):
        for j in range(2):
            acc = zero
            for t in range(2):
                product = multiply(a[i][t], b[t][j])
                after = add(acc, product)
                trace.append(dict(direction="forward", i=i, j=j, t=t,
                                  before=exact(acc), product=exact(product), after=exact(after)))
                acc = after
            c[i][j] = acc
    for i in reversed(range(2)):
        for j in reversed(range(2)):
            acc = c[i][j]
            for t in reversed(range(2)):
                product = multiply(a[i][t], b[t][j])
                after = add(acc, (-product[0], -product[1]))
                trace.append(dict(direction="reverse", i=i, j=j, t=t,
                                  before=exact(acc), product=exact(product), after=exact(after)))
                acc = after
    return trace
