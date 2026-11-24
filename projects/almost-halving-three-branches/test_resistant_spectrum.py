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
