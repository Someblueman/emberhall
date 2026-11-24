import json
import random
import unittest
from copy import deepcopy
import full_shorter_coupling as fc
import shorter_arm_elimination as se
from test_shorter_arm_elimination import parameters
from test_aperiodic_completion import bfs_shells


class FullCouplingTests(unittest.TestCase):
    def test_low_exact_columns_all_endpoints(self):
        for t in (1,2,3,7):
            for h in sorted({0,1,20*t-1}):
                L,H=fc.geometry(t,h)
                vertices=[(0,0)]+[(i,d) for i,n in enumerate(L,1) for d in range(1,n+1)]
                cols={v:fc.shell_column(L,H,v) for v in vertices if v not in H}
                for r in range(1,3*t+2):
                    cert=fc.low_certificate(t,h,r)
                    actual={v:sum(c*col.get(e,0) for e,c in cert.items()) for v,col in cols.items()}
                    self.assertEqual({v:c for v,c in actual.items() if c},fc.low_terms(t,h,r))

    def test_low_identity_independent_bfs(self):
        rng=random.Random(38109)
        for t in (1,2,3):
            for h in sorted({0,1,20*t-1}):
                L,H=fc.geometry(t,h)
                vertices=[(0,0)]+[(i,d) for i,n in enumerate(L,1) for d in range(1,n+1)]
                signs={v:rng.choice((-1,1)) for v in vertices if v not in H}
                F,_=bfs_shells(L,signs)
                for r in range(1,3*t+2):
                    lhs=sum(c*signs[v] for v,c in fc.low_terms(t,h,r).items())
                    rhs=sum(c*(F[e]-F[e-1]) for e,c in fc.low_certificate(t,h,r).items())
                    self.assertEqual(lhs,rhs)

    def test_real_pair_and_balanced_alteration_beyond_previous_rows(self):
        q,signs=parameters()
        compressed=dict(t=1,h=19,centre=q['centre'],arm2=q['arm2'],middle_third=q['arm3'][13:18])
        result=fc.reconstruct_third(compressed)
        self.assertEqual(result['parameters']['arm3'],q['arm3'])
        self.assertEqual(result['report']['free_retained_signs_bound'],85)
        _,pairs=bfs_shells(q['lengths'],signs)
        self.assertEqual(pairs[1],pairs[-1])
        bad=deepcopy(q);w=list(bad['arm3']);w[0],w[1]=w[1],w[0];bad['arm3']=''.join(w)
        self.assertFalse(se.coupled_constraint(bad)['excluded_by_necessary_constraint'])
        altered=dict(signs);altered[3,1],altered[3,2]=altered[3,2],altered[3,1]
        self.assertEqual(sum(altered.values()),0)
        self.assertTrue(any(sum(c*altered[v] for v,c in fc.low_terms(1,19,r).items())
                            for r in range(1,5)))
        _,pairs=bfs_shells(q['lengths'],altered)
        self.assertNotEqual(pairs[1],pairs[-1])

    def test_middle_operator_against_independent_bfs_inhomogeneous(self):
        rng=random.Random(6617)
        for t in (1,2,3):
            for h in sorted({0,1,2*t-1}):
                L,H=fc.geometry(t,h)
                y={d:rng.choice((-1,1)) for d in range(1,79*t+1)}
                sigma=1 if h else 0
                zero={d:0 for d in range(13*t+1,18*t+1)}
                z={d:rng.choice((-2,-1,0,1,2)) for d in zero}
                baseline=fc.linear_completion(t,h,sigma,y,zero)
                changed=fc.linear_completion(t,h,sigma,y,z)
                # Occupancy includes zero signed coordinates. BFS sums arbitrary
                # integers here; the shell identity is a linear identity.
                F0,_=bfs_shells(L,baseline)
                F1,_=bfs_shells(L,changed)
                for r in zero:
                    e=79*t+1+r
                    expected=-sum(c*z[d] for d,c in fc.middle_operator(t,h,r).items())
                    self.assertEqual(F1[e]-F1[e-1]-F0[e]+F0[e-1],expected)

    def test_failed_singleton_is_retained_as_a_discriminating_control(self):
        y={d:0 for d in range(1,80)}
        z={d:int(d==14) for d in range(14,19)}
        signs=fc.linear_completion(1,0,0,y,z)
        rows=fc.shell_rows(*fc.geometry(1,0),signs)
        self.assertEqual(rows[98],1)  # Not -z_18=0.
        self.assertEqual(fc.middle_operator(1,0,18),{18:1,15:2,14:-1})

    def test_proved_periodic_operator_kernel_is_not_a_completion(self):
        from math import gcd
        for t,h in [(3,2),(5,4),(11,2),(15,19),(20,19),(25,19),(31,8)]:
            g=gcd(3*t,h+1)
            representatives=[a for a in range(g) if a<(10*t+1-a)%g]
            self.assertEqual(len(representatives),g//2)
            for a in representatives:
                z=fc.periodic_middle_vector(t,h,a)
                self.assertTrue(any(z.values()))
                for r in z:
                    self.assertEqual(sum(c*z[d] for d,c in fc.middle_operator(t,h,r).items()),0)
        # Independent BFS at a genuine nontrivial operator-kernel scale.
        t,h=15,19
        z=fc.periodic_middle_vector(t,h,0)
        y={d:0 for d in range(1,79*t+1)}
        signs=fc.linear_completion(t,h,0,y,z)
        F,_=bfs_shells([99*t,79*t,23*t],signs)
        for r in z:
            e=79*t+1+r
            self.assertEqual(F[e]-F[e-1],0)
        self.assertTrue(any(F.values()))  # Kernel of selected rows only.

    def test_large_scale_and_rejected_geometry(self):
        t=2661
        q=dict(t=t,h=19,centre=1,arm2='+'*(79*t),middle_third='+'*(5*t))
        result=fc.reconstruct_third(q)
        self.assertEqual(result['report']['free_retained_signs_bound'],223525)
        self.assertEqual(result['report']['checked_rows'],61203)
        self.assertFalse(result['report']['first_arm_completion_proved'])
        for t,h in [(0,0),(1,-1),(1,20),(True,0)]:
            with self.assertRaises(ValueError):fc.validate(t,h)
        with self.assertRaises(ValueError):fc.middle_operator(1,19,14)
        with self.assertRaises(ValueError):fc.reconstruct_third(dict(q,middle_third='?'))

    def test_affine_seed_recovery_exact_and_compatibility_rejection(self):
        rng=random.Random(723)
        for t in (1,2,3,11,15,31,2661):
            for h in sorted({0,1,19,2*t-2}):
                if h>2*t-2:continue
                z={r:rng.choice((-1,1)) for r in range(13*t+1,18*t+1)}
                b={i:sum(c*z[d] for d,c in fc.middle_operator(t,h,13*t+i).items())
                   for i in range(1,5*t+1)}
                seed={i:z[13*t+i] for i in range(2*t-h-1,2*t+h+1)}
                self.assertEqual(fc.recover_middle(t,h,b,seed),z)
        z={r:1 for r in range(14,19)}
        b={i:sum(c*z[d] for d,c in fc.middle_operator(1,0,13+i).items()) for i in range(1,6)}
        with self.assertRaises(ValueError):fc.recover_middle(1,0,b,{1:1,2:-1})
        with self.assertRaises(ValueError):fc.recover_middle(1,1,b,{})


if __name__=='__main__':unittest.main()
