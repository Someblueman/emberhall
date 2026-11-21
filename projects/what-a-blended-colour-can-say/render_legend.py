"""Generate the regenerable Milestone 1 vector probability-range legend (SVG),
checked rational witnesses (JSON), and responsive HTML inspection sheet.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import html
import json
from pathlib import Path
import sys
from typing import Sequence

PROJECT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

import blended_colour as bc


def _pct(val_str: str) -> float:
    return float(Fraction(val_str)) * 100.0


def _fmt_pct(val_str: str) -> str:
    pct = _pct(val_str)
    if abs(pct - round(pct)) < 1e-9:
        return f"{int(round(pct))}%"
    return f"{pct:.1f}%"


def _badge_style(status: str) -> tuple[str, str, str]:
    if status == "EXACT":
        return "#e6f4ea", "#137333", "#a8dab5"
    if status == "BOUNDED":
        return "#e8f0fe", "#1967d2", "#aecbfa"
    return "#fce8e6", "#b31412", "#f6aea9"


def build_svg(swatches: list[dict]) -> str:
    """Render a crisp, standalone 780x1040 vector probability-interval legend."""
    palettes = bc.builtin_palettes()
    p5 = palettes["five_colour_tetra_3d"]
    p2 = palettes["two_colour_diverging"]
    p1 = palettes["five_colour_ramp"]

    w, h = 780, 1040
    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" role="img" aria-labelledby="legend-title legend-desc">',
        '<title id="legend-title">What a Blended Colour Can Say — First Probability-Interval Legend</title>',
        '<desc id="legend-desc">Finite-palette colour blending legend showing exact, bounded, and unidentifiable event probabilities.</desc>',
        "<defs>",
        '  <pattern id="unid-hatch" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">',
        '    <rect width="10" height="10" fill="#fce8e6"/>',
        '    <line x1="0" y1="0" x2="0" y2="10" stroke="#c5221f" stroke-width="3.5" stroke-opacity="0.45"/>',
        "  </pattern>",
        '  <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1 L 8 5 L 0 9 z" fill="#4a5568"/>',
        "  </marker>",
        "</defs>",
        '<style>',
        '  .bg { fill: #fbfaf7; }',
        '  .card { fill: #ffffff; stroke: #dcd7cc; stroke-width: 1.25; }',
        '  .title { font: 700 22px "Georgia", "Times New Roman", serif; fill: #1c2026; }',
        '  .subtitle { font: 400 13px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #4a5568; }',
        '  .sec { font: 700 14px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #1c2026; letter-spacing: 0.4px; }',
        '  .lbl { font: 600 13px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #1c2026; }',
        '  .small { font: 400 12px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #4a5568; }',
        '  .bar-light { font: 600 11.5px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #ffffff; }',
        '  .bar-dark { font: 600 11.5px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #1c2026; }',
        '  .mono { font: 600 12px "SFMono-Regular", Consolas, monospace; fill: #1c2026; }',
        '  .badge { font: 700 11px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; letter-spacing: 0.4px; }',
        '</style>',
        f'<rect class="bg" x="0" y="0" width="{w}" height="{h}"/>',
        # Header
        '<text class="title" x="32" y="42">What a Blended Colour Can Say</text>',
        '<text class="subtitle" x="32" y="64">Probability-interval legend under exact linear RGB blending (Milestone 1)</text>',
        '<line x1="32" y1="78" x2="748" y2="78" stroke="#dcd7cc" stroke-width="1"/>',
    ]

    # Section 1: Palette Stops
    parts.append('<rect class="card" x="32" y="92" width="716" height="138" rx="8"/>')
    parts.append('<text class="sec" x="48" y="116">1. DECLARED PALETTES &amp; TARGET EVENT E = {L4, L5}</text>')
    parts.append('<text class="small" x="48" y="136">5-Colour 3D Palette (non-coplanar, nullspace dim 1):</text>')
    for i, (lab, hx) in enumerate(zip(p5.labels, p5.hex_colours())):
        sx = 48 + i * 96
        sy = 146
        if i in (3, 4):
            parts.append(f'<rect x="{sx-4}" y="{sy-4}" width="88" height="66" rx="6" fill="#fff5eb" stroke="#d95f02" stroke-width="1.5" stroke-dasharray="4 2"/>')
        parts.append(f'<rect x="{sx}" y="{sy}" width="80" height="26" rx="4" fill="{hx}" stroke="#1c2026" stroke-opacity="0.25"/>')
        parts.append(f'<text class="lbl" x="{sx}" y="{sy+42}">{html.escape(lab.split()[0])}</text>')
        parts.append(f'<text class="mono" x="{sx}" y="{sy+57}">{hx}</text>')
    parts.append('<text class="badge" x="392" y="136" style="fill:#b44600">EVENT E = L4 or L5</text>')
    # 2-colour legend mini note
    parts.append('<line x1="538" y1="126" x2="538" y2="216" stroke="#e6e1d6"/>')
    parts.append('<text class="small" x="554" y="136">2-Colour Baseline:</text>')
    for i, (lab, hx) in enumerate(zip(("Low", "High"), p2.hex_colours())):
        sx = 554 + i * 92
        parts.append(f'<rect x="{sx}" y="146" width="80" height="26" rx="4" fill="{hx}" stroke="#1c2026" stroke-opacity="0.25"/>')
        parts.append(f'<text class="lbl" x="{sx}" y="188">{lab}</text>')
        parts.append(f'<text class="mono" x="{sx}" y="203">{hx}</text>')

    # Section 2: Ambiguous Witness (Dist A vs Dist B -> same swatch)
    parts.append('<rect class="card" x="32" y="244" width="716" height="178" rx="8"/>')
    parts.append('<text class="sec" x="48" y="268">2. AMBIGUOUS WITNESS: TWO DISTRIBUTIONS, ONE IDENTICAL COLOUR</text>')
    # Dist A bar (100% L3)
    parts.append('<text class="lbl" x="48" y="294">Dist. A (100% L3):</text>')
    parts.append(f'<rect x="176" y="280" width="204" height="22" rx="3" fill="{p5.hex_colours()[2]}" stroke="#1c2026" stroke-opacity="0.3"/>')
    parts.append('<text class="bar-light" x="184" y="295">100% L3  |  P(E) = 0%</text>')
    # Dist B stacked bar (20% L1, 40% L2, 30% L4, 10% L5)
    parts.append('<text class="lbl" x="48" y="334">Dist. B (0% L3):</text>')
    dist_b = [(0, 0.20, "20%", "bar-light"), (1, 0.40, "40%", "bar-dark"), (3, 0.30, "30%", "bar-dark"), (4, 0.10, "", "bar-light")]
    bx = 176.0
    for idx, frac, txt, cls in dist_b:
        bw = frac * 204.0
        parts.append(f'<rect x="{bx:.1f}" y="320" width="{bw:.1f}" height="22" fill="{p5.hex_colours()[idx]}" stroke="#ffffff" stroke-width="1"/>')
        if txt:
            parts.append(f'<text class="{cls}" x="{bx+5:.1f}" y="335">{txt}</text>')
        bx += bw
    parts.append('<text class="small" x="176" y="358">20% L1 + 40% L2 + 30% L4 + 10% L5</text>')
    parts.append('<text class="small" x="176" y="374">P(E) = 40% high-risk mass</text>')
    # Arrows to shared colour
    parts.append('<line x1="386" y1="291" x2="432" y2="312" stroke="#4a5568" stroke-width="1.6" marker-end="url(#arrow)"/>')
    parts.append('<line x1="386" y1="331" x2="432" y2="320" stroke="#4a5568" stroke-width="1.6" marker-end="url(#arrow)"/>')
    # Shared swatch
    shared_hex = p5.hex_colours()[2]
    parts.append(f'<rect x="442" y="284" width="68" height="62" rx="8" fill="{shared_hex}" stroke="#1c2026" stroke-width="1.5"/>')
    parts.append(f'<text class="mono" x="448" y="362">{shared_hex}</text>')
    # Interpretation callout
    parts.append('<text class="lbl" x="528" y="296">Identical pixel colour!</text>')
    parts.append('<text class="small" x="528" y="316">• P(L4 or L5): [0%, 40%] (BOUNDED)</text>')
    parts.append('<text class="small" x="528" y="336">• P(Exact L3): [0%, 100%]</text>')
    parts.append('<rect x="528" y="346" width="126" height="22" rx="4" fill="#fce8e6" stroke="#f6aea9"/>')
    parts.append('<text class="badge" x="537" y="361" style="fill:#b31412">UNIDENTIFIABLE</text>')
    parts.append('<text class="small" x="48" y="406">Takeaway: a static stop legend labels #707396 as "100% L3", hiding up to 40% high-risk weight.</text>')

    # Section 3: Probability-Interval Swatches
    parts.append('<rect class="card" x="32" y="436" width="716" height="464" rx="8"/>')
    parts.append('<text class="sec" x="48" y="462">3. PROBABILITY-INTERVAL LEGEND (CHECKED SWATCHES &amp; HELD-OUT CASE)</text>')
    parts.append('<text class="small" x="48" y="482">Swatch</text>')
    parts.append('<text class="small" x="126" y="482">Case / Event</text>')
    parts.append('<text class="small" x="394" y="482">Certified Range [P_min, P_max]</text>')
    parts.append('<text class="small" x="614" y="482">Status</text>')
    parts.append('<line x1="48" y1="490" x2="732" y2="490" stroke="#e2ddd3"/>')

    bar_x = 394
    bar_w = 196
    for idx, item in enumerate(swatches):
        ry = 502 + idx * 63
        cert = item["certificate"]
        status = cert["status"]
        pmin = _pct(cert["p_min"])
        pmax = _pct(cert["p_max"])
        bg_b, fg_b, brd_b = _badge_style(status)

        if item.get("held_out"):
            parts.append(f'<rect x="42" y="{ry-4}" width="696" height="56" rx="6" fill="#fffdf5" stroke="#e2c675" stroke-dasharray="4 3"/>')

        # Colour swatch
        parts.append(f'<rect x="48" y="{ry+2}" width="52" height="36" rx="6" fill="{item["hex"]}" stroke="#1c2026" stroke-width="1.2"/>')
        parts.append(f'<text class="mono" x="48" y="{ry+50}">{item["id"]} {item["hex"]}</text>')

        # Title & concise subtitle (bounded width before bar_x=394)
        parts.append(f'<text class="lbl" x="126" y="{ry+16}">{html.escape(item["title"])}</text>')
        parts.append(f'<text class="small" x="126" y="{ry+34}">{html.escape(item["event_label"])} · {html.escape(item["subtitle"])}</text>')

        # Interval track 0..100%
        parts.append(f'<rect x="{bar_x}" y="{ry+12}" width="{bar_w}" height="14" rx="4" fill="#ebe7df" stroke="#d0c9bb"/>')
        for tick in (0.0, 0.5, 1.0):
            tx = bar_x + tick * bar_w
            parts.append(f'<line x1="{tx:.1f}" y1="{ry+10}" x2="{tx:.1f}" y2="{ry+28}" stroke="#a09a8e" stroke-width="1"/>')

        x1 = bar_x + (pmin / 100.0) * bar_w
        x2 = bar_x + (pmax / 100.0) * bar_w
        if status == "EXACT":
            parts.append(f'<polygon points="{x1:.1f},{ry+9} {x1+7:.1f},{ry+19} {x1:.1f},{ry+29} {x1-7:.1f},{ry+19}" fill="#137333" stroke="#ffffff" stroke-width="1"/>')
        elif status == "UNIDENTIFIABLE":
            parts.append(f'<rect x="{bar_x}" y="{ry+12}" width="{bar_w}" height="14" rx="4" fill="url(#unid-hatch)" stroke="#c5221f" stroke-width="1.3"/>')
        else:
            iw = max(4.0, x2 - x1)
            parts.append(f'<rect x="{x1:.1f}" y="{ry+12}" width="{iw:.1f}" height="14" rx="3" fill="#1967d2" fill-opacity="0.82" stroke="#114a9f" stroke-width="1"/>')

        rng_txt = _fmt_pct(cert["p_min"]) if status == "EXACT" else f"{_fmt_pct(cert['p_min'])} – {_fmt_pct(cert['p_max'])}"
        parts.append(f'<text class="mono" x="{bar_x}" y="{ry+42}">{rng_txt}</text>')

        # Status badge
        bw_badge = 122 if status == "UNIDENTIFIABLE" else 84
        parts.append(f'<rect x="610" y="{ry+8}" width="{bw_badge}" height="22" rx="4" fill="{bg_b}" stroke="{brd_b}"/>')
        parts.append(f'<text class="badge" x="619" y="{ry+23}" style="fill:{fg_b}">{status}</text>')

    # Section 4: Geometry summary
    parts.append('<rect class="card" x="32" y="914" width="716" height="102" rx="8"/>')
    parts.append('<text class="sec" x="48" y="938">4. WHY PALETTE GEOMETRY CONTROLS IDENTIFIABILITY</text>')
    parts.append(f'<text class="small" x="48" y="960">• 2 colours (nullspace dim {bc.nullspace_dimension(p2)}): unique recovery on the segment [c1, c2].</text>')
    parts.append(f'<text class="small" x="48" y="979">• 5-colour 1D ramp (nullspace dim {bc.nullspace_dimension(p1)}): 3-D ambiguity polytope; S5 tail spans 0%–67%.</text>')
    parts.append(f'<text class="small" x="48" y="998">• 5-colour 3D palette (nullspace dim {bc.nullspace_dimension(p5)}): 1-D fiber gives tight bounds (S2 exact, S3 10pp) and flags Radon ambiguities (S6).</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def build_html(svg_markup: str, swatches: list[dict]) -> str:
    rows = []
    for item in swatches:
        c = item["certificate"]
        rng = _fmt_pct(c["p_min"]) if c["status"] == "EXACT" else f"{_fmt_pct(c['p_min'])}–{_fmt_pct(c['p_max'])}"
        rows.append(
            f"<tr><td><code>{html.escape(item['id'])}</code></td>"
            f"<td><span class='chip' style='background:{item['hex']}'></span> <code>{item['hex']}</code></td>"
            f"<td class='col-case'>{html.escape(item['title'])}</td>"
            f"<td>{html.escape(item['event_label'])}</td>"
            f"<td><strong>{rng}</strong></td>"
            f"<td><span class='pill pill-{c['status'].lower()}'>{c['status']}</span></td></tr>"
        )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>What a Blended Colour Can Say — First Vector Legend</title>
<style>
  :root {{ color-scheme: light; }}
  body {{ margin: 0; padding: 16px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f4f1ea; color: #1c2026; line-height: 1.45; }}
  main {{ max-width: 820px; margin: 0 auto; }}
  h1 {{ font-family: Georgia, serif; font-size: 1.45rem; margin: 0 0 0.25rem; }}
  p.lead {{ margin: 0 0 1rem; color: #4a5568; font-size: 0.95rem; }}
  .svg-frame {{ background: #fbfaf7; border: 1px solid #d5cfc3; border-radius: 10px; padding: 8px; overflow: hidden; }}
  .svg-frame svg {{ display: block; width: 100%; height: auto; }}
  .table-wrap {{ margin-top: 16px; background: #fff; border: 1px solid #d5cfc3; border-radius: 10px; overflow-x: auto; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
  th, td {{ text-align: left; padding: 7px 8px; border-bottom: 1px solid #ece7dc; }}
  th {{ background: #faf8f3; font-weight: 600; }}
  @media (max-width: 600px) {{
    table {{ font-size: 0.76rem; }}
    th, td {{ padding: 6px 5px; }}
    .col-case {{ display: none; }}
  }}
  .chip {{ display: inline-block; width: 14px; height: 14px; border-radius: 3px; vertical-align: middle; border: 1px solid rgba(0,0,0,0.25); }}
  .pill {{ display: inline-block; padding: 2px 7px; border-radius: 4px; font-size: 0.74rem; font-weight: 700; }}
  .pill-exact {{ background: #e6f4ea; color: #137333; }}
  .pill-bounded {{ background: #e8f0fe; color: #1967d2; }}
  .pill-unidentifiable {{ background: #fce8e6; color: #b31412; }}
  footer {{ margin-top: 12px; font-size: 0.82rem; color: #5f6368; }}
</style>
</head>
<body>
<main>
  <h1>What a Blended Colour Can Say</h1>
  <p class="lead">Preview wrapper for the regenerable Milestone 1 vector legend (<code>first_legend.svg</code>) and exact rational LP certificates (<code>witnesses.json</code>).</p>
  <section class="svg-frame" aria-label="Probability-Interval Vector Legend">
    {svg_markup}
  </section>
  <section class="table-wrap" aria-label="Checked Swatch Certificates Summary">
    <table>
      <thead><tr><th>ID</th><th>Colour</th><th class="col-case">Case</th><th>Event</th><th>Range</th><th>Status</th></tr></thead>
      <tbody>{"".join(rows)}</tbody>
    </table>
  </section>
  <footer>Model premise: exact linear weighted average over declared rational RGB stops. Regenerate with <code>python3 projects/what-a-blended-colour-can-say/render_legend.py</code>.</footer>
</main>
</body>
</html>
"""


def generate_all(out_dir: Path | None = None) -> dict[str, str]:
    target_dir = out_dir or (PROJECT_DIR / "legends")
    target_dir.mkdir(parents=True, exist_ok=True)

    swatches = bc.showcase_witnesses()
    svg_markup = build_svg(swatches)
    html_markup = build_html(svg_markup, swatches)

    svg_path = target_dir / "first_legend.svg"
    html_path = target_dir / "first_legend.html"
    witness_path = target_dir / "witnesses.json"

    svg_path.write_text(svg_markup + "\n", encoding="utf-8")
    html_path.write_text(html_markup, encoding="utf-8")
    witness_path.write_text(
        json.dumps(
            {
                "model": "exact_rational_linear_rgb_weighted_average",
                "palettes": {
                    name: {
                        "labels": list(pal.labels),
                        "colours_hex": list(pal.hex_colours()),
                        "nullspace_dim": bc.nullspace_dimension(pal),
                    }
                    for name, pal in bc.builtin_palettes().items()
                },
                "swatches": swatches,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "svg": str(svg_path),
        "html": str(html_path),
        "witnesses": str(witness_path),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Regenerate first vector legend and verified witnesses.")
    parser.add_argument("--out", type=Path, default=PROJECT_DIR / "legends", help="Output directory")
    args = parser.parse_args(argv)

    manifest = generate_all(args.out)
    data = json.loads(Path(manifest["witnesses"]).read_text(encoding="utf-8"))
    print(f"Verified {len(data['swatches'])} swatches; wrote {manifest['svg']}, {manifest['html']}, {manifest['witnesses']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
