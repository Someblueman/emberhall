import collections
import unittest
import balance_elimination as be
import full_shorter_coupling as fc
import parametric_balance_distance as pd


class ParametricBalanceTests(unittest.TestCase):
    def test_affine_order_proof_on_whole_ray(self):
        proof,segments,counts = pd.symbolic_coefficients()
        self.assertEqual(proof.minimum_t,21)
        self.assertTrue(proof.verify())
        self.assertEqual(len(segments),98)
        self.assertEqual(counts,{-4:(0,2),-3:(0,5),-2:(7,-7),-1:(29,-3),
                                0:(14,6),1:(24,-7),2:(2,2),3:(3,0),4:(0,2)})
        # These are linear polynomial identities, not values at chosen t.
        total = (sum(a for a,b in counts.values()),sum(b for a,b in counts.values()))
        weighted = (sum(c*a for c,(a,b) in counts.items()),
                    sum(c*b for c,(a,b) in counts.items()))
        self.assertEqual(total,(79,0))
        self.assertEqual(weighted,(-6,-1))
        for left,right,margin in proof.inequalities:
            a,b = pd.minus(right,left)
            self.assertGreaterEqual(a,0)
            self.assertGreaterEqual(a*21+b,margin)

    def test_symbolic_coefficients_against_exact_depth_compiler(self):
        proof,segments,counts = pd.symbolic_coefficients()
        for t in (21,22,23,31,2661):
            exact = be.balance_coefficients(t,19)
            represented = {i:c for lo,hi,c in segments
                           for i in range(pd.value(lo,t),pd.value(hi,t)+1)}
            self.assertEqual(represented,exact)
            self.assertEqual(collections.Counter(exact.values()),
                             {c:pd.value(n,t) for c,n in counts.items()})

    def test_interval_operations_and_strict_empty_threshold(self):
        proof = pd.OrderProof()
        # [t,20] is empty for all integer t>=21, not at20.
        self.assertIsNone(proof.intersect(((1,0),(1,10)),((0,1),(0,20))))
        self.assertEqual(proof.minimum_t,21)
        self.assertTrue(proof.verify())
        with self.assertRaises(ArithmeticError):proof.require((1,0),(0,1000))
        s = [((1,1),(2,3),2)]
        self.assertEqual(pd.shift(s,(3,-2)),[((4,-1),(5,1),2)])
        self.assertEqual(pd.reflect(s,(5,0)),[((3,-3),(4,-1),2)])
        self.assertEqual(pd.add(s,pd.scale(s,-1)),[])
        proof = pd.OrderProof()
        proof.require((0,8),(1,0),1)
        self.assertEqual(proof.minimum_t,9)
        self.assertTrue(proof.verify())
        proof.minimum_t = 8
        self.assertFalse(proof.verify())

    def test_closed_bounds_and_resistant_substitution(self):
        for t in (21,22,23,31,101):
            coefficients = be.balance_coefficients(t,19)
            for sigma in (-1,1):
                exact = be.constant_word_distance_bounds(t,19,sigma,coefficients)
                self.assertEqual(pd.distance_bounds(t,sigma),exact)
        # Symbolic substitution t=2660k+1 in the closed ceilings. Large k
        # does not allocate a tree or pretend to be a large computation.
        for k in (1,2,10**20):
            t = 2660*k+1
            self.assertEqual(pd.distance_bounds(t,1),
                             dict(all_positive=1995*k-4,all_negative=1995*k-3))
            self.assertEqual(pd.distance_bounds(t,-1),
                             dict(all_positive=1995*k-3,all_negative=1995*k-4))

    def test_tight_balance_only_controls_independently_summed(self):
        for t in (21,23,31):
            for sigma in (-1,1):
                for constant in (-1,1):
                    y,middle = pd.balance_tight_word(t,sigma,constant)
                    self.assertEqual(set(y.values()),{-1,1})
                    self.assertFalse(set(middle.values())-{-1,1})
                    expected = pd.distance_bounds(t,sigma)[
                        'all_positive' if constant==1 else 'all_negative']
                    self.assertEqual(sum(s!=constant for s in y.values()),expected)
                    signs = fc.linear_completion(t,19,sigma,y,middle)
                    self.assertEqual(sum(signs.values()),0)
                    # Tightness is for balance alone. These examples fail
                    # the literalness required for a homometric signing.
                    self.assertTrue(any(s not in (-1,1) for s in signs.values()))

    def test_two_parameter_cone_and_general_hole_controls(self):
        proof,segments,counts = pd.symbolic_coefficients(pd.AffineH(1,0),pd.ConeProof())
        self.assertTrue(proof.verify())
        self.assertEqual(len(proof.inequalities),481)
        for left,right,margin in proof.inequalities:
            a,b = pd.minus(right,left)
            b = pd.AffineH.lift(b)
            self.assertGreaterEqual(min(a,a+b.slope,5*a+3*b.slope+b.intercept-margin),0)
        for t,h in ((5,3),(6,3),(6,4),(17,15),(21,3),(31,29)):
            represented = {}
            for lo,hi,c in segments:
                def evaluate(endpoint):
                    a,b = endpoint
                    b = pd.AffineH.lift(b)
                    return a*t+b.slope*h+b.intercept
                represented.update({i:c for i in range(evaluate(lo),evaluate(hi)+1)})
            self.assertEqual(represented,be.balance_coefficients(t,h))
        for t,h in ((17,3),(17,15),(21,10)):
            coefficients = be.balance_coefficients(t,h)
            self.assertEqual(pd.distance_bounds(t,1,h),
                             be.constant_word_distance_bounds(t,h,1,coefficients))
            y,middle = pd.balance_tight_word(t,1,1,h)
            self.assertEqual(sum(fc.linear_completion(t,h,1,y,middle).values()),0)
        # A genuine two-parameter crossing is rejected rather than resolved
        # by numerical samples or an arbitrary lexicographic choice.
        with self.assertRaises(ArithmeticError):
            pd.ConeProof().require((1,pd.AffineH(0,0)),(0,pd.AffineH(10,0)))

    def test_input_scope(self):
        for t,sigma in ((16,1),(20,1),(True,1),(21,0),(21,True)):
            with self.assertRaises(ValueError):pd.distance_bounds(t,sigma)
        with self.assertRaises(ValueError):pd.balance_tight_word(22,1,1)
        with self.assertRaises(ValueError):pd.balance_tight_word(21,1,0)
        with self.assertRaises(ValueError):pd.resistant_check(0)


if __name__ == '__main__':
    unittest.main()
