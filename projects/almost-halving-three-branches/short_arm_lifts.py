"""Exact two-row lift classifications for T(a,b,1), b in {2,4,6,8}, even a>b.

This classifies a subdivision template, not arbitrary homometric partitions.
Python standard library only. See SHORT_ARM_LIFTS.md for the proof.
"""
from __future__ import annotations

import argparse
from collections import Counter
from itertools import product
import json

from two_param_lifts import _l_add as add, _l_neg as neg, _l_mul as mul, _l_star as star


def mon(z=0, u=0, c=1):
    return {(z, u): c} if c else {}


def elimination(b, x, y, p, q):
    """Return P and low numerators of X1,Y1 with independent A=z^a.

    P X1 = N0 + A N1. P has constant term -1, so the first a
    coefficients through degree a-2 are forced by N0. The last
    coefficient additionally receives -(y[-1]+q) for X1 and
    -(x[-1]+p) for Y1.
    """
    one, z, A, B = mon(), mon(1), mon(u=1), mon(b)
    F = add(one, neg(z), neg(B))
    G = add(one, neg(z), neg(A))
    X = {(k, 0): v for k, v in enumerate(x)}
    Y = {(k, 0): v for k, v in enumerate(y)}

    def rhs(X, Y, p, q):
        return add(neg(mul(G, X)), mul(mon(b-1), star(Y)),
                   neg(mul(add(one, neg(A), neg(B)), mon(c=p))), mon(c=q))

    r1, r2 = rhs(X, Y, p, q), rhs(Y, X, q, p)
    P = mul(mon(b), add(mul(F, star(F)), neg(one)))

    def numerator(r1, r2):
        return add(mul(mon(b), mul(star(F), r1)),
                   mul(mon(b-1, 1), star(r2)))

    nums = [numerator(r1, r2), numerator(r2, r1)]
    if any(z < (-1 if u == 1 else 0) or u not in (0, 1) for n in nums for z, u in n):
        raise ArithmeticError("unexpected elimination support")
    return {z: c for (z, _), c in P.items()}, [
        {z: c for (z, u), c in n.items() if u == 0} for n in nums]


def period_bound_certificate(b):
    """Verify P divides (1-z^T)^2, T=b(b-1), by exact integer division."""
    if type(b) is not int or b < 2 or b % 2:
        raise ValueError("require even b>=2")
    T = b*(b-1)
    P = Counter()
    for i, ci in ((0, -1), (1, 1)):
        for j, cj in ((0, 1), (b, -1)):
            for k, ck in ((0, 1), (b-1, 1)):
                P[i+j+k] += ci*cj*ck
    P = {k: v for k, v in P.items() if v}
    remainder = {0: 1, T: -2, 2*T: 1}
    degree, quotient = max(P), {}
    while remainder and max(remainder) >= degree:
        shift = max(remainder)-degree
        coeff = remainder[max(remainder)]//P[degree]
        quotient[shift] = coeff
        for k, v in P.items():
            pos = k+shift
            remainder[pos] = remainder.get(pos, 0)-coeff*v
            if not remainder[pos]:
                del remainder[pos]
    if remainder:
        raise ArithmeticError("period annihilator division failed")
    return {"proof": "PASS", "period_multiple": T,
            "quotient_degree": max(quotient), "remainder_terms": 0,
            "stream_check_bound": 3*T+2*b+2}


def forced_stream(b, x, y, p=1, q=1):
    """Exact recurrence until first invalid sign or witnessed periodic state.

    A state is the last 2b coefficients of BOTH words. Once the low
    numerators vanish, equal states force identical infinite continuations.
    """
    P, nums = elimination(b, x, y, p, q)
    if P.get(0) != -1:
        raise ArithmeticError("elimination constant must be -1")
    seq, seen = [[], []], {}
    start = max(max(n, default=0) for n in nums) + 2*b
    # P divides (1-z^(b(b-1)))^2. Beyond the numerator each
    # residue subsequence is affine; three valid signs force zero slope.
    # The proved quadratic bound includes a full repeated 2b-word window.
    for k in range(3*b*(b-1)+2*b+2):
        for s, n in zip(seq, nums):
            s.append(-(n.get(k, 0) - sum(c*s[k-j] for j, c in P.items() if 0 < j <= k)))
        if any(s[-1] not in (-1, 1) for s in seq):
            return seq, {"kind": "invalid", "first": k}
        if k >= start:
            state = tuple(tuple(s[-2*b:]) for s in seq)
            if state in seen:
                end = seen[state]
                return seq, {"kind": "periodic", "start": end-2*b+1, "period": k-end}
            seen[state] = k
    raise ArithmeticError("finite-state bound exceeded")


def extend(seq, info, length):
    if len(seq) >= length:
        return seq[:length]
    if info["kind"] != "periodic":
        raise ValueError("invalid stream cannot be extended")
    start, period = info["start"], info["period"]
    return [seq[k] if k < len(seq) else seq[start+(k-start) % period] for k in range(length)]


def residuals(a, b, x1, y1, x2, y2, p, q):
    """Direct, uncleared E1/E2, with ordinary finite sign words."""
    A = [mon(a), mon(b), mon(1)]
    X = [{(k, 0): v for k, v in enumerate(w)} for w in (x1, x2, [p])]
    Y = [{(k, 0): v for k, v in enumerate(w)} for w in (y1, y2, [q])]
    return _residual_polys(A, X, Y, reflected_scale=None)


def _residual_polys(A, X, Y, reflected_scale):
    result = []
    for forward, reverse in ((X, Y), (Y, X)):
        out = {}
        for i in range(3):
            factor = add(mon(), *[neg(A[j]) for j in range(3) if j != i])
            out = add(out, mul(forward[i], factor),
                      mul(mon(-1 if reflected_scale is None else reflected_scale-1,
                              c=-1 if reflected_scale is None else 1),
                          mul(A[i], star(reverse[i]))))
        result.append(out)
    return result


def branches(b=4):
    # Fix X3=+1 by global sign. Every solution has exactly one representative.
    for values in product((-1, 1), repeat=2*b+1):
        x, y, q = values[:b], values[b:2*b], values[-1]
        seq, info = forced_stream(b, x, y, 1, q)
        yield x, y, q, seq, info


def _solve_branches(a, b, source):
    solutions = []
    for x, y, q, seq, info in source:
        if info["kind"] == "invalid" and info["first"] < a-1:
            continue
        long = [extend(s, info, a) for s in seq]
        long[0][-1] -= y[-1]+q
        long[1][-1] -= x[-1]+1
        if any(v not in (-1, 1) for word in long for v in word):
            continue
        if not any(residuals(a, b, *long, x, y, 1, q)):
            solutions.append({"X": [long[0], list(x), [1]], "Y": [long[1], list(y), [q]]})
    return solutions


def solve(a, b=4):
    if type(a) is not int or type(b) is not int or b < 2 or b > 8 or a <= b or a % 2 or b % 2:
        raise ValueError("require even a>b, with even b between 2 and 8")
    return _solve_branches(a, b, branches(b))


def symbolic_tail(a0, x, y, q, seq, info, b=4):
    """Clear 1-z^period for all a=a0+period*n at once using independent U=z^(6n)."""
    period = info["period"]
    D = add(mon(), mon(period, c=-1))
    long = []
    for s in seq:
        prefix = {(k, 0): v for k, v in enumerate(extend(s, info, a0))}
        block = {(k, 0): v for k, v in enumerate(extend(s, info, a0+period)[a0:])}
        long.append(add(mul(D, prefix), mul(mon(a0), mul(block, add(mon(), mon(u=1, c=-1))))))
    long[0] = add(long[0], mul(D, mon(a0-1, 1, -y[-1]-q)))
    long[1] = add(long[1], mul(D, mon(a0-1, 1, -x[-1]-1)))
    X = [long[0], mul(D, {(k, 0): v for k, v in enumerate(x)}), mul(D, mon())]
    Y = [long[1], mul(D, {(k, 0): v for k, v in enumerate(y)}), mul(D, mon(c=q))]
    return _residual_polys([mon(a0, 1), mon(b), mon(1)], X, Y, reflected_scale=period)


def cancellation_indices(poly, period):
    """All n>=0 for which R0(z)+z^(period*n) R1(z)=0, or None if all."""
    if not poly:
        return None
    if any(u not in (0, 1) for _, u in poly):
        raise ArithmeticError("tail residual is not affine in U")
    low = {z: c for (z, u), c in poly.items() if u == 0}
    high = {z: c for (z, u), c in poly.items() if u == 1}
    if not low or not high:
        return set()
    shift = min(low)-min(high)
    if shift < 0 or shift % period:
        return set()
    return {shift//period} if low == {z+shift: -c for z, c in high.items()} else set()


def prove_fixed_middle(b=4):
    """Exhaust boundary states, then certify every eventual length symbolically."""
    if b not in (2, 4, 6, 8):
        raise ValueError("proved middle lengths are 2,4,6,8")
    period_certificate = period_bound_certificate(b)
    counts, periodic, relevant_bad, latest_bad = Counter(), [], [], -1
    for x, y, q, seq, info in branches(b):
        counts[info["kind"]] += 1
        item = (x, y, q, seq, info)
        if info["kind"] == "invalid":
            latest_bad = max(latest_bad, info["first"])
            if info["first"] >= b+1:
                relevant_bad.append(item)
        else:
            periodic.append(item)
    period = 2*(b-1)
    if any(i["period"] != period for *_, i in periodic):
        raise ArithmeticError("unexpected branch period")
    threshold = max(latest_bad+2, max(i["start"] for *_, i in periodic)+1, b+2)
    threshold += threshold % 2
    tail_counts = {}
    for a0 in range(threshold, threshold+period, 2):
        universal = 0
        for args in periodic:
            x, y, q, streams, info = args
            # The final-coefficient correction is periodic in a too.
            # Certify the sign constraint, not only the linear equations.
            last_x, last_y = [extend(word, info, a0)[-1] for word in streams]
            if last_x-y[-1]-q not in (-1, 1) or last_y-x[-1]-1 not in (-1, 1):
                continue
            residual = symbolic_tail(a0, *args, b=b)
            allowed = [cancellation_indices(r, period) for r in residual]
            if all(v is None for v in allowed):
                universal += 1
            else:
                finite = [v for v in allowed if v is not None]
                if set.intersection(*finite):
                    raise ArithmeticError("unexpected exceptional tail length")
        tail_counts[a0 % period] = universal
    initial = {a: len(_solve_branches(a, b, relevant_bad+periodic))
               for a in range(b+2, threshold, 2)}
    expected = {
        2: (29, 3, 4, {4: 3}, "every even a>2"),
        4: (503, 9, 13, {6: 3, 8: 10, 12: 1}, "a divisible by 6, or a=8"),
        6: (8159, 33, 30, {8: 2, 10: 1, 12: 40, 20: 1, 30: 1},
            "a divisible by 10, or a=8 or a=12"),
    }
    expected[8] = (130943, 129, 56,
                   {10: 2, 12: 10, 14: 1, 16: 160, 28: 1, 42: 1, 56: 1},
                   "a divisible by 14, or a=10 or a=12 or a=16")
    invalid, cycles, bad, positive, criterion = expected[b]
    if (counts != {"invalid": invalid, "periodic": cycles} or latest_bad != bad
            or {a: n for a, n in initial.items() if n} != positive
            or tail_counts != {r: int(r == 0) for r in range(0, period, 2)}):
        raise ArithmeticError("classification changed")
    return {"proof": "PASS", "scope": f"two-row E1=E2=0 on T(a,{b},1), even a>{b}",
            "criterion": criterion, "boundary_choices_up_to_sign": 2**(2*b+1),
            "invalid": invalid, "latest_invalid_coefficient": bad,
            "stream_check_bound": period_certificate["stream_check_bound"],
            "periodic": cycles, "period": period, "tail_starts_at": threshold,
            "tail_solution_counts_up_to_sign": tail_counts, "initial_counts_up_to_sign": initial}


def prove_four_arm():
    return prove_fixed_middle(4)


def construct(a, g, summary=False, b=4):
    """Build an actual full partition from the classified two-row template."""
    from two_param_lifts import _apply_lift
    solutions = solve(a, b)
    if not solutions:
        raise ValueError("no two-row lift for this length; arbitrary partitions are not ruled out")
    solution = solutions[0]
    words = tuple(tuple("".join("+" if v == 1 else "-" for v in word)
                        for word in pair) for pair in zip(solution["X"], solution["Y"]))
    return _apply_lift((a, b, 1), words, g, summary)


def prove_uniform_family():
    """Exact independent-variable certificate for a=2k(b-1), even b."""
    one = {(0, 0, 0): 1}
    z, R, A = {(1, 0, 0): 1}, {(0, 1, 0): 1}, {(0, 0, 1): 1}
    B = mul(z, R)
    D = mul(add(one, neg(z)), add(one, R))
    N = [neg(mul(add(one, neg(R)), add(one, neg(A)))),
         neg(mul(add(one, neg(B)), add(one, R))), D]
    ends = [A, B, z]
    def residual(numerators):
        out = {}
        for i in range(3):
            factor = add(one, *[neg(ends[j]) for j in range(3) if j != i])
            out = add(out, mul(numerators[i], factor),
                      neg(mul(mul(ends[i], R), star(numerators[i]))))
        return out
    answer = residual(N)
    corrupt = residual([N[0], N[1], neg(N[2])])
    reflection = add(mul(B, star(D)), D)
    if answer or reflection or not corrupt:
        raise ArithmeticError("uniform family certificate failed")
    return {"proof": "PASS", "ring": "Z[z,z^-1,R,R^-1,A,A^-1]",
            "e1_terms": len(answer), "e2_terms": len(answer),
            "denominator_reflection_terms": len(reflection),
            "corrupt_short_word_terms": len(corrupt),
            "scope": "even b>=2, k>=1, a=2k(b-1)>b; every odd g>=3"}


def construct_uniform(b, k, g, summary=False):
    """Uniform construction for arbitrary even middle length, no enumeration."""
    from two_param_lifts import _apply_lift
    if type(b) is not int or b < 2 or b % 2 or type(k) is not int or k < 1:
        raise ValueError("require even b>=2 and integer k>=1")
    a = 2*k*(b-1)
    if a <= b:
        raise ValueError("require 2k(b-1)>b")
    X = (("-"*(b-1)+"+"*(b-1))*k, "-"*b, "+")
    Y = tuple("".join("-" if c == "+" else "+" for c in word) for word in X)
    return _apply_lift((a, b, 1), tuple(zip(X, Y)), g, summary)


def prove_double_family():
    """Independent z,B certificate for T(2b,b,1), every even b>=4."""
    one, z, B = mon(), mon(1), mon(u=1)
    D = add(one, neg(z))
    X = [{(0, 0): 1, (-1, 1): -2, (1, 1): 2, (0, 2): -1},
         add(neg(one), B), D]
    Y = [{(0, 0): 1, (1, 0): -2, (-2, 1): 2, (-1, 1): -2,
          (-2, 2): 2, (0, 2): -1},
         {(0, 0): -1, (1, 0): 2, (-2, 1): -2, (0, 1): 1}, D]
    ends = [mul(B, B), B, z]
    answer = _residual_polys(ends, X, Y, reflected_scale=1)
    corrupt = _residual_polys(ends, [X[0], X[1], neg(D)], Y, reflected_scale=1)
    if any(answer) or not any(corrupt):
        raise ArithmeticError("double family certificate failed")
    return {"proof": "PASS", "ring": "Z[z,z^-1,B,B^-1]",
            "e1_terms": len(answer[0]), "e2_terms": len(answer[1]),
            "corrupt_short_word_terms": sum(map(len, corrupt)),
            "scope": "every even b>=4 and every odd g>=3 on T(2bg,bg,g)"}


def construct_double(b, g, summary=False):
    from two_param_lifts import _apply_lift
    if type(b) is not int or b < 4 or b % 2:
        raise ValueError("require even b>=4")
    X = ("+"*(b-1)+"--"+"+"*(b-1), "-"*b, "+")
    Y = ("+"+"-"*(b-3)+"+"+"-"*(b-1)+"++", "-"+"+"*(b-3)+"--", "+")
    return _apply_lift((2*b, b, 1), tuple(zip(X, Y)), g, summary)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prove", action="store_true")
    group.add_argument("--solve", type=int, nargs=2, metavar=("A", "B"))
    group.add_argument("--uniform", type=int, nargs=3, metavar=("B", "K", "G"))
    group.add_argument("--prove-uniform", action="store_true")
    group.add_argument("--double", type=int, nargs=2, metavar=("B", "G"))
    group.add_argument("--prove-double", action="store_true")
    group.add_argument("--construct", type=int, nargs=2, metavar=("A", "G"))
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--middle", type=int, choices=(2,4,6,8), default=4)
    args = parser.parse_args()
    try:
        if args.prove_double:
            result = prove_double_family()
        elif args.double:
            result = construct_double(*args.double, summary=args.summary)
        elif args.prove_uniform:
            result = prove_uniform_family()
        elif args.uniform:
            result = construct_uniform(*args.uniform, summary=args.summary)
        elif args.prove:
            result = prove_fixed_middle(args.middle)
        elif args.construct:
            result = construct(*args.construct, summary=args.summary, b=args.middle)
        else:
            result = {"a": args.solve[0], "b": args.solve[1], "solutions": solve(*args.solve)}
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
