"""A real caller: declare a palette, certify its blend, import the SVG renderer.

Run directly, or let render_legend.py regenerate this output alongside the atlas.
"""

from fractions import Fraction as F
import json
from pathlib import Path
import tempfile

import blended_colour as bc
import display_colour as dc
import quantized_bounds as qb
import render_legend as rl


def run_example(out_dir: Path | None = None) -> dict:
    palette = bc.Palette(
        'survey-risk', ('None', 'Low', 'Middle', 'High', 'Extreme'),
        tuple(F(i) for i in range(5)),
        ((F(0), F(0), F(0)), (F(1), F(0), F(0)),
         (F(2, 5), F(3, 10), F(1, 10)), (F(0), F(1), F(0)), (F(0), F(0), F(1))),
    )
    case = rl.Case('Survey', 'A caller-defined risk palette', palette.name,
                   (F(1, 4), F(0), F(1, 4), F(1, 2), F(0)), (3, 4), 'P(High or Extreme)')
    rgb = bc.blend_colour(palette, case.weights)
    exact = bc.solve_event_bounds(palette, rgb, case.event_indices)
    bc.verify_certificate(palette, rgb, case.event_indices, exact)
    observed = dc.encode_rgb(rgb)
    quantized = qb.solve_observation(palette, observed, case.event_indices)
    qb.verify_observation(palette, observed, case.event_indices, quantized)
    rendered = rl.render_atlas({palette.name: palette}, (case,))
    # Temporary directory only when called without a destination (e.g. unit tests).
    with tempfile.TemporaryDirectory() as temporary:
        target = out_dir if out_dir is not None else Path(temporary)
        target.mkdir(parents=True, exist_ok=True)
        (target / 'example.svg').write_text(rendered['svg'], encoding='utf-8')
        (target / 'example-certificates.json').write_text(rendered['witnesses'], encoding='utf-8')
        return dict(palette=palette.name, hex=dc.hex_rgb(observed), p_min=str(exact.p_min),
                    p_max=str(exact.p_max), status=exact.status,
                    srgb8_min=str(quantized.p_min), srgb8_max=str(quantized.p_max),
                    svg_bytes=(target / 'example.svg').stat().st_size)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=Path(__file__).resolve().parent / 'legends')
    args = parser.parse_args()
    print(json.dumps(run_example(args.out), indent=2, sort_keys=True))
