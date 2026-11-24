#!/usr/bin/env python3
"""Exact upper-shell completion and twenty-four forced interior repair signs.

Standard library only. This is a necessary restriction, not a full solution.
See INTERMEDIATE_SHELL_REPAIR.md. No modular distance folding is used.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from math import lcm


# Literal seed from residue_2660.py, retained here for a self-contained checker.
SEED = ('+-+-+-+-+-+-+-+-+-0-+-++++++++++++++++-+-++++++++++++++++'
        '-+-++++++++++++++++-+--+-+-+-+-+-+-+-+-+-0',
        '+-+-+-+-+-+-+-+-+-++-+----------------+-+----------------'
        '+-++-+-+-+-+-+-+-+-+-+',
        '+-+-----------------+-+')

LOCAL_K = (-1, -1, -1, -1, 1, 1, 3, 3, 5, 5, 7, 7, 9, 9, 11, 11, 13, 13)
FORCED = {**{j: 1 for j in range(5, 20, 2)}, 20: 1, 21: -1, 22: 1, 23: -1}


def geometry(lengths, h):
    if (not isinstance(lengths, (list, tuple)) or len(lengths) != 3
            or any(type(n) is not int for n in lengths)):
        raise ValueError('three integer lengths required')
    a, b, c = lengths
    if not a > b > c >= 1 or type(h) is not int or not 1 <= h < a-b+1:
        raise ValueError('require A>B>C>=1 and 1<=hole<A-B+1')
    return a, b, c


def signs(word, length):
    if (not isinstance(word, (list, tuple)) or len(word) != length
            or any(type(v) is not int or v not in (-1, 1) for v in word)):
        raise ValueError('literal integer signs of the stated length required')
    return list(word)


def complete_upper(lengths, h, arm2, arm3):
    """The unique suffix at depths A-B+1..A-1 satisfying every shell d>A.

    Integer outputs outside +/-1 certify impossibility for these shorter
    arms. The two holes are on arm one at h and A. No balance is assumed.
    """
    a, b, c = geometry(lengths, h)
    y, z = signs(arm2, b), signs(arm3, c)
    lag, onset = b-c, a-c
    q = [0]  # q[r] is the sign at depth A-r
    for r in range(1, b):
        value = -y[b-r]
        if r > lag:
            j = r-lag
            value -= q[j] + z[c-j]
        if r >= onset:
            j = r-onset
            value -= y[b-1-j] + z[c-1-j]
        q.append(value)
    bad = [(a-r, v) for r, v in enumerate(q[1:], 1) if v not in (-1, 1)]
    return {'start_depth': a-b+1, 'suffix': list(reversed(q[1:])),
            'sign_feasible': not bad, 'invalid_count': len(bad),
            'first_invalid': bad[0] if bad else None,
            'shells_completed': b-1, 'full_homometry_claimed': False}


def validate_words(lengths, h, words):
    a, _, _ = geometry(lengths, h)
    if not isinstance(words, (list, tuple)) or len(words) != 3:
        raise ValueError('three complete words required')
    for i, (word, n) in enumerate(zip(words, lengths)):
        if len(word) != n:
            raise ValueError('word length mismatch')
        for d, v in enumerate(word, 1):
            allowed = (0,) if i == 0 and d in (h, a) else (-1, 1)
            if type(v) is not int or v not in allowed:
                raise ValueError('only the stated holes can be zero')


def audit_upper(lengths, h, words):
    validate_words(lengths, h, words)
    result = complete_upper(lengths, h, words[1], words[2])
    actual = words[0][result['start_depth']-1:lengths[0]-1]
    mismatches = [(result['start_depth']+i, v, got)
                  for i, (v, got) in enumerate(zip(result['suffix'], actual)) if v != got]
    return {'upper_shells_equal': not mismatches,
            'forced_suffix_sign_feasible': result['sign_feasible'],
            'first_mismatch': mismatches[0] if mismatches else None,
            'mismatch_count': len(mismatches),
            'shells_checked': result['shells_completed'],
            'full_homometry_claimed': False}


def actual_upper_counts(lengths, h, words, distance):
    """Fresh literal-vertex counter, independent of the completion recurrence.

    At d>A every pair crosses two different arms. Enumerate its actual
    depths and count ++ and -- pairs separately, without a sign-sum formula.
    """
    validate_words(lengths, h, words)
    if type(distance) is not int or not lengths[0] < distance <= lengths[0]+lengths[1]:
        raise ValueError('counter requires distance above the longest arm')
    positive = negative = 0
    for i in range(3):
        for j in range(i+1, 3):
            lo, hi = max(1, distance-lengths[j]), min(lengths[i], distance-1)
            for u in range(lo, hi+1):
                v = distance-u
                left, right = words[i][u-1], words[j][v-1]
                positive += left == right == 1
                negative += left == right == -1
    return positive, negative





def boundary_twenty_count():
    """All ordered pairs of 19-sign prefixes passing the first 20 shells.

    Records the first branch sum separately; it returns in shell 20.
    These are boundary solutions only, not full homometric colourings.
    """
    states = {(0, None): 1}
    for j, constant in enumerate(LOCAL_K[1:], 1):
        following = Counter()
        for (running, initial), count in states.items():
            for step, multiplicity in ((-2, 1), (0, 2), (2, 1)):
                if constant+running+step in (-1, 1):
                    first = step if j == 1 else initial
                    following[running+step, first] += count*multiplicity
        states = following
    eighteen = sum(states.values())
    twenty = 0
    for (running, first), count in states.items():
        x37 = LOCAL_K[-1]+running
        for step18, m18 in ((-2, 1), (0, 2), (2, 1)):
            x38 = x37+2+step18
            if x38 not in (-1, 1):
                continue
            for step19, m19 in ((-2, 1), (0, 2), (2, 1)):
                if x38+step19-first in (-1, 1):
                    twenty += count*m18*m19
    return {'first_18_prefix_pairs': eighteen, 'first_20_prefix_pairs': twenty,
            'full_homometry_claimed': False}


def local_twenty(arm2_18_19, arm3_18_19):
    """Exact next two forced signs after Tern's displayed 18-shell prefix.

    All 256 sharp tail repairs have the same last 20 signs. Arbitrary
    other inserted signs cannot change these two coefficient equations.
    """
    y, z = signs(arm2_18_19, 2), signs(arm3_18_19, 2)
    x38 = 1+y[0]+z[0]
    x39 = x38+y[1]+z[1]
    return {'valid': x38 in (-1, 1) and x39 in (-1, 1),
            'arm1_depth38': x38, 'arm1_depth39': x39,
            'full_homometry_claimed': False}


def full_identity(lengths, h, centre, words):
    """Literal coefficients of (1-z)F-2zS, with original occupied shells.

    F[d] is twice the signed same-colour pair discrepancy. This direct
    geometric formula is separate from both completion recurrences.
    """
    validate_words(lengths, h, words)
    if type(centre) is not int or centre not in (-1, 1):
        raise ValueError('signed centre required')
    a, b, _ = lengths
    out = [0]*(a+b+2)
    out[1] += centre
    for n in lengths:
        out[n+1] -= centre
    for hole in (h, a):
        out[hole] -= centre
        out[hole+1] += centre
    for i, word in enumerate(words):
        for d, sign in enumerate(word, 1):
            if not sign:
                continue
            out[d+1] += sign
            out[lengths[i]+1-d] -= sign
            for j, n in enumerate(lengths):
                if i != j:
                    out[d+n+1] -= sign
            for hole in (h, a):
                distance = abs(d-hole) if i == 0 else d+hole
                out[distance] -= sign
                out[distance+1] += sign
    return {d: v for d, v in enumerate(out) if v}


def complete_family_first_arm(k, centre, prefix, arm2, arm3):
    """Exact iff completion on T(99t,79t,23t), t=2660k+1.

    Uses upper shells to force 79t-1 signs, then low shells to force the
    remaining 20t-19 signs. Final undivided identity enforces every shell.
    k=0 admits the published seed as an independent positive control.
    """
    if type(k) is not int or k < 0:
        raise ValueError('nonnegative integer k required')
    if type(centre) is not int or centre not in (-1, 1):
        raise ValueError('signed centre required')
    p = signs(prefix, 18)
    t = 2660*k+1
    a, b, c = 99*t, 79*t, 23*t
    y, z = signs(arm2, b), signs(arm3, c)
    upper = complete_upper((a, b, c), 19, y, z)
    if not upper['sign_feasible']:
        return {'valid': False, 'reason': 'upper-shell forced sign',
                'first_invalid': upper['first_invalid']}
    x = [0]*a
    x[:18] = p
    x[20*t:a-1] = upper['suffix']

    def get(word, depth):
        return word[depth-1] if 1 <= depth <= len(word) else 0

    for depth in range(20, 20*t+1):
        n = depth-19
        f = centre*((n == 1)-(n == 19)+(n == 20))
        for word in (y, z):
            f += get(word, n-1)-get(word, n-19)+get(word, n-20)
            f -= get(word, len(word)+1-n)
        f += -get(p, 19-n)+get(p, 20-n)
        value = get(x, depth-1)+get(x, n-1)-get(x, a-n)+f
        if value not in (-1, 1):
            return {'valid': False, 'reason': 'low-shell forced sign',
                    'depth': depth, 'coefficient': value}
        x[depth-1] = value
    residual = full_identity((a, b, c), 19, centre, (x, y, z))
    if residual:
        first = min(residual)
        return {'valid': False, 'reason': 'remaining exact shell identity',
                'first_residual': [first, residual[first]],
                'residual_terms': len(residual)}
    return {'valid': True, 'arm1': x, 'lengths': [a, b, c],
            'size': (a+b+c-1)//2, 'all_original_distances_equal': True}



def periodic_words(k, blocks, choice=0):
    """Literal periodic insertion candidate, for checking the obstruction.

    Blocks have one common period dividing 2660*k. They may differ between
    arms; no relation, balance or residue-count assumption is made.
    """
    if type(k) is not int or k < 1 or type(choice) is not int or not 0 <= choice < 256:
        raise ValueError('positive k and choice in 0..255 required')
    if not isinstance(blocks, (list, tuple)) or len(blocks) != 3:
        raise ValueError('three blocks required')
    period = len(blocks[0])
    if period < 1 or (2660*k) % period:
        raise ValueError('common period must divide 2660*k')
    blocks = [signs(b, period) for b in blocks]
    words = []
    for i, (base, cut) in enumerate(((99, 19), (79, 0), (23, 0))):
        seed = [0 if v == '0' else 1 if v == '+' else -1 for v in SEED[i]]
        words.append(seed[:cut]+blocks[i]*(base*2660*k//period)+seed[cut:])
    for bit, r in enumerate(range(61, 76, 2)):
        arm = (choice >> bit) & 1
        depth = (99-r+99*2660*k) if arm == 0 else (80-r+79*2660*k)
        words[arm][depth-1] = -1
    return words


def _coefficient_row(lengths, h, n):
    """Coefficient n of R as a sparse row on literal vertex signs."""
    a = lengths[0]
    out = Counter()

    def put(arm, depth, value):
        if arm == 0:
            if depth == 0:
                out[0, 0] += value
        elif (1 <= depth <= lengths[arm-1]
              and not (arm == 1 and depth in (h, a))):
            out[arm, depth] += value

    put(0, 0, (n == 1)-sum(n == v+1 for v in lengths)
        -sum(n == v for v in (h, a))+sum(n == v+1 for v in (h, a)))
    for arm, length in enumerate(lengths, 1):
        put(arm, n-1, 1)
        put(arm, length+1-n, -1)
        for other, other_length in enumerate(lengths, 1):
            if arm != other:
                put(arm, n-other_length-1, -1)
        for hole in (h, a):
            if arm == 1:
                if n > 0:
                    put(arm, hole-n, -1)
                    put(arm, hole+n, -1)
                if n > 1:
                    put(arm, hole-n+1, 1)
                    put(arm, hole+n-1, 1)
            else:
                put(arm, n-hole, -1)
                put(arm, n-hole-1, 1)
    return {key: value for key, value in out.items() if value}


def local_repair_equation(k, period):
    """A necessary equation on a bounded set of arbitrary inserted signs.

    Same-residue equality is required only at positions named by this
    equation, not throughout the words. Such local matching is impossible
    for a complete repair; all other inserted signs can be arbitrary.
    """
    certificate = periodic_obstruction(period, k)
    p = certificate['effective_period']
    t = 2660*k+1
    lengths = [99*t, 79*t, 23*t]
    combined = Counter()
    for base in (0, 23, 79, 99):
        n = 6+base*2660*k
        combined.update(_coefficient_row(lengths, 19, n))
        combined.subtract(_coefficient_row(lengths, 19, n-p))
    terms, constant = [], 0
    grouped = Counter()
    for (arm, depth), value in sorted(combined.items()):
        if not value:
            continue
        if arm == 0:
            constant -= value
            continue
        base, cut = (99, 79, 23)[arm-1], 19 if arm == 1 else 0
        if cut < depth <= cut+base*2660*k:
            residue = (depth-cut-1) % p
            terms.append([arm, depth, value, residue])
            grouped[arm, residue] += value
        else:
            old = depth if depth <= cut else depth-base*2660*k
            char = SEED[arm-1][old-1]
            sign = 0 if char == '0' else 1 if char == '+' else -1
            # Choice zero suffices: all eight binary choices cancel from
            # this row combination, as the formal four-row certificate shows.
            if arm == 1 and old in range(24, 39, 2):
                sign = -1
            constant += value*sign
    if constant != -2 or any(grouped.values()):
        raise ArithmeticError('local matching certificate failed')
    return {'k': k, 'period': period, 'effective_period': p,
            'constant': constant, 'terms': terms,
            'equation': 'constant + sum(coefficient * sign_at_depth) = 0',
            'matching_rule': 'equal signs within each named arm/residue group',
            'all_other_inserted_signs': 'arbitrary',
            'locally_matching_repairs_excluded': True}



def audit_repair_window(k, period, words):
    """Evaluate the necessary equation on arbitrary literal insertion words.

    Reject inputs outside the exact retained-seed repair class, and never
    turn one satisfied linear functional into a full-homometry verdict.
    """
    equation = local_repair_equation(k, period)
    t = 2660*k+1
    lengths = [99*t, 79*t, 23*t]
    validate_words(lengths, 19, words)
    conflicts = set(range(61, 76, 2))
    for arm, text in enumerate(SEED, 1):
        base, cut = (99, 79, 23)[arm-1], 19 if arm == 1 else 0
        for old, char in enumerate(text, 1):
            paired = ((arm == 1 and 99-old in conflicts)
                      or (arm == 2 and 80-old in conflicts))
            if paired:
                continue
            depth = old if old <= cut else old+base*2660*k
            expected = 0 if char == '0' else 1 if char == '+' else -1
            if words[arm-1][depth-1] != expected:
                raise ValueError('retained seed is outside the sharp repair class')
    for r in conflicts:
        x = words[0][99-r+99*2660*k-1]
        y = words[1][80-r+79*2660*k-1]
        if x != -y:
            raise ValueError('each conflicting pair needs exactly one retained flip')
    value = equation['constant']
    groups = {}
    for arm, depth, coefficient, residue in equation['terms']:
        sign = words[arm-1][depth-1]
        value += coefficient*sign
        groups.setdefault((arm, residue), set()).add(sign)
    return {'necessary_equation_value': value,
            'necessary_equation_passes': value == 0,
            'locally_matching': all(len(values) == 1 for values in groups.values()),
            'named_positions': len(equation['terms']),
            'excluded_by_this_equation': value != 0,
            'full_homometry_claimed': False}


def periodic_obstruction(period, k=1):
    """Four exact coefficient rows, whose variable terms cancel to -2.

    For p>=7 these are coefficients of (1-z**p)R at z**6 times
    W**(0,23m,79m,99m), where m=2660*k/p and W=z**p.
    A smaller period embeds in lcm(p,20). See the coefficient proof.
    """
    if type(k) is not int or k < 1:
        raise ValueError('positive k required')
    if type(period) is not int or period < 1 or (2660*k) % period:
        raise ValueError('period must be a positive divisor of 2660*k')
    effective = lcm(period, 20) if period < 7 else period
    rows = [
        {'constant': 0, 'a5': 1, 'a6': -1, 'b5': 1, 'c5': 1},
        {'constant': -1, 'c5': -1},
        {'constant': 0, 'b5': -1, 'u75': -1},
        {'constant': -1, 'a5': -1, 'a6': 1, 'u75': 1},
    ]
    total = Counter()
    for row in rows:
        total.update(row)
    total = {key: value for key, value in total.items() if value}
    if total != {'constant': -2}:
        raise ArithmeticError('coefficient certificate failed')
    return {'period': period, 'effective_period': effective,
            'k': k, 'rows': rows, 'sum': total, 'all_admissible_blocks_excluded': True,
            'W_exponents': [base*(2660*k//effective) for base in (0, 23, 79, 99)],
            'minimum_bin_separation': 7980*k,
            'maximum_z_span': effective+180,
            'scope': 'all 256 sharp tail repairs with common periodic insertions',
            'arbitrary_insertion_obstruction_claimed': False}


def frontier_restriction(k):
    """Necessary signs for all 256 minimal tail repairs, every insertion word."""
    if type(k) is not int or k < 1:
        raise ValueError('positive integer k required')
    t = 2660*k+1
    return {'k': k, 't': t, 'lengths': [99*t, 79*t, 23*t],
            'required_arm1': [[43*t-j, sign] for j, sign in FORCED.items()],
            'required_arm2': [[23*t-j+1, sign] for j, sign in FORCED.items()],
            'distance_pairs': [[122*t-j, 122*t-j+1] for j in FORCED],
            'scope': 'the 256 sharp tail repairs; arbitrary inserted signs',
            'local_boundary_counts': boundary_twenty_count(),
            'full_homometry_claimed': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--k', type=int, default=1, help='scale for periodic certificate')
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--frontier-restriction', type=int, metavar='K')
    mode.add_argument('--periodic-obstruction', type=int, metavar='PERIOD')
    mode.add_argument('--audit', metavar='JSON')
    mode.add_argument('--audit-repair', metavar='JSON')
    mode.add_argument('--complete', metavar='JSON')
    mode.add_argument('--complete-family', metavar='JSON')
    args = parser.parse_args()
    try:
        if args.periodic_obstruction is not None:
            out = periodic_obstruction(args.periodic_obstruction, args.k)
        elif args.frontier_restriction is not None:
            out = frontier_restriction(args.frontier_restriction)
        else:
            with open(args.audit or args.audit_repair or args.complete or args.complete_family, encoding='utf-8') as stream:
                data = json.load(stream)
            if args.audit_repair:
                out = audit_repair_window(data['k'], data['period'], data['words'])
            elif args.complete_family:
                out = complete_family_first_arm(data['k'], data['centre'], data['prefix'],
                                                data['arm2'], data['arm3'])
            elif args.audit:
                out = audit_upper(data['lengths'], data['hole'], data['words'])
            else:
                out = complete_upper(data['lengths'], data['hole'], data['arm2'], data['arm3'])
        print(json.dumps(out, sort_keys=True))
        return 0
    except (ValueError, KeyError, TypeError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    raise SystemExit(main())
