"""Minimal example importing blended_colour and render_legend to compute a bound
and render a custom legend directory.
"""

from fractions import Fraction
from pathlib import Path
import sys
import tempfile

PROJECT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

import blended_colour as bc
import render_legend as rl


def run_example(out_dir: Path | None = None) -> dict:
    palette = bc.builtin_palettes()["five_colour_tetra_3d"]
    weights = (Fraction(1, 4), Fraction(0), Fraction(1, 4), Fraction(1, 2), Fraction(0))
    rgb = bc.blend_colour(palette, weights)
    cert = bc.solve_event_bounds(palette, rgb, event_indices=(3, 4))
    bc.verify_certificate(palette, rgb, (3, 4), cert)

    with tempfile.TemporaryDirectory() as tmp:
        target = out_dir or Path(tmp)
        manifest = rl.generate_all(target)
        return {
            "hex": bc.rgb_to_hex(rgb),
            "p_min": str(cert.p_min),
            "p_max": str(cert.p_max),
            "status": cert.status,
            "svg_bytes": Path(manifest["svg"]).stat().st_size,
        }


if __name__ == "__main__":
    print(run_example())
