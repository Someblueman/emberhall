"""All-scale middle-operator kernel, rank, left-kernel duality, and compatibility classification."""
import argparse
from fractions import Fraction
import json
from math import gcd
from numbers import Rational
import sys
import full_shorter_coupling as fc


def validate(t, h):
    fc.validate(t, h)
    if h > 2 * t - 2:
        raise ValueError('require 0<=h<=2t-2')


def v2(n):
    """Exact 2-adic valuation of a positive integer."""
    if type(n) is not int or n < 1:
        raise ValueError('require a positive integer for 2-adic valuation')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count


def nullity_classification(t, h):
    """Exact closed-form rank and nullity of M(t, h) for every t>=1, 0<=h<=2t-2."""
    validate(t, h)
    g1 = gcd(3 * t, h + 1)
    d1 = g1 // 2
    if h == 0:
        g2 = 1
        type2_active = False
        d2 = 0
    else:
        g2 = gcd(3 * t + 2, h)
        type2_active = v2(3 * t + 2) > v2(h)
        d2 = (gcd(3 * t + 2, 2 * h) - g2) // 2
    nullity = d1 + d2
    width = 2 * h + 2
    return dict(
        t=t,
        h=h,
        matrix_size=5 * t,
        seed_width=width,
        seed_rank=width - nullity,
        rank=5 * t - nullity,
        nullity=nullity,
        cokernel_dimension=nullity,
        invertible=(nullity == 0),
        type1_period=g1,
        type1_nullity=d1,
        type2_antiperiod=g2 if h > 0 else None,
        type2_active=type2_active,
        type2_nullity=d2,
        universal_existence_proved=False,
        all_hole_placements_covered=False,
    )


def kernel_basis(t, h):
    """Explicit integer basis of ker M(t, h) with entries in {-1, 0, +1}.

    Combines d1 = floor(gcd(3t, h+1)/2) Type-I periodic antisymmetric vectors
    and d2 = floor((gcd(3t+2, 2h) - gcd(3t+2, h))/2) Type-II antiperiodic
    antisymmetric vectors.
    """
    validate(t, h)
    n = 5 * t
    lo, hi = 2 * t - h - 1, 2 * t + h
    basis = []
    g1 = gcd(3 * t, h + 1)
    for r in range(g1):
        rp = (10 * t + 1 - r) % g1
        if r < rp:
            z = {i: int(i % g1 == r) - int(i % g1 == rp) for i in range(1, n + 1)}
            basis.append(dict(
                kind='type1_periodic',
                modulus=g1,
                residue_pair=[r, rp],
                reflection_quotient=(10 * t + 1 - r - rp) // g1,
                seed=[z[i] for i in range(lo, hi + 1)],
                vector=z,
            ))
    if h > 0 and v2(3 * t + 2) > v2(h):
        g2 = gcd(3 * t + 2, h)
        for r in range(g2):
            rp = (10 * t + 1 - r) % g2
            if r < rp:
                q2 = (10 * t + 1 - r - rp) // g2
                z = {}
                for i in range(1, n + 1):
                    rem = i % g2
                    if rem == r:
                        z[i] = (-1) ** ((i - r) // g2)
                    elif rem == rp:
                        z[i] = (-1) ** (q2 + 1 + (i - rp) // g2)
                    else:
                        z[i] = 0
                basis.append(dict(
                    kind='type2_antiperiodic',
                    modulus=g2,
                    residue_pair=[r, rp],
                    reflection_quotient=q2,
                    seed=[z[i] for i in range(lo, hi + 1)],
                    vector=z,
                ))
    return basis


def dual_left_vector(t, h, z):
    """Exact left-right kernel duality isomorphism L: ker M(t, h) -> ker(M(t, h)^T).

    Because L^T M = M^T L is globally symmetric on Q^(5t), L maps every
    right-kernel vector z in ker M(t, h) to an exact left-kernel vector w.
    """
    validate(t, h)
    if set(z) != set(range(1, 5 * t + 1)):
        raise ValueError('require 5t middle coordinates')
    lo = 2 * t - h - 1
    w = {i: 0 for i in range(1, lo)}
    w[lo] = z[5 * t]
    for r in range(h):
        w[2 * t - h + r] = z[5 * t - 1 - r] - z[5 * t - r]
    for i in range(2 * t, 5 * t + 1):
        w[i] = z[i]
    return w


def left_kernel_basis(t, h):
    """Explicit integer basis of ker(M(t, h)^T) via the duality isomorphism L."""
    out = []
    for item in kernel_basis(t, h):
        w = dual_left_vector(t, h, item['vector'])
        out.append(dict(
            kind=item['kind'],
            modulus=item['modulus'],
            residue_pair=list(item['residue_pair']),
            reflection_quotient=item['reflection_quotient'],
            weights=w,
        ))
    return out


def straddle_corrected_upper(t, h, b):
    """Reduced upper right-hand side tilde_b = b_U - M_{U,S} b_S on 2t..5t."""
    validate(t, h)
    if set(b) != set(range(1, 5 * t + 1)) or any(not isinstance(v, Rational) or isinstance(v, bool) for v in b.values()):
        raise ValueError('require 5t rational forcing coordinates')
    tb = {i: b[i] for i in range(2 * t, 5 * t + 1)}
    if h == 0:
        tb[5 * t] = b[5 * t] + b[2 * t - 1]
    else:
        tb[5 * t - h] = b[5 * t - h] + b[2 * t - 1]
        for r in range(1, h):
            tb[5 * t - r] = b[5 * t - r] - b[2 * t - h + r] + b[2 * t - h - 1 + r]
        tb[5 * t] = b[5 * t] - b[2 * t - h] + b[2 * t - h - 1]
    return tb


def compatibility_residuals(t, h, b):
    """Necessary and sufficient seed-free forcing compatibility equalities w^T b = 0."""
    tb = straddle_corrected_upper(t, h, b)
    lbasis = left_kernel_basis(t, h)
    type1 = []
    type2 = []
    first_failure = None
    for idx, item in enumerate(lbasis):
        w = item['weights']
        val = sum(w[i] * b[i] for i in range(1, 5 * t + 1))
        entry = dict(
            index=idx,
            kind=item['kind'],
            modulus=item['modulus'],
            residue_pair=item['residue_pair'],
            residual=val,
        )
        if item['kind'] == 'type1_periodic':
            type1.append(entry)
        else:
            type2.append(entry)
        if val != 0 and first_failure is None:
            first_failure = dict(
                index=idx,
                kind=item['kind'],
                modulus=item['modulus'],
                residue_pair=item['residue_pair'],
                residual=int(val) if isinstance(val, int) or (isinstance(val, Fraction) and val.denominator == 1) else str(val),
            )
    info = nullity_classification(t, h)
    return dict(
        t=t,
        h=h,
        compatible=(first_failure is None),
        nullity=info['nullity'],
        type1_nullity=info['type1_nullity'],
        type2_nullity=info['type2_nullity'],
        type1_residuals=[int(e['residual']) if isinstance(e['residual'], int) or (isinstance(e['residual'], Fraction) and e['residual'].denominator == 1) else str(e['residual']) for e in type1],
        type2_residuals=[int(e['residual']) if isinstance(e['residual'], int) or (isinstance(e['residual'], Fraction) and e['residual'].denominator == 1) else str(e['residual']) for e in type2],
        failed_equalities=sum(e['residual'] != 0 for e in type1 + type2),
        first_failure=first_failure,
        straddle_corrected_upper=tb,
    )


def forcing(t, h, sigma, word):
    """Zero-middle shell residual forcing b_i = K_{92t+1+i} for i=1..5t."""
    validate(t, h)
    if type(sigma) is not int or (sigma not in (-1, 1) if h else sigma != 0):
        raise ValueError('centre sign disagrees with hole placement')
    if not isinstance(word, str) or len(word) != 79 * t or set(word) - set('+-'):
        raise ValueError('require a literal second word of length 79t')
    y = {d: 1 if ch == '+' else -1 for d, ch in enumerate(word, 1)}
    zero = {d: 0 for d in range(13 * t + 1, 18 * t + 1)}
    rows = fc.shell_rows(*fc.geometry(t, h), fc.linear_completion(t, h, sigma, y, zero))
    return {i: rows.get(92 * t + 1 + i, 0) for i in range(1, 5 * t + 1)}


def recurrence_forcing(t, h, b):
    validate(t, h)
    if set(b) != set(range(1, 5 * t + 1)) or any(not isinstance(v, Rational) or isinstance(v, bool) for v in b.values()):
        raise ValueError('require 5t rational forcing coordinates')
    def R(a):
        return b[7 * t - h - a] - b[a + h]
    return {
        i: b[i] - b[i - 1] + R(7 * t - i + 1) + R(7 * t - i - h + 1) - R(7 * t - i - h)
        for i in range(2 * t + h + 1, 5 * t + 1)
    }


def affine_transfer(t, h, b):
    """Propagate p(b) + T * seed from the forward recurrence and lower equations."""
    c = recurrence_forcing(t, h, b)
    lo, hi, n = 2 * t - h - 1, 2 * t + h, 5 * t
    width = 2 * h + 2
    p = {i: Fraction(0) for i in range(lo, hi + 1)}
    T = {i: [int(j == i - lo) for j in range(width)] for i in p}
    dp = {i: p[i] - p[i - 1] for i in range(lo + 1, hi + 1)}
    dt = {i: [x - y for x, y in zip(T[i], T[i - 1])] for i in dp}
    for i in range(hi + 1, n + 1):
        if h:
            dp[i] = dp[i - 2 * h - 1] + dp[i - h - 1] - dp[i - h] + c[i]
            dt[i] = [x + y - z for x, y, z in zip(dt[i - 2 * h - 1], dt[i - h - 1], dt[i - h])]
        else:
            dp[i] = dp[i - 1] + Fraction(c[i], 2)
            dt[i] = list(dt[i - 1])
        p[i] = p[i - 1] + dp[i]
        T[i] = [x + y for x, y in zip(T[i - 1], dt[i])]
    D = 3 * t + 1
    for i in range(1, lo):
        p[i] = b[i] + p[i + D] - p[i + D + h + 1] + p[i + D + h]
        T[i] = [x - y + z for x, y, z in zip(T[i + D], T[i + D + h + 1], T[i + D + h])]
    return p, T


def solve_middle(t, h, b):
    """Check closed-form compatibility equalities, then solve M(t, h) z = b."""
    comp = compatibility_residuals(t, h, b)
    info = nullity_classification(t, h)
    if not comp['compatible']:
        return dict(
            consistent=False,
            classification=info,
            compatibility=comp,
            literal_middle_checked=True,
            literal_middle_excluded=True,
            exclusion_reason='failed_left_kernel_compatibility',
        )
    p, T = affine_transfer(t, h, b)
    width = 2 * h + 2
    basis = {}
    # Only active rows lo..2t+2h need to be scanned, though scanning lo..5t is exact.
    lo = 2 * t - h - 1
    for i in range(lo, 5 * t + 1):
        terms = {d - 13 * t: a for d, a in fc.middle_operator(t, h, 13 * t + i).items()}
        row = [Fraction(sum(a * T[d][j] for d, a in terms.items())) for j in range(width)]
        rhs = Fraction(b[i]) - sum(a * p[d] for d, a in terms.items())
        for pivot, (br, bv) in sorted(basis.items()):
            scale = row[pivot]
            if scale:
                row = [x - scale * y for x, y in zip(row, br)]
                rhs -= scale * bv
        pivot = next((j for j, x in enumerate(row) if x), None)
        if pivot is None:
            if rhs:
                raise AssertionError('compatibility theorem violation: row inconsistent after passing left kernel')
        else:
            scale = row[pivot]
            basis[pivot] = ([x / scale for x in row], rhs / scale)
    if len(basis) != info['seed_rank']:
        raise AssertionError('seed rank disagrees with proved classification')
    seed = [Fraction(0) for _ in range(width)]
    for pivot, (row, rhs) in sorted(basis.items(), reverse=True):
        seed[pivot] = rhs - sum(row[j] * seed[j] for j in range(pivot + 1, width))
    particular = {i: p[i] + sum(a * x for a, x in zip(T[i], seed)) for i in p}
    for i in range(1, 5 * t + 1):
        if sum(a * particular[d - 13 * t] for d, a in fc.middle_operator(t, h, 13 * t + i).items()) != b[i]:
            raise AssertionError('particular solution failed an original middle row')
    kbasis = kernel_basis(t, h)
    unique = (info['nullity'] == 0)
    nonliteral = sum(v not in (-1, 1) for v in particular.values())
    return dict(
        consistent=True,
        classification=info,
        compatibility=comp,
        particular=particular,
        kernel_basis=kbasis,
        unique_middle=unique,
        particular_nonliteral_values=nonliteral,
        literal_middle_checked=unique,
        literal_middle_excluded=bool(unique and nonliteral > 0),
        exclusion_reason='unique_rational_middle_nonliteral' if (unique and nonliteral > 0) else None,
    )


def audit_word(t, h, sigma, word):
    """Audit a literal second word via closed-form nullity and compatibility."""
    b = forcing(t, h, sigma, word)
    solved = solve_middle(t, h, b)
    cls = solved['classification']
    comp = solved['compatibility']
    return dict(
        t=t,
        h=h,
        consistent=solved['consistent'],
        nullity=cls['nullity'],
        rank=cls['rank'],
        seed_width=cls['seed_width'],
        seed_rank=cls['seed_rank'],
        type1_period=cls['type1_period'],
        type1_nullity=cls['type1_nullity'],
        type2_antiperiod=cls['type2_antiperiod'],
        type2_active=cls['type2_active'],
        type2_nullity=cls['type2_nullity'],
        type1_residuals=comp['type1_residuals'],
        type2_residuals=comp['type2_residuals'],
        failed_equalities=comp['failed_equalities'],
        first_failure=comp['first_failure'],
        unique_middle=solved.get('unique_middle', False),
        particular_nonliteral_values=solved.get('particular_nonliteral_values'),
        literal_middle_checked=solved['literal_middle_checked'],
        literal_middle_excluded=solved['literal_middle_excluded'],
        exclusion_reason=solved['exclusion_reason'],
        full_candidate_constructed=False,
        balance_checked=False,
        unused_shells_checked=False,
        universal_existence_proved=False,
        all_hole_placements_covered=False,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', nargs='?', help='JSON file with t,h,centre,arm2; - reads stdin')
    parser.add_argument('--classify', nargs=2, type=int, metavar=('T', 'H'),
                        help='print exact nullity, rank, and basis metadata for (t, h)')
    parser.add_argument('--control', type=int, help='all-positive second word at scale t')
    parser.add_argument('--h', type=int, default=19, help='shallow hole depth h (default 19)')
    parser.add_argument('--negative-depths', default='',
                        help='comma-separated 1-based second-arm negative depths for --control')
    args = parser.parse_args()
    try:
        if args.classify is not None:
            t, h = args.classify
            result = nullity_classification(t, h)
            result['kernel_basis_summary'] = [
                dict(kind=item['kind'], modulus=item['modulus'], residue_pair=item['residue_pair'])
                for item in kernel_basis(t, h)
            ]
            print(json.dumps(result, sort_keys=True))
            return
        if args.control is not None:
            t, h = args.control, args.h
            validate(t, h)
            word = ['+'] * (79 * t)
            for depth in filter(None, args.negative_depths.split(',')):
                d = int(depth)
                if not 1 <= d <= len(word):
                    raise ValueError('negative depth outside second arm')
                word[d - 1] = '-'
            payload = dict(t=t, h=h, centre=1 if h else 0, arm2=''.join(word))
        elif args.input is not None:
            with (sys.stdin if args.input == '-' else open(args.input)) as stream:
                payload = json.load(stream)
        else:
            parser.error('supply an input JSON file, --classify T H, or --control T')
            return
        result = audit_word(payload['t'], payload['h'], payload['centre'], payload['arm2'])
        print(json.dumps(result, sort_keys=True))
    except (ValueError, KeyError) as exc:
        parser.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()
