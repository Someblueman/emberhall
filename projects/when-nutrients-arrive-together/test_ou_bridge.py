import unittest
import numpy as np
from numpy.testing import assert_allclose
from ou_bridge import bridge


class BridgeChecks(unittest.TestCase):
    def test_stationary_joint_law_and_unchanged_endpoints(self):
        rng=np.random.default_rng(47)
        spacing=.25; variance=.005; a=np.exp(-spacing/2)
        left=rng.normal(size=(20000,30))*np.sqrt(variance)
        right=a*a*left+rng.normal(size=left.shape)*np.sqrt(variance*(1-a**4))
        base=np.r_[np.ones(24),np.full(6,3.)]
        endpoints=np.empty((40000,30))
        endpoints[::2]=left+base;endpoints[1::2]=right+base
        fine=bridge(endpoints,spacing,823)
        self.assertTrue(np.array_equal(fine[::2],endpoints))
        mid=fine[1::4]-base
        observed=np.cov(np.array([left.ravel(),mid.ravel(),right.ravel()]))
        expected=variance*np.array([[1,a,a*a],[a,1,a],[a*a,a,1]])
        assert_allclose(observed,expected,rtol=.01,atol=1e-5)


if __name__=='__main__':unittest.main()
