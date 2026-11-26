import itertools
import unittest

import numpy as np
from numpy.testing import assert_allclose

from transient_law import gaussian_bounds
from uniform_start import box_norm, box_gaussian_bounds, initial_box, conditioned_comparison


class UniformStartChecks(unittest.TestCase):
    def test_all_four_envelopes_dominate_exhaustive_box_corners(self):
        rng=np.random.default_rng(781203)
        for dimension in [1,2,4,8]:
            for _ in range(7):
                a=rng.normal(size=(5,dimension));c=rng.normal(size=5)
                radii=rng.uniform(0,2,dimension)
                if dimension>1:radii[1]=0
                result=box_norm(c,a,radii)
                exact=max(np.linalg.norm(c+a@(radii*np.array(z)))
                          for z in itertools.product([-1,1],repeat=dimension))
                for name in ['upper','triangle','spectral','coordinate','gram']:
                    self.assertGreaterEqual(result[name]+1e-12,exact)
                self.assertLessEqual(result['lower'],exact+1e-12)

    def test_nonnormal_and_cancellation_sensitive_geometry(self):
        a=np.array([[30.,-29.,.01],[0.,.02,-.01],[0.,0.,.001]])
        c=np.array([-.5,.2,-.1]);r=np.array([.7,1.1,.3])
        result=box_norm(c,a,r)
        exact=max(np.linalg.norm(c+a@(r*np.array(z))) for z in itertools.product([-1,1],repeat=3))
        self.assertGreaterEqual(result['upper']+1e-12,exact)
        assert_allclose(result['lower'],exact,rtol=1e-12)
        # Opposing mean/map coordinates are kept inside the absolute quadratic bound.
        g=box_norm(np.array([1.,-1.]),np.array([[1.],[1.]]),np.ones(1))
        assert_allclose(g['gram'],2.,rtol=1e-14)
        self.assertLess(g['gram'],g['triangle'])

    def test_degenerate_boxes_and_zero_map(self):
        c=np.array([.2,-.7])
        for a,r in [(np.ones((2,4)),np.zeros(4)),(np.empty((2,0)),np.empty(0)),
                    (np.zeros((2,3)),np.ones(3))]:
            result=box_norm(c,a,r)
            assert_allclose(result['upper'],np.linalg.norm(c),rtol=1e-14)
            assert_allclose(result['lower'],np.linalg.norm(c),rtol=1e-14)

    def test_uniform_divergences_dominate_every_corner_and_interior(self):
        rng=np.random.default_rng(781204)
        for dimension in [1,2,4]:
            size=5
            a=rng.normal(size=(size,size));p=a@a.T+np.eye(size)
            a=rng.normal(size=(size,size));q=a@a.T+.3*np.eye(size)
            c=rng.normal(size=size);mapping=rng.normal(size=(size,dimension));r=rng.uniform(.1,1,dimension)
            result=box_gaussian_bounds(p,q-p,c,mapping,r)
            points=list(itertools.product([-1,1],repeat=dimension))+list(rng.uniform(-1,1,(50,dimension)))
            for point in points:
                exact=gaussian_bounds(p,c+mapping@(r*np.array(point)),q-p)
                for key in ['kl','negative_log_affinity']:
                    self.assertGreaterEqual(result[key+'_upper']+1e-11,exact[key])
                self.assertGreaterEqual(result['tv_upper']+1e-12,exact['tv_upper'])

    def test_point_box_recovers_equal_covariance_bound(self):
        p=np.array([[2.,.3],[.3,1.]])
        mean=np.array([.2,-.1])
        expected=gaussian_bounds(p,mean,np.zeros_like(p))
        result=box_gaussian_bounds(p,np.zeros_like(p),mean,np.eye(2),np.zeros(2))
        assert_allclose(result['kl_upper'],expected['kl'],rtol=1e-13)
        assert_allclose(result['negative_log_affinity_upper'],expected['negative_log_affinity'],rtol=1e-13)
        assert_allclose(result['tv_upper'],expected['tv_upper'],rtol=1e-13)

    def test_physical_box_uses_log_consumers_and_unlogged_resources(self):
        x=np.array([2.,7.]);resources=np.array([.2,.8,1.3])
        center,radii=initial_box(x,resources)
        for sign in [-1,1]:
            perturbation=center.copy();perturbation[:5]+=sign*radii
            assert_allclose(x*np.exp(perturbation[:2]),.5 if sign<0 else 2.,rtol=1e-14)
            assert_allclose(resources+perturbation[2:5],.5 if sign<0 else 2.,rtol=1e-14)
            assert_allclose(perturbation[5:],0,atol=0)
        # The all-ones accepted baseline belongs to the box: consumer z=0,
        # resource z=-1/3. No assumption that both coordinate centers are one.
        baseline=center.copy();baseline[2:5]-=radii[2:]/3
        assert_allclose(x*np.exp(baseline[:2]),1.,rtol=1e-14)
        assert_allclose(resources+baseline[2:5],1.,rtol=1e-14)
        with self.assertRaises(ValueError):initial_box(np.array([0.]),resources)

    def test_scalar_mean_box_divergence_extrema_are_exact(self):
        for variance in [.2,1.,3.]:
            p=np.array([[1.7]]);d=np.array([[variance-1.7]])
            c=np.array([-.3]);mapping=np.array([[.2,-.8]])
            radii=np.array([.4,.7])
            result=box_gaussian_bounds(p,d,c,mapping,radii)
            corners=[gaussian_bounds(p,c+mapping@(radii*np.array(z)),d)
                     for z in itertools.product([-1,1],repeat=2)]
            for key in ['kl','negative_log_affinity']:
                assert_allclose(result[key+'_upper'],max(v[key] for v in corners),rtol=1e-13)

    def test_common_event_conditional_tv_bound_on_exhaustive_discrete_laws(self):
        # Exact integer check over every pair of four-cell laws on a sixth grid.
        laws=[v for v in itertools.product(range(7),repeat=4) if sum(v)==6 and sum(v[:2])>0]
        for left in laws:
            p=sum(left[:2])
            for right in laws:
                q=sum(right[:2])
                total=sum(abs(a-b) for a,b in zip(left,right))
                numerator=sum(abs(left[i]*q-right[i]*p) for i in range(2))
                # TV(P_A,Q_A)<=TV(P,Q)/max(P(A),Q(A)), with all factors canceled.
                self.assertLessEqual(numerator*max(p,q),total*p*q)
                result=conditioned_comparison(total/12,p/6)
                if result['guarantees_positive_transient_success']:
                    self.assertGreaterEqual(result['tv_upper']+1e-14,numerator/(2*p*q))

    def test_conditioning_bound_is_sharp_and_does_not_invent_survivors(self):
        result=conditioned_comparison(.1,.4)
        assert_allclose(result['tv_upper'],.25,rtol=1e-14)
        # P=(.2,.2,.6), Q=(.3,.1,.6), common event first two cells.
        self.assertAlmostEqual(abs(.2/.4-.3/.4),result['tv_upper'])
        for delta,p in [(0.,0.),(.2,.2),(.3,.2)]:
            result=conditioned_comparison(delta,p)
            self.assertEqual(result['tv_upper'],1.)
            self.assertFalse(result['guarantees_positive_transient_success'])
        for delta,p in [(-.1,.4),(.1,1.1),(np.nan,.4)]:
            with self.assertRaises(ValueError):conditioned_comparison(delta,p)

    def test_identical_unconditional_laws_do_not_justify_different_filters(self):
        # Distinct disjoint success sets can give conditional TV=1 even at delta=0.
        p=np.array([.25,.25,.25,.25]);left=p*np.array([1,1,0,0]);right=p*np.array([0,0,1,1])
        left/=left.sum();right/=right.sum()
        self.assertEqual(abs(left-right).sum()/2,1.)
        self.assertEqual(conditioned_comparison(0.,.5)['tv_upper'],0.)
        # The apparent disagreement is intentional: that API requires one common event.

    def test_conditioning_arithmetic_contains_exact_float_input_fractions(self):
        from fractions import Fraction
        tiny=np.nextafter(0.,1.)
        for p in [1.,.4,np.finfo(float).tiny,4*tiny]:
            for delta in [0.,p/3,np.nextafter(p,0.),p]:
                result=conditioned_comparison(delta,p)
                exact_success=max(Fraction(0),Fraction(p)-Fraction(delta))
                self.assertLessEqual(Fraction(result['transient_success_lower']),exact_success)
                if p>delta:
                    self.assertGreaterEqual(Fraction(result['tv_upper']),Fraction(delta)/Fraction(p))
        result=conditioned_comparison(tiny,1.)
        self.assertGreater(result['tv_upper'],0.)

    def test_nonfinite_derived_geometry_is_retained_as_failure(self):
        with np.errstate(over='ignore',invalid='ignore'):
            with self.assertRaises(ValueError):
                box_norm(np.array([1e200]),np.array([[1e200]]),np.ones(1))
            with self.assertRaises(ValueError):
                box_norm(np.array([1e200]),np.ones((1,1)),np.zeros(1))
            with self.assertRaises(ValueError):
                box_norm(np.zeros(1),np.array([[1e308]]),np.array([2.]))

    def test_invalid_boxes_and_nonpositive_gaussian_covariance_rejected(self):
        for radii in [np.array([-1.,1.]),np.array([1.]),np.array([np.nan,1.])]:
            with self.assertRaises(ValueError):box_norm(np.zeros(2),np.eye(2),radii)
        with self.assertRaises(ValueError):box_norm(np.zeros(3),np.eye(2),np.ones(2))
        with self.assertRaises(ValueError):
            box_gaussian_bounds(np.eye(2),-np.eye(2),np.zeros(2),np.eye(2),np.ones(2))


if __name__=='__main__':unittest.main()
