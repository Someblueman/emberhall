"""Independent vertex enumeration and certificate-corruption checks."""
from dataclasses import replace
from fractions import Fraction as F
from itertools import combinations
import unittest
from unittest.mock import patch

import blended_colour as bc
import display_colour as dc
import quantized_bounds as qb


def vertices(palette, lower, upper):
    """Enumerate active constraints; Gaussian elimination here is not the LP solver."""
    n = palette.size
    boundaries = [([F(int(i == j)) for i in range(n)], F(0)) for j in range(n)]
    for j in range(3):
        row = [c[j] for c in palette.colours]
        boundaries.extend(((row, lower[j]), (row, upper[j])))
    for active in combinations(boundaries, n - 1):
        matrix = [[F(1)] * n + [F(1)]] + [list(row) + [rhs] for row, rhs in active]
        for col in range(n):
            pivot = next((r for r in range(col, n) if matrix[r][col]), None)
            if pivot is None:
                break
            matrix[col], matrix[pivot] = matrix[pivot], matrix[col]
            divisor = matrix[col][col]
            matrix[col] = [v / divisor for v in matrix[col]]
            for r in range(n):
                if r != col:
                    factor = matrix[r][col]
                    matrix[r] = [a - factor*b for a, b in zip(matrix[r], matrix[col])]
        else:
            weights = tuple(row[-1] for row in matrix)
            if any(w < 0 for w in weights):
                continue
            rgb = tuple(sum(w*c[j] for w, c in zip(weights, palette.colours)) for j in range(3))
            if all(a <= x <= b for a, x, b in zip(lower, rgb, upper)):
                yield weights


class BoxTests(unittest.TestCase):
    def setUp(self):
        self.p = bc.builtin_palettes()['five_colour_tetra_3d']
        self.bw = bc.Palette('bw', ('B', 'W'), (F(0), F(1)), ((F(0),)*3, (F(1),)*3))

    def test_hand_checkable_gray_half_tie(self):
        cert = qb.solve_observation(self.bw, (128, 128, 128), (1,), 'linear8')
        self.assertEqual((cert.p_min, cert.p_max), (F(1, 2), F(257, 510)))
        self.assertEqual(cert.witness_min, (F(1, 2), F(1, 2)))
        self.assertEqual(cert.witness_max, (F(253, 510), F(257, 510)))
        self.assertEqual(dc.encode_channel(F(257, 510), 'linear8'), 129)
        # Upper bound is a supremum of the half-open byte bin, not attained there.

    def test_vertex_enumeration_agrees_for_3d_and_collinear_palettes(self):
        palettes = bc.builtin_palettes()
        for palette in palettes.values():
            weights = tuple(F(1, palette.size) for _ in range(palette.size))
            target = bc.blend_colour(palette, weights)
            for mode in dc.MODES:
                rgb = dc.encode_rgb(target, mode)
                lower, upper = dc.observation_box(rgb, mode)
                event = (palette.size - 1,)
                cert = qb.solve_box(palette, lower, upper, event)
                values = [p[-1] for p in vertices(palette, lower, upper)]
                self.assertTrue(values)
                self.assertEqual((cert.p_min, cert.p_max), (min(values), max(values)))

    def test_degenerate_point_box_recovers_existing_exact_bounds(self):
        for palette in bc.builtin_palettes().values():
            target = palette.colours[palette.size // 2]
            event = (palette.size - 1,)
            exact = bc.solve_event_bounds(palette, target, event)
            box = qb.solve_box(palette, target, target, event)
            self.assertEqual((box.p_min, box.p_max), (exact.p_min, exact.p_max))

    def test_boundary_events_and_infeasible_observation(self):
        self.assertEqual(qb.solve_observation(self.bw, (0, 0, 0), (1,)).p_min, 0)
        self.assertEqual(qb.solve_observation(self.bw, (255, 255, 255), (1,)).p_max, 1)
        for mode in dc.MODES:
            full = qb.solve_observation(self.bw, (128,)*3, (0, 1), mode)
            self.assertEqual((full.p_min, full.p_max), (1, 1))
            with self.assertRaises(bc.InfeasibleColourError):
                qb.solve_observation(self.bw, (255, 0, 0), (1,), mode)

    def test_corruption_rejection_without_using_solver(self):
        rgb, event = dc.encode_rgb(self.p.colours[2]), (3, 4)
        cert = qb.solve_observation(self.p, rgb, event)
        mutants = [replace(cert, p_max=cert.p_max - F(1, 1000)),
                   replace(cert, event_indices=(1,)),
                   replace(cert, witness_min=cert.witness_min[:-1]),
                   replace(cert, witness_max=tuple(F(0) for _ in cert.witness_max)),
                   replace(cert, dual_min=(F(0),)*7),
                   replace(cert, dual_max=(cert.dual_max[0] + 1, *cert.dual_max[1:])),
                   replace(cert, dual_min=(F(0), F(1), *cert.dual_min[2:])),
                   replace(cert, dual_max=cert.dual_max[:-1])]
        # Zero lower dual is valid for this case, so corrupt it by claiming a negative intercept.
        mutants[4] = replace(cert, dual_min=(-F(1), *cert.dual_min[1:]))
        with patch.object(bc, '_simplex_minimize', side_effect=AssertionError('Verifier called solver')):
            qb.verify_observation(self.p, rgb, event, qb.certificate_from_dict(cert.to_dict()))
            for mutant in mutants:
                with self.assertRaises(ValueError):
                    qb.verify_observation(self.p, rgb, event, mutant)
            with self.assertRaises(ValueError):
                qb.verify_observation(self.p, (0, 0, 0), event, cert)
            with self.assertRaises(ValueError):
                qb.verify_observation(self.p, rgb, event, cert, 'linear8')

    def test_invalid_boxes_and_events(self):
        for lower, upper in (((F(0),)*2, (F(1),)*3), ((F(1),)*3, (F(0),)*3)):
            with self.assertRaises(ValueError):
                qb.solve_box(self.p, lower, upper, (1,))
        for event in ((), (-1,), (5,), (True,), (1.5,)):
            with self.assertRaises(ValueError):
                qb.solve_observation(self.p, (128,)*3, event)


if __name__ == '__main__':
    unittest.main()
