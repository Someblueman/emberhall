"""Local linear transfer check for the explicitly chosen pilot equilibrium."""
import json
from pathlib import Path

import numpy as np
from scipy.integrate import quad_vec
from scipy.linalg import solve_continuous_lyapunov
from scipy.optimize import root

from reference import community


def equilibrium(uptake, gain, base):
    def resource(z):
        return base / (.5 + uptake.T @ np.exp(z))
    solution = root(lambda z: gain @ resource(z) - .3, np.full(6, 2.5), tol=1e-11)
    if not solution.success or np.max(np.abs(solution.fun)) > 1e-10:
        raise ValueError('no positive equilibrium certified')
    return np.exp(solution.x), resource(solution.x)


def linear_system(uptake, gain, x, resources):
    # Coordinates: (delta log x, delta R, Q). B injects Q into delta R.
    j = np.block([[np.zeros((6, 6)), gain],
                  [-resources[:, None] * uptake.T * x[None, :],
                   -np.diag(.5 + uptake.T @ x)]])
    b = np.vstack((np.zeros((6, 30)), np.eye(30)))
    return j, b


def stationary(j, b, amplitude=.1, omega=1):
    dimension, inputs = b.shape
    matrix = np.block([[j, b], [np.zeros((inputs, dimension)), -omega * np.eye(inputs)]])
    diffusion = np.zeros_like(matrix)
    diffusion[dimension:, dimension:] = amplitude**2 * omega * np.eye(inputs)
    if np.max(np.linalg.eigvals(matrix).real) >= 0:
        raise ValueError('linearization is not asymptotically stable')
    covariance = solve_continuous_lyapunov(matrix, -diffusion)
    residual = np.max(np.abs(matrix @ covariance + covariance @ matrix.T + diffusion))
    return covariance[:6, :6], float(residual)


def spectrum(angular_frequency, j, b, amplitude=.1, omega=1):
    # Two-sided angular spectrum; covariance is integral S(w) dw/(2*pi).
    response = np.linalg.solve(1j * angular_frequency * np.eye(len(j)) - j, b)[:6]
    return response @ response.conj().T * amplitude**2 * omega / (omega**2 + angular_frequency**2)


def verify(seed):
    uptake, gain, _ = community(seed)
    base = np.r_[np.ones(24), np.full(6, 3)]
    x, resources = equilibrium(uptake, gain, base)
    j, b = linear_system(uptake, gain, x, resources)
    covariance, residual = stationary(j, b)
    integrated, error = quad_vec(lambda w: spectrum(w, j, b).real / np.pi,
                                  0, np.inf, epsabs=1e-10, epsrel=1e-7)
    relative = np.linalg.norm(integrated - covariance) / np.linalg.norm(covariance)
    return dict(seed=seed, equilibrium_residual=float(np.max(np.abs(gain @ resources - .3))),
                lyapunov_residual=residual, frequency_integral_relative_error=float(relative),
                quadrature_error_bound=float(error),
                slowest_decay=float(-np.max(np.linalg.eigvals(j).real)),
                log_variances=np.diag(covariance).tolist())


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('/tmp/nutrient-reference/linear.json'))
    args = parser.parse_args()
    result = [verify(seed) for seed in range(4)]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print('linear covariance/transfer checks:', max(r['frequency_integral_relative_error'] for r in result))
