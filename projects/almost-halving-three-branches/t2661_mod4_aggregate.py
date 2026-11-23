#!/usr/bin/env python3
"""Exact mod-4 compatible recolourings; no claim of full homometry.

All arithmetic is integral. See T2661_MOD4_AGGREGATE.md for the infinite
parity-class extension and the independent large-tree recount.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from t2661_same_parity import BASE, modular_shell, modular_profiles


def classes(k, hole_parity):
    if type(k) is not int or k < 1 or hole_parity not in ('odd', 'even'):
        raise ValueError('positive k and odd/even holes required')
    t = 2660*k+1
    lengths = tuple(t*b for b in BASE)
    holes = ((0, 19), (0, lengths[0])) if hole_parity == 'odd' else ((0, 18), (0, lengths[0]-1))
    groups = [{'arm': None, 'first': 0, 'count': 1}]
    for a, L in enumerate(lengths):
        boundaries = [0]+sorted(d for arm, d in holes if a == arm)+[L+1]
        for lo, hi in zip(boundaries, boundaries[1:]):
            for residue in range(4):
                first = lo+1+(residue-lo-1) % 4
                if first < hi:
                    groups.append({'arm': a, 'first': first, 'count': (hi-1-first)//4+1})
    Q = sum(L//4 for L in lengths)
    columns = []
    for group in groups:
        a, d = group['arm'], group['first']
        if a is None:
            shell = [sum(L//4+int(r != 0 and r <= L % 4) for L in lengths)
                     -sum(hd % 4 == r for _, hd in holes) for r in range(4)]
        else:
            shell = modular_shell(lengths, holes, True, a, d, 4)
        columns.append([1]+[n-Q for n in shell])
    return lengths, holes, groups, list(map(list, zip(*columns)))


def allocation(k, hole_parity):
    """Solve the fixed-size normalized residue system, keeping every bound."""
    lengths, holes, groups, A = classes(k, hole_parity)
    pops = [g['count'] for g in groups]
    totals = [sum(a*n for a, n in zip(row, pops)) for row in A]
    if any(n % 2 for n in totals):
        raise ArithmeticError('nonintegral half histogram')
    target = [n//2 for n in totals]
    large = [j for j, n in enumerate(pops) if n >= 1000]
    corrections = {
        ('odd', 1): (2, 2, 2, 0), ('odd', 0): (2, -1, 2, 0),
        ('even', 1): (0, 4, 2, 0), ('even', 0): (2, 1, 0, 0),
    }[hole_parity, k % 2]+(0,)*8
    if len(large) != 12:
        raise ArithmeticError('unexpected residue class structure')
    x = [n//2 for n in pops]
    for j, value in zip(large, corrections):
        x[j] += value
    if not all(0 <= n <= population for n, population in zip(x, pops)):
        raise ArithmeticError('allocation outside population bounds')
    if any(sum(a*n for a, n in zip(row, x)) != b for row, b in zip(A, target)):
        raise ArithmeticError('allocation equation failed')
    return {'k': k, 't': 2660*k+1, 'hole_parity': hole_parity,
            'lengths': lengths, 'holes': holes, 'groups': groups,
            'negative_counts': x, 'corrections': corrections,
            'normalized_matrix': A}


def materialize(result):
    words = [[1]*L for L in result['lengths']]
    for a, d in result['holes']:
        words[a][d-1] = 0
    centre = 1
    for group, negative in zip(result['groups'], result['negative_counts']):
        a, first = group['arm'], group['first']
        if a is None:
            centre = -1 if negative else 1
        else:
            for j in range(negative):
                words[a][first+4*j-1] = -1
    return words, centre


def check(result):
    """Recount actual vertex-pair bins by the independently written counter."""
    words, centre = materialize(result)
    left, right = modular_profiles(words, centre, 4)
    positive = int(centre == 1)+sum(w.count(1) for w in words)
    negative = int(centre == -1)+sum(w.count(-1) for w in words)
    observed_holes = [(a, d) for a, w in enumerate(words) for d, s in enumerate(w, 1) if not s]
    target = (1+sum(result['lengths']))//2-1
    valid = positive == negative == target and observed_holes == list(result['holes']) and left == right
    edge_difference = 0
    for w in words:
        edge_difference += sum(a for a, b in zip(w, w[1:]) if a == b and a)
        if w[0] == centre:
            edge_difference += centre
    return {'valid_mod4': valid, 'positive_size': positive, 'negative_size': negative,
            'target': target, 'left_bins': left, 'right_bins': right,
            'distance_one_left_minus_right': edge_difference, 'full_homometry_claimed': False}


def parity_extension():
    """Verify both base parity classes and the affine extension identities.

    For k+=2, each large population grows by 1330*BASE_arm, each allocation
    by half that amount; small populations and normalized columns stay fixed.
    Thus base cases k=1,2 with bounded corrections cover every k>=1.
    """
    records = []
    for parity in ('odd', 'even'):
        for k in (1, 2):
            first, later = allocation(k, parity), allocation(k+2, parity)
            if first['normalized_matrix'] != later['normalized_matrix']:
                raise ArithmeticError('normalized matrix changed')
            if first['corrections'] != later['corrections']:
                raise ArithmeticError('parity correction changed')
            for g, h, x, y in zip(first['groups'], later['groups'],
                                  first['negative_counts'], later['negative_counts']):
                growth = h['count']-g['count']
                expected = 1330*BASE[g['arm']] if g['count'] >= 1000 else 0
                if growth != expected or y-x != growth//2:
                    raise ArithmeticError('affine extension mismatch')
            records.append({'hole_parity': parity, 'k_parity': k % 2,
                            'large_class_corrections': first['corrections']})
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--k', type=int, default=1)
    parser.add_argument('--parity', choices=('odd', 'even', 'both'), default='both')
    parser.add_argument('--prove', action='store_true')
    args = parser.parse_args()
    output = {'scope': 'modular distance equality only', 'records': []}
    for parity in (('odd', 'even') if args.parity == 'both' else (args.parity,)):
        result = allocation(args.k, parity)
        verified = check(result)
        if not verified['valid_mod4']:
            raise ArithmeticError('independent mod-4 recount failed')
        output['records'].append({'k': args.k, 'holes': [[a+1, d] for a, d in result['holes']],
                                  'negative_counts': result['negative_counts'], **verified})
    if args.prove:
        output['parity_extension'] = parity_extension()
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
