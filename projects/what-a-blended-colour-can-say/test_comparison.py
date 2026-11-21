"""Tests for the frozen M3 held-out comparison pack, certificates, views, and scorer."""

from copy import deepcopy
from fractions import Fraction as F
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

PROJECT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

import blended_colour as bc
import comparison as cmp_mod
import display_colour as dc
import quantized_bounds as qb
import render_legend as rl
from verify_atlas import verify_atlas


class ComparisonPackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.palettes = cmp_mod.heldout_palettes()
        cls.specs = cmp_mod.heldout_specs()
        cls.comp_dir = PROJECT_DIR / "comparison"

    def test_heldout_cases_are_absent_from_existing_tests_and_witnesses(self) -> None:
        existing_palettes = set(bc.builtin_palettes().keys()) | {"survey-risk", "binary", "bw"}
        for name in self.palettes:
            self.assertNotIn(name, existing_palettes)

        existing_signatures = set()
        for case in rl.default_cases():
            existing_signatures.add((case.palette, case.weights, case.event_indices))
        for item in bc.showcase_witnesses():
            existing_signatures.add(
                (item["palette"], tuple(map(F, item["weights"])), tuple(item["event_indices"]))
            )
        # Exclude example_import and test_quantized_bounds cases as well.
        existing_signatures.add(
            ("survey-risk", (F(1, 4), F(0), F(1, 4), F(1, 2), F(0)), (3, 4))
        )

        self.assertEqual(len(self.specs), 10)
        set_a = [s for s in self.specs if s.set_name == "A"]
        set_b = [s for s in self.specs if s.set_name == "B"]
        self.assertEqual(len(set_a), 5)
        self.assertEqual(len(set_b), 5)

        seen_weights = set()
        for spec in self.specs:
            sig = (spec.case.palette, spec.case.weights, spec.case.event_indices)
            self.assertNotIn(sig, existing_signatures)
            self.assertNotIn(sig, seen_weights)
            seen_weights.add(sig)
            self.assertTrue(spec.case.held_out)

    def test_both_sets_cover_all_required_regimes_with_clear_probe_margins(self) -> None:
        required_regimes = {"EXACT", "BOUNDED", "UNIDENTIFIABLE", "ROUNDED_SRGB8", "ROUNDED_LINEAR8"}
        for set_name in ("A", "B"):
            subset = [s for s in self.specs if s.set_name == set_name]
            self.assertEqual({s.regime for s in subset}, required_regimes)
            self.assertEqual({s.query_mode for s in subset}, {"exact", "srgb8", "linear8"})
            q4_answers = set()
            for spec in subset:
                pal = self.palettes[spec.case.palette]
                rgb = bc.blend_colour(pal, spec.case.weights)
                if spec.query_mode == "exact":
                    cert = bc.solve_event_bounds(pal, rgb, spec.case.event_indices)
                    p_min, p_max = cert.p_min, cert.p_max
                else:
                    obs = dc.encode_rgb(rgb, spec.query_mode)
                    cert = qb.solve_observation(pal, obs, spec.case.event_indices, spec.query_mode)
                    p_min, p_max = cert.p_min, cert.p_max
                    exact = bc.solve_event_bounds(pal, rgb, spec.case.event_indices)
                    self.assertGreater(p_max - p_min, exact.p_max - exact.p_min)
                # Ensure probe threshold is well separated from the queried bound (> 0.005 margin).
                if spec.probe_op == "gt":
                    self.assertGreater(abs(p_max - spec.probe_threshold), F(1, 200))
                    q4_answers.add(p_max > spec.probe_threshold)
                elif spec.probe_op == "lt":
                    self.assertGreater(abs(p_min - spec.probe_threshold), F(1, 200))
                    q4_answers.add(p_min < spec.probe_threshold)
                else:
                    self.fail(f"Unexpected probe_op: {spec.probe_op}")
            self.assertEqual(q4_answers, {True, False})

    def test_independent_radon_and_ramp_identities_without_solver(self) -> None:
        pa = self.palettes["citrus_slate_3d"]
        pb = self.palettes["ochre_indigo_3d"]
        pr = self.palettes["amber_navy_ramp"]

        # Citrus Slate: c2 = 1/4 c0 + 1/4 c1 + 1/5 c3 + 3/10 c4
        expected_c2 = bc.blend_colour(pa, (F(1, 4), F(1, 4), F(0), F(1, 5), F(3, 10)))
        self.assertEqual(pa.colours[2], expected_c2)

        # Ochre Indigo: d2 = 3/10 d0 + 1/5 d1 + 1/4 d3 + 1/4 d4
        expected_d2 = bc.blend_colour(pb, (F(3, 10), F(1, 5), F(0), F(1, 4), F(1, 4)))
        self.assertEqual(pb.colours[2], expected_d2)

        # Amber Navy ramp unidentifiable point: 1/4 r0 + 3/4 r2 == 3/4 r1 + 1/4 r3
        rgb_ev_0 = bc.blend_colour(pr, (F(1, 4), F(0), F(3, 4), F(0), F(0)))
        rgb_ev_1 = bc.blend_colour(pr, (F(0), F(3, 4), F(0), F(1, 4), F(0)))
        self.assertEqual(rgb_ev_0, rgb_ev_1)

    def test_deterministic_regeneration_and_committed_files_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            first_dir = Path(tmp) / "run1"
            second_dir = Path(tmp) / "run2"
            cmp_mod.generate_comparison_pack(first_dir)
            cmp_mod.generate_comparison_pack(second_dir)

            files1 = sorted(p.relative_to(first_dir) for p in first_dir.rglob("*") if p.is_file())
            files2 = sorted(p.relative_to(second_dir) for p in second_dir.rglob("*") if p.is_file())
            self.assertEqual(files1, files2)
            self.assertGreaterEqual(len(files1), 13)
            for rel in files1:
                self.assertEqual((first_dir / rel).read_bytes(), (second_dir / rel).read_bytes(), str(rel))
                committed = self.comp_dir / rel
                self.assertTrue(committed.exists(), f"Missing committed file {rel}")
                self.assertEqual((first_dir / rel).read_bytes(), committed.read_bytes(), f"Drift in {rel}")

    def test_committed_certificates_and_keys_verify_without_optimizer(self) -> None:
        with patch.object(bc, "_simplex_minimize", side_effect=AssertionError("called optimizer")):
            cases_count, obs_count = cmp_mod.verify_comparison_pack(self.comp_dir)
        self.assertEqual(cases_count, 10)
        self.assertEqual(obs_count, 20)

        # Verify corruption of an answer key or certificate is caught.
        cert_path = self.comp_dir / "certificates" / "set_a_certificates.json"
        bad_cert = deepcopy(json.loads(cert_path.read_text(encoding="utf-8")))
        bad_cert["swatches"][0]["hex"] = "#000000"
        with self.assertRaises(ValueError):
            verify_atlas(bad_cert)

    def test_views_are_well_formed_and_baseline_does_not_leak_answers(self) -> None:
        for set_letter in ("a", "b"):
            atlas_dir = self.comp_dir / f"atlas_{set_letter}"
            svg_text = (atlas_dir / "first_legend.svg").read_text(encoding="utf-8")
            ET.fromstring(svg_text)
            atlas_html = (atlas_dir / "first_legend.html").read_text(encoding="utf-8")
            self.assertIn(svg_text, atlas_html)
            self.assertIn('id="case-choice"', atlas_html)
            self.assertIn('id="vector-toggle"', atlas_html)

            dist_html = (self.comp_dir / f"dist_{set_letter}" / "index.html").read_text(encoding="utf-8")
            self.assertIn('id="case-choice"', dist_html)
            self.assertIn('class="bar"', dist_html)
            for forbidden in ("EXACT", "BOUNDED", "UNIDENTIFIABLE", "conservative", "witnesses.json", "answer_keys"):
                self.assertNotIn(forbidden, dist_html)
            for idx in range(5):
                case_id = f"H{idx + 1}{set_letter.upper()}"
                self.assertIn(case_id, atlas_html)
                self.assertIn(case_id, dist_html)

        prompts_text = (self.comp_dir / "prompts.json").read_text(encoding="utf-8")
        self.assertNotIn("answer_keys", prompts_text)
        prompts = json.loads(prompts_text)
        for item in prompts["cases"]:
            self.assertNotIn("weights", item)
            self.assertNotIn("p_min", item)
            self.assertNotIn("p_max", item)
            self.assertNotIn("status", item)

    def test_scorer_enforces_preregistered_pass_inconclusive_and_fail_rules(self) -> None:
        keys = json.loads((self.comp_dir / "keys" / "answer_keys.json").read_text(encoding="utf-8"))

        def make_perfect_answers(set_name: str, rating: int) -> dict:
            out = {}
            for cid, key in keys["cases"].items():
                if key["set"] != set_name:
                    continue
                out[cid] = {
                    "q1_p_min": key["p_min"],
                    "q2_p_max": key["p_max"],
                    "q3_status": key["status"],
                    "q4_probe": key["q4_answer"],
                    "q5_clarity": rating,
                }
            return out

        # 1. PASS: Order 1 (Dist A -> Atlas B), Atlas 20/20 (clarity 5), Dist 16/20 (clarity 3).
        dist_a = make_perfect_answers("A", 3)
        dist_a["H2A"]["q1_p_min"] = "1/5"
        dist_a["H2A"]["q2_p_max"] = "4/5"
        dist_a["H3A"]["q3_status"] = "BOUNDED"
        dist_a["H4A"]["q4_probe"] = "NO"
        atlas_b = make_perfect_answers("B", 5)
        pass_result = cmp_mod.score_responses(
            {
                "order": "dist_a_then_atlas_b",
                "atlas_view": atlas_b,
                "dist_view": dist_a,
                "phone_desktop_ok": True,
            },
            keys,
        )
        self.assertEqual(pass_result["outcome"], "PASS")
        self.assertEqual(pass_result["atlas_score"], 20)
        self.assertEqual(pass_result["dist_score"], 16)

        # 2. PASS via intelligibility margin when both score >= 18/20.
        tie_acc_pass = cmp_mod.score_responses(
            {
                "order": "dist_a_then_atlas_b",
                "atlas_view": make_perfect_answers("B", 5),
                "dist_view": make_perfect_answers("A", 3),
                "phone_desktop_ok": True,
            },
            keys,
        )
        self.assertEqual(tie_acc_pass["outcome"], "PASS")

        # 3. INCONCLUSIVE when both get 20/20 and equal clarity (4 vs 4).
        inconclusive = cmp_mod.score_responses(
            {
                "order": "dist_a_then_atlas_b",
                "atlas_view": make_perfect_answers("B", 4),
                "dist_view": make_perfect_answers("A", 4),
                "phone_desktop_ok": True,
            },
            keys,
        )
        self.assertEqual(inconclusive["outcome"], "INCONCLUSIVE")

        # 4. FAIL when unidentifiable case is misclassified in Atlas even with 19/20 total.
        missed_unid = make_perfect_answers("B", 5)
        missed_unid["H3B"]["q3_status"] = "BOUNDED"
        fail_unid = cmp_mod.score_responses(
            {
                "order": "dist_a_then_atlas_b",
                "atlas_view": missed_unid,
                "dist_view": make_perfect_answers("A", 3),
                "phone_desktop_ok": True,
            },
            keys,
        )
        self.assertEqual(fail_unid["outcome"], "FAIL")

        # 5. FAIL when Atlas score < 17/20 or clarity < 4.0 or Dist beats Atlas.
        low_clarity = cmp_mod.score_responses(
            {
                "order": "dist_a_then_atlas_b",
                "atlas_view": make_perfect_answers("B", 3),
                "dist_view": make_perfect_answers("A", 2),
                "phone_desktop_ok": True,
            },
            keys,
        )
        self.assertEqual(low_clarity["outcome"], "FAIL")

    def test_cli_verify_exits_zero(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(PROJECT_DIR / "comparison.py"), "verify"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("VERIFIED", proc.stdout)


if __name__ == "__main__":
    unittest.main()
