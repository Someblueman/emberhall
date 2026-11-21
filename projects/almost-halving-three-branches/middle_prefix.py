"""Full retained partitions for every odd b >= 3 and odd 1 <= d < b.

The signed-reflection path proof is in MIDDLE_PREFIX.md. Standard library only.
"""
from __future__ import annotations

import argparse
import json

from progression_partitions import validate
from published_cases import check_pair


def parameters(b: int, d: int) -> tuple[int, int, int]:
    validate(b, d)
    if b < 3 or b % 2 != 1 or d % 2 != 1:
        raise ValueError("require odd b >= 3 and odd 1 <= d < b")
    return b + d, b - 2, b - d


def parity_sign(q: int) -> int:
    return -1 if q % 2 else 1


def reflection_word(b: int, d: int) -> tuple[int, ...]:
    """Assign signs along the connected path of two signed reflections."""
    _, m, c = parameters(b, d)
    period = d + 2
    word = [0] * period
    word[0] = -1
    pending = [0]
    while pending:
        j = pending.pop()
        neighbours = (((m - j) % period, 1),
                      ((c - j) % period, parity_sign((c - j) // period)))
        for k, factor in neighbours:
            value = factor * word[j]
            if word[k] == 0:
                word[k] = value
                pending.append(k)
            elif word[k] != value:
                raise ArithmeticError("inconsistent signed reflection path")
    if 0 in word:
        raise ArithmeticError("reflection path is disconnected")
    return tuple(word)


def short_sign(p: int, period: int, word: tuple[int, ...]) -> int:
    quotient, residue = divmod(p, period)
    return -parity_sign(quotient) * word[residue]


def checked_witness(b: int, d: int, signs: dict) -> dict:
    retained = parameters(b, d)
    vertices = {(0, 0)} | {(i, p) for i, length in enumerate(retained, 1)
                           for p in range(1, length + 1)}
    if set(signs) != vertices or any(s not in (-1, 1) for s in signs.values()):
        raise ValueError("signs must colour every retained vertex exactly once")
    left = sorted(v for v, s in signs.items() if s == 1)
    right = sorted(v for v, s in signs.items() if s == -1)
    lengths = b + d, b, b - d
    result = check_pair(lengths, left, right)
    if not result["homometric"] or len(left) != (3 * b - 1) // 2:
        raise ValueError("retained signs are not a balanced homometric partition")
    return {**result, "lengths": lengths, "retained_lengths": retained,
            "left": left, "right": right, "omitted": [(2, b - 1), (2, b)]}


def construct(b: int, d: int) -> dict:
    """Construct and check the two-middle-tip witness, without search."""
    a, m, c = parameters(b, d)
    period = d + 2
    word = reflection_word(b, d)
    signs = {(0, 0): 1}
    signs.update({(1, p): word[p % period] for p in range(1, a + 1)})
    signs.update({(2, p): -word[p % period] for p in range(1, m + 1)})
    signs.update({(3, p): short_sign(p, period, word) for p in range(1, c + 1)})
    return {**checked_witness(b, d, signs), "period": period,
            "construction": "signed reflection path"}


def formal_identity() -> dict:
    """Expand Q = B*H_relation + (1-C)*period_relation in a free Laurent ring.

    K,B,C,P,V,Pstar,Vstar,H,R are nine independent symbols. No finite
    values of b or d, or samples of a sign word, enter this calculation.
    """
    def add(*polys):
        out = {}
        for poly in polys:
            for exponent, coefficient in poly.items():
                out[exponent] = out.get(exponent, 0) + coefficient
        return {e: c for e, c in out.items() if c}

    def neg(poly):
        return {e: -c for e, c in poly.items()}

    def mul(*polys):
        out = {(0,) * 9: 1}
        for poly in polys:
            product = {}
            for a, x in out.items():
                for b, y in poly.items():
                    e = tuple(i + j for i, j in zip(a, b))
                    product[e] = product.get(e, 0) + x * y
            out = {e: c for e, c in product.items() if c}
        return out

    one = {(0,) * 9: 1}
    symbols = [{tuple(int(i == j) for i in range(9)): 1} for j in range(9)]
    K, B, C, P, V, Pstar, Vstar, H, R = symbols
    K_inverse = {(-1,) + (0,) * 8: 1}
    A = mul(K, B)
    U = add(P, neg(mul(K, V)))
    Ustar = add(Pstar, neg(mul(K_inverse, Vstar)))
    # H=1+W and H=C*Hstar, so C*Wstar=H-C.
    Q = add(one, neg(A), neg(B), neg(C),
            mul(U, add(one, neg(B), neg(C))), neg(mul(A, Ustar)),
            mul(V, add(one, neg(A), neg(C))), neg(mul(B, Vstar)),
            mul(add(H, neg(one)), add(one, neg(A), neg(B))), neg(H), C)
    period_relation = add(P, mul(add(one, neg(K)), V), neg(mul(B, R)))
    H_relation = add(mul(add(one, neg(C)), R), neg(P),
                     neg(mul(K, Pstar)), neg(mul(add(one, K), H)))
    return add(Q, neg(mul(B, H_relation)),
               neg(mul(add(one, neg(C)), period_relation)))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("b", type=int, nargs="?")
    parser.add_argument("d", type=int, nargs="?")
    parser.add_argument("--prove", action="store_true")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()
    if args.prove:
        if args.b is not None or args.d is not None:
            parser.error("--prove takes no parameters")
        if formal_identity():
            raise ArithmeticError("nonzero universal Laurent residual")
        print("PASS: universal Laurent identity; signed-path existence proof in MIDDLE_PREFIX.md")
        return 0
    if args.b is None or args.d is None:
        parser.error("give b and d, or --prove")
    try:
        result = construct(args.b, args.d)
    except ValueError as error:
        parser.exit(2, str(error) + "\n")
    if args.summary:
        result = {k: v for k, v in result.items()
                  if k not in {"left", "right", "left_profile", "right_profile", "difference"}}
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
