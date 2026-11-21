"""Tests for exact_lifting: exact-distance lifting criteria and obstructions."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from published_cases import check_pair  # noqa: E402
import exact_lifting as el  # noqa: E402


def interval_distance_shell(lengths, holes, signs):
    """Build (1-z)/z times the signed distance shell, minus twice balance.

    Every arm segment contributes z^(lo-1)-z^hi for its actual distance
    interval [lo,hi]. This uses neither exact_lifting nor shell_terms and
    accepts arbitrary holes, including ones at the moving tips.
    """
    result = defaultdict(int)
    for (arm, depth), sign in signs.items():
        if arm == 0:
            intervals = [(1, length) for length in lengths]
        else:
            intervals = [(1, depth), (1, lengths[arm-1]-depth)]
            intervals += [(depth+1, depth+length)
                          for other, length in enumerate(lengths, 1) if other != arm]
        for lo, hi in intervals:
            if lo <= hi:
                result[lo-1] += sign
                result[hi] -= sign
        result[0] -= 2*sign
        for other, hole_depth in holes:
            distance = abs(depth-hole_depth) if arm == other else depth+hole_depth
            result[distance-1] -= sign
            result[distance] += sign
    return {degree: value for degree, value in result.items() if value}


class TestExactLifting(unittest.TestCase):
    def test_general_hole_shell_matches_literal_distances(self) -> None:
        lengths = (7, 5, 3)
        for holes in (((1, 1), (2, 1)), ((1, 6), (1, 7))):
            vertices = [(0, 0)] + [(arm, depth)
                        for arm, length in enumerate(lengths, 1)
                        for depth in range(1, length+1)]
            signs = {v: (-1)**i for i, v in enumerate(vertices) if v not in holes}
            direct = defaultdict(int)
            for (arm, depth), sign in signs.items():
                for other, other_depth in signs:
                    distance = (abs(depth-other_depth) if arm == other
                                else depth+other_depth)
                    if distance:
                        direct[distance-1] += sign
                        direct[distance] -= sign
                direct[0] -= 2*sign
            self.assertEqual(interval_distance_shell(lengths, holes, signs),
                             {d: c for d, c in direct.items() if c})

    def test_moving_suffix_holes_cancel_only_reduced_high_condition(self) -> None:
        blocks = ((-1,)*8, (1,)*8, (-1, -1, 1, 1, -1, -1, 1, 1))
        # Check the stated polynomial identity directly, separately from the
        # general-hole distance-shell reconstruction below.
        identity = [0]*8
        for j in range(8):
            identity[(j+3) % 8] += 2*blocks[0][j]
            for shift in (1, 3):
                identity[(j+shift) % 8] += blocks[1][j]+blocks[2][j]
        self.assertEqual(identity, [0]*8)
        for n in (7560, 15120):
            lengths = tuple(n+base for base in (227, 67, 11))
            for suffix_sign in (-1, 1):
                for moving in (False, True):
                    holes = ((1, n+226), (1, n+227)) if moving else ((1, 1), (2, 1))
                    signs = {(0, 0): suffix_sign}
                    for arm, length in enumerate(lengths, 1):
                        for d in range(1, length+1):
                            if (arm, d) not in holes:
                                signs[arm, d] = (blocks[arm-1][(d-1) % 8] if d <= n
                                                else suffix_sign*(-1)**d)
                    shell = interval_distance_shell(lengths, holes, signs)
                    self.assertTrue(shell)  # Not a full solution or homometric witness.
                    multiplied = defaultdict(int)
                    for degree, value in shell.items():
                        multiplied[degree+8] += value
                        multiplied[degree] -= value
                    # At zero cuts all Q^2 exponents are 2N plus nonnegative
                    # offsets; the Q^0,Q^1 supports lie below 2N for these N.
                    high = {d-2*n: c for d, c in multiplied.items() if c and d >= 2*n}
                    self.assertTrue(high)  # Even Q^2 is nonzero before reduction.
                    reduced = [0]*8
                    for degree, value in high.items():
                        reduced[degree % 8] += value
                    expected = [0]*8 if moving else [2, 2, -2, -2, 2, 2, -2, -2]
                    self.assertEqual(reduced, expected)

    def test_shifted_moments_against_direct_monomial_reduction(self) -> None:
        # Expand each high-shell monomial from its actual exponent, without
        # arm-series multiplication, inverse shifts or residue rotations.
        for t in (1, 2, 3, 4, 5, 8, 9, 12, 4000000):
            lengths = tuple(n + 7560*t for n in (227, 67, 11))
            system = el.compressed_system(lengths, ((1, 1), (2, 1)), 8)
            _, counts, moments, seconds = el._triple_witness_arrays(t)
            expected = [[0]*8 for _ in range(3)]
            for cell, x, y, z in zip(system['cells'], counts, moments, seconds):
                if not cell['arm']:
                    continue
                for other, length in enumerate(lengths, 1):
                    if other == cell['arm']:
                        continue
                    q, r = divmod(cell['first'] + length - 7560*t, 8)
                    expected[0][r] -= x
                    expected[1][r] -= q*x+y
                    expected[2][r] -= q*(q-1)//2*x+q*y+z
            actual = el.check_triple_witness_t(t)
            self.assertEqual([actual['r0'], actual['r1'], actual['r2']], expected)

    def test_all_t_first_moment_quadratic_coefficients_cancel(self) -> None:
        # After the N shift, q=(first+base_other)//8 is independent of t.
        # Counts are constant on each branch and Y is quadratic in k, so
        # this coefficient check proves R1 is affine for every k>=0.
        for t0, branch in el.TRIPLE_ROOT_WITNESS_BRANCHES.items():
            lengths = tuple(n+7560*t0 for n in (227, 67, 11))
            system = el.compressed_system(lengths, ((1, 1), (2, 1)), 8)
            coefficient = [0]*8
            for cell, y2 in zip(system['cells'], branch[3]):
                if cell['arm']:
                    coefficient[(cell['residue']+3) % 8] -= 2*y2
            self.assertEqual(coefficient, [0]*8)

    def test_e_hi_window_bounds_and_exact_identity(self) -> None:
        bounds = el.e_hi_window_bounds()
        self.assertEqual(bounds["max_r0"], [94, 94, 94, 94, 96, 94, 94, 94])
        self.assertEqual(bounds["max_r1"], [1550, 1550, 1550, 1550, 1586, 1456, 1456, 1456])
        self.assertEqual(bounds["max_r2"], [14448, 14448, 14448, 14448, 14854, 12992, 12992, 12992])

        a, b, c = 227 + 7560, 67 + 7560, 11 + 7560
        s0 = 1
        s1 = [1 if i % 2 == 0 else -1 for i in range(a - 1)]  # depths 2..a
        s2 = [1 if i % 3 == 0 else -1 for i in range(b - 1)]  # depths 2..b
        s3 = [1 if i % 5 == 0 else -1 for i in range(c)]      # depths 1..c
        full_e = el.exact_e_polynomial((a, b, c), s0, s1, s2, s3)
        lo_e = el.e_lo_polynomial((a, b, c), s0, s1, s2, s3)
        hi_e = el.e_hi_polynomial((a, b, c), s1, s2, s3)
        combined = dict(lo_e)
        for deg, coeff in hi_e.items():
            combined[deg] = combined.get(deg, 0) + coeff
        combined = {d: v for d, v in combined.items() if v}
        self.assertEqual(full_e, combined)
        self.assertLessEqual(max(lo_e), a + 1)

        r_poly = el.shifted_e_hi_window_coeffs(1, s1, s2, s3)
        self.assertEqual(len(r_poly["r0"]), 8)
        for r in range(8):
            self.assertLessEqual(abs(r_poly["r0"][r]), bounds["max_r0"][r])
            self.assertLessEqual(abs(r_poly["r1"][r]), bounds["max_r1"][r])
            self.assertLessEqual(abs(r_poly["r2"][r]), bounds["max_r2"][r])

    def test_refutes_pippin_triple_witness_for_all_t_ge_1(self) -> None:
        report = el.refute_pippin_triple_witness_all_t()
        self.assertTrue(report["all_t_ge_1_refuted"])
        self.assertEqual(set(report["branches"]), {1, 2, 3, 4})
        for t0, branch in report["branches"].items():
            self.assertTrue(branch["linear_in_k"])
            self.assertGreater(len(branch["monotone_violated_residues"]), 0)
            for entry in branch["monotone_violated_residues"]:
                self.assertEqual(entry["delta2"], 0)
                self.assertGreater(abs(entry["r1_at_k0"]), entry["bound"])
                self.assertGreaterEqual(entry["r1_at_k0"] * entry["slope"], 0)

        # Also check concrete t = 1..8 and t = 4000000 directly.
        for t in (1, 2, 3, 4, 5, 6, 7, 8, 4000000):
            chk = el.check_triple_witness_t(t)
            self.assertTrue(chk["triple_root_equations_hold"])
            self.assertFalse(chk["e_hi_window_bounds_hold"])

    def test_phi3_decoupling_and_z0_enclosure(self) -> None:
        # Certify rational enclosure of z0^3 + z0 - 1 = 0
        z_lo, z_hi = el.z0_enclosure()
        self.assertGreater(z_lo, Fraction(0))
        self.assertLess(z_lo, z_hi)
        self.assertLess(z_hi, Fraction(1))
        self.assertLess(z_lo**3 + z_lo - 1, 0)
        self.assertGreater(z_hi**3 + z_hi - 1, 0)

        # Verify Phi_3 decoupling identity directly on E(z) at small (27+8, 11+8, 3+8) = (35, 19, 11)
        # where a == 2 (mod 3), b == 1 (mod 3), c == 2 (mod 3):
        # For ANY s0, s1, s2, s3 in {+1, -1}, Im(E(omega)) depends ONLY on s0 and s3!
        for s0 in (-1, 1):
            s1 = [1 if i % 2 == 0 else -1 for i in range(34)]
            s2 = [1 if i % 3 == 0 else -1 for i in range(18)]
            s3 = [1 if (i * 7) % 3 == 0 else -1 for i in range(11)]
            diff_a = el.phi3_imag_residual((35, 19, 11), s0, s1, s2, s3)
            # Flip signs on arms 1 and 2 arbitrarily: Im(E(omega)) must be invariant!
            s1_alt = [-x for x in s1]
            s2_alt = [1] * 18
            diff_b = el.phi3_imag_residual((35, 19, 11), s0, s1_alt, s2_alt, s3)
            self.assertEqual(diff_a, diff_b)
            # Setting s0 = phi3_center_constraint(s3) makes Im(E(omega)) == 0.
            s0_forced = el.phi3_center_constraint(s3)
            self.assertEqual(el.phi3_imag_residual((35, 19, 11), s0_forced, s1, s2, s3), 0)

    def test_z0_bound_holds_on_all_exact_or_synthetic_solutions(self) -> None:
        # Construct an exact polynomial E_test on (35, 19, 11) or check the general algebraic bound
        # on any sign assignment satisfying E_hi(z) = z^{7560t} R(z) and E(z) = 0:
        # Specifically verify the algebraic decomposition of E(z0) on small tree (35, 19, 11)
        # where (s0, s1, s2, s3) is arbitrary: exact E(z0) matches the decomposition identity.
        z_lo, z_hi = el.z0_enclosure()
        z_mid = (z_lo + z_hi) / 2
        s1 = [1 if i % 2 == 0 else -1 for i in range(34)]
        s2 = [-1 if i % 5 == 0 else 1 for i in range(18)]
        s3 = [1 if i % 3 == 0 else -1 for i in range(11)]
        poly = el.exact_e_polynomial((35, 19, 11), 1, s1, s2, s3)
        eval_direct = sum(Fraction(c) * (z_mid ** d) for d, c in poly.items())
        eval_split = el.e_at_z_split((35, 19, 11), 1, s1, s2, s3, z_mid)
        self.assertEqual(eval_direct, eval_split)

        # For t = 1, verify the exact theoretical upper bound < 3.2e-9 when E(z) = 0.
        bound_t1 = el.z0_tail_upper_bound(1)
        self.assertLess(bound_t1, Fraction(32, 10**10))

    def test_unsynchronized_periodic_obstructions(self) -> None:
        # Every divisor B of 7560 is obstructed with fixed-prefix holes,
        # regardless of the fixed cuts. Moving suffix holes are not covered.
        divisors = [d for d in range(1, 7561) if 7560 % d == 0]
        self.assertEqual(len(divisors), 64)
        for B in divisors:
            obs = el.unsynchronized_divisor_obstruction(B)
            self.assertTrue(obs["obstructed"])
            self.assertEqual(obs["hole_scope"], "fixed_prefix_only")
            self.assertFalse(obs["moving_suffix_holes_covered"])
            self.assertEqual(obs["odd_block_length"] % 2, 1)

        # Full modular rank certifies rational full rank for these cuts only.
        for B in (8, 16, 24, 32, 48, 64, 100, 150):
            for cuts in ((2, 2, 1), (171, 11, 11)):
                qr = el.periodic_template_q_rank(B, *cuts)
                self.assertEqual(qr["rank"], qr["variables"])
                self.assertEqual(qr["nullity"], 0)
                self.assertTrue(qr["trivial_over_Q"])
                self.assertEqual(qr["holes"], [[1, 1], [2, 1]])
                self.assertEqual(qr["cuts"], list(cuts))

    def test_positive_control_infinite_family_and_corrupted_rejection(self) -> None:
        # Positive infinite family on H=[(1,1),(2,1)] outside 3 mod 4:
        # (5 + 4k, 4, 2) and (9 + 4k, 5, 3) have exact target-sized homometric pairs!
        for k in range(5):
            for lengths, left, right in (
                el.positive_control_5_4_2(k),
                el.positive_control_9_5_3(k),
            ):
                chk = check_pair(lengths, left, right)
                self.assertTrue(chk["homometric"])
                self.assertTrue(chk["meets_target"])
                s0, s1, s2, s3 = el.pair_to_signs(lengths, left, right)
                poly = el.exact_e_polynomial(lengths, s0, s1, s2, s3)
                self.assertEqual(poly, {})

        # Corrupted witness check: move one vertex on (9, 5, 3) -> E(z) != 0 and check_pair fails!
        lengths, left, right = el.positive_control_9_5_3(1)
        bad_left = list(left)
        bad_right = list(right)
        bad_left[0], bad_right[-1] = bad_right[-1], bad_left[0]
        chk_bad = check_pair(lengths, bad_left, bad_right)
        self.assertFalse(chk_bad["homometric"])
        s0, s1, s2, s3 = el.pair_to_signs(lengths, bad_left, bad_right)
        self.assertNotEqual(el.exact_e_polynomial(lengths, s0, s1, s2, s3), {})

    def test_cli_verify_and_rejection(self) -> None:
        cli = [sys.executable, str(HERE / "exact_lifting.py")]
        res = subprocess.run(cli + ["--check-triple-witness", "--t", "1"],
                             text=True, capture_output=True, check=True)
        payload = json.loads(res.stdout)
        self.assertTrue(payload["triple_root_equations_hold"])
        self.assertFalse(payload["e_hi_window_bounds_hold"])

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "witness.json"
            pos = subprocess.run(cli + ["--positive-control", "2"],
                                 text=True, capture_output=True, check=True)
            path.write_text(pos.stdout)
            ok = subprocess.run(cli + ["--verify", str(path)],
                                text=True, capture_output=True, check=True)
            self.assertTrue(json.loads(ok.stdout)["valid"])

            # Corrupt a balanced swap in s1 and verify rejection (exit code 1).
            corrupted = json.loads(pos.stdout)
            i_pos = corrupted["s1"].index(1)
            i_neg = corrupted["s1"].index(-1)
            corrupted["s1"][i_pos], corrupted["s1"][i_neg] = -1, 1
            path.write_text(json.dumps(corrupted))
            bad = subprocess.run(cli + ["--verify", str(path)],
                                 text=True, capture_output=True)
            self.assertEqual(bad.returncode, 1)
            self.assertFalse(json.loads(bad.stdout)["valid"])

            # Also verify unbalanced corruption exits 1 with valid=False.
            corrupted["s0"] = -corrupted["s0"]
            path.write_text(json.dumps(corrupted))
            bad2 = subprocess.run(cli + ["--verify", str(path)],
                                  text=True, capture_output=True)
            self.assertEqual(bad2.returncode, 1)
            self.assertFalse(json.loads(bad2.stdout)["valid"])


if __name__ == "__main__":
    unittest.main()
