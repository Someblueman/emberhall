import copy
from collections import Counter, defaultdict, deque
from fractions import Fraction as Q
from itertools import combinations, product
import random
import unittest
import literal_fibre as f


def example():
    from gap_99_79_23 import witness
    pair = witness(1)
    signs = {tuple(v):s for key,s in [('left',1),('right',-1)] for v in pair[key]}
    return dict(t=1,centre=signs[0,0],third=''.join('+' if signs[3,d] == 1 else '-' for d in range(1,24)))


def bfs_columns(t):
    lengths,holes = f.geometry(t)
    graph = defaultdict(list)
    for arm,n in enumerate(lengths,1):
        for d in range(1,n+1):
            u,v = (arm,d),((arm,d-1) if d > 1 else (0,0))
            graph[u].append(v)
            graph[v].append(u)
    occupied = set(graph)-holes
    columns = {}
    for source in occupied:
        distances = {source:0}
        queue = deque([source])
        while queue:
            u = queue.popleft()
            for v in graph[u]:
                if v not in distances:
                    distances[v] = distances[u]+1
                    queue.append(v)
        counts = Counter(distances[v] for v in occupied if v != source)
        k = defaultdict(int,{1:-2})
        for e,n in counts.items():
            k[e] += n
            k[e+1] -= n
        columns[source] = {e:c for e,c in k.items() if c}
    return columns


class LiteralFibreTests(unittest.TestCase):
    def test_radius_corollary_on_fresh_unequal_branch_ratios(self):
        for multipliers,h,t in [((5,3,2),1,19),((9,6,2),2,31),((7,5,3),4,47)]:
            lengths = [n*t for n in multipliers]
            holes = {(1,h),(1,lengths[0])}
            vertices = [(0,0)] + [(a,d) for a,n in enumerate(lengths,1)
                                  for d in range(1,n+1) if (a,d) not in holes]
            for vertex in vertices:
                for e in f.shell.shell_column(lengths,holes,vertex):
                    self.assertLessEqual(abs(f.folded_level(t,e)-f.folded_level(t,vertex[1])),h+1)

    def test_graph_partition_reconstructs_every_row(self):
        rng = random.Random(163201)
        for t in (163,201):
            lengths,holes = f.geometry(t)
            signs = {(0,0):-1}
            signs.update({(a,d):rng.choice((-1,1)) for a,n in enumerate(lengths,1)
                          for d in range(1,n+1) if (a,d) not in holes})
            direct = defaultdict(int)
            for vertex,s in signs.items():
                for e,c in f.shell.shell_column(lengths,holes,vertex).items():
                    direct[e] += s*c
            self.assertEqual(f.folded_residual(t,signs),{e:c for e,c in direct.items() if c})
        with self.assertRaises(ValueError):
            f.folded_residual(161,{})

    def test_both_symbolic_boundaries_at_first_and_later_odd_scale(self):
        left,right = f.boundary_stencils()
        for t in (163,201):
            half = t//2
            lengths,holes = f.geometry(t)
            actual_left = defaultdict(lambda:defaultdict(int))
            actual_right = defaultdict(lambda:defaultdict(int))
            vertices = [(0,0)] + [(a,d) for a,n in enumerate(lengths,1)
                                  for d in range(1,n+1) if (a,d) not in holes]
            for arm,d in vertices:
                level = f.folded_level(t,d)
                s = 1 if d%t <= half else -1
                q = (d-s*level)//t
                for e,c in f.shell.shell_column(lengths,holes,(arm,d)).items():
                    r = f.folded_level(t,e)
                    tau = 1 if e%t <= half else -1
                    quotient = (e-tau*r)//t
                    if r <= 20:
                        self.assertLessEqual(level,40)
                        actual_left[quotient,tau*r][arm,q,s*level] += c
                    if r >= half-20:
                        self.assertGreaterEqual(level,half-40)
                        actual_right[quotient,tau,r-half][arm,q,s,level-half] += c
            def trim(rows):
                return {row:{v:c for v,c in terms.items() if c}
                        for row,terms in rows.items() if any(terms.values())}
            self.assertEqual(left,trim(actual_left))
            self.assertEqual(right,trim(actual_right))

    def test_symbolic_folded_stencil_against_actual_columns(self):
        stencil = f.interior_stencil()
        self.assertEqual(len(f.slice_labels()),402)
        self.assertEqual(len(set(f.slice_labels())),402)
        self.assertEqual(max(abs(v[3]) for row in stencil.values() for v in row),20)
        for t,r in [(162,21),(162,60),(163,21),(163,60),(201,50),(239,98)]:
            lengths,holes = f.geometry(t)
            actual = defaultdict(lambda:defaultdict(int))
            for arm,n in enumerate(lengths,1):
                for d in range(1,n+1):
                    if (arm,d) in holes:
                        continue
                    level = f.folded_level(t,d)
                    for e,c in f.shell.shell_column(lengths,holes,(arm,d)).items():
                        self.assertLessEqual(abs(f.folded_level(t,e)-level),20)
                        if f.folded_level(t,e) != r:
                            continue
                        s = 1 if d%t <= t//2 else -1
                        q = (d-s*level)//t
                        tau = 1 if e%t <= t//2 else -1
                        quotient = (e-tau*r)//t
                        actual[quotient,tau][arm,q,s,level-r] += c
            actual = {row:{v:c for v,c in terms.items() if c}
                      for row,terms in actual.items() if any(terms.values())}
            self.assertEqual(stencil,actual)

    def test_finite_graph_edge_predicate(self):
        labels = f.slice_labels()
        index = {v:i for i,v in enumerate(labels)}
        rng = random.Random(402)
        slices = [rng.getrandbits(402) for _ in range(41)]
        residual = f.stencil_residual(slices)
        # Direct evaluate the selected actual K rows, using original depths.
        t,r = 201,50
        lengths,holes = f.geometry(t)
        direct = defaultdict(int)
        for delta in range(-20,21):
            for arm,q,s in labels:
                d = q*t+s*(r+delta)
                sign = 1-2*((slices[delta+20] >> index[arm,q,s]) & 1)
                for e,c in f.shell.shell_column(lengths,holes,(arm,d)).items():
                    if f.folded_level(t,e) == r:
                        tau = 1 if e%t <= t//2 else -1
                        direct[(e-tau*r)//t,tau] += c*sign
        self.assertEqual(residual,{row:c for row,c in direct.items() if c})
        self.assertTrue(f.folded_theorem()['eventual_periodicity_proved'])
        self.assertFalse(f.folded_theorem()['resistant_scales_decided'])
        with self.assertRaises(ValueError):
            f.stencil_residual([0]*40)

    def test_columns_include_original_paths_through_holes(self):
        for t in (1,2):
            lengths,holes = f.geometry(t)
            for vertex,column in bfs_columns(t).items():
                self.assertEqual(column,f.shell.shell_column(lengths,holes,vertex))

    def test_tail_reduction_entire_affine_system(self):
        rng = random.Random(20261124)
        for t in (1,2,3,7):
            for third in (None, '+-'*(23*t//2)+'+'*(23*t%2)):
                vertices,rows,retained = f.system(t,third,-1)
                values = [rng.randrange(-3,4) for _ in vertices]
                signs = retained | dict(zip(vertices,values))
                signs.update({(1,d):-signs[2,d-20*t+1] for d in range(43*t,99*t)})
                # Independent direct pair-distance sums, rather than K columns.
                shells = defaultdict(int)
                for (a,d),(b,e) in combinations(signs,2):
                    distance = abs(d-e) if a == b else d+e
                    shells[distance] += signs[a,d]+signs[b,e]
                raw = defaultdict(int,{1:-2*sum(signs.values())})
                for e,c in shells.items():
                    raw[e] += c
                    raw[e+1] -= c
                expected = {e:sum(c*values[i] for i,c in row.items())-rhs for e,row,rhs in rows}
                self.assertEqual({e:c for e,c in raw.items() if c},
                                 {e:c for e,c in expected.items() if c})

    def test_tail_theorem_resistant_scale_without_matrix(self):
        result = f.tail_theorem(7981)
        self.assertEqual(result['forced_pairs'],446936)
        self.assertEqual(result['reduced_two_arm_unknowns'],973680)
        self.assertFalse(result['literal_existence_decided'])

    def test_quadratic_reduction_in_dimension_two(self):
        # x+y+z=1 has three cube points; zero has none. Both fibres have dim2.
        for rhs,count in [(1,3),(0,0),(Q(1,2),0)]:
            fibre = f.rational_fibre(3,[(9,{0:1,1:1,2:1},rhs)])
            self.assertEqual(len(fibre['free']),2)
            polynomials = f.constraints(fibre)
            zeros = [bits for bits in range(4) if all(f.value(p,bits) == 0 for p in polynomials)]
            direct = [s for s in product((-1,1),repeat=3) if sum(s) == rhs]
            self.assertEqual(len(zeros),count)
            self.assertEqual(len(direct),count)
            energy = {}
            for p in polynomials:
                energy = f.add(energy,f.multiply(p,p))
            inverse,bits = f.inverse_on_cube(energy,2)
            if count:
                self.assertIn(bits,zeros)
                self.assertIsNone(inverse)
            else:
                self.assertEqual(f.multiply(energy,inverse),{0:Q(1)})
                bad = f.add(inverse,{0:1})
                self.assertNotEqual(f.multiply(energy,bad),{0:Q(1)})

    def test_dimension_three_and_zero(self):
        for size in (0,1,3):
            fibre = f.rational_fibre(size,[])
            self.assertTrue(all(not p for p in f.constraints(fibre)))
            self.assertEqual(f.inverse_on_cube({},size),(None,0))
        fibre = f.rational_fibre(1,[(1,{0:1},Q(1,2))])
        energy = f.multiply(f.constraints(fibre)[0],f.constraints(fibre)[0])
        inverse,_ = f.inverse_on_cube(energy,0)
        self.assertEqual(f.multiply(energy,inverse),{0:Q(1)})

    def test_positive_original_distance_recount_and_damaged_pair(self):
        saved = f.solve(example())
        self.assertEqual((saved['status'],saved['dimension'],saved['size']),('found',1,100))
        self.assertEqual(f.verify(saved)['size'],100)
        damaged = copy.deepcopy(saved)
        # Swap two opposite signs outside the retained data, preserving size.
        positive = next(v for v in damaged['signing'] if v[0] in (1,2) and v[2] == 1)
        negative = next(v for v in damaged['signing'] if v[0] in (1,2) and v[2] == -1)
        positive[2],negative[2] = negative[2],positive[2]
        with self.assertRaises(ValueError):
            f.verify(damaged)

    def test_boolean_unsat_and_changed_inverse(self):
        saved = f.solve(dict(t=1,third='+'*23,centre=1))
        self.assertEqual((saved['status'],saved['kind']),('unsat','boolean'))
        self.assertTrue(f.verify(saved)['verified'])
        saved['certificate'][0][1] = str(Q(saved['certificate'][0][1])+1)
        with self.assertRaises(ValueError):
            f.verify(saved)

    def test_linear_unsat_and_changed_combination(self):
        saved = f.solve(dict(t=1,third='-'+'+'*22,centre=1))
        self.assertEqual((saved['status'],saved['kind']),('unsat','linear'))
        self.assertTrue(f.verify(saved)['verified'])
        saved['certificate'][0][1] = str(Q(saved['certificate'][0][1])+1)
        with self.assertRaises(ValueError):
            f.verify(saved)

    def test_all_third_words_are_not_a_fixed_word_refusal(self):
        saved = f.solve(dict(t=1,third=None,centre=1))
        self.assertTrue(saved['all_third_words'])
        self.assertEqual(saved['dimension'],23)
        self.assertEqual(saved['status'],'resource_limit')
        self.assertFalse(saved['existence_decided'])
        with self.assertRaises(ValueError):
            f.verify(saved)
        large = f.solve(dict(t=7981,third=None,centre=1))
        self.assertEqual((large['status'],large['stage']),('resource_limit','matrix'))
        self.assertEqual(large['reduced_unknowns'],1157243)

    def test_validation_and_zero_budget(self):
        for t in (0,-1,True,1.5):
            with self.assertRaises(ValueError):
                f.geometry(t)
        with self.assertRaises(ValueError):
            f.system(1,'?'*23,1)
        with self.assertRaises(ValueError):
            f.solve(example(),-1)
        self.assertEqual(f.solve(example(),0)['status'],'resource_limit')
        with self.assertRaises(ValueError):
            f.decode([[0,'1'],[0,'2']],1)


if __name__ == '__main__':
    unittest.main()
