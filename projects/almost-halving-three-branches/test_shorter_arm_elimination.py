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


if __name__=='__main__':unittest.main()
