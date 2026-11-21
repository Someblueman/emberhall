"""Importable, parameterized vector atlas of exact and byte-observed bounds."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from fractions import Fraction as F
from html import escape
import json
from pathlib import Path
from typing import Mapping, Sequence

import blended_colour as bc
import display_colour as dc
import quantized_bounds as qb
from verify_atlas import verify_atlas

PROJECT_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Case:
    id: str
    title: str
    palette: str
    weights: tuple[F, ...]
    event_indices: tuple[int, ...]
    event_label: str
    held_out: bool = False


def default_cases() -> tuple[Case, ...]:
    """Preserve the six accepted exact problems, then extend the same model."""
    old = bc.showcase_witnesses()
    cases = [Case(s['id'], s['title'], s['palette'], tuple(map(F, s['weights'])),
                  tuple(s['event_indices']), s['event_label'], s['held_out']) for s in old]
    p2, p5 = 'two_colour_diverging', 'five_colour_tetra_3d'
    cases.extend((
        Case('S7', 'Held-out rational mixture', p5, (F(1, 7), F(2, 7), F(0), F(3, 7), F(1, 7)),
             (3, 4), 'P(Level >= 4)', True),
        Case('S8', 'Binary low endpoint', p2, (F(1), F(0)), (1,), 'P(High)'),
        Case('S9', 'Binary high endpoint', p2, (F(0), F(1)), (1,), 'P(High)'),
        Case('S10', 'Certain event control', p5, (F(1, 5),) * 5, (0, 1, 2, 3, 4), 'P(Any level)'),
    ))
    return tuple(cases)


def evaluate_cases(palettes: Mapping[str, bc.Palette], cases: Sequence[Case],
                   modes: Sequence[str] = dc.MODES) -> list[dict]:
    """Compute and verify all certificates before producing any markup."""
    if not cases or not modes or len(set(c.id for c in cases)) != len(cases):
        raise ValueError('Need cases with unique IDs and at least one display mode')
    if len(set(modes)) != len(modes) or any(m not in dc.MODES for m in modes):
        raise ValueError('Unsupported or duplicate display mode')
    result = []
    for case in cases:
        palette = palettes[case.palette]
        rgb = bc.blend_colour(palette, case.weights)
        cert = bc.solve_event_bounds(palette, rgb, case.event_indices)
        bc.verify_certificate(palette, rgb, case.event_indices, cert)
        observations = []
        for mode in modes:
            rgb8 = dc.encode_rgb(rgb, mode)
            box = dc.observation_box(rgb8, mode)
            bound = qb.solve_observation(palette, rgb8, case.event_indices, mode)
            observations.append(dict(mode=mode, rgb8=list(rgb8), hex=dc.hex_rgb(rgb8),
                                     lower=list(map(str, box[0])), upper=list(map(str, box[1])),
                                     certificate=bound.to_dict()))
        result.append(dict(id=case.id, title=case.title, palette=case.palette,
                           event_label=case.event_label, event_indices=list(case.event_indices),
                           weights=list(map(str, case.weights)), rgb=list(map(str, rgb)),
                           hex=bc.rgb_to_hex(rgb), held_out=case.held_out,
                           certificate=cert.to_dict(), observations=observations))
    return result


def _pct(value: str, upper: bool = False) -> str:
    """Outward two-decimal percent, using integer arithmetic."""
    x = F(value) * 10000
    n = -(-x.numerator // x.denominator) if upper else x.numerator // x.denominator
    return f'{n // 100}.{n % 100:02d}%'


def _range(cert: dict, exact: bool = False) -> str:
    if exact:
        return f"[{cert['p_min']}, {cert['p_max']}]"
    return f"[{_pct(cert['p_min'])}, {_pct(cert['p_max'], True)}]"


def _text(x: float, y: float, value: str, cls: str = '') -> str:
    return f'<text x="{x:g}" y="{y:g}" class="{cls}">{escape(value)}</text>'


def _bars(palette: bc.Palette, weights: Sequence[str], x: int, y: int) -> str:
    parts = []
    cursor = F(x)
    for i, weight in enumerate(weights):
        width = F(weight) * 410
        if width:
            fill = bc.rgb_to_hex(palette.colours[i])
            parts.append(f'<rect x="{float(cursor):.5f}" y="{y}" width="{float(width):.5f}" height="22" fill="{fill}"/>')
            cursor += width
    # Labels outside colours: readability does not depend on palette contrast.
    label = '  '.join(f'{i + 1}: {w}' for i, w in enumerate(weights) if F(w))
    parts.append(_text(x, y + 42, label, 'small'))
    return ''.join(parts)


def build_svg(swatches: list[dict], palettes: Mapping[str, bc.Palette] | None = None,
              title: str = 'What a Blended Colour Can Say') -> str:
    palettes = palettes if palettes is not None else bc.builtin_palettes()
    height = 150 + 290 * len(swatches)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1040" height="{height}" viewBox="0 0 1040 {height}" role="img" aria-labelledby="title desc">',
             f'<title id="title">{escape(title)}</title>',
             '<desc id="desc">Exact probability intervals, conservative byte observation intervals, and endpoint distributions beside each displayed swatch.</desc>',
             '<style>text{font:16px sans-serif;fill:#172c3c}.title{font:bold 29px Georgia,serif}.heading{font:bold 19px sans-serif}.small{font:14px monospace}.label{font:bold 15px sans-serif}</style>',
             f'<rect width="1040" height="{height}" fill="#f3f1e9"/>',
             _text(30, 43, title, 'title'),
             _text(30, 76, 'Linear-light blends. Opaque, flat sRGB swatches. Exact fractions are authoritative.'),
             _text(30, 105, 'Byte ranges are conservative; percentages round outward. Distribution bars show exact-case endpoints.'),
             _text(30, 130, 'linear8 is raw linear data: its hex preview is NOT equivalent displayed light. No reader study claimed.')]
    for j, s in enumerate(swatches):
        y = 150 + 290 * j
        cert = s['certificate']
        parts.extend((f'<rect x="18" y="{y}" width="1004" height="276" rx="10" fill="white"/>',
                      _text(34, y + 30, f"{s['id']} / {s['title']}", 'heading'),
                      _text(34, y + 56, f"{s['event_label']}  {_range(cert, True)}  {cert['status']}", 'label'),
                      f'<rect x="34" y="{y + 77}" width="92" height="76" fill="{s["hex"]}" stroke="#526776"/>',
                      _text(34, y + 178, s['hex'], 'small'),
                      _text(144, y + 94, 'Displayed sRGB8', 'label'),
                      _text(144, y + 120, s['palette'], 'small'),
                      _text(552, y + 58, 'Explicit distributions at exact lower / upper bounds', 'label')))
        for k, endpoint in enumerate(('witness_min', 'witness_max')):
            by = y + 77 + k * 70
            parts.append(_bars(palettes[s['palette']], cert[endpoint], 552, by))
        for k, obs in enumerate(s['observations']):
            oy = y + 214 + 27 * k
            parts.append(_text(34, oy, f"{obs['mode']} {obs['hex']} -> {_range(obs['certificate'])} conservative", 'small'))
        parts.append(_text(552, y + 252, 'Segment labels: stop number : exact probability', 'small'))
    parts.append('</svg>')
    return '\n'.join(parts)


def build_html(swatches: list[dict], palettes: Mapping[str, bc.Palette],
               title: str = 'What a Blended Colour Can Say') -> str:
    cards = []
    options = ''.join(f'<option value="{i}">{escape(s["id"] + " / " + s["title"])}</option>'
                      for i, s in enumerate(swatches))
    for i, s in enumerate(swatches):
        cert, palette = s['certificate'], palettes[s['palette']]
        distributions = []
        for name, key in (('Lower endpoint', 'witness_min'), ('Upper endpoint', 'witness_max')):
            bars = ''.join(f'<span style="flex:{float(F(w)):.12g};background:{bc.rgb_to_hex(palette.colours[i])}"></span>'
                           for i, w in enumerate(cert[key]) if F(w))
            labels = '; '.join(f'{palette.labels[i]}: {w}' for i, w in enumerate(cert[key]) if F(w))
            distributions.append(f'<p><b>{name}</b></p><div class="bar" aria-hidden="true">{bars}</div><p class="numbers">{escape(labels)}</p>')
        observations = ''.join(f'<p><b>{o["mode"]}</b> <code>{o["hex"]}</code>: {_range(o["certificate"])} (conservative)</p>' for o in s['observations'])
        cards.append(f'<article data-case="{i}"><h2>{escape(s["id"] + " / " + s["title"])}</h2><div class="columns"><section>'
                     f'<div class="swatch" style="background:{s["hex"]}" role="img" aria-label="Displayed sRGB colour {s["hex"]}"></div>'
                     f'<p><code>{s["hex"]}</code> · displayed sRGB8</p><p>{escape(s["event_label"])}: <b>{_range(cert, True)}</b> ({cert["status"]})</p>{observations}'
                     f'</section><section aria-label="Explicit endpoint distributions">{"".join(distributions)}</section></div></article>')
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#f3f1e9;color:#172c3c;font:17px/1.5 system-ui,sans-serif}}main{{max-width:1080px;margin:auto;padding:24px}}h1{{font:36px Georgia,serif}}h2{{font-size:22px}}article{{background:white;border:1px solid #d6d9d8;border-radius:12px;margin:24px 0;padding:22px}}a{{color:#14547a}}.columns{{display:grid;grid-template-columns:1fr 1fr;gap:32px}}.bar{{height:28px;display:flex;border:1px solid #526776}}.numbers{{overflow-wrap:anywhere;font-size:15px}}.swatch{{width:140px;height:95px;border:1px solid #526776}}code{{font-size:15px}}@media(max-width:650px){{main{{padding:14px}}h1{{font-size:29px}}.columns{{grid-template-columns:1fr;gap:8px}}article{{padding:16px}}}}
[hidden]{{display:none!important}}button,select{{font:inherit;padding:8px;max-width:100%}}button{{cursor:pointer}}.tools{{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:16px 0}}:focus-visible{{outline:3px solid #14547a;outline-offset:3px}}#vector-window{{height:560px;max-height:65vh;overflow:auto;border:1px solid #526776;background:#f3f1e9}}#vector-window svg{{display:block;width:1040px;max-width:none;height:auto}}.vector-help{{font-size:15px}}
</style></head><body><main><h1>{escape(title)}</h1>
<p>What probability could hide behind one blended colour? Every interval below has exact rational certificates and endpoint distributions you can inspect.</p>
<div class="tools" id="view-tools" hidden>
<label for="case-choice">Case</label><select id="case-choice"><option value="all">All cases</option>{options}</select>
<button type="button" id="vector-toggle" aria-pressed="false">Open the complete vector atlas</button></div>
<p><a href="first_legend.svg" download>Download SVG for printing or zooming</a> · <a href="witnesses.json">Rational certificates</a> · <a href="example-output.txt">Real importing program output</a></p>
<section id="vector-view" aria-label="Complete vector atlas" hidden>
<p class="vector-help">Text stays at its printed size. Swipe sideways or focus the diagram and use arrow keys. Choose a case above to jump to its row.</p>
<div class="tools"><button type="button" id="vector-left">Swatch and interval</button><button type="button" id="vector-right">Endpoint distributions</button></div>
<div id="vector-window" tabindex="0" role="region" aria-label="Scrollable vector atlas">{build_svg(swatches, palettes, title)}</div></section>
<div id="card-view">
<p>Compute a linear-light blend, transfer to sRGB, then round to bytes. The opaque, flat sRGB8 swatches follow that pipeline. Raw linear8 data has a separate byte bound; its hex preview does not have the same displayed light.</p>
<p>Byte intervals conservatively include every compatible distribution. Percentage endpoints round outward; the exact fractions in the certificates are authoritative. Bars show the two <em>exact-case</em> endpoint distributions beside the same swatch. This is a supplied comparison, not a blind readability study.</p>
{''.join(cards)}</div><footer>Supported: declared rational linear-light sRGB palettes, exact colours, sRGB8 and linear8 observations, half-up rounding. No screenshots, compression, alpha compositing, colour profiles or encoded-space blending. See DISPLAY.md in the repository for the derivation and limits.</footer></main><script>
const choice = document.getElementById('case-choice');
const vector = document.getElementById('vector-view');
const viewport = document.getElementById('vector-window');
const toggle = document.getElementById('vector-toggle');
function showCase() {{
  const index = choice.value;
  document.querySelectorAll('article[data-case]').forEach(card => {{
    card.hidden = index !== 'all' && card.dataset.case !== index;
  }});
  viewport.scrollTop = index === 'all' ? 0 : 150 + 290 * Number(index);
}}
toggle.addEventListener('click', () => {{
  const showing = vector.hidden;
  vector.hidden = !showing;
  document.getElementById('card-view').hidden = showing;
  toggle.textContent = showing ? 'Read the responsive cards' : 'Open the complete vector atlas';
  toggle.setAttribute('aria-pressed', String(showing));
  showCase();
}});
choice.addEventListener('change', showCase);
document.getElementById('vector-left').addEventListener('click', () => {{ viewport.scrollLeft = 0; }});
document.getElementById('vector-right').addEventListener('click', () => {{ viewport.scrollLeft = 520; }});
document.getElementById('view-tools').hidden = false;
</script></body></html>'''


def render_atlas(palettes: Mapping[str, bc.Palette], cases: Sequence[Case], *,
                 modes: Sequence[str] = dc.MODES,
                 title: str = 'What a Blended Colour Can Say') -> dict[str, str]:
    """Pure renderer: caller-owned palettes/cases -> SVG, HTML and certificate JSON."""
    swatches = evaluate_cases(palettes, cases, modes)
    data = dict(schema='blended-colour-atlas-v2', model='rational-linear-light-srgb',
                rounding='half-up', observation_claim='closed-rational-outer-box',
                palettes={name: dict(labels=list(p.labels), values=list(map(str, p.values)),
                                     colours=[list(map(str, c)) for c in p.colours])
                          for name, p in palettes.items()}, swatches=swatches)
    verify_atlas(data)
    return dict(svg=build_svg(swatches, palettes, title), html=build_html(swatches, palettes, title),
                witnesses=json.dumps(data, indent=2, sort_keys=True) + '\n')


def generate_all(out_dir: Path | None = None) -> dict[str, str]:
    target = out_dir if out_dir is not None else PROJECT_DIR / 'legends'
    target.mkdir(parents=True, exist_ok=True)
    outputs = render_atlas(bc.builtin_palettes(), default_cases())
    names = dict(svg='first_legend.svg', html='first_legend.html', witnesses='witnesses.json')
    for kind, name in names.items():
        (target / name).write_text(outputs[kind], encoding='utf-8')
    from example_import import run_example
    summary = run_example(target)
    (target / 'example-output.txt').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return {kind: str(target / name) for kind, name in names.items()}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Regenerate the vector atlas, certificates and real importing example.')
    parser.add_argument('--out', type=Path, default=PROJECT_DIR / 'legends')
    args = parser.parse_args(argv)
    generate_all(args.out)
    output = (args.out / 'example-output.txt').read_text(encoding='utf-8')
    print(f'Verified {len(default_cases())} exact cases and {2 * len(default_cases())} byte boxes; wrote atlas and importing example.')
    print(output, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
