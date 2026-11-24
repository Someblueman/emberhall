#!/usr/bin/env python3
"""Sparse exact joint-modulus reduction. Mod-2 feasibility is not a colouring."""
from __future__ import annotations
from collections import Counter
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
sys.path.insert(0, str(Path(__file__).resolve().parent))
from t2661_same_parity import BASE


def derivative_column(lengths, holes, arm, depth, modulus):
    """Cyclic difference A_r(v)-A_(r-1)(v), with at most ten terms.

    Multiply the full occupied distance shell by 1-z before folding
    modulo z^P-1; this avoids a dense P-entry histogram per vertex class.
    """
    out = Counter()
    def term(exponent, coefficient):
        out[exponent % modulus] += coefficient
    if arm is None:
        term(1, 3)
        for L in lengths:
            term(L+1, -1)
    else:
        term(1, 2)
        term(depth+1, 1)
        for a, L in enumerate(lengths):
            if a != arm:
                term(depth+L+1, -1)
        term(lengths[arm]-depth+1, -1)
    for a, d in holes:
        distance = d if arm is None else abs(depth-d) if arm == a else depth+d
        term(distance, -1)
        term(distance+1, 1)
    return {r: n for r, n in out.items() if n}


def anchor_coefficient(lengths, holes, arm, depth, modulus):
    """A_0(v)-Q; adding this row retains the constant cyclic mode over
    finite fields too. It is computed in O(arms+holes), without a dense bin.
    """
    Q = sum(L//modulus for L in lengths)
    if arm is None:
        return -sum(d % modulus == 0 for _, d in holes)
    value = (depth-1)//modulus+(lengths[arm]-depth)//modulus
    value += int(depth % modulus == 0)
    for a, L in enumerate(lengths):
        if a != arm:
            r = (-depth) % modulus
            value += L//modulus+int(r != 0 and r <= L % modulus)
    value -= sum((abs(depth-d) if a == arm else depth+d) % modulus == 0 for a, d in holes)
    return value-Q


def reduction(lengths, holes, modulus):
    """Exact bounded integer system on residue/interval sign classes.

    x_j counts negatives, 0<=x_j<=population_j. The returned equations
    are A x = A population / 2, including the first balance row.
    """
    if len(lengths) != 3 or any(type(L) is not int or L < 1 for L in lengths):
        raise ValueError('three positive integer lengths required')
    if type(modulus) is not int or modulus < 1:
        raise ValueError('positive modulus required')
    if len(set(holes)) != 2 or any(a not in range(3) or not 1 <= d <= lengths[a] for a, d in holes):
        raise ValueError('two distinct valid arm holes required')
    groups = [{'arm': None, 'first': 0, 'population': 1}]
    for a, L in enumerate(lengths):
        boundaries = [0]+sorted(d for arm, d in holes if arm == a)+[L+1]
        for lo, hi in zip(boundaries, boundaries[1:]):
            for residue in range(modulus):
                first = lo+1+(residue-lo-1) % modulus
                if first < hi:
                    groups.append({'arm': a, 'first': first,
                                   'population': (hi-1-first)//modulus+1})
    columns = [derivative_column(lengths, holes, g['arm'], g['first'], modulus) for g in groups]
    population = [g['population'] for g in groups]
    anchor = [anchor_coefficient(lengths, holes, g['arm'], g['first'], modulus) for g in groups]
    totals = [sum(population), sum(a*n for a, n in zip(anchor, population))]+[0]*modulus
    for column, n in zip(columns, population):
        for r, coefficient in column.items():
            totals[r+2] += coefficient*n
    if any(n % 2 for n in totals):
        raise ArithmeticError('half system is nonintegral')
    return {'lengths': tuple(lengths), 'holes': tuple(holes), 'modulus': modulus,
            'groups': groups, 'columns': columns, 'anchor': anchor, 'population': population,
            'rhs': [n//2 for n in totals]}


def lhs(system, counts):
    if len(counts) != len(system['groups']):
        raise ValueError('wrong allocation length')
    out = [sum(counts), sum(a*n for a, n in zip(system['anchor'], counts))]+[0]*system['modulus']
    for column, n in zip(system['columns'], counts):
        for r, coefficient in column.items():
            out[r+2] += coefficient*n
    return out


def bounded_allocation(system, counts):
    return (len(counts) == len(system['population'])
            and all(type(x) is int and 0 <= x <= n for x, n in zip(counts, system['population']))
            and lhs(system, counts) == system['rhs'])


def parity_test(system):
    """Necessary integer-system test; return an independently checked dual
    contradiction or a solution of the equations over GF(2) only.
    """
    n = len(system['columns'])
    rhsbit = 1 << n
    rows = [sum(1 << j for j in range(n)), sum(1 << j for j, a in enumerate(system['anchor']) if a % 2)]+[0]*system['modulus']
    for j, column in enumerate(system['columns']):
        for r, coefficient in column.items():
            if coefficient % 2:
                rows[r+2] ^= 1 << j
    for i, value in enumerate(system['rhs']):
        if value % 2:
            rows[i] ^= rhsbit
    original = rows[:]
    basis = {}
    for index, row in enumerate(rows):
        support = 1 << index
        while row & (rhsbit-1):
            pivot = (row & (rhsbit-1)).bit_length()-1
            if pivot not in basis:
                basis[pivot] = row, support
                break
            other, source = basis[pivot]
            row ^= other
            support ^= source
        else:
            if row == rhsbit:
                equations = [i for i in range(len(rows)) if (support >> i) & 1]
                check = 0
                for i in equations:
                    check ^= original[i]
                if check != rhsbit:
                    raise ArithmeticError('invalid parity contradiction')
                return {'consistent_mod2': False, 'rank': len(basis),
                        'dual_equations': equations, 'solution_bits': None}
    solution = 0
    for pivot in sorted(basis):
        row = basis[pivot][0]
        value = int(bool(row & rhsbit)) ^ ((row & (rhsbit-1) & solution).bit_count() % 2)
        if value:
            solution |= 1 << pivot
    counts = [(solution >> j) & 1 for j in range(n)]
    actual = lhs(system, counts)
    if any((x-y) % 2 for x, y in zip(actual, system['rhs'])):
        raise ArithmeticError('invalid parity solution')
    return {'consistent_mod2': True, 'rank': len(basis), 'dual_equations': [],
            'solution_bits': counts}


def lift_problem(system, bits):
    """Exact residual integer problem for one chosen mod-2 branch.

    x=bits+2y. Failure in this branch does not exclude other parity solutions.
    The columns stay sparse, and finite bounds remain explicit.
    """
    if len(bits) != len(system['population']) or any(x not in (0, 1) for x in bits):
        raise ValueError('one bit per class required')
    residual = [b-a for a, b in zip(lhs(system, bits), system['rhs'])]
    if any(n % 2 for n in residual):
        raise ValueError('bits do not satisfy the necessary parity equations')
    return {**system, 'population': [(n-u)//2 for n, u in zip(system['population'], bits)],
            'rhs': [n//2 for n in residual], 'offsets': list(bits)}


def family(k, parity, modulus=2660):
    if type(k) is not int or k < 1 or parity not in ('odd', 'even', 'opposite'):
        raise ValueError('positive k and a recognized hole parity required')
    lengths = tuple((2660*k+1)*b for b in BASE)
    holes = ((0, 19), (0, lengths[0])) if parity == 'odd' else (
        ((0, 18), (0, lengths[0]-1)) if parity == 'even' else ((0, 19), (0, lengths[0]-1)))
    return reduction(lengths, holes, modulus)


def report(k=1, parity='odd'):
    start = time.perf_counter()
    system = family(k, parity)
    tested = parity_test(system)
    bits = tested.pop('solution_bits')
    dual = tested.pop('dual_equations')
    exact = bounded_allocation(system, bits) if bits is not None else False
    result = {'k': k, 'hole_parity': parity, 'modulus': 2660,
              'classes': len(system['groups']), 'rows': 2662,
              'nonzero_entries': len(system['groups'])+sum(bool(a) for a in system['anchor'])+sum(map(len, system['columns'])),
              **tested, 'dual_equation_count': len(dual),
              'dual_equations': dual if len(dual) <= 32 else None,
              'dual_sha256': hashlib.sha256(json.dumps(dual, separators=(',', ':')).encode()).hexdigest(),
              'actual_integer_allocation': exact,
              'seconds': round(time.perf_counter()-start, 4)}
    if bits is not None:
        residual = [a-b for a, b in zip(lhs(system, bits), system['rhs'])]
        result['nonzero_integer_residual_rows'] = sum(bool(n) for n in residual)
        lifted = lift_problem(system, bits)
        result['lift_fixed_variables'] = sum(n == 0 for n in lifted['population'])
        result['lift_largest_upper_bound'] = max(lifted['population'])
        result['parity_solution_sha256'] = hashlib.sha256(bytes(bits)).hexdigest()
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--k', type=int, default=1)
    p.add_argument('--parity', choices=('odd', 'even', 'opposite', 'all'), default='all')
    args = p.parse_args()
    parities = ('odd', 'even', 'opposite') if args.parity == 'all' else (args.parity,)
    print(json.dumps({'scope': 'exact reduction and necessary parity test only',
                      'records': [report(args.k, parity) for parity in parities]}, indent=2))


if __name__ == '__main__':
    main()
