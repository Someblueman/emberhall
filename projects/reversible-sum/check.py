#!/usr/bin/env python3
"""Run the collision and complete matrix trace. No external packages or inputs."""

from fractions import Fraction

import native
from arithmetic import Binary, ONE, ZERO, family, matrices, matrix_trace, power


def word(value: Fraction) -> str:
    if not value:
        return "0"
    sign = "-" if value < 0 else ""
    value = abs(value)
    n, d = value.numerator, value.denominator
    if n == d == 1:
        return sign + "1"
    if n & (n - 1) == 0 and d & (d - 1) == 0:
        return f"{sign}2^{n.bit_length() - d.bit_length()}"
    return sign + str(value)


def pair_text(pair: tuple[Fraction, Fraction]) -> str:
    return "(" + ", ".join(map(word, pair)) + ")"


def check_family(arithmetic: Binary, indices: list[int] | range) -> int:
    p = arithmetic.precision
    for j in indices:
        small, addend = family(p, j)
        assert arithmetic.valid(small) and arithmetic.valid(addend), (p, j)
        assert arithmetic.add(small, addend) == addend, (p, j)
        assert arithmetic.multiply(small, ONE) == small, (p, j)
        assert arithmetic.multiply(addend, ONE) == addend, (p, j)
    return len(indices)


def check_matrix(arithmetic: Binary, index: int) -> list[dict]:
    trace, result = matrix_trace(arithmetic, index)
    small, _ = family(arithmetic.precision, index)
    assert result == [[(-small[0], Fraction(0)), ZERO], [ZERO, ZERO]]
    failures = [row for row in trace if row["after"] != row["expected"]]
    assert [(row["i"], row["j"], row["t"]) for row in failures] == (
        [(0, 0, 1), (0, 0, 0)] if index else []
    )
    # The actual retained matrices reproduce every saved forward predecessor.
    a, b = matrices(arithmetic.precision, index)
    for row in trace:
        if row["direction"] == "reverse":
            recovered = ZERO
            for t in range(row["t"]):
                recovered = arithmetic.add(
                    recovered, arithmetic.multiply(a[row["i"]][t], b[t][row["j"]])
                )
            assert recovered == row["expected"]
    return trace


def check_native(indices: list[int], trace: list[dict]) -> None:
    native.require_binary64()
    for j in indices:
        small, addend = family(53, j)
        assert native.exact(native.add(native.floating(small), native.floating(addend))) == addend
        for operand in (small, addend):
            assert native.exact(native.multiply(native.floating(operand), (1.0, 0.0))) == operand
    a, b = matrices(53, 1)
    native_a, native_b = ([[native.floating(pair) for pair in row] for row in matrix]
                          for matrix in (a, b))
    native_trace = native.matrix_trace(native_a, native_b)
    assert native_trace == [{key: value for key, value in row.items() if key != "expected"}
                            for row in trace]


def main() -> None:
    count = sum(check_family(Binary(p, -3 * p - 4, 2), range(2**p)) for p in range(3, 11))
    print(f"Exact model: all {count} family members checked for p=3..10.")
    arithmetic = Binary(53, -1022, 1023)
    indices = sorted({0, 1, 2**53 - 1, *(2**k for k in range(53)),
                      *(2**k - 1 for k in range(1, 54))})
    check_family(arithmetic, indices)
    print(f"Binary64 model: {len(indices)} boundary/power samples share (1, 2^-54).")
    trace = check_matrix(arithmetic, 1)
    check_matrix(arithmetic, 0)
    check_native(indices, trace)
    print("Native binary64: all sampled outputs, unit products and trace steps agree.")
    print("Algorithm 4: A=[[(2^-163,0),(1,2^-54)],[(0,0),(0,0)]]")
    print("             B=[[(1,0),(0,0)],[(1,0),(0,0)]]")
    print("Retained Cdd=[[(1,2^-54),(0,0)],[(0,0),(0,0)]], with A and B unchanged.")
    print("direction cell t | before | product | after | required after")
    for row in trace:
        values = " | ".join(pair_text(row[key]) for key in ("before", "product", "after", "expected"))
        print(f"{row['direction']:7} {row['i']},{row['j']} {row['t']} | {values}")
    print("Final Z[0,0]=(-2^-163,0); all other cells=(0,0).")
    print("Control j=0: every reversed word restored. Retained-input replay: all predecessors restored.")
    # Exactly p bits distinguish the 2**p members for this local inverse.
    for j in indices:
        small, addend = family(53, j)
        saved_index = f"{j:053b}"
        assert len(saved_index) == 53
        recovered = (int(saved_index, 2) * power(-163), Fraction(0))
        assert recovered == small and arithmetic.add(recovered, addend) == addend
    print("Distinguishing-state control: saved j recovers each sampled predecessor.")
    print("Universal claims require proof.md; sampling alone does not establish them.")


if __name__ == "__main__":
    main()
