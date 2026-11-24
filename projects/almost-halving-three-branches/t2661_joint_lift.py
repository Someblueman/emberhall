#!/usr/bin/env python3
"""Explicit bounded joint-modulus allocations and literal-vertex pair counting.

The integer polynomial counter uses no sparse-shell equations and no numerical
FFT. A passing modular allocation does not establish full homometry.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from t2661_joint_residue import family, bounded_allocation, parity_test, lift_problem


def vertices(system, counts):
    """Realize each class by colouring its earliest `count` vertices negative."""
    if len(counts) != len(system['population']) or any(
            type(x) is not int or not 0 <= x <= n
            for x, n in zip(counts, system['population'])):
        raise ValueError('integer allocation outside class bounds')
    positive, negative = set(), set()
    p = system['modulus']
    for g, x in zip(system['groups'], counts):
        for i in range(g['population']):
            v = (g['arm'], g['first']+p*i)
            (negative if i < x else positive).add(v)
    return positive, negative


def _pack(depths, length, width, reverse=False):
    data = bytearray(width*(length+1))
    for d in depths:
        data[width*(length-d if reverse else d)] = 1
    return int.from_bytes(data, 'little')


def _fold(product, first, stop, shift, modulus, width):
    """Read exact base-2^(8*width) polynomial coefficients, without carries."""
    data = product.to_bytes(width*stop, 'little')
    out = [0]*modulus
    for i in range(first, stop):
        value = int.from_bytes(data[width*i:width*(i+1)], 'little')
        out[(i-shift) % modulus] += value
    return out


def actual_pair_bins(lengths, selected, modulus):
    """Count actual unordered vertex pairs by distance modulo modulus.

    Same-arm distances are positive lags of F(z) F_reverse(z). Cross-arm
    distances are depth sums, coefficients of F_a(z) F_b(z). The centre
    contributes one copy of each selected arm depth. Integer multiplication
    is an exact convolution; each coefficient is at most the vertex count,
    strictly below the packing radix. No reduction/shell columns are used.
    """
    if len(lengths) != 3 or any(type(n) is not int or n < 1 for n in lengths):
        raise ValueError('three positive arm lengths required')
    if type(modulus) is not int or modulus < 1:
        raise ValueError('positive distance modulus required')
    selected = list(selected)
    if len(set(selected)) != len(selected):
        raise ValueError('duplicate selected vertex')
    arms = [set() for _ in lengths]
    centre = False
    for a, d in selected:
        if a is None and d == 0:
            centre = True
        elif type(a) is int and a in range(3) and type(d) is int and 1 <= d <= lengths[a]:
            arms[a].add(d)
        else:
            raise ValueError('invalid vertex')
    width = max(1, ((sum(lengths)+1).bit_length()+7)//8)
    packed = [_pack(ds, n, width) for ds, n in zip(arms, lengths)]
    out = [0]*modulus
    def add(values):
        for r, value in enumerate(values):
            out[r] += value
    for a, (ds, n) in enumerate(zip(arms, lengths)):
        add(_fold(packed[a]*_pack(ds, n, width, True), n+1, 2*n+1,
                  n, modulus, width))
        if centre:
            for d in ds:
                out[d % modulus] += 1
        for b in range(a):
            add(_fold(packed[a]*packed[b], 0, n+lengths[b]+1,
                      0, modulus, width))
    if sum(out) != len(selected)*(len(selected)-1)//2:
        raise ArithmeticError('pair counter lost a pair')
    return out


def verify(system, counts, actual=True, full=False):
    """Check bounds/equations, then independently count the realized pair."""
    if not bounded_allocation(system, counts):
        return {'valid': False, 'reason': 'bounds or exact integer equations'}
    positive, negative = vertices(system, counts)
    occupied = {(None, 0)} | {(a, d) for a, n in enumerate(system['lengths'])
                             for d in range(1, n+1)}
    occupied.difference_update(system['holes'])
    if positive & negative or positive | negative != occupied or len(positive) != len(negative):
        raise ArithmeticError('allocation realization is not a balanced partition')
    result = {'valid': True, 'size_each': len(positive), 'modulus': system['modulus'],
              'actual_counter': False, 'full_homometry_claimed': False}
    if actual or full:
        p = sum(sorted(system['lengths'])[-2:])+1 if full else system['modulus']
        a = actual_pair_bins(system['lengths'], positive, p)
        b = actual_pair_bins(system['lengths'], negative, p)
        if full:
            differences = [(i, x-y) for i, (x, y) in enumerate(zip(a, b)) if x != y]
            result['full_distance_check'] = {
                'equal': not differences, 'unequal_distances': len(differences),
                'first_difference': differences[0] if differences else None}
            folded_a, folded_b = [0]*system['modulus'], [0]*system['modulus']
            for i, (x, y) in enumerate(zip(a, b)):
                folded_a[i % system['modulus']] += x
                folded_b[i % system['modulus']] += y
            a, b = folded_a, folded_b
        if a != b:
            raise ArithmeticError('actual pair counter disagrees with sparse system')
        result['actual_counter'] = True
        result['histogram_sha256'] = hashlib.sha256(json.dumps(a).encode()).hexdigest()
    return result


def sparse_rows(system):
    """Transpose the sparse columns; retain balance and the anchor."""
    rows = [{j: 1 for j in range(len(system['population']))},
            {j: a for j, a in enumerate(system['anchor']) if a}]
    rows.extend({} for _ in range(system['modulus']))
    for j, column in enumerate(system['columns']):
        for r, a in column.items():
            rows[r+2][j] = a
    return rows


def parity_analysis(rows, rhs, variables):
    """Packed exact elimination, including a complete left nullspace basis."""
    basis, dependencies = {}, []
    for i, (row, value) in enumerate(zip(rows, rhs)):
        bits = sum(1 << j for j, a in row.items() if a % 2)
        value %= 2
        source = 1 << i
        while bits:
            pivot = (bits & -bits).bit_length()-1
            if pivot not in basis:
                basis[pivot] = bits, value, source
                break
            other, other_value, other_source = basis[pivot]
            bits ^= other
            value ^= other_value
            source ^= other_source
        else:
            dependencies.append(source)
            if value:
                return {'consistent': False, 'rank': len(basis),
                        'contradiction': source, 'bits': None,
                        'dependencies': dependencies}
    solution = 0
    for pivot in sorted(basis, reverse=True):
        row, value, _ = basis[pivot]
        if value ^ ((row & solution).bit_count() % 2):
            solution |= 1 << pivot
    bits = [(solution >> j) & 1 for j in range(variables)]
    if any((sum(a*bits[j] for j, a in row.items())-b) % 2
           for row, b in zip(rows, rhs)):
        raise ArithmeticError('invalid parity solution')
    return {'consistent': True, 'rank': len(basis), 'bits': bits,
            'dependencies': dependencies, 'contradiction': None}


def divided_equation(rows, rhs, source):
    """Exact consequence (sum of selected original equations)/2.

    The caller can independently rebuild this row from its source bitset.
    Every integer solution satisfies it, irrespective of its parity branch.
    """
    if type(source) is not int or not 0 < source < (1 << len(rows)):
        raise ValueError('invalid source equation set')
    coefficients = Counter()
    total = 0
    for i, (row, b) in enumerate(zip(rows, rhs)):
        if source >> i & 1:
            total += b
            for j, a in row.items():
                coefficients[j] += a
    if total % 2 or any(a % 2 for a in coefficients.values()):
        raise ValueError('selected equations are not divisible by two')
    return {j: a//2 for j, a in coefficients.items() if a}, total//2


def divisibility_refinement(system):
    """One complete mod-4 extendability test, with exact row provenance.

    A parity vector extends to an unrestricted solution modulo four iff it
    satisfies the returned derived equations modulo two as well as A u=b
    modulo two. This statement concerns congruences, not finite bounds.
    """
    rows, rhs = sparse_rows(system), list(system['rhs'])
    first = parity_analysis(rows, rhs, len(system['population']))
    if not first['consistent']:
        return {'initial': first, 'refined': first, 'derived': [], 'rows': rows, 'rhs': rhs}
    derived = [divided_equation(rows, rhs, source) for source in first['dependencies']]
    extended = rows+[row for row, _ in derived]
    values = rhs+[b for _, b in derived]
    second = parity_analysis(extended, values, len(system['population']))
    return {'initial': first, 'refined': second, 'derived': derived,
            'rows': extended, 'rhs': values}


def refinement_report(system):
    result = divisibility_refinement(system)
    first, second = result['initial'], result['refined']
    old = first['bits']
    parity_bits = parity_test(system)['solution_bits']
    violated = None if old is None else sum(
        (sum(a*old[j] for j, a in row.items())-b) % 2
        for row, b in result['derived'])
    return {'classes': len(system['population']), 'rows': len(system['rhs']),
            'initial_rank': first['rank'], 'refined_rank': second['rank'],
            'consistent': second['consistent'], 'derived_equations': len(result['derived']),
            'initial_bit_vector_violations': violated,
            'predecessor_bit_vector_violations': sum(
                (sum(a*parity_bits[j] for j, a in row.items())-b) % 2
                for row, b in result['derived']) if parity_bits is not None else None,
            'bounded_integer_feasibility': 'unresolved'}


def branch_probe(system, max_levels=16, initial_bits=None):
    """Follow one explicitly chosen parity branch, never all kernel choices.

    At every level upper-bound-zero variables are equations, not freely
    assignable parity bits. A contradiction rejects only the chosen prefix.
    """
    if type(max_levels) is not int or max_levels < 1:
        raise ValueError('positive level limit required')
    current = system
    offset = [0]*len(system['population'])
    factor = 1
    transcript = []
    for level in range(max_levels):
        rows = sparse_rows(current)
        rhs = list(current['rhs'])
        fixed = [j for j, n in enumerate(current['population']) if n == 0]
        rows.extend({j: 1} for j in fixed)
        rhs.extend(0 for _ in fixed)
        tested = parity_analysis(rows, rhs, len(offset))
        record = {'level': level, 'rank': tested['rank'], 'fixed_variables': len(fixed),
                  'largest_upper_bound': max(current['population']),
                  'consistent': tested['consistent']}
        transcript.append(record)
        if not tested['consistent']:
            # Verify the dual against actual integer equations independently
            # of the elimination's row operations.
            source = tested['contradiction']
            coefficients = Counter()
            value = 0
            for i, (row, b) in enumerate(zip(rows, rhs)):
                if source >> i & 1:
                    value += b
                    for j, a in row.items():
                        coefficients[j] += a
            if any(a % 2 for a in coefficients.values()) or value % 2 != 1:
                raise ArithmeticError('invalid branch contradiction')
            record['verified_dual_rows'] = source.bit_count()
            return {'status': 'chosen_prefix_rejected', 'levels': transcript,
                    'all_parity_branches_examined': False}
        bits = initial_bits if level == 0 and initial_bits is not None else tested['bits']
        if any(type(u) is not int or u not in (0, 1) for u in bits) or len(bits) != len(offset):
            raise ValueError('invalid initial parity vector')
        if any((sum(a*bits[j] for j, a in row.items())-b) % 2
               for row, b in zip(rows, rhs)):
            raise ValueError('initial bits violate parity or fixed-zero bounds')
        offset = [x+factor*u for x, u in zip(offset, bits)]
        if bounded_allocation(system, offset):
            return {'status': 'allocation', 'counts': offset, 'levels': transcript,
                    'all_parity_branches_examined': False}
        current = lift_problem(current, bits)
        factor *= 2
    return {'status': 'level_limit', 'levels': transcript,
            'all_parity_branches_examined': False}


def alternating_kernel(system, arm=None):
    """Zero on tiny classes; alternating depth residues on each large arm.

    This kernel is proved for the odd-hole family, not arbitrary systems.
    """
    return [0 if g['arm'] is None or (g['arm'] == 0 and g['first'] < 19)
            or (arm is not None and g['arm'] != arm)
            else (-1 if g['first'] % 2 else 1) for g in system['groups']]


def joint_allocation(k=1):
    """Bounded joint-modulus witness for every positive k, odd holes only.

    x = seed_negative + (k*arm_base + (k mod 2)*alternating_kernel)/2
    on the large classes. Tiny classes keep the exact FRONTIER seed signs.
    See T2661_JOINT_LIFT.md for the all-k proof and full-homometry limitation.
    """
    from t2661_same_parity import BASE, FRONTIER
    system = family(k, 'odd')
    kernel = alternating_kernel(system)
    counts = []
    for j, group in enumerate(system['groups']):
        arm, first = group['arm'], group['first']
        if arm is None:
            counts.append(1)  # FRONTIER centre is negative.
        elif arm == 0 and first < 19:
            counts.append(int(FRONTIER[arm][first-1] == '-'))
        else:
            residue = first % 2660
            seed_present = (20 <= residue < 99) if arm == 0 else 1 <= residue <= BASE[arm]
            seed_negative = seed_present and FRONTIER[arm][residue-1] == '-'
            counts.append((k*BASE[arm]+(k % 2)*kernel[j])//2+int(seed_negative))
    if not bounded_allocation(system, counts):
        raise ArithmeticError('joint allocation failed exact equations or bounds')
    return system, counts


def even_scale_allocation(k):
    """Inherited special case: no alternating correction is needed at even k."""
    if type(k) is not int or k < 2 or k % 2:
        raise ValueError('positive even k required for the inherited joint control')
    return joint_allocation(k)


def known_control(parity='odd'):
    """Recount the earlier mod-4 witness at joint modulus 2660."""
    from t2661_mod4_aggregate import allocation, materialize
    witness = allocation(1, parity)
    words, centre = materialize(witness)
    positive, negative = [], []
    for a, word in enumerate(words):
        for d, sign in enumerate(word, 1):
            if sign:
                (positive if sign == 1 else negative).append((a, d))
    (positive if centre == 1 else negative).append((None, 0))
    a = actual_pair_bins(witness['lengths'], positive, 2660)
    b = actual_pair_bins(witness['lengths'], negative, 2660)
    mod4 = [sum(a[r::4]) for r in range(4)] == [sum(b[r::4]) for r in range(4)]
    if not mod4 or a == b or len(positive) != len(negative):
        raise ArithmeticError('known positive/negative control changed')
    return {'size_each': len(positive), 'mod4_equal': mod4, 'mod2660_equal': a == b,
            'unequal_joint_bins': sum(x != y for x, y in zip(a, b)),
            'actual_counter': True, 'full_homometry_claimed': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--full', action='store_true', help='also check every original distance, without folding')
    parser.add_argument('--construct', action='store_true', help='construct and independently verify the odd-hole witness (default)')
    parser.add_argument('--even-scale', action='store_true', help='verify the inherited joint positive control at positive even k')
    parser.add_argument('--control', action='store_true', help='independently count a known large mod-4 witness')
    parser.add_argument('--branch', action='store_true', help='probe one parity prefix, with tiny-class bounds')
    parser.add_argument('--refine', action='store_true', help='report branch-independent mod-4 restrictions')
    parser.add_argument('--allocation', type=Path,
                        help='JSON list: one negative count per interval/residue class')
    parser.add_argument('--parity', choices=('odd', 'even'), default='odd')
    parser.add_argument('--k', type=int, default=1)
    parser.add_argument('--output', type=Path, help='save a found branch allocation as JSON')
    args = parser.parse_args()
    start = time.perf_counter()
    system = family(args.k, args.parity)
    if args.even_scale:
        if args.parity != 'odd':
            parser.error('--even-scale uses odd holes')
        system, counts = even_scale_allocation(args.k)
        result = {'inherited_positive_control': True, **verify(system, counts, full=args.full)}
        if args.output is not None:
            args.output.write_text(json.dumps(counts)+'\n')
    elif args.control:
        if args.k != 1:
            parser.error('--control uses k=1')
        result = known_control(args.parity)
    elif args.branch:
        result = branch_probe(system, initial_bits=parity_test(system)['solution_bits'])
        if 'counts' in result:
            counts = result.pop('counts')
            result['verification'] = verify(system, counts, full=args.full)
            result['allocation_sha256'] = hashlib.sha256(json.dumps(counts).encode()).hexdigest()
            if args.output is not None:
                args.output.write_text(json.dumps(counts)+'\n')
                result['allocation_file'] = str(args.output)
    elif args.refine:
        result = refinement_report(system)
    elif args.allocation is not None:
        result = verify(system, json.loads(args.allocation.read_text()), full=args.full)
    else:
        if args.parity != 'odd':
            parser.error('the construction currently uses odd holes')
        system, counts = joint_allocation(args.k)
        result = verify(system, counts, full=args.full)
        if args.output is not None:
            args.output.write_text(json.dumps(counts)+'\n')
    print(json.dumps({**result, 'seconds': round(time.perf_counter()-start, 3)}, indent=2))
    return 0 if result.get('valid', True) else 1


if __name__ == '__main__':
    raise SystemExit(main())
