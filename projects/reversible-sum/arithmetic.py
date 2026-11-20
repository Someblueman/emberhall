"""Exact model of the printed pair arithmetic, not a double-double library."""

from dataclasses import dataclass
from fractions import Fraction

Pair = tuple[Fraction, Fraction]
ZERO: Pair = (Fraction(0), Fraction(0))
ONE: Pair = (Fraction(1), Fraction(0))


def power(exponent: int) -> Fraction:
    return Fraction(2**exponent) if exponent >= 0 else Fraction(1, 2**-exponent)


@dataclass(frozen=True)
class Binary:
    """p-bit round-to-nearest, ties-to-even, with gradual underflow."""

    precision: int
    emin: int
    emax: int

    def __post_init__(self) -> None:
        if self.precision < 2 or self.emin > self.emax:
            raise ValueError("invalid binary format")

    def round(self, value: Fraction) -> Fraction:
        value = Fraction(value)
        if not value:
            return value
        magnitude = abs(value)
        exponent = magnitude.numerator.bit_length() - magnitude.denominator.bit_length()
        if magnitude < power(exponent):
            exponent -= 1
        quantum = power(max(exponent, self.emin) - self.precision + 1)
        scaled = magnitude / quantum
        integer, remainder = divmod(scaled.numerator, scaled.denominator)
        if 2 * remainder > scaled.denominator or (
            2 * remainder == scaled.denominator and integer % 2
        ):
            integer += 1
        rounded = integer * quantum
        maximum = (2 - power(1 - self.precision)) * power(self.emax)
        if rounded > maximum:
            raise OverflowError("nonfinite rounded result")
        return rounded if value > 0 else -rounded

    def valid(self, pair: Pair) -> bool:
        high, low = pair
        return (
            self.round(high) == high
            and self.round(low) == low
            and abs(low) <= power(-self.precision) * abs(high)
        )

    def two_sum(self, left: Fraction, right: Fraction) -> Pair:
        high = self.round(left + right)
        low = self.round(left + right - high)
        if high + low != left + right:
            raise ArithmeticError("TwoSum residual is not exactly representable")
        return high, low

    def two_product(self, left: Fraction, right: Fraction) -> Pair:
        high = self.round(left * right)
        low = self.round(left * right - high)
        if high + low != left * right:
            raise ArithmeticError("TwoProd residual is not exactly representable")
        return high, low

    def add(self, left: Pair, right: Pair) -> Pair:
        """Section 2.4.1, preserving its printed parentheses and unused u."""
        h1, l1 = left
        h2, l2 = right
        s, e1 = self.two_sum(h1, h2)
        t, e2 = self.two_sum(l1, l2)
        _, e3 = self.two_sum(e1, t)
        errors = self.round(self.round(e1 + e2) + e3)
        return s, self.round(self.round(l1 + l2) + errors)

    def subtract(self, left: Pair, right: Pair) -> Pair:
        return self.add(left, (-right[0], -right[1]))

    def multiply(self, left: Pair, right: Pair) -> Pair:
        """Section 2.4.2; low-word additions evaluated left to right."""
        h1, l1 = left
        h2, l2 = right
        p, e1 = self.two_product(h1, h2)
        c1, e2 = self.two_product(h1, l2)
        c2, e3 = self.two_product(l1, h2)
        s, e4 = self.two_sum(c1, c2)
        t, e5 = self.two_sum(e1, e2)
        _, e6 = self.two_sum(e3, e4)
        v, e7 = self.two_sum(t, s)
        hp, e8 = self.two_sum(p, v)
        low = self.round(l1 * l2)
        for error in (e5, e6, e7, e8):
            low = self.round(low + error)
        return hp, low


def family(precision: int, index: int) -> tuple[Pair, Pair]:
    if precision < 3 or not 0 <= index < 2**precision:
        raise ValueError("family needs p >= 3 and 0 <= j < 2**p")
    return (index * power(-3 * precision - 4), Fraction(0)), (Fraction(1), power(-precision - 1))


def matrices(precision: int, index: int) -> tuple[list[list[Pair]], list[list[Pair]]]:
    small, addend = family(precision, index)
    return [[small, addend], [ZERO, ZERO]], [[ONE, ZERO], [ONE, ZERO]]


def matrix_trace(arithmetic: Binary, index: int) -> tuple[list[dict], list[list[Pair]]]:
    """Algorithm 4: record both words before/after all 16 accumulator steps."""
    a, b = matrices(arithmetic.precision, index)
    c = [[ZERO, ZERO], [ZERO, ZERO]]
    trace = []
    predecessors = {}
    for i in range(2):
        for j in range(2):
            acc = ZERO
            for t in range(2):
                product = arithmetic.multiply(a[i][t], b[t][j])
                predecessors[i, j, t] = acc
                after = arithmetic.add(acc, product)
                trace.append(dict(direction="forward", i=i, j=j, t=t,
                                  before=acc, product=product, after=after, expected=after))
                acc = after
            c[i][j] = acc
    z = [row.copy() for row in c]
    for i in reversed(range(2)):
        for j in reversed(range(2)):
            acc = z[i][j]
            for t in reversed(range(2)):
                product = arithmetic.multiply(a[i][t], b[t][j])
                after = arithmetic.subtract(acc, product)
                trace.append(dict(direction="reverse", i=i, j=j, t=t,
                                  before=acc, product=product, after=after,
                                  expected=predecessors[i, j, t]))
                acc = after
            z[i][j] = acc
    return trace, z
