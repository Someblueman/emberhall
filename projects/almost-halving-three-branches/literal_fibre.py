"""Exact Boolean quotient of a rational tripod fibre, in every dimension.

No search limit is an obstruction. Certificates refer only to the supplied
retained data and fixed holes; third=None quantifies over every third word.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
from itertools import combinations
import json
import full_shorter_coupling as shell


def geometry(t):
    if type(t) is not int or t < 1:
        raise ValueError('require a positive integer scale')
    return [99*t, 79*t, 23*t], {(1, 19), (1, 99*t)}


def tail_theorem(t):
    """Constant-size description of a symbolic elimination, not a rank claim."""
    geometry(t)
    return dict(t=t,forced_pairs=56*t,first_tail=[43*t,99*t-1],
                second_tail=[23*t+1,79*t],second_depth_shift=1-20*t,
                largest_competing_distance=122*t-1,
                reduced_two_arm_unknowns=122*t-2,maximum_reduced_degree=122*t,
                all_scale=True,literal_existence_decided=False)


def folded_level(t, depth):
    residue = depth % t
    return min(residue,t-residue)


def slice_labels():
    """d=q*t+orientation*r at an interior folded level r: 402 labels."""
    return [(arm,q,orientation) for arm,n in enumerate((99,79,23),1)
            for orientation in (1,-1)
            for q in (range(n) if orientation == 1 else range(1,n+1))]


def interior_stencil():
    """Symbolic coefficient extraction at e=Q*t+tau*r, 20<r<t/2-20.

    Each term below is (Q,tau,coefficient,delta) after solving its constant
    offset for d=q*t+s*(r+delta). No sampled scale defines the stencil.
    """
    rows = defaultdict(lambda: defaultdict(int))
    for arm,q,s in slice_labels():
        if arm == 1:
            terms = [(q,s,1,-s),(79+q,s,-1,-s),(23+q,s,-1,-s),
                     (99-q,-s,-1,0),(q,s,-1,19*s),(q,s,1,18*s)]
        else:
            own,other = (79,23) if arm == 2 else (23,79)
            terms = [(q,s,1,-s),(own-q,-s,-1,s),(other+q,s,-1,-s),
                     (99+q,s,-1,0),(q,s,-1,-19*s),(q,s,1,-20*s)]
        for quotient,orientation,c,delta in terms:
            rows[quotient,orientation][arm,q,s,delta] += c
    return {row:{v:c for v,c in terms.items() if c}
            for row,terms in rows.items() if any(terms.values())}


def affine_column(arm, q, alpha, beta, shallow=False):
    """Formal exponents Q*t+tau*R+c for depth q*t+alpha*R+beta."""
    if arm == 0:
        return [(0,0,1,1),(99,0,0,-1),(79,0,1,-1),
                (23,0,1,-1),(0,0,19,-1),(0,0,20,1)]
    if arm == 1:
        hole = [(0,0,19-beta,-1),(0,0,20-beta,1)] if shallow else [
                (q,alpha,beta-19,-1),(q,alpha,beta-18,1)]
        return [(q,alpha,beta+1,1),(79+q,alpha,beta+1,-1),
                (23+q,alpha,beta+1,-1),(99-q,-alpha,-beta,-1)]+hole
    own,other = (79,23) if arm == 2 else (23,79)
    return [(q,alpha,beta+1,1),(own-q,-alpha,1-beta,-1),
            (other+q,alpha,beta+1,-1),(99+q,alpha,beta,-1),
            (q,alpha,beta+19,-1),(q,alpha,beta+20,1)]


def boundary_stencils():
    """Exact fixed left/right predicates for odd t=2*L+1 >=163.

    Left labels are depth q*t+delta, |delta|<=40, plus the centre.
    Right labels are q*t+s*(L+j), -40<=j<=0. No sample scale is used.
    """
    left = defaultdict(lambda:defaultdict(int))
    right = defaultdict(lambda:defaultdict(int))
    sources = [(0,0,0)]
    for arm,n in enumerate((99,79,23),1):
        for delta in range(-40,41):
            qs = range(1,n+1) if delta <= 0 else range(n)
            for q in qs:
                if (arm,q,delta) not in ((1,0,19),(1,99,0)):
                    sources.append((arm,q,delta))
    for arm,q,delta in sources:
        shallow = arm == 1 and q == 0 and delta < 19
        for quotient,alpha,c,coefficient in affine_column(arm,q,0,delta,shallow):
            assert alpha == 0
            if abs(c) <= 20:
                left[quotient,c][arm,q,delta] += coefficient
    for arm,q,s in slice_labels():
        for j in range(-40,1):
            for quotient,tau,c,coefficient in affine_column(arm,q,s,s*j):
                # Canonicalize around the odd half: t=2*L+1, exactly.
                if tau == 1:
                    row = (quotient,1,c) if c <= 0 else (quotient+1,-1,1-c)
                else:
                    row = (quotient,-1,-c) if c >= 0 else (quotient-1,1,1+c)
                if -20 <= row[2] <= 0:
                    right[row][arm,q,s,j] += coefficient
    def trim(rows):
        return {row:{v:c for v,c in terms.items() if c}
                for row,terms in rows.items() if any(terms.values())}
    return trim(left),trim(right)


def stencil_residual(slices):
    """An exact edge predicate for the fixed finite graph (41 packed slices).

    A bit is a sign 1-2*b. The centre of this window has folded level r;
    the next slice r+20 completes precisely these interior row equations.
    """
    labels = slice_labels()
    if len(slices) != 41 or any(type(bits) is not int or not 0 <= bits < 1 << len(labels) for bits in slices):
        raise ValueError('require 41 slices of 402 sign bits')
    index = {v:i for i,v in enumerate(labels)}
    result = {}
    for row,terms in interior_stencil().items():
        value = sum(c*(1-2*((slices[delta+20] >> index[arm,q,s]) & 1))
                    for (arm,q,s,delta),c in terms.items())
        if value:
            result[row] = value
    return result


def folded_theorem():
    return dict(slice_signs=402,row_level_radius=20,row_level_span=40,
                stored_slice_count=40,stored_sign_bound=16080,
                interior_rows=len(interior_stencil()),minimum_odd_scale=163,
                graph_edge_count_formula='(t-1)/2 - 41',
                graph_states_at_most='2^16080',
                eventual_periodicity_proved=True,
                resistant_scales_decided=False,
                scope='fixed holes 19 and 99t; centre positive; all third words free')


def folded_residual(t, signs):
    """Reassemble every K coefficient from the fixed graph and boundaries.

    This linear audit permits arbitrary rational values. Missing holes have
    no coordinate, including the unused ghost in the first graph state.
    """
    geometry(t)
    if t%2 != 1 or t < 163:
        raise ValueError('the fixed-boundary graph requires odd t>=163')
    half = t//2
    left,right = boundary_stencils()
    stencil = interior_stencil()
    residual = {}
    def record(e, value):
        if e in residual:
            raise AssertionError('overlapping row partition')
        if value:
            residual[e] = value
    for (q,delta),terms in left.items():
        record(q*t+delta,sum(c*signs[arm,quotient*t+offset]
                            for (arm,quotient,offset),c in terms.items()))
    for r in range(21,half-20):
        for (q,s),terms in stencil.items():
            record(q*t+s*r,sum(c*signs[arm,quotient*t+orientation*(r+delta)]
                               for (arm,quotient,orientation,delta),c in terms.items()))
    for (q,s,j),terms in right.items():
        record(q*t+s*(half+j),sum(c*signs[arm,quotient*t+orientation*(half+offset)]
                                  for (arm,quotient,orientation,offset),c in terms.items()))
    return residual


def validate_data(t, third, centre):
    lengths, holes = geometry(t)
    if type(centre) is not int or centre not in (-1, 1):
        raise ValueError('require a literal centre')
    if third is not None and (not isinstance(third, str) or
            len(third) != 23*t or set(third)-set('+-')):
        raise ValueError('require a literal third word, or null for all words')
    return lengths,holes


def system(t, third, centre):
    """Strip the forced opposite tails, retaining every remaining K row."""
    lengths,holes = validate_data(t,third,centre)
    vertices = [(1,d) for d in range(1,43*t) if d != 19]
    vertices += [(2,d) for d in range(1,79*t+1)]
    if third is None:
        vertices += [(3,d) for d in range(1,23*t+1)]
    position = {v:i for i,v in enumerate(vertices)}
    rows = defaultdict(lambda: defaultdict(int))
    rhs = defaultdict(int)
    retained = {(0,0):centre}
    if third is not None:
        retained.update({(3,d):1 if s == '+' else -1
                         for d,s in enumerate(third,1)})
    for arm,n in enumerate(lengths,1):
        for d in range(1,n+1):
            v = (arm,d)
            if v in holes:
                continue
            column = shell.shell_column(lengths,holes,v)
            if v in retained:
                for e,c in column.items():
                    rhs[e] -= c*retained[v]
            else:
                source, factor = ((2,d-20*t+1),-1) if arm == 1 and d >= 43*t else (v,1)
                for e,c in column.items():
                    rows[e][position[source]] += factor*c
    for e,c in shell.shell_column(lengths,holes,(0,0)).items():
        rhs[e] -= c*centre
    equations = []
    for e in sorted(rows.keys() | rhs.keys()):
        row = {i:c for i,c in rows[e].items() if c}
        if e > 122*t and (row or rhs[e]):
            raise AssertionError('opposite-tail cancellation failed')
        if row or rhs[e]:
            equations.append((e,row,rhs[e]))
    return vertices, equations, retained


def rational_fibre(size, equations):
    """Echelon elimination, with an independently replayable linear refusal."""
    pivots = {}
    for label, coefficients, target in equations:
        row, rhs, trace = {i:Q(c) for i,c in coefficients.items()}, Q(target), {label:Q(1)}
        for pivot,(old,b,history) in sorted(pivots.items()):
            factor = row.get(pivot,0)
            if not factor:
                continue
            for i,c in old.items():
                row[i] = row.get(i,0)-factor*c
                if not row[i]:
                    del row[i]
            rhs -= factor*b
            for e,c in history.items():
                trace[e] = trace.get(e,0)-factor*c
                if not trace[e]:
                    del trace[e]
        if not row:
            if rhs:
                return dict(compatible=False, contradiction={e:c/rhs for e,c in trace.items()})
            continue
        pivot = min(row)
        divisor = row[pivot]
        pivots[pivot] = ({i:c/divisor for i,c in row.items()}, rhs/divisor,
                         {e:c/divisor for e,c in trace.items()})
    free = sorted(set(range(size))-pivots.keys())
    def recover(seed, homogeneous=False):
        values = dict(zip(free,seed))
        for pivot,(row,rhs,_) in sorted(pivots.items(),reverse=True):
            values[pivot] = (0 if homogeneous else rhs)-sum(c*values[i] for i,c in row.items() if i != pivot)
        return [Q(values[i]) for i in range(size)]
    p = recover([0]*len(free))
    basis = [recover([int(i == j) for i in range(len(free))],True) for j in range(len(free))]
    # Free coordinates themselves are original literal coordinates. No matrix
    # inversion or primitive-basis normalization changes their +/- domain.
    return dict(compatible=True,particular=p,basis=basis,free=free)


def clean(poly):
    return {i:Q(c) for i,c in poly.items() if c}


def add(left, right):
    out = dict(left)
    for i,c in right.items():
        out[i] = out.get(i,0)+c
    return clean(out)


def multiply(left, right):
    """Q[z]/(z_j^2-1): squarefree monomials multiply by XOR."""
    out = defaultdict(Q)
    for a,c in left.items():
        for b,d in right.items():
            out[a ^ b] += c*d
    return clean(out)


def constraints(fibre):
    p,basis = fibre['particular'],fibre['basis']
    result = []
    for i,c in enumerate(p):
        linear = clean({0:c} | {1 << j:column[i] for j,column in enumerate(basis)})
        result.append(add(multiply(linear,linear),{0:-1}))
    return result


def value(poly, bits):
    return sum(c*(-1 if (mask & bits).bit_count()%2 else 1) for mask,c in poly.items())


def inverse_on_cube(poly, dimension):
    """Return its exact inverse, or a zero of poly. Exponential, explicit."""
    values = [value(poly,bits) for bits in range(1 << dimension)]
    if 0 in values:
        return None, values.index(0)
    coefficients = [1/c for c in values]
    width = 1
    while width < len(coefficients):
        for start in range(0,len(coefficients),2*width):
            for j in range(start,start+width):
                a,b = coefficients[j],coefficients[j+width]
                coefficients[j],coefficients[j+width] = a+b,a-b
        width *= 2
    return clean({i:c/len(coefficients) for i,c in enumerate(coefficients)}), None


def encode(poly):
    return [[i,str(c)] for i,c in sorted(poly.items())]


def decode(data, dimension):
    if not isinstance(data,list):
        raise ValueError('require a coefficient list')
    result = {}
    for item in data:
        if not isinstance(item,list) or len(item) != 2:
            raise ValueError('invalid coefficient')
        i,c = item
        if type(i) is not int or not 0 <= i < 1 << dimension or i in result:
            raise ValueError('invalid or repeated monomial')
        result[i] = Q(c)
    return clean(result)


def verify_pair(t, signs):
    lengths,holes = geometry(t)
    expected = {(0,0)} | {(a,d) for a,n in enumerate(lengths,1) for d in range(1,n+1)}
    if any(type(a) is not int or type(d) is not int for a,d in signs):
        raise ValueError('invalid vertex coordinates')
    if set(signs) != expected-holes or any(type(s) not in (int,Q) or s not in (-1,1) for s in signs.values()):
        raise ValueError('incorrect literal coverage')
    groups = [[v for v,s in signs.items() if s == colour] for colour in (-1,1)]
    def distances(group):
        return Counter(abs(d-e) if a == b else d+e for (a,d),(b,e) in combinations(group,2))
    if len(groups[0]) != len(groups[1]) or distances(groups[0]) != distances(groups[1]):
        raise ValueError('unequal sizes or distance multiplicities')
    return len(groups[0])


def prepare(payload):
    if not isinstance(payload,dict) or set(payload) != {'t','third','centre'}:
        raise ValueError('require exactly t, third and centre')
    vertices,rows,retained = system(**payload)
    fibre = rational_fibre(len(vertices),rows)
    return vertices,rows,retained,fibre


def solve(payload, max_dimension=8, max_unknowns=2000):
    if type(max_dimension) is not int or max_dimension < 0:
        raise ValueError('require a nonnegative dimension budget')
    if type(max_unknowns) is not int or max_unknowns < 0:
        raise ValueError('require a nonnegative matrix budget')
    if not isinstance(payload,dict) or set(payload) != {'t','third','centre'}:
        raise ValueError('require exactly t, third and centre')
    validate_data(**payload)
    count = (145 if payload['third'] is None else 122)*payload['t']-2
    if count > max_unknowns:
        return dict(input=payload,status='resource_limit',stage='matrix',
                    reduced_unknowns=count,existence_decided=False,
                    all_holes_decided=False,all_third_words=payload['third'] is None)
    vertices,rows,retained,fibre = prepare(payload)
    base = dict(input=payload, all_holes_decided=False,
                all_third_words=payload['third'] is None,
                reduced_unknowns=len(vertices), reduced_rows=len(rows))
    if not fibre['compatible']:
        return base | dict(status='unsat',kind='linear',certificate=encode(fibre['contradiction']))
    k = len(fibre['free'])
    base['dimension'] = k
    if k > max_dimension:
        return base | dict(status='resource_limit',existence_decided=False)
    polynomials = constraints(fibre)
    energy = {}
    for f in polynomials:
        energy = add(energy,multiply(f,f))
    inverse,bits = inverse_on_cube(energy,k)
    if inverse is not None:
        return base | dict(status='unsat',kind='boolean',certificate=encode(inverse))
    coordinates = [c+sum(column[i]*(-1 if bits >> j & 1 else 1)
                          for j,column in enumerate(fibre['basis']))
                   for i,c in enumerate(fibre['particular'])]
    signs = retained | dict(zip(vertices,coordinates))
    t = payload['t']
    signs.update({(1,d):-signs[2,d-20*t+1] for d in range(43*t,99*t)})
    size = verify_pair(t,signs)
    return base | dict(status='found',bits=bits,size=size,
                       signing=[[a,d,int(s)] for (a,d),s in sorted(signs.items())])


def verify(saved):
    """Do not trust saved status, dimension, counts, or a claimed inverse."""
    vertices,rows,retained,fibre = prepare(saved['input'])
    if saved.get('status') == 'found':
        raw = saved['signing']
        signs = {(a,d):s for a,d,s in raw}
        if len(signs) != len(raw) or any(signs.get(v) != s for v,s in retained.items()):
            raise ValueError('duplicate vertex or changed retained data')
        return dict(verified=True,size=verify_pair(saved['input']['t'],signs))
    if saved.get('status') != 'unsat':
        raise ValueError('no conclusive certificate')
    if saved.get('kind') == 'linear':
        # Labels are shell exponents, not Boolean monomial indices.
        certificate = decode(saved['certificate'],(178*saved['input']['t']).bit_length())
        by_label = {e:(row,rhs) for e,row,rhs in rows}
        combined = defaultdict(Q)
        target = Q(0)
        for e,c in certificate.items():
            if e not in by_label:
                raise ValueError('unknown equation label')
            row,rhs = by_label[e]
            target += c*rhs
            for i,a in row.items():
                combined[i] += c*a
        if any(combined.values()) or target != 1:
            raise ValueError('invalid linear contradiction')
    elif saved.get('kind') == 'boolean' and fibre['compatible']:
        k = len(fibre['free'])
        inverse = decode(saved['certificate'],k)
        energy = {}
        for f in constraints(fibre):
            energy = add(energy,multiply(f,f))
        if multiply(energy,inverse) != {0:Q(1)}:
            raise ValueError('invalid Boolean inverse')
    else:
        raise ValueError('certificate kind does not match fibre')
    return dict(verified=True,fixed_support_only=True,
                all_third_words=saved['input']['third'] is None)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',nargs='?')
    parser.add_argument('--verify')
    parser.add_argument('--example',action='store_true')
    parser.add_argument('--tail-scale',type=int)
    parser.add_argument('--folded-theorem',action='store_true')
    parser.add_argument('--max-dimension',type=int,default=8)
    parser.add_argument('--max-unknowns',type=int,default=2000)
    parser.add_argument('--write')
    args = parser.parse_args()
    if args.folded_theorem:
        result = folded_theorem()
    elif args.tail_scale is not None:
        result = tail_theorem(args.tail_scale)
    elif args.verify:
        with open(args.verify) as handle:
            result = verify(json.load(handle))
    else:
        if args.example:
            from gap_99_79_23 import witness
            pair = witness(1)
            signs = {tuple(v):s for key,s in [('left',1),('right',-1)] for v in pair[key]}
            payload = dict(t=1,centre=signs[0,0],third=''.join('+' if signs[3,d] == 1 else '-' for d in range(1,24)))
        else:
            with open(args.input) as handle:
                payload = json.load(handle)
        result = solve(payload,args.max_dimension,args.max_unknowns)
    if args.write:
        with open(args.write,'w') as handle:
            json.dump(result,handle,sort_keys=True)
            handle.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('signing','certificate')},sort_keys=True))


if __name__ == '__main__':
    main()
