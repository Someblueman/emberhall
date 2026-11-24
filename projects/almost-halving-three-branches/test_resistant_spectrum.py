"""Audit every compiled equation against original physical shell columns."""
from collections import defaultdict
import unittest
import itertools
import random
from unittest.mock import patch
import resistant_spectrum as rs
import full_shorter_coupling as fc


def normalized(rows):
    return {tuple(sorted((i,c) for i,c in row.items() if c)) for row in rows
            if any(row.values())}


class SpectrumTests(unittest.TestCase):
    def test_parity_quotient_against_every_literal_solution(self):
        rng = random.Random(428)
        for size in range(1,8):
            for _ in range(15):
                rows = [{i:rng.randrange(-3,4) for i in range(size) if rng.random()<0.6}
                        for _ in range(4)]
                truth = {v for v in itertools.product((-1,1),repeat=size)
                         if all(sum(c*v[i] for i,c in row.items())==0 for row in rows)}
                q = rs.parity_sign_quotient(size,rows,seconds=5)
                self.assertTrue(q['complete'])
                if q['conflict']:
                    self.assertFalse(truth)
                    continue
                self.assertTrue(q['binary_fibre_verified'])
                lifted = {tuple(s*v[j] for j,s in q['aliases'])
                          for v in itertools.product((-1,1),repeat=q['size'])
                          if all(sum(c*v[i] for i,c in row.items())==0 for row in q['rows'])}
                self.assertEqual(lifted,truth)
        with patch.object(rs.time,'monotonic',side_effect=itertools.count()):
            q = rs.parity_sign_quotient(2,[{0:1,1:1}],seconds=0.1)
        self.assertFalse(q['complete'])
        self.assertNotIn('binary_fibre_verified',q)

    def test_exact_rational_recovery_and_denominator_clearing(self):
        rows = [{0:2,1:3,2:-1},{2:1,3:1}]
        r = rs.rational_recovery(4,rows,seconds=5)
        self.assertTrue(r['complete'])
        self.assertEqual(r['rank'],2)
        self.assertTrue(r['kernel_verified'])
        self.assertEqual(len(r['free']),2)
        for seed in itertools.product((-2,-1,0,1,2),repeat=2):
            parameters = dict(zip(r['free'],seed))
            values = {i:sum(c*parameters[j] for j,c in expression.items())
                      for i,expression in r['expressions'].items()}
            self.assertTrue(all(sum(c*values[i] for i,c in row.items())==0
                                for row in rows+r['normalized_rows']))
            for i in r['free']: self.assertEqual(values[i],parameters[i])
        self.assertEqual(rs.rational_recovery(1,[{0:3}])['rank'],1)
        self.assertEqual(len(rs.ternary_echelon([{0:3}])['basis']),0)
        with patch.object(rs.time,'monotonic',side_effect=itertools.count()):
            r = rs.rational_recovery(2,[{0:1,1:1}],seconds=0.1)
        self.assertFalse(r['complete'])
        self.assertNotIn('kernel_verified',r)

    def test_moving_driver_budgets_and_positive_verifier_rejections(self):
        result = rs.moving_search(1,seconds=5,nodes=0)
        self.assertEqual(result['status'],'ansatz_refused_by_modular_nonzero')
        self.assertFalse(result['all_pairs_decided'])
        result = rs.moving_search(10,seconds=5,nodes=0,closure_steps=0)
        self.assertEqual(result['status'],'unknown')
        with self.assertRaises(ValueError): rs.verify_saved(result)
        keys,_ = rs.moving_periodic_system(10)
        fake = dict(mode='moving',period=10,status='sat',assignment=[[list(k),1] for k in keys])
        with self.assertRaises(ValueError): rs.verify_saved(fake)
        with self.assertRaises(ValueError): rs.moving_search(10,seconds=float('nan'))

    def test_long_rows_against_exhaustive_three_sign_controls(self):
        rng = random.Random(183)
        for _ in range(30):
            rows = [{i:rng.choice((-2,-1,1,2)) for i in range(18)}]
            rows.extend({i:1,i%3:-1} for i in range(3,18))
            truth = [v for v in itertools.product((-1,1),repeat=3)
                     if v[0]==1 and all(sum(c*v[i%3] for i,c in row.items())==0 for row in rows)]
            refusal,basis = rs.binary_elimination(rows)
            if refusal is not None:
                self.assertFalse(truth)
                continue
            engine = rs.make_engine(18,rows,basis,seconds=5,nodes=10000)
            status,values = engine.run({0:1})
            self.assertEqual(status,'sat' if truth else 'unsat')
            if values is not None:
                self.assertTrue(all(sum(c*values[i] for i,c in row.items())==0 for row in rows))
        rows = [{i:1 for i in range(18)}]
        _,basis = rs.binary_elimination(rows)
        engine = rs.make_engine(18,rows,basis,seconds=5,nodes=10000)
        self.assertEqual(engine.run({0:1})[0],'sat')
        engine = rs.make_engine(18,rows,basis,seconds=5,nodes=10000)
        self.assertEqual(engine.run(dict.fromkeys(range(18),1))[0],'unsat')

    def test_signed_quotient_lifts_exact_integer_equations(self):
        rows = [{0:2,1:-3,2:5,3:1,4:-2}]
        relations = [(0,1,-1),(1,2,1),(3,4,-1)]
        result = rs.sign_relation_quotient(5,rows,relations)
        self.assertFalse(result['conflict'])
        self.assertEqual(result['size'],2)
        for v in itertools.product((-1,1),repeat=2):
            lifted = [s*v[j] for j,s in result['aliases']]
            self.assertTrue(all(lifted[i]==s*lifted[j] for i,j,s in relations))
            self.assertEqual(sum(c*lifted[i] for i,c in rows[0].items()),
                             sum(c*v[i] for i,c in result['rows'][0].items()))
        self.assertTrue(rs.sign_relation_quotient(2,[],[(0,1,1),(0,1,-1)])['conflict'])
        # Deep chains must not depend on Python's recursion limit.
        result = rs.sign_relation_quotient(3000,[],[(i,i+1,-1) for i in range(2999)])
        self.assertEqual(result['size'],1)
        self.assertEqual(result['aliases'][0][1],-result['aliases'][-1][1])

    def test_moving_compiler_against_every_physical_shell_column(self):
        for period,k in ((1,2),(3,1),(3,2),(10,2)):
            t = period*k+1
            keys,formal = rs.moving_periodic_system(period)
            positions = {v:i for i,v in enumerate(keys)}
            lengths,holes = fc.geometry(t,19*t)
            expected = defaultdict(lambda:defaultdict(int))
            vertices = [(0,0)]+[(a,d) for a,n in enumerate(lengths,1)
                                for d in range(1,n+1) if (a,d) not in holes]
            for a,d in vertices:
                edge,u = divmod(d,t)
                key = (a,edge,0 if not u else (u-1)%period+1)
                i = positions[key]
                for e,c in fc.shell_column(lengths,holes,(a,d)).items():
                    expected[e][i] += c
                    expected[e+period][i] -= c
            actual = defaultdict(lambda:defaultdict(int))
            for (q,c),row in formal.items():
                for i,value in row.items(): actual[q*t+c][i] += value
            def clean(rows):
                return {e:{i:c for i,c in row.items() if c}
                        for e,row in rows.items() if any(row.values())}
            self.assertEqual(clean(actual),clean(expected))
            self.assertEqual(len(keys),200+201*period)
        with self.assertRaises(ValueError): rs.moving_periodic_system(0)

    def test_hybrid_ternary_kernel_against_exhaustive_modular_solutions(self):
        rng = random.Random(39128)
        for size in range(1,6):
            for _ in range(12):
                rows = [{i:rng.randrange(-3,4) for i in range(size)
                         if rng.random()<0.6} for _ in range(5)]
                truth = [v for v in itertools.product(range(3),repeat=size)
                         if all(sum(c*v[i] for i,c in row.items())%3==0 for row in rows)]
                for budget in (0,2,100):
                    result = rs.ternary_analysis(size,rows,seconds=5,sparse_pivots=budget)
                    self.assertTrue(result['complete'])
                    self.assertTrue(result['kernel_verified'])
                    self.assertEqual(len(truth),3**result['nullity'])
                    self.assertEqual(result['rank']+result['nullity'],size)
                    self.assertEqual(result['forced_zero_coordinates'],
                                     [i for i in range(size) if all(v[i]==0 for v in truth)])
                    self.assertFalse(result['literal_existence_decided'])
                result = rs.ternary_analysis(size,rows,retain_kernel=True)
                relations = rs.ternary_nonzero_relations(result['kernel'])
                for v in truth:
                    if all(v):
                        self.assertTrue(all((v[i]-s*v[j])%3==0 for i,j,s in relations))
        # Full rank is a modular property. The API never reports a sign witness.
        result = rs.ternary_analysis(2,[{0:1},{1:1}])
        self.assertEqual(result['forced_zero_coordinates'],[0,1])
        with patch.object(rs.time,'monotonic',side_effect=itertools.count()):
            result = rs.ternary_analysis(2,[{0:1,1:1}],seconds=0.1)
        self.assertFalse(result['complete'])
        self.assertNotIn('rank',result)
        self.assertNotIn('kernel_verified',result)
        self.assertFalse(result['literal_existence_decided'])
        with self.assertRaises(ValueError): rs.ternary_analysis(2,[{2:1}])
        with self.assertRaises(ValueError): rs.ternary_analysis(2,[],sparse_pivots=-1)

    def test_ternary_bitsets_and_independent_dense_rank(self):
        def encode(values):
            return (sum(1<<i for i,v in enumerate(values) if v==1),
                    sum(1<<i for i,v in enumerate(values) if v==2))
        rng = random.Random(3128)
        for n in range(1,9):
            for _ in range(30):
                a,b = [[rng.randrange(3) for _ in range(n)] for _ in range(2)]
                self.assertEqual(rs.ternary_add(encode(a),encode(b)),
                                 encode([(x+y)%3 for x,y in zip(a,b)]))
                matrix = [[rng.randrange(-4,5) for _ in range(n)] for _ in range(10)]
                rows = [{i:c for i,c in enumerate(row) if c} for row in matrix]
                actual = rs.ternary_echelon(rows,seconds=5)
                self.assertTrue(actual['complete'])
                # Separate dense left-to-right elimination, without bitsets.
                dense = [[c%3 for c in row] for row in matrix]
                rank = 0
                for col in range(n):
                    selected = next((r for r in range(rank,len(dense)) if dense[r][col]),None)
                    if selected is None: continue
                    dense[rank],dense[selected] = dense[selected],dense[rank]
                    factor = dense[rank][col]
                    dense[rank] = [c*factor%3 for c in dense[rank]]
                    for r in range(rank+1,len(dense)):
                        factor = dense[r][col]
                        dense[r] = [(x-factor*y)%3 for x,y in zip(dense[r],dense[rank])]
                    rank += 1
                self.assertEqual(len(actual['basis']),rank)
                for pivot,(one,two) in actual['basis'].items():
                    self.assertFalse(one&two)
                    self.assertEqual((one|two).bit_length()-1,pivot)
                    self.assertTrue(one>>pivot&1)
        with self.assertRaises(ValueError): rs.ternary_echelon([{-1:1}])
        with self.assertRaises(ValueError): rs.ternary_echelon([{0:1.5}])
        with self.assertRaises(ValueError): rs.ternary_echelon([],seconds=float('inf'))

    def test_meet_in_middle_tables_match_independent_exhaustion(self):
        rng = random.Random(7416)
        for width in range(17):
            for _ in range(4):
                word = tuple(rng.choice((-103,-3,-1,1,2,107)) for _ in range(width))
                expected = [b for b in range(1<<width)
                            if not sum(c*(1 if b>>j&1 else -1) for j,c in enumerate(word))]
                masks,full = rs.literal_row_table(word)
                self.assertEqual(full,(1<<len(expected))-1)
                self.assertEqual(masks,[sum(1<<p for p,b in enumerate(expected) if b>>j&1)
                                        for j in range(width)])
        with self.assertRaises(ValueError): rs.literal_row_table([0])
        with self.assertRaises(ValueError): rs.literal_row_table([1]*17)

    def test_reduced_binary_basis_has_exactly_the_same_solutions(self):
        rng = random.Random(7479)
        for size in range(1,9):
            for _ in range(20):
                rows = [{i:rng.randrange(-3,4) for i in range(size)} for _ in range(3)]
                refusal,basis = rs.binary_elimination(rows)
                if refusal is not None: continue
                reduced = rs.reduced_binary_basis(basis)
                for p,(mask,_) in reduced.items():
                    self.assertEqual({q for q in basis if mask>>q&1},{p})
                for bits in range(1<<size):
                    def valid(equations):
                        return all((bits&m).bit_count()%2==rhs for m,rhs in equations.values())
                    self.assertEqual(valid(basis),valid(reduced))

    def test_dense_ternary_copies_are_literal_equalities(self):
        kernel = dict(free=[0,1,2],expressions={0:(1,0),1:(2,0),2:(4,0),
                                               3:(7,0),4:(0,7),5:(7,0)})
        relations = rs.ternary_copy_relations(kernel)
        self.assertIn((4,3,-1),relations)
        self.assertIn((5,3,1),relations)
        for parameters in itertools.product((1,2),repeat=3):
            values = {i:sum((1 if a>>j&1 else 2)*parameters[j]
                            for j in range(3) if (a|b)>>j&1)%3
                      for i,(a,b) in kernel['expressions'].items()}
            if all(values.values()):
                self.assertTrue(all((values[i]-s*values[j])%3==0 for i,j,s in relations))

    def test_joint_field_quotients_preserve_exact_literal_fibre(self):
        rng = random.Random(2474)
        for size in range(1,8):
            for _ in range(12):
                rows = [{i:rng.randrange(-3,4) for i in range(size)} for _ in range(3)]
                report = rs.joint_sign_closure(size,rows,seconds=5)
                truth = [v for v in itertools.product((-1,1),repeat=size)
                         if all(not sum(c*v[i] for i,c in row.items()) for row in rows)]
                if report['conflict']:
                    self.assertFalse(truth)
                    continue
                self.assertTrue(report['complete'])
                aliases = report['aliases']
                for v in truth:
                    projected = {}
                    for i,(j,s) in enumerate(aliases):
                        if j in projected: self.assertEqual(projected[j],s*v[i])
                        projected[j] = s*v[i]
                lifted_truth = []
                for q in itertools.product((-1,1),repeat=report['size']):
                    if any(sum(c*q[i] for i,c in row.items()) for row in report['rows']): continue
                    lifted_truth.append(tuple(s*q[j] for j,s in aliases))
                self.assertCountEqual(lifted_truth,truth)
        with patch.object(rs.time,'monotonic',side_effect=itertools.count()):
            report = rs.joint_sign_closure(2,[{0:1,1:-1}],seconds=0.1)
        self.assertFalse(report['complete'])
        with self.assertRaises(ValueError): rs.joint_sign_closure(1,[],seconds=0)
        with self.assertRaises(ValueError): rs.joint_sign_closure(1,[],steps=0)

    def test_quadratic_lift_against_every_nonzero_modular_solution(self):
        rng = random.Random(798010)
        for size in range(1,8):
            for _ in range(15):
                rows = [{i:rng.randrange(-2,3) for i in range(size)} for _ in range(3)]
                base = rs.ternary_analysis(size,rows,seconds=5,retain_kernel=True)
                self.assertTrue(base['complete'])
                pairs,lifted = rs.quadratic_sign_lift(base['kernel'])
                for signs in itertools.product((-1,1),repeat=size):
                    if any(sum(c*signs[i] for i,c in row.items())%3 for row in rows): continue
                    products = [1]+[signs[i]*signs[j] for i,j in pairs[1:]]
                    self.assertTrue(all(sum(c*products[i] for i,c in row.items())%3==0
                                        for row in lifted))
                report = rs.quadratic_sign_analysis(size,rows,seconds=5)
                self.assertTrue(report['complete'])
                for signs in itertools.product((-1,1),repeat=size):
                    if any(sum(c*signs[i] for i,c in row.items())%3 for row in rows): continue
                    self.assertFalse(report['conflict'])
                    bits = sum(1<<i for i,s in enumerate(signs) if s==1)
                    self.assertTrue(all((m&bits).bit_count()%2==rhs
                                        for m,rhs in report['parity_rows']))
        # A product of the first two free coordinates appears with factor 2.
        pairs,rows = rs.quadratic_sign_lift(dict(free=[0,1],expressions={2:(3,0)}))
        self.assertEqual(pairs,[None,(0,1)])
        self.assertEqual(rows,[{0:1,1:2}])
        with self.assertRaises(ValueError):
            rs.quadratic_sign_lift(dict(free=[0],expressions={0:(1,1)}))
        with patch.object(rs.time,'monotonic',side_effect=itertools.count()):
            report = rs.quadratic_sign_analysis(2,[{0:1,1:-1}],seconds=0.1)
        self.assertFalse(report['complete'])
        with self.assertRaises(ValueError): rs.quadratic_sign_analysis(1,[],seconds=0)

    def test_local_affine_hulls_preserve_every_literal_solution(self):
        rng = random.Random(24011)
        for size in range(1,9):
            for _ in range(25):
                rows = [{i:rng.choice((-3,-2,-1,1,2,3)) for i in range(size)
                         if rng.random()<0.6} for _ in range(4)]
                valid = [b for b in range(1<<size)
                         if all(not sum(c*(2*((b>>i)&1)-1) for i,c in row.items())
                                for row in rows)]
                report = rs.affine_shell_closure(size,rows,seconds=5)
                if report['conflict']: self.assertFalse(valid)
                for b in valid:
                    self.assertTrue(all((b&m).bit_count()%2==rhs
                                        for m,rhs in report['basis'].values()))
        # Basic parity sees one equation; exact local signs force three.
        rows = [{0:3,1:1,2:1,3:1}]
        self.assertEqual(len(rs.binary_elimination(rows)[1]),1)
        report = rs.affine_shell_closure(4,rows,seconds=5)
        self.assertTrue(report['complete'])
        self.assertEqual(report['rank'],3)
        self.assertEqual(report['free'],1)
        refused = rs.affine_shell_closure(3,[{0:3,1:1,2:2},{0:1,1:-1}],seconds=5)
        self.assertTrue(refused['conflict'])

    def test_local_affine_hulls_limits_and_search_augmentation(self):
        report = rs.affine_shell_closure(4,[{0:3,1:1,2:1,3:1}],seconds=5,local_rank=0)
        self.assertFalse(report['conflict'])
        self.assertTrue(report['history'][0]['skipped'])
        report = rs.affine_shell_closure(4,[{0:3,1:1,2:1,3:1}],seconds=5,rounds=1)
        self.assertFalse(report['complete'])
        self.assertEqual(report['stage'],'round_limit')
        with patch.object(rs.time,'monotonic',side_effect=itertools.count()):
            report = rs.affine_shell_closure(2,[{0:1,1:-1}],seconds=0.1)
        self.assertFalse(report['complete'])
        for kwargs in ({'size':0},{'seconds':0},{'rounds':0},{'local_rank':17}):
            params = dict(size=2,original=[{0:1,1:-1}],seconds=5)
            params.update(kwargs)
            with self.assertRaises(ValueError): rs.affine_shell_closure(**params)
        with self.assertRaises(ValueError): rs.affine_shell_closure(2,[{2:1}],seconds=5)
        # A completed positive assignment still goes through untouched rows.
        result = rs.moving_search(1,seconds=5,nodes=100,affine_shells=True)
        self.assertIn(result['status'],('sat','unsat','unknown',
                      'ansatz_refused_by_modular_nonzero','ansatz_refused_by_affine_shells'))
        if result['status']=='sat': self.assertTrue(rs.verify_saved(result)['verified'])

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
