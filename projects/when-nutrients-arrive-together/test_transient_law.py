import unittest

import numpy as np
from numpy.testing import assert_allclose
from scipy.special import ndtr
from scipy.integrate import quad
from scipy.stats import norm

from transient_law import gaussian_bounds, _log_gap, _affinity_gap


class TransientLawChecks(unittest.TestCase):
    def test_equal_covariance_dominates_exact_shift_distance(self):
        for shift in [0,1e-12,1e-5,.1,1,5,20]:
            result=gaussian_bounds(np.eye(2),np.array([shift,0.]),np.zeros((2,2)))
            exact=2*ndtr(shift/2)-1
            self.assertGreaterEqual(result['tv_upper']+1e-15,exact)
            assert_allclose(result['kl'],shift**2/2,rtol=1e-14,atol=0)
            assert_allclose(result['negative_log_affinity'],shift**2/8,rtol=1e-14,atol=0)

    def test_scalar_covariance_distance_and_affinity_by_integration(self):
        for variance in [.04,.3,.9,1.1,2.,25.]:
            for mean in [0.,.7]:
                result=gaussian_bounds(np.ones((1,1)),np.array([mean]),np.array([[variance-1]]))
                p=lambda x:norm.pdf(x)
                q=lambda x:norm.pdf(x,loc=mean,scale=np.sqrt(variance))
                tv=quad(lambda x:abs(p(x)-q(x))/2,-np.inf,np.inf,epsabs=1e-10)[0]
                affinity=quad(lambda x:np.sqrt(p(x)*q(x)),-np.inf,np.inf,epsabs=1e-10)[0]
                self.assertGreaterEqual(result['tv_upper']+2e-9,tv)
                assert_allclose(np.exp(-result['negative_log_affinity']),affinity,rtol=1e-9)
                assert_allclose(result['kl'],.5*(variance-1-np.log(variance)+mean**2),rtol=1e-12)

    def test_general_covariance_kl_and_affine_invariance(self):
        p=np.array([[2.,.4],[.4,1.]])
        q=np.array([[.7,-.1],[-.1,1.3]])
        mean=np.array([.8,-.2])
        result=gaussian_bounds(p,mean,q-p)
        exact=.5*(np.trace(np.linalg.solve(p,q))-2+np.linalg.slogdet(p)[1]
                   -np.linalg.slogdet(q)[1]+mean@np.linalg.solve(p,mean))
        assert_allclose(result['kl'],exact,rtol=1e-13)
        a=np.array([[1.,3.],[-.2,.7]])
        transformed=gaussian_bounds(a@p@a.T,a@mean,a@(q-p)@a.T)
        for key in ['tv_upper','kl','negative_log_affinity']:
            assert_allclose(result[key],transformed[key],rtol=1e-12)

    def test_near_stationary_differences_do_not_cancel(self):
        for exponent in [5,10,20,50,100]:
            delta=10.**(-exponent)
            result=gaussian_bounds(np.eye(2),np.zeros(2),np.diag([delta,-delta]))
            assert_allclose(result['kl']/delta**2,.5,rtol=1e-8)
            assert_allclose(result['negative_log_affinity']/delta**2,.125,rtol=1e-8)
            self.assertGreater(result['tv_upper'],0)
        assert_allclose(_log_gap(np.array([.009,-.009])),
                        np.array([.009,-.009])-np.log1p([.009,-.009]),rtol=1e-12)
        self.assertTrue(np.all(_affinity_gap(np.array([.009,-.009]))>0))

    def test_degenerate_and_invalid_covariances_rejected(self):
        for delta in [-1.,-1.01]:
            with self.assertRaises(ValueError):
                gaussian_bounds(np.eye(1),np.zeros(1),np.array([[delta]]))
        with self.assertRaises(np.linalg.LinAlgError):
            gaussian_bounds(np.zeros((1,1)),np.zeros(1),np.eye(1))
        with self.assertRaises(ValueError):
            gaussian_bounds(np.eye(2),np.zeros(3),np.eye(2))

    def test_whole_record_data_processing_on_exact_scalar_example(self):
        # For a scalar AR process with equal starting variances, the future
        # record contains its start. Its Gaussian KL equals starting KL.
        f=.7;n=9;shift=.4
        covariance=np.array([[f**abs(t-u) for u in range(n)] for t in range(n)])
        mean=shift*f**np.arange(n)
        record=gaussian_bounds(covariance,mean,np.zeros((n,n)))
        start=gaussian_bounds(np.eye(1),np.array([shift]),np.zeros((1,1)))
        assert_allclose(record['kl'],start['kl'],rtol=1e-13)
        # A later observation alone loses information, as the kernel predicts.
        later=gaussian_bounds(np.eye(1),np.array([shift*f**(n-1)]),np.zeros((1,1)))
        self.assertLess(later['tv_upper'],start['tv_upper'])


if __name__=='__main__':unittest.main()
