"""Palindromic-cell constructions via an Euler tour; standard library only.

Every distinct-arm tripod with gcd(a-b,b-c)=1 meets the target. An even-sum
base also gives every dilation. An obstructed cell graph is not a general
tripod obstruction. See RATIO_51_33_10.md for the proof and exact scope.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from math import gcd
from pathlib import Path
import sys

from published_cases import check_pair, validate_lengths

BASE = (51, 33, 10)
BOUNDARY = -1


def cell_identity(words: list[str] | tuple[str, ...]) -> dict[int, int]:
    """Coefficients of sum_i F_i(x) sum_(j!=i) x^n_j, independently of the graph."""
    if (not isinstance(words, (list, tuple)) or len(words) != 3
            or any(not isinstance(w, str) or not w or set(w)-set('+-')
                               for w in words)):
        raise ValueError("three nonempty sign words are required")
    lengths = [len(word) for word in words]
    result = Counter()
    for arm, word in enumerate(words):
        for other, length in enumerate(lengths):
            if arm != other:
                for depth, sign in enumerate(word):
                    result[depth+length] += 1 if sign == '+' else -1
    return {degree: coefficient for degree, coefficient in sorted(result.items()) if coefficient}


def verify_template(words: list[str] | tuple[str, ...]) -> bool:
    residual = cell_identity(words)
    return (not residual and all(word == word[::-1] for word in words)
            and abs(sum(1 if word[0] == '+' else -1 for word in words)) == 1)


def classify(lengths: object) -> dict:
    """Exact admission for this method, not an obstruction to arbitrary pairs."""
    lengths = validate_lengths(lengths)
    divisor = gcd(lengths[0]-lengths[1], lengths[1]-lengths[2])
    if not divisor:
        reason = 'three equal cell lengths give an odd coefficient sum'
    elif any(n % divisor for n in lengths):
        reason = 'residue populations have both parities'
    elif sum(n//divisor for n in lengths) % 2:
        reason = 'each residue population is odd'
    else:
        reason = None
    return {'cell_lengths': lengths, 'divisor': divisor, 'admitted': reason is None,
            'reason': reason, 'scope': 'palindromic-cell method',
            'general_tripod_obstruction': False}


def cell_graph(lengths: object) -> tuple[list[tuple[int, int]], list[tuple[int, tuple[int, ...]]]]:
    """Fold polynomial degrees and palindromic variable pairs; retain multiedges."""
    lengths = validate_lengths(lengths)
    total = sum(lengths)
    if total % 2:
        raise ValueError("cell lengths must have even sum")
    edges, variables = [], []
    for arm, length in enumerate(lengths):
        for j in range((length+1)//2):
            positions = tuple(sorted({j, length-1-j}))
            counts = Counter(min(p+n, total-1-p-n)
                             for p in positions for other, n in enumerate(lengths)
                             if other != arm)
            if any(count % 2 for count in counts.values()):
                raise ArithmeticError("a reflected degree pair failed to fold")
            ends = [degree for degree, count in sorted(counts.items())
                    for _ in range(count//2)]
            if len(ends) == 1:
                ends.append(BOUNDARY)
            if len(ends) != 2:
                raise ArithmeticError("a cell variable is not an edge or half-edge")
            edges.append(tuple(ends))
            variables.append((arm, positions))
    return edges, variables


def template(lengths: object = BASE) -> dict:
    """Decide this cell method exactly and construct words when it succeeds."""
    lengths = validate_lengths(lengths)
    edges, variables = cell_graph(lengths)
    adjacency = defaultdict(list)
    for edge_id, (u, v) in enumerate(edges):
        adjacency[u].append(edge_id)
        adjacency[v].append(edge_id)  # A loop contributes twice to its degree.
    if any(len(incident) % 2 for v, incident in adjacency.items() if v != BOUNDARY):
        raise ArithmeticError("an interior cell-graph degree is odd")
    used = set()
    signs = {}
    components = []
    starts = ([BOUNDARY] if BOUNDARY in adjacency else []) + sorted(
        v for v in adjacency if v != BOUNDARY)
    for start in starts:
        if all(edge in used for edge in adjacency[start]):
            continue
        stack, tour = [(start, None)], []
        while stack:
            vertex, arrival = stack[-1]
            while adjacency[vertex] and adjacency[vertex][-1] in used:
                adjacency[vertex].pop()
            if not adjacency[vertex]:
                stack.pop()
                if arrival is not None:
                    tour.append(arrival)
            else:
                edge = adjacency[vertex].pop()
                used.add(edge)
                u, v = edges[edge]
                stack.append((v if u == vertex else u, edge))
        tour.reverse()
        boundary = start == BOUNDARY
        components.append({"edge_count": len(tour), "has_boundary": boundary})
        for index, edge in enumerate(tour):
            signs[edge] = 1 if index % 2 == 0 else -1
    obstructed = any(not c["has_boundary"] and c["edge_count"] % 2 for c in components)
    if obstructed == classify(lengths)['admitted']:
        raise ArithmeticError('the graph and arithmetic admission tests disagree')
    result = {"cell_lengths": lengths, "components": components,
              "gcd_differences": gcd(lengths[0]-lengths[1], lengths[1]-lengths[2]),
              "status": "obstructed" if obstructed else "constructed",
              "scope": "palindromic-cell method", "general_tripod_obstruction": False}
    if obstructed:
        return result
    words = [['?']*n for n in lengths]
    for edge, (arm, positions) in enumerate(variables):
        for j in positions:
            words[arm][j] = '+' if signs[edge] == 1 else '-'
    words = [''.join(word) for word in words]
    if not verify_template(words):
        raise ArithmeticError("the Euler tour failed the independent cell identity")
    if sum(1 if word[0] == '+' else -1 for word in words) == 1:
        words = [''.join('-' if sign == '+' else '+' for sign in word) for word in words]
    return {**result, "words": words, "center_sign": -1,
            "identity_residual": cell_identity(words)}


def construct(t: int, lengths: object = BASE) -> dict:
    if type(t) is not int or t < 1:
        raise ValueError("the scale must be a positive integer")
    certified = template(lengths)
    if certified['status'] != 'constructed':
        raise ValueError("an odd closed component obstructs this cell method; "
                         "no general tripod obstruction is claimed")
    left, right = [], [(0, 0)]
    for arm, word in enumerate(certified['words'], 1):
        for j, sign in enumerate(word):
            # Cell zero has t-1 vertices; every other cell has t vertices.
            for depth in range(max(1, j*t), (j+1)*t):
                (left if sign == '+' else right).append((arm, depth))
    original = [n*t for n in certified['cell_lengths']]
    checked = check_pair(original, left, right)
    if not checked['homometric'] or checked['size'] != sum(original)//2-1:
        raise ArithmeticError("the certified dilation failed its original-tree recount")
    return {"scale": t, "lengths": original, "left": left, "right": right,
            "cell_lengths": certified['cell_lengths'], **checked}


def original_tree(lengths: object) -> dict:
    """Apply the cell method at scale one, using a full partition when possible."""
    lengths = validate_lengths(lengths)
    cells = lengths if sum(lengths) % 2 == 0 else tuple(n+1 for n in lengths)
    witness = construct(1, cells)
    checked = check_pair(lengths, witness['left'], witness['right'])
    if not checked['homometric'] or not checked['meets_target']:
        raise ArithmeticError("the original-tree conversion failed")
    return {**witness, "lengths": lengths, **checked}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--witness', type=int, metavar='T')
    mode.add_argument('--tree', type=int, nargs=3, metavar=('A', 'B', 'C'))
    mode.add_argument('--prove', action='store_true')
    mode.add_argument('--classify', type=int, nargs=3, metavar=('A', 'B', 'C'))
    mode.add_argument('--check', metavar='FILE')
    parser.add_argument('--base', type=int, nargs=3, default=BASE)
    args = parser.parse_args()
    try:
        if args.classify is not None:
            result = classify(args.classify)
        elif args.prove:
            result = template(args.base)
        elif args.witness is not None:
            result = construct(args.witness, args.base)
        elif args.tree is not None:
            result = original_tree(args.tree)
        else:
            data = sys.stdin.read() if args.check == '-' else Path(args.check).read_text()
            pair = json.loads(data)
            result = check_pair(pair['lengths'], pair['left'], pair['right'])
        print(json.dumps(result, sort_keys=True))
        return 0 if result.get('homometric', True) and result.get('status') != 'obstructed' else 1
    except (KeyError, TypeError, ValueError, OSError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    raise SystemExit(main())
