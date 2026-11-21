"""Independent pick, deletion, graph and perturbation checks for the cut."""

from fractions import Fraction
from itertools import combinations, permutations
import json
from math import factorial
from pathlib import Path
import random
import subprocess
import sys
import unittest

from frozen_pair_obstruction import (connect_guarded, example, omitted_pair_failures, repair,
                                     restricted_census, separation_certificate,
                                     uniform_lift_guard)


def fair(u, a, omit=None):
    for i, row in enumerate(u):
        if i == omit:
            continue
        own = sum(row[g] for g, owner in enumerate(a) if owner == i)
        for j in range(len(u)):
            if j == omit:
                continue
            goods = [g for g, owner in enumerate(a) if owner == j]
            if goods and not any(own >= sum(row[g] for g in goods if g != h) for h in goods):
                return False
    return True


def owners(w):
    return tuple(next(i for i, h in w if h == g) for g in range(len(w)))


def picks(u, w, r):
    pool = set(range(len(w)))
    assert len(w) == 2*r+2
    assert {i for i, _ in w[:r+2]} == set(range(r+2))
    assert {i for i, _ in w[r+2:]} == set(range(r))
    for i, g in w:
        assert g in pool and all(u[i][g] > u[i][h] for h in pool if h != g)
        pool.remove(g)
    assert not pool


def all_fixed(r):
    """Permutation generator independent of the production combinations tree."""
    m = 2*r+2
    pool = tuple(g for g in range(1, m) if g not in (r, m-1))
    found = set()
    for holder in (r, r+1):
        for p in permutations(pool):
            a = [r-1]*m
            a[0], a[p[0]] = holder, 2*r+1-holder
            for index, g in enumerate(p[1:]):
                a[g] = index//2
            found.add(tuple(a))
    return found


class FrozenPairTests(unittest.TestCase):
    def check_route(self, u, left, right, route, r):
        picks(u, left, r)
        picks(u, right, r)
        self.assertEqual((route[0], route[-1]), (owners(left), owners(right)))
        for a in route:
            self.assertTrue(fair(u, a))
            self.assertEqual(tuple(a.count(i) for i in range(r+2)), (2,)*r+(1,1))
            self.assertIn(a[0], (r, r+1))
            self.assertEqual(a[-1], r-1)  # The other frozen good never moves.
        for a, b in zip(route, route[1:]):
            changed = [g for g in range(len(a)) if a[g] != b[g]]
            self.assertEqual(len(changed), 2)
            x, y = changed
            self.assertEqual((a[x], a[y]), (b[y], b[x]))

    def test_family_and_open_perturbation_box(self):
        rng = random.Random(205011)
        for r in (2, 3, 4, 5, 8, 12):
            original, left, right = example(r)
            for trial in range(8):
                u = tuple(tuple(Fraction(v)+Fraction(rng.randrange(-3,4),16)
                                if trial else v for v in row) for row in original)
                self.assertTrue(all(min(row)>0 and len(set(row))==len(row) for row in u))
                route = repair(r)
                self.check_route(u, left, right, route, r)
                proof = separation_certificate(u, route[0], route[-1], r-1, 0, (r,r+1))
                self.assertEqual(len(proof['excluded_pivots']), len(left)-3)
                for e in proof['excluded_pivots']:
                    self.assertEqual(e['value'], u[e['observer']][e['good']])
                    self.assertLess(e['value'], min(u[e['observer']][g] for g in (r,len(left)-1)))

    def test_entire_restricted_graph(self):
        for r in (2,3,4):
            u, left, right = example(r)
            states = all_fixed(r)
            good = {a for a in states if fair(u,a)}
            todo, sizes = set(good), []
            while todo:
                queue, count = [todo.pop()], 0
                while queue:
                    a = queue.pop()
                    count += 1
                    for x,y in combinations(range(len(a)),2):
                        b = list(a)
                        b[x],b[y] = b[y],b[x]
                        b = tuple(b)
                        if b in todo:
                            todo.remove(b)
                            queue.append(b)
                sizes.append(count)
            expected = [factorial(2*r-2)//2**(r-1)]*2
            self.assertEqual(sorted(sizes), expected)
            census = restricted_census(u, owners(left), owners(right), r-1, 0, (r,r+1))
            self.assertEqual(census, dict(all_restricted_states=len(states), ef1_states=len(good),
                                         component_sizes=expected, endpoints_separated=True))

    def test_removed_observer_and_uniform_guard(self):
        u, left, _ = example(4)
        a = list(owners(left))
        a[6], a[8] = a[8], a[6]
        self.assertTrue(fair(u,a,omit=3))
        self.assertFalse(fair(u,a))
        self.assertEqual(omitted_pair_failures(u,a,3), [dict(observer=5, target=3, own=9,
                                                           after_best_deletion=30)])
        self.assertFalse(uniform_lift_guard(u,owners(left),3))
        safe = tuple(tuple(0 if i!=3 and g in (4,9) else v for g,v in enumerate(row))
                     for i,row in enumerate(u))
        self.assertTrue(uniform_lift_guard(safe,owners(left),3))
        for a in all_fixed(4):
            if fair(u,a,omit=3):
                self.assertEqual(fair(u,a), not omitted_pair_failures(u,a,3))
            if fair(safe,a,omit=3):
                self.assertTrue(fair(safe,a))
                self.assertEqual(omitted_pair_failures(safe,a,3), [])
        self.assertTrue(uniform_lift_guard(((1,1,1),(0,0,0)),(0,0,1),0))

    def test_optimal_protected_and_unrestricted_distances(self):
        def radius_two(u, start, protected, r):
            distances, frontier = {start: 0}, {start}
            for depth in (1,2):
                following = set()
                for a in frontier:
                    for x,y in combinations(range(len(a)),2):
                        if a[x] == a[y]:
                            continue
                        b = list(a)
                        b[x],b[y] = b[y],b[x]
                        b = tuple(b)
                        if b in distances or (protected and b[0] not in (r,r+1)):
                            continue
                        if fair(u,b):
                            distances[b] = depth
                            following.add(b)
                frontier = following
            return distances
        for r in (2,3,4):
            u,left,right = example(r)
            for protected, expected in ((True,4),(False,2)):
                a = radius_two(u,owners(left),protected,r)
                b = radius_two(u,owners(right),protected,r)
                self.assertEqual(min(a[s]+b[s] for s in a.keys() & b.keys()),expected)

    def test_whole_protected_graph_has_a_guarded_constructor(self):
        rng = random.Random(51020)
        for r in (2,3,4,8):
            u,left,right = example(r)
            target = owners(right)
            samples = {owners(left), target}
            if r <= 3:
                for holder in (r,r+1):
                    for p in permutations(range(1,2*r+2)):
                        a = [holder]*(2*r+2)
                        a[p[0]] = 2*r+1-holder
                        for index,g in enumerate(p[1:]):
                            a[g] = index//2
                        a = tuple(a)
                        if fair(u,a):
                            samples.add(a)
            for _ in range(200):
                labels = list(range(r))*2+[r,r+1]
                rng.shuffle(labels)
                a = tuple(labels)
                if a[0] in (r,r+1) and fair(u,a):
                    samples.add(a)
            for start in samples:
                route = connect_guarded(u,start,target,0,(r,r+1),r)
                self.assertEqual((route[0],route[-1]),(start,target))
                self.assertLessEqual(len(route)-1,2*r+2)
                self.assertTrue(all(fair(u,a) and a[0] in (r,r+1) for a in route))
                for a,b in zip(route,route[1:]):
                    changed = [g for g in range(len(a)) if a[g]!=b[g]]
                    self.assertEqual(len(changed),2)
                    x,y = changed
                    self.assertEqual((a[x],a[y]),(b[y],b[x]))
            invalid = [list(row) for row in u]
            invalid[0][1] = 10000
            with self.assertRaisesRegex(ValueError,'automatic-fairness'):
                connect_guarded(tuple(map(tuple,invalid)),owners(left),target,0,(r,r+1),r)

    def test_labels_and_refusal_boundaries(self):
        u,left,right = example(4)
        agents, goods = (2,4,0,5,1,3), (9,7,1,3,8,0,5,2,6,4)
        uu = [[0]*10 for _ in u]
        for i,row in enumerate(u):
            for g,v in enumerate(row): uu[agents[i]][goods[g]] = v
        def mapped(a):
            b = [0]*10
            for g,i in enumerate(a): b[goods[g]] = agents[i]
            return tuple(b)
        aa,bb = mapped(owners(left)),mapped(owners(right))
        self.assertIsNotNone(separation_certificate(tuple(map(tuple,uu)),aa,bb,agents[3],goods[0],(agents[4],agents[5])))
        self.assertIsNone(separation_certificate(((0,)*10,)*6,owners(left),owners(right),3,0,(4,5)))
        for r in (True,1,0,-1):
            with self.assertRaises(ValueError): example(r)
        for frozen,favorite,carriers in ((4,0,(4,5)),(3,False,(4,5)),(3,0,(4,4))):
            with self.assertRaises(ValueError): separation_certificate(u,owners(left),owners(right),frozen,favorite,carriers)

    def test_actual_command(self):
        command = [sys.executable,str(Path(__file__).with_name('frozen_pair_obstruction.py')),'--pairs','4','--enumerate']
        result = json.loads(subprocess.run(command,check=True,capture_output=True,text=True).stdout)
        self.assertEqual(result['census']['component_sizes'],[90,90])
        self.assertEqual(result['proved_component_sizes'],[90,90])
        self.assertEqual(len(result['repair']),5)


if __name__ == '__main__':
    unittest.main()
