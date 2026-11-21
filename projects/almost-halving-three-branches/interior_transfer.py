"""Path-transfer constructions and exact obstructions to fixed-colour extensions."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from math import gcd
from pathlib import Path

from paired_edge_five import check_pair
from unrestricted_odd_fields import INTERIOR_FAMILY, interior_pair


def _add(*polynomials):
    result = Counter()
    for polynomial in polynomials:
        for power, coefficient in polynomial.items():
            result[power] += coefficient
    return {power: coefficient for power, coefficient in result.items() if coefficient}


def _multiply(a, b):
    return _add(*({i+j: x*y for j, y in b.items()} for i, x in a.items()))


def _validate(arms, word):
    if (len(arms) != 2 or len(set(arms)) != 2
            or any(type(a) is not int or a not in (1, 2, 3) for a in arms)):
        raise ValueError("choose two distinct arms from 1, 2, 3")
    if not word or any(type(s) is not int or s not in (-1, 1) for s in word):
        raise ValueError("the appended word must contain signs +/-1")


def rooted_profiles(pair, arm):
    """Unsigned and signed profiles from an original tip, even if omitted."""
    root = pair["lengths"][arm-1]
    unsigned, signed = Counter(), Counter()
    for vertices, sign in ((pair["left"], 1), (pair["right"], -1)):
        for a, depth in vertices:
            distance = abs(root-depth) if a == arm else root+depth
            unsigned[distance] += 1
            signed[distance] += sign
    return dict(unsigned), {d: c for d, c in signed.items() if c}


def transfer_residual(pair, arms, word):
    """Return twice the new distance-profile difference, assuming a base pair.

    The old pair must be homometric. The two appended paths receive word and
    its negative; all old vertices and both original omissions stay put.
    """
    _validate(arms, word)
    if not check_pair(pair)["homometric"]:
        raise ValueError("the original pair must be homometric")
    u, f = rooted_profiles(pair, arms[0])
    v, g = rooted_profiles(pair, arms[1])
    X = {j: sign for j, sign in enumerate(word, 1)}
    G = {j: 1 for j in range(1, len(word)+1)}
    return _add(_multiply(X, _add(u, {d: -c for d, c in v.items()})),
                _multiply(G, _add(f, g)))


def append_words(pair, arms, words):
    if len(words) != 2 or len(words[0]) != len(words[1]):
        raise ValueError("append two words of the same positive length")
    for word in words:
        _validate(arms, word)
    lengths = list(pair["lengths"])
    left, right = list(pair["left"]), list(pair["right"])
    for arm, word in zip(arms, words):
        for j, sign in enumerate(word, 1):
            (left if sign == 1 else right).append((arm, lengths[arm-1]+j))
        lengths[arm-1] += len(word)
    return {"lengths": lengths, "left": left, "right": right}


def prove_tip_obstruction(tails=None):
    """Exclude every word length, for every k, using only 62 local shells."""
    if tails is None:
        tails = [row[2] for row in INTERIOR_FAMILY]
    if len(tails) != 3 or any(len(t) < 64 or set(t)-set("+-0") for t in tails):
        raise ValueError("require the three fixed tails through distance 63")
    suffixes = [[0 if c == "0" else 1 if c == "+" else -1
                 for c in tail[::-1][:64]] for tail in tails]
    records = []
    for other, first_bad in ((1, 62), (2, 6)):
        B = [a+b for a, b in zip(suffixes[0], suffixes[other])]
        forced = [sum(B[:j]) for j in range(1, first_bad+1)]
        if (any(s not in (-1, 1) for s in forced[:-1])
                or forced[-1] != (-3 if other == 1 else 3)):
            raise ArithmeticError("the stated first forbidden sign is not verified")
        short = []
        for h in range(1, first_bad):
            # A=-1 through degree 63, so these first h signs are forced.
            residual = [(d, sum(B[d-r] for r in range(1, min(h, d)+1))
                         - (forced[d-1] if d <= h else 0)) for d in range(1, 64)]
            mismatch = next(((d, c) for d, c in residual if c), None)
            if mismatch is None:
                raise ArithmeticError("a short word has no proved local contradiction")
            short.append((h, *mismatch))
        records.append({"arms": [1, other+1], "first_forbidden_position": first_bad,
                        "forced_sign": forced[-1], "short_lengths_excluded": len(short),
                        "maximum_witness_distance": max(d for _, d, _ in short)})
    B = [a+b for a, b in zip(suffixes[1], suffixes[2])]
    if B[:6] != [0, 0, 0, 0, 0, 2]:
        raise ArithmeticError("the middle/short distance-six contradiction failed")
    records.append({"arms": [2, 3], "distance": 6, "residual": 2})
    return {"proof": "PASS", "tip_pairs": records,
            "scope": "every k>=0 and every nonempty opposite-word tip extension",
            "long_middle_arbitrary_tail_words_excluded": True,
            "arbitrary_two_parameter_construction_excluded": False}


def path_transfer_pair(a, b, c):
    """A family obtained by extending a reflected path pair."""
    if any(type(v) is not int or v < 1 for v in (a, b, c)) or a <= b+1:
        raise ValueError("require positive a,b,c with a>b+1")
    r = a-b-1
    retained_c = c if (r+c) % 2 == 0 else c-1
    if b % r and (retained_c % r or ((retained_c//r) % 2 == 0 and b % 2)):
        raise ValueError("outside the proved path-transfer families")
    if b % r and (retained_c//r) % 2 == 0:
        g = gcd(r, b)  # Even here: r and b are both even.
        central_sign = lambda j: ((1 if ((j-1)//r) % 2 == 0 else -1)
                                  * (1 if (j-1) % g < g//2 else -1))
    else:
        midpoint = (r+retained_c)//2+1
        central_sign = lambda j: 1 if ((j-midpoint)//r) % 2 == 0 else -1
    signs = {}
    # The retained central path has coordinates 1 through c+r, with the
    # future branch centre at r and an omitted root at coordinate zero.
    for j in range(1, retained_c+r+1):
        vertex = (1, r-j) if j < r else (0, 0) if j == r else (3, j-r)
        signs[vertex] = central_sign(j)
    for j in range(1, b+1):
        sign = central_sign(r-(j-1) % r)
        signs[1, r+j] = sign
        signs[2, j] = -sign
    return {"lengths": (a, b, c),
            "left": [v for v, sign in signs.items() if sign == 1],
            "right": [v for v, sign in signs.items() if sign == -1],
            "omitted": [(1, r), (1, b+r+1)]+([] if retained_c == c else [(3, c)])}


def path_family_identity(orientation=-1):
    """Check the rooted reduction and XA+GH in independent formal variables.

    z,R,C,B represent z,z**r,z**retained_c,z**b. I is the first-block
    polynomial, J its negative reversal, and T its last sign. Word validity
    follows from the midpoint square wave proved in INTERIOR_TRANSFER.md.
    """
    one = {(0,)*7: 1}
    z, R, C, B, I, J, T = [{tuple(int(i == j) for i in range(7)): 1}
                          for j in range(7)]

    def negative(p):
        return {e: -c for e, c in p.items()}

    def product(*polynomials):
        result = one
        for p in polynomials:
            result = _add(*({tuple(a+b for a, b in zip(e, f)): c*d
                            for f, d in p.items()} for e, c in result.items()))
        return result

    root = _add(product(z, C), negative(one))
    one_minus_R = _add(one, negative(R))
    one_minus_B = _add(one, negative(B))
    A = product(root, one_minus_R)
    H = product(root, J)
    X = {e: orientation*c for e, c in product(z, one_minus_B, J).items()}
    G = product(z, one_minus_B)
    central_unsigned = product(z, _add(one, negative(product(R, C))))
    centre_unsigned = _add(one_minus_R, product(z, _add(one, negative(C))))
    # Substitute (1+R)P=I+z*C*R*J into R*H, and remove the repeated root.
    rooted_signed = _add(I, product(z, C, R, J), negative(product(R, J)),
                         negative(product(T, R)), negative(I), product(T, R))
    return {
        "unsigned_roots": _add(central_unsigned, negative(centre_unsigned), negative(A)),
        "signed_roots": _add(rooted_signed, negative(product(R, H))),
        "transfer": _add(product(X, A), product(G, H, one_minus_R)),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--example", action="store_true")
    mode.add_argument("--family", type=int, nargs=3, metavar=("A", "B", "C"))
    mode.add_argument("--prove-family", action="store_true")
    parser.add_argument("--witness", type=Path)
    parser.add_argument("--k", type=int, default=0)
    parser.add_argument("--arms", type=int, nargs=2, default=[1, 2])
    parser.add_argument("--word", default="+-")
    args = parser.parse_args()
    try:
        if args.witness and args.family is None:
            parser.error("--witness requires --family")
        if args.prove_family:
            if any(path_family_identity().values()):
                raise ArithmeticError("the path-transfer identity failed")
            result = {"proof": "PASS", "family": "T((m+1)r+1,mr,c); all positive r,m,c",
                      "universal_milestone_solved": False}
        elif args.family is not None:
            pair = path_transfer_pair(*args.family)
            result = check_pair(pair)
            if args.witness:
                args.witness.write_text(json.dumps(pair)+"\n")
        elif args.example:
            if set(args.word)-set("+-"):
                raise ValueError("--word contains only + and -")
            word = [1 if c == "+" else -1 for c in args.word]
            pair = interior_pair(args.k)
            residual = transfer_residual(pair, args.arms, word)
            result = {**check_pair(append_words(pair, args.arms, (word, [-s for s in word]))),
                      "transfer_residual_coefficients": len(residual)}
        else:
            result = prove_tip_obstruction()
    except (ValueError, TypeError) as error:
        parser.error(str(error))
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
