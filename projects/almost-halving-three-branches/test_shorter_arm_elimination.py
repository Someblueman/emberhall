import json
import unittest
from copy import deepcopy
import aperiodic_completion as ac
import shorter_arm_elimination as se
from gap_99_79_23 import witness
from test_aperiodic_completion import bfs_shells


def parameters(t=1):
    p=witness(t)
    signs={tuple(v):s for k,s in [('left',1),('right',-1)] for v in p[k]}
    L=p['lengths']
    q=dict(lengths=L,holes=sorted(set(ac.vertices(L))-signs.keys()),centre=signs.get((0,0),0))
    for i in [2,3]:q[f'arm{i}']=''.join({1:'+',-1:'-',0:'0'}[signs.get((i,d),0)] for d in range(1,L[i-1]+1))
    return q,signs


class ForcingTests(unittest.TestCase):
    def test_compiled_profile_against_independent_bfs(self):
        for t in [1,3]:
            q,signs=parameters(t)
            compiled=se.compile_forcing(q)
            known={v:s if v[0]!=1 else 0 for v,s in signs.items()}
            F0,_=bfs_shells(q['lengths'],known)
            self.assertEqual(compiled['F0'],{d:c for d,c in F0.items() if c})
            self.assertEqual(compiled['S0'],sum(known.values()))

    def test_valid_pair_and_exact_short_word_rejection(self):
        q,_=parameters()
        result=se.constraint(q,[1,0,0,1])
        self.assertFalse(result['excluded_by_necessary_constraint'])
        changed=deepcopy(q)
        changed['arm3']='-'+changed['arm3'][1:]
        self.assertEqual(q['arm3'][0],'+')
        result=se.constraint(changed,[1,0,0,1])
        self.assertTrue(result['excluded_by_necessary_constraint'])
        self.assertFalse(result['all_scale_family_proved'])
        with self.assertRaises(ValueError):se.constraint(q,[1,1,1])

    def test_laurent_reduction(self):
        self.assertEqual(se.remainder({-1:1},[1,0,0,1]),{2:1000002})
        self.assertEqual(se.remainder({3:1,0:1},[1,0,0,1]),{})




class CouplingTests(unittest.TestCase):
    def test_exact_certificates_without_rank_computation(self):
        # Check every coefficient, including centre and omitted coordinates.
        for t in (1,2,3,7):
            L=[99*t,79*t,23*t]
            for h in sorted({0,1,19,23*t}):
                H={((1,h) if h else (0,0)),(1,99*t)}
                columns={v:ac.column(L,H,v) for v in ac.vertices(L) if v not in H}
                for r in range(3*t+2,23*t+1):
                    cert=se.certificate_rows(t,h,r)
                    actual={v:sum(c*col.get(e,0) for e,c in cert.items())
                            for v,col in columns.items()}
                    self.assertEqual({v:c for v,c in actual.items() if c},se.coupling_terms(t,h,r))

    def test_independent_bfs_certificates_and_hole_endpoints(self):
        import random
        rng=random.Random(90317)
        for t in (1,2,3):
            L=[99*t,79*t,23*t]
            for h in sorted({0,1,19,23*t}):
                H={((1,h) if h else (0,0)),(1,99*t)}
                signs={v:rng.choice((-1,1)) for v in ac.vertices(L) if v not in H}
                F,_=bfs_shells(L,signs)
                for r in range(3*t+2,23*t+1):
                    # All certificate exponents exceed one, so the -2zS
                    # term is absent even for this unbalanced random signing.
                    lhs=sum(c*signs[v] for v,c in se.coupling_terms(t,h,r).items())
                    rhs=sum(c*(F[e]-F[e-1]) for e,c in se.certificate_rows(t,h,r).items())
                    self.assertEqual(lhs,rhs)

    def test_true_pair_recovered_and_balanced_alteration_rejected(self):
        q,signs=parameters()
        self.assertFalse(se.coupled_constraint(q)['excluded_by_necessary_constraint'])
        free=set(range(1,5))|set(range(14,19))
        w=se.force_third_band(1,19,q['arm2'],{d:signs[3,d] for d in free})
        self.assertEqual(w,q['arm3'])
        compressed=dict(q,arm3=''.join(ch if d in free else '?'
                                      for d,ch in enumerate(q['arm3'],1)))
        self.assertEqual(se.reconstruct_third(compressed)['parameters'],q)
        with self.assertRaises(ValueError):se.reconstruct_third(q)
        _,pairs=bfs_shells(q['lengths'],signs)
        self.assertEqual(pairs[1],pairs[-1])
        changed=deepcopy(q)
        y=list(changed['arm2'])
        self.assertNotEqual(y[38],y[47])
        y[38],y[47]=y[47],y[38]
        changed['arm2']=''.join(y)
        # Both altered positions are outside every old ternary clause.
        for r in range(5,24):
            self.assertEqual(tuple(changed['arm2'][d-1] for d in (r,56+r)),
                             tuple(q['arm2'][d-1] for d in (r,56+r)))
        self.assertTrue(se.coupled_constraint(changed)['excluded_by_necessary_constraint'])
        altered=dict(signs)
        altered[2,39],altered[2,48]=altered[2,48],altered[2,39]
        self.assertEqual(sum(altered.values()),0)
        _,pairs=bfs_shells(q['lengths'],altered)
        self.assertNotEqual(pairs[1],pairs[-1])

    def test_all_scale_strictness_and_reflection_elimination(self):
        for t in (1,2,3,11,2661):
            for h in sorted({0,1,19,23*t}):
                r=3*t+2
                d=r+23*t+h+1
                self.assertGreater(d,23*t)
                self.assertLess(d,59*t+2)
                self.assertGreater(se.coupling_terms(t,h,r)[2,d],0)
                for j in {13*t+1,18*t}:
                    terms=se.second_arm_terms(t,h,j)
                    self.assertTrue(terms)
                    self.assertTrue(all(i==2 for i,_ in terms))
        # Full-scale necessary-row run, no graph or first-arm variables.
        t=2661
        q=dict(lengths=[99*t,79*t,23*t],holes=[[1,19],[1,99*t]],
               centre=1,arm2='+'*(79*t),arm3='+'*(23*t))
        result=se.coupled_constraint(q)
        self.assertEqual(result['checked_rows'],53219)
        self.assertEqual(result['free_retained_signs_bound'],231509)
        self.assertFalse(result['excluded_by_necessary_constraint'])
        self.assertFalse(result['existence_decided'])
        y=list(q['arm2']);y[26*t+22-1]='-';q['arm2']=''.join(y)
        self.assertTrue(se.coupled_constraint(q)['excluded_by_necessary_constraint'])

    def test_literal_forcing_and_invalid_geometry(self):
        for t,h,r in [(0,1,2),(1,-1,5),(1,24,5),(1,19,4),(1,19,24)]:
            with self.assertRaises(ValueError):se.coupling_terms(t,h,r)
        q,_=parameters()
        central=dict(q,holes=[[0,0],[1,99]],centre=0,arm2='+'*79,arm3='+'*23)
        self.assertEqual(se.coupled_constraint(central)['free_retained_signs_bound'],88)
        with self.assertRaises(ValueError):se.coupled_constraint(dict(central,centre=1))
        for holes in [[],[[1,19]],[[1,24],[1,99]],[[2,19],[1,99]]]:
            bad=deepcopy(q);bad['holes']=holes
            with self.assertRaises(ValueError):se.coupled_constraint(bad)
        free={d:1 for d in set(range(1,5))|set(range(14,19))}
        self.assertEqual(se.force_third_band(1,19,'+'*79,free),'+'*23)
        y=list('+'*79);y[47]='-'
        with self.assertRaises(ValueError):se.force_third_band(1,19,''.join(y),free)


if __name__=='__main__':unittest.main()
