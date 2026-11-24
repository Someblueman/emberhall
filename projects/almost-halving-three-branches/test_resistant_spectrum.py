"""Audit every compiled equation against original physical shell columns."""
from collections import defaultdict
import unittest
import itertools
import random
import resistant_spectrum as rs
import full_shorter_coupling as fc


def normalized(rows):
    return {tuple(sorted((i,c) for i,c in row.items() if c)) for row in rows
            if any(row.values())}


class SpectrumTests(unittest.TestCase):
    def test_complete_original_shells_after_periodic_identification(self):
        for half,period,width in ((123,1,40),(127,3,40),(133,3,43)):
            keys,actual = rs.compile_system(half,period,width)
            positions = {k:i for i,k in enumerate(keys)}
            t = 2*half+1
            lengths,holes = fc.geometry(t,19)
            expected = defaultdict(lambda:defaultdict(int))
            def key(a,d):
                q,r = divmod(d,t)
                s = 1
                if r>half:
                    q,r,s = q+1,t-r,-1
                if r<=width: return ('left',a,q,s*r)
                if r>=half-width: return ('right',a,q,s,r-half)
                return ('period',a,q,s,r%period)
            for a,n in enumerate(lengths,1):
                for d in range(1,n+1):
                    if (a,d) in holes: continue
                    v,factor = ((2,d-20*t+1),-1) if a==1 and d>=43*t else ((a,d),1)
                    i = positions[key(*v)]
                    for e,c in fc.shell_column(lengths,holes,(a,d)).items():
                        expected[e][i] += c*factor
            for e,c in fc.shell_column(lengths,holes,(0,0)).items():
                expected[e][positions['left',0,0,0]] += c
            self.assertEqual(normalized(actual),normalized(expected.values()))
            damaged = [dict(row) for row in actual]
            i = next(iter(damaged[0]))
            damaged[0][i] += 1
            self.assertNotEqual(normalized(damaged),normalized(expected.values()))

    def test_parity_certificate_against_literal_solutions(self):
        rng = random.Random(1623)
        for n in range(1,8):
            for _ in range(25):
                rows = [{i:rng.choice((-3,-2,-1,1,2,3)) for i in range(n)
                         if rng.random()<0.6} for _ in range(4)]
                truth = [v for v in itertools.product((-1,1),repeat=n)
                         if all(sum(c*v[i] for i,c in row.items())==0 for row in rows)]
                certificate = rs.parity_refusal(rows)
                if certificate is not None:
                    self.assertFalse(truth)
                    self.assertTrue(rs.verify_refusal(rows,certificate))
                    self.assertFalse(rs.verify_refusal(rows,certificate+certificate))
        rows = [{0:1,1:-1},{0:1,1:1}]
        certificate = rs.parity_refusal(rows)
        self.assertTrue(rs.verify_refusal(rows,certificate))
        self.assertFalse(rs.verify_refusal(rows,certificate[:-1]))
        self.assertFalse(rs.verify_refusal([{0:1,1:-1}]*2,certificate))

    def test_hybrid_search_against_exhaustive_literal_solutions(self):
        rng = random.Random(7981)
        for n in range(2,8):
            for _ in range(12):
                rows = [{i:rng.choice((-2,-1,1,2)) for i in range(n)
                         if rng.random()<0.6} for _ in range(4)]
                truth = [v for v in itertools.product((-1,1),repeat=n)
                         if v[0]==1 and all(sum(c*v[i] for i,c in row.items())==0 for row in rows)]
                refusal,basis = rs.binary_elimination(rows)
                if refusal is not None:
                    self.assertFalse(truth)
                    continue
                engine = rs.make_engine(n,rows,basis,seconds=5,nodes=10000,
                                        free_order=rng.choice(('natural','connected')))
                status,values = engine.run({0:1})
                self.assertEqual(status,'sat' if truth else 'unsat')
                if values is not None: self.assertIn(tuple(values),truth)

    def test_saved_refusal_is_reconstructed_and_damage_rejected(self):
        saved = rs.search(123,1,seconds=1,nodes=0)
        self.assertEqual(saved['status'],'ansatz_refused_by_parity')
        self.assertTrue(rs.verify_saved(saved)['verified'])
        saved['t'] = 7981
        self.assertTrue(rs.verify_saved(saved)['verified'])
        saved['certificate'] = saved['certificate'][:-1]
        with self.assertRaises(ValueError): rs.verify_saved(saved)
        with self.assertRaises(ValueError): rs.verify_saved(dict(t=247,period=1,patch_width=40,status='unknown'))

    def test_scale_phase_and_resource_limit(self):
        # Equal phase, different lengths: exactly the same finite equations.
        for p in (1,3):
            k,r = rs.compile_system(130,p)
            k2,r2 = rs.compile_system(130+2*p,p)
            self.assertEqual(k,k2)
            self.assertEqual(r,r2)
        result = rs.search(123,1,seconds=1,nodes=0)
        self.assertIn(result['status'],('unknown','unsat','ansatz_refused_by_parity'))
        self.assertFalse(result['all_pairs_decided'])
        with self.assertRaises(ValueError): rs.compile_system(122,1)


if __name__=='__main__': unittest.main()
