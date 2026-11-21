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


def _pct(value: str, upper: bool = False, *, nearest: bool = False) -> str:
    """Two-decimal percent: outward bounds or half-up distribution labels."""
    x = F(value) * 10000
    if nearest:
        x += F(1, 2)
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


# Keep closed native selects usable with real keys on both desktop and mobile.
# Popup menus retain their browser behavior; this handles keys delivered to the page.
SELECT_KEYS = """
document.querySelectorAll('select').forEach(control => {
  control.addEventListener('keydown', event => {
    if (event.altKey || event.ctrlKey || event.metaKey) return;
    const moves = {Home: 0, End: control.options.length - 1,
                   ArrowDown: control.selectedIndex + 1, ArrowUp: control.selectedIndex - 1};
    if (!(event.key in moves)) return;
    event.preventDefault();
    control.selectedIndex = Math.max(0, Math.min(control.options.length - 1, moves[event.key]));
    control.dispatchEvent(new Event('change'));
  });
});
"""


def _mode_result(s: dict, mode: str) -> tuple[dict, str, str]:
    if mode == 'exact':
        cert, scope = s['certificate'], 'Exact linear-light colour'
    else:
        observation = next(o for o in s['observations'] if o['mode'] == mode)
        cert = observation['certificate']
        scope = f"{mode} observation {observation['hex']} (conservative outer box)"
    lo, hi = F(cert['p_min']), F(cert['p_max'])
    status = 'EXACT' if lo == hi else 'UNIDENTIFIABLE' if (lo, hi) == (0, 1) else 'BOUNDED'
    return cert, scope, status


def _mode_svg(swatches: list[dict], palettes: Mapping[str, bc.Palette], title: str,
              queries: Mapping[str, str], *, all_modes: bool = False) -> str:
    height = 140 + 320 * len(swatches)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1040" height="{height}" viewBox="0 0 1040 {height}" role="img" aria-labelledby="mode-title mode-desc">',
             f'<title id="mode-title">{escape(title)}</title>',
             '<desc id="mode-desc">Each row states its observation model, corresponding probability bounds, status and extremal distributions.</desc>',
             '<style>[hidden]{display:none}text{font:16px sans-serif;fill:#172c3c}.heading{font:bold 20px sans-serif}.small{font:14px monospace}.label{font:bold 16px sans-serif}</style>',
             f'<rect width="1040" height="{height}" fill="#f3f1e9"/>',
             _text(30, 40, title, 'heading'),
             _text(30, 74, 'One observation model per row. The bounds, status and distributions all belong to that model.'),
             _text(30, 103, 'Rounded models use closed conservative boxes; exact fractions in certificates are authoritative.')]
    for i, s in enumerate(swatches):
        y = 140 + 320 * i
        for mode in ('exact', *(o['mode'] for o in s['observations'])):
            if not all_modes and mode != queries[s['id']]:
                continue
            cert, scope, status = _mode_result(s, mode)
            hidden = '' if mode == queries[s['id']] else ' hidden="hidden"'
            parts.extend((f'<g data-case="{i}" data-mode="{mode}" data-query="{queries[s["id"]]}"{hidden}>',
                          f'<rect x="18" y="{y}" width="1004" height="306" rx="10" fill="white"/>',
                          _text(34, y + 30, f"{s['id']} / {s['title']}", 'heading'),
                          _text(34, y + 60, scope, 'label'),
                          _text(34, y + 94, f"{s['event_label']} {_range(cert, mode == 'exact')} / {status}", 'heading'),
                          f'<rect x="34" y="{y+118}" width="92" height="72" fill="{s["hex"]}" stroke="#526776"/>',
                          _text(144, y + 142, f"Displayed sRGB: {s['hex']}"),
                          _text(144, y + 172, 'linear8 bytes are data, not displayed light.', 'small'),
                          _text(34, y + 232, 'EXACT: one value; BOUNDED: a restricted interval.', 'small'),
                          _text(34, y + 258, 'UNIDENTIFIABLE: any probability from 0 to 1.', 'small'),
                          _text(552, y + 60, f'{mode}: lower / upper endpoint distributions', 'label')))
            for k, key in enumerate(('witness_min', 'witness_max')):
                weights = cert[key]
                # Rounded endpoint fractions can be thousands of digits long.
                bars = _bars(palettes[s['palette']], weights, 552, y + 85 + 86*k)
                labels = [f'{j+1}: {_pct(w, nearest=True)}' for j, w in enumerate(weights) if F(w)]
                bars = bars[:bars.index('<text')]
                for line in range(0, len(labels), 3):
                    bars += _text(552, y + 127 + 86*k + 18*(line//3), '  '.join(labels[line:line+3]), 'small')
                parts.append(bars)
            parts.extend((_text(552, y+260, 'Labels: stop number : rounded probability', 'small'),
                          _text(552, y+283, 'Exact weights: cards and rational certificates', 'small'), '</g>'))
    return '\n'.join(parts + ['</svg>'])


def _mode_html(swatches: list[dict], palettes: Mapping[str, bc.Palette], title: str,
               queries: Mapping[str, str], svg: str) -> str:
    cards = []
    modes = ('exact', *(o['mode'] for o in swatches[0]['observations']))
    for i, s in enumerate(swatches):
        palette = palettes[s['palette']]
        for mode in modes:
            cert, scope, status = _mode_result(s, mode)
            hidden = '' if mode == queries[s['id']] else ' hidden'
            endpoints = []
            for name, key in (('Lower endpoint', 'witness_min'), ('Upper endpoint', 'witness_max')):
                bars = ''.join(f'<span style="flex:{float(F(w)):.12g};background:{bc.rgb_to_hex(palette.colours[j])}"></span>' for j, w in enumerate(cert[key]) if F(w))
                labels = '; '.join(f'{palette.labels[j]}: {w if mode == "exact" else _pct(w, nearest=True)}' for j, w in enumerate(cert[key]) if F(w))
                endpoints.append(f'<h3>{name}</h3><div class="bar" aria-hidden="true">{bars}</div><p class="numbers">{escape(labels)}</p>')
            targets = ', '.join(palette.labels[j] for j in s['event_indices'])
            cards.append(f'<article data-case="{i}" data-mode="{mode}" data-query="{queries[s["id"]]}"{hidden}>'
                         f'<h2>{escape(s["id"] + " / " + s["title"])}</h2><p class="scope">{escape(scope)}</p>'
                         f'<p class="result">{escape(s["event_label"])}: <strong>{_range(cert, mode == "exact")}</strong><br><b>{status}</b></p>'
                         f'<p>Target stops: {escape(targets)}</p><div class="columns"><section>'
                         f'<div class="swatch" style="background:{s["hex"]}" role="img" aria-label="Displayed sRGB colour {s["hex"]}"></div>'
                         f'<p>Displayed sRGB: <code>{s["hex"]}</code></p><p>All bounds and distributions in this card use <b>{mode}</b>.</p>'
                         f'</section><section aria-label="Endpoint distributions for {mode}">{"".join(endpoints)}</section></div></article>')
    options = ''.join(f'<option value="{i}">{escape(s["id"]+" / "+s["title"])}</option>' for i, s in enumerate(swatches))
    mode_options = ''.join(f'<option value="{m}">{m}</option>' for m in modes)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}</title><style>
*{{box-sizing:border-box}}[hidden]{{display:none!important}}body{{margin:0;background:#f3f1e9;color:#172c3c;font:17px/1.5 system-ui,sans-serif}}main{{max-width:1080px;margin:auto;padding:24px}}h1{{font:36px Georgia,serif}}h2{{font-size:22px}}h3{{font-size:17px}}article{{background:white;border:1px solid #d6d9d8;border-radius:12px;margin:24px 0;padding:22px}}.scope{{font-weight:bold;border-left:5px solid #14547a;padding:10px;background:#edf4f7}}.result{{font-size:23px}}.columns{{display:grid;grid-template-columns:1fr 1fr;gap:32px}}.bar{{display:flex;height:28px;border:1px solid #526776}}.numbers{{overflow-wrap:anywhere;font-size:15px}}.swatch{{width:140px;height:95px;border:1px solid #526776}}.tools{{display:flex;flex-wrap:wrap;gap:10px;align-items:center}}button,select{{font:inherit;padding:8px;max-width:100%}}:focus-visible{{outline:3px solid #14547a;outline-offset:3px}}a{{color:#14547a}}#vector-window{{height:560px;max-height:65vh;overflow:auto;border:1px solid #526776}}#vector-window svg{{display:block;width:1040px;max-width:none;height:auto}}@media(max-width:650px){{main{{padding:14px}}h1{{font-size:29px}}article{{padding:16px}}.columns{{grid-template-columns:1fr;gap:8px}}}}
</style></head><body><main><h1>{escape(title)}</h1>
<p>Choose the observation model. Every visible interval, status and endpoint distribution uses that selection.</p>
<div class="tools" id="view-tools" hidden><label for="mode-choice">Observation model</label><select id="mode-choice"><option value="query">Case question</option>{mode_options}</select>
<label for="case-choice">Case</label><select id="case-choice"><option value="all">All cases</option>{options}</select><button id="vector-toggle" type="button" aria-pressed="false">Open the complete vector atlas</button></div>
<p id="selection" role="status" aria-live="polite">Showing each case's stated model.</p>
<p>EXACT means one probability; BOUNDED means a restricted interval; UNIDENTIFIABLE means [0, 1]. Byte bounds conservatively enclose rounded observations. Percentages round outward. linear8 bytes are raw data; the swatch always shows sRGB light.</p>
<p><a href="first_legend.svg" download>Download vector atlas</a> · <a href="witnesses.json">Rational certificates</a></p>
<section id="vector-view" aria-label="Selected observation model vector atlas" hidden><p>Use the model and case selectors above in either view. Pan sideways with arrow keys or the column buttons.</p><div class="tools"><button id="vector-left" type="button">Swatch and interval</button><button id="vector-right" type="button">Endpoint distributions</button></div><div id="vector-window" tabindex="0" role="region" aria-label="Scrollable vector atlas">{svg}</div></section><template id="vector-models">{_mode_svg(swatches, palettes, title, queries, all_modes=True)}</template>
<div id="card-view">{''.join(cards)}</div><footer>Closed rational outer boxes, half-up byte rounding and declared linear-light palettes only. No screenshot decoding, profiles, compression or alpha compositing. No reader benefit is claimed.</footer></main><script>
const choice=document.getElementById('case-choice'), mode=document.getElementById('mode-choice'), viewport=document.getElementById('vector-window');
function select() {{
  document.querySelectorAll('article[data-mode]').forEach(node=>{{
    const wanted=mode.value==='query'?node.dataset.query:mode.value;
    node.hidden=node.dataset.mode!==wanted || (choice.value!=='all' && node.dataset.case!==choice.value);
  }});
  const diagram=document.getElementById('vector-models').content.firstElementChild.cloneNode(true);
  diagram.querySelectorAll('g[data-mode]').forEach(node=>{{
    const wanted=mode.value==='query'?node.dataset.query:mode.value;
    if(node.dataset.mode!==wanted || (choice.value!=='all' && node.dataset.case!==choice.value)) node.remove();
    else node.removeAttribute('hidden');
  }});
  viewport.replaceChildren(diagram);
  viewport.scrollTop=choice.value==='all'?0:140+320*Number(choice.value);
  document.getElementById('selection').textContent=mode.value==='query'?"Showing each case's stated model.":'Showing '+mode.value+' bounds, status and endpoint distributions.';
}}
choice.addEventListener('change',select);mode.addEventListener('change',select);
document.getElementById('vector-toggle').addEventListener('click',event=>{{
 const showing=document.getElementById('vector-view').hidden;
 document.getElementById('vector-view').hidden=!showing;document.getElementById('card-view').hidden=showing;
 event.target.setAttribute('aria-pressed',String(showing));event.target.textContent=showing?'Read the responsive cards':'Open the complete vector atlas';select();
}});
document.getElementById('vector-left').addEventListener('click',()=>{{viewport.scrollLeft=0;}});
document.getElementById('vector-right').addEventListener('click',()=>{{viewport.scrollLeft=520;}});
document.getElementById('view-tools').hidden=false;
{SELECT_KEYS}
</script></body></html>'''


def render_atlas(palettes: Mapping[str, bc.Palette], cases: Sequence[Case], *,
                 modes: Sequence[str] = dc.MODES,
                 title: str = 'What a Blended Colour Can Say', mode_led: bool = False,
                 query_modes: Mapping[str, str] | None = None) -> dict[str, str]:
    """Render caller cases; mode_led opts into scope-led cards and vector rows.

    The default presentation is fixed for the archived first experiment and
    existing importers. Certificates and the return contract are identical.
    """
    swatches = evaluate_cases(palettes, cases, modes)
    data = dict(schema='blended-colour-atlas-v2', model='rational-linear-light-srgb',
                rounding='half-up', observation_claim='closed-rational-outer-box',
                palettes={name: dict(labels=list(p.labels), values=list(map(str, p.values)),
                                     colours=[list(map(str, c)) for c in p.colours])
                          for name, p in palettes.items()}, swatches=swatches)
    verify_atlas(data)
    if mode_led:
        queries = {s['id']: (query_modes or {}).get(s['id'], modes[0]) for s in swatches}
        if any(m not in ('exact', *modes) for m in queries.values()):
            raise ValueError('Query mode must have a computed certificate')
        svg = _mode_svg(swatches, palettes, title, queries)
        return dict(svg=svg, html=_mode_html(swatches, palettes, title, queries, svg),
                    witnesses=json.dumps(data, indent=2, sort_keys=True) + '\n')
    return dict(svg=build_svg(swatches, palettes, title), html=build_html(swatches, palettes, title),
                witnesses=json.dumps(data, indent=2, sort_keys=True) + '\n')


def generate_all(out_dir: Path | None = None) -> dict[str, str]:
    target = out_dir if out_dir is not None else PROJECT_DIR / 'legends'
    target.mkdir(parents=True, exist_ok=True)
    outputs = render_atlas(bc.builtin_palettes(), default_cases(), mode_led=True)
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
