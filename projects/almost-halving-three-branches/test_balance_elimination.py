import itertools
import random
import unittest
import balance_elimination as be
import full_shorter_coupling as fc
import second_word_forcing as sw
from test_aperiodic_completion import bfs_shells


class BalanceTests(unittest.TestCase):
    def test_integer_identity_including_endpoints(self):
        rng = random.Random(721993)
        for t in (1,2,3,7,11):
            for h in sorted({0,1,2*t-2,2*t-1}):
                y = {i:rng.randrange(-3,4) for i in range(1,79*t+1)}
                m = {i:rng.randrange(-4,5) for i in range(13*t+1,18*t+1)}
                zero = dict.fromkeys(m,0)
                sigma = rng.randrange(-2,3) if h else 0
                baseline = sum(fc.linear_completion(t,h,sigma,y,zero).values())
                actual = sum(fc.linear_completion(t,h,sigma,y,m).values())
                expected = baseline + sum(c*m[r] for r,c in be.middle_balance_weights(t,h).items())
                self.assertEqual(actual,expected,(t,h))

    def test_every_middle_column_small_boundaries(self):
        for t in (1,2,3):
            for h in range(2*t):
                y = dict.fromkeys(range(1,79*t+1),0)
                m = dict.fromkeys(range(13*t+1,18*t+1),0)
                weights = be.middle_balance_weights(t,h)
                for r in m:
                    m[r] = 1
                    self.assertEqual(sum(fc.linear_completion(t,h,0,y,m).values()),weights.get(r,0))
                    m[r] = 0

    def test_exact_attainable_totals_by_exhaustive_literal_middle(self):
        for t,h in ((1,0),(1,1),(2,2),(2,3)):
            weights = be.middle_balance_weights(t,h)
            # Independent direct candidate sums at t=1, then exhaustive
            # weighted signs at the larger boundary with a doubled endpoint.
            if t == 1:
                y = dict.fromkeys(range(1,79*t+1),1)
                attainable = {sum(fc.linear_completion(t,h,1 if h else 0,y,
                              dict(zip(range(13*t+1,18*t+1),v))).values())
                              for v in itertools.product((-1,1),repeat=5*t)}
                baseline = -6*t-1+(1 if h else -1)
            else:
                baseline = 0
                attainable = {sum(c*s for c,s in zip(weights.values(),v))
                              for v in itertools.product((-1,1),repeat=len(weights))}
            n = 3*t+1
            self.assertEqual(attainable,set(range(baseline-n,baseline+n+1,2)))
        for t,h in ((1,0),(1,1),(2,2),(3,5)):
            n = 3*t+1
            for baseline in range(-n-3,n+4):
                m = be.balanced_middle(t,h,baseline)
                if m is None:
                    self.assertTrue(abs(baseline)>n or (baseline+n)%2)
                else:
                    self.assertEqual(set(m.values()) - {-1,1},set())
                    self.assertEqual(baseline+sum(c*m[r] for r,c in be.middle_balance_weights(t,h).items()),0)

    def test_uniform_second_word_all_scale_control_and_discrimination(self):
        for t in (1,2,3,11,31):
            for h in sorted({0,1,2*t-1}):
                for sigma in ((-1,1) if h else (0,)):
                    p = dict(t=t,h=h,centre=sigma,arm2='+'*(79*t))
                    result = be.second_word_balance(p)
                    self.assertEqual(result['baseline'],-6*t-1+sigma if h else -6*t-2)
                    self.assertTrue(result['balance_excluded'])
                    self.assertFalse(result['existence_decided'])
        p = dict(t=11,h=19,centre=1,arm2='+'*869)
        self.assertFalse(sw.second_word_constraint(p)['excluded'])
        self.assertTrue(be.second_word_balance(p)['balance_excluded'])

    def test_literal_candidate_independently_counted(self):
        t,h = 11,19
        y = dict.fromkeys(range(1,79*t+1),1)
        middle = dict.fromkeys(range(13*t+1,18*t+1),1)
        signs = fc.linear_completion(t,h,1,y,middle)
        self.assertTrue(all(s in (-1,1) for s in signs.values()))
        left = [v for v,s in signs.items() if s == 1]
        right = [v for v,s in signs.items() if s == -1]
        self.assertEqual(len(left)-len(right),1-3*t)
        # Explicit distance counts, independent of the polynomial columns.
        _,pair = bfs_shells([99*t,79*t,23*t],signs)
        self.assertNotEqual(pair[1],pair[-1])
        # A balanced swap preserves balance but is still rejected by distance.
        signs[left[0]],signs[right[0]] = -1,1
        self.assertEqual(sum(signs.values()),1-3*t)
        _,pair = bfs_shells([99*t,79*t,23*t],signs)
        self.assertNotEqual(pair[1],pair[-1])

    def test_transposed_second_word_coefficients(self):
        rng = random.Random(8021)
        for t,h in ((1,0),(1,1),(2,2),(3,5),(11,19)):
            coefficients = be.balance_coefficients(t,h)
            y = {i:rng.randrange(-3,4) for i in coefficients}
            zero = dict.fromkeys(range(13*t+1,18*t+1),0)
            sigma = 1 if h else 0
            self.assertEqual(sigma+sum(c*y[r] for r,c in coefficients.items()),
                             sum(fc.linear_completion(t,h,sigma,y,zero).values()))
            # Independently probe every second-arm column at the smallest
            # boundary, rather than only checking the transposed program.
            if t == 1:
                y = dict.fromkeys(y,0)
                for r,c in coefficients.items():
                    y[r] = 1
                    self.assertEqual(sum(fc.linear_completion(t,h,0,y,zero).values()),c)
                    y[r] = 0

    def test_pass_is_balance_only(self):
        word = '++++-+-++----+--++-------+--++----+--++--+-++-+++--+-++---+++--+----+-+++--+-+-'
        payload = dict(t=1,h=1,centre=1,arm2=word)
        result = be.second_word_balance(payload)
        self.assertFalse(result['balance_excluded'])
        self.assertFalse(result['existence_decided'])
        y = {i:1 if c=='+' else -1 for i,c in enumerate(word,1)}
        middle = be.balanced_middle(1,1,result['baseline'])
        signs = fc.linear_completion(1,1,1,y,middle)
        self.assertEqual(sum(signs.values()),0)
        self.assertTrue(any(s not in (-1,1) for s in signs.values()))

    def test_constant_distance_lower_bound_small_exhaustive(self):
        # A small independent weighted functional: no one-flip word can
        # reach the window; two flips can. The compiler domain is tested above.
        coefficients = {1:-4,2:-3,3:-2,4:-1}
        bounds = be.constant_word_distance_bounds(1,1,1,coefficients)
        for signs in itertools.product((-1,1),repeat=4):
            baseline = 1+sum(c*s for c,s in zip(coefficients.values(),signs))
            if abs(baseline) <= 4:
                self.assertGreaterEqual(signs.count(-1),bounds['all_positive'])
                self.assertGreaterEqual(signs.count(1),bounds['all_negative'])

    def test_joint_subsystem_exhaustively(self):
        rng = random.Random(2007)
        for t,h in ((1,0),(2,2)):
            weights = {r-13*t:c for r,c in be.middle_balance_weights(t,h).items()}
            attainable = {}
            for values in itertools.product((-1,1),repeat=5*t):
                z = dict(enumerate(values,1))
                diff = tuple((z[7*t-i-h]-z[7*t-i-h-1])
                             -(z[i-h]-z[i-h-1]) for i in range(2*t,5*t+1))
                attainable.setdefault(diff,set()).add(sum(c*z[r] for r,c in weights.items()))
            # Enumerate all small forcing values at the smallest endpoint;
            # at the larger endpoint probe independent forcing and each
            # attainable difference profile, covering both accepted/rejected.
            if t == 1:
                forcings = [dict(enumerate(v,1)) for v in
                            itertools.product((-2,0,2),repeat=5)]
            else:
                forcings = [{i:rng.choice((-4,-2,0,2,4)) for i in range(1,5*t+1)}
                            for _ in range(100)]
                for diff in attainable:
                    b = dict.fromkeys(range(1,5*t+1),0)
                    for i,d in zip(range(2*t,5*t+1),diff):
                        if i < 7*t-i:
                            b[i] = d
                    forcings.append(b)
            for b in forcings:
                diff = tuple(b[i]-b[7*t-i] for i in range(2*t,5*t+1))
                for baseline in range(-3*t-3,3*t+4):
                    result = be.joint_reflected_balance(t,h,baseline,b)
                    self.assertEqual(not result['joint_excluded'],
                                     -baseline in attainable.get(diff,set()),(t,h,b,baseline))

    def test_joint_stronger_than_separate_checks_actual_word(self):
        word = '+-+---+++++-++-++-+++++-++-+----------+++++++--+-+-+-+-++-+----+++++++-++++++++'
        p = dict(t=1,h=0,centre=0,arm2=word)
        self.assertFalse(be.second_word_balance(p)['balance_excluded'])
        reflected = sw.second_word_constraint(p)
        self.assertFalse(reflected['excluded'])
        self.assertTrue(reflected['individual_middle_row_bound_passed'])
        result = be.second_word_balance(p,joint=True)
        self.assertTrue(result['joint_reflected_balance']['joint_excluded'])
        # Check the claim against every actual middle word without using
        # the pair-elimination algorithm or its interval representation.
        y = {i:1 if c=='+' else -1 for i,c in enumerate(word,1)}
        for values in itertools.product((-1,1),repeat=5):
            signs = fc.linear_completion(1,0,0,y,dict(zip(range(14,19),values)))
            residual = fc.shell_rows(*fc.geometry(1,0),signs)
            if all(residual.get(93+i,0)==residual.get(93+7-i,0)
                   for i in range(2,6)):
                self.assertNotEqual(sum(signs.values()),0)

    def test_validation(self):
        for t,h in ((0,0),(True,0),(2,4),(2,-1)):
            with self.assertRaises(ValueError):be.middle_balance_weights(t,h)
        with self.assertRaises(ValueError):be.balance_window(1,0,True)
        for payload in (dict(t=1,h=0,centre=1,arm2='+'*79),
                        dict(t=1,h=1,centre=1,arm2='+'*78)):
            with self.assertRaises(ValueError):be.second_word_balance(payload)


if __name__ == '__main__':
    unittest.main()
