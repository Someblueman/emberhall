"""Fixed-size necessary equations for arbitrary holes; not a homometry solver.

Only standard-library integer arithmetic. See LONG_FRONTIER_INFINITE.md.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from published_cases import check_pair, validate_lengths, validate_vertices


def distance(u, v):
    return abs(u[1] - v[1]) if u[0] == v[0] else u[1] + v[1]


def shell_terms(lengths, vertex, holes):
    """(Exponent, coefficient, slope) as the vertex advances by g depths.

    Slope measures exponent change divided by g; it is constant inside
    each hole-cut interval. The centre does not advance.
    """
    arm, depth = vertex
    terms = []
    if arm == 0:
        terms.append((0, 1, 0))
        for length in lengths:
            terms.append((length, -1, 0))
    else:
        terms.extend([(depth, 1, 1), (lengths[arm - 1] - depth, -1, -1)])
        for other, length in enumerate(lengths, 1):
            if other != arm:
                terms.append((depth + length, -1, 1))
    for hole in holes:
        delta = distance(vertex, hole)
        slope = 0 if arm == 0 else (-1 if arm == hole[0] and depth < hole[1] else 1)
        terms.extend([(delta - 1, -1, slope), (delta, 1, slope)])
    return terms


def column(lengths, vertex, holes, modulus):
    """Coefficients of balance and the normalized shell modulo z^g-1."""
    result = [1] + [0] * modulus
    for power, value, _ in shell_terms(lengths, vertex, holes):
        result[1 + power % modulus] += value
    return result


def compressed_system(lengths, holes=(), modulus=8):
    """At most 1+g*(3+|H|) cells, independent of arm lengths.

    A cell is a depth residue within an arm interval cut at each omitted
    vertex. Its integer variable is a signed count, not an individual sign.
    """
    lengths = validate_lengths(lengths)
    holes = validate_vertices(lengths, holes)
    if type(modulus) is not int or not 2 <= modulus <= 256:
        raise ValueError("modulus must be an integer from 2 through 256")
    if len(holes) > 2:
        raise ValueError("this reduction accepts at most two omitted vertices")
    if (1 + sum(lengths) - len(holes)) % 2:
        raise ValueError("the retained order must be even")
    cells = []

    def append(arm, lo, hi, residue, first, count):
        moment_constant, moment_linear = [0]*modulus, [0]*modulus
        for power, value, slope in shell_terms(lengths, (arm, first), holes):
            quotient, remainder = divmod(power, modulus)
            moment_constant[remainder] += value * quotient
            moment_linear[remainder] += value * slope
        cells.append({"arm": arm, "lo": lo, "hi": hi, "residue": residue,
                      "first": first, "count": count,
                      "column": column(lengths, (arm, first), holes, modulus),
                      "moment_constant": moment_constant, "moment_linear": moment_linear})

    if (0, 0) not in holes:
        append(0, 0, 0, 0, 0, 1)
    for arm, length in enumerate(lengths, 1):
        cuts = [0] + sorted(d for i, d in holes if i == arm) + [length + 1]
        for left, right in zip(cuts, cuts[1:]):
            lo, hi = left + 1, right - 1
            for residue in range(modulus):
                first = lo + (residue - lo) % modulus
                if first <= hi:
                    append(arm, lo, hi, residue, first,
                           (hi - first) // modulus + 1)
    return {"lengths": list(lengths), "holes": [list(h) for h in holes],
            "modulus": modulus, "cells": cells, "equations": modulus + 1,
            "retained": 1 + sum(lengths) - len(holes),
            "cell_bound": 1 + modulus * (3 + len(holes)),
            "status": "necessary_equations_only", "infinite_family_proved": False}


def verify_counts(system, counts):
    """Validate an aggregate witness by rebuilding, never trusting saved cells."""
    rebuilt = compressed_system(system["lengths"], system["holes"], system["modulus"])
    cells = rebuilt["cells"]
    if len(counts) != len(cells):
        raise ValueError("one signed count is required for each rebuilt cell")
    for cell, value in zip(cells, counts):
        if type(value) is not int or abs(value) > cell["count"] or (
                value - cell["count"]) % 2:
            raise ValueError("signed count violates a cell's bounds or parity")
    residual = [sum(value * cell["column"][row]
                    for cell, value in zip(cells, counts))
                for row in range(rebuilt["equations"])]
    return {"aggregate_equations_hold": not any(residual), "residual": residual,
            "homometric_pair_proved": False}


def verify_moments(system, counts, moments):
    """Necessary double-root equations, with exact local attainability bounds.

    A moment is sum(j * sign_j) over the cell's positions j=0,...,n-1.
    Passing is not an exact-distance verdict.
    """
    checked = verify_counts(system, counts)
    rebuilt = compressed_system(system["lengths"], system["holes"], system["modulus"])
    if len(moments) != len(counts):
        raise ValueError("one signed first moment is required for each cell")
    for cell, value, moment in zip(rebuilt["cells"], counts, moments):
        n = cell["count"]
        plus = (n + value) // 2
        total = n*(n-1)//2
        low = plus*(plus-1) - total
        high = plus*(2*n-plus-1) - total
        if type(moment) is not int or not low <= moment <= high or (moment + total) % 2:
            raise ValueError("signed moment is not attainable with this cell count")
    residual = [sum(value*cell["moment_constant"][r] + moment*cell["moment_linear"][r]
                    for cell, value, moment in zip(rebuilt["cells"], counts, moments))
                for r in range(rebuilt["modulus"])]
    checked.update(first_moment_equations_hold=checked["aggregate_equations_hold"] and not any(residual),
                   moment_residual=residual)
    return checked


EVEN_COUNTS = (1, 0, 1, 1, 1, 0, 0, 0, 0, -1, -1, -1, -1, -1, 1, 1,
               1, 1, 1, 1, 0, 1, 1, -1, -1, -1, 0, 0, 0, -1, -1, -1, -1)


def even_barrier(t):
    """Exact modular-distance witness for every even t, without a search."""
    if type(t) is not int or t < 0 or t % 2:
        raise ValueError("the proved modular barrier requires even nonnegative t")
    system = compressed_system(tuple(n + 7560*t for n in (227, 67, 11)),
                               [(2, 4), (2, 10)])
    system["signed_counts"] = list(EVEN_COUNTS)
    system.update(verify_counts(system, EVEN_COUNTS))
    return system


def moment_obstruction(t):
    """Reject the displayed counts at t=0 mod 4, for every possible local order.

    This does not reject other signed counts, or other omitted vertices.
    """
    if type(t) is not int or t < 0 or t % 4:
        raise ValueError("the first-moment obstruction requires t divisible by four")
    system = even_barrier(t)
    weights = (0, -1, 1, 2, 2, 1, -1, 0)
    coefficients = [sum(w*v for w, v in zip(weights, cell["moment_linear"]))
                    for cell in system["cells"]]
    constant = sum(value*sum(w*v for w, v in zip(weights, cell["moment_constant"]))
                   for cell, value in zip(system["cells"], system["signed_counts"]))
    parity_term = sum(coefficient*(-cell["count"]*(cell["count"]-1)//2 % 2)
                      for coefficient, cell in zip(coefficients, system["cells"]))
    actual = (constant + parity_term) % 8
    valid = all(c % 4 == 0 for c in coefficients) and actual != 0
    return {"t": t, "weights": weights, "modulus": 8, "constant": constant,
            "parity_term": parity_term, "weighted_residual_modulus": actual,
            "fixed_counts_obstructed": valid, "arbitrary_counts_obstructed": False,
            "all_omissions_obstructed": False, "infinite_family_proved": False}


def lift_counts(system, counts, max_vertices=512):
    """Realize signed counts by choosing the earliest depths in each cell.

    This constructs a modular-distance pair only, not an exact-distance pair.
    The explicit bound prevents accidental expansion of a huge symbolic tree.
    """
    rebuilt = compressed_system(system["lengths"], system["holes"], system["modulus"])
    if 1 + sum(rebuilt["lengths"]) > max_vertices:
        raise ValueError("lift size limit exceeded; no exact-distance verdict")
    if not verify_counts(rebuilt, counts)["aggregate_equations_hold"]:
        raise ValueError("cannot lift a failed aggregate certificate")
    left, right = [], []
    for cell, value in zip(rebuilt["cells"], counts):
        plus = (cell["count"] + value) // 2
        for j in range(cell["count"]):
            vertex = (cell["arm"], cell["first"] + j * rebuilt["modulus"])
            (left if j < plus else right).append(vertex)
    return left, right


def small_counts(system, max_odd=32):
    """Try only zero on even cells and +/-1 on odd cells, by meet in the middle.

    Failure is inconclusive even for the compressed equations. This search
    finds small aggregate witnesses; it does not assign homometric sets.
    """
    cells = system["cells"]
    odd = [i for i, cell in enumerate(cells) if cell["count"] % 2]
    if len(odd) > max_odd:
        return None
    # Simultaneous negation permits fixing the first nonzero count to +1.
    fixed = odd[:1]
    rest = odd[1:]
    middle = len(rest) // 2

    def vectors(indices):
        width = system["equations"]
        value = [-sum(cells[i]["column"][r] for i in indices) for r in range(width)]
        previous = 0
        yield tuple(value), 0
        for word in range(1, 1 << len(indices)):
            gray = word ^ (word >> 1)
            changed = gray ^ previous
            bit = changed.bit_length() - 1
            step = 2 if gray & changed else -2
            for r, coefficient in enumerate(cells[indices[bit]]["column"]):
                value[r] += step * coefficient
            yield tuple(value), gray
            previous = gray

    left, right = rest[:middle], rest[middle:]
    lookup = {value: word for value, word in vectors(left)}
    base = cells[fixed[0]]["column"] if fixed else [0] * system["equations"]
    for value, right_word in vectors(right):
        wanted = tuple(-a - b for a, b in zip(base, value))
        if wanted in lookup:
            result = [0] * len(cells)
            for i in fixed:
                result[i] = 1
            for indices, word in [(left, lookup[wanted]), (right, right_word)]:
                for bit, index in enumerate(indices):
                    result[index] = 1 if word >> bit & 1 else -1
            return result
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("t", type=int, nargs="?", default=0)
    parser.add_argument("--omit", nargs=2, type=int, action="append", default=[])
    parser.add_argument("--modulus", type=int, default=8)
    parser.add_argument("--system", action="store_true", help="include exact integer columns")
    parser.add_argument("--small-counts", action="store_true")
    parser.add_argument("--barrier-even", action="store_true",
                        help="use the proved modular witness for even t")
    parser.add_argument("--lift-check", action="store_true",
                        help="check the canonical lift on the original tree (at most 512 vertices)")
    parser.add_argument("--first-moments", action="store_true",
                        help="test the earliest-plus lift's normalized shell at double roots")
    parser.add_argument("--moment-obstruction", action="store_true",
                        help="reject the displayed signed counts for every order, at t=0 mod 4")
    parser.add_argument("--verify", type=Path, help="verify a saved aggregate witness")
    args = parser.parse_args()
    try:
        if args.verify:
            saved = json.loads(args.verify.read_text())
            result = (verify_moments(saved, saved["signed_counts"], saved["signed_moments"])
                      if "signed_moments" in saved else verify_counts(saved, saved["signed_counts"]))
            print(json.dumps(result, sort_keys=True))
            return 0 if result.get("first_moment_equations_hold", result["aggregate_equations_hold"]) else 1
        if args.t < 0:
            raise ValueError("t must be nonnegative")
        if args.moment_obstruction:
            if args.omit or args.modulus != 8:
                raise ValueError("the moment obstruction fixes holes (2,4),(2,10) and modulus eight")
            print(json.dumps(moment_obstruction(args.t), sort_keys=True))
            return 0
        lengths = tuple(n + 7560 * args.t for n in (227, 67, 11))
        if args.barrier_even and (args.omit or args.modulus != 8):
            raise ValueError("the proved barrier fixes holes (2,4),(2,10) and modulus eight")
        result = (even_barrier(args.t) if args.barrier_even else
                  compressed_system(lengths, args.omit, args.modulus))
        if args.small_counts:
            counts = small_counts(result)
            result["signed_counts"] = counts
            result["small_counts_search"] = "found" if counts is not None else "inconclusive"
            if counts is not None:
                result.update(verify_counts(result, counts))
        if args.lift_check:
            if result.get("signed_counts") is None:
                raise ValueError("lift checking requires a signed-count witness")
            left, right = lift_counts(result, result["signed_counts"])
            checked = check_pair(lengths, left, right)
            result["lift_check"] = {key: checked[key] for key in
                                    ("homometric", "size", "target", "meets_target")}
            difference = checked["difference"]
            result["lift_check"]["first_mismatch"] = (
                [min(difference), difference[min(difference)]] if difference else None)
        if args.first_moments:
            if result.get("signed_counts") is None:
                raise ValueError("first moments require a signed-count witness")
            counts = result["signed_counts"]
            moments = []
            for cell, value in zip(result["cells"], counts):
                n = cell["count"]
                plus = (n + value)//2
                moments.append(plus*(plus-1) - n*(n-1)//2)
            result["signed_moments"] = moments
            result.update(verify_moments(result, counts, moments))
        result["cell_count"] = len(result["cells"])
        if not args.system:
            del result["cells"]
        print(json.dumps(result, sort_keys=True))
        return 0
    except (ValueError, TypeError, KeyError, OSError) as error:
        parser.exit(2, f"error: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
