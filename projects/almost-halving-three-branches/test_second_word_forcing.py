import random
import unittest
import full_shorter_coupling as fc
import second_word_forcing as sw
from test_aperiodic_completion import bfs_shells


class SecondWordTests(unittest.TestCase):
    def test_telescoping_identity_every_interval_and_endpoint(self):
        rng=random.Random(41211)
        for t in (1,2,3,11):
            for h in sorted({0,2*t-2}):
                z={i:rng.choice((-1,1)) for i in range(1,5*t+1)}
                b={i:sum(c*z[d-13*t] for d,c in fc.middle_operator(t,h,13*t+i).items())
                   for i in z}
                self.assertFalse(sw.interval_constraint(t,h,b)['excluded'])
                for u in range(2*t,5*t+1):
                    for v in range(u,5*t+1):
                        lhs=sum(b[i]-b[7*t-i] for i in range(u,v+1))
                        rhs=z[7*t-u-h]-z[7*t-v-h-1]-z[v-h]+z[u-h-1]
                        self.assertEqual(lhs,rhs)
                        self.assertLessEqual(abs(rhs),4)

    def test_affine_forcing_independent_adjacency_bfs(self):
        rng=random.Random(9931)
        for t,h in ((1,0),(2,0),(2,2),(3,1),(3,4)):
            L,H=fc.geometry(t,h)
            y={i:rng.choice((-1,1)) for i in range(1,79*t+1)}
            zero=dict.fromkeys(range(13*t+1,18*t+1),0)
            middle={i:rng.choice((-1,1)) for i in zero}
            sigma=1 if h else 0
            F0,_=bfs_shells(L,fc.linear_completion(t,h,sigma,y,zero))
            F1,_=bfs_shells(L,fc.linear_completion(t,h,sigma,y,middle))
            for i in range(2*t,5*t+1):
                e=92*t+1+i
                baseline=F0[e]-F0[e-1]
                row=F1[e]-F1[e-1]
                j=7*t-i
                z=lambda a:middle[13*t+a]
                self.assertEqual(row,baseline-(z(i)+z(j)+z(j-h)-z(j-h-1)))

    def test_new_constraint_beyond_literal_recovery_and_individual_bounds(self):
        # Full reconstructed words are literal, including the long-arm
        # ternary high rows. Passing those rows does not imply this bound.
        for t in (11,31,2661):
            y=dict.fromkeys(range(1,79*t+1),1)
            y[71*t+2]=-1
            middle=dict.fromkeys(range(13*t+1,18*t+1),1)
            middle[15*t+2]=-1
            signs=fc.linear_completion(t,19,1,y,middle)
            L,H=fc.geometry(t,19)
            self.assertEqual(len(signs),sum(L)-1)
            self.assertFalse(set(signs)&H)
            self.assertTrue(all(s in (-1,1) for s in signs.values()))
            w=fc.third_word(t,19,y,middle)
            for r in range(3*t+2,18*t+1):
                self.assertEqual(sum(c*(y[d] if a==2 else w[d])
                                     for (a,d),c in fc.se.coupling_terms(t,19,r).items()),0)
            for r in range(1,3*t+2):
                self.assertEqual(sum(c*(y[d] if a==2 else w[d])
                                     for (a,d),c in fc.low_terms(t,19,r).items()),0)
            payload=dict(t=t,h=19,centre=1,
                         arm2=''.join('+' if y[i]==1 else '-' for i in y))
            result=sw.second_word_constraint(payload)
            self.assertTrue(result['individual_middle_row_bound_passed'])
            self.assertTrue(result['excluded'])
            self.assertEqual(result['maximum_interval_magnitude'],6)
            self.assertFalse(result['existence_decided'])
            if t==11:
                # No reliance on the shell-column implementation to reject
                # these literal disjoint sets' distance multisets.
                _,pair=bfs_shells(L,signs)
                self.assertNotEqual(pair[1],pair[-1])
                # A deliberate alteration is rejected by that same independent
                # counter; it does not turn this already invalid pair valid.
                changed=dict(signs)
                u=next(v for v,s in signs.items() if s==1)
                v=next(v for v,s in signs.items() if s==-1)
                changed[u],changed[v]=changed[v],changed[u]
                _,altered=bfs_shells(L,changed)
                self.assertNotEqual(altered[1],altered[-1])

    def test_exact_reflected_subsystem_exhaustively_at_small_endpoint(self):
        import itertools
        t,h=1,0
        attainable=set()
        for values in itertools.product((-1,1),repeat=5):
            z=dict(enumerate(values,1))
            attainable.add(tuple((z[7-i]-z[6-i])-(z[i]-z[i-1])
                                 for i in range(2,6)))
        for values in itertools.product((-4,-2,0,2,4),repeat=5):
            b=dict(enumerate(values,1))
            differences=tuple(b[i]-b[7-i] for i in range(2,6))
            self.assertEqual(not sw.interval_constraint(t,h,b)['excluded'],
                             differences in attainable)
        # Range four alone can miss the odd-t fixed reflection coordinate.
        b=dict(enumerate((-4,-4,-2,-4,0),1))
        result=sw.interval_constraint(1,0,b)
        self.assertEqual(result['maximum_interval_magnitude'],4)
        self.assertTrue(result['excluded'])

    def test_valid_pair_and_balanced_alteration_independent_counter(self):
        from gap_99_79_23 import witness
        q=witness(1)
        signs={tuple(v):s for key,s in [('left',1),('right',-1)] for v in q[key]}
        self.assertEqual(sum(signs.values()),0)
        _,pair=bfs_shells(q['lengths'],signs)
        self.assertEqual(pair[1],pair[-1])
        u,v=tuple(q['left'][0]),tuple(q['right'][1])
        signs[u],signs[v]=signs[v],signs[u]
        self.assertEqual(sum(signs.values()),0)
        _,pair=bfs_shells(q['lengths'],signs)
        self.assertNotEqual(pair[1],pair[-1])
        # This control is outside this note's shallow-hole scope.

    def test_input_boundaries(self):
        for t,h in ((0,0),(True,0),(1,1),(2,-1)):
            with self.assertRaises(ValueError):sw.interval_constraint(t,h,{})
        with self.assertRaises(ValueError):sw.interval_constraint(1,0,{i:0 for i in range(1,5)})
        b={i:0 for i in range(1,6)}
        self.assertFalse(sw.interval_constraint(1,0,b)['excluded'])
        b[2]=4;b[5]=-4
        self.assertEqual(sw.interval_constraint(1,0,b)['maximum_interval_magnitude'],8)
        self.assertTrue(sw.interval_constraint(1,0,b)['excluded'])


if __name__=='__main__':unittest.main()
