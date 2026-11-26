import unittest
import numpy as np
from numpy.testing import assert_allclose
from linear_calibration import covariance_factor,stationary_sample,setup


class ExactSampleChecks(unittest.TestCase):
    def test_covariance_factor_refuses_material_indefiniteness(self):
        with self.assertRaisesRegex(ValueError,'indefinite'):
            covariance_factor(np.diag([1,-.001]))
        factor,minimum=covariance_factor(np.diag([1,-1e-14]))
        self.assertLess(minimum,0)
        assert_allclose(factor@factor.T,np.diag([1,0]),atol=1e-15)

    def test_stationary_covariance_and_lag_in_independent_two_state_control(self):
        transition=np.array([[.8,.1],[0,.6]])
        p=np.array([[1,.3],[.3,2]])
        x,diagnostics=stationary_sample(transition,p,881,100000)
        assert_allclose(np.cov(x.T,bias=True),p,atol=.035)
        assert_allclose(x[1:].T@x[:-1]/(len(x)-1),transition@p,atol=.035)
        self.assertLess(diagnostics['transition_covariance_residual'],1e-12)

    def test_model_transition_preserves_continuous_stationary_covariance(self):
        transition,p,_,_=setup(4)
        _,diagnostics=stationary_sample(transition,p,888,32)
        self.assertLess(diagnostics['transition_covariance_residual'],1e-13)
