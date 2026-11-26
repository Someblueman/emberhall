import unittest
import numpy as np
from numpy.testing import assert_allclose
from amplitude_limit import exact_linear_response, nonlinear_response
from reference import community,rhs
from linear_reference import equilibrium,linear_system


class AmplitudeChecks(unittest.TestCase):
    def test_ramp_response_matches_independent_scalar_closed_form(self):
        spacing=.125
        forcing=(.2+.3*np.arange(65)*spacing)[:,None]
        result=exact_linear_response(np.array([[-.7]]),np.ones((1,1)),forcing,spacing)[:,0]
        times=np.arange(65)*spacing
        expected=.2*(1-np.exp(-.7*times))/.7 + .3*(times/.7-(1-np.exp(-.7*times))/.7**2)
        assert_allclose(result,expected,atol=2e-14)

    def test_jacobian_matches_numerical_derivative_of_original_nonlinear_rhs(self):
        uptake,gain,_=community(4)
        base=np.r_[np.ones(24),np.full(6,3.)]
        x,resources=equilibrium(uptake,gain,base)
        initial=np.r_[np.log(x),resources]
        j,b=linear_system(uptake,gain,x,resources)
        numeric=np.column_stack([(rhs(initial+v*1e-5,base,uptake,gain)-
                                  rhs(initial-v*1e-5,base,uptake,gain))/(2e-5)
                                 for v in np.eye(36)])
        assert_allclose(numeric,j,rtol=1e-8,atol=1e-8)
        supply=np.column_stack([(rhs(initial,base+v*1e-5,uptake,gain)-
                                 rhs(initial,base-v*1e-5,uptake,gain))/(2e-5)
                                for v in np.eye(30)])
        assert_allclose(supply,b,atol=1e-10)

    def test_nonlinear_zero_input_stays_at_same_equilibrium(self):
        uptake,gain,_=community(4)
        base=np.r_[np.ones(24),np.full(6,3.)]
        x,resources=equilibrium(uptake,gain,base)
        initial=np.r_[np.log(x),resources]
        response=nonlinear_response(uptake,gain,base,initial,np.zeros((65,30)),
                                   .0625,1.,np.arange(4.),.03125,1e-10)
        assert_allclose(response,0,atol=1e-11)
