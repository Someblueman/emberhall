"""Search periodic folded interiors with independently free endpoint patches.

A failed search is unknown; even an exhaustive refusal excludes only this
ansatz on the fixed holes (1,19),(1,99t). It never excludes arbitrary pairs.
"""
import argparse
from collections import defaultdict
from fractions import Fraction
import json
import heapq
import math
import time
import reduced_folded_fibre as rf
from literal_shell_search import LiteralSearch


def moving_periodic_system(period):
    """Formal (1-z**period)*K for t=period*k+1; holes 19t and 99t.

    A variable (arm,edge,r), 1<=r<=period, repeats at depths
    edge*t+r+j*period, 0<=j<k. r=0 denotes an old vertex at edge*t.
    Rows are coefficients of Z**q*z**c before substituting Z=z**t.
    Thus formal solutions work for every k>=1. For t>period+1 the
    exponents 0<=c<=period+1 do not collide, so the converse holds too.
    """
    if type(period) is not int or period<1: raise ValueError('require a positive period')
    lengths = (99,79,23)
    keys,rows = [],defaultdict(lambda:defaultdict(int))
    def add(key,terms,coarse=False):
        i = len(keys)
        keys.append(key)
        for q,c,value in terms:
            rows[q,c][i] += value
            if coarse: rows[q,c+period][i] -= value
    centre = [(0,1,1)]+[(n,1,-1) for n in lengths]
    for h in (19,99): centre.extend(((h,0,-1),(h,1,1)))
    add((0,0,0),centre,True)
    for arm,n in enumerate(lengths,1):
        for d in range(1,n+1):
            if arm==1 and d in (19,99): continue
            terms = [(d,1,1),(n-d,1,-1)]
            terms.extend((other+d,1,-1) for j,other in enumerate(lengths,1) if j!=arm)
            for h in (19,99):
                distance = abs(d-h) if arm==1 else d+h
                terms.extend(((distance,0,-1),(distance,1,1)))
            add((arm,d,0),terms,True)
        for edge in range(n):
            for r in range(1,period+1):
                pos = [(0,r,1),(1,r-1,-1)]
                neg = [(-1,period+1-r,1),(0,period-r,-1)]
                terms = []
                def shifted(source,q,c,value):
                    terms.extend((a+q,b+c,s*value) for a,b,s in source)
                shifted(pos,edge,1,1)
                shifted(neg,n-edge,1,-1)
                for j,other in enumerate(lengths,1):
                    if j!=arm: shifted(pos,other+edge,1,-1)
                for h in (19,99):
                    source = neg if arm==1 and edge<h else pos
                    distance = abs(edge-h) if arm==1 else edge+h
                    shifted(source,distance,0,-1)
                    shifted(source,distance,1,1)
                add((arm,edge,r),terms)
    return keys,{e:{i:c for i,c in row.items() if c}
                 for e,row in rows.items() if any(row.values())}


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


def joint_sign_closure(size,original,seconds=30,steps=20):
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
        relations = ternary_copy_relations(modular['kernel'])
        quotient = sign_relation_quotient(size,rows,relations)
        if quotient['conflict']: return result(True,True,stage='ternary_nonzero')
        history.append(dict(step=step+1,variables_before=before,
                            rational_nullity=before-rational['rank'],
                            binary_variables=binary['size'],binary_free=binary['free'],
                            ternary_nullity=modular['nullity'],ternary_relations=len(relations),
                            variables_after=quotient['size']))
        lift = quotient['aliases']
        aliases = [(lift[i][0],s*lift[i][1]) for i,s in aliases]
        size,rows = quotient['size'],quotient['rows']
        if size==before: return result(True,stop='no_more_signed_merges')
    return result(False,stage='step_limit')


def moving_search(period,seconds=30,nodes=10000,free_order='connected',closure_steps=20,rational=False,affine_shells=False,square_lift=False,joint_fields=False,reduced_xor=False):
    """Search one explicit all-scale moving-hole word ansatz, never all pairs."""
    if (type(seconds) not in (int,float) or not math.isfinite(seconds) or seconds<=0
            or type(nodes) is not int or nodes<0 or type(closure_steps) is not int or closure_steps<0):
        raise ValueError('require positive finite time and nonnegative node/closure budgets')
    start = time.monotonic()
    keys,formal = moving_periodic_system(period)
    original = list(formal.values())
    rows,size = original,len(keys)
    aliases,history = [(i,1) for i in range(size)],[]
    result = dict(mode='moving',period=period,all_pairs_decided=False,
                  scope='holes 19t and 99t; each edge repeats one period; t=period*k+1')
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
        joint = joint_sign_closure(size,rows,remaining)
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
    if saved.get('mode')=='moving':
        if saved['status']!='sat': raise ValueError('no saved moving sign witness')
        keys,formal = moving_periodic_system(saved['period'])
        supplied = saved['assignment']
        assignment = {tuple(k):v for k,v in supplied}
        if len(assignment)!=len(supplied) or set(assignment)!=set(keys):
            raise ValueError('require each moving coordinate exactly once')
        values = [assignment[k] for k in keys]
        if any(type(v) is not int or v not in (-1,1) for v in values):
            raise ValueError('require literal signs')
        if values[0]!=1 or any(sum(c*values[i] for i,c in row.items()) for row in formal.values()):
            raise ValueError('moving formal shell equation fails')
        return dict(verified=True,claim='formal moving-hole construction for t=period*k+1, k>=1',
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
    p.add_argument('--reduced-xor',action='store_true',help='fully reduce moving-word binary equations before branching')
    p.add_argument('--joint-fields',action='store_true',help='alternate rational, binary and ternary sign quotients')
    p.add_argument('--square-lift',action='store_true',help='derive moving-word constraints from sign squares')
    p.add_argument('--affine-shells',action='store_true',help='derive binary equations from exact local sign patterns')
    p.add_argument('--rational',action='store_true',help='augment moving search with exact recovery equations')
    p.add_argument('--parity-quotient',action='store_true',help='merge parity-forced signs before ternary analysis')
    args = p.parse_args()
    if (args.joint_fields or args.square_lift or args.rational or args.reduced_xor) and not args.moving:
        p.error('--joint-fields, --square-lift, --reduced-xor and --rational require --moving')
    if args.moving:
        result = moving_search(args.period,args.seconds,args.nodes,args.free_order,rational=args.rational,affine_shells=args.affine_shells,square_lift=args.square_lift,joint_fields=args.joint_fields,reduced_xor=args.reduced_xor)
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
