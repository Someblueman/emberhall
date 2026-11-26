import unittest

import numpy as np
from numpy.testing import assert_allclose

from reference import auc, community, measures, ou, rhs, simulate


class ReferenceChecks(unittest.TestCase):
    def test_uncoupled_resource_has_exact_solution(self):
        uptake = np.zeros((6, 30))
        supply = np.ones((41, 30))
        # Resource-only subsystem: R(t)=2-exp(-t/2). Consumer log x=-.3t.
        # A resource-dependent log derivative makes resource error observable.
        gain = np.full((6, 30), .01)
        log_x, _ = simulate(uptake, gain, supply, .25, 10, 0, .125, 1e-9)
        times = np.arange(10)
        expected = .3 * times - .6 * (1 - np.exp(-times / 2))
        assert_allclose(log_x, np.repeat(expected[:, None], 6, axis=1), atol=1e-8)

    def test_equilibrium_and_mass_balance(self):
        uptake = np.eye(6)
        gain = uptake.copy()
        state = np.r_[np.zeros(6), np.full(6, .3)]
        assert_allclose(rhs(state, np.full(6, .45), uptake, gain), 0, atol=1e-15)

    def test_ou_stationary_law_and_independence(self):
        samples = ou(320, 10000, spacing=.25) - np.r_[np.ones(24), np.full(6, 3)]
        assert_allclose(samples.var(0), .005, rtol=.12)
        correlation = np.corrcoef(samples.T)
        self.assertLess(np.max(np.abs(correlation - np.eye(30))), .08)
        lag = np.mean(samples[:-1] * samples[1:], axis=0) / samples.var(0)
        assert_allclose(lag, np.exp(-.25), atol=.035)

    def test_ties_and_inverted_classifier(self):
        truth = [True, False, True, False]
        self.assertEqual(auc(truth, [1, 1, 1, 1]), .5)
        self.assertEqual(auc(truth, [1, 0, 1, 0]), 1)
        self.assertEqual(auc(truth, [0, 1, 0, 1]), 0)

    def test_spectral_negative_control(self):
        rng = np.random.default_rng(221)
        x = rng.normal(size=(8192, 6))
        x[:, 1] = np.roll(x[:, 0], 3)
        values = measures(x, 60)
        # Delayed pair (0,1) has near-unit coherence, independent pairs do not.
        self.assertGreater(values['coherence'][0], .4)
        self.assertLess(np.max(values['coherence'][1:5]), .03)
        self.assertLess(abs(values['correlation'][0]), .04)
        for transformed in (x * np.arange(1, 7), x + np.arange(6)):
            for name, scores in measures(transformed, 60).items():
                assert_allclose(scores, values[name], atol=1e-12)

    def test_private_resources_are_private(self):
        uptake, gain, _ = community(0)
        assert_allclose(uptake[:, 24:], .1 * np.eye(6))
        self.assertTrue(np.all(gain >= 0))


class LinearChecks(unittest.TestCase):
    def test_jacobian_against_original_nonlinear_equations(self):
        from linear_reference import equilibrium, linear_system
        uptake, gain, _ = community(0)
        base = np.r_[np.ones(24), np.full(6, 3)]
        x, resources = equilibrium(uptake, gain, base)
        state = np.r_[np.log(x), resources]
        jacobian, _ = linear_system(uptake, gain, x, resources)
        numeric = np.column_stack([
            (rhs(state + np.eye(36)[i] * 1e-5, base, uptake, gain)
             - rhs(state - np.eye(36)[i] * 1e-5, base, uptake, gain)) / 2e-5
            for i in range(36)])
        assert_allclose(jacobian, numeric, atol=2e-9)

    def test_covariance_from_two_independent_calculations(self):
        from linear_reference import verify
        result = verify(0)
        self.assertLess(result['frequency_integral_relative_error'], 1e-6)
        self.assertLess(result['lyapunov_residual'], 1e-10)
        self.assertTrue(np.all(np.array(result['log_variances']) > 0))


class ClusteringChecks(unittest.TestCase):
    def test_connection_thresholds_against_independent_component_search(self):
        from reference import PAIRS, single_linkage_scores
        rng = np.random.default_rng(48)
        # Negative values and ties must work, including isolated vertices.
        weights = rng.integers(-3, 4, 15)
        closed = single_linkage_scores(weights)
        edges = list(zip(*PAIRS))
        for threshold in range(-4, 5):
            adjacency = [set() for _ in range(6)]
            for (i, j), weight in zip(edges, weights):
                if weight >= threshold:
                    adjacency[i].add(j); adjacency[j].add(i)
            connected = []
            for source, target in edges:
                seen, todo = {source}, [source]
                while todo:
                    for neighbor in adjacency[todo.pop()] - seen:
                        seen.add(neighbor); todo.append(neighbor)
                connected.append(target in seen)
            np.testing.assert_array_equal(closed >= threshold, connected)



if __name__ == '__main__':
    unittest.main()
