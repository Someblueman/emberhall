#!/usr/bin/env python3
"""Modularly indistinguishable two-hole lifts; NOT homometric witnesses.

Standard library only. See T2661_SAME_PARITY.md for the lifting theorem,
exact rational-shell audit, finite search scope, and remaining open question.
"""
from __future__ import annotations
import argparse
from collections import Counter
from itertools import combinations, product
import json
import hashlib
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from residue_2660 import FRONTIER, BASE


def add(*polys):
    out = Counter()
    for p in polys:
        out.update(p)
    return {e: c for e, c in out.items() if c}


def scale(p, s):
    return {e: s*c for e, c in p.items() if s*c}


def shift(p, k):
    return {e+k: c for e, c in p.items()}


def mul(p, q):
    out = Counter()
    for e, c in p.items():
        for f, d in q.items():
            out[e+f] += c*d
    return {e: c for e, c in out.items() if c}


def star(p):
    return {-e: c for e, c in p.items()}


def frontier():
    return [[1 if ch == '+' else -1 if ch == '-' else 0 for ch in w]
            for w in FRONTIER]


def validate(words, centre, require_balance=True):
    if len(words) != 3 or centre not in (-1, 0, 1):
        raise ValueError('three arm words and a signed/omitted centre required')
    if any(not w or any(s not in (-1, 0, 1) for s in w) for w in words):
        raise ValueError('nonempty words with signs -1, 0, 1 required')
    if require_balance and centre + sum(map(sum, words)):
        raise ValueError('unequal set sizes')


def lift(words, centre, halves, cuts, patterns):
    """Insert W^(H/P) followed by (-W)^(H/P) after each cut."""
    validate(words, centre)
    _parameters(words, halves, cuts, patterns)
    out = []
    for w, h, c, b in zip(words, halves, cuts, patterns):
        block = list(b) * (h // len(b))
        out.append(w[:c] + block + [-s for s in block] + w[c:])
    return out


def _parameters(words, halves, cuts, patterns):
    if not (len(halves) == len(cuts) == len(patterns) == 3):
        raise ValueError('three halves, cuts and patterns required')
    periods = {len(b) for b in patterns}
    if len(periods) != 1 or 0 in periods:
        raise ValueError('one common positive pattern period required')
    for w, h, c, b in zip(words, halves, cuts, patterns):
        if type(h) is not int or h < 1 or h % len(b):
            raise ValueError('half lengths must be positive multiples of period')
        if type(c) is not int or not 0 <= c <= len(w):
            raise ValueError('cut outside base word')
        if any(s not in (-1, 1) for s in b):
            raise ValueError('inserted words must have signs +/-1')


def modular_profiles(words, centre, modulus):
    """Independent packed-integer pair count, using ordered depths.

    Within an arm the later depth minus the earlier is the distance;
    between arms the depths add. Zero distance residue includes positive
    distances divisible by modulus, never self-pairs.
    """
    validate(words, centre)
    if type(modulus) is not int or modulus < 1:
        raise ValueError('positive modulus required')
    # Each digit has room for every pair in the entire tree: additions
    # cannot carry between residue counts. Rotating the reversed histogram
    # adds all earlier depths in one integer operation, with no FFT/library.
    nvertices = 1+sum(map(len, words))
    bits = max(1, (nvertices*nvertices).bit_length())
    width = bits*modulus
    mask = (1 << width)-1
    units = [1 << (bits*((-r) % modulus)) for r in range(modulus)]
    profiles = []
    for sign in (1, -1):
        packed_counts = 0
        histograms = []
        for w in words:
            hist = [0] * modulus
            packed_hist = 0
            for d, s in enumerate(w, 1):
                if s != sign:
                    continue
                r = d % modulus
                shift_bits = bits*r
                packed_counts += ((packed_hist << shift_bits) & mask) | (packed_hist >> (width-shift_bits))
                packed_hist += units[r]
                hist[r] += 1
            histograms.append(hist)
        digit_mask = (1 << bits)-1
        counts = [(packed_counts >> (bits*r)) & digit_mask for r in range(modulus)]
        for a, b in combinations(histograms, 2):
            for r, n in enumerate(a):
                for s, k in enumerate(b):
                    counts[(r+s) % modulus] += n*k
        if centre == sign:
            for hist in histograms:
                for r, n in enumerate(hist):
                    counts[r] += n
        profiles.append(counts)
    return profiles


def exact_numerator(words, centre, halves, cuts, patterns, require_balance=True):
    """Return 2(1-z)(1-z^P)(distance_profile_left-right), sparsely.

    Audits the entire inflated tree exactly without materializing it.
    Uses Laurent polynomials internally; final exponents are nonnegative.
    """
    validate(words, centre, require_balance)
    _parameters(words, halves, cuts, patterns)
    period = len(patterns[0])
    D = {0: 1, period: -1}
    lengths = [len(w)+2*h for w, h in zip(words, halves)]
    numerators, terms = [], []
    holes = [(None, 0)] if centre == 0 else []
    for a, (w, h, c, b) in enumerate(zip(words, halves, cuts, patterns)):
        singles = {d + (2*h if d > c else 0): s
                   for d, s in enumerate(w, 1) if s}
        holes.extend((a, d + (2*h if d > c else 0))
                     for d, s in enumerate(w, 1) if not s)
        inserted = mul({c+1+j: s for j, s in enumerate(b)},
                       {0: 1, h: -2, 2*h: 1})
        numerators.append(add(mul(D, singles), inserted))
        terms.append((singles, inserted, c+1, c+2*h))
    ends = add({0: 1}, *({L: -1} for L in lengths))
    result = add(scale(shift(mul(D, ends), 1), centre),
                 scale(shift(D, 1), 2*(centre+sum(map(sum, words)))))
    for a, N in enumerate(numerators):
        others = add({0: 1}, *({L: -1} for j, L in enumerate(lengths) if j != a))
        result = add(result, shift(mul(N, others), 1),
                     shift(star(N), lengths[a]+period+1))
    for a, d in holes:
        if a is None:
            hole_N = add(*numerators)
        else:
            singles, inserted, lo, hi = terms[a]
            # A hole is an original vertex, hence never inside insertion.
            low = mul(D, {e: s for e, s in singles.items() if e < d})
            high = mul(D, {e: s for e, s in singles.items() if e > d})
            if hi < d:
                low = add(low, inserted)
            elif lo > d:
                high = add(high, inserted)
            else:
                raise ArithmeticError('hole inside inserted block')
            hole_N = add(scale(shift(D, d), centre),
                         shift(add(*(N for j, N in enumerate(numerators) if j != a)), d),
                         scale(shift(star(low), d+period), -1), shift(high, -d))
        result = add(result, scale(mul({0: 1, 1: -1}, hole_N), -1))
    if any(e < 0 for e in result):
        raise ArithmeticError('uncancelled negative power')
    return result


def brute_difference(words, centre):
    """Quadratic oracle for small tests only."""
    profiles = []
    for sign in (1, -1):
        vertices = ([(0, 0)] if centre == sign else [])
        vertices += [(a, d) for a, w in enumerate(words, 1)
                     for d, s in enumerate(w, 1) if s == sign]
        profiles.append(Counter(abs(d-e) if a == b else d+e
                                for (a, d), (b, e) in combinations(vertices, 2)))
    return add(profiles[0], scale(profiles[1], -1))


def hensel_obstruction(words, centre, halves, cuts, period, free_base=False, defects=()):
    """Necessary mod-4 exact-shell test over ALL 2^(3P) block words.

    On failure returns a directly verified XOR certificate of coefficient
    equations. Consistency makes no claim of an integer or sign solution.
    Original base signs and cut locations remain fixed.
    """
    defects = tuple(sorted(set(defects)))
    if any(a not in range(3) or not 0 <= offset < halves[a] for a, offset in defects):
        raise ValueError('defect outside first half-word')
    patterns = ((1,)*period,)*3
    if free_base:
        words = [[int(bool(s)) for s in w] for w in words]
        centre = int(bool(centre))
    baseline = exact_numerator(words, centre, halves, cuts, patterns, require_balance=not free_base)
    if any(c % 2 for c in baseline.values()):
        raise ArithmeticError('shell numerator must be even')
    lengths = [len(w)+2*h for w, h in zip(words, halves)]
    holes = [(None, 0)] if centre == 0 else []
    for a, (w, h, cut) in enumerate(zip(words, halves, cuts)):
        holes.extend((a, d+(2*h if d > cut else 0))
                     for d, sign in enumerate(w, 1) if not sign)
    base_vertices = ([(None, 0)] if centre else []) + [
        (a, d+(2*h if d > cut else 0))
        for a, (w, h, cut) in enumerate(zip(words, halves, cuts))
        for d, sign in enumerate(w, 1) if sign]
    if free_base and len(base_vertices) % 2:
        raise ValueError('an even occupied base order is required')
    nvars = 3*period + len(defects) + (len(base_vertices) if free_base else 0)
    rhsbit = 1 << nvars
    rows = {e: rhsbit for e, c in baseline.items() if (c//2) % 2}
    for a, (h, cut, L) in enumerate(zip(halves, cuts, lengths)):
        direct = shift(add({0: 1}, *({end: -1} for j, end in enumerate(lengths) if j != a)), 1)
        reverse = {L+period+1: 1}
        for ha, d in holes:
            if ha != a:
                direct = add(direct, {d: -1, d+1: 1})
            elif d <= cut:  # insertion is above the hole
                direct = add(direct, {-d: -1, 1-d: 1})
            else:  # insertion is below the hole
                reverse = add(reverse, {d+period: 1, d+period+1: -1})
        for j, (arm, offset) in enumerate(defects):
            if arm != a:
                continue
            # Split one anti-paired position from its periodic residue class.
            insert = mul({0: 1, period: -1},
                         {cut+1+offset: 1, cut+1+offset+h: -1})
            column = add(mul(direct, insert), mul(reverse, star(insert)))
            bit = (1 << (a*period+offset % period)) ^ (1 << (3*period+j))
            for e, c in column.items():
                if c % 2:
                    rows[e] = rows.get(e, 0) ^ bit
        Q = {0: 1, h: -2, 2*h: 1}
        for j in range(period):
            insert = shift(Q, cut+1+j)
            column = add(mul(direct, insert), mul(reverse, star(insert)))
            bit = 1 << (a*period+j)
            for e, c in column.items():
                if c % 2:
                    rows[e] = rows.get(e, 0) ^ bit
    if free_base:
        D = {0: 1, period: -1}
        for j, (a, d) in enumerate(base_vertices):
            if a is None:
                column = shift(mul(D, add({0: 3}, *({L: -1} for L in lengths))), 1)
            else:
                others = add({0: 1}, *({L: -1} for b, L in enumerate(lengths) if b != a))
                column = add(scale(shift(D, 1), 2), shift(mul(D, others), d+1),
                             scale(shift(D, lengths[a]-d+1), -1))
            for ha, hd in holes:
                distance = d if ha is None else hd if a is None else abs(d-hd) if a == ha else d+hd
                column = add(column, scale(shift(mul(D, {0: 1, 1: -1}), distance), -1))
            bit = 1 << (3*period+len(defects)+j)
            for e, coefficient in column.items():
                if coefficient % 2:
                    rows[e] = rows.get(e, 0) ^ bit
        # Balance is also required; each paired insertion contributes zero.
        rows[-1] = sum(1 << (3*period+len(defects)+j) for j in range(len(base_vertices)))
        if (len(base_vertices)//2) % 2:
            rows[-1] ^= rhsbit
    equations = sorted((e, row) for e, row in rows.items() if row)
    basis = {}
    for index, (exponent, original) in enumerate(equations):
        row, source = original, 1 << index
        while row & (rhsbit-1):
            pivot = (row & (rhsbit-1)).bit_length()-1
            if pivot not in basis:
                basis[pivot] = row, source
                break
            other, support = basis[pivot]
            row ^= other
            source ^= support
        else:
            if row == rhsbit:
                support = [i for i in range(len(equations)) if (source >> i) & 1]
                # Verify the contradiction against the unevaluated equations.
                check = 0
                for i in support:
                    check ^= equations[i][1]
                if check != rhsbit:
                    raise ArithmeticError('invalid contradiction certificate')
                return {'period': period, 'variables': nvars, 'rank': len(basis),
                        'excluded': True, 'xor_exponents': [equations[i][0] for i in support]}
    return {'period': period, 'variables': nvars, 'rank': len(basis),
            'excluded': False, 'xor_exponents': []}


def verify_obstruction_by_shells(words, centre, halves, cuts, period, exponents, free_base=False, full_words=False, defects=(), max_indices=64):
    """Independent O(N * certificate size) check using graph neighbours.

    No polynomial multiplication or Gaussian elimination. At distance k,
    a vertex has at most two neighbours on its arm, the centre, and one
    vertex on each other arm. Aggregate these counts over each word variable.
    """
    _parameters(words, halves, cuts, ((1,)*period,)*3)
    lengths = [len(w)+2*h for w, h in zip(words, halves)]
    holes = {(a, d+(2*h if d > c else 0))
             for a, (w, h, c) in enumerate(zip(words, halves, cuts))
             for d, sign in enumerate(w, 1) if not sign}
    weights = Counter()
    for e in exponents:
        for k, coefficient in ((e, 1), (e-1, -1), (e-period, -1), (e-period-1, 1)):
            if k > 0:
                weights[k] += coefficient
    weights = {k: v for k, v in weights.items() if v}

    # Range sums of distance weights count all possible neighbours at
    # once. Removing each hole then gives the occupied graph shell exactly.
    largest = max(weights, default=0)
    prefix = [0]*(largest+1)
    for k in range(1, largest+1):
        prefix[k] = prefix[k-1]+weights.get(k, 0)

    def F(k):
        return prefix[min(max(k, 0), largest)]

    def kernel(a, d):
        total = int(-1 in exponents)
        if a is None:
            total += sum(F(L) for L in lengths)
            total -= sum(weights.get(hd, 0) for _, hd in holes)
        else:
            total += F(d-1)+F(lengths[a]-d)
            total += sum(F(d+L)-F(d) for j, L in enumerate(lengths) if j != a)
            if centre:
                total += weights.get(d, 0)
            total -= sum(weights.get(abs(d-hd) if a == ha else d+hd, 0)
                         for ha, hd in holes)
        return total

    base_coefficients = [kernel(None, 0)] if centre else []
    constant = centre*kernel(None, 0)
    defects = tuple(sorted(set(defects)))
    defect_indices = {entry: 3*period+j for j, entry in enumerate(defects)}
    coefficients = [0]*(sum(halves) if full_words else 3*period+len(defects))
    for a, (w, h, c) in enumerate(zip(words, halves, cuts)):
        for d, sign in enumerate(w, 1):
            if sign:
                value = kernel(a, d+(2*h if d > c else 0))
                constant += sign*value
                base_coefficients.append(value)
        for offset in range(2*h):
            j = offset % (h if full_words else period)
            phase = 1 if offset < h else -1
            index = (sum(halves[:a])+j if full_words else
                     defect_indices.get((a, offset % h), a*period+offset % period))
            coefficients[index] += phase*kernel(a, c+1+offset)
    if free_base:
        coefficients.extend(base_coefficients)
        constant = 0
    residue = (constant+sum(coefficients)) % 4
    verified = residue == 2 and all(v % 2 == 0 for v in coefficients)
    return {'verified': verified, 'baseline_residue_mod4': residue,
            'odd_variable_coefficients': sum(v % 2 != 0 for v in coefficients),
            'odd_variable_indices': [i for i, v in enumerate(coefficients) if v % 2][:max_indices]}


def refine_blocks(iterations=5, include_certificate=False):
    """Bounded attempt to escape by freeing non-periodic anti-paired sites."""
    if type(iterations) is not int or not 1 <= iterations <= 20:
        raise ValueError('refinement iterations must be between 1 and 20')
    halves, cuts = tuple(1330*b for b in BASE), (19, 0, 0)
    defects, history = set(), []
    for iteration in range(iterations+1):
        r = hensel_obstruction(frontier(), -1, halves, cuts, 1330, True, defects)
        history.append({'free_sites': len(defects), 'excluded': r['excluded'],
                        'certificate_equations': len(r['xor_exponents'])})
        if not r['excluded'] or iteration == iterations:
            break
        full = verify_obstruction_by_shells(frontier(), -1, halves, cuts, 1330,
                                           r['xor_exponents'], True, True, max_indices=2048)
        if full['odd_variable_coefficients'] > 2048:
            break
        previous = len(defects)
        for index in full['odd_variable_indices']:
            for a, h in enumerate(halves):
                if index < h:
                    defects.add((a, index))
                    break
                index -= h
        if len(defects) == previous:
            break
    verification = None
    if r['excluded']:
        verification = verify_obstruction_by_shells(frontier(), -1, halves, cuts, 1330,
                                                    r['xor_exponents'], True, defects=defects)
    if verification is not None and not verification['verified']:
        raise ArithmeticError('independent refinement certificate failed')
    certificate = r['xor_exponents']
    digest = hashlib.sha256(json.dumps(certificate, separators=(',', ':')).encode()).hexdigest()
    return {'history': history,
            'last_certificate_exponents': certificate if include_certificate or len(certificate) <= 200 else None,
            'last_certificate_count': len(certificate), 'last_certificate_sha256': digest,
            'last_independent_verification': verification,
            'consistent_is_not_existence': True}


def modular_shell(lengths, holes, centre_present, arm, depth, p):
    """Occupied distance-shell bins from one arm vertex, by interval counts."""
    def count(n, residue):
        return n//p+int(residue != 0 and residue <= n % p)
    out = []
    for r in range(p):
        n = count(depth-1, r)+count(lengths[arm]-depth, r)
        n += int(centre_present and depth % p == r)
        n += sum(count(L, (r-depth) % p) for j, L in enumerate(lengths) if j != arm)
        n -= sum(int((abs(depth-d) if arm == a else depth+d) % p == r)
                 for a, d in holes)
        out.append(n)
    return out


def mod4_halfword_obstruction(k=1):
    """All arbitrary anti-paired half-words, with FRONTIER colours fixed.

    For odd k, equality forces signed offset sums S0=S2 and S1=S3;
    their population differences are odd. For even k the modular lifting
    lemma itself preserves mod 4, so this obstruction is expressly absent.
    """
    if type(k) is not int or k < 1:
        raise ValueError('positive k required')
    halves = tuple(1330*k*b for b in BASE)
    lengths = tuple(b+2*h for b, h in zip(BASE, halves))
    cuts, holes = (19, 0, 0), ((0, 19), (0, lengths[0]))
    if k % 2 == 0:
        return {'k': k, 'excluded_for_fixed_frontier': False,
                'reason': 'every half length is divisible by 4; lifting lemma applies'}
    expected = [[-2, -1, 2, 1], [2, -1, -2, 1],
                [2, 1, -2, -1], [-2, 1, 2, -1]]
    for a, (h, cut) in enumerate(zip(halves, cuts)):
        for offset in range(4):
            d = cut+1+offset
            first = modular_shell(lengths, holes, True, a, d, 4)
            second = modular_shell(lengths, holes, True, a, d+h, 4)
            if [x-y for x, y in zip(first, second)] != expected[offset]:
                raise ArithmeticError('mod-4 shell signature mismatch')
    populations = [sum((h+3-r)//4 for h in halves) for r in range(4)]
    if populations[0]-populations[2] != 3 or populations[1]-populations[3] != 3:
        raise ArithmeticError('offset parity certificate mismatch')
    return {'k': k, 'excluded_for_fixed_frontier': True,
            'signature_by_offset': expected, 'offset_populations': populations,
            'reason': 'S0=S2 and S1=S3 required, but each population difference is odd'}


def audit_mod4_cut_classes(k=1):
    """Audit all cut residues while the long insertion separates its holes.

    Occupied mod-4 shells are periodic within each insertion. Geometry
    changes only when a cut crosses a hole. The 4^3 representatives thus
    cover every 19<=c1<99, 0<=c2<=79, 0<=c3<=23.
    """
    if type(k) is not int or k < 1 or k % 2 == 0:
        raise ValueError('positive odd k required')
    h = tuple(1330*k*b for b in BASE)
    lengths = tuple(b+2*x for b, x in zip(BASE, h))
    holes, weights = ((0, 19), (0, lengths[0])), (-2, -2, -1, 0)
    rotations = {tuple((4, 0, -4, 0)[(i+j) % 4] for i in range(4)) for j in range(4)}
    for cuts in product(range(19, 23), range(4), range(4)):
        baseline = 0
        for a, cut in enumerate(cuts):
            projected = []
            for offset in range(4):
                d = cut+1+offset
                first = modular_shell(lengths, holes, True, a, d, 4)
                second = modular_shell(lengths, holes, True, a, d+h[a], 4)
                projected.append(sum(w*(x-y) for w, x, y in zip(weights, first, second)))
            if tuple(projected) not in rotations:
                raise ArithmeticError('mod-4 cut-class signature mismatch')
            baseline += projected[0]+projected[1]
        if baseline % 8 != 4:
            raise ArithmeticError('mod-4 cut-class parity mismatch')
    return {'cut_residue_classes': 64, 'excluded_for_fixed_frontier': True,
            'weights_on_twice_pair_difference': weights, 'residue_mod8': 4}


def run(k=1, sweep=False):
    if type(k) is not int or k < 1:
        raise ValueError('k must be positive')
    words = frontier()
    halves = tuple(1330*k*b for b in BASE)
    cuts = (19, 0, 0)
    patterns = ((1, -1),)*3
    inflated = lift(words, -1, halves, cuts, patterns)
    modular = {}
    for p in (2, 5, 7, 19, 1330):
        left, right = modular_profiles(inflated, -1, p)
        if left != right:
            raise ArithmeticError(f'modular lift failed at {p}')
        modular[str(p)] = {'equal': True, 'pairs_per_side': sum(left), 'counts': left if p <= 19 else None}
    numerator = exact_numerator(words, -1, halves, cuts, patterns)
    result = {'t': 2660*k+1, 'lengths': list(map(len, inflated)),
              'size': (sum(map(len, inflated))-1)//2,
              'holes': [[1, 19], [1, 99+2*halves[0]]],
              'modular_profiles': modular, 'mod4_halfword_obstruction': mod4_halfword_obstruction(k),
              'mod4_cut_class_audit': audit_mod4_cut_classes(k) if k % 2 else None,
              'homometric': not numerator,
              'first_distance_discrepancy': min(numerator) if numerator else None,
              'left_minus_right_at_first': numerator[min(numerator)]//2 if numerator else 0}
    if sweep:
        choices = [(0, len(w)//2, len(w)) for w in words]
        n, hits, histogram = 0, [], Counter()
        # Each arm independently chooses one of ALL four period-two words.
        for c in product(*choices):
            for flat in product((-1, 1), repeat=6):
                b = tuple(tuple(flat[2*i:2*i+2]) for i in range(3))
                N = exact_numerator(words, -1, halves, c, b)
                n += 1
                if not N:
                    hits.append({'cuts': c, 'patterns': b})
                else:
                    histogram[min(N)] += 1
        result['finite_menu'] = {'tested': n, 'homometric_hits': hits,
                                'first_discrepancy_histogram': dict(sorted(histogram.items()))}
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--k', type=int, default=1)
    p.add_argument('--sweep', action='store_true')
    p.add_argument('--refine', type=int, metavar='N', help='free non-periodic sites for N rounds (1..20)')
    p.add_argument('--hensel', action='store_true', help='audit arbitrary words at selected periods')
    args = p.parse_args()
    result = run(args.k, args.sweep)
    if args.hensel:
        halves = tuple(1330*args.k*b for b in BASE)
        result['arbitrary_word_tests'] = [hensel_obstruction(frontier(), -1, halves, (19, 0, 0), p)
                                           for p in (2, 5, 7, 10, 14, 19, 38, 70, 1330)]
        result['free_base_test'] = hensel_obstruction(frontier(), -1, halves, (19, 0, 0), 1330, free_base=True)
        last = result['free_base_test']
        if last['excluded']:
            result['independent_shell_certificate'] = verify_obstruction_by_shells(
                frontier(), -1, halves, (19, 0, 0), 1330, last['xor_exponents'], free_base=True)
        if not result.get('independent_shell_certificate', {'verified': True})['verified']:
            raise ArithmeticError('independent shell certificate failed')
        result['unrestricted_half_word_escape'] = verify_obstruction_by_shells(
            frontier(), -1, halves, (19, 0, 0), 1330, [30590*args.k+2],
            free_base=True, full_words=True)
    if args.refine is not None:
        if args.k != 1:
            p.error('--refine currently audits only k=1')
        result['bounded_refinement'] = refine_blocks(args.refine)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
