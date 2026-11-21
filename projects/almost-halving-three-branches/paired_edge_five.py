"""A partial, unrestricted reduction for the five-fold prefix; not a solution."""
from __future__ import annotations

import argparse
from itertools import product
import json
from math import comb, gcd

from mixed_edge_seven import _add, _mon, _mul, _scale


def reflection_cases() -> list[dict]:
    """All sixteen necessary masks; three coefficients describe the odd arm."""
    cases = []
    for odd in product((-1, 1), repeat=3):
        if odd[0] * odd[1] * odd[2] != -1:
            continue
        for middle in product((-1, 1), repeat=2):
            cases.append({
                "odd": odd,
                "middle": middle,
                "long": tuple(odd[k % 3] * middle[k % 2] for k in range(6)),
            })
    return cases


def reduction(t: int) -> dict:
    if type(t) is not int or t < 0:
        raise ValueError("t must be a nonnegative integer")
    lengths = a, b, c = tuple(n + 1064 * t for n in (18, 14, 3))
    divisors = (gcd(a, c), gcd(b, c), gcd(a, b))
    domain = (t % 3 == 0 and t % 15 != 3 and t % 11 not in (1, 6, 9))
    if not domain:
        raise ValueError("this reduction is recorded only for the 32 missing classes")
    if divisors != (3, 1, 2) or (a % 6, b % 6, c % 6) != (0, 2, 3):
        raise ArithmeticError("the stated gcd and parity hypotheses failed")
    cases = reflection_cases()
    remaining = [case for case in cases if case["odd"] != (-1, -1, -1)]
    # The four discarded masks are excluded by proved necessary conditions.
    if a % 22 == 0 or b % 30 == 0:
        raise ArithmeticError("a discarded constant mask satisfies its divisibility")
    return {
        "t": t, "lengths": lengths, "pairwise_gcds": divisors,
        "odd_arm_forced_period": 3,
        "necessary_reflection_masks": len(cases),
        "eliminated_reflection_masks": 4,
        "remaining_reflection_masks": remaining,
        "odd_words_up_to_global_negation": [(1, x, y) for x, y in product((-1, 1), repeat=2)],
        "remaining_mask_word_combinations": 48,
        "paired_edge_assignment_excluded": False,
        "status": "partial reduction; 48 cases remain unresolved",
    }


def observed_mask(x, y) -> dict:
    """Check a supplied pair's pointwise reversal signs against the mask list."""
    if len(x) != 3 or len(y) != 3:
        raise ValueError("require three arms in each row")
    words = []
    for first, second in zip(x, y):
        if len(first) != len(second) or not first:
            raise ValueError("paired arms must have equal positive lengths")
        if any(type(s) is not int or s not in (-1, 1) for s in (*first, *second)):
            raise ValueError("edge signs must be -1 or 1")
        words.append(tuple(a * b for a, b in zip(first, reversed(second))))
    for case in reflection_cases():
        patterns = (case["long"], case["middle"], case["odd"])
        if all(all(s == pattern[k % len(pattern)] for k, s in enumerate(word))
               for word, pattern in zip(words, patterns)):
            return case
    raise ValueError("pair does not obey the necessary reflection masks")


def alternating_taylor_certificate() -> bool:
    """Check the Cramer numerator's cubic term, before any odd field is fixed."""
    from itertools import permutations

    one, A, B, C = _mon(), _mon(a=1), _mon(b=1), _mon(c=1)
    neg = lambda p: _scale(p, -1)
    AB, AC, BC = _mul(A, B), _mul(A, C), _mul(B, C)
    K = _add(_scale(one, 2), neg(B), neg(C))
    J = _add(_scale(BC, -2), B, C)
    matrix = [
        [_add(one, neg(A), neg(C)), neg(one), _add(one, neg(A), neg(B)), one],
        [neg(AC), _add(AC, neg(A), neg(C)), neg(AB), _add(neg(AB), A, B)],
        [neg(one), _add(one, A, neg(C)), one, _add(one, A, neg(B))],
        [_add(neg(AC), A, neg(C)), AC, _add(AB, neg(A), B), AB],
    ]

    def determinant(rows):
        terms = []
        for order in permutations(range(4)):
            sign = (-1) ** sum(order[i] > order[j] for i in range(4)
                                for j in range(i + 1, 4))
            terms.append(_scale(_mul(*(rows[i][j] for i, j in enumerate(order))), sign))
        return _add(*terms)

    def cubic_taylor(polynomial):
        # Coefficients after A=1+x, B=1+y, C=1+z, through total degree three.
        result = {}
        for i, j, k in product(range(4), repeat=3):
            if i + j + k > 3:
                continue
            value = sum(coefficient * comb(p[0], i) * comb(p[1], j) * comb(p[2], k)
                        for p, coefficient in polynomial.items()
                        if p[0] >= i and p[1] >= j and p[2] >= k)
            if value:
                result[i, j, k] = value
        return result

    cramer = []
    for column in ((neg(K), neg(J), {}, {}), ({}, {}, neg(K), neg(J))):
        rows = [[column[i], *row[1:]] for i, row in enumerate(matrix)]
        cramer.append(cubic_taylor(determinant(rows)))
    return (not cubic_taylor(determinant(matrix))
            and cramer == [{(0, 1, 2): 8, (0, 2, 1): -8}, {}])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("t", type=int, nargs="?", default=0)
    parser.add_argument("--prove-partial", action="store_true")
    args = parser.parse_args()
    if args.prove_partial:
        if not alternating_taylor_certificate():
            raise ArithmeticError("alternating-reflection Taylor certificate failed")
        print("PASS: partial alternating-reflection certificate; 48 cases remain open")
        return 0
    try:
        result = reduction(args.t)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
