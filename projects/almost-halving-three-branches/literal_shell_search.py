"""Bounded exact literal-sign search on all shell equations.

A search limit returns unknown. This is a finite computation, not an
all-scale obstruction. Uses the standard library and the exact shell column.
"""
import argparse
from collections import defaultdict
import json
import math
import time
import full_shorter_coupling as fc


class LiteralSearch:
    def __init__(self, size, rows, node_budget=100000, seconds=10, parity=False, extra_xor_rows=(), priority=()):
        if type(size) is not int or size < 1:
            raise ValueError('require a positive variable count')
        if type(node_budget) is not int or node_budget < 0:
            raise ValueError('require a nonnegative integer node budget')
        if type(seconds) not in (int,float) or not math.isfinite(seconds) or seconds <= 0:
            raise ValueError('require a positive finite search time')
        extra_xor_rows = list(extra_xor_rows)
        if any(type(mask) is not int or not 0<=mask<1<<size or
               type(rhs) is not int or rhs not in (0,1) or mask.bit_count()%2
               for mask,rhs in extra_xor_rows):
            raise ValueError('extra parity rows must preserve global complementation')
        rows = list(rows)
        self.priority = list(priority)
        if any(type(i) is not int or not 0<=i<size for i in self.priority):
            raise ValueError('invalid priority variable')
        self.tables = []
        self.links = [[] for _ in range(size)]
        for row in rows:
            if (len(row)>16 or any(type(i) is not int or not 0<=i<size or
                                  type(c) is not int or not c for i,c in row.items())):
                raise ValueError('require integer sparse rows of width at most16')
            ids,cs = list(row),list(row.values())
            patterns = [bits for bits in range(1<<len(ids))
                        if sum(c*(1 if bits>>j&1 else -1) for j,c in enumerate(cs))==0]
            masks = [sum(1<<p for p,bits in enumerate(patterns) if bits>>j&1)
                     for j in range(len(ids))]
            rid = len(self.tables)
            self.tables.append((ids,masks,(1<<len(patterns))-1))
            for j,i in enumerate(ids):
                self.links[i].append((rid,j))
        self.allowed = [full for ids,masks,full in self.tables]
        self.values = [0]*size
        self.trail = []
        self.nodes = 0
        self.node_budget = node_budget
        self.seconds = seconds
        self.assigned = self.positive = 0
        self.xor_rows = []
        self.xor_links = [[] for _ in range(size)]
        self.parity_impossible = False
        if parity:
            equations = [(sum(1<<i for i,c in row.items() if c%2),sum(row.values())//2%2)
                         for row in rows if sum(row.values())%2==0]
            equations.extend(extra_xor_rows)
            basis = {}
            for mask,rhs in equations:
                while mask:
                    pivot = mask.bit_length()-1
                    if pivot not in basis:
                        basis[pivot] = (mask,rhs)
                        break
                    old,b = basis[pivot]
                    mask,rhs = mask^old,rhs^b
                if not mask and rhs:
                    self.parity_impossible = True
            for pivot in sorted(basis):
                mask,rhs = basis[pivot]
                for other in basis:
                    if other>pivot and basis[other][0]>>pivot&1:
                        a,b = basis[other]
                        basis[other] = a^mask,b^rhs
            self.xor_rows = list(basis.values())
            for rid,(mask,rhs) in enumerate(self.xor_rows):
                for i in range(size):
                    if mask>>i&1:
                        self.xor_links[i].append(rid)

    def undo(self,mark):
        while len(self.trail)>mark:
            kind,i,old = self.trail.pop()
            (self.values if kind==0 else self.allowed)[i] = old
            if kind==0:
                self.assigned &= ~(1<<i)
                self.positive &= ~(1<<i)

    def propagate(self,queue):
        while queue:
            i,s = queue.pop()
            if self.values[i]:
                if self.values[i]!=s:
                    return False
                continue
            self.trail.append((0,i,0))
            self.values[i] = s
            self.assigned |= 1<<i
            if s==1:
                self.positive |= 1<<i
            for rid in self.xor_links[i]:
                mask,rhs = self.xor_rows[rid]
                unknown = mask & ~self.assigned
                required = rhs ^ ((mask & self.positive).bit_count()%2)
                if not unknown:
                    if required:
                        return False
                elif unknown & (unknown-1)==0:
                    queue.append((unknown.bit_length()-1,1 if required else -1))
            for rid,j in self.links[i]:
                ids,masks,full = self.tables[rid]
                old = self.allowed[rid]
                new = old & (masks[j] if s==1 else full^masks[j])
                if not new:
                    return False
                if new==old:
                    continue
                self.trail.append((1,rid,old))
                self.allowed[rid] = new
                for pos,k in enumerate(ids):
                    if not self.values[k]:
                        if not new & masks[pos]:
                            queue.append((k,-1))
                        elif not new & (full^masks[pos]):
                            queue.append((k,1))
        return True

    def choose(self):
        for i in self.priority:
            if not self.values[i]:
                return i
        eligible = [r for r,(ids,_,_) in enumerate(self.tables)
                    if any(not self.values[i] for i in ids)]
        if not eligible:
            return next(i for i,s in enumerate(self.values) if not s)
        rid = min(eligible,key=lambda r:self.allowed[r].bit_count())
        ids,_,_ = self.tables[rid]
        return max((i for i in ids if not self.values[i]),key=lambda i:len(self.links[i]))

    def run(self, seeds=None):
        """One use per instance; seeds map variable indices to literal signs."""
        seeds = {} if seeds is None else dict(seeds)
        if any(type(i) is not int or not 0<=i<len(self.values) or
               type(s) is not int or s not in (-1,1) for i,s in seeds.items()):
            raise ValueError('invalid seed variable or sign')
        deadline = time.monotonic()+self.seconds
        if self.parity_impossible or any(not a for a in self.allowed):
            return 'unsat',None
        # With no fixed data, global reversal makes fixing one sign complete.
        if not seeds:
            seeds = {0:1}
        if not self.propagate(list(seeds.items())):
            return 'unsat',None
        stack = []
        while True:
            if self.nodes>=self.node_budget or time.monotonic()>=deadline:
                return 'unknown',None
            self.nodes += 1
            if all(self.values):
                return 'sat',list(self.values)
            i = self.choose()
            stack.append([i,0,len(self.trail)])
            if self.propagate([(i,1)]):
                continue
            # Each frame records its plus and minus subtrees explicitly;
            # no recursion depth can silently truncate a proof of unsat.
            while stack:
                i,stage,mark = stack[-1]
                self.undo(mark)
                if stage==0:
                    stack[-1][1] = 1
                    if self.propagate([(i,-1)]):
                        break
                else:
                    stack.pop()
            else:
                return 'unsat',None


def shell_system(t,h):
    lengths,holes = fc.geometry(t,h)
    vertices = [(0,0)]+[(a,d) for a,n in enumerate(lengths,1) for d in range(1,n+1)]
    vertices = [v for v in vertices if v not in holes]
    if len(vertices)>5000:
        raise ValueError('boundary-scale search supports at most5000 occupied vertices')
    rows = defaultdict(dict)
    for i,v in enumerate(vertices):
        for e,c in fc.shell_column(lengths,holes,v).items():
            rows[e][i] = c
    return lengths,holes,vertices,[row for e,row in sorted(rows.items())]


def search(t,h,node_budget=100000,seconds=10,seeds=None,parity=False,third_first=False):
    start = time.monotonic()
    lengths,holes,vertices,rows = shell_system(t,h)
    if len(vertices)%2:
        return dict(t=t,h=h,status='unsat',nodes=0,occupied_vertices=len(vertices),
                    shell_equations=len(rows),proof='occupied vertex count is odd',
                    elapsed_seconds=round(time.monotonic()-start,6),universal_result=False)
    engine = LiteralSearch(len(vertices),rows,node_budget,seconds,parity,
                           ([((1<<len(vertices))-1,(len(vertices)//2)%2)] if len(vertices)%2==0 else []),
                           [i for i,v in enumerate(vertices) if v[0]==3] if third_first else [])
    index = {v:i for i,v in enumerate(vertices)}
    if seeds is not None and not set(seeds)<=set(index):
        raise ValueError('seed includes an omitted or out-of-range vertex')
    translated = None if seeds is None else {index[v]:s for v,s in seeds.items()}
    status,values = engine.run(translated)
    result = dict(t=t,h=h,status=status,nodes=engine.nodes,
                  occupied_vertices=len(vertices),shell_equations=len(rows),
                  search_node_budget=node_budget,search_seconds=seconds,
                  elapsed_seconds=round(time.monotonic()-start,6),
                  seeded_vertices=len(seeds or {}),third_first=third_first,
                  parity_propagation=parity,universal_result=False)
    if values is not None:
        signs = dict(zip(vertices,values))
        if sum(values) or fc.shell_rows(lengths,holes,signs):
            raise ArithmeticError('search candidate failed full balance/shell verification')
        result['left'] = [list(v) for v,s in signs.items() if s==1]
        result['right'] = [list(v) for v,s in signs.items() if s==-1]
    return result


def modular_rank(rows, columns):
    """Exact rank over F_101; a full-column result certifies rational injectivity."""
    columns = set(columns)
    basis = {}
    for source in rows:
        row = {i:c%101 for i,c in source.items() if i in columns and c%101}
        while row:
            pivot = max(row)
            if pivot not in basis:
                inverse = pow(row[pivot],-1,101)
                basis[pivot] = {i:c*inverse%101 for i,c in row.items()}
                break
            multiplier = row[pivot]
            for i,c in basis[pivot].items():
                updated = (row.get(i,0)-multiplier*c)%101
                if updated:
                    row[i] = updated
                else:
                    row.pop(i,None)
    return len(basis)


def two_arm_rank(t,h):
    """Condition on the entire third arm and centre; study two unknown arms."""
    start = time.monotonic()
    lengths,holes,vertices,rows = shell_system(t,h)
    columns = {i for i,v in enumerate(vertices) if v[0] in (1,2)}
    rank = modular_rank(rows,columns)
    return dict(t=t,h=h,field=101,unknown_two_arm_columns=len(columns),
                rank_modulo_field=rank,rational_nullity_at_most=len(columns)-rank,
                rational_injectivity_proved=rank==len(columns),
                elapsed_seconds=round(time.monotonic()-start,6),
                existence_decided=False,all_scale_result=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('t',type=int)
    parser.add_argument('h',type=int)
    parser.add_argument('--nodes',type=int,default=100000)
    parser.add_argument('--seconds',type=float,default=10)
    parser.add_argument('--parity',action='store_true',help='also propagate exact reduced parity equations')
    parser.add_argument('--arm2',help='fix a literal +/- second-arm word')
    parser.add_argument('--arm3',help='fix a literal +/- third-arm word')
    parser.add_argument('--centre',type=int,choices=(-1,1))
    parser.add_argument('--third-first',action='store_true',help='branch on unknown third-arm signs first')
    parser.add_argument('--two-arm-rank',action='store_true',
                        help='certify finite two-long-arm rank instead of searching signs')
    args = parser.parse_args()
    if args.two_arm_rank:
        print(json.dumps(two_arm_rank(args.t,args.h),sort_keys=True))
        return
    seeds = {}
    for arm,word,n in ((2,args.arm2,79*args.t),(3,args.arm3,23*args.t)):
        if word is not None:
            if len(word)!=n or set(word)-set('+-'):
                parser.error('fixed arm word must have its full length and only +/- signs')
            seeds.update({(arm,i):1 if c=='+' else -1 for i,c in enumerate(word,1)})
    if args.centre is not None:
        if args.h==0:
            parser.error('the centre is omitted when h=0')
        seeds[0,0] = args.centre
    print(json.dumps(search(args.t,args.h,args.nodes,args.seconds,seeds or None,args.parity,args.third_first),sort_keys=True))


if __name__ == '__main__':
    main()
