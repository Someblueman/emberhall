"""Uniform bounded-stream theorem for even-b unit-short-arm two-row lifts.

The spectral/CRT proof is in SHORT_ARM_STRUCTURE.md. This self-contained
standard-library checker verifies the exact recurrence, explicit survivors,
algebraic identities, base case, and concrete invalid-sign witnesses.
"""
from __future__ import annotations

import argparse
from itertools import product
import json
import sys


def add(*polys):
    out = {}
    for p in polys:
        for k, v in p.items():
            out[k] = out.get(k, 0)+v
    return {k: v for k, v in out.items() if v}


def neg(p):
    return {k: -v for k, v in p.items()}


def mul(p, q):
    out = {}
    for i, x in p.items():
        for j, y in q.items():
            out[i+j] = out.get(i+j, 0)+x*y
    return {k: v for k, v in out.items() if v}


def validate(x, y, q):
    b = len(x)
    if b < 2 or b % 2 or len(y) != b or any(type(v) is not int or v not in (-1, 1) for v in (*x, *y, q)):
        raise ValueError("two equal even-length sign words and q=+/-1 are required")
    return b


def survivor_type(x, y, q):
    validate(x, y, q)
    if q == 1 and tuple(y) == tuple(x)[::-1] and x[0] == x[-1]:
        return "A"
    if q == -1 and all(v == -1 for v in x) and all(v == 1 for v in y):
        return "B"
    return None


def numerator(b, x, y, p, q):
    """Independent one-variable N0 from the explicit elimination formula."""
    z, R, B, one = {1: 1}, {b-1: 1}, {b: 1}, {0: 1}
    C = add(B, neg(R), neg(one))
    X = dict(enumerate(x))
    Ystar = {-k: v for k, v in enumerate(y)}
    return add(neg(mul(add(one, neg(z)),
                       add(mul(C, X), mul({2*b-2: 1}, Ystar)))),
               neg(mul(add(one, neg(B)), add({k: p*v for k, v in C.items()}, {0: q}))))


def coefficients(x, y, q, length):
    """Generate exact forced coefficients; no theorem membership is assumed."""
    b = validate(x, y, q)
    P = neg(mul(mul({0: 1, 1: -1}, {0: 1, b: -1}), {0: 1, b-1: 1}))
    nums = [numerator(b, x, y, 1, q), numerator(b, y, x, q, 1)]
    seq = [[], []]
    for k in range(length):
        for s, n in zip(seq, nums):
            s.append(-n.get(k, 0)+sum(c*s[k-j] for j, c in P.items() if 0 < j <= k))
    return seq


def explicit_stream(x, y, q, length):
    """All coefficients of the two proved infinite survivor classes."""
    b = validate(x, y, q)
    kind, L = survivor_type(x, y, q), b-1
    if kind == "B":
        left = [-1 if (k//L) % 2 == 0 else 1 for k in range(length)]
        return [left, [-v for v in left]]
    if kind == "A":
        out = []
        for word in (x, y):
            seq = []
            for k in range(length):
                block, pos = divmod(k, L)
                if k == 0:
                    seq.append(-word[0])
                elif pos == 0:
                    seq.append((-1)**block)
                else:
                    seq.append(-(-1)**block*word[pos])
            out.append(seq)
        return out
    raise ValueError("this boundary has no infinite sign continuation")


def classify(x, y, q):
    b = validate(x, y, q)
    kind = survivor_type(x, y, q)
    bound = 3*b*(b-1)+2*b+2
    seq = coefficients(x, y, q, bound)
    first = next(((k, i, s[k]) for k in range(bound)
                  for i, s in enumerate(seq) if s[k] not in (-1, 1)), None)
    if kind:
        if first or seq != explicit_stream(x, y, q, bound):
            raise ArithmeticError("explicit survivor and independent recurrence disagree")
    elif first is None:
        raise ArithmeticError("counterexample to the uniform structure theorem")
    return {"b": b, "type": kind, "infinite_valid": kind is not None,
            "first_invalid": list(first) if first else None,
            "period_from_index": (1 if kind == "A" else 0) if kind else None,
            "period": 2*(b-1) if kind else None}


def prove_identities():
    # Exact Laurent arithmetic in independent z,R,V,W.
    def m(z=0, r=0, v=0, w=0):
        return {(z, r, v, w): 1}
    def times(p, q):
        out = {}
        for i, x in p.items():
            for j, y in q.items():
                k = tuple(a+b for a, b in zip(i, j))
                out[k] = out.get(k, 0)+x*y
        return {k: v for k, v in out.items() if v}
    one, z, R, V = m(), m(1), m(r=1), m(v=1)
    B = times(z, R)
    C = add(B, neg(R), neg(one))
    omz, omB, opR = add(one, neg(z)), add(one, neg(B)), add(one, R)
    P = neg(times(times(omz, omB), opR))
    nA = add(neg(times(omz, times(add(C, R), V))), neg(times(omB, add(C, one))))
    resA = add(times(opR, nA), times(P, add(V, R)))
    nB = add(times(omB, add(C, neg(R))), neg(times(omB, add(C, neg(one)))))
    resB = add(nB, neg(times(omB, add(one, neg(R)))))
    corrupt = add(times(opR, nA), neg(times(P, add(V, R))))
    W = m(w=1)
    R2 = times(R, R)
    zm1 = add(z, neg(one))
    numerator_q1 = add(neg(V), times(R, add(times(zm1, V), W, neg(one))), times(z, R2))
    truncated = add(neg(V), times(R, add(W, neg(one))),
                    times(R2, add(neg(times(z, V)), times(zm1, W), one)))
    remainder = add(numerator_q1, neg(times(times(omB, opR), truncated)))
    prefix = {k: v for k, v in remainder.items() if k[1] < 3}
    if prefix:
        raise ArithmeticError("uniform local-coefficient identity failed")
    if resA or resB or not corrupt:
        raise ArithmeticError("formal survivor identities failed")
    count = 0
    for values in product((-1, 1), repeat=5):
        result = classify(values[:2], values[2:4], values[4])
        count += result["infinite_valid"]
    if count != 3:
        raise ArithmeticError("b=2 base case failed")
    return {"algebra": "PASS", "type_A_identity_terms": len(resA),
            "type_B_identity_terms": len(resB), "corrupt_identity_terms": len(corrupt),
            "local_coefficient_identity_terms": len(prefix),
            "base_b2_boundaries": 32, "base_b2_survivors": count,
            "theorem": "2^(b-1)+1 infinite valid boundaries for every even b>=2",
            "proof": "See the spectral and coprime-period argument in SHORT_ARM_STRUCTURE.md"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prove", action="store_true")
    group.add_argument("--classify", nargs=3, metavar=("X2", "Y2", "Q"))
    raw = list(sys.argv[1:] if argv is None else argv)
    # A valid sign word may be exactly "--". In this explicit mode its
    # three operands are literal data, including all-minus words.
    if len(raw) == 4 and raw[0] == "--classify":
        args = argparse.Namespace(prove=False, classify=raw[1:])
    else:
        args = parser.parse_args(raw)
    try:
        if args.prove:
            result = prove_identities()
        else:
            xs, ys, rawq = args.classify
            if set(xs+ys)-set("+-"):
                raise ValueError("words must contain only + and -")
            result = classify(tuple(1 if c == "+" else -1 for c in xs),
                              tuple(1 if c == "+" else -1 for c in ys), int(rawq))
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
