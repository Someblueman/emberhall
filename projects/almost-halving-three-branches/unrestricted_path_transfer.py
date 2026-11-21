"""Exact admission boundary for all reflection-antisymmetric path transfers."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from math import gcd
from pathlib import Path

from published_cases import check_pair


def parameters(r: int, b: int, c: int) -> tuple[int, int]:
    if any(type(n) is not int or n < 1 for n in (r, b, c)):
        raise ValueError("r, b and the original short-arm length c must be positive integers")
    retained_c = c - (r + c) % 2
    return retained_c, r + retained_c


def old_admission(r: int, b: int, c: int) -> bool:
    """The completed anti-periodic template's domain, not a general tripod bound."""
    retained_c, _ = parameters(r, b, c)
    return b % r == 0 or (retained_c % r == 0
                         and (retained_c // r % 2 == 1 or b % 2 == 0))


def classify(r: int, b: int, c: int) -> dict:
    """Apply the complete classification proved by reflection and residue parity."""
    retained_c, length = parameters(r, b, c)
    rigid = gcd(b, r) == gcd(b, retained_c + 1) == 1
    admitted = old_admission(r, b, c)
    return {
        "lengths": [b + r + 1, b, c], "r": r, "b": b,
        "retained_c": retained_c, "central_length": length,
        "gcd_b_r": gcd(b, r), "gcd_b_cprime_plus_one": gcd(b, retained_c + 1),
        "gcd_r_cprime_plus_one": gcd(r, retained_c + 1),
        "constant_tails_proved_necessary": rigid,
        "status": "constructible" if admitted else "obstructed",
        "old_template_admitted": admitted,
        "scope": "reflection-antisymmetric central path and opposite b-vertex tails",
        "universal_tripod_obstruction": False,
    }


def _signs(word: str) -> list[int]:
    if not isinstance(word, str) or not word or set(word) - {"+", "-"}:
        raise ValueError("words must be nonempty strings containing only + and -")
    return [1 if char == "+" else -1 for char in word]


def rooted_polynomials(r: int, central: str) -> tuple[dict, dict]:
    """A=U_0-U_r and H=F_0+F_r, using the uncontracted path."""
    p = _signs(central)
    if type(r) is not int or not 1 <= r <= len(p):
        raise ValueError("attachment coordinate must lie on the central path")
    if len(p) % 2 or any(p[j] != -p[-1-j] for j in range(len(p))):
        raise ValueError("central word must be reflection-antisymmetric")
    a, h = Counter(), Counter()
    for j, sign in enumerate(p, 1):
        a[j] += 1
        a[abs(j-r)] -= 1
        h[j] += sign
        h[abs(j-r)] += sign
    return ({d: n for d, n in a.items() if n}, {d: n for d, n in h.items() if n})


def residual(r: int, central: str, tail: str) -> dict[int, int]:
    """Twice the full pair-distance difference after opposite tails are added."""
    a, h = rooted_polynomials(r, central)
    result = Counter()
    for j, sign in enumerate(_signs(tail), 1):
        for d, n in a.items():
            result[j+d] += sign*n
        for d, n in h.items():
            result[j+d] += n
    return {d: n for d, n in sorted(result.items()) if n}


def word_pair(r: int, b: int, c: int, central: str, tail: str) -> dict:
    """Check actual unrestricted words against all original-tree distances."""
    retained_c, length = parameters(r, b, c)
    p, x = _signs(central), _signs(tail)
    if len(p) != length or len(x) != b:
        raise ValueError("central and tail lengths must be r+cprime and b")
    transfer = residual(r, central, tail)
    left, right = [], []
    for j, sign in enumerate(p, 1):
        vertex = (1, r-j) if j < r else (0, 0) if j == r else (3, j-r)
        (left if sign == 1 else right).append(vertex)
    for j, sign in enumerate(x, 1):
        (left if sign == 1 else right).append((1, r+j))
        (right if sign == 1 else left).append((2, j))
    lengths = (b+r+1, b, c)
    checked = check_pair(lengths, left, right)
    if transfer != {d: 2*n for d, n in checked["difference"].items()}:
        raise ArithmeticError("transfer polynomial disagrees with original-tree distances")
    omitted = [(1, r), (1, b+r+1)] + ([(3, c)] if retained_c != c else [])
    return {**checked, "lengths": lengths, "left": left, "right": right,
            "omitted": omitted, "central": central, "tail": tail,
            "transfer_residual": transfer,
            "anti_periodic": all(p[j+r] == -p[j] for j in range(length-r))}


def construct_pair(r: int, b: int, c: int) -> dict:
    """Construct within the exact domain; retain the predecessor's sign rules."""
    retained_c, length = parameters(r, b, c)
    if not old_admission(r, b, c):
        raise ValueError("no reflection-antisymmetric path transfer exists for these lengths")
    if b % r and retained_c // r % 2 == 0:
        g = gcd(r, b)
        p = [(1 if (j//r) % 2 == 0 else -1)
             * (1 if j % g < g//2 else -1) for j in range(length)]
    else:
        midpoint = length//2+1
        p = [1 if ((j-midpoint)//r) % 2 == 0 else -1 for j in range(1, length+1)]
    central = "".join("+" if sign == 1 else "-" for sign in p)
    tail = "".join("+" if p[r-1-j % r] == 1 else "-" for j in range(b))
    result = word_pair(r, b, c, central, tail)
    if not result["homometric"] or result["size"] != b + length//2:
        raise ArithmeticError("path-transfer construction failed")
    return result


def reflection_transfer_identity(r: int, central: str, tail: str) -> dict[int, int]:
    """Check the Laurent elimination identity, even for nonhomometric words.

    (1-z)[z^(M+1)E + z^(M+b+2)E*] = z(z^(cprime+1)-1)K,
    where E=XA+GH and K=(1+z^r)(1-z^b)P+(1-z^r)(z^M X-Y).
    """
    p, x = _signs(central), _signs(tail)
    m, b = len(p), len(x)
    e = residual(r, central, tail)
    lhs, k = Counter(), Counter()
    for d, value in e.items():
        for power in (m+1+d, m+b+2-d):
            lhs[power] += value
            lhs[power+1] -= value
    for j, value in enumerate(p, 1):
        for shift, sign in ((0, 1), (b, -1), (r, 1), (b+r, -1)):
            k[j+shift] += sign*value
    for j, value in enumerate(x, 1):
        k[m+j] += value
        k[m+r+j] -= value
        k[b+1-j] -= value
        k[r+b+1-j] += value
    for d, value in k.items():
        lhs[d+m-r+2] -= value
        lhs[d+1] += value
    return {d: value for d, value in lhs.items() if value}


def constant_tail_identity(orientation: int = 1) -> dict[tuple[int, int, int], int]:
    """Clear R(1-z) in H + orientation*A, using R=z^r and V=z^M.

    The block word has (1+R)P=I(1-V), I=z(1-R)/(1-z).
    The rooted reduction gives R*H=(1+R)P+(R-1)(I-R).
    Thus the cleared expression is
    (1-R)[z(R-V)+R(1-z)+orientation*(zV-R)].
    """
    if type(orientation) is not int or orientation not in (-1, 1):
        raise ValueError("orientation must be +/-1")
    inner = [((1, 1, 0), 1), ((1, 0, 1), -1),
             ((0, 1, 0), 1), ((1, 1, 0), -1),
             ((1, 0, 1), orientation), ((0, 1, 0), -orientation)]
    result = Counter()
    for (z, r, v), value in inner:
        result[z, r, v] += value
        result[z, r+1, v] -= value
    return {power: n for power, n in result.items() if n}


def elimination_identity(reflection_sign: int = -1) -> dict:
    """Verify the denominator-cleared elimination in nine independent variables.

    R=z^r, C=z^cprime, B=z^b; P,I,J,X,Y are formal polynomials,
    J=I*, Y=z^(b+1)X*. Correct reflection is P*=-P/(zRC).
    """
    if type(reflection_sign) is not int or reflection_sign not in (-1, 1):
        raise ValueError("reflection sign must be +/-1")
    names = ("z", "R", "C", "B", "P", "I", "J", "X", "Y")

    def mon(coefficient=1, **powers):
        return {tuple(powers.get(name, 0) for name in names): coefficient}

    def add(*polynomials):
        result = Counter()
        for polynomial in polynomials:
            for powers, value in polynomial.items():
                result[powers] += value
        return {powers: value for powers, value in result.items() if value}

    def mul(*polynomials):
        result = mon()
        for polynomial in polynomials:
            product = Counter()
            for powers, value in result.items():
                for other, coefficient in polynomial.items():
                    product[tuple(a+b for a, b in zip(powers, other))] += value*coefficient
            result = {powers: value for powers, value in product.items() if value}
        return result

    a = mul(add(mon(z=1, C=1), mon(-1)), add(mon(), mon(-1, R=1)))
    g = add(mon(z=1), mon(-1, z=1, B=1))
    h = add(mon(P=1), mon(R=-1, P=1), mon(R=1, J=1), mon(-1, R=-1, I=1))
    pstar = mon(reflection_sign, z=-1, R=-1, C=-1, P=1)
    hstar = add(mul(add(mon(), mon(R=1)), pstar), mon(R=-1, I=1), mon(-1, R=1, J=1))
    e = add(mul(a, mon(X=1)), mul(g, h))
    estar = add(mul(a, mon(-1, z=-1, R=-1, C=-1, B=-1, Y=1)),
                mul(g, hstar, mon(z=-1, B=-1)))
    k = add(mul(add(mon(), mon(R=1)), add(mon(), mon(-1, B=1)), mon(P=1)),
            mul(add(mon(), mon(-1, R=1)), add(mon(R=1, C=1, X=1), mon(-1, Y=1))))
    return add(mul(mon(z=1, R=1, C=1), e), mul(mon(z=2, R=1, C=1, B=1), estar),
               mul(mon(-1, z=1), add(mon(z=1, C=1), mon(-1)), k))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("r", type=int, nargs="?")
    parser.add_argument("b", type=int, nargs="?")
    parser.add_argument("c", type=int, nargs="?")
    parser.add_argument("--prove", action="store_true")
    parser.add_argument("--central")
    parser.add_argument("--tail")
    parser.add_argument("--witness", type=Path)
    args = parser.parse_args()
    try:
        if args.prove:
            if any(value is not None for value in
                   (args.r, args.b, args.c, args.central, args.tail, args.witness)):
                raise ValueError("--prove takes no parameters or words")
            if (constant_tail_identity() or not constant_tail_identity(-1)
                    or elimination_identity() or not elimination_identity(1)):
                raise ArithmeticError("constant-tail identity or corruption control failed")
            print(json.dumps({"constant_tail_identity": "PASS",
                              "elimination_identity": "PASS",
                              "changed_sign_rejected": True,
                              "theorem": "exact unrestricted path-transfer admission boundary",
                              "scope": "proof in UNRESTRICTED_PATH_TRANSFER.md"}))
            return 0
        if any(value is None for value in (args.r, args.b, args.c)):
            raise ValueError("supply r, b and c")
        report = classify(args.r, args.b, args.c)
        if (args.central is None) != (args.tail is None):
            raise ValueError("supply both --central and --tail")
        pair = None
        if args.central is not None:
            pair = word_pair(args.r, args.b, args.c, args.central, args.tail)
        elif report["status"] == "constructible":
            pair = construct_pair(args.r, args.b, args.c)
        if args.witness is not None:
            if pair is None:
                raise ValueError("no witness available; supply words or choose a constructible case")
            args.witness.write_text(json.dumps(pair, sort_keys=True) + "\n")
        if pair is not None:
            report.update({k: pair[k] for k in ("homometric", "size", "target", "anti_periodic")})
            report["first_transfer_mismatch"] = next(iter(pair["transfer_residual"].items()), None)
        print(json.dumps(report, sort_keys=True))
        return 1 if pair is not None and not pair["homometric"] else 0
    except ValueError as error:
        parser.error(str(error))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
