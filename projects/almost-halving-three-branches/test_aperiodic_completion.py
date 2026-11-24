import copy
import itertools
import random
import unittest
from collections import Counter, defaultdict, deque
import aperiodic_completion as ac
from gap_99_79_23 import witness


def bfs_shells(lengths, signs):
    """Independent adjacency BFS: no depth distance or polynomial helpers."""
    adj = defaultdict(list)
    for i, n in enumerate(lengths, 1):
        prev = (0, 0)
        for d in range(1, n+1):
            v = (i, d)
            adj[v].append(prev)
            adj[prev].append(v)
            prev = v
    f = Counter()
    pair = {1: Counter(), -1: Counter()}
    for u, s in signs.items():
        dist = {u: 0}
        q = deque([u])
        while q:
            v = q.popleft()
            for w in adj[v]:
                if w not in dist:
                    dist[w] = dist[v]+1
                    q.append(w)
        for v, sign in signs.items():
            if u != v:
                f[dist[v]] += s
                if u < v and sign == s and s in pair:
                    pair[s][dist[v]] += 1
    return f, pair


class CompletionTests(unittest.TestCase):
    def test_exact_shell_identity_with_every_hole_type(self):
        rng = random.Random(481)
        lengths = [8, 5, 3]
        verts = list(ac.vertices(lengths))
        for holes in [set()] + [{v} for v in verts] + [set(rng.sample(verts, 2)) for _ in range(60)]:
            signs = {v: rng.choice([-1, 1]) for v in verts if v not in holes}
            f, _ = bfs_shells(lengths, signs)
            lhs = defaultdict(int)
            rhs = defaultdict(int)
            for d, c in f.items():
                lhs[d] += c
                lhs[d+1] -= c
            rhs[1] = 2*sum(signs.values())
            for v, s in signs.items():
                for e, c in ac.column(lengths, holes, v).items():
                    rhs[e] += s*c
            self.assertEqual({e:c for e,c in lhs.items() if c}, {e:c for e,c in rhs.items() if c})

    def test_bfs_reconstruction_and_altered_pair_rejection(self):
        for t in [1, 3, 7]:
            payload = witness(t)
            signs, same = ac.recover_payload(payload)
            self.assertTrue(same)
            self.assertEqual(sum(signs.values()), 0)
            _, pair = bfs_shells(payload['lengths'], signs)
            self.assertEqual(pair[1], pair[-1])
            self.assertEqual(len(payload['left']), len(payload['right']))
            self.assertFalse(set(map(tuple, payload['left'])) & set(map(tuple, payload['right'])))
        payload = witness(1)
        changed = copy.deepcopy(payload)
        changed['left'][0], changed['right'][1] = changed['right'][1], changed['left'][0]
        altered = {tuple(v): s for k,s in [('left',1),('right',-1)] for v in changed[k]}
        _, pair = bfs_shells(changed['lengths'], altered)
        self.assertNotEqual(pair[1], pair[-1])
        try:
            recovered, same = ac.recover_payload(changed)
            self.assertFalse(same)
        except ValueError:
            pass

    def test_arbitrary_holes_rank_certificates(self):
        rng = random.Random(15)
        for t in [1, 2, 3, 7]:
            verts = list(ac.vertices([99*t,79*t,23*t]))
            samples = [[], [(0,0)], [(1,1),(1,2)], [(2,79*t),(3,23*t)], [(1,18),(1,99*t-1)]]
            samples += [rng.sample(verts, 2) for _ in range(40)]
            for holes in samples:
                c = ac.certificate(t, holes)
                self.assertEqual(c['interval_rank'], sum((1,d) not in set(map(tuple, holes)) for d in range(c['interval'][0],c['interval'][1]+1)))
                self.assertEqual(c['retained_sign_parameters'], 102*t+1-sum(i != 1 for i,d in set(map(tuple,holes))))
                self.assertFalse(c['universal_milestone_decided'])

    def test_first_open_scale_exact_rank(self):
        c = ac.certificate(2661, [(1,19),(1,99*2661)])
        self.assertEqual(c['interval'], [1,53220])
        self.assertEqual(c['interval_rank'], 53219)
        self.assertEqual(c['singleton_pivots'], 53219)
        self.assertEqual(c['retained_sign_parameters'], 271423)

    def test_fractional_pivots_and_inconsistency(self):
        result, peeled = ac.reduce_rows([({1:2,2:1},3), ({1:1,2:2},3)])
        self.assertEqual(result, {1:1,2:1})
        self.assertEqual(peeled, 0)
        with self.assertRaises(ValueError):
            ac.reduce_rows([({1:1},1),({1:1},-1)])
        with self.assertRaises(ValueError):
            ac.reduce_rows([({1:1,2:1},0)])

    def test_two_shell_linear_certificate(self):
        # Audit every vertex column, not merely a chosen signing.
        for t in [1,2,3]:
            lengths = [99*t,79*t,23*t]
            holes = {(1,19),(1,99*t)}
            for r in [3*t+2, 13*t, 23*t]:
                got = {}
                e, f = 99*t+r, 155*t+r
                for v in ac.vertices(lengths):
                    if v in holes:
                        continue
                    col = ac.column(lengths,holes,v)
                    c = col.get(e,0)-col.get(f,0)
                    if c:
                        got[v] = c
                self.assertEqual(got, {(1,20*t+r-1):-1,
                    (2,56*t+r):1,(2,r):-1,(3,r):-1})
        allowed = sum(y-x-w in (-1,1) for y,x,w in itertools.product([-1,1],repeat=3))
        self.assertEqual(allowed,6)

    def test_all_k_prefix_obstruction(self):
        from residue_2660 import FRONTIER
        self.assertEqual(FRONTIER[1][74], '+')
        self.assertEqual(FRONTIER[2][18], '-')
        for k in [1,2,3,10,10**12]:
            c = ac.prefix_obstruction(k)
            self.assertGreaterEqual(c['inserted_negative_count'], c['inserted_occurrence'])
            self.assertEqual(c['forced_sign'],3)
            self.assertFalse(c['universal_milestone_decided'])
        # Independently construct the existing words for a real first-open-scale rejection.
        from unrestricted_insertion_lift import prefix_realization
        words = prefix_realization(1)
        t = 2661
        known = {(0,0):-1}
        for i in [2,3]:
            known.update({(i,d):s for d,s in enumerate(words[i-1],1)})
        found = ac.shorter_arm_obstruction(t,known)
        self.assertEqual(found['first_arm_depth'],43*t-5)
        self.assertEqual(found['forced_sign'],3)
        with self.assertRaisesRegex(ValueError,'two-shell obstruction'):
            ac.recover([99*t,79*t,23*t],[(1,19),(1,99*t)],known)

    def test_fresh_unequal_triples_in_recovery_cone(self):
        from fixed_difference_family import construct
        for c in [25,29,43]:
            payload = construct(c)
            recovered, same = ac.recover_payload(payload)
            self.assertTrue(same)
            _, pair = bfs_shells(payload['lengths'],recovered)
            self.assertEqual(pair[1],pair[-1])
        rng = random.Random(75)
        for lengths in [[101,81,25],[105,85,29],[119,99,43],[40,34,12]]:
            verts = list(ac.vertices(lengths))
            for _ in range(12):
                holes = set(rng.sample(verts,2))
                m,lo,hi = ac.interval_plan(lengths,holes)
                rows = ac.interval_rows(lengths,holes,lo,hi)
                result,_ = ac.reduce_rows([(r,0) for r in rows.values()])
                self.assertEqual(len(result),m-sum(i==1 and d<=m for i,d in holes))
        with self.assertRaises(ValueError):
            ac.interval_plan([100,50,20],set())

    def test_independent_bfs_rank_for_every_small_tree_hole_set(self):
        # Full shell matrix, independently built by BFS, and independent modular
        # elimination. Full rank modulo a prime proves rational column rank.
        lengths = [17,16,6]
        adj = defaultdict(list)
        for i,n in enumerate(lengths,1):
            prev = (0,0)
            for d in range(1,n+1):
                v = (i,d)
                adj[prev].append(v)
                adj[v].append(prev)
                prev = v
        verts = sorted(adj)
        distances = {}
        for u in verts:
            dist = {u:0}
            queue = deque([u])
            while queue:
                v = queue.popleft()
                for w in adj[v]:
                    if w not in dist:
                        dist[w] = dist[v]+1
                        queue.append(w)
            distances[u] = dist
        prime = 1000003
        cases = [()] + [(v,) for v in verts] + list(itertools.combinations(verts,2))
        self.assertEqual(len(cases),821)
        for holes in cases:
            occupied = set(verts)-set(holes)
            unknown = sorted(v for v in occupied if v[0]==1)
            columns = []
            for u in unknown:
                counts = Counter(distances[u][v] for v in occupied if v != u)
                columns.append([1]+[counts[d] for d in range(1,34)])
            matrix = [list(row) for row in zip(*columns)]
            rank = 0
            for j in range(len(unknown)):
                pivot = next((i for i in range(rank,len(matrix)) if matrix[i][j] % prime),None)
                self.assertIsNotNone(pivot,holes)
                matrix[rank],matrix[pivot] = matrix[pivot],matrix[rank]
                inv = pow(matrix[rank][j],-1,prime)
                matrix[rank] = [x*inv % prime for x in matrix[rank]]
                for i in range(rank+1,len(matrix)):
                    c = matrix[i][j] % prime
                    if c:
                        matrix[i] = [(x-c*y)%prime for x,y in zip(matrix[i],matrix[rank])]
                rank += 1
            self.assertEqual(rank,len(unknown))
        payload = __import__('published_cases').witness(lengths)
        recovered,same = ac.recover_payload(payload)
        self.assertTrue(same)
        _,pair = bfs_shells(lengths,recovered)
        self.assertEqual(pair[1],pair[-1])

    def test_parameter_only_completion(self):
        p = witness(3)
        original = {tuple(v):s for key,s in [('left',1),('right',-1)] for v in p[key]}
        L = p['lengths']
        holes = sorted(set(ac.vertices(L))-original.keys())
        params = dict(lengths=L, holes=holes, centre=original.get((0,0),0))
        for i in [2,3]:
            params[f'arm{i}'] = ''.join({-1:'-',0:'0',1:'+'}[original.get((i,d),0)] for d in range(1,L[i-1]+1))
        got = ac.complete_parameters(params)
        self.assertEqual(got, original)
        _, pair = bfs_shells(L,got)
        self.assertEqual(pair[1],pair[-1])
        params['arm2'] = params['arm2'][:-1]+'?'
        with self.assertRaises(ValueError):
            ac.complete_parameters(params)

    def test_global_radial_gcd_bound_and_path_control(self):
        for L,H in [([99,79,23],[(1,19),(1,99)]),
                    ([9,7,3],[]),([12,8,3],[(2,2),(3,1)])]:
            receipt = ac.radial_gcd_bound(L,H)
            self.assertTrue(receipt['injectivity_proved'])
            # Independently audit full shell column rank by exact elimination.
            rows = defaultdict(dict)
            for d in range(1,L[0]+1):
                if (1,d) in H:
                    continue
                for e,c in ac.column(L,set(H),(1,d)).items():
                    rows[e][d]=c
            rows[-1]={d:1 for d in range(1,L[0]+1) if (1,d) not in H}
            result,_=ac.reduce_rows([(r,0) for r in rows.values()])
            self.assertEqual(len(result),L[0]-sum(i==1 for i,d in H))
        # Removing the only short-arm vertex leaves an occupied path. Two
        # reflected long-arm vertices then have identical profiles: noninjective.
        L=[8,4,1];H={(3,1)}
        receipt=ac.radial_gcd_bound(L,H)
        self.assertFalse(receipt['injectivity_proved'])
        signs={(1,1):1,(1,3):-1}
        # Their coordinates on the remaining path are 5 and 7 in 0..12.
        occupied=set(ac.vertices(L))-H
        profiles=[]
        for u in signs:
            profiles.append(Counter(abs(u[1]-(d if i==1 else -d))
                                    for i,d in occupied if (i,d)!=u))
        self.assertEqual(profiles[0],profiles[1])
        self.assertTrue(ac.radial_gcd_bound([1,3,2],[(1,1)])['injectivity_proved'])
        with self.assertRaises(ValueError):
            ac.radial_gcd_bound([99,79,23],[],degree_limit=10)
        with self.assertRaises(ValueError):
            ac.radial_gcd_bound([99*10**12,79*10**12,23*10**12],[])

    def test_inhomogeneous_radial_identity_including_balance(self):
        payload=witness(1)
        L=payload['lengths']
        signs={tuple(v):s for k,s in [('left',1),('right',-1)] for v in payload[k]}
        known={v:(s if v[0]!=1 else 0) for v,s in signs.items()}
        F0,_=bfs_shells(L,known)
        S0=sum(known.values())
        radial=Counter()
        for i,d in signs:
            radial[d if i==1 else -d]+=1
        X={d:s for (i,d),s in signs.items() if i==1}
        C=Counter()
        for d,s in X.items():
            for q,n in radial.items():
                C[d-q]+=s*n
        lhs=defaultdict(int)
        for e,c in C.items():
            lhs[e]+=c
            lhs[-e]+=c
        rhs=defaultdict(int)
        rhs[0]=-2*S0
        for e,c in F0.items():
            rhs[e]-=c
            rhs[-e]-=c
        clean=lambda p:{e:c for e,c in p.items() if c}
        self.assertEqual(clean(lhs),clean(rhs))
        # Balance's constant coefficient is essential; deleting it must fail.
        self.assertNotEqual(S0,0)
        wrong=dict(rhs)
        wrong[0]=0
        self.assertNotEqual(clean(lhs),clean(wrong))
        # Independently audit the padded reversal and shift in equation (12).
        a=max(d for i,d in signs if i==1)
        b=max(d for i,d in signs if i in (2,3))
        N=a+b
        P={b+q:n for q,n in radial.items()}
        Y={b+d:s for d,s in X.items()}
        polynomial=defaultdict(int)
        for y,c in Y.items():
            for p,n in P.items():
                polynomial[y+N-p]+=c*n
                polynomial[N-y+p]+=c*n
        self.assertEqual(clean(polynomial),{N+e:c for e,c in clean(rhs).items()})

    def test_invalid_signings(self):
        bad = witness(1)
        bad['left'][0] = bad['right'][0]
        with self.assertRaises(ValueError):
            ac.recover_payload(bad)
        with self.assertRaises(ValueError):
            ac.certificate(0, [])
        for holes in [[1], [[1]], [[True,2]], [[4,1]]]:
            with self.assertRaises(ValueError):
                ac.validate([99,79,23],holes)


if __name__ == '__main__':
    unittest.main()
