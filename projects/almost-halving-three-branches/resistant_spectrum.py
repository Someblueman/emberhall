"""Exact sign reductions and endpoint checks for resistant tripod attempts.

Search limits are unknown. Every refusal names its support and word scope;
none of the reductions here decides arbitrary homometric pairs.
"""
import argparse
from collections import defaultdict
from fractions import Fraction
import json
import heapq
import itertools
import math
import time
from array import array
import reduced_folded_fibre as rf
from literal_shell_search import LiteralSearch


def residue_shell_groups(lengths, holes, period=4):
    """Exact column multiplicities after reducing shell exponents modulo period.

    Signs remain unrestricted. Between consecutive holes on an arm, each
    distance is affine in depth with slope +1 or -1; columns therefore repeat
    every period. This compilation never visits every vertex of a long arm.
    """
    holes = [tuple(hole) for hole in holes]
    bipartition_support_obstruction(lengths, holes)  # validate the support
    if type(period) is not int or period < 1:
        raise ValueError('require a positive residue period')
    import full_shorter_coupling as physical
    holes = set(holes)
    groups = defaultdict(int)

    def column(vertex):
        out = [0]*period
        for exponent, coefficient in physical.shell_column(lengths, holes, vertex).items():
            out[exponent % period] += coefficient
        return tuple(out)

    if (0, 0) not in holes:
        groups[column((0, 0))] += 1
    for arm, length in enumerate(lengths, 1):
        cuts = [0]+sorted(d for a, d in holes if a == arm)+[length+1]
        for left, right in zip(cuts, cuts[1:]):
            for depth in range(left+1, min(right, left+1+period)):
                groups[column((arm, depth))] += (right-1-depth)//period+1
    return dict(groups)


def fourth_root_mod8_states(groups):
    """All attainable four coefficient residues; an exact congruence relaxation.

    A group of n identical columns contributes (n-2k)*column for 0<=k<=n.
    Modulo eight only k modulo four matters. Compatibility is not a signing
    of the original integer shell equations, or even of their root quotient.
    """
    states = {(0, 0, 0, 0)}
    for column, count in sorted(groups.items()):
        if len(column) != 4 or type(count) is not int or count < 1:
            raise ValueError('require four-entry columns with positive multiplicities')
        contributions = {tuple((count-2*k)*c % 8 for c in column)
                         for k in range(min(count+1, 4))}
        states = {tuple((a+b) % 8 for a, b in zip(state, contribution))
                  for state in states for contribution in contributions}
    return states


def residue_zero_certificate(groups):
    """Find an odd group forced to zero by exact rational residue equations.

    Returns an integer combination of the residue rows supported on just
    that group. Every column dot product is checked before returning it.
    None means only that this particular necessary obstruction was absent.
    """
    items = sorted(groups.items())
    if not items:
        return None
    period = len(items[0][0])
    rows = [[Fraction(column[r]) for column, _ in items]
            +[Fraction(i == r) for i in range(period)] for r in range(period)]
    pivot_row = 0
    for j in range(len(items)):
        selected = next((i for i in range(pivot_row, period) if rows[i][j]), None)
        if selected is None:
            continue
        rows[pivot_row], rows[selected] = rows[selected], rows[pivot_row]
        factor = rows[pivot_row][j]
        rows[pivot_row] = [x/factor for x in rows[pivot_row]]
        for i in range(period):
            if i != pivot_row and rows[i][j]:
                factor = rows[i][j]
                rows[i] = [x-factor*y for x, y in zip(rows[i], rows[pivot_row])]
        pivot_row += 1
        if pivot_row == period:
            break
    for row in rows[:pivot_row]:
        support = [j for j, x in enumerate(row[:len(items)]) if x]
        if len(support) != 1 or items[support[0]][1] % 2 == 0:
            continue
        j = support[0]
        denominator = math.lcm(*(x.denominator for x in row))
        weights = [int(x*denominator) for x in row[len(items):]]
        coefficient = int(row[j]*denominator)
        certificate = dict(column=list(items[j][0]), count=items[j][1],
                           weights=weights, coefficient=coefficient)
        verify_residue_zero_certificate(groups, certificate)
        return certificate
    return None


def verify_residue_zero_certificate(groups, certificate):
    """Check only integer dot products, without trusting Gaussian elimination."""
    column = tuple(certificate['column'])
    weights, coefficient = certificate['weights'], certificate['coefficient']
    if (not groups or column not in groups or certificate['count'] != groups[column]
            or groups[column] % 2 != 1 or type(coefficient) is not int or not coefficient
            or len(weights) != len(column) or any(type(w) is not int for w in weights)):
        raise ValueError('invalid odd-group certificate')
    for other in groups:
        if len(other) != len(weights):
            raise ValueError('inconsistent residue dimensions')
        actual = sum(a*b for a, b in zip(weights, other))
        if actual != (coefficient if other == column else 0):
            raise ValueError('row combination does not isolate the claimed group')
    return True


def verify_residue_parity_certificate(groups, certificate):
    """Verify an integer row combination whose primitive coefficients have odd parity.

    Each aggregate sign sum has the parity of its group multiplicity. If
    w*C is divisible by d, then (w*C/d)*S=0 is a necessary integer equation.
    An odd value of (w*C/d)*counts contradicts it. Only integer arithmetic
    enters this checker; no diagonalization or rank claim is trusted.
    """
    weights, divisor = certificate['weights'], certificate['divisor']
    if (not groups or type(divisor) is not int or divisor < 1 or not weights
            or any(type(w) is not int for w in weights)):
        raise ValueError('invalid residue parity certificate')
    parity = 0
    for column, count in groups.items():
        if len(column) != len(weights) or type(count) is not int or count < 1:
            raise ValueError('invalid residue group')
        value = sum(a*b for a, b in zip(weights, column))
        if value % divisor:
            raise ValueError('row combination is not divisible by the claimed divisor')
        parity ^= (value//divisor*count) % 2
    if not parity:
        raise ValueError('row combination has no parity contradiction')
    return True


def residue_integer_parity(groups, seconds=10, max_bits=1024, retain_kernel=False):
    """Decide unbounded integer aggregate feasibility with prescribed parities.

    Integer Euclidean row/column operations diagonalize C to U*C*V=D,
    with U,V unimodular. At a diagonal pivot d the primitive row U*C/d
    must have even dot product with the group counts. These conditions are
    sufficient for unbounded aggregates, since V preserves the integer
    lattice. They say nothing about the bounds |S_j|<=count_j. Resource
    limits return unknown; every refusal has a separately checked witness.
    """
    if (not groups or not math.isfinite(seconds) or seconds <= 0
            or type(max_bits) is not int or max_bits < 1):
        raise ValueError('require nonempty groups and positive resource limits')
    items = sorted(groups.items())
    period, size = len(items[0][0]), len(items)
    if (not period or any(len(c) != period or any(type(x) is not int for x in c)
                          or type(n) is not int or n < 1 for c, n in items)):
        raise ValueError('invalid residue groups')
    matrix = [[column[r] for column, _ in items] for r in range(period)]
    transform = [[int(i == j) for j in range(period)] for i in range(period)]
    peak_bits = max(abs(x).bit_length() for row in matrix for x in row)
    started, rank = time.monotonic(), 0
    operations = []
    parities = [n % 2 for _, n in items]

    def swap_columns(a, b):
        for row in matrix:
            row[a], row[b] = row[b], row[a]
        if retain_kernel:
            operations.append(('swap', a, b))
            parities[a], parities[b] = parities[b], parities[a]

    if retain_kernel:
        # Prefer large groups as pivots: their sums have room to absorb the
        # small free sums. Record this permutation in the same reversible map.
        order = list(range(size))
        for k, target in enumerate(sorted(order, key=lambda j: (-items[j][1], j))):
            j = order.index(target)
            swap_columns(k, j)
            order[k], order[j] = order[j], order[k]

    def limited():
        reason = ('coefficient_limit' if peak_bits > max_bits else
                  'time_limit' if time.monotonic()-started >= seconds else None)
        return (dict(status='unknown', reason=reason, pivots=rank,
                     all_pairs_decided=False) if reason else None)

    for k in range(min(period, size)):
        stopped = limited()
        if stopped:
            return stopped
        position = min(((abs(matrix[i][j]), j, i) if retain_kernel else
                        (abs(matrix[i][j]), i, j)
                        for i in range(k, period) for j in range(k, size) if matrix[i][j]),
                       default=None)
        if position is None:
            break
        if retain_kernel:
            _, j, i = position
        else:
            _, i, j = position
        matrix[k], matrix[i] = matrix[i], matrix[k]
        transform[k], transform[i] = transform[i], transform[k]
        swap_columns(k, j)
        while True:
            stopped = limited()
            if stopped:
                return stopped
            i = next((i for i in range(k+1, period) if matrix[i][k]), None)
            if i is not None:
                quotient = matrix[i][k]//matrix[k][k]
                matrix[i] = [x-quotient*y for x, y in zip(matrix[i], matrix[k])]
                transform[i] = [x-quotient*y for x, y in zip(transform[i], transform[k])]
                peak_bits = max(peak_bits, *(abs(x).bit_length()
                                            for x in matrix[i]+transform[i]))
                if matrix[i][k]:
                    matrix[k], matrix[i] = matrix[i], matrix[k]
                    transform[k], transform[i] = transform[i], transform[k]
                continue
            j = next((j for j in range(k+1, size) if matrix[k][j]), None)
            if j is not None:
                quotient = matrix[k][j]//matrix[k][k]
                for row in matrix:
                    row[j] -= quotient*row[k]
                    peak_bits = max(peak_bits, abs(row[j]).bit_length())
                if retain_kernel:
                    operations.append(('subtract', k, j, quotient))
                    parities[k] = (parities[k]+quotient*parities[j]) % 2
                if matrix[k][j]:
                    swap_columns(k, j)
                continue
            break
        rank += 1
        weights = transform[k]
        dots = [sum(a*b for a, b in zip(weights, column)) for column, _ in items]
        divisor = math.gcd(*dots)
        if divisor != abs(matrix[k][k]):
            raise AssertionError('unimodular diagonal pivot has the wrong row gcd')
        if sum(value//divisor*count for value, (_, count) in zip(dots, items)) % 2:
            certificate = dict(weights=[(w+divisor) % (2*divisor)-divisor for w in weights],
                               divisor=divisor)
            verify_residue_parity_certificate(groups, certificate)
            return dict(status='support_refused_by_residue_parity', certificate=certificate,
                        pivots=rank, all_pairs_decided=False)
    result = dict(status='compatible_unbounded_aggregates', pivots=rank,
                  all_pairs_decided=False)
    if retain_kernel:
        if any(parities[:rank]):
            raise AssertionError('diagonal kernel parity disagrees with primitive rows')
        result['kernel'] = dict(operations=operations, parities=parities, rank=rank)
    return result


def verify_bounded_residue_witness(groups, values):
    """Check actual integer sums, their parity and their physical bounds.

    Any accepted sums can be realized by signs independently within each
    column group. This verifies the projected shell equations only.
    """
    items = sorted(groups.items())
    if not items or len(values) != len(items):
        raise ValueError('wrong aggregate count')
    period = len(items[0][0])
    for (column, count), value in zip(items, values):
        if (not period or len(column) != period or any(type(c) is not int for c in column)
                or type(count) is not int or count < 1
                or type(value) is not int or abs(value) > count
                or (value-count) % 2):
            raise ValueError('invalid bounded aggregate')
    if any(sum(column[r]*value for (column, _), value in zip(items, values))
           for r in range(period)):
        raise ValueError('aggregate sums do not cancel the exact residue rows')
    return True


def residue_bounded_search(groups, seconds=10, max_bits=1024, attempts=256):
    """Search the exact integer kernel; failure is unknown, never refusal."""
    if type(attempts) is not int or attempts < 1:
        raise ValueError('require a positive attempt count')
    started = time.monotonic()
    result = residue_integer_parity(groups, seconds, max_bits, retain_kernel=True)
    kernel = result.pop('kernel', None)
    if kernel is None:
        return result
    # A fixed seed makes the probe reproducible without making its failure a proof.
    import random
    rng = random.Random(0)
    parities, rank = kernel['parities'], kernel['rank']
    for attempt in range(attempts):
        if time.monotonic()-started >= seconds:
            break
        values = [0]*rank + [(p if attempt == 0 else
                  rng.choice((-1, 1)) if p else rng.choice((-2, 0, 2)))
                 for p in parities[rank:]]
        limited = False
        for index, operation in enumerate(reversed(kernel['operations'])):
            kind, a, b, *rest = operation
            if kind == 'swap':
                values[a], values[b] = values[b], values[a]
            else:
                values[a] -= rest[0]*values[b]
            if (max(abs(values[a]).bit_length(), abs(values[b]).bit_length()) > max_bits
                    or index % 256 == 0 and time.monotonic()-started >= seconds):
                limited = True
                break
        if limited:
            continue
        try:
            verify_bounded_residue_witness(groups, values)
        except ValueError:
            continue
        return dict(status='compatible_bounded_aggregates', aggregate_sums=values,
                    attempts=attempt+1, all_pairs_decided=False)
    return dict(status='unknown', reason='bounded_witness_not_found',
                unbounded_compatible=True, all_pairs_decided=False)


def verify_residue_aggregate_witness(groups, witness):
    """Independently verify unbounded compatibility from a Hadamard-sized modular vector."""
    items = sorted(groups.items())
    if not items:
        raise ValueError('require nonempty groups')
    period = len(items[0][0])
    if (not period or any(len(c)!=period or any(type(x) is not int for x in c)
                          or type(n) is not int or n<1 for c,n in items)):
        raise ValueError('invalid residue groups')
    norm_squared = max(sum(x*x for x in c) for c,_ in items)
    required = 1+min(period,len(items))*((norm_squared.bit_length()+1)//2)
    bits, values = witness['modulus_bits'], witness['aggregate_residues']
    if type(bits) is not int or bits != required or len(values) != len(items):
        raise ValueError('witness modulus does not meet the exact minor bound')
    modulus = 1 << bits
    if any(type(value) is not int or not 0<=value<modulus or value%2 != count%2
           for value,(_,count) in zip(values,items)):
        raise ValueError('aggregate witness has invalid residues or parities')
    if any(sum(value*column[r] for value,(column,_) in zip(values,items)) % modulus
           for r in range(period)):
        raise ValueError('aggregate witness fails a modular shell row')
    return True


def residue_dyadic_parity(groups, seconds=10, max_bits=1024, retain_witness=False):
    """The same complete unbounded relaxation, using bounded powers-of-two arithmetic.

    A Hadamard bound makes the modulus large enough to see every nonzero
    elementary divisor's two-adic valuation. Thus this is not a fixed small
    congruence probe. Modular row operations provide the same independently
    checkable integer parity certificates as Euclidean diagonalization.
    """
    if (not groups or not math.isfinite(seconds) or seconds <= 0
            or type(max_bits) is not int or max_bits < 1):
        raise ValueError('require nonempty groups and positive resource limits')
    items = sorted(groups.items())
    period, size = len(items[0][0]), len(items)
    if (not period or any(len(c) != period or any(type(x) is not int for x in c)
                          or type(n) is not int or n < 1 for c, n in items)):
        raise ValueError('invalid residue groups')
    norm_squared = max(sum(x*x for x in column) for column, _ in items)
    bits = 1+min(period,size)*((norm_squared.bit_length()+1)//2)
    if bits > max_bits:
        return dict(status='unknown', reason='coefficient_limit', required_bits=bits,
                    pivots=0, all_pairs_decided=False)
    modulus, mask = 1 << bits, (1 << bits)-1
    matrix = [[column[r] & mask for column, _ in items] for r in range(period)]
    transform = [[int(i == j) for j in range(period)] for i in range(period)]
    operations, parities = [], [count%2 for _,count in items]
    started, rank = time.monotonic(), 0

    def timed_out():
        return time.monotonic()-started >= seconds

    def unknown():
        return dict(status='unknown', reason='time_limit', modulus_bits=bits,
                    pivots=rank, all_pairs_decided=False)

    for k in range(min(period,size)):
        if timed_out():
            return unknown()
        position = min((((matrix[i][j] & -matrix[i][j]).bit_length()-1, i, j)
                        for i in range(k,period) for j in range(k,size) if matrix[i][j]),
                       default=None)
        if position is None:
            break
        valuation, i, j = position
        divisor = 1 << valuation
        matrix[k], matrix[i] = matrix[i], matrix[k]
        transform[k], transform[i] = transform[i], transform[k]
        for row in matrix:
            row[k], row[j] = row[j], row[k]
        if retain_witness and k != j:
            operations.append(('swap',k,j))
            parities[k],parities[j] = parities[j],parities[k]
        inverse = pow(matrix[k][k]//divisor, -1, modulus)
        matrix[k] = [x*inverse & mask for x in matrix[k]]
        transform[k] = [x*inverse & mask for x in transform[k]]
        for i in range(k+1,period):
            if timed_out():
                return unknown()
            quotient = matrix[i][k]//divisor
            if quotient:
                matrix[i] = [(x-quotient*y) & mask for x,y in zip(matrix[i],matrix[k])]
                transform[i] = [(x-quotient*y) & mask for x,y in zip(transform[i],transform[k])]
        for j in range(k+1,size):
            if timed_out():
                return unknown()
            quotient = matrix[k][j]//divisor
            if quotient:
                for row in matrix:
                    row[j] = (row[j]-quotient*row[k]) & mask
                if retain_witness:
                    operations.append(('add',k,j,quotient))
                    parities[k] ^= (quotient&1)*parities[j]
        rank += 1
        weights = transform[k]
        # Exact dots, not residues, are passed to the independent checker.
        dots = [sum(a*b for a,b in zip(weights,column)) for column,_ in items]
        if any(value % divisor for value in dots):
            raise AssertionError('dyadic pivot does not divide the original row combination')
        if sum(value//divisor*count for value,(_,count) in zip(dots,items)) % 2:
            certificate = dict(weights=[(w+divisor) % (2*divisor)-divisor for w in weights],
                               divisor=divisor)
            verify_residue_parity_certificate(groups,certificate)
            return dict(status='support_refused_by_residue_parity', certificate=certificate,
                        modulus_bits=bits, pivots=rank, all_pairs_decided=False)
    result = dict(status='compatible_unbounded_aggregates', modulus_bits=bits,
                  pivots=rank, all_pairs_decided=False)
    if retain_witness:
        if any(parities[:rank]):
            raise AssertionError('diagonal aggregate parities disagree with row certificates')
        values = [0]*rank+parities[rank:]
        for operation in reversed(operations):
            _,k,j = operation[:3]
            if operation[0]=='swap':
                values[k],values[j] = values[j],values[k]
            else:
                values[k] = (values[k]-operation[3]*values[j]) & mask
        witness = dict(modulus_bits=bits,aggregate_residues=values)
        verify_residue_aggregate_witness(groups,witness)
        result['witness'] = witness
    return result


def resistant_residue_audit(max_period=256, seconds=900, max_bits=1024, bounded=False):
    """Audit every resistant scale phase for fixed odd and moving odd holes.

    For period p, increasing t by 2p preserves all residue columns and
    multiplicities modulo two on these supports. All varying segments in the
    chosen representatives exceed p; the fixed shallow patch is unchanged.
    The exact 2p/gcd(7980,2p) scale phases
    therefore cover every t=7980m+1, m>=1, at each listed period. This is
    only a residue relaxation audit, never a full physical signing. In bounded
    mode group counts only increase along each phase, so a bounded witness
    at its first scale stays valid at every later scale in that phase.
    """
    if (type(max_period) is not int or not 4 <= max_period <= 256 or max_period & (max_period-1)
            or not math.isfinite(seconds) or seconds <= 0):
        raise ValueError('require a power-of-two maximum period in 4..256 and a positive budget')
    started, reports, cache, complete = time.monotonic(), [], {}, True
    period = 4
    while period <= max_period:
        phases = 2*period//math.gcd(7980,2*period)
        report = dict(period=period,scale_phases=phases,cases=0,compatible=0,refused=0,unknown=0)
        for m in range(1,phases+1):
            scale = 7980*m+1
            lengths = [99*scale,79*scale,23*scale]
            for mode, shallow in (('fixed',19),('moving',19*scale)):
                remaining = seconds-(time.monotonic()-started)
                if remaining <= 0:
                    return dict(complete=False,reason='time_limit',reports=reports+[report],
                                all_pairs_decided=False)
                holes = [(1,shallow),(1,99*scale)]
                groups = residue_shell_groups(lengths,holes,period)
                key = tuple(sorted((column,count if bounded else count%2)
                                   for column,count in groups.items()))
                if key not in cache:
                    solver = residue_bounded_search if bounded else residue_dyadic_parity
                    cache[key] = solver(groups,remaining,max_bits)
                result = cache[key]
                report['cases'] += 1
                expected = 'compatible_bounded_aggregates' if bounded else 'compatible_unbounded_aggregates'
                if result['status']==expected:
                    if bounded:
                        verify_bounded_residue_witness(groups,result['aggregate_sums'])
                    report['compatible'] += 1
                elif result['status']=='support_refused_by_residue_parity':
                    report['refused'] += 1
                    verify_residue_parity_certificate(groups,result['certificate'])
                    if 'first_refusal' not in report:
                        report['first_refusal'] = dict(result,mode='residue_parity',t=scale,
                                                       holes=holes,period=period,support_kind=mode)
                else:
                    report['unknown'] += 1
                    complete = False
                    if 'first_unknown' not in report:
                        report['first_unknown'] = dict(t=scale,support_kind=mode,
                                                      reason=result.get('reason','unknown'))
        reports.append(report)
        period *= 2
    return dict(complete=complete,reports=reports,distinct_signatures=len(cache),
                scope=('bounded residue aggregates on two named supports only' if bounded else
                       'unbounded integer aggregate parities on two named supports only'),
                all_pairs_decided=False)


def residue_gap_representatives(length, hole_count):
    """Cover every ordered placement of <=2 arm holes up to mod-eight columns.

    Gaps count retained vertices. Replacing g>=12 by 12+(g-12)%32
    preserves its column residues and each column's available signed sums
    modulo eight. Reduced gaps lie in 0..43. Lift the first large gap to
    recover the specified arm length. No representative means no placement.
    """
    if (type(length) is not int or length < 1 or
            type(hole_count) is not int or not 0 <= hole_count <= min(2, length)):
        raise ValueError('require a positive length and zero, one or two holes')
    for gaps in itertools.product(range(44), repeat=hole_count+1):
        extra = length-hole_count-sum(gaps)
        if extra < 0 or extra % 32:
            continue
        lifted = list(gaps)
        if extra:
            large = next((j for j, gap in enumerate(gaps) if gap >= 12), None)
            if large is None:
                continue
            lifted[large] += extra
        depth, holes = 0, []
        for gap in lifted[:-1]:
            depth += gap+1
            holes.append(depth)
        yield tuple(holes)


def fourth_root_mod8_census():
    """Finite replay for all two-hole supports at t=1 mod 4, t>=9.

    Each arm length exceeds 131, so representability of reduced gaps depends
    only on length modulo 32. The eight scale phases below cover all cases.
    This classifies a congruence and an exact forced-zero obstruction, not
    homometric pairs. The two reports must not be conflated.
    """
    cache, zeros, counts, phase_counts = {}, {}, defaultdict(int), []
    for scale in (33, 37, 9, 13, 17, 21, 25, 29):
        lengths = [99*scale, 79*scale, 23*scale]
        single = [list(residue_gap_representatives(n, 1)) for n in lengths]

        def supports():
            for arm, length in enumerate(lengths, 1):
                for depths in residue_gap_representatives(length, 2):
                    yield {(arm, d) for d in depths}
                for depths in single[arm-1]:
                    yield {(0, 0), (arm, depths[0])}
            for a, b in itertools.combinations(range(1, 4), 2):
                for da in single[a-1]:
                    for db in single[b-1]:
                        yield {(a, da[0]), (b, db[0])}

        phase = defaultdict(int)
        for holes in supports():
            groups = residue_shell_groups(lengths, holes)
            # n modulo eight and min(n,3) determine the available residues.
            key = tuple(sorted((c, n % 8, min(n, 3)) for c, n in groups.items()))
            if key not in cache:
                cache[key] = (0, 0, 0, 0) in fourth_root_mod8_states(groups)
                zeros[key] = residue_zero_certificate(groups) is not None
            odd_refused = bipartition_support_obstruction(lengths, holes)['obstructed']
            label = ('odd_shell_refused' if odd_refused else 'compatible')
            if cache[key] == odd_refused:
                raise AssertionError('fourth-root congruence differs from odd-shell condition')
            phase[label] += 1
            counts[label] += 1
            if not odd_refused:
                label = 'additional_exact_refusal' if zeros[key] else 'not_decided'
                phase[label] += 1
                counts[label] += 1
        phase_counts.append(dict(scale_residue=scale % 32, **phase))
    return dict(scope='fourth-root congruence and exact odd-group zero obstruction only',
                scale_condition='t >= 9 and t = 1 modulo 4',
                complete=True, all_pairs_decided=False, distinct_signatures=len(cache),
                representatives=counts['odd_shell_refused']+counts['compatible'],
                counts=dict(counts), phases=phase_counts)


def split_edge_system(hole=19, patch=0, pieces=2, word_period=1, hole_offset=0,
                      _constant_bounds=None, hole_piece=0):
    """Formal (1-z**word_period)K for t=pieces*L+1.

    Each piece has L vertices; its first/last patch vertices are independent.
    Each remaining piece repeats its own independent word of word_period
    signs. Require word_period|L, word_period|2*patch, L>=2*patch+word_period.
    Exponents are pairs (coefficient of L, constant), never sampled ranks.
    Holes are first-arm vertices hole*t+hole_offset and 99*t. The offset
    is within a free endpoint patch; hole_piece shifts the hole by that
    many whole piece lengths L. No repeated word crosses a hole.
    This is an ansatz, not a reduction of every possible signing.
    """
    if type(hole) is not int or not 1 <= hole < 99:
        raise ValueError('require 1<=hole<99')
    if type(patch) is not int or patch < 0:
        raise ValueError('require a nonnegative patch width')
    if type(pieces) is not int or pieces < 2:
        raise ValueError('require at least two pieces')
    if type(word_period) is not int or word_period < 1 or (2*patch)%word_period:
        raise ValueError('require a positive word period dividing twice the patch width')
    if type(hole_offset) is not int or abs(hole_offset)>patch:
        raise ValueError('require an integer hole offset within the endpoint patch')
    if (type(hole_piece) is not int or not 0<=hole_piece<pieces
            or (hole_piece and (not patch or hole_offset<1-patch))):
        raise ValueError('require a valid hole piece and a hole inside its endpoint patch')
    lengths = (99,79,23)
    keys, rows = [], defaultdict(lambda:defaultdict(int))

    def add(a,b): return a[0]+b[0],a[1]+b[1]
    def neg(a): return -a[0],-a[1]
    def old(q): return pieces*q,q

    holes = (add(old(hole),(hole_piece,hole_offset)),old(99))
    def before(left,right):
        # Prove strict order for every admissible L, not just lexicographically.
        slope,constant=add(right,neg(left))
        return slope>=0 and slope*(2*patch+word_period)+constant>0

    def terms(arm, lo, hi, centre=False):
        # Entries (slope in d, affine offset, coefficient) of a physical K column.
        if centre:
            out = [(0,(0,1),1)]+[(0,add(old(n),(0,1)),-1) for n in lengths]
        else:
            out = [(1,(0,1),1),(-1,add(old(lengths[arm-1]),(0,1)),-1)]
            out += [(1,add(old(n),(0,1)),-1) for a,n in enumerate(lengths,1) if a!=arm]
        for h in holes:
            if centre:
                slope,offset = 0,h
            elif arm==1 and before(hi,h):
                slope,offset = -1,h
            elif arm==1 and before(h,lo):
                slope,offset = 1,neg(h)
            elif arm==1:
                raise AssertionError('a repeated interval crosses a hole')
            else:
                slope,offset = 1,h
            out += [(slope,offset,-1),(slope,add(offset,(0,1)),1)]
        return out

    def column(key,arm,edge,lo,hi,single=False,centre=False):
        if single and arm==1 and lo in holes:
            return
        i=len(keys);keys.append(key)
        for slope,offset,c in terms(arm,lo,hi,centre):
            if single:
                e=add(tuple(slope*x for x in lo),offset)
                ends=((e,c),(add(e,(0,word_period)),-c))
            elif slope==1:
                ends=((add(lo,offset),c),(add(add(hi,offset),(0,word_period)),-c))
            elif slope==-1:
                ends=((add(neg(hi),offset),c),(add(add(neg(lo),offset),(0,word_period)),-c))
            else:
                raise AssertionError('a run has constant distance')
            if _constant_bounds is not None:
                _constant_bounds.extend(e[1] for e,value in ends)
            for e,value in ends:rows[e][i]+=value

    column(('old',0,0),0,0,(0,0),(0,0),True,True)
    for arm,n in enumerate(lengths,1):
        for q in range(1,n+1):
            column(('old',arm,q),arm,q,old(q),old(q),True)
        for edge in range(n):
            for half in range(pieces):
                lo=(pieces*edge+half,edge+1)
                hi=(pieces*edge+half+1,edge)
                for side in (0,1):
                    for r in range(patch):
                        d=add(lo,(0,r)) if side==0 else add(hi,(0,-r))
                        column(('patch',arm,edge,half,side,r),arm,edge,d,d,True)
                for j in range(1,word_period+1):
                    key=(('half',arm,edge,half) if word_period==1 else
                         ('word',arm,edge,half,j))
                    column(key,arm,edge,add(lo,(0,patch+j-1)),
                           add(hi,(0,-patch-word_period+j)))
    return keys,{e:{i:c for i,c in row.items() if c} for e,row in rows.items() if any(row.values())}


def split_endpoint_system(hole=19,patch=0,word_period=1,hole_offset=0):
    """Fixed necessary endpoint rows for every number p>=2 of word pieces.

    Retain slope exponents divisible by p. Only the first and last pieces
    enter: a forward run contributes at r and r+1, a reflected run at -r-1
    and -r, modulo p. The p=2 extraction therefore defines the uniform map.
    Free patches and repeating words are allowed. Only the outermost patch
    signs and words at the two edge ends occur in these rows.
    """
    keys,formal=split_edge_system(hole,patch,2,word_period,hole_offset)
    rows={(q//2,c):row for (q,c),row in formal.items() if q%2==0}
    return keys,dict(sorted(rows.items()))


def split_bulk_system():
    """Necessary aggregate rows for all flat pieces with finite end patches.

    In (1-z)K retain q=0 mod p, then sum every constant offset c.
    Single-vertex columns cancel; only the first/last long pieces survive.
    Renaming these two signs gives the same rows for all p>=2,w>=0.
    The physical-to-formal converse is valid when L>=179+2w.
    """
    lengths = (99,79,23)
    keys = [('first' if side==0 else 'last',arm,edge)
            for arm,n in enumerate(lengths,1) for edge in range(n) for side in (0,1)]
    rows = defaultdict(lambda:defaultdict(int))
    for i,(side,arm,e) in enumerate(keys):
        n = lengths[arm-1]
        if side=='first':
            terms = [(e,1),(n-e,1)]+[(e+m,-1) for j,m in enumerate(lengths,1) if j!=arm]
        else:
            terms = [(e+1,-1),(n-e-1,-1)]+[(e+m+1,1) for j,m in enumerate(lengths,1) if j!=arm]
        for q,value in terms: rows[q][i] += value
    return keys,{q:{i:c for i,c in row.items() if c}
                 for q,row in sorted(rows.items()) if any(row.values())}


def flat_piece_any_holes_bound(piece_length,pieces=2,patch=0):
    """Exclude sufficiently long flat interiors with ANY two physical holes.

    A full-support flat signing has a nonzero K plateau of length L-178.
    Two arbitrary holes and the patch changes affect at most the stated
    number of coefficient positions. This support-count argument makes no
    assumption about hole alignment. It is still only a flat-word theorem.
    """
    if (type(pieces) is not int or pieces<2 or type(patch) is not int or patch<0
            or type(piece_length) is not int or piece_length<2*patch+1):
        raise ValueError('require pieces>=2, patch>=0, and piece length>=2*patch+1')
    split_bulk_refusal()  # fixed independent parity proof of a nonzero plateau
    # 201p constant intervals, 202 old points, and at most one split per hole.
    hole_correction_support = 2*(2*(201*pieces+202+1))
    changed_vertices = 402*pieces*patch+2
    correction_support = hole_correction_support+8*changed_vertices
    plateau = max(0,piece_length-178)
    refused = plateau>correction_support
    return dict(mode='flat_any_holes',pieces=pieces,patch=patch,piece_length=piece_length,
                t=pieces*piece_length+1,nonzero_plateau_lower_bound=plateau,
                correction_support_upper_bound=correction_support,
                minimum_refused_piece_length=804*pieces+3216*pieces*patch+1007,
                status='flat_ansatz_refused' if refused else 'not_decided_by_bound',
                all_pairs_decided=False,
                scope='constant piece interiors with endpoint patches; any two physical holes')


def split_bulk_refusal():
    keys,rows = split_bulk_system()
    original = list(rows.values())
    # A fixed square wave gives a short human-readable parity argument:
    # the selected sum has 24 coefficients +2 and 25 coefficients -2.
    certificate = [i for i,q in enumerate(rows) if q%8>=4]
    coefficients = defaultdict(int)
    for i in certificate:
        for j,c in original[i].items(): coefficients[j] += c
    nonzero = [c for c in coefficients.values() if c]
    if sorted(nonzero)!=[-2]*25+[2]*24 or not verify_refusal(original,certificate):
        raise AssertionError('flat-interior bulk refusal was not verified')
    return dict(mode='split_bulk',status='ansatz_refused_by_parity',
                variables=len(keys),rows=len(rows),certificate=certificate,
                minimum_piece_length='179+2*patch',all_pairs_decided=False,
                scope='all p>=2 constant interiors, arbitrary finite end patches and holes at old vertices')


def split_endpoint_refusal(hole=19,patch=0,word_period=1,hole_offset=0):
    keys,rows=split_endpoint_system(hole,patch,word_period,hole_offset)
    certificate,_=binary_elimination(list(rows.values()))
    if certificate is None or not verify_refusal(list(rows.values()),certificate):
        raise ValueError('the endpoint rows have no verified parity refusal')
    constants=[]
    split_edge_system(hole,patch,2,word_period,hole_offset,constants)
    # Raw constants are independent of p; collect before any p-specific
    # cancellations could hide a specialization collision.
    span=max(constants)-min(constants)
    minimum=max(2*patch+word_period,span+1)
    minimum=((minimum+word_period-1)//word_period)*word_period
    return dict(mode='split_endpoints',status='ansatz_refused_by_parity',
                hole=hole,patch=patch,word_period=word_period,hole_offset=hole_offset,
                variables=len(keys),rows=len(rows),certificate=certificate,
                exponent_constant_span=span,minimum_piece_length=minimum,
                piece_length_divisor=word_period,
                scope='all p>=2 equal pieces with these words, patches and shifted holes; L at least minimum_piece_length',
                all_pairs_decided=False)


def enumerate_binary_fibre(size,rows,max_free=16,seconds=None):
    """Exhaust the necessary parity fibre when it has few free coordinates.

    The echelon pivot is the largest index in its row, so ascending pivots
    recover each binary assignment uniquely. Every recovered signing is
    checked against the untouched integer rows, not just their parities.
    """
    if type(max_free) is not int or not 0<=max_free<=20:
        raise ValueError('require a free-coordinate limit between zero and twenty')
    if seconds is not None and (type(seconds) not in (int,float) or not math.isfinite(seconds) or seconds<=0):
        raise ValueError('require a positive finite enumeration time')
    deadline=None if seconds is None else time.monotonic()+seconds
    certificate,basis=binary_elimination(rows)
    if certificate is not None:
        return dict(status='unsat',complete=True,enumerated=0,certificate=certificate)
    free=sorted(set(range(size))-set(basis))
    if len(free)>max_free:
        return dict(status='unknown',complete=False,free=len(free),enumerated=0)
    ordered=sorted(basis.items())
    for choice in range(1<<len(free)):
        if deadline is not None and time.monotonic()>=deadline:
            return dict(status='unknown',complete=False,free=len(free),enumerated=choice)
        bits=sum(1<<i for j,i in enumerate(free) if choice>>j&1)
        for pivot,(mask,rhs) in ordered:
            if rhs^((mask&bits).bit_count()&1):bits|=1<<pivot
        if all(not sum(c*(1 if bits>>i&1 else -1) for i,c in row.items()) for row in rows):
            return dict(status='sat',complete=True,free=len(free),enumerated=choice+1,
                        values=[1 if bits>>i&1 else -1 for i in range(size)])
    return dict(status='unsat',complete=True,free=len(free),enumerated=1<<len(free))


def split_edge_search(hole=19,patch=0,seconds=30,nodes=10000,pieces=2,word_period=1,hole_offset=0,hole_piece=0):
    """Try literal edge-piece plateaus; a timeout has no mathematical outcome."""
    start=time.monotonic()
    constants=[]
    keys,formal=split_edge_system(hole,patch,pieces,word_period,hole_offset,constants,hole_piece)
    original=list(formal.values())
    result=dict(mode='split_edge',hole=hole,hole_offset=hole_offset,hole_piece=hole_piece,patch=patch,pieces=pieces,word_period=word_period,
                variables=len(keys),rows=len(original),minimum_piece_length=2*patch+word_period,
                piece_length_divisor=word_period,all_pairs_decided=False,
                scope='independent periodic edge-piece interiors with free endpoint patches')
    def done(status,**extra):
        answer=dict(**result,status=status,elapsed=time.monotonic()-start,**extra)
        if status.startswith('ansatz_refused'):
            minimum=max(2*patch+word_period,max(constants)-min(constants)+1)
            answer['minimum_piece_length']=((minimum+word_period-1)//word_period)*word_period
        return answer
    certificate,basis=binary_elimination(original)
    if certificate is not None:
        return done('ansatz_refused_by_parity',certificate=certificate)
    if len(keys)-len(basis)<=16:
        remaining=seconds-(time.monotonic()-start)
        if remaining<=0:return done('unknown')
        audit=enumerate_binary_fibre(len(keys),original,seconds=remaining)
        result['parity_free']=audit['free']
        result['enumerated']=audit['enumerated']
        if audit['status']=='unsat':return done('ansatz_refused_by_binary_fibre')
        if not audit['complete']:return done('unknown')
        restored=audit['values']
        return done('sat',assignment=[[list(k),v] for k,v in zip(keys,restored)])
    joint=joint_sign_closure(len(keys),original,seconds,short_recovery=True)
    result['closure']=joint['history']
    if joint['conflict']:return done('ansatz_refused_by_joint_fields')
    remaining=seconds-(time.monotonic()-start)
    if not joint['complete'] or remaining<=0:return done('unknown')
    certificate,basis=binary_elimination(joint['rows'])
    if certificate is not None:return done('ansatz_refused_after_quotient')
    engine=make_engine(joint['size'],joint['rows'],basis,remaining,nodes,'connected')
    i,s=joint['aliases'][0]
    status,values=engine.run({i:s})
    if values is None:return done(status,nodes=engine.nodes)
    restored=[sign*values[i] for i,sign in joint['aliases']]
    if any(sum(c*restored[i] for i,c in row.items()) for row in original):
        raise AssertionError('split-edge lift fails untouched formal rows')
    return done(status,nodes=engine.nodes,assignment=[[list(k),v] for k,v in zip(keys,restored)])


def moving_periodic_system(period,hole=19,edge_patch=0):
    """Formal (1-z**period)*K for t=period*k+1; holes hole*t and 99t.

    Without patches, (arm,edge,r), 1<=r<=period, repeats at depths
    edge*t+r+j*period, 0<=j<k. r=0 denotes an old vertex at edge*t.
    With width w=edge_patch, the first and last w inserted vertices of
    every old edge are independent. The repeated interior starts at w+1.
    Require period|2w and t>=2w+period+1, t=1 mod period.
    Rows are coefficients of Z**q*z**c before substituting Z=z**t.
    Thus formal solutions work at every admissible scale. Without patches,
    for t>period+1 the exponents 0<=c<=period+1 do not collide, so the
    converse holds too. No converse for patched words is used here.
    """
    if type(period) is not int or period<1: raise ValueError('require a positive period')
    if type(hole) is not int or not 1<=hole<99: raise ValueError('require 1<=hole<99')
    if type(edge_patch) is not int or edge_patch<0 or 2*edge_patch%period:
        raise ValueError('require nonnegative edge patch with period dividing twice its width')
    lengths = (99,79,23)
    keys,rows = [],defaultdict(lambda:defaultdict(int))
    def add(key,terms,coarse=False):
        i = len(keys)
        keys.append(key)
        for q,c,value in terms:
            rows[q,c][i] += value
            if coarse: rows[q,c+period][i] -= value
    centre = [(0,1,1)]+[(n,1,-1) for n in lengths]
    for h in (hole,99): centre.extend(((h,0,-1),(h,1,1)))
    add((0,0,0),centre,True)
    for arm,n in enumerate(lengths,1):
        for d in range(1,n+1):
            if arm==1 and d in (hole,99): continue
            terms = [(d,1,1),(n-d,1,-1)]
            terms.extend((other+d,1,-1) for j,other in enumerate(lengths,1) if j!=arm)
            for h in (hole,99):
                distance = abs(d-h) if arm==1 else d+h
                terms.extend(((distance,0,-1),(distance,1,1)))
            add((arm,d,0),terms,True)
        for edge in range(n):
            for r in range(1,edge_patch+1):
                for q,c,side in ((edge,r,'prefix'),(edge+1,-r,'suffix')):
                    terms = [(q,c+1,1),(n-q,1-c,-1)]
                    terms.extend((other+q,c+1,-1) for j,other in enumerate(lengths,1) if j!=arm)
                    for h in (hole,99):
                        if arm!=1: dq,dc=q+h,c
                        elif q<h or (q==h and c<0): dq,dc=h-q,-c
                        else: dq,dc=q-h,c
                        terms.extend(((dq,dc,-1),(dq,dc+1,1)))
                    add((arm,edge,side,r),terms,True)
            for r in range(1,period+1):
                pos = [(0,edge_patch+r,1),(1,-edge_patch+r-1,-1)]
                neg = [(-1,period+1+edge_patch-r,1),(0,period-edge_patch-r,-1)]
                terms = []
                def shifted(source,q,c,value):
                    terms.extend((a+q,b+c,s*value) for a,b,s in source)
                shifted(pos,edge,1,1)
                shifted(neg,n-edge,1,-1)
                for j,other in enumerate(lengths,1):
                    if j!=arm: shifted(pos,other+edge,1,-1)
                for h in (hole,99):
                    source = neg if arm==1 and edge<h else pos
                    distance = abs(edge-h) if arm==1 else edge+h
                    shifted(source,distance,0,-1)
                    shifted(source,distance,1,1)
                add((arm,edge,r),terms)
    return keys,{e:{i:c for i,c in row.items() if c}
                 for e,row in rows.items() if any(row.values())}


def residue_lift_sign(period, scale, vertex):
    """A literal balanced lift, homometric only after reducing distances mod period.

    Old vertices retain the recorded t=1 signs. In each old edge, inserted
    vertices come in blocks of period plus signs, then period minus signs.
    The theorem requires scale=1 mod (2*period); it claims no exact pair.
    """
    from residue_2660 import FRONTIER
    if (type(period) is not int or period < 1 or type(scale) is not int
            or scale < 1 or (scale-1) % (2*period)):
        raise ValueError('require positive period and scale=1 modulo twice period')
    if (not isinstance(vertex,(tuple,list)) or len(vertex)!=2
            or any(type(v) is not int for v in vertex)):
        raise ValueError('require an integer arm and depth')
    arm,depth = vertex
    if (arm,depth)==(0,0): return -1
    if not 1<=arm<=3 or not 1<=depth<=scale*len(FRONTIER[arm-1]):
        raise ValueError('vertex is outside the scaled tree')
    old,remainder = divmod(depth,scale)
    if not remainder:
        return {'+':1,'-':-1,'0':0}[FRONTIER[arm-1][old-1]]
    return 1 if ((remainder-1)//period)%2==0 else -1


def residue_lift_plan(periods, index=1):
    """An infinite resistant subfamily passing any finite list of residue tests.

    This checks the small base by direct pair distances and checks every old
    column after specialization. Inserted columns cancel in equal-residue
    opposite-sign pairs; their number is represented without expanding t.
    See RESISTANT_SPECTRUM.md for why balance upgrades the shell congruence
    to equality of the distance profiles modulo z**period-1.
    """
    from residue_2660 import t1_witness, check_pair
    import full_shorter_coupling as physical
    if (not isinstance(periods,(tuple,list)) or not periods
            or any(type(p) is not int or p<1 for p in periods)
            or type(index) is not int or index<1):
        raise ValueError('require nonempty positive integer periods and positive index')
    periods = sorted(set(periods))
    period = math.lcm(*periods)
    stride = math.lcm(7980,2*period)
    scale = 1+stride*index
    base = t1_witness()
    checked = check_pair(base['lengths'],base['left'],base['right'])
    if not checked['homometric'] or checked['size']!=100:
        raise AssertionError('the recorded base pair fails its direct distance counter')
    lengths = [n*scale for n in base['lengths']]
    holes = [(a,d*scale) for a,d in base['holes']]
    residual = defaultdict(int)
    for side,sign in (('left',1),('right',-1)):
        for arm,depth in base[side]:
            old_column = defaultdict(int)
            for e,c in physical.shell_column(base['lengths'],base['holes'],(arm,depth)).items():
                old_column[e%period] += c
            scaled_column = defaultdict(int)
            for e,c in physical.shell_column(lengths,holes,(arm,depth*scale)).items():
                scaled_column[e%period] += c
            if {e:c for e,c in old_column.items() if c}!={e:c for e,c in scaled_column.items() if c}:
                raise AssertionError('an old column changed under residue specialization')
            for e,c in scaled_column.items(): residual[e] += sign*c
    if any(residual.values()): raise AssertionError('old columns do not cancel')
    # In a balanced signing, twice the edge-profile difference is
    # sum_v (degree_in_retained_support(v)-2)*sign(v). These are exactly
    # its six exceptional vertices; all others have retained degree two.
    exceptions = [(1,(0,0)),(-1,(2,79*scale)),(-1,(3,23*scale)),
                  (-1,(1,19*scale-1)),(-1,(1,19*scale+1)),(-1,(1,99*scale-1))]
    twice_edge_defect = sum(c*residue_lift_sign(period,scale,v) for c,v in exceptions)
    if twice_edge_defect!=-2: raise AssertionError('distance-one defect changed')
    return dict(mode='residue_lift',status='modular_profiles_only',periods=periods,
                period=period,index=index,stride=stride,t=scale,lengths=lengths,
                holes=[list(h) for h in holes],pair_size=(201*scale-1)//2,
                inserted_opposite_pairs=201*(scale-1)//2,
                block_pairs_per_old_edge=(scale-1)//(2*period),
                base_pair_verified=True,old_residue_columns_verified=True,
                distance_one_difference=-1,exact_homometric=False,
                all_pairs_decided=False,
                scope='literal balanced pair; distance multiplicities equal modulo each listed period only')


def growing_lift_shell_events():
    """Exact K coefficient jumps at affine exponents a*P+b, t=2P+1.

    Each old edge has P plus signs followed by P minus signs. A constant
    interval of signs maps to four shell intervals and two per hole. The
    holes are old edge endpoints, so no interval crosses a hole. Runtime
    and output size are independent of P. P>=1 is not expanded here.
    """
    from residue_2660 import FRONTIER
    events = defaultdict(int)
    def add(x,y): return x[0]+y[0],x[1]+y[1]
    def sub(x,y): return x[0]-y[0],x[1]-y[1]
    def old(d): return 2*d,d
    one = (0,1)
    def interval(lo,hi,value):
        events[lo] += value
        events[add(hi,one)] -= value
    def column(arm,lo,hi,sign):
        n = old(len(FRONTIER[arm-1]))
        interval(add(lo,one),add(hi,one),sign)
        interval(sub(add(n,one),hi),sub(add(n,one),lo),-sign)
        for j,word in enumerate(FRONTIER,1):
            if j!=arm:
                offset = add(old(len(word)),one)
                interval(add(offset,lo),add(offset,hi),-sign)
        for h in (19,99):
            hole = old(h)
            if arm!=1:
                left,right = add(lo,hole),add(hi,hole)
            # Compare at P=2; the enclosing old edge never crosses a hole.
            elif 2*hi[0]+hi[1] < 2*hole[0]+hole[1]:
                left,right = sub(hole,hi),sub(hole,lo)
            else:
                left,right = sub(lo,hole),sub(hi,hole)
            interval(left,right,-sign)
            interval(add(left,one),add(right,one),sign)
    # Centre sign is -1. These are its physical shell monomials.
    centre = [((0,1),1)]+[(add(old(len(w)),one),-1) for w in FRONTIER]
    for h in (19,99): centre.extend(((old(h),-1),(add(old(h),one),1)))
    for exponent,value in centre: interval(exponent,exponent,-value)
    for arm,word in enumerate(FRONTIER,1):
        for d,ch in enumerate(word,1):
            sign = {'+':1,'-':-1,'0':0}[ch]
            if sign: column(arm,old(d),old(d),sign)
        for edge in range(len(word)):
            column(arm,(2*edge,edge+1),(2*edge+1,edge),1)
            column(arm,(2*edge+1,edge+1),(2*edge+2,edge),-1)
    return {key:value for key,value in events.items() if value}


def growing_lift_shell_runs(scale):
    """Nonzero inclusive coefficient runs of K, without expanding the tree."""
    if type(scale) is not int or scale<3 or scale%2!=1:
        raise ValueError('require odd scale>=3')
    half = (scale-1)//2
    events = defaultdict(int)
    for (a,b),value in growing_lift_shell_events().items():
        events[a*half+b] += value
    runs,value,previous = [],0,None
    for exponent,change in sorted(events.items()):
        if previous is not None and exponent>previous and value:
            if runs and runs[-1][1]+1==previous and runs[-1][2]==value:
                runs[-1][1] = exponent-1
            else: runs.append([previous,exponent-1,value])
        value += change
        previous = exponent
    if value: raise AssertionError('shell polynomial did not terminate')
    return runs


def growing_lift_repair_bound(scale):
    """A Hamming lower bound from this lift to any exact pair on its support.

    Prove the affine jump order for every P>=2, then sum interval lengths
    times absolute coefficients symbolically. P=1 is checked separately.
    A physical column has coefficient l1 norm <=8, so a sign flip changes
    K by norm <=16. This excludes bounded/local repairs, not other pairs.
    """
    if type(scale) is not int or scale<3 or scale%2!=1:
        raise ValueError('require odd scale>=3')
    events = growing_lift_shell_events()
    ordered = sorted(events,key=lambda x:(2*x[0]+x[1],x[0]))
    norm = [0,0]
    value = 0
    for left,right in zip(ordered,ordered[1:]):
        value += events[left]
        a,b = right[0]-left[0],right[1]-left[1]
        if a<0 or 2*a+b<0:
            raise AssertionError('affine order is not proved for every P>=2')
        norm[0] += a*abs(value)
        norm[1] += b*abs(value)
    if value+events[ordered[-1]]:
        raise AssertionError('formal shell polynomial did not terminate')
    if norm!=[1000,244]: raise AssertionError('unexpected symbolic shell norm')
    smallest = sum((hi-lo+1)*abs(c) for lo,hi,c in growing_lift_shell_runs(3))
    if smallest!=1244: raise AssertionError('exceptional endpoint scale differs')
    shell_norm = 500*scale-256
    return dict(mode='growing_lift_repair_bound',t=scale,
                shell_l1=shell_norm,minimum_sign_changes=(shell_norm+15)//16,
                retained_vertices=201*scale-1,column_l1_upper_bound=8,
                norm_in_half_scale=norm,all_pairs_decided=False,
                scope='distance from the named growing-block lift; identical two-hole support only')


def verify_residue_lift(saved):
    expected = residue_lift_plan(saved.get('periods'),saved.get('index'))
    # Strict JSON comparison also rejects booleans masquerading as integer data.
    if json.dumps(saved,sort_keys=True)!=json.dumps(expected,sort_keys=True):
        raise ValueError('saved residue-lift data do not match the checked construction')
    return dict(verified=True,all_pairs_decided=False,
                claim='balanced literal construction with equal modular distance profiles, but one fewer positive distance-one pair')


def full_partition_subdivision_bound(lengths,scale):
    """Inherit the base root-of-unity full-partition obstruction.

    Without holes, shell rows e=1 mod scale see exactly the old vertices
    at depths divisible by scale. Relabel e=(E-1)*scale+1: their columns
    are precisely the base full-partition columns. Hence every full
    signing at the scaled tree would induce one at the base tree.
    """
    if (len(lengths)!=3 or any(type(n) is not int or n<1 for n in lengths)
            or type(scale) is not int or scale<1):
        raise ValueError('require three positive arm lengths and a positive integer scale')
    divisor = math.gcd(*(n+1 for n in lengths))
    quotient_sum = sum((n+1)//divisor for n in lengths)
    base_refused = divisor%2==0 and quotient_sum%2==1
    total = 1+scale*sum(lengths)
    inherited = base_refused and total%2==0
    return dict(base=list(lengths),scale=scale,base_divisor=divisor,
                base_quotient_sum=quotient_sum,full_partition_refused=inherited or total%2==1,
                homometric_pair_upper_bound=total//2-int(inherited),
                inherited_from_base=inherited,all_pairs_decided=False,
                scope='full partitions only; no bound below half-minus-one')


def full_partition_subdivision_audit(lengths,scale):
    """Direct-column control of every residue at a finite scaled tree."""
    full_partition_subdivision_bound(lengths,scale)
    import full_shorter_coupling as physical
    scaled = [scale*n for n in lengths]
    vertices = [(0,0)]+[(a,d) for a,n in enumerate(scaled,1) for d in range(1,n+1)]
    old_columns = nongrid_columns = 0
    for a,d in vertices:
        column = physical.shell_column(scaled,set(),(a,d))
        selected = {e:c for e,c in column.items() if (e-1)%scale==0}
        if d%scale:
            if selected: raise AssertionError('a nongrid vertex entered a coarse shell row')
            nongrid_columns += 1
        else:
            recovered = {(e-1)//scale+1:c for e,c in selected.items()}
            if recovered!=physical.shell_column(lengths,set(),(a,d//scale)):
                raise AssertionError('coarse full-partition column differs from base column')
            old_columns += 1
    return dict(verified=True,old_columns=old_columns,nongrid_columns=nongrid_columns)


def bipartition_support_obstruction(lengths,holes=()):
    """Exact obstruction from the odd-distance shell, for a fixed support.

    If each set has k vertices and a,b black vertices, equality of odd
    distances gives (a-b)*(k-a-b)=0. Thus the retained black count a+b
    must be even or equal k. This is only one necessary shell condition.
    """
    if (len(lengths)!=3 or any(type(n) is not int or n<1 for n in lengths)):
        raise ValueError('require three positive integer arm lengths')
    holes = list(holes)
    if len(set(holes))!=len(holes): raise ValueError('require distinct holes')
    for a,d in holes:
        if (type(a) is not int or type(d) is not int or
                not ((a==0 and d==0) or (1<=a<=3 and 1<=d<=lengths[a-1]))):
            raise ValueError('hole is not a tree vertex')
    retained = 1+sum(lengths)-len(holes)
    if retained%2: raise ValueError('require an even retained support')
    k = retained//2
    black = 1+sum(n//2 for n in lengths)-sum(d%2==0 for _,d in holes)
    return dict(pair_size=k,retained_black=black,retained_white=retained-black,
                obstructed=black%2==1 and black!=k,
                scope='odd-distance shell on this exact support only',all_pairs_decided=False)


def coarse_support_system(hole=19):
    """Untwisted t=1 shell system, in moving-compiler coordinate order.

    This is necessary for *every* formal moving-word period: specialize
    Z=z, so each inserted geometric sum vanishes, and cancel 1-z**p.
    It is not a necessary condition on unrestricted pairs at larger t.
    """
    import full_shorter_coupling as physical
    if type(hole) is not int or not 1<=hole<99:
        raise ValueError('require 1<=hole<99')
    lengths,holes = (99,79,23),{(1,hole),(1,99)}
    keys = [(0,0,0)]+[(a,d,0) for a,n in enumerate(lengths,1)
                      for d in range(1,n+1) if (a,d) not in holes]
    rows = defaultdict(dict)
    for i,(a,d,_) in enumerate(keys):
        for e,c in physical.shell_column(lengths,holes,(a,d)).items():
            rows[e][i] = c
    return keys,dict(rows)


def coarse_projection_audit(period,hole=19):
    """Check Z=z specialization against independent physical columns.

    Keep zero coefficients out of both maps; every inserted-word column
    must cancel, and the old columns must equal (1-z**p)*K_old exactly.
    No sign-search or rank assumption enters this check.
    """
    keys,formal = moving_periodic_system(period,hole)
    old_keys,old_rows = coarse_support_system(hole)
    positions = {key:i for i,key in enumerate(keys)}
    actual,expected = defaultdict(lambda:defaultdict(int)),defaultdict(lambda:defaultdict(int))
    for (q,c),row in formal.items():
        for i,value in row.items(): actual[q+c][i] += value
    for e,row in old_rows.items():
        for i,value in row.items():
            j = positions[old_keys[i]]
            expected[e][j] += value
            expected[e+period][j] -= value
    def clean(rows):
        return {e:{i:c for i,c in row.items() if c} for e,row in rows.items()
                if any(row.values())}
    if clean(actual)!=clean(expected):
        raise AssertionError('formal specialization does not equal the old physical shells')
    return dict(period=period,hole=hole,verified=True,old_variables=len(old_keys),
                old_rows=len(old_rows),inserted_columns_cancelled=len(keys)-len(old_keys))


def coarse_search(hole=19,seconds=30,nodes=1000000):
    """Search the necessary old support only; never an inflated signing."""
    start = time.monotonic()
    keys,formal = coarse_support_system(hole)
    original = list(formal.values())
    closure = joint_sign_closure(len(keys),original,seconds)
    result = dict(mode='coarse',hole=hole,all_pairs_decided=False,
                  scope='old tripod only; necessary for formal moving words',
                  closure=closure['history'])
    def done(status,**details):
        return dict(**result,status=status,elapsed=time.monotonic()-start,**details)
    if closure['conflict']: return done('coarse_refused_by_joint_fields')
    remaining = seconds-(time.monotonic()-start)
    if not closure['complete'] or remaining<=0: return done('unknown')
    refusal,basis = binary_elimination(closure['rows'])
    if refusal is not None: return done('coarse_refused_by_parity')
    engine = make_engine(closure['size'],closure['rows'],basis,remaining,nodes,'connected')
    i,s = closure['aliases'][0]
    status,values = engine.run({i:s})
    if values is None: return done(status,nodes=engine.nodes)
    restored = [s*values[i] for i,s in closure['aliases']]
    if any(sum(c*restored[i] for i,c in row.items()) for row in original):
        raise AssertionError('old support signing fails original physical shells')
    return done(status,nodes=engine.nodes,
                assignment=[[list(k),v] for k,v in zip(keys,restored)])


def kernel_sign_patterns(size,rows,seconds=30,max_free=22):
    """Enumerate the literal cube of a verified rational kernel, up to sign.

    Every free coordinate is an original coordinate, so it is a sign.
    Fixing its first sign positive removes exactly global complementation.
    Meet-in-the-middle sum tables filter all 2**(nullity-1) assignments;
    this is exhaustive only when complete=True. The dimension cap bounds
    allocation, not a mathematical restriction on the input equations.
    """
    if type(max_free) is not int or not 1<=max_free<=24:
        raise ValueError('require 1<=max_free<=24')
    start = time.monotonic()
    kernel = rational_recovery(size,rows,seconds)
    if not kernel['complete']: return dict(complete=False,stage='rational')
    free = kernel['free']
    n = len(free)
    if n>max_free: return dict(complete=False,stage='dimension_limit',nullity=n)
    if n==0: return dict(complete=True,free=[],patterns=[],forms={},nullity=0)
    positions = {i:j for j,i in enumerate(free)}
    forms = {}
    for i,expression in kernel['expressions'].items():
        denominator = math.lcm(*(c.denominator for c in expression.values()))
        coefficients = [0]*n
        for v,c in expression.items(): coefficients[positions[v]] = int(c*denominator)
        forms[i] = coefficients,denominator
    candidates = range(1,1<<n,2)
    split = n//2
    mask = (1<<split)-1
    def sums(word):
        values = [-sum(word)]*(1<<len(word))
        for b in range(1,len(values)):
            bit = b&-b
            values[b] = values[b^bit]+2*word[bit.bit_length()-1]
        return values
    ordered = sorted(forms.values(),key=lambda form:(
        sum(c!=0 for c in form[0]),-sum(abs(c) for c in form[0])))
    for coefficients,denominator in ordered:
        if time.monotonic()-start>=seconds:
            return dict(complete=False,stage='cube_filter',nullity=n)
        nonzero = [c for c in coefficients if c]
        if len(nonzero)==1 and abs(nonzero[0])==denominator: continue
        left,right = sums(coefficients[:split]),sums(coefficients[split:])
        candidates = [b for b in candidates
                      if abs(left[b&mask]+right[b>>split])==denominator]
        if not candidates: break
    return dict(complete=True,free=free,patterns=list(candidates),forms=forms,nullity=n)


def coarse_catalog(hole=19,seconds=30,max_free=24):
    """All centre-positive signings of one old support; no inflated claim."""
    start = time.monotonic()
    keys,formal = coarse_support_system(hole)
    rows = list(formal.values())
    joint = joint_sign_closure(len(keys),rows,seconds)
    if joint['conflict']:
        return dict(complete=True,hole=hole,keys=keys,assignments=[],count=0,all_pairs_decided=False)
    remaining = seconds-(time.monotonic()-start)
    if not joint['complete'] or remaining<=0:
        return dict(complete=False,hole=hole,stage='closure')
    cube = kernel_sign_patterns(joint['size'],joint['rows'],remaining,max_free)
    if not cube['complete']:
        return dict(complete=False,hole=hole,stage=cube['stage'],nullity=cube.get('nullity'))
    assignments = []
    for bits in cube['patterns']:
        values = {i:sum(c*(1 if bits>>j&1 else -1) for j,c in enumerate(coefficients))//denominator
                  for i,(coefficients,denominator) in cube['forms'].items()}
        restored = [s*values[i] for i,s in joint['aliases']]
        restored = [restored[0]*v for v in restored]
        if any(v not in (-1,1) for v in restored) or any(
                sum(c*restored[i] for i,c in row.items()) for row in rows):
            raise AssertionError('catalog entry fails original old-support equations')
        assignments.append(restored)
    assignments.sort()
    if len({tuple(v) for v in assignments})!=len(assignments):
        raise AssertionError('global sign normalization duplicated a catalog entry')
    return dict(complete=True,hole=hole,keys=keys,assignments=assignments,
                count=len(assignments),nullity=cube['nullity'],
                elapsed=time.monotonic()-start,all_pairs_decided=False)


def moving_boundary_system(hole=19):
    """Universal endpoint relaxation for every formal period p>=2.

    Extract exponents symbolically as beta*p+offset, without selecting a
    representative period. Rows c=0,1,p,p+1 see word positions 1,2,p-1,p.
    Endpoints are independent here; identifying them at p=2,3 cannot rescue
    a refusal. The coefficient map is checked against the full compiler.
    """
    old,_ = coarse_support_system(hole)
    lengths = (99,79,23)
    keys = [('old',a,d) for a,d,_ in old]
    keys += [(side,a,edge,r) for a,n in enumerate(lengths,1)
             for edge in range(n) for side,values in (('left',(1,2)),('right',(-1,0)))
             for r in values]
    positions = {key:i for i,key in enumerate(keys)}
    rows = defaultdict(lambda:defaultdict(int))
    def put(key,q,beta,offset,value):
        if offset in (0,1):
            if beta not in (0,1): raise AssertionError('unexpected period coefficient')
            rows[q,'left' if beta==0 else 'right',offset][positions[key]] += value
    for a,d,_ in old:
        key = ('old',a,d)
        if a==0:
            terms = [(0,1,1)]+[(n,1,-1) for n in lengths]
        else:
            terms = [(d,1,1),(lengths[a-1]-d,1,-1)]
            terms += [(d+n,1,-1) for j,n in enumerate(lengths,1) if j!=a]
        for h in (hole,99):
            distance = abs(d-h) if a==1 else d+h
            terms += [(distance,0,-1),(distance,1,1)]
        # Multiply each old physical column by 1-z**p.
        for q,offset,value in terms:
            put(key,q,0,offset,value)
            put(key,q,1,offset,-value)
    for a,n in enumerate(lengths,1):
        for edge in range(n):
            for side,ends in (('left',(1,2)),('right',(-1,0))):
                for offset in ends:
                    key = (side,a,edge,offset)
                    beta = int(side=='right')
                    # r=beta*p+offset. P and N are represented directly
                    # in (Z exponent, p coefficient, offset, coefficient).
                    forward = [(0,beta,offset,1),(1,beta,offset-1,-1)]
                    reflected = [(-1,1-beta,1-offset,1),(0,1-beta,-offset,-1)]
                    def shifted(source,q,u,factor):
                        for dq,b,j,c in source: put(key,q+dq,b,j+u,c*factor)
                    shifted(forward,edge,1,1)
                    shifted(reflected,n-edge,1,-1)
                    for j,other in enumerate(lengths,1):
                        if j!=a: shifted(forward,other+edge,1,-1)
                    for h in (hole,99):
                        source = reflected if a==1 and edge<h else forward
                        distance = abs(edge-h) if a==1 else edge+h
                        shifted(source,distance,0,-1)
                        shifted(source,distance,1,1)
    return keys,{label:{i:c for i,c in row.items() if c}
                 for label,row in rows.items() if any(row.values())}


def moving_boundary_audit(period,hole=19):
    """Exact coefficient check, allowing endpoint identifications at p=2,3."""
    if type(period) is not int or period<2: raise ValueError('require period>=2')
    keys,universal = moving_boundary_system(hole)
    physical,formal = moving_periodic_system(period,hole)
    positions = {key:i for i,key in enumerate(physical)}
    image = []
    for key in keys:
        if key[0]=='old': _,a,d = key; target = (a,d,0)
        else:
            side,a,edge,r = key
            target = (a,edge,r if side=='left' else period+r)
        image.append(positions[target])
    expected = {}
    for (q,side,c),row in universal.items():
        label = (q,c if side=='left' else period+c)
        terms = defaultdict(int)
        for i,value in row.items(): terms[image[i]] += value
        expected[label] = {i:c for i,c in terms.items() if c}
    actual = {label:row for label,row in formal.items() if label[1] in (0,1,period,period+1)}
    expected = {label:row for label,row in expected.items() if row}
    if expected!=actual: raise AssertionError('universal boundary columns differ from formal coefficients')
    return dict(period=period,hole=hole,verified=True,universal_variables=len(keys),
                boundary_rows=len(actual),endpoint_identifications=len(image)-len(set(image)))


def moving_boundary_refusal(hole=19,seconds=30):
    """Replay a necessary-boundary refusal uniform over every word period.

    Period one is separately impossible by retained-support parity at k=1.
    For every p>=2 the universal endpoint model is necessary. A compatible
    relaxation reports unknown, never a construction or a negative claim.
    """
    start = time.monotonic()
    catalog = coarse_catalog(hole,seconds)
    report = dict(mode='boundary',hole=hole,all_pairs_decided=False,branches=[],
                  scope='all formal moving-word periods; holes ht and 99t only')
    def done(status,**details):
        return dict(**report,status=status,elapsed=time.monotonic()-start,**details)
    if not catalog['complete']: return done('unknown',stage='old_catalog')
    report['coarse_count'] = catalog['count']
    keys,formal = moving_boundary_system(hole)
    positions = {key:i for i,key in enumerate(keys)}
    for b,assignment in enumerate(catalog['assignments']):
        remaining = seconds-(time.monotonic()-start)
        if remaining<=0: return done('unknown',stage='boundary_budget')
        rows = list(formal.values())+[
            {positions['old',a,d]:1,positions['old',0,0]:-value}
            for (a,d,_),value in zip(catalog['keys'],assignment) if a or d]
        closure = joint_sign_closure(len(keys),rows,remaining/(catalog['count']-b))
        report['branches'].append(dict(branch=b,complete=closure['complete'],
                                       refused=closure['conflict'],stage=closure.get('stage'),
                                       variables=closure['size']))
        if not closure['complete'] or not closure['conflict']:
            return done('unknown',stage='boundary_relaxation')
    return done('every_formal_period_refused')


def coarse_support_catalog(seconds=300):
    """Classify the 98 old supports; never classify arbitrary inflated pairs."""
    if type(seconds) not in (int,float) or not math.isfinite(seconds) or seconds<=0:
        raise ValueError('require a positive finite time')
    start = time.monotonic()
    entries = []
    for hole in range(1,99):
        obstruction = bipartition_support_obstruction((99,79,23),((1,hole),(1,99)))
        if obstruction['obstructed']:
            entries.append(dict(hole=hole,complete=True,count=0,reason='odd_distance_shell'))
            continue
        remaining = seconds-(time.monotonic()-start)
        if remaining<=0:
            entries.append(dict(hole=hole,complete=False))
            continue
        catalog = coarse_catalog(hole,min(30,remaining))
        entries.append({k:v for k,v in catalog.items()
                        if k in ('hole','complete','count','nullity','stage')})
    return dict(complete=all(e['complete'] for e in entries),
                surviving_holes=[(e['hole'],e['count']) for e in entries if e.get('count')],
                unknown_holes=[e['hole'] for e in entries if not e['complete']],
                old_supports=98,colour_refusals=sum(e.get('reason')=='odd_distance_shell' for e in entries),
                elapsed=time.monotonic()-start,all_pairs_decided=False,
                scope='old tripod only; necessary for every formal moving-word period')


def moving_coarse_search(period=10,hole=19,seconds=300,nodes=1000000,short_recovery=False):
    """Disjoin the exhaustive old-support catalog before moving-word search.

    Every branch is still only this formal word ansatz. A timeout or an
    incomplete catalog can never become a refusal. Refusals are replayable
    diagnostics, not saved certificates accepted by verify_saved.
    """
    start = time.monotonic()
    # Validate the period and independently check the specialization first.
    audit = coarse_projection_audit(period,hole)
    if (type(seconds) not in (int,float) or not math.isfinite(seconds) or seconds<=0
            or type(nodes) is not int or nodes<0):
        raise ValueError('require a positive finite time and nonnegative node budget')
    catalog = coarse_catalog(hole,seconds)
    result = dict(mode='moving_coarse',period=period,hole=hole,
                  all_pairs_decided=False,projection_verified=audit['verified'],
                  coarse_catalog_complete=True,branches=[])
    def done(status,**details):
        return dict(**result,status=status,elapsed=time.monotonic()-start,**details)
    if not catalog['complete']: return done('unknown',stage='coarse_catalog')
    result['coarse_count'] = catalog['count']
    keys,formal = moving_periodic_system(period,hole)
    positions = {key:i for i,key in enumerate(keys)}
    for branch,assignment in enumerate(catalog['assignments']):
        remaining = seconds-(time.monotonic()-start)
        if remaining<=0: return done('unknown',stage='branch_budget')
        budget = remaining/(catalog['count']-branch)
        original = list(formal.values())
        # Use centre as the homogeneous constant. Global complementation
        # normalizes every true moving signing into exactly one old branch.
        conditioned = original+[{positions[key]:1,0:-v}
                                for key,v in zip(catalog['keys'],assignment) if key!=(0,0,0)]
        branch_start = time.monotonic()
        closure = joint_sign_closure(len(keys),conditioned,budget,short_recovery=short_recovery)
        summary = dict(branch=branch,complete=closure['complete'],
                       stage=closure.get('stage'),variables=closure['size'])
        result['branches'].append(summary)
        if closure['conflict']:
            summary['status'] = 'refused_by_joint_fields'
            continue
        available = budget-(time.monotonic()-branch_start)
        if not closure['complete'] or available<=0:
            summary['status'] = 'unknown'
            continue
        refusal,basis = binary_elimination(closure['rows'])
        if refusal is not None:
            summary['status'] = 'refused_by_parity'
            continue
        engine = make_engine(closure['size'],closure['rows'],reduced_binary_basis(basis),
                             available,nodes,'connected')
        i,s = closure['aliases'][0]
        status,values = engine.run({i:s})
        summary.update(status=status,nodes=engine.nodes)
        if values is not None:
            restored = [s*values[i] for i,s in closure['aliases']]
            if any(sum(c*restored[i] for i,c in row.items()) for row in conditioned):
                raise AssertionError('conditioned moving solution fails an untouched equation')
            return done('sat',assignment=[[list(k),v] for k,v in zip(keys,restored)])
    if any(b['status']=='unknown' for b in result['branches']): return done('unknown')
    return done('ansatz_refused_by_coarse_branches')


def verify_coarse_assignment(hole,assignment):
    """Independent direct distance counter for a saved original support."""
    from collections import Counter
    keys,_ = coarse_support_system(hole)
    supplied = {tuple(k):v for k,v in assignment}
    if len(supplied)!=len(assignment) or set(supplied)!=set(keys):
        raise ValueError('require every original support coordinate once')
    if any(type(v) is not int or v not in (-1,1) for v in supplied.values()):
        raise ValueError('require literal signs')
    if supplied[0,0,0]!=1: raise ValueError('require positive centre')
    positive = [(a,d) for (a,d,_),s in supplied.items() if s==1]
    negative = [(a,d) for (a,d,_),s in supplied.items() if s==-1]
    def distances(vertices):
        return Counter(abs(d-e) if a==b else d+e
                       for i,(a,d) in enumerate(vertices) for b,e in vertices[:i])
    if len(positive)!=len(negative) or distances(positive)!=distances(negative):
        raise ValueError('original support pair fails size or distance multiplicities')
    return dict(verified=True,pair_size=len(positive),
                claim='original support only; no inflated construction',all_pairs_decided=False)




def moving_folded_labels(reduced=False):
    return [(a,q,s) for a,n in enumerate((43 if reduced else 99,79,23),1)
            for s in (1,-1) for q in (range(n) if s==1 else range(1,n+1))]
def _moving_affine_column(a,q,alpha,beta,h=19):
    if a==0:return [(0,0,1,1),(79,0,1,-1),(23,0,1,-1),(99,0,0,-1),(h,0,0,-1),(h,0,1,1)]
    n=(99,79,23)[a-1]
    out=[(q,alpha,beta+1,1)]+[(m+q,alpha,beta+1,-1) for j,m in enumerate((99,79,23),1) if j!=a and not (a!=1 and j==1)]
    if a==1:
        out.append((99-q,-alpha,-beta,-1))
        before=q<h or(q==h and (alpha<0 or(alpha==0 and beta<0)))
        if before:out.extend(((h-q,-alpha,-beta,-1),(h-q,-alpha,1-beta,1)))
        else:out.extend(((q-h,alpha,beta,-1),(q-h,alpha,beta+1,1)))
    else:out.extend(((n-q,-alpha,1-beta,-1),(99+q,alpha,beta,-1),(h+q,alpha,beta,-1),(h+q,alpha,beta+1,1)))
    return out

def _moving_strip_column(a,q,alpha,beta,h,reduced):
    terms=_moving_affine_column(a,q,alpha,beta,h)
    tail=(a==2 and (q>23 or (q==23 and (alpha>0 or (alpha==0 and beta>=1)))))
    if reduced and tail:
        terms += [(Q,u,c,-value) for Q,u,c,value in
                  _moving_affine_column(1,q+20,alpha,beta-1,h)]
    return terms


def moving_folded_stencils(h=19,reduced=False):
    """All-word radius-one shell equations for holes (1,h*t),(1,99*t).

    Left rows have folded level 0 or 1, interior rows 2..L-1, and
    right rows L, where t=2L+1. This is not an existence decision.
    """
    if type(h) is not int or not 1<=h<(43 if reduced else 99):
        raise ValueError('require 1<=h<=42 when reduced, otherwise 1<=h<99')
    interior=defaultdict(lambda:defaultdict(int));left=defaultdict(lambda:defaultdict(int));right=defaultdict(lambda:defaultdict(int))
    for a,q,s in moving_folded_labels(reduced):
        for Q,u,c,v in _moving_strip_column(a,q,s,0,h,reduced):interior[Q,u][a,q,s,-u*c]+=v
        for j in (-1,0):
            for Q,u,c,v in _moving_strip_column(a,q,s,s*j,h,reduced):
                if u==1:
                    if c==0:row=Q,1
                    elif c==1:row=Q+1,-1
                    else:continue
                else:
                    if c==0:row=Q,-1
                    elif c==-1:row=Q-1,1
                    else:continue
                right[row][a,q,s,j]+=v
    sources=[(0,0,0)]
    for a,n in enumerate((43 if reduced else 99,79,23),1):
        for d in range(-2,3):
            for q in (range(1,n+1) if d<=0 else range(n)):
                if (a,q,d) not in ((1,h,0),(1,43 if reduced else 99,0)):sources.append((a,q,d))
    for a,q,d in sources:
        for Q,u,c,v in _moving_strip_column(a,q,0,d,h,reduced):
            assert u==0
            if abs(c)<=1:left[Q,c][a,q,d]+=v
    def trim(rows):return {r:{k:c for k,c in row.items() if c} for r,row in rows.items() if any(row.values())}
    return trim(left),trim(interior),trim(right)


def interior_parity_cocycle(hole=19):
    """Certify a parity observable alternating on every unrestricted interior.

    No levels are identified. Fixed shell weights Q mod 8 in 4..7 give
    P(S)b=1, with P(S)=(1+S)Q(S) over F_2 and Q supported at -1,0.
    This excludes odd-period interiors, not physical endpoint completion.
    """
    left,stencils,_ = moving_folded_stencils(hole)
    selected = [list(key) for key in sorted(stencils) if key[0]%8 >= 4]
    coefficients = defaultdict(int)
    rhs = 0
    for key in selected:
        row = stencils[tuple(key)]
        if sum(row.values())%2:
            raise ValueError('shell row has odd coefficient sum')
        rhs ^= sum(row.values())//2%2
        for coordinate,c in row.items(): coefficients[coordinate] ^= c%2
    observable = []
    for a,q,s in moving_folded_labels():
        if coefficients[a,q,s,-1]: observable.append([a,q,s,-1])
        if coefficients[a,q,s,1]: observable.append([a,q,s,0])
    certificate = dict(kind='moving-interior-cocycle-v1',hole=hole,
                       shell_rows=selected,observable=observable,rhs=rhs,
                       left_rows=[list(key) for key in sorted(left) if key[0]%8>=4],
                       initial_phase=1,
                       literal_existence_decided=False,all_pairs_decided=False)
    if not verify_interior_parity_cocycle(certificate):
        raise ValueError('alternating observable identity not obtained')
    return certificate


def verify_interior_parity_cocycle(certificate):
    """Check the polynomial identity directly, without parity elimination."""
    if (certificate.get('kind')!='moving-interior-cocycle-v1' or
            type(certificate.get('rhs')) is not int or certificate['rhs']!=1 or
            certificate.get('literal_existence_decided') is not False or
            certificate.get('all_pairs_decided') is not False): return False
    try: left,stencils,_ = moving_folded_stencils(certificate.get('hole'))
    except (TypeError,ValueError): return False
    rows = certificate.get('shell_rows')
    if rows != [list(key) for key in sorted(stencils) if key[0]%8 >= 4]:
        return False
    observable = certificate.get('observable')
    labels = set(moving_folded_labels())
    if not isinstance(observable,list) or not observable: return False
    if any(not isinstance(key,list) or len(key)!=4 or
           any(type(v) is not int for v in key) or tuple(key[:3]) not in labels or
           key[3] not in (-1,0) for key in observable): return False
    if len(set(map(tuple,observable)))!=len(observable): return False
    lhs,rhs = set(),0
    for key in rows:
        row = stencils[tuple(key)]
        total = sum(row.values())
        if total%2: return False
        rhs ^= total//2%2
        for coordinate,c in row.items():
            if c%2: lhs.symmetric_difference_update((coordinate,))
    difference = set()
    for a,q,s,d in observable:
        difference.symmetric_difference_update(((a,q,s,d),(a,q,s,d+1)))
    if rhs!=1 or lhs!=difference: return False
    left_rows = certificate.get('left_rows')
    if (left_rows != [list(key) for key in sorted(left) if key[0]%8>=4] or
            type(certificate.get('initial_phase')) is not int or
            certificate['initial_phase']!=1): return False
    lhs,rhs = set(),0
    for key in left_rows:
        row = left[tuple(key)]
        total = sum(row.values())
        if total%2: return False
        rhs ^= total//2%2
        for coordinate,c in row.items():
            if c%2: lhs.symmetric_difference_update((coordinate,))
    initial = set()
    for a,q,s,d in observable:
        initial.symmetric_difference_update(((a,q,s*(2+d)),))
    return rhs==1 and lhs==initial


def _parity_trace_basis(vectors):
    """Binary row basis retaining source-row combinations (small exact matrices)."""
    basis = {}
    for index,vector in enumerate(vectors):
        source = 1 << index
        while vector:
            pivot = vector.bit_length()-1
            if pivot not in basis:
                basis[pivot] = vector,source
                break
            row,proof = basis[pivot]
            vector ^= row
            source ^= proof
    return basis


def _parity_trace_reduce(vector,basis):
    source = 0
    while vector:
        pivot = vector.bit_length()-1
        if pivot not in basis: break
        row,proof = basis[pivot]
        vector ^= row
        source ^= proof
    return vector,source


def _parity_trace_data(hole):
    left,interior,right = moving_folded_stencils(hole)
    labels = moving_folded_labels()
    # The five fixed shell selectors, the same for every hole 1..98.
    selectors = (
        lambda q,u: q%8>=4,
        lambda q,u: (q%8 in (3,4,5,6) if u==1 else q%8 in (0,5,6,7)),
        lambda q,u: (q%4==0 if u==1 else q%4==3),
        lambda q,u: (q%4==2 if u==1 else q%4==1),
        lambda q,u: (q%4==1 if u==1 else q%4==2))
    laws = []
    evaluated = []
    for row in interior.values():
        evaluated.append(sum((sum(row.get((*k,d),0) for d in (-1,0,1))%2)<<i
                             for i,k in enumerate(labels)))
    for selector in selectors:
        rows = [key for key in sorted(interior) if selector(*key)]
        coefficients = set()
        drift = 0
        for key in rows:
            row = interior[key]
            if sum(row.values())%2: raise ValueError('odd shell sum')
            drift ^= sum(row.values())//2%2
            coefficients.symmetric_difference_update(k for k,c in row.items() if c%2)
        observable = sorted((*k,d) for k in labels for d in (-1,0)
                            if (*k,-1 if d==-1 else 1) in coefficients)
        laws.append(dict(shell_rows=[list(k) for k in rows],
                         observable=[list(k) for k in observable],drift=drift))
    return left,interior,right,laws,evaluated


def parity_trace_certificate(hole=19):
    """Complete constant-row two-level parity laws, including both endpoints.

    This classifies one precise method. It does not decide the literal cube.
    """
    left,_,right,laws,_ = _parity_trace_data(hole)
    endpoints = {}
    for name,rows,masks in (('left',left,(1,6,24)),('right',right,(3,12,16))):
        keys = sorted(rows)
        coordinates = sorted({k for row in rows.values() for k in row})
        indices = {k:i for i,k in enumerate(coordinates)}
        vectors = [sum((c%2)<<indices[k] for k,c in rows[key].items()) for key in keys]
        basis = _parity_trace_basis(vectors)
        proofs = []
        for mask in masks:
            target = set()
            for i,law in enumerate(laws):
                if mask>>i&1:
                    for a,q,s,d in law['observable']:
                        target.symmetric_difference_update(((a,q,s*(2+d)) if name=='left'
                                                            else (a,q,s,d),))
            residual,source = _parity_trace_reduce(sum(1<<indices[k] for k in target),basis)
            if residual: raise ValueError('endpoint identity not obtained')
            selected = [key for j,key in enumerate(keys) if source>>j&1]
            phase = 0
            for key in selected: phase ^= sum(rows[key].values())//2%2
            proofs.append(dict(mask=mask,shell_rows=[list(k) for k in selected],phase=phase))
        endpoints[name] = proofs
    certificate = dict(kind='moving-parity-trace-v1',hole=hole,laws=laws,
                       endpoints=endpoints,phases_at_two=[1,1,0,0,0],
                       literal_existence_decided=False,all_pairs_decided=False)
    if not verify_parity_trace_certificate(certificate):
        raise ValueError('parity trace classification failed')
    return certificate


def verify_parity_trace_certificate(certificate):
    """Rebuild shell rows, check identities, ranks and every endpoint combination."""
    if (certificate.get('kind')!='moving-parity-trace-v1' or
            certificate.get('literal_existence_decided') is not False or
            certificate.get('all_pairs_decided') is not False): return False
    try:
        left,interior,right,laws,evaluated = _parity_trace_data(certificate.get('hole'))
        if certificate.get('laws')!=laws or certificate.get('phases_at_two')!=[1,1,0,0,0]:
            return False
        labels = moving_folded_labels()
        positions = {(*k,d):2*i+(d==0) for i,k in enumerate(labels) for d in (-1,0)}
        observables = []
        for law in laws:
            lhs = set()
            for key in law['shell_rows']:
                lhs.symmetric_difference_update(k for k,c in interior[tuple(key)].items() if c%2)
            difference = set()
            for a,q,s,d in law['observable']:
                difference.symmetric_difference_update(((a,q,s,d),(a,q,s,d+1)))
            if lhs!=difference: return False
            observables.append(sum(1<<positions[tuple(k)] for k in law['observable']))
        # 356 row types, rank 351 at z=1: precisely five dependencies.
        # Their five independent observables prove these are all such laws.
        if (len(evaluated)!=356 or len(_parity_trace_basis(evaluated))!=351 or
                len(_parity_trace_basis(observables))!=5 or
                [law['drift'] for law in laws]!=[1,1,1,1,0]): return False
        for name,rows,masks in (('left',left,(1,6,24)),('right',right,(3,12,16))):
            proofs = certificate['endpoints'][name]
            if not isinstance(proofs,list) or len(proofs)!=3: return False
            coordinates = sorted({k for row in rows.values() for k in row})
            indices = {k:i for i,k in enumerate(coordinates)}
            vectors = [sum((c%2)<<indices[k] for k,c in row.items()) for row in rows.values()]
            basis = _parity_trace_basis(vectors)
            if any(sum(row.values())%2 for row in rows.values()): return False
            augmented = [v | ((sum(row.values())//2%2)<<len(indices))
                         for v,row in zip(vectors,rows.values())]
            if len(_parity_trace_basis(augmented))!=len(basis): return False
            for proof,mask in zip(proofs,masks):
                if type(proof['mask']) is not int or proof['mask']!=mask: return False
                source = proof['shell_rows']
                if not isinstance(source,list) or len(source)>len(rows): return False
                if len(set(map(tuple,source)))!=len(source): return False
                lhs = set(); rhs = 0
                for key in source:
                    row = rows[tuple(key)]
                    if sum(row.values())%2: return False
                    rhs ^= sum(row.values())//2%2
                    lhs.symmetric_difference_update(k for k,c in row.items() if c%2)
                target = set()
                for i,law in enumerate(laws):
                    if mask>>i&1:
                        for a,q,s,d in law['observable']:
                            target.symmetric_difference_update(((a,q,s*(2+d)) if name=='left'
                                                                else (a,q,s,d),))
                if lhs!=target or type(proof['phase']) is not int or proof['phase']!=rhs:
                    return False
                expected = {1:1,6:1,24:0}.get(mask,0)
                if rhs!=expected: return False
            # Check all 31 nonzero combinations: exactly this 3-space is fixed
            # by each endpoint. No extra endpoint-determined law is omitted.
            span = {0}
            for mask in masks: span |= {v^mask for v in tuple(span)}
            for mask in range(1,32):
                target = 0
                for i,law in enumerate(laws):
                    if mask>>i&1:
                        for a,q,s,d in law['observable']:
                            k = (a,q,s*(2+d)) if name=='left' else (a,q,s,d)
                            target ^= 1<<indices[k]
                residual,_ = _parity_trace_reduce(target,basis)
                if (not residual)!=(mask in span): return False
        return True
    except (KeyError,TypeError,ValueError,IndexError):
        return False


def parity_completion_certificate(hole=19,half_parity=0):
    """A full mod-four shell signing, not an integer shell solution.

    Two-periodic bits and six free endpoint levels suffice. The fixed
    quotient extends to every L>=18 of this parity, with t=2L+1.
    """
    if type(half_parity) is not int or half_parity not in (0,1):
        raise ValueError('require half parity zero or one')
    keys,rows = compile_moving_folded(18+half_parity,2,6,hole)
    refusal,basis = binary_elimination(rows)
    if refusal is not None: raise ValueError('no mod-four completion in this quotient')
    bits = 0
    for pivot,(mask,rhs) in sorted(basis.items()):
        if rhs ^ ((mask & bits).bit_count()%2): bits |= 1<<pivot
    if bits>>keys.index(('left',0,0,0))&1: bits ^= (1<<len(keys))-1
    certificate = dict(kind='moving-parity-completion-v1',hole=hole,
                       half_parity=half_parity,minimum_half=18,period=2,patch=6,
                       bits=hex(bits),variables=len(keys),
                       literal_existence_decided=False,all_pairs_decided=False)
    if not verify_parity_completion_certificate(certificate):
        raise ValueError('invalid mod-four completion')
    return certificate


def verify_parity_completion_certificate(certificate):
    """Substitute actual signs in every untouched integer row modulo four."""
    try:
        parity = certificate['half_parity']
        if (certificate.get('kind')!='moving-parity-completion-v1' or
                type(parity) is not int or parity not in (0,1) or
                certificate.get('minimum_half')!=18 or certificate.get('period')!=2 or
                certificate.get('patch')!=6 or
                certificate.get('literal_existence_decided') is not False or
                certificate.get('all_pairs_decided') is not False): return False
        keys,rows = compile_moving_folded(18+parity,2,6,certificate['hole'])
        encoded = certificate['bits']
        if not isinstance(encoded,str) or len(encoded)>2+(len(keys)+3)//4: return False
        bits = int(encoded,16)
        if (bits<0 or bits.bit_length()>len(keys) or certificate.get('variables')!=len(keys)
                or bits>>keys.index(('left',0,0,0))&1): return False
        if any(sum(c*(1-2*(bits>>i&1)) for i,c in row.items())%4 for row in rows):
            return False
        # A guard on the compiler's canonical quotient and endpoint conventions.
        # The length-independent extension is proved by the row partition.
        if (keys,rows)!=compile_moving_folded(20+parity,2,6,certificate['hole']): return False
        return True
    except (KeyError,ValueError,TypeError):
        return False


def _periodic_phase_system(hole,period):
    """Original even-periodic integer rows and checked absolute endpoint traces."""
    if type(period) is not int or period<2 or period%2:
        raise ValueError("require a positive even period")
    _,stencils,_,laws,_ = _parity_trace_data(hole)
    keys = [(*k,j) for k in moving_folded_labels() for j in range(period)]
    positions = {k:i for i,k in enumerate(keys)}
    original = []
    for level in range(period):
        for stencil in stencils.values():
            row = defaultdict(int)
            for (*k,d),c in stencil.items(): row[positions[(*k,(level+d)%period)]] += c
            original.append({i:c for i,c in row.items() if c})
    equations = []
    for level in range(period):
        for j,law in enumerate(laws):
            mask = 0
            rhs = (level-1)%2 if j<2 else level%2 if j<4 else 0
            for a,q,s,d in law['observable']:
                mask ^= 1<<positions[a,q,s,(level+d)%period]
            equations.append((mask,rhs))
    return len(keys),original,equations


def _period_two_phase_system(hole):
    return _periodic_phase_system(hole,2)


def period_two_phase_refusal(hole=19,seconds=300,max_pivots=40000):
    """Generate a scoped Boolean identity, retaining no solver-only refusal."""
    started = time.monotonic()
    trace = parity_trace_certificate(hole)
    size,rows,equations = _period_two_phase_system(hole)
    remaining = seconds-(time.monotonic()-started)
    if remaining<=0: raise ValueError('no time remains for proof extraction')
    analysis = cubic_shell_analysis(size,rows,remaining,max_pivots,
                                    True,extra_binary=equations)
    return dict(kind='moving-period-two-phase-v1',hole=hole,
                status=analysis.get('status','unknown'),trace=trace,
                cubic_proof=analysis.get('cubic_proof',[]),
                elapsed=time.monotonic()-started,
                literal_existence_decided=False,all_pairs_decided=False)


def verify_period_two_phase_refusal(certificate):
    """Rebuild the original binary fibre; multiply saved Boolean identities.

    No rational/ternary quotient, external solver or cubic search is used.
    """
    if (certificate.get('kind')!='moving-period-two-phase-v1' or
            certificate.get('status')!='refused' or
            certificate.get('literal_existence_decided') is not False or
            certificate.get('all_pairs_decided') is not False): return False
    try:
        trace = certificate['trace']
        if trace['hole']!=certificate['hole'] or not verify_parity_trace_certificate(trace):
            return False
        size,rows,equations = _period_two_phase_system(certificate['hole'])
        return verify_cubic_shell_proof(size,rows,
                                       certificate['cubic_proof'],extra_binary=equations)
    except (KeyError,ValueError,TypeError,IndexError):
        return False


def periodic_phase_refusal(hole=19,period=4,seconds=300,max_pivots=12000,prior=None,sweep=False,
                           retain_quadratics=False):
    """Retain original-row identities for a specified even periodic interior."""
    started=time.monotonic()
    trace=parity_trace_certificate(hole)
    size,rows,equations=_periodic_phase_system(hole,period)
    remaining=seconds-(time.monotonic()-started)
    if remaining<=0:raise ValueError('no time remains for proof extraction')
    previous=[]
    if prior is not None:
        if (prior.get('kind')!='moving-periodic-phase-v1' or prior.get('hole')!=hole
                or prior.get('period')!=period or prior.get('trace')!=trace
                or prior.get('status')!='unknown'
                or prior.get('all_pairs_decided') is not False
                or prior.get('literal_existence_decided') is not False):
            raise ValueError('resume requires the same unknown phase system')
        previous=prior.get('cubic_proof')
        if not isinstance(previous,list):raise ValueError('invalid prior proof rounds')
    analysis=cubic_shell_analysis(size,rows,remaining,max_pivots,True,
                                  extra_binary=equations,initial_proofs=previous,sweep=sweep,
                                  retain_quadratics=retain_quadratics)
    return dict(kind='moving-periodic-phase-v1',hole=hole,period=period,
                status=analysis.get('status','unknown'),trace=trace,
                cubic_proof=analysis.get('cubic_proof',[]),
                history=analysis.get('history',[]),stage=analysis.get('stage'),
                free_count=analysis.get('free_count'),
                remaining_variables=analysis.get('remaining_variables'),
                elapsed=time.monotonic()-started,
                literal_existence_decided=False,all_pairs_decided=False)


def verify_periodic_phase_refusal(certificate):
    """Rebuild the scope and check every retained polynomial identity."""
    if (certificate.get('kind')!='moving-periodic-phase-v1' or
            certificate.get('status')!='refused' or
            certificate.get('literal_existence_decided') is not False or
            certificate.get('all_pairs_decided') is not False):return False
    try:
        trace=certificate['trace']
        if trace['hole']!=certificate['hole'] or not verify_parity_trace_certificate(trace):
            return False
        size,rows,equations=_periodic_phase_system(certificate['hole'],certificate['period'])
        return verify_cubic_shell_proof(size,rows,certificate['cubic_proof'],equations)
    except (KeyError,ValueError,TypeError,IndexError):return False


def interior_rank_matrix(hole=19,prime=5):
    """Evaluate the unrestricted Laurent shell matrix at z=2 over a small prime field.

    A nonzero maximal minor here proves the same minor is nonzero over
    Q(z). No period or endpoint identification is imposed on the words.
    """
    if prime not in (5,7,11,13,17,19): raise ValueError('unsupported certificate prime')
    labels = moving_folded_labels()
    positions = {label:i for i,label in enumerate(labels)}
    rows = []
    for _,terms in sorted(moving_folded_stencils(hole)[1].items()):
        row = defaultdict(int)
        for (a,q,s,d),c in terms.items():
            row[positions[a,q,s]] += c*pow(2,d,prime)
        rows.append({i:c%prime for i,c in row.items() if c%prime})
    return labels,rows


def interior_rank_certificate(hole=19):
    """Select a maximal minor; the separate verifier checks its determinant."""
    for prime in (5,7,11,13,17,19):
        labels,rows = interior_rank_matrix(hole,prime)
        basis = {}
        for original in rows:
            row = {i:c for i,c in original.items() if i<356}
            while row:
                pivot = min(row)
                if pivot not in basis:
                    inverse = pow(row[pivot],-1,prime)
                    basis[pivot] = {i:c*inverse%prime for i,c in row.items()}
                    break
                factor = row[pivot]
                for i,c in basis[pivot].items():
                    value = (row.get(i,0)-factor*c)%prime
                    if value: row[i] = value
                    else: row.pop(i,None)
        if len(basis)==len(rows):
            return dict(kind='moving-interior-rank-v1',hole=hole,
                        prime=prime,evaluation=2,columns=sorted(basis),
                        rows=len(rows),variables=len(labels),free_arm=3,
                        literal_existence_decided=False,all_pairs_decided=False)
    raise ValueError('no two-arm minor found; not a rank refusal')


def verify_interior_rank_certificate(certificate):
    """Rebuild a square minor and eliminate by row swaps, without the selector."""
    if (certificate.get('kind')!='moving-interior-rank-v1' or
            certificate.get('prime') not in (5,7,11,13,17,19) or certificate.get('evaluation')!=2 or
            certificate.get('literal_existence_decided') is not False or
            certificate.get('all_pairs_decided') is not False):
        return False
    prime = certificate.get('prime')
    try: labels,rows = interior_rank_matrix(certificate.get('hole'),prime)
    except (TypeError,ValueError): return False
    columns = certificate.get('columns')
    if (not isinstance(columns,list) or len(columns)!=len(rows) or
            any(type(i) is not int or not 0<=i<len(labels) for i in columns) or
            len(set(columns))!=len(columns) or certificate.get('rows')!=len(rows)
            or certificate.get('variables')!=len(labels) or
            certificate.get('free_arm')!=3 or columns!=list(range(356))):
        return False
    # This fixed column order and row-pivot algorithm differs from selection.
    matrix = [[row.get(i,0) for i in columns] for row in rows]
    for j in range(len(rows)):
        pivot = next((r for r in range(j,len(rows)) if matrix[r][j]),None)
        if pivot is None: return False
        matrix[j],matrix[pivot] = matrix[pivot],matrix[j]
        inverse = pow(matrix[j][j],-1,prime)
        for r in range(j+1,len(rows)):
            factor = matrix[r][j]*inverse%prime
            if factor:
                matrix[r][j:] = [(a-factor*b)%prime for a,b in
                                 zip(matrix[r][j:],matrix[j][j:])]
    return True


def moving_folded_residual(scale,coordinates,hole=19,reduced=False):
    """Evaluate every exact physical shell row through the moving-hole strip."""
    if type(scale) is not int or scale<9 or scale%2!=1:
        raise ValueError('require odd scale>=9')
    half=scale//2
    left,interior,right=moving_folded_stencils(hole,reduced)
    result={}
    def put(exponent,value):
        if value:result[exponent]=value
    for (q,offset),row in left.items():
        put(q*scale+offset,sum(c*coordinates[a,k*scale+d] for (a,k,d),c in row.items()))
    for r in range(2,half):
        for (q,s),row in interior.items():
            put(q*scale+s*r,sum(c*coordinates[a,k*scale+u*(r+d)]
                              for (a,k,u,d),c in row.items()))
    for (q,s),row in right.items():
        put(q*scale+s*half,sum(c*coordinates[a,k*scale+u*(half+j)]
                             for (a,k,u,j),c in row.items()))
    return result


def moving_folded_audit(scale,hole=19,reduced=False):
    """Compare the complete strip matrix with every original physical column."""
    if type(scale) is not int or scale<9 or scale%2!=1:
        raise ValueError('require odd scale>=9')
    import full_shorter_coupling as physical
    half=scale//2
    left,interior,right=moving_folded_stencils(hole,reduced)
    actual={}
    def put(exponent,terms):
        if exponent in actual:raise AssertionError('strip row partition overlaps')
        row=defaultdict(int)
        for vertex,c in terms:row[vertex]+=c
        actual[exponent]={v:c for v,c in row.items() if c}
    for (q,d),row in left.items():
        put(q*scale+d,[((a,k*scale+j),c) for (a,k,j),c in row.items()])
    for r in range(2,half):
        for (q,s),row in interior.items():
            put(q*scale+s*r,[((a,k*scale+u*(r+d)),c) for (a,k,u,d),c in row.items()])
    for (q,s),row in right.items():
        put(q*scale+s*half,[((a,k*scale+u*(half+j)),c) for (a,k,u,j),c in row.items()])
    lengths=[n*scale for n in (99,79,23)]
    holes={(1,hole*scale),(1,99*scale)}
    source_lengths=[43*scale-1,79*scale,23*scale] if reduced else lengths
    vertices=[(0,0)]+[(a,d) for a,n in enumerate(source_lengths,1) for d in range(1,n+1)
                      if (a,d) not in holes]
    expected=defaultdict(dict)
    for vertex in vertices:
        column=defaultdict(int,physical.shell_column(lengths,holes,vertex))
        a,d=vertex
        if reduced and a==2 and d>23*scale:
            for exponent,c in physical.shell_column(lengths,holes,(1,d+20*scale-1)).items():
                column[exponent]-=c
        for exponent,c in column.items():
            if c:expected[exponent][vertex]=c
    if {e:r for e,r in actual.items() if r}!=dict(expected):
        raise AssertionError('moving strip differs from the physical shell matrix')
    slices=290 if reduced else 402
    return dict(t=scale,hole=hole,reduced=reduced,matched_physical_columns=201*scale-1,
                matched_source_columns=len(vertices),matched_shell_rows=len(expected),
                slice_signs=slices,row_radius=1,stored_slice_signs=2*slices,path_edges=half-2,
                all_pairs_decided=False,literal_existence_decided=False)


def compile_moving_folded(half,period,patch=2,h=19):
    """Exact periodic-interior quotient of the all-word moving-hole strip.

    End patches are independent. The result extends to every sufficiently
    large half-length with the same residue modulo period, not other supports.
    """
    if (any(type(v) is not int for v in (half,period,patch,h)) or patch<2
                    or period<1 or half<2*patch+4+period or not 1<=h<99):
        raise ValueError('require patch>=2, period>=1, half>=2*patch+4+period and 1<=hole<99')
    keys=[];positions={};rows=[]
    def index(k):
        if k not in positions:positions[k]=len(keys);keys.append(k)
        return positions[k]
    def coordinate(a,q,s,r):
        if r<=patch:return 'left',a,q,s*r
        if r>=half-patch:return 'right',a,q,s,r-half
        return 'period',a,q,s,r%period
    def add(terms):
        row=defaultdict(int)
        for k,c in terms:row[index(k)]+=c
        row={i:c for i,c in row.items() if c}
        if row:rows.append(row)
    left,interior,right=moving_folded_stencils(h)
    for terms in left.values():add([(('left',a,q,d),c) for (a,q,d),c in terms.items()])
    levels=sorted(set(range(2,patch+2))|set(range(half-patch-1,half))|set(range(patch+2,patch+2+period)))
    for r in levels:
        for terms in interior.values():add([(coordinate(a,q,s,r+d),c) for (a,q,s,d),c in terms.items()])
    for terms in right.values():add([(('right',a,q,s,j),c) for (a,q,s,j),c in terms.items()])
    # Record every sign, even when its shell coefficient cancels.
    for arm,n in enumerate((99,79,23),1):
        for q in range(1,n+1):
            if (arm,q) not in ((1,h),(1,99)):index(('left',arm,q,0))
    for arm,q,orientation in moving_folded_labels():
        for level in range(1,patch+1):index(coordinate(arm,q,orientation,level))
        for offset in range(-patch,1):index(coordinate(arm,q,orientation,half+offset))
        for residue in range(period):index(('period',arm,q,orientation,residue))
    index(('left',0,0,0))
    return keys,rows



def moving_folded_search(half=3990,period=4,patch=2,hole=19,seconds=900,nodes=1000000):
    """A bounded search on a named all-word strip quotient; limits are unknown."""
    start=time.monotonic()
    keys,rows=compile_moving_folded(half,period,patch,hole)
    result=dict(mode='moving_folded',half=half,period=period,patch=patch,hole=hole,
                variables=len(keys),rows=len(rows),minimum_half=2*patch+4+period,
                half_residue=half%period,all_pairs_decided=False)
    def done(status,**extra):return dict(result,status=status,elapsed=time.monotonic()-start,**extra)
    if period%2:
        # Fully periodic centres patch+2 .. half-patch-2 contain at least
        # one whole period by the compiler's minimum-half validation.
        return done('ansatz_refused_by_interior_cocycle',
                    certificate=interior_parity_cocycle(hole))
    certificate,basis=binary_elimination(rows)
    if certificate is not None:return done('ansatz_refused_by_parity',certificate=certificate)
    remaining=seconds-(time.monotonic()-start)
    if remaining<=0:return done('unknown')
    joint=joint_sign_closure(len(keys),rows,remaining,short_recovery=True)
    result['closure']=joint['history']
    if joint['conflict']:return done('ansatz_refused_by_joint_fields')
    remaining=seconds-(time.monotonic()-start)
    if not joint['complete'] or remaining<=0:return done('unknown')
    certificate,basis=binary_elimination(joint['rows'])
    if certificate is not None:return done('ansatz_refused_after_quotient')
    engine=make_engine(joint['size'],joint['rows'],basis,remaining,nodes,'connected')
    i,sign=joint['aliases'][keys.index(('left',0,0,0))]
    status,values=engine.run({i:sign})
    if values is None:return done(status,nodes=engine.nodes)
    restored=[sign*values[i] for i,sign in joint['aliases']]
    if any(sum(c*restored[i] for i,c in row.items()) for row in rows):
        raise AssertionError('moving folded witness fails untouched rows')
    return done('sat',nodes=engine.nodes,assignment=[[list(k),v] for k,v in zip(keys,restored)])


def compile_system(half, period, patch_width=40):
    """Exact quotient of every reduced shell equation under this ansatz.

    Levels 0..patch_width and half-patch_width..half remain independent. Between them,
    signs with the same (arm,q,orientation,level mod period) agree.
    Interface rows use their actual levels; only wholly periodic rows
    are represented by one complete period.
    """
    if (type(half) is not int or type(period) is not int or type(patch_width) is not int or
            period < 1 or patch_width < 40 or half < 2*patch_width+42+period):
        raise ValueError('require patch_width>=40, period>=1, half>=2*patch_width+42+period')
    keys, positions, rows = [], {}, []
    def index(key):
        if key not in positions:
            positions[key] = len(keys)
            keys.append(key)
        return positions[key]
    def coordinate(arm, q, s, level):
        if level <= patch_width:
            return ('left',arm,q,s*level)
        if level >= half-patch_width:
            return ('right',arm,q,s,level-half)
        return ('period',arm,q,s,level%period)
    def add(terms):
        row = defaultdict(int)
        for key,c in terms:
            row[index(key)] += c
        row = {i:c for i,c in row.items() if c}
        if row:
            rows.append(row)
    left,right = rf.boundaries()
    for terms in left.values():
        add([(('left',a,q,d),c) for (a,q,d),c in terms.items()])
    # Interface rows can see a patch; all other rows depend only on r mod p.
    levels = sorted(set(range(21,patch_width+21)) |
                    set(range(half-patch_width-20,half-20)) |
                    set(range(patch_width+21,patch_width+21+period)))
    stencil = rf.interior()
    for r in levels:
        for terms in stencil.values():
            add([(coordinate(a,q,s,r+d),c) for (a,q,s,d),c in terms.items()])
    for terms in right.values():
        add([(('right',a,q,s,j),c) for (a,q,s,j),c in terms.items()])
    # Include all literal coordinates, even if a coefficient canceled.
    for a,q,s in rf.labels():
        for r in range(1,patch_width+1): index(coordinate(a,q,s,r))
        for j in range(-patch_width,1): index(coordinate(a,q,s,half+j))
        for r in range(period): index(('period',a,q,s,r))
    index(('left',0,0,0))
    # Level-zero signs are included by left boundary source enumeration.
    return keys,rows


def binary_elimination(rows):
    """Return a refusal or an echelon basis of necessary binary equations."""
    basis = {}
    for label,row in enumerate(rows):
        if sum(row.values())%2:
            return [label],{}
        mask = sum(1<<i for i,c in row.items() if c%2)
        rhs,trace = sum(row.values())//2%2,1<<label
        while mask:
            pivot = mask.bit_length()-1
            if pivot not in basis:
                basis[pivot] = mask,rhs,trace
                break
            old,b,history = basis[pivot]
            mask,rhs,trace = mask^old,rhs^b,trace^history
        if not mask and rhs:
            return [i for i in range(len(rows)) if trace>>i&1],{}
    return None,{pivot:(mask,rhs) for pivot,(mask,rhs,trace) in basis.items()}


def reduced_binary_basis(basis):
    """Eliminate every other pivot from each equivalent binary equation."""
    basis = dict(basis)
    for p in sorted(basis):
        mask,rhs = basis[p]
        for q in basis:
            if q>p and basis[q][0]>>p&1:
                m,b = basis[q]
                basis[q] = m^mask,b^rhs
    return basis


def parity_refusal(rows):
    return binary_elimination(rows)[0]


def binary_shell_quadratics(size, original, seconds=30, max_free=256, extra_binary=()):
    """Exact shell equations modulo eight on the complete parity fibre.

    Write s_i=(-1)**(a_i*x+b_i). Parity makes every row divisible by
    four for every x. Its quotient modulo two has degree at most two.
    Product coordinates are relaxed independently only by the analyzer;
    compilation itself is an identity on every binary choice of x.
    """
    if (type(size) is not int or size<1 or type(max_free) is not int
            or not 0<=max_free<=256 or type(seconds) not in (int,float)
            or not math.isfinite(seconds) or seconds<=0):
        raise ValueError('require positive size/time and a free limit in 0..256')
    started=time.monotonic()
    original=list(original)
    if any(type(i) is not int or not 0<=i<size or type(c) is not int
           for row in original for i,c in row.items()):
        raise ValueError('invalid integer shell row')
    certificate,basis=binary_elimination(original)
    if certificate is not None:
        return dict(complete=True,parity_conflict=True,certificate=certificate)
    for mask,rhs in extra_binary:
        if (type(mask) is not int or mask<0 or mask.bit_length()>size or
                type(rhs) is not int or rhs not in (0,1)):
            raise ValueError('invalid additional binary equation')
        while mask:
            pivot=mask.bit_length()-1
            if pivot not in basis:
                basis[pivot]=mask,rhs
                break
            old,b=basis[pivot];mask^=old;rhs^=b
        if not mask and rhs:
            return dict(complete=True,parity_conflict=True)
    free=[i for i in range(size) if i not in basis]
    n=len(free)
    if n>max_free:
        return dict(complete=False,stage='dimension_limit',free_count=n)
    expressions={i:(1<<j,0) for j,i in enumerate(free)}
    for pivot,(mask,rhs) in sorted(basis.items()):
        mask^=1<<pivot
        value=0
        while mask:
            bit=mask&-mask
            a,b=expressions[bit.bit_length()-1]
            value^=a;rhs^=b;mask^=bit
        expressions[pivot]=value,rhs
    # Check the entire affine map, rather than samples of free assignments.
    for row in original:
        mask,rhs=0,sum(row.values())//2%2
        for i,c in row.items():
            if c%2:
                a,b=expressions[i];mask^=a;rhs^=b
        if mask or rhs:raise AssertionError('parity fibre fails an input row')
    cache={}
    def products(mask):
        if mask not in cache:
            value,left=0,mask
            while left:
                bit=left&-left
                j=bit.bit_length()-1
                # Pair (i,j), i<j, occupies n+j*(j-1)//2+i.
                value^=(mask&(bit-1))<<(n+j*(j-1)//2)
                left^=bit
            cache[mask]=value
        return cache[mask]
    quadratic=[]
    for row in original:
        if time.monotonic()-started>=seconds:
            return dict(complete=False,stage='quadratic_compilation',free_count=n)
        constant,mask=0,0
        linear=defaultdict(int)
        for i,c in row.items():
            a,b=expressions[i]
            c*=(-1 if b else 1)
            constant+=c
            left=a
            while left:
                bit=left&-left
                linear[bit.bit_length()-1]+=c
                left^=bit
            if c%2:mask^=products(a)
        if constant%4 or any(c%2 for c in linear.values()):
            raise AssertionError('row is not identically divisible by four')
        for j,c in linear.items():
            if c//2%2:mask^=1<<j
        quadratic.append((mask,constant//4%2))
    return dict(complete=True,parity_conflict=False,free=free,
                expressions=expressions,quadratic_rows=quadratic,
                product_coordinates=n*(n-1)//2,elapsed=time.monotonic()-started)


def _mapped_boolean_product(polynomial,mapping,output_bytes):
    """XOR mapped monomials without repeatedly copying a wide integer."""
    if polynomial.bit_count()<64:
        row=0
        while polynomial:
            bit=polynomial&-polynomial;polynomial^=bit
            row^=1<<mapping[bit.bit_length()-1]
        return row
    packed=bytearray(output_bytes)
    while polynomial:
        bit=polynomial&-polynomial;polynomial^=bit
        position=mapping[bit.bit_length()-1]
        packed[position//8]^=1<<(position%8)
    return int.from_bytes(packed,'little')


def boolean_cubic_lift(quadratics, variables, seconds=30, max_pivots=20000, proof=False,sweep=False,
                       linear_first=False,quadratic_limit=0):
    """Bounded degree-three Boolean ideal relaxation, with x*x=x.

    Input monomials are constant, singletons, then colexicographic pairs.
    Multiply an independent quadratic basis by every binary variable and
    eliminate in constant/singleton/pair/triple order. A zero constant is a
    necessary condition, not a witness. Resource stops are always unknown.
    With sweep, a full pivot store discards further nonlinear pivots but
    examines subsequent products. At most variables+1 additional linear
    pivots are retained. Discarding any row prevents a compatibility claim.
    linear_first returns checked input-span linear rows before multiplication.
    quadratic_limit retains up to sixteen new checked quadratic rows for a
    caller that will explicitly extend its next round's premises.
    """
    if (type(variables) is not int or not 0<=variables<=192
            or type(max_pivots) is not int or max_pivots<1
            or type(seconds) not in (int,float) or not math.isfinite(seconds)
            or seconds<=0 or type(quadratic_limit) is not int or not 0<=quadratic_limit<=16):
        raise ValueError('require 0..192 variables and positive limits')
    quadratics=list(quadratics)
    terms=[()]+[(i,) for i in range(variables)]+list(
        (i,j) for j in range(variables) for i in range(j))
    width=len(terms)
    output_bytes=(width+variables*(variables-1)*(variables-2)//6+7)//8
    if any(type(row) is not int or row<0 or row.bit_length()>width
           for row in quadratics):
        raise ValueError('invalid quadratic polynomial')
    started=time.monotonic();basis={};processed=0;products=0;discarded=0
    # A sweep normally reaches its time bound. Keep time for extracting the
    # identities already found; otherwise that bound would erase all proof.
    search_seconds=seconds*.8 if (sweep or quadratic_limit) and proof else seconds
    proof_nodes=[];proof_ids={}
    def certificate(node):
        active=1<<node;raw=0;multipliers=[0]*len(independent);visited=0
        while active:
            if visited%1024==0 and time.monotonic()-started>=seconds:
                raise TimeoutError('Boolean certificate extraction time limit')
            visited+=1
            index=active.bit_length()-1;active^=1<<index
            source,parents=proof_nodes[index]
            if source[0]=='input':raw^=1<<source[1]
            else:multipliers[source[1]]^=1<<source[2]
            for parent in parents:active^=1<<parent
        if time.monotonic()-started>=seconds:
            raise TimeoutError('Boolean certificate extraction time limit')
        return dict(raw=raw,multipliers=multipliers)
    def result(status,stage):
        if discarded and status=='compatible_cubic_relaxation':
            status,stage='unknown','pivot_limit'
        linear=[row for p,row in sorted(basis.items()) if p<=variables]
        out=dict(status=status,complete=status!='unknown',stage=stage,
                    variables=variables,rank=len(basis),products=products,
                    processed=processed,discarded=discarded,linear_polynomials=linear,
                    literal_existence_decided=False,
                    elapsed=time.monotonic()-started)
        if proof:
            try:
                out['proof']=[dict(polynomial=basis[p],**certificate(proof_ids[p]))
                              for p in ([0] if status=='refused' else sorted(basis)) if p<=variables]
                if quadratic_limit and independent and not out['proof']:
                    span={q.bit_length()-1:q for q in independent}
                    more=[]
                    for p,row in sorted(basis.items()):
                        if not variables<p<width:continue
                        reduced=row
                        while reduced and reduced.bit_length()-1 in span:
                            reduced^=span[reduced.bit_length()-1]
                        if reduced:
                            span[reduced.bit_length()-1]=reduced
                            more.append(dict(polynomial=row,**certificate(proof_ids[p])))
                            if len(more)>=quadratic_limit:break
                    out['quadratic_proof']=more
            except TimeoutError:
                out.update(proof=[],quadratic_proof=[],status='unknown',complete=False,stage='proof_time_limit',
                           algebra_status=status)
        out['elapsed']=time.monotonic()-started
        return out
    def insert(row,source):
        nonlocal discarded
        parents=array('I') if proof else None
        while row:
            if time.monotonic()-started>=search_seconds:return 'time_limit'
            p=row.bit_length()-1
            if p not in basis:
                if len(basis)>=max_pivots:
                    if not sweep or source[0]=='input':return 'pivot_limit'
                    if p>variables:
                        discarded+=1
                        return 'discarded'
                basis[p]=row
                if proof:
                    proof_ids[p]=len(proof_nodes)
                    proof_nodes.append((source,parents))
                return 'conflict' if p==0 else None
            if proof:parents.append(proof_ids[p])
            row^=basis[p]
        return None
    independent=[]
    for label,row in enumerate(quadratics):
        stop=insert(row,('input',label));processed+=1
        if stop:return result('refused' if stop=='conflict' else 'unknown',stop)
    # Only quadratic pivots exist here. Their span equals the input span,
    # so multiplying this basis generates the same truncated ideal space.
    independent=list(basis.values())
    if linear_first and any(p<=variables for p in basis):
        return result('unknown','linear_reduction')
    def position(term):
        if len(term)==1:return 1+term[0]
        if len(term)==2:
            i,j=term;return 1+variables+j*(j-1)//2+i
        i,j,k=term
        return width+k*(k-1)*(k-2)//6+j*(j-1)//2+i
    # One multiplier map at a time bounds auxiliary memory independently
    # of the number of products. All powers are reduced before elimination.
    for variable in range(variables):
        mapping=[position(tuple(sorted(set(term+(variable,))))) for term in terms]
        for label,polynomial in enumerate(independent):
            if time.monotonic()-started>=search_seconds:return result('unknown','time_limit')
            row=_mapped_boolean_product(polynomial,mapping,output_bytes)
            stop=insert(row,('product',label,variable));products+=1;processed+=1
            if stop=='discarded':continue
            if stop:return result('refused' if stop=='conflict' else 'unknown',stop)
    return result('compatible_cubic_relaxation','complete')


def verify_boolean_cubic_identity(quadratics, variables, identity):
    """Check one explicit sum q_i*l_i=p, without cubic elimination."""
    quadratics=list(quadratics);basis={}
    for row in quadratics:
        while row:
            p=row.bit_length()-1
            if p not in basis:basis[p]=row;break
            row^=basis[p]
    independent=list(basis.values())
    raw=identity.get('raw');multipliers=identity.get('multipliers')
    target=identity.get('polynomial')
    if (type(raw) is not int or raw<0 or raw.bit_length()>len(quadratics)
            or type(target) is not int or target<0 or not isinstance(multipliers,list)
            or len(multipliers) not in (0,len(independent)) or any(type(m) is not int or m<0
            or m.bit_length()>variables for m in multipliers)):
        raise ValueError('invalid Boolean cubic identity')
    value=0
    for i,q in enumerate(quadratics):
        if raw>>i&1:value^=q
    terms=[()]+[(i,) for i in range(variables)]+[
        (i,j) for j in range(variables) for i in range(j)]
    def position(term):
        if not term:return 0
        if len(term)==1:return 1+term[0]
        if len(term)==2:
            i,j=term;return 1+variables+j*(j-1)//2+i
        i,j,k=term
        return len(terms)+k*(k-1)*(k-2)//6+j*(j-1)//2+i
    for variable in range(variables):
        # Reorder the sum: multiply each aggregate quadratic just once.
        q=0
        for row,m in zip(independent,multipliers):
            if m>>variable&1:q^=row
        while q:
            bit=q&-q;term=terms[bit.bit_length()-1];q^=bit
            value^=1<<position(tuple(sorted(set(term+(variable,)))))
    if value!=target:raise ValueError('Boolean cubic polynomial identity failed')
    return True


def append_checked_quadratics(polynomials,variables,identities):
    """Append independent quadratic consequences after checking each identity."""
    if not isinstance(identities,list) or not identities:raise ValueError('empty quadratic round')
    polynomials=list(polynomials)
    span={}
    def insert(row):
        while row and row.bit_length()-1 in span:row^=span[row.bit_length()-1]
        if not row:return False
        span[row.bit_length()-1]=row
        return True
    for row in polynomials:insert(row)
    width=1+variables+variables*(variables-1)//2
    appended=[]
    for identity in identities:
        if not isinstance(identity,dict):raise ValueError('invalid quadratic identity')
        verify_boolean_cubic_identity(polynomials,variables,identity)
        row=identity['polynomial']
        if not variables+1<row.bit_length()<=width or not insert(row):
            raise ValueError('require new quadratic consequences')
        appended.append(row)
    return list(polynomials)+appended


def verify_cubic_shell_proof(size, original, proofs, extra_binary=()):
    """Verify quadratic extensions and affine reductions ending in 1=0.

    Scoped callers must establish why any additional conditions are necessary.
    """
    compiled=binary_shell_quadratics(size,original,seconds=300,max_free=192,
                                    extra_binary=extra_binary)
    if not compiled['complete'] or compiled.get('parity_conflict'):
        raise ValueError('require a complete compatible original parity fibre')
    if not isinstance(proofs,list) or not proofs:raise ValueError('no cubic proof')
    polynomials=[m<<1|b for m,b in compiled['quadratic_rows']]
    variables=len(compiled['free'])
    for index,identities in enumerate(proofs):
        if isinstance(identities,dict):
            if set(identities)!={'quadratics'}:raise ValueError('invalid quadratic round')
            polynomials=append_checked_quadratics(polynomials,variables,identities['quadratics'])
            continue
        if not isinstance(identities,list) or not identities:raise ValueError('empty cubic proof round')
        linear=[]
        for identity in identities:
            verify_boolean_cubic_identity(polynomials,variables,identity)
            row=identity['polynomial']
            if not row or row.bit_length()>variables+1:raise ValueError('require nonzero linear consequences')
            linear.append(row)
        if 1 in linear:
            if index!=len(proofs)-1:raise ValueError('trailing proof after contradiction')
            return True
        free,expressions=boolean_linear_substitution(variables,linear)
        if len(free)>=variables:raise ValueError('cubic proof did not reduce parameters')
        polynomials=substitute_boolean_quadratics(polynomials,expressions,len(free))
        variables=len(free)
    raise ValueError('cubic proof has no constant contradiction')


def boolean_linear_substitution(variables, linear):
    """Parameterize binary linear zero-polynomials in free original bits."""
    if type(variables) is not int or not 0<=variables<=192:
        raise ValueError('require 0..192 binary variables')
    linear=list(linear)
    basis={}
    for row in linear:
        if type(row) is not int or row<0 or row.bit_length()>variables+1:
            raise ValueError('invalid linear polynomial')
        while row:
            p=row.bit_length()-1
            if p==0:raise ValueError('inconsistent linear polynomials')
            if p not in basis:basis[p]=row;break
            row^=basis[p]
    free=[i for i in range(variables) if i+1 not in basis]
    expressions={i:1<<(j+1) for j,i in enumerate(free)}
    for p,row in sorted(basis.items()):
        row^=1<<p
        value=row&1;row>>=1
        while row:
            bit=row&-row;value^=expressions[bit.bit_length()-1];row^=bit
        expressions[p-1]=value
    # Every relation is checked as a polynomial identity.
    for row in linear:
        value=row&1;row>>=1
        while row:
            bit=row&-row;value^=expressions[bit.bit_length()-1];row^=bit
        if value:raise AssertionError('linear recovery does not satisfy input')
    return free,[expressions[i] for i in range(variables)]


def substitute_boolean_quadratics(polynomials, expressions, new_variables):
    """Exact polynomial substitution in F_2[x]/(x_i^2-x_i), degree<=2."""
    if type(new_variables) is not int or not 0<=new_variables<=192:
        raise ValueError('require 0..192 new variables')
    expressions=list(expressions)
    old_variables=len(expressions)
    if any(type(e) is not int or e<0 or e.bit_length()>new_variables+1
           for e in expressions):raise ValueError('invalid affine expression')
    terms=[1]+list(expressions)
    for j in range(old_variables):
        for i in range(j):
            left,right=expressions[i],expressions[j]
            value=(left&1)*(right&1)
            if left&1:value^=right&~1
            if right&1:value^=left&~1
            left>>=1;right>>=1
            while left:
                bit=left&-left;a=bit.bit_length()-1;left^=bit
                rest=right
                while rest:
                    bit=rest&-rest;b=bit.bit_length()-1;rest^=bit
                    if a==b:position=1+a
                    else:
                        lo,hi=sorted((a,b))
                        position=1+new_variables+hi*(hi-1)//2+lo
                    value^=1<<position
            terms.append(value)
    out=[]
    for polynomial in polynomials:
        if type(polynomial) is not int or polynomial<0 or polynomial.bit_length()>len(terms):
            raise ValueError('invalid quadratic polynomial')
        value=0
        while polynomial:
            bit=polynomial&-polynomial;value^=terms[bit.bit_length()-1];polynomial^=bit
        out.append(value)
    return out


def cubic_shell_analysis(size, original, seconds=30, max_pivots=20000, proof=False,
                         extra_binary=(),initial_proofs=(),sweep=False,retain_quadratics=False):
    """Lift necessary mod-eight shell quadratics; no arbitrary-support claim."""
    if retain_quadratics and not proof:raise ValueError('quadratic reuse requires explicit proofs')
    started=time.monotonic()
    compiled=binary_shell_quadratics(size,original,seconds,max_free=192,
                                    extra_binary=extra_binary)
    if not compiled['complete']:return compiled
    if compiled['parity_conflict']:
        return dict(complete=True,status='refused_by_parity',literal_existence_decided=False)
    remaining=seconds-(time.monotonic()-started)
    if remaining<=0:return dict(complete=False,status='unknown',stage='compilation')
    polynomials=[mask<<1|rhs for mask,rhs in compiled['quadratic_rows']]
    variables=len(compiled['free']);history=[];parameter_ids=list(compiled['free']);proofs=[]
    recovery=[1<<(i+1) for i in range(variables)]
    for identities in initial_proofs:
        if isinstance(identities,dict):
            if set(identities)!={'quadratics'}:raise ValueError('invalid prior quadratic round')
            polynomials=append_checked_quadratics(polynomials,variables,identities['quadratics'])
            if proof:proofs.append(identities)
            continue
        if not isinstance(identities,list):raise ValueError('invalid prior proof round')
        if not identities:continue
        linear=[]
        for identity in identities:
            verify_boolean_cubic_identity(polynomials,variables,identity)
            row=identity['polynomial']
            if not row or row.bit_length()>variables+1:
                raise ValueError('prior consequence must be nonzero and linear')
            linear.append(row)
        free,expressions=boolean_linear_substitution(variables,linear)
        if len(free)>=variables:raise ValueError('prior round does not reduce parameters')
        polynomials=substitute_boolean_quadratics(polynomials,expressions,len(free))
        recovery=substitute_boolean_quadratics(recovery,expressions,len(free))
        parameter_ids=[parameter_ids[i] for i in free]
        variables=len(free)
        if proof:proofs.append(identities)
    while True:
        remaining=seconds-(time.monotonic()-started)
        if remaining<=0:
            result=dict(complete=False,status='unknown',stage='substitution_time_limit')
            break
        result=boolean_cubic_lift(polynomials,variables,remaining,max_pivots,proof,sweep,
                                  linear_first=True,quadratic_limit=16 if retain_quadratics else 0)
        more=result.pop('quadratic_proof',[])
        if proof:
            identities=result.pop('proof')
            if identities:proofs.append(identities)
        history.append({k:v for k,v in result.items() if k!='linear_polynomials'})
        if result['status']=='refused':break
        if result['stage']=='proof_time_limit':break
        linear=result['linear_polynomials']
        if not linear:
            if more:
                polynomials=append_checked_quadratics(polynomials,variables,more)
                proofs.append(dict(quadratics=more))
                continue
            break
        free,expressions=boolean_linear_substitution(variables,linear)
        polynomials=substitute_boolean_quadratics(polynomials,expressions,len(free))
        recovery=substitute_boolean_quadratics(recovery,expressions,len(free))
        parameter_ids=[parameter_ids[i] for i in free]
        variables=len(free)
    result['history']=history
    if proof:result['cubic_proof']=proofs
    result['remaining_variables']=variables
    result['recovery']=recovery
    result['parameter_ids']=parameter_ids
    result['literal_existence_decided']=False
    result['free']=compiled['free']
    result['elapsed']=time.monotonic()-started
    return result


def cubic_sign_basis(size, original, analysis):
    """Retain cubic-derived affine recovery during untouched integer search.

    Recovery uses negative-sign bits. The literal engine uses positive-sign
    bits, so an equation's right side changes by its mask's cardinality.
    """
    certificate,basis=binary_elimination(original)
    if certificate is not None:raise ValueError('inconsistent original parity')
    if analysis.get('status')=='refused':raise ValueError('refused cubic system')
    free=analysis['free'];parameters=analysis['parameter_ids']
    recovery=analysis['recovery']
    if (len(free)!=len(recovery) or any(type(i) is not int or not 0<=i<size
            for i in free+parameters)):
        raise ValueError('invalid cubic recovery coordinates')
    for i,expression in zip(free,recovery):
        if type(expression) is not int or expression<0 or expression.bit_length()>len(parameters)+1:
            raise ValueError('invalid cubic recovery expression')
        mask=1<<i
        for j,p in enumerate(parameters):
            if expression>>(j+1)&1:mask^=1<<p
        rhs=(expression&1)^(mask.bit_count()%2)
        while mask:
            p=mask.bit_length()-1
            if p not in basis:basis[p]=mask,rhs;break
            old,c=basis[p];mask^=old;rhs^=c
        if not mask and rhs:raise ValueError('conflicting cubic recovery')
    return basis


def dyadic_quadratic_analysis(size, original, seconds=30, max_free=256):
    """Linear consequences of the exact mod-eight quadratic equations.

    XOR traces certify every consequence. A compatible product relaxation
    is neither a binary quadratic solution nor a literal shell signing.
    """
    original=list(original)
    started=time.monotonic()
    compiled=binary_shell_quadratics(size,original,seconds,max_free)
    if not compiled['complete']:return compiled
    if compiled['parity_conflict']:
        return dict(complete=True,status='refused_by_parity',
                    certificate=compiled['certificate'])
    basis={}
    for label,(mask,rhs) in enumerate(compiled['quadratic_rows']):
        trace=1<<label
        while mask:
            if time.monotonic()-started>=seconds:
                return dict(complete=False,stage='quadratic_elimination')
            pivot=mask.bit_length()-1
            if pivot not in basis:
                basis[pivot]=mask,rhs,trace
                break
            a,b,c=basis[pivot];mask^=a;rhs^=b;trace^=c
        if not mask and rhs:
            return dict(complete=True,status='refused_by_quadratics',
                        free=compiled['free'],certificate=[i for i in range(len(original))
                                                         if trace>>i&1])
    relations=[]
    for pivot,(mask,rhs,trace) in sorted(basis.items()):
        if pivot<len(compiled['free']):
            relations.append(dict(mask=mask,rhs=rhs,
                                  certificate=[i for i in range(len(original)) if trace>>i&1]))
    return dict(complete=True,status='compatible_product_relaxation',
                free=compiled['free'],quadratic_rank=len(basis),
                product_coordinates=compiled['product_coordinates'],
                linear_relations=relations,elapsed=time.monotonic()-started,
                literal_existence_decided=False)


def verify_dyadic_consequence(size, original, consequence):
    """Rebuild the full fibre and XOR the named untouched quadratic rows."""
    original=list(original)
    compiled=binary_shell_quadratics(size,original,seconds=300)
    if not compiled['complete'] or compiled.get('parity_conflict'):
        raise ValueError('no complete compatible parity fibre')
    certificate=consequence.get('certificate')
    if (not isinstance(certificate,list)
            or any(type(i) is not int or not 0<=i<len(original) for i in certificate)
            or len(set(certificate))!=len(certificate)):
        raise ValueError('invalid quadratic XOR trace')
    mask,rhs=0,0
    for i in certificate:
        a,b=compiled['quadratic_rows'][i];mask^=a;rhs^=b
    if (type(consequence.get('mask')) is not int or type(consequence.get('rhs')) is not int
            or consequence['rhs'] not in (0,1)
            or (mask,rhs)!=(consequence['mask'],consequence['rhs'])):
        raise ValueError('quadratic consequence did not verify')
    return True


def parity_sign_quotient(size,original,seconds=30):
    """Merge signs with identical affine dependencies in the full binary fibre."""
    if (type(size) is not int or size<1 or type(seconds) not in (int,float)
            or not math.isfinite(seconds) or seconds<=0):
        raise ValueError('require positive size and finite positive time')
    start = time.monotonic()
    original = list(original)
    basis = {}
    def limited(): return dict(complete=False,rank_lower_bound=len(basis),elapsed=time.monotonic()-start)
    for row in original:
        if any(type(i) is not int or not 0<=i<size or type(c) is not int for i,c in row.items()):
            raise ValueError('invalid integer shell row')
        if sum(row.values())%2: return dict(complete=True,conflict=True)
        mask = sum(1<<i for i,c in row.items() if c%2)
        rhs = sum(row.values())//2%2
        while mask:
            if time.monotonic()-start>=seconds: return limited()
            p = mask.bit_length()-1
            if p not in basis:
                basis[p] = mask,rhs
                break
            old,b = basis[p]
            mask,rhs = mask^old,rhs^b
        if not mask and rhs: return dict(complete=True,conflict=True)
    rank = len(basis)
    free = [i for i in range(size) if i not in basis]
    expressions = {i:(1<<j,0) for j,i in enumerate(free)}
    for p,(mask,rhs) in sorted(basis.items()):
        if time.monotonic()-start>=seconds: return limited()
        mask ^= 1<<p
        expression = 0
        while mask:
            bit = mask&-mask
            a,b = expressions[bit.bit_length()-1]
            expression,rhs = expression^a,rhs^b
            mask ^= bit
        expressions[p] = expression,rhs
    # Check the affine parameterization against every untouched binary row.
    for row in original:
        if time.monotonic()-start>=seconds: return limited()
        expression,rhs = 0,sum(row.values())//2%2
        for i,c in row.items():
            if c%2:
                a,b = expressions[i]
                expression,rhs = expression^a,rhs^b
        if expression or rhs: raise AssertionError('binary fibre fails an original row')
    positions,aliases = {},[]
    for i in range(size):
        mask,rhs = expressions[i]
        if mask not in positions: positions[mask] = len(positions)
        aliases.append((positions[mask],-1 if rhs else 1))
    compact = []
    for row in original:
        out = defaultdict(int)
        for i,c in row.items():
            j,s = aliases[i]
            out[j] += s*c
        out = {j:c for j,c in out.items() if c}
        if out: compact.append(out)
    return dict(complete=True,conflict=False,size=len(positions),rows=compact,aliases=aliases,
                rank=rank,free=len(free),binary_fibre_verified=True,elapsed=time.monotonic()-start)


def affine_shell_closure(size, original, seconds=30, rounds=20, local_rank=12, blocks=()):
    """Necessary binary closure using exact local sign-pattern affine hulls.

    All parameters remain binary coordinates of original signs. A local hull
    contains every locally valid assignment, so adding its equations never
    removes a literal solution. A compatible hull is not a sign witness.
    Optional blocks are tuples of row indices tested simultaneously, retaining
    correlations lost by taking the affine hull of each row separately.
    """
    if (type(size) is not int or size<1 or type(seconds) not in (int,float)
            or not math.isfinite(seconds) or seconds<=0 or type(rounds) is not int
            or rounds<1 or type(local_rank) is not int or not 0<=local_rank<=16):
        raise ValueError('require positive size/time/rounds and local rank in 0..16')
    original = list(original)
    if any(type(i) is not int or not 0<=i<size or type(c) is not int
           for row in original for i,c in row.items()):
        raise ValueError('invalid integer shell row')
    blocks = list(blocks)
    if any(not isinstance(block,(list,tuple)) or not block or
           any(type(i) is not int or not 0<=i<len(original) for i in block)
           for block in blocks):
        raise ValueError('require nonempty blocks of valid row indices')
    clusters = [(i,) for i in range(len(original))]+[tuple(b) for b in blocks]
    start = time.monotonic()
    basis,cache,history = {},{},[]
    def add(mask,rhs):
        while mask:
            p = mask.bit_length()-1
            if p not in basis:
                basis[p] = mask,rhs
                return True
            old,b = basis[p]
            mask,rhs = mask^old,rhs^b
        return not rhs
    def result(complete,conflict=False,**extra):
        return dict(complete=complete,conflict=conflict,basis=dict(basis),
                    rank=len(basis),free=size-len(basis),history=history,
                    cache_entries=len(cache),elapsed=time.monotonic()-start,**extra)
    for row in original:
        if time.monotonic()-start>=seconds: return result(False,stage='initial_parity')
        total = sum(row.values())
        if total%2 or not add(sum(1<<i for i,c in row.items() if c%2),total//2%2):
            return result(True,True,stage='initial_parity')
    for iteration in range(rounds):
        before = len(basis)
        expressions = {}
        for i in range(size):
            if time.monotonic()-start>=seconds: return result(False,stage='parameterization')
            if i not in basis:
                expressions[i] = 1<<i,0
                continue
            mask,rhs = basis[i]
            mask ^= 1<<i
            out = 0
            while mask:
                bit = mask&-mask
                a,b = expressions[bit.bit_length()-1]
                out,rhs = out^a,rhs^b
                mask ^= bit
            expressions[i] = out,rhs
        skipped = 0
        for label,cluster in enumerate(clusters):
            if time.monotonic()-start>=seconds: return result(False,stage='local_hulls')
            local_basis,generators,conditions = {},[],[]
            for row_index in cluster:
                terms = defaultdict(int)
                for i,c in original[row_index].items():
                    mask,rhs = expressions[i]
                    local = 0
                    while mask:
                        p = mask.bit_length()-1
                        if p not in local_basis:
                            bit = 1<<len(generators)
                            generators.append(mask)
                            local_basis[p] = mask,bit
                            local ^= bit
                            break
                        m,b = local_basis[p]
                        mask,local = mask^m,local^b
                    terms[local] += c*(-1 if rhs else 1)
                conditions.append(tuple(sorted((m,c) for m,c in terms.items() if c)))
            n = len(generators)
            if n>local_rank:
                skipped += 1
                continue
            signature = n,tuple(conditions)
            if signature not in cache:
                valid = []
                for v in range(1<<n):
                    if time.monotonic()-start>=seconds: return result(False,stage='local_enumeration')
                    if all(not sum(c*(-1 if (m&v).bit_count()%2 else 1) for m,c in terms)
                           for terms in signature[1]):
                        valid.append(v)
                if not valid:
                    return result(True,True,stage='empty_local_hull',row=label,block=cluster)
                # Row-echelon span of differences gives the affine hull.
                span = {}
                for v in valid[1:]:
                    m = v^valid[0]
                    while m:
                        p = m.bit_length()-1
                        if p not in span:
                            span[p] = m
                            break
                        m ^= span[p]
                equations = []
                for j in range(n):
                    if j in span: continue
                    m = 1<<j
                    for p in sorted(span):
                        if (span[p]&m).bit_count()%2: m |= 1<<p
                    equations.append((m,(m&valid[0]).bit_count()%2))
                cache[signature] = equations
            for local,rhs in cache[signature]:
                mask = 0
                for j,g in enumerate(generators):
                    if local>>j&1: mask ^= g
                if not add(mask,rhs):
                    return result(True,True,stage='inconsistent_hulls',row=label,block=cluster)
        history.append(dict(round=iteration+1,added=len(basis)-before,skipped=skipped))
        if len(basis)==before: return result(True,fixed_point=True)
    return result(False,stage='round_limit')


def binary_relation_overlap(left, right):
    """Coordinate maps for the intersection of two independent GF(2) spans.

    Each returned pair (a,b) denotes the same original linear form in the
    left and right generators. These pairs form a basis of the intersection.
    """
    basis, overlap = {}, []
    for side, generators in enumerate((left,right)):
        for j,mask in enumerate(generators):
            a,b = (1<<j,0) if side==0 else (0,1<<j)
            while mask:
                pivot = mask.bit_length()-1
                if pivot not in basis:
                    basis[pivot] = mask,a,b
                    break
                old,c,d = basis[pivot]
                mask,a,b = mask^old,a^c,b^d
            if not mask:
                if side==0 or not a or not b:
                    raise ValueError('generators must be independent')
                overlap.append((a,b))
    return overlap


def relational_shell_consistency(size, original, pairs=(), seconds=30, local_rank=12):
    """Keep exact local sign relations, then semijoin their shared linear forms.

    Unlike affine hull closure this retains holes inside each local relation.
    A deletion lacks a compatible assignment in another necessary relation,
    so cannot remove a full literal solution. Empty means a scoped refusal;
    a nonempty fixed point is only a relaxation, never a sign witness.
    Only supplied row pairs are joined; oversized rows are safely skipped.
    """
    if (type(size) is not int or size<1 or type(seconds) not in (int,float)
            or not math.isfinite(seconds) or seconds<=0 or type(local_rank) is not int
            or not 0<=local_rank<=16):
        raise ValueError('require positive size/time and local rank in 0..16')
    original = list(original)
    if any(type(i) is not int or not 0<=i<size or type(c) is not int
           for row in original for i,c in row.items()):
        raise ValueError('invalid integer shell row')
    pairs = list(pairs)
    if any(not isinstance(pair,(tuple,list)) or len(pair)!=2 or
           any(type(i) is not int or not 0<=i<len(original) for i in pair)
           for pair in pairs):
        raise ValueError('require pairs of valid row indices')
    start = time.monotonic()
    tables,skipped,joins,history = {},[],[],[]
    def expired(): return time.monotonic()-start>=seconds
    def result(complete,conflict=False,**extra):
        return dict(complete=complete,conflict=conflict,tables=tables,
                    skipped=skipped,joins=len(joins),history=history,
                    elapsed=time.monotonic()-start,**extra)
    refusal,basis = binary_elimination(original)
    if refusal is not None: return result(True,True,stage='initial_parity')
    expressions = {}
    for i in range(size):
        if expired(): return result(False,stage='parameterization')
        if i not in basis:
            expressions[i] = 1<<i,0
            continue
        mask,rhs = basis[i]
        mask ^= 1<<i
        out = 0
        while mask:
            bit = mask&-mask
            a,b = expressions[bit.bit_length()-1]
            out,rhs = out^a,rhs^b
            mask ^= bit
        expressions[i] = out,rhs
    for index,row in enumerate(original):
        local_basis,generators,terms = {},[],defaultdict(int)
        for i,c in row.items():
            mask,rhs = expressions[i]
            local = 0
            while mask:
                pivot = mask.bit_length()-1
                if pivot not in local_basis:
                    bit = 1<<len(generators)
                    generators.append(mask)
                    local_basis[pivot] = mask,bit
                    local ^= bit
                    break
                old,b = local_basis[pivot]
                mask,local = mask^old,local^b
            terms[local] += c*(-1 if rhs else 1)
        if len(generators)>local_rank:
            skipped.append(index)
            continue
        terms = [(m,c) for m,c in terms.items() if c]
        valid = []
        for v in range(1<<len(generators)):
            if expired(): return result(False,stage='enumeration')
            if not sum(c*(-1 if (m&v).bit_count()%2 else 1) for m,c in terms):
                valid.append(v)
        tables[index] = dict(generators=generators,valid=valid)
        if not valid: return result(True,True,stage='empty_row',row=index)
    for i,j in sorted(set(tuple(sorted(pair)) for pair in pairs)):
        if expired(): return result(False,stage='overlap')
        if i==j or i not in tables or j not in tables: continue
        overlap = binary_relation_overlap(tables[i]['generators'],tables[j]['generators'])
        if overlap: joins.append((i,j,overlap))
    def project(v,masks):
        return sum(((v&m).bit_count()%2)<<k for k,m in enumerate(masks))
    while True:
        removed = 0
        for i,j,overlap in joins:
            if expired(): return result(False,stage='semijoin')
            left,right = tables[i]['valid'],tables[j]['valid']
            lp = [project(v,[a for a,b in overlap]) for v in left]
            rp = [project(v,[b for a,b in overlap]) for v in right]
            common = set(lp)&set(rp)
            if not common: return result(True,True,stage='empty_overlap',pair=(i,j))
            new_left = [v for v,p in zip(left,lp) if p in common]
            new_right = [v for v,p in zip(right,rp) if p in common]
            removed += len(left)+len(right)-len(new_left)-len(new_right)
            tables[i]['valid'],tables[j]['valid'] = new_left,new_right
        history.append(removed)
        if not removed: return result(True,stage='fixed_point')


def folded_hull_diagnostic(half=3990,period=4,patch=2,hole=19,seconds=600,
                           local_rank=16,joint_fields=False,exact_relations=False,relation_search=False,nodes=1000000):
    """Necessary joint-row hulls on one periodic moving-hole word system.

    Choose, for each row, the two rows sharing the most literal coordinates
    (ties by row index). This does not claim to inspect every row pair. A
    complete fixed point may still skip blocks above the local rank limit.
    """
    if (type(seconds) not in (int,float) or not math.isfinite(seconds) or seconds<=0
            or type(local_rank) is not int or not 0<=local_rank<=16):
        raise ValueError('require positive finite time and local rank in 0..16')
    start = time.monotonic()
    keys,rows = compile_moving_folded(half,period,patch,hole)
    size = len(keys)
    source_rows = rows
    report = dict(mode='folded_relations' if exact_relations else 'folded_hulls',half=half,period=period,patch=patch,hole=hole,
                  input_variables=size,input_rows=len(rows),local_rank=local_rank,
                  all_pairs_decided=False)
    def done(**extra):
        return dict(report,elapsed=time.monotonic()-start,**extra)
    if joint_fields:
        remaining = seconds-(time.monotonic()-start)
        if remaining<=0:return done(complete=False,stage='compilation')
        joint = joint_sign_closure(size,rows,remaining,short_recovery=True)
        report['joint_history'] = joint['history']
        if not joint['complete'] or joint['conflict']:
            return done(complete=joint['complete'],conflict=joint['conflict'],stage='joint_fields')
        size,rows = joint['size'],joint['rows']
    links = defaultdict(list)
    for j,row in enumerate(rows):
        for i in row:links[i].append(j)
    blocks = set()
    for j,row in enumerate(rows):
        neighbors = defaultdict(int)
        for i in row:
            for k in links[i]:
                if k!=j:neighbors[k] += 1
        for k in sorted(neighbors,key=lambda k:(-neighbors[k],k))[:2]:
            blocks.add(tuple(sorted((j,k))))
        if time.monotonic()-start>=seconds:
            return done(complete=False,stage='block_selection')
    remaining = seconds-(time.monotonic()-start)
    if remaining<=0:return done(complete=False,stage='block_selection')
    if exact_relations:
        hull = relational_shell_consistency(size,rows,pairs=sorted(blocks),
                                           seconds=remaining,local_rank=local_rank)
        if relation_search and hull['complete'] and not hull['conflict']:
            remaining = seconds-(time.monotonic()-start)
            if remaining<=0:
                report['search'] = dict(status='unknown',nodes=0)
            else:
                engine = make_relational_engine(size,rows,hull,remaining,nodes)
                remaining = seconds-(time.monotonic()-start)
                if remaining<=0:
                    report['search'] = dict(status='unknown',nodes=0)
                else:
                    engine.seconds = remaining
                    status,values = engine.run({0:1})
                    report['search'] = dict(status=status,nodes=engine.nodes,
                                           auxiliaries=len(engine.values)-size)
                    if values is not None:
                        restored = ([sign*values[i] for i,sign in joint['aliases']]
                                    if joint_fields else values[:size])
                        if any(sum(c*restored[i] for i,c in row.items()) for row in source_rows):
                            raise AssertionError('relational witness fails untouched rows')
                        report['assignment'] = [[list(k),v] for k,v in zip(keys,restored)]
        tables = hull.pop('tables')
        hull['tables'] = len(tables)
        hull['patterns'] = sum(len(t['valid']) for t in tables.values())
        hull['skipped'] = len(hull['skipped'])
    else:
        hull = affine_shell_closure(size,rows,seconds=remaining,local_rank=local_rank,
                                   blocks=sorted(blocks))
    report.update(variables=size,rows=len(rows),blocks=len(blocks))
    return done(analysis={k:v for k,v in hull.items() if k!='basis'},
                complete=hull['complete'] and report.get('search',{}).get('status')!='unknown',
                conflict=hull['conflict'] or report.get('search',{}).get('status')=='unsat')


def quadratic_sign_lift(kernel):
    """Necessary linear equations over F_3 for all pair products of free signs.

    Coordinate zero of the lift denotes the constant one. Every other
    coordinate is a product of two distinct free original coordinates.
    A solution of the lift need not factor into such products.
    """
    free,expressions = kernel['free'],kernel['expressions']
    if (len(free)>128 or len(set(free))!=len(free)
            or any(type(i) is not int or i<0 for i in free)):
        raise ValueError('require at most 128 distinct original free coordinates')
    pairs = [None]+[(a,b) for j,a in enumerate(free) for b in free[j+1:]]
    positions = {pair:i for i,pair in enumerate(pairs)}
    rows = []
    for one,two in expressions.values():
        if (type(one) is not int or type(two) is not int or one<0 or two<0
                or one&two or (one|two).bit_length()>len(free)):
            raise ValueError('invalid ternary kernel expression')
        terms = [(free[j],1 if one>>j&1 else 2) for j in range(len(free))
                 if (one|two)>>j&1]
        row = {0:(len(terms)-1)%3}
        for j,(a,c) in enumerate(terms):
            for b,d in terms[j+1:]: row[positions[a,b]] = 2*c*d%3
        row = {i:c for i,c in row.items() if c}
        if row: rows.append(row)
    return pairs,rows


def quadratic_sign_analysis(size,rows,seconds=30):
    """Verified modular lift and necessary parity relations, never a witness."""
    if type(seconds) not in (int,float) or not math.isfinite(seconds) or seconds<=0:
        raise ValueError('require positive finite time')
    start = time.monotonic()
    base = ternary_analysis(size,rows,seconds,retain_kernel=True)
    result = dict(complete=False,literal_existence_decided=False)
    if not base['complete']: return dict(result,stage='base_kernel')
    if base['forced_zero_coordinates']:
        return dict(complete=True,conflict=True,stage='base_nonzero',
                    literal_existence_decided=False)
    if base['nullity']>128: return dict(result,stage='dimension_limit')
    pairs,lifted = quadratic_sign_lift(base['kernel'])
    remaining = seconds-(time.monotonic()-start)
    if remaining<=0: return dict(result,stage='lift_compilation')
    report = ternary_analysis(len(pairs),lifted,remaining,retain_kernel=True)
    result.update(base_nullity=base['nullity'],product_coordinates=len(pairs),
                  product_rows=len(lifted),elapsed=time.monotonic()-start)
    if not report['complete']: return dict(result,stage='product_kernel')
    parity = set()
    relations = ternary_copy_relations(report['kernel'])
    for i,j,s in relations:
        mask = 0
        for index in (i,j):
            if pairs[index] is not None:
                for v in pairs[index]: mask ^= 1<<v
        parity.add((mask,0 if s==1 else 1))
    return dict(result,complete=True,conflict=bool(report['forced_zero_coordinates']),
                product_rank=report['rank'],product_nullity=report['nullity'],
                kernel_verified=report['kernel_verified'],
                forced_zero_count=len(report['forced_zero_coordinates']),
                parity_rows=sorted(parity),nonzero_relations=len(relations))


def ternary_add(left, right):
    """Add disjoint (coefficient-one, coefficient-two) bitsets over F_3."""
    a,b = left
    c,d = right
    zero_left,zero_right = ~(a|b),~(c|d)
    return ((a&zero_right)|(c&zero_left)|(b&d),
            (b&zero_right)|(d&zero_left)|(a&c))


def ternary_echelon(rows, seconds=30):
    """Bounded homogeneous elimination; never a literal-sign certificate.

    Bitsets avoid repeatedly copying sparse dictionaries after fill-in.
    A timeout returns only the rank of the processed independent rows.
    Even a complete rank computation does not enforce nonzero coordinates.
    """
    if type(seconds) not in (int,float) or not math.isfinite(seconds) or seconds<=0:
        raise ValueError('require a positive finite elimination time')
    start = time.monotonic()
    basis,operations,processed = {},0,0
    for row in rows:
        if any(type(i) is not int or i<0 or type(c) is not int
               for i,c in row.items()):
            raise ValueError('require nonnegative coordinate indices and integer coefficients')
        a = sum(1<<i for i,c in row.items() if c%3==1)
        b = sum(1<<i for i,c in row.items() if c%3==2)
        while a|b:
            if time.monotonic()-start >= seconds:
                return dict(complete=False,basis=basis,operations=operations,
                            processed_rows=processed,elapsed=time.monotonic()-start)
            pivot = (a|b).bit_length()-1
            if pivot not in basis:
                basis[pivot] = (b,a) if b>>pivot&1 else (a,b)
                break
            c,d = basis[pivot]
            a,b = ternary_add((a,b),(d,c) if a>>pivot&1 else (c,d))
            operations += 1
        processed += 1
    return dict(complete=True,basis=basis,operations=operations,
                processed_rows=processed,elapsed=time.monotonic()-start)


def ternary_analysis(size, original, seconds=30, sparse_pivots=40000, retain_kernel=False):
    """Rank and an independently recounted kernel, keeping original coordinates.

    A modular kernel allows zero entries; it is NOT a literal assignment.
    The sparse prefix chooses low-degree columns before bitset fill-in.
    Resource exhaustion returns a rank lower bound, never a refusal.
    """
    if (type(size) is not int or size<1 or type(sparse_pivots) is not int or sparse_pivots<0
            or type(seconds) not in (int,float) or not math.isfinite(seconds) or seconds<=0):
        raise ValueError('require positive size/time and a nonnegative sparse pivot budget')
    start = time.monotonic()
    deadline = start+seconds
    original = list(original)
    rows,columns = {},defaultdict(set)
    for r,row in enumerate(original):
        if any(type(i) is not int or not 0<=i<size or type(c) is not int for i,c in row.items()):
            raise ValueError('invalid integer shell row')
        reduced = {i:c%3 for i,c in row.items() if c%3}
        if reduced:
            rows[r] = reduced
            for i in reduced: columns[i].add(r)
    heap = [(len(v),i) for i,v in columns.items()]
    heapq.heapify(heap)
    pivots = []
    def unknown(rank,stage):
        return dict(complete=False,rank_lower_bound=rank,stage=stage,
                    elapsed=time.monotonic()-start,literal_existence_decided=False)
    while heap and len(pivots)<sparse_pivots:
        if time.monotonic()>=deadline: return unknown(len(pivots),'sparse')
        degree,p = heapq.heappop(heap)
        if p not in columns or degree!=len(columns[p]): continue
        r = min(columns[p],key=lambda r:(len(rows[r]),r))
        row = rows.pop(r)
        factor = row[p]  # Every nonzero element of F_3 is its own inverse.
        row = {i:c*factor%3 for i,c in row.items()}
        pivots.append((p,row))
        for i in row: columns[i].remove(r)
        for other in list(columns[p]):
            if time.monotonic()>=deadline: return unknown(len(pivots),'sparse')
            target = rows[other]
            factor = target[p]
            for i,c in row.items():
                old = target.get(i,0)
                value = (old-factor*c)%3
                if value:
                    target[i] = value
                    if not old: columns[i].add(other)
                elif old:
                    del target[i]
                    columns[i].remove(other)
            if not target: del rows[other]
        del columns[p]
        for i in row:
            if i in columns:
                if columns[i]: heapq.heappush(heap,(len(columns[i]),i))
                else: del columns[i]
        if len(heap)>10*max(1,len(columns)):
            heap = [(len(v),i) for i,v in columns.items()]
            heapq.heapify(heap)
    if time.monotonic()>=deadline: return unknown(len(pivots),'sparse')
    active = sorted(columns)
    positions = {i:j for j,i in enumerate(active)}
    compact = [{positions[i]:c for i,c in row.items()} for row in rows.values()]
    report = ternary_echelon(compact,seconds=max(1e-9,deadline-time.monotonic()))
    rank = len(pivots)+len(report['basis'])
    if not report['complete']: return unknown(rank,'bitsets')
    # Reverse triangular recovery, with free *original* coordinates as parameters.
    for p,(one,two) in sorted(report['basis'].items(),reverse=True):
        row = {}
        while one|two:
            bit = (one|two)&-(one|two)
            j = bit.bit_length()-1
            row[active[j]] = 1 if one&bit else 2
            one &= ~bit
            two &= ~bit
        pivots.append((active[p],row))
    pivot_ids = {p for p,_ in pivots}
    free = [i for i in range(size) if i not in pivot_ids]
    expressions = {i:(1<<j,0) for j,i in enumerate(free)}
    for p,row in reversed(pivots):
        if time.monotonic()>=deadline: return unknown(rank,'kernel')
        result = (0,0)
        for i,c in row.items():
            if i==p: continue
            one,two = expressions[i]
            result = ternary_add(result,(two,one) if c==1 else (one,two))
        expressions[p] = result
    # This verification uses untouched shell rows, not echelon equations.
    for row in original:
        if time.monotonic()>=deadline: return unknown(rank,'verification')
        result = (0,0)
        for i,c in row.items():
            if c%3:
                one,two = expressions[i]
                result = ternary_add(result,(one,two) if c%3==1 else (two,one))
        if result!=(0,0): raise AssertionError('recovered modular kernel fails an original row')
    result = dict(complete=True,rank=rank,nullity=len(free),kernel_verified=True,
                forced_zero_coordinates=[i for i in range(size) if expressions[i]==(0,0)],
                elapsed=time.monotonic()-start,literal_existence_decided=False)
    if retain_kernel: result['kernel'] = dict(free=free,expressions=expressions)
    return result


def ternary_nonzero_relations(kernel):
    """Necessary sign equalities from kernel expressions of weight one/two.

    Every parameter is an original coordinate and hence must be nonzero.
    Over F_3, ax+by is nonzero for nonzero x,y iff ax=by; then
    ax+by=-ax. Coefficients 2 are reported as the literal sign -1.
    These are necessary relations only, never a claimed sign assignment.
    """
    free,expressions = kernel['free'],kernel['expressions']
    relations = []
    for i,(one,two) in expressions.items():
        mask = one|two
        weight = mask.bit_count()
        if weight not in (1,2): continue
        bits = []
        while mask:
            bit = mask&-mask
            bits.append((free[bit.bit_length()-1],1 if one&bit else -1))
            mask ^= bit
        j,a = bits[0]
        if weight==1:
            if i!=j: relations.append((i,j,a))
        else:
            k,b = bits[1]
            relations.extend(((j,k,a*b),(i,j,-a)))
    return relations


def ternary_short_sign_rows(kernel):
    """Exact integer consequences of nonzero modular recoveries of width <=3.

    For two signed terms the only nonzero sums mod 3 are +/-2, so
    2*x_i+sum=0. For three terms +/-3 is forbidden by x_i!=0;
    the surviving sums are +/-1, hence x_i=sum over the integers.
    Width four has no such unambiguous lift and is deliberately omitted.
    """
    free,expressions = kernel['free'],kernel['expressions']
    rows = []
    for i,(one,two) in expressions.items():
        mask = one|two
        weight = mask.bit_count()
        if not 1<=weight<=3: continue
        terms = {}
        while mask:
            bit = mask&-mask
            terms[free[bit.bit_length()-1]] = 1 if one&bit else -1
            mask ^= bit
        row = defaultdict(int,{i:2 if weight==2 else 1})
        for j,c in terms.items(): row[j] += c if weight==2 else -c
        row = {j:c for j,c in row.items() if c}
        if row: rows.append(row)
    return rows




def ternary_copy_relations(kernel):
    """Include identical/opposite kernel expressions of arbitrary support."""
    relations = list(ternary_nonzero_relations(kernel))
    seen = {}
    for i,expression in kernel['expressions'].items():
        if expression==(0,0): continue
        opposite = expression[::-1]
        key = min(expression,opposite)
        sign = 1 if expression==key else -1
        if key in seen:
            j,s = seen[key]
            relations.append((i,j,sign*s))
        else:
            seen[key] = i,sign
    return sorted(set(relations))


def sign_relation_quotient(size,rows,relations):
    """Substitute supplied necessary signed equalities, with a reversible lift."""
    parent,sign = list(range(size)),[1]*size
    def find(i):
        root,factor = i,1
        while parent[root]!=root:
            factor *= sign[root]
            root = parent[root]
        answer = root,factor
        while parent[i]!=i:
            next_i,old = parent[i],sign[i]
            parent[i],sign[i] = root,factor
            factor *= old
            i = next_i
        return answer
    for i,j,s in relations:
        if (type(i) is not int or type(j) is not int or not 0<=i<size or not 0<=j<size
                or type(s) is not int or s not in (-1,1)):
            raise ValueError('invalid signed equality')
        a,x = find(i)
        b,y = find(j)
        if a==b:
            if x!=s*y: return dict(conflict=True)
        else:
            parent[a],sign[a] = b,s*x*y
    roots = {r:i for i,r in enumerate(sorted({find(i)[0] for i in range(size)}))}
    aliases = [(roots[find(i)[0]],find(i)[1]) for i in range(size)]
    compact = []
    for row in rows:
        out = defaultdict(int)
        for i,c in row.items():
            j,s = aliases[i]
            out[j] += s*c
        out = {j:c for j,c in out.items() if c}
        if out: compact.append(out)
    return dict(conflict=False,size=len(roots),rows=compact,aliases=aliases)


def rational_recovery(size,original,seconds=30):
    """Exact homogeneous kernel and denominator-cleared recovery equations."""
    if (type(size) is not int or size<1 or type(seconds) not in (int,float)
            or not math.isfinite(seconds) or seconds<=0):
        raise ValueError('require positive size and finite positive time')
    start = time.monotonic()
    original = list(original)
    rows,columns = {},defaultdict(set)
    for r,row in enumerate(original):
        if any(type(i) is not int or not 0<=i<size or type(c) is not int for i,c in row.items()):
            raise ValueError('invalid integer shell row')
        row = {i:Fraction(c) for i,c in row.items() if c}
        if row:
            rows[r] = row
            for i in row: columns[i].add(r)
    heap = [(len(v),i) for i,v in columns.items()]
    heapq.heapify(heap)
    pivots = []
    def limited():
        return dict(complete=False,rank_lower_bound=len(pivots),elapsed=time.monotonic()-start)
    while heap:
        if time.monotonic()-start>=seconds: return limited()
        degree,p = heapq.heappop(heap)
        if p not in columns or degree!=len(columns[p]): continue
        r = min(columns[p],key=lambda r:(len(rows[r]),r))
        row = rows.pop(r)
        factor = row[p]
        row = {i:c/factor for i,c in row.items()}
        pivots.append((p,row))
        for i in row: columns[i].remove(r)
        for other in list(columns[p]):
            if time.monotonic()-start>=seconds: return limited()
            target = rows[other]
            factor = target[p]
            for i,c in row.items():
                old = target.get(i,0)
                value = old-factor*c
                if value:
                    target[i] = value
                    if not old: columns[i].add(other)
                elif old:
                    del target[i]
                    columns[i].remove(other)
            if not target: del rows[other]
        del columns[p]
        for i in row:
            if i in columns:
                if columns[i]: heapq.heappush(heap,(len(columns[i]),i))
                else: del columns[i]
        if len(heap)>10*max(1,len(columns)):
            heap = [(len(v),i) for i,v in columns.items()]
            heapq.heapify(heap)
    free = sorted(set(range(size))-{p for p,_ in pivots})
    expressions = {i:{i:Fraction(1)} for i in free}
    for p,row in reversed(pivots):
        if time.monotonic()-start>=seconds: return limited()
        out = defaultdict(Fraction)
        for i,c in row.items():
            if i!=p:
                for j,d in expressions[i].items(): out[j] -= c*d
        expressions[p] = {j:c for j,c in out.items() if c}
    for row in original:
        if time.monotonic()-start>=seconds: return limited()
        out = defaultdict(Fraction)
        for i,c in row.items():
            for j,d in expressions[i].items(): out[j] += c*d
        if any(out.values()): raise AssertionError('rational kernel fails an original row')
    normalized = []
    for i,e in expressions.items():
        if i in free: continue
        denominator = math.lcm(*(c.denominator for c in e.values()))
        row = {i:denominator,**{j:int(-c*denominator) for j,c in e.items()}}
        divisor = math.gcd(*row.values())
        normalized.append({j:c//divisor for j,c in row.items()})
    return dict(complete=True,rank=len(pivots),free=free,expressions=expressions,
                normalized_rows=normalized,kernel_verified=True,elapsed=time.monotonic()-start)


def joint_sign_closure(size,original,seconds=30,steps=20,short_recovery=False):
    """Alternate exact rational recovery, binary copies and ternary copies.

    Every quotient records a reversible signed alias. Stopping with no new
    copies says nothing about whether its remaining literal cube is empty.
    """
    if (type(seconds) not in (int,float) or not math.isfinite(seconds) or seconds<=0
            or type(steps) is not int or steps<1):
        raise ValueError('require positive finite time and positive step count')
    start = time.monotonic()
    rows,aliases,history = list(original),[(i,1) for i in range(size)],[]
    def result(complete,conflict=False,**extra):
        return dict(complete=complete,conflict=conflict,size=size,rows=rows,
                    aliases=aliases,history=history,elapsed=time.monotonic()-start,**extra)
    def remaining(): return seconds-(time.monotonic()-start)
    for step in range(steps):
        before = size
        if remaining()<=0: return result(False,stage='rational')
        rational = rational_recovery(size,rows,remaining())
        if not rational['complete']: return result(False,stage='rational')
        rows += rational['normalized_rows']
        # Remove repeated/scaled homogeneous equations before the next round.
        unique = {}
        for row in rows:
            entries = sorted((i,c) for i,c in row.items() if c)
            if not entries: continue
            divisor = math.gcd(*(c for _,c in entries))
            if entries[0][1]<0: divisor = -divisor
            key = tuple((i,c//divisor) for i,c in entries)
            unique[key] = dict(key)
        rows = list(unique.values())
        if remaining()<=0: return result(False,stage='binary')
        binary = parity_sign_quotient(size,rows,remaining())
        if not binary['complete']: return result(False,stage='binary')
        if binary['conflict']: return result(True,True,stage='binary')
        lift = binary['aliases']
        aliases = [(lift[i][0],s*lift[i][1]) for i,s in aliases]
        size,rows = binary['size'],binary['rows']
        if remaining()<=0: return result(False,stage='ternary')
        modular = ternary_analysis(size,rows,remaining(),retain_kernel=True)
        if not modular['complete']: return result(False,stage='ternary')
        if modular['forced_zero_coordinates']: return result(True,True,stage='ternary_nonzero')
        added = 0
        if short_recovery:
            def canonical(row):
                entries = sorted((i,c) for i,c in row.items() if c)
                if not entries: return ()
                divisor = math.gcd(*(c for _,c in entries))
                if entries[0][1]<0: divisor = -divisor
                return tuple((i,c//divisor) for i,c in entries)
            seen = {canonical(row) for row in rows}
            for row in ternary_short_sign_rows(modular['kernel']):
                key = canonical(row)
                if key and key not in seen:
                    rows.append(dict(key))
                    seen.add(key)
                    added += 1
        relations = ternary_copy_relations(modular['kernel'])
        quotient = sign_relation_quotient(size,rows,relations)
        if quotient['conflict']: return result(True,True,stage='ternary_nonzero')
        history.append(dict(step=step+1,variables_before=before,
                            rational_nullity=before-rational['rank'],
                            binary_variables=binary['size'],binary_free=binary['free'],
                            ternary_nullity=modular['nullity'],ternary_relations=len(relations),
                            variables_after=quotient['size'],short_recovery_rows=added))
        lift = quotient['aliases']
        aliases = [(lift[i][0],s*lift[i][1]) for i,s in aliases]
        size,rows = quotient['size'],quotient['rows']
        if size==before and not added: return result(True,stop='no_more_signed_merges')
    return result(False,stage='step_limit')




def moving_search(period,seconds=30,nodes=10000,free_order='connected',closure_steps=20,rational=False,affine_shells=False,square_lift=False,joint_fields=False,reduced_xor=False,hole=19,edge_patch=0,short_recovery=False):
    """Search one explicit all-scale moving-hole word ansatz, never all pairs."""
    if (type(seconds) not in (int,float) or not math.isfinite(seconds) or seconds<=0
            or type(nodes) is not int or nodes<0 or type(closure_steps) is not int or closure_steps<0):
        raise ValueError('require positive finite time and nonnegative node/closure budgets')
    start = time.monotonic()
    keys,formal = moving_periodic_system(period,hole,edge_patch)
    original = list(formal.values())
    rows,size = original,len(keys)
    aliases,history = [(i,1) for i in range(size)],[]
    result = dict(mode='moving',period=period,hole=hole,edge_patch=edge_patch,
                  minimum_scale=2*edge_patch+period+1,all_pairs_decided=False,
                  scope=f'holes {hole}t and 99t; independent edge patches of width {edge_patch}; periodic interiors; t=1 mod period')
    def done(status,**details):
        return dict(**result,status=status,closure=history,variables=size,rows=len(rows),
                    elapsed=time.monotonic()-start,**details)
    for _ in range(closure_steps):
        remaining = seconds-(time.monotonic()-start)
        if remaining<=0: return done('unknown',stage='closure')
        report = ternary_analysis(size,rows,remaining,retain_kernel=True)
        if not report['complete']: return done('unknown',stage='modular_elimination')
        kernel = report.pop('kernel')
        relations = ternary_nonzero_relations(kernel)
        history.append(dict(variables=size,rank=report['rank'],nullity=report['nullity'],
                            relations=len(relations),forced_zero=len(report['forced_zero_coordinates'])))
        if report['forced_zero_coordinates']: return done('ansatz_refused_by_modular_nonzero')
        quotient = sign_relation_quotient(size,rows,relations)
        if quotient['conflict']: return done('ansatz_refused_by_modular_nonzero')
        if quotient['size']==size: break
        lift = quotient['aliases']
        aliases = [(lift[i][0],s*lift[i][1]) for i,s in aliases]
        size,rows = quotient['size'],quotient['rows']
    if joint_fields:
        remaining = seconds-(time.monotonic()-start)
        if remaining<=0: return done('unknown',stage='joint_fields')
        joint = joint_sign_closure(size,rows,remaining,short_recovery=short_recovery)
        result['joint_fields'] = {k:v for k,v in joint.items() if k not in ('rows','aliases')}
        if joint['conflict']: return done('ansatz_refused_by_joint_fields')
        if not joint['complete']: return done('unknown',stage='joint_fields')
        lift = joint['aliases']
        aliases = [(lift[i][0],s*lift[i][1]) for i,s in aliases]
        size,rows = joint['size'],joint['rows']
    if rational and not joint_fields:
        remaining = seconds-(time.monotonic()-start)
        if remaining<=0: return done('unknown',stage='rational_recovery')
        report = rational_recovery(size,rows,remaining)
        if not report['complete']: return done('unknown',stage='rational_recovery')
        result.update(rational_rank=report['rank'],rational_nullity=len(report['free']))
        rows = rows+report['normalized_rows']
    if affine_shells:
        remaining = seconds-(time.monotonic()-start)
        if remaining<=0: return done('unknown',stage='affine_shells')
        closure = affine_shell_closure(size,rows,remaining)
        basis = closure.pop('basis')
        result['affine_shells'] = closure
        if closure['conflict']: return done('ansatz_refused_by_affine_shells')
        if not closure['complete']: return done('unknown',stage='affine_shells')
    else:
        refusal,basis = binary_elimination(rows)
        if refusal is not None: return done('ansatz_refused_by_parity')
    if square_lift:
        remaining = seconds-(time.monotonic()-start)
        if remaining<=0: return done('unknown',stage='square_lift')
        report = quadratic_sign_analysis(size,rows,remaining)
        parity = report.pop('parity_rows',[])
        result['square_lift'] = report
        if not report['complete']: return done('unknown',stage='square_lift')
        if report['conflict']: return done('ansatz_refused_by_square_lift')
        before = len(basis)
        for mask,rhs in parity:
            while mask:
                p = mask.bit_length()-1
                if p not in basis:
                    basis[p] = mask,rhs
                    break
                m,b = basis[p]
                mask,rhs = mask^m,rhs^b
            if not mask and rhs: return done('ansatz_refused_by_square_lift')
        result['square_lift']['added_binary_rows'] = len(basis)-before
    if reduced_xor:
        before = sum(m.bit_count() for m,_ in basis.values())
        basis = reduced_binary_basis(basis)
        result['binary_nonzeros'] = [before,sum(m.bit_count() for m,_ in basis.values())]
    remaining = seconds-(time.monotonic()-start)
    if remaining<=0: return done('unknown',stage='search')
    engine = make_engine(size,rows,basis,remaining,nodes,free_order)
    i,s = aliases[0]
    status,values = engine.run({i:s})
    if values is None: return done(status,nodes=engine.nodes)
    restored = [s*values[i] for i,s in aliases]
    if any(sum(c*restored[i] for i,c in row.items()) for row in original):
        raise AssertionError('lifted moving-hole signing fails the original formal equations')
    return done(status,nodes=engine.nodes,assignment=[[list(k),v] for k,v in zip(keys,restored)])


def verify_refusal(rows, certificate):
    if not isinstance(certificate,list) or not certificate or len(set(certificate))!=len(certificate):
        return False
    mask = rhs = 0
    for i in certificate:
        if type(i) is not int or not 0<=i<len(rows): return False
        row = rows[i]
        if sum(row.values())%2: return len(certificate)==1
        mask ^= sum(1<<j for j,c in row.items() if c%2)
        rhs ^= sum(row.values())//2%2
    return mask==0 and rhs==1


class LongRowSearch(LiteralSearch):
    """Keep exact short-row tables and safe interval propagation on long rows."""
    def propagate(self,queue):
        while queue:
            mark = len(self.trail)
            if not super().propagate(queue): return False
            affected = {rid for kind,i,_ in self.trail[mark:] if kind==0
                        for rid in self.long_links[i]}
            queue = []
            for rid in affected:
                row = self.long_rows[rid]
                total = sum(c*self.values[i] for i,c in row.items() if self.values[i])
                unknown = [(i,c) for i,c in row.items() if not self.values[i]]
                radius = sum(abs(c) for _,c in unknown)
                if abs(total)>radius: return False
                for i,c in unknown:
                    if abs(total+c)>radius-abs(c): queue.append((i,-1))
                    if abs(total-c)>radius-abs(c): queue.append((i,1))
        return True


def literal_row_table(coefficients):
    """Exact short-row truth table by meet-in-the-middle signed sums."""
    coefficients = tuple(coefficients)
    if len(coefficients)>16 or any(type(c) is not int or not c for c in coefficients):
        raise ValueError('require at most sixteen nonzero integer coefficients')
    split = len(coefficients)//2
    def sums(word):
        values = [(0,0)]
        for j,c in enumerate(word):
            values = [(s-c,b) for s,b in values]+[(s+c,b|(1<<j)) for s,b in values]
        return values
    right = defaultdict(list)
    for total,bits in sums(coefficients[split:]): right[total].append(bits)
    patterns = sorted(a|(b<<split) for total,a in sums(coefficients[:split])
                      for b in right.get(-total,()))
    packed = [bytearray((len(patterns)+7)//8) for _ in coefficients]
    for index,bits in enumerate(patterns):
        for j in range(len(coefficients)):
            if bits>>j&1: packed[j][index//8] |= 1<<(index%8)
    return [int.from_bytes(p,'little') for p in packed],(1<<len(patterns))-1


def make_engine(size,rows,basis,seconds,nodes,free_order='natural'):
    # Truth tables depend on coefficient words, not variable names. The strip
    # repeats a few such words thousands of times; construct each table once.
    engine = LongRowSearch(size,[],node_budget=nodes,seconds=seconds)
    engine.long_rows,engine.long_links = [],[[] for _ in range(size)]
    cache = {}
    for row in rows:
        ids,coefficients = list(row),tuple(row.values())
        if any(type(i) is not int or not 0<=i<size for i in ids):
            raise ValueError('invalid variable index')
        if any(type(c) is not int or not c for c in coefficients):
            raise ValueError('require nonzero integer coefficients')
        if len(ids)>16:
            rid = len(engine.long_rows)
            engine.long_rows.append(dict(row))
            for i in ids: engine.long_links[i].append(rid)
            continue
        if coefficients not in cache:
            cache[coefficients] = literal_row_table(coefficients)
        masks,full = cache[coefficients]
        rid = len(engine.tables)
        engine.tables.append((ids,masks,full))
        engine.allowed.append(full)
        for j,i in enumerate(ids): engine.links[i].append((rid,j))
    # Preserve the echelon constraints during literal branching. Assign free
    # binary coordinates first; one-unknown rows then recover pivot signs.
    engine.xor_rows = list(basis.values())
    engine.xor_links = [[] for _ in range(size)]
    used = set()
    for rid,(mask,_) in enumerate(engine.xor_rows):
        while mask:
            bit = mask & -mask
            i = bit.bit_length()-1
            engine.xor_links[i].append(rid)
            used.add(i)
            mask ^= bit
    if free_order not in ('natural','connected'): raise ValueError('invalid free-coordinate order')
    engine.priority = sorted(used-set(basis),key=(
        (lambda i:(-len(engine.links[i])-len(engine.xor_links[i])-len(engine.long_links[i]),i))
        if free_order=='connected' else (lambda i:i)))
    return engine


def make_relational_engine(size,rows,relations,seconds=30,nodes=1000000):
    """Add retained nonlinear relations to the exact untouched-row search.

    Auxiliary positive bits encode parity of *negative* original free bits.
    The offset below is essential for even-weight generators. Explicitly
    fixing original sign zero uses the true global reversal symmetry; the
    auxiliaries need not all reverse together.
    """
    refusal,basis = binary_elimination(rows)
    if refusal is not None or relations['conflict'] or not relations['complete']:
        raise ValueError('require completed compatible relations and parity fibre')
    engine = make_engine(size,rows,basis,seconds,nodes,'connected')
    masks = sorted({m for t in relations['tables'].values() for m in t['generators']})
    index = {m:size+j for j,m in enumerate(masks)}
    engine.values.extend([0]*len(masks))
    engine.links.extend([] for _ in masks)
    engine.long_links.extend([] for _ in masks)
    engine.xor_links.extend([] for _ in masks)
    for m,i in index.items():
        rid = len(engine.xor_rows)
        equation = m|(1<<i)
        engine.xor_rows.append((equation,m.bit_count()%2))
        while equation:
            bit = equation&-equation
            engine.xor_links[bit.bit_length()-1].append(rid)
            equation ^= bit
    for table in relations['tables'].values():
        ids = [index[m] for m in table['generators']]
        patterns = table['valid']
        packed = [bytearray((len(patterns)+7)//8) for _ in ids]
        for k,v in enumerate(patterns):
            for j in range(len(ids)):
                if v>>j&1: packed[j][k//8] |= 1<<(k%8)
        columns = [int.from_bytes(p,'little') for p in packed]
        full = (1<<len(patterns))-1
        rid = len(engine.tables)
        engine.tables.append((ids,columns,full))
        engine.allowed.append(full)
        for j,i in enumerate(ids): engine.links[i].append((rid,j))
    return engine


def search(half=3990, period=1, seconds=30, nodes=10000, patch_width=40, free_order='natural'):
    keys,rows = compile_system(half,period,patch_width)
    certificate,basis = binary_elimination(rows)
    if certificate is not None:
        assert verify_refusal(rows,certificate)
        return dict(t=2*half+1,period=period,patch_width=patch_width,status='ansatz_refused_by_parity',
                    variables=len(keys),rows=len(rows),certificate=certificate,
                    scope='fixed two holes; periodic folded interior; free endpoint patches',
                    all_pairs_decided=False)
    engine = make_engine(len(keys),rows,basis,seconds,nodes,free_order)
    status,values = engine.run({keys.index(('left',0,0,0)):1})
    result = dict(t=2*half+1,period=period,patch_width=patch_width,variables=len(keys),rows=len(rows),
                  status=status,nodes=engine.nodes,free_order=free_order,all_pairs_decided=False,
                  scope='fixed two holes; periodic folded interior; free endpoint patches')
    if values is not None:
        assert all(sum(c*values[i] for i,c in row.items())==0 for row in rows)
        result['assignment'] = [[list(k),v] for k,v in zip(keys,values)]
    return result


def verify_saved(saved):
    if saved.get('kind')=='moving-periodic-phase-v1':
        if not verify_periodic_phase_refusal(saved):
            raise ValueError('invalid endpoint-phase periodic refusal')
        return dict(verified=True,hole=saved['hole'],period=saved['period'],
                    claim='specified periodic interior with physical endpoint phases only',
                    literal_existence_decided=False,all_pairs_decided=False)
    if saved.get('kind')=='moving-period-two-phase-v1':
        if not verify_period_two_phase_refusal(saved):
            raise ValueError('invalid endpoint-phase period-two refusal')
        return dict(verified=True,hole=saved['hole'],
                    claim='period-two interiors with physical endpoint phases only',
                    literal_existence_decided=False,all_pairs_decided=False)
    if saved.get('kind')=='moving-parity-completion-v1':
        if not verify_parity_completion_certificate(saved):
            raise ValueError('invalid mod-four shell completion')
        return dict(verified=True,hole=saved['hole'],minimum_half=18,
                    half_parity=saved['half_parity'],
                    claim='all shell equations hold modulo four only; no integer signing claimed',
                    literal_existence_decided=False,all_pairs_decided=False)
    if saved.get('kind')=='moving-parity-trace-v1':
        if not verify_parity_trace_certificate(saved):
            raise ValueError('invalid two-level parity trace certificate')
        return dict(verified=True,hole=saved['hole'],laws=5,
                    phases_at_two=[1,1,0,0,0],drift=[1,1,1,1,0],
                    claim='complete constant-row two-level parity laws and endpoint phases only',
                    literal_existence_decided=False,all_pairs_decided=False)
    if saved.get('kind')=='moving-interior-cocycle-v1':
        if not verify_interior_parity_cocycle(saved):
            raise ValueError('invalid unrestricted interior parity cocycle')
        return dict(verified=True,claim='unrestricted interior alternating parity only',
                    hole=saved['hole'],odd_periods_excluded=True,initial_phase=1,
                    literal_existence_decided=False,all_pairs_decided=False)
    if saved.get('kind')=='moving-interior-rank-v1':
        if not verify_interior_rank_certificate(saved):
            raise ValueError('invalid unrestricted interior rank certificate')
        return dict(verified=True,rank=saved['rows'],
                    rational_function_nullity=saved['variables']-saved['rows'],
                    claim='unrestricted interior rational rank only',
                    literal_existence_decided=False,all_pairs_decided=False)
    if saved.get('mode')=='folded_cubic':
        if saved.get('status')!='refused' or saved.get('all_pairs_decided') is not False or 'joint_history' in saved:
            raise ValueError('no scoped cubic refusal certificate')
        keys,rows=compile_moving_folded(saved['half'],saved['period'],saved['patch'],saved['hole'])
        verify_cubic_shell_proof(len(keys),rows,saved.get('cubic_proof'))
        return dict(verified=True,claim='only the named periodic-interior ansatz is refused by Boolean identities',
                    all_pairs_decided=False)
    if saved.get('mode')=='moving_folded':
        keys,rows=compile_moving_folded(saved['half'],saved['period'],saved['patch'],saved['hole'])
        if (saved.get('minimum_half')!=2*saved['patch']+4+saved['period']
                or saved.get('half_residue')!=saved['half']%saved['period']
                or saved.get('all_pairs_decided') is not False):
            raise ValueError('incorrect moving-folded family scope')
        if saved.get('status')=='ansatz_refused_by_interior_cocycle':
            certificate = saved.get('certificate',{})
            if (saved['period']%2!=1 or not isinstance(certificate,dict) or
                    certificate.get('hole')!=saved['hole'] or
                    not verify_interior_parity_cocycle(certificate)):
                raise ValueError('invalid odd-period interior refusal')
            return dict(verified=True,claim='only the named odd-period interior ansatz is refused',
                        all_pairs_decided=False)
        if saved.get('status')=='ansatz_refused_by_parity':
            if not verify_refusal(rows,saved.get('certificate',[])):
                raise ValueError('invalid moving-folded parity refusal')
            return dict(verified=True,claim='only the named periodic-interior ansatz is refused',
                        all_pairs_decided=False)
        assignment=saved.get('assignment',[])
        if (saved.get('status')!='sat' or len(assignment)!=len(keys)
                or [tuple(k) for k,v in assignment]!=keys
                or any(type(v) is not int or v not in (-1,1) for k,v in assignment)):
            raise ValueError('no complete literal moving-folded witness')
        values=[v for k,v in assignment]
        if any(sum(c*values[i] for i,c in row.items()) for row in rows):
            raise ValueError('moving-folded witness fails an untouched shell row')
        return dict(verified=True,claim='literal moving-hole signing on the stated infinite half-length phase',
                    all_pairs_decided=False)
    if saved.get('mode')=='split_dyadic':
        keys,formal=split_edge_system(saved['hole'],saved['patch'],saved['pieces'],
                                     saved['word_period'],saved['hole_offset'],
                                     hole_piece=saved['hole_piece'])
        original=list(formal.values())
        report=saved['analysis']
        if not report.get('complete'):raise ValueError('incomplete dyadic analysis')
        if report.get('status')=='refused_by_parity':
            if not verify_refusal(original,report.get('certificate',[])):
                raise ValueError('invalid initial parity refusal')
        elif report.get('status')=='refused_by_quadratics':
            verify_dyadic_consequence(len(keys),original,
                                     dict(mask=0,rhs=1,certificate=report.get('certificate')))
        elif report.get('status')=='compatible_product_relaxation':
            rebuilt=dyadic_quadratic_analysis(len(keys),original,seconds=300)
            for field in ('complete','status','free','quadratic_rank','product_coordinates'):
                if report.get(field)!=rebuilt.get(field):
                    raise ValueError('dyadic analysis did not reconstruct')
            if [(v.get('mask'),v.get('rhs')) for v in report.get('linear_relations',[])]!=[
                    (v['mask'],v['rhs']) for v in rebuilt.get('linear_relations',[])]:
                raise ValueError('dyadic linear consequences differ')
            for relation in report['linear_relations']:
                verify_dyadic_consequence(len(keys),original,relation)
        else:raise ValueError('unknown dyadic result')
        return dict(verified=True,claim='necessary mod-eight constraints on the stated split-edge ansatz only',
                    all_pairs_decided=False,literal_existence_decided=False)
    if saved.get('mode')=='growing_lift_repair_bound':
        expected = growing_lift_repair_bound(saved.get('t'))
        if json.dumps(saved,sort_keys=True)!=json.dumps(expected,sort_keys=True):
            raise ValueError('saved repair bound does not match the symbolic shell calculation')
        return dict(verified=True,all_pairs_decided=False,claim=expected['scope'])
    if saved.get('mode')=='flat_any_holes':
        expected = flat_piece_any_holes_bound(saved.get('piece_length'),saved.get('pieces'),saved.get('patch'))
        if json.dumps(saved,sort_keys=True)!=json.dumps(expected,sort_keys=True):
            raise ValueError('saved any-hole flat-piece bound differs from the proof')
        return dict(verified=True,all_pairs_decided=False,status=expected['status'],claim=expected['scope'])
    if saved.get('mode')=='split_bulk':
        _,rows = split_bulk_system()
        if not verify_refusal(list(rows.values()),saved.get('certificate',[])):
            raise ValueError('invalid patched-flat-interior bulk refusal')
        return dict(verified=True,all_pairs_decided=False,
                    claim='only long flat interiors with arbitrary finite endpoint patches are refused')
    if saved.get('mode')=='split_endpoints':
        _,rows=split_endpoint_system(saved.get('hole',19),saved.get('patch',0),
                                     saved.get('word_period',1),saved.get('hole_offset',0))
        if not verify_refusal(list(rows.values()),saved.get('certificate',[])):
            raise ValueError('invalid uniform flat-piece endpoint refusal')
        expected=split_endpoint_refusal(saved.get('hole',19),saved.get('patch',0),
                                        saved.get('word_period',1),saved.get('hole_offset',0))
        for field in ('minimum_piece_length','piece_length_divisor','exponent_constant_span'):
            if field in saved and saved[field]!=expected[field]:
                raise ValueError('incorrect endpoint specialization threshold')
        return dict(verified=True,claim='only the stated equal-piece word and patch ansatz is refused',
                    minimum_piece_length=expected['minimum_piece_length'],
                    piece_length_divisor=expected['piece_length_divisor'],all_pairs_decided=False)
    if saved.get('mode')=='split_edge':
        word_period=saved.get('word_period',1)
        constants=[]
        keys,formal=split_edge_system(saved['hole'],saved['patch'],saved['pieces'],word_period,saved.get('hole_offset',0),
                                      constants,saved.get('hole_piece',0))
        minimum=max(2*saved['patch']+word_period,max(constants)-min(constants)+1)
        minimum=((minimum+word_period-1)//word_period)*word_period
        if saved.get('status')=='ansatz_refused_by_parity':
            if not verify_refusal(list(formal.values()),saved['certificate']):
                raise ValueError('invalid split-edge parity refusal')
            return dict(verified=True,claim='only the split-edge ansatz is refused',
                        minimum_piece_length=minimum,piece_length_divisor=word_period,all_pairs_decided=False)
        if saved.get('status')=='ansatz_refused_by_binary_fibre':
            audit=enumerate_binary_fibre(len(keys),list(formal.values()))
            if (audit['status']!='unsat' or not audit['complete']
                    or audit.get('free')!=saved.get('parity_free')
                    or audit['enumerated']!=saved.get('enumerated')
                    or saved.get('minimum_piece_length')!=minimum):
                raise ValueError('binary-fibre exhaustion did not verify')
            return dict(verified=True,claim='only the stated split-edge ansatz is refused',
                        minimum_piece_length=minimum,piece_length_divisor=word_period,all_pairs_decided=False)
        assignment=saved.get('assignment',[])
        if len(assignment)!=len(keys) or [tuple(k) for k,v in assignment]!=keys:
            raise ValueError('no complete split-edge assignment')
        values=[v for k,v in assignment]
        if any(type(v) is not int or v not in (-1,1) for v in values):
            raise ValueError('require literal signs')
        if any(sum(c*values[i] for i,c in row.items()) for row in formal.values()):
            raise ValueError('split-edge shell equation fails')
        return dict(verified=True,claim='formal split-edge shell equations vanish',
                    minimum_piece_length=2*saved['patch']+word_period,
                    piece_length_divisor=word_period,all_pairs_decided=False)
    if saved.get('mode')=='residue_lift':
        return verify_residue_lift(saved)
    if saved.get('mode') in ('residue_zero','residue_parity'):
        parity = saved['mode']=='residue_parity'
        expected = 'support_refused_by_residue_parity' if parity else 'support_refused_by_odd_group'
        aggregate = parity and saved.get('status')=='compatible_unbounded_aggregates'
        bounded = parity and saved.get('status')=='compatible_bounded_aggregates'
        if saved.get('status')!=expected and not aggregate and not bounded:
            raise ValueError('no saved residue refusal')
        scale = saved['t']
        if type(scale) is not int or scale < 1:
            raise ValueError('require a positive integer scale')
        holes = [tuple(hole) for hole in saved['holes']]
        if len(holes) != 2:
            raise ValueError('require exactly two holes')
        groups = residue_shell_groups([99*scale,79*scale,23*scale],holes,saved['period'])
        if bounded:
            verify_bounded_residue_witness(groups,saved['aggregate_sums'])
            return dict(verified=True,claim='bounded residue aggregates exist; full shell equations remain unchecked',
                        all_pairs_decided=False)
        if aggregate:
            if 'witness' not in saved:
                raise ValueError('no saved aggregate compatibility witness')
            verify_residue_aggregate_witness(groups,saved['witness'])
            return dict(verified=True,claim='unbounded residue aggregates exist; no literal signing claimed',
                        all_pairs_decided=False)
        if parity:
            verify_residue_parity_certificate(groups,saved['certificate'])
        else:
            verify_residue_zero_certificate(groups,saved['certificate'])
        return dict(verified=True,claim='this exact two-hole support is impossible for every word',
                    all_pairs_decided=False)
    if saved.get('mode')=='coarse':
        if saved.get('status')!='sat': raise ValueError('no saved coarse sign witness')
        return verify_coarse_assignment(saved.get('hole',19),saved['assignment'])
    if saved.get('mode') in ('moving_coarse','boundary'):
        raise ValueError('replay diagnostic is not a standalone saved certificate')
    if saved.get('mode')=='moving':
        if saved['status']!='sat': raise ValueError('no saved moving sign witness')
        keys,formal = moving_periodic_system(saved['period'],saved.get('hole',19),saved.get('edge_patch',0))
        supplied = saved['assignment']
        assignment = {tuple(k):v for k,v in supplied}
        if len(assignment)!=len(supplied) or set(assignment)!=set(keys):
            raise ValueError('require each moving coordinate exactly once')
        values = [assignment[k] for k in keys]
        if any(type(v) is not int or v not in (-1,1) for v in values):
            raise ValueError('require literal signs')
        if values[0]!=1 or any(sum(c*values[i] for i,c in row.items()) for row in formal.values()):
            raise ValueError('moving formal shell equation fails')
        return dict(verified=True,claim='formal moving-hole construction for t=1 mod period at or above minimum_scale',
                    minimum_scale=2*saved.get('edge_patch',0)+saved['period']+1,
                    all_pairs_decided=False)
    t,period,width = saved['t'],saved['period'],saved['patch_width']
    if type(t) is not int or t%2!=1: raise ValueError('require an odd scale')
    keys,rows = compile_system(t//2,period,width)
    if saved['status']=='ansatz_refused_by_parity':
        if not verify_refusal(rows,saved['certificate']):
            raise ValueError('invalid parity refusal')
        return dict(verified=True,claim='only this periodic ansatz is impossible',all_pairs_decided=False)
    if saved['status']=='sat':
        supplied = saved['assignment']
        assignment = {tuple(k):v for k,v in supplied}
        if len(assignment)!=len(supplied) or set(assignment)!=set(keys):
            raise ValueError('require each literal coordinate exactly once')
        values = [assignment[k] for k in keys]
        if any(type(v) is not int or v not in (-1,1) for v in values):
            raise ValueError('require literal signs')
        if assignment['left',0,0,0]!=1 or any(sum(c*values[i] for i,c in row.items()) for row in rows):
            raise ValueError('shell or centre equation fails')
        return dict(verified=True,claim='periodic construction satisfies all shells',all_pairs_decided=False)
    raise ValueError('an unknown result is not a certificate')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--residue-lift',nargs='+',type=int,metavar='ORDER',
                   help='construct a resistant subfamily passing all listed distance-residue tests')
    p.add_argument('--lift-repair-bound',type=int,metavar='SCALE',
                   help='prove a sign-change lower bound for the growing-block modular lift')
    p.add_argument('--lift-index',type=int,default=1,help='positive index in the residue-lift subfamily')
    p.add_argument('--hole',type=int,default=19,help='old first-arm vertex omitted in moving mode, 1..98')
    p.add_argument('--hole-offset',type=int,default=0,help='split-edge hole offset within an endpoint patch')
    p.add_argument('--hole-piece',type=int,default=0,help='split-edge hole includes this many piece lengths')
    p.add_argument('--half',type=int,default=3990)
    p.add_argument('--period',type=int,default=1)
    p.add_argument('--patch-width',type=int,default=40)
    p.add_argument('--seconds',type=float,default=30)
    p.add_argument('--nodes',type=int,default=10000)
    p.add_argument('--free-order',choices=('natural','connected'),default='natural')
    p.add_argument('--write')
    p.add_argument('--verify')
    p.add_argument('--ternary',action='store_true',help='bounded modular rank diagnostic; not a sign search')
    p.add_argument('--sparse-pivots',type=int,default=40000)
    p.add_argument('--moving',action='store_true',help='search moving holes 19t and 99t')
    p.add_argument('--moving-folded',action='store_true',help='search the radius-one moving-hole folded strip')
    p.add_argument('--relation-search',action='store_true',help='with --folded-relations, search retained exact constraints against untouched rows')
    p.add_argument('--folded-relations',action='store_true',help='retain exact local sign relations and semijoin shared binary forms')
    p.add_argument('--folded-hulls',action='store_true',help='diagnose joint row correlations in one periodic moving-hole strip')
    p.add_argument('--hull-rank',type=int,default=16,help='maximum local binary rank in folded hull diagnostics, 0..16')
    p.add_argument('--moving-strip-audit',type=int,metavar='SCALE',help='compare every moving-hole strip column with the physical shell matrix')
    p.add_argument('--moving-reduced',action='store_true',help='eliminate forced opposite tails in the moving strip audit, hole<=42')
    p.add_argument('--folded-patch',type=int,default=2,help='independent patch width in the moving folded strip')
    p.add_argument('--edge-patch',type=int,default=0,help='free endpoint vertices in moving or split-edge mode')
    p.add_argument('--split-edge',action='store_true',help='independent constant edge pieces; t=pieces*L+1')
    p.add_argument('--split-dyadic',action='store_true',help='derive exact quadratic mod-eight constraints for split-edge signs')
    p.add_argument('--edge-pieces',type=int,default=2,help='number of constant pieces per edge in split-edge mode')
    p.add_argument('--piece-period',type=int,default=1,help='independent repeating word length within each edge piece')
    p.add_argument('--flat-any-holes',type=int,metavar='PIECE_LENGTH',help='support-count obstruction to flat interiors with any two holes')
    p.add_argument('--split-bulk',action='store_true',help='uniform flat-interior refusal with arbitrary finite endpoint patches')
    p.add_argument('--split-endpoints',action='store_true',help='portable endpoint refusal for every piece count with the given words, patches and hole offset')
    p.add_argument('--reduced-xor',action='store_true',help='fully reduce moving-word binary equations before branching')
    p.add_argument('--joint-fields',action='store_true',help='alternate rational, binary and ternary sign quotients')
    p.add_argument('--square-lift',action='store_true',help='derive moving-word constraints from sign squares')
    p.add_argument('--affine-shells',action='store_true',help='derive binary equations from exact local sign patterns')
    p.add_argument('--rational',action='store_true',help='augment moving search with exact recovery equations')
    p.add_argument('--parity-quotient',action='store_true',help='merge parity-forced signs before ternary analysis')
    p.add_argument('--audit-coarse',action='store_true',help='verify Z=z formal specialization against old physical shells')
    p.add_argument('--coarse-catalog',action='store_true',help='enumerate all centre-positive signings of one old support')
    p.add_argument('--coarse',action='store_true',help='search one old support')
    p.add_argument('--condition-coarse',action='store_true',help='disjoin old-support catalog before moving-word search')
    p.add_argument('--short-recovery',action='store_true',help='add exact width<=3 modular recovery equations in joint closure')
    p.add_argument('--audit-boundary',action='store_true',help='verify universal endpoint model against formal moving system')
    p.add_argument('--boundary-refusal',action='store_true',help='replay universal endpoint refusal over all old-support branches')
    p.add_argument('--coarse-supports',action='store_true',help='classify all 98 old first-arm supports')
    p.add_argument('--full-partition-bound',type=int,help='report inherited full-partition upper bound at a scale')
    p.add_argument('--fourth-root-census',action='store_true',help='replay the unrestricted two-hole mod-eight method limitation')
    p.add_argument('--residue-zero',type=int,metavar='SCALE',help='seek a portable unrestricted support refusal at this scale')
    p.add_argument('--residue-parity',type=int,metavar='SCALE',help='decide the unbounded integer residue-aggregate relaxation')
    p.add_argument('--max-bits',type=int,default=1024,help='integer coefficient limit for residue-parity elimination')
    p.add_argument('--dyadic',action='store_true',help='use Hadamard-bounded powers-of-two residue elimination')
    p.add_argument('--folded-cubic',action='store_true',help='bounded Boolean degree-three lift of folded shell equations')
    p.add_argument('--cubic-pivots',type=int,default=20000,help='maximum stored Boolean lift pivots; reaching it is unknown')
    p.add_argument('--cubic-search',action='store_true',help='reserve half the post-closure budget for exact integer search')
    p.add_argument('--cubic-proof',action='store_true',help='retain explicit Boolean polynomial identities for independent refusal verification')
    p.add_argument('--bounded',action='store_true',help='seek exact residue sums within physical group bounds; failure is unknown')
    p.add_argument('--retain-residue-witness',action='store_true',help='save independently verifiable aggregate compatibility with --dyadic and --write')
    p.add_argument('--audit-resistant-residues',action='store_true',help='audit all resistant scale phases through --period')
    p.add_argument('--holes',nargs=2,metavar='ARM:DEPTH',help='exactly two physical holes, centre is 0:0')
    p.add_argument('--interior-rank',action='store_true',
                   help='certify unrestricted interior rank over the rational function field')
    p.add_argument('--interior-cocycle',action='store_true',
                   help='certify an alternating parity observable on unrestricted interior words')
    p.add_argument('--parity-traces',action='store_true',
                   help='classify all constant-row two-level parity laws and endpoint phases')
    p.add_argument('--parity-completion',action='store_true',
                   help='certify a full mod-four shell signing for the parity of --half')
    p.add_argument('--resume-phase',help='recheck and reuse partial phase identities from this JSON file')
    p.add_argument('--cubic-sweep',action='store_true',help='continue examining phase products after the nonlinear pivot store fills')
    p.add_argument('--retain-quadratics',action='store_true',help='retain checked phase quadratic consequences and reuse them in the next pass')
    p.add_argument('--periodic-phase-refusal',action='store_true',help='seek a checked phase refusal at the even --period')
    p.add_argument('--period-two-phase-refusal',action='store_true',
                   help='seek a Boolean refusal of period-two interiors with endpoint phases')
    args = p.parse_args()
    if args.periodic_phase_refusal:
        prior=None
        if args.resume_phase:
            with open(args.resume_phase) as f:prior=json.load(f)
        certificate=periodic_phase_refusal(args.hole,args.period,args.seconds,args.cubic_pivots,prior,
                                           args.cubic_sweep,args.retain_quadratics)
        if args.write:
            with open(args.write,'w') as f:json.dump(certificate,f)
        result=(verify_saved(certificate) if certificate['status']=='refused' else
                dict(status=certificate['status'],history=certificate['history'],
                     stage=certificate['stage'],free_count=certificate['free_count'],
                     remaining_variables=certificate['remaining_variables'],all_pairs_decided=False))
        print(json.dumps(result|dict(elapsed=certificate['elapsed']),sort_keys=True))
        return
    if args.period_two_phase_refusal:
        certificate = period_two_phase_refusal(args.hole,args.seconds,args.cubic_pivots)
        if args.write:
            with open(args.write,'w') as f: json.dump(certificate,f)
        result = (verify_saved(certificate) if certificate['status']=='refused'
                  else dict(status=certificate['status'],all_pairs_decided=False))
        print(json.dumps(result|dict(elapsed=certificate['elapsed']),sort_keys=True))
        return
    if args.parity_completion:
        certificate = parity_completion_certificate(args.hole,args.half%2)
        if args.write:
            with open(args.write,'w') as f: json.dump(certificate,f)
        print(json.dumps(verify_saved(certificate),sort_keys=True))
        return
    if args.parity_traces:
        certificate = parity_trace_certificate(args.hole)
        if args.write:
            with open(args.write,'w') as f: json.dump(certificate,f)
        print(json.dumps(verify_saved(certificate),sort_keys=True))
        return
    if args.interior_cocycle:
        certificate = interior_parity_cocycle(args.hole)
        if args.write:
            with open(args.write,'w') as f: json.dump(certificate,f)
        print(json.dumps(verify_saved(certificate) |
                         dict(shell_rows=len(certificate['shell_rows']),
                              observable_terms=len(certificate['observable'])),sort_keys=True))
        return
    if args.interior_rank:
        certificate = interior_rank_certificate(args.hole)
        verified = verify_interior_rank_certificate(certificate)
        if args.write:
            with open(args.write,'w') as f: json.dump(certificate,f)
        print(json.dumps({k:v for k,v in certificate.items() if k!='columns'} |
                         dict(verified=verified,
                              rational_function_nullity=(certificate['variables']-
                                                        certificate['rows']) if verified else None),
                         sort_keys=True))
        return
    if args.folded_cubic:
        if args.cubic_pivots<1 or not math.isfinite(args.seconds) or args.seconds<=0:
            p.error('require positive --seconds and --cubic-pivots')
        if args.cubic_proof and args.joint_fields:
            p.error('--cubic-proof currently requires the original unquotiented shell rows')
        started=time.monotonic()
        keys,rows=compile_moving_folded(args.half,args.period,args.folded_patch,args.hole)
        source_rows=rows
        size=len(keys);joint=None
        if args.joint_fields:
            remaining=args.seconds-(time.monotonic()-started)
            joint=joint_sign_closure(size,rows,max(remaining,.000001),short_recovery=True)
            if joint['complete'] and not joint['conflict']:
                size,rows=joint['size'],joint['rows']
        remaining=args.seconds-(time.monotonic()-started)
        if joint is not None and joint['conflict']:
            result=dict(status='refused_by_joint_fields',complete=True)
        elif remaining<=0 or (joint is not None and not joint['complete']):
            result=dict(status='unknown',stage='joint_fields',complete=False)
        else:result=cubic_shell_analysis(size,rows,remaining/2 if args.cubic_search else remaining,args.cubic_pivots,args.cubic_proof)
        if args.cubic_search and 'recovery' in result and result.get('status')!='refused':
            basis=cubic_sign_basis(size,rows,result)
            remaining=args.seconds-(time.monotonic()-started)
            if remaining>0:
                engine=make_engine(size,rows,reduced_binary_basis(basis),remaining,args.nodes,'connected')
                remaining=args.seconds-(time.monotonic()-started)
                if remaining>0:
                    engine.seconds=remaining
                    index,sign=joint['aliases'][0] if joint is not None else (0,1)
                    status,values=engine.run({index:sign})
                    result['search']=dict(status=status,nodes=engine.nodes,parity_free=size-len(basis))
                    if values is not None:
                        restored=([s*values[i] for i,s in joint['aliases']] if joint is not None else values)
                        if any(sum(c*restored[i] for i,c in row.items()) for row in source_rows):
                            raise AssertionError('cubic-assisted signing fails untouched shell rows')
                        result['assignment']=[[list(k),v] for k,v in zip(keys,restored)]
        if joint is not None:result['joint_history']=joint['history']
        result.update(mode='folded_cubic',half=args.half,period=args.period,
                      patch=args.folded_patch,hole=args.hole,all_pairs_decided=False,
                      literal_existence_decided=False,elapsed=time.monotonic()-started)
        if 'assignment' in result:
            result.update(mode='moving_folded',method='cubic_assisted',status='sat',
                          complete=True,literal_existence_decided=True,
                          minimum_half=2*args.folded_patch+4+args.period,
                          half_residue=args.half%args.period)
        if args.write:
            with open(args.write,'w') as f:json.dump(result,f)
        print(json.dumps({k:v for k,v in result.items() if k not in
                          ('free','parameter_ids','recovery','linear_polynomials','assignment','cubic_proof')},sort_keys=True))
        return
    if args.relation_search and not args.folded_relations:
        p.error('--relation-search requires --folded-relations')
    if args.folded_hulls or args.folded_relations:
        if not 0<=args.hull_rank<=16:p.error('--hull-rank must be in 0..16')
        result=folded_hull_diagnostic(args.half,args.period,args.folded_patch,args.hole,
                                     args.seconds,args.hull_rank,args.joint_fields,args.folded_relations,
                                     args.relation_search,args.nodes)
        if args.write:
            with open(args.write,'w') as f:json.dump(result,f)
        print(json.dumps(result,sort_keys=True))
        return
    if args.moving_reduced and args.moving_strip_audit is None:
        p.error('--moving-reduced requires --moving-strip-audit')
    if args.moving_strip_audit is not None:
        print(json.dumps(moving_folded_audit(args.moving_strip_audit,args.hole,args.moving_reduced),sort_keys=True))
        return
    if args.moving_folded:
        result=moving_folded_search(args.half,args.period,args.folded_patch,args.hole,args.seconds,args.nodes)
        if args.write:
            with open(args.write,'w') as f:json.dump(result,f)
        print(json.dumps({k:v for k,v in result.items() if k not in ('assignment','certificate')},sort_keys=True))
        return
    if args.hole_piece and not (args.split_edge or args.split_dyadic):
        p.error('--hole-piece requires --split-edge or --split-dyadic')
    if args.hole_offset and not (args.split_edge or args.split_endpoints or args.split_dyadic):
        p.error('--hole-offset requires a split-edge analysis')
    if args.split_dyadic:
        keys,formal=split_edge_system(args.hole,args.edge_patch,args.edge_pieces,
                                     args.piece_period,args.hole_offset,hole_piece=args.hole_piece)
        analysis=dyadic_quadratic_analysis(len(keys),list(formal.values()),args.seconds)
        result=dict(mode='split_dyadic',hole=args.hole,patch=args.edge_patch,
                    pieces=args.edge_pieces,word_period=args.piece_period,
                    hole_offset=args.hole_offset,hole_piece=args.hole_piece,
                    analysis=analysis,all_pairs_decided=False)
        if args.write:
            with open(args.write,'w') as f:json.dump(result,f)
        summary={k:v for k,v in analysis.items() if k not in ('free','certificate','linear_relations')}
        summary.update(free_count=len(analysis.get('free',[])),
                       necessary_linear_relations=len(analysis.get('linear_relations',[])),
                       all_pairs_decided=False)
        print(json.dumps(summary,sort_keys=True))
        return
    if args.lift_repair_bound is not None:
        result = growing_lift_repair_bound(args.lift_repair_bound)
        if args.write:
            with open(args.write,'w') as f: json.dump(result,f)
        print(json.dumps(result,sort_keys=True))
        return
    if args.split_bulk:
        result = split_bulk_refusal()
        if args.write:
            with open(args.write,'w') as f: json.dump(result,f)
        print(json.dumps({k:v for k,v in result.items() if k!='certificate'},sort_keys=True))
        return
    if args.split_endpoints:
        result=split_endpoint_refusal(args.hole,args.edge_patch,args.piece_period,args.hole_offset)
        if args.write:
            with open(args.write,'w') as f:json.dump(result,f)
        print(json.dumps({k:v for k,v in result.items() if k!='certificate'},sort_keys=True))
        return
    if args.flat_any_holes is not None:
        result = flat_piece_any_holes_bound(args.flat_any_holes,args.edge_pieces,args.edge_patch)
        if args.write:
            with open(args.write,'w') as f: json.dump(result,f)
        print(json.dumps(result,sort_keys=True))
        return
    if args.edge_patch and not (args.moving or args.split_edge):
        p.error('--edge-patch requires --moving or --split-edge')
    if args.split_edge:
        result=split_edge_search(args.hole,args.edge_patch,args.seconds,args.nodes,args.edge_pieces,
                                 args.piece_period,args.hole_offset,args.hole_piece)
        if args.write:
            with open(args.write,'w') as f:json.dump(result,f)
        print(json.dumps({k:v for k,v in result.items() if k not in ('assignment','certificate')},sort_keys=True))
        return
    if args.residue_lift is not None:
        result = residue_lift_plan(args.residue_lift,args.lift_index)
        if args.write:
            with open(args.write,'w') as f: json.dump(result,f)
        print(json.dumps(result,sort_keys=True))
        return
    if args.bounded and (not (args.residue_parity is not None or args.audit_resistant_residues)
                         or args.dyadic or args.retain_residue_witness):
        p.error('--bounded requires residue parity analysis or audit, without dyadic witness mode')
    if args.audit_resistant_residues:
        result = resistant_residue_audit(args.period,args.seconds,args.max_bits,args.bounded)
        if args.write:
            with open(args.write,'w') as f: json.dump(result,f)
        print(json.dumps(result,sort_keys=True))
        return
    if args.residue_zero is not None or args.residue_parity is not None:
        if args.residue_zero is not None and args.residue_parity is not None:
            p.error('choose one residue analysis')
        parity = args.residue_parity is not None
        scale = args.residue_parity if parity else args.residue_zero
        if args.retain_residue_witness and not (parity and args.dyadic and args.write):
            p.error('--retain-residue-witness requires --residue-parity, --dyadic and --write')
        if not args.holes:
            p.error('residue analysis requires --holes ARM:DEPTH ARM:DEPTH')
        try:
            holes = [tuple(map(int,text.split(':'))) for text in args.holes]
            if any(len(hole)!=2 for hole in holes):
                raise ValueError('require arm:depth holes')
            groups = residue_shell_groups([99*scale,79*scale,23*scale],holes,args.period)
            if parity:
                if args.bounded:
                    result = residue_bounded_search(groups,args.seconds,args.max_bits)
                else:
                    solver = residue_dyadic_parity if args.dyadic else residue_integer_parity
                    result = (solver(groups,args.seconds,args.max_bits,args.retain_residue_witness)
                              if args.dyadic else solver(groups,args.seconds,args.max_bits))
        except (ValueError,TypeError) as error:
            p.error(str(error))
        if parity:
            result.update(mode='residue_parity',t=scale,holes=holes,period=args.period)
        else:
            certificate = residue_zero_certificate(groups)
            result = dict(mode='residue_zero',t=scale,holes=holes,period=args.period,
                          status='support_refused_by_odd_group' if certificate else 'unknown',
                          certificate=certificate,all_pairs_decided=False)
        if args.write:
            with open(args.write,'w') as f: json.dump(result,f)
        summary = {k:v for k,v in result.items() if k not in ('witness','aggregate_sums')}
        if 'aggregate_sums' in result:
            summary['bounded_aggregates'] = len(result['aggregate_sums'])
        if 'witness' in result:
            summary['witness_residues'] = len(result['witness']['aggregate_residues'])
        print(json.dumps(summary,sort_keys=True))
        return
    if args.fourth_root_census:
        print(json.dumps(fourth_root_mod8_census(),sort_keys=True))
        return
    if args.full_partition_bound is not None:
        print(json.dumps(full_partition_subdivision_bound((99,79,23),args.full_partition_bound),sort_keys=True))
        return
    if args.audit_coarse:
        print(json.dumps(coarse_projection_audit(args.period,args.hole),sort_keys=True))
        return
    if args.audit_boundary:
        print(json.dumps(moving_boundary_audit(args.period,args.hole),sort_keys=True))
        return
    if args.boundary_refusal:
        print(json.dumps(moving_boundary_refusal(args.hole,args.seconds),sort_keys=True))
        return
    if args.coarse_supports:
        print(json.dumps(coarse_support_catalog(args.seconds),sort_keys=True))
        return
    if args.coarse_catalog:
        result = coarse_catalog(args.hole,args.seconds)
        if args.write:
            with open(args.write,'w') as f: json.dump(result,f)
        print(json.dumps({k:v for k,v in result.items() if k not in ('assignments','keys')},sort_keys=True))
        return
    if args.coarse:
        result = coarse_search(args.hole,args.seconds,args.nodes)
        if args.write:
            with open(args.write,'w') as f: json.dump(result,f)
        print(json.dumps({k:v for k,v in result.items() if k!='assignment'},sort_keys=True))
        return
    if args.condition_coarse:
        result = moving_coarse_search(args.period,args.hole,args.seconds,args.nodes,args.short_recovery)
        if args.write:
            with open(args.write,'w') as f: json.dump(result,f)
        print(json.dumps({k:v for k,v in result.items() if k!='assignment'},sort_keys=True))
        return
    if (args.joint_fields or args.square_lift or args.rational or args.reduced_xor) and not args.moving:
        p.error('--joint-fields, --square-lift, --reduced-xor and --rational require --moving')
    if args.moving:
        result = moving_search(args.period,args.seconds,args.nodes,args.free_order,rational=args.rational,affine_shells=args.affine_shells,square_lift=args.square_lift,joint_fields=args.joint_fields,reduced_xor=args.reduced_xor,hole=args.hole,edge_patch=args.edge_patch,short_recovery=args.short_recovery)
        if args.write:
            with open(args.write,'w') as f: json.dump(result,f)
        print(json.dumps({k:v for k,v in result.items() if k!='assignment'},sort_keys=True))
        return
    if args.affine_shells:
        keys,rows = compile_system(args.half,args.period,args.patch_width)
        report = affine_shell_closure(len(keys),rows,args.seconds)
        report.pop('basis')
        print(json.dumps(dict(t=2*args.half+1,period=args.period,
                              all_pairs_decided=False,**report),sort_keys=True))
        return
    if args.ternary:
        keys,rows = compile_system(args.half,args.period,args.patch_width)
        start = time.monotonic()
        size,extra = len(keys),{}
        if args.parity_quotient:
            quotient = parity_sign_quotient(size,rows,args.seconds)
            if not quotient['complete'] or quotient.get('conflict'):
                print(json.dumps(dict(stage='parity_quotient',**{k:v for k,v in quotient.items()
                                      if k not in ('rows','aliases')},all_pairs_decided=False),sort_keys=True))
                return
            size,rows = quotient['size'],quotient['rows']
            extra = dict(quotient_variables=size,binary_rank=quotient['rank'])
        remaining = args.seconds-(time.monotonic()-start)
        result = (ternary_analysis(size,rows,remaining,args.sparse_pivots,
                                  retain_kernel=args.parity_quotient) if remaining>0 else
                  dict(complete=False,stage='parity_quotient'))
        if 'kernel' in result:
            result['nonzero_relation_count'] = len(ternary_nonzero_relations(result.pop('kernel')))
        print(json.dumps(dict(t=2*args.half+1,period=args.period,patch_width=args.patch_width,
                              variables=len(keys),rows=len(rows),all_pairs_decided=False,
                              **extra,**result),sort_keys=True))
        return
    if args.verify:
        with open(args.verify) as f: print(json.dumps(verify_saved(json.load(f)),sort_keys=True))
        return
    result = search(args.half,args.period,args.seconds,args.nodes,args.patch_width,args.free_order)
    if args.write:
        with open(args.write,'w') as f: json.dump(result,f)
    print(json.dumps({**{k:v for k,v in result.items() if k not in ('assignment','certificate')},
                      'certificate_rows':len(result.get('certificate',[]))},sort_keys=True))


if __name__ == '__main__': main()
