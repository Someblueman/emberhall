from collections import Counter,defaultdict,deque
import itertools
import random
import unittest
import literal_shell_search as ls
from test_aperiodic_completion import bfs_shells


class LiteralShellTests(unittest.TestCase):
    def test_small_linear_systems_against_exhaustive_signs(self):
        rng = random.Random(44451)
        for n in range(1,8):
            for _ in range(15):
                rows = [{i:rng.choice((-2,-1,1,2)) for i in range(n) if rng.random()<0.5}
                        for _ in range(5)]
                seeds = {0:-1} if rng.random()<0.5 else None
                truth = [v for v in itertools.product((-1,1),repeat=n)
                         if (not seeds or v[0]==-1) and
                         all(sum(c*v[i] for i,c in row.items())==0 for row in rows)]
                engine = ls.LiteralSearch(n,rows,node_budget=10000,seconds=10)
                status,values = engine.run(seeds)
                self.assertEqual(status,'sat' if truth else 'unsat')
                if values is not None:
                    self.assertIn(tuple(values),truth)

    def test_all_shell_columns_by_independent_adjacency_bfs(self):
        for h in (0,1,19):
            lengths,holes,vertices,rows = ls.shell_system(1,h)
            adjacency = defaultdict(list)
            for arm,n in enumerate(lengths,1):
                prior = (0,0)
                for depth in range(1,n+1):
                    v = (arm,depth)
                    adjacency[prior].append(v)
                    adjacency[v].append(prior)
                    prior = v
            expected = defaultdict(dict)
            for i,u in enumerate(vertices):
                distances = {u:0}
                queue = deque([u])
                while queue:
                    v = queue.popleft()
                    for w in adjacency[v]:
                        if w not in distances:
                            distances[w] = distances[v]+1
                            queue.append(w)
                f = Counter(distances[v] for v in vertices if v!=u)
                for e in range(1,max(f)+2):
                    c = f[e]-f[e-1]-2*(e==1)
                    if c:
                        expected[e][i] = c
            self.assertEqual(rows,[row for e,row in sorted(expected.items())])

    def test_boundary_holes_no_literal_solution(self):
        for h in (0,1):
            result = ls.search(1,h,node_budget=100000,seconds=30)
            self.assertEqual(result['status'],'unsat')
            self.assertFalse(result['universal_result'])
            self.assertNotIn('left',result)

    def test_known_third_word_completes_two_missing_arms(self):
        from gap_99_79_23 import witness
        pair = witness(1)
        signs = {tuple(v):s for key,s in [('left',1),('right',-1)] for v in pair[key]}
        seeds = {v:s for v,s in signs.items() if v[0] in (0,3)}
        result = ls.search(1,19,node_budget=1000,seconds=10,seeds=seeds)
        self.assertEqual(result['status'],'sat')
        found = {tuple(v):s for key,s in [('left',1),('right',-1)] for v in result[key]}
        self.assertEqual(found,signs)
        _,distances = bfs_shells([99,79,23],found)
        self.assertEqual(len(result['left']),100)
        self.assertEqual(len(result['right']),100)
        self.assertEqual(distances[1],distances[-1])
        u,v = tuple(result['left'][0]),tuple(result['right'][0])
        found[u],found[v] = found[v],found[u]
        _,altered = bfs_shells([99,79,23],found)
        self.assertNotEqual(altered[1],altered[-1])

    def test_limit_returns_unknown_and_never_unsat(self):
        self.assertEqual(ls.search(1,0,node_budget=0,seconds=10)['status'],'unknown')
        engine = ls.LiteralSearch(3,[{0:1,1:-1}],node_budget=0)
        status,values = engine.run()
        self.assertEqual(status,'unknown')
        self.assertIsNone(values)
        # An actual local impossibility may still be proved before branching.
        status,_ = ls.LiteralSearch(1,[{0:1}],node_budget=0).run()
        self.assertEqual(status,'unsat')

    def test_parity_hybrid_against_exhaustive_systems(self):
        rng = random.Random(404001)
        for n in range(1,8):
            for _ in range(15):
                rows = [{i:rng.choice((-2,-1,1,2)) for i in range(n) if rng.random()<0.6}
                        for _ in range(5)]
                truth = [v for v in itertools.product((-1,1),repeat=n)
                         if all(sum(c*v[i] for i,c in row.items())==0 for row in rows)]
                engine = ls.LiteralSearch(n,rows,node_budget=10000,seconds=10,parity=True,priority=list(reversed(range(n))))
                status,values = engine.run()
                self.assertEqual(status,'sat' if truth else 'unsat')
                if values is not None:
                    self.assertIn(tuple(values),truth)
        from gap_99_79_23 import witness
        pair = witness(1)
        signs = {tuple(v):s for key,s in [('left',1),('right',-1)] for v in pair[key]}
        result = ls.search(1,19,node_budget=1000,seconds=10,
                           seeds={v:s for v,s in signs.items() if v[0]!=1},parity=True)
        self.assertEqual(result['status'],'sat')
        self.assertTrue(result['parity_propagation'])

    def test_modular_rank_certifies_only_lower_bound(self):
        self.assertEqual(ls.modular_rank([{0:2,1:3},{0:4,1:7}],{0,1}),2)
        # Loss modulo the field does not imply a rational kernel.
        self.assertEqual(ls.modular_rank([{0:101},{1:1}],{0,1}),1)
        result = ls.two_arm_rank(3,19)
        self.assertEqual(result['unknown_two_arm_columns'],532)
        self.assertTrue(result['rational_injectivity_proved'])
        self.assertFalse(result['existence_decided'])
        self.assertFalse(result['all_scale_result'])

    def test_scope_and_validation(self):
        for budget in (-1,True):
            with self.assertRaises(ValueError):ls.LiteralSearch(1,[],node_budget=budget)
        for seconds in (0,float('inf'),True):
            with self.assertRaises(ValueError):ls.LiteralSearch(1,[],seconds=seconds)
        with self.assertRaises(ValueError):ls.shell_system(2661,19)
        with self.assertRaises(ValueError):ls.LiteralSearch(1,[{0:True}])
        with self.assertRaises(ValueError):ls.LiteralSearch(17,[dict.fromkeys(range(17),1)])
        with self.assertRaises(ValueError):ls.LiteralSearch(1,[]).run({0:0})
        with self.assertRaises(ValueError):ls.LiteralSearch(1,[],priority=[1])
        with self.assertRaises(ValueError):ls.LiteralSearch(1,[],parity=True,extra_xor_rows=[(1,0)])
        self.assertEqual(ls.search(2,1)['proof'],'occupied vertex count is odd')


if __name__ == '__main__':
    unittest.main()
