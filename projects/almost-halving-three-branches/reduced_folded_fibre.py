"""A 290-sign stationary strip after exact opposite-tail elimination.

This compresses the fixed graph, not its accepted scale set. No resistant
scale is decided. Requires literal_fibre from the same source contribution.
"""
import argparse
from collections import defaultdict
import json
import random
import literal_fibre as full


def labels():
    return [(arm,q,s) for arm,n in enumerate((43,79,23),1)
            for s in (1,-1) for q in (range(n) if s == 1 else range(1,n+1))]


def column(arm,q,alpha,beta,shallow=False):
    """Formal reduced column at depth q*t+alpha*R+beta.

    The caller's interior/right ranges ensure R+delta>0. At the left
    boundary alpha=0 and the threshold is tested with beta exactly.
    """
    terms = full.affine_column(arm,q,alpha,beta,shallow)
    tail = arm == 2 and (q >= (23 if alpha > 0 else 24) if alpha else
                         (q > 23 or (q == 23 and beta >= 1)))
    if tail:
        # x_(d+20t-1)=-y_d; this source is always deeper than 19.
        terms += [(a,b,c,-coefficient) for a,b,c,coefficient in
                  full.affine_column(1,q+20,alpha,beta-1)]
    return terms


def trim(rows):
    return {row:{v:c for v,c in terms.items() if c}
            for row,terms in rows.items() if any(terms.values())}


def interior():
    rows = defaultdict(lambda:defaultdict(int))
    for arm,q,s in labels():
        for delta in range(-20,21):
            for quotient,tau,c,coefficient in column(arm,q,s,s*delta):
                if c == 0:
                    rows[quotient,tau][arm,q,s,delta] += coefficient
    return trim(rows)


def boundaries():
    left = defaultdict(lambda:defaultdict(int))
    right = defaultdict(lambda:defaultdict(int))
    sources = [(0,0,0)]
    for arm,n in enumerate((43,79,23),1):
        for delta in range(-40,41):
            for q in (range(1,n+1) if delta <= 0 else range(n)):
                if (arm,q,delta) not in ((1,0,19),(1,43,0)):
                    sources.append((arm,q,delta))
    for arm,q,delta in sources:
        shallow = arm == 1 and q == 0 and delta < 19
        for quotient,alpha,c,coefficient in column(arm,q,0,delta,shallow):
            assert alpha == 0
            if abs(c) <= 20:
                left[quotient,c][arm,q,delta] += coefficient
    for arm,q,s in labels():
        for j in range(-40,1):
            for quotient,tau,c,coefficient in column(arm,q,s,s*j):
                if tau == 1:
                    row = (quotient,1,c) if c <= 0 else (quotient+1,-1,1-c)
                else:
                    row = (quotient,-1,-c) if c >= 0 else (quotient-1,1,1+c)
                if -20 <= row[2] <= 0:
                    right[row][arm,q,s,j] += coefficient
    return trim(left),trim(right)


def residual(t,coordinates,stencil=None):
    full.geometry(t)
    if t < 163 or t%2 != 1:
        raise ValueError('require odd t>=163')
    half = t//2
    left,right = boundaries()
    stencil = interior() if stencil is None else stencil
    result = {}
    def put(e,value):
        if value:
            result[e] = value
    for (q,delta),terms in left.items():
        put(q*t+delta,sum(c*coordinates[arm,quotient*t+offset]
                          for (arm,quotient,offset),c in terms.items()))
    for r in range(21,half-20):
        for (q,s),terms in stencil.items():
            put(q*t+s*r,sum(c*coordinates[arm,quotient*t+orientation*(r+delta)]
                            for (arm,quotient,orientation,delta),c in terms.items()))
    for (q,s,j),terms in right.items():
        put(q*t+s*(half+j),sum(c*coordinates[arm,quotient*t+orientation*(half+offset)]
                               for (arm,quotient,orientation,offset),c in terms.items()))
    return result


def control(t):
    full.geometry(t)
    if t < 163 or t%2 != 1:
        raise ValueError('require odd t>=163')
    rng = random.Random(t)
    coordinates = {(0,0):1}
    coordinates.update({(a,d):rng.choice((-1,1)) for a,n in enumerate((43*t-1,79*t,23*t),1)
                        for d in range(1,n+1) if (a,d) != (1,19)})
    expanded = dict(coordinates)
    expanded.update({(1,d):-coordinates[2,d-20*t+1] for d in range(43*t,99*t)})
    lengths,holes = full.geometry(t)
    original = full.shell.shell_rows(lengths,holes,expanded)
    return coordinates,original


def audit(t):
    coordinates,expected = control(t)
    actual = residual(t,coordinates)
    if actual != expected:
        raise ValueError('reduced graph differs from the original shell coefficients')
    return dict(t=t,all_coefficients_reconstructed=True,
                reduced_unknowns=len(coordinates)-1,nonzero_rows=len(actual),
                homometry_claimed=False)


def theorem():
    return dict(slice_signs=len(labels()),stored_slices=40,stored_sign_bound=11600,
                interior_rows=len(interior()),row_radius=20,minimum_odd_scale=163,
                graph_states_at_most='2^11600',eventual_periodicity_proved=True,
                resistant_scales_decided=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audit',type=int)
    args = parser.parse_args()
    result = theorem()
    if args.audit is not None:
        result['control'] = audit(args.audit)
    print(json.dumps(result,sort_keys=True))


if __name__ == '__main__':
    main()
