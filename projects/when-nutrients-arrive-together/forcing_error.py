"""Exact mean-square error of linear interpolation of a stationary OU path.

This quantifies unresolved input, not a bound on nonlinear score error.
"""
import json
import numpy as np
from scipy.integrate import quad


def relative_error(theta, scaled_mesh):
    """Var[Q(theta*h) - ((1-theta)Q(0)+theta Q(h))]/Var[Q]."""
    if not 0 <= theta <= 1 or scaled_mesh <= 0:
        raise ValueError('theta in [0,1] and positive omega*h required')
    # Constant terms cancel; expm1 is stable for fine meshes.
    return float(2*theta*(1-theta)*np.expm1(-scaled_mesh)
                 -2*(1-theta)*np.expm1(-scaled_mesh*theta)
                 -2*theta*np.expm1(-scaled_mesh*(1-theta)))


def interpolation_error(mesh, amplitude=.1, omega=1):
    if mesh <= 0 or amplitude <= 0 or omega <= 0:
        raise ValueError('positive parameters required')
    variance = amplitude**2/2
    average, quadrature = quad(lambda theta: relative_error(theta, omega*mesh), 0, 1,
                               epsabs=1e-13, epsrel=1e-11)
    return dict(mesh=mesh, stationary_variance=variance,
                mean_square_input_error=variance*average,
                rms_input_error=float(np.sqrt(variance*average)),
                relative_rms_input_error=float(np.sqrt(average)),
                quadrature_error=variance*quadrature)


if __name__ == '__main__':
    print(json.dumps([interpolation_error(h) for h in (.25, .125, .0625, .03125)], indent=2))
