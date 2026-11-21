"""An obstruction to arbitrary paired edge fields; see MIXED_EDGE_SEVEN.md.

The proof and command use only Python's standard library. This excludes a
declared subdivision construction, not arbitrary homometric vertex pairs.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from itertools import permutations
import json
from math import gcd


def obstruction(lengths: tuple[int, int, int]) -> dict:
    """Apply the proved necessary conditions, without searching edge signs."""
    if (len(lengths) != 3 or any(type(n) is not int or n < 1 for n in lengths)):
        raise ValueError("require three positive integer edge lengths")
    a, b, c = lengths
    divisors = (gcd(a, b), gcd(a, c), gcd(b, c))
    hypotheses = (a > b > c and a % 2 == 1 and b % 4 == c % 4 == 2
                  and divisors == (1, 1, 2))
    branches = (b % (2 * (a - c)) == 0, c % (2 * (a - b)) == 0) if a > b > c else None
    return {
        "lengths": lengths, "pairwise_gcds": divisors,
        "hypotheses_hold": hypotheses,
        "constant_reflection_divisibilities": branches,
        "paired_edge_assignment_excluded": hypotheses and not any(branches),
        "arbitrary_vertex_pairs_excluded": False,
    }


def affine_obstruction(t: int) -> dict:
    if type(t) is not int or t < 0:
        raise ValueError("t must be a nonnegative integer")
    result = obstruction(tuple(n + 760 * t for n in (13, 10, 2)))
    target = 88 + 7980 * t
    return {**result, "t": t,
            "original_lengths": tuple(n + 5320 * t for n in (91, 71, 15)),
            "original_target": target,
            "retained_prefix": tuple(7 * n for n in result["lengths"]),
            "retained_prefix_upper_bound": (
                target - 1 if result["paired_edge_assignment_excluded"] else None),
            "in_previously_missing_classes": (
                t % 3 == 0 and t % 15 != 3 and t % 11 not in (1, 6, 9))}


def paired_residual(lengths: tuple[int, int, int], x, y) -> tuple[dict, dict]:
    """Return every coefficient of F_X-W_Y and F_Y-W_X, without rounding."""
    obstruction(lengths)  # Validate lengths, even outside the theorem's domain.
    for row in (x, y):
        if len(row) != 3 or any(len(word) != n for word, n in zip(row, lengths)):
            raise ValueError("one sign per edge is required in each of three arms")
        if any(type(s) is not int or s not in (-1, 1) for word in row for s in word):
            raise ValueError("edge signs must be integers -1 or 1")
    residuals = []
    for first, second in ((x, y), (y, x)):
        coefficients = defaultdict(int)
        for i, n in enumerate(lengths):
            for k, sign in enumerate(first[i]):
                coefficients[k] += sign
                for j, end in enumerate(lengths):
                    if i != j:
                        coefficients[k + end] -= sign
            for k, sign in enumerate(second[i]):
                coefficients[n - 1 - k] -= sign
        residuals.append({k: v for k, v in sorted(coefficients.items()) if v})
    return tuple(residuals)


# Sparse polynomials in independent A, B, C, z; used only for finite identities.
Poly = dict[tuple[int, int, int, int], int]


def _mon(a=0, b=0, c=0, z=0) -> Poly:
    return {(a, b, c, z): 1}


def _add(*polynomials: Poly) -> Poly:
    out = defaultdict(int)
    for polynomial in polynomials:
        for powers, value in polynomial.items():
            out[powers] += value
    return {p: v for p, v in out.items() if v}


def _scale(polynomial: Poly, scalar: int) -> Poly:
    return {p: v * scalar for p, v in polynomial.items() if v * scalar}


def _mul(*polynomials: Poly) -> Poly:
    out = _mon()
    for polynomial in polynomials:
        terms = defaultdict(int)
        for p, v in out.items():
            for q, w in polynomial.items():
                terms[tuple(a + b for a, b in zip(p, q))] += v * w
        out = {p: v for p, v in terms.items() if v}
    return out


def _minus_argument(polynomial: Poly) -> Poly:
    return {p: v * (-1) ** (p[0] + p[3]) for p, v in polynomial.items()}


def proof_residuals() -> dict[str, Poly]:
    """Exact eliminations used in the proof, before specializing any lengths."""
    one, A, B, C, z = _mon(), _mon(a=1), _mon(b=1), _mon(c=1), _mon(z=1)
    add, mul, neg = _add, _mul, lambda p: _scale(p, -1)
    minus = lambda p: add(one, neg(p))
    AB, AC, BC = mul(A, B), mul(A, C), mul(B, C)
    square_gap = add(mul(A, A), neg(BC))
    # beta=-1, alpha=+1. The other alpha is obtained by exchanging X and Y.
    matrix = [
        [add(one, neg(A), neg(C)), neg(one), add(one, neg(A), neg(B)), one],
        [neg(AC), add(AC, neg(A), neg(C)), neg(AB), add(neg(AB), A, B)],
        [neg(one), add(one, A, neg(C)), one, add(one, A, neg(B))],
        [add(neg(AC), A, neg(C)), AC, add(AB, neg(A), B), AB],
    ]
    determinant = {}
    for order in permutations(range(4)):
        inversions = sum(order[i] > order[j] for i in range(4) for j in range(i + 1, 4))
        determinant = add(determinant, _scale(mul(*(matrix[i][j]
                              for i, j in enumerate(order))), (-1) ** inversions))
    expected_det = _scale(mul(add(A, neg(one)), add(A, one), square_gap,
                              add(B, neg(one)), add(C, neg(one))), 4)
    D = mul(square_gap, add(mul(z, z), neg(one)))
    U = mul(square_gap, add(A, neg(one)), add(z, one))
    V = mul(square_gap, add(A, one), add(z, neg(one)))
    P = add(mul(add(B, neg(one)), add(mul(BC, add(z, neg(one))),
                                      neg(mul(A, A, add(z, one))))),
            _scale(mul(A, B, add(C, neg(one)), z), 2))
    R = add(neg(mul(add(C, neg(one)),
                    add(mul(A, A, add(z, one)), mul(BC, add(z, neg(one)))))),
            _scale(mul(A, C, add(B, neg(one))), 2))
    numerators = (P, _minus_argument(P), R, _minus_argument(R))
    constants = (add(_scale(one, 2), neg(B), neg(C)),
                 add(_scale(BC, -2), B, C))
    residuals = {"beta_minus_determinant": add(determinant, neg(expected_det))}
    for i, row in enumerate(matrix):
        residuals[f"beta_minus_equation_{i + 1}"] = add(
            *(mul(coefficient, numerator) for coefficient, numerator in zip(row, numerators)),
            mul(constants[i % 2], U if i < 2 else V))
    # The pole contradiction is N(1)=0 and N'(1)=2(c-b), independently of a.
    value = sum(P.values())
    derivatives = tuple(sum(p[i] * v for p, v in P.items()) for i in range(4))
    residuals["beta_minus_value_at_one"] = _scale(one, value)
    residuals["beta_minus_derivative"] = _scale(one, int(derivatives != (0, -2, 2, 0)))
    for alpha in (1, -1):
        eps = (-1, alpha, -alpha)
        ends = (A, B, C)
        differences = []
        for i, e in enumerate(eps):
            j, k = (q for q in range(3) if q != i)
            e1 = add(_scale(one, 1 - e), neg(ends[j]), neg(ends[k]))
            e2 = add(_scale(mul(ends[j], ends[k]), e - 1),
                     _scale(add(ends[j], ends[k]), -e))
            differences.append(add(e2, neg(e1)))
        expected = [_scale(mul(minus(B), minus(C)), -2), {}, {}]
        other = 2 if alpha == 1 else 1
        expected[other] = _scale(mul(minus(A), minus(B if alpha == 1 else C)), -2)
        for i in range(3):
            residuals[f"constant_reflection_{alpha}_{i}"] = add(differences[i], neg(expected[i]))
    numerator = add(AB, AC, BC, neg(A), neg(B), neg(C))
    complemented = {tuple(1 - p[i] if i < 3 else p[i] for i in range(4)): v
                    for p, v in numerator.items()}
    residuals["forcing_reciprocity"] = add(numerator, complemented)
    # Check the explicitly uncovered progression t=165*n by exact divisibility.
    slope = 760 * 165
    residuals["infinite_progression_arithmetic"] = _scale(one, int(
        slope % (3 * 8 * 11) != 0 or slope % 22 != 0 or slope % 6 != 0
        or tuple(gcd(x, y) for x, y in ((13, 10), (13, 2), (10, 2))) != (1, 1, 2)
        or 10 % 22 == 0 or 2 % 6 == 0))
    assert D  # Its specialized factors are nonzero for a>b>c>0.
    return residuals


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("t", type=int, nargs="?")
    parser.add_argument("--prove", action="store_true")
    args = parser.parse_args()
    if args.prove:
        if args.t is not None:
            parser.error("--prove takes no parameter")
        failed = [name for name, residual in proof_residuals().items() if residual]
        if failed:
            raise ArithmeticError("failed proof identities: " + ", ".join(failed))
        print("PASS: exact reflection eliminations and t=165*n obstruction arithmetic")
        return 0
    try:
        result = affine_obstruction(0 if args.t is None else args.t)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
