"""Audit every compiled equation against original physical shell columns."""
from collections import defaultdict
from fractions import Fraction
import unittest
import itertools
import functools
import random
from unittest.mock import patch
import resistant_spectrum as rs
import full_shorter_coupling as fc


def normalized(rows):
    return {tuple(sorted((i,c) for i,c in row.items() if c)) for row in rows
            if any(row.values())}


class SpectrumTests(unittest.TestCase):
    def test_adjacent_zero_observable_examples_both_phases(self):
        driver=rs.adjacent_integral_driver(43)
        for first in (2,3,4,11):
            cert=rs.adjacent_zero_observable_example(43,first)
            self.assertTrue(rs.verify_saved(cert)['verified'])
            keys,rows,phases=rs.adjacent_phase_system(43,2,first)
            bits=int(cert['bits'],16)
            values={key:1-2*(bits>>i&1) for i,key in enumerate(keys)}
            self.assertEqual(len(rows),356)
            self.assertEqual(len(phases),5)
            states=[[values[(*label,level)] for label in rs.moving_folded_labels()]
                    for level in (first,first+1)]
            counts=[len(rs.adjacent_unit_boundary_obstructions(driver,state,reverse))
                    for state,reverse in zip(states,(True,False))]
            self.assertEqual(counts,[47,55] if first%2 else [49,50])
        with self.assertRaises(ValueError):rs.adjacent_zero_observable_example(25)

    def test_adjacent_prefix_alternating_all_37_odd_holes(self):
        for hole in range(25,98,2):
            laws=rs.adjacent_conserved_observables(rs.adjacent_integral_driver(hole))
            rows=rs.adjacent_transfer_blocks(hole)['prefix']
            weights=rs.adjacent_endpoint_row_weights(hole)['alternating_prefix_weights']
            combined=defaultdict(Fraction)
            for index,n,d in weights:
                for key,c in rows[index].items():combined[key]+=Fraction(n,d)*c
            self.assertEqual({k:v for k,v in combined.items() if v},
                             {('slice',*label,2):w
                              for label,w in zip(rs.moving_folded_labels(),laws['alternating'])})

    def test_adjacent_prefix_balance_all_75_holes(self):
        for hole in range(24,99):
            driver=rs.adjacent_integral_driver(hole)
            moment=rs.adjacent_conserved_observables(driver)['moment']
            rows=rs.adjacent_transfer_blocks(hole)['prefix']
            weights=rs.adjacent_endpoint_row_weights(hole)['prefix_balance_weights']
            combined=defaultdict(Fraction)
            for index,n,d in weights:
                for key,c in rows[index].items():combined[key]+=Fraction(n,d)*c
            self.assertEqual({k:v for k,v in combined.items() if v},
                             {('slice',*label,2):1+2*w
                              for label,w in zip(rs.moving_folded_labels(),moment)})

    def test_adjacent_right_moment_all_75_holes(self):
        for hole in range(24,99):
            certificate=rs.adjacent_right_moment_identity(hole)
            self.assertTrue(rs.verify_saved(certificate)['verified'])
            if hole==43:
                self.assertEqual(len(certificate['row_weights']),531)
                damaged=dict(certificate,row_weights=[list(z) for z in certificate['row_weights']])
                damaged['row_weights'][0][1]+=1
                with self.assertRaises(ValueError):rs.verify_adjacent_right_moment(damaged)
                duplicated=dict(certificate,row_weights=certificate['row_weights']*2)
                with self.assertRaises(ValueError):rs.verify_adjacent_right_moment(duplicated)
                damaged=dict(certificate,prefix_balance_weights=[])
                with self.assertRaises(ValueError):rs.verify_adjacent_right_moment(damaged)

    def test_adjacent_unit_boundary_obstructions_and_actual_continuation(self):
        driver=rs.adjacent_integral_driver(43)
        cert=rs.adjacent_balanced_example()
        keys,_,_=rs.adjacent_phase_system(43,3,2)
        bits=int(cert['bits'],16)
        values={key:1-2*(bits>>i&1) for i,key in enumerate(keys)}
        states=[[values[(*label,level)] for label in rs.moving_folded_labels()]
                for level in (2,3,4)]
        self.assertEqual(len(rs.adjacent_unit_boundary_obstructions(driver,states[0],True)),43)
        self.assertEqual(len(rs.adjacent_unit_boundary_obstructions(driver,states[2])),47)
        laws=rs.adjacent_conserved_observables(driver)
        self.assertEqual([sum(c*v for c,v in zip(laws['moment'],state))
                          for state in states],[-128,-128,-128])
        self.assertEqual([sum(c*v for c,v in zip(laws['alternating'],state))
                          for state in states],[-8,8,-8])
        with self.assertRaises(ValueError):
            rs.verify_adjacent_phase_signs(dict(cert,zero_moment_slices=True))
        with self.assertRaises(ValueError):
            rs.verify_adjacent_phase_signs(dict(cert,zero_alternating_slices=True))
        # These directions have actual witnesses, independently checked above.
        for state,reverse in ((states[0],False),(states[1],False),
                              (states[1],True),(states[2],True)):
            self.assertEqual(rs.adjacent_unit_boundary_obstructions(driver,state,reverse),[])
        with self.assertRaises(ValueError):
            rs.adjacent_unit_boundary_obstructions(driver,[True]*402)
        damaged=dict(driver,recoveries=driver['recoveries'][:-1])
        with self.assertRaises(ValueError):
            rs.adjacent_unit_boundary_obstructions(damaged,states[0])

    def test_adjacent_balanced_word_both_parities_and_dead_boundaries(self):
        driver=rs.adjacent_integral_driver(43)
        permutation=rs.adjacent_time_reversal(43)
        labels=rs.moving_folded_labels()
        for first in (2,3,4,11):
            certificate=rs.adjacent_balanced_example(43,first)
            self.assertEqual(rs.verify_saved(certificate)['slice_sums'],[0,0,0])
        certificate=rs.adjacent_balanced_example(43,2)
        keys,_,_=rs.adjacent_phase_system(43,3,2)
        bits=int(certificate['bits'],16)
        values={key:1-2*(bits>>i&1) for i,key in enumerate(keys)}
        counts=[]
        for level,reverse in ((2,True),(4,False)):
            state=[values[(*label,level)] for label in labels]
            if reverse:state=[state[i] for i in permutation]
            bad=0
            for z in driver['recoveries']:
                if all(i%2==0 for i,c in z['expression']):
                    bad+=abs(sum(c*state[i//2] for i,c in z['expression']))!=1
            counts.append(bad)
        self.assertEqual(counts,[43,47])
        with self.assertRaises(ValueError):
            rs.verify_adjacent_phase_signs(dict(rs.adjacent_phase_example(43,3),
                                               balanced_slices=True))
        with self.assertRaises(ValueError):
            rs.adjacent_balanced_example(19,2)

    def test_adjacent_balance_drift_all_37_odd_holes(self):
        for hole in range(25,98,2):
            law=rs.adjacent_balance_drift(rs.adjacent_integral_driver(hole))
            self.assertEqual(law['unit_bound'],402)
            self.assertEqual(law['minimum_states_for_zero_sum'],405)
        with self.assertRaises(ValueError):
            rs.adjacent_balance_drift(rs.adjacent_integral_driver(24))

    def test_adjacent_integral_driver_all_75_holes(self):
        for hole in range(24,99):
            certificate=rs.adjacent_integral_driver(hole)
            laws=rs.adjacent_conserved_observables(certificate)
            self.assertEqual(len(laws['moment']),402)
            self.assertEqual(len(certificate['inputs']),448)
            self.assertEqual(len(certificate['recoveries']),356)
            laws=rs.adjacent_driver_phase_laws(certificate)
            self.assertEqual([x['drift'] for x in laws],[1,1,1,1,0])
        for hole in (True,0,19,23,99):
            with self.assertRaises(ValueError):rs.adjacent_integral_driver(hole)

    def test_adjacent_driver_random_odd_trajectory_and_actual_unit_word(self):
        rng=random.Random(20261125)
        certificate=rs.adjacent_integral_driver(43)
        source=rs.open_phase_example(43)
        oldkeys,_,_=rs.open_phase_system(43,3,3)
        oldbits=int(source['bits'],16)
        old={k:1-2*(oldbits>>i&1) for i,k in enumerate(oldkeys)}
        labels=rs.moving_folded_labels()
        previous=[old[(*label,3)] for label in labels]
        third=[old[(*label,4)] for label in labels if label[0]==3]
        following=rs.adjacent_driver_step(certificate,previous,third)
        self.assertEqual(following,[old[(*label,4)] for label in labels])
        previous_third=[old[(*label,3)] for label in labels if label[0]==3]
        self.assertEqual(rs.adjacent_driver_predecessor(certificate,following,previous_third),
                         previous)
        permutation=rs.adjacent_time_reversal(43)
        reversed_previous=[previous[i] for i in permutation]
        forced_predecessor=[]
        for recovery in certificate['recoveries']:
            if all(i%2==0 for i,c in recovery['expression']):
                value=sum(c*reversed_previous[i//2] for i,c in recovery['expression'])
                if abs(value)!=1:
                    forced_predecessor.append((labels[permutation[recovery['target']//2]],value))
        self.assertEqual(len(forced_predecessor),43)
        self.assertIn(((1,45,-1),3),forced_predecessor)
        failed=rs.adjacent_driver_step(certificate,previous,[1]*46)
        bad=[(labels[i],v) for i,v in enumerate(failed) if abs(v)!=1]
        self.assertEqual(len(bad),49)
        self.assertEqual(bad[0],((1,1,1),3))
        self.assertEqual(max(map(abs,failed)),7)
        # The recorded last middle state is a genuine dead end, even if
        # its entire next third arm and the old outside level are replaced.
        last=[old[(*label,5)] for label in labels]
        forced=[]
        for recovery in certificate['recoveries']:
            if all(i%2==0 for i,c in recovery['expression']):
                value=sum(c*last[i//2] for i,c in recovery['expression'])
                if abs(value)!=1:forced.append((labels[recovery['target']//2],value))
        self.assertEqual(len(forced),55)
        self.assertEqual(forced[0],((1,45,1),-3))
        # Arbitrary odd controls preserve the exact shells and phases, but
        # deliberately do not preserve the unit-value requirement.
        nonunit=False
        drift=rs.adjacent_balance_drift(certificate)
        observable=drift['observable'];history=[]
        for first in range(3,11):
            history.append((sum(c*v for c,v in zip(observable,previous)),sum(previous)))
            third=[rng.choice((-3,-1,1,3)) for _ in range(46)]
            following=rs.adjacent_driver_step(certificate,previous,third)
            self.assertTrue(all(v%2 for v in following))
            nonunit |= any(abs(v)!=1 for v in following)
            _,rows,traces=rs.adjacent_phase_system(43,2,first)
            values=[v for pair in zip(previous,following) for v in pair]
            self.assertTrue(all(sum(c*values[i] for i,c in row.items())==0 for row in rows))
            bits=sum((((1-v)//2)%2)<<i for i,v in enumerate(values))
            self.assertTrue(all((mask&bits).bit_count()%2==rhs for mask,rhs in traces))
            previous=following
        self.assertTrue(nonunit)
        self.assertEqual({total for value,total in history},{-8})
        self.assertTrue(all(history[i+2][0]-history[i][0]==-2*history[i][1]
                            for i in range(len(history)-2)))
        laws=rs.adjacent_driver_phase_laws(certificate)
        basis={}
        for law in laws:
            mask=int(law['mask'],16)
            while mask:
                p=mask.bit_length()-1
                if p not in basis:basis[p]=mask;break
                mask^=basis[p]
        self.assertEqual(len(basis),5)
        masks=[int(law['mask'],16) for law in laws]
        self.assertTrue(all(mask.bit_count()%2==0 for mask in masks))
        for i,j in enumerate((1,0,3,2,4)):
            reflected=sum(1<<permutation[k] for k in range(402) if masks[i]>>k&1)
            self.assertEqual(reflected,masks[j])

    def test_adjacent_driver_damaged_row_identities_are_rejected(self):
        import copy
        certificate=rs.adjacent_integral_driver(43)
        self.assertTrue(rs.verify_saved(certificate)['verified'])
        for change in ('coefficient','weight','target','missing','duplicate','scope'):
            damaged=copy.deepcopy(certificate)
            row=damaged['recoveries'][0]
            if change=='coefficient':row['expression'][0][1]+=2
            elif change=='weight':row['row_weights'][0][1]+=1
            elif change=='target':row['target']=damaged['inputs'][0]
            elif change=='missing':damaged['recoveries'].pop()
            elif change=='duplicate':row['expression'].append(row['expression'][0])
            else:damaged['all_pairs_decided']=True
            with self.assertRaises(ValueError):rs.verify_adjacent_integral_driver(damaged)

    def test_adjacent_blocks_recover_complete_physical_matrix(self):
        from collections import Counter
        def canonical(rows):
            return Counter(tuple(sorted((k,c) for k,c in row.items() if c))
                           for row in rows if any(row.values()))
        for scale,hole in ((9,1),(9,43),(11,19),(11,43),(11,97),(15,98)):
            half=scale//2
            blocks=rs.adjacent_transfer_blocks(hole)
            compiled=[]
            def physical(row,offset):
                out=defaultdict(int)
                for key,c in row.items():
                    if key[0]=='edge':_,a,q=key;vertex=(a,q*scale)
                    else:
                        _,a,q,s,j=key;vertex=(a,q*scale+s*(j+offset))
                    out[vertex]+=c
                return dict(out)
            compiled.extend(physical(row,0) for row in blocks['prefix'])
            for j in range(2,half-1):
                compiled.extend(physical(row,j) for row in blocks['transition'])
            compiled.extend(physical(row,half-1) for row in blocks['suffix'])
            expected=defaultdict(lambda:defaultdict(int))
            lengths=[n*scale for n in (99,79,23)]
            holes={(1,hole*scale),(1,99*scale)}
            vertices=[(0,0)]+[(a,d) for a,n in enumerate(lengths,1)
                                    for d in range(1,n+1) if (a,d) not in holes]
            for vertex in vertices:
                for exponent,c in fc.shell_column(lengths,holes,vertex).items():
                    expected[exponent][vertex]+=c
            self.assertEqual(canonical(compiled),canonical(expected.values()))
            self.assertEqual({v for row in compiled for v in row},set(vertices))
            self.assertEqual(blocks['state_signs'],402)
            self.assertEqual(len(range(2,half-1)),half+blocks['path_edges_offset'])

    def test_adjacent_rows_are_exactly_all_contained_interior_rows(self):
        for hole in range(1,99):
            blocks=rs.adjacent_transfer_blocks(hole)
            permutation=rs.adjacent_time_reversal(hole)
            self.assertEqual(len(set(permutation)),402)
            self.assertEqual(len(blocks['transition']),356)
            self.assertTrue(all({k[-1] for k in row}=={0,1}
                                for row in blocks['transition']))
        for hole,first,levels in ((1,3,4),(19,3,3),(43,3,4),(97,4,5),(98,3,2)):
            keys,rows,phases=rs.adjacent_phase_system(hole,levels,first)
            positions={k:i for i,k in enumerate(keys)}
            oldkeys,oldrows,oldphases=rs.open_phase_system(hole,levels,first)
            contained=[]
            for row in oldrows:
                if all(oldkeys[i] in positions for i in row):
                    contained.append({positions[oldkeys[i]]:c for i,c in row.items()})
            contained_phases=[]
            for mask,rhs in oldphases:
                terms=[oldkeys[i] for i in range(len(oldkeys)) if mask>>i&1]
                if all(k in positions for k in terms):
                    contained_phases.append((sum(1<<positions[k] for k in terms),rhs))
            self.assertEqual(normalized(rows),normalized(contained))
            self.assertEqual(set(phases),set(contained_phases))
            self.assertEqual((len(keys),len(rows),len(phases)),
                             (402*levels,356*(levels-1),5*(levels-1)))
        for levels,first in ((1,2),(True,2),(67,2),(2,1),(2,2.0)):
            with self.assertRaises(ValueError):rs.adjacent_phase_system(19,levels,first)

    def test_adjacent_positive_path_restriction_and_corruption(self):
        # Two consecutive transitions from Rook's actual three-centre word.
        old=rs.open_phase_example(43)
        oldkeys,_,_=rs.open_phase_system(43,3,3)
        oldbits=int(old['bits'],16)
        values={k:oldbits>>i&1 for i,k in enumerate(oldkeys)}
        keys,rows,phases=rs.adjacent_phase_system(43,3,3)
        bits=sum(values[k]<<i for i,k in enumerate(keys))
        certificate=dict(kind='moving-adjacent-phase-signs-v1',status='local_signing',
                         hole=43,levels=3,first=3,minimum_half=6,variables=len(keys),
                         bits=hex(bits),literal_existence_decided=False,all_pairs_decided=False)
        self.assertTrue(rs.verify_adjacent_phase_signs(certificate))
        self.assertTrue(rs.verify_saved(certificate)['verified'])
        active=next(iter(rows[0]))
        for key,value in (('bits',hex(bits^(1<<active))),('bits','0x'+'f'*10000),
                          ('minimum_half',5),('variables',len(keys)-1),('first',4),
                          ('literal_existence_decided',True),('all_pairs_decided',True)):
            with self.assertRaises(ValueError):
                rs.verify_adjacent_phase_signs(dict(certificate,**{key:value}))
        with self.assertRaises(ValueError):rs.adjacent_phase_search(seconds=float('inf'))

    def test_power_two_solution_against_small_exhaustion(self):
        rng=random.Random(20261125)
        for modulus in (2,4,8):
            for _ in range(35):
                rows=[{i:rng.randrange(-4,5) for i in range(3)} for _ in range(4)]
                rhs=[rng.randrange(modulus) for _ in rows]
                expected=next((x for x in itertools.product(range(modulus),repeat=3)
                               if all((sum(c*x[i] for i,c in row.items())-b)%modulus==0
                                      for row,b in zip(rows,rhs))),None)
                actual=rs.power_two_solution(3,rows,rhs,modulus)
                self.assertEqual(actual is None,expected is None)
                if actual is not None:
                    self.assertTrue(all((sum(c*actual[i] for i,c in row.items())-b)%modulus==0
                                        for row,b in zip(rows,rhs)))
        self.assertIsNone(rs.power_two_solution(1,[{0:4}],[2],8))
        self.assertEqual(rs.power_two_solution(1,[{0:4}],[4],8),[1])
        for modulus in (True,0,1,3,6):
            with self.assertRaises(ValueError):rs.power_two_solution(1,[{0:1}],[1],modulus)

    def test_periodic_odd_all_holes_with_independent_substitution(self):
        for hole in range(1,98,2):
            certificate=rs.periodic_phase_odd_example(hole)
            with patch.object(rs,'rational_recovery',side_effect=AssertionError), \
                    patch.object(rs,'power_two_solution',side_effect=AssertionError):
                self.assertTrue(rs.verify_periodic_phase_odd(certificate))
            self.assertLess(max(map(abs,certificate['values'])),10**51)
            self.assertFalse(any(abs(v)==1 for v in certificate['values']))
        for field,value in [('period',True),('period',4),('variables',True),
                            ('values',certificate['values'][:-1]),('hole',18),
                            ('literal_existence_decided',True),('all_pairs_decided',True)]:
            with self.assertRaises(ValueError):
                rs.verify_periodic_phase_odd(dict(certificate,**{field:value}))
        for value in (True,0,certificate['values'][0]+4):
            damaged=dict(certificate,values=list(certificate['values']))
            damaged['values'][0]=value
            with self.assertRaises(ValueError):rs.verify_periodic_phase_odd(damaged)

    def test_periodic_odd_restricts_to_compatible_translated_windows(self):
        for hole in (19,97):
            certificate=rs.periodic_phase_odd_example(hole)
            labels=rs.moving_folded_labels()
            periodic={(*label,j):certificate['values'][2*i+j]
                      for i,label in enumerate(labels) for j in range(2)}
            for first,length in ((3,3),(4,8),(99,7)):
                keys,_,_=rs.open_phase_system(hole,length,first)
                values=[periodic[(*key[:3],key[3]%2)] for key in keys]
                window=dict(kind='moving-open-phase-odd-v1',hole=hole,length=length,
                            first=first,variables=len(keys),values=values,
                            literal_existence_decided=False,all_pairs_decided=False)
                self.assertTrue(rs.verify_open_phase_odd(window))
                # The same absolute coordinate has the same value in every window.
                self.assertEqual(values[0],periodic[(*keys[0][:3],(first-1)%2)])
        with patch.object(rs,'rational_recovery',return_value={'complete':False}):
            with self.assertRaisesRegex(ValueError,'unknown'):
                rs.periodic_phase_odd_example(19)

    def test_periodic_odd_against_original_physical_columns(self):
        for hole in (19,97):
            certificate=rs.periodic_phase_odd_example(hole)
            word={(*label,j):certificate['values'][2*i+j]
                  for i,label in enumerate(rs.moving_folded_labels()) for j in range(2)}
            half=11; scale=2*half+1
            lengths=[n*scale for n in (99,79,23)]
            holes={(1,hole*scale),(1,99*scale)}; coordinates={(0,0):0}
            for arm,n in enumerate(lengths,1):
                for depth in range(1,n+1):
                    if (arm,depth) in holes: continue
                    q,level=divmod(depth,scale); orientation=1
                    if level>half: q+=1; level=scale-level; orientation=-1
                    coordinates[arm,depth]=word[arm,q,orientation,level%2] if level else 0
            residual=fc.shell_rows(lengths,holes,coordinates)
            self.assertFalse(any(v for e,v in residual.items()
                                 if 2<=min(e%scale,scale-e%scale)<=half-1))
            self.assertTrue(residual)  # The physical endpoints have not been solved.

    def test_phase_odd_rank_all_odd_holes_and_independent_replay(self):
        for hole in range(1,98,2):
            certificate=rs.phase_odd_rank_certificate(hole)
            with patch.object(rs,'phase_odd_rank_certificate',side_effect=AssertionError), \
                    patch.object(rs,'binary_elimination',side_effect=AssertionError):
                self.assertTrue(rs.verify_phase_odd_rank(certificate))
        for field,value in [('hole',18),('period',True),('variables',1),
                            ('bits','0x0'),('literal_existence_decided',True),
                            ('all_pairs_decided',True)]:
            damaged=dict(certificate);damaged[field]=value
            with self.assertRaises(ValueError):rs.verify_phase_odd_rank(damaged)
        damaged=dict(certificate,rank=dict(certificate['rank'],hole=19))
        with self.assertRaises(ValueError):rs.verify_phase_odd_rank(damaged)

    def test_odd_residue_lift_exact_arithmetic_and_scope(self):
        # The odd denominator three must be cleared with a multiplier 1 mod 4.
        self.assertEqual(rs.odd_residue_lift(2,[{0:3,1:1}],[1,1]),[1,-3])
        rows=[{0:3,1:1},{1:3,2:1}]
        values=rs.odd_residue_lift(3,rows,[1,1,1])
        self.assertTrue(all((x-1)%4==0 for x in values))
        self.assertTrue(all(sum(c*values[i] for i,c in row.items())==0 for row in rows))
        for rows,residues in [([{0:2,1:2}],[1,1]),([{0:3,1:1}],[1,-1]),
                              ([{0:3,1:1}],[True,1]),([{0:3,1:1}],[1])]:
            with self.assertRaises(ValueError):rs.odd_residue_lift(2,rows,residues)

    def test_open_phase_odd_exact_windows_and_damaged_values(self):
        for hole,first in [(19,4),(97,3)]:
            certificate=rs.open_phase_odd_example(hole,3,first)
            with patch.object(rs,'odd_residue_lift',side_effect=AssertionError), \
                    patch.object(rs,'binary_elimination',side_effect=AssertionError):
                self.assertTrue(rs.verify_open_phase_odd(certificate))
            self.assertGreater(max(map(abs,certificate['values'])),1)
            for field,value in [('variables',1),('values',certificate['values'][:-1]),
                                ('literal_existence_decided',True),('all_pairs_decided',True)]:
                with self.assertRaises(ValueError):
                    rs.verify_open_phase_odd(dict(certificate,**{field:value}))
            for value in [True,0,certificate['values'][0]+4]:
                damaged=dict(certificate,values=list(certificate['values']))
                damaged['values'][0]=value
                with self.assertRaises(ValueError):rs.verify_open_phase_odd(damaged)

    def test_binary_laurent_rank_has_independent_field_and_window_controls(self):
        def multiply(a,b):
            product=0
            while b:
                if b&1:product^=a
                b>>=1;a<<=1
            for power in range(product.bit_length()-1,1,-1):
                if product>>power&1:product^=7<<(power-2)
            return product
        for a in range(4):
            for b in range(4):
                self.assertEqual(rs._GF4_PRODUCTS[a][b],multiply(a,b))
            if a:self.assertEqual(multiply(a,rs._GF4_INVERSES[a]),1)
        for hole in (19,97):
            certificate=rs.interior_binary_rank_certificate(hole)
            self.assertEqual(certificate['rows'],356)
            self.assertTrue(rs.verify_interior_binary_rank_certificate(certificate))
            self.assertTrue(rs.verify_saved(certificate)['verified'])
            for length in (1,3,7):
                keys,rows,_=rs.open_phase_system(hole,length)
                refusal,basis=rs.binary_elimination(rows)
                self.assertIsNone(refusal)
                self.assertEqual(len(basis),len(rows))
                self.assertEqual(len(keys)-len(basis),46*length+804)

    def test_binary_laurent_rank_rejects_singular_minor_and_broader_scope(self):
        import copy
        certificate=rs.interior_binary_rank_certificate(19)
        for key,value in [('hole',2),('field_polynomial',5),('evaluation',3),
                          ('columns',list(range(356))),('columns',[0]*356),
                          ('rows',355),('variables',401),('odd_integer_windows_possible',False),
                          ('literal_existence_decided',True),('all_pairs_decided',True)]:
            damaged=copy.deepcopy(certificate);damaged[key]=value
            self.assertFalse(rs.verify_interior_binary_rank_certificate(damaged))
        with patch.object(rs,'interior_binary_rank_certificate',side_effect=AssertionError), \
             patch.object(rs,'_parity_trace_data',side_effect=AssertionError):
            self.assertTrue(rs.verify_interior_binary_rank_certificate(certificate))
        with self.assertRaises(ValueError):rs.interior_binary_rank_certificate(98)
        self.assertFalse(rs.verify_interior_binary_rank_certificate({}))

    def test_odd_integer_sign_flip_certificate_has_independent_integer_replay(self):
        for hole in (1,49,97):
            certificate=rs.antiperiod_two_odd_refusal(hole)
            self.assertEqual(certificate['status'],'refused')
            with patch.object(rs,'binary_shell_quadratics',side_effect=AssertionError), \
                 patch.object(rs,'rational_recovery',side_effect=AssertionError), \
                 patch.object(rs,'_parity_trace_data',side_effect=AssertionError):
                self.assertTrue(rs.verify_antiperiod_two_odd_refusal(certificate))
                self.assertTrue(rs.verify_saved(certificate)['verified'])
            rows=rs._antiperiod_two_odd_rows(hole)
            low,high=map(lambda v:int(v,16),certificate['weights'])
            combined=defaultdict(int)
            for index,row in enumerate(rows):
                for i,c in row.items():
                    combined[i]+=((low>>index&1)+2*(high>>index&1))*c
            self.assertTrue(all(c%4==0 for c in combined.values()))
            self.assertEqual(sum(c//4 for c in combined.values())%2,1)
        self.assertEqual(rs._antiperiod_two_system(19)[1],rs._periodic_phase_system(19,4)[1])

    def test_odd_integer_sign_flip_scope_and_weight_damage_rejected(self):
        import copy
        certificate=rs.antiperiod_two_odd_refusal(97)
        for key,value in [('hole',19),('hole',2),('period',8),('sign_shift',4),
                          ('shift_factor',1),('divisor',2),('divisor',4.0),
                          ('literal_existence_decided',True),('all_pairs_decided',True),
                          ('weights',['0x0','0x0']),('weights',['0x0']),
                          ('weights',['0x'+('f'*1000),'0x0'])]:
            damaged=copy.deepcopy(certificate);damaged[key]=value
            self.assertFalse(rs.verify_antiperiod_two_odd_refusal(damaged))
        damaged=copy.deepcopy(certificate)
        damaged['weights'][0]=hex(int(damaged['weights'][0],16)^1)
        self.assertFalse(rs.verify_antiperiod_two_odd_refusal(damaged))
        self.assertFalse(rs.verify_antiperiod_two_odd_refusal({}))
        for hole in (19,91):
            unknown=rs.antiperiod_two_odd_refusal(hole)
            self.assertEqual(unknown['status'],'unknown')
            self.assertNotIn('weights',unknown)
            self.assertFalse(rs.verify_antiperiod_two_odd_refusal(unknown))
        # The Boolean sign obstruction at91 is not silently strengthened to
        # an obstruction for all odd integers.
        self.assertEqual(rs.antiperiod_two_refusal(91)['status'],'refused')

    def test_antiperiod_two_input_span_refusal_replays_without_phase_laws(self):
        for hole in (1,49,91,97):
            certificate=rs.antiperiod_two_refusal(hole)
            self.assertEqual(certificate['status'],'refused')
            self.assertEqual(certificate['identity']['multipliers'],[])
            self.assertTrue(rs.verify_antiperiod_two_refusal(certificate))
            self.assertTrue(rs.verify_saved(certificate)['verified'])
        # Compilation can calculate trace laws, but this proof must not use
        # their endpoint phases as extra binary assumptions.
        size,rows,equations=rs._antiperiod_two_system(97)
        self.assertEqual(size,1608)
        self.assertEqual(len(rows),1424)
        self.assertEqual(len(equations),804)
        self.assertTrue(all(mask.bit_count()==2 and rhs==1 for mask,rhs in equations))

    def test_antiperiod_two_proof_rejects_damage_and_broader_scope(self):
        import copy
        certificate=rs.antiperiod_two_refusal(97)
        for key,value in [('hole',19),('period',2),('period',True),
                          ('sign_shift',4),('shift_factor',1),
                          ('free_count',0),('free_count',98.0),('literal_existence_decided',True),
                          ('all_pairs_decided',True),('status','unknown')]:
            damaged=copy.deepcopy(certificate);damaged[key]=value
            self.assertFalse(rs.verify_antiperiod_two_refusal(damaged))
        for key,value in [('raw',0),('raw',-1),('raw',1.0),('raw',1<<1424),
                          ('polynomial',0),('polynomial',True),('multipliers',[1])]:
            damaged=copy.deepcopy(certificate);damaged['identity'][key]=value
            self.assertFalse(rs.verify_antiperiod_two_refusal(damaged))
        self.assertFalse(rs.verify_antiperiod_two_refusal({}))
        for hole in (0,2,98,True,3.0):
            with self.assertRaises(ValueError):rs.antiperiod_two_refusal(hole)

    def test_antiperiod_two_no_input_span_refusal_remains_unknown(self):
        certificate=rs.antiperiod_two_refusal(19)
        self.assertEqual(certificate['status'],'unknown')
        self.assertNotIn('identity',certificate)
        self.assertFalse(certificate['literal_existence_decided'])
        self.assertFalse(certificate['all_pairs_decided'])
        self.assertFalse(rs.verify_antiperiod_two_refusal(certificate))
        with self.assertRaises(ValueError):rs.verify_saved(certificate)

    def test_antiperiod_two_constraints_are_exact_sign_reversals(self):
        size,rows,equations=rs._antiperiod_two_system(19)
        # Every assignment of two levels extends uniquely with sign flips.
        randomizer=random.Random(307)
        for _ in range(3):
            values=[randomizer.randrange(2) for _ in range(size//2)]
            bits=sum((values[2*(i//4)+i%2]^(i%4//2))<<i for i in range(size))
            self.assertTrue(all((bits&mask).bit_count()%2==rhs for mask,rhs in equations))
            damaged=bits^1
            self.assertFalse(all((damaged&mask).bit_count()%2==rhs for mask,rhs in equations))
        # Reversing two levels negates the original homogeneous row; rows
        # are not quietly replaced by a rational or ternary relaxation.
        width=len(rows)//4
        for level in range(2):
            for left,right in zip(rows[level*width:(level+1)*width],
                                  rows[(level+2)*width:(level+3)*width]):
                def quotient(row):
                    out=defaultdict(int)
                    for i,c in row.items():
                        label,position=divmod(i,4)
                        out[label*2+position%2]+=c*(-1 if position>=2 else 1)
                    return {i:c for i,c in out.items() if c}
                self.assertEqual(quotient(left),{i:-c for i,c in quotient(right).items()})

    def test_recorded_open_windows_satisfy_all_original_integer_rows(self):
        for hole in (19,43,97):
            for first in (3,4,11,20):
                if hole==43 and first%2==0:
                    with self.assertRaises(ValueError):rs.open_phase_example(hole,first)
                    continue
                certificate=rs.open_phase_example(hole,first)
                self.assertTrue(rs.verify_open_phase_signs(certificate))
                bits=int(certificate['bits'],16)
                length=3 if hole==43 else 2
                _,rows,equations=rs.open_phase_system(hole,length,first)
                self.assertEqual(len(rows),356*length)
                self.assertTrue(all(sum(c*(1-2*(bits>>i&1)) for i,c in row.items())==0
                                    for row in rows))
                self.assertTrue(all((mask&bits).bit_count()%2==rhs for mask,rhs in equations))
        with self.assertRaises(ValueError):rs.open_phase_example(1)
        with self.assertRaises(ValueError):rs.open_phase_example(19,2)
        certificate=rs.open_phase_example(43)
        _,rows,_=rs.open_phase_system(43,3,3)
        changed=int(certificate['bits'],16)^(1<<next(iter(rows[0])))
        with self.assertRaises(ValueError):
            rs.verify_open_phase_signs(dict(certificate,bits=hex(changed)))

    def test_recorded_windows_are_not_unchecked_constructions(self):
        # These particular words cannot simply be extended: the next
        # centre already has a nonzero shell row using only fixed signs.
        for hole in (19,97):
            certificate=rs.open_phase_example(hole)
            bits=int(certificate['bits'],16)
            oldkeys,_,_=rs.open_phase_system(hole,2,3)
            values={k:1-2*(bits>>i&1) for i,k in enumerate(oldkeys)}
            keys,rows,_=rs.open_phase_system(hole,3,3)
            row_keys=list(rs.moving_folded_stencils(hole)[1])
            next_row=rows[2*len(row_keys)+row_keys.index((0,1))]
            self.assertTrue(all(keys[i] in values for i in next_row))
            self.assertEqual(sum(c*values[keys[i]] for i,c in next_row.items()),-2)
        # The new three-centre word also needs repair before extension.
        certificate=rs.open_phase_example(43)
        bits=int(certificate['bits'],16)
        oldkeys,_,_=rs.open_phase_system(43,3,3)
        values={k:1-2*(bits>>i&1) for i,k in enumerate(oldkeys)}
        keys,rows,_=rs.open_phase_system(43,4,3)
        contained=[row for row in rows[1068:] if all(keys[i] in values for i in row)]
        self.assertEqual(len(contained),178)
        self.assertEqual(sum(bool(sum(c*values[keys[i]] for i,c in row.items()))
                             for row in contained),74)

    def test_open_window_rows_match_physical_columns_without_identifying_ends(self):
        for hole in (19,43,97):
            first,length=3,3 if hole==43 else 4
            scale=2*(first+length+1)+1  # The advertised minimum half-length.
            coordinates,rows,equations=rs.open_phase_system(hole,length,first)
            positions={k:i for i,k in enumerate(coordinates)}
            expected=defaultdict(lambda:defaultdict(int))
            lengths=[n*scale for n in (99,79,23)]
            holes={(1,hole*scale),(1,99*scale)}
            for arm,n in enumerate(lengths,1):
                for depth in range(1,n+1):
                    q,r=divmod(depth,scale)
                    if not r:continue
                    if r>scale//2:q,r,orientation=q+1,scale-r,-1
                    else:orientation=1
                    for exponent,c in fc.shell_column(lengths,holes,(arm,depth)).items():
                        expected[exponent][arm,q,orientation,r]+=c
            row_keys=list(rs.moving_folded_stencils(hole)[1])
            for level in range(first,first+length):
                for offset,(q,orientation) in enumerate(row_keys):
                    physical=expected[q*scale+orientation*level]
                    self.assertTrue(all(k in positions for k,c in physical.items() if c))
                    self.assertEqual({positions[k]:c for k,c in physical.items() if c},
                                     rows[(level-first)*len(row_keys)+offset])
            # Both boundary levels are actual distinct coordinates, even
            # though an even periodic quotient would alias some of them.
            self.assertEqual(len(coordinates),402*(length+2))
            for label in rs.moving_folded_labels():
                self.assertNotEqual(positions[(*label,first-1)],positions[(*label,first+length)])
            self.assertEqual(len(equations),5*length)
        for length,first in ((0,3),(True,3),(65,3),(1,2),(1,3.0)):
            with self.assertRaises(ValueError):rs.open_phase_system(19,length,first)

    def test_open_window_positive_search_and_damaged_witness(self):
        certificate=rs.open_phase_search(19,1,3,seconds=10,nodes=10000)
        self.assertEqual(certificate['status'],'local_signing')
        self.assertTrue(rs.verify_open_phase_signs(certificate))
        verified=rs.verify_saved(certificate)
        self.assertFalse(verified['literal_existence_decided'])
        self.assertFalse(verified['all_pairs_decided'])
        _,rows,_=rs.open_phase_system(19,1,3)
        active=next(iter(rows[0]))
        for key,value in (('bits',hex(int(certificate['bits'],16)^(1<<active))),
                          ('bits','0x'+('f'*10000)),('first',4),('minimum_half',99),
                          ('literal_existence_decided',True),('all_pairs_decided',True)):
            damaged=dict(certificate);damaged[key]=value
            with self.assertRaises(ValueError):rs.verify_open_phase_signs(damaged)
        with self.assertRaises(ValueError):rs.open_phase_search(seconds=float('inf'))

    def test_quadratic_consequences_are_checked_reused_and_resumed(self):
        # xy=x and yz=y imply xy=xz, a new quadratic relation.
        polynomials=[18,68]
        with self.assertRaises(ValueError):rs.cubic_shell_analysis(3,[],retain_quadratics=True)
        result=rs.boolean_cubic_lift(polynomials,3,proof=True,quadratic_limit=16)
        identities=result['quadratic_proof']
        self.assertEqual([i['polynomial'] for i in identities],[48])
        self.assertEqual(rs.append_checked_quadratics(polynomials,3,identities),[18,68,48])
        compiled=dict(complete=True,parity_conflict=False,free=[0,1,2],
                      quadratic_rows=[(9,0),(34,0)])
        with patch.object(rs,'binary_shell_quadratics',return_value=compiled):
            analysis=rs.cubic_shell_analysis(3,[],proof=True,retain_quadratics=True)
            self.assertEqual(analysis['cubic_proof'],[dict(quadratics=identities)])
            replay=rs.cubic_shell_analysis(3,[],proof=True,initial_proofs=analysis['cubic_proof'])
            self.assertEqual(replay['remaining_variables'],3)
            self.assertEqual(replay['cubic_proof'],analysis['cubic_proof'])
            with self.assertRaises(ValueError):
                rs.verify_cubic_shell_proof(3,[],analysis['cubic_proof'])
        damaged=dict(identities[0]);damaged['polynomial']^=1
        for bad in ([damaged],identities+identities,[],[None]):
            with self.assertRaises(ValueError):rs.append_checked_quadratics(polynomials,3,bad)
        limited=rs.boolean_cubic_lift(polynomials,3,proof=True,max_pivots=1,quadratic_limit=16)
        self.assertEqual(limited.get('quadratic_proof',[]),[])

    def test_quadratic_round_followed_by_a_checked_contradiction(self):
        polynomials=[18,68,3,8]  # Also x=1 and z=0: inconsistent.
        identity=dict(polynomial=48,raw=0,multipliers=[4,1,0,0])
        expanded=rs.append_checked_quadratics(polynomials,3,[identity])
        final=rs.boolean_cubic_lift(expanded,3,proof=True)
        self.assertEqual(final['status'],'refused')
        proofs=[dict(quadratics=[identity]),final['proof']]
        compiled=dict(complete=True,parity_conflict=False,free=[0,1,2],
                      quadratic_rows=[(q>>1,q&1) for q in polynomials])
        with patch.object(rs,'binary_shell_quadratics',return_value=compiled):
            self.assertTrue(rs.verify_cubic_shell_proof(3,[],proofs))
            with self.assertRaises(ValueError):
                rs.verify_cubic_shell_proof(3,[],[proofs[0],proofs[0],proofs[1]])
            with self.assertRaises(ValueError):
                rs.cubic_shell_analysis(3,[],proof=True,
                    initial_proofs=[dict(quadratics=[identity],untrusted=True)])

    def test_linear_consequences_are_used_before_cubic_products(self):
        # x+xy=0 and y+xy=0 already imply x=y by addition alone.
        # A product pass cannot improve that reduction's provenance.
        polynomials=[10,12]
        result=rs.boolean_cubic_lift(polynomials,2,proof=True,linear_first=True)
        self.assertEqual(result['stage'],'linear_reduction')
        self.assertEqual(result['products'],0)
        self.assertEqual(result['proof'][0]['polynomial'],6)
        self.assertTrue(rs.verify_boolean_cubic_identity(polynomials,2,result['proof'][0]))
        self.assertTrue(all(not m for m in result['proof'][0]['multipliers']))
        compiled=dict(complete=True,parity_conflict=False,free=[0,1],
                      quadratic_rows=[(5,0),(6,0)])
        with patch.object(rs,'binary_shell_quadratics',return_value=compiled):
            analysis=rs.cubic_shell_analysis(2,[],proof=True)
        self.assertEqual(analysis['remaining_variables'],1)
        self.assertEqual(analysis['history'][0]['stage'],'linear_reduction')
        self.assertEqual(analysis['history'][0]['products'],0)
        self.assertEqual(analysis['recovery'][0],analysis['recovery'][1])

    def test_packed_boolean_products_against_monomial_sets(self):
        rng=random.Random(3111)
        for n in (4,16):
            terms=[()]+[(i,) for i in range(n)]+[(i,j) for j in range(n) for i in range(j)]
            all_terms=terms+[(i,j,k) for k in range(n) for j in range(k) for i in range(j)]
            positions={term:i for i,term in enumerate(all_terms)}
            for variable in (0,n//2,n-1):
                products=[tuple(sorted(set(term)|{variable})) for term in terms]
                mapping=[positions[term] for term in products]
                for count in (1,min(63,len(terms)),min(64,len(terms)),len(terms)//2):
                    selected=rng.sample(range(len(terms)),count)
                    polynomial=sum(1<<i for i in selected)
                    expected=set()
                    for i in selected:expected.symmetric_difference_update((products[i],))
                    result=rs._mapped_boolean_product(polynomial,mapping,(len(all_terms)+7)//8)
                    self.assertEqual(result,sum(1<<positions[term] for term in expected))
        # Arbitrary wide maps test packing independently of the monomial
        # index formula, including collisions that must cancel by XOR.
        for width in (188,192):
            output_bits=1+width+width*(width-1)//2+width*(width-1)*(width-2)//6
            mapping=[rng.randrange(output_bits) for _ in range(200)]
            mapping[0]=mapping[1]
            for count in (1,63,64,128,200):
                selected=rng.sample(range(200),count)
                expected=set()
                for i in selected:expected.symmetric_difference_update((mapping[i],))
                result=rs._mapped_boolean_product(sum(1<<i for i in selected),mapping,(output_bits+7)//8)
                self.assertEqual(result,sum(1<<i for i in expected))

    def test_capped_sweep_finds_a_later_checked_contradiction(self):
        # Three Boolean equations with no common assignment. The first
        # variable's products fill a four-pivot store before a later product
        # exposes 1=0. Discarded rows must never become proof premises.
        polynomials=[33,70,124]
        old=rs.boolean_cubic_lift(polynomials,3,max_pivots=4,proof=True)
        self.assertEqual(old['status'],'unknown')
        result=rs.boolean_cubic_lift(polynomials,3,max_pivots=4,proof=True,sweep=True)
        self.assertEqual(result['status'],'refused')
        self.assertGreater(result['discarded'],0)
        self.assertLessEqual(result['rank'],4+3+1)
        self.assertEqual(result['proof'][0]['polynomial'],1)
        self.assertTrue(rs.verify_boolean_cubic_identity(polynomials,3,result['proof'][0]))
        damaged=dict(result['proof'][0]);damaged['raw']^=1
        with self.assertRaises(ValueError):
            rs.verify_boolean_cubic_identity(polynomials,3,damaged)

    def test_capped_sweep_consequences_against_exhaustive_models(self):
        rng=random.Random(3107)
        for n in range(2,6):
            # The implementation uses colexicographic pair order.
            terms=[()]+[(i,) for i in range(n)]+[(i,j) for j in range(n) for i in range(j)]
            def evaluate(polynomial,assignment):
                return sum(all(assignment>>i&1 for i in term)
                           for j,term in enumerate(terms) if polynomial>>j&1)%2
            for _ in range(25):
                polynomials=[rng.randrange(1,1<<len(terms)) for _ in range(n)]
                models=[a for a in range(1<<n)
                        if all(evaluate(q,a)==0 for q in polynomials)]
                cap=n+1
                result=rs.boolean_cubic_lift(polynomials,n,max_pivots=cap,proof=True,sweep=True)
                self.assertLessEqual(result['rank'],cap+n+1)
                if result['discarded']:
                    self.assertNotEqual(result['status'],'compatible_cubic_relaxation')
                if result['status']=='refused':self.assertEqual(models,[])
                for identity in result['proof']:
                    self.assertTrue(rs.verify_boolean_cubic_identity(polynomials,n,identity))
                    self.assertTrue(all(evaluate(identity['polynomial'],a)==0 for a in models))

    def test_resume_rechecks_partial_boolean_identities(self):
        # Independent algebraic control: x+xy=0 and y+xy=0 imply x=y.
        compiled=dict(complete=True,parity_conflict=False,free=[0,1],
                      quadratic_rows=[(5,0),(6,0)])
        identity=dict(raw=3,multipliers=[],polynomial=6)
        with patch.object(rs,'binary_shell_quadratics',return_value=compiled):
            result=rs.cubic_shell_analysis(2,[],proof=True,initial_proofs=[[identity]])
            self.assertEqual(result['remaining_variables'],1)
            self.assertEqual(result['recovery'][0],result['recovery'][1])
            self.assertEqual(result['cubic_proof'][0],[identity])
            damaged=dict(identity);damaged['polynomial']^=1
            with self.assertRaises(ValueError):
                rs.cubic_shell_analysis(2,[],proof=True,initial_proofs=[[damaged]])
        inconsistent=dict(compiled,quadratic_rows=[(5,0),(6,0),(1,0),(2,1)])
        with patch.object(rs,'binary_shell_quadratics',return_value=inconsistent):
            result=rs.cubic_shell_analysis(2,[],proof=True,initial_proofs=[[identity]])
            self.assertEqual(result['status'],'refused')
            self.assertTrue(rs.verify_cubic_shell_proof(2,[],result['cubic_proof']))
        for prior in ({},dict(kind='moving-periodic-phase-v1',hole=97,period=4)):
            with self.assertRaises(ValueError):
                rs.periodic_phase_refusal(19,4,seconds=5,prior=prior)

    def test_general_phase_refusal_roundtrip_and_scope_damage(self):
        certificate=rs.periodic_phase_refusal(97,2,seconds=120,max_pivots=40000)
        self.assertEqual(certificate['status'],'refused')
        self.assertTrue(rs.verify_saved(certificate)['verified'])
        for key,value in (('period',4),('period',3),('hole',19),
                          ('all_pairs_decided',True),('literal_existence_decided',True),
                          ('cubic_proof',[]),('status','unknown')):
            damaged=dict(certificate);damaged[key]=value
            self.assertFalse(rs.verify_periodic_phase_refusal(damaged))

    def test_periodic_phase_rows_against_original_physical_columns(self):
        # Independently fold physical vertices, then compare each interior
        # coefficient, rather than evaluating only selected sign assignments.
        for period in (4,6):
            scale,hole=23,19
            labels=rs.moving_folded_labels()
            positions={k:i for i,k in enumerate(labels)}
            _,rows,_=rs._periodic_phase_system(hole,period)
            stencils=rs.moving_folded_stencils(hole)[1]
            expected=defaultdict(lambda:defaultdict(int))
            lengths=[n*scale for n in (99,79,23)]
            holes={(1,hole*scale),(1,99*scale)}
            for arm,n in enumerate(lengths,1):
                for depth in range(1,n+1):
                    q,r=divmod(depth,scale)
                    if not r:continue
                    if r>scale//2:q,r,orientation=q+1,scale-r,-1
                    else:orientation=1
                    index=positions[arm,q,orientation]*period+r%period
                    for exponent,c in fc.shell_column(lengths,holes,(arm,depth)).items():
                        expected[exponent][index]+=c
            keys=list(stencils)
            for level in range(3,3+period):
                for offset,(q,orientation) in enumerate(keys):
                    physical={i:c for i,c in expected[q*scale+orientation*level].items() if c}
                    self.assertEqual(physical,rows[(level%period)*len(keys)+offset])

    def test_even_period_phase_system_projects_to_period_two(self):
        size2,rows2,equations2=rs._period_two_phase_system(19)
        labels=rs.moving_folded_labels()
        for period in (4,6):
            size,rows,equations=rs._periodic_phase_system(19,period)
            self.assertEqual(size,len(labels)*period)
            def project(row):
                out=defaultdict(int)
                for i,c in row.items():
                    label,phase=divmod(i,period)
                    out[2*label+phase%2]+=c
                return {i:c for i,c in out.items() if c}
            count=len(rows2)//2
            for level in range(period):
                self.assertEqual([project(r) for r in rows[level*count:(level+1)*count]],
                                 rows2[(level%2)*count:(level%2+1)*count])
            for index,(mask,rhs) in enumerate(equations):
                folded=0
                while mask:
                    bit=mask&-mask;mask^=bit
                    label,phase=divmod(bit.bit_length()-1,period)
                    folded^=1<<(2*label+phase%2)
                self.assertEqual((folded,rhs),equations2[index%10])
        for invalid in (0,1,3,True,4.0):
            with self.assertRaises(ValueError):rs._periodic_phase_system(19,invalid)

    def test_wide_cubic_proof_and_sparse_monomial_indices(self):
        # Multiply q=(1+x_0*x_last) by x_0; the retained linear identity
        # exercises high triple positions without constructing all triples.
        for variables in (3,128,188,192):
            pair=1+variables+(variables-1)*(variables-2)//2
            polynomials=[1|(1<<pair),1<<1]
            result=rs.boolean_cubic_lift(polynomials,variables,seconds=10,
                                         max_pivots=20,proof=True)
            self.assertEqual(result['status'],'refused')
            for identity in result['proof']:
                self.assertTrue(rs.verify_boolean_cubic_identity(polynomials,variables,identity))
            bad=dict(result['proof'][0]);bad['polynomial']^=2
            with self.assertRaises(ValueError):
                rs.verify_boolean_cubic_identity(polynomials,variables,bad)
        with self.assertRaises(ValueError):
            rs.boolean_cubic_lift([],193)
        free,expressions=rs.boolean_linear_substitution(188,[2^4])
        self.assertEqual(len(free),187)
        self.assertEqual(expressions[0],expressions[1])
        self.assertEqual(rs.substitute_boolean_quadratics([2^4],expressions,187),[0])

    def test_cubic_proof_with_explicit_additional_binary_conditions(self):
        rows = [{i:1 for i in range(4)}]
        extra = [(1,0),(2,0),(4,0)]
        # These phases force all four signs positive. The row is zero mod four
        # but not mod eight, so the contradiction has a one-input certificate.
        analysis = rs.cubic_shell_analysis(4,rows,proof=True,extra_binary=extra)
        self.assertEqual(analysis['status'],'refused')
        self.assertTrue(rs.verify_cubic_shell_proof(4,rows,analysis['cubic_proof'],extra))
        with self.assertRaises(ValueError):
            rs.verify_cubic_shell_proof(4,rows,analysis['cubic_proof'])
        conflict = rs.binary_shell_quadratics(4,rows,extra_binary=[(15,1)])
        self.assertTrue(conflict['parity_conflict'])
        for equation in ((16,0),(-1,0),(1,2),(True,0)):
            with self.assertRaises(ValueError):
                rs.binary_shell_quadratics(4,rows,extra_binary=[equation])
        with patch.object(rs,'joint_sign_closure',side_effect=AssertionError('quotient entered')):
            size,original,equations = rs._period_two_phase_system(19)
        self.assertEqual((size,len(original),len(equations)),(804,712,10))
        compiled = rs.binary_shell_quadratics(size,original,extra_binary=equations)
        self.assertEqual(len(compiled['free']),94)
        for mask,rhs in equations:
            residual = 0
            for i in range(size):
                if mask>>i&1:
                    a,b = compiled['expressions'][i]; residual ^= a; rhs ^= b
            self.assertEqual((residual,rhs),(0,0))
        # Scoped refusal checks reject missing proof and unsupported claims.
        for certificate in ({'kind':'moving-period-two-phase-v1','status':'unknown'},
                            {'kind':'moving-period-two-phase-v1','status':'refused',
                             'all_pairs_decided':True}):
            self.assertFalse(rs.verify_period_two_phase_refusal(certificate))

    def test_mod_four_completion_every_odd_support_and_damage(self):
        for hole in range(1,99,2):
            for parity in (0,1):
                certificate = rs.parity_completion_certificate(hole,parity)
                self.assertTrue(rs.verify_saved(certificate)['verified'])
        for hole in (2,42,98):
            with self.assertRaises(ValueError): rs.parity_completion_certificate(hole)
        certificate = rs.parity_completion_certificate(89)
        for change in ({'minimum_half':17},{'patch':5},{'period':4},
                       {'half_parity':2},{'bits':'-1'},{'bits':'0'},
                       {'bits':'0x1'+'0'*certificate['variables']},
                       {'literal_existence_decided':True},{'all_pairs_decided':True}):
            self.assertFalse(rs.verify_parity_completion_certificate(certificate|change))
        with patch.object(rs,'binary_elimination',side_effect=AssertionError('solver entered')):
            self.assertTrue(rs.verify_saved(certificate)['verified'])

    def test_mod_four_completion_expanded_into_physical_shells(self):
        for half,hole in ((18,19),(19,89),(20,97),(23,89)):
            certificate = rs.parity_completion_certificate(hole,half%2)
            keys,_ = rs.compile_moving_folded(18+half%2,2,6,hole)
            bits = int(certificate['bits'],16)
            signs = {key:1-2*(bits>>i&1) for i,key in enumerate(keys)}
            scale = 2*half+1
            lengths = [n*scale for n in (99,79,23)]
            holes = {(1,hole*scale),(1,99*scale)}
            residual = defaultdict(int)
            for arm,n in enumerate((0,*lengths)):
                for depth in (range(1,n+1) if arm else (0,)):
                    if (arm,depth) in holes: continue
                    q,level = divmod(depth,scale)
                    orientation = 1
                    if level>half:
                        q += 1; level = scale-level; orientation = -1
                    if level<=6:
                        key = ('left',arm,q,orientation*level)
                    elif level>=half-6:
                        key = ('right',arm,q,orientation,level-half)
                    else:
                        key = ('period',arm,q,orientation,level%2)
                    for distance,c in fc.shell_column(lengths,holes,(arm,depth)).items():
                        residual[distance] += c*signs[key]
            self.assertTrue(all(v%4==0 for v in residual.values()),(half,hole))
            self.assertTrue(any(residual.values())) # This witness is not an integer solution.

    def test_complete_parity_traces_all_supports_and_damaged_certificates(self):
        import copy
        for hole in range(1,99):
            certificate = rs.parity_trace_certificate(hole)
            self.assertTrue(rs.verify_parity_trace_certificate(certificate),hole)
            self.assertEqual(rs.verify_saved(certificate)['drift'],[1,1,1,1,0])
        certificate = rs.parity_trace_certificate(19)
        mutations = []
        for path,value in ((('hole',),0),(('all_pairs_decided',),True),
                           (('phases_at_two',),[1,0,0,0,0]),
                           (('laws',1,'drift'),0),
                           (('laws',2,'observable'),[]),
                           (('endpoints','left',1,'phase'),0),
                           (('endpoints','right',0,'mask'),1),
                           (('endpoints','right',2,'shell_rows'),[])):
            damaged = copy.deepcopy(certificate)
            target = damaged
            for key in path[:-1]: target = target[key]
            target[path[-1]] = value
            mutations.append(damaged)
        for damaged in mutations:
            self.assertFalse(rs.verify_parity_trace_certificate(damaged))
            with self.assertRaises(ValueError): rs.verify_saved(damaged)
        # The separate verifier must not ask the producer to approve its output.
        with patch.object(rs,'parity_trace_certificate',side_effect=AssertionError('producer entered')):
            self.assertTrue(rs.verify_saved(certificate)['verified'])

    def test_parity_trace_phases_against_physical_shell_rows(self):
        # Independent physical matrix, with every level distinct and no period.
        # Carry augmented right sides in a fresh elimination, then ask whether
        # each predicted observable is actually implied by physical equations.
        # Odd h: even h already has the known odd-distance obstruction.
        for scale,hole in ((9,1),(9,19),(9,97),(11,19)):
            lengths = [n*scale for n in (99,79,23)]
            holes = {(1,hole*scale),(1,99*scale)}
            vertices = [(0,0)]+[(a,d) for a,n in enumerate(lengths,1)
                               for d in range(1,n+1) if (a,d) not in holes]
            positions = {v:i for i,v in enumerate(vertices)}
            rows = defaultdict(dict)
            for vertex in vertices:
                for distance,c in fc.shell_column(lengths,holes,vertex).items():
                    if c: rows[distance][vertex] = c
            basis = {}
            for row in rows.values():
                self.assertEqual(sum(row.values())%2,0)
                v = sum(1<<positions[k] for k,c in row.items() if c%2)
                rhs = sum(row.values())//2%2
                while v:
                    pivot = v.bit_length()-1
                    if pivot not in basis:
                        basis[pivot] = v,rhs
                        break
                    w,b = basis[pivot]; v ^= w; rhs ^= b
                if not v: self.assertEqual(rhs,0)
            laws = rs.parity_trace_certificate(hole)['laws']
            for level in range(2,scale//2+1):
                for i,law in enumerate(laws):
                    v = 0
                    for a,q,s,d in law['observable']:
                        v ^= 1<<positions[a,q*scale+s*(level+d)]
                    rhs = 0
                    while v:
                        pivot = v.bit_length()-1
                        self.assertIn(pivot,basis)
                        w,b = basis[pivot]; v ^= w; rhs ^= b
                    expected = ((level-1)%2 if i<2 else level%2 if i<4 else 0)
                    self.assertEqual(rhs,expected,(scale,hole,level,i))

    def test_odd_period_driver_uses_checked_interior_refusal(self):
        for period,hole in ((1,19),(3,97),(5,1)):
            half = 8+period
            with patch.object(rs,'joint_sign_closure',side_effect=AssertionError('search entered')):
                saved = rs.moving_folded_search(half,period,2,hole)
            self.assertEqual(saved['status'],'ansatz_refused_by_interior_cocycle')
            self.assertTrue(rs.verify_saved(saved)['verified'])
            for change in ({'hole':hole+1},{'half':half-1},
                           {'certificate':saved['certificate']|{'rhs':0}},
                           {'period':2,'minimum_half':10,'half_residue':half%2},
                           {'all_pairs_decided':True}):
                with self.assertRaises(ValueError): rs.verify_saved(saved|change)
        with patch.object(rs,'interior_parity_cocycle',side_effect=AssertionError('even period filtered')):
            with patch.object(rs,'joint_sign_closure',return_value={
                    'history':[],'conflict':False,'complete':False}):
                result = rs.moving_folded_search(12,2,2,19)
        self.assertNotEqual(result['status'],'ansatz_refused_by_interior_cocycle')

    def test_unrestricted_cocycle_all_supports_and_damage(self):
        for hole in range(1,99):
            certificate = rs.interior_parity_cocycle(hole)
            self.assertEqual(len(certificate['shell_rows']),176)
            self.assertEqual(len(certificate['left_rows']),264)
            # Independent closed formula from the physical column exponents.
            # The first/last-arm cross lengths 79 and 23 agree modulo eight.
            f = lambda q: int(q%8>=4)
            expected = set()
            for a,q,orientation in rs.moving_folded_labels():
                if a==1:
                    before = q<hole or (q==hole and orientation==-1)
                    direct = f(q) if before else f(q)^f(q-hole)
                    reflected = f(hole-q) if before else 0
                else:
                    direct = f(q)^f(q+7)^f(q+hole)
                    reflected = f(7-q)
                minus,plus = ((direct,reflected) if orientation==1
                              else (reflected,direct))
                if minus: expected.add((a,q,orientation,-1))
                if plus: expected.add((a,q,orientation,0))
            self.assertEqual(set(map(tuple,certificate['observable'])),expected)
            self.assertTrue(rs.verify_interior_parity_cocycle(certificate))
            self.assertEqual(rs.verify_saved(certificate)['initial_phase'],1)
            for change in ({'rhs':0},{'initial_phase':0},{'hole':0},
                           {'shell_rows':certificate['shell_rows'][:-1]},
                           {'left_rows':certificate['left_rows'][:-1]},
                           {'observable':certificate['observable'][:-1]},
                           {'observable':certificate['observable']*2},
                           {'all_pairs_decided':True},
                           {'literal_existence_decided':True}):
                damaged = certificate | change
                self.assertFalse(rs.verify_interior_parity_cocycle(damaged))
                with self.assertRaises(ValueError): rs.verify_saved(damaged)

    def test_cocycle_against_independent_distance_shells(self):
        # Build K columns by directly counting distances in the retained tree.
        # Neither the folded stencil compiler nor shell_column constructs them.
        for scale,hole in ((9,19),(11,97)):
            lengths = [99*scale,79*scale,23*scale]
            holes = {(1,hole*scale),(1,99*scale)}
            vertices = [(0,0)]+[(a,d) for a,n in enumerate(lengths,1)
                                for d in range(1,n+1) if (a,d) not in holes]
            certificate = rs.interior_parity_cocycle(hole)
            half = scale//2
            checks = []
            initial_rows = {q*scale+d for q,d in certificate['left_rows']}
            initial = set()
            for a,q,s,d in certificate['observable']:
                v = a,q*scale+s*(2+d)
                initial.symmetric_difference_update((v,))
            checks.append((initial_rows,initial))
            for level in range(2,half):
                shell_rows = {q*scale+s*level for q,s in certificate['shell_rows']}
                difference = set()
                for a,q,s,d in certificate['observable']:
                    for shift in (0,1):
                        v = a,q*scale+s*(level+d+shift)
                        difference.symmetric_difference_update((v,))
                checks.append((shell_rows,difference))
            sums = [0]*len(checks)
            for v in vertices:
                shell = defaultdict(int)
                for w in vertices:
                    if w==v: continue
                    distance = abs(v[1]-w[1]) if v[0]==w[0] else v[1]+w[1]
                    shell[distance] += 1
                column = defaultdict(int,{1:-2})
                for distance,count in shell.items():
                    column[distance] += count
                    column[distance+1] -= count
                for i,(rows,expected) in enumerate(checks):
                    value = sum(column.get(e,0) for e in rows)
                    self.assertEqual(value%2,int(v in expected))
                    sums[i] += value
            self.assertTrue(all(total%4==2 for total in sums))

    def test_cocycle_matches_periodic_binary_systems(self):
        labels = rs.moving_folded_labels()
        positions = {key:i for i,key in enumerate(labels)}
        for hole in (1,19,43,97,98):
            stencils = rs.moving_folded_stencils(hole)[1]
            for period in (1,2,3,4):
                rows = []
                for level in range(period):
                    for terms in stencils.values():
                        row = defaultdict(int)
                        for (a,q,s,d),c in terms.items():
                            row[((level+d)%period)*402+positions[a,q,s]] += c
                        rows.append({i:c for i,c in row.items() if c})
                refusal,_ = rs.binary_elimination(rows)
                self.assertEqual(refusal is not None,period%2==1)
                # Even-period compatibility here is only a binary relaxation.

    def test_unrestricted_interior_minor_and_damaged_certificate(self):
        for hole in (1,19,43,79,97,98):
            certificate = rs.interior_rank_certificate(hole)
            self.assertEqual(certificate['rows'],356)
            self.assertEqual(certificate['variables'],402)
            self.assertEqual(certificate['free_arm'],3)
            self.assertEqual(certificate['columns'],list(range(356)))
            self.assertTrue(rs.verify_interior_rank_certificate(certificate))
            report = rs.verify_saved(certificate)
            self.assertEqual(report['rational_function_nullity'],46)
            self.assertFalse(report['literal_existence_decided'])
            for change in ({'hole':0},{'prime':4},{'evaluation':1},
                           {'columns':certificate['columns'][:-1]},
                           {'columns':[0]*356},{'variables':401},
                           {'free_arm':1},
                           {'all_pairs_decided':True},
                           {'literal_existence_decided':True}):
                damaged = certificate | change
                self.assertFalse(rs.verify_interior_rank_certificate(damaged))
                with self.assertRaises(ValueError):rs.verify_saved(damaged)

    def test_interior_specialization_matches_integer_stencil_evaluation(self):
        labels,actual = rs.interior_rank_matrix(19)
        # Multiply by two to clear every possible z^-1 term first;
        # specialization and reduction must commute, including cancellation.
        expected = []
        for _,terms in sorted(rs.moving_folded_stencils(19)[1].items()):
            row = defaultdict(int)
            for (a,q,s,d),c in terms.items():
                self.assertIn(d,(-1,0,1))
                row[labels.index((a,q,s))] += c*2**(d+1)
            expected.append({i:c*3%5 for i,c in row.items() if c%5})
        self.assertEqual(actual,expected)

    def test_finite_unrestricted_interior_windows_have_predicted_rank(self):
        labels = rs.moving_folded_labels()
        positions = {label:i for i,label in enumerate(labels)}
        for hole in (1,19,98):
            stencils = rs.moving_folded_stencils(hole)[1]
            for width in (3,4,7):
                rows = [{(r+d)*402+positions[a,q,s]:c
                         for (a,q,s,d),c in row.items()}
                        for r in range(1,width-1) for row in stencils.values()]
                report = rs.ternary_analysis(402*width,rows)
                self.assertTrue(report['complete'])
                self.assertEqual(report['rank'],356*(width-2))
                self.assertEqual(report['nullity'],46*width+712)

    def test_boolean_cubic_lift_matches_independent_macaulay_space(self):
        rng=random.Random(3759)
        for n in range(1,6):
            monomials=[frozenset()]+[frozenset((i,)) for i in range(n)]
            monomials += [frozenset((i,j)) for j in range(n) for i in range(j)]
            cubic=monomials+[frozenset((i,j,k)) for k in range(n)
                             for j in range(k) for i in range(j)]
            positions={m:i for i,m in enumerate(cubic)}
            for _ in range(12):
                rows=[rng.getrandbits(len(monomials)) for _ in range(3)]
                reference=[]
                for row in rows:
                    reference.append(row)
                    for variable in range(n):
                        multiplied=0
                        for i,term in enumerate(monomials):
                            if row>>i&1:multiplied ^= 1<<positions[term|{variable}]
                        reference.append(multiplied)
                basis={}
                for row in reference:
                    while row:
                        pivot=row.bit_length()-1
                        if pivot not in basis:basis[pivot]=row;break
                        row ^= basis[pivot]
                report=rs.boolean_cubic_lift(rows,n)
                self.assertTrue(report['complete'])
                self.assertEqual(report['status']=='refused',0 in basis)
                if 0 not in basis:self.assertEqual(report['rank'],len(basis))
                for value in range(1<<n):
                    def evaluate(polynomial,terms):
                        return sum(all(value>>j&1 for j in term)
                                   for i,term in enumerate(terms) if polynomial>>i&1)%2
                    if any(evaluate(row,monomials) for row in rows):continue
                    self.assertNotEqual(report['status'],'refused')
                    for row in report['linear_polynomials']:
                        self.assertEqual(evaluate(row,cubic),0)

    def test_boolean_cubic_detects_product_incompatibility_and_limits(self):
        # xy=1, xz=0, yz=1 has compatible independent product values,
        # but no binary x,y,z. Multiplication exposes the contradiction.
        rows=[(1<<4)|1,1<<5,(1<<6)|1]
        result=rs.boolean_cubic_lift(rows,3)
        self.assertEqual(result['status'],'refused')
        self.assertGreater(result['products'],0)
        limited=rs.boolean_cubic_lift(rows,3,max_pivots=2)
        self.assertEqual(limited['status'],'unknown')
        self.assertFalse(limited['complete'])
        with patch.object(rs.time,'monotonic',side_effect=itertools.count()):
            result=rs.boolean_cubic_lift(rows,3,seconds=.5)
        self.assertEqual(result['status'],'unknown')
        for invalid in (-1,1<<7):
            with self.assertRaises(ValueError):rs.boolean_cubic_lift([invalid],3)

    def test_cubic_shell_consequences_preserve_literal_signs(self):
        rows=[{0:1,1:1,2:1,3:1},{1:1,2:-1,4:1,5:-1}]
        report=rs.cubic_shell_analysis(6,rows)
        self.assertTrue(report['complete'])
        for signs in itertools.product((-1,1),repeat=6):
            if any(sum(c*signs[i] for i,c in row.items()) for row in rows):continue
            self.assertNotEqual(report['status'],'refused')
            value=sum((signs[i]<0)<<j for j,i in enumerate(report['free']))
            for polynomial in report['linear_polynomials']:
                self.assertEqual(((polynomial>>1&value).bit_count()^(polynomial&1))%2,0)

    def test_boolean_quadratic_substitution_is_exact_on_every_assignment(self):
        rng=random.Random(3980)
        for n in range(1,7):
            for _ in range(8):
                # Compatible affine constraints are chosen through one
                # witnessed point, independently of polynomial substitution.
                witness=rng.randrange(1<<n)
                linear=[]
                for _ in range(n//2):
                    mask=rng.randrange(1<<n)
                    linear.append(mask<<1|((mask&witness).bit_count()%2))
                free,expressions=rs.boolean_linear_substitution(n,linear)
                rows=[rng.getrandbits(1+n+n*(n-1)//2) for _ in range(4)]
                transformed=rs.substitute_boolean_quadratics(rows,expressions,len(free))
                def evaluate(row,value,dimension):
                    terms=[()]+[(i,) for i in range(dimension)]+[
                        (i,j) for j in range(dimension) for i in range(j)]
                    return sum(all(value>>i&1 for i in term) for j,term in enumerate(terms)
                               if row>>j&1)%2
                recovered=set()
                for value in range(1<<len(free)):
                    old=sum(evaluate(e,value,len(free))<<i for i,e in enumerate(expressions))
                    recovered.add(old)
                    self.assertTrue(all(not evaluate(row,old,n) for row in linear))
                    for a,b in zip(rows,transformed):
                        self.assertEqual(evaluate(a,old,n),evaluate(b,value,len(free)))
                expected={v for v in range(1<<n) if all(not evaluate(row,v,n) for row in linear)}
                self.assertEqual(recovered,expected)
        with self.assertRaises(ValueError):rs.boolean_linear_substitution(2,[1])

    def test_cubic_recovery_uses_negative_bits_and_search_positive_bits(self):
        analysis=dict(free=[0,1,2],parameter_ids=[2],recovery=[1,3,2])
        basis=rs.cubic_sign_basis(3,[],analysis)
        for positive in range(8):
            satisfies=all((positive&mask).bit_count()%2==rhs for mask,rhs in basis.values())
            negative=positive^7
            expected=not (positive&1) and ((negative>>1)&1)==(1^((negative>>2)&1))
            self.assertEqual(satisfies,expected)
        engine=rs.make_engine(3,[],basis,seconds=1,nodes=100)
        status,values=engine.run({0:-1})
        self.assertEqual(status,'sat')
        self.assertEqual(values[0],-1)
        self.assertEqual(values[1],-values[2])

    def test_cubic_driver_witness_uses_untouched_row_verifier(self):
        import contextlib
        import io
        import json
        import tempfile
        from pathlib import Path
        keys=[('left',0,0,0),('left',1,1,0)]
        rows=[{0:1,1:-1}]
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory)/'witness.json'
            with patch.object(rs,'compile_moving_folded',return_value=(keys,rows)), \
                    patch('sys.argv',['resistant_spectrum.py','--folded-cubic','--cubic-search',
                                      '--period','4','--seconds','2','--write',str(target)]), \
                    contextlib.redirect_stdout(io.StringIO()):
                rs.main()
                saved=json.loads(target.read_text())
                self.assertEqual(saved['status'],'sat')
                self.assertEqual(saved['method'],'cubic_assisted')
                self.assertTrue(rs.verify_saved(saved)['verified'])
                saved['assignment'][1][1]*=-1
                with self.assertRaises(ValueError):rs.verify_saved(saved)

    def test_boolean_cubic_certificates_are_explicit_polynomial_identities(self):
        rng=random.Random(9817)
        for n in range(1,6):
            for _ in range(10):
                rows=[rng.getrandbits(1+n+n*(n-1)//2) for _ in range(4)]
                report=rs.boolean_cubic_lift(rows,n,proof=True)
                for identity in report['proof']:
                    self.assertTrue(rs.verify_boolean_cubic_identity(rows,n,identity))
                    damaged=dict(identity,polynomial=identity['polynomial']^1)
                    with self.assertRaises(ValueError):rs.verify_boolean_cubic_identity(rows,n,damaged)
                if report['status']=='refused':
                    self.assertIn(1,[identity['polynomial'] for identity in report['proof']])

    def test_cubic_shell_refusal_certificate_rejects_damage(self):
        rows=[dict(enumerate(word)) for word in ((1,1,1,1),(1,-1,1,-1),
                                               (1,1,-1,-1),(1,-1,-1,1))]
        report=rs.cubic_shell_analysis(4,rows,proof=True)
        self.assertEqual(report['status'],'refused')
        self.assertTrue(rs.verify_cubic_shell_proof(4,rows,report['cubic_proof']))
        import copy
        damaged=copy.deepcopy(report['cubic_proof'])
        damaged[-1][0]['raw']^=1
        with self.assertRaises(ValueError):rs.verify_cubic_shell_proof(4,rows,damaged)
        saved=dict(mode='folded_cubic',status='refused',all_pairs_decided=False,
                   half=3990,period=4,patch=2,hole=19,cubic_proof=report['cubic_proof'])
        with patch.object(rs,'compile_moving_folded',return_value=(list(range(4)),rows)):
            self.assertTrue(rs.verify_saved(saved)['verified'])
            with self.assertRaises(ValueError):rs.verify_saved(dict(saved,all_pairs_decided=True))
            with self.assertRaises(ValueError):rs.verify_saved(dict(saved,joint_history=[]))

    def test_cubic_proof_budget_covers_extraction(self):
        rows=[(1<<4)|1,1<<5,(1<<6)|1]
        extraction_stops=0
        # Move the deadline across every clock boundary of this small run;
        # no fixed count of internal elimination operations is assumed.
        for cutoff in range(1,100):
            calls=itertools.count()
            with patch.object(rs.time,'monotonic',side_effect=lambda:float(next(calls)>=cutoff)):
                report=rs.boolean_cubic_lift(rows,3,seconds=.5,proof=True)
            if report['stage']=='proof_time_limit':
                extraction_stops+=1
                self.assertEqual(report['status'],'unknown')
                self.assertFalse(report['complete'])
                self.assertEqual(report['proof'],[])
        self.assertGreater(extraction_stops,0)

    def test_relational_shells_preserve_every_literal_solution(self):
        rng = random.Random(43272)
        systems = [(9,[{0:1,2:-1,4:1,8:1,3:1,5:-1},
                       {1:1,5:1,0:1,7:1,2:-1,8:-1,6:-1,3:-1},
                       {3:-1,7:1,8:1,5:1},
                       {6:-1,5:1,3:-1,0:1,7:-1,1:1}])]
        for size in range(2,8):
            for _ in range(10):
                rows = [{i:c for i in range(size) if (c:=rng.randrange(-2,3))}
                        for _ in range(4)]
                for row in rows:
                    if sum(row.values())%2:
                        row[0] = row.get(0,0)+1
                        if not row[0]:del row[0]
                systems.append((size,rows))
        stronger_size,stronger_rows = systems[0]
        self.assertFalse(rs.affine_shell_closure(stronger_size,stronger_rows)['conflict'])
        self.assertTrue(rs.relational_shell_consistency(stronger_size,stronger_rows,
                        list(itertools.combinations(range(4),2)))['conflict'])
        for size,rows in systems:
            report = rs.relational_shell_consistency(size,rows,
                         list(itertools.combinations(range(len(rows)),2)))
            self.assertTrue(report['complete'])
            literal = [v for v in range(1<<size) if all(
                not sum(c*(-1 if v>>i&1 else 1) for i,c in row.items()) for row in rows)]
            if report['conflict']: self.assertFalse(literal)
            # Reconstruct the necessary parity fibre independently with the
            # public reduced basis, rather than the implementation's recursion.
            refusal,basis = rs.binary_elimination(rows)
            reduced = rs.reduced_binary_basis(basis)
            for v in literal:
                free = v & ~sum(1<<p for p in basis)
                for i,(mask,rhs) in reduced.items():
                    self.assertEqual((v>>i)&1,((free&mask).bit_count()%2)^rhs)
                for table in report['tables'].values():
                    local = sum(((free&m).bit_count()%2)<<j
                                for j,m in enumerate(table['generators']))
                    self.assertIn(local,table['valid'])
        skipped = rs.relational_shell_consistency(4,[{i:1 for i in range(4)}],local_rank=0)
        self.assertEqual(skipped['skipped'],[0])
        self.assertFalse(skipped['conflict'])
        self.assertEqual(rs.relational_shell_consistency(2,[],seconds=1e-30)['complete'],False)
        for pairs in ([(0,)],[(0,True)],[(0,4)]):
            with self.assertRaises(ValueError):
                rs.relational_shell_consistency(4,[{0:1,1:1}],pairs)

    def test_relational_search_checks_literal_signs_with_both_parity_offsets(self):
        systems = [([{0:1,1:1,2:1,3:1}],4),
                   ([{0:1,1:-1,2:1,3:-1},{1:1,2:1,4:1,5:1}],6),
                   ([{1:-1,3:1,2:-1,4:-1},{4:-1,0:1,1:1,5:-1},
                     {4:-1,5:-1,0:1,2:1}],6)]
        offsets = set()
        for rows,size in systems:
            for rank in (0,12):
                relations = rs.relational_shell_consistency(size,rows,local_rank=rank)
                self.assertTrue(relations['complete'])
                self.assertFalse(relations['conflict'])
                offsets.update(m.bit_count()%2 for t in relations['tables'].values()
                               for m in t['generators'])
                engine = rs.make_relational_engine(size,rows,relations,seconds=5,nodes=10000)
                status,values = engine.run({0:1})
                self.assertEqual(status,'sat')
                self.assertTrue(all(not sum(c*values[i] for i,c in row.items()) for row in rows))
                for bits in range(1<<size):
                    signs = [1 if bits>>i&1 else -1 for i in range(size)]
                    literal = all(not sum(c*signs[i] for i,c in row.items()) for row in rows)
                    engine = rs.make_relational_engine(size,rows,relations,seconds=5,nodes=10000)
                    status,values = engine.run(dict(enumerate(signs)))
                    self.assertEqual(status,'sat' if literal else 'unsat')
                    if values is not None:self.assertEqual(values[:size],signs)
        self.assertEqual(offsets,{0,1})
        # The CLI uses the same compact report without retaining truth tables.
        diagnostic = rs.folded_hull_diagnostic(period=1,seconds=5,exact_relations=True)
        self.assertEqual(diagnostic['mode'],'folded_relations')
        self.assertTrue(diagnostic['conflict'])

    def test_binary_relation_overlap_is_the_entire_shared_span(self):
        rng = random.Random(43273)
        def span(generators):
            return {functools.reduce(int.__xor__,(m for j,m in enumerate(generators)
                    if v>>j&1),0) for v in range(1<<len(generators))}
        for _ in range(60):
            generators = []
            for side in range(2):
                basis = {}
                for mask in (rng.randrange(1,64) for _ in range(4)):
                    while mask:
                        p = mask.bit_length()-1
                        if p not in basis:
                            basis[p] = mask
                            break
                        mask ^= basis[p]
                generators.append(list(basis.values()))
            left,right = generators
            overlap = rs.binary_relation_overlap(left,right)
            shared = []
            for a,b in overlap:
                x = functools.reduce(int.__xor__,(m for j,m in enumerate(left) if a>>j&1),0)
                y = functools.reduce(int.__xor__,(m for j,m in enumerate(right) if b>>j&1),0)
                self.assertEqual(x,y)
                shared.append(x)
            self.assertEqual(span(shared),span(left)&span(right))

    def test_joint_row_hulls_keep_correlations_and_all_literal_solutions(self):
        # Separately each balanced four-sign row spans the same parity plane.
        # Together they force opposite pairs, which that plane cannot express.
        rows = [{0:1,1:1,2:1,3:1},{0:1,1:1,2:-1,3:-1}]
        single = rs.affine_shell_closure(4,rows,seconds=5)
        joint = rs.affine_shell_closure(4,rows,seconds=5,blocks=[(0,1)])
        self.assertEqual((single['rank'],joint['rank']),(1,2))
        generator = random.Random(43097)
        systems = [(4,rows)]
        for size in range(2,7):
            for _ in range(12):
                systems.append((size,[{i:c for i in range(size)
                                       if (c:=generator.randrange(-2,3))}
                                      for _ in range(3)]))
        for size,rows in systems:
            report = rs.affine_shell_closure(size,rows,seconds=5,
                                             blocks=[tuple(range(len(rows)))])
            self.assertTrue(report['complete'])
            literal = []
            for bits in range(1<<size):
                if all(not sum(c*(1 if bits>>i&1 else -1) for i,c in row.items())
                       for row in rows):
                    literal.append(bits)
            self.assertEqual(report['conflict'],not bool(literal))
            for bits in literal:
                for mask,rhs in report['basis'].values():
                    self.assertEqual((bits&mask).bit_count()%2,rhs)
        skipped = rs.affine_shell_closure(4,systems[0][1],seconds=5,
                                          local_rank=0,blocks=[(0,1)])
        self.assertFalse(skipped['conflict'])
        self.assertEqual(skipped['rank'],1)
        for blocks in ([()],[(2,)],[(True,)],['bad']):
            with self.assertRaises(ValueError):
                rs.affine_shell_closure(4,systems[0][1],blocks=blocks)

    def test_moving_forced_tails_and_reduced_radius_one_strip(self):
        generator=random.Random(580)
        for scale,hole in ((9,1),(11,19),(15,42)):
            lengths=[n*scale for n in (99,79,23)]
            holes={(1,hole*scale),(1,99*scale)}
            high=defaultdict(dict)
            for arm,n in enumerate(lengths,1):
                for d in range(1,n+1):
                    if (arm,d) in holes:continue
                    for e,c in fc.shell_column(lengths,holes,(arm,d)).items():
                        if e>122*scale:high[e][arm,d]=c
            for e in range(122*scale+1,178*scale+1):
                self.assertEqual(high[e],{(1,e-79*scale-1):-1,(2,e-99*scale):-1})
            audit=rs.moving_folded_audit(scale,hole,reduced=True)
            self.assertEqual(audit['matched_source_columns'],145*scale-1)
            self.assertEqual((audit['slice_signs'],audit['stored_slice_signs']),(290,580))
            self.assertEqual(len(rs.moving_folded_labels(True)),290)
            reduced={(0,0):1}
            reduced.update({(a,d):generator.choice((-1,1))
                            for a,n in enumerate((43*scale-1,79*scale,23*scale),1)
                            for d in range(1,n+1) if (a,d) not in holes})
            restored=dict(reduced)
            restored.update({(1,d+20*scale-1):-reduced[2,d]
                             for d in range(23*scale+1,79*scale+1)})
            self.assertEqual(len(restored),201*scale-1)
            self.assertEqual(rs.moving_folded_residual(scale,reduced,hole,reduced=True),
                             fc.shell_rows(lengths,holes,restored))
            # Every unshifted interior term stays at offset -1,0 or 1.
            for a,q,s in rs.moving_folded_labels(True):
                self.assertTrue(all(c in (-1,0,1) for Q,u,c,v in
                                    rs._moving_strip_column(a,q,s,0,hole,True)))

    def test_deep_hole_forced_tails_and_exceptional_unpaired_vertex(self):
        generator=random.Random(20261125)
        for scale,hole in ((9,43),(11,44),(15,97),(9,98)):
            lengths=[n*scale for n in (99,79,23)]
            holes={(1,hole*scale),(1,99*scale)}
            cutoff=(hole+79)*scale+1
            high=defaultdict(dict)
            for arm,n in enumerate(lengths,1):
                for d in range(1,n+1):
                    if (arm,d) in holes:continue
                    for e,c in fc.shell_column(lengths,holes,(arm,d)).items():
                        if e>=cutoff:high[e][arm,d]=c
            exceptional=(hole-20)*scale+1
            self.assertEqual(high[cutoff],{(2,exceptional):-1,(2,79*scale):1})
            for e in range(cutoff+1,178*scale+1):
                self.assertEqual(high[e],{(1,e-79*scale-1):-1,(2,e-99*scale):-1})
            reduced={(0,0):1}
            reduced.update({(a,d):generator.choice((-1,1))
                            for a,n in enumerate((hole*scale-1,79*scale,23*scale),1)
                            for d in range(1,n+1)})
            restored=dict(reduced)
            restored.update({(1,d+20*scale-1):-reduced[2,d]
                             for d in range(exceptional+1,79*scale+1)})
            self.assertEqual(len(restored),201*scale-1)
            self.assertNotIn((1,hole*scale),restored)
            self.assertEqual(rs.moving_folded_residual(scale,reduced,hole,reduced=True),
                             fc.shell_rows(lengths,holes,restored))
            # The unpaired coordinate remains in the reduced shell equation.
            residual=rs.moving_folded_residual(scale,reduced,hole,reduced=True)
            self.assertEqual(residual.get(cutoff,0),
                             reduced[2,79*scale]-reduced[2,exceptional])
            self.assertEqual(len(rs.moving_folded_labels(True,hole)),2*(hole+102))

    def test_reduced_complete_matrix_for_every_hole(self):
        for hole in range(1,99):
            audit=rs.moving_folded_audit(9,hole,reduced=True)
            self.assertEqual(audit['slice_signs'],2*(max(43,hole)+102))
            expected=(145*9-1 if hole<=42 else (hole+102)*9)
            self.assertEqual(audit['matched_source_columns'],expected)
        for hole in (True,0,99):
            with self.assertRaises(ValueError):rs.moving_folded_labels(True,hole)
            with self.assertRaises(ValueError):rs.moving_folded_stencils(hole,True)

    def test_high_arm_recovery_from_every_original_high_row(self):
        scale=9
        for hole in range(1,99):
            lengths=[n*scale for n in (99,79,23)]
            holes={(1,hole*scale),(1,99*scale)}
            high=defaultdict(lambda:defaultdict(int))
            recovery,remaining=rs.moving_high_arm_relations(scale,hole)
            for arm,n in enumerate(lengths,1):
                for d in range(1,n+1):
                    vertex=arm,d
                    if vertex in holes:continue
                    for e,c in fc.shell_column(lengths,holes,vertex).items():
                        if e>122*scale:high[e][vertex]+=c
            expected={}
            for vertex,expression in recovery.items():
                # The target occurs once, with coefficient -1. Every other
                # coefficient must be the claimed integer recovery expression.
                e=vertex[1]+79*scale+1
                expected[e]={vertex:-1,**expression}
            if remaining:expected[(hole+79)*scale+1]=remaining
            actual={e:{v:c for v,c in row.items() if c}
                    for e,row in high.items() if any(row.values())}
            self.assertEqual(actual,expected)
            self.assertEqual(len(recovery),56*scale-(hole>=43))
            self.assertTrue(all(len(row)==(3 if vertex[1]<hole*scale else 1)
                                for vertex,row in recovery.items()))
        for a,b,c in itertools.product((-1,1),repeat=3):
            value=-a+b-c
            self.assertEqual(abs(value)==1,a==b or c==b)
            self.assertEqual(abs(value)==3,a==c and a!=b)
        for scale,hole in ((True,19),(7,19),(10,19),(9,True),(9,0),(9,99)):
            with self.assertRaises(ValueError):rs.moving_high_arm_relations(scale,hole)

    def test_moving_strip_complete_matrix_and_direct_distance_counts(self):
        from collections import Counter
        for scale,hole in ((9,19),(11,1),(15,98)):
            audit=rs.moving_folded_audit(scale,hole)
            self.assertEqual(audit['matched_physical_columns'],201*scale-1)
            self.assertEqual(audit['path_edges'],scale//2-2)
        scale,hole=9,19
        vertices=[(0,0)]+[(a,d) for a,n in enumerate((99,79,23),1)
                          for d in range(1,n*scale+1) if (a,d) not in ((1,hole*scale),(1,99*scale))]
        random.Random(7391).shuffle(vertices)
        first,second=vertices[:len(vertices)//2],vertices[len(vertices)//2:]
        def distances(part):
            return Counter(abs(d-e) if a==b else d+e
                           for i,(a,d) in enumerate(part) for b,e in part[:i])
        delta=distances(first)
        delta.subtract(distances(second))
        expected=defaultdict(int)
        for d,c in delta.items():expected[d]+=2*c;expected[d+1]-=2*c
        signs={v:1 for v in first};signs.update({v:-1 for v in second})
        self.assertEqual(rs.moving_folded_residual(scale,signs,hole),
                         {d:c for d,c in expected.items() if c})

    def test_moving_folded_compiler_against_all_physical_columns_and_phases(self):
        cases=[(10,1,2,19),(12,2,2,1),(14,3,3,98),
               (18,4,2,7),(18,4,2,19),(18,4,2,97)]
        cases=[(*case,False) for case in cases]+[
            (14,4,2,hole,True) for hole in (1,19,42,43,44,97,98)]
        for half,period,width,hole,reduced in cases:
            keys,rows=rs.compile_moving_folded(half,period,width,hole,reduced)
            scale=2*half+1
            positions={key:i for i,key in enumerate(keys)}
            expected=defaultdict(lambda:defaultdict(int))
            covered=set()
            first=(max(43,hole)*scale-1) if reduced else 99*scale
            for arm,n in enumerate((0,first,79*scale,23*scale)):
                for depth in (range(1,n+1) if arm else (0,)):
                    if (arm,depth) in ((1,hole*scale),(1,99*scale)):continue
                    if arm==0:key=('left',0,0,0)
                    else:
                        q,r=divmod(depth,scale)
                        if not r:key=('left',arm,q,0)
                        else:
                            orientation=1
                            if r>half:q+=1;r=scale-r;orientation=-1
                            if r<=width:key=('left',arm,q,orientation*r)
                            elif r>=half-width:key=('right',arm,q,orientation,r-half)
                            else:key=('period',arm,q,orientation,r%period)
                    covered.add(key)
                    column=defaultdict(int,fc.shell_column([99*scale,79*scale,23*scale],
                                              {(1,hole*scale),(1,99*scale)},(arm,depth)))
                    if (reduced and arm==2 and depth>(max(43,hole)-20)*scale
                            and not (hole>=43 and depth==(hole-20)*scale+1)):
                        for e,c in fc.shell_column([99*scale,79*scale,23*scale],
                                {(1,hole*scale),(1,99*scale)},(1,depth+20*scale-1)).items():
                            column[e]-=c
                    for e,c in column.items():
                        expected[e][positions[key]]+=c
            self.assertEqual(covered,set(keys))
            self.assertEqual(normalized(rows),normalized(expected.values()))
            next_keys,next_rows=rs.compile_moving_folded(half+period,period,width,hole,reduced)
            self.assertEqual(keys,next_keys)
            self.assertEqual(normalized(rows),normalized(next_rows))
            if reduced:
                target_keys,target_rows=rs.compile_moving_folded(3990,period,width,hole,True)
                self.assertEqual(keys,target_keys)
                self.assertEqual(normalized(rows),normalized(target_rows))
        for half,period,width in ((10,0,2),(10,1,1),(3,1,2),(True,1,2)):
            with self.assertRaises(ValueError):rs.compile_moving_folded(half,period,width)

    def test_moving_folded_saved_refusal_and_witness_validation(self):
        saved=rs.moving_folded_search(half=3990,period=2,patch=2)
        self.assertEqual(saved['status'],'ansatz_refused_by_parity')
        self.assertTrue(rs.verify_saved(saved)['verified'])
        for damaged in (dict(saved,certificate=[]),dict(saved,minimum_half=1),
                        dict(saved,half_residue=1),dict(saved,all_pairs_decided=True)):
            with self.assertRaises(ValueError):rs.verify_saved(damaged)
        # Planted positive control of the witness checker; the mocked two-sign
        # system is not presented as a tripod witness or a family construction.
        positive=dict(saved,status='sat',assignment=[[['u'],1],[['v'],-1]])
        with patch.object(rs,'compile_moving_folded',return_value=([('u',),('v',)],[{0:1,1:1}])):
            self.assertTrue(rs.verify_saved(positive)['verified'])
            for bad in ([[['u'],1],[['v'],1]],[[['u'],1],[['v'],0]],[[['u'],True],[['v'],-1]]):
                with self.assertRaises(ValueError):rs.verify_saved(dict(positive,assignment=bad))

    def test_new_commands_round_trip_through_real_cli(self):
        import json
        from pathlib import Path
        import subprocess
        import sys
        import tempfile
        script=Path(rs.__file__)
        with tempfile.TemporaryDirectory() as directory:
            for flags in (['--moving-folded','--period','2'],
                          ['--split-dyadic','--edge-patch','4','--piece-period','2','--hole-offset','-2']):
                destination=Path(directory)/'result.json'
                run=subprocess.run([sys.executable,str(script),*flags,'--write',str(destination)],
                                   check=True,text=True,capture_output=True)
                self.assertFalse(json.loads(run.stdout)['all_pairs_decided'])
                run=subprocess.run([sys.executable,str(script),'--verify',str(destination)],
                                   check=True,text=True,capture_output=True)
                self.assertTrue(json.loads(run.stdout)['verified'])

    def test_moving_unrestricted_strip_reconstructs_every_physical_row(self):
        generator=random.Random(7980)
        for scale,hole in ((9,1),(11,19),(15,98),(21,7),(25,19)):
            lengths=[n*scale for n in (99,79,23)]
            holes={(1,hole*scale),(1,99*scale)}
            coordinates={(0,0):generator.randint(-3,3)}
            coordinates.update({(arm,d):generator.randint(-3,3)
                                for arm,n in enumerate(lengths,1) for d in range(1,n+1)
                                if (arm,d) not in holes})
            self.assertEqual(rs.moving_folded_residual(scale,coordinates,hole),
                             fc.shell_rows(lengths,holes,coordinates))
        # Per-column controls prevent cancellation between mistakes in two
        # source columns from being hidden by any one random signing.
        scale,hole=9,19
        vertices=[(0,0)]+[(a,d) for a,n in enumerate((99,79,23),1)
                          for d in range(1,n*scale+1) if (a,d) not in ((1,hole*scale),(1,99*scale))]
        for vertex in generator.sample(vertices,12):
            coordinates=defaultdict(int,{vertex:1})
            self.assertEqual(rs.moving_folded_residual(scale,coordinates,hole),
                             fc.shell_column([99*scale,79*scale,23*scale],
                                             {(1,hole*scale),(1,99*scale)},vertex))
        for scale in (1,8,True):
            with self.assertRaises(ValueError):rs.moving_folded_residual(scale,{})
        with self.assertRaises(ValueError):rs.moving_folded_stencils(99)

    def test_dyadic_quadratics_are_exact_mod_eight_on_every_binary_choice(self):
        generator=random.Random(20261124)
        for size in range(1,7):
            for repeat in range(16):
                # Plant a literal solution, while retaining arbitrary negative
                # coefficients and coefficients divisible by two and four.
                witness=[generator.choice((-1,1)) for _ in range(size)]
                rows=[]
                for _ in range(3):
                    row={i:generator.randint(-4,4) for i in range(size-1)}
                    row[size-1]=-sum(c*witness[i] for i,c in row.items())*witness[-1]
                    rows.append(row)
                compiled=rs.binary_shell_quadratics(size,rows)
                self.assertTrue(compiled['complete'])
                self.assertFalse(compiled['parity_conflict'])
                n=len(compiled['free'])
                seen=set()
                for choice in range(1<<n):
                    values=[(-1 if ((a&choice).bit_count()^b)&1 else 1)
                            for a,b in (compiled['expressions'][i] for i in range(size))]
                    seen.add(tuple(values))
                    monomials=choice
                    for b in range(n):
                        for a in range(b):
                            if choice>>a&1 and choice>>b&1:
                                monomials|=1<<(n+b*(b-1)//2+a)
                    for row,(mask,rhs) in zip(rows,compiled['quadratic_rows']):
                        total=sum(c*values[i] for i,c in row.items())
                        self.assertEqual(total%4,0)
                        self.assertEqual((total//4)%2,((mask&monomials).bit_count()^rhs)&1)
                # Independent enumeration verifies completeness of the affine
                # fibre, including signs that fail the original integer rows.
                expected={values for values in itertools.product((-1,1),repeat=size)
                          if all(sum(c*values[i] for i,c in row.items())%4==0 for row in rows)}
                self.assertEqual(seen,expected)

    def test_dyadic_quadratic_consequences_and_refusals(self):
        rows=[{0:1,1:1,2:4}]
        self.assertIsNone(rs.binary_elimination(rows)[0])
        report=rs.dyadic_quadratic_analysis(3,rows)
        self.assertEqual(report['status'],'refused_by_quadratics')
        proof=dict(mask=0,rhs=1,certificate=report['certificate'])
        self.assertTrue(rs.verify_dyadic_consequence(3,rows,proof))
        for damaged in (dict(proof,rhs=0),dict(proof,certificate=[]),
                        dict(proof,certificate=[0,0]),dict(proof,certificate=[[]])):
            with self.assertRaises(ValueError):rs.verify_dyadic_consequence(3,rows,damaged)
        # This row is compatible modulo four, but modulo eight additionally
        # forces its two free signs to be opposite: 2*s0+2*s1=0.
        rows=[{0:2,1:2}]
        report=rs.dyadic_quadratic_analysis(2,rows)
        self.assertEqual(len(report['linear_relations']),1)
        self.assertEqual((report['linear_relations'][0]['mask'],
                          report['linear_relations'][0]['rhs']),(3,1))
        self.assertTrue(rs.verify_dyadic_consequence(2,rows,report['linear_relations'][0]))
        # Compatibility must never be promoted to a literal witness.
        report=rs.dyadic_quadratic_analysis(2,[{0:4,1:4}])
        self.assertEqual(report['status'],'compatible_product_relaxation')
        self.assertFalse(report['literal_existence_decided'])
        self.assertEqual(rs.dyadic_quadratic_analysis(1,[{0:2}])['status'],'refused_by_parity')
        self.assertEqual(rs.binary_shell_quadratics(3,[],max_free=2)['stage'],'dimension_limit')
        for size,rows in ((True,[]),(2,[{2:1}]),(1,[{0:0.5}])):
            with self.assertRaises(ValueError):rs.binary_shell_quadratics(size,rows)

    def test_flat_any_holes_support_count_against_physical_columns(self):
        rng = random.Random(9309)
        for pieces,width,length in ((2,0,200),(2,1,60),(3,1,60)):
            scale = pieces*length+1
            lengths = [n*scale for n in (99,79,23)]
            baseline = {(0,0):1}
            for arm,n in enumerate((99,79,23),1):
                for edge in range(n):
                    signs = [rng.choice((-1,1)) for _ in range(pieces)]
                    for part,sign in enumerate(signs):
                        lo = edge*scale+part*length+1
                        baseline.update({(arm,d):sign for d in range(lo,lo+length)})
                    baseline[arm,(edge+1)*scale] = rng.choice((-1,1))
            nohole = fc.shell_rows(lengths,set(),baseline)
            if length>178:
                longest = current = 0
                for exponent in range(max(nohole)+1):
                    current = current+1 if nohole.get(exponent,0) else 0
                    longest = max(longest,current)
                self.assertGreaterEqual(longest,length-178)
            # Cross a piece interior; also remove the centre in one case.
            for holes in ({(1,length//2),(3,scale+length+2)},
                          {(0,0),(2,2*scale-1)}):
                corrected = dict(baseline)
                for arm,n in enumerate((99,79,23),1):
                    for edge in range(n):
                        for part in range(pieces):
                            lo = edge*scale+part*length+1
                            for offset in range(width):
                                corrected[arm,lo+offset] *= -1
                                corrected[arm,lo+length-1-offset] *= -1
                for hole in holes: corrected[hole] = 0
                with_holes = fc.shell_rows(lengths,holes,baseline)
                actual = fc.shell_rows(lengths,holes,corrected)
                def support_difference(left,right):
                    return sum(left.get(e,0)!=right.get(e,0) for e in left.keys()|right.keys())
                self.assertLessEqual(support_difference(with_holes,nohole),804*pieces+812)
                changed = sum(corrected[v]!=baseline[v] for v in baseline)
                self.assertLessEqual(support_difference(actual,with_holes),8*changed)
                bound = rs.flat_piece_any_holes_bound(length,pieces,width)
                self.assertLessEqual(support_difference(actual,nohole),bound['correction_support_upper_bound'])

    def test_flat_any_holes_threshold_and_saved_controls(self):
        for pieces,width in ((2,0),(2,1),(3,7),(100,50)):
            threshold = 804*pieces+3216*pieces*width+1007
            self.assertEqual(rs.flat_piece_any_holes_bound(threshold-1,pieces,width)['status'],
                             'not_decided_by_bound')
            result = rs.flat_piece_any_holes_bound(threshold,pieces,width)
            self.assertEqual(result['status'],'flat_ansatz_refused')
            self.assertTrue(rs.verify_saved(result)['verified'])
        for m in (1,2,10**50):
            result = rs.flat_piece_any_holes_bound(3990*m)
            self.assertEqual(result['t'],7980*m+1)
            self.assertEqual(result['status'],'flat_ansatz_refused')
            self.assertFalse(result['all_pairs_decided'])
        for field,value in (('status','all_pairs_refused'),('t',1),
                            ('correction_support_upper_bound',0),('all_pairs_decided',True)):
            damaged = dict(result)
            damaged[field] = value
            with self.assertRaises(ValueError): rs.verify_saved(damaged)
        for length,pieces,width in ((0,2,0),(1,1,0),(3,2,2),(True,2,0),(3,2,-1)):
            with self.assertRaises(ValueError): rs.flat_piece_any_holes_bound(length,pieces,width)

    def test_bulk_refusal_independent_of_piece_count_and_patch(self):
        keys,expected = rs.split_bulk_system()
        expected = {q:{keys[i]:c for i,c in row.items()} for q,row in expected.items()}
        for pieces,width in ((2,0),(2,1),(2,3),(3,0),(3,2),(4,1),(7,2),(10,0)):
            source,formal = rs.split_edge_system(19,width,pieces,1)
            actual = defaultdict(lambda:defaultdict(int))
            for (q,c),row in formal.items():
                if q%pieces: continue
                for i,value in row.items():
                    key = source[i]
                    if key[0]=='half':
                        _,arm,edge,part = key
                        # Middle pieces must cancel; retain their identities
                        # until after aggregation to catch an omitted endpoint.
                        label = ('first',arm,edge) if part==0 else (
                            ('last',arm,edge) if part==pieces-1 else key)
                    else: label = key
                    actual[q//pieces][label] += value
            actual = {q:{key:c for key,c in row.items() if c}
                      for q,row in actual.items() if any(row.values())}
            self.assertEqual(actual,expected)
            offsets = [c for q,c in formal]
            self.assertGreaterEqual(min(offsets),1-width)
            self.assertLessEqual(max(offsets),179+width)

    def test_bulk_refusal_binary_replay_and_damage(self):
        from functools import reduce
        keys,rows = rs.split_bulk_system()
        saved = rs.split_bulk_refusal()
        self.assertEqual((len(keys),len(rows)),(402,179))
        # Reconstruct and XOR binary equations without verify_refusal.
        binary = []
        for row in rows.values():
            total = sum(row.values())
            self.assertEqual(total%2,0)
            binary.append((sum(1<<i for i,c in row.items() if c%2),total//2%2))
        self.assertEqual(reduce(lambda a,j:(a[0]^binary[j][0],a[1]^binary[j][1]),
                                saved['certificate'],(0,0)),(0,1))
        self.assertTrue(rs.verify_saved(saved)['verified'])
        self.assertFalse(rs.verify_saved(saved)['all_pairs_decided'])
        for bad in ([],saved['certificate'][:-1],saved['certificate']+[len(rows)]):
            damaged = dict(saved,certificate=bad)
            with self.assertRaises(ValueError): rs.verify_saved(damaged)

    def test_split_edge_columns_against_every_physical_shell(self):
        import full_shorter_coupling as physical
        for hole,patch,pieces,period in ((19,0,2,1),(7,1,2,1),(19,2,2,1),(19,0,3,1),
                                         (7,1,4,1),(19,0,10,1),(19,0,2,2),(19,2,2,2),
                                         (19,4,2,2),(7,3,3,3),(19,1,2,2),
                                         (7,2,3,4),(19,3,2,6)):
            keys,rows=rs.split_edge_system(hole,patch,pieces,period)
            for half_length in (2*patch+period,2*patch+3*period):
                t=pieces*half_length+1
                actual=[defaultdict(int) for _ in keys]
                for (q,c),row in rows.items():
                    for i,value in row.items():actual[i][q*half_length+c]+=value
                for i,key in enumerate(keys):
                    if key[0]=='old':
                        _,arm,q=key;depths=[q*t]
                    else:
                        _,arm,edge,half,*rest=key
                        lo=edge*t+1+half*half_length
                        hi=lo+half_length-1
                        if key[0]=='half':depths=range(lo+patch,hi-patch+1)
                        elif key[0]=='word':
                            j,=rest;depths=range(lo+patch+j-1,hi-patch+1,period)
                        else:
                            side,r=rest;depths=[lo+r if side==0 else hi-r]
                    expected=defaultdict(int)
                    for d in depths:
                        for e,c in physical.shell_column([99*t,79*t,23*t],{(1,hole*t),(1,99*t)},(arm,d)).items():
                            expected[e]+=c;expected[e+period]-=c
                    self.assertEqual({e:c for e,c in actual[i].items() if c},
                                     {e:c for e,c in expected.items() if c},(hole,patch,half_length,key))
        for hole,patch in ((0,0),(99,0),(19,-1),(19,0.5)):
            with self.assertRaises(ValueError):rs.split_edge_system(hole,patch)
        for period in (0,-1,1.5,3):
            with self.assertRaises(ValueError):rs.split_edge_system(patch=1,word_period=period)

    def test_offset_holes_against_physical_columns(self):
        for hole,width,pieces,period,offset,hole_piece in (
                (19,1,2,1,-1,0),(19,1,2,1,1,0),
                (19,2,2,2,-2,0),(19,2,2,2,2,0),
                (7,2,3,4,-1,0),(7,2,3,4,1,0),
                (98,3,2,3,-3,0),(1,3,2,3,3,0),
                (19,2,2,2,-1,1),(19,2,2,2,0,1),
                (19,2,2,2,2,1),(7,2,3,4,1,2)):
            keys,rows=rs.split_edge_system(hole,width,pieces,period,offset,hole_piece=hole_piece)
            for length in (2*width+period,2*width+2*period):
                t=pieces*length+1
                holes={(1,hole*t+hole_piece*length+offset),(1,99*t)}
                actual=[defaultdict(int) for _ in keys]
                for (q,c),row in rows.items():
                    for i,value in row.items():actual[i][q*length+c]+=value
                covered=set()
                for i,key in enumerate(keys):
                    if key[0]=='old':
                        _,arm,q=key;depths=[q*t]
                    else:
                        _,arm,edge,piece,*rest=key
                        lo=edge*t+1+piece*length;hi=lo+length-1
                        if key[0]=='half':depths=range(lo+width,hi-width+1)
                        elif key[0]=='word':
                            j,=rest;depths=range(lo+width+j-1,hi-width+1,period)
                        else:
                            side,r=rest;depths=[lo+r if side==0 else hi-r]
                    expected=defaultdict(int)
                    for d in depths:
                        vertex=(arm,d)
                        self.assertNotIn(vertex,holes)
                        self.assertNotIn(vertex,covered)
                        covered.add(vertex)
                        for e,c in fc.shell_column([99*t,79*t,23*t],holes,vertex).items():
                            expected[e]+=c;expected[e+period]-=c
                    self.assertEqual({e:c for e,c in actual[i].items() if c},
                                     {e:c for e,c in expected.items() if c},(key,t,offset,hole_piece))
                self.assertEqual(len(covered),201*t-1)
                self.assertIn((0,0),covered)
                self.assertTrue(all(0<=a<=3 and (d==0 if a==0 else 1<=d<=[0,99*t,79*t,23*t][a])
                                    for a,d in covered))
        for offset in (-3,3,True,1.5):
            with self.assertRaises(ValueError):rs.split_edge_system(patch=2,hole_offset=offset)

        for piece in (-1,2,True,1.5):
            with self.assertRaises(ValueError):rs.split_edge_system(patch=2,hole_piece=piece)
        with self.assertRaises(ValueError):rs.split_edge_system(hole_piece=1)
        with self.assertRaises(ValueError):rs.split_edge_system(patch=2,hole_piece=1,hole_offset=-2)

    def test_shifted_support_portable_refusal(self):
        saved=rs.split_edge_search(patch=4,word_period=2,hole_offset=-2)
        self.assertEqual(saved['status'],'ansatz_refused_by_parity')
        self.assertEqual(saved['hole_offset'],-2)
        self.assertTrue(rs.verify_saved(saved)['verified'])
        with self.assertRaises(ValueError):
            rs.verify_saved(dict(saved,certificate=[]))
        with self.assertRaises(ValueError):
            rs.verify_saved(dict(saved,hole_offset=-5))
        with self.assertRaises(ValueError):
            rs.verify_saved(dict(saved,status='unknown',assignment=[]))

    def test_word_endpoint_system_independent_of_piece_count(self):
        for hole,width,period,offset in ((19,4,2,-2),(19,4,2,2),(7,2,4,1),(1,3,3,-3)):
            keys,expected=rs.split_endpoint_system(hole,width,period,offset)
            for pieces in (2,3,7):
                all_keys,rows=rs.split_edge_system(hole,width,pieces,period,offset)
                def relabel(key):
                    if key[0]=='old':return key
                    kind,arm,edge,r,*tail=key
                    self.assertIn(r,(0,pieces-1))
                    return (kind,arm,edge,int(r!=0),*tail)
                actual={(q//pieces,c):{keys.index(relabel(all_keys[i])):v for i,v in row.items()}
                        for (q,c),row in rows.items() if q%pieces==0}
                self.assertEqual(actual,expected)
                raw,reference=[],[]
                rs.split_edge_system(hole,width,pieces,period,offset,raw)
                rs.split_edge_system(hole,width,2,period,offset,reference)
                self.assertEqual(set(raw),set(reference))
        saved=rs.split_endpoint_refusal(19,4,2,-2)
        checked=rs.verify_saved(saved)
        self.assertGreater(checked['minimum_piece_length'],saved['exponent_constant_span'])
        self.assertEqual(checked['minimum_piece_length']%2,0)
        with self.assertRaises(ValueError):
            rs.verify_saved(dict(saved,minimum_piece_length=2))
        with self.assertRaises(ValueError):
            rs.verify_saved(dict(saved,certificate=[]))
        with self.assertRaises(ValueError):
            rs.split_endpoint_refusal(19,8,2,-2)

    def test_binary_fibre_exhaustion_against_all_signs(self):
        generator=random.Random(731)
        for size in range(1,7):
            for repeat in range(12):
                rows=[{i:c for i in range(size) if (c:=generator.randint(-2,2))}
                      for row in range(4)]
                solutions=[values for values in itertools.product((-1,1),repeat=size)
                           if all(sum(c*values[i] for i,c in row.items())==0 for row in rows)]
                audit=rs.enumerate_binary_fibre(size,rows,max_free=6)
                self.assertTrue(audit['complete'])
                self.assertEqual(audit['status']=='sat',bool(solutions))
                if solutions:self.assertIn(tuple(audit['values']),solutions)
        # Unconditioned random systems above are all unsatisfiable for this
        # seed. Plant witnesses as a separate positive control.
        for size in range(1,7):
            for repeat in range(12):
                witness=[generator.choice((-1,1)) for i in range(size)]
                rows=[]
                for row in range(4):
                    coefficients={i:generator.randint(-2,2) for i in range(size-1)}
                    coefficients[size-1]=-sum(c*witness[i] for i,c in coefficients.items())*witness[-1]
                    rows.append({i:c for i,c in coefficients.items() if c})
                solutions=[values for values in itertools.product((-1,1),repeat=size)
                           if all(sum(c*values[i] for i,c in row.items())==0 for row in rows)]
                audit=rs.enumerate_binary_fibre(size,rows,max_free=6)
                self.assertEqual(audit['status'],'sat')
                self.assertIn(tuple(audit['values']),solutions)
        self.assertEqual(rs.enumerate_binary_fibre(5,[],max_free=4)['status'],'unknown')
        with self.assertRaises(ValueError):rs.enumerate_binary_fibre(2,[],max_free=21)
        with patch.object(rs.time,'monotonic',side_effect=[0,2]):
            audit=rs.enumerate_binary_fibre(3,[],seconds=1)
        self.assertEqual((audit['status'],audit['complete'],audit['enumerated']),('unknown',False,0))
        saved=rs.split_edge_search(patch=2,word_period=2,hole_piece=1)
        self.assertEqual(saved['status'],'ansatz_refused_by_binary_fibre')
        self.assertEqual((saved['parity_free'],saved['enumerated']),(10,1024))
        self.assertTrue(rs.verify_saved(saved)['verified'])
        with self.assertRaises(ValueError):rs.verify_saved(dict(saved,enumerated=1023))
        with self.assertRaises(ValueError):rs.verify_saved(dict(saved,minimum_piece_length=6))

    def test_uniform_flat_piece_endpoint_refusal(self):
        keys,expected=rs.split_endpoint_system()
        for pieces in (2,3,4,7,10,31):
            all_keys,rows=rs.split_edge_system(19,0,pieces)
            def relabel(key):
                if key[0]=='old':return key
                kind,arm,edge,r=key
                self.assertIn(r,(0,pieces-1))
                return kind,arm,edge,int(r!=0)
            actual={(q//pieces,c):{keys.index(relabel(all_keys[i])):v for i,v in row.items()}
                    for (q,c),row in rows.items() if q%pieces==0}
            self.assertEqual(actual,expected)
            constants=[c for q,c in rows]
            self.assertEqual(max(constants)-min(constants),178)
        saved=rs.split_endpoint_refusal()
        self.assertTrue(rs.verify_saved(saved)['verified'])
        with self.assertRaises(ValueError):rs.verify_saved(dict(saved,certificate=[]))
        for pieces in (0,1,2.5):
            with self.assertRaises(ValueError):rs.split_edge_system(pieces=pieces)
        keys,_=rs.split_edge_system()
        bad=dict(mode='split_edge',hole=19,patch=0,pieces=2,
                 assignment=[[list(k),1] for k in keys])
        with self.assertRaises(ValueError):rs.verify_saved(bad)

    def test_moving_edge_patches_against_all_physical_columns(self):
        for period,width,hole in ((1,1,19),(2,4,19),(3,3,7),(4,4,19),(8,8,19)):
            keys,rows = rs.moving_periodic_system(period,hole,width)
            for repeats in (1,2):
                scale = 2*width+period*repeats+1
                columns = [defaultdict(int) for _ in keys]
                for (q,c),row in rows.items():
                    for i,value in row.items(): columns[i][q*scale+c] += value
                for i,key in enumerate(keys):
                    if len(key)==3:
                        arm,edge,r = key
                        depths = [edge*scale] if r==0 else range(
                            edge*scale+width+r,(edge+1)*scale-width,period)
                    else:
                        arm,edge,side,r = key
                        depths = [edge*scale+r if side=='prefix' else (edge+1)*scale-r]
                    expected = defaultdict(int)
                    for depth in depths:
                        for e,c in fc.shell_column([99*scale,79*scale,23*scale],
                                {(1,hole*scale),(1,99*scale)},(arm,depth)).items():
                            expected[e] += c
                            expected[e+period] -= c
                    self.assertEqual({e:c for e,c in columns[i].items() if c},
                                     {e:c for e,c in expected.items() if c},(period,width,key))
        for period,width in ((2,-1),(3,1),(1,True)):
            with self.assertRaises(ValueError): rs.moving_periodic_system(period,19,width)
        keys,_ = rs.moving_periodic_system(2,19,4)
        fake = dict(mode='moving',period=2,edge_patch=4,status='sat',
                    assignment=[[list(k),1] for k in keys])
        with self.assertRaises(ValueError): rs.verify_saved(fake)
        unknown = rs.moving_search(4,edge_patch=4,seconds=5,nodes=0,closure_steps=0)
        self.assertEqual(unknown['status'],'unknown')
        self.assertEqual(unknown['minimum_scale'],13)
        with self.assertRaises(ValueError): rs.verify_saved(unknown)

    def test_general_tree_residue_lift_by_adjacency_bfs(self):
        from collections import Counter,deque
        edges = [(0,1),(1,2),(2,3),(1,4),(4,5),(4,6)]
        def distances(edges):
            adjacency = defaultdict(list)
            for u,v in edges:
                adjacency[u].append(v)
                adjacency[v].append(u)
            result = {}
            for start in adjacency:
                seen = {start:0}
                queue = deque([start])
                while queue:
                    u = queue.popleft()
                    for v in adjacency[u]:
                        if v not in seen:
                            seen[v] = seen[u]+1
                            queue.append(v)
                result[start] = seen
            return result
        def profile(group,metric,period=None):
            return Counter(metric[u][v] if period is None else metric[u][v]%period
                           for u,v in itertools.combinations(group,2))
        base_metric = distances(edges)
        for left,right in (([0,1],[4,5]),([0,2],[5,6]),([2,3],[4,5])):
            # Only homometric base pairs are admitted; holes remain in the metric.
            self.assertEqual(profile(left,base_metric),profile(right,base_metric))
            for period in (1,2,3):
                scale = 2*period+1
                signs = {v:(1 if v in left else -1 if v in right else 0) for v in range(7)}
                expanded = []
                for edge,(u,v) in enumerate(edges):
                    chain = [u]+[(edge,r) for r in range(1,scale)]+[v]
                    expanded.extend(zip(chain,chain[1:]))
                    for r in range(1,scale):
                        signs[edge,r] = 1 if ((r-1)//period)%2==0 else -1
                metric = distances(expanded)
                positive = [v for v,s in signs.items() if s==1]
                negative = [v for v,s in signs.items() if s==-1]
                self.assertEqual(len(positive),len(left)+len(edges)*(scale-1)//2)
                self.assertEqual(len(positive),len(negative))
                self.assertEqual(profile(positive,metric,period),profile(negative,metric,period))

    def test_residue_lift_direct_distance_profiles_and_edge_defect(self):
        from collections import Counter
        # Count actual unordered distances, independently of the shell compiler.
        for period in (1,2,3,5):
            for repetitions in (1,2):
                scale = 2*period*repetitions+1
                groups = {1:[], -1:[]}
                zeros = []
                vertices = [(0,0)]+[(a,d) for a,n in enumerate((99,79,23),1)
                                     for d in range(1,n*scale+1)]
                for vertex in vertices:
                    sign = rs.residue_lift_sign(period,scale,vertex)
                    if sign: groups[sign].append(vertex)
                    else: zeros.append(vertex)
                self.assertEqual(zeros,[(1,19*scale),(1,99*scale)])
                self.assertEqual(len(groups[1]),(201*scale-1)//2)
                self.assertEqual(len(groups[1]),len(groups[-1]))
                def profile(group):
                    return Counter(abs(d-e) if a==b else d+e
                                   for i,(a,d) in enumerate(group) for b,e in group[:i])
                left,right = profile(groups[1]),profile(groups[-1])
                self.assertEqual(left[1]-right[1],-1)
                def reduced(profile):
                    result = Counter()
                    for d,n in profile.items(): result[d%period] += n
                    return result
                self.assertEqual(reduced(left),reduced(right))

    def test_growing_lift_compressed_runs_against_physical_shells(self):
        for scale in (3,5,7,11,101):
            half = (scale-1)//2
            lengths = [n*scale for n in (99,79,23)]
            holes = {(1,19*scale),(1,99*scale)}
            signs = {(0,0):-1}
            signs.update({(a,d):rs.residue_lift_sign(half,scale,(a,d))
                          for a,n in enumerate(lengths,1) for d in range(1,n+1)})
            actual = fc.shell_rows(lengths,holes,signs)
            recovered = {}
            for lo,hi,value in rs.growing_lift_shell_runs(scale):
                self.assertGreaterEqual(lo,0)
                self.assertLessEqual(lo,hi)
                for e in range(lo,hi+1):
                    self.assertNotIn(e,recovered)
                    recovered[e] = value
            self.assertEqual(recovered,actual)
            self.assertEqual(sum(abs(c) for c in actual.values()),500*scale-256)
            # The column bound used for arbitrary alternative signings is
            # independent of the chosen lift, including at hole neighbours.
            self.assertTrue(all(sum(abs(c) for c in fc.shell_column(lengths,holes,v).values())<=8
                                for v in signs if v not in holes))

    def test_growing_lift_runs_against_unordered_distances(self):
        from collections import Counter
        # This control counts actual pairs, independently of shell_column.
        for scale in (3,5):
            sides = {1:[], -1:[]}
            for v in [(0,0)]+[(a,d) for a,n in enumerate((99,79,23),1)
                               for d in range(1,n*scale+1)]:
                sign = rs.residue_lift_sign((scale-1)//2,scale,v)
                if sign: sides[sign].append(v)
            difference = Counter()
            for sign,vertices in sides.items():
                for i,(a,d) in enumerate(vertices):
                    for b,e in vertices[:i]:
                        distance = abs(d-e) if a==b else d+e
                        difference[distance] += sign
            expected = defaultdict(int)
            for e,c in difference.items():
                expected[e] += 2*c
                expected[e+1] -= 2*c
            expected = {e:c for e,c in expected.items() if c}
            actual = {e:c for lo,hi,c in rs.growing_lift_shell_runs(scale)
                         for e in range(lo,hi+1)}
            self.assertEqual(actual,expected)

    def test_growing_lift_symbolic_repair_bound_and_damage(self):
        import copy
        for scale in (3,5,7981,15961,10**80+1):
            result = rs.growing_lift_repair_bound(scale)
            self.assertEqual(result['shell_l1'],500*scale-256)
            self.assertEqual(result['minimum_sign_changes'],(500*scale-241)//16)
            self.assertFalse(result['all_pairs_decided'])
            self.assertTrue(rs.verify_saved(result)['verified'])
        result = rs.growing_lift_repair_bound(7981)
        for key,value in (('shell_l1',0),('minimum_sign_changes',1),
                          ('column_l1_upper_bound',7),('all_pairs_decided',True),
                          ('t',True),('retained_vertices',0),('norm_in_half_scale',[0,0])):
            damaged = copy.deepcopy(result)
            damaged[key] = value
            with self.assertRaises(ValueError): rs.verify_saved(damaged)
        for scale in (True,1,2,4,-3,3.0):
            with self.assertRaises(ValueError): rs.growing_lift_repair_bound(scale)
            with self.assertRaises(ValueError): rs.growing_lift_shell_runs(scale)

    def test_residue_lift_all_orders_and_certificate_controls(self):
        for m in (1,2,7,10**25):
            growing = rs.residue_lift_plan([3990*m])
            self.assertEqual(growing['t'],7980*m+1)
            self.assertEqual(growing['block_pairs_per_old_edge'],1)
            self.assertEqual(growing['distance_one_difference'],-1)
        for periods in ([1],[4,8,16],[3,5,7,19],[2,3,5,16,19],[10**50+7]):
            for index in (1,2,10**30):
                plan = rs.residue_lift_plan(periods,index)
                self.assertEqual((plan['t']-1)%7980,0)
                self.assertTrue(all((plan['t']-1)%(2*p)==0 for p in periods))
                self.assertEqual(plan['pair_size'],(201*plan['t']-1)//2)
                self.assertEqual(plan['distance_one_difference'],-1)
                self.assertFalse(plan['exact_homometric'])
                self.assertTrue(rs.verify_saved(plan)['verified'])
        import copy
        plan = rs.residue_lift_plan([3,16,19])
        for key,value in [('t',plan['t']+2),('pair_size',1),
                          ('distance_one_difference',0),('exact_homometric',True),
                          ('base_pair_verified',1),('all_pairs_decided',True)]:
            damaged = copy.deepcopy(plan)
            damaged[key] = value
            with self.assertRaises(ValueError): rs.verify_saved(damaged)
        for periods,index in (([],1),([True],1),([0],1),([3],False),([3],0)):
            with self.assertRaises(ValueError): rs.residue_lift_plan(periods,index)
        for period,scale,vertex in ((0,3,(0,0)),(2,3,(0,0)),(1,3,(True,1)),
                                     (1,3,(0,1)),(1,3,(1,298))):
            with self.assertRaises(ValueError): rs.residue_lift_sign(period,scale,vertex)

    def test_bounded_aggregate_witness_against_tiny_complete_cubes(self):
        rng = random.Random(67219)
        for _ in range(80):
            groups = {}
            while len(groups) < 3:
                groups[tuple(rng.randrange(-3, 4) for _ in range(2))] = rng.randrange(1, 4)
            items = sorted(groups.items())
            feasible = []
            for values in itertools.product(*(range(-n, n+1, 2) for _, n in items)):
                if all(sum(c[i]*v for (c, _), v in zip(items, values)) == 0 for i in range(2)):
                    feasible.append(values)
            result = rs.residue_bounded_search(groups, seconds=5, attempts=32)
            if result['status'] == 'compatible_bounded_aggregates':
                self.assertIn(tuple(result['aggregate_sums']), feasible)
            if not feasible:
                self.assertNotEqual(result['status'], 'compatible_bounded_aggregates')
            # The retained integer operations must reconstruct exact kernel vectors,
            # even when the heuristic never finds a bounded member.
            exact = rs.residue_integer_parity(groups, retain_kernel=True)
            if 'kernel' in exact:
                kernel = exact['kernel']
                values = [0]*kernel['rank']+kernel['parities'][kernel['rank']:]
                for kind, a, b, *rest in reversed(kernel['operations']):
                    if kind == 'swap': values[a], values[b] = values[b], values[a]
                    else: values[a] -= rest[0]*values[b]
                self.assertTrue(all((v-n) % 2 == 0 for (_, n), v in zip(items, values)))
                self.assertTrue(all(sum(c[i]*v for (c, _), v in zip(items, values)) == 0
                                    for i in range(2)))
        # Unbounded compatibility alone cannot pass the bounded verifier.
        groups = {(1,):1, (3,):1}
        with self.assertRaises(ValueError): rs.verify_bounded_residue_witness(groups, [-3, 1])
        self.assertEqual(rs.residue_bounded_search(groups)['status'], 'unknown')
        for values in ([1, 1], [0, 0], [True, 1], [1]):
            with self.assertRaises(ValueError): rs.verify_bounded_residue_witness(groups, values)
        with patch.object(rs.time, 'monotonic', side_effect=itertools.count()):
            self.assertEqual(rs.residue_bounded_search(groups, seconds=0.1)['status'], 'unknown')
        with self.assertRaises(ValueError): rs.residue_bounded_search(groups, attempts=0)

    def test_bounded_resistant_phase_witnesses_and_lifts(self):
        import math
        for period in (4, 8, 16):
            phases = 2*period//math.gcd(7980, 2*period)
            for m in range(1, phases+1):
                scale = 7980*m+1
                for moving in (False, True):
                    def groups_at(t):
                        return rs.residue_shell_groups((99*t, 79*t, 23*t),
                            [(1,19*t if moving else 19), (1,99*t)], period)
                    groups = groups_at(scale)
                    result = rs.residue_bounded_search(groups, seconds=5)
                    self.assertEqual(result['status'], 'compatible_bounded_aggregates')
                    values = result['aggregate_sums']
                    self.assertTrue(rs.verify_bounded_residue_witness(groups, values))
                    # Same columns, same parities, increasing counts: the identical
                    # finite witness remains within bounds on the larger support.
                    for step in (1, 7, 10**12):
                        larger = groups_at(scale+7980*phases*step)
                        self.assertEqual(set(groups), set(larger))
                        self.assertTrue(all(larger[c] >= n and (larger[c]-n) % 2 == 0
                                            for c, n in groups.items()))
                        self.assertTrue(rs.verify_bounded_residue_witness(larger, values))
        saved = dict(result, mode='residue_parity', t=scale, period=period,
                     holes=[(1,19*scale), (1,99*scale)])
        self.assertIn('full shell equations remain unchecked', rs.verify_saved(saved)['claim'])
        saved['aggregate_sums'] = values[:-1]
        with self.assertRaises(ValueError): rs.verify_saved(saved)
        audit = rs.resistant_residue_audit(16, seconds=20, bounded=True)
        self.assertTrue(audit['complete'])
        self.assertEqual([r['compatible'] for r in audit['reports']], [4, 8, 16])
        self.assertIn('bounded residue', audit['scope'])

    def test_residue_groups_against_every_direct_column(self):
        for lengths in ((3, 5, 7), (8, 6, 3), (15, 3, 7)):
            vertices = [(0, 0)]+[(a, d) for a, n in enumerate(lengths, 1)
                                 for d in range(1, n+1)]
            for holes in itertools.combinations(vertices, 2):
                for period in (1, 4, 7):
                    expected = defaultdict(int)
                    for vertex in set(vertices)-set(holes):
                        column = [0]*period
                        for exponent, value in fc.shell_column(lengths, holes, vertex).items():
                            column[exponent % period] += value
                        expected[tuple(column)] += 1
                    self.assertEqual(rs.residue_shell_groups(lengths, holes, period), expected)
        with self.assertRaises(ValueError): rs.residue_shell_groups((3, 5, 7), (), 0)

    def test_fourth_root_states_against_all_literal_assignments(self):
        rng = random.Random(76251)
        for _ in range(60):
            columns = [tuple(rng.randrange(-3, 4) for _ in range(4))
                       for _ in range(rng.randrange(1, 9))]
            groups = defaultdict(int)
            for column in columns:
                groups[column] += 1
            direct = {tuple(sum(s*c[r] for s, c in zip(signs, columns)) % 8
                            for r in range(4))
                      for signs in itertools.product((-1, 1), repeat=len(columns))}
            self.assertEqual(rs.fourth_root_mod8_states(groups), direct)
        # Multiplicity saturation is essential; four copies are not one sign.
        column = (1, 0, 0, 0)
        self.assertIn((0, 0, 0, 0), rs.fourth_root_mod8_states({column: 4}))
        self.assertNotIn((0, 0, 0, 0), rs.fourth_root_mod8_states({column: 1}))

    def test_gap_cover_against_all_actual_hole_placements(self):
        def signature(lengths, holes):
            return tuple(sorted((c, n % 8, min(n, 3))
                                for c, n in rs.residue_shell_groups(lengths, holes).items()))
        # Exceeds the reduction threshold: these actual placements include
        # short/long gaps on both sides and between two holes.
        for length in (45, 153):
            lengths = (length, 3, 7)
            for count in (1, 2):
                def support(depths):
                    return {(1, d) for d in depths} | ({(0, 0)} if count == 1 else set())
                actual = {signature(lengths, support(depths))
                          for depths in itertools.combinations(range(1, length+1), count)}
                covered = {signature(lengths, support(depths))
                           for depths in rs.residue_gap_representatives(length, count)}
                self.assertEqual(actual, covered)
        with self.assertRaises(ValueError): list(rs.residue_gap_representatives(3, 3))

    def test_fourth_root_congruence_all_scale_phases(self):
        result = rs.fourth_root_mod8_census()
        self.assertTrue(result['complete'])
        self.assertFalse(result['all_pairs_decided'])
        self.assertEqual(result['representatives'], 139200)
        self.assertEqual(result['counts'], dict(odd_shell_refused=69600, compatible=69600,
                                               additional_exact_refusal=13260, not_decided=56340))
        self.assertEqual({p['scale_residue'] for p in result['phases']}, set(range(1, 32, 4)))

    def test_odd_group_certificates_against_literal_signings_and_tampering(self):
        rng = random.Random(52919)
        found = 0
        for _ in range(100):
            columns = [tuple(rng.randrange(-2, 3) for _ in range(4))
                       for _ in range(rng.randrange(1, 9))]
            groups = defaultdict(int)
            for column in columns:
                groups[column] += 1
            certificate = rs.residue_zero_certificate(groups)
            if certificate is None:
                continue
            found += 1
            self.assertTrue(rs.verify_residue_zero_certificate(groups, certificate))
            self.assertFalse(any(all(sum(s*c[r] for s, c in zip(signs, columns)) == 0
                                     for r in range(4))
                                 for signs in itertools.product((-1, 1), repeat=len(columns))))
            damaged = dict(certificate, coefficient=certificate['coefficient']+1)
            with self.assertRaises(ValueError): rs.verify_residue_zero_certificate(groups, damaged)
            damaged = dict(certificate, count=certificate['count']+2)
            with self.assertRaises(ValueError): rs.verify_residue_zero_certificate(groups, damaged)
        self.assertGreater(found, 10)

    def test_even_hole_theorems_with_arbitrary_arm_and_depth_choices(self):
        for scale in (1, 5, 9, 13, 7981, 15961):
            lengths = (99*scale, 79*scale, 23*scale)
            for holes in ({(1, 4), (1, 8)}, {(0, 0), (3, 4)}, {(1, 8), (2, 20)},
                          {(1, 4), (2, 2)}, {(0, 0), (3, 6)}, {(1, 12), (1, 18)}):
                zero_holes = sum(depth % 4 == 0 for _, depth in holes)
                groups = rs.residue_shell_groups(lengths, holes)
                if zero_holes == 2:
                    column, weights = (-5, 3, 0, 0), [-7, -1, -3, -5]
                    count = (201*scale-13)//4
                    refused = scale % 8 == 1
                else:
                    column, weights = (-4, 2, -1, 1), [-9, 1, -1, -7]
                    count = (201*scale-9)//4
                    refused = scale % 8 == 5
                self.assertEqual(groups[column], count)
                self.assertTrue(all(sum(a*b for a, b in zip(weights, other))
                                    == (32 if other == column else 0) for other in groups))
                self.assertEqual(count % 2 == 1, refused)
                certificate = dict(column=list(column), count=count, weights=weights, coefficient=32)
                if refused:
                    self.assertTrue(rs.verify_residue_zero_certificate(groups, certificate))
                else:
                    with self.assertRaises(ValueError): rs.verify_residue_zero_certificate(groups, certificate)

    def test_saved_unrestricted_support_refusal(self):
        holes = [[1, 4], [2, 2]]
        groups = rs.residue_shell_groups((790119, 630499, 183563), holes)
        saved = dict(mode='residue_zero', t=7981, period=4, holes=holes,
                     status='support_refused_by_odd_group',
                     certificate=rs.residue_zero_certificate(groups))
        result = rs.verify_saved(saved)
        self.assertTrue(result['verified'])
        self.assertFalse(result['all_pairs_decided'])
        for changed in (dict(saved, t=7982), dict(saved, period=1),
                        dict(saved, holes=holes+holes[:1]), dict(saved, status='unknown')):
            with self.assertRaises(ValueError): rs.verify_saved(changed)

    def test_eighth_root_fixed_holes_infinite_obstruction(self):
        target = (-2, 1, -1, 1, -2, 1, 0, 0)
        weights = [-25, -15, -1, 25, 7, 17, -1, -39]
        holes = {(1, 2), (1, 4)}
        expected_columns = {
            target, (-2,1,0,0,-2,1,-1,1), (-1,1,-3,1,0,0,-1,1),
            (0,-3,2,-2,1,0,0,0), (0,-1,1,-1,1,-2,1,-1),
            (0,0,-1,1,-1,1,-3,1), (1,-2,1,-2,1,0,0,-1),
            (1,-2,1,-1,0,-1,1,-1), (1,0,0,-1,1,-2,1,-2)}
        for scale in (1, 9, 17, 25, 33, 31921):
            lengths = (99*scale, 79*scale, 23*scale)
            # These classes exhaust all columns symbolically for t=1 mod8:
            # centre, the two retained vertices before/among the holes,
            # then eight residues beyond them, and eight on each other arm.
            classes = [(0, 0), (1, 1), (1, 3)]
            classes += [(1, d) for d in range(5, 13)]
            classes += [(a, d) for a in (2, 3) for d in range(1, 9)]
            columns = set()
            for vertex in classes:
                column = [0]*8
                for exponent, value in fc.shell_column(lengths, holes, vertex).items():
                    column[exponent % 8] += value
                columns.add(tuple(column))
            self.assertEqual(columns, expected_columns)
            groups = rs.residue_shell_groups(lengths, holes, 8)
            self.assertEqual(set(groups), expected_columns)
            count = (201*scale-17)//8
            self.assertEqual(groups[target], count)
            self.assertTrue(all(sum(a*b for a, b in zip(weights, column))
                                == (64 if column == target else 0) for column in groups))
            certificate = dict(column=list(target), count=count, weights=weights, coefficient=64)
            if scale % 16 == 1:
                self.assertTrue(rs.verify_residue_zero_certificate(groups, certificate))
                saved = dict(mode='residue_zero', t=scale, period=8,
                             holes=sorted(holes), status='support_refused_by_odd_group',
                             certificate=certificate)
                self.assertTrue(rs.verify_saved(saved)['verified'])
            else:
                with self.assertRaises(ValueError): rs.verify_residue_zero_certificate(groups, certificate)

    def test_integer_residue_parities_against_exhaustive_small_lattices(self):
        rng = random.Random(92753)
        for _ in range(150):
            period, size = rng.randrange(1, 4), rng.randrange(1, 4)
            groups = {}
            while len(groups) < size:
                groups[tuple(rng.randrange(-2, 3) for _ in range(period))] = rng.randrange(1, 4)
            items = sorted(groups.items())
            # In <=3 variables with entries <=2, rank-two primitive kernel
            # coordinates are 2x2 minors of magnitude <=8; rank one needs
            # no larger coordinates. Thus this is a complete tiny control.
            truth = any(all(sum(column[r]*value for (column, _), value in zip(items, values)) == 0
                            for r in range(period))
                        for values in itertools.product(*(range(-8+count%2, 9, 2)
                                                          for _, count in items)))
            result = rs.residue_integer_parity(groups, seconds=5)
            self.assertNotEqual(result['status'], 'unknown')
            self.assertEqual(result['status'] == 'compatible_unbounded_aggregates', truth)
            self.assertFalse(result['all_pairs_decided'])
            if not truth:
                self.assertTrue(rs.verify_residue_parity_certificate(groups, result['certificate']))
            dyadic = rs.residue_dyadic_parity(groups, seconds=5, retain_witness=True)
            self.assertEqual(dyadic['status'], result['status'])
            if not truth:
                certificate = dyadic['certificate']
                self.assertTrue(rs.verify_residue_parity_certificate(groups, certificate))
                self.assertLessEqual(max(abs(w) for w in certificate['weights']), certificate['divisor'])
            else:
                self.assertTrue(rs.verify_residue_aggregate_witness(groups,dyadic['witness']))
        # Compatibility allows group sums outside their physical bounds.
        groups = {(1,): 1, (3,): 1}
        self.assertEqual(rs.residue_integer_parity(groups)['status'], 'compatible_unbounded_aggregates')
        self.assertFalse(any(a+3*b == 0 for a, b in itertools.product((-1, 1), repeat=2)))

    def test_integer_residue_certificates_and_resource_limits(self):
        holes, scale = [(1, 2), (1, 4)], 31921
        groups = rs.residue_shell_groups((99*scale, 79*scale, 23*scale), holes, 16)
        # Finer groups hide the earlier single-group zero, but its parity
        # consequence must survive refinement of the residue quotient.
        self.assertIsNone(rs.residue_zero_certificate(groups))
        result = rs.residue_integer_parity(groups)
        self.assertEqual(result['status'], 'support_refused_by_residue_parity')
        certificate = result['certificate']
        saved = dict(result, mode='residue_parity', t=scale, period=16, holes=holes)
        self.assertTrue(rs.verify_saved(saved)['verified'])
        for damaged in (dict(certificate, divisor=0),
                        dict(certificate, divisor=certificate['divisor']*2),
                        dict(certificate, weights=[0]*16), dict(certificate, weights=[1])):
            with self.assertRaises(ValueError): rs.verify_residue_parity_certificate(groups, damaged)
        limited = rs.residue_integer_parity(groups, max_bits=1)
        self.assertEqual(limited['status'], 'unknown')
        self.assertEqual(limited['reason'], 'coefficient_limit')
        with patch.object(rs.time, 'monotonic', side_effect=itertools.count()):
            limited = rs.residue_integer_parity(groups, seconds=0.1)
        self.assertEqual(limited['status'], 'unknown')
        self.assertEqual(limited['reason'], 'time_limit')
        with self.assertRaises(ValueError):
            rs.verify_saved(dict(limited, mode='residue_parity', t=scale, period=16, holes=holes))
        with self.assertRaises(ValueError): rs.residue_integer_parity(groups, seconds=0)

    def test_dyadic_saturation_and_large_coefficient_differential_controls(self):
        # Every equation is zero modulo 2**30, but dividing out the common
        # power exposes an impossible parity. A small fixed modulus misses it.
        groups = {(1 << 30,): 1, (1 << 31,): 2}
        result = rs.residue_dyadic_parity(groups)
        self.assertEqual(result['status'], 'support_refused_by_residue_parity')
        self.assertTrue(rs.verify_residue_parity_certificate(groups, result['certificate']))
        self.assertGreater(result['modulus_bits'], 30)
        self.assertEqual(rs.residue_dyadic_parity(groups, max_bits=8)['status'], 'unknown')
        with patch.object(rs.time, 'monotonic', side_effect=itertools.count()):
            self.assertEqual(rs.residue_dyadic_parity(groups, seconds=0.1)['status'], 'unknown')
        rng = random.Random(56420)
        for _ in range(100):
            groups = {}
            while len(groups) < 4:
                groups[tuple(rng.randrange(-32, 33) for _ in range(4))] = rng.randrange(1, 5)
            exact = rs.residue_integer_parity(groups, seconds=5)
            dyadic = rs.residue_dyadic_parity(groups, seconds=5)
            self.assertNotEqual(exact['status'], 'unknown')
            self.assertEqual(exact['status'], dyadic['status'])
            if 'certificate' in dyadic:
                self.assertTrue(rs.verify_residue_parity_certificate(groups, dyadic['certificate']))

    def test_resistant_residue_phase_cover_and_unknowns(self):
        for period in (4, 8, 16, 32):
            for m in (1, 2, 3):
                scale = 7980*m+1
                for moving in (False, True):
                    def signature(t):
                        holes = {(1,19*t if moving else 19),(1,99*t)}
                        groups = rs.residue_shell_groups((99*t,79*t,23*t),holes,period)
                        return {(column,count%2) for column,count in groups.items()}
                    self.assertEqual(signature(scale), signature(scale+2*period))
        result = rs.resistant_residue_audit(16, seconds=20)
        self.assertTrue(result['complete'])
        self.assertEqual([r['cases'] for r in result['reports']], [4, 8, 16])
        self.assertTrue(all(r['compatible'] == r['cases'] for r in result['reports']))
        limited = rs.resistant_residue_audit(4, seconds=20, max_bits=1)
        self.assertFalse(limited['complete'])
        self.assertEqual(limited['reports'][0]['unknown'], 4)
        with patch.object(rs.time, 'monotonic', side_effect=itertools.count()):
            self.assertFalse(rs.resistant_residue_audit(4, seconds=0.1)['complete'])
        with self.assertRaises(ValueError): rs.resistant_residue_audit(3)
        with self.assertRaises(ValueError): rs.resistant_residue_audit(512)

    def test_independent_aggregate_witness_and_saved_scope(self):
        groups = {(1,):1,(3,):1}
        result = rs.residue_dyadic_parity(groups,retain_witness=True)
        witness = result['witness']
        self.assertTrue(rs.verify_residue_aggregate_witness(groups,witness))
        changed = witness['aggregate_residues'][:]
        changed[0] ^= 2  # parity preserved, equation broken
        for damaged in (dict(witness,modulus_bits=witness['modulus_bits']-1),
                        dict(witness,aggregate_residues=changed),
                        dict(witness,aggregate_residues=witness['aggregate_residues'][:-1])):
            with self.assertRaises(ValueError): rs.verify_residue_aggregate_witness(groups,damaged)
        scale, holes = 7981, [(1,19),(1,790119)]
        groups = rs.residue_shell_groups((99*scale,79*scale,23*scale),holes,16)
        result = rs.residue_dyadic_parity(groups,retain_witness=True)
        saved = dict(result,mode='residue_parity',t=scale,period=16,holes=holes)
        verified = rs.verify_saved(saved)
        self.assertTrue(verified['verified'])
        self.assertIn('no literal signing',verified['claim'])
        self.assertFalse(verified['all_pairs_decided'])
        del saved['witness']
        with self.assertRaises(ValueError): rs.verify_saved(saved)

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
        for period,k,hole in ((1,2,19),(3,1,19),(3,2,19),(10,2,19),
                              (1,3,1),(2,2,43),(3,2,98)):
            t = period*k+1
            keys,formal = rs.moving_periodic_system(period,hole)
            positions = {v:i for i,v in enumerate(keys)}
            lengths,holes = [99*t,79*t,23*t],{(1,hole*t),(1,99*t)}
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
        for hole in (0,99,1.5):
            with self.assertRaises(ValueError): rs.moving_periodic_system(1,hole)

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

    def test_full_partition_subdivision_and_resistant_upper_bound(self):
        for lengths,scale in (((1,2,3),2),((2,3,4),3),((99,79,23),3),((3,3,7),4)):
            report = rs.full_partition_subdivision_audit(lengths,scale)
            self.assertTrue(report['verified'])
            self.assertEqual(report['old_columns'],1+sum(lengths))
            self.assertEqual(report['nongrid_columns'],(scale-1)*sum(lengths))
        for m in (1,2,5):
            t = 7980*m+1
            report = rs.full_partition_subdivision_bound((99,79,23),t)
            self.assertEqual(report['base_divisor'],4)
            self.assertEqual(report['base_quotient_sum'],51)
            self.assertTrue(report['inherited_from_base'])
            self.assertEqual(report['homometric_pair_upper_bound'],(201*t-1)//2)
            self.assertFalse(report['all_pairs_decided'])
        # No unsupported strengthening on an odd total or an unrefused base.
        report = rs.full_partition_subdivision_bound((99,79,23),2)
        self.assertFalse(report['inherited_from_base'])
        self.assertEqual(report['homometric_pair_upper_bound'],201)
        report = rs.full_partition_subdivision_bound((3,3,7),1)
        self.assertFalse(report['full_partition_refused'])
        self.assertEqual(report['homometric_pair_upper_bound'],7)
        for scale in (0,1.5,True):
            with self.assertRaises(ValueError): rs.full_partition_subdivision_bound((99,79,23),scale)

    def test_universal_boundary_coefficients_and_uniform_refusal(self):
        for period,hole in ((2,19),(3,19),(4,19),(11,19),(2,1),(3,43),(7,98)):
            audit = rs.moving_boundary_audit(period,hole)
            self.assertTrue(audit['verified'])
            self.assertEqual(audit['universal_variables'],1004)
            self.assertEqual(audit['endpoint_identifications'],201*max(0,4-period))
        original = rs.moving_boundary_system
        def damaged(hole):
            keys,rows = original(hole)
            row = next(iter(rows.values()))
            i = next(iter(row))
            row[i] += 1
            return keys,rows
        with patch.object(rs,'moving_boundary_system',side_effect=damaged):
            with self.assertRaises(AssertionError): rs.moving_boundary_audit(3,19)
        result = rs.moving_boundary_refusal(19,seconds=20)
        self.assertEqual(result['status'],'every_formal_period_refused')
        self.assertEqual(result['coarse_count'],4)
        self.assertEqual(len(result['branches']),4)
        self.assertTrue(all(b['complete'] and b['refused'] for b in result['branches']))
        self.assertFalse(result['all_pairs_decided'])
        with self.assertRaises(ValueError): rs.verify_saved(result)
        with self.assertRaises(ValueError): rs.moving_boundary_audit(1)
        # A compatible necessary relaxation must remain unknown.
        catalog = rs.coarse_catalog(19,seconds=20)
        compatible = dict(complete=True,conflict=False,size=1004)
        with patch.object(rs,'coarse_catalog',return_value=catalog), patch.object(
                rs,'joint_sign_closure',return_value=compatible):
            self.assertEqual(rs.moving_boundary_refusal()['status'],'unknown')

    def test_short_ternary_recovery_on_every_small_modular_signing(self):
        rng = random.Random(241120)
        for size in range(1,8):
            for _ in range(15):
                rows = [{i:rng.randrange(-3,4) for i in range(size)} for _ in range(3)]
                analysis = rs.ternary_analysis(size,rows,retain_kernel=True)
                extra = rs.ternary_short_sign_rows(analysis['kernel'])
                for v in itertools.product((-1,1),repeat=size):
                    if all(sum(c*v[i] for i,c in row.items())%3==0 for row in rows):
                        self.assertTrue(all(sum(c*v[i] for i,c in row.items())==0 for row in extra))
        # A genuinely new integer consequence of a modular three-term recovery.
        kernel = dict(free=[1,2,3],expressions={0:(7,0),1:(1,0),2:(2,0),3:(4,0)})
        self.assertEqual(rs.ternary_short_sign_rows(kernel),[{0:1,1:-1,2:-1,3:-1}])
        # Four terms cannot be lifted this way: sums +/-2 and +/-4 are both allowed.
        kernel = dict(free=[1,2,3,4],expressions={0:(15,0)})
        self.assertEqual(rs.ternary_short_sign_rows(kernel),[])
        for size in range(2,7):
            for _ in range(8):
                rows = [{i:rng.randrange(-2,3) for i in range(size)} for _ in range(3)]
                truth = {v for v in itertools.product((-1,1),repeat=size)
                         if all(sum(c*v[i] for i,c in row.items())==0 for row in rows)}
                reduced = rs.joint_sign_closure(size,rows,seconds=5,short_recovery=True)
                self.assertTrue(reduced['complete'])
                if reduced['conflict']:
                    self.assertFalse(truth)
                    continue
                lifted = set()
                for v in itertools.product((-1,1),repeat=reduced['size']):
                    if all(sum(c*v[i] for i,c in row.items())==0 for row in reduced['rows']):
                        lifted.add(tuple(s*v[i] for i,s in reduced['aliases']))
                self.assertEqual(lifted,truth)

    def test_odd_distance_obstruction_matches_all_colour_splits(self):
        for k in range(1,9):
            for black in range(2*k+1):
                feasible = any(a*(k-a)==(black-a)*(k-black+a)
                               for a in range(k+1) if 0<=black-a<=k)
                self.assertEqual(feasible,black%2==0 or black==k)
        # Actual trees, checking odd distances directly rather than shell columns.
        for lengths in ((1,1,1),(1,2,2),(1,3,3),(2,2,3)):
            vertices = [(0,0)]+[(a,d) for a,n in enumerate(lengths,1)
                                for d in range(1,n+1)]
            for holes in itertools.combinations(vertices,2):
                support = [v for v in vertices if v not in holes]
                if len(support)%2: continue
                report = rs.bipartition_support_obstruction(lengths,holes)
                k = len(support)//2
                feasible = False
                def odd_pairs(word):
                    return sum((abs(d-e) if a==b else d+e)%2
                               for i,(a,d) in enumerate(word) for b,e in word[:i])
                for positive in itertools.combinations(support,k):
                    negative = [v for v in support if v not in positive]
                    if odd_pairs(positive)==odd_pairs(negative): feasible = True
                self.assertEqual(report['obstructed'],not feasible)
        for m in (1,2,9):
            t = 7980*m+1
            lengths = (99*t,79*t,23*t)
            for holes in (((1,99*t),(1,2*t)),((0,0),(3,1))):
                self.assertTrue(rs.bipartition_support_obstruction(lengths,holes)['obstructed'])
            self.assertFalse(rs.bipartition_support_obstruction(lengths,((1,99*t),(1,19*t)))['obstructed'])
            self.assertFalse(rs.bipartition_support_obstruction(lengths,((0,0),(2,2)))['obstructed'])
        with self.assertRaises(ValueError): rs.bipartition_support_obstruction((1,1,1),((0,1),))
        with self.assertRaises(ValueError): rs.bipartition_support_obstruction((1,1,1),((0,0),(0,0)))

    def test_desubdivision_projection_keeps_all_columns_and_holes(self):
        for period,hole in ((1,1),(2,19),(10,19),(3,43),(4,98)):
            audit = rs.coarse_projection_audit(period,hole)
            self.assertTrue(audit['verified'])
            self.assertEqual(audit['old_variables'],200)
            self.assertEqual(audit['inserted_columns_cancelled'],201*period)
        # An altered formal coefficient must fail the independent projection.
        original = rs.moving_periodic_system
        def damaged(period,hole):
            keys,rows = original(period,hole)
            row = next(iter(rows.values()))
            i = next(iter(row))
            row[i] += 1
            return keys,rows
        with patch.object(rs,'moving_periodic_system',side_effect=damaged):
            with self.assertRaises(AssertionError): rs.coarse_projection_audit(2,19)

    def test_rational_cube_filter_against_complete_small_sign_cubes(self):
        rng = random.Random(241119)
        for size in range(1,8):
            for _ in range(12):
                rows = [{i:rng.randrange(-3,4) for i in range(size)} for _ in range(3)]
                truth = {v for v in itertools.product((-1,1),repeat=size)
                         if all(sum(c*v[i] for i,c in row.items())==0 for row in rows)}
                cube = rs.kernel_sign_patterns(size,rows,seconds=5)
                self.assertTrue(cube['complete'])
                restored = set()
                for bits in cube['patterns']:
                    values = tuple(sum(c*(1 if bits>>j&1 else -1)
                                       for j,c in enumerate(cube['forms'][i][0]))
                                   //cube['forms'][i][1] for i in range(size))
                    restored.update((values,tuple(-v for v in values)))
                self.assertEqual(restored,truth)
        self.assertFalse(rs.kernel_sign_patterns(3,[],max_free=2)['complete'])
        with patch.object(rs.time,'monotonic',side_effect=itertools.count()):
            self.assertFalse(rs.kernel_sign_patterns(3,[],seconds=0.1)['complete'])

    def test_coarse_catalog_and_independent_distance_verifier(self):
        catalog = rs.coarse_catalog(19,seconds=20)
        self.assertTrue(catalog['complete'])
        self.assertEqual(catalog['count'],4)
        self.assertEqual(catalog['nullity'],20)
        self.assertEqual(rs.coarse_catalog(1,seconds=20)['count'],0)
        for values in catalog['assignments']:
            assignment = [[list(k),v] for k,v in zip(catalog['keys'],values)]
            report = rs.verify_coarse_assignment(19,assignment)
            self.assertEqual(report['pair_size'],100)
            self.assertFalse(report['all_pairs_decided'])
            saved = dict(mode='coarse',status='sat',hole=19,assignment=assignment)
            self.assertTrue(rs.verify_saved(saved)['verified'])
            # Flip a pair of opposite signs, preserving size and disjointness.
            changed = [[k[:],v] for k,v in assignment]
            i = next(i for i,(_,v) in enumerate(changed) if i and v==1)
            j = next(i for i,(_,v) in enumerate(changed) if i and v==-1)
            changed[i][1] *= -1
            changed[j][1] *= -1
            with self.assertRaises(ValueError): rs.verify_coarse_assignment(19,changed)
            with self.assertRaises(ValueError): rs.verify_coarse_assignment(19,assignment+assignment[:1])
        with self.assertRaises(ValueError):
            rs.verify_saved(dict(mode='coarse',status='unknown',hole=19))

    def test_conditioned_search_cannot_refuse_unfinished_branches(self):
        # Control flow only: mathematical closure is checked exhaustively above.
        incomplete = dict(complete=False,stage='dimension_limit')
        with patch.object(rs,'coarse_catalog',return_value=incomplete):
            result = rs.moving_coarse_search(2,19,seconds=1)
        self.assertEqual(result['status'],'unknown')
        self.assertFalse(result['all_pairs_decided'])
        with self.assertRaises(ValueError):
            rs.verify_saved(dict(mode='moving_coarse',status='ansatz_refused_by_coarse_branches',period=10))

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
