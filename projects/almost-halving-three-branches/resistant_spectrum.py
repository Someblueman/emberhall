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


def split_edge_system(hole=19, patch=0, pieces=2, word_period=1):
    """Formal (1-z**word_period)K for t=pieces*L+1.

    Each piece has L vertices; its first/last patch vertices are independent.
    Each remaining piece repeats its own independent word of word_period
    signs. Require word_period|L, word_period|2*patch, L>=2*patch+word_period.
    Exponents are pairs (coefficient of L, constant), never sampled ranks.
    Holes are old first-arm vertices hole*t and 99*t. This is an ansatz.
    """
    if type(hole) is not int or not 1 <= hole < 99:
        raise ValueError('require 1<=hole<99')
    if type(patch) is not int or patch < 0:
        raise ValueError('require a nonnegative patch width')
    if type(pieces) is not int or pieces < 2:
        raise ValueError('require at least two pieces')
    if type(word_period) is not int or word_period < 1 or (2*patch)%word_period:
        raise ValueError('require a positive word period dividing twice the patch width')
    lengths = (99,79,23)
    keys, rows = [], defaultdict(lambda:defaultdict(int))

    def add(a,b): return a[0]+b[0],a[1]+b[1]
    def neg(a): return -a[0],-a[1]
    def old(q): return pieces*q,q

    def terms(arm, edge, centre=False):
        # Entries (slope in d, affine offset, coefficient) of a physical K column.
        if centre:
            out = [(0,(0,1),1)]+[(0,add(old(n),(0,1)),-1) for n in lengths]
        else:
            out = [(1,(0,1),1),(-1,add(old(lengths[arm-1]),(0,1)),-1)]
            out += [(1,add(old(n),(0,1)),-1) for a,n in enumerate(lengths,1) if a!=arm]
        for h in (hole,99):
            if centre:
                slope,offset = 0,old(h)
            elif arm==1 and edge<h:
                slope,offset = -1,old(h)
            else:
                slope,offset = 1,neg(old(h)) if arm==1 else old(h)
            out += [(slope,offset,-1),(slope,add(offset,(0,1)),1)]
        return out

    def column(key,arm,edge,lo,hi,single=False,centre=False):
        i=len(keys);keys.append(key)
        for slope,offset,c in terms(arm,edge,centre):
            if single:
                e=add(tuple(slope*x for x in lo),offset)
                ends=((e,c),(add(e,(0,word_period)),-c))
            elif slope==1:
                ends=((add(lo,offset),c),(add(add(hi,offset),(0,word_period)),-c))
            elif slope==-1:
                ends=((add(neg(hi),offset),c),(add(add(neg(lo),offset),(0,word_period)),-c))
            else:
                raise AssertionError('a run has constant distance')
            for e,value in ends:rows[e][i]+=value

    column(('old',0,0),0,0,(0,0),(0,0),True,True)
    for arm,n in enumerate(lengths,1):
        for q in range(1,n+1):
            if arm==1 and q in (hole,99):continue
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


def split_endpoint_system():
    """Fixed necessary endpoint rows for every number p>=2 of flat pieces.

    Retain slope exponents divisible by p. Only the first and last pieces
    enter: a forward run contributes at r and r+1, a reflected run at -r-1
    and -r, modulo p. The p=2 extraction therefore defines the uniform map.
    No endpoint patches are included in this relaxation.
    """
    keys,formal=split_edge_system(19,0,2)
    rows={(q//2,c):row for (q,c),row in formal.items() if q%2==0}
    return keys,dict(sorted(rows.items()))


def split_endpoint_refusal():
    keys,rows=split_endpoint_system()
    certificate,_=binary_elimination(list(rows.values()))
    if certificate is None or not verify_refusal(list(rows.values()),certificate):
        raise AssertionError('uniform flat-piece endpoint refusal was not verified')
    return dict(mode='split_endpoints',status='ansatz_refused_by_parity',
                variables=len(keys),rows=len(rows),certificate=certificate,
                scope='all p>=2 equal constant pieces, no patches, holes 19t and 99t',
                all_pairs_decided=False)


def split_edge_search(hole=19,patch=0,seconds=30,nodes=10000,pieces=2,word_period=1):
    """Try literal edge-piece plateaus; a timeout has no mathematical outcome."""
    start=time.monotonic()
    keys,formal=split_edge_system(hole,patch,pieces,word_period)
    original=list(formal.values())
    result=dict(mode='split_edge',hole=hole,patch=patch,pieces=pieces,word_period=word_period,
                variables=len(keys),rows=len(original),minimum_piece_length=2*patch+word_period,
                piece_length_divisor=word_period,all_pairs_decided=False,
                scope='independent periodic edge-piece interiors with free endpoint patches')
    def done(status,**extra):return dict(**result,status=status,elapsed=time.monotonic()-start,**extra)
    certificate,basis=binary_elimination(original)
    if certificate is not None:
        return done('ansatz_refused_by_parity',certificate=certificate)
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


def affine_shell_closure(size, original, seconds=30, rounds=20, local_rank=12):
    """Necessary binary closure using exact local sign-pattern affine hulls.

    All parameters remain binary coordinates of original signs. A local hull
    contains every locally valid assignment, so adding its equations never
    removes a literal solution. A compatible hull is not a sign witness.
    """
    if (type(size) is not int or size<1 or type(seconds) not in (int,float)
            or not math.isfinite(seconds) or seconds<=0 or type(rounds) is not int
            or rounds<1 or type(local_rank) is not int or not 0<=local_rank<=16):
        raise ValueError('require positive size/time/rounds and local rank in 0..16')
    original = list(original)
    if any(type(i) is not int or not 0<=i<size or type(c) is not int
           for row in original for i,c in row.items()):
        raise ValueError('invalid integer shell row')
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
        for label,row in enumerate(original):
            if time.monotonic()-start>=seconds: return result(False,stage='local_hulls')
            local_basis,generators,terms = {},[],defaultdict(int)
            for i,c in row.items():
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
            n = len(generators)
            if n>local_rank:
                skipped += 1
                continue
            signature = n,tuple(sorted((m,c) for m,c in terms.items() if c))
            if signature not in cache:
                valid = []
                for v in range(1<<n):
                    if time.monotonic()-start>=seconds: return result(False,stage='local_enumeration')
                    if not sum(c*(-1 if (m&v).bit_count()%2 else 1) for m,c in signature[1]):
                        valid.append(v)
                if not valid: return result(True,True,stage='empty_local_hull',row=label)
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
                if not add(mask,rhs): return result(True,True,stage='inconsistent_hulls',row=label)
        history.append(dict(round=iteration+1,added=len(basis)-before,skipped=skipped))
        if len(basis)==before: return result(True,fixed_point=True)
    return result(False,stage='round_limit')


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
    if saved.get('mode')=='growing_lift_repair_bound':
        expected = growing_lift_repair_bound(saved.get('t'))
        if json.dumps(saved,sort_keys=True)!=json.dumps(expected,sort_keys=True):
            raise ValueError('saved repair bound does not match the symbolic shell calculation')
        return dict(verified=True,all_pairs_decided=False,claim=expected['scope'])
    if saved.get('mode')=='split_endpoints':
        _,rows=split_endpoint_system()
        if not verify_refusal(list(rows.values()),saved.get('certificate',[])):
            raise ValueError('invalid uniform flat-piece endpoint refusal')
        return dict(verified=True,claim='only equal constant pieces on the named support are refused',
                    all_pairs_decided=False)
    if saved.get('mode')=='split_edge':
        word_period=saved.get('word_period',1)
        keys,formal=split_edge_system(saved['hole'],saved['patch'],saved['pieces'],word_period)
        if saved.get('status')=='ansatz_refused_by_parity':
            if not verify_refusal(list(formal.values()),saved['certificate']):
                raise ValueError('invalid split-edge parity refusal')
            return dict(verified=True,claim='only the split-edge ansatz is refused',all_pairs_decided=False)
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
    p.add_argument('--edge-patch',type=int,default=0,help='free endpoint vertices in moving or split-edge mode')
    p.add_argument('--split-edge',action='store_true',help='independent constant edge pieces; t=pieces*L+1')
    p.add_argument('--edge-pieces',type=int,default=2,help='number of constant pieces per edge in split-edge mode')
    p.add_argument('--piece-period',type=int,default=1,help='independent repeating word length within each edge piece')
    p.add_argument('--split-endpoints',action='store_true',help='portable endpoint refusal for every number of flat pieces')
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
    p.add_argument('--bounded',action='store_true',help='seek exact residue sums within physical group bounds; failure is unknown')
    p.add_argument('--retain-residue-witness',action='store_true',help='save independently verifiable aggregate compatibility with --dyadic and --write')
    p.add_argument('--audit-resistant-residues',action='store_true',help='audit all resistant scale phases through --period')
    p.add_argument('--holes',nargs=2,metavar='ARM:DEPTH',help='exactly two physical holes, centre is 0:0')
    args = p.parse_args()
    if args.lift_repair_bound is not None:
        result = growing_lift_repair_bound(args.lift_repair_bound)
        if args.write:
            with open(args.write,'w') as f: json.dump(result,f)
        print(json.dumps(result,sort_keys=True))
        return
    if args.split_endpoints:
        result=split_endpoint_refusal()
        if args.write:
            with open(args.write,'w') as f:json.dump(result,f)
        print(json.dumps({k:v for k,v in result.items() if k!='certificate'},sort_keys=True))
        return
    if args.edge_patch and not (args.moving or args.split_edge):
        p.error('--edge-patch requires --moving or --split-edge')
    if args.split_edge:
        result=split_edge_search(args.hole,args.edge_patch,args.seconds,args.nodes,args.edge_pieces,args.piece_period)
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
