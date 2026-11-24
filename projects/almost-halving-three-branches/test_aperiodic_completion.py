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
                if u < v and sign == s:
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
                self.assertGreaterEqual(c['interval_rank'], (20*t-2+2)//3)
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

    def test_invalid_signings(self):
        bad = witness(1)
        bad['left'][0] = bad['right'][0]
        with self.assertRaises(ValueError):
            ac.recover_payload(bad)
        with self.assertRaises(ValueError):
            ac.certificate(0, [])


if __name__ == '__main__':
    unittest.main()
