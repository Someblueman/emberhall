import json
import math
import sys
import unittest
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent / "projects" / "shadow-theatre"
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from shadow_model import (  # noqa: E402
    CHALLENGES,
    compute_shadows,
    export_challenge,
    import_challenge,
    matches_target,
)


class ShadowModelTests(unittest.TestCase):
    def test_analytic_endpoint_projection(self):
        # Light at (0, 50), screen at x=100, prop at x=50 from y=40 to y=60
        # Magnification = (100 - 0) / (50 - 0) = 2.0
        # Projected: [50 + 2*(40-50), 50 + 2*(60-50)] = [30, 70]
        res = compute_shadows(
            light={"x": 0.0, "y": 50.0},
            props=[{"x": 50.0, "yLow": 40.0, "yHigh": 60.0}],
            screen={"x": 100.0, "yMin": 0.0, "yMax": 100.0},
        )
        self.assertEqual(res["intervals"], [[30.0, 70.0]])
        self.assertAlmostEqual(res["totalLength"], 40.0)

    def test_overlapping_intervals_merge(self):
        # Two props casting [20, 60] and [40, 80] -> [20, 80]
        res = compute_shadows(
            light={"x": 0.0, "y": 50.0},
            props=[
                {"x": 50.0, "yLow": 35.0, "yHigh": 55.0},  # [20, 60]
                {"x": 50.0, "yLow": 45.0, "yHigh": 65.0},  # [40, 80]
            ],
            screen={"x": 100.0, "yMin": 0.0, "yMax": 100.0},
        )
        self.assertEqual(res["intervals"], [[20.0, 80.0]])
        self.assertAlmostEqual(res["totalLength"], 60.0)

    def test_touching_intervals_merge(self):
        # Two props casting [20, 50] and [50, 80] -> [20, 80]
        res = compute_shadows(
            light={"x": 0.0, "y": 50.0},
            props=[
                {"x": 50.0, "yLow": 35.0, "yHigh": 50.0},  # [20, 50]
                {"x": 50.0, "yLow": 50.0, "yHigh": 65.0},  # [50, 80]
            ],
            screen={"x": 100.0, "yMin": 0.0, "yMax": 100.0},
        )
        self.assertEqual(res["intervals"], [[20.0, 80.0]])
        self.assertAlmostEqual(res["totalLength"], 60.0)

    def test_disjoint_intervals_stay_separate_and_sorted(self):
        # Second prop listed first, casts [70, 90]; first casts [10, 30]
        res = compute_shadows(
            light={"x": 0.0, "y": 50.0},
            props=[
                {"x": 50.0, "yLow": 60.0, "yHigh": 70.0},  # [70, 90]
                {"x": 50.0, "yLow": 30.0, "yHigh": 40.0},  # [10, 30]
            ],
            screen={"x": 100.0, "yMin": 0.0, "yMax": 100.0},
        )
        self.assertEqual(res["intervals"], [[10.0, 30.0], [70.0, 90.0]])
        self.assertAlmostEqual(res["totalLength"], 40.0)

    def test_clipping_partial_and_offscreen(self):
        # Prop 1 casts [-20, 20] -> clipped to [0, 20]
        # Prop 2 casts [80, 130] -> clipped to [80, 100]
        # Prop 3 casts [110, 140] -> completely offscreen (empty)
        res = compute_shadows(
            light={"x": 0.0, "y": 50.0},
            props=[
                {"x": 50.0, "yLow": 15.0, "yHigh": 35.0},   # [-20, 20]
                {"x": 50.0, "yLow": 65.0, "yHigh": 90.0},   # [80, 130]
                {"x": 50.0, "yLow": 80.0, "yHigh": 95.0},   # [110, 140]
            ],
            screen={"x": 100.0, "yMin": 0.0, "yMax": 100.0},
        )
        self.assertEqual(res["intervals"], [[0.0, 20.0], [80.0, 100.0]])
        self.assertAlmostEqual(res["totalLength"], 40.0)

    def test_forbidden_source_and_prop_positions(self):
        screen = {"x": 100.0, "yMin": 0.0, "yMax": 100.0}
        # Light at or beyond screen
        with self.assertRaises(ValueError):
            compute_shadows({"x": 100.0, "y": 50.0}, [], screen)
        with self.assertRaises(ValueError):
            compute_shadows({"x": 120.0, "y": 50.0}, [], screen)

        # Prop at or behind light
        with self.assertRaises(ValueError):
            compute_shadows({"x": 20.0, "y": 50.0}, [{"x": 20.0, "yLow": 40.0, "yHigh": 60.0}], screen)
        with self.assertRaises(ValueError):
            compute_shadows({"x": 20.0, "y": 50.0}, [{"x": 10.0, "yLow": 40.0, "yHigh": 60.0}], screen)

        # Prop at or beyond screen
        with self.assertRaises(ValueError):
            compute_shadows({"x": 20.0, "y": 50.0}, [{"x": 100.0, "yLow": 40.0, "yHigh": 60.0}], screen)
        with self.assertRaises(ValueError):
            compute_shadows({"x": 20.0, "y": 50.0}, [{"x": 110.0, "yLow": 40.0, "yHigh": 60.0}], screen)

        # More than 3 props
        props = [
            {"x": 30.0, "yLow": 10.0, "yHigh": 20.0},
            {"x": 40.0, "yLow": 30.0, "yHigh": 40.0},
            {"x": 50.0, "yLow": 50.0, "yHigh": 60.0},
            {"x": 60.0, "yLow": 70.0, "yHigh": 80.0},
        ]
        with self.assertRaises(ValueError):
            compute_shadows({"x": 0.0, "y": 50.0}, props, screen)

    def test_degenerate_and_non_finite_cases(self):
        screen = {"x": 100.0, "yMin": 0.0, "yMax": 100.0}
        # Zero-length or inverted prop
        with self.assertRaises(ValueError):
            compute_shadows({"x": 0.0, "y": 50.0}, [{"x": 50.0, "yLow": 40.0, "yHigh": 40.0}], screen)
        with self.assertRaises(ValueError):
            compute_shadows({"x": 0.0, "y": 50.0}, [{"x": 50.0, "yLow": 60.0, "yHigh": 40.0}], screen)

        # Degenerate screen
        with self.assertRaises(ValueError):
            compute_shadows({"x": 0.0, "y": 50.0}, [], {"x": 100.0, "yMin": 50.0, "yMax": 50.0})

        # Non-finite coordinates
        with self.assertRaises(ValueError):
            compute_shadows({"x": math.nan, "y": 50.0}, [], screen)

    def test_repeated_results_deterministic(self):
        light = {"x": 10.0, "y": 45.0}
        props = [
            {"x": 40.0, "yLow": 30.0, "yHigh": 50.0},
            {"x": 70.0, "yLow": 55.0, "yHigh": 75.0},
        ]
        screen = {"x": 100.0, "yMin": 0.0, "yMax": 100.0}
        r1 = compute_shadows(light, props, screen)
        r2 = compute_shadows(light, props, screen)
        self.assertEqual(r1, r2)

    def test_lossless_challenge_import_export(self):
        for ch in CHALLENGES:
            exported = export_challenge(ch)
            imported = import_challenge(exported)
            self.assertEqual(imported, ch)

        with self.assertRaises(ValueError):
            import_challenge("{not valid json")
        with self.assertRaises(ValueError):
            import_challenge(json.dumps({"id": "bad"}))

    def test_three_challenges_exist_and_are_solvable(self):
        self.assertEqual(len(CHALLENGES), 3)
        for ch in CHALLENGES:
            # Initial state is valid
            init_res = compute_shadows(ch["light"], ch["props"], ch["screen"])
            self.assertIn("intervals", init_res)
            # Solution state matches target
            sol = ch["solution"]
            sol_res = compute_shadows(sol["light"], sol["props"], ch["screen"])
            self.assertTrue(
                matches_target(sol_res["intervals"], ch["target"], ch.get("tolerance", 0.5)),
                f"Challenge {ch['id']} solution did not match target",
            )


if __name__ == "__main__":
    unittest.main()
