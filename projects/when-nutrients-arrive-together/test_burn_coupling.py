import unittest
import numpy as np

from burn_coupling import coupled
from reference import community, simulate
from linear_reference import equilibrium


class CouplingTests(unittest.TestCase):
    def test_input_refinement_preserves_prefix_when_record_grows(self):
        from reference import ou
        from ou_bridge import bridge
        short = ou(80900, 2, 1/16)
        longer = ou(80900, 4, 1/16)
        np.testing.assert_array_equal(short, longer[:len(short)])
        fine = bridge(short, 1/16, 90900)
        longer_fine = bridge(longer, 1/16, 90900)
        np.testing.assert_array_equal(fine, longer_fine[:len(fine)])

    def test_separate_solve_and_initial_state_are_preserved(self):
        u, g, _ = community(4)
        base = np.r_[np.ones(24), np.full(6, 3.)]
        x, r = equilibrium(u, g, base)
        initial = np.array([np.r_[np.zeros(6), np.ones(30)], np.r_[np.log(x), r]])
        supply = np.repeat(base[None, :], 81, axis=0)
        states = coupled(u, g, supply, .25, 20, initial, .1, 1e-10)
        original, _ = simulate(u, g, supply, .25, 20, 0, .1, 1e-10)
        np.testing.assert_allclose(states[0], initial, atol=0, rtol=0)
        np.testing.assert_allclose(states[:, 0, :6], original, atol=2e-8, rtol=0)
        np.testing.assert_allclose(states[:, 1], np.repeat(initial[1][None, :], 20, axis=0), atol=1e-10, rtol=0)
        self.assertGreater(np.abs(states[0, 0]-states[0, 1]).max(), 1)

    def test_negative_supply_is_not_repaired(self):
        u, g, _ = community(4)
        supply = np.ones((5, 30)); supply[1, 0] = -1
        with self.assertRaisesRegex(ValueError, 'nonpositive'):
            coupled(u, g, supply, .25, 1, np.r_[np.zeros(6), np.ones(30)][None, :], .1, 1e-8)


if __name__ == '__main__':
    unittest.main()
