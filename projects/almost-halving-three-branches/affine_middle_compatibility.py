"""Seed-independent rectangle bounds for exact affine middle forcing."""
import argparse
import json
from numbers import Rational
import full_shorter_coupling as fc


def validate(t, h):
    fc.validate(t, h)
    if h > 2*t-2:
        raise ValueError('require 0<=h<=2t-2')


def forcing(t, h, sigma, word):
    validate(t, h)
    if type(sigma) is not int or (sigma not in (-1, 1) if h else sigma != 0):
        raise ValueError('centre disagrees with holes')
    if not isinstance(word, str) or len(word) != 79*t or set(word)-set('+-'):
        raise ValueError('require a literal second word')
    y = {d: 1 if s == '+' else -1 for d, s in enumerate(word, 1)}
    zero = {d: 0 for d in range(13*t+1, 18*t+1)}
    rows = fc.shell_rows(*fc.geometry(t, h), fc.linear_completion(t, h, sigma, y, zero))
    return {i: rows.get(92*t+1+i, 0) for i in range(1, 5*t+1)}


def recurrence_forcing(t, h, b):
    validate(t, h)
    if set(b) != set(range(1, 5*t+1)) or any(not isinstance(v, Rational) or isinstance(v, bool) for v in b.values()):
        raise ValueError('require 5t rational forcing coordinates')
    def R(a):
        return b[7*t-h-a]-b[a+h]
    return {i: b[i]-b[i-1]+R(7*t-i+1)+R(7*t-i-h+1)-R(7*t-i-h)
            for i in range(2*t+h+1, 5*t+1)}


def endpoint_terms(h, u, v, m):
    """Coefficients after both telescopings; coincident endpoints cancel."""
    terms = {}
    for i, a in [(v, 1), (u-1, -1), (v-h, 1), (u-h-1, -1),
                 (v-m*(h+1), -1), (u-m*(h+1)-1, 1),
                 (v-h-m*(h+1), -1), (u-h-m*(h+1)-1, 1)]:
        terms[i] = terms.get(i, 0)+a
    return {i: a for i, a in terms.items() if a}


def rectangle_test(t, h, b):
    """All rectangle bounds of 8, O((3t-h)^2/(h+1)) integer operations.

    Returns a witnessed failing rectangle as soon as one occurs. Passing
    checks all rectangles, but does not assert literal feasibility.
    """
    c = recurrence_forcing(t, h, b)
    a, n, H = 2*t+h+1, 5*t, h+1
    step = {}
    prefix = {a-1: 0}
    for i in range(a, n+1):
        step[i] = c[i]+step.get(i-H, 0)
        prefix[i] = prefix[i-1]+step[i]
    largest = 0
    checked = 0
    for m in range(1, (n-a)//H+2):
        start = a+(m-1)*H-1
        low = high = prefix[start]-prefix.get(start-m*H, 0)
        ilo = ihi = start
        for v in range(start+1, n+1):
            q = prefix[v]-prefix.get(v-m*H, 0)
            candidates = [(q-low, ilo+1, v), (high-q, ihi+1, v)]
            for magnitude, u, end in candidates:
                largest = max(largest, magnitude)
                if magnitude > 8:
                    value = sum(c[i-k*H] for i in range(u, end+1) for k in range(m))
                    terms = endpoint_terms(h, u, end, m)
                    return dict(excluded=True, rectangle=[u, end, m], value=value,
                                endpoint_bound=sum(abs(x) for x in terms.values()),
                                endpoint_terms=terms, maximum_seen=largest,
                                recurrence_rows=len(c), completed_widths=checked)
            if q < low: low, ilo = q, v
            if q > high: high, ihi = q, v
        checked += 1
    return dict(excluded=False, maximum_seen=largest, recurrence_rows=len(c),
                completed_widths=checked)


def affine_transfer(t, h, b):
    """p+T*s from the proved recurrence, without accepting leftover rows.

    p has zero seed; T has identity seed. T is stored by coordinate.
    """
    from fractions import Fraction
    c = recurrence_forcing(t, h, b)
    lo, hi, n = 2*t-h-1, 2*t+h, 5*t
    width = 2*h+2
    p = {i: Fraction(0) for i in range(lo, hi+1)}
    T = {i: [int(j == i-lo) for j in range(width)] for i in p}
    dp = {i: p[i]-p[i-1] for i in range(lo+1, hi+1)}
    dt = {i: [x-y for x, y in zip(T[i], T[i-1])] for i in dp}
    for i in range(hi+1, n+1):
        if h:
            dp[i] = dp[i-2*h-1]+dp[i-h-1]-dp[i-h]+c[i]
            dt[i] = [x+y-z for x, y, z in zip(dt[i-2*h-1], dt[i-h-1], dt[i-h])]
        else:
            dp[i] = dp[i-1]+Fraction(c[i], 2)
            dt[i] = list(dt[i-1])
        p[i] = p[i-1]+dp[i]
        T[i] = [x+y for x, y in zip(T[i-1], dt[i])]
    D = 3*t+1
    for i in range(1, lo):
        p[i] = b[i]+p[i+D]-p[i+D+h+1]+p[i+D+h]
        T[i] = [x-y+z for x, y, z in zip(T[i+D], T[i+D+h+1], T[i+D+h])]
    return p, T


def exact_middle(t, h, b):
    """Exact affine seed elimination, not a rank conjecture from samples.

    Returns one rational solution plus a factored basis of the full kernel,
    or a seed-free incompatibility witness. Every original row is processed.
    """
    from fractions import Fraction
    p, T = affine_transfer(t, h, b)
    width = 2*h+2
    basis = {}
    for i in range(1, 5*t+1):
        terms = {d-13*t: a for d, a in fc.middle_operator(t, h, 13*t+i).items()}
        row = [Fraction(sum(a*T[d][j] for d, a in terms.items())) for j in range(width)]
        rhs = b[i]-sum(a*p[d] for d, a in terms.items())
        for pivot, (br, bv) in sorted(basis.items()):
            scale = row[pivot]
            if scale:
                row = [x-scale*y for x, y in zip(row, br)]
                rhs -= scale*bv
        pivot = next((j for j, x in enumerate(row) if x), None)
        if pivot is None:
            if rhs:
                return dict(consistent=False, failed_middle_row=i,
                            incompatible_residual=str(rhs), seed_width=width)
        else:
            scale = row[pivot]
            basis[pivot] = ([x/scale for x in row], rhs/scale)
    def backsub(free, homogeneous=False):
        seed = [Fraction(free.get(j, 0)) for j in range(width)]
        for pivot, (row, rhs) in sorted(basis.items(), reverse=True):
            seed[pivot] = (0 if homogeneous else rhs)-sum(row[j]*seed[j] for j in range(pivot+1, width))
        return seed
    free = [j for j in range(width) if j not in basis]
    seed = backsub({})
    z = {i: p[i]+sum(a*x for a, x in zip(T[i], seed)) for i in p}
    for i in range(1, 5*t+1):
        if sum(a*z[d-13*t] for d, a in fc.middle_operator(t, h, 13*t+i).items()) != b[i]:
            raise AssertionError('exact seed elimination failed an original middle row')
    # Kernel vectors stay factored as T times a small seed vector.
    kernel = [backsub({j: 1}, True) for j in free]
    return dict(consistent=True, middle=z, transfer=T, kernel_seeds=kernel,
                seed_width=width, seed_rank=len(basis),
                rational_kernel_dimension=len(free), rational_cokernel_dimension=len(free))


def solve_centre_hole(t, b):
    """Exact rational inverse of the full middle operator when h=0.

    Literal feasibility requires all returned coordinates to be +/-1.
    This does not solve balance or unused shells.
    """
    from fractions import Fraction
    c = recurrence_forcing(t, 0, b)
    l, n, D = 2*t-1, 5*t, 3*t+1
    z = {l: Fraction(0), l+1: Fraction(0)}
    delta = Fraction(0)
    for i in range(2*t+1, n+1):
        delta += Fraction(c[i], 2)
        z[i] = z[i-1]+delta
    for i in range(1, l):
        z[i] = b[i]+2*z[i+D]-z[i+D+1]
    def image(i):
        return sum(a*z[d-13*t] for d, a in fc.middle_operator(t, 0, 13*t+i).items())
    rn, rl = b[n]-image(n), b[l]-image(l)
    A = -(rn+rl)/(6*t)
    B = (rn-(7*t+1)*A)/2
    for i in z:
        z[i] += A*(i if i >= l else i+3*t)+B
    if any(image(i) != b[i] for i in range(1, n+1)):
        raise AssertionError('centre-hole inverse identity failed')
    return z


def reflected_test(t, b):
    """Aster's exact endpoint-sum test, independently implemented for controls."""
    p = 0
    candidates = {-2, 0, 2}
    for v in range(2*t, 5*t+1):
        p += b[v]-b[7*t-v]
        allowed = {-2, 2} if 2*v == 7*t-1 else {-2, 0, 2}
        candidates = {C for C in candidates if C-p in allowed}
    return sorted(candidates)


def audit(t, h, sigma, word):
    b = forcing(t, h, sigma, word)
    result = rectangle_test(t, h, b)
    result.update(t=t, h=h, reflected_endpoint_sums=reflected_test(t, b),
                  literal_second_word=True, full_candidate_constructed=False,
                  literal_completion_checked=False, balance_checked=False,
                  unused_shells_checked=False, universal_existence_proved=False,
                  all_hole_placements_covered=False)
    if h == 0:
        z = solve_centre_hole(t, b)
        bad = [i for i, value in z.items() if value not in (-1, 1)]
        result.update(middle_rational_kernel_dimension=0,
                      middle_rational_cokernel_dimension=0,
                      unique_middle_nonliteral_values=len(bad),
                      excluded_by_unique_middle=bool(bad))
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input', nargs='?', help='JSON file with t,h,centre,arm2; - reads stdin')
    p.add_argument('--control', type=int, help='all-positive second word at this scale')
    p.add_argument('--h', type=int, default=19)
    p.add_argument('--exact-middle', action='store_true', help='also eliminate the full rational middle seed')
    p.add_argument('--negative-depths', default='', help='comma-separated control-word negative depths')
    args = p.parse_args()
    if args.control is not None:
        word = ['+']*(79*args.control)
        for depth in filter(None, args.negative_depths.split(',')):
            d = int(depth)
            if not 1 <= d <= len(word): p.error('negative depth outside second arm')
            word[d-1] = '-'
        q = dict(t=args.control, h=args.h, centre=1 if args.h else 0, arm2=''.join(word))
    else:
        import sys
        with (sys.stdin if args.input == '-' else open(args.input)) as stream:
            q = json.load(stream)
    result = audit(q['t'], q['h'], q['centre'], q['arm2'])
    if args.exact_middle:
        exact = exact_middle(q['t'], q['h'], forcing(q['t'], q['h'], q['centre'], q['arm2']))
        result['exact_middle'] = {k: v for k, v in exact.items() if k not in ('middle', 'transfer', 'kernel_seeds')}
        if exact['consistent']:
            result['exact_middle']['particular_nonliteral_values'] = sum(v not in (-1, 1) for v in exact['middle'].values())
            result['exact_middle']['unique_middle'] = exact['rational_kernel_dimension'] == 0
            result['exact_middle']['middle_literal_values_checked'] = exact['rational_kernel_dimension'] == 0
            result['exact_middle']['excluded_by_unique_middle'] = (exact['rational_kernel_dimension'] == 0 and any(v not in (-1, 1) for v in exact['middle'].values()))
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
