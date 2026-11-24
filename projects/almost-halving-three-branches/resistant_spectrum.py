"""Search periodic folded interiors with independently free endpoint patches.

A failed search is unknown; even an exhaustive refusal excludes only this
ansatz on the fixed holes (1,19),(1,99t). It never excludes arbitrary pairs.
"""
import argparse
from collections import defaultdict
import json
import reduced_folded_fibre as rf
from literal_shell_search import LiteralSearch


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


def parity_refusal(rows):
    return binary_elimination(rows)[0]


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


def make_engine(size,rows,basis,seconds,nodes,free_order='natural'):
    # Truth tables depend on coefficient words, not variable names. The strip
    # repeats a few such words thousands of times; construct each table once.
    engine = LiteralSearch(size,[],node_budget=nodes,seconds=seconds)
    cache = {}
    for row in rows:
        ids,coefficients = list(row),tuple(row.values())
        if any(type(i) is not int or not 0<=i<size for i in ids):
            raise ValueError('invalid variable index')
        if coefficients not in cache:
            prototype = LiteralSearch(len(ids) or 1,[dict(enumerate(coefficients))],
                                      node_budget=nodes,seconds=seconds)
            _,masks,full = prototype.tables[0]
            cache[coefficients] = masks,full
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
        (lambda i:(-len(engine.links[i])-len(engine.xor_links[i]),i))
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
    args = p.parse_args()
    if args.verify:
        with open(args.verify) as f: print(json.dumps(verify_saved(json.load(f)),sort_keys=True))
        return
    result = search(args.half,args.period,args.seconds,args.nodes,args.patch_width,args.free_order)
    if args.write:
        with open(args.write,'w') as f: json.dump(result,f)
    print(json.dumps({**{k:v for k,v in result.items() if k not in ('assignment','certificate')},
                      'certificate_rows':len(result.get('certificate',[]))},sort_keys=True))


if __name__ == '__main__': main()
