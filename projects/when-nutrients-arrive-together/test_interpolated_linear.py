import unittest
import numpy as np
from numpy.testing import assert_allclose
from interpolated_linear import interpolated_system,predictions
from linear_calibration import setup
from linear_welch import predictions as accepted_prediction


class InterpolatedInputChecks(unittest.TestCase):
    def test_scalar_stationary_covariance_matches_closed_recurrence(self):
        a=.7;rate=1.3;h=.25;v=.005
        transition,covariance,residual=interpolated_system(np.array([[-a]]),np.ones((1,1)),h,rate,v)
        p=np.exp(-a*h);r=np.exp(-rate*h)
        u=1/a-(1-p)/(a*a*h)
        l=(1-p)/a-u
        cross=v*(l*r+u)/(1-p*r)
        coefficient=l+u*r
        variance=(coefficient**2*v+u*u*v*(1-r*r)+2*p*coefficient*cross)/(1-p*p)
        assert_allclose(covariance,[[variance,cross],[cross,v]],atol=1e-15)
        self.assertLess(residual,1e-13)

    def test_scalar_covariance_approaches_continuous_ou_at_second_order(self):
        a=.7;rate=1.3;v=.005
        exact=np.array([[v/(a*(a+rate)),v/(a+rate)],[v/(a+rate),v]])
        errors=[]
        for h in (.25,.125,.0625):
            _,p,_=interpolated_system(np.array([[-a]]),np.ones((1,1)),h,rate,v)
            errors.append(np.linalg.norm(p-exact))
        assert_allclose(np.array(errors[:-1])/errors[1:],4,rtol=.02)

    def test_continuous_limit_scoring_matches_accepted_welch_reference(self):
        f,p,gain,labels=setup(4)
        scores,values=predictions(f,p,gain,labels)
        accepted=accepted_prediction(4)
        for metric in scores:
            assert_allclose(values[metric],accepted['pair_measures'][metric],rtol=1e-12,atol=1e-14)
            for target,value in scores[metric].items():
                assert_allclose(value,accepted['scores'][metric][target],atol=1e-14)
