"""Exact distance-parity certificates and bounded exhaustive support completion.

No parity success is an existence certificate. See LONG_FRONTIER.md.
"""
from __future__ import annotations

import argparse
from itertools import combinations
import json
from pathlib import Path

from published_cases import check_pair, validate_lengths, validate_vertices


def penultimate_certificate(lengths, modulus=8, arms=(1, 2)):
    """Symbolic obstruction for two penultimate tips, for every admitted length."""
    lengths = validate_lengths(lengths)
    if type(modulus) is not int or modulus < 5:
        raise ValueError("modulus must be an integer at least five")
    if any(n < 3 or (n-3) % modulus for n in lengths):
        raise ValueError("each length must be three modulo the modulus")
    if (len(arms) != 2 or any(type(i) is not int or i not in (1, 2, 3) for i in arms)
            or arms[0] == arms[1]):
        raise ValueError("choose two distinct arms from 1, 2, 3")
    k = sum((n-3)//modulus for n in lengths)
    if modulus*k % 2:
        raise ValueError("the original tree must have even order")
    half = modulus*k//2 + 4
    edge_count = 6*k + 7 + modulus*k*(k+1)//2
    return {
        "lengths": lengths, "omitted": [(i, lengths[i-1]-1) for i in arms],
        "distance_residue": 2, "modulus": modulus, "size": half,
        "degree_parity": (k+1) % 2, "selected_edges": edge_count,
        "required_edge_parity": ((k+1)*half) % 2,
        "actual_edge_parity": edge_count % 2,
        "status": "support_obstructed", "all_omissions_obstructed": False,
        "proof": "LONG_FRONTIER.md: penultimate-hole theorem",
    }


def support_rows(lengths, omitted=(), max_vertices=512):
    """Build integer degree bit planes and the exact parity system on a support."""
    lengths = validate_lengths(lengths)
    omitted = validate_vertices(lengths, omitted)
    if type(max_vertices) is not int or max_vertices < 1:
        raise ValueError("max_vertices must be positive")
    if 1+sum(lengths) > max_vertices:
        raise ValueError("size limit exceeded; no obstruction or existence verdict")
    holes = set(omitted)
    vertices = [v for v in [(0, 0)] + [(i, d) for i, n in enumerate(lengths, 1)
                                      for d in range(1, n+1)] if v not in holes]
    n = len(vertices)
    if n == 0 or n % 2:
        raise ValueError("retained support must have positive even size")
    degrees = {}
    edges = {}
    for i, j in combinations(range(n), 2):
        u, v = vertices[i], vertices[j]
        d = abs(u[1]-v[1]) if u[0] == v[0] else u[1]+v[1]
        if d not in degrees:
            degrees[d] = [0]*n
            edges[d] = 0
        degrees[d][i] += 1
        degrees[d][j] += 1
        edges[d] += 1
    rows = []
    for d in sorted(degrees):
        planes = {}
        for i, degree in enumerate(degrees[d]):
            for bit in range(degree.bit_length()):
                if degree >> bit & 1:
                    planes[bit] = planes.get(bit, 0) | (1 << i)
        rows.append((d, planes, edges[d]))
    return vertices, rows


def parity_basis(n, rows):
    """Return a basis or an independently checkable constant-degree certificate."""
    basis = {}
    equations = [((1 << n)-1, (n//2) % 2, 1)]
    equations.extend((planes.get(0, 0), edges % 2, 1 << j)
                     for j, (_, planes, edges) in enumerate(rows, 1))
    for a, b, history in equations:
        while a:
            pivot = a.bit_length()-1
            if pivot not in basis:
                basis[pivot] = (a, b, history)
                break
            old, rhs, used = basis[pivot]
            a, b, history = a ^ old, b ^ rhs, history ^ used
        if not a and b:
            return basis, {"distances": [d for j, (d, _, _) in enumerate(rows, 1)
                                          if history >> j & 1],
                           "degree_parity": history & 1}
    return basis, None


def verify_certificate(lengths, omitted, certificate, max_vertices=512):
    """Recount every selected original-tree edge; do not trust elimination history."""
    vertices, rows = support_rows(lengths, omitted, max_vertices)
    distances = certificate.get("distances")
    parity = certificate.get("degree_parity")
    if (not isinstance(distances, list) or len(distances) != len(set(distances))
            or any(type(d) is not int or d < 1 for d in distances)
            or type(parity) is not int or parity not in (0, 1)):
        raise ValueError("invalid distance-parity certificate")
    available = {d for d, _, _ in rows}
    if not set(distances) <= available:
        raise ValueError("certificate names an absent distance")
    degree_mask = 0
    edge_count = 0
    for d, planes, edges in rows:
        if d in distances:
            degree_mask ^= planes.get(0, 0)
            edge_count += edges
    uniform = degree_mask == (((1 << len(vertices))-1) if parity else 0)
    return {"valid": uniform and edge_count % 2 != parity*(len(vertices)//2) % 2,
            "selected_edges": edge_count, "uniform_degree_parity": uniform}


def complete_support(lengths, omitted=(), max_free=16, max_vertices=512):
    """Exhaust parity solutions, then check the exact integer shell equations."""
    lengths = validate_lengths(lengths)
    omitted = validate_vertices(lengths, omitted)
    if type(max_free) is not int or max_free < 0:
        raise ValueError("max_free must be nonnegative")
    order = 1+sum(lengths)
    retained = order-len(omitted)
    if order > max_vertices:
        raise ValueError("size limit exceeded; no obstruction or existence verdict")
    if retained == 0 or retained % 2:
        raise ValueError("retained support must have positive even size")
    even = 1+sum(n//2 for n in lengths)-sum(depth % 2 == 0 for _, depth in omitted)
    if even % 2 and even != retained//2:
        return {"lengths": lengths, "omitted": omitted, "size": retained//2,
                "status": "support_obstructed", "proof": "bipartition count",
                "even_depth_count": even, "all_omissions_obstructed": False}
    vertices, rows = support_rows(lengths, omitted, max_vertices)
    n = len(vertices)
    basis, certificate = parity_basis(n, rows)
    report = {"lengths": lengths, "omitted": omitted, "size": n//2,
              "independent_parity_rows": len(basis), "all_omissions_obstructed": False}
    if certificate is not None:
        verified = verify_certificate(lengths, omitted, certificate, max_vertices)
        if not verified["valid"]:
            raise ArithmeticError("generated parity certificate failed verification")
        report.update(status="support_obstructed", certificate=certificate,
                      certificate_check=verified)
        return report
    # Complementation preserves every equation: fix the first vertex outside A.
    a = 1
    while a:
        p = a.bit_length()-1
        if p not in basis:
            basis[p] = (a, 0, 0)
            break
        a ^= basis[p][0]
    free = [i for i in range(n) if i not in basis]
    report["free_bits_after_complement"] = len(free)
    if len(free) > max_free:
        report.update(status="inconclusive", reason="parity nullity exceeds max_free")
        return report
    ordered = sorted(basis.items())

    def recover(word, homogeneous=False):
        for pivot, (row, rhs, _) in ordered:
            if (row & word).bit_count() % 2 ^ (0 if homogeneous else rhs):
                word |= 1 << pivot
        return word

    word = recover(0)
    kernel = [recover(1 << bit, True) for bit in free]
    last_gray = 0
    balanced = 0
    for count in range(1 << len(free)):
        gray = count ^ (count >> 1)
        changed = gray ^ last_gray
        if changed:
            word ^= kernel[changed.bit_length()-1]
        last_gray = gray
        if word.bit_count() != n//2:
            continue
        balanced += 1
        if all(sum((word & mask).bit_count() << bit for bit, mask in planes.items())
               == edges for _, planes, edges in rows):
            left = [v for i, v in enumerate(vertices) if word >> i & 1]
            right = [v for i, v in enumerate(vertices) if not word >> i & 1]
            report.update(status="witness", left=left, right=right,
                          check=check_pair(lengths, left, right))
            return report
    report.update(status="support_obstructed", proof="exhaustive parity completion",
                  parity_candidates=1 << len(free), balanced_candidates=balanced)
    return report


def census(lengths, max_free=16, max_vertices=512):
    """Exhaust every support that could meet half-minus-one, for even order only."""
    lengths = validate_lengths(lengths)
    order = 1+sum(lengths)
    if order % 2 or order < 4:
        raise ValueError("census requires even order at least four")
    if order > max_vertices:
        raise ValueError("size limit exceeded; no all-pairs verdict")
    vertices = [(0, 0)]+[(i, d) for i, n in enumerate(lengths, 1)
                         for d in range(1, n+1)]
    counts = {"bipartition count": 0, "parity certificate": 0,
              "exhaustive parity completion": 0, "inconclusive": 0}
    tested = 0
    for omissions in (0, 2):
        for holes in combinations(vertices, omissions):
            result = complete_support(lengths, holes, max_free, max_vertices)
            tested += 1
            if result["status"] == "witness":
                result.update(tested_supports=tested, census_complete=False)
                return result
            if result["status"] == "inconclusive":
                counts["inconclusive"] += 1
            elif "certificate" in result:
                counts["parity certificate"] += 1
            else:
                counts[result["proof"]] += 1
    report = {"lengths": lengths, "target": order//2-1, "tested_supports": tested,
              "counts": counts, "census_complete": not counts["inconclusive"],
              "infinite_family_proved": False}
    if not counts["inconclusive"]:
        report.update(status="finite_all_pairs_bound", all_pairs_upper_bound=order//2-2)
    else:
        report["status"] = "inconclusive"
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--penultimate", type=int, metavar="T")
    mode.add_argument("--solve", nargs=3, type=int, metavar=("A", "B", "C"))
    mode.add_argument("--census", nargs=3, type=int, metavar=("A", "B", "C"))
    mode.add_argument("--check", type=Path, metavar="PAIR_JSON")
    mode.add_argument("--verify-certificate", type=Path, metavar="JSON")
    parser.add_argument("--arms", nargs=2, type=int, default=(1, 2))
    parser.add_argument("--omit", nargs=2, type=int, action="append", default=[])
    parser.add_argument("--max-free", type=int, default=16)
    parser.add_argument("--max-vertices", type=int, default=512)
    args = parser.parse_args()
    try:
        if args.penultimate is not None:
            if args.penultimate < 0:
                raise ValueError("T must be nonnegative")
            t = args.penultimate
            result = penultimate_certificate((227+7560*t, 67+7560*t, 11+7560*t),
                                             arms=args.arms)
        elif args.census is not None:
            result = census(args.census, args.max_free, args.max_vertices)
        elif args.solve is not None:
            result = complete_support(args.solve, args.omit, args.max_free, args.max_vertices)
        elif args.check is not None:
            pair = json.loads(args.check.read_text())
            result = check_pair(pair["lengths"], pair["left"], pair["right"])
        else:
            data = json.loads(args.verify_certificate.read_text())
            result = verify_certificate(data["lengths"], data["omitted"],
                                        data["certificate"], args.max_vertices)
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.error(str(error))
    print(json.dumps(result, sort_keys=True))
    if args.check:
        return 0 if result["homometric"] else 1
    if args.verify_certificate:
        return 0 if result["valid"] else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
