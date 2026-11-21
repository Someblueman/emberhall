"""Full five-fold partitions for eight previously missing affine classes.

Standard library only. See PAIRED_EDGE_FIVE.md for the all-parameter proof.
"""
from __future__ import annotations

import argparse
import hashlib
from itertools import combinations
import json
from pathlib import Path

# Every block is repeated k times, followed by its tail. Signs start at
# depth one for coarse vertices, and at edge zero for X.
COARSE_BLOCKS = (
    "--++++---+---+---++++---+---+-",
    "++----+++-+++----++++---+---++",
    "++----+++-+++-+++----+++-+++-+",
)
COARSE_TAILS = ("--++++---+---+---++++---", "++----+++-+++----+++", "++----+++")
EDGE_BLOCKS = (
    "+++++++++++-++-+++++++++++-++-",
    "-+--+--+--+--+--------+--++--+",
    "+--+--+--+--+--+--+--+--+--+--",
)
EDGE_TAILS = ("+++++++++++-++-++-+++-++", "-+--+--+--+--+---+--", "+--+--+--")
TAIL_LENGTHS = (24, 20, 9)

# Sparse integer Laurent polynomials in z and V; V is independently formal.
Poly = dict[tuple[int, int], int]


def add(*polys: Poly) -> Poly:
    result: Poly = {}
    for poly in polys:
        for term, coefficient in poly.items():
            result[term] = result.get(term, 0) + coefficient
    return {term: coefficient for term, coefficient in result.items() if coefficient}


def scale(poly: Poly, coefficient: int) -> Poly:
    return {term: coefficient*value for term, value in poly.items() if coefficient*value}


def multiply(*polys: Poly) -> Poly:
    result = {(0, 0): 1}
    for poly in polys:
        terms: Poly = {}
        for (a, b), c in result.items():
            for (d, e), f in poly.items():
                term = a+d, b+e
                terms[term] = terms.get(term, 0) + c*f
        result = {term: coefficient for term, coefficient in terms.items() if coefficient}
    return result


def word_polynomial(word: str, start: int = 0, masked: bool = False) -> Poly:
    if any(s not in "+-" for s in word):
        raise ValueError("a sign word contains a character other than + or -")
    return {(i+start, 0): (1 if s == "+" else -1)*((1, -1, 1)[(i+start) % 3] if masked else 1)
            for i, s in enumerate(word)}


def proof_residuals(edge_blocks=EDGE_BLOCKS, edge_tails=EDGE_TAILS) -> dict[str, Poly]:
    """Check the coarse shell and both edge equations in independent z,V."""
    if tuple(map(len, edge_blocks)) != (30, 30, 30) or tuple(map(len, edge_tails)) != TAIL_LENGTHS:
        raise ValueError("wrong edge block or tail lengths")
    one, v, z30 = {(0, 0): 1}, {(0, 1): 1}, {(30, 0): 1}
    denominator = add(one, scale(z30, -1))
    endpoints = [{(n, 1): 1} for n in TAIL_LENGTHS]

    def numerators(blocks, tails, start=0, mask=False):
        return [add(multiply(word_polynomial(block, start, mask and i != 1),
                             add(one, scale(v, -1))),
                    multiply(v, denominator, word_polynomial(tail, start, mask and i != 1)))
                for i, (block, tail) in enumerate(zip(blocks, tails))]

    coarse = numerators(COARSE_BLOCKS, COARSE_TAILS, start=1)
    x = numerators(edge_blocks, edge_tails)
    reflected_y = numerators(edge_blocks, edge_tails, mask=True)
    shell = multiply(denominator, add(one, *(scale(a, -1) for a in endpoints)))
    first: Poly = {}
    reversed_second: Poly = {}
    for i in range(3):
        j, k = (j for j in range(3) if j != i)
        factor = add(one, scale(endpoints[j], -1), scale(endpoints[k], -1))
        star = {(-a, -b): c for (a, b), c in coarse[i].items()}
        shell = add(shell, multiply(coarse[i], factor), multiply(endpoints[i], z30, star))
        first = add(first, multiply(x[i], factor), scale(reflected_y[i], -1))
        reversed_second = add(reversed_second,
                              multiply(add(reflected_y[i], scale(x[i], -1)),
                                       endpoints[j], endpoints[k]),
                              scale(multiply(reflected_y[i], add(endpoints[j], endpoints[k])), -1))
    return {"coarse_shell": shell, "first_edge_equation": first,
            "reversed_second_edge_equation": reversed_second}


# A separate exact family refuting the inherited claim that every odd-arm
# edge row must have period three. Each row is prefix + block*k + suffix.
NONPERIODIC_PATTERNS = (
    ('+++++++++++-', '++++++++++++++++++++++++++++++', '+++++++++++++++++++++-++++++++++++++++++++'),
    ('-+--+--+', '--+--+---++-+++++-++-+++--+---', '--+--+---++-+++++-++-+++-++---------------'),
    ('+', '------------------------------', '----------------------------+--+------'),
)


def nonperiodic_rows(k: int):
    if type(k) is not int or k < 0:
        raise ValueError("k must be a nonnegative integer")
    x = [prefix+block*k+suffix for prefix, block, suffix in NONPERIODIC_PATTERNS]
    y = []
    for arm, word in enumerate(x):
        masked = [c if arm == 1 or (1, -1, 1)[j % 3] == 1 else ("-" if c == "+" else "+")
                  for j, c in enumerate(word)]
        y.append("".join(masked)[::-1])
    return x, y


def nonperiodic_residuals() -> tuple[Poly, Poly]:
    """Certify both edge equations for every counterexample parameter k."""
    one, v = {(0, 0): 1}, {(0, 1): 1}
    denominator = add(one, {(30, 0): -1})
    endpoints = [{(n, 1): 1} for n in (54, 50, 39)]
    numerators, masked = [], []
    for arm, (prefix, block, suffix) in enumerate(NONPERIODIC_PATTERNS):
        for is_masked, target in ((False, numerators), (arm != 1, masked)):
            target.append(add(
                multiply(denominator, word_polynomial(prefix, masked=is_masked)),
                multiply(add(one, scale(v, -1)), word_polynomial(block, len(prefix), is_masked)),
                multiply(v, denominator, word_polynomial(suffix, len(prefix), is_masked))))
    first, second = {}, {}
    for i in range(3):
        j, k = (j for j in range(3) if j != i)
        first = add(first, multiply(numerators[i], add(one, scale(endpoints[j], -1),
                                                      scale(endpoints[k], -1))), scale(masked[i], -1))
        second = add(second, multiply(add(masked[i], scale(numerators[i], -1)),
                                      endpoints[j], endpoints[k]),
                     scale(multiply(masked[i], add(endpoints[j], endpoints[k])), -1))
    return first, second


def parameter_k(t: int) -> int:
    if type(t) is not int or t < 0 or t % 15 != 9:
        raise ValueError("construction requires nonnegative t=9 mod 15; other cases are not ruled out")
    return (532*t-3)//15


def build_pair(k: int) -> dict:
    """Partition the five-fold prefix, omitting its two appended original tips."""
    if type(k) is not int or k < 0:
        raise ValueError("k must be a nonnegative integer")
    coarse_lengths = tuple(30*k+n for n in TAIL_LENGTHS)
    retained = tuple(5*n for n in coarse_lengths)
    lengths = retained[0]+1, retained[1]+1, retained[2]
    left, right = [(0, 0)], []
    for arm, (block, tail, edge_block, edge_tail) in enumerate(
            zip(COARSE_BLOCKS, COARSE_TAILS, EDGE_BLOCKS, EDGE_TAILS), 1):
        coarse, x = block*k+tail, edge_block*k+edge_tail
        mask = "+"*len(x) if arm == 2 else ("+-+"*((len(x)+2)//3))[:len(x)]
        reflected = "".join("+" if a == b else "-" for a, b in zip(x, mask))
        y = reflected[::-1]
        for edge, old in enumerate(coarse):
            for offset, sign in enumerate((x[edge], x[edge], y[edge], y[edge], old), 1):
                (left if sign == "+" else right).append((arm, 5*edge+offset))
    return {"lengths": lengths, "left": left, "right": right,
            "omitted": [(1, lengths[0]), (2, lengths[1])], "base_k": k}


def validate_pair(lengths, left, right):
    if len(lengths) != 3 or any(type(n) is not int or n <= 0 for n in lengths):
        raise ValueError("require three positive integer arm lengths")
    selections = []
    for vertices in (left, right):
        selected = set()
        for vertex in vertices:
            if not isinstance(vertex, (list, tuple)) or len(vertex) != 2:
                raise ValueError("a vertex must be [arm, depth]")
            arm, depth = vertex
            if type(arm) is not int or type(depth) is not int or not (
                    (arm, depth) == (0, 0) or 1 <= arm <= 3 and 1 <= depth <= lengths[arm-1]):
                raise ValueError("vertex outside the original tree")
            if (arm, depth) in selected:
                raise ValueError("duplicate vertex")
            selected.add((arm, depth))
        selections.append(selected)
    if selections[0] & selections[1]:
        raise ValueError("the two subsets overlap")
    return selections


def distance_profile(lengths, vertices) -> list[int]:
    """Exact original-tree counts using carry-free integer convolutions.

    Same-arm distances are differences of depths; cross-arm distances are
    sums. Omitted vertices remain in those paths. Each convolution digit is
    at most the longest arm, so the chosen base prevents all carries.
    """
    width = max(1, (max(lengths).bit_length()+7)//8)
    selected = [bytearray((n+1)*width) for n in lengths]
    reversed_selected = [bytearray((n+1)*width) for n in lengths]
    profile = [0] * (sum(sorted(lengths)[-2:])+1)
    centre = (0, 0) in vertices
    for arm, depth in vertices:
        if arm:
            selected[arm-1][depth*width] = 1
            reversed_selected[arm-1][(lengths[arm-1]-depth)*width] = 1
            if centre:
                profile[depth] += 1
    packed = [int.from_bytes(row, "little") for row in selected]
    for i, n in enumerate(lengths):
        product = packed[i] * int.from_bytes(reversed_selected[i], "little")
        digits = product.to_bytes((2*n+1)*width, "little")
        for distance in range(1, n+1):
            start = (n+distance)*width
            profile[distance] += int.from_bytes(digits[start:start+width], "little")
    for i, j in combinations(range(3), 2):
        limit = lengths[i]+lengths[j]
        digits = (packed[i]*packed[j]).to_bytes((limit+1)*width, "little")
        for distance in range(2, limit+1):
            start = distance*width
            profile[distance] += int.from_bytes(digits[start:start+width], "little")
    return profile


def check_pair(pair) -> dict:
    lengths, left, right = pair["lengths"], pair["left"], pair["right"]
    left, right = validate_pair(lengths, left, right)
    first, second = distance_profile(lengths, left), distance_profile(lengths, right)
    if sum(first) != len(left)*(len(left)-1)//2 or sum(second) != len(right)*(len(right)-1)//2:
        raise ArithmeticError("distance counter lost or duplicated a pair")
    equal = len(left) == len(right)
    homometric = equal and first == second
    return {"lengths": lengths, "size": len(left), "right_size": len(right),
            "target": (1+sum(lengths))//2-1, "homometric": homometric,
            "meets_target": homometric and len(left) >= (1+sum(lengths))//2-1,
            "left_distance_pairs": sum(first), "right_distance_pairs": sum(second),
            "profile_sha256": hashlib.sha256(json.dumps(first, separators=(",", ":")).encode()).hexdigest(),
            "mismatch_distance": next((d for d, (x, y) in enumerate(zip(first, second)) if x != y), None)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--prove", action="store_true")
    mode.add_argument("--check", type=Path, metavar="JSON")
    mode.add_argument("--base-k", type=int)
    parser.add_argument("t", type=int, nargs="?")
    parser.add_argument("--witness", type=Path, metavar="JSON")
    args = parser.parse_args()
    if args.prove:
        if args.t is not None or args.witness:
            parser.error("--prove takes no t or witness file")
        residuals = proof_residuals()
        if any(residuals.values()) or any(nonperiodic_residuals()):
            raise ArithmeticError("an exact polynomial identity failed")
        print("PASS: coarse shell and both edge identities; every k>=0, hence every t=9 mod15; "
              "nonperiodic counterexample identities verified")
        return 0
    if args.check and (args.t is not None or args.witness):
        parser.error("--check takes no t or witness file")
    if args.base_k is not None and args.t is not None:
        parser.error("choose t or --base-k")
    try:
        if args.check:
            pair = json.loads(args.check.read_text())
        else:
            if args.base_k is None and args.t is None:
                parser.error("give t, --base-k, --prove or --check")
            pair = build_pair(args.base_k if args.base_k is not None else parameter_k(args.t))
        result = check_pair(pair)
        if not args.check:
            result.update(base_k=pair["base_k"], omitted=pair["omitted"], affine_t=args.t)
        if args.witness:
            args.witness.write_text(json.dumps(pair, separators=(",", ":"))+"\n")
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.error(str(error))
    print(json.dumps(result, sort_keys=True))
    return 0 if result["homometric"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
