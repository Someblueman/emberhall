"""Tests for the exact finite-palette weighted-average colour model,
primal/dual event-probability certificates, and regenerable vector legend.
"""

from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

PROJECT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

import blended_colour as bc
import example_import as ei
import render_legend as rl


class WeightedAverageModelTests(unittest.TestCase):
    def test_two_colour_palette_is_uniquely_identifiable(self):
        palette = bc.builtin_palettes()["two_colour_diverging"]
        self.assertEqual(bc.nullspace_dimension(palette), 0)

        weights = (Fraction(1, 4), Fraction(3, 4))
        rgb = bc.blend_colour(palette, weights)
        cert = bc.solve_event_bounds(palette, rgb, event_indices=(1,))
        bc.verify_certificate(palette, rgb, (1,), cert)

        self.assertEqual(cert.p_min, Fraction(3, 4))
        self.assertEqual(cert.p_max, Fraction(3, 4))
        self.assertEqual(cert.status, "EXACT")
        self.assertEqual(cert.witness_min, weights)
        self.assertEqual(cert.witness_max, weights)

    def test_five_colour_3d_palette_has_exact_ambiguous_witness_pair(self):
        palette = bc.builtin_palettes()["five_colour_tetra_3d"]
        self.assertEqual(bc.nullspace_dimension(palette), 1)

        # Pure stop c3 vs convex combination of c1, c2, c4, c5: exact same RGB.
        p_a = (Fraction(0), Fraction(0), Fraction(1), Fraction(0), Fraction(0))
        p_b = (Fraction(1, 5), Fraction(2, 5), Fraction(0), Fraction(3, 10), Fraction(1, 10))
        rgb_a = bc.blend_colour(palette, p_a)
        rgb_b = bc.blend_colour(palette, p_b)
        self.assertEqual(rgb_a, rgb_b)

        # For event "High risk (Level >= 4)", p_a has 0 while p_b has 2/5.
        cert_high = bc.solve_event_bounds(palette, rgb_a, event_indices=(3, 4))
        bc.verify_certificate(palette, rgb_a, (3, 4), cert_high)
        self.assertEqual(cert_high.p_min, Fraction(0))
        self.assertEqual(cert_high.p_max, Fraction(2, 5))
        self.assertEqual(cert_high.status, "BOUNDED")

        # For event "Exact Level 3", pure stop c3 is completely unidentifiable [0, 1].
        cert_mid = bc.solve_event_bounds(palette, rgb_a, event_indices=(2,))
        bc.verify_certificate(palette, rgb_a, (2,), cert_mid)
        self.assertEqual(cert_mid.p_min, Fraction(0))
        self.assertEqual(cert_mid.p_max, Fraction(1))
        self.assertEqual(cert_mid.status, "UNIDENTIFIABLE")

    def test_five_colour_3d_outer_blend_gives_tight_tail_bound(self):
        palette = bc.builtin_palettes()["five_colour_tetra_3d"]
        # Blend near face (c1, c3, c4) with high Level-4 weight.
        p = (Fraction(1, 4), Fraction(0), Fraction(1, 4), Fraction(1, 2), Fraction(0))
        rgb = bc.blend_colour(palette, p)
        cert = bc.solve_event_bounds(palette, rgb, event_indices=(3, 4))
        bc.verify_certificate(palette, rgb, (3, 4), cert)
        self.assertEqual(cert.p_min, Fraction(1, 2))
        self.assertEqual(cert.p_max, Fraction(3, 5))
        self.assertEqual(cert.status, "BOUNDED")

        # Pure boundary face blend without c3 is uniquely recovered.
        p_face = (Fraction(1, 5), Fraction(1, 5), Fraction(0), Fraction(3, 5), Fraction(0))
        rgb_face = bc.blend_colour(palette, p_face)
        cert_face = bc.solve_event_bounds(palette, rgb_face, event_indices=(3, 4))
        bc.verify_certificate(palette, rgb_face, (3, 4), cert_face)
        self.assertEqual(cert_face.p_min, Fraction(3, 5))
        self.assertEqual(cert_face.p_max, Fraction(3, 5))
        self.assertEqual(cert_face.status, "EXACT")

    def test_1d_linear_ramp_is_more_ambiguous_than_3d_palette(self):
        ramp = bc.builtin_palettes()["five_colour_ramp"]
        self.assertEqual(bc.nullspace_dimension(ramp), 3)

        # Midpoint colour c3 on a 1D ramp gives wide bounds on P(Level >= 4).
        rgb_mid = ramp.colours[2]
        cert = bc.solve_event_bounds(ramp, rgb_mid, event_indices=(3, 4))
        bc.verify_certificate(ramp, rgb_mid, (3, 4), cert)
        self.assertEqual(cert.p_min, Fraction(0))
        self.assertEqual(cert.p_max, Fraction(2, 3))
        self.assertEqual(cert.status, "BOUNDED")

        # Extreme-vs-middle event E={0, 4} at midpoint is totally unidentifiable [0, 1].
        cert_ext = bc.solve_event_bounds(ramp, rgb_mid, event_indices=(0, 4))
        bc.verify_certificate(ramp, rgb_mid, (0, 4), cert_ext)
        self.assertEqual(cert_ext.p_min, Fraction(0))
        self.assertEqual(cert_ext.p_max, Fraction(1))
        self.assertEqual(cert_ext.status, "UNIDENTIFIABLE")

    def test_out_of_gamut_colour_raises_infeasible(self):
        palette = bc.builtin_palettes()["five_colour_tetra_3d"]
        with self.assertRaises(bc.InfeasibleColourError):
            bc.solve_event_bounds(palette, (Fraction(1), Fraction(1), Fraction(1)), (3, 4))

    def test_corrupted_certificate_is_rejected(self):
        palette = bc.builtin_palettes()["five_colour_tetra_3d"]
        rgb = palette.colours[2]
        cert = bc.solve_event_bounds(palette, rgb, event_indices=(3, 4))

        # 1. Corrupt bound value.
        bad_bound = bc.BoundCertificate(
            event_indices=cert.event_indices,
            p_min=cert.p_min,
            p_max=cert.p_max - Fraction(1, 100),
            witness_min=cert.witness_min,
            witness_max=cert.witness_max,
            dual_min=cert.dual_min,
            dual_max=cert.dual_max,
            status=cert.status,
        )
        with self.assertRaises(ValueError):
            bc.verify_certificate(palette, rgb, (3, 4), bad_bound)

        # 2. Corrupt dual hyperplane so one stop violates dual inequality.
        bad_dual = bc.BoundCertificate(
            event_indices=cert.event_indices,
            p_min=cert.p_min,
            p_max=cert.p_max,
            witness_min=cert.witness_min,
            witness_max=cert.witness_max,
            dual_min=cert.dual_min,
            dual_max=(cert.dual_max[0] - Fraction(1, 20), *cert.dual_max[1:]),
            status=cert.status,
        )
        with self.assertRaises(ValueError):
            bc.verify_certificate(palette, rgb, (3, 4), bad_dual)

        # 3. Corrupt primal witness weights so they do not sum to 1.
        w_bad = list(cert.witness_max)
        w_bad[0] += Fraction(1, 50)
        bad_witness = bc.BoundCertificate(
            event_indices=cert.event_indices,
            p_min=cert.p_min,
            p_max=cert.p_max,
            witness_min=cert.witness_min,
            witness_max=tuple(w_bad),
            dual_min=cert.dual_min,
            dual_max=cert.dual_max,
            status=cert.status,
        )
        with self.assertRaises(ValueError):
            bc.verify_certificate(palette, rgb, (3, 4), bad_witness)


class LegendGenerationTests(unittest.TestCase):
    def test_regenerates_valid_svg_html_and_checked_witnesses(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            manifest = rl.generate_all(out_dir)
            svg_path = out_dir / "first_legend.svg"
            html_path = out_dir / "first_legend.html"
            witness_path = out_dir / "witnesses.json"

            self.assertTrue(svg_path.exists())
            self.assertTrue(html_path.exists())
            self.assertTrue(witness_path.exists())

            # Parse SVG as strict XML and confirm key readable content.
            tree = ET.parse(svg_path)
            root = tree.getroot()
            self.assertTrue(root.tag.endswith("svg"))
            svg_text = "".join(root.itertext())
            self.assertIn("UNIDENTIFIABLE", svg_text)
            self.assertIn("EXACT", svg_text)
            self.assertIn("BOUNDED", svg_text)

            # Verify every exported witness certificate against exact rational solver.
            data = json.loads(witness_path.read_text(encoding="utf-8"))
            self.assertGreaterEqual(len(data["swatches"]), 5)
            for item in data["swatches"]:
                pal = bc.builtin_palettes()[item["palette"]]
                rgb = tuple(Fraction(x) for x in item["rgb"])
                ev = tuple(item["event_indices"])
                cert = bc.certificate_from_dict(item["certificate"])
                bc.verify_certificate(pal, rgb, ev, cert)

            # Check manifest matches written filenames.
            self.assertEqual(Path(manifest["svg"]).name, "first_legend.svg")

    def test_cli_generates_reproducible_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run(
                [sys.executable, str(PROJECT_DIR / "render_legend.py"), "--out", tmp],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("Verified", proc.stdout)

    def test_import_example_runs_and_renders(self):
        summary = ei.run_example()
        self.assertEqual(summary["p_min"], "1/2")
        self.assertEqual(summary["p_max"], "3/5")
        self.assertEqual(summary["status"], "BOUNDED")
        self.assertGreater(summary["svg_bytes"], 1000)


if __name__ == "__main__":
    unittest.main()
