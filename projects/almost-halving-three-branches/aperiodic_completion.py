#!/usr/bin/env python3
"""Exact arbitrary-word long-arm recovery; no periodic assumption."""
from collections import defaultdict, deque
from fractions import Fraction
from pathlib import Path
import argparse
import json


def vertices(lengths):
    yield (0, 0)
    for i, n in enumerate(lengths, 1):
        for d in range(1, n + 1):
            yield (i, d)


def validate(lengths, holes):
    if not isinstance(lengths,(list,tuple)) or len(lengths) != 3 or any(type(n) is not int or n < 1 for n in lengths):
        raise ValueError('three positive integer lengths required')
    try:
        holes = set(map(tuple, holes))
    except TypeError as exc:
        raise ValueError('holes must be coordinate pairs') from exc
    if len(holes)>2 or any(len(v)!=2 or any(type(c) is not int for c in v) or
            not (v==(0,0) or 1<=v[0]<=3 and 1<=v[1]<=lengths[v[0]-1]) for v in holes):
        raise ValueError('invalid holes')
    return holes


def column(lengths, holes, v):
    """Coefficients of K=(1-z)F-2zS, for one occupied signed vertex."""
    i, d = v
    out = defaultdict(int)
    if i == 0:
        out[1] += 1
        for n in lengths:
            out[n+1] -= 1
    else:
        out[d+1] += 1
        out[lengths[i-1]+1-d] -= 1
        for j, n in enumerate(lengths, 1):
            if j != i:
                out[d+n+1] -= 1
    for j, h in holes:
        dist = abs(d-h) if i == j else d+h
        out[dist] -= 1
        out[dist+1] += 1
    return {e: c for e, c in out.items() if c}


def interval_plan(lengths, holes):
    """Full proximal interval left after upper-shell transfer."""
    A, B, C = lengths
    if not A > B > C:
        raise ValueError('require descending distinct arm lengths')
    delta = next(j for j in range(3) if (2, B-j) not in holes)
    m = A-B+delta
    if not (C > 2 and C > m and B-C-m-delta > m and B-m-delta > 2*m):
        raise ValueError('lengths do not satisfy the proved recovery separation bounds')
    return m, 1, m


def recovery_plan(lengths, holes):
    m, lo, hi = interval_plan(lengths, holes)
    C = lengths[2]
    # Exact diagonal coefficient test, not a floating-point rank estimate.
    clear = True
    for d in range(1, m+1):
        if (1, d) in holes:
            continue
        projected = {e-C-1: c for e, c in column(lengths, holes, (1,d)).items()
                     if C+2 <= e <= C+m+1}
        if projected != {d: -1}:
            clear = False
            break
    return (m, 1, m, 'clear-short-bin') if clear else (m, lo, hi, 'full-proximal')


def reduce_rows(rows):
    """Reversible singleton substitution, then exact sparse rational pivots.

    Returns a unique solution or raises for inconsistency/nonunique input.
    Rows are (coefficient dictionary, right hand side).
    """
    rows = [(dict(a), Fraction(b)) for a, b in rows]
    incidence = defaultdict(set)
    for k, (a, _) in enumerate(rows):
        for v in a:
            incidence[v].add(k)
    queue = deque(k for k, (a, _) in enumerate(rows) if len(a) == 1)
    solution = {}
    while queue:
        k = queue.popleft()
        a, b = rows[k]
        if len(a) != 1:
            continue
        v, c = next(iter(a.items()))
        value = b/c
        solution[v] = value
        for j in incidence[v]:
            aa, bb = rows[j]
            if v in aa:
                bb -= aa.pop(v)*value
                rows[j] = (aa, bb)
                if len(aa) == 1:
                    queue.append(j)
    peeled = len(solution)
    pivots = {}
    for a, b in rows:
        a = {v: Fraction(c) for v, c in a.items()}
        while a:
            v = min(a)
            if v not in pivots:
                c = a[v]
                pivots[v] = ({w: x/c for w, x in a.items()}, b/c)
                break
            aa, bb = pivots[v]
            c = a[v]
            b -= c*bb
            for w, x in aa.items():
                a[w] = a.get(w, 0)-c*x
                if not a[w]:
                    a.pop(w, None)
        if not a and b:
            raise ValueError('inconsistent shell equations')
    for v in sorted(pivots, reverse=True):
        a, b = pivots[v]
        if any(w != v and w not in solution for w in a):
            raise ValueError('nonunique recovery')
        solution[v] = b-sum(c*solution[w] for w, c in a.items() if w != v)
    if len(solution) != len(incidence):
        raise ValueError('nonunique recovery')
    return solution, peeled


def interval_rows(lengths, holes, lo, hi):
    rows = defaultdict(dict)
    for d in range(lo, hi+1):
        if (1, d) in holes:
            continue
        for e, c in column(lengths, holes, (1, d)).items():
            rows[e][d] = c
    # Include balance, though the interval injectivity proof does not need it.
    rows[-1] = {d: 1 for d in range(lo, hi+1) if (1,d) not in holes}
    return rows


def certificate(t, holes):
    if type(t) is not int or t < 1:
        raise ValueError('positive integer scale required')
    lengths = [99*t, 79*t, 23*t]
    holes = validate(lengths, holes)
    m, lo, hi, strategy = recovery_plan(lengths, holes)
    rows = interval_rows(lengths, holes, lo, hi)
    recovered, peeled = reduce_rows([(r, 0) for r in rows.values()])
    upper = sum((1, d) not in holes for d in range(m+1, lengths[0]+1))
    occupied = 1+sum(lengths)-len(holes)
    eliminated = upper+sum((1,d) not in holes for d in range(lo,hi+1))
    return dict(lengths=lengths, holes=sorted(holes), upper_forced=upper,
                proximal_limit=m, interval=[lo, hi], strategy=strategy, interval_rank=len(recovered),
                singleton_pivots=peeled, retained_sign_parameters=occupied-eliminated,
                eliminated_signs=eliminated, full_homometry_claimed=False,
                universal_milestone_decided=False)


def shorter_arm_obstruction(t, known):
    """First violated necessary ternary clause for holes (1,19),(1,99t)."""
    for r in range(23*t, 3*t+1, -1):
        forced = known[(2,56*t+r)]-known[(2,r)]-known[(3,r)]
        if forced not in (-1, 1):
            return {'first_arm_depth':20*t+r-1, 'forced_sign':forced,
                    'short_depth':r, 'long_second_depth':56*t+r,
                    'shell_rows':[99*t+r, 155*t+r]}
    return None


def prefix_obstruction(k):
    """Closed-form all-k certificate for the published earliest-negative words."""
    if type(k) is not int or k < 1:
        raise ValueError('positive integer k required')
    t = 2660*k+1
    # Depth 23t-4 has residue 19 and occurrence 23k+1 in arm two.
    negative_count = (79*k-(k % 2))//2
    occurrence = 23*k+1
    assert negative_count >= occurrence
    return dict(k=k, t=t, first_arm_depth=43*t-5, forced_sign=3,
                second_arm_tip_minus_four=1, second_arm_short_tip_minus_four=-1,
                third_arm_tip_minus_four=-1, inserted_negative_count=negative_count,
                inserted_occurrence=occurrence, all_first_arm_words_excluded=True,
                universal_milestone_decided=False)


def recover(lengths, holes, known):
    """Recover all omitted long-arm coordinates from retained literal signs.

    Exact rejection applies to this particular retained assignment, never to
    other assignments or hole sets. Final checks include every shell and balance.
    """
    holes = validate(lengths, holes)
    m, lo, hi, strategy = recovery_plan(lengths, holes)
    occupied = set(vertices(lengths))-holes
    unknown = {(1, d) for d in range(m+1, lengths[0]+1) if (1, d) not in holes}
    unknown.update((1, d) for d in range(lo, hi+1) if (1,d) not in holes)
    if set(known) != occupied-unknown or any(type(v) is not int or v not in (-1, 1) for v in known.values()):
        raise ValueError('retained coordinates/signs do not match the reduction')
    if lengths[0] % 99 == 0 and lengths[1]*99 == lengths[0]*79 and lengths[2]*99 == lengths[0]*23 and holes == {(1,19),(1,lengths[0])}:
        obstruction = shorter_arm_obstruction(lengths[0]//99, known)
        if obstruction:
            raise ValueError('two-shell obstruction: '+json.dumps(obstruction, sort_keys=True))
    residual = defaultdict(int)
    signs = dict(known)
    for v, sign in signs.items():
        for e, c in column(lengths, holes, v).items():
            residual[e] += c*sign
    delta = next(j for j in range(3) if (2, lengths[1]-j) not in holes)

    def assign(d, value, stage):
        if value not in (-1, 1):
            raise ValueError(f'{stage} forces {value} at first-arm depth {d}')
        signs[(1, d)] = int(value)
        for e, c in column(lengths, holes, (1,d)).items():
            residual[e] += c*value

    # The residual contains known and already recovered columns only.
    for d in range(lengths[0], m, -1):
        if (1, d) not in holes:
            e = lengths[1]-delta+1+d
            assign(d, residual[e], 'upper transfer')
    if strategy == 'clear-short-bin':
        for d in range(lo, hi+1):
            if (1,d) not in holes:
                assign(d, residual[lengths[2]+1+d], 'short band')
    else:
        rows = interval_rows(lengths, holes, lo, hi)
        rhs = {e: -value for e, value in residual.items()}
        rhs[-1] = -sum(signs.values())
        lower, _ = reduce_rows([(rows.get(e, {}), rhs.get(e, 0))
                               for e in rows.keys() | rhs.keys()])
        for d, value in lower.items():
            assign(d, value, 'interval recovery')
    if set(signs) != occupied or sum(signs.values()):
        raise ValueError('recovered assignment fails support or balance')
    if any(residual.values()):
        raise ValueError('recovered assignment fails an exact shell')
    return signs


def recover_payload(payload):
    lengths = payload['lengths']
    left, right = [list(map(tuple, payload[k])) for k in ('left', 'right')]
    if len(set(left)) != len(left) or len(set(right)) != len(right) or set(left) & set(right):
        raise ValueError('duplicate or overlapping vertices')
    allv = set(vertices(lengths))
    if not set(left+right) <= allv:
        raise ValueError('vertex outside tree')
    signs = {v: 1 for v in left} | {v: -1 for v in right}
    holes = allv-set(signs)
    m, lo, hi, strategy = recovery_plan(lengths, validate(lengths, holes))
    retained = {v: s for v, s in signs.items() if v[0] != 1 or v[1] <= m and not lo <= v[1] <= hi}
    result = recover(lengths, holes, retained)
    return result, result == signs


def complete_parameters(payload):
    lengths = payload['lengths']
    holes = validate(lengths, payload['holes'])
    centre = payload['centre']
    if type(centre) is not int or centre not in (-1,0,1):
        raise ValueError('centre must be -1, 0 or 1')
    known = {} if centre == 0 else {(0,0):centre}
    for i in (2,3):
        word = payload[f'arm{i}']
        if not isinstance(word,str) or len(word) != lengths[i-1] or set(word)-set('+-0'):
            raise ValueError('shorter arms must be literal + - 0 strings of the stated lengths')
        for d,ch in enumerate(word,1):
            if ch != '0':
                known[(i,d)] = 1 if ch == '+' else -1
    return recover(lengths,holes,known)


def radial_gcd_bound(lengths, holes, degree_limit=10000):
    """Independent sufficient injectivity certificate, valid beyond the cone.

    A modular gcd degree bounds the rational gcd degree from above. This
    diagnostic deliberately refuses large dense polynomial divisions; the
    geometric theorem has no scale cap and is the primary recovery method.
    """
    holes = validate(lengths,holes)
    ends = list(lengths)
    for i in range(3):
        while ends[i] and (i+1,ends[i]) in holes:
            ends[i] -= 1
    a,b = ends[0],max(ends[1:])
    N = a+b
    if not a:
        return dict(radial_degree=N, negative_extent=b, prime=1000003,
                    rational_gcd_degree_at_most=None, injectivity_proved=True,
                    reason='no occupied first-arm vertices', universal_milestone_decided=False)
    if N > degree_limit:
        raise ValueError('radial polynomial exceeds this diagnostic degree limit')
    coefficients = [0]*(N+1)
    for i,d in vertices(lengths):
        if (i,d) in holes:
            continue
        q = d if i==1 else -d
        coefficients[b+q] += 1
    # Fixed prime, with a direct primality check rather than an assumed field.
    prime = 1000003
    assert all(prime % d for d in range(2,1001))
    P = {i:c % prime for i,c in enumerate(coefficients) if c % prime}
    R = {N-i:c for i,c in P.items()}
    while R:
        degree = max(R)
        inv = pow(R[degree],-1,prime)
        while P and max(P)>=degree:
            shift = max(P)-degree
            c = P[shift+degree]*inv % prime
            for e,v in R.items():
                k=e+shift
                P[k]=(P.get(k,0)-c*v)%prime
                if not P[k]:
                    del P[k]
        P,R=R,P
    bound = max(P)
    return dict(radial_degree=N, negative_extent=b, prime=prime,
                rational_gcd_degree_at_most=bound,
                injectivity_proved=bound<=b, universal_milestone_decided=False)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument('--reduce', type=int, metavar='T')
    g.add_argument('--recover', type=Path, metavar='WITNESS')
    g.add_argument('--complete', type=Path, metavar='PARAMETERS')
    g.add_argument('--radial-bound', type=Path, metavar='GEOMETRY')
    g.add_argument('--prefix-obstruction', type=int, metavar='K')
    p.add_argument('--output', type=Path, help='write an accepted full witness with --complete or --recover')
    p.add_argument('--holes', type=json.loads, help='JSON coordinates; default long-arm depths 19 and 99t')
    args = p.parse_args()
    try:
        if args.output is not None and args.complete is None and args.recover is None:
            raise ValueError('--output requires --complete or --recover')
        if args.radial_bound is not None:
            geometry = json.loads(args.radial_bound.read_text())
            print(json.dumps(radial_gcd_bound(geometry['lengths'],geometry['holes']),sort_keys=True))
        elif args.prefix_obstruction is not None:
            print(json.dumps(prefix_obstruction(args.prefix_obstruction), sort_keys=True))
        elif args.reduce is not None:
            t = args.reduce
            print(json.dumps(certificate(t, args.holes if args.holes is not None else [(1,19),(1,99*t)]), sort_keys=True))
        else:
            payload = json.loads((args.complete or args.recover).read_text())
            if args.complete is not None:
                signs, same = complete_parameters(payload), True
            else:
                signs, same = recover_payload(payload)
            if not same:
                raise ValueError('input differs from its unique homometric completion')
            if args.output is not None:
                args.output.write_text(json.dumps(dict(lengths=payload['lengths'],
                    left=sorted(v for v,s in signs.items() if s==1),
                    right=sorted(v for v,s in signs.items() if s==-1)))+'\n')
            print(json.dumps(dict(recovered=len(signs), size=len(signs)//2, matches_input=same, full_homometry_verified=True), sort_keys=True))
    except (ValueError, KeyError) as exc:
        p.exit(1, str(exc)+'\n')


if __name__ == '__main__':
    main()
